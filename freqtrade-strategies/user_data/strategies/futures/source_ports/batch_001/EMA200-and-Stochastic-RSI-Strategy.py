"""Port of sources/SM_45aea4db46e2aec6.pine (batch_001/EMA200-and-Stochastic-RSI-Strategy.md).

Pine v5 source that is NOT an author-written strategy: it declares no
`indicator()`/`strategy()` call at all and only *plots*; the file's last two
statements are an order block appended by the conversion station:

    if longCondition
        strategy.entry("Enter Long", strategy.long)
    else if shortCondition
        strategy.entry("Enter Short", strategy.short)

and that block is the entire trade behaviour (PINE_SEMANTICS.md 1.17): enter on
the condition, never exit. There is no `strategy.close`, no `strategy.exit`, no
stop, no target and no `? -1 : 0` flag, so nothing has to be un-rewritten here.

Indicators, transcribed from the source:

    rsi1   = ta.rsi(close, 14)
    stoch  = ta.stoch(rsi1, rsi1, rsi1, 14)
    k      = ta.sma(stoch, 3)
    d      = ta.sma(k, 3)
    ema200 = ta.ema(close, 200)

    longCondition  = close > ema200 and (k < 20 and d < 20 and ta.crossover(k, d))
                     and high > high[1] and close[1] > open[1]
                     and (close > open and (high - close) / (high - low) <= highLowShadowRatio / 100
                          and (close / open) - 1 >= keyCandlestickChange / 100)
    shortCondition = close < ema200 and (k > 80 and d > 80 and ta.crossunder(k, d))
                     and low < low[1] and close[1] < open[1]
                     and (close < open and math.abs(high - open) / math.abs(high - close) <= highLowShadowRatio / 100
                          and 1 - (close / open) >= keyCandlestickChange / 100)

`ta.stoch` is not exposed by pine_ta; it is expanded here from its definition
`100 * (source - lowest(low, length)) / (highest(high, length) - lowest(low, length))`.

`strategy()` IS PRESENT IN THE FILE BUT COMMENTED OUT -- line 13
`//strategy("70000%", overlay = true, initial_capital = 100, commission_value =
0.04, ..., pyramiding = 1, default_qty_value = 100, default_qty_type =
strategy.cash, currency = currency.USDT)`. A commented-out call declares
nothing, so every `source_*` property below is Pine's DOCUMENTED DEFAULT
(fixed / 1 contract, initial capital 1000000, commission 0%, pyramiding 0),
not the values inside the comment. The commented values are recorded here
rather than applied, per rule 2 (the source's code is the authority).

The `/*backtest` header declares `period: 1h` on Futures_Binance BTC_USDT, so
`timeframe` is "1h"; its `basePeriod: 15m` is the host backtester's own
granularity for filling those 1h bars, not the strategy's period.

FIDELITY:

* md-vs-source disagreements, all resolved in favour of the code and all left
  unreconciled: the md says the long body condition is "at least 5% larger than
  the previous candle's body", while the code tests `(close/open) - 1 >=
  keyCandlestickChange/100` with a default of 0.5 (i.e. 0.5%) and never looks at
  the previous candle's body; the md's short rule says "at least 5% smaller"
  where the code tests `1 - close/open >= 0.5%`; and the md describes the
  Stochastic RSI as "crossed above the RSI" where the code tests
  `ta.crossover(k, d)` on the two smoothed Stochastic lines.
* The ATR legs the indicator computes for its two `plot(..., trackprice=true)`
  calls -- `a`, `x = rma(tr(true), 14) * m + high` and
  `x2 = low - rma(tr(true), 14) * m` -- are plotted lines, never orders. They
  are computed and kept as ledger columns for the record, and are NOT wired to
  any stop, because the appended block contains no exit at all.
* `rewardRiskRatio` (default 1.5) is read into a variable by the source and
  then never used anywhere; it is kept in `source_defaults` and likewise never
  read.
* Division by zero (`high - low == 0`, `high - close == 0`) yields na in Pine
  and makes the comparison false; the port reproduces that by letting the
  comparison against NaN be False.
* `sma` returns na until its window is full and `ta.rsi`/`ta.rma` need their
  own warmup, so `d` is na for the first 31 bars and every condition is false
  there; na propagates rather than being filled.
* `ta.ema` is seeded with the first non-na observation (pine_ta's documented
  model); TradingView's seeding rule is unpublished -- PINE_SEMANTICS.md 3.1.
* `plot`/`plotshape`/`color` declarations are display-only and place no order.
* No exit of any kind exists, so `source_reproduce_stops` is False and a
  position open at the end of the window stays open. Reversals are the only
  way out: an opposing `strategy.entry` nets the position (PINE_SEMANTICS 1.1).
* Leverage, margin, liquidation, funding and the venue's contract-step
  rounding are not modelled.
"""
import numpy as np
import pandas as pd
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


