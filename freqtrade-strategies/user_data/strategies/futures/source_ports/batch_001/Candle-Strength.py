"""Port of sources/SM_a40394ca58ce25ef.pine (batch_001/Candle-Strength.md).

Pine v5 (`//@version=5`, `indicator(...)`), 4h. Trade_by_DB's "Candle Strength"
-- a candle-colour indicator. The file declares an INDICATOR, not a strategy, and
a conversion tool has appended an order block after it (PINE_SEMANTICS.md 1.17):

    if (close>open)
        ...
        strategy.entry("Enter Long", strategy.long)
    else if (open > close)
        ...
        strategy.entry("Enter Short", strategy.short)

`strategy.entry` cannot compile inside `indicator()`, so the "original strategy"
IS the indicator plus that block, and its trading behaviour is the simplest in
the corpus: open a long on an up candle, open a short on a down candle, and NEVER
exit. There is no `strategy.close`, no `strategy.exit`, not even a commented-out
exit line -- the block is the entire trading behaviour.

The indicator itself, transcribed (it is display-only and gates nothing):

    roundn(x, n) =>
        mult = 1
        if n != 0
            for i = 1 to math.abs(n) by 1
                mult *= 10
        n >= 0 ? math.round(x * mult) / mult : math.round(x / mult) * mult

    green = roundn(((close-low)/(high-low) * 100), 2)
    red   = roundn(((high-close)/(high-low) * 100), 2)

`green` and `red` are the up/down share of the candle's range in percent, and the
source uses them ONLY as label text (`str.tostring(green) + " %"`). They enter no
condition, so they are reproduced as columns for fidelity and change nothing
about the orders -- the entry test reads `close` and `open` alone.

INDENTATION QUIRK (read, not "corrected"): the appended block is unevenly
indented -- the long entry sits at 5 spaces, the short entry at 1 space, both
under a branch header at column 0. The converter's template writes one entry per
branch; the port reads each entry as the body of its own branch (long under
`close > open`, short under `open > close`) and preserves that if / else-if
order. Reading the 1-space line as a top-level statement instead would fire it on
every bar rather than only on down candles.

A doji (`close == open`) satisfies neither branch, so no order is placed on it.

FIDELITY -- translation choices and source/md mismatches:

1. The md contains NO prose at all: no strategy description, no argument table,
   no logic, no risk notes -- just the name, the author, the source listing and
   the fmz.com detail link. It neither confirms nor contradicts the appended
   order block, so the block is read from the source alone.
2. There is no `input()` call anywhere in the source, so `source_defaults` is
   empty and every literal in the formulas is the source's own.
3. `math.round` is Pine's half-AWAY-FROM-ZERO rounding, not banker's rounding;
   `pine_ta.pine_round` implements that, and the local `_pine_roundn` mirrors the
   source's helper including its `n < 0` branch (which the source never reaches,
   since both calls pass n = 2).
4. `(high - low)` is the division's denominator: on a zero-range bar the source's
   float division is na in Pine, and the port masks the resulting inf/NaN to na
   for the same reason. Neither value gates an order, so this cannot move a trade.
5. No `strategy()` call exists, so every strategy property is Pine's documented
   default: `fixed` sizing of 1 contract, initial capital 1000000, commission 0%,
   `pyramiding = 0`, `process_orders_on_close = false`. With `pyramiding = 0` an
   entry in the direction already held is ignored by the engine, so the position
   only ever flips.
6. `label.new` / `label.set_yloc` / `str.tostring` / `bar_index` and the `overlay`
   flag are display-only and are not reproduced.
7. The `/*backtest` header declares `period: 4h` on Futures_Binance BTC_USDT,
   hence `timeframe = "4h"`; its `basePeriod: 15m` is the FMZ backtester's own
   intrabar fill granularity, not the strategy's period.
8. No `request.security()`, no `barstate.isrealtime` branch, no repainting: the
   entry test reads only the current bar. Note the source's own reputation --
   "Candle Strength" on the current bar is known at that bar's close, and the
   engine fills on the next open, which is the modelled Pine timing.
9. Leverage, margin, liquidation, funding and the venue's contract-step rounding
   of order quantities are not modelled (PINE_SEMANTICS.md section 2).
"""
import numpy as np

from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


def _pine_roundn(value, n):
    """The source's own `roundn(x, n)` helper, transcribed line for line.

    `mult` starts at 1 and is multiplied by 10 `math.abs(n)` times when n is
    non-zero; the return is `math.round(x * mult) / mult` for n >= 0 and
    `math.round(x / mult) * mult` otherwise. Pine's `math.round` is half away
    from zero, which is `pine_ta.pine_round`.
    """
    n = int(n)
    mult = 1
    if n != 0:
        for _ in range(abs(n)):
            mult *= 10
    if n >= 0:
        return ta.pine_round(value * mult) / mult
    return ta.pine_round(value / mult) * mult


