"""Port of sources/SM_2ecf3b6936e4a4c1.pine
(batch_001/Inverted-Hammer-Extended-Options.md).

Pine v5, long only, 4h. The file declares an INDICATOR, not a strategy:

    indicator("Inverted Hammer", overlay=true)

and a converter has appended an order block after it (PINE_SEMANTICS.md 1.17):

    invertedHammer = body_qualify and upper_wick_qualify and lower_wick_qualify ? low : na
    if invertedHammer
        strategy.entry("buy", strategy.long)

`strategy.entry` cannot compile inside a v5 `indicator()`, so the "original
strategy" is the indicator plus that appended block, and its trade behaviour is
exactly one line: open a long when the hammer qualifies. THERE IS NO EXIT CALL
ANYWHERE in the file -- not an active one and not a commented-out one -- so a
position opened here is never closed by the source.

`strategy()` is not declared at all, so every strategy property is Pine's
documented default: `strategy.fixed` sizing of 1 contract, initial capital
1000000, commission 0%, `pyramiding = 0`, `process_orders_on_close = false`.
With `pyramiding = 0` the first fill is the only fill the source can ever make:
every later signal is ignored outright, and the engine reports one open trade
that is still open at the end of the window.

THE SIGNAL IS A FLOAT, NOT A BOOL. `invertedHammer` is `low` (or `na`), and the
converter tests it as a bare condition. Pine and Python both treat a non-zero
number as true, and `low` is never 0, so "true" here is exactly "not na"; the
port keeps the float form and never rewrites it into an equality test, the same
discipline PINE_SEMANTICS.md 1.17 records for the `? -1 : 0` variant.

FIDELITY -- translation choices and source/md mismatches:

1. The md's argument table renders `v_input_float_3` ("Max Lower Wick X Body")
   as `true`. That is FMZ's bool column showing the source's `input.float(1)`.
   The source's real default, 1.0, is declared here.
2. The md has no prose section at all (no strategy description, no logic, no
   risks) -- the file is name + argument table + source listing. Nothing in the
   md contradicts the source, and nothing in it documents the appended order
   block, so the block is read from the source alone.
3. `ta.ema` is pine_ta's modelled choice (seed = first non-na observation),
   which PINE_SEMANTICS.md 3.1 records as an unresolved parity risk.
4. `plot(...)` is display-only and is not reproduced; the plotted series is kept
   as a column instead, because the entry test reads that same value.
5. `high > high[1]` is false on the first bar (na compares false in Pine), and
   `up_only` / `broke_high` default to false, so with the source's defaults only
   the wick and body ratios gate the signal.
6. `body > body_min / 100 * (high - low)` uses the bar's own range, not the body.
7. The `/*backtest` header declares `period: 4h` on Futures_Binance BTC_USDT,
   hence `timeframe = "4h"`; its `basePeriod: 15m` is the FMZ backtester's
   intrabar fill granularity, not the strategy's period.
8. Leverage, margin, liquidation, funding and the venue's contract-step rounding
   are not modelled; the chain verifier measures the step rounding separately.
9. `ta.ema` needs `downtrend_threshold` bars of history and the wick/body ratios
   use the current bar only, so the first signal needs 10 bars (with the default
   threshold); no signal can fire before then.
"""
import pandas as pd

from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


