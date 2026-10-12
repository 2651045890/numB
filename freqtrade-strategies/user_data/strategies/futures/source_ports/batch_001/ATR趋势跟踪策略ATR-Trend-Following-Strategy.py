"""Port of sources/SM_0f287b808ea41da7.pine
(ATR趋势跟踪策略ATR-Trend-Following-Strategy / "ATR Strategy").

A v3-era port of HPotter's ATR trailing stop, declared with only a title and a
commission:

    strategy(title="ATR Strategy", overlay=true,
             commission_type=strategy.commission.percent, commission_value=0.075)
    nATRPeriod = input(5)
    nATRMultip = input(3.5)
    xATR = ta.atr(nATRPeriod)
    nLoss = nATRMultip * xATR
    xATRTrailingStop = iff(close >  nz(xATRTrailingStop[1], 0)
                             and close[1] > nz(xATRTrailingStop[1], 0),
                           math.max(nz(xATRTrailingStop[1], 0), close - nLoss),
                       iff(close <  nz(xATRTrailingStop[1], 0)
                             and close[1] < nz(xATRTrailingStop[1], 0),
                           math.min(nz(xATRTrailingStop[1], 0), close + nLoss),
                       iff(close > nz(xATRTrailingStop[1], 0),
                           close - nLoss, close + nLoss)))

    barbuy  = close > xATRTrailingStop
    barsell = close < xATRTrailingStop

    strategy.entry("Long",  strategy.long,  when = barbuy)
    strategy.entry("Short", strategy.short, when = barsell)

so the whole trade body is one ratcheting ATR band and two opposite market
entries: price above the band goes long, price below it goes short. Because
`barbuy` and `barsell` cannot both hold, at most one entry is placed per bar,
and with Pine's default pyramiding of 0 a repeat of the side already held does
nothing -- the position flips only when price crosses the band.

`xATRTrailingStop` is a self-referencing variable: reading `xATRTrailingStop[1]`
gives it implicit history (a `var`-like series buffer), which is the standard
Pine v3/v4 idiom. It is a pure function of `close`, `high`, `low` and the ATR --
nothing about the position or the order book feeds into it -- so the port
computes the entire series up front in `pine_indicators` and the script only
reads it. That is exact, not an approximation: bar `i`'s value depends on bar
`i-1`'s value and nothing later.

Seeding: `nz(x, 0)` replaces the initial na with 0, so on the first bar the
`close > 0` branch wins and the band is `close - nLoss`; and `ta.atr(5)` is na
until five true ranges have accumulated, which makes `nLoss` na and the band na
for bars 0..3. From bar 4 onward the recursion runs normally.

`pos`, `color` and `barcolor()` in the source feed only `plot()` colouring --
`pos` never reaches an entry or exit -- so they are dropped: they cannot move a
fill. The source declares no `strategy.exit`, no stop/limit entry and no
`strategy.close`, so `source_reproduce_stops` is False.

`strategy()` declares no sizing, so Pine's documented default applies:
`default_qty_type = strategy.fixed`, `default_qty_value = 1`. Commission is
declared at 0.075% per side and is carried into `source_commission_percent`, so
the backtest is priced on the source's own cost basis rather than the venue's
taker fee (PINE_SEMANTICS.md 5.1).
"""
import numpy as np
import pandas as pd

from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


def _nz(value: float) -> float:
    """Pine `nz`: an na value becomes 0."""
    return 0.0 if value is None or np.isnan(value) else float(value)


def _pine_gt(left: float, right: float) -> bool:
    """Pine `>`: a comparison with an na operand is false."""
    if np.isnan(left) or np.isnan(right):
        return False
    return bool(left > right)


def _pine_lt(left: float, right: float) -> bool:
    """Pine `<`: a comparison with an na operand is false."""
    if np.isnan(left) or np.isnan(right):
        return False
    return bool(left < right)


