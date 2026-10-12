"""Port of sources/SM_8a9eb5d3ace1e653.pine (batch_001/EMA-RSI-MACD动态止盈止损交易策略-EMA-RSI-MACD-Dynamic-Take-Profit-and-Stop-Loss-Trading-Strategy.md).

Pine v5. Every indicator is computed from HLCC4, not from `close`, and the
entry is a three-filter confirmation of a 9/21 EMA cross:

    hlcc4_custom = (high + low + close + close) / 4
    ema1 = ta.ema(hlcc4_custom, 9)
    ema2 = ta.ema(hlcc4_custom, 21)
    ema3 = ta.ema(hlcc4_custom, 34)
    rsi  = ta.rsi(hlcc4_custom, 14)
    [a, b, histogram] = ta.macd(hlcc4_custom, 12, 26, 9)   # histogram = macd - signal

    emaCrossUp   = ta.crossover(ema1, ema2)
    emaCrossDown = ta.crossunder(ema1, ema2)

    buySignal  = emaCrossUp   and hlcc4 > ema3 and rsi >  50 and close > open and histogram > 0
    sellSignal = emaCrossDown and hlcc4 < ema3 and rsi <  50 and close < open and histogram < 0

and each entry carries a fixed 10-pip take profit and 10-pip stop loss measured
with `syminfo.mintick`.

The order sequence is reproduced in the source's own order, which matters
because the first block reads `strategy.position_size` before the second and
third can change it, and because the same-bar close and entry of a reversal are
two separate calls:

    if strategy.opentrades > 0
        if sellSignal and strategy.position_size >  0 -> strategy.close("Buy")
        if buySignal  and strategy.position_size <  0 -> strategy.close("Sell")
    if buySignal  and strategy.position_size == 0
        entryPrice := close
        tpPrice    := entryPrice + tpPips * syminfo.mintick
        slPrice    := entryPrice - slPips * syminfo.mintick
        strategy.entry("Buy", strategy.long)
        strategy.exit("Take Profit/Stop Loss", "Buy", limit=tpPrice, stop=slPrice)
    if sellSignal and strategy.position_size == 0
        entryPrice := close
        tpPrice    := entryPrice - tpPips * syminfo.mintick
        slPrice    := entryPrice + slPips * syminfo.mintick
        strategy.entry("Sell", strategy.short)
        strategy.exit("Take Profit/Stop Loss", "Sell", limit=tpPrice, stop=slPrice)

`strategy()` declares only `title` and `overlay`, so every property is Pine's
documented default: `strategy.fixed` / 1 contract, initial capital 1000000,
commission 0%, pyramiding 0, `process_orders_on_close=false`. No explicit `qty`
is passed anywhere, so the default 1 contract is what orders are sized with.
`var float entryPrice / tpPrice / slPrice` are carried across bars by the
source; each is overwritten in full at the moment an order is placed, so the
port reads them off the signal bar directly instead of keeping state.

FIDELITY:

* The take profit and stop loss are placed as one OCA `strategy.exit`, and both
  levels are anchored to the SIGNAL BAR'S CLOSE (`entryPrice := close`), not to
  the fill price -- the position fills one bar later at that bar's open, so the
  two legs sit `10 * mintick` around a price the fill may never have touched.
  The port passes those exact levels to `broker.exit`; the engine's
  `_exit_fill` then fills inside the bar, which is where Pine fills them.
* `syminfo.mintick` is read off the symbol and is not a source input. For the
  header's `Futures_Binance` BTC_USDT contract the minimum price increment is
  0.1, which is what `source_mintick` declares; 10 pips therefore means 1.0
  price unit. `source_mintick` is what the engine converts `profit=` / `loss=`
  with, and the port computes `tpPrice` / `slPrice` itself from the same value.
* `ta.ema` is seeded with the first non-na observation and an na observation
  does not advance the recursion (pine_ta's modelled choice; TradingView does
  not publish its seeding rule -- PINE_SEMANTICS.md 3.1). Here that makes all
  three EMAs and the MACD histogram defined from the first bar, while `ta.rsi`
  still needs its 14-bar `ta.rma` warm-up, so `rsi > 50` / `rsi < 50` are the
  binding warm-up constraint. Early-bar differences against the original
  platform are possible on this axis and are not corrected.
* `histogram` is the THIRD value of `ta.macd` (`macd - signal`), which
  `pine_ta.pine_macd` returns as the `hist` column; the first two (`a`, `b`)
  are bound and never read by the source.
* The reversal close (`strategy.close("Buy")` / `("Sell")`) and the entry that
  follows it are two orders on one bar. Pine fills the entry on the next open);
  the engine models the close and the entry as separate pending orders, and the
  projection emits `exit_*` plus the opposing `enter_*` for the same bar.
* `comment=` strings, the two `plotshape` calls and the three `plot` calls are
  display-only and place no condition.
* No `strategy.risk.*`, no `request.security`, no `barstate` branch, no
  `varip`, no pyramiding and no leverage in the source.
* Leverage, margin, liquidation, funding and the venue's contract-step rounding
  are not modelled; the chain verifier measures the step rounding separately
  (PINE_SEMANTICS.md 1.6) rather than treating it as a signal difference.
"""
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


