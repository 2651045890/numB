"""Port of sources/SM_b9c452e955f0d0be.pine
(batch_001/EMA交叉RSI中性区域动态风控策略-Dynamic-EMA-Crossover-RSI-Neutral-Zone-Strategy-with-ATR-Risk-Management.md).

Pine v5. EMA(20)/EMA(50) cross filtered by RSI, with ATR-distance stop and
target legs on both the entry and the exit:

    emaFast = ta.ema(close, 20)
    emaSlow = ta.ema(close, 50)
    rsi     = ta.rsi(close, 14)
    atr     = ta.atr(14)
    sl = atr * riskMultiplier          // riskMultiplier = 1
    tp = atr * riskMultiplier

    buyCond  = ta.crossover(emaFast, emaSlow)   and (rsi > 40 and rsi < 70)
    sellCond = ta.crossunder(emaFast, emaSlow)  and (rsi < 60 and rsi > 30)

    if (buyCond)
        strategy.entry("Buy",  strategy.long,  stop=low - sl, limit=high + tp)
    if (sellCond)
        strategy.entry("Sell", strategy.short, stop=high + sl, limit=low - tp)

    strategy.exit("Exit Buy",  from_entry="Buy",  stop=low - sl, limit=high + tp)
    strategy.exit("Exit Sell", from_entry="Sell", stop=high + sl, limit=low - tp)

`strategy()` declares `default_qty_type=strategy.fixed` and
`default_qty_value=1` and nothing else, so initial capital is Pine's documented
1000000, commission 0%, pyramiding 0 and `process_orders_on_close=false`. The
`/*backtest` header declares `period: 2m` on Futures_Binance TRX_USD, so
`timeframe` is "2m" -- a period with no local history here, so the chain
comparison is reported as `skipped_no_local_data` rather than passed.

The two entries carry BOTH a `stop=` and a `limit=`, and both exits are
re-issued unconditionally on every bar (no `when=`), which is what keeps their
levels current: `strategy.exit` with an id that is already resting REPLACES the
order, so the level live during bar t is the one computed from bar t-1's
high/low/ATR.

FIDELITY:

* PINE_SEMANTICS 2.11 (framework boundary): an entry carrying a resting price
  cannot be expressed to Freqtrade, and the engine models an entry that has both
  `stop=` and `limit=` as a plain STOP entry -- the `limit=` leg of the entry is
  not modelled at all (`PineBroker.entry` picks `stop` when both are given).
  Here that is nearly harmless in the engine: `stop = low - sl` sits below the
  bar's own low, so the next bar's high clears it and the fill lands on the
  open, which is what the framework's projected next-open entry does too. It is
  NOT a faithful reproduction of a stop-limit entry on the original platform,
  and it is recorded as such rather than smoothed over.
* The exits carry the same two legs, and there the modelling is exact for what
  the framework can carry: the engine resolves both, and `pine_stop_level` /
  `pine_limit_level` hand the stop to `custom_stoploss` and the target to the
  ROI hooks (PINE_SEMANTICS 1.8), so `source_reproduce_stops` is True.
* The exits are issued on every bar, including bars where the position is flat
  or on the wrong side. The engine keeps an exit whose `from_entry` entry is not
  open resting but neither fills nor publishes it (PINE_SEMANTICS 1.12), which
  is what stops `Exit Buy` from closing a short.
* `ta.atr(14)` is `ta.rma(ta.tr(true), 14)`; the port uses `pine_ta.pine_atr`,
  which implements exactly that. Its 14 comes from a literal in the source, not
  from an `input()`, and stays a literal here.
* PINE_SEMANTICS 3.7: `pine_tr` gives the first bar `high - low` whereas Pine's
  `ta.tr(true)` (handle_na=true) does the same, so the RMA seed point agrees.
  `ta.tr`'s default (handle_na=false) does not apply -- the source uses the
  one-argument `ta.atr`, which is the handle_na=true form.
* PINE_SEMANTICS 3.1 (modelled choice): `pine_ema` seeds with the first non-na
  observation and an na observation does not advance the recursion;
  TradingView's seeding rule is unpublished, so early signals are an unresolved
  parity risk. 3.3: `pine_rsi` returns 100 with no losses in the window and na
  until the average gain/loss exists.
* The `plot` / `plotshape` calls and `overlay=true` are display-only; the
  `rsiOB` / `rsiOS` inputs feed the conditions, not the plots.
* PINE_SEMANTICS 1.6 / 5.1: the venue's contract-step rounding and non-zero
  taker fees are not modelled; the source declares 0% commission, which is the
  cost basis the port carries.
* Leverage, margin, liquidation and funding are not modelled.
"""
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


