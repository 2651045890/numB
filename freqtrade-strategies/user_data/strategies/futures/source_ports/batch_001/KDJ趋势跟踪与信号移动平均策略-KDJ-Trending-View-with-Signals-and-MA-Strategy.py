"""Port of sources/SM_8f6288523359e3b5.pine
(batch_001/KDJ趋势跟踪与信号移动平均策略-KDJ-Trending-View-with-Signals-and-MA-Strategy.md).

Pine v5, FUTURES_BINANCE BTC_USDT, 1h chart. KDJ against a 20-period SMA:

    kdj_highest = ta.highest(high, kdjLength)          // 9
    kdj_lowest  = ta.lowest(low,   kdjLength)
    kdjRSV      = 100 * ((close - kdj_lowest) / (kdj_highest - kdj_lowest))
    kdjK        = ta.sma(kdjRSV, kdjSignal)            // 3
    kdjD        = ta.sma(kdjK,   kdjSignal)
    kdjJ        = 3 * kdjK - 2 * kdjD

    ma          = ta.sma(close, maLength)              // 20, SMA hard-coded
    maCrossUp   = ta.crossover(close, ma)
    maCrossDown = ta.crossunder(close, ma)

    if (kdjJ >= kdjOverbought and maCrossDown)   // 80
        strategy.entry("Short", strategy.short, qty=1, comment="Short Entry")
    if (kdjJ <= kdjOversold and maCrossUp)       // 20
        strategy.entry("Long", strategy.long, qty=1, comment="Long Entry")

There is no exit call of any kind: a position is only ever closed by the
opposite entry reversing it, so `source_reproduce_stops` is False and a
position open at the end of the window stays open.

The `/*backtest` header declares `period: 1h`, so `timeframe` is "1h"; its
`basePeriod: 15m` is the FMZ backtester's fill granularity, not the period.

`strategy("KDJ Trending View with Signals and MA Strategy", overlay=true)`
declares nothing else, so Pine's documented defaults apply:
`default_qty_type = strategy.fixed`, `default_qty_value = 1`, initial capital
1000000, commission 0%, `pyramiding = 0`, `process_orders_on_close = false`.
The `qty=1` on both entries equals that default and is written out anyway.

FIDELITY (see `source_fidelity_notes` for the full list):

* `maType = input.string("SMA", ...)` is declared and NEVER read: `ma` is
  hard-coded to `ta.sma`, so the port computes the SMA regardless of the input.
* `longMargin` / `shortMargin` are declared and never read; they size nothing
  and no leverage is applied.
* `kdj_highest`/`kdj_lowest` are na until 9 bars have elapsed and na propagates
  through `ta.sma`, so `kdjK`/`kdjD`/`kdjJ` only begin to exist around bar 12;
  this is Pine's own warmup, reproduced through `pine_ta`.
* Division by zero in `kdjRSV` is Pine's na, not an infinity: when the 9-bar
  high equals the 9-bar low the ratio is na in Pine, and the port masks the
  quotient to na on a zero span to match.
* `ta.ema` is not used; the two SMA seeds are the shared layer's (PINE_SEMANTICS
  .md 3.2) modelled na handling, which has not been compared bar by bar.
* The `plot`, `plotshape` and `maColor` lines are display-only.
* Leverage, margin, liquidation and funding are not modelled; the venue's
  contract-step rounding is not modelled either and `verify_chain` measures it
  separately (PINE_SEMANTICS.md 1.6).
"""
from __future__ import annotations

import numpy as np
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