class SMEmarsiMacdDynamic_8a9eb5(PinePortBase, IStrategy):
    source_id = "SM_8a9eb5d3ace1e653"
    source_file = "EMA-RSI-MACD动态止盈止损交易策略-EMA-RSI-MACD-Dynamic-Take-Profit-and-Stop-Loss-Trading-Strategy.md"
    timeframe = "1d"
    can_short = True
    source_defaults: dict = {
        "ema1Length": 9,
        "ema2Length": 21,
        "ema3Length": 34,
        "rsiLength": 14,
        "rsiThreshold": 50,
        "macdFastLength": 12,
        "macdSlowLength": 26,
        "macdSignalSmoothing": 9,
        "tpPips": 10,
        "slPips": 10,
    }
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    source_reproduce_stops = True
    # syminfo.mintick for the header's Futures_Binance BTC_USDT contract; the
    # source multiplies its pip counts by it, and so does this port.
    source_mintick = 0.1
    source_fidelity_notes = [
        "Both exit legs of the single `strategy.exit` are reproduced: `limit=` "
        "as the take profit and `stop=` as the stop loss. A port that wired "
        "only the stop would silently hold every winner to the next signal "
        "(PINE_SEMANTICS.md 1.8).",
        "Take profit and stop loss are anchored to the SIGNAL bar's close "
        "(`entryPrice := close`), not to the fill price: the position fills on "
        "the next bar's open, so both levels sit 10*mintick around a price the "
        "fill may never have traded at. Reproduced as written.",
        "`syminfo.mintick` is not an input. 0.1 is the minimum price increment "
        "of the header's Futures_Binance BTC_USDT contract, so tpPips=10 / "
        "slPips=10 are 1.0 price units each. Declared in `source_mintick` so "
        "the engine and this port agree.",
        "`ta.ema` is seeded with the first non-na value (pine_ta's modelled "
        "choice; PINE_SEMANTICS.md 3.1), so ema1/ema2/ema3 and the MACD "
        "histogram are defined from bar 0 while TradingView may leave them na "
        "for the first `length-1` bars. Early-bar differences on that axis are "
        "a known, uncorrected equivalence risk.",
        "`rsi > rsiThreshold` / `rsi < rsiThreshold` are the binding warm-up "
        "condition: pine_ta's `ta.rsi` needs 14 bars before its Wilder averages "
        "exist, and an na comparison is false, so no signal can fire earlier.",
        "`[a, b, histogram] = ta.macd(...)` binds three values and reads only "
        "the third; the port reads the `hist` column and leaves `macd` / "
        "`signal` unused, exactly as the source does.",
        "The reversal path issues `strategy.close(\"Buy\")` and, on the same "
        "bar, `strategy.entry(\"Sell\", ...)`. Both are replayed in source "
        "order; `strategy.close` on an entry id that is not held is a no-op in "
        "the engine (PINE_SEMANTICS.md 1.12), which is also Pine's behaviour.",
        "`strategy.opentrades` counts open entry records, not sign of position; "
        "the engine's `open_trades` is the same count, so the first block's "
        "gate is reproduced literally rather than simplified to a sign test.",
        "comment= strings, two plotshape and three plot calls are display-only "
        "and place no condition.",
        "No pyramiding, no trailing stop, no `strategy.risk.*`, no "
        "`request.security`, no barstate branch and no `varip` in the source.",
        "Leverage, margin, liquidation, funding and contract-step rounding are "
        "not modelled; the venue's rounding of the engine's float quantity is "
        "measured by the chain verifier instead of being hidden here.",
    ]

    def pine_indicators(self, dataframe, params):
        high = dataframe["high"]
        low = dataframe["low"]
        close = dataframe["close"]
        open_ = dataframe["open"]

        # hlcc4_custom = (high + low + close + close) / 4
        hlcc4 = (high + low + close + close) / 4.0

        ema1 = ta.pine_ema(hlcc4, params["ema1Length"])
        ema2 = ta.pine_ema(hlcc4, params["ema2Length"])
        ema3 = ta.pine_ema(hlcc4, params["ema3Length"])
        rsi = ta.pine_rsi(hlcc4, params["rsiLength"])
        # ta.macd's third return value is the histogram, macd - signal.
        histogram = ta.pine_macd(
            hlcc4,
            params["macdFastLength"],
            params["macdSlowLength"],
            params["macdSignalSmoothing"],
        )["hist"]

        ema_cross_up = ta.pine_crossover(ema1, ema2)
        ema_cross_down = ta.pine_crossunder(ema1, ema2)

        buy_signal = (
            ema_cross_up
            & (hlcc4 > ema3)
            & (rsi > params["rsiThreshold"])
            & (close > open_)
            & (histogram > 0)
        )
        sell_signal = (
            ema_cross_down
            & (hlcc4 < ema3)
            & (rsi < params["rsiThreshold"])
            & (close < open_)
            & (histogram < 0)
        )

        dataframe["pine_hlcc4"] = hlcc4
        dataframe["pine_ema1"] = ema1
        dataframe["pine_ema2"] = ema2
        dataframe["pine_ema3"] = ema3
        dataframe["pine_rsi"] = rsi
        dataframe["pine_macd_hist"] = histogram
        dataframe["pine_buy_signal"] = buy_signal
        dataframe["pine_sell_signal"] = sell_signal
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "buy": dataframe["pine_buy_signal"].to_numpy(),
            "sell": dataframe["pine_sell_signal"].to_numpy(),
            "close": dataframe["close"].to_numpy(),
            "tp_pips": float(params["tpPips"]),
            "sl_pips": float(params["slPips"]),
        }

    def pine_script(self, broker, i, ctx):
        buy = bool(ctx["buy"][i])
        sell = bool(ctx["sell"][i])
        tick = float(self.source_mintick)
        tp_pips = ctx["tp_pips"]
        sl_pips = ctx["sl_pips"]

        # if strategy.opentrades > 0
        #     if sellSignal and strategy.position_size > 0
        #         strategy.close("Buy", comment="Close Buy Order")
        #     if buySignal and strategy.position_size < 0
        #         strategy.close("Sell", comment="Close Sell Order")
        if broker.open_trades > 0:
            if sell and broker.position_size > 0:
                broker.close("Buy")
            if buy and broker.position_size < 0:
                broker.close("Sell")

        # if buySignal and strategy.position_size == 0
        if buy and broker.position_size == 0:
            entry_price = float(ctx["close"][i])
            # strategy.entry("Buy", strategy.long)
            broker.entry("Buy", "long")
            # strategy.exit("Take Profit/Stop Loss", "Buy", limit=tpPrice, stop=slPrice)
            broker.exit(
                "Take Profit/Stop Loss",
                from_entry="Buy",
                limit=entry_price + tp_pips * tick,
                stop=entry_price - sl_pips * tick,
            )

        # if sellSignal and strategy.position_size == 0
        if sell and broker.position_size == 0:
            entry_price = float(ctx["close"][i])
            # strategy.entry("Sell", strategy.short)
            broker.entry("Sell", "short")
            broker.exit(
                "Take Profit/Stop Loss",
                from_entry="Sell",
                limit=entry_price - tp_pips * tick,
                stop=entry_price + sl_pips * tick,
            )
