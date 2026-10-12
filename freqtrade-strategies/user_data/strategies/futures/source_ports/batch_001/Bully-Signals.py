"""Port of sources/SM_96afaca77301ad3a.pine (batch_001/Bully-Signals.md).

Pine v5. The file declares `indicator('Bully signals', overlay=true)`, NOT
`strategy(...)`: the two `strategy.entry` calls at the bottom are an order
block APPENDED to the indicator by the converter site that published it
(fmz.com/strategy/376314, named in the md's Detail link). Pine does not compile
`strategy.entry` inside `indicator()`, so the "original strategy" is the
indicator PLUS that appended block, and the trading behaviour it defines is
entry-only:

    if qqeLong
        strategy.entry("Enter Long", strategy.long)
    else if qqeShort
        strategy.entry("Enter Short", strategy.short)

The indicator is colinmck's QQE (Quantitative Qualitative Estimation):

    Wilders_Period = RSI_Period * 2 - 1
    Rsi      = ta.rsi(close, RSI_Period)
    RsiMa    = ta.ema(Rsi, SF)
    AtrRsi   = abs(RsiMa[1] - RsiMa)
    MaAtrRsi = ta.ema(AtrRsi, Wilders_Period)
    dar      = ta.ema(MaAtrRsi, Wilders_Period) * QQE

    longband  := RsiMa[1] > longband[1]  and RsiMa > longband[1]  ? max(longband[1],  RsiMa - dar) : RsiMa - dar
    shortband := RsiMa[1] < shortband[1] and RsiMa < shortband[1] ? min(shortband[1], RsiMa + dar) : RsiMa + dar
    cross_1   = ta.cross(longband[1], RsiMa)
    trend     := ta.cross(RsiMa, shortband[1]) ? 1 : cross_1 ? -1 : nz(trend[1], 1)
    FastAtrRsiTL = trend == 1 ? longband : shortband

    QQExlong  := FastAtrRsiTL < RsiMa ? QQExlong + 1 : 0
    QQExshort := FastAtrRsiTL > RsiMa ? QQExshort + 1 : 0
    qqeLong   = QQExlong  == 1 ? FastAtrRsiTL[1] - 50 : na
    qqeShort  = QQExshort == 1 ? FastAtrRsiTL[1] - 50 : na

The appended block is driven by `if qqeLong` / `else if qqeShort` where those
are FLOATS (either `FastAtrRsiTL[1] - 50` or na), so Pine's float-truthiness
applies: na is false and 0.0 is false, every other value is true. The port
evaluates exactly `not na and != 0` rather than converting to a bool.

There is NO exit of any kind in the source -- no `strategy.close`, no
`strategy.exit`, and not even a commented-out one. A position is therefore only
ever left by the opposite entry, which the engine models as a reversal.
`pyramiding` keeps Pine's default of 0.

FIDELITY:

* The longband/shortband/trend/QQEx recursions are BAR-BY-BAR series recursions
  with their own `[1]` history references (the source overwrites each with `:=`
  on every bar). They are written out as a literal loop, in the source's own
  statement order, rather than replaced by any vectorised indicator -- a
  library QQE would not reproduce the na warmup or the `nz(trend[1], 1)` seed.
* `trend = 0` is declared and then overwritten with `:=` on every bar; the only
  place the declaration's 0 could survive is bar 0, and there the `:=` fires
  first with `nz(trend[1], 1)` = 1. The port therefore seeds trend[0] = 1 via
  the same nz path.
* `ta.cross(a, b)` is the source's own call and is reproduced as Pine's
  `(a > b and a[1] <= b[1]) or (a < b and a[1] >= b[1])` on the two history
  references the arguments carry (`longband[1]` / `shortband[1]` shift the
  arguments, so the crossing is tested one bar further back than it looks).
  An na operand makes the comparison false, which is what Pine does.
* na propagation through `ta.ema` follows pine_ta's documented seeding rule
  (PINE_SEMANTICS.md 3.1: first non-na value as seed, na does not advance the
  recursion); TradingView does not publish its own seeding rule, so this is a
  recorded modelling choice, not a verified identity.
* `ThreshHold = input(10)` is declared and never read anywhere in the source;
  it is recorded in source_defaults and kept as dead code, not deleted.
* The source declares `indicator(...)`, so no strategy() properties exist and
  Pine's documented defaults apply (fixed size 1, 0% commission, pyramiding 0,
  initial capital 1000000).
* `plotshape` / `alertcondition` are display- or alert-only and place no order;
  dropped.
* The header's backtest window (2021-07-27 to 2022-08-02) is extraction
  metadata, not an `input.time` filter, so no data is trimmed. The header's
  `basePeriod: 15m` is the host's intrabar granularity for filling 1h bars, not
  the strategy's period.
* No stop, limit or trail exit exists, so `source_reproduce_stops` is False.
* Leverage, margin, liquidation, funding and the venue's contract-step rounding
  are not modelled (PINE_SEMANTICS.md 1.6 measures the rounding separately).
"""
import numpy as np
import pandas as pd
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


