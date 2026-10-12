"""Port of sources/SM_a1f5803a4b4329cd.pine (batch_001/Ks-Reversal-Indicator-I.md).

Pine v5 (`//@version = 5`, `indicator(...)`), 30m. Sofien-Kaabar's "K's Reversal
Indicator I": the MACD line cross against its signal line, gated by a 100-period
Bollinger band. The file declares an INDICATOR, not a strategy, and a conversion
tool has appended an order block after it (PINE_SEMANTICS.md 1.17):

    if buy_signal
        strategy.entry("Enter Long", strategy.long)
    else if sell_signal
        strategy.entry("Enter Short", strategy.short)

`strategy.entry` cannot compile inside `indicator()`, so the "original strategy"
IS the indicator plus that appended block, and its trading behaviour is "enter on
the signal, and NEVER exit". The file has no `strategy.close`, no
`strategy.exit`, not even a commented-out exit line -- which the md itself
concedes ("There are no clear exit rules ... it does not show when to exit the
positions"). A position is only ever ended by the opposite entry reversing it.

The indicator, transcribed:

    macd_line   = ta.ema(close, 12) - ta.ema(close, 26)
    signal_line = ta.ema(macd_line, 9)
    lower_boll  = ta.sma(close, 100) - (2 * ta.stdev(close, 100))
    upper_boll  = ta.sma(close, 100) + (2 * ta.stdev(close, 100))
    mid_line    = ta.sma(close, 100)
    buy_signal  = math.min(open[1], close[1]) <= lower_boll[1]
                  and math.max(open[1], close[1]) <= mid_line
                  and macd_line[1] > signal_line[1]
                  and macd_line[2] < signal_line[2]
    sell_signal = math.max(open[1], close[1]) >= upper_boll[1]
                  and math.min(open[1], close[1]) >= mid_line
                  and macd_line[1] < signal_line[1]
                  and macd_line[2] > signal_line[2]

`mid_line` is the SAME sma as the bands' basis and the source writes it out a
second time; the port keeps one computation and uses it for both.

THE `[1]`/`[2]` OFFSETS ARE ASYMMETRIC IN THE SOURCE and are kept verbatim: the
band levels and the previous candle's body are read at `[1]` (the previous bar's
open/close against the previous bar's bands), `mid_line` is read at the CURRENT
bar (no offset), and the MACD cross is `macd_line[1] > signal_line[1] and
macd_line[2] < signal_line[2]` -- the cross happened between bars t-2 and t-1.
"Normalising" the mid_line offset to `[1]` would change which bars signal.

`strategy()` is never declared, so every strategy property is Pine's documented
default: `fixed` sizing of 1 contract, initial capital 1000000, commission 0%,
`pyramiding = 0`, `process_orders_on_close = false`.

FIDELITY -- translation choices and source/md mismatches:

1. MD/SOURCE MISMATCH: the md's bullet describes the buy signal as "the current
   market price is below the 100-period lower Bollinger band". The source tests
   the PREVIOUS bar's `math.min(open[1], close[1])` against `lower_boll[1]` --
   a different bar, and the body's extreme rather than "market price".
2. MD/SOURCE MISMATCH: the md never mentions the `mid_line` clause at all
   (`math.max(open[1], close[1]) <= mid_line` for the buy, the mirror for the
   sell), which is a conjunct in the source and materially narrows the signals.
3. MD/SOURCE MISMATCH: the md says "the MACD value must be above its signal
   line. At the same time, the previous MACD value must be below its previous
   signal line"; the source compares `[1]` (above) against `[2]` (below), i.e.
   two bars back from the current one, not "current" and "previous".
4. MD/SOURCE MISMATCH: the md's argument table lists "Bollinger Lookback" 100
   and "Multiplier" 2 exactly as the source declares them; no numeric default
   differs between the two.
5. `ta.stdev` is the POPULATION standard deviation (ddof = 0) --
   `pine_ta.pine_stdev` implements exactly that. A sample stdev would widen both
   bands slightly and change the signal bars.
6. `ta.sma(close, 100)` returns na until 100 bars have elapsed and propagates na
   inside the window (PINE_SEMANTICS.md 3.2); `ta.ema` is pine_ta's modelled
   seeding (first non-na observation, PINE_SEMANTICS.md 3.1) -- TradingView does
   not publish the exact EMA seed rule, so the early MACD values are a modelled
   choice. With the default lengths the first possible signal is after bar 101.
7. `math.min(open[1], close[1])` / `math.max(open[1], close[1])` are the
   previous bar's candle body extremes, not `low[1]` / `high[1]`.
8. An na operand makes a Pine `and` falsy, and a pandas comparison against NaN is
   likewise False, so the warm-up bars evaluate to False on both sides without
   special-casing.
9. There is no exit call of any kind, so `source_reproduce_stops` is False and a
   position open at the end of the window stays open.
10. `plot` / `overlay` / the `indicator` title are display-only and are not
    reproduced; the series the signals read are kept as columns.
11. The `/*backtest` header declares `period: 30m` on Futures_Binance BTC_USDT,
    hence `timeframe = "30m"`; its `basePeriod: 15m` is the FMZ backtester's own
    intrabar fill granularity, not the strategy's period.
12. No `request.security()`, no `barstate.isrealtime` branch, no repainting: the
    signals read only the current and earlier bars.
13. Leverage, margin, liquidation, funding and the venue's contract-step
    rounding of order quantities are not modelled (PINE_SEMANTICS.md section 2).
"""
import pandas as pd

