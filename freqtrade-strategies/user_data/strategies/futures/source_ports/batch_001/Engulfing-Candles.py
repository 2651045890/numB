"""Port of sources/SM_066ad9451779ee8d.pine (batch_001/Engulfing-Candles.md).

Pine v3. The file declares an INDICATOR -- `study("Engulfing Candles", overlay =
true)` -- and the two candle patterns it colours:

    bullishEngulfing = (open <= close[1]) and (open < open[1]) and (close > open[1])
    bearishEngulfing = (open >= close[1]) and (open > open[1]) and (close < open[1])

There is no author-written `strategy()` in this file: the only one present is
COMMENTED OUT (`//strategy("Engulfing Candles") //keep this commented out unless
backtesting`), as are the two entry/exit pairs under `// === EXECUTION ===`.
The executable trading behaviour is the block at the end of the file, which the
converter appended to the indicator:

    if bullishEngulfing
        strategy.entry("Enter Long", strategy.long)
    else if bearishEngulfing
        strategy.entry("Enter Short", strategy.short)

so the source's trades are ENTRIES ONLY. Rule 1 of this batch: the port
reproduces what the appended block actually does, not what the indicator's
author meant by the commented-out `//keep this commented out unless backtesting`
lines. Those commented lines place no order and are NOT restored.

The commented `strategy(..)` and the commented entry/exit pairs are read the
same way: commented code is not a declaration. `strategy()` therefore declares
nothing and Pine's documented defaults apply -- `default_qty_type=strategy.fixed`
with `default_qty_value=1`, `initial_capital=1000000`, commission 0%,
`pyramiding=0`, `process_orders_on_close=false`. The commented block's contents
are recorded in `source_fidelity_notes` so nothing is hidden by that reading.

Note the commented-out `strategy.entry("L", strategy.long, 25000, when=...)`
carried a literal `qty=25000` and a `// strategy.exit("exit", "L", profit = 1000,
loss = 50)` stop/target pair. Those are comments: no exit exists in this source,
which is why `source_reproduce_stops` is False and a position open at the end of
the window stays open.

FIDELITY:

* The appended block has NO exit of any kind. The only thing that can end a
  position is the opposite entry reversing it (`strategy.entry` nets against the
  open position, Pine semantics), so the port calls `broker.entry` and never
  `broker.close`.
* `bullishEngulfing` / `bearishEngulfing` are `na`-free booleans on every bar
  from bar 1; `open[1]` / `close[1]` are na on bar 0, and Pine compares na as
  false, so bar 0 can signal neither. The pandas comparison does the same.
* `strategy.entry` is called with no `qty`, so the engine sizes it from
  `default_qty_type` / `default_qty_value`.
* `alertcondition(...)` is an alert, not an order, and is not reproduced.
* `study(..., overlay=true)` and the title are display metadata.
* Leverage, margin, liquidation and funding are not modelled, and the venue's
  contract-step rounding is not modelled either (the chain verifier measures
  that separately rather than treating it as a signal difference).
"""
import pandas as pd

from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


class SMEngulfingCandles_066ad9(PinePortBase, IStrategy):
    source_id = "SM_066ad9451779ee8d"
    source_file = "Engulfing-Candles.md"
    timeframe = "1h"
    can_short = True
    # Pine evaluates the script from the first bar of the window.
    startup_candle_count = 0
    # No input() call exists anywhere in the source.
    source_defaults: dict = {}
    # `study()` is not a strategy declaration, and the file's only strategy()
    # call is commented out, so Pine's documented defaults apply. source:
    # `//strategy("Engulfing Candles")` (commented) -- see the docstring.
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    # The appended block places no stop, limit, target or trailing exit.
    source_reproduce_stops = False
    source_fidelity_notes = [
        "This is a converter-appended source: the file declares an indicator "
        "(`study(\"Engulfing Candles\", overlay=true)`) and the tool appended "
        "the block `if bullishEngulfing / strategy.entry(\"Enter Long\", "
        "strategy.long) else if bearishEngulfing / strategy.entry(\"Enter "
        "Short\", strategy.short)`. Pine v3 cannot call strategy.entry from a "
        "study, so the port reproduces the appended block's actual behaviour "
        "(entries only).",
        "NO exit exists in this source. The commented `// strategy.exit(\"exit\", "
        "\"L\", profit = 1000, loss = 50)` and `// strategy.exit(\"exit\", \"S\", "
        "profit = 1000, loss = 50)` lines are comments and place no order; "
        "`source_reproduce_stops` is False and a position open at the end of the "
        "window stays open.",
        "The `strategy()` declaration is commented out (`//strategy(\"Engulfing "
        "Candles\")`), so it declares nothing and Pine's documented defaults are "
        "used: fixed sizing, qty 1, initial capital 1000000, commission 0%, "
        "pyramiding 0, process_orders_on_close=false. Commented code is read the "
        "same way in both directions here -- the commented exit pair is not "
        "restored either.",
        "The commented `strategy.entry(\"L\", strategy.long, 25000, when = "
        "bullishEngulfing == 1 and window())` carried a literal qty of 25000 and "
        "a `window()` time filter; both are inside comments and place nothing.",
        "The appended entries pass no `qty`, so the engine sizes them from "
        "default_qty_type / default_qty_value.",
        "`alertcondition(bullishEngulfing, ...)` / `alertcondition("
        "bearishEngulfing, ...)` are alerts, not orders, and are not reproduced.",
        "`study()`'s title and `overlay=true` are display metadata.",
        "Leverage, margin, liquidation and funding are not modelled; the venue's "
        "contract-step rounding is not modelled either (the chain verifier "
        "measures that separately).",
    ]

    def pine_indicators(self, dataframe: pd.DataFrame, params: dict) -> pd.DataFrame:
        open_ = dataframe["open"]
        close = dataframe["close"]
        open_prev = open_.shift(1)
        close_prev = close.shift(1)

        # If current bar open is less than equal to the previous bar close AND
        # current bar open is less than previous bar open AND current bar close
        # is greater than previous bar open THEN True
        dataframe["pine_bullish_engulfing"] = (
            (open_ <= close_prev) & (open_ < open_prev) & (close > open_prev)
        ).fillna(False)
        # If current bar open is greater than equal to the previous bar close
        # AND current bar open is greater than previous bar open AND current bar
        # close is less than previous bar open THEN True
        dataframe["pine_bearish_engulfing"] = (
            (open_ >= close_prev) & (open_ > open_prev) & (close < open_prev)
        ).fillna(False)
        return dataframe

    def pine_context(self, dataframe: pd.DataFrame, params: dict) -> dict:
        return {
            "bullish_engulfing": dataframe["pine_bullish_engulfing"].to_numpy(),
            "bearish_engulfing": dataframe["pine_bearish_engulfing"].to_numpy(),
        }

    def pine_script(self, broker, i: int, ctx: dict) -> None:
        # if bullishEngulfing
        #     strategy.entry("Enter Long", strategy.long)
        # else if bearishEngulfing
        #     strategy.entry("Enter Short", strategy.short)
        if ctx["bullish_engulfing"][i]:
            broker.entry("Enter Long", "long")
        elif ctx["bearish_engulfing"][i]:
            broker.entry("Enter Short", "short")