def pine_atr_trailing_stop(dataframe: pd.DataFrame, atr_period: int,
                           atr_multiplier: float) -> pd.Series:
    """The source's `xATRTrailingStop` series, bar by bar.

    The three-way `iff` is reproduced in source order. `math.max` / `math.min`
    propagate na here (`pine_ta.pine_max` / `pine_min` are `np.maximum` /
    `np.minimum`), which is what makes the band na on the bars where `nLoss` is
    still na: `nz()` only zeroes the PREVIOUS band value, not the new candidate.

    The ratchet is the point of the indicator: while price stays on one side of
    the band the band only ever moves in that direction, and it is the crossing
    of `close` back over it that flips the trade.
    """
    atr = ta.pine_atr(dataframe, int(atr_period))
    n_loss = float(atr_multiplier) * atr
    close = dataframe["close"].to_numpy(dtype=float)
    loss = n_loss.to_numpy(dtype=float)

    size = len(dataframe)
    trailing = np.full(size, np.nan)
    for i in range(size):
        # nz(xATRTrailingStop[1], 0): na on the first bar, 0 after nz().
        previous = _nz(trailing[i - 1]) if i >= 1 else 0.0
        previous_close = close[i - 1] if i >= 1 else np.nan
        if _pine_gt(close[i], previous) and _pine_gt(previous_close, previous):
            trailing[i] = ta.pine_max(previous, close[i] - loss[i])
        elif _pine_lt(close[i], previous) and _pine_lt(previous_close, previous):
            trailing[i] = ta.pine_min(previous, close[i] + loss[i])
        elif _pine_gt(close[i], previous):
            trailing[i] = close[i] - loss[i]
        else:
            trailing[i] = close[i] + loss[i]
    return pd.Series(trailing, index=dataframe.index, dtype=float)


