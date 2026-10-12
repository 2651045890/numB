"""Port of sources/SM_0aa6811452595103.pine
(batch_001/EMA双均线交叉策略-EMA-Dual-Moving-Average-Crossover-Strategy.md).

Pine v5. Two EMAs crossed, reversal entries, plus a daily loss / profit guard
built around `strategy.equity`. Reproduced call for call, in the source's own
order:

    shortMa = ta.ema(close, shortMaLength)          // 9
    longMa  = ta.ema(close, longMaLength)           // 21
    crossUp   = ta.crossover(shortMa, longMa)
    crossDown = ta.crossunder(shortMa, longMa)

    if crossUp
        strategy.entry("Long", strategy.long)
    if crossDown
        strategy.entry("Short", strategy.short)

    var float startOfDayEquity = na
    if (na(startOfDayEquity) or ta.change(time('D')) != 0)
        startOfDayEquity := strategy.equity

    maxDailyLoss   = 50000 * 0.0025
    maxDailyProfit = 50000 * 0.02
    currentDailyPL = strategy.equity - startOfDayEquity

    if currentDailyPL <= -maxDailyLoss
        strategy.close_all(comment="Max Daily Loss Reached")
    if currentDailyPL >= maxDailyProfit
        strategy.close_all(comment="Max Daily Profit Reached")

THE DAILY GUARD IS STRUCTURALLY INERT ON THE SOURCE'S OWN PERIOD, and that is
reproduced rather than "fixed". `time('D')` is the start of the bar's day, so on
a 1d chart `ta.change(time('D'))` is non-zero on EVERY bar: `startOfDayEquity` is
re-assigned to `strategy.equity` on the same bar whose P/L is then measured
against it, and `currentDailyPL` is exactly 0 on every bar. `0 <= -125` and
`0 >= 1000` are both false, so neither `close_all` ever fires. The two readings
of `strategy.equity` are separated by no order call, and placing an entry does
not move Pine's equity, so the two reads are the same number -- the zero is
exact, not approximate. The port keeps the whole computation (day-start
bookkeeping, both comparisons and both close_all calls) so the behaviour is
reproduced, not summarised away.

`ta.change(time('D'))` is evaluated on the bar's UTC day boundary; the project's
market data is UTC (PINE_SEMANTICS.md 3.4). On a frame whose index is not a
DatetimeIndex the change is na -- Pine treats an na comparison as false -- and
only the `na(startOfDayEquity)` clause fires, on the first bar.

FIDELITY:

* The md states the guard's base is the account's INITIAL capital ("账户初始资金
  的 0.25% / 2%"), but the source hardcodes the literal 50000, which is neither
  the md's claimed base nor Pine's documented default initial capital (1000000).
  The source is followed (50000); the md's description is wrong. Inert here
  because the guard never fires, but recorded rather than reconciled.
* `strategy()` declares only `title` and `overlay`, so every property is Pine's
  documented default: strategy.fixed / 1 contract, initial capital 1000000,
  commission 0%, pyramiding 0, `process_orders_on_close=false`. Neither entry
  passes a `qty`.
* There is no `strategy.exit` of any kind, so `source_reproduce_stops` is False
  and a position is closed only by the opposite entry reversing it (or by a
  close_all, which cannot fire -- see above). A position still open at the end
  of the window stays open.
* `ta.ema`'s seeding is the modelled first-non-na-value rule, a parity risk
  recorded in PINE_SEMANTICS.md 3.1; Pine does not publish its own rule.
* The two `plot()` calls and the two `plotshape()` calls are display-only and
  are not reproduced. `plotshape(series=crossUp, ...)` reads the same series the
  order calls read and adds no condition.
* The `/*backtest` header declares `period: 1d` on Futures_Binance BTC_USDT, so
  `timeframe` is "1d"; its `basePeriod: 1h` is the FMZ backtester's own
  granularity for filling those bars, not the strategy's period.
* Leverage, margin, liquidation and funding are not modelled, and the venue's
  contract-step rounding is not modelled either; the chain verifier measures the
  last one separately (PINE_SEMANTICS.md 1.6).
"""
import numpy as np
import pandas as pd
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase

# Literals in the source, not inputs: `maxDailyLoss = 50000 * 0.0025` and
# `maxDailyProfit = 50000 * 0.02`.
DAILY_BASE = 50000.0
DAILY_LOSS_FRACTION = 0.0025
DAILY_PROFIT_FRACTION = 0.02


def _day_change(index) -> np.ndarray:
    """`ta.change(time('D'))` in seconds: the bar's day start minus the previous.

    na on the first bar, exactly as Pine's `ta.change` is. `time('D')` is the
    start of the bar's day in the exchange's timezone, which for this project's
    data is UTC (PINE_SEMANTICS.md 3.4).
    """
    if isinstance(index, pd.DatetimeIndex):
        day_starts = index.normalize()
        return day_starts.to_series().diff().dt.total_seconds().to_numpy()
    return np.full(len(index), np.nan)


