"""Port of sources/SM_09e4df3803aabf23.pine
(batch_001/Advanced-Fair-Value-Gap-Detection-Strategy-with-Dynamic-Risk-Management-and-Fixed-Take-Profit-基于动态风险管理和固定获利的高级公允价值缺口检测策略.md).

Pine v5. A three-bar gap detector, entry in the gap's direction with a fixed
point target:

    pipsToPriceChange(pips) => syminfo.mintick * pips * 10
    detectFVG(dir) =>
        gap = 0.0
        if dir > 0
            gap := low[2] - high[1]        // "bullish"
        else
            gap := low[1] - high[2]        // "bearish"
        math.abs(gap) > (close * fvgThreshold / 100)

    bullishFVG = detectFVG(1)
    bearishFVG = detectFVG(-1)
    longCondition  = bullishFVG
    shortCondition = bearishFVG

    if (longCondition)
        strategy.entry("Long", strategy.long)
    if (shortCondition)
        strategy.entry("Short", strategy.short)

    if (strategy.position_size > 0)
        strategy.exit("Long TP", "Long", limit=longTakeProfit)
        strategy.close("Long SL", when=strategy.openprofit < -stopLossAmount)
    else if (strategy.position_size < 0)
        strategy.exit("Short TP", "Short", limit=shortTakeProfit)
        strategy.close("Short SL", when=strategy.openprofit < -stopLossAmount)

`strategy()` declares `initial_capital=500`, `default_qty_type=strategy.fixed`
and `default_qty_value=1`, so commission is 0% and pyramiding 0 (Pine's
defaults) and `process_orders_on_close=false`. The `/*backtest` header declares
`period: 1d` on Futures_Binance BTC_USDT, so `timeframe` is "1d".

TWO SOURCE FACTS DECIDE THE WHOLE TRADE BEHAVIOUR, and both are reproduced
rather than repaired (rule 2):

1. `strategy.close("Long SL", ...)` / `strategy.close("Short SL", ...)` name an
   order id that no `strategy.entry` ever created. Pine's `strategy.close(id)`
   closes the position opened by the entry with THAT id (PINE_SEMANTICS, first
   table), so both calls are no-ops: the "SL" leg never closes anything. The
   port issues the calls as written and the engine's `_close_entries` matches
   nothing, exactly as the platform does. Renaming them to close "Long"/"Short"
   would be a different strategy -- this is NOT the risk management the md's
   prose describes.
2. `math.abs(gap)` makes the two conditions pure magnitude tests, so
   `longCondition` and `shortCondition` differ only in which pair of bars they
   measure and can both be true on one bar. The md's prose describes
   directional FVG rules ("high[1] < low[2]" for bullish); the source's `abs()`
   is broader than that. The source wins.

Consequence of the declared wallet: `qty` is 1 contract while
`initial_capital` is 500 and BTC/USDT:USDT trades near 40000, so one contract's
notional (~40000) is two orders of magnitude above the source's own wallet. The
engine is a cash-flow model and does not deduct the notional on entry, but
Freqtrade does: `custom_stake_amount` records the engine's notional, the venue's
max-stake gate refuses it, and the backtest reports the run as vetoed
(`one_sided_trades` / `mismatch_framework_veto`) rather than matched. That is
PINE_SEMANTICS 1.5 / 1.6 -- a venue-and-framework boundary, not a porting
error -- and the source's `initial_capital` is NOT adjusted to make it go away
(1.6: doing so would violate both "keep the initialisation" and "no tuning").

FIDELITY:

* `takeProfitPips = 50` is a literal in the source, not an `input()`, and stays
  a literal. `syminfo.mintick` is not readable offline; the port uses the
  declared `source_mintick` (0.1 for this pair), so the target distance is
  `0.1 * 50 * 10 = 50` price units.
* The take-profit is `strategy.position_avg_price +/- 50`, resolved AT THE BAR
  THE ORDER IS PLACED, and re-placed every bar the position is open; the exit
  id is replaced, not stacked.
* `stopLossAmount = strategy.equity * 0.01` -- equity, not capital, so it is
  read from the engine's own running equity at the bar being processed.
* `source_reproduce_stops` is False: the source's only resting leg is the
  take-profit `limit=`; the "SL" calls are the market `strategy.close` no-ops
  above. The take-profit series is built regardless (`PinePortBase` keeps
  `_pine_takes` even when stops are not reproduced).
* The md files' embedded Pine block is byte-identical to the source .pine.
* PINE_SEMANTICS 3.1 / 3.3 (modelled choices): not exercised here -- the source
  uses no `ta.*` moving average, only `low[]` / `high[]` / `close` / `math.abs`.
* PINE_SEMANTICS 1.6 / 5.1: the venue's contract-step rounding and non-zero
  taker fees are not modelled; the source declares 0% commission, which is the
  cost basis the port carries.
* Leverage, margin, liquidation and funding are not modelled.
"""
from freqtrade.strategy import IStrategy

import numpy as np
import pandas as pd

from pine_port_base import PinePortBase


