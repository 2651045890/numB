"""Port of sources/SM_7683de8d045ff936.pine (batch_001/BMSB-Breakout-Strategy-BMSB-突破策略.md).

Pine v5. The BMSB band -- a 20-period SMA against a 21-period EMA -- traded as
a two-sided breakout:

    sma = ta.sma(close, 20)
    ema = ta.ema(close, 21)
    outSma = request.security(syminfo.tickerid, timeframe.period, sma)
    outEma = request.security(syminfo.tickerid, timeframe.period, ema)

    buySignal  = ta.crossover(close, outSma)
    sellSignal = ta.crossunder(close, outEma)

    if (buySignal)
        if (strategy.opentrades > 0)
            strategy.close_all()
        strategy.entry("Buy", strategy.long)

    if (sellSignal)
        if (strategy.opentrades > 0)
            strategy.close_all()
        strategy.entry("Sell", strategy.short)

The two lengths (20 and 21) are literals in the source, not inputs, and stay
literals here.

`strategy()` declares only `title` and `overlay`, so every property is Pine's
documented default: `strategy.fixed` / 1 contract, initial capital 1000000,
commission 0%, `pyramiding 0`, `process_orders_on_close=false`.

The `/*backtest` header declares `period: 1h` on Futures_Binance BTC_USDT, so
`timeframe` is "1h"; its `basePeriod: 15m` is the FMZ backtester's own
granularity for filling those 1h bars, not the strategy's period.

Both branches place entries in a direction, so `can_short` is True. Nothing in
the source places a stop or limit exit -- `close_all` is a market call -- so
`source_reproduce_stops` is False and a position still open at the end of the
window stays open.

FIDELITY:

* `request.security(syminfo.tickerid, timeframe.period, <expr>)` asks for the
  SAME symbol on the SAME timeframe the script runs on, so `outSma` / `outEma`
  are the local `sma` / `ema` series and the port reads them directly. The
  engine does not resample (PINE_SEMANTICS.md section 二.1); nothing has to be
  resampled for this source because the requested timeframe is the chart's own,
  and the default `barmerge.lookahead_off` is not overridden. Had either
  argument differed, this port would need an explicitly aligned series.
* `strategy.close_all()` is placed on the SAME bar as the entry it precedes.
  The engine fills both at the next bar's open in creation order -- close_all
  first, then the entry -- so the result is a fresh position in the new
  direction, which is what the source asks for. The projection carries the
  closing leg too (`exit_long` / `exit_short` alongside `enter_*`), so the
  framework nets the same way.
* With `pyramiding 0` the source's re-entry after a `close_all` is allowed
  again only because the close has emptied the position by the time the entry
  fills; the engine evaluates the pyramiding limit at CREATION, where the
  position still exists but is in the OPPOSITE direction (`_can_add` permits a
  reversal), so the order is not blocked.
* `ta.sma` is na until 20 bars have elapsed and `ta.ema` propagates na, so
  neither signal can be true before the windows are full; both `crossover` and
  `crossunder` return false while any term is na.
* The md prose describes the same 20 SMA / 21 EMA breakout the code implements
  and adds no condition; its "timely stop-loss" phrasing describes the
  `close_all` + reverse, not a stop order.
* `plot`, `plotshape`, `fill` and `overlay` are display-only and are not
  reproduced.
* Leverage, margin, liquidation, funding and contract-step rounding are not
  modelled; the venue's rounding can differ from the engine's float quantity,
  which the chain verifier measures separately.
"""
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


class SMBmsbBreakout_7683de(PinePortBase, IStrategy):
    source_id = "SM_7683de8d045ff936"
    source_file = "BMSB-Breakout-Strategy-BMSB-突破策略.md"
    timeframe = "1h"
    can_short = True
    source_defaults: dict = {}
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    source_reproduce_stops = False
    source_fidelity_notes = [
        "`request.security(syminfo.tickerid, timeframe.period, expr)` requests "
        "the same symbol on the same timeframe, so the requested series IS the "
        "local one and the port reads `sma` / `ema` directly. No resampling is "
        "modelled; with a different symbol or timeframe this port would need an "
        "explicitly aligned series (PINE_SEMANTICS.md section 二.1).",
        "`close_all()` and the entry it precedes are placed on the same bar; "
        "the engine fills them at the next open in creation order, netting to a "
        "fresh position in the new direction, and the projection carries both "
        "legs so the framework nets the same way.",
        "The 20 / 21 lengths are literals in the source, not inputs, and stay "
        "literals.",
        "Both branches place entries, so can_short is True; no stop or limit "
        "exit exists anywhere, so source_reproduce_stops is False.",
        "ta.sma is na until its window is full and ta.ema propagates na, so no "
        "signal can be true before 20 bars of history.",
        "plot / plotshape / fill / overlay are display-only and not reproduced.",
        "Leverage, margin, liquidation, funding and contract-step rounding are "
        "not modelled; the venue's rounding can differ from the engine's float "
        "quantity, which the chain verifier measures separately.",
    ]

    def pine_indicators(self, dataframe, params):
        close = dataframe["close"]
        # sma = ta.sma(close, 20) ; ema = ta.ema(close, 21)
        sma = ta.pine_sma(close, 20)
        ema = ta.pine_ema(close, 21)
        # outSma / outEma: same symbol, same timeframe -> the local series.
        dataframe["pine_sma"] = sma
        dataframe["pine_ema"] = ema
        dataframe["pine_buy_signal"] = ta.pine_crossover(close, sma)
        dataframe["pine_sell_signal"] = ta.pine_crossunder(close, ema)
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "buy_signal": dataframe["pine_buy_signal"].to_numpy(),
            "sell_signal": dataframe["pine_sell_signal"].to_numpy(),
        }

    def pine_script(self, broker, i, ctx):
        # if (buySignal)
        #     if (strategy.opentrades > 0)
        #         strategy.close_all()
        #     strategy.entry("Buy", strategy.long)
        if ctx["buy_signal"][i]:
            if broker.open_trades > 0:
                broker.close_all()
            broker.entry("Buy", "long")

        # if (sellSignal)
        #     if (strategy.opentrades > 0)
        #         strategy.close_all()
        #     strategy.entry("Sell", strategy.short)
        if ctx["sell_signal"][i]:
            if broker.open_trades > 0:
                broker.close_all()
            broker.entry("Sell", "short")
