"""Port of sources/SM_72ad9cb5ac8c3be7.pine
(batch_001/Bullish-Bearish-Engulfing.md).

Pine v5 (`//@version=5`). The file is an INDICATOR that a conversion tool
appended an order block to -- the pattern PINE_SEMANTICS.md 1.17 records:

    indicator("Bullish & Bearish Engulfing", overlay=true)
    ...
    if bullEngulf
        strategy.entry("Enter Long", strategy.long)
    else if bearEngulf
        strategy.entry("Enter Short", strategy.short)

`strategy.entry` does not compile inside `indicator()`, so the trading
behaviour of this source is exactly what that appended block does: open a
position when the pattern fires, and NEVER close it. No exit call of any kind
exists in the file -- not even a commented-out one. The position is therefore
only ever ended by the opposite entry reversing it.

The pattern (verbatim from the source):

    engulfScale    = input.float(3.0, "Scale of engulfing candle")
    candlePipSize  = input.int(30, "Minimum Candle size in pips")
    engulfSizeBull = close - open
    prevCandleBull = open[1] - close[1]
    engulfSizeBear = open - close
    prevCandleBear = close[1] - open[1]
    isGradeABull = engulfSizeBull >= prevCandleBull * engulfScale
    isGradeABear = engulfSizeBear >= prevCandleBear * engulfScale
    isWorthBull  = engulfSizeBull >= candlePipSize / 10
    isWorthBear  = engulfSizeBear >= candlePipSize / 10
    bullEngulf = open[1] > close[1] and open < close and close >= open[1]
                 and isGradeABull and isWorthBull
    bearEngulf = open[1] < close[1] and open > close and close <= open[1]
                 and isGradeABear and isWorthBear

Note that the two conditions are NOT symmetric: each compares `close` against
`open[1]` (the previous body's open), not against the previous body's extreme,
and each grade test multiplies the PREVIOUS candle's body by `engulfScale`.
Both are reproduced as written.

No `strategy(...)` call exists, so the Pine defaults apply: `fixed` / 1
contract, initial capital 1000000, commission 0%, `pyramiding 0`,
`process_orders_on_close=false`.

FIDELITY:

* The source carries NO backtest-period header (the md has no `/*backtest`
  block at all), so `timeframe` falls back to the mandated "1h" default.
* There is no `? -1 : 0` integer-truthiness construct in this source; the two
  conditions are plain booleans, so the PINE_SEMANTICS.md 1.17 trap does not
  apply here.
* `candlePipSize / 10` is int-divided-by-int in the source. In Pine v5 integer
  division applies only when BOTH operands are const int; `candlePipSize` is
  bound to `input.int`, so the quotient is a float. Written as
  `float(candlePipSize) / 10.0`, i.e. 3.0 at the default 30. At a non-multiple
  of 10 the two readings would differ; the default is a multiple.
* Older bars are read with `[1]`; the first bar's `[1]` references are na and
  every comparison against na is false in Pine, which is what the NaN-aware
  comparisons here reproduce (the port never fires on bar 0).
* The commented-out `engulfShadow = high > high[1] and low < low[1]` guard and
  the commented-out `label.new` test block place no condition and are NOT
  restored.
* `plotshape` and `alertcondition` are display/alert-only and are not
  reproduced (PINE_SEMANTICS.md 二.7).
* There is no `security()` call, no `barstate.isrealtime` branch and no other
  future reference: the source does not repaint.
* Leverage, margin, liquidation and funding are not modelled, and neither is
  the venue's contract-step rounding of order quantities.
"""
import pandas as pd
from freqtrade.strategy import IStrategy

from pine_port_base import PinePortBase