class SMATRTrendFollowing_0f287b(PinePortBase, IStrategy):
    source_id = "SM_0f287b808ea41da7"
    source_file = "batch_001/ATR趋势跟踪策略ATR-Trend-Following-Strategy.md"
    timeframe = "1d"
    can_short = True
    source_defaults = {
        # input(5)
        "nATRPeriod": 5,
        # input(3.5)
        "nATRMultip": 3.5,
    }
    # strategy() declares no default_qty_type / default_qty_value, so Pine's
    # documented defaults apply: strategy.fixed with a value of 1.
    source_qty_type = "fixed"
    source_qty_value = 1.0
    # commission_type=strategy.commission.percent, commission_value=0.075
    source_commission_percent = 0.075
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0  # not declared in the source -> Pine default
    # No strategy.exit / stop / limit / close anywhere: entries only.
    source_reproduce_stops = False
    source_fidelity_notes = [
        "The source has no strategy.exit(), no stop=/limit= on strategy.entry() "
        "and no strategy.close()/close_all(). A position ends only when the "
        "opposite entry fills, so the port sets source_reproduce_stops=False and "
        "the engine's pine_stop_level / pine_limit_level stay nan on every bar. "
        "Despite the name 'ATR Trailing Stop', xATRTrailingStop is an indicator "
        "series used as an entry trigger -- it is never handed to a broker as a "
        "stop order, so mirroring it into custom_stoploss would invent an exit "
        "the source does not have.",
        "pos, color and barcolor() in the source are plot-only: pos is consumed "
        "only by `color = pos == -1 ? ...` and both feed plot()/barcolor(). "
        "Neither reaches an entry or an exit condition, so both are dropped. "
        "Dropping them cannot move a fill.",
        "ta.atr is ta.rma(ta.tr(true), nATRPeriod) with pine_ta's documented "
        "Wilder seeding (the SMA of the first nATRPeriod non-na true ranges) and "
        "na observations skipped without advancing the recursion. TradingView "
        "does not publish its exact seeding for this, so the band's first bars "
        "are a modelled result (PINE_SEMANTICS.md sections 3.1-3.3); the ATR "
        "values converge quickly, but this port's earliest bars are not "
        "certified against the platform.",
        "math.max / math.min are modelled as na-propagating (np.maximum / "
        "np.minimum), so `math.max(nz(xATRTrailingStop[1]), close - nLoss)` is "
        "na while nLoss is na. nz() zeroes only the PREVIOUS band value, not the "
        "new candidate, which is why the band is na on bars 0..3 where a "
        "5-period ATR does not exist yet, and the band's first defined value is "
        "on bar index 4. A na-propagating reading of math.max is the choice "
        "PINE_SEMANTICS.md records for pine_ta.pine_max.",
        "xATRTrailingStop is a self-referencing variable, so Pine gives it "
        "implicit history (a var-like series). The port evaluates the whole "
        "recursion in pine_indicators rather than incrementally inside "
        "pine_script. This is exact rather than an approximation: the series "
        "depends only on close/high/low and the ATR, so bar i depends on bar i-1 "
        "and on nothing the position does.",
        "Pine's crossover semantics at equality: the source tests `close > "
        "xATRTrailingStop` and `close < xATRTrailingStop`, so a close exactly ON "
        "the band places no entry and leaves the current position untouched. The "
        "port keeps that -- the two predicates are strict and are not replaced "
        "by a cross-over/cross-under operator.",
        "With pyramiding 0 (Pine's default; the source does not declare it) a "
        "repeated same-side entry while that side is held is ignored at "
        "order-creation time, which is what leaves the position flipping only "
        "when price crosses the band.",
        "Initial capital is not declared in strategy(), so Pine's documented "
        "default of 1000000 is used and recorded here; Freqtrade's own wallet "
        "default is not a substitute for it (PINE_SEMANTICS.md 1.4).",
        "pine_engine does not apply the venue's contract-size rounding "
        "(mintick / step truncation) -- the engine trades floating quantities "
        "(PINE_SEMANTICS.md section 2). verify_chain measures the framework's "
        "rounded amount against the engine's quantity separately.",
        "The backtest header's `basePeriod: 1h` asks the platform for 1h "
        "intrabar fills (bar magnifier). pine_engine resolves every order "
        "against the daily bar alone, so intrabar sequencing within the bar is "
        "not reproduced. The header's start/end window is extraction metadata, "
        "not an input.time filter in the script, so no data is trimmed by it.",
        "Version note (source kept as extracted, not 'fixed'): the file mixes "
        "`iff()`, which Pine removed in v5, with `ta.atr()`, which only exists "
        "from v5, and declares no //@version. It therefore does not compile "
        "under any single Pine version. The port translates the source as "
        "written; no behaviour was changed to make it version-consistent.",
        "The strategy is always in the market once it starts: `barbuy` or "
        "`barsell` holds on essentially every bar after warm-up, so each bar "
        "re-issues an entry for the band's current side. Only the flips fill.",
    ]

    def pine_indicators(self, dataframe, params):
        dataframe["pine_atr"] = ta.pine_atr(dataframe, int(params["nATRPeriod"]))
        dataframe["pine_atr_trailing_stop"] = pine_atr_trailing_stop(
            dataframe, int(params["nATRPeriod"]), float(params["nATRMultip"])
        )
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "trailing_stop": dataframe["pine_atr_trailing_stop"].to_numpy(dtype=float),
            "close": dataframe["close"].to_numpy(dtype=float),
        }

    def pine_script(self, broker, i, ctx):
        # One Pine bar's worth of logic, verbatim: the two entries are the whole
        # trade body. `when=` is Pine's own guard -- a false condition means the
        # call places nothing, not that it places a dormant order.
        trailing_stop = ctx["trailing_stop"][i]
        close = ctx["close"][i]
        barbuy = _pine_gt(close, trailing_stop)
        barsell = _pine_lt(close, trailing_stop)
        broker.entry("Long", "long", when=barbuy)
        broker.entry("Short", "short", when=barsell)
