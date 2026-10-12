"""Port of sources/SM_69dd8ff93c53ea55.pine
(batch_001/Angle-Attack-Follow-Line-Indicator.md).

Pine v5. The file declares `indicator(...)`, NOT `strategy(...)`: the
`if buy_0 / else if sell_0` block near the bottom is an order block APPENDED to
the indicator by the converter site that published it (the md's Detail link
names fmz.com/strategy/362256). Pine v5 does not compile `strategy.entry` inside
`indicator()`, so the "original strategy" is the indicator PLUS that appended
block, and the trading behaviour it defines is entry-only.

What that block reads, in full:

    BBUpper  = ta.sma(close, BBperiod) + ta.stdev(close, BBperiod) * BBdeviations
    BBLower  = ta.sma(close, BBperiod) - ta.stdev(close, BBperiod) * BBdeviations
    BBSignal = close > BBUpper ? 1 : close < BBLower ? -1 : 0

    TrendLine := <ratchet, see below>
    iTrend    := iTrend[1]; +1 if TrendLine > TrendLine[1], -1 if it is lower

    buy_0  = iTrend[1] < 0 and iTrend > 0 and Buy_0
             and MODE == 'NO FILTER HIGHER TIME FRAME' ? 1 : 0
    sell_0 = iTrend[1] > 0 and iTrend < 0 and Sell_0
             and MODE == 'NO FILTER HIGHER TIME FRAME' ? 1 : 0

    if buy_0
        strategy.entry("Enter Long", strategy.long)
    else if sell_0
        strategy.entry("Enter Short", strategy.short)

The ratchet (with the source's default `UseATRfilter = true`, i.e. the
`UseATRfilter == 1` branches):

    BBSignal ==  1 -> TrendLine := low  - ta.atr(5); ratchet it UP   (never lower)
    BBSignal == -1 -> TrendLine := high + ta.atr(5); ratchet it DOWN (never higher)
    BBSignal ==  0 -> TrendLine := TrendLine[1]

so `TrendLine` is a one-sided stair that only ever tightens in the direction the
last band break implied, and `iTrend` is the sign of its last change. The entry
is therefore a change of that sign, not a band break.

Everything else in the 408-line file is off the order path: the whole
`request.security(..., RES='240', ...)` block (`MA_MTF`, `close_`, `low_`,
`high_`, `atr_`, `BBUpper_`, `BBLower_`, `TrendLine_MTF`, `iTrend_` and all the
`*_A` "FILTER HIGHER TIME FRAME" signals), the `ma()`/`cti`/`smma` smoothing
dispatch (`MA`, default TYPE 'SMA'), `_angle_fl`, the add/reduce angle
conditions, the ADX/DMI block at the end, and every plot/hline/bgcolor/
alertcondition. None of them is read by an order call -- see the FIDELITY notes.

There is NO active exit in the source, and no commented-out one either. The
`Add Long` / `Add Short` entries ARE commented out (lines 376-379) and are NOT
reproduced. A position is only ever left by the opposite entry, which the engine
models as a reversal. `pyramiding` keeps Pine's default of 0, so a repeated
signal while already positioned that way is ignored.

FIDELITY:

* `buy_0` / `sell_0` are `? 1 : 0` integer series and are used as BARE
  conditions (`if buy_0`). The port keeps them as integers and tests them bare,
  so Pine's integer truthiness is preserved verbatim; it does NOT rewrite them
  into `== 1`. Note this source is not the `? -1 : 0` form of
  PINE_SEMANTICS.md 1.17 -- the -1 form appears only in `BBSignal`, which the
  source always compares explicitly (`== 1` / `== -1` / `== 0`), so no bare
  truthiness of a -1 arises anywhere.
* `UseATRfilter` is `input(defval=true, ...)`, i.e. a bool, and the source tests
  it as `UseATRfilter == 1`. Python's `True == 1` is also True, so the literal
  transcription selects the same branch Pine does. Unlike the `!= 0` form
  PINE_SEMANTICS.md 1.16 warns about, this comparison does NOT invert under a
  direct translation; it is kept as a comparison against 1 rather than being
  normalised to a bare truth test, so the original spelling is preserved.
* The ratchet is reproduced bar by bar with Pine's na-comparison rule (a
  comparison with na is false): `ta.atr(5)` is na for the first four bars, and
  `TrendLine[1]` is na on bar 0, so the first assignable bar takes the raw
  `low - atr` / `high + atr` candidate without ratcheting. `iTrend[1]` is na on
  bar 0, so the earliest bar on which either entry condition can be true is
  bar 2.
* `ta.stdev` is Pine's POPULATION standard deviation (ddof=0), and `ta.atr` is
  `ta.rma(ta.tr(true), 5)`; pine_ta implements both. The `ta.rma` seeding (SMA
  of the first `length` true ranges) and the `ta.ema` seeding (first non-na
  observation) are unpublished TradingView rules and are MODELLED choices
  (PINE_SEMANTICS.md 3.1/3.2, and 3.7 for `ta.tr`'s first-bar na). ATR seeds the
  ratchet, so this is on the order path here.
* `ta.stdev` and `ta.sma` return na until their window is full and propagate na
  inside it, so `BBSignal` is 0 (not -1/1) for the first 20 bars; that is Pine's
  behaviour as well.
* The 4h `request.security` block is NOT reproduced. It is reachable only from
  the `*_A` signals, the plots, the labels and `bgcolor`, none of which any
  `strategy.*` call reads; the appended block uses `buy_0` / `sell_0`, the
  "NO FILTER HIGHER TIME FRAME" variants, which read only the chart-resolution
  series. Multi-timeframe data is not modelled by the engine (PINE_SEMANTICS.md
  section 2 item 1); omitting a block that cannot move a fill avoids that
  limitation rather than hiding it.
* `ma()` is never reached on the order path either: `MA = ma(TYPE, SOUR, LEN)`
  feeds only `MA_MTF`, the 4h series. `TYPE` defaults to 'SMA', and the dispatch
  also names LSMA (an alias that returns `src`) and CTI (a six-stage lag
  smoother); none of them is reproduced because none is read.
* `_angle_fl = f_angle(TrendLine, 8, 10)` and the add/reduce conditions built
  from it are computed but read only by plots and alertconditions.
* `smma()` is defined but only reachable via `TYPE == 'SMMA'`, which the default
  never selects; the ADX block at the end computes DIPlus/DIMinus/DX/ADX with
  its own `len = 14` / `th = 20` inputs and plots them, and no order call reads
  them.
* The appended block's two conditions are mutually exclusive (`iTrend[1] < 0`
  with `iTrend > 0` cannot coexist with the reverse), so the `else if` order is
  not load-bearing for the fills -- only for faithfulness; it is kept as `elif`.
* The source declares `indicator(..., overlay=false, max_bars_back=1000)`, not
  `strategy(...)`, so Pine's documented defaults are what the `source_*`
  attributes record (fixed size 1, 0% commission, pyramiding 0, initial capital
  1000000).
* No stop, limit or trail exit exists, so `source_reproduce_stops` is False.
* Leverage, margin, liquidation, funding and the venue's contract-step rounding
  are not modelled (PINE_SEMANTICS.md 1.6, 2.4).
"""
import numpy as np
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


