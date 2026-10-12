"""Port of sources/SM_08a9fa4961942da8.pine (batch_001/EMA与RSI交叉策略-EMA-RSI-Crossover-Strategy.md).

Pine v5, two-sided, one-bar-per-entry. The whole script:

    rsi_period = input.int(7, "RSI Period")
    rsi_val    = ta.rsi(close[1], rsi_period)      // NOTE: the PREVIOUS close
    buyRsiFlag  = rsi_val < 20
    sellRsiFlag = rsi_val > 80

    ema      = ta.ema(close, 50)                   // 50 is a literal, not an input
    buyFlag  = ema > close ? true : false          // price BELOW the EMA
    sellFlag = ema < close ? true : false          // price ABOVE the EMA

    atr_length = input(14, title="ATR Length")
    atr_value  = ta.atr(atr_length)
    candleBody = math.abs(close - open)
    slDist     = atr_value + candleBody

    stop_loss_long    = close - slDist             // anchored to the BAR CLOSE
    take_profit_long  = close + (1.2 * slDist)
    stop_loss_short   = high + slDist              // anchored to the BAR HIGH
    take_profit_short = high - (1.2 * slDist)

    if (buyFlag and buyRsiFlag and strategy.opentrades >= 0 and greenCandle)
        strategy.entry("Long", strategy.long)
        strategy.exit("Take Profit/Stop Loss", "Long", stop=stop_loss_long, limit=take_profit_long)

    if (sellFlag and sellRsiFlag and strategy.opentrades <= 0 and redCandle)
        strategy.entry("Short", strategy.short)
        strategy.exit("Take Profit/Stop Loss", "Short", stop=stop_loss_short, limit=take_profit_short)

with `greenCandle = close > close[1]` and `redCandle = close < close[1]`.

THE TWO `strategy.opentrades` GUARDS ARE NOT SYMMETRIC, and the asymmetry is
load-bearing. `>= 0` is unconditionally true (opentrades is never negative), so
the long side has NO position gate at all; `<= 0` gates the short side to a flat
account. Both are reproduced literally rather than "tidied" to the same shape.

THE EXIT IS RE-ISSUED ON EVERY BAR THE ENTRY CONDITION HOLDS, not only on the
bar the position opens. With `pyramiding=0` a repeated same-direction entry is
blocked, but the `strategy.exit` next to it is not an entry and is placed anyway,
so the resting stop/target is REPLACED with levels recomputed from that bar's
own close/high. That is why the levels are read per bar here instead of frozen at
the fill.

`strategy()` declares only `overlay=true, margin_long=100, margin_short=100`
(`margin_*=100` is 100% margin, i.e. no leverage effect). Everything else is
Pine's documented default: `default_qty_type=strategy.fixed`, `default_qty_value`
1, commission 0%, pyramiding 0, initial capital 1000000, and the entry calls pass
no `qty`, so each order is 1 contract. `process_orders_on_close` is left at false,
which matches the engine's bar-close evaluation / next-open fill.

The `/*backtest` header declares `period: 1d` on Futures_Binance BTC_USDT, so
`timeframe` is "1d"; its `basePeriod: 1h` is the FMZ backtester's own fill
granularity, not the strategy's period.

FIDELITY:

* The md describes the stop/target as anchored to the ENTRY price ("止损价位为开仓
  价格减去..."), but the source anchors them to the SIGNAL BAR's own close for the
  long side and to the bar's HIGH for the short side. The entry itself fills on
  the NEXT bar's open, so the source's levels are not entry-relative at all.
  Recorded, not "corrected" toward the md: the source is the authority (rule 2).
* `close > open != close[1] > open[1]` (the display-only `is_body_bigger_long`)
  parses in Pine as `(close > open) != (close[1] > open[1])` -- `<`/`>` bind
  tighter than `!=`. It feeds a `bgcolor()` only and places no order, so it is not
  reproduced; nothing behavioural depends on it.
* `rsi_val` is computed on `close[1]`, i.e. a one-bar-lagged close series, not on
  `close`. Reproduced as `pine_rsi(close.shift(1), 7)`. Computing it on `close`
  would be a different strategy.
* `ta.atr(length)` is `ta.rma(ta.tr(true), length)`; `pine_atr` uses
  `pine_tr(handle_na=True)`, so the first bar contributes `high - low` and the
  RMA seeds there. PINE_SEMANTICS.md 3.7 records the `ta.tr` (handle_na=false)
  seeding offset; `ta.atr` is not affected by it.
* Both `strategy.exit` calls share the id "Take Profit/Stop Loss" and differ only
  by `from_entry`. The engine replaces a resting exit by order id, so a
  same-bar re-issue of the other side would replace this one -- but `buyFlag` and
  `sellFlag` (`ema > close` / `ema < close`) can never both be true on one bar, so
  the two branches are mutually exclusive and the collision is unreachable. Noted
  rather than reworked.
* `margin_long=100` / `margin_short=100`, leverage, liquidation and funding are
  not modelled (the engine is an unlevered cash simulation); the venue's
  contract-step rounding is not modelled either, and the chain verifier measures
  that separately (PINE_SEMANTICS.md 1.6, 二.4).
* md and source agree on the RSI thresholds (20/80), the EMA length (50) and the
  ATR length (14); the md's "较短周期EMA上穿较长周期EMA" framing does not match the
  source at all (the source never compares two EMAs -- it compares price to one
  EMA), and the md's step 3 is what the code actually does.
"""
from __future__ import annotations

