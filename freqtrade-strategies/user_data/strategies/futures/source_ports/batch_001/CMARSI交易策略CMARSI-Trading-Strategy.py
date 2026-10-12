"""Port of sources/SM_889fa30bb32d7c64.pine
(batch_001/CMARSI交易策略CMARSI-Trading-Strategy.md).

Pine v3 Connors-RSI oscillator, the "CMARSI" script on FMZ strategy/427929.
The indicator block is identical to the sibling port
`Composite-Entry-Signal-RSI-Trading-Strategy.py`; the exit call is not:

    src = close, lenrsi = 3, lenupdown = 2, lenroc = 100, malengt = 2,
    low = 40, high = 70, a = 1

    updown(s) =>                        # recursive run-length of closes
        isEqual   = s == s[1]
        isGrowing = s > s[1]
        ud = 0.0
        ud := isEqual ? 0 : isGrowing ? (nz(ud[1]) <= 0 ? 1 : nz(ud[1])+1)
                                      : (nz(ud[1]) >= 0 ? -1 : nz(ud[1])-1)
        ud
    rsi        = rsi(src, 3)
    updownrsi  = rsi(updown(src), 2)
    percentrank= percentrank(roc(src, 1), 100)
    crsi       = avg(rsi, updownrsi, percentrank)
    MA         = sma(crsi, 2)

    if crossover(MA, band0)
        strategy.entry("buy", strategy.long, when=strategy.position_size <= 0)
    if crossunder(MA, band1)
        strategy.exit("sell", "buy", profit=1000000, stop=10000000)

The two exit arguments are NOT the same kind of quantity. Pine counts
`profit=` in TICKS from the entry price (PINE_SEMANTICS 3.5), so the port passes
it through as ticks and lets the engine resolve it against the position's
average price instead of pre-multiplying by `mintick` itself: at `mintick = 0.1`
(BTC/USDT quotes in 0.1) it rests the take-profit 100000 price units above the
entry, far enough that no bar reaches it. `stop=`, on the other hand, is a
PRICE, not a tick distance: the source hands the engine the absolute level
10000000, which sits far ABOVE any BTC price in the window. A sell stop whose
level has already been passed is immediately marketable, so it triggers on the
first evaluated bar and the position is closed at that bar's open -- the exit
fires, one bar after its `crossunder` bar. The source's author presumably meant
10000000 ticks and wrote `stop=` where `loss=` was needed, but the call is
transcribed as written; what it does, rather than what it looks like it should
do, is what the port reproduces.

`strategy("CMARSI")` is called with a title and nothing else, so every property
is Pine's documented default: `default_qty_type=fixed`, `default_qty_value=1`,
`initial_capital=1000000`, `commission_value=0`, `pyramiding=0`,
`process_orders_on_close=false`. The `//@version=2` line above the call is a
decoration: the script header is `//@version=3`.

There is no short entry anywhere in the source, so `can_short` is False.

FIDELITY:

* The sibling source `SM_45aa6f7ba3499b37` is the same script with a different
  exit (`strategy.exit("close", "buy")`, no price legs) and two extra plot
  constants. Both are ported as written; neither the shared indicator block nor
  the differing exit was copied across without being read from its own source.
* `percentrank` is NOT in pine_ta, so it is implemented here from Pine's
  generic form. Two parts of that are MODELLED CHOICES (identical reasoning to
  the sibling port): bars that do not exist yet are na and are not counted
  while the denominator stays `length` -- the alternative "na until the window
  is full", this layer's rule for `sma`/`highest` (PINE_SEMANTICS 3.2), would
  make `crsi` and `MA` na for the first 100 bars -- and the rank counts `<=`.
* `avg(rsi, updownrsi, percentrank)` is the arithmetic mean with na
  propagation, Pine's default arithmetic rule; the source says nothing about na
  in `avg`.
* `profit=1000000, stop=10000000` are transcribed as ticks, per PINE_SEMANTICS
  3.5. The engine resolves them to prices 100000 / 1000000 units from the
  average entry, so the exit never fires -- which is also what the source's own
  author intended.
* `low`, `high` are the variables `40` and `70` reused as plot levels; the
  `plot()` calls are display-only, as is `plot(strategy.equity)`.
* Leverage, margin, funding and the venue's contract-step rounding are not
  modelled (PINE_SEMANTICS 1.6, 2.4).
"""
import numpy as np
import pandas as pd
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


def _updown(source: pd.Series) -> pd.Series:
    """Pine v3 `updown(s)`: signed run length of consecutive equal/growing bars.

    Recursive through `nz(ud[1])`, so it is a stateful walk, not a window.
    Pine v3 `nz(x)` with one argument replaces na with 0, which seeds bar 0;
    a comparison against na is false, so bar 0 takes the falling branch with
    `nz(ud[1]) = 0` and yields -1.
    """
    values = source.to_numpy(dtype=float)
    out = np.full(len(values), np.nan)
    previous = np.nan  # ud[1]
    for i, current in enumerate(values):
        last_source = values[i - 1] if i > 0 else np.nan
        comparable = not np.isnan(current) and not np.isnan(last_source)
        is_equal = comparable and current == last_source
        is_growing = comparable and current > last_source
        nz_previous = 0.0 if np.isnan(previous) else previous
        if is_equal:
            value = 0.0
        elif is_growing:
            value = 1.0 if nz_previous <= 0 else nz_previous + 1.0
        else:
            value = -1.0 if nz_previous >= 0 else nz_previous - 1.0
        out[i] = value
        previous = value
    return pd.Series(out, index=source.index, dtype=float)