def _nz(value: float, replacement: float = 0.0) -> float:
    """Pine `nz`: an na value becomes `replacement`."""
    return replacement if value is None or np.isnan(value) else float(value)


def _cross_at(x_now, x_prev, y_now, y_prev) -> bool:
    """Pine `ta.cross` for one bar; an na operand makes the comparison false."""
    if (
        np.isnan(x_now)
        or np.isnan(x_prev)
        or np.isnan(y_now)
        or np.isnan(y_prev)
    ):
        return False
    return bool(
        (x_now > y_now and x_prev <= y_prev)
        or (x_now < y_now and x_prev >= y_prev)
    )


class SMBullySignals_96afac(PinePortBase, IStrategy):
    source_id = "SM_96afaca77301ad3a"
    source_file = "Bully-Signals.md"
    timeframe = "1h"
    can_short = True
    # Input defaults exactly as written; ThreshHold is never read by the source.
    source_defaults: dict = {
        "RSI_Period": 14,
        "SF": 6,
        "QQE": 4.238,
        "ThreshHold": 10,
    }
    # indicator(...), not strategy(...): Pine's documented defaults apply.
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    # No strategy.close / strategy.exit / stop / limit / trail anywhere.
    source_reproduce_stops = False
    source_mintick = 0.1
    source_fidelity_notes = [
        "The file declares indicator(...), not strategy(...): the strategy.entry "
        "pair at the bottom is an order block appended by the converter site "
        "(fmz.com/strategy/376314 per the md's Detail link). The port reproduces "
        "the indicator PLUS that appended block, i.e. entry-only behaviour.",
        "The appended block tests qqeLong / qqeShort, which are FLOATS (either "
        "FastAtrRsiTL[1] - 50 or na). Pine's float-truthiness applies: na is "
        "false and 0.0 is false, every other value -- including negatives -- is "
        "true. The port evaluates exactly `not na and != 0`; it does NOT coerce "
        "to a presence test alone, which would differ on an exact 0.0.",
        "longband/shortband/trend/QQExlong/QQExshort are bar-by-bar series "
        "recursions with their own [1] history references, written out as a "
        "literal loop in the source's statement order. No library QQE is "
        "substituted: it would not reproduce the na warmup or the "
        "nz(trend[1], 1) seed.",
        "trend is declared `trend = 0` and then overwritten by `:=` on every "
        "bar, so the declared 0 never survives a bar: on bar 0 the `:=` runs "
        "first and takes nz(trend[1], 1) = 1. The port seeds trend[0] = 1 "
        "through the same nz path.",
        "ta.cross(a, b) is Pine's (a > b and a[1] <= b[1]) or (a < b and a[1] "
        ">= b[1]). Its arguments here are themselves history references "
        "(longband[1] / shortband[1]), so the crossing is compared one bar "
        "further back than the call site suggests; the port keeps that shift "
        "explicit and returns False when any operand is na.",
        "ta.ema seeding follows pine_ta's documented rule (first non-na value as "
        "seed, na does not advance the recursion) -- PINE_SEMANTICS.md 3.1 "
        "records that TradingView does not publish its own rule, so this is a "
        "modelling choice, not a verified identity.",
        "ThreshHold = input(10) is dead code: it is declared and never read "
        "anywhere in the source. Recorded in source_defaults and kept as an "
        "unused value, not deleted.",
        "The source has no exit of any kind: no strategy.close, no "
        "strategy.exit, no stop or limit order, and no commented-out exit line. "
        "A position is only left by the opposite entry, which the engine models "
        "as a reverse fill. source_reproduce_stops is False accordingly.",
        "The source declares indicator(...), so no strategy() properties exist "
        "and Pine's documented defaults are used: default_qty_type fixed, "
        "default_qty_value 1, commission 0%, pyramiding 0, initial capital "
        "1000000 USD.",
        "MD-vs-SOURCE: the md front matter names the author as 'ChaoZhang', "
        "while the source file's own header reads '(c) colinmck' -- the md "
        "records the fmz uploader, the source the original author. No effect on "
        "behaviour; recorded, not reconciled.",
        "The md's argument table (v_input_1 14 RSI Length, v_input_2 6 RSI "
        "Smoothing, v_input_3 4.238 Fast QQE Factor, v_input_4 10 Thresh-hold) "
        "and its embedded source block are verbatim identical to the .pine "
        "source.",
        "The header's backtest window is extraction metadata, not an input.time "
        "filter, so the port runs on whatever range the caller supplies; "
        "basePeriod: 15m is the host's intrabar fill granularity, not the "
        "strategy's period.",
        "Leverage, margin, liquidation, funding and the venue's contract-step "
        "rounding are not modelled (PINE_SEMANTICS.md 1.6).",
    ]

    def pine_indicators(self, dataframe, params):
        rsi_period = int(params["RSI_Period"])
        sf = int(params["SF"])
        qqe = float(params["QQE"])
        wilders_period = rsi_period * 2 - 1

        close = dataframe["close"]
        rsi = ta.pine_rsi(close, rsi_period)
        rsi_ma = ta.pine_ema(rsi, sf)
        atr_rsi = (rsi_ma.shift(1) - rsi_ma).abs()
        ma_atr_rsi = ta.pine_ema(atr_rsi, wilders_period)
        dar = ta.pine_ema(ma_atr_rsi, wilders_period) * qqe

        rs = rsi_ma.to_numpy(dtype=float)
        dd = dar.to_numpy(dtype=float)
        n = len(rs)

        longband = np.full(n, np.nan)
        shortband = np.full(n, np.nan)
        trend = np.full(n, np.nan)
        fast = np.full(n, np.nan)
        qqex_long = np.full(n, np.nan)
        qqex_short = np.full(n, np.nan)
        qqe_long = np.full(n, np.nan)
        qqe_short = np.full(n, np.nan)

        for t in range(n):
            rs_now = rs[t]
            rs_prev = rs[t - 1] if t >= 1 else np.nan
            rs_prev2 = rs[t - 2] if t >= 2 else np.nan

            # newlongband / newshortband
            new_long = rs_now - dd[t]
            new_short = rs_now + dd[t]

            # longband := RsiMa[1] > longband[1] and RsiMa > longband[1]
            #             ? max(longband[1], newlongband) : newlongband
            long_prev = longband[t - 1] if t >= 1 else np.nan
            long_prev2 = longband[t - 2] if t >= 2 else np.nan
            if (rs_prev > long_prev) and (rs_now > long_prev):
                longband[t] = max(long_prev, new_long)
            else:
                longband[t] = new_long

            # shortband := RsiMa[1] < shortband[1] and RsiMa < shortband[1]
            #              ? min(shortband[1], newshortband) : newshortband
            short_prev = shortband[t - 1] if t >= 1 else np.nan
            short_prev2 = shortband[t - 2] if t >= 2 else np.nan
            if (rs_prev < short_prev) and (rs_now < short_prev):
                shortband[t] = min(short_prev, new_short)
            else:
                shortband[t] = new_short

            # cross_1 = ta.cross(longband[1], RsiMa)
            cross_1 = _cross_at(long_prev, long_prev2, rs_now, rs_prev)
            # trend := ta.cross(RsiMa, shortband[1]) ? 1 : cross_1 ? -1 : nz(trend[1], 1)
            if _cross_at(rs_now, rs_prev, short_prev, short_prev2):
                trend[t] = 1.0
            elif cross_1:
                trend[t] = -1.0
            else:
                trend[t] = _nz(trend[t - 1] if t >= 1 else np.nan, 1.0)

            # FastAtrRsiTL = trend == 1 ? longband : shortband
            fast[t] = longband[t] if trend[t] == 1.0 else shortband[t]

            # QQExlong := nz(QQExlong[1]); QQExlong := FastAtrRsiTL < RsiMa ? +1 : 0
            prev_qqex_long = qqex_long[t - 1] if t >= 1 else np.nan
            qqex_long[t] = _nz(prev_qqex_long, 0.0) + 1.0 if fast[t] < rs_now else 0.0
            prev_qqex_short = qqex_short[t - 1] if t >= 1 else np.nan
            qqex_short[t] = _nz(prev_qqex_short, 0.0) + 1.0 if fast[t] > rs_now else 0.0

            # qqeLong = QQExlong == 1 ? FastAtrRsiTL[1] - 50 : na
            fast_prev = fast[t - 1] if t >= 1 else np.nan
            qqe_long[t] = (fast_prev - 50.0) if qqex_long[t] == 1.0 else np.nan
            qqe_short[t] = (fast_prev - 50.0) if qqex_short[t] == 1.0 else np.nan

        dataframe["pine_rsi"] = rsi
        dataframe["pine_rsi_ma"] = rsi_ma
        dataframe["pine_dar"] = dar
        dataframe["pine_longband"] = longband
        dataframe["pine_shortband"] = shortband
        dataframe["pine_trend"] = trend
        dataframe["pine_fast_atr_rsi_tl"] = fast
        # if qqeLong / else if qqeShort: float truthiness -- na is false and 0.0
        # is false, everything else (including negatives) is true. -1 stays -1.
        dataframe["pine_qqe_long"] = qqe_long
        dataframe["pine_qqe_short"] = qqe_short
        dataframe["pine_long_condition"] = np.isfinite(qqe_long) & (qqe_long != 0.0)
        dataframe["pine_short_condition"] = np.isfinite(qqe_short) & (qqe_short != 0.0)
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "fast_atr_rsi_tl": dataframe["pine_fast_atr_rsi_tl"].to_numpy(),
            "qqe_long": dataframe["pine_qqe_long"].to_numpy(),
            "qqe_short": dataframe["pine_qqe_short"].to_numpy(),
            "long_condition": dataframe["pine_long_condition"].to_numpy(),
            "short_condition": dataframe["pine_short_condition"].to_numpy(),
        }

    def pine_script(self, broker, i, ctx):
        # if qqeLong
        #     strategy.entry("Enter Long", strategy.long)
        # else if qqeShort
        #     strategy.entry("Enter Short", strategy.short)
        if ctx["long_condition"][i]:
            broker.entry("Enter Long", "long")
        elif ctx["short_condition"][i]:
            broker.entry("Enter Short", "short")