class SMEmaDualMovingAverageCrossover_0aa681(PinePortBase, IStrategy):
    source_id = "SM_0aa6811452595103"
    source_file = "EMA双均线交叉策略-EMA-Dual-Moving-Average-Crossover-Strategy.md"
    timeframe = "1d"
    can_short = True
    source_defaults: dict = {"shortMaLength": 9, "longMaLength": 21}
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    # No stop / limit / trail / profit / loss leg exists anywhere in the source,
    # so there is no engine stop level for the framework to mirror.
    source_reproduce_stops = False
    source_mintick = 0.1
    source_fidelity_notes = [
        "The daily loss/profit guard is structurally inert on the source's own "
        "declared period. `time('D')` advances on every 1d bar, so "
        "`ta.change(time('D')) != 0` is true on every bar and startOfDayEquity "
        "is re-assigned to strategy.equity on the very bar whose P/L is measured "
        "against it: currentDailyPL is exactly 0 and neither close_all can fire. "
        "The whole computation is reproduced anyway (day-start bookkeeping, both "
        "comparisons, both close_all calls), not summarised away.",
        "The md says the guard's base is the account's INITIAL capital (0.25% / "
        "2%), but the source hardcodes the literal 50000 -- neither the md's "
        "base nor Pine's default initial capital (1000000). The source is "
        "followed; the md's description is wrong. Inert either way because the "
        "guard never fires.",
        "strategy() declares only title and overlay, so every property is Pine's "
        "documented default: strategy.fixed / 1 contract, initial capital "
        "1000000, commission 0%, pyramiding 0, process_orders_on_close=false. "
        "Neither entry passes a qty.",
        "There is no strategy.exit of any kind, so source_reproduce_stops is "
        "False: a position is closed only by the opposite entry reversing it "
        "(or by a close_all, which cannot fire). A position open at the end of "
        "the window stays open.",
        "ta.ema's seeding is the modelled first-non-na-value rule, a parity risk "
        "recorded in PINE_SEMANTICS.md 3.1; Pine does not publish its own rule.",
        "ta.change(time('D')) is evaluated on the bar's UTC day boundary "
        "(PINE_SEMANTICS.md 3.4). On a frame whose index is not a DatetimeIndex "
        "it is na, which Pine treats as false, leaving only the "
        "na(startOfDayEquity) clause on the first bar.",
        "plot() / plotshape() are display-only and are not reproduced; they "
        "read the same series the order calls read and add no condition.",
        "The /*backtest header's basePeriod: 1h is the FMZ backtester's own "
        "granularity for filling the 1d bars, not the strategy's period.",
        "Leverage, margin, liquidation, funding and the venue's contract-step "
        "rounding are not modelled; the chain verifier measures the last one "
        "separately (PINE_SEMANTICS.md 1.6).",
    ]

    def pine_indicators(self, dataframe, params):
        close = dataframe["close"]
        short_ma = ta.pine_ema(close, int(params["shortMaLength"]))
        long_ma = ta.pine_ema(close, int(params["longMaLength"]))
        dataframe["pine_short_ma"] = short_ma
        dataframe["pine_long_ma"] = long_ma
        dataframe["pine_cross_up"] = ta.pine_crossover(short_ma, long_ma)
        dataframe["pine_cross_down"] = ta.pine_crossunder(short_ma, long_ma)
        # `ta.change(time('D'))`, in seconds. nan on the first bar.
        dataframe["pine_day_change"] = _day_change(dataframe.index)
        return dataframe

    def pine_context(self, dataframe, params):
        del params
        return {
            "cross_up": dataframe["pine_cross_up"].to_numpy(),
            "cross_down": dataframe["pine_cross_down"].to_numpy(),
            "day_change": dataframe["pine_day_change"].to_numpy(),
            # `var float startOfDayEquity = na` persists across bars; the dict is
            # built once per run and handed to every bar's script call.
            "state": {"start_of_day_equity": None},
        }

    def pine_script(self, broker, i, ctx):
        # if (crossUp)
        #     strategy.entry("Long", strategy.long)
        if ctx["cross_up"][i]:
            broker.entry("Long", "long")
        # if (crossDown)
        #     strategy.entry("Short", strategy.short)
        if ctx["cross_down"][i]:
            broker.entry("Short", "short")

        # var float startOfDayEquity = na
        # if (na(startOfDayEquity) or ta.change(time('D')) != 0)
        #     startOfDayEquity := strategy.equity
        state = ctx["state"]
        change = ctx["day_change"][i]
        if state["start_of_day_equity"] is None or (
            not np.isnan(change) and change != 0.0
        ):
            state["start_of_day_equity"] = broker.equity

        # currentDailyPL = strategy.equity - startOfDayEquity
        current_daily_pl = broker.equity - state["start_of_day_equity"]

        # if (currentDailyPL <= -maxDailyLoss)
        #     strategy.close_all(comment="Max Daily Loss Reached")
        if current_daily_pl <= -(DAILY_BASE * DAILY_LOSS_FRACTION):
            broker.close_all()
        # if (currentDailyPL >= maxDailyProfit)
        #     strategy.close_all(comment="Max Daily Profit Reached")
        if current_daily_pl >= DAILY_BASE * DAILY_PROFIT_FRACTION:
            broker.close_all()
