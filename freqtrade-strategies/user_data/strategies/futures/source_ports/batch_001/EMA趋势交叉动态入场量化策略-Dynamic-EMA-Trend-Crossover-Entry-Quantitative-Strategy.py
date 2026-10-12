"""Port of sources/SM_88f0c32b4472155f.pine (batch_001/EMA趋势交叉动态入场量化策略-Dynamic-EMA-Trend-Crossover-Entry-Quantitative-Strategy.md).

Pine v5. A dual-EMA crossover, long only, exited by the opposite cross:

    shortEmaLength = 14   (input)
    longEmaLength  = 100  (input)
    shortEma = ta.ema(close, shortEmaLength)
    longEma  = ta.ema(close, longEmaLength)
    buySignal  = ta.crossover(shortEma, longEma)    -> strategy.entry("Buy", strategy.long)
    sellSignal = ta.crossunder(shortEma, longEma)   -> strategy.close("Buy")

`strategy("EMA Crossover Strategy", overlay=true)` declares ONLY title and
overlay, so every other property is Pine's documented default: `strategy.fixed`
/ 1 contract, initial capital 1000000, commission 0%, pyramiding 0,
`process_orders_on_close=false`. `source_initial_capital` is therefore the
documented 1000000 rather than a number the source states.

The only other state in the source is a pair of `var float` trackers --
`lastBuyPrice` and `lastSellPrice`, each assigned `close` on its own signal bar
and never read anywhere. They place no condition and drive no order; they are
reproduced as ledger columns so the port does not silently drop them, and
nothing in `pine_script` reads them.

FIDELITY:

* `strategy.close("Buy")` fires on the sell signal regardless of position, which
  is the source's own shape; the engine's `from_entry` matching makes it a no-op
  when no "Buy" entry is held (PINE_SEMANTICS.md 1.12), and the signal projector
  honours the same guard.
* Pine's `ta.ema` seeding is not publicly specified; `pine_ta.pine_ema` seeds
  with the first non-na observation (PINE_SEMANTICS.md 3.1). Both EMAs are
  seeded that way here and the choice is a modelled one, not a certified rule.
* `pine_ta.pine_crossover` / `pine_crossunder` implement Pine's `a > b and a[1]
  <= b[1]` / `a < b and a[1] >= b[1]`; an na on either side makes the comparison
  false in a boolean context, so no cross fires while either EMA is still
  seeding.
* There is no stop, limit or trailing exit in the source -- the only way out is
  the crossunder -- so `source_reproduce_stops` is False and a position still
  open at the end of the window stays open.
* `can_short` is False: the source never calls `strategy.entry` with
  `strategy.short`, and its "SELL" label is a chart annotation on a close.
* `plot` / `plotshape` / the `color.*` and `text=` arguments are display-only.
* The md describes the exit as a "sell signal" and calls the 14/100 pair
  short/长期 without naming the exit order type; the code is a level
  `strategy.close`, which is what is reproduced.
* The `/*backtest` header declares `period: 1d` on Futures_Binance BTC_USDT, so
  `timeframe` is "1d"; its `basePeriod: 1d` is the FMZ backtester's own filling
  granularity, not the strategy's period.
* Leverage, margin, liquidation, funding and the venue's contract-step rounding
  are not modelled.
"""
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


class SMDynamicEmaTrendCrossoverEntry_88f0c3(PinePortBase, IStrategy):
    source_id = "SM_88f0c32b4472155f"
    source_file = (
        "EMA趋势交叉动态入场量化策略-Dynamic-EMA-Trend-Crossover-Entry-Quantitative-Strategy.md"
    )
    timeframe = "1d"
    can_short = False
    source_defaults: dict = {"shortEmaLength": 14, "longEmaLength": 100}
    # `strategy("EMA Crossover Strategy", overlay=true)` states nothing about
    # sizing, so these are Pine's documented defaults, not source-given values.
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    source_reproduce_stops = False
    source_fidelity_notes = [
        "`strategy()` declares only title and overlay, so fixed/1 contract, "
        "initial capital 1000000, commission 0% and pyramiding 0 are Pine's "
        "documented defaults rather than values the source states.",
        "Long only: the source never calls `strategy.entry` with "
        "`strategy.short`, so can_short is False and the `SELL` plotshape is a "
        "chart annotation on the `strategy.close`, not a short entry.",
        "`ta.ema` seeding is unspecified by TradingView; the port uses "
        "pine_ta.pine_ema's modelled first-non-na seed (PINE_SEMANTICS.md 3.1) "
        "for both the 14 and the 100 EMA.",
        "`var float lastBuyPrice` / `lastSellPrice` are assigned but never read; "
        "they place no condition and are kept only as ledger columns.",
        "`strategy.close(\"Buy\")` is issued on the sell signal regardless of "
        "position and is a no-op when no Buy entry is held (PINE_SEMANTICS.md "
        "1.12).",
        "No stop / limit / trail exit exists, so source_reproduce_stops is False "
        "and a position open at the end of the window stays open.",
        "plot / plotshape and their colour and text arguments are display-only.",
        "The header's `basePeriod: 1d` is the FMZ backtester's filling "
        "granularity, not the strategy's period; `period: 1d` is.",
        "Leverage, margin, liquidation, funding and venue contract-step rounding "
        "are not modelled.",
    ]

    def pine_indicators(self, dataframe, params):
        close = dataframe["close"]
        short_ema = ta.pine_ema(close, int(params["shortEmaLength"]))
        long_ema = ta.pine_ema(close, int(params["longEmaLength"]))
        buy_signal = ta.pine_crossover(short_ema, long_ema)
        sell_signal = ta.pine_crossunder(short_ema, long_ema)
        dataframe["pine_short_ema"] = short_ema
        dataframe["pine_long_ema"] = long_ema
        dataframe["pine_buy_signal"] = buy_signal
        dataframe["pine_sell_signal"] = sell_signal
        # `var float lastBuyPrice = na` + `if (buySignal) lastBuyPrice := close`:
        # a `var` keeps its last assigned value, which is a forward fill of the
        # values written on signal bars.
        dataframe["pine_last_buy_price"] = close.where(buy_signal).ffill()
        dataframe["pine_last_sell_price"] = close.where(sell_signal).ffill()
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "buy_signal": dataframe["pine_buy_signal"].to_numpy(),
            "sell_signal": dataframe["pine_sell_signal"].to_numpy(),
        }

    def pine_script(self, broker, i, ctx):
        # if (buySignal)
        #     strategy.entry("Buy", strategy.long)
        if ctx["buy_signal"][i]:
            broker.entry("Buy", "long")
        # if (sellSignal)
        #     strategy.close("Buy")
        if ctx["sell_signal"][i]:
            broker.close("Buy")
