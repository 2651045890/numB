"""Port of sources/SM_3977544e53a386d6.pine
(batch_001/EMA与超级趋势相结合的量化交易策略-EMA-and-Supertrend-Combination-Quantitative-Trading-Strategy.md).

Pine v5. A 20-period EMA of close crossed from below, filtered by the
Supertrend indicator being in its bullish state; the same cross in the other
direction while Supertrend is bearish closes the long:

    ema = ta.ema(close, 20)
    Periods = 10 ; src = hl2 ; Multiplier = 3.0
    atr2 = ta.sma(ta.tr, Periods)
    atr  = changeATR ? ta.atr(Periods) : atr2
    up = src - Multiplier * atr
    up1 = na(up[1]) ? up : up[1]
    up := close[1] > up1 ? math.max(up, up1) : up
    dn = src + Multiplier * atr
    dn1 = na(dn[1]) ? dn : dn[1]
    dn := close[1] < dn1 ? math.min(dn, dn1) : dn
    trend = 1
    trend := na(trend[1]) ? trend : trend[1]
    trend := trend == -1 and close > dn1 ? 1 : trend == 1 and close < up1 ? -1 : trend

    buySignalEMA  = ta.crossover(close, ema)  and trend ==  1
    sellSignalEMA = ta.crossunder(close, ema) and trend == -1

    if (buySignalEMA)
        strategy.entry("Buy", strategy.long)
    if (sellSignalEMA)
        strategy.close("Buy")

`strategy()` declares only `title` and `overlay`, so every property is Pine's
documented default: `strategy.fixed` / 1 contract, initial capital 1000000,
commission 0%, pyramiding 0, `process_orders_on_close=false`. The `/*backtest`
header declares `period: 1d` on Futures_Binance BTC_USDT, so `timeframe` is
"1d"; its `basePeriod: 1h` is the FMZ backtester's own granularity for filling
those daily bars, not the strategy's period.

The source has no short entry -- only `strategy.entry(..., strategy.long)` and
`strategy.close("Buy")` -- so `can_short` is False, and there is no stop, limit,
trail or cancel call, so `source_reproduce_stops` is False and a position still
open at the end of the window stays open.

The Supertrend block is transcribed sequentially rather than as a vectorised
formula because Pine's `:=` reassignments make each bar depend on the FINAL
values of the previous bar, and the `na(...) ? ... : ...` guards change what
"previous" means on the first bars. In particular `up1` is the previous bar's
post-assignment `up`, and `trend` is seeded to 1 and is never na, so while the
ATR (and therefore `up`/`dn`) is still na the trend filter is `1` -- the
bullish filter is satisfied unconditionally and `buySignalEMA` degenerates to
`ta.crossover(close, ema)` for that warmup stretch. That is the source's own
behaviour, reproduced rather than repaired.

FIDELITY:

* The md's prose and its embedded Pine block agree with the source file
  character for character; no md-vs-source disagreement to record.
* `showsignals` and `highlighting` are `plotshape` / `fill` switches only; they
  gate no order call, so they are declared in `source_defaults` and change
  nothing. The plots, `fill`s and `alertcondition`s are display-only.
* `atr2 = ta.sma(ta.tr, Periods)` is dead under the default `changeATR=true`.
  It is computed anyway (the source computes it), and the port honours
  `changeATR=false` by selecting it, because the source does.
* PINE_SEMANTICS 3.7 (inherited, public layer, not worked around here):
  `pine_ta.pine_tr` returns `high - low` on the first bar where Pine's bare
  `ta.tr` (handle_na=false) returns na. Only the `changeATR=false` branch reads
  `ta.sma(ta.tr, ...)`, so the deviation is reachable only through that input;
  `pine_atr` uses the handle_na=True form that corresponds to `ta.atr`.
* PINE_SEMANTICS 3.1 (modelled choice): `ta.ema` is seeded with the first non-na
  observation and an na observation does not advance the recursion. TradingView
  does not publish its seeding rule.
* PINE_SEMANTICS 3.2 (modelled choice): `ta.sma` returns na until its window is
  full and na inside the window propagates.
* PINE_SEMANTICS 二.2 (not modelled): the intrabar path. Only one price leg
  exists here and it is a market order, so no stop/limit is being resolved
  inside a bar.
* PINE_SEMANTICS 1.6 / 5.1: the venue's contract-step rounding and non-zero
  taker fees are not modelled; the source declares 0% commission, which is the
  cost basis the port carries, and the chain verifier measures the rounding
  separately.
* Leverage, margin, liquidation and funding are not modelled.
"""
from freqtrade.strategy import IStrategy

