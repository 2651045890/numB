"""Port of sources/SM_39af3bea425e2178.pine (batch_001/HODL-LINE.md).

AstrideUnicorn's "Asymmetrical Trend Filter aka HODL Line" (`//@version=5`,
`indicator("HODL LINE", overlay=true)`) is an INDICATOR: the HODL line is the
midpoint of the length-bar highest/lowest close, divided by 2 + asymmetry, so
that the line sits a fixed fraction below the top of the range; crossings of
price (or of its Hull moving average) with that line are bull/bear signals. A
converter appended an order block at the end of the file -- `indicator()` cannot
host `strategy.entry`, so the block is the whole of the trading behaviour:

    HODL_line = (ta.highest(close, length) + ta.lowest(close, length)) / (2.0 + 0.05)
    smoothed_price = ta.hma(close, 50)
    price_model = use_smoothing ? smoothed_price : close
    crossing_condition_bull = ta.crossover(price_model, HODL_line)
    crossing_condition_bear = ta.crossunder(price_model, HODL_line)

    if crossing_condition_bull
        strategy.entry("Enter Long", strategy.long)
    else if crossing_condition_bear
        strategy.entry("Enter Short", strategy.short)

There is NO exit anywhere in the file -- not live and not commented out -- so a
position is closed only by an opposite entry reversing it.

FIDELITY:

* `length` is declared as `300` and then REASSIGNED from the `sensitivity`
  input, which is a dropdown with four options; the default "Hold Short Term"
  therefore leaves `length` at 100, not 300. The mapping is reproduced
  (Super Sensitive 50 / Hold Short Term 100 / Hold Medium Term 300 / Hold Long
  Term 500) with the declared 300 as the fallback for an out-of-range value, so
  the declared initial value is not lost.
* `asymmetry = 0.05` is NOT an input: the source's own
  `input.float(defval=0.05, ...)` is commented out on that line, so 0.05 is a
  literal in the source and stays a literal here. It is deliberately not
  exposed as a parameter.
* `ta.hma(close, 50)` is `ta.wma(2 * ta.wma(src, length/2) - ta.wma(src,
  length), math.round(math.sqrt(length)))`. pine_ta has no `hma`, so the port
  composes it from pine_ta.pine_wma and documents the parts: 50/2 = 25 exactly,
  and math.round(math.sqrt(50)) = round(7.0711) = 7 (so the round-vs-truncate
  ambiguity in Pine's implicit float->int cast does not arise at this length).
  `wma` needs a full window, so the HMA is na until bar 55.
* `ta.highest` / `ta.lowest` are Pine's rolling extremes: na until the window
  is full, and na anywhere in the window propagates (PINE_SEMANTICS.md
  section 3.2), which is what pine_ta.pine_highest / pine_lowest do. With
  length = 100 the HODL line is na for the first 99 bars.
* The bull/bear crosses are pine_ta.pine_crossover / pine_crossunder, whose na
  handling matches Pine's "a comparison against na is false" reading; during
  the warm-up neither can fire.
* `plot` / `bgcolor` and the two `plotshape` circle markers are display only
  and are not reproduced; none of them reaches an order.
* No `strategy()` call exists anywhere, so every trade property is Pine's own
  default: `default_qty_type` fixed, 1 contract, 1000000 initial capital, 0%
  commission, pyramiding 0, `process_orders_on_close` false.
* `/*backtest` declares `period: 5m` on Futures_Binance BTC_USDT, so timeframe
  is "5m"; `basePeriod: 1m` is the FMZ backtester's fill granularity.
* Leverage, margin, liquidation, funding and the venue's contract-step rounding
  are not modelled.
"""
import math

from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase

# The source declares `length = 300` and then reassigns it from the
# `sensitivity` dropdown; the dropdown covers every option, so the declared 300
# survives only as the fallback for a value outside the list.
SENSITIVITY_LENGTHS = {
    "Super Sensitive": 50,
    "Hold Short Term": 100,
    "Hold Medium Term": 300,
    "Hold Long Term": 500,
}
DECLARED_LENGTH = 300


def _pine_int(value: float) -> int:
    """Pine's implicit float -> int cast: round half away from zero."""
    return int(math.floor(abs(value) + 0.5)) * (1 if value >= 0 else -1)


