"""Port of sources/SM_bf3b1f5b3fb76f00.pine (batch_001/EMA动量交易策略-EMA-Momentum-Trading-Strategy.md).

Pine v5, the author's own "EMA Crossover Strategy". A 10/21 EMA cross, with the
entry DELAYED by one bar:

    shortEmaLength = 10
    longEmaLength  = 21

    shortEma = ta.ema(close, shortEmaLength)
    longEma  = ta.ema(close, longEmaLength)

    longCondition  = ta.crossover(shortEma, longEma)
    shortCondition = ta.crossunder(shortEma, longEma)

    longSignal  = ta.valuewhen(longCondition, close, 1)
    shortSignal = ta.valuewhen(shortCondition, close, 1)

    if (longCondition[1])
        strategy.entry("Long", strategy.long)
    if (shortCondition[1])
        strategy.entry("Short", strategy.short)

The two EMA lengths are LOCAL VARIABLES, not `input()`s, so the port declares no
source parameters and keeps 10 / 21 as literals. `longSignal` / `shortSignal`
are assigned and never read by anything -- the entries test `longCondition[1]`
and `shortCondition[1]` directly -- so they are computed as columns and left
unread, exactly as the source leaves them.

`longCondition[1]` is the PREVIOUS bar's crossover value, so a cross on bar `t`
places the order on bar `t+1`, which the engine then fills at bar `t+2`'s open.
That is a two-bar delay in total, and it is what the source says: the "delay by
one bar" the md describes is the `[1]` on the condition, not a repricing of the
order.

`strategy()` declares only `title` and `overlay`, so every property is Pine's
documented default: `strategy.fixed` / 1 contract, initial capital 1000000,
commission 0%, `pyramiding 0`, `process_orders_on_close=false`. Neither entry
passes `qty`, so the default quantity supplies it.

The `/*backtest` header declares `period: 1d` on Futures_Binance BTC_USDT, so
`timeframe` is "1d".

There is no `strategy.close` / `strategy.exit` and no stop or limit in the
source, so `source_reproduce_stops` is False: a position is only closed by the
opposite entry reversing it, and a position open at the end of the window stays
open.

FIDELITY:

* The `[1]` history reference is over the CHART's bars, not over the signal
  bars: `longCondition[1]` is the crossover value of the immediately preceding
  bar. On the frame's first bar it is na, and Pine treats a na condition as
  false, so no order is placed there. Reproduced by shifting the boolean series
  once and reading the shifted value.
* `ta.crossover` / `ta.crossunder` are `pine_ta.pine_crossover` /
  `pine_crossunder`: `a > b and a[1] <= b[1]` (and the mirror), with na on either
  side yielding false, as Pine treats na comparisons.
* `ta.ema` is `pine_ta.pine_ema`, seeded with the first non-na observation and
  with na observations not advancing the recursion. TradingView does not publish
  its seeding rule; PINE_SEMANTICS.md 3.1 records this as a parity risk rather
  than a certified equivalence.
* `ta.valuewhen(longCondition, close, 1)` is the close on the second-most-recent
  occurrence of the condition, carried forward between occurrences; the port
  uses `pine_ta.pine_valuewhen` with occurrence 1. Its output is never read by
  the order logic.
* The `plot` calls and the two `plotshape` calls are display-only and place no
  condition.
* Both `if` blocks are independent (not `else if`) and are kept in the source's
  written order; the two conditions are mutually exclusive on the same bar, but
  their one-bar-lagged images can both be true on the same bar (a cross up
  immediately followed by a cross down), in which case the Long block runs
  first. The written order is preserved for exactly that case.
* The md reproduces the source verbatim (same code, no arguments table because
  the source declares no inputs); no md/source disagreement was found.
* Leverage, margin, liquidation, funding and the venue's contract-step rounding
  are not modelled; the chain verifier measures the rounding separately.
"""
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


