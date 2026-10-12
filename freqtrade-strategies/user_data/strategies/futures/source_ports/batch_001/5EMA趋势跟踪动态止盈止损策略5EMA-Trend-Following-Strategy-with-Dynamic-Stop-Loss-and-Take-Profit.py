"""Port of sources/SM_32e761601fea0a6f.pine
(batch_001/5EMA趋势跟踪动态止盈止损策略5EMA-Trend-Following-Strategy-with-Dynamic-Stop-Loss-and-Take-Profit.md).

Pine v5 (`//@version=5`), short only, with no exit call at all. The whole
source, verbatim:

    emaLength      = input.int(5, "EMA Length", minval=1)
    riskRewardRatio= input.float(3.0, "Risk-Reward Ratio", minval=1.0, step=0.1)

    ema5           = ta.ema(close, emaLength)
    isAlertCandle  = low > ema5 and low[1] > ema5[1]
    entryCondition = isAlertCandle[1] and low <= low[1]
    stopLoss       = high[1]
    entryPrice     = low[1]
    target         = entryPrice - (stopLoss - entryPrice) * riskRewardRatio

    var float tradeEntry / tradeSL / tradeTarget = na
    if (entryCondition)
        strategy.entry("Short", strategy.short, stop=stopLoss, limit=target)
        tradeEntry := entryPrice
        tradeSL := stopLoss
        tradeTarget := target

`strategy("5 EMA Short", overlay=true)` declares the title and `overlay` and
nothing else, so every other property is Pine's documented default:
`default_qty_type=fixed`, `default_qty_value=1`, `initial_capital=1000000`,
`commission_value=0`, `pyramiding=0`, `process_orders_on_close=false`. The
markdown body claims a 0.1% commission ("考虑了0.1%的交易佣金"); the source
declares none, so the port carries 0% and the claim is recorded as a
md-vs-source difference (the source is the authority).

The one order call is an ENTRY carrying both `stop=` and `limit=`, i.e. a
stop-limit entry (Pine: one leg is the trigger, the other the price). There is
no `strategy.exit`, no `strategy.close` and no `strategy.cancel`, so
`source_reproduce_stops` is False -- there is no resting exit level for the
framework to mirror -- and a short open at the end of the window stays open.

FIDELITY:

* The markdown says the entry price is the alert candle's low and describes the
  trade as "entering at the low of the alert candle". The source's order fills
  at the STOP level (`stopLoss = high[1]`), not at `low[1]`; `entryPrice` is
  only stored into `tradeEntry` for a `plotshape`. Transcribed as written: the
  port places the resting order the source places and never fakes a market fill
  at `low[1]`.
* The markdown also claims a 0.1% commission and a "percentage risk model".
  The source declares neither (`strategy()` has no `commission_value` and no
  `default_qty_type`, so the sizing is 1 fixed contract). Recorded, not applied.
* The markdown's "Strategy Arguments" table is absent here, but its prose names
  the inputs as EMA period and risk-reward ratio, which is what the source has:
  `emaLength = 5`, `riskRewardRatio = 3.0`. Both are carried in
  `source_defaults` under the source's own variable names. `minval` / `maxval` /
  `step` only constrain the UI and place no behaviour.
* `stop=` is a PRICE and `limit=` is a PRICE in Pine's `strategy.entry`; only
  `profit=` / `loss=` are tick distances (PINE_SEMANTICS 3.5). The port passes
  the source's own values, so `stop=high[1]` and `limit=low[1] - 3*(high[1] -
  low[1])` are reached as prices.
* RESTING ENTRY ORDERS CANNOT BE PROJECTED TO FREQTRADE (PINE_SEMANTICS 2.11).
  The engine fills the order on whatever later bar actually reaches it; the
  signal projection can only emit `enter_short` on the bar the order was
  PLACED, which Freqtrade fills at the next bar's open. The timing and the
  price are therefore both a modelling approximation of the source: the port
  records this rather than dropping the entry, which would be a rewrite.
* The engine models an entry that carries both legs as a stop order: its
  `PineOrder` keeps `kind="stop"` and `_price_order_fill` consults `stop` only,
  so the `limit` leg is carried but not evaluated. Pine's stop-limit would only
  fill once the price came back to `target`. This is a public-layer modelling
  choice (reported, not changed here).
* Same-id resting entry orders ACCUMULATE in the engine instead of replacing
  each other (PINE_SEMANTICS 1.12, last paragraph, recorded there as unverified
  against the platform). `entryCondition` can be true on consecutive bars, so
  the source's single resting order and the engine's stack of them can differ
  in which level is reached first.
* The alert candle needs `ema5[1]`, so the first possible signal is on bar 2;
  `pine_ema` seeds with the first observation (PINE_SEMANTICS 3.1), which is a
  public-layer choice, and the first `bar_index` bar has no `[1]` and is na ->
  False.
* `plot(ema5, ...)` and the three `plotshape` calls are display-only, as are
  `var float tradeEntry / tradeSL / tradeTarget`.
* Leverage, margin, funding and the venue's contract-step rounding are not
  modelled (PINE_SEMANTICS 1.6, 2.4).
"""
import numpy as np
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