from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


class SMKsReversalIndicatorI_a1f580(PinePortBase, IStrategy):
    source_id = "SM_a1f5803a4b4329cd"
    source_file = "Ks-Reversal-Indicator-I.md"
    timeframe = "30m"
    # The appended block has both arms: entry("Enter Long") and
    # entry("Enter Short").
    can_short = True
    source_defaults: dict = {
        # fast = input(defval = 12, title = 'Fast')
        "fast": 12,
        # slow = input(defval = 26, title = 'Slow')
        "slow": 26,
        # signal = input(defval = 9, title = 'Signal')
        "signal": 9,
        # length = input(defval = 100, title = 'Bollinger Lookback')
        "length": 100,
        # multiplier = input(defval = 2, title = 'Multiplier')
        "multiplier": 2,
    }
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
        "buy_signal / sell_signal entry pair is the conversion tool's appended "
        "order block (PINE_SEMANTICS.md 1.17). `strategy.entry` cannot compile "
        "inside indicator(), so the original strategy IS the indicator plus that "
        "block -- read from the source, not from the author's intent.",
        "NO EXIT CALL EXISTS -- no strategy.close, no strategy.exit, not even a "
        "commented-out one. The md says the same thing in prose ('there are no "
        "clear exit rules'). source_reproduce_stops is False and a position is "
        "only ended by the opposite entry reversing it.",
        "No `? -1 : 0` construct is present, so the integer-truthiness trap of "
        "PINE_SEMANTICS.md 1.17 does not apply. The source's if / else-if order "
        "(buy first) is preserved in pine_script.",
        "The [1] / [2] offsets are asymmetric in the source and are kept "
        "verbatim: bands and the previous candle's body at [1], mid_line at the "
        "CURRENT bar, and the MACD cross as macd_line[1] > signal_line[1] with "
        "macd_line[2] < signal_line[2]. 'Normalising' mid_line to [1] would "
        "move the signal bars.",
        "MD/SOURCE MISMATCH: the md describes the buy trigger as 'the current "
        "market price is below the 100-period lower Bollinger band'; the source "
        "tests math.min(open[1], close[1]) against lower_boll[1] -- the previous "
        "bar's body low, not the current price.",
        "MD/SOURCE MISMATCH: the md never mentions the mid_line conjunct "
        "(math.max(open[1], close[1]) <= mid_line on the buy side), which the "
        "source applies and which narrows the signals.",
        "MD/SOURCE MISMATCH: the md says the MACD 'must be above its signal "
        "line' while 'the previous MACD value must be below its previous signal "
        "line'; the source compares bar [1] against bar [2], not current "
        "against previous.",
        "ta.stdev is the population standard deviation (ddof=0), as "
        "pine_ta.pine_stdev computes it; a sample stdev would widen both bands.",
        "ta.sma returns na until its window is full and propagates na inside it "
        "(PINE_SEMANTICS.md 3.2), so with length=100 the first possible signal "
        "is after bar 101.",
        "ta.ema is pine_ta's modelled seeding (first non-na observation, "
        "PINE_SEMANTICS.md 3.1); TradingView's exact EMA seed rule is "
        "unpublished, so the early MACD values are a modelled choice.",
        "`signal = 9` is the EMA length for the MACD signal line, not a signal "
        "flag; math.min/math.max(open[1], close[1]) are the previous bar's body "
        "extremes, not low[1]/high[1].",
        "plot / overlay / the indicator title are display-only and are not "
        "reproduced; the series the signals read are kept as columns.",
        "/*backtest declares period: 30m on Futures_Binance BTC_USDT; "
        "basePeriod: 15m is the FMZ backtester's fill granularity, not the "
        "strategy's period.",
        "No security() call, no barstate.isrealtime branch, no repainting.",
        "Leverage, margin, liquidation, funding and the venue's contract-step "
        "rounding are not modelled (PINE_SEMANTICS.md section 2).",
    ]

    def pine_indicators(self, dataframe, params):
        open_ = dataframe["open"]
        close = dataframe["close"]

        # macd_line = ta.ema(close, fast) - ta.ema(close, slow)
        fast = int(params["fast"])
        slow = int(params["slow"])
        macd_line = ta.pine_ema(close, fast) - ta.pine_ema(close, slow)
        # signal_line = ta.ema(macd_line, signal)
        signal_line = ta.pine_ema(macd_line, int(params["signal"]))

        # lower_boll = ta.sma(close, length) - (multiplier * ta.stdev(close, length))
        # upper_boll = ta.sma(close, length) + (multiplier * ta.stdev(close, length))
        # mid_line   = ta.sma(close, length)          <- the same sma, written twice
        length = int(params["length"])
        multiplier = float(params["multiplier"])
        basis = ta.pine_sma(close, length)
        deviation = multiplier * ta.pine_stdev(close, length)
        lower_boll = basis - deviation
        upper_boll = basis + deviation
        mid_line = basis

        # math.min(open[1], close[1]) / math.max(open[1], close[1]): the
        # PREVIOUS bar's candle body extremes.
        body_low = pd.concat([open_, close], axis=1).min(axis=1)
        body_high = pd.concat([open_, close], axis=1).max(axis=1)
        previous_body_low = body_low.shift(1)
        previous_body_high = body_high.shift(1)

        # buy_signal = math.min(open[1], close[1]) <= lower_boll[1]
        #              and math.max(open[1], close[1]) <= mid_line
        #              and macd_line[1] > signal_line[1]
        #              and macd_line[2] < signal_line[2]
        buy_signal = (
            (previous_body_low <= lower_boll.shift(1))
            & (previous_body_high <= mid_line)
            & (macd_line.shift(1) > signal_line.shift(1))
            & (macd_line.shift(2) < signal_line.shift(2))
        )
        # sell_signal = math.max(open[1], close[1]) >= upper_boll[1]
        #               and math.min(open[1], close[1]) >= mid_line
        #               and macd_line[1] < signal_line[1]
        #               and macd_line[2] > signal_line[2]
        sell_signal = (
            (previous_body_high >= upper_boll.shift(1))
            & (previous_body_low >= mid_line)
            & (macd_line.shift(1) < signal_line.shift(1))
            & (macd_line.shift(2) > signal_line.shift(2))
        )

        dataframe["pine_macd_line"] = macd_line
        dataframe["pine_signal_line"] = signal_line
        dataframe["pine_lower_boll"] = lower_boll
        dataframe["pine_upper_boll"] = upper_boll
        dataframe["pine_mid_line"] = mid_line
        dataframe["pine_buy_signal"] = buy_signal.fillna(False).astype(bool)
        dataframe["pine_sell_signal"] = sell_signal.fillna(False).astype(bool)
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "buy_signal": dataframe["pine_buy_signal"].to_numpy(dtype=bool),
            "sell_signal": dataframe["pine_sell_signal"].to_numpy(dtype=bool),
        }

    def pine_script(self, broker, i, ctx):
        # if buy_signal
        #     strategy.entry("Enter Long", strategy.long)
        # else if sell_signal
        #     strategy.entry("Enter Short", strategy.short)
        if ctx["buy_signal"][i]:
            broker.entry("Enter Long", "long")
        elif ctx["sell_signal"][i]:
            broker.entry("Enter Short", "short")