from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


class SMEmaRsiCross_08a9fa(PinePortBase, IStrategy):
    source_id = "SM_08a9fa4961942da8"
    source_file = "EMA与RSI交叉策略-EMA-RSI-Crossover-Strategy.md"
    timeframe = "1d"
    can_short = True
    source_defaults: dict = {
        # rsi_period = input.int(7, "RSI Period")
        "rsi_period": 7,
        # atr_length = input(14, title="ATR Length")
        "atr_length": 14,
    }
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    source_reproduce_stops = True
    source_fidelity_notes = [
        "rsi_val is computed on close[1] (the PREVIOUS close), not close; "
        "pine_rsi(close.shift(1), 7) reproduces that. Any other source series "
        "would be a different strategy.",
        "The long side's guard is `strategy.opentrades >= 0` (unconditionally "
        "true, so no position gate) while the short side's is `<= 0` (flat only). "
        "The asymmetry is the source's and is reproduced literally.",
        "The exit is re-issued on every bar the entry condition holds, so the "
        "resting stop/target is replaced with levels recomputed from that bar's "
        "close/high even when the (pyramiding-blocked) entry is not.",
        "Stop/target anchors: long legs off the signal bar's CLOSE, short legs "
        "off the signal bar's HIGH. The md says both are entry-price-relative "
        "('% stop from the entry price'), which is not what the code does. The "
        "source is authoritative; recorded, not changed.",
        "`is_body_bigger_long` (with its `close > open != close[1] > open[1]` "
        "boolean-mismatch expression) drives a bgcolor() only and places no "
        "order; not reproduced.",
        "`strategy.exit` is called with the same id for both sides but the two "
        "branches are mutually exclusive per bar, so the engine's same-id "
        "replacement can never collide across sides.",
        "Both strategy.exit calls carry stop= AND limit=, i.e. an OCA pair; "
        "reproduced as the broker's exit() with both legs so neither the stop "
        "nor the take-profit is silently dropped (PINE_SEMANTICS.md 1.8).",
        "ta.atr(length) is ta.rma(ta.tr(true), length); pine_atr matches, so the "
        "3.7 ta.tr handle_na seeding offset does not apply here.",
        "margin_long=100 / margin_short=100, leverage, liquidation, funding and "
        "contract-step rounding are not modelled by the engine.",
        "The md's overview describes 'short EMA crossing a longer EMA'; the "
        "source compares price to a single 50-period EMA and has no second EMA. "
        "Recorded as an md/source disagreement; the source is followed.",
    ]

    def pine_indicators(self, dataframe, params):
        close = dataframe["close"]
        high = dataframe["high"]
        source_open = dataframe["open"]

        # rsi_val = ta.rsi(close[1], rsi_period)
        rsi_val = ta.pine_rsi(close.shift(1), int(params["rsi_period"]))
        # ema = ta.ema(close, 50)
        ema = ta.pine_ema(close, 50)
        # atr_value = ta.atr(atr_length)
        atr_value = ta.pine_atr(dataframe, int(params["atr_length"]))

        # candleBody = math.abs(close - open); slDist = atr_value + candleBody
        candle_body = (close - source_open).abs()
        sl_dist = atr_value + candle_body

        dataframe["pine_rsi"] = rsi_val
        dataframe["pine_ema50"] = ema
        dataframe["pine_atr"] = atr_value
        dataframe["pine_sl_dist"] = sl_dist
        # stop_loss_long = close - slDist / take_profit_long = close + 1.2 * slDist
        dataframe["pine_stop_loss_long"] = close - sl_dist
        dataframe["pine_take_profit_long"] = close + 1.2 * sl_dist
        # stop_loss_short = high + slDist / take_profit_short = high - 1.2 * slDist
        dataframe["pine_stop_loss_short"] = high + sl_dist
        dataframe["pine_take_profit_short"] = high - 1.2 * sl_dist

        # buyRsiFlag = rsi_val < 20 / sellRsiFlag = rsi_val > 80; an na on either
        # side of a Pine comparison is false.
        dataframe["pine_buy_rsi_flag"] = (rsi_val < 20.0).astype(bool)
        dataframe["pine_sell_rsi_flag"] = (rsi_val > 80.0).astype(bool)
        # buyFlag = ema > close / sellFlag = ema < close
        dataframe["pine_buy_flag"] = (ema > close).astype(bool)
        dataframe["pine_sell_flag"] = (ema < close).astype(bool)
        # greenCandle = close > close[1] / redCandle = close < close[1]
        previous_close = close.shift(1)
        dataframe["pine_green_candle"] = (close > previous_close).astype(bool)
        dataframe["pine_red_candle"] = (close < previous_close).astype(bool)
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "buy_flag": dataframe["pine_buy_flag"].to_numpy(dtype=bool),
            "sell_flag": dataframe["pine_sell_flag"].to_numpy(dtype=bool),
            "buy_rsi_flag": dataframe["pine_buy_rsi_flag"].to_numpy(dtype=bool),
            "sell_rsi_flag": dataframe["pine_sell_rsi_flag"].to_numpy(dtype=bool),
            "green_candle": dataframe["pine_green_candle"].to_numpy(dtype=bool),
            "red_candle": dataframe["pine_red_candle"].to_numpy(dtype=bool),
            "stop_loss_long": dataframe["pine_stop_loss_long"].to_numpy(dtype=float),
            "take_profit_long": dataframe["pine_take_profit_long"].to_numpy(dtype=float),
            "stop_loss_short": dataframe["pine_stop_loss_short"].to_numpy(dtype=float),
            "take_profit_short": dataframe["pine_take_profit_short"].to_numpy(dtype=float),
        }

    def pine_script(self, broker, i, ctx):
        # if (buyFlag and buyRsiFlag and strategy.opentrades >= 0 and greenCandle)
        #     strategy.entry("Long", strategy.long)
        #     strategy.exit("Take Profit/Stop Loss", "Long", stop=..., limit=...)
        if (ctx["buy_flag"][i] and ctx["buy_rsi_flag"][i]
                and broker.open_trades >= 0 and ctx["green_candle"][i]):
            broker.entry("Long", "long")
            broker.exit(
                "Take Profit/Stop Loss",
                from_entry="Long",
                stop=float(ctx["stop_loss_long"][i]),
                limit=float(ctx["take_profit_long"][i]),
            )

        # if (sellFlag and sellRsiFlag and strategy.opentrades <= 0 and redCandle)
        #     strategy.entry("Short", strategy.short)
        #     strategy.exit("Take Profit/Stop Loss", "Short", stop=..., limit=...)
        if (ctx["sell_flag"][i] and ctx["sell_rsi_flag"][i]
                and broker.open_trades <= 0 and ctx["red_candle"][i]):
            broker.entry("Short", "short")
            broker.exit(
                "Take Profit/Stop Loss",
                from_entry="Short",
                stop=float(ctx["stop_loss_short"][i]),
                limit=float(ctx["take_profit_short"][i]),
            )
