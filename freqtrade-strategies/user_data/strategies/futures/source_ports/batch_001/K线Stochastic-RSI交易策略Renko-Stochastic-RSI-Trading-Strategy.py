"""Port of sources/SM_5a591065cea25145.pine (batch_001/K线Stochastic-RSI交易策略Renko-Stochastic-RSI-Trading-Strategy.md).

Pine v3. Stochastic RSI of close, traded on the K/D cross:

    Source = close
    lengthRSI = input(20, minval=1), lengthStoch = input(3, minval=1)
    smoothK = input(5, minval=1), smoothD = input(2, minval=1)
    rsi1 = rsi(Source, lengthRSI)
    k = sma(stoch(rsi1, rsi1, rsi1, lengthStoch), smoothK)
    d = sma(k, smoothD)
    plot(k, color=aqua, linewidth=2, transp=0)
    plot(d, color=fuchsia, linewidth=2, transp=0)

    longCondition = crossover(k, d)
    if (longCondition)
        strategy.entry("Long", strategy.long)

    shortCondition = crossunder(k, d)
    if (shortCondition)
        strategy.entry("Short", strategy.short)

`stoch(rsi1, rsi1, rsi1, lengthStoch)` passes the SAME series as Pine's three
arguments -- source, high and low -- so it is the raw %K of RSI over
`lengthStoch` = 3 bars:

    100 * (rsi1 - lowest(rsi1, 3)) / (highest(rsi1, 3) - lowest(rsi1, 3))

`stoch` is not in pine_ta, so it is written out in this file. Pine applies no
smoothing of its own inside `stoch`; the single smoothing is the source's
explicit `sma(..., smoothK)`.

Both entries are plain market orders with no stop, limit or quantity argument,
so the engine fills them at the NEXT bar's open with the script's default
sizing. The source has no `strategy.close` and no `strategy.exit` anywhere, so a
position is only ever left by the opposite entry, which the engine models as a
reverse fill (close the old side, open the new one). `pyramiding = 0` (explicit
in the source) additionally means a repeated signal while already positioned in
that direction is ignored by the engine at order-creation time.

`crossover` and `crossunder` of two series cannot both be true on one bar, so
the two `if` blocks, although sequential, can never both place an order.

The source declares `strategy()` WITHOUT `default_qty_type` / `default_qty_value`
/ `slippage`, and with only `pyramiding`, `initial_capital` and the percent
commission set, so Pine's documented defaults are what the `source_*`
attributes record: fixed sizing of 1, pyramiding 0. The two `plot()` calls are
display-only and are reproduced as no code.
"""
import numpy as np
import pandas as pd
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


def _stoch_rsi(rsi1: pd.Series, length: int) -> pd.Series:
    """Pine `stoch(source, high, low, length)` with all three arguments equal.

    100 * (source - lowest(low, length)) / (highest(high, length) - lowest(low, length)),
    over `length` BARS. Pine's ta.stoch returns na when the denominator is zero
    (a flat window gives 0/0, which Pine evaluates to na); that is modelled here
    as na rather than as a division warning.
    """
    lowest = ta.pine_lowest(rsi1, length)
    highest = ta.pine_highest(rsi1, length)
    denominator = highest - lowest
    with np.errstate(divide="ignore", invalid="ignore"):
        value = 100.0 * (rsi1 - lowest) / denominator
    return value.where(denominator != 0.0)