class SMBullishBearishEngulfing_72ad9c(PinePortBase, IStrategy):
    source_id = "SM_72ad9cb5ac8c3be7"
    source_file = "Bullish-Bearish-Engulfing.md"
    timeframe = "1h"
    can_short = True
    source_defaults: dict = {"engulfScale": 3.0, "candlePipSize": 30}
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    source_reproduce_stops = False
    source_fidelity_notes = [
        "Converter-appended order block (PINE_SEMANTICS 1.17): the file "
        "declares indicator() and the trailing `if bullEngulf / else if "
        "bearEngulf` block is what the tool added. The port reproduces that "
        "block's actual behaviour -- enter on the pattern, never exit.",
        "NO exit call exists in the source, not even a commented-out one; "
        "source_reproduce_stops is False and a position is only ever ended by "
        "the opposite entry reversing it.",
        "No `? -1 : 0` construct is present, so the 1.17 integer-truthiness "
        "trap does not apply; both conditions are plain booleans and the "
        "if / else-if order (long first) is preserved.",
        "The source has NO backtest-period header, so timeframe falls back to "
        "the mandated 1h default.",
        "md/source check: the md's embedded PineScript block is line-for-line "
        "identical to sources/SM_72ad9cb5ac8c3be7.pine, and its two argument "
        "rows (3 / 30) match the two input defaults; the table renders "
        "input.float's 3.0 as `3` and omits minval/step/tooltip.",
        "`candlePipSize / 10` is written as float division: in Pine v5 an "
        "int/int quotient is an integer only when both operands are const "
        "int, and candlePipSize is bound to input.int, so the source's value "
        "is a float (3.0 at the default 30).",
        "The conditions are asymmetric as written -- both compare close "
        "against open[1], not against the previous body's extreme -- and are "
        "reproduced verbatim rather than 'corrected'.",
        "The commented-out engulfShadow guard and label.new test block place "
        "no condition and are not restored.",
        "plotshape / alertcondition are display and alert only, not "
        "reproduced (PINE_SEMANTICS 2.7).",
        "No security() call, no barstate.isrealtime branch, no repainting.",
        "On the validator's synthetic fixture this port runs but never signals "
        "(run_status ran_but_never_signalled_on_synthetic_data): isWorthBull / "
        "isWorthBear require a body of at least candlePipSize / 10 = 3.0 "
        "PRICE UNITS, while the fixture's prices sit near 100 with mean candle "
        "bodies of about 0.3, so that sub-condition is never met. This is the "
        "source's own threshold, not a porting choice -- on the high-priced "
        "instrument the pip test is calibrated for the same 3.0 threshold is "
        "routinely exceeded. Recorded, not adjusted: the threshold was NOT "
        "re-scaled to make the fixture produce trades.",
        "Leverage, margin, liquidation, funding and the venue's contract-step "
        "rounding of order quantities are not modelled.",
    ]

    def pine_indicators(self, dataframe, params):
        scale = float(params["engulfScale"])
        pip_size = float(params["candlePipSize"])

        open_ = dataframe["open"]
        close = dataframe["close"]
        prev_open = open_.shift(1)
        prev_close = close.shift(1)

        # Compare current and prev candle sizes.
        engulf_size_bull = close - open_
        prev_candle_bull = prev_open - prev_close
        engulf_size_bear = open_ - close
        prev_candle_bear = prev_close - prev_open

        is_grade_a_bull = engulf_size_bull >= (prev_candle_bull * scale)
        is_grade_a_bear = engulf_size_bear >= (prev_candle_bear * scale)

        # Check engulfing candle size. `candlePipSize / 10` -> float division.
        is_worth_bull = engulf_size_bull >= (pip_size / 10.0)
        is_worth_bear = engulf_size_bear >= (pip_size / 10.0)

        # Check the Bullish Engulfing.
        bull_engulf = (
            (prev_open > prev_close)
            & (open_ < close)
            & (close >= prev_open)
            & is_grade_a_bull
            & is_worth_bull
        )
        # Check the Bearish Engulfing.
        bear_engulf = (
            (prev_close > prev_open)
            & (open_ > close)
            & (close <= prev_open)
            & is_grade_a_bear
            & is_worth_bear
        )

        dataframe["pine_bull_engulf"] = bull_engulf
        dataframe["pine_bear_engulf"] = bear_engulf
        dataframe["pine_long_condition"] = bull_engulf
        dataframe["pine_short_condition"] = bear_engulf
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "long_condition": dataframe["pine_long_condition"].to_numpy(),
            "short_condition": dataframe["pine_short_condition"].to_numpy(),
        }

    def pine_script(self, broker, i, ctx):
        # if bullEngulf
        #     strategy.entry("Enter Long", strategy.long)
        # else if bearEngulf
        #     strategy.entry("Enter Short", strategy.short)
        if ctx["long_condition"][i]:
            broker.entry("Enter Long", "long")
        elif ctx["short_condition"][i]:
            broker.entry("Enter Short", "short")