def _pine_stoch(source: pd.Series, high: pd.Series, low: pd.Series,
                length: int) -> pd.Series:
    """Pine `ta.stoch(source, high, low, length)`.

    `100 * (source - lowest(low, length)) / (highest(high, length) - lowest(low, length))`.
    A zero span is a division by zero, which Pine evaluates to na; the
    comparison that consumes it is then false, exactly as a NaN comparison is.
    """
    lowest = ta.pine_lowest(low, length)
    highest = ta.pine_highest(high, length)
    span = highest - lowest
    with np.errstate(divide="ignore", invalid="ignore"):
        value = 100.0 * (source - lowest) / span
    return value.where(span != 0.0)


class SMEma200AndStochasticRsiStrategy_45aea4(PinePortBase, IStrategy):
    source_id = "SM_45aea4db46e2aec6"
    source_file = "EMA200-and-Stochastic-RSI-Strategy.md"
    timeframe = "1h"
    can_short = True
    source_defaults: dict = {
        "m": 2,
        "rewardRiskRatio": 1.5,
        "highLowShadowRatio": 20,
        "keyCandlestickChange": 0.5,
    }
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    source_reproduce_stops = False
    source_fidelity_notes = [
        "The file is an indicator plus an order block APPENDED by the "
        "conversion station: the last two statements are `if longCondition -> "
        "strategy.entry(\"Enter Long\", long) else if shortCondition -> "
        "strategy.entry(\"Enter Short\", short)` and they are the whole trade "
        "behaviour. There is no exit call anywhere, so source_reproduce_stops "
        "is False (PINE_SEMANTICS.md 1.17).",
        "The `strategy(...)` line is COMMENTED OUT, so no strategy() property "
        "is declared and Pine's documented defaults apply: fixed / 1 contract, "
        "initial capital 1000000, commission 0%, pyramiding 0. The commented "
        "line's own values (initial_capital=100, commission 0.04%, pyramiding "
        "1, cash sizing of 100) are NOT applied -- a comment places nothing.",
        "md-vs-source: the md says the body rule is 'at least 5% larger than "
        "the previous candle's body'; the code tests `(close/open) - 1 >= "
        "keyCandlestickChange/100` (default 0.5 = 0.5%) and never reads the "
        "previous candle's body. The code is followed.",
        "md-vs-source: the md says the short body rule is 'at least 5% "
        "smaller'; the code tests `1 - (close/open) >= 0.5%`. Code followed.",
        "md-vs-source: the md says the Stochastic RSI 'has crossed above the "
        "RSI'; the code tests `ta.crossover(k, d)` between the two smoothed "
        "Stochastic lines (d being an SMA of k, not the RSI). Code followed.",
        "`ta.stoch` is not in pine_ta and is expanded here from its "
        "definition; a zero highest-lowest span is a division by zero (na in "
        "Pine) and the port reproduces that instead of substituting a value.",
        "The ATR legs `a`, `x = rma(tr(true), 14)*m + high` and "
        "`x2 = low - rma(tr(true), 14)*m` are display-only (`plot(... "
        "trackprice=true)`); they are computed for the record and are NOT "
        "reproduced as stops, because the appended block has no exit.",
        "`rewardRiskRatio` (1.5) is assigned by the source and never read; it "
        "is kept in source_defaults and likewise never read here.",
        "Division by zero in the body/shadow ratios yields na in Pine and "
        "makes that term false; the port lets the NaN comparison be False "
        "rather than guarding it.",
        "warmup: ta.rsi(14) -> ta.stoch(14) -> sma(3) -> sma(3) makes `d` na "
        "for 31 bars, so every condition is false there. na propagates.",
        "ta.ema is seeded with the first non-na observation (pine_ta's "
        "documented model); TradingView's seeding rule is unpublished, so the "
        "EMA200 differs from the original platform's until it converges "
        "(PINE_SEMANTICS.md 3.1).",
        "plot/plotshape are display-only and place no order.",
        "Leverage, margin, liquidation, funding and contract-step rounding are "
        "not modelled; the venue's rounding can differ from the engine's float "
        "quantity, which the chain verifier measures separately.",
    ]

    def pine_indicators(self, dataframe: pd.DataFrame, params: dict) -> pd.DataFrame:
        close = dataframe["close"]
        open_ = dataframe["open"]
        high = dataframe["high"]
        low = dataframe["low"]

        # rsi1 = ta.rsi(close, 14); the literal 14 is in the source, not an input.
        rsi1 = ta.pine_rsi(close, 14)
        # k = ta.sma(ta.stoch(rsi1, rsi1, rsi1, 14), 3); d = ta.sma(k, 3)
        stoch = _pine_stoch(rsi1, rsi1, rsi1, 14)
        k = ta.pine_sma(stoch, 3)
        d = ta.pine_sma(k, 3)
        ema200 = ta.pine_ema(close, 200)

        # Display-only ATR legs, kept for the record and never read by an order.
        atr14 = ta.pine_rma(ta.pine_tr(dataframe, handle_na=True), 14)
        m = float(params["m"])

        shadow_ratio = float(params["highLowShadowRatio"]) / 100.0
        key_change = float(params["keyCandlestickChange"]) / 100.0

        with np.errstate(divide="ignore", invalid="ignore"):
            long_shadow = (high - close) / (high - low)
            long_body = (close / open_) - 1.0
            short_shadow = (high - open_).abs() / (high - close).abs()
            short_body = 1.0 - (close / open_)

        long_condition = (
            (close > ema200)
            & (k < 20)
            & (d < 20)
            & ta.pine_crossover(k, d)
            & (high > high.shift(1))
            & (close.shift(1) > open_.shift(1))
            & (close > open_)
            & (long_shadow <= shadow_ratio)
            & (long_body >= key_change)
        )
        short_condition = (
            (close < ema200)
            & (k > 80)
            & (d > 80)
            & ta.pine_crossunder(k, d)
            & (low < low.shift(1))
            & (close.shift(1) < open_.shift(1))
            & (close < open_)
            & (short_shadow <= shadow_ratio)
            & (short_body >= key_change)
        )

        dataframe["pine_rsi"] = rsi1
        dataframe["pine_stoch"] = stoch
        dataframe["pine_k"] = k
        dataframe["pine_d"] = d
        dataframe["pine_ema200"] = ema200
        dataframe["pine_atr_short_stop"] = atr14 * m + high
        dataframe["pine_atr_long_stop"] = low - atr14 * m
        dataframe["pine_long_condition"] = long_condition.fillna(False)
        dataframe["pine_short_condition"] = short_condition.fillna(False)
        return dataframe

    def pine_context(self, dataframe: pd.DataFrame, params: dict) -> dict:
        return {
            "long_condition": dataframe["pine_long_condition"].to_numpy(),
            "short_condition": dataframe["pine_short_condition"].to_numpy(),
        }

    def pine_script(self, broker, i: int, ctx: dict) -> None:
        # if longCondition
        #     strategy.entry("Enter Long", strategy.long)
        # else if shortCondition
        #     strategy.entry("Enter Short", strategy.short)
        if ctx["long_condition"][i]:
            broker.entry("Enter Long", "long")
        elif ctx["short_condition"][i]:
            broker.entry("Enter Short", "short")
