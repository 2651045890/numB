"""Port of sources/SM_257077f6a4736bac.pine (batch_001/EMA交叉与RSI过滤的双重趋势策略-Dual-Trend-Strategy-with-EMA-Crossover-and-RSI-Filter.md).

Pine v5. A dual-confirmation EMA crossover: the fast/slow EMA cross chooses the
direction, RSI and MACD gate it:

    short_ma_length = input.int(9)      // Kısa EMA
    long_ma_length  = input.int(21)     // Uzun EMA
    rsi_length      = input.int(14)     // RSI Periyodu
    rsi_overbought  = input.int(70)     // RSI Aşırı Alım
    rsi_oversold    = input.int(30)     // RSI Aşırı Satım

    short_ema = ta.ema(close, short_ma_length)
    long_ema  = ta.ema(close, long_ma_length)
    rsi       = ta.rsi(close, rsi_length)
    [macdLine, signalLine, _] = ta.macd(close, 12, 26, 9)

    longCondition  = ta.crossover(short_ema, long_ema)  and rsi < rsi_overbought and macdLine > signalLine
    shortCondition = ta.crossunder(short_ema, long_ema) and rsi > rsi_oversold   and macdLine < signalLine

    if (longCondition)
        strategy.entry("Long", strategy.long)
    if (shortCondition)
        strategy.entry("Short", strategy.short)

Both entries are plain market entries and there is no exit call at all: a
position is only ever closed by the opposite entry reversing it. The port
therefore declares `source_reproduce_stops = False`, and a position still open
at the end of the window stays open.

`strategy()` declares only `title`, `shorttitle` and `overlay`, so Pine's
documented defaults apply: `default_qty_type = strategy.fixed`,
`default_qty_value = 1`, `commission_value = 0`, `pyramiding = 0`, initial
capital 1000000 and `process_orders_on_close = false`. The `/*backtest` header
declares `period: 1d` on Futures_Binance BTC_USDT, so `timeframe` is "1d"; its
`basePeriod: 1h` is the FMZ backtester's own granularity for filling those daily
bars, not the strategy's period.

FIDELITY:

* The md says the long entry needs "MACD线上穿信号线" (the MACD line CROSSING
  above the signal line) and the short entry "MACD线下穿信号线". The source does
  NOT test a cross: it tests the standing inequality `macdLine > signalLine` /
  `macdLine < signalLine`, which stays true for the whole time the two lines are
  ordered that way. The source wins; recorded, not corrected.
* The RSI gates are strict: `rsi < rsi_overbought` (70) and `rsi > rsi_oversold`
  (30), never `<=` / `>=`. Transcribed as written.
* `rsi` is na until Wilder's average gain and loss have both formed (Pine's
  `ta.rsi`), and `ta.rsi` returns 100 when the window holds no losses. A na RSI
  makes the gate falsy, which is what `pine_ta.pine_rsi` propagates and what
  Pine's comparison-with-na does. Not replaced by a library RSI.
* `ta.ema`'s seeding rule is not published by TradingView; `pine_ta.pine_ema`
  seeds with the first observation and does not advance the recursion on na
  (PINE_SEMANTICS §3.1). The four EMAs (9 / 21 for the close, 12 / 26 / 9 inside
  MACD) are not swapped for library moving averages. The EMA cross is evaluated
  with `ta.crossover`'s own definition (`a > b and a[1] <= b[1]`), not as a sign
  test of the difference.
* The MACD lengths 12 / 26 / 9 are literals in the source, not inputs, and stay
  literals here.
* `plot`, `hline`, `bgcolor` and every title/colour are display-only and are not
  reproduced.
* A repeated entry in a direction that is already open is refused by Pine's
  `pyramiding` default of 0, which `pine_engine` reproduces by blocking
  same-direction stacking, so these entries only ever open or reverse.
* Contract-step rounding, leverage, margin, liquidation and funding are not
  modelled (PINE_SEMANTICS §1.6, §二-4); the chain verifier measures the
  rounding separately rather than treating it as a signal difference.
"""
import numpy as np
import pandas as pd

from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