class SM5EmaShort_32e761(PinePortBase, IStrategy):
    source_id = "SM_32e761601fea0a6f"
    source_file = (
        "5EMA趋势跟踪动态止盈止损策略5EMA-Trend-Following-Strategy-with-"
        "Dynamic-Stop-Loss-and-Take-Profit.md"
    )
    # /*backtest ... period: 2h ... */ on Futures_Binance BTC_USDT.
    timeframe = "2h"
    # The source has a real short entry: strategy.entry("Short", strategy.short).
    can_short = True
    source_defaults: dict = {"emaLength": 5, "riskRewardRatio": 3.0}
    # strategy("5 EMA Short", overlay=true): title and overlay only, so Pine's
    # documented defaults apply -- fixed 1 contract, 1000000 initial capital,
    # 0% commission, pyramiding 0, process_orders_on_close false.
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    # The only order is an entry; there is no strategy.exit / strategy.close, so
    # no resting exit level exists for the framework to mirror.
    source_reproduce_stops = False
    source_fidelity_notes = [
        "The markdown's '0.1% commission' is not in the source: strategy() "
        "declares no commission_value, so Pine's default 0% is carried.",
        "The markdown says the entry fills at the alert candle's low; the "
        "source's order is a resting stop at high[1] (entryPrice/low[1] is only "
        "plotted). Transcribed as written.",
        "The markdown's 'percentage risk model' has no counterpart in the "
        "source: strategy() declares no default_qty_type, so sizing is 1 fixed "
        "contract.",
        "Stop-limit ENTRY orders cannot be projected to Freqtrade "
        "(PINE_SEMANTICS 2.11): the engine fills on the bar that reaches the "
        "order, while the framework can only enter at the next open after the "
        "placing bar. Recorded, not repaired.",
        "The engine evaluates an entry that carries both stop= and limit= as a "
        "stop order only; the limit leg is stored but never consulted. Pine's "
        "stop-limit needs the price to come back to `target`. Public-layer "
        "modelling choice, reported rather than changed.",
        "Resting entry orders with the same id accumulate in the engine instead "
        "of replacing each other (PINE_SEMANTICS 1.12, unverified there), so a "
        "repeated entryCondition can rest a stack of orders where Pine keeps "
        "one.",
        "There is no exit call anywhere in the source, so a short open at the "
        "end of the window stays open.",
        "emaLength/riskRewardRatio defaults 5 / 3.0 are the source's input "
        "defaults; minval/maxval/step place no behaviour.",
        "pine_ema seeds with the first observation (PINE_SEMANTICS 3.1), a "
        "public-layer choice; the source's ta.ema seeding is unpublished.",
        "plot()/plotshape() and the three var float plot variables are "
        "display-only.",
        "Leverage, margin, funding and the venue's contract-step rounding are "
        "not modelled (PINE_SEMANTICS 1.6, 2.4).",
    ]

    def pine_indicators(self, dataframe, params):
        close = dataframe["close"]
        low = dataframe["low"]
        high = dataframe["high"]
        ema5 = ta.pine_ema(close, int(params["emaLength"]))
        # isAlertCandle = low > ema5 and low[1] > ema5[1]
        is_alert_candle = (low > ema5) & (low.shift(1) > ema5.shift(1))
        is_alert_candle = is_alert_candle.fillna(False)
        # entryCondition = isAlertCandle[1] and low <= low[1]
        entry_condition = is_alert_candle.shift(1, fill_value=False) & (low <= low.shift(1))
        entry_condition = entry_condition.fillna(False)
        # stopLoss = high[1]; target = low[1] - (high[1] - low[1]) * ratio
        stop_loss = high.shift(1)
        risk_reward = float(params["riskRewardRatio"])
        target = low.shift(1) - (high.shift(1) - low.shift(1)) * risk_reward
        dataframe["pine_ema5"] = ema5
        dataframe["pine_is_alert_candle"] = is_alert_candle
        dataframe["pine_entry_condition"] = entry_condition
        dataframe["pine_stop_loss"] = stop_loss
        dataframe["pine_target"] = target
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "entry_condition": dataframe["pine_entry_condition"].to_numpy(),
            "stop_loss": dataframe["pine_stop_loss"].to_numpy(),
            "target": dataframe["pine_target"].to_numpy(),
        }

    def pine_script(self, broker, i, ctx):
        # if (entryCondition)
        #     strategy.entry("Short", strategy.short, stop=stopLoss, limit=target)
        if not ctx["entry_condition"][i]:
            return
        stop_loss = ctx["stop_loss"][i]
        target = ctx["target"][i]
        # A level that does not exist cannot be an order; the condition itself
        # needs low[1]/high[1], so this only guards the frame's first bars.
        if not (np.isfinite(stop_loss) and np.isfinite(target)):
            return
        broker.entry("Short", "short", stop=float(stop_loss), limit=float(target))