class SMCandleStrength_a40394(PinePortBase, IStrategy):
    source_id = "SM_a40394ca58ce25ef"
    source_file = "Candle-Strength.md"
    timeframe = "4h"
    # The appended block has both arms: entry("Enter Long") on an up candle and
    # entry("Enter Short") on a down candle.
    can_short = True
    # The source declares no input() at all.
    source_defaults: dict = {}
    # No `strategy()` call exists in the source, so Pine's documented defaults
    # apply: `fixed` / 1 contract, initial capital 1000000, commission 0%,
    # pyramiding 0, process_orders_on_close = false.
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    # No stop / limit / trail leg exists: the file has no exit call of any kind.
    source_reproduce_stops = False
    source_fidelity_notes = [
        "The source declares indicator(), not strategy(): the trailing "
        "if (close>open) / else if (open > close) entry pair is the conversion "
        "tool's appended order block (PINE_SEMANTICS.md 1.17). `strategy.entry` "
        "cannot compile inside indicator(), so the original strategy IS the "
        "indicator plus that block -- read from the source, not from the "
        "author's intent.",
        "NO EXIT CALL EXISTS: no strategy.close, no strategy.exit, not even a "
        "commented-out one. source_reproduce_stops is False; a position is only "
        "ended by the opposite entry reversing it, and one still open at the end "
        "of the window stays open.",
        "No `? -1 : 0` construct is present, so the integer-truthiness trap of "
        "PINE_SEMANTICS.md 1.17 does not apply. The if / else-if order is "
        "preserved in pine_script.",
        "INDENTATION QUIRK: the appended block indents the long entry at 5 "
        "spaces and the short entry at 1 space under a column-0 branch header. "
        "Each entry is read as the body of its own branch, matching the "
        "converter's one-entry-per-branch template; reading the 1-space line as "
        "top-level would fire the short on every bar.",
        "A doji (close == open) satisfies neither branch, so no order is placed "
        "on it.",
        "green and red (the candle's up/down share of its range) are computed "
        "exactly as the source does but are used ONLY as label text there; they "
        "gate no order. They are kept as columns for fidelity, and the entry "
        "test reads close and open alone.",
        "roundn is the source's own helper, transcribed including the n < 0 "
        "branch (never reached: both calls pass n = 2). math.round is half away "
        "from zero, which pine_ta.pine_round implements -- NOT Python's banker's "
        "rounding.",
        "(high - low) is the divisor; a zero-range bar makes it a float division "
        "by zero, which is na in Pine. The port masks the resulting inf/NaN to "
        "na for the same reason. Neither value gates an order.",
        "The md carries NO prose description and no argument table -- only the "
        "name, the author, the source listing and the fmz.com link -- so it "
        "neither confirms nor contradicts the appended order block.",
        "The source declares no input() at all; source_defaults is empty and "
        "every literal in the formulas is the source's own.",
        "No `strategy()` call exists, so the sizing is Pine's default fixed / 1 "
        "contract against the default initial capital 1000000 -- notably NOT a "
        "percentage of equity.",
        "label.new / label.set_yloc / str.tostring / bar_index / overlay are "
        "display-only and are not reproduced.",
        "/*backtest declares period: 4h on Futures_Binance BTC_USDT; "
        "basePeriod: 15m is the FMZ backtester's fill granularity, not the "
        "strategy's period.",
        "No security() call, no barstate.isrealtime branch, no repainting: the "
        "entry test reads only the current bar, and the engine fills on the next "
        "open (Pine's modelled timing).",
        "Leverage, margin, liquidation, funding and the venue's contract-step "
        "rounding are not modelled (PINE_SEMANTICS.md section 2).",
    ]

    def pine_indicators(self, dataframe, params):
        open_ = dataframe["open"]
        high = dataframe["high"]
        low = dataframe["low"]
        close = dataframe["close"]

        candle_range = high - low
        with np.errstate(divide="ignore", invalid="ignore"):
            # green = roundn(((close-low)/(high-low) * 100), 2)
            green = _pine_roundn((close - low) / candle_range * 100.0, 2)
            # red = roundn(((high-close)/(high-low) * 100), 2)
            red = _pine_roundn((high - close) / candle_range * 100.0, 2)
        # Pine's float division by zero is na, not inf.
        green = green.where(np.isfinite(green))
        red = red.where(np.isfinite(red))

        # if (close>open) ... else if (open > close) ...
        up_candle = close > open_
        down_candle = open_ > close

        dataframe["pine_green"] = green
        dataframe["pine_red"] = red
        dataframe["pine_up_candle"] = up_candle
        dataframe["pine_down_candle"] = down_candle
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "up_candle": dataframe["pine_up_candle"].to_numpy(dtype=bool),
            "down_candle": dataframe["pine_down_candle"].to_numpy(dtype=bool),
        }

    def pine_script(self, broker, i, ctx):
        # if (close>open)
        #     ...
        #     strategy.entry("Enter Long", strategy.long)
        # else if (open > close)
        #     ...
        #  strategy.entry("Enter Short", strategy.short)
        if ctx["up_candle"][i]:
            broker.entry("Enter Long", "long")
        elif ctx["down_candle"][i]:
            broker.entry("Enter Short", "short")
