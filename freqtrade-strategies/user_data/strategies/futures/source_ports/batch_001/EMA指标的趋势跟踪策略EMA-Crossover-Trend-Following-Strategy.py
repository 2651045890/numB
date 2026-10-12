"""Port of sources/SM_793c7bd9896bf5b5.pine
(batch_001/EMA指标的趋势跟踪策略EMA-Crossover-Trend-Following-Strategy.md).

Pine v4. A two-EMA trend follower with an OCA exit, written in this order:

    emaShort = ema(close, 9)
    emaLong  = ema(close, 21)
    strategy.entry("Buy", strategy.long, when=crossover(emaShort, emaLong))
    strategy.close("Buy", when=crossunder(emaShort, emaLong))
    atrValue = atr(14)                       // computed, never referenced
    stopLossLevel = close * (1 - 0.01)
    takeProfitLevel = close * 2
    strategy.exit("Take Profit/Stop Loss", from_entry="Buy",
                  loss=stopLossLevel, profit=takeProfitLevel)

`strategy()` declares only `title` and `overlay`, so every other property is
Pine's documented default: `fixed` sizing of 1 contract, no commission,
`pyramiding = 0`, initial capital 1000000, `process_orders_on_close = false`.
The /*backtest header declares `period: 1d` on Futures_Binance BTC_USDT, so
`timeframe` is "1d" (its `basePeriod: 1h` is the FMZ backtester's intrabar fill
granularity, not the strategy's period).

The order of the three calls is load-bearing and is preserved verbatim: entry,
then `strategy.close`, then `strategy.exit`. The exit is re-issued on EVERY bar
and bound to `from_entry="Buy"`, so while flat it is a Pine no-op, and the copy
resting when the entry fills is the one that armed on the signal bar.

FIDELITY -- translation choices and source/original mismatches:

1. `loss=` / `profit=` IN `strategy.exit` ARE TICK DISTANCES, NOT PRICES
   (Pine_SEMANTICS.md section 3.5). The source passes PRICE-valued expressions
   into both -- `close * (1 - 0.01)` and `close * 2` -- so what the platform
   actually rests is a stop `close * 0.99 * mintick` away and a take-profit
   `close * 2 * mintick` away, i.e. roughly 9.9% and 20% of the price on BTC at
   mintick 0.1, rather than the 1% / "2x" the input names suggest. This is a
   bug in the source, and it is reproduced as written rather than corrected:
   the port passes the same two expressions as `loss=` / `profit=` and lets the
   engine apply `mintick` exactly as the platform would.
2. `mintick` is exchange metadata the source never pins down. The port keeps
   the base class's 0.1 (BTC_USDT futures tick), which is also what its
   PineBrokerConfig receives, so the two cannot drift apart. A different venue
   tick would rescale both exit distances.
3. The source computes `atrValue = atr(14)` and never references it again -- it
   is not plotted and feeds no order. The port computes the same series into
   `pine_atr14` so the formula is on the record, and reads it nowhere.
4. `plot(emaShort, ...)` / `plot(emaLong, ...)` are display-only and are not
   reproduced.
5. The source md's argument table lists `v_input_3` as `true` with the
   description "Stop Loss (%)". That is FMZ's rendering of an integer `1`
   through the bool column of its table: the source's own default is `input(1)`,
   divided by 100 at the assignment. The port declares the INPUT default (1),
   not the rendered `true`, and applies the `/100` where the source does.
6. `ta.ema`'s seeding rule is not published by TradingView; pine_ta seeds with
   the first non-na value (Pine_SEMANTICS.md section 3.1). Both EMAs therefore
   converge from a first-value seed rather than an SMA seed.
7. The exit is a resting stop/limit pair, so it fills INSIDE a bar on the
   original platform. The engine resolves the two legs as an OCA group against
   each bar's range and exposes them as pine_stop_level / pine_limit_level;
   run_pine emits no next-open exit signal for them, and the port base mirrors
   the stop into `custom_stoploss` and the limit into the ROI hooks. A bar that
   spans both legs takes the price worse for the position -- intrabar path is
   not knowable from OHLC (Pine_SEMANTICS.md section 2, item 2).
8. Leverage, margin, liquidation, funding and the venue's contract-step
   rounding are not modelled; the chain verifier measures the step rounding
   separately instead of treating it as a signal difference.
"""
import numpy as np  # noqa: F401  (kept for symmetry with the other ports)

from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