import numpy as np
import pandas as pd

import pine_ta as ta
from pine_port_base import PinePortBase


class SMEmaSupertrend_397754(PinePortBase, IStrategy):
    source_id = "SM_3977544e53a386d6"
    source_file = "EMA与超级趋势相结合的量化交易策略-EMA-and-Supertrend-Combination-Quantitative-Trading-Strategy.md"
    timeframe = "1d"
    can_short = False
    source_defaults: dict = {
        "emaLength": 20,
        "supertrendMultiplier": 3.0,
        "supertrendPeriod": 10,
        "changeATR": True,
        "showsignals": True,
        "highlighting": True,
    }
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    source_reproduce_stops = False
    source_fidelity_notes = [
        "The md's prose and its embedded Pine block are identical to the source "
        "file; there is no md-vs-source disagreement to record.",
        "The Supertrend block is transcribed bar-by-bar because the source's "
        "`:=` reassignments make each bar read the FINAL up/dn/trend of the "
        "previous bar, and the `na(...) ? ... : ...` guards change what "
        "'previous' means on the first bars.",
        "`trend` is seeded to 1 by `trend = 1` and is never na, so while the ATR "
        "(and hence up/dn) is na the `trend == 1` filter passes unconditionally "
        "and buySignalEMA degenerates to ta.crossover(close, ema) for the warmup "
        "stretch. This is the source's behaviour and is reproduced, not repaired.",
        "`atr2 = ta.sma(ta.tr, Periods)` is dead under the default "
        "changeATR=true; it is still computed because the source computes it, "
        "and the changeATR=false branch selects it because the source's ternary "
        "does.",
        "PINE_SEMANTICS 3.7 (inherited, public layer, not worked around): "
        "pine_ta.pine_tr returns `high - low` on the first bar where Pine's bare "
        "ta.tr (handle_na=false) returns na. Only the changeATR=false branch "
        "reads ta.sma(ta.tr, ...), so the deviation is reachable only through "
        "that input.",
        "PINE_SEMANTICS 3.1 (modelled choice): ta.ema is seeded with the first "
        "non-na observation and an na observation does not advance the "
        "recursion; TradingView does not publish its seeding rule.",
        "PINE_SEMANTICS 3.2 (modelled choice): ta.sma is na until its window is "
        "full and na inside the window propagates.",
        "`showsignals` and `highlighting` are plotshape/fill switches only -- "
        "they gate no order call, so they are declared but change nothing. The "
        "plots, fills and alertconditions are display-only.",
        "No short entry and no stop/limit/trail exit exist, so can_short is "
        "False and source_reproduce_stops is False; a position open at the end "
        "of the window stays open.",
        "PINE_SEMANTICS 1.6 / 5.1: the venue's contract-step rounding and "
        "non-zero taker fees are not modelled. The source declares 0% "
        "commission, which is the cost basis the port carries.",
        "Leverage, margin, liquidation and funding are not modelled.",
    ]

    def pine_indicators(self, dataframe, params):
        close = dataframe["close"]
        high = dataframe["high"]
        low = dataframe["low"]

        ema_length = int(params["emaLength"])
        periods = int(params["supertrendPeriod"])
        multiplier = float(params["supertrendMultiplier"])
        change_atr = bool(params["changeATR"])

        # ema = ta.ema(close, emaLength)
        ema = ta.pine_ema(close, ema_length)

        # Periods = supertrendPeriod ; src = hl2 ; Multiplier = supertrendMultiplier
        src = (high + low) / 2.0
        # atr2 = ta.sma(ta.tr, Periods)
        atr2 = ta.pine_sma(ta.pine_tr(dataframe), periods)
        # atr = changeATR ? ta.atr(Periods) : atr2
        atr = ta.pine_atr(dataframe, periods) if change_atr else atr2

        n = len(dataframe)
        src_v = src.to_numpy(dtype=float)
        close_v = close.to_numpy(dtype=float)
        atr_v = atr.to_numpy(dtype=float)

        up = np.full(n, np.nan)
        dn = np.full(n, np.nan)
        trend = np.ones(n, dtype=float)

        # Pine's bar-0 state: up[1] / dn[1] / trend[1] / close[1] are all na, and
        # `na` in a comparison behaves as false (the `if`/ternary false branch).
        prev_up = np.nan
        prev_dn = np.nan
        prev_close = np.nan
        prev_trend = 1.0  # `trend = 1` runs before `trend := na(trend[1]) ? ...`

        for i in range(n):
            # up = src - (Multiplier * atr)
            up_raw = src_v[i] - multiplier * atr_v[i]
            # up1 = na(up[1]) ? up : up[1]
            up1 = up_raw if not np.isfinite(prev_up) else prev_up
            # up := close[1] > up1 ? math.max(up, up1) : up
            if prev_close > up1:
                up_raw = max(up_raw, up1)
            up[i] = up_raw

            # dn = src + (Multiplier * atr)
            dn_raw = src_v[i] + multiplier * atr_v[i]
            # dn1 = na(dn[1]) ? dn : dn[1]
            dn1 = dn_raw if not np.isfinite(prev_dn) else prev_dn
            # dn := close[1] < dn1 ? math.min(dn, dn1) : dn
            if prev_close < dn1:
                dn_raw = min(dn_raw, dn1)
            dn[i] = dn_raw

            # trend := na(trend[1]) ? trend : trend[1]
            level = trend[i] if not np.isfinite(prev_trend) else prev_trend
            # trend := trend == -1 and close > dn1 ? 1
            #        : trend == 1 and close < up1 ? -1 : trend
            if level == -1.0 and close_v[i] > dn1:
                level = 1.0
            elif level == 1.0 and close_v[i] < up1:
                level = -1.0
            trend[i] = level
            prev_up, prev_dn, prev_close, prev_trend = up_raw, dn_raw, close_v[i], level

        trend_s = pd.Series(trend, index=dataframe.index)
        # buySignalEMA = ta.crossover(close, ema) and trend == 1
        # sellSignalEMA = ta.crossunder(close, ema) and trend == -1
        buy_signal = ta.pine_crossover(close, ema) & (trend_s == 1.0)
        sell_signal = ta.pine_crossunder(close, ema) & (trend_s == -1.0)

        dataframe["pine_ema"] = ema
        dataframe["pine_atr"] = atr
        dataframe["pine_supertrend_up"] = up
        dataframe["pine_supertrend_dn"] = dn
        dataframe["pine_supertrend_trend"] = trend
        dataframe["pine_buy_signal"] = buy_signal
        dataframe["pine_sell_signal"] = sell_signal
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "buy_signal": dataframe["pine_buy_signal"].to_numpy(),
            "sell_signal": dataframe["pine_sell_signal"].to_numpy(),
        }

    def pine_script(self, broker, i, ctx):
        # if (buySignalEMA)
        #     strategy.entry("Buy", strategy.long)
        if ctx["buy_signal"][i]:
            broker.entry("Buy", "long")
        # if (sellSignalEMA)
        #     strategy.close("Buy")
        if ctx["sell_signal"][i]:
            broker.close("Buy")
