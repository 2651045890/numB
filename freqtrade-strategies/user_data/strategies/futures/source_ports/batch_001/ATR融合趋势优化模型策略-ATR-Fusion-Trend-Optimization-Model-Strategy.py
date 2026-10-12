"""Port of sources/SM_7c1d6352a6c23f41.pine (batch_001/ATR融合趋势优化模型策略-ATR-Fusion-Trend-Optimization-Model-Strategy.md).

Pine v5, "Fibonacci ATR Fusion - Strategy [presentTrading]". A Fibonacci-weighted
buying-pressure oscillator against fixed thresholds, two-sided:

    true_low  = math.min(low, close[1])
    true_high = math.max(high, close[1])
    true_range = true_high - true_low
    bp = close - true_low

    calc_ratio(len) =>
        sum_bp = math.sum(bp, len)
        sum_tr = math.sum(true_range, len)
        100 * sum_bp / sum_tr

    weighted_avg     = (5*calc_ratio(8) + 4*calc_ratio(13) + 3*calc_ratio(21)
                        + 2*calc_ratio(34) + calc_ratio(55)) / 15
    weighted_avg_sma = ta.sma(weighted_avg, 3)

    longCondition  = ta.crossover(weighted_avg_sma, 58.0)
    shortCondition = ta.crossunder(weighted_avg_sma, 42.0)
    longExit       = ta.crossunder(weighted_avg_sma, 42.0)
    shortExit      = ta.crossover(weighted_avg_sma, 58.0)

    if (tradingDirection == "Long" or tradingDirection == "Both")
        if (longCondition)
            strategy.entry("Long", strategy.long)
            if useTakeProfit
                strategy.exit("TP1/2/3 Long", from_entry="Long",
                              qty_percent=12.0,
                              limit=strategy.position_avg_price +/- n*ATR)
        if (longExit)
            strategy.close("Long")
    if (tradingDirection == "Short" or tradingDirection == "Both")
        ... mirror ...

`true_high - true_low` is algebraically `ta.tr` on every bar where `close[1]`
exists (`max(high, pc) - min(low, pc)` equals `max(high-low, |high-pc|,
|low-pc|)`), but it is NOT reproduced with `pine_ta.pine_tr`: the source spells
the formula out from `close[1]`, so it is spelled out here too, and its na on the
first bar propagates through `bp` / `true_range`.

`strategy()` declares `overlay=false`, `precision=3`, `currency=currency.USD`,
`commission_value = 0.1` (percent), `slippage = 1`,
`default_qty_type = strategy.percent_of_equity`, `default_qty_value = 10` and
`initial_capital = 10000`. Neither entry passes a `qty`, so both are sized at 10%
of equity. `pyramiding` is not declared and stays Pine's default 0.
`useTakeProfit` defaults to FALSE, so the four-step ATR take-profit is OFF in the
source's own configuration and no `strategy.exit` is ever placed.

The header declares `period: 1d` on Futures_Binance BTC_USDT, so `timeframe` is
"1d".

FIDELITY:

* `slippage = 1` (one tick on market orders) is not modelled; pine_engine fills
  at the bar's open with no slippage.
* `math.sum` is modelled by `pine_ta.pine_sum`: a rolling sum over `length` bars
  that propagates na. Pine does not publish its na rule for `math.sum`; the only
  na here is the first bar (`close[1]` is na), so the choice shifts the warm-up
  edge by nothing beyond that bar. Recorded, not hidden.
* The take-profit branch is off by default and, when switched on, CANNOT be
  reproduced: `strategy.exit(... qty_percent=12)` closes 12% of the entry, and
  neither the engine (`PineBroker.exit` closes the whole entry, no
  `qty_percent` parameter) nor the framework's single-position model can express
  a partial close. Switching `useTakeProfit` on would therefore close the whole
  position three times over instead of 12% at each level. The calls are placed
  faithfully, the limitation is recorded, and the DEFAULT configuration -- the
  one the source ships and the one verified -- does not touch this branch.
* `strategy.position_avg_price` is read from the engine's `broker.avg_price`
  (na while flat), which is the same quantity the source reads.
* `tradingDirection` is an `input.string`; the two directional guard blocks are
  reproduced verbatim, so overriding it to "Long" or "Short" suppresses the
  other side exactly as the source does.
* `input.bool` is tested directly (`if useTakeProfit`), never in a numeric
  context, so the Pine v2/v3 bool-as-1/0 trap of PINE_SEMANTICS.md 1.16 does not
  apply here.
* `plot(...)` of the indicator, `precision=3` and `overlay` are display-only.
* Leverage, margin, liquidation, funding and the venue's contract-step rounding
  are not modelled; the chain verifier measures the rounding separately.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase

# Literals in the source: the five Fibonacci lookbacks and their weights.
RATIO_LENGTHS = (8, 13, 21, 34, 55)
RATIO_WEIGHTS = (5, 4, 3, 2, 1)
# Literal in the source: atrPeriod = 14 (not an input).
ATR_PERIOD = 14


def _pine_bool(value) -> bool:
    """An `input.bool` default or override as a Python bool.

    `bool("false")` is True, so a string override has to be read the way the
    platform would read it; numeric forms keep their truthiness.
    """
    if isinstance(value, str):
        return value.strip().lower() not in ("", "0", "false", "na", "none")
    return bool(value)


class SMFiboAtrFusion_7c1d63(PinePortBase, IStrategy):
    source_id = "SM_7c1d6352a6c23f41"
    source_file = (
        "ATR融合趋势优化模型策略-ATR-Fusion-Trend-Optimization-Model-Strategy.md"
    )
    timeframe = "1d"
    can_short = True
    source_defaults = {
        "tradingDirection": "Both",
        "long_entry_threshold": 58.0,
        "short_entry_threshold": 42.0,
        "long_exit_threshold": 42.0,
        "short_exit_threshold": 58.0,
        "useTakeProfit": False,
        "tp1ATR": 3.0,
        "tp2ATR": 8.0,
        "tp3ATR": 14.0,
        "tp1_percent": 12.0,
        "tp2_percent": 12.0,
        "tp3_percent": 12.0,
    }
    source_qty_type = "percent_of_equity"
    source_qty_value = 10.0
    # commission_type = strategy.commission.percent, commission_value = 0.1.
    source_commission_percent = 0.1
    source_pyramiding = 0
    source_initial_capital = 10000.0
    # No stop / trailing leg exists anywhere in the source. The only price-leg
    # exits are the four-step take-profits, and `useTakeProfit` defaults to
    # False, so the source's own configuration places none.
    source_reproduce_stops = False
    source_fidelity_notes = [
        "The four-step ATR take-profit is OFF in the source's own default "
        "configuration (useTakeProfit = false), so no strategy.exit is placed. "
        "When switched on it CANNOT be reproduced: strategy.exit(qty_percent=12) "
        "closes 12% of the entry, while PineBroker.exit closes the whole entry "
        "(no qty_percent parameter) and the framework holds a single position. The "
        "calls are placed faithfully and the limitation is recorded; the default "
        "path verified here does not reach them.",
        "slippage = 1 is declared by the source and is not modelled; pine_engine "
        "fills market orders at the bar's open with zero slippage.",
        "true_high - true_low is algebraically ta.tr once close[1] exists, but the "
        "source spells it out from close[1] rather than calling ta.tr, so it is "
        "spelled out here the same way; its na on the first bar propagates through "
        "bp and true_range.",
        "math.sum is modelled by pine_ta.pine_sum (rolling sum, na-propagating). "
        "Pine does not publish math.sum's na rule; the only na in reach is the "
        "first bar, whose close[1] is na, so the window simply fills one bar later.",
        "strategy.position_avg_price is read from the engine's broker.avg_price "
        "(na while flat), the same quantity the source reads.",
        "tradingDirection is an input.string and both directional guard blocks are "
        "reproduced verbatim, so overriding it to \"Long\" or \"Short\" suppresses "
        "the other side exactly as the source does.",
        "input.bool is only ever tested as a condition (`if useTakeProfit`), never "
        "in a numeric context, so PINE_SEMANTICS.md 1.16's bool-as-1/0 trap does "
        "not apply to this source.",
        "The five lookbacks (8, 13, 21, 34, 55), their weights (5, 4, 3, 2, 1) and "
        "atrPeriod = 14 are literals in the source, not inputs, and stay literals.",
        "default_qty_type=percent_of_equity / default_qty_value=10 is the source's "
        "declaration and is reproduced from the engine's own recorded fill notional "
        "rather than re-derived from the live wallet (PINE_SEMANTICS.md 1.4).",
        "can_short is True: with the default tradingDirection = \"Both\" the source "
        "places a real strategy.short entry.",
        "plot(), precision=3, overlay and currency are display-only.",
        "Leverage, margin, liquidation, funding and the venue's contract-step "
        "rounding are not modelled; the chain verifier measures that rounding "
        "separately rather than treating it as a signal difference.",
    ]

    def pine_indicators(self, dataframe, params):
        high = dataframe["high"].astype(float)
        low = dataframe["low"].astype(float)
        close = dataframe["close"].astype(float)

        # true_low = math.min(low, close[1]) / true_high = math.max(high, close[1])
        previous_close = close.shift(1)
        true_low = pd.concat([low, previous_close], axis=1).min(axis=1)
        true_high = pd.concat([high, previous_close], axis=1).max(axis=1)
        true_range = true_high - true_low
        bp = close - true_low

        # calc_ratio(len) = 100 * math.sum(bp, len) / math.sum(true_range, len)
        numerator = 0.0
        denominator_weight = 0.0
        ratios = []
        for length, weight in zip(RATIO_LENGTHS, RATIO_WEIGHTS):
            ratio = 100.0 * ta.pine_sum(bp, length) / ta.pine_sum(true_range, length)
            ratios.append(ratio)
            numerator = numerator + weight * ratio
            denominator_weight += weight
        weighted_avg = numerator / denominator_weight
        weighted_avg_sma = ta.pine_sma(weighted_avg, 3)

        long_entry = float(params["long_entry_threshold"])
        short_entry = float(params["short_entry_threshold"])
        long_exit = float(params["long_exit_threshold"])
        short_exit = float(params["short_exit_threshold"])

        long_condition = ta.pine_crossover(weighted_avg_sma, long_entry)
        short_condition = ta.pine_crossunder(weighted_avg_sma, short_entry)
        long_exit_condition = ta.pine_crossunder(weighted_avg_sma, long_exit)
        short_exit_condition = ta.pine_crossover(weighted_avg_sma, short_exit)

        for index, (length, ratio) in enumerate(zip(RATIO_LENGTHS, ratios)):
            dataframe[f"pine_ratio{length}"] = ratio
            del index
        dataframe["pine_weighted_avg"] = weighted_avg
        dataframe["pine_weighted_avg_sma"] = weighted_avg_sma
        dataframe["pine_long_condition"] = long_condition.astype(bool)
        dataframe["pine_short_condition"] = short_condition.astype(bool)
        dataframe["pine_long_exit"] = long_exit_condition.astype(bool)
        dataframe["pine_short_exit"] = short_exit_condition.astype(bool)
        # atrPeriod = 14 is a literal in the source, not an input.
        atr_value = ta.pine_atr(dataframe, ATR_PERIOD)
        dataframe["pine_atr"] = atr_value
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "long_condition": dataframe["pine_long_condition"].to_numpy(),
            "short_condition": dataframe["pine_short_condition"].to_numpy(),
            "long_exit": dataframe["pine_long_exit"].to_numpy(),
            "short_exit": dataframe["pine_short_exit"].to_numpy(),
            "atr": dataframe["pine_atr"].to_numpy(dtype=float),
            # Inputs are read through source_parameters(), so they are broadcast
            # per bar and read in pine_script like any other Pine series.
            "direction": np.full(len(dataframe), str(params["tradingDirection"]), dtype=object),
            "use_take_profit": np.full(len(dataframe), _pine_bool(params["useTakeProfit"])),
            "tp_atr": np.column_stack([
                np.full(len(dataframe), float(params["tp1ATR"])),
                np.full(len(dataframe), float(params["tp2ATR"])),
                np.full(len(dataframe), float(params["tp3ATR"])),
            ]),
        }

    def pine_script(self, broker, i, ctx):
        direction = str(ctx["direction"][i])
        take_profit = bool(ctx["use_take_profit"][i])
        atr_value = ctx["atr"][i]

        # if (tradingDirection == "Long" or tradingDirection == "Both")
        if direction in ("Long", "Both"):
            #     if (longCondition)
            if ctx["long_condition"][i]:
                #         strategy.entry("Long", strategy.long)
                broker.entry("Long", "long")
                #         if useTakeProfit
                #             strategy.exit("TPn Long", from_entry="Long",
                #                           qty_percent=tpn_percent, limit=tpPricen)
                if take_profit:
                    self._place_take_profits(broker, "Long", 1.0, atr_value, ctx, i)
            #     if (longExit)
            #         strategy.close("Long")
            if ctx["long_exit"][i]:
                broker.close("Long")

        # if (tradingDirection == "Short" or tradingDirection == "Both")
        if direction in ("Short", "Both"):
            #     if (shortCondition)
            if ctx["short_condition"][i]:
                #         strategy.entry("Short", strategy.short)
                broker.entry("Short", "short")
                if take_profit:
                    self._place_take_profits(broker, "Short", -1.0, atr_value, ctx, i)
            #     if (shortExit)
            #         strategy.close("Short")
            if ctx["short_exit"][i]:
                broker.close("Short")

    def _place_take_profits(self, broker, entry_id, sign, atr_value, ctx, i):
        """The three `strategy.exit(..., limit=position_avg_price +/- n*ATR)` legs.

        `strategy.position_avg_price` is na while flat, and so is the resulting
        limit; the engine treats a non-finite resting level as never touched, the
        same way the platform treats an na price argument.
        """
        average_price = broker.position_avg_price
        for level, multiplier in enumerate(ctx["tp_atr"][i], start=1):
            limit = average_price + sign * float(multiplier) * atr_value
            # NOTE: qty_percent is not expressible here -- see source_fidelity_notes.
            broker.exit(f"TP{level} {entry_id}", from_entry=entry_id, limit=limit)
