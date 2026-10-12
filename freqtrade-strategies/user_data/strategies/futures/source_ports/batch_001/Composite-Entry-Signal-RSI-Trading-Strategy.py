"""Port of sources/SM_45aa6f7ba3499b37.pine
(batch_001/Composite-Entry-Signal-RSI-Trading-Strategy.md).

Pine v3 Connors-RSI oscillator. The source is the well-known "CMARSI" script
(`strategy("CMARSI")`), published on FMZ as strategy/426361; the markdown file
that carries it is named after a different FMZ strategy (426361's sibling
427929, "CMARSI-Trading-Strategy"), and the two bodies differ only in the exit
call and in two unused plot constants -- see FIDELITY. The source text is the
authority here.

The indicator, verbatim:

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

and the whole order set, verbatim:

    if crossover(MA, 40)
        strategy.entry("buy", strategy.long, when=strategy.position_size <= 0)
    if crossunder(MA, 70)
        strategy.exit("close", "buy")

`strategy("CMARSI")` is called with a title and nothing else, so every property
is Pine's documented default: `default_qty_type=fixed`, `default_qty_value=1`,
`initial_capital=1000000`, `commission_value=0`, `pyramiding=0`,
`process_orders_on_close=false`. The `//@version=2` line above the call is a
decoration: the script's header is `//@version=3` and the calls used exist in
both.

There is no short entry anywhere in the source, so `can_short` is False.

FIDELITY:

* `percentrank` is NOT in pine_ta, so it is implemented here from Pine's
  generic form -- a loop over the last `length` bars counting the values less
  than or equal to the current one, divided by `length`, times 100. Two parts
  of that are MODELLED CHOICES, because TradingView publishes the definition
  but not the implementation: (a) values that do not exist yet (`source[i]`
  past the start of the series) are na and Pine's comparison against na is
  false, so they are not counted while the denominator stays `length`; the
  alternative reading -- "na until the window is full", which is what this
  layer does for `sma`/`highest`/`stdev` (PINE_SEMANTICS 3.2) -- would make
  `crsi`, and therefore `MA`, na for the first 100 bars instead; (b) the rank
  counts `<=`, i.e. the current value counts itself, as `array.percentrank`
  -- the v5 spelling of the same idea -- is documented to.
* `avg(rsi, updownrsi, percentrank)` is the arithmetic mean with na
  propagation, which is Pine's default arithmetic rule. `avg` documented itself
  as "the average of its arguments" and said nothing about na; the alternative
  (skip na arguments) would move the first evaluable `crsi` from bar 4 to bar 3
  and is not chosen, because leaving na implicit in the sum is the reading that
  needs no extra assumption.
* `strategy.exit("close", "buy")` passes NO price leg. Pine's compiler rejects
  that call as doing nothing (PINE_SEMANTICS 1.15): the engine creates a
  resting exit order that can never fill, while the signal projection reads it
  as a market exit. The call is transcribed as written -- dropping it would be
  a rewrite of the source, and `broker.exit` with no legs is what the source
  says. The consequence is recorded, not repaired: the framework will close
  positions the engine keeps open.
* `low`, `high`, `vlow`, `band2` and the `plot()` calls are display-only.
  `band2 = 20` and `plot(vlow, ...)` are never read by an order call.
* `plot(strategy.equity)` is display-only.
* Leverage, margin and funding are not modelled; the venue's contract-step
  rounding is not modelled either (PINE_SEMANTICS 1.6 and 2.4).
"""
import numpy as np
import pandas as pd
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


def _updown(source: pd.Series) -> pd.Series:
    """Pine v3 `updown(s)`: signed run length of consecutive equal/growing bars.

    The function is recursive through `nz(ud[1])`, so it is a stateful walk over
    the series rather than a windowed formula. Pine v3 `nz(x)` with one argument
    replaces na with 0, which is what seeds bar 0 (and any na bar). A comparison
    against na is false in Pine, so bar 0 takes the falling branch with
    `nz(ud[1]) = 0`, giving -1.
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
    module docstring for why this reading was chosen over "na until full".
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


class SMCompositeEntrySignalRsi_45aa6f(PinePortBase, IStrategy):
    source_id = "SM_45aa6f7ba3499b37"
    source_file = "Composite-Entry-Signal-RSI-Trading-Strategy.md"
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
    # The only exit in the source is `strategy.exit("close", "buy")` with no
    # price leg, so there is no resting stop for the engine to mirror.
    source_reproduce_stops = False
    source_mintick = 0.1
    source_fidelity_notes = [
        "Source is the FMZ 'CMARSI' script (strategy/426361) while the markdown "
        "stem names a different FMZ strategy; the source body is the authority.",
        "percentrank() is not in pine_ta and is implemented from Pine's loop "
        "form: count(source[i] <= source over the last `length` bars)/length*100. "
        "MODELLED CHOICES: bars before the series start are na and are not "
        "counted while the denominator stays length (the alternative, 'na until "
        "the window is full', would make crsi and MA na for the first 100 bars); "
        "the rank counts <=, as array.percentrank is documented to.",
        "avg(rsi, updownrsi, percentrank) is the arithmetic mean with na "
        "propagation, Pine's default arithmetic rule; the source does not say "
        "how avg treats na.",
        "strategy.exit('close', 'buy') has NO price leg: Pine treats that call "
        "as doing nothing (PINE_SEMANTICS 1.15), the engine keeps the exit "
        "resting forever, and the signal projection still reads it as a market "
        "exit. Transcribed as written; the divergence is recorded, not repaired.",
        "There is no short entry, so can_short is False.",
        "low/high/vlow/band2 and every plot() are display-only; band2 and vlow "
        "are never read by an order call.",
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
        #     strategy.exit("close", "buy")
        if ctx["cross_down_70"][i]:
            broker.exit("close", from_entry="buy")