def _hma(source, length):
    """`ta.hma(source, length)`, composed from pine_ta.pine_wma.

        ta.wma(2 * ta.wma(source, length / 2) - ta.wma(source, length),
               math.round(math.sqrt(length)))
    """
    length = int(length)
    inner = 2.0 * ta.pine_wma(source, _pine_int(length / 2)) - ta.pine_wma(
        source, length
    )
    return ta.pine_wma(inner, _pine_int(math.sqrt(length)))


class SMHodlLine_39af3b(PinePortBase, IStrategy):
    source_id = "SM_39af3bea425e2178"
    source_file = "HODL-LINE.md"
    timeframe = "5m"
    can_short = True
    source_defaults: dict = {
        "sensitivity": "Hold Short Term",
        "use_smoothing": True,
    }
    # No strategy() call exists, so Pine's documented defaults apply.
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    # No exit exists in the source at all.
    source_reproduce_stops = False
    source_mintick = 0.1
    source_fidelity_notes = [
        "Converter-appended order block: the file is `indicator(\"HODL LINE\")` "
        "(Pine v5) and appends `if crossing_condition_bull -> "
        "strategy.entry(\"Enter Long\", long)` / `else if "
        "crossing_condition_bear -> strategy.entry(\"Enter Short\", short)`. "
        "That block is the whole trading behaviour.",
        "The source has no exit -- neither called nor commented out -- so "
        "source_reproduce_stops is False and a position is closed only by an "
        "opposite entry reversing it.",
        "`length` is declared 300 and then reassigned from the sensitivity "
        "dropdown, so the default 'Hold Short Term' leaves it at 100. The "
        "mapping (50/100/300/500) is reproduced with the declared 300 as the "
        "fallback for a value outside the list.",
        "`asymmetry = 0.05` is a literal: the source's own input.float on that "
        "line is commented out. It is kept a literal and not exposed as a "
        "parameter.",
        "pine_ta has no hma, so ta.hma(close, 50) is composed from "
        "pine_ta.pine_wma: wma(2*wma(src, 25) - wma(src, 50), round(sqrt(50))) "
        "= wma(..., 7). 50/2 and sqrt(50) are exact enough that Pine's "
        "round-vs-truncate float->int cast cannot change the result here.",
        "ta.highest / ta.lowest are rolling extremes that are na until the "
        "window is full and propagate na through it (PINE_SEMANTICS section "
        "3.2); the HODL line is therefore na for the first 99 bars and the HMA "
        "for the first 55, so no signal can fire before bar 99.",
        "plot / bgcolor / plotshape are display only and are not reproduced.",
        "No strategy() call exists, so all trade properties are Pine's "
        "documented defaults, including default_qty_value = 1 CONTRACT (fixed).",
        "Venue contract-step rounding, leverage, margin, liquidation and funding "
        "are not modelled.",
    ]

    def pine_indicators(self, dataframe, params):
        close = dataframe["close"]
        asymmetry = 0.05
        sensitivity = str(params["sensitivity"])
        length = SENSITIVITY_LENGTHS.get(sensitivity, DECLARED_LENGTH)

        # HODL_line = (ta.highest(close, length) + ta.lowest(close, length))
        #             / (2.0 + asymmetry)
        hodl_line = (ta.pine_highest(close, length) + ta.pine_lowest(close, length)) / (
            2.0 + asymmetry
        )

        # smoothed_price = ta.hma(close, 50)
        smoothed_price = _hma(close, 50)

        # price_model = use_smoothing ? smoothed_price : close
        if bool(params["use_smoothing"]):
            price_model = smoothed_price
        else:
            price_model = close

        # crossing_condition_bull / bear
        crossing_bull = ta.pine_crossover(price_model, hodl_line)
        crossing_bear = ta.pine_crossunder(price_model, hodl_line)

        dataframe["pine_hodl_line"] = hodl_line
        dataframe["pine_smoothed_price"] = smoothed_price
        dataframe["pine_crossing_bull"] = crossing_bull
        dataframe["pine_crossing_bear"] = crossing_bear
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "crossing_bull": dataframe["pine_crossing_bull"].to_numpy(dtype=bool),
            "crossing_bear": dataframe["pine_crossing_bear"].to_numpy(dtype=bool),
        }

    def pine_script(self, broker, i, ctx):
        # if crossing_condition_bull
        #     strategy.entry("Enter Long", strategy.long)
        # else if crossing_condition_bear
        #     strategy.entry("Enter Short", strategy.short)
        if ctx["crossing_bull"][i]:
            broker.entry("Enter Long", "long")
        elif ctx["crossing_bear"][i]:
            broker.entry("Enter Short", "short")
