"""Port of sources/SM_27d3826d1961990e.pine (batch_001/EMA均线收盘策略EMA-Close-Strategy.md).

Pine v4 (`//@version=4`, © x11joe). Five EMAs of the SAME source series, and a
two-sided entry that only looks at the 8 / 13 / 21 against the 55:

    out1 = ema(src1, 8)
    out2 = ema(src2, 13)
    out3 = ema(src3, 21)
    out4 = ema(src4, 55)
    out5 = ema(src5, 200)

    if (out1 > out4 and out2 > out4 and out3 > out4 and close > out4)
        strategy.entry("Long", strategy.long)
    if (out1 < out4 and out2 < out4 and out3 < out4 and close < out4)
        strategy.entry("Short", strategy.short)

`len5` / `out5` (the 200 EMA) is plotted and never read by either condition --
dead code, reproduced as a column and likewise never read.

Every `srcN` is an `input(close, ...)`, i.e. a Pine `input.source` whose default
is the `close` series; the port resolves it through `pine_ta.pine_source` so a
`source_parameters` override naming another series is honoured the way the
platform's input would be.

`strategy()` declares exactly `title`, `overlay`, `initial_capital = 1000`,
commission (percent, 0.26) and `default_qty_type = strategy.percent_of_equity`
with `default_qty_value = 100`. Neither entry passes a `qty`, so both are sized
by that declaration: 100% of equity, notional = `strategy.equity`. `pyramiding`
is not declared and stays Pine's default 0, so a repeat signal in a direction
that is already open is refused by the source's own rule, and there is no exit
call anywhere -- a position is closed only by the opposite entry reversing it.

The header declares `period: 30m` on Futures_Binance BTC_USDT, so `timeframe` is
"30m"; its `basePeriod: 15m` is the FMZ backtester's own granularity for filling
30m bars, not the strategy's period.

FIDELITY:

* The exit is the opposite `strategy.entry` alone. No `strategy.close`, no
  `strategy.exit`, so `source_reproduce_stops` is False and a position still open
  at the end of the window stays open.
* The three `plot(outN, color = close >= outN ? colour : colour, ...)` calls use
  the SAME colour on both branches of the ternary -- they encode no information
  and are display-only. Not reproduced.
* Pine v4's bare `ema()` is `ta.ema`; `pine_ta.pine_ema` seeds the recursion with
  the first non-na observation, which PINE_SEMANTICS.md 3.1 records as an
  unresolved parity risk against TradingView's unpublished seeding. `close`
  carries no na here.
* `percent_of_equity / 100` is reproduced from the engine's own recorded fill
  notional, not re-derived from the live wallet (PINE_SEMANTICS.md 1.4).
* There is no short/long asymmetry to report: the source is genuinely two-sided,
  so `can_short` is True.
* Leverage, margin, liquidation, funding and the venue's contract-step rounding
  are not modelled; the chain verifier measures the rounding separately.
"""
from __future__ import annotations

import numpy as np
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


class SMEmaClose_27d382(PinePortBase, IStrategy):
    source_id = "SM_27d3826d1961990e"
    source_file = "EMA均线收盘策略EMA-Close-Strategy.md"
    timeframe = "30m"
    can_short = True
    source_defaults = {
        # len1..len5 = input(8/13/21/55/200, minval=1, title="EMA #N")
        "len1": 8,
        "len2": 13,
        "len3": 21,
        "len4": 55,
        "len5": 200,
        # src1..src5 = input(close, title="EMA Source #N")
        "src1": "close",
        "src2": "close",
        "src3": "close",
        "src4": "close",
        "src5": "close",
    }
    source_qty_type = "percent_of_equity"
    source_qty_value = 100.0
    # commission_type = strategy.commission.percent, commission_value = 0.26.
    source_commission_percent = 0.26
    source_pyramiding = 0
    source_initial_capital = 1000.0
    # No strategy.close / strategy.exit anywhere: the only exit is the opposite entry.
    source_reproduce_stops = False
    source_fidelity_notes = [
        "No exit call exists: a position is closed only when the opposite "
        "strategy.entry reverses it, so source_reproduce_stops is False and a "
        "position open at the end of the window stays open.",
        "out5 (the 200 EMA, len5=200) is assigned and plotted but never read by "
        "either entry condition. It is computed here and kept as a column, and "
        "likewise never read -- dead code is reproduced, not deleted.",
        "The three plot() calls colour both branches of `close >= outN ? colour : "
        "colour` identically, so they encode nothing; plot() and overlay are "
        "display-only and are not reproduced.",
        "Pine v4's bare ema() is ta.ema; pine_ta.pine_ema seeds the recursion with "
        "the first non-na observation (PINE_SEMANTICS.md 3.1). TradingView's own "
        "seeding is not published, so this remains a parity risk.",
        "All five srcN are input.source with a default of `close`; they are "
        "resolved through pine_ta.pine_source so an override naming another "
        "series behaves as the platform's input would.",
        "default_qty_type=percent_of_equity with default_qty_value=100 is the "
        "source's declaration and is reproduced from the engine's own recorded "
        "fill notional rather than re-derived from the live wallet "
        "(PINE_SEMANTICS.md 1.4).",
        "The header's basePeriod: 15m is the FMZ backtester's own fill "
        "granularity, not the strategy's period; the declared period is 30m.",
        "can_short is True: the source places a real strategy.short entry.",
        "Leverage, margin, liquidation, funding and the venue's contract-step "
        "rounding are not modelled; the chain verifier measures that rounding "
        "separately rather than treating it as a signal difference.",
    ]

    def pine_indicators(self, dataframe, params):
        out1 = ta.pine_ema(ta.pine_source(dataframe, params["src1"]), int(params["len1"]))
        out2 = ta.pine_ema(ta.pine_source(dataframe, params["src2"]), int(params["len2"]))
        out3 = ta.pine_ema(ta.pine_source(dataframe, params["src3"]), int(params["len3"]))
        out4 = ta.pine_ema(ta.pine_source(dataframe, params["src4"]), int(params["len4"]))
        # out5 is dead in the source: computed, plotted, never read.
        out5 = ta.pine_ema(ta.pine_source(dataframe, params["src5"]), int(params["len5"]))

        close = dataframe["close"].astype(float)
        # if(out1>out4 and out2>out4 and out3>out4 and close>out4)
        long_condition = (out1 > out4) & (out2 > out4) & (out3 > out4) & (close > out4)
        # if(out1<out4 and out2<out4 and out3<out4 and close<out4)
        short_condition = (out1 < out4) & (out2 < out4) & (out3 < out4) & (close < out4)

        dataframe["pine_out1"] = out1
        dataframe["pine_out2"] = out2
        dataframe["pine_out3"] = out3
        dataframe["pine_out4"] = out4
        dataframe["pine_out5"] = out5
        dataframe["pine_long_condition"] = long_condition.astype(bool)
        dataframe["pine_short_condition"] = short_condition.astype(bool)
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "long_condition": dataframe["pine_long_condition"].to_numpy(),
            "short_condition": dataframe["pine_short_condition"].to_numpy(),
        }

    def pine_script(self, broker, i, ctx):
        # if(out1>out4 and out2>out4 and out3>out4 and close>out4)
        #     strategy.entry("Long",strategy.long)
        if ctx["long_condition"][i]:
            broker.entry("Long", "long")
        # if(out1<out4 and out2<out4 and out3<out4 and close<out4)
        #     strategy.entry("Short",strategy.short)
        if ctx["short_condition"][i]:
            broker.entry("Short", "short")
