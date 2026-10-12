"""Port of sources/SM_979624b1af03d75f.pine
(batch_001/Flawless-Victory-DCA-动量与波动率策略Flawless-Victory-DCA-Momentum-and-Volatility-Strategy.md).

Pine v4, long only. RSI(14) and a 1.0-deviation 20-bar Bollinger Band, with a
DCA branch that only changes the ORDER ID of the entry:

    up   = rma(max(change(src), 0), 14)
    down = rma(-min(change(src), 0), 14)
    rsi  = down == 0 ? 100 : up == 0 ? 0 : 100 - 100 / (1 + up / down)

    basis = sma(src, 20)
    dev   = 1.0 * stdev(src, 20)
    upper = basis + dev
    lower = basis - dev

    BBBuyTrigger  = src < lower          BBSellTrigger  = src > upper
    rsiBuyGuard   = rsi > 42             rsiSellGuard   = rsi > 70
    buy_condition = BBBuyTrigger and rsiBuyGuard
    sell_condition = BBSellTrigger and rsiSellGuard

    if dca_enabled and (hour % dca_interval == 0)
        strategy.entry("DCA Long", strategy.long, when = buy_condition, ...)
    else
        strategy.entry("Long", strategy.long, when = buy_condition, ...)

    strategy.exit("Stoploss/TP", "Long", stop = stoploss_level,
                  limit = takeprofit_level, when = sell_condition, ...)

Note that the buy is a MEAN-REVERSION buy: price BELOW the lower band, yet the
RSI guard demands RSI ABOVE 42. The sell is `src > upper and rsi > 70`, and the
`strategy.exit` legs are 6.604% below and 2.328% above the position's average
entry price -- the take-profit is the TIGHTER of the two.

Two structural properties of this source are load-bearing and are reproduced
rather than repaired (see `source_fidelity_notes`):

* The exit is bound to the entry id `"Long"` (second positional argument of
  `strategy.exit` is `from_entry`). When DCA is enabled the entry id becomes
  `"DCA Long"`, so the exit never matches a live entry and neither the stop nor
  the take-profit is ever applied.
* The exit is only PLACED on bars where `sell_condition` holds (`when=`). It is
  not a permanently armed OCA exit.

`strategy(overlay=true, default_qty_type = strategy.percent_of_equity,
initial_capital = 100000, default_qty_value = 100, pyramiding = 0,
currency = 'USD')`: 100% of a 100000-unit account per entry, no commission
declared (0%), long only -- nothing in the source ever enters short.

The `/*backtest` header declares `period: 1d` on Futures_Binance BTC_USDT, so
`timeframe` is "1d"; its `basePeriod: 1h` is the backtester's fill granularity
for those daily bars and is not modelled.
"""
import numpy as np
import pandas as pd
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