class SMKdjTrendingViewSignalsMa_8f6288(PinePortBase, IStrategy):
    source_id = "SM_8f6288523359e3b5"
    source_file = (
        "KDJ趋势跟踪与信号移动平均策略-KDJ-Trending-View-with-Signals-and-MA-Strategy.md"
    )
    timeframe = "1h"
    # Both directions have a live entry.
    can_short = True
    source_defaults: dict = {
        "kdjLength": 9,
        "kdjSignal": 3,
        "kdjOverbought": 80,
        "kdjOversold": 20,
        "longMargin": 2.0,
        "shortMargin": 2.0,
        "maLength": 20,
        "maType": "SMA",
    }
    # strategy("KDJ Trending View with Signals and MA Strategy", overlay=true)
    # declares nothing else, so these are Pine's documented defaults.
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    source_reproduce_stops = False
    source_fidelity_notes = [
        "`maType = input.string(\"SMA\", ...)` is declared and never read: the "
        "source hard-codes `ma = ta.sma(close, maLength)`, so the port computes "
        "the SMA and the input has no effect.",
        "`longMargin` / `shortMargin` are declared and never read by any order "
        "call; no leverage or margin is applied anywhere in the source.",
        "Both entries pass `qty=1`, which equals Pine's default_qty_value of 1; "
        "it is reproduced explicitly.",
        "There is no exit call at all: positions are only closed by the "
        "opposite entry reversing them, so source_reproduce_stops is False and "
        "a position open at the end of the window stays open.",
        "`kdjRSV`'s division by a zero span is na in Pine (not an infinity); "
        "the port masks a zero high-low span to na to match.",
        "`ta.highest` / `ta.lowest` are na until their window is full and na "
        "propagates through `ta.sma`, giving the source's own warmup of about "
        "12 bars before kdjJ exists.",
        "The `plot`, `plotshape` and `maColor` statements are display-only and "
        "do not place orders.",
        "`ta.sma`'s na handling (PINE_SEMANTICS.md 3.2) is the shared layer's "
        "modelled choice, not a bar-by-bar comparison with the platform.",
    ]

    def pine_indicators(self, dataframe, params):
        high = dataframe["high"].astype(float)
        low = dataframe["low"].astype(float)
        close = dataframe["close"].astype(float)

        # kdj_highest = ta.highest(high, kdjLength)
        kdj_highest = ta.pine_highest(high, int(params["kdjLength"]))
        # kdj_lowest = ta.lowest(low, kdjLength)
        kdj_lowest = ta.pine_lowest(low, int(params["kdjLength"]))
        # kdjRSV = 100 * ((close - kdj_lowest) / (kdj_highest - kdj_lowest))
        span = kdj_highest - kdj_lowest
        with np.errstate(divide="ignore", invalid="ignore"):
            rsv = 100.0 * (close - kdj_lowest) / span
        # Pine's float division by zero is na; a zero span is masked rather
        # than left as an infinity.
        rsv = rsv.where(span != 0.0)
        # kdjK = ta.sma(kdjRSV, kdjSignal) / kdjD = ta.sma(kdjK, kdjSignal)
        kdj_k = ta.pine_sma(rsv, int(params["kdjSignal"]))
        kdj_d = ta.pine_sma(kdj_k, int(params["kdjSignal"]))
        # kdjJ = 3 * kdjK - 2 * kdjD
        kdj_j = 3.0 * kdj_k - 2.0 * kdj_d

        # ma = ta.sma(close, maLength)  -- maType is declared but never read.
        ma = ta.pine_sma(close, int(params["maLength"]))
        # maCrossUp = ta.crossover(close, ma) / maCrossDown = ta.crossunder(close, ma)
        ma_cross_up = ta.pine_crossover(close, ma)
        ma_cross_down = ta.pine_crossunder(close, ma)

        overbought = float(params["kdjOverbought"])
        oversold = float(params["kdjOversold"])
        dataframe["pine_short_entry"] = (kdj_j >= overbought) & ma_cross_down
        dataframe["pine_long_entry"] = (kdj_j <= oversold) & ma_cross_up
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "short_entry": dataframe["pine_short_entry"].to_numpy(),
            "long_entry": dataframe["pine_long_entry"].to_numpy(),
        }

    def pine_script(self, broker, i, ctx):
        # if (kdjJ >= kdjOverbought and maCrossDown)
        #     strategy.entry("Short", strategy.short, qty=1, comment="Short Entry")
        if ctx["short_entry"][i]:
            broker.entry("Short", "short", qty=1)
        # if (kdjJ <= kdjOversold and maCrossUp)
        #     strategy.entry("Long", strategy.long, qty=1, comment="Long Entry")
        if ctx["long_entry"][i]:
            broker.entry("Long", "long", qty=1)