class SMInvertedHammerExtendedOptions_2ecf3b(PinePortBase, IStrategy):
    source_id = "SM_2ecf3b6936e4a4c1"
    source_file = "Inverted-Hammer-Extended-Options.md"
    timeframe = "4h"
    # The only order call in the file is `strategy.entry("buy", strategy.long)`.
    can_short = False
    source_defaults: dict = {
        # input.int(10, "Downtrend EMA Threshold", minval=0, maxval=200, step=1)
        "downtrend_threshold": 10,
        # input.float(2, "Min Upper Wick X Body", minval=2, maxval=20, step=1)
        "upper_wick_min": 2.0,
        # input.float(20, "Max Upper Wick X Body", minval=3, maxval=100, step=1)
        "upper_wick_max": 20.0,
        # input.float(1, "Max Lower Wick X Body", minval=.25, maxval=10, step=.25)
        "lower_wick_max": 1.0,
        # input.float(2, "Min Body % of Candle", minval=1, maxval=50, step=1)
        "body_min": 2.0,
        # input.bool(false, "Positive Candles Only")
        "up_only": False,
        # input.bool(false, "Broke Previous High")
        "broke_high": False,
    }
    # No `strategy()` declaration exists (not even a commented-out one), so every
    # property is Pine's documented default: fixed / 1 contract, 0% commission,
    # pyramiding 0, initial capital 1000000, process_orders_on_close false.
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    # No stop / limit / trail leg: the file has no exit call of any kind.
    source_reproduce_stops = False
    source_fidelity_notes = [
        "The source declares `indicator(...)`, not `strategy()`: the trailing "
        "`if invertedHammer / strategy.entry(\"buy\", strategy.long)` block is "
        "the converter station's appended order block (PINE_SEMANTICS.md 1.17). "
        "Pine v5 cannot compile strategy.* inside indicator(), so the original "
        "strategy IS the indicator plus that block -- read from the source, not "
        "from the (absent) author intent.",
        "THE SOURCE HAS NO EXIT AT ALL: no strategy.close, no strategy.exit, "
        "active or commented out. The trade behaviour reproduced is therefore "
        "'open a long when the hammer qualifies and never close it'.",
        "source_reproduce_stops is False because no stop/limit/trail leg exists.",
        "`invertedHammer` is `low` or `na` -- a FLOAT used as a bare condition. "
        "Pine and Python both read a non-zero float as true and `low` is never "
        "0, so the condition is reproduced as 'not na' with the float value kept "
        "as its own column. It is NOT rewritten into `== 1` or `> 0` "
        "(PINE_SEMANTICS.md 1.17's trap).",
        "MD/SOURCE MISMATCH: the md's argument table shows `true` for "
        "v_input_float_3 (Max Lower Wick X Body); the source declares "
        "input.float(1). The source's 1.0 is used.",
        "The md carries no prose description, so it neither confirms nor "
        "contradicts the appended order block.",
        "ta.ema is pine_ta's modelled seeding (first non-na observation, "
        "PINE_SEMANTICS.md 3.1); TradingView's exact seed rule is unpublished.",
        "plot() is display-only and is not an order; it is not reproduced as a "
        "plot, but the plotted value is kept as a column because the entry test "
        "reads it.",
        "`high > high[1]` is na (falsy) on the first bar; with the default "
        "`broke_high = false` the conjunct is short-circuited to true anyway.",
        "No strategy() declaration exists, so the sizing is Pine's default "
        "fixed / 1 contract against the default initial capital 1000000 -- "
        "notably NOT a percentage of equity.",
        "Leverage, margin, liquidation, funding and contract-step rounding are "
        "not modelled; the chain verifier measures the step rounding separately.",
    ]

    def pine_indicators(self, dataframe, params):
        open_ = dataframe["open"]
        high = dataframe["high"]
        low = dataframe["low"]
        close = dataframe["close"]

        # bodyGreen = close > open
        body_green = close > open_
        # body = math.abs(close - open)
        body = (close - open_).abs()
        # upper_wick = high - math.max(open, close)
        # lower_wick = math.min(open, close) - low
        candle_top = pd.concat([open_, close], axis=1).max(axis=1)
        candle_bottom = pd.concat([open_, close], axis=1).min(axis=1)
        upper_wick = high - candle_top
        lower_wick = candle_bottom - low

        upper_wick_min = float(params["upper_wick_min"])
        upper_wick_max = float(params["upper_wick_max"])
        lower_wick_max = float(params["lower_wick_max"])
        body_min = float(params["body_min"])
        up_only = bool(params["up_only"])
        broke_high = bool(params["broke_high"])

        # upper_wick_qualify = (body * upper_wick_min <= upper_wick) and
        #                       (body * upper_wick_max >= upper_wick) and
        #                       (not broke_high or high > high[1])
        upper_wick_qualify = (body * upper_wick_min <= upper_wick) & (
            body * upper_wick_max >= upper_wick
        )
        if broke_high:
            upper_wick_qualify = upper_wick_qualify & (high > high.shift(1))

        # lower_wick_qualify = (lower_wick <= body * lower_wick_max)
        lower_wick_qualify = lower_wick <= body * lower_wick_max

        # body_qualify = (bodyGreen or not up_only) and
        #                (body > (body_min / 100 * (high - low))) and
        #                (downtrend_threshold == 0 or close < ta.ema(close, downtrend_threshold))
        body_qualify = body > (body_min / 100.0 * (high - low))
        if up_only:
            # `(bodyGreen or not up_only)`: the disjunct is true whenever
            # `up_only` is false, so only the true branch adds a condition.
            body_qualify = body_qualify & body_green
        threshold = int(params["downtrend_threshold"])
        if threshold > 0:
            # Pine short-circuits: `downtrend_threshold == 0 or ...` is true
            # whenever the threshold is 0, so the ema is only needed above 0.
            body_qualify = body_qualify & (
                close < ta.pine_ema(close, threshold)
            )

        # invertedHammer = body_qualify and upper_wick_qualify and lower_wick_qualify ? low : na
        inverted_hammer = body_qualify & upper_wick_qualify & lower_wick_qualify
        dataframe["pine_inverted_hammer"] = inverted_hammer
        dataframe["pine_inverted_hammer_level"] = low.where(inverted_hammer)
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "inverted_hammer": dataframe["pine_inverted_hammer"].to_numpy(dtype=bool),
        }

    def pine_script(self, broker, i, ctx):
        # if invertedHammer
        #    strategy.entry("buy", strategy.long)
        #
        # `invertedHammer` is `low` / na; Pine tests its truth value, which is
        # "not na". No exit call exists, so nothing here ever closes the entry.
        if ctx["inverted_hammer"][i]:
            broker.entry("buy", "long")
