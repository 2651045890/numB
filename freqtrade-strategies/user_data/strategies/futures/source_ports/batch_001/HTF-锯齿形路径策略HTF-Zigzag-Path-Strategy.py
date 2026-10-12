"""Port of sources/SM_05c34f32de97c742.pine (batch_001/HTF-锯齿形路径策略HTF-Zigzag-Path-Strategy.md).

Pine v5. The trading logic is two lines: a bar whose close is below its own
open is bought, and a bar whose close is above its own open is sold short. What
those prices ARE, however, is the subject of the port's one real gap -- they
come from a `request.security` call on another timeframe:

    htf_timeframe = input.timeframe("15", title="Higher Time Frame")
    [htfO, htfH, htfL, htfC, htfOpenTime, htfCloseTime] =
        request.security(syminfo.tickerid, htf_timeframe,
                         [open, high, low, close, time, time_close])

    longSignal  = htfC < htfO
    shortSignal = htfC > htfO

    if longSignal
        strategy.entry("Alım", strategy.long)
    if shortSignal
        strategy.entry("Satım", strategy.short)

NOT REPRODUCIBLE AS WRITTEN. The engine does not resample (PINE_SEMANTICS.md
section 二.1): a port only ever receives bars at the strategy's own timeframe,
so there is no 15-minute series for the expression to be evaluated on. The
port therefore evaluates the same expressions on the strategy's own bars, so
`htfO` is this bar's open and `htfC` this bar's close -- which is the
convention already used for the other port whose source requests a timeframe
the engine cannot serve (`SMSuperTrendDualMaCross_7d4ce4`, batch_002). The
script's structure is preserved (bar direction -> netting long/short market
entries, fixed qty 1) but not its sampling: the original reads a 15-minute bar
on a daily chart, this port reads the daily bar. Every signal time may differ.
This is the port's dominant fidelity gap and is repeated in
`source_fidelity_notes`.

Note also the direction: the request is for a LOWER timeframe than the chart
(`period: 1d`, requesting "15"), the reverse of the usual HTF-filter idiom.

The two "zigzag" variables are dead code: `prevHigh` / `prevLow` are `var
float` updated on every bar, and BOTH branches of the `if na(prevHigh) or
na(prevLow)` do exactly the same assignment (`prevHigh := htfH`, `prevLow :=
htfL`), so the variables merely track the requested high/low. The only
consumers are `line.new(...)` / `box.new(...)` calls that are commented out in
the source. They are computed here too, kept as columns, and never read.

`strategy()` declares `title` / `overlay` / `max_boxes_count` -- the last is a
drawing limit with no trading meaning -- so every property is Pine's documented
default: `strategy.fixed` / 1 contract, initial capital 1000000, commission 0%,
pyramiding 0, `process_orders_on_close=false`. There is no exit call of any
kind, so a position only changes through the opposite entry's netting;
`source_reproduce_stops` is False and a position open at the window end stays
open. Both directions are entered, so `can_short` is True.

FIDELITY:

* `request.security(syminfo.tickerid, htf_timeframe, ...)` cannot be honoured.
  See above; the requested 15-minute series does not exist for the engine, and
  a port cannot fetch one (Freqtrade's dataprovider is not wired into the
  offline engine, and no informative pair is registered by the harness).
* `request.security` defaults to `lookahead=barmerge.lookahead_off`, so the
  source itself introduces no future data; the port is causal as well. A
  lower-timeframe request on a higher-timeframe chart updates intrabar on the
  original platform, which is not modelled either.
* `input.color` declarations (`upColor`, `downColor`, `zigzagColor`) are
  display-only styling and are NOT carried in `source_defaults`, matching the
  convention recorded for `SMKuberanStrategy_11e4c6`. The colour defaults are
  recorded here in prose instead: white / white / black.
* `htfOpenTime` / `htfCloseTime` are requested but never read by the source and
  are not computed here (they are time values, not prices, and no order uses
  them).
* `prevHigh` / `prevLow` are dead code (see above); both branches of the guard
  assign the same values, so the "update history" comment describes nothing
  beyond tracking the current requested high/low. Computed and kept as columns.
* md-vs-source: the md prose describes a ZigZag path built from the HTF highs
  and lows as the source of the signals. The code builds no such path for
  trading -- every `line.new` / `box.new` that would draw it is commented out --
  and the signals come only from `htfC < htfO` / `htfC > htfO`. Code followed,
  prose recorded.
* md-vs-source: the md's argument table lists only the four inputs
  (`v_input_timeframe_1` = 15 and the three colours) and omits
  `max_boxes_count`, which the source passes to `strategy()`. It is a drawing
  limit and has no trading effect.
* The entries are unconditional market orders with the default quantity; there
  is no `qty=` argument in the source.
* `/*backtest` header: `period: 1d`, `basePeriod: 1h`.
* Leverage, margin, liquidation, funding and the venue's contract-step rounding
  are not modelled; the chain verifier measures the rounding separately.
"""
from freqtrade.strategy import IStrategy