class SMEmaCrossoverTrendFollowing_793c7b(PinePortBase, IStrategy):
    source_id = "SM_793c7bd9896bf5b5"
    source_file = "EMA指标的趋势跟踪策略EMA-Crossover-Trend-Following-Strategy.md"
    timeframe = "1d"
    # No short entry exists anywhere in the source: the only entry is
    # `strategy.entry("Buy", strategy.long)`.
    can_short = False
    source_defaults: dict = {
        # input(9, title="Short EMA Period")
        "shortPeriod": 9,
        # input(21, title="Long EMA Period")
        "longPeriod": 21,
        # input(1, title="Stop Loss (%)")  -- the source divides this by 100
        "stopLossPercent": 1,
        # input(2, title="Take Profit Multiplier")
        "takeProfitMultiplier": 2,
    }
    # strategy("EMA Crossover Strategy", overlay=true): title and overlay only,
    # so Pine's documented defaults apply -- fixed / 1 contract, 0% commission,
    # pyramiding 0, initial capital 1000000.
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    # syminfo.mintick: the source's own exchange (Futures_Binance BTC_USDT)
    # quotes in 0.1. Declared explicitly so the stop/take-profit tick distances
    # and the engine's PineBrokerConfig.mintick cannot drift apart.
    source_mintick = 0.1
    source_reproduce_stops = True
    source_fidelity_notes = [
        "The stop and take-profit are tick distances, not prices, while the "
        "source passes prices into `loss=` / `profit=` (Pine_SEMANTICS 3.5). "
        "Reproduced as written, so the resting stop is close*0.99*mintick and "
        "the take-profit close*2*mintick away -- about 9.9% and 20% of price at "
        "mintick 0.1, NOT the 1% and '2x' the input names imply. A source bug, "
        "not silently corrected.",
        "syminfo.mintick is exchange metadata the source never states; the port "
        "uses 0.1 (BTC_USDT futures tick). Both exit distances scale with it, "
        "so a different venue tick would change every trade.",
        "`atrValue = atr(14)` is computed by the source and then never "
        "referenced: it feeds no order and no plot. The port computes the same "
        "series into pine_atr14 and reads it nowhere.",
        "Call order preserved verbatim: entry, then strategy.close, then "
        "strategy.exit. The exit is re-issued every bar and bound to "
        "from_entry=\"Buy\", so it is a no-op while flat.",
        "The exit is a resting stop/limit pair: the engine fills it inside the "
        "bar and publishes pine_stop_level / pine_limit_level; the port base "
        "mirrors the stop into custom_stoploss and the limit into the ROI "
        "hooks. No next-open exit signal is emitted for it.",
        "The md's argument table renders v_input_3 as `true`; the source's own "
        "default is the integer 1 (then /100). The port declares 1.",
        "ta.ema seeding: pine_ta seeds with the first non-na value, not an SMA "
        "of the first `length` bars (Pine_SEMANTICS 3.1, a parity risk).",
        "plot() calls are display-only and are not reproduced.",
    ]

    def pine_indicators(self, dataframe, params):
        close = dataframe["close"]
        # emaShort = ema(close, shortPeriod); emaLong = ema(close, longPeriod)
        ema_short = ta.pine_ema(close, int(params["shortPeriod"]))
        ema_long = ta.pine_ema(close, int(params["longPeriod"]))
        dataframe["pine_ema_short"] = ema_short
        dataframe["pine_ema_long"] = ema_long
        # strategy.entry("Buy", strategy.long, when=crossover(emaShort, emaLong))
        dataframe["pine_cross_up"] = ta.pine_crossover(ema_short, ema_long)
        # strategy.close("Buy", when=crossunder(emaShort, emaLong))
        dataframe["pine_cross_down"] = ta.pine_crossunder(ema_short, ema_long)
        # atrValue = atr(14) -- computed by the source, never referenced.
        dataframe["pine_atr14"] = ta.pine_atr(dataframe, 14)
        # stopLossLevel = close * (1 - stopLossPercent), takeProfitLevel = close * takeProfitMultiplier.
        # Both are TICK COUNTS in strategy.exit, so they stay tick counts here.
        stop_loss_percent = float(params["stopLossPercent"]) / 100.0
        dataframe["pine_stop_ticks"] = close * (1.0 - stop_loss_percent)
        dataframe["pine_profit_ticks"] = close * float(params["takeProfitMultiplier"])
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "cross_up": dataframe["pine_cross_up"].to_numpy(dtype=bool),
            "cross_down": dataframe["pine_cross_down"].to_numpy(dtype=bool),
            "stop_ticks": dataframe["pine_stop_ticks"].to_numpy(dtype=float),
            "profit_ticks": dataframe["pine_profit_ticks"].to_numpy(dtype=float),
        }

    def pine_script(self, broker, i, ctx):
        # strategy.entry("Buy", strategy.long, when=crossover(emaShort, emaLong))
        if ctx["cross_up"][i]:
            broker.entry("Buy", "long")
        # strategy.close("Buy", when=crossunder(emaShort, emaLong))
        if ctx["cross_down"][i]:
            broker.close("Buy")
        # strategy.exit("Take Profit/Stop Loss", from_entry="Buy",
        #               loss=stopLossLevel, profit=takeProfitLevel)
        # Unconditional in the source: re-issued on every bar, and a no-op
        # (entry not open) while flat.
        broker.exit(
            "Take Profit/Stop Loss",
            from_entry="Buy",
            loss=float(ctx["stop_ticks"][i]),
            profit=float(ctx["profit_ticks"][i]),
        )