class SMEmaCrossRsiDualTrend_257077(PinePortBase, IStrategy):
    source_id = "SM_257077f6a4736bac"
    source_file = "EMA交叉与RSI过滤的双重趋势策略-Dual-Trend-Strategy-with-EMA-Crossover-and-RSI-Filter.md"
    timeframe = "1d"
    can_short = True
    source_defaults: dict = {
        "short_ma_length": 9,
        "long_ma_length": 21,
        "rsi_length": 14,
        "rsi_overbought": 70,
        "rsi_oversold": 30,
    }
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    source_reproduce_stops = False
    source_fidelity_notes = [
        "The md describes the MACD gate as the MACD line CROSSING its signal "
        "line; the source tests the standing inequality macdLine > signalLine "
        "(and < for shorts), which holds for as long as the lines stay ordered "
        "that way. The source wins; recorded, not corrected.",
        "The RSI gates are strict (< 70 for longs, > 30 for shorts), never "
        "<= / >=; transcribed as written.",
        "pine_ta.pine_ema seeds with the first observation and does not advance "
        "the recursion on na; TradingView does not publish its seeding rule "
        "(PINE_SEMANTICS §3.1). None of the four EMAs is replaced by a library "
        "moving average.",
        "The EMA cross uses ta.crossover / ta.crossunder's own definition "
        "(a > b and a[1] <= b[1]), not a sign test of short_ema - long_ema.",
        "ta.rsi returns 100 when the window holds no losses and is na until both "
        "Wilder averages have formed; a na RSI makes its gate falsy, matching "
        "Pine's comparison-with-na.",
        "The MACD lengths 12/26/9 are literals in the source, not inputs, and "
        "stay literals.",
        "There is no exit call in the source: a position is closed only by the "
        "opposite entry reversing it, so source_reproduce_stops is False and a "
        "position open at the end of the window stays open.",
        "A repeated same-direction entry while that direction is already open is "
        "refused by Pine's pyramiding default of 0, which pine_engine reproduces "
        "by blocking same-direction stacking.",
        "strategy() declares only title/shorttitle/overlay, so Pine's defaults "
        "apply: qty_type fixed, qty_value 1, commission 0, pyramiding 0, initial "
        "capital 1000000, process_orders_on_close false.",
        "plot / hline / bgcolor / titles / colours are display-only and are not "
        "reproduced.",
        "Contract-step rounding, leverage, margin, liquidation and funding are "
        "not modelled (PINE_SEMANTICS §1.6, §二-4).",
    ]

    def pine_indicators(self, dataframe, params):
        close = dataframe["close"]
        short_ema = ta.pine_ema(close, int(params["short_ma_length"]))
        long_ema = ta.pine_ema(close, int(params["long_ma_length"]))
        rsi = ta.pine_rsi(close, int(params["rsi_length"]))
        macd = ta.pine_macd(close, 12, 26, 9)
        macd_line = macd["macd"]
        signal_line = macd["signal"]
        overbought = float(params["rsi_overbought"])
        oversold = float(params["rsi_oversold"])

        # longCondition = ta.crossover(short_ema, long_ema) and
        #                 rsi < rsi_overbought and macdLine > signalLine
        long_condition = (
            ta.pine_crossover(short_ema, long_ema)
            & (rsi < overbought)
            & (macd_line > signal_line)
        )
        # shortCondition = ta.crossunder(short_ema, long_ema) and
        #                  rsi > rsi_oversold and macdLine < signalLine
        short_condition = (
            ta.pine_crossunder(short_ema, long_ema)
            & (rsi > oversold)
            & (macd_line < signal_line)
        )

        dataframe["pine_short_ema"] = short_ema
        dataframe["pine_long_ema"] = long_ema
        dataframe["pine_rsi"] = rsi
        dataframe["pine_macd_line"] = macd_line
        dataframe["pine_macd_signal"] = signal_line
        dataframe["pine_long_condition"] = long_condition.fillna(False).astype(bool)
        dataframe["pine_short_condition"] = short_condition.fillna(False).astype(bool)
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "long_condition": dataframe["pine_long_condition"].to_numpy(dtype=bool),
            "short_condition": dataframe["pine_short_condition"].to_numpy(dtype=bool),
        }

    def pine_script(self, broker, i, ctx):
        # if (longCondition)
        #     strategy.entry("Long", strategy.long)
        if ctx["long_condition"][i]:
            broker.entry("Long", "long")
        # if (shortCondition)
        #     strategy.entry("Short", strategy.short)
        if ctx["short_condition"][i]:
            broker.entry("Short", "short")