def _pine_trend_line(bb_signal, high, low, atr, use_atr):
    """The source's ratcheting `TrendLine` plus the `iTrend` sign recursion.

    Reproduced bar by bar because both are series that carry state across bars.
    Every comparison follows Pine's rule that an operand of na makes the
    comparison false, which is what lets the first assignable bar ignore the na
    `TrendLine[1]` instead of ratcheting against it.
    """
    size = len(bb_signal)
    trend_line = np.full(size, np.nan)
    itrend = np.full(size, np.nan)
    previous_line = np.nan      # TrendLine[1]; na on bar 0
    previous_trend = np.nan     # iTrend[1]; na on bar 0
    for i in range(size):
        line = previous_line
        if bb_signal[i] == 1:
            candidate = low[i] - atr[i] if use_atr else low[i]
            if candidate < line:            # na < x is false -> candidate wins
                candidate = line
            line = candidate
        elif bb_signal[i] == -1:
            candidate = high[i] + atr[i] if use_atr else high[i]
            if candidate > line:            # na > x is false -> candidate wins
                candidate = line
            line = candidate
        # bb_signal == 0 leaves `line` at TrendLine[1], which is what the source
        # assigns there.
        trend = previous_trend
        if line > previous_line:
            trend = 1.0
        elif line < previous_line:
            trend = -1.0
        trend_line[i] = line
        itrend[i] = trend
        previous_line = line
        previous_trend = trend
    return trend_line, itrend