class SMAdvancedFairValueGapDetection_09e4df(PinePortBase, IStrategy):
    source_id = "SM_09e4df3803aabf23"
    source_file = (
        "Advanced-Fair-Value-Gap-Detection-Strategy-with-Dynamic-Risk-"
        "Management-and-Fixed-Take-Profit-基于动态风险管理和固定获利的高级公允价值缺口检测策略.md"
    )
    timeframe = "1d"
    # strategy.entry(..., strategy.short, ...) exists.
    can_short = True
    source_defaults: dict = {"fvgThreshold": 0.5}
    # strategy("..." , overlay=true, initial_capital=500,
    #           default_qty_type=strategy.fixed, default_qty_value=1)
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 500.0
    # The only resting leg is the take-profit limit; the "SL" calls are
    # strategy.close, which is a market exit, not a stop level.
    source_reproduce_stops = False
    source_fidelity_notes = [
        "`strategy.close(\"Long SL\", ...)` / `strategy.close(\"Short SL\", ...)` "
        "name an order id that no strategy.entry ever created. Pine's "
        "strategy.close(id) closes the position opened by the entry with THAT "
        "id, so both calls are no-ops (PINE_SEMANTICS, first table, and 1.12 for "
        "the engine's matching rule). The port reproduces the no-op rather than "
        "renaming the id to \"Long\"/\"Short\" -- renaming would be a different "
        "strategy, and rule 2 says record the difference, not repair it.",
        "The md's prose describes directional gap rules (bullish FVG = the "
        "previous bar's high below the low two bars back) and calls the 1% "
        "equity rule an active stop loss. The source computes math.abs(gap), "
        "which makes both conditions pure magnitude tests that can be true on "
        "the same bar, and its stop-loss call is the no-op above. The source is "
        "authoritative; the prose is recorded as inaccurate.",
        "takeProfitPips = 50 is a literal in the source, not an input(), and "
        "stays a literal. syminfo.mintick cannot be read offline, so the port "
        "uses the declared source_mintick (0.1): the target distance is "
        "mintick * 50 * 10 = 50 price units.",
        "The take-profit is strategy.position_avg_price +/- the tick distance, "
        "re-placed every bar the position is open, and the same-id strategy.exit "
        "REPLACES rather than stacks. It is first placed on the bar AFTER the "
        "entry fills, because the source guards it with strategy.position_size "
        "> 0, so the level is live from the second bar of the trade onwards.",
        "stopLossAmount = strategy.equity * 0.01 -- equity, not initial capital "
        "-- so it is evaluated from the engine's running equity at the bar being "
        "processed. It feeds the strategy.close no-op and therefore does not "
        "change any fill; it is reproduced because the source computes it.",
        "source_reproduce_stops is False: the only resting leg is the "
        "take-profit limit. PinePortBase still builds the take-profit series, "
        "which reaches Freqtrade through the ROI hooks (PINE_SEMANTICS 1.8).",
        "The declared wallet (initial_capital = 500) against qty = 1 contract of "
        "BTC/USDT:USDT makes every entry's notional (~40000) far larger than the "
        "framework's wallet, so the venue's max-stake gate refuses the entry and "
        "the chain comparison reports the run as one-sided / framework-vetoed "
        "rather than matched (PINE_SEMANTICS 1.5, 1.6). initial_capital is NOT "
        "raised to force a match: 1.6 records that as both a parameter change "
        "and a loss of the source's initialisation.",
        "The md files' embedded Pine block is byte-identical to the source "
        ".pine.",
        "The plotshape calls and overlay=true are display-only.",
        "PINE_SEMANTICS 1.6 / 5.1: the venue's contract-step rounding and "
        "non-zero taker fees are not modelled; the source declares 0% "
        "commission, which is the cost basis the port carries.",
        "Leverage, margin, liquidation and funding are not modelled.",
    ]

    def pine_indicators(self, dataframe, params):
        high = dataframe["high"]
        low = dataframe["low"]
        close = dataframe["close"]
        threshold = float(params["fvgThreshold"])

        # detectFVG(1):  gap = low[2] - high[1]
        gap_bullish = low.shift(2) - high.shift(1)
        # detectFVG(-1): gap = low[1] - high[2]
        gap_bearish = low.shift(1) - high.shift(2)
        # math.abs(gap) > (close * fvgThreshold / 100)
        limit = close * threshold / 100.0
        bullish_fvg = (gap_bullish.abs() > limit).fillna(False)
        bearish_fvg = (gap_bearish.abs() > limit).fillna(False)

        dataframe["pine_gap_bullish"] = gap_bullish
        dataframe["pine_gap_bearish"] = gap_bearish
        dataframe["pine_bullish_fvg"] = bullish_fvg
        dataframe["pine_bearish_fvg"] = bearish_fvg
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "long_condition": dataframe["pine_bullish_fvg"].to_numpy(),
            "short_condition": dataframe["pine_bearish_fvg"].to_numpy(),
        }

    def pine_script(self, broker, i, ctx):
        # pipsToPriceChange(pips) => syminfo.mintick * pips * 10, pips = 50
        pips_to_price = float(self.source_mintick) * 50.0 * 10.0

        # if (longCondition)
        #     strategy.entry("Long", strategy.long)
        if ctx["long_condition"][i]:
            broker.entry("Long", "long")
        # if (shortCondition)
        #     strategy.entry("Short", strategy.short)
        if ctx["short_condition"][i]:
            broker.entry("Short", "short")

        # stopLossAmount = strategy.equity * 0.01
        stop_loss_amount = broker.equity * 0.01
        avg_price = broker.position_avg_price

        if broker.position_size > 0:
            # strategy.exit("Long TP", "Long", limit=longTakeProfit)
            broker.exit("Long TP", from_entry="Long",
                        limit=avg_price + pips_to_price if np.isfinite(avg_price)
                        else np.nan)
            # strategy.close("Long SL", when=strategy.openprofit < -stopLossAmount)
            broker.close("Long SL",
                         when=bool(broker.open_profit < -stop_loss_amount))
        elif broker.position_size < 0:
            # strategy.exit("Short TP", "Short", limit=shortTakeProfit)
            broker.exit("Short TP", from_entry="Short",
                        limit=avg_price - pips_to_price if np.isfinite(avg_price)
                        else np.nan)
            # strategy.close("Short SL", when=strategy.openprofit < -stopLossAmount)
            broker.close("Short SL",
                         when=bool(broker.open_profit < -stop_loss_amount))
