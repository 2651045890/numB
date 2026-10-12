"""Port of sources/SM_8cfd5375db6489bf.pine
(batch_001/ADXRSISMA多指标组合交易策略ADXRSISMA-Multi-Indicator-Combined-Trading-Strategy.md).

Pine v5, 45-minute chart, long and short. Four order blocks, in this written
order (which is the engine's fill priority, so the order is preserved):

    if upTrend and close > pineSupertrend and close > sma20 and os
        strategy.entry("Buy", strategy.long)                       # market long

    if ta.crossunder(close, sma20) or ob
        strategy.close_all()                                       # market flat

    if (not na(close[length]))
        strategy.entry("ChBrkLE", strategy.long,  stop = upBound  + syminfo.mintick)
    strategy.entry    ("ChBrkSE", strategy.short, stop = downBound - syminfo.mintick)

The last two are STOP entries -- resting breakout orders, not market orders --
and only the LONG one is inside the `if`. The short stop-entry is UNCONDITIONAL:
it is placed on every bar, including the first bars where `downBound` is still
na (its stop is then na and it can never fill). Pine replaces an order whose id
is already working, so at most one of each is ever live on the original
platform.

`strategy()` is commented out (line 10), so nothing is declared and Pine's
documented defaults are in force: `strategy.fixed` / 1 contract, initial capital
1000000, commission 0%, `pyramiding = 0`, `process_orders_on_close = false`. The
commented line asks for `default_qty_value=100`, `initial_capital=1000` and
`margin_long=0.1` (10x); none of it is applied, and the 10x margin in particular
is not modelled by the engine at all. Recorded in source_fidelity_notes.

The source is NOT a converter-appended order block: it declares nothing active
(no `indicator()`, no `study()`, and its only `strategy()` line is commented
out), and its `strategy.entry` / `strategy.close_all` calls are the author's own
active code. Its tier_reason's "declares indicator()/study(), tool appended
strategy.entry pair; NO exits" is false on both counts.

FIDELITY -- translation choices and source/md mismatches:

1. `fixnan` is not in pine_ta and is implemented here from its Pine definition:
   `fixnan(x)` = x with na replaced by the last non-na value (a forward fill).
   It is applied to the two DI lines, exactly where the source applies it.
2. `ta.tr` in the source uses Pine's default `handle_na = false`, so the port
   calls `pine_ta.pine_tr` with its default too. The layer's pandas version still
   yields `high - low` on the first bar where Pine's yields na
   (PINE_SEMANTICS.md 3.7), which moves the RMA seed by one bar. Recorded, not
   corrected -- a shared-layer boundary.
3. The `if na(atr[1]) and ta.rsi(close,21) < 66 and ta.rsi(close,3) > 80 and
   ta.rsi(close,28) > 49 and sig > 20` branch is DEAD CODE: `na(atr[1])` is true
   only on bars 0..9 (atr needs 10 bars), and on exactly those bars
   `ta.rsi(close, 21)` and `ta.rsi(close, 28)` are still na, so the `and` is
   false; from bar 10 on, `na(atr[1])` is false. It is reproduced as written and
   can never change `direction`.
4. `nz(lowerBand[1])` / `nz(upperBand[1])` make the bands 0.0 -- not na -- on the
   first bar, so the source's first-bar SuperTrend is literally 0.0 with
   direction -1. Reproduced, including that `superTrend[1]` (unlike the bands) is
   NOT nz-wrapped, so the `prevSuperTrend == prevUpperBand` test is false on the
   first bar even though both would print 0.
5. `os = a > OB` and `ob = a < OS` are named the opposite way round from what
   they mean: `os` (over-"sold") is RSI(14) > 70, i.e. OVERBOUGHT, and the long
   entry requires it; `ob` is RSI(14) < 30 and closes everything. The source's
   names are kept verbatim rather than corrected.
6. MD/SOURCE MISMATCH (ADX): the md lists the ADX as one of the five indicators
   that gate entry ("ADX判断趋势存在且足够强势"). The only use of `sig` in the
   whole file is inside the dead branch of (3); the ADX therefore has no effect
   on any trade. The source is followed.
7. MD/SOURCE MISMATCH (SMA): the md says entry happens "on SMA crossover"
   (价格突破SMA均线时入场). The entry's SMA test is a plain level comparison
   (`close > sma20`); the only crossover is in the EXIT
   (`ta.crossunder(close, sma20)`). The source is followed.
8. MD/SOURCE MISMATCH (SAR): the md's Chinese text calls indicator 4
   "极速SAR指标" (Parabolic SAR) while its English text calls the same item
   "SuperTrend". The source has no `ta.sar` call; it has a custom
   `pine_supertrend(3, 10)`. The md's own two languages disagree with each other.
9. MD/SOURCE MISMATCH (short side): the md never mentions short entries. The
   source places an unconditional short stop-entry (`ChBrkSE`) on every bar, so
   the strategy is two-sided.
10. The md's Argument table matches the source's defaults (7 / 7 / 70 / 30 / 5).
    `v_input_5` [sic: the md writes v_input_int_1] is the `input.int` Length.
11. `length = input.int(title="Length", minval=1, maxval=1000, defval=5)` is
    declared AFTER the indicator blocks it is used by; Pine allows that and the
    port keeps the value in source_defaults.
12. The two stop-entry orders cannot be projected onto Freqtrade, whose strategy
    interface has no "rest a stop entry order" expression
    (PINE_SEMANTICS.md section 二.11): a signal projection can only fire on the
    bar the order was PLACED, while the engine fills on a later bar at the stop
    price. This is a framework boundary, not a gap that can be filled here; the
    engine still executes both orders, so the port's engine-side behaviour is
    the source's.
13. `syminfo.mintick` is not in the source's text and is taken from the port's
    `source_mintick` (0.1, the BTC/USDT:USDT quote increment). Pine reads it off
    the symbol; a 0.1 difference in the breakout triggers is possible on another
    instrument.
14. `/*backtest` `period: 45m` is the timeframe; `basePeriod: 5m` is the FMZ
    backtester's own intrabar fill granularity, not the strategy's period.
15. plot / label are display-only and are not reproduced.
16. Leverage, margin, liquidation, funding and the venue's contract-step rounding
    are not modelled; the commented `margin_long=0.1` is not modelled either.
    The chain verifier measures the step rounding separately.
"""
import numpy as np
import pandas as pd

