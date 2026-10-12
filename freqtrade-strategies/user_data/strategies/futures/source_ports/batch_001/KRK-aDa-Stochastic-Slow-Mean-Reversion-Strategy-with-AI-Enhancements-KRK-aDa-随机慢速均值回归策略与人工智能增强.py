"""Port of sources/SM_cc0d5fa7c9eddb7f.pine (batch_001/KRK-aDa-Stochastic-Slow-Mean-Reversion-Strategy-with-AI-Enhancements-KRK-aDa-随机慢速均值回归策略与人工智能增强.md).

Pine v5, both sides. A slow stochastic against a 200-bar SMA trend filter, with
a dummy "AI" input (RSI(14) > 50) and four entry paths:

    k = ta.sma(ta.stoch(close, high, low, 26), 3)
    d = ta.sma(k, 3)
    co = ta.crossover(k, d)
    cu = ta.crossunder(k, d)

    ema200 = ta.sma(close, 200)                   // an SMA, despite the name
    ai_signal = ta.rsi(close, 14) > 50 ? 1 : -1

    longCondition  = ta.crossover(close, ema200)  and k < 20  and k > 11 and ai_signal ==  1
    shortCondition = ta.crossunder(close, ema200) and k > 81  and k > 11 and ai_signal == -1

    if (not na(k) and not na(d))
        if (co and k < 20 and k > 11) -> strategy.entry("StochLE",    strategy.long)
        if (cu and k > 81 and k > 11) -> strategy.entry("StochSE",    strategy.short)
        if (longCondition)           -> strategy.entry("LongEntry",  strategy.long)
                                        strategy.exit("StopLoss", "LongEntry",  loss = close * 0.9)
        if (shortCondition)          -> strategy.entry("ShortEntry", strategy.short)
                                        strategy.exit("StopLoss", "ShortEntry", loss = close * 1.1)

`strategy()` declares only `title` and `overlay`, so every order property is
Pine's documented default: `strategy.fixed` quantity of 1 contract, initial
capital 1000000, commission 0%, pyramiding 0, `process_orders_on_close=false`.
The `/*backtest` header declares `period: 1h` on Futures_Binance BTC_USDT, so
`timeframe` is "1h"; `basePeriod: 15m` is the FMZ backtester's own fill
granularity.

THE `loss=` ARGUMENT IS PASSED THROUGH VERBATIM, UNCONVERTED. Pine's `loss=` is
counted in TICKS, and this source hands it `close * 0.9` -- a PRICE. The engine
consumes it as ticks too (`PineBroker._order_stop_limit`: `avg_price - side *
loss_ticks * mintick`), so the two agree by construction and the stop ends up
about `close * 0.9 * 0.1` price units away, i.e. far enough that it never fires
on this data. That is the source's own units error, reproduced rather than
"fixed" (铁律 2/6): writing `loss = (close * 0.9) / syminfo.mintick` would be a
different strategy, not a faithful port. The md's claim of a 10% stop describes
the author's intent, which the code does not implement.

FIDELITY:

* `ta.stoch` is not in pine_ta, so the port implements Pine's documented formula
  inline: `100 * (close - ta.lowest(low, length)) / (ta.highest(high, length) -
  ta.lowest(low, length))`. A zero denominator is masked to na, matching Pine's
  x/0 -> na rather than becoming inf.
* `ema200` IS A 200-BAR SMA, not an EMA. The name is the source's; the formula is
  what is reproduced (铁律 3) and `pine_ta.pine_sma` is used, not `pine_ema`.
* `ai_signal = ta.rsi(close, 14) > 50 ? 1 : -1` is an INT (1 / -1), not a bool,
  so the `== 1` / `== -1` comparisons are numeric and PINE_SEMANTICS.md 1.16
  (bool compared as a number) does not apply. While the RSI is na, `na > 50` is
  false so the else branch gives -1, which is why "short" is the AI default in
  the warm-up -- the source's own arithmetic, reproduced.
* `longCondition` / `shortCondition` are ANDed with the stochastic level tests,
  so they are stoch-based as well: the trend-filter entry can only fire with k
  in the same band as the stochastic entry.
* BOTH entry arms pair an entry with a `strategy.exit` on the SAME id
  ("StopLoss"), so Pine's same-id replacement means only one resting stop exists
  at a time, and it is bound to whichever `from_entry` was placed last; the
  engine models exactly that (`PineBroker._place`, PINE_SEMANTICS.md 1.12).
* The exit is placed ONLY on the bar its entry fires, so it is not re-issued
  every bar -- the resting stop persists and, per PINE_SEMANTICS.md 1.9, the
  level is read positionally from what the engine evaluated on each bar.
* The `if (not na(k) and not na(d))` wrapper gates every order. `ta.stoch` is na
  until its 26-bar window is full and `ta.sma` is na until its own window is
  full, so k needs 28 bars and d needs 30 -- before that nothing is placed.
* `ta.rsi` uses pine_ta.pine_rsi (Wilder's rma of gains/losses, 100 when there
  were no losses in the window); Pine's exact seeding is not published, so the
  early bars carry the documented parity risk.
* `plot(ema200, ...)` and `overlay` are display-only and place no order.
* The md's argument table agrees with the source's six input defaults
  (26 / 81 / 20 / 3 / 3 / 11); no input disagreement to record.
* Leverage, margin, liquidation, funding and contract-step rounding are not
  modelled; the chain verifier measures the rounding separately.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


class SMKrkStochasticSlowMeanReversion_cc0d5f(PinePortBase, IStrategy):
    source_id = "SM_cc0d5fa7c9eddb7f"
    source_file = (
        "KRK-aDa-Stochastic-Slow-Mean-Reversion-Strategy-with-AI-Enhancements-"
        "KRK-aDa-随机慢速均值回归策略与人工智能增强.md"
    )
    timeframe = "1h"
    can_short = True
    source_defaults: dict = {
        "length": 26,
        "OverBought": 81,
        "OverSold": 20,
        "smoothK": 3,
        "smoothD": 3,
        "minKValue": 11,
    }
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    source_reproduce_stops = True
    source_mintick = 0.1
    source_fidelity_notes = [
        "`loss = close * 0.9` / `close * 1.1` is passed through VERBATIM. Pine's "
        "loss= is counted in TICKS and this source hands it a PRICE; the engine "
        "consumes ticks too (avg_price - side * loss_ticks * mintick), so the "
        "stop ends up ~close*0.09 price units below/above the entry and never "
        "fires on this data. This is the source's own units error (the md calls "
        "it a 10% stop), reproduced rather than silently converted -- converting "
        "would be a different strategy (铁律 2/6, PINE_SEMANTICS.md 3.5).",
        "`ta.stoch` is not in pine_ta, so Pine's documented formula is "
        "implemented inline: 100 * (close - lowest(low, length)) / "
        "(highest(high, length) - lowest(low, length)). A zero denominator is "
        "masked to na, matching Pine's x/0 -> na.",
        "`ema200` IS A 200-BAR SMA, not an EMA. The formula is what is "
        "reproduced, not the name (铁律 3): pine_ta.pine_sma is used.",
        "`ai_signal = ta.rsi(close, 14) > 50 ? 1 : -1` is an INT, so the "
        "`== 1` / `== -1` tests are numeric and PINE_SEMANTICS.md 1.16 does not "
        "apply. While the RSI is na the comparison is false and the else branch "
        "yields -1, so the AI term defaults to the SHORT side during the RSI's "
        "warm-up -- the source's own arithmetic.",
        "longCondition / shortCondition are ANDed with the same stochastic level "
        "bands the stochastic entry uses (k < OverSold > 11 / k > OverBought > "
        "11), so both entry paths are stoch-based.",
        "Both entry arms place a `strategy.exit` on the SAME id ('StopLoss'), so "
        "Pine's same-id replacement leaves only one resting stop, bound to the "
        "entry placed last; the engine models that (PINE_SEMANTICS.md 1.12).",
        "The exit is placed only on its entry's bar, not re-issued every bar, so "
        "the resting level persists; the framework reads the level the engine "
        "actually evaluated on each bar (PINE_SEMANTICS.md 1.9).",
        "The `if (not na(k) and not na(d))` wrapper gates every order: ta.stoch "
        "is na until 26 bars and ta.sma until its own window is full, so k needs "
        "28 bars and d needs 30 before anything can be placed.",
        "ta.rsi uses pine_ta.pine_rsi (Wilder rma of gains/losses, 100 when the "
        "window had no losses); Pine does not publish its seeding rule, so the "
        "early bars carry the documented parity risk.",
        "`strategy()` declares only title/overlay, so qty_type=fixed, qty_value="
        "1 contract, commission=0%, pyramiding=0 and initial_capital=1000000 are "
        "Pine's documented defaults.",
        "plot(ema200, ...) and overlay are display-only and place no order.",
        "The md's argument table matches the source's six input defaults "
        "(26 / 81 / 20 / 3 / 3 / 11); no input disagreement to record.",
        "Leverage, margin, liquidation, funding and contract-step rounding are "
        "not modelled; the chain verifier measures the rounding separately.",
    ]

    def pine_indicators(self, dataframe, params):
        close = dataframe["close"]
        high = dataframe["high"]
        low = dataframe["low"]
        length = int(params["length"])
        over_bought = float(params["OverBought"])
        over_sold = float(params["OverSold"])
        min_k_value = float(params["minKValue"])

        # ta.stoch(source, high, low, length):
        #   100 * (source - ta.lowest(low, length)) /
        #         (ta.highest(high, length) - ta.lowest(low, length))
        lowest_low = ta.pine_lowest(low, length)
        highest_high = ta.pine_highest(high, length)
        span = (highest_high - lowest_low).replace(0.0, np.nan)
        stoch = 100.0 * (close - lowest_low) / span

        k = ta.pine_sma(stoch, int(params["smoothK"]))
        d = ta.pine_sma(k, int(params["smoothD"]))
        co = ta.pine_crossover(k, d)
        cu = ta.pine_crossunder(k, d)

        # ema200 is really a 200-bar SMA.
        sma200 = ta.pine_sma(close, 200)

        # ai_signal = ta.rsi(close, 14) > 50 ? 1 : -1   (na > 50 is false -> -1)
        ai_signal = pd.Series(
            np.where(ta.pine_rsi(close, 14) > 50.0, 1.0, -1.0), index=dataframe.index
        )

        long_condition = (
            ta.pine_crossover(close, sma200)
            & (k < over_sold)
            & (k > min_k_value)
            & (ai_signal == 1.0)
        )
        short_condition = (
            ta.pine_crossunder(close, sma200)
            & (k > over_bought)
            & (k > min_k_value)
            & (ai_signal == -1.0)
        )

        dataframe["pine_k"] = k
        dataframe["pine_d"] = d
        dataframe["pine_sma200"] = sma200
        dataframe["pine_co"] = co
        dataframe["pine_cu"] = cu
        dataframe["pine_guard"] = k.notna() & d.notna()
        dataframe["pine_stoch_long"] = co & (k < over_sold) & (k > min_k_value)
        dataframe["pine_stoch_short"] = cu & (k > over_bought) & (k > min_k_value)
        dataframe["pine_long_condition"] = long_condition
        dataframe["pine_short_condition"] = short_condition
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "close": dataframe["close"].to_numpy(dtype=float),
            "guard": dataframe["pine_guard"].to_numpy(dtype=bool),
            "stoch_long": dataframe["pine_stoch_long"].to_numpy(dtype=bool),
            "stoch_short": dataframe["pine_stoch_short"].to_numpy(dtype=bool),
            "long_condition": dataframe["pine_long_condition"].to_numpy(dtype=bool),
            "short_condition": dataframe["pine_short_condition"].to_numpy(dtype=bool),
        }

    def pine_script(self, broker, i, ctx):
        # if (not na(k) and not na(d))
        if not ctx["guard"][i]:
            return
        close = float(ctx["close"][i])

        # if (co and k < OverSold and k > minKValue)
        #     strategy.entry("StochLE", strategy.long)
        if ctx["stoch_long"][i]:
            broker.entry("StochLE", "long")
        # if (cu and k > OverBought and k > minKValue)
        #     strategy.entry("StochSE", strategy.short)
        if ctx["stoch_short"][i]:
            broker.entry("StochSE", "short")
        # if (longCondition)
        #     strategy.entry("LongEntry", strategy.long)
        #     strategy.exit("StopLoss", "LongEntry", loss = close * 0.9)
        if ctx["long_condition"][i]:
            broker.entry("LongEntry", "long")
            # loss= counts TICKS; the source passes a price. Verbatim.
            broker.exit("StopLoss", "LongEntry", loss=close * 0.9)
        # if (shortCondition)
        #     strategy.entry("ShortEntry", strategy.short)
        #     strategy.exit("StopLoss", "ShortEntry", loss = close * 1.1)
        if ctx["short_condition"][i]:
            broker.entry("ShortEntry", "short")
            # loss= counts TICKS; the source passes a price. Verbatim.
            broker.exit("StopLoss", "ShortEntry", loss=close * 1.1)