class SMDynamicEmaCrossoverRsiNeutralZone_b9c452(PinePortBase, IStrategy):
    source_id = "SM_b9c452e955f0d0be"
    source_file = (
        "EMA交叉RSI中性区域动态风控策略-Dynamic-EMA-Crossover-RSI-Neutral-Zone-"
        "Strategy-with-ATR-Risk-Management.md"
    )
    timeframe = "2m"
    # strategy.entry(..., strategy.short, ...) exists.
    can_short = True
    source_defaults: dict = {
        "emaFastLength": 20,
        "emaSlowLength": 50,
        "rsiLength": 14,
        "rsiOB": 70,
        "rsiOS": 30,
        "riskMultiplier": 1.0,
    }
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    # Both exit arms rest a stop level the engine can mirror.
    source_reproduce_stops = True
    source_fidelity_notes = [
        "PINE_SEMANTICS 2.11: both entries pass BOTH stop= and limit=. The "
        "engine's PineBroker.entry() collapses that to a plain STOP entry -- the "
        "entry's limit leg is not modelled -- and Freqtrade's strategy interface "
        "has no way to express a resting entry at all. In practice the entries "
        "here behave as next-open market entries on both sides (stop = low - sl "
        "is below the bar's low, stop = high + sl is above its high), which is "
        "what the projected next-open signal does too, but the original "
        "platform's stop-limit semantics are NOT reproduced. Recorded, not "
        "approximated away.",
        "The two strategy.exit calls have no `when=` and are re-issued on every "
        "bar; an exit id that is already resting is REPLACED, so the level live "
        "during bar t is the one computed from bar t-1's high/low/ATR. The "
        "engine and the projected pine_stop_level / pine_limit_level series both "
        "read it from the same ledger, so the framework sees that same level.",
        "strategy.exit(id, from_entry=...) is a no-op while the named entry is "
        "not open (PINE_SEMANTICS 1.12): both arms are called every bar, and the "
        "one for the side that is not held neither fills nor publishes levels.",
        "source_reproduce_stops is True: the stop legs are resting levels, so "
        "they reach Freqtrade through custom_stoploss while the limit legs reach "
        "the ROI hooks (PINE_SEMANTICS 1.8).",
        "ta.atr(14)'s length is a literal in the source, not an input(), and "
        "stays a literal. pine_ta.pine_atr is ta.rma(ta.tr(true), 14), which is "
        "the v5 one-argument ta.atr.",
        "PINE_SEMANTICS 3.1 (modelled choice): pine_ema seeds with the first "
        "non-na observation and an na observation does not advance the "
        "recursion; TradingView's seeding rule is unpublished, so the early part "
        "of the EMA cross series is an unresolved parity risk. 3.3: pine_rsi "
        "returns 100 with no losses and na until the average gain/loss exists.",
        "The plot / plotshape calls and overlay=true are display-only; rsiOB and "
        "rsiOS feed the entry conditions, not the plots.",
        "PINE_SEMANTICS 1.6 / 5.1: the venue's contract-step rounding and "
        "non-zero taker fees are not modelled; the source declares 0% "
        "commission, which is the cost basis the port carries.",
        "Leverage, margin, liquidation and funding are not modelled.",
    ]

    def pine_indicators(self, dataframe, params):
        close = dataframe["close"]
        ema_fast = ta.pine_ema(close, int(params["emaFastLength"]))
        ema_slow = ta.pine_ema(close, int(params["emaSlowLength"]))
        rsi = ta.pine_rsi(close, int(params["rsiLength"]))

        # atr = ta.atr(14); sl = atr * riskMultiplier; tp = atr * riskMultiplier
        atr = ta.pine_atr(dataframe, 14)
        risk = float(params["riskMultiplier"])
        sl = atr * risk
        tp = atr * risk

        rsi_ob = float(params["rsiOB"])
        rsi_os = float(params["rsiOS"])
        # buyCond  = ta.crossover(emaFast, emaSlow)  and (rsi > 40 and rsi < rsiOB)
        buy_cond = (
            ta.pine_crossover(ema_fast, ema_slow)
            & (rsi > 40.0)
            & (rsi < rsi_ob)
        )
        # sellCond = ta.crossunder(emaFast, emaSlow) and (rsi < 60 and rsi > rsiOS)
        sell_cond = (
            ta.pine_crossunder(ema_fast, ema_slow)
            & (rsi < 60.0)
            & (rsi > rsi_os)
        )

        dataframe["pine_ema_fast"] = ema_fast
        dataframe["pine_ema_slow"] = ema_slow
        dataframe["pine_rsi"] = rsi
        dataframe["pine_atr"] = atr
        dataframe["pine_sl"] = sl
        dataframe["pine_tp"] = tp
        dataframe["pine_buy_cond"] = buy_cond
        dataframe["pine_sell_cond"] = sell_cond
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "buy_cond": dataframe["pine_buy_cond"].to_numpy(),
            "sell_cond": dataframe["pine_sell_cond"].to_numpy(),
            "low": dataframe["low"].to_numpy(),
            "high": dataframe["high"].to_numpy(),
            "sl": dataframe["pine_sl"].to_numpy(),
            "tp": dataframe["pine_tp"].to_numpy(),
        }

    def pine_script(self, broker, i, ctx):
        low = ctx["low"][i]
        high = ctx["high"][i]
        sl = ctx["sl"][i]
        tp = ctx["tp"][i]

        # if (buyCond)
        #     strategy.entry("Buy", strategy.long, stop=low - sl, limit=high + tp)
        if ctx["buy_cond"][i]:
            broker.entry("Buy", "long", stop=low - sl, limit=high + tp)
        # if (sellCond)
        #     strategy.entry("Sell", strategy.short, stop=high + sl, limit=low - tp)
        if ctx["sell_cond"][i]:
            broker.entry("Sell", "short", stop=high + sl, limit=low - tp)

        # strategy.exit("Exit Buy", from_entry="Buy", stop=low - sl, limit=high + tp)
        broker.exit("Exit Buy", from_entry="Buy", stop=low - sl, limit=high + tp)
        # strategy.exit("Exit Sell", from_entry="Sell", stop=high + sl, limit=low - tp)
        broker.exit("Exit Sell", from_entry="Sell", stop=high + sl, limit=low - tp)