from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase

# `pine_supertrend(3, 10)` -- literals in the source, not inputs, so they are
# module constants rather than source_defaults entries.
_ST_FACTOR = 3.0
_ST_ATR_PERIOD = 10


def _pine_supertrend_variant(frame, factor, atr_period, sig):
    """The source's `pine_supertrend(3, 10)` -- returns (superTrend, direction).

    Bar-by-bar transcription of the source's `:=` chain, including the
    `nz(lowerBand[1])` / `nz(upperBand[1])` seeds that make the first bar's bands
    0.0 rather than na, and the `na(atr[1]) and ...` branch, which is dead: it
    needs `na(atr[1])` (bars 0..9) and `ta.rsi(close, 21) < 66` at the same time,
    and the RSI is still na over exactly those bars.
    """
    factor = float(factor)
    high = frame["high"].to_numpy(dtype=float)
    low = frame["low"].to_numpy(dtype=float)
    close = frame["close"].to_numpy(dtype=float)
    hl2 = (high + low) / 2.0
    atr = ta.pine_atr(frame, int(atr_period)).to_numpy(dtype=float)
    rsi21 = ta.pine_rsi(frame["close"], 21).to_numpy(dtype=float)
    rsi3 = ta.pine_rsi(frame["close"], 3).to_numpy(dtype=float)
    rsi28 = ta.pine_rsi(frame["close"], 28).to_numpy(dtype=float)
    sig = np.asarray(sig, dtype=float)

    size = len(frame)
    upper = np.full(size, np.nan)
    lower = np.full(size, np.nan)
    supertrend = np.full(size, np.nan)
    direction = np.full(size, np.nan)
    prev_lower = np.nan
    prev_upper = np.nan
    prev_supertrend = np.nan
    prev_close = np.nan
    for i in range(size):
        upper_raw = hl2[i] + factor * atr[i]
        lower_raw = hl2[i] - factor * atr[i]
        # prevLowerBand = nz(lowerBand[1]) ; prevUpperBand = nz(upperBand[1])
        prev_lower_band = 0.0 if np.isnan(prev_lower) else prev_lower
        prev_upper_band = 0.0 if np.isnan(prev_upper) else prev_upper

        # lowerBand := lowerBand > prevLowerBand or close[1] < prevLowerBand
        #              ? lowerBand : prevLowerBand
        if (lower_raw > prev_lower_band) or (prev_close < prev_lower_band):
            lower[i] = lower_raw
        else:
            lower[i] = prev_lower_band
        # upperBand := upperBand < prevUpperBand or close[1] > prevUpperBand
        #              ? upperBand : prevUpperBand
        if (upper_raw < prev_upper_band) or (prev_close > prev_upper_band):
            upper[i] = upper_raw
        else:
            upper[i] = prev_upper_band

        # prevSuperTrend = superTrend[1]   (NOT nz-wrapped)
        atr_prev_is_na = i == 0 or np.isnan(atr[i - 1])
        # if na(atr[1]) and ta.rsi(close,21) < 66 and ta.rsi(close,3) > 80
        #    and ta.rsi(close,28) > 49 and sig > 20
        #     direction := 1
        if (
            atr_prev_is_na
            and (rsi21[i] < 66.0)
            and (rsi3[i] > 80.0)
            and (rsi28[i] > 49.0)
            and (sig[i] > 20.0)
        ):
            direction[i] = 1.0
        # else if prevSuperTrend == prevUpperBand
        elif prev_supertrend == prev_upper_band:
            # direction := close > upperBand ? -1 : 1
            direction[i] = -1.0 if close[i] > upper[i] else 1.0
        else:
            # direction := close < lowerBand ? 1 : -1
            direction[i] = 1.0 if close[i] < lower[i] else -1.0
        # superTrend := direction == -1 ? lowerBand : upperBand
        supertrend[i] = lower[i] if direction[i] == -1.0 else upper[i]

        prev_lower = lower[i]
        prev_upper = upper[i]
        prev_supertrend = supertrend[i]
        prev_close = close[i]
    return (
        pd.Series(supertrend, index=frame.index, dtype=float),
        pd.Series(direction, index=frame.index, dtype=float),
    )