class SMFlawlessVictoryDcaMomentumAndVolatility_979624(PinePortBase, IStrategy):
    source_id = "SM_979624b1af03d75f"
    source_file = (
        "Flawless-Victory-DCA-动量与波动率策略"
        "Flawless-Victory-DCA-Momentum-and-Volatility-Strategy.md"
    )
    timeframe = "1d"
    can_short = False
    source_defaults: dict = {
        # input(6.604, title='Stop Loss %', type=input.float, minval=0.01)/100
        "stoploss_input": 6.604,
        # input(2.328, title='Take Profit %', type=input.float, minval=0.01)/100
        "takeprofit_input": 2.328,
        # input(false, title="Enable DCA")
        "dca_enabled": False,
        # input(1, title="DCA Interval (hours)", type=input.integer)
        "dca_interval": 1,
    }
    # strategy(default_qty_type = strategy.percent_of_equity, initial_capital = 100000,
    #          default_qty_value = 100, pyramiding = 0, currency = 'USD')
    source_qty_type = "percent_of_equity"
    source_qty_value = 100.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 100_000.0
    source_reproduce_stops = True
    source_fidelity_notes = [
        "`strategy.exit(\"Stoploss/TP\", \"Long\", ...)`: the second POSITIONAL "
        "argument is `from_entry`, so the exit is bound to the entry id "
        "\"Long\". The entry id is conditional -- \"DCA Long\" when "
        "`dca_enabled and (hour % dca_interval == 0)` -- so with DCA enabled "
        "(and dca_interval=1, where `hour % 1 == 0` holds on every bar) the "
        "exit's from_entry names an entry that never exists and NEITHER the "
        "stop nor the take-profit is ever applied. Reproduced as written; this "
        "is the source's own coupling, not a transcription slip.",
        "`strategy.exit(...)` carries `when = sell_condition`, so the resting "
        "stop/take order is only PLACED on bars where the sell condition holds. "
        "It is not a permanently armed OCA exit: between sell signals no stop "
        "rests at all, and pine_engine's `_place` replaces the same order id "
        "and drops exit orders once the position is flat. No always-armed exit "
        "was invented.",
        "The stop and take-profit are resting legs (`strategy.exit(stop=..., "
        "limit=...)`), so pine_engine fills them INSIDE the bar and exposes "
        "the levels as `pine_stop_level` / `pine_limit_level`; run_pine does "
        "not project them as next-open exit signals. The port base mirrors the "
        "stop leg into `custom_stoploss`.",
        "`stoploss_level` / `takeprofit_level` are derived from "
        "`strategy.position_avg_price`, which is na while flat. The source "
        "computes them unconditionally on every bar, so na legs are handed to "
        "`strategy.exit` there; NaN levels never trigger, so the port passes "
        "the same na-derived values through rather than guarding them.",
        "The RSI is written out from the source's own expression "
        "(`down == 0 ? 100 : up == 0 ? 0 : 100 - 100 / (1 + up / down)`) "
        "rather than substituted with `pine_ta.pine_rsi`, so the zero and na "
        "branches are the source's, in the source's order.",
        "`sma` and `stdev` are Pine v4 bare builtins; the shared layer's "
        "`pine_sma` (na until the window fills) and `pine_stdev` (population, "
        "ddof=0 -- Pine's `ta.stdev` default `biased=true`) are used. The "
        "Bollinger multiplier `mult = 1.0` is a source LITERAL, not an input.",
        "`len = 14`, `length = 20`, `mult = 1.0`, `RSILowerLevel = 42` and "
        "`RSIUpperLevel = 70` are hard-coded literals in the source, not "
        "inputs, and are reproduced as literals.",
        "CODE vs MD: the markdown's argument table lists `v_input_4` as "
        "`true` for 'DCA Interval (hours)', while the source code is "
        "`input(1, title=\"DCA Interval (hours)\", type=input.integer)`. The "
        "code wins: the default carried is the integer 1.",
        "`hour` is Pine's exchange-time-zone hour (PINE_SEMANTICS 3.4); the "
        "port reads the bar's UTC hour off a UTC index, which is Binance's "
        "exchange time. The DCA branch is inert at the default "
        "`dca_enabled = false`.",
        "`stoploss_input` / `takeprofit_input` carry the PERCENT defaults "
        "(6.604 / 2.328) and the `/100` is part of the script body; that split "
        "is reproduced verbatim -- the parameters hold the input defaults and "
        "pine_script divides by 100.",
        "`currency = 'USD'`, leverage, margin, liquidation, funding and venue "
        "contract-step rounding are not modelled.",
    ]

    def pine_indicators(self, dataframe, params):
        close = dataframe["close"]

        # RSI -- len = 14, src = close, written as the source writes it.
        change = ta.pine_change(close)
        up = ta.pine_rma(np.maximum(change, 0.0), 14)
        down = ta.pine_rma(-np.minimum(change, 0.0), 14)
        up_values = up.to_numpy(dtype=float)
        down_values = down.to_numpy(dtype=float)
        with np.errstate(divide="ignore", invalid="ignore"):
            fallback = 100.0 - 100.0 / (1.0 + up_values / down_values)
        # down == 0 wins over up == 0 (the source's nested ternary order), and
        # both comparisons are false against na, leaving the na fallback.
        rsi = np.where(
            down_values == 0.0, 100.0,
            np.where(up_values == 0.0, 0.0, fallback),
        )
        rsi = pd.Series(rsi, index=dataframe.index, dtype=float)

        # Bollinger Bands -- length = 20, mult = 1.0 (both literals).
        basis = ta.pine_sma(close, 20)
        dev = 1.0 * ta.pine_stdev(close, 20)
        upper = basis + dev
        lower = basis - dev

        bb_buy_trigger = (close < lower).to_numpy(bool)
        bb_sell_trigger = (close > upper).to_numpy(bool)
        rsi_buy_guard = (rsi > 42).to_numpy(bool)
        rsi_sell_guard = (rsi > 70).to_numpy(bool)

        dataframe["pine_rsi"] = rsi
        dataframe["pine_basis"] = basis
        dataframe["pine_dev"] = dev
        dataframe["pine_upper"] = upper
        dataframe["pine_lower"] = lower
        dataframe["pine_buy_condition"] = bb_buy_trigger & rsi_buy_guard
        dataframe["pine_sell_condition"] = bb_sell_trigger & rsi_sell_guard

        # hour % dca_interval == 0
        interval = int(params["dca_interval"])
        dataframe["pine_dca_gate"] = (dataframe.index.hour % interval) == 0
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "buy_condition": dataframe["pine_buy_condition"].to_numpy(bool),
            "sell_condition": dataframe["pine_sell_condition"].to_numpy(bool),
            "dca_gate": dataframe["pine_dca_gate"].to_numpy(bool),
            "dca_enabled": bool(params["dca_enabled"]),
        }

    def pine_script(self, broker, i, ctx):
        params = self.source_parameters()

        # stoploss_level = strategy.position_avg_price * (1 - stoploss_input)
        # takeprofit_level = strategy.position_avg_price * (1 + takeprofit_input)
        # na while flat, exactly as the source computes them.
        avg_price = broker.position_avg_price
        stoploss_level = avg_price * (1.0 - params["stoploss_input"] / 100.0)
        takeprofit_level = avg_price * (1.0 + params["takeprofit_input"] / 100.0)

        # if dca_enabled and (hour % dca_interval == 0)
        #     strategy.entry("DCA Long", strategy.long, when = buy_condition, ...)
        # else
        #     strategy.entry("Long", strategy.long, when = buy_condition, ...)
        if ctx["dca_enabled"] and ctx["dca_gate"][i]:
            broker.entry("DCA Long", "long", when=ctx["buy_condition"][i])
        else:
            broker.entry("Long", "long", when=ctx["buy_condition"][i])

        # strategy.exit("Stoploss/TP", "Long", stop = stoploss_level,
        #               limit = takeprofit_level, when = sell_condition, ...)
        broker.exit(
            "Stoploss/TP", "Long",
            stop=stoploss_level, limit=takeprofit_level,
            when=ctx["sell_condition"][i],
        )