from pine_port_base import PinePortBase


class SMHtfZigzagPath_05c34f(PinePortBase, IStrategy):
    source_id = "SM_05c34f32de97c742"
    source_file = "HTF-锯齿形路径策略HTF-Zigzag-Path-Strategy.md"
    timeframe = "1d"
    can_short = True
    source_defaults: dict = {"htf_timeframe": "15"}
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    source_reproduce_stops = False
    source_fidelity_notes = [
        "DOMINANT GAP: request.security(syminfo.tickerid, htf_timeframe, "
        "[open, high, low, close, time, time_close]) is not reproducible -- the "
        "engine does not resample (PINE_SEMANTICS.md section 二.1) and a port "
        "receives only strategy-timeframe bars, so the requested 15-minute "
        "series does not exist. htfO/htfC are evaluated on the strategy's own "
        "bars (this bar's open and close); every signal time may differ from "
        "the original. This follows the convention already used for "
        "SMSuperTrendDualMaCross_7d4ce4 in batch_002.",
        "The request is for a LOWER timeframe than the chart (period: 1d, "
        "requesting \"15\") -- the reverse of the usual higher-timeframe "
        "filter. Not modelled either way.",
        "request.security uses Pine's default lookahead=barmerge.lookahead_off, "
        "so the source introduces no future data; the port is causal too.",
        "input.color declarations (upColor, downColor, zigzagColor) are "
        "display-only and are not carried in source_defaults (their defaults "
        "are white / white / black). Matches the SMKuberanStrategy_11e4c6 "
        "convention.",
        "htfOpenTime / htfCloseTime are requested but never read by the source; "
        "not computed here either -- no order uses them.",
        "prevHigh / prevLow are dead code: both branches of `if na(prevHigh) or "
        "na(prevLow)` assign the same values, and their only consumers are "
        "commented-out line.new/box.new calls. Computed and kept as columns, "
        "never read.",
        "md-vs-source: the md prose presents a ZigZag path as the signal "
        "source; every drawing call that would build it is commented out and "
        "the signals come only from htfC < htfO / htfC > htfO. Code followed.",
        "md-vs-source: the md's argument table omits max_boxes_count, which the "
        "source passes to strategy(); it is a drawing limit with no trading "
        "effect.",
        "No exit exists: a position changes only through the opposite entry's "
        "netting, so source_reproduce_stops is False and a position open at the "
        "window end stays open.",
        "Entries are unconditional market orders at the default quantity; the "
        "source passes no qty=.",
        "Leverage, margin, liquidation, funding and venue contract-step "
        "rounding are not modelled; the chain verifier measures the rounding "
        "separately.",
    ]

    def pine_indicators(self, dataframe, params):
        # The requested series, evaluated on the port's own bars -- see the
        # DOMINANT GAP note above.
        htf_o = dataframe["open"]
        htf_h = dataframe["high"]
        htf_l = dataframe["low"]
        htf_c = dataframe["close"]
        dataframe["pine_htf_open"] = htf_o
        dataframe["pine_htf_high"] = htf_h
        dataframe["pine_htf_low"] = htf_l
        dataframe["pine_htf_close"] = htf_c
        # prevHigh / prevLow are dead code; both guard branches assign the same
        # values, so the tracked state is just the current requested high/low.
        dataframe["pine_prev_high"] = htf_h
        dataframe["pine_prev_low"] = htf_l
        dataframe["pine_long_signal"] = htf_c < htf_o
        dataframe["pine_short_signal"] = htf_c > htf_o
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "long_signal": dataframe["pine_long_signal"].to_numpy(),
            "short_signal": dataframe["pine_short_signal"].to_numpy(),
        }

    def pine_script(self, broker, i, ctx):
        # if longSignal
        #     strategy.entry("Alım", strategy.long)
        if ctx["long_signal"][i]:
            broker.entry("Alım", "long")
        # if shortSignal
        #     strategy.entry("Satım", strategy.short)
        if ctx["short_signal"][i]:
            broker.entry("Satım", "short")