def _percentrank(source: pd.Series, length: int) -> pd.Series:
    """Pine v3 `percentrank(source, length)`, in Pine's generic loop form.

    `count(source[i] <= source, i in 0..length-1) / length * 100`. A value that
    does not exist yet is na, and a Pine comparison against na is false, so it
    is simply not counted; the denominator stays `length`. See FIDELITY in the
    module docstring.
    """
    values = source.to_numpy(dtype=float)
    out = np.full(len(values), np.nan)
    for i in range(len(values)):
        current = values[i]
        if np.isnan(current):
            continue
        start = max(0, i - length + 1)
        window = values[start:i + 1]
        count = int(np.sum(window <= current))
        out[i] = count / length * 100.0
    return pd.Series(out, index=source.index, dtype=float)


class SMCMARSITradingStrategy_889fa3(PinePortBase, IStrategy):
    source_id = "SM_889fa30bb32d7c64"
    source_file = "CMARSI交易策略CMARSI-Trading-Strategy.md"
    timeframe = "1d"
    can_short = False
    source_defaults: dict = {}
    # strategy("CMARSI") declares no sizing, so Pine's defaults apply: fixed
    # quantity of 1 contract, initial capital 1000000, 0% commission,
    # pyramiding 0, process_orders_on_close false.
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    # The source's only exit is an OCA with a tick `stop=` leg (10000000 ticks),
    # so there IS a resting stop for the engine to mirror -- it simply sits far
    # enough away that no bar ever reaches it.
    source_reproduce_stops = True
    source_mintick = 0.1
    source_fidelity_notes = [
        "Same indicator block as the sibling source SM_45aa6f7ba3499b37; the "
        "exit differs (tick profit/stop here, a legless strategy.exit there). "
        "Each was read from its own source rather than assumed from the family.",
        "percentrank() is not in pine_ta and is implemented from Pine's loop "
        "form: count(source[i] <= source over the last `length` bars)/length*100. "
        "MODELLED CHOICES: bars before the series start are na and are not "
        "counted while the denominator stays length (the alternative, 'na until "
        "the window is full', would make crsi and MA na for the first 100 bars); "
        "the rank counts <=, as array.percentrank is documented to.",
        "avg(rsi, updownrsi, percentrank) is the arithmetic mean with na "
        "propagation, Pine's default arithmetic rule; the source does not say "
        "how avg treats na.",
        "profit=1000000 is TICKS (PINE_SEMANTICS 3.5) and rests the take-profit "
        "100000 price units above the entry, unreachable; stop=10000000 is a "
        "PRICE (not ticks) and sits above every BTC price in the window, so the "
        "sell stop is already marketable and closes the position at the next "
        "bar's open. Both transcribed as written.",
        "The engine evaluates a resting exit with a stop level that the market "
        "has already passed as triggering on the first bar it is checked, which "
        "is standard stop-order behaviour; the framework's custom_stoploss "
        "declines the same level (a long position has no stop above its rate), "
        "so the two sides part company here by construction.",
        "There is no short entry, so can_short is False.",
        "low/high are the level variables 40/70; all plot() calls, including "
        "plot(strategy.equity), are display-only.",
        "Markdown claims the strategy enters on a cross above 40 and exits on a "
        "cross below 70 of the composite RSI; the source evaluates the crosses "
        "on MA = sma(crsi, 2), not on crsi itself. The source is ported.",
        "Leverage, margin, funding and the venue's contract-step rounding are "
        "not modelled (PINE_SEMANTICS 1.6, 2.4).",
    ]

    def pine_indicators(self, dataframe, params):
        close = dataframe["close"]
        rsi = ta.pine_rsi(close, 3)
        updownrsi = ta.pine_rsi(_updown(close), 2)
        percentrank = _percentrank(ta.pine_roc(close, 1), 100)
        # crsi = avg(rsi, updownrsi, percentrank); MA = sma(crsi, 2)
        crsi = (rsi + updownrsi + percentrank) / 3.0
        ma = ta.pine_sma(crsi, 2)
        dataframe["pine_crsi"] = crsi
        dataframe["pine_ma"] = ma
        # if crossover(MA, band0)  /  if crossunder(MA, band1)
        dataframe["pine_cross_up_40"] = ta.pine_crossover(ma, 40.0)
        dataframe["pine_cross_down_70"] = ta.pine_crossunder(ma, 70.0)
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "ma": dataframe["pine_ma"].to_numpy(),
            "cross_up_40": dataframe["pine_cross_up_40"].to_numpy(),
            "cross_down_70": dataframe["pine_cross_down_70"].to_numpy(),
        }

    def pine_script(self, broker, i, ctx):
        # if crossover(MA, band0)
        #     strategy.entry("buy", strategy.long, when=strategy.position_size <= 0)
        if ctx["cross_up_40"][i]:
            broker.entry("buy", "long", when=broker.position_size <= 0)
        # if crossunder(MA, band1)
        #     strategy.exit("sell", "buy", profit=1000000, stop=10000000)
        if ctx["cross_down_70"][i]:
            broker.exit("sell", from_entry="buy", profit=1_000_000.0, stop=10_000_000.0)
