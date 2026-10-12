"""Port of sources/SM_21ccef83430f0c28.pine (batch_001/Logarithmic-Weighted-Moving-Average-Trading-Strategy-Based-on-Cross-Signal-Analysis-基于对数加权移动平均交叉信号的量化交易策略.md).

Pine v6. Weighted moving averages taken in log-price space and mapped back,
long on a cross above and short on a cross below:

    log_close    = math.log(close)
    log_shortWMA = ta.wma(log_close, shortWMA_length)   // 5
    log_longWMA  = ta.wma(log_close, longWMA_length)    // 20
    shortWMA     = math.exp(log_shortWMA)
    longWMA      = math.exp(log_longWMA)

    if longCondition:  strategy.entry("AL",  strategy.long)
    if shortCondition: strategy.entry("SAT", strategy.short)

where `longCondition = ta.crossover(shortWMA, longWMA)` and
`shortCondition = ta.crossunder(shortWMA, longWMA)`.

`strategy()` declares only `title` and `overlay`, so every property is Pine's
documented default: `strategy.fixed` / 1 contract, initial capital 1000000,
commission 0%, pyramiding 0. Neither entry passes `qty`, so the default 1
contract is what fills.

There is no exit call: a position is closed only by the opposite entry
reversing it, so `source_reproduce_stops` is False and a position open at the
end of the window stays open.

The comparison is made on the EXPONENTIATED averages, not on the log-space
values -- `exp` is monotone, so the crossover bar is the same either way, but
the source's own order (wma -> exp -> cross) is what is reproduced rather than
short-circuited.

FIDELITY:

* `ta.wma` is Pine's weighted MA with weights 1..length and the newest bar
  heaviest, and it returns na until its window is full. `pine_ta.pine_wma`
  supplies exactly that; `shortWMA` is therefore defined from bar 4 and
  `longWMA` from bar 19, and no cross can fire before bar 20.
* `math.log` is the NATURAL logarithm and `math.exp` its inverse;
  `np.log` / `np.exp` are the same functions. Taking the log of price makes the
  exp-of-wma a geometric-style mean, which is the point of the source and is
  not simplified into a plain WMA of close.
* THE MD HAS NO ARGUMENT TABLE -- its "Strategy Arguments" section is absent,
  so both input defaults (5 and 20) come from the source's `input.int` calls
  and nowhere else. The md's prose agrees with the code on the periods, so
  there is no md/source conflict to record here.
* `alert(...)` calls in the source are notification-only and are not modelled
  (PINE_SEMANTICS.md 2.7); they place no order. Their `freq_once_per_bar_close`
  cadence has no bearing on entries, which are evaluated at bar close anyway.
* `plot(shortWMA)` / `plot(longWMA)` are display-only and are not reproduced.
* Leverage, margin, liquidation and funding are not modelled; the venue's
  contract-step rounding is not modelled either, so the framework and the
  engine can differ by a rounded quantity.
"""
import numpy as np
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


class SMLogarithmicWeightedMovingAverage_21ccef(PinePortBase, IStrategy):
    source_id = "SM_21ccef83430f0c28"
    source_file = (
        "Logarithmic-Weighted-Moving-Average-Trading-Strategy-Based-on-Cross-Signal-Analysis-"
        "基于对数加权移动平均交叉信号的量化交易策略.md"
    )
    timeframe = "1d"
    can_short = True
    source_defaults: dict = {"shortWMA_length": 5, "longWMA_length": 20}
    # strategy(title, overlay=true): Pine defaults, nothing declared.
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    source_reproduce_stops = False
    source_fidelity_notes = [
        "No exit call exists: a position is closed only by the opposite entry "
        "reversing it, so source_reproduce_stops is False and a position open "
        "at the end of the window stays open.",
        "The WMAs are taken on math.log(close) and mapped back with math.exp, as "
        "the source does; the averages are NOT simplified into WMAs of close.",
        "The crossovers are evaluated on the exponentiated series, in the "
        "source's own order (wma -> exp -> cross).",
        "pine_ta.pine_wma returns na until its window is full, so shortWMA is "
        "defined from bar 4, longWMA from bar 19, and no signal can fire before "
        "bar 20 -- on the original platform the first longWMA is the 20th bar.",
        "alert(...) calls are notification-only and are not modelled "
        "(PINE_SEMANTICS.md 2.7); they place no order.",
        "plot(...) calls are display-only and are not reproduced.",
        "The md carries no Strategy Arguments table, so both input defaults are "
        "taken from the source's input.int calls; the md's prose agrees with the "
        "code on the 5/20 periods, so there is no md/source conflict.",
    ]

    def pine_indicators(self, dataframe, params):
        close = dataframe["close"]
        # log_close = math.log(close)
        log_close = np.log(close)
        # log_shortWMA / log_longWMA = ta.wma(log_close, n)
        log_short = ta.pine_wma(log_close, int(params["shortWMA_length"]))
        log_long = ta.pine_wma(log_close, int(params["longWMA_length"]))
        # shortWMA / longWMA = math.exp(...)
        short_wma = np.exp(log_short)
        long_wma = np.exp(log_long)

        dataframe["pine_short_wma"] = short_wma
        dataframe["pine_long_wma"] = long_wma
        dataframe["pine_long_condition"] = ta.pine_crossover(short_wma, long_wma)
        dataframe["pine_short_condition"] = ta.pine_crossunder(short_wma, long_wma)
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "long_condition": dataframe["pine_long_condition"].to_numpy(),
            "short_condition": dataframe["pine_short_condition"].to_numpy(),
        }

    def pine_script(self, broker, i, ctx):
        # if (longCondition)
        #     strategy.entry("AL", strategy.long)
        if ctx["long_condition"][i]:
            broker.entry("AL", "long")
        # if (shortCondition)
        #     strategy.entry("SAT", strategy.short)
        if ctx["short_condition"][i]:
            broker.entry("SAT", "short")