class SMAdxRsiSmaMultiIndicator_8cfd53(PinePortBase, IStrategy):
    source_id = "SM_8cfd5375db6489bf"
    source_file = (
        "ADXRSISMA多指标组合交易策略"
        "ADXRSISMA-Multi-Indicator-Combined-Trading-Strategy.md"
    )
    timeframe = "45m"
    # `strategy.entry("ChBrkSE", strategy.short, ...)` -- the source is two-sided.
    can_short = True
    source_defaults: dict = {
        # adxlen = input(7, title="ADX Smoothing")
        "adxlen": 7,
        # dilen = input(7, title="DI Length")
        "dilen": 7,
        # OB = input(70)
        "OB": 70.0,
        # OS = input(30)
        "OS": 30.0,
        # length = input.int(title="Length", minval=1, maxval=1000, defval=5)
        "length": 5,
    }
    # The only strategy() declaration is commented out (line 10), so Pine's
    # documented defaults apply: fixed / 1 contract, commission 0%, pyramiding 0,
    # initial capital 1000000, process_orders_on_close false.
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    # Every exit here is a market `strategy.close_all()`; the only stop levels in
    # the file belong to the two stop ENTRY orders, which are not exit legs.
    source_reproduce_stops = False
    source_fidelity_notes = [
        "NOT a converter-appended order block: the file declares nothing active "
        "(no indicator(), no study(), and its only strategy() line is COMMENTED "
        "OUT) and its strategy.entry / strategy.close_all calls are the author's "
        "own active code. Its tier_reason's 'declares indicator()/study(), tool "
        "appended strategy.entry pair; NO exits' is false on both counts.",
        "RECORDED BUT NOT APPLIED (commented out): strategy(\"Combined "
        "Strategy\", overlay=true, default_qty_value=100, initial_capital=1000, "
        "margin_long=0.1). Being a comment it declares nothing, so Pine's "
        "documented defaults are in force: fixed / 1 contract, 0% commission, "
        "pyramiding 0, initial capital 1000000. The 10x margin_long is not "
        "modelled by the engine in any case.",
        "fixnan is not in pine_ta and is implemented here from its Pine "
        "definition (na replaced by the last non-na value, i.e. a forward fill), "
        "applied to the two DI lines exactly where the source applies it.",
        "The `if na(atr[1]) and ta.rsi(close,21) < 66 and ta.rsi(close,3) > 80 "
        "and ta.rsi(close,28) > 49 and sig > 20` branch is DEAD CODE and can "
        "never set direction: na(atr[1]) is true only on bars 0..9, and on "
        "exactly those bars ta.rsi(close, 21) and ta.rsi(close, 28) are still na, "
        "so the `and` is false; from bar 10 on na(atr[1]) is false. Reproduced as "
        "written. It also means the ADX (`sig`) never influences a trade.",
        "MD/SOURCE MISMATCH (ADX): the md lists the ADX among the five indicators "
        "that gate entry. Its only occurrence in the file is inside that dead "
        "branch. Source followed.",
        "MD/SOURCE MISMATCH (SMA): the md says entry happens on an SMA crossover. "
        "The entry's SMA test is a plain level comparison (close > sma20); the "
        "only crossover is in the EXIT (ta.crossunder(close, sma20)). Source "
        "followed.",
        "MD/SOURCE MISMATCH (indicator 4): the md's Chinese text calls it "
        "极速SAR指标 (Parabolic SAR) while its English text calls the same item "
        "SuperTrend, and the source is neither ta.sar nor ta.supertrend -- it is a "
        "hand-written pine_supertrend(3, 10). The md's two languages contradict "
        "each other.",
        "MD/SOURCE MISMATCH (short side): the md never mentions short entries; "
        "the source places an unconditional short stop-entry on every bar, so the "
        "strategy is two-sided.",
        "The source's `os` / `ob` names are the opposite way round from their "
        "meaning: os = RSI(14) > 70 (OVERBOUGHT) gates the LONG entry and ob = "
        "RSI(14) < 30 closes everything. Names kept verbatim, not corrected.",
        "nz(lowerBand[1]) / nz(upperBand[1]) make the bands 0.0 -- not na -- on "
        "the first bar, so the source's first-bar superTrend is literally 0.0 "
        "with direction -1. Reproduced. superTrend[1] is NOT nz-wrapped, so the "
        "`prevSuperTrend == prevUpperBand` test is false on the first bar even "
        "though both print 0.",
        "MD/SOURCE MISMATCH (arguments): the md's table matches the source's "
        "defaults (7 / 7 / 70 / 30 / 5). It renders v_input_3/v_input_4 as the "
        "numbers 70/30, which the source declares as `input(70)` / `input(30)`.",
        "STOP ENTRIES ARE NOT PROJECTABLE (PINE_SEMANTICS.md section 二.11): "
        "Freqtrade's strategy interface has no way to rest a stop entry order -- "
        "a projected signal can only fire on the bar the order was PLACED, "
        "whereas the engine fills on a later bar at the stop price. This is a "
        "framework boundary, not an implementation gap. The engine still "
        "executes both orders, so the engine-side behaviour is the source's; the "
        "PROJECTED enter_long / enter_short for these two ids are not the bars "
        "the source would trade on.",
        "SAME-ID STOP ENTRIES ACCUMULATE IN THE ENGINE (PINE_SEMANTICS.md "
        "section 1.12): Pine replaces an order whose id is already working, "
        "while `_place` only replaces `kind == 'exit'`, so ChBrkLE / ChBrkSE "
        "pile up one per bar while flat. The first level a bar reaches fills and "
        "the rest are dropped by the pyramiding limit, so at most one fill "
        "happens -- but the level that triggers can be an OLD one rather than "
        "the newest. Recorded, not worked around: changing it would mean editing "
        "the shared engine.",
        "`if (not na(close[length]))` guards ONLY the long stop-entry; the short "
        "one is outside the `if` and is placed on every bar, including the first "
        "bars where downBound is still na (its stop is then na and it can never "
        "fill). Reproduced exactly, indentation included.",
        "syminfo.mintick is read from the port's source_mintick (0.1, the "
        "BTC/USDT:USDT quote increment) because the source never states it. On an "
        "instrument with a different tick the breakout triggers would shift.",
        "`period: 45m` is taken from the /*backtest header as the timeframe; "
        "basePeriod: 5m is the FMZ backtester's intrabar fill granularity, not "
        "the strategy's period.",
        "ta.tr in the source uses Pine's default handle_na=false, so pine_tr is "
        "called with its default too; the layer's pandas version still returns "
        "high - low on the first bar where Pine's returns na (PINE_SEMANTICS.md "
        "3.7), moving the RMA seed by one bar. Recorded, not corrected.",
        "plot / label are display-only and are not reproduced.",
        "Leverage, margin, liquidation, funding and the venue's contract-step "
        "rounding are not modelled; the chain verifier measures the step "
        "rounding separately.",
    ]

    def pine_indicators(self, dataframe, params):
        high = dataframe["high"]
        low = dataframe["low"]
        close = dataframe["close"]
        dilen = int(params["dilen"])
        adxlen = int(params["adxlen"])

        # ---- dirmov(len) ----
        # up = ta.change(high) ; down = -ta.change(low)
        up = ta.pine_change(high)
        down = -ta.pine_change(low)
        # plusDM  = na(up)   ? na : (up   > down and up   > 0 ? up   : 0)
        # minusDM = na(down) ? na : (down > up   and down > 0 ? down : 0)
        plus_dm = up.where((up > down) & (up > 0), 0.0).mask(up.isna())
        minus_dm = down.where((down > up) & (down > 0), 0.0).mask(down.isna())
        # truerange = ta.rma(ta.tr, len)   -- ta.tr's default handle_na=false
        truerange = ta.pine_rma(ta.pine_tr(dataframe), dilen)
        # plus = fixnan(100 * ta.rma(plusDM, len) / truerange)  (and minus)
        plus = (100.0 * ta.pine_rma(plus_dm, dilen) / truerange).ffill()
        minus = (100.0 * ta.pine_rma(minus_dm, dilen) / truerange).ffill()

        # ---- adx(dilen, adxlen) ----
        # sum = plus + minus
        di_sum = plus + minus
        # adx = 100 * ta.rma(math.abs(plus - minus) / (sum == 0 ? 1 : sum), adxlen)
        # na == 0 is false, so a na sum falls through unchanged.
        denominator = di_sum.where(di_sum != 0.0, 1.0)
        sig = 100.0 * ta.pine_rma((plus - minus).abs() / denominator, adxlen)

        # ---- pine_supertrend(3, 10) ----
        pine_supertrend, pine_direction = _pine_supertrend_variant(
            dataframe, _ST_FACTOR, _ST_ATR_PERIOD, sig
        )
        # upTrend = pineDirection < 0 ; downTrend = pineDirection > 0
        # (na compares false on both sides, so a na direction is neither.)
        up_trend = pine_direction < 0
        down_trend = pine_direction > 0

        # sma20 = ta.sma(close, 20)
        sma20 = ta.pine_sma(close, 20)

        # a = ta.rsi(close,14) ; os = a > OB ; ob = a < OS
        rsi14 = ta.pine_rsi(close, 14)
        os_flag = rsi14 > float(params["OB"])
        ob_flag = rsi14 < float(params["OS"])

        # upBound = ta.highest(high, length) ; downBound = ta.lowest(low, length)
        length = int(params["length"])
        up_bound = ta.pine_highest(high, length)
        down_bound = ta.pine_lowest(low, length)

        dataframe["pine_sig"] = sig
        dataframe["pine_plus_di"] = plus
        dataframe["pine_minus_di"] = minus
        dataframe["pine_supertrend"] = pine_supertrend
        dataframe["pine_direction"] = pine_direction
        dataframe["pine_up_trend"] = up_trend
        dataframe["pine_down_trend"] = down_trend
        dataframe["pine_sma20"] = sma20
        dataframe["pine_rsi14"] = rsi14
        dataframe["pine_os"] = os_flag
        dataframe["pine_ob"] = ob_flag
        dataframe["pine_up_bound"] = up_bound
        dataframe["pine_down_bound"] = down_bound

        # if upTrend and close > pineSupertrend and close > sma20 and os
        dataframe["pine_entry_buy"] = (
            up_trend & (close > pine_supertrend) & (close > sma20) & os_flag
        )
        # if ta.crossunder(close, sma20) or ob
        dataframe["pine_close_all"] = ta.pine_crossunder(close, sma20) | ob_flag
        # if (not na(close[length]))
        dataframe["pine_chbrkle_ok"] = close.shift(length).notna()
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "entry_buy": dataframe["pine_entry_buy"].to_numpy(dtype=bool),
            "close_all": dataframe["pine_close_all"].to_numpy(dtype=bool),
            "chbrkle_ok": dataframe["pine_chbrkle_ok"].to_numpy(dtype=bool),
            "up_bound": dataframe["pine_up_bound"].to_numpy(dtype=float),
            "down_bound": dataframe["pine_down_bound"].to_numpy(dtype=float),
            # syminfo.mintick
            "mintick": float(self.source_mintick),
        }

    def pine_script(self, broker, i, ctx):
        # Order preserved verbatim: Buy, close_all, ChBrkLE, ChBrkSE.
        # if upTrend and close > pineSupertrend and close > sma20 and os
        if ctx["entry_buy"][i]:
            broker.entry("Buy", "long")

        # if ta.crossunder(close, sma20) or ob
        if ctx["close_all"][i]:
            broker.close_all()

        # if (not na(close[length]))
        #     strategy.entry("ChBrkLE", strategy.long, stop=upBound + syminfo.mintick)
        if ctx["chbrkle_ok"][i]:
            broker.entry(
                "ChBrkLE", "long", stop=ctx["up_bound"][i] + ctx["mintick"]
            )

        # strategy.entry("ChBrkSE", strategy.short, stop=downBound - syminfo.mintick)
        # Placed unconditionally, outside the `if`, exactly as the source has it.
        # While downBound is still na the stop is na and the order can never fill.
        broker.entry(
            "ChBrkSE", "short", stop=ctx["down_bound"][i] - ctx["mintick"]
        )