class SMStochasticRsi_5a5910(PinePortBase, IStrategy):
    source_id = "SM_5a591065cea25145"
    source_file = "K线Stochastic-RSI交易策略Renko-Stochastic-RSI-Trading-Strategy.md"
    # /*backtest ... period: 3h, basePeriod: 15m
    timeframe = "3h"
    can_short = True
    source_defaults = {
        "lengthRSI": 20,
        "lengthStoch": 3,
        "smoothK": 5,
        "smoothD": 2,
    }
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0675
    source_pyramiding = 0
    source_initial_capital = 100.0
    # No strategy.close / strategy.exit / stop anywhere in the source.
    source_reproduce_stops = False
    source_fidelity_notes = [
        "Pine's `stoch` is not exposed by pine_ta, so it is written out in this "
        "file: 100 * (source - lowest(low, length)) / (highest(high, length) - "
        "lowest(low, length)) over `length` bars, with all three of source/high/"
        "low bound to `rsi1` here, which is what makes it a Stochastic RSI. The "
        "denominator being zero gives na (Pine's 0/0); no source bar on BTC is "
        "expected to reach it, but the masking is explicit rather than a "
        "division warning.",
        "`rsi` is pine_ta.pine_rsi (100 - 100/(1 + rma(gain)/rma(loss))), whose "
        "rma is seeded with the SMA of the first `length` observations; "
        "TradingView's own ta.rma is documented with the same SMA startup "
        "formula, but the seeding has not been compared bar by bar against the "
        "original platform (PINE_SEMANTICS.md 3.3).",
        "`rsi1` is na for the first `lengthRSI` = 20 bars (pine_rsi returns na "
        "until both rma legs exist), so `k` is na until 20 + lengthStoch - 1 + "
        "smoothK - 1 bars have elapsed and `d` two bars after that. The engine "
        "evaluates the conditions bar by bar and na comparisons are false, so "
        "no order is placed before that; the count is stated as arithmetic on "
        "the source's own lengths, not as a measured first-signal bar.",
        "The source is on a Renko chart ('This is designed for Renko Charts "
        "Only' in the source comments, and the md says so in prose). Renko "
        "bricks are a chart-construction property of the host platform and "
        "cannot be rebuilt from OHLCV, so the port runs on the /*backtest "
        "header's `period: 3h` candles -- which is what the recorded fmz.com "
        "backtest itself used (basePeriod: 15m is that platform's intrabar "
        "granularity). On a real Renko chart the same script sees a different "
        "bar series entirely; that difference is recorded, not papered over.",
        "The source has no exit of any kind: no strategy.close, no "
        "strategy.exit, no stop or limit order. A position is only left by the "
        "opposite entry, which the engine models as a reverse fill. "
        "source_reproduce_stops is False accordingly.",
        "The source declares strategy(...) without default_qty_type or "
        "default_qty_value, so Pine's documented defaults (strategy.fixed, 1) "
        "are used; initial_capital is the source's own 100 and the commission is "
        "its percent commission_value 0.0675. slippage is not declared, i.e. "
        "Pine's default 0.",
        "The two plot() calls are display-only and are reproduced as no code. "
        "No variable in the source is computed and left unread.",
        "The backtest window in the header (2023-08-18 to 2023-09-17) is not "
        "applied: the port runs on whatever range the caller supplies. Pine's "
        "`input()` arguments are all wired to the strategy's behaviour; there is "
        "no input.time window in this source.",
        "Leverage, margin, liquidation and funding are not modelled, and the "
        "venue's contract-step rounding is not modelled either.",
    ]

    def pine_indicators(self, dataframe, params):
        close = dataframe["close"]
        length_rsi = int(params["lengthRSI"])
        length_stoch = int(params["lengthStoch"])
        smooth_k = int(params["smoothK"])
        smooth_d = int(params["smoothD"])

        # rsi1 = rsi(Source, lengthRSI)
        rsi1 = ta.pine_rsi(close, length_rsi)
        # k = sma(stoch(rsi1, rsi1, rsi1, lengthStoch), smoothK)
        k = ta.pine_sma(_stoch_rsi(rsi1, length_stoch), smooth_k)
        # d = sma(k, smoothD)
        d = ta.pine_sma(k, smooth_d)
        dataframe["rsi1"] = rsi1
        dataframe["k"] = k
        dataframe["d"] = d

        # longCondition = crossover(k, d) / shortCondition = crossunder(k, d)
        dataframe["longCondition"] = ta.pine_crossover(k, d)
        dataframe["shortCondition"] = ta.pine_crossunder(k, d)
        return dataframe

    def pine_context(self, dataframe, params):
        del params
        return {
            "longCondition": dataframe["longCondition"].to_numpy(dtype=bool),
            "shortCondition": dataframe["shortCondition"].to_numpy(dtype=bool),
        }

    def pine_script(self, broker, i, ctx):
        # if (longCondition)
        #     strategy.entry("Long", strategy.long)
        if bool(ctx["longCondition"][i]):
            broker.entry("Long", "long")
        # if (shortCondition)
        #     strategy.entry("Short", strategy.short)
        if bool(ctx["shortCondition"][i]):
            broker.entry("Short", "short")