class SMEmaMomentum_bf3b1f(PinePortBase, IStrategy):
    source_id = "SM_bf3b1f5b3fb76f00"
    source_file = "EMA动量交易策略-EMA-Momentum-Trading-Strategy.md"
    timeframe = "1d"
    can_short = True
    # The source declares no `input()`: the two EMA lengths are local variables.
    source_defaults: dict = {}
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    source_reproduce_stops = False
    source_fidelity_notes = [
        "shortEmaLength / longEmaLength (10 / 21) are local variables in the "
        "source, not inputs, so the port declares no source parameters and "
        "keeps both lengths as literals.",
        "longSignal / shortSignal (ta.valuewhen(..., close, 1)) are assigned and "
        "never read: the entries test longCondition[1] / shortCondition[1] "
        "directly. They are computed as columns and left unread, as in the "
        "source.",
        "`[1]` is a CHART-bar history reference: the entry fires on the bar "
        "AFTER the cross, and the engine then fills at the following bar's "
        "open. On the first bar the lagged condition is na, which Pine treats "
        "as false -- no order is placed there.",
        "ta.ema is pine_ta.pine_ema, seeded with the first non-na observation "
        "(an unpublished TradingView rule; PINE_SEMANTICS.md 3.1).",
        "ta.crossover / ta.crossunder treat na as false, as Pine does.",
        "The source has no strategy.close / strategy.exit and no stop or limit, "
        "so source_reproduce_stops is False and the only exit is the opposite "
        "entry reversing the position.",
        "Both `if` blocks are independent (not `else if`) and keep the source's "
        "written order; a cross up immediately followed by a cross down makes "
        "both lagged conditions true on one bar, and the Long block runs first.",
        "plot / plotshape are display-only and are not reproduced.",
        "The md reproduces the source verbatim; no md/source disagreement.",
        "Leverage, margin, liquidation, funding and contract-step rounding are "
        "not modelled.",
    ]
    _SHORT_EMA_LENGTH = 10
    _LONG_EMA_LENGTH = 21

    def pine_indicators(self, dataframe, params):
        close = dataframe["close"].astype(float)

        short_ema = ta.pine_ema(close, self._SHORT_EMA_LENGTH)
        long_ema = ta.pine_ema(close, self._LONG_EMA_LENGTH)
        dataframe["pine_short_ema"] = short_ema
        dataframe["pine_long_ema"] = long_ema

        # longCondition = ta.crossover(shortEma, longEma)
        # shortCondition = ta.crossunder(shortEma, longEma)
        long_condition = ta.pine_crossover(short_ema, long_ema)
        short_condition = ta.pine_crossunder(short_ema, long_ema)

        # longSignal = ta.valuewhen(longCondition, close, 1)  -- dead code, kept
        # shortSignal = ta.valuewhen(shortCondition, close, 1)
        dataframe["pine_long_signal"] = ta.pine_valuewhen(long_condition, close, 1)
        dataframe["pine_short_signal"] = ta.pine_valuewhen(short_condition, close, 1)

        dataframe["pine_long_condition"] = long_condition
        dataframe["pine_short_condition"] = short_condition
        # `longCondition[1]` / `shortCondition[1]`: the previous CHART bar's
        # value, na on the first bar and therefore false.
        dataframe["pine_long_condition_prev"] = (
            long_condition.shift(1).fillna(False).astype(bool)
        )
        dataframe["pine_short_condition_prev"] = (
            short_condition.shift(1).fillna(False).astype(bool)
        )
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "long_condition_prev": dataframe["pine_long_condition_prev"].to_numpy(dtype=bool),
            "short_condition_prev": dataframe["pine_short_condition_prev"].to_numpy(dtype=bool),
        }

    def pine_script(self, broker, i, ctx):
        # if (longCondition[1])
        #     strategy.entry("Long", strategy.long)
        if ctx["long_condition_prev"][i]:
            broker.entry("Long", "long")
        # if (shortCondition[1])
        #     strategy.entry("Short", strategy.short)
        if ctx["short_condition_prev"][i]:
            broker.entry("Short", "short")