class SMAngleAttackFollowLineIndicator_69dd8f(PinePortBase, IStrategy):
    source_id = "SM_69dd8ff93c53ea55"
    source_file = "Angle-Attack-Follow-Line-Indicator.md"
    timeframe = "15m"
    can_short = True
    # Every input() of the source, with its declared default, in source order.
    # SOUR's default is the `close` series, recorded by name.
    source_defaults: dict = {
        "FL": True,
        "BBperiod": 21,
        "BBdeviations": 1.00,
        "UseATRfilter": True,
        "ATRperiod": 5,
        "FLH": True,
        "AIB": True,
        "TYPE": "SMA",
        "RES": "240",
        "LEN": 21,
        "BBdeviations_": 1.00,
        "ATRperiod_": 5,
        "SOUR": "close",
        "MD": True,
        "MODE": "NO FILTER HIGHER TIME FRAME",
        "AC": True,
        "i_lookback": 8,
        "i_atrPeriod": 10,
        "BSA": True,
        "Buy_0": True,
        "Sell_0": True,
        "Add_Buy_0": True,
        "Add_Sell_0": True,
        "Add_Buy_1": False,
        "Add_Sell_1": False,
        "Add_Buy_2": False,
        "Add_Sell_2": False,
        "Max_level_1": 40,
        "Max_level_2": 65,
        "Min_level_1": -40,
        "Min_level_2": -65,
        "Red_Buy_0": True,
        "Red_Buy_1": True,
        "Red_Buy_2": False,
        "Red_Buy_3": True,
        "Red_Buy_4": False,
        "Red_Sell_0": True,
        "Red_Sell_1": True,
        "Red_Sell_2": False,
        "Red_Sell_3": True,
        "Red_Sell_4": False,
        "i_barColor": True,
        "h_lables": False,
        "len": 14,
        "th": 20,
    }
    # indicator(...), not strategy(...): Pine's documented defaults apply.
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    # No active exit; the Add Long / Add Short entries are commented out.
    source_reproduce_stops = False
    source_mintick = 0.1
    source_fidelity_notes = [
        "The file declares indicator(...), not strategy(...); the strategy.entry "
        "pair near the bottom is an order block appended to the indicator by the "
        "converter site that published it (the md's Detail link names "
        "fmz.com/strategy/362256). The original strategy is the indicator plus "
        "that appended block, and its trading behaviour is entry-only.",
        "The source has no exit of any kind, active or commented out. The "
        "`Add Long` / `Add Short` entries (source lines 376-379) ARE commented "
        "out and are NOT reproduced: the port trades only the appended "
        "`Enter Long` / `Enter Short` block. A position is only ever left by the "
        "opposite entry, which the engine models as a reverse fill. "
        "source_reproduce_stops is False accordingly.",
        "buy_0 and sell_0 are `? 1 : 0` integer series used as bare conditions "
        "(`if buy_0`). The port stores them as integers and tests them bare, "
        "preserving Pine's integer truthiness verbatim rather than rewriting them "
        "as `== 1`. This source is not PINE_SEMANTICS.md 1.17's `? -1 : 0` form: "
        "the -1 appears only in BBSignal, which the source always compares "
        "explicitly, so no bare truthiness of a -1 arises anywhere.",
        "UseATRfilter is a bool input (defval=true) tested as `UseATRfilter == 1`. "
        "Python's `True == 1` is also True, so the literal comparison selects the "
        "same branch Pine does. Unlike the `!= 0` form PINE_SEMANTICS.md 1.16 "
        "warns about, this does not invert under direct translation; the spelling "
        "is kept as written rather than normalised to a bare truth test.",
        "The TrendLine ratchet and the iTrend sign recursion are stateful across "
        "bars and are reproduced bar by bar with Pine's na rule (a comparison "
        "with na is false). ta.atr(5) is na for the first four bars and "
        "TrendLine[1] / iTrend[1] are na on bar 0, so the first assignable bar "
        "takes the raw candidate and the earliest bar either entry can fire on is "
        "bar 2. A port that treated na as a ratchetable value would arm on "
        "different bars.",
        "ta.stdev is Pine's population standard deviation (ddof=0) and ta.atr is "
        "ta.rma(ta.tr(true), 5); pine_ta implements both. The ta.rma seeding (SMA "
        "of the first `length` true ranges) and the ta.ema seeding (first non-na "
        "observation) are unpublished TradingView rules and are modelled choices "
        "(PINE_SEMANTICS.md 3.1/3.2). ATR feeds the ratchet directly, so this sits "
        "on the order path: the bars on which iTrend flips are a modelled result, "
        "not certified equivalence.",
        "ta.sma and ta.stdev return na until their 21-bar window is full and "
        "propagate na inside it, so BBSignal is 0 (not +/-1) for the first 20 "
        "bars, as in Pine.",
        "The whole 4h request.security block (MA_MTF, close_, low_, high_, atr_, "
        "BBUpper_, BBLower_, TrendLine_MTF, iTrend_ and every `*_A` FILTER HIGHER "
        "TIME FRAME signal) is NOT reproduced. The appended block reads buy_0 / "
        "sell_0 -- the NO FILTER variants -- which touch only chart-resolution "
        "series, and the *_A signals, labels and bgcolor are not read by any "
        "strategy.* call. Multi-timeframe data is not modelled by the engine "
        "(PINE_SEMANTICS.md section 2 item 1); leaving out a block that cannot "
        "move a fill avoids that limitation instead of hiding it. If a caller "
        "ever switches MODE to 'FILTER HIGHER TIME FRAME', buy_0/sell_0 become "
        "vacuously false and the port would place no orders -- so that override "
        "must not be used against this port.",
        "ma() is never reached on the order path: MA = ma(TYPE, SOUR, LEN) feeds "
        "only MA_MTF, the 4h series. Its dispatch names LSMA (an alias returning "
        "src) and CTI (a six-stage lag smoother) as well; none is reproduced "
        "because none is read. smma() is only reachable via TYPE == 'SMMA', which "
        "the default never selects.",
        "_angle_fl = f_angle(TrendLine, 8, 10) and every add/reduce condition "
        "built from it are computed by the source but read only by plots and "
        "alertconditions. The ADX/DMI block at the end computes DIPlus, DIMinus, "
        "DX and ADX from its own len = 14 / th = 20 inputs and plots them; no "
        "order call reads them. All are dropped, and their input defaults are "
        "still recorded in source_defaults.",
        "The two appended conditions are mutually exclusive (iTrend[1] < 0 with "
        "iTrend > 0 cannot coexist with the reverse), so `else if` ordering is "
        "not load-bearing for the fills -- only for faithfulness; it is kept as "
        "elif.",
        "The source declares indicator(..., overlay=false, max_bars_back=1000), "
        "not strategy(...), so no strategy() properties exist and Pine's "
        "documented defaults are used: default_qty_type fixed, default_qty_value "
        "1, commission 0%, pyramiding 0, initial capital 1000000 USD.",
        "The header declares period: 15m with basePeriod: 5m (intrabar data); the "
        "engine evaluates at bar close and fills at the next open, so intrabar "
        "path differences are not modelled. The backtest window (2022-05-02 to "
        "2022-05-08) is extraction metadata, not an input.time filter, so the "
        "port runs on whatever range the caller supplies.",
        "Leverage, margin, liquidation, funding and the venue's contract-step "
        "rounding are not modelled; the chain verifier measures the rounding "
        "separately (PINE_SEMANTICS.md 1.6).",
    ]

    def pine_indicators(self, dataframe, params):
        close = dataframe["close"]
        # BBUpper = ta.sma(close, BBperiod) + ta.stdev(close, BBperiod) * BBdeviations
        # BBLower = ta.sma(close, BBperiod) - ta.stdev(close, BBperiod) * BBdeviations
        basis = ta.pine_sma(close, int(params["BBperiod"]))
        deviation = ta.pine_stdev(close, int(params["BBperiod"]))
        upper = basis + deviation * float(params["BBdeviations"])
        lower = basis - deviation * float(params["BBdeviations"])
        # BBSignal = close > BBUpper ? 1 : close < BBLower ? -1 : 0
        bb_signal = np.zeros(len(dataframe), dtype=int)
        bb_signal[(close.to_numpy() < lower.to_numpy())] = -1
        bb_signal[(close.to_numpy() > upper.to_numpy())] = 1
        # `UseATRfilter == 1`: the source compares its bool input against the
        # integer 1. Python's `True == 1` is True as well, so the literal
        # comparison reproduces Pine's reading (this is not the `!= 0` form of
        # PINE_SEMANTICS.md 1.16, which would invert).
        use_atr = params["UseATRfilter"] == 1
        atr = ta.pine_atr(dataframe, int(params["ATRperiod"])).to_numpy(dtype=float)
        trend_line, itrend = _pine_trend_line(
            bb_signal,
            dataframe["high"].to_numpy(dtype=float),
            dataframe["low"].to_numpy(dtype=float),
            atr,
            bool(use_atr),
        )
        dataframe["pine_bb_signal"] = bb_signal
        dataframe["pine_trend_line"] = trend_line
        dataframe["pine_itrend"] = itrend
        # The two entry flags are `? 1 : 0` integer series in the source and are
        # kept as integers so the bare `if buy_0` in pine_script carries the same
        # truthiness.
        previous = np.concatenate(([np.nan], itrend[:-1]))
        enabled = str(params["MODE"]) == "NO FILTER HIGHER TIME FRAME"
        buy_0 = (
            (previous < 0) & (itrend > 0) & bool(params["Buy_0"]) & enabled
        ).astype(int)
        sell_0 = (
            (previous > 0) & (itrend < 0) & bool(params["Sell_0"]) & enabled
        ).astype(int)
        dataframe["pine_buy_0"] = buy_0
        dataframe["pine_sell_0"] = sell_0
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "buy_0": dataframe["pine_buy_0"].to_numpy(dtype=int),
            "sell_0": dataframe["pine_sell_0"].to_numpy(dtype=int),
        }

    def pine_script(self, broker, i, ctx):
        # if buy_0
        #     strategy.entry("Enter Long", strategy.long)
        # else if sell_0
        #     strategy.entry("Enter Short", strategy.short)
        # buy_0 / sell_0 are integers: 1 is true here exactly as it is in Pine.
        if ctx["buy_0"][i]:
            broker.entry("Enter Long", "long")
        elif ctx["sell_0"][i]:
            broker.entry("Enter Short", "short")
