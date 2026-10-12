"""Port of sources/SM_8083c71f86952134.pine (batch_001/Get-your-trend.md).

Pine v4. A confluence long-only system. Every condition below is evaluated on
every bar and the two order calls at the end of the file are the whole strategy:

    if Long_MA and Volume_condt and L_adx and not S_cloud
        strategy.entry("L", strategy.long)
    strategy.close_all(when = close_condt)

with

    Long_MA      = SMA1 < close and SMA2 < close and SMA3 < close      (5/15/25)
    Volume_condt = volume > sma(volume, 30) * 1.8
    L_adx        = DIPlus > DIMinus and ADX > 15        (classic DI/ADX, len 20)
    S_cloud      = kama < kama[1]                       (MESA/AMA cloud)
    close_condt  = S_cloud and S_ATR,  S_ATR = Trend == -1

`Trend` is the pivot-centred ATR ratchet (`center` from pivothigh/pivotlow with
`prd = 15`, `Up/Dn = center -/+ Factor*atr(Pd)` with `Factor = 1`, `Pd = 1`).

`strategy("Get your trend", overlay = true)` declares only display arguments,
so Pine's documented defaults apply: `fixed` / 1 unit, commission 0%,
`pyramiding = 0`, `initial_capital = 1000000`,
`process_orders_on_close = false`.

The `/*backtest` header declares `period: 1d` on Bitfinex BTC_USD, so
`timeframe` is "1d"; its `basePeriod: 1h` is the FMZ backtester's own bar grid.
There is no short entry anywhere in the source, so `can_short` is False.

FIDELITY:

* `calcADX` and `calcADX_Masanakamura` are BOTH evaluated by the source on every
  bar and then selected by `ADX_options`; the port implements both so a
  non-default `Adx Type` stays faithful (default "CLASSIC").
* `tr` in `calcADX` is Pine v4's bare `tr` builtin (`handle_na = false`), not
  `ta.tr(true)`. `pine_ta.pine_tr` gives `high - low` on the very first bar
  where Pine returns na -- a one-bar difference in the seed of `rma(tr, 20)`
  that shifts the whole ATR/DI warmup. PINE_SEMANTICS.md §3.7 records this as an
  uncorrected boundary of the shared layer; it is used as-is here and NOT
  patched, because patching it in one port would make that port disagree with
  every other port using the same function.
* `fixnan` is not in `pine_ta`; it is implemented here as a forward fill, which
  is the documented behaviour (replace na with the last defined value). The
  formula is copied next to the helper.
* The MESA/AMA block (`hilbertTransform` / `computeComponent` / `computeAlpha`,
  then `mama` / `fama` / `kama`) is reproduced statement for statement as a
  per-bar recursion. Pine keeps series history for function-local variables
  assigned with `:=`, so `nz(mesaPeriod[1])`, `nz(I2[1])`, `nz(phase[1])` and
  `nz(I1[2..6])` all read the previous bars' final values -- including for the
  values passed into `hilbertTransform(I1, ...)` / `computeComponent(Q1, ...)`,
  which carry the history of the I1 / Q1 locals rather than of a global series.
  `pine_ta` has no equivalent, so it is written out here.
* `center = ... : na` uses ph/pl as ternary CONDITIONS. A Pine float is false
  when it is na or zero, so `lastpp` falls through to `pl` when `ph` is na, and
  `if lastpp` is false for both na and 0.0. That reading is what makes the
  pivot ratchet work at all (if a comparison/ternary against na produced na,
  `TDown` could never leave na); the port follows it.
* `SMA1/2/3`, `hl2`-style plots, `plot()`, `bgcolor`, the `mama`/`fama` outputs
  and the `PositionPrice` / `nLongs` / `sectionLongs` / `sum_long` bookkeeping
  are computed in the source but feed NO order call, so they are not
  reproduced; the two order calls above are unaffected by them.
* `src` is an `input(close)` source selector; the default is used and is
  exposed as a parameter.
* `ema` seeding note does not apply here (no `ema()` call); `sma`, `rma` and
  `pivot*` na behaviour is Pine_SEMANTICS.md §3.2, and the pivot tie rule
  (strict, unique extreme) is the shared layer's choice, not a Pine-documented
  one.
* `Start Time` / `End Time` inputs do not exist in this source and
  `inDateRange` is not used; no date filter is applied (§二.8).
* Leverage, margin, liquidation, funding and contract-step rounding are not
  modelled (§二.4, §1.6).
"""
import math

import numpy as np
import pandas as pd
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase

# pine_ta has no fixnan; Pine's fixnan replaces na with the last defined value.
_fixnan = lambda series: series.ffill()  # noqa: E731 - documented one-liner


def _nz(values, index):
    """Pine `nz(x[n])`: 0.0 for an na observation and for out-of-range history."""
    if index < 0 or index >= len(values):
        return 0.0
    value = values[index]
    return 0.0 if np.isnan(value) else float(value)


def _hilbert(values, i, mult):
    """hilbertTransform(src) * mesaPeriodMult, with src's own history [2][4][6]."""
    return (
        0.0962 * values[i]
        + 0.5769 * _nz(values, i - 2)
        - 0.5769 * _nz(values, i - 4)
        - 0.0962 * _nz(values, i - 6)
    ) * mult


def _compute_alpha(src, fast_limit, slow_limit):
    """computeAlpha(): alpha = fastLimit/deltaPhase, poked into [slowLimit, ...].

    Written out bar by bar because every state it carries (`mesaPeriod`,
    `smooth`, `detrender`, `I2`, `Q2`, `Re`, `Im`, `phase`) is read through
    `nz(x[1])` / `x[n]`, i.e. from the previous bars' final values.
    """
    n = len(src)
    pi = 2.0 * math.asin(1.0)
    alpha_out = np.full(n, np.nan)

    smooth = np.full(n, np.nan)
    detrender = np.full(n, np.nan)
    i1 = np.full(n, np.nan)
    q1 = np.full(n, np.nan)
    i2 = np.full(n, np.nan)
    q2 = np.full(n, np.nan)
    re = np.full(n, np.nan)
    im = np.full(n, np.nan)
    phase = np.full(n, np.nan)
    mesa_period = np.full(n, np.nan)

    for t in range(n):
        previous = t - 1
        prev_mesa_period = mesa_period[previous] if t >= 1 else np.nan
        nz_prev_mesa_period = 0.0 if np.isnan(prev_mesa_period) else float(prev_mesa_period)
        mult = 0.075 * nz_prev_mesa_period + 0.54

        # smooth := (4*src + 3*nz(src[1]) + 2*nz(src[2]) + nz(src[3])) / 10
        smooth[t] = (
            4.0 * src[t]
            + 3.0 * _nz(src, t - 1)
            + 2.0 * _nz(src, t - 2)
            + _nz(src, t - 3)
        ) / 10.0
        # detrender := computeComponent(smooth, mesaPeriodMult)
        detrender[t] = _hilbert(smooth, t, mult)
        # I1 = nz(detrender[3])
        i1[t] = _nz(detrender, t - 3)
        # Q1 = computeComponent(detrender, mesaPeriodMult)
        q1[t] = _hilbert(detrender, t, mult)
        # jI / jQ use the I1 / Q1 locals' own history
        j_i = _hilbert(i1, t, mult)
        j_q = _hilbert(q1, t, mult)

        # I2 := I1 - jQ ; Q2 := Q1 + jI ; then the 0.2/0.8 smoothing
        current_i2 = i1[t] - j_q
        current_q2 = q1[t] + j_i
        current_i2 = 0.2 * current_i2 + 0.8 * _nz(i2, previous)
        current_q2 = 0.2 * current_q2 + 0.8 * _nz(q2, previous)
        i2[t] = current_i2
        q2[t] = current_q2
        previous_i2 = _nz(i2, previous)
        previous_q2 = _nz(q2, previous)
        current_re = current_i2 * previous_i2 + current_q2 * previous_q2
        current_im = current_i2 * previous_q2 - current_q2 * previous_i2
        current_re = 0.2 * current_re + 0.8 * _nz(re, previous)
        current_im = 0.2 * current_im + 0.8 * _nz(im, previous)
        re[t] = current_re
        im[t] = current_im

        # `mesaPeriod = 0.0` at the top of the function, then the guard chain.
        period = 0.0
        if current_re != 0 and current_im != 0:
            period = 2.0 * pi / math.atan(current_im / current_re)
        if period > 1.5 * nz_prev_mesa_period:
            period = 1.5 * nz_prev_mesa_period
        if period < 0.67 * nz_prev_mesa_period:
            period = 0.67 * nz_prev_mesa_period
        if period < 6.0:
            period = 6.0
        if period > 50.0:
            period = 50.0
        period = 0.2 * period + 0.8 * nz_prev_mesa_period
        mesa_period[t] = period

        current_phase = 0.0
        if i1[t] != 0:
            current_phase = (180.0 / pi) * math.atan(q1[t] / i1[t])
        phase[t] = current_phase
        prev_phase = phase[previous] if t >= 1 else np.nan
        delta_phase = (0.0 if np.isnan(prev_phase) else float(prev_phase)) - current_phase
        if delta_phase < 1:
            delta_phase = 1.0
        alpha = fast_limit[t] / delta_phase
        if alpha < slow_limit[t]:
            alpha = slow_limit[t]
        alpha_out[t] = alpha

    return alpha_out


def _masanakamura_adx(dataframe, length):
    """calcADX_Masanakamura(_len) -> (DIP, DIM, adx), bar by bar."""
    high = dataframe["high"].to_numpy(dtype=float)
    low = dataframe["low"].to_numpy(dtype=float)
    close = dataframe["close"].to_numpy(dtype=float)
    n = len(high)
    smoothed_tr = np.full(n, np.nan)
    smoothed_plus = np.full(n, np.nan)
    smoothed_minus = np.full(n, np.nan)
    dip = np.full(n, np.nan)
    dim = np.full(n, np.nan)

    for t in range(n):
        previous = t - 1
        prev_close = _nz(close, previous)
        prev_high = _nz(high, previous)
        prev_low = _nz(low, previous)
        true_range = max(
            max(high[t] - low[t], abs(high[t] - prev_close)),
            abs(low[t] - prev_close),
        )
        up_move = high[t] - prev_high
        down_move = prev_low - low[t]
        movement_plus = max(up_move, 0.0) if up_move > down_move else 0.0
        movement_minus = max(down_move, 0.0) if down_move > up_move else 0.0

        state_tr = _nz(smoothed_tr, previous)
        state_plus = _nz(smoothed_plus, previous)
        state_minus = _nz(smoothed_minus, previous)
        smoothed_tr[t] = state_tr - (state_tr / length) + true_range
        smoothed_plus[t] = state_plus - (state_plus / length) + movement_plus
        smoothed_minus[t] = state_minus - (state_minus / length) + movement_minus

        # DIP = SDMP / STR * 100 (division by zero is na in Pine)
        dip[t] = np.nan if smoothed_tr[t] == 0 else smoothed_plus[t] / smoothed_tr[t] * 100.0
        dim[t] = np.nan if smoothed_tr[t] == 0 else smoothed_minus[t] / smoothed_tr[t] * 100.0

    with np.errstate(divide="ignore", invalid="ignore"):
        denominator = dip + dim
        dx = np.where(denominator == 0, np.nan, np.abs(dip - dim) / denominator * 100.0)
    index = dataframe.index
    dx_series = pd.Series(dx, index=index, dtype=float)
    adx = ta.pine_sma(dx_series, length)
    return (
        pd.Series(dip, index=index, dtype=float),
        pd.Series(dim, index=index, dtype=float),
        adx,
    )


class SMGetYourTrend_8083c7(PinePortBase, IStrategy):
    source_id = "SM_8083c71f86952134"
    source_file = "Get-your-trend.md"
    timeframe = "1d"
    can_short = False
    # Every `input()` in the source, defaults verbatim.
    source_defaults: dict = {
        "src": "close",
        "Length1": 5,
        "Length2": 15,
        "Length3": 25,
        "prd": 15,
        "Factor": 1,
        "Pd": 1,
        "ADX_options": "CLASSIC",
        "ADX_len": 20,
        "th": 15,
        "len": 30,
        "volume_f": 1.8,
        "sma_length": 30,
    }
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    source_reproduce_stops = False
    source_fidelity_notes = [
        "md vs source: the md's Strategy Arguments table lists v_input_6 / "
        "v_input_7 as `true` (ATR Factor / ATR Period) and v_input_8 as `0` "
        "(Adx Type). Those are the md exporter's bool / option-index renderings "
        "of the source's input(1), input(1) and "
        "input(\"CLASSIC\", options=[\"CLASSIC\", \"MASANAKAMURA\"]). The source "
        "literals (Factor=1, Pd=1, \"CLASSIC\") are used; the md table is not.",
        "Both calcADX (classic) and calcADX_Masanakamura are evaluated every bar "
        "in the source and then selected by ADX_options; both are implemented so "
        "the non-default Adx Type stays faithful.",
        "`tr` in calcADX is v4's bare tr builtin (handle_na=false). "
        "pine_ta.pine_tr returns high-low on the first bar where Pine returns "
        "na, which seeds rma(tr, 20) one bar early and shifts the ATR/DI "
        "warmup -- PINE_SEMANTICS.md §3.7, an uncorrected shared-layer "
        "boundary, used as-is rather than patched locally.",
        "fixnan is not in pine_ta; implemented as a forward fill (Pine: replace "
        "na with the last defined value).",
        "The MESA/AMA chain (hilbertTransform / computeComponent / computeAlpha "
        "-> mama / fama / kama) is reproduced statement for statement as a "
        "per-bar recursion, including the fact that the values passed into "
        "hilbertTransform(I1, ...) and computeComponent(Q1, ...) carry the "
        "history of the I1 / Q1 locals. pine_ta has no equivalent.",
        "ph/pl are used as ternary CONDITIONS and `if lastpp` tests a float: in "
        "Pine na and 0.0 are both false, so lastpp falls through to pl when ph "
        "is na. That reading is what lets the pivot ratchet ever leave na; "
        "followed as written.",
        "pivothigh/pivotlow tie handling (strict, unique extreme) is the shared "
        "layer's rule (PINE_SEMANTICS.md §3.2 note), not a Pine-documented one.",
        "Dead-for-orders source content not reproduced: PositionPrice, nLongs / "
        "nShorts, sectionLongs / sectionShorts, last_open_*Condition, "
        "last_long/shortCondition, sum_long / sum_short, Short_MA, S_adx, "
        "Trailingsl, bsignal / ssignal, L_cloud and every plot(). None of them "
        "is read by either order call.",
        "No stop/limit/trail exit exists (close_all is a market close), so "
        "source_reproduce_stops is False.",
        "The source has no date-range inputs and no inDateRange flag; the "
        "/*backtest window is the backtester's, not the strategy's (§二.8).",
        "strategy() declares only title/overlay: Pine defaults fixed / 1 unit, "
        "commission 0%, pyramiding 0, initial capital 1000000, "
        "process_orders_on_close=false.",
        "Leverage, margin, liquidation, funding and contract-step rounding are "
        "not modelled (§二.4, §1.6).",
    ]

    def pine_indicators(self, dataframe, params):
        high = dataframe["high"]
        low = dataframe["low"]
        close = dataframe["close"]
        volume = dataframe["volume"]
        src = ta.pine_source(dataframe, params["src"])

        adx_len = int(params["ADX_len"])
        threshold = float(params["th"])
        pivot_len = int(params["prd"])
        factor = float(params["Factor"])
        atr_len = int(params["Pd"])
        cloud_len = int(params["len"])
        volume_mult = float(params["volume_f"])
        volume_len = int(params["sma_length"])

        # ---- calcADX(ADX_len), the CLASSIC branch --------------------------
        up = high.diff()
        down = -low.diff()
        plus_dm = up.where((up > down) & (up > 0), 0.0).where(up.notna())
        minus_dm = down.where((down > up) & (down > 0), 0.0).where(down.notna())
        true_range = ta.pine_rma(ta.pine_tr(dataframe), adx_len)
        di_plus_classic = _fixnan(100.0 * ta.pine_rma(plus_dm, adx_len) / true_range)
        di_minus_classic = _fixnan(100.0 * ta.pine_rma(minus_dm, adx_len) / true_range)
        di_sum = di_plus_classic + di_minus_classic
        # (sum == 0 ? 1 : sum) -- na != 0 stays na, as Pine's na == 0 is false
        denominator = di_sum.where(di_sum != 0, 1.0)
        adx_classic = 100.0 * ta.pine_rma(
            (di_plus_classic - di_minus_classic).abs() / denominator, adx_len
        )

        di_plus_masa, di_minus_masa, adx_masa = _masanakamura_adx(dataframe, adx_len)

        classic = params["ADX_options"] == "CLASSIC"
        di_plus = di_plus_classic if classic else di_plus_masa
        di_minus = di_minus_classic if classic else di_minus_masa
        adx = adx_classic if classic else adx_masa

        l_adx = (di_plus > di_minus) & (adx > threshold)

        # ---- pivot-centred ATR ratchet -------------------------------------
        pivot_high = ta.pine_pivothigh(high, pivot_len, pivot_len)
        pivot_low = ta.pine_pivotlow(low, pivot_len, pivot_len)
        ph = pivot_high.to_numpy(dtype=float)
        pl = pivot_low.to_numpy(dtype=float)
        n = len(dataframe)
        center = np.full(n, np.nan)
        running_center = np.nan
        for t in range(n):
            # lastpp = ph ? ph : pl ? pl : na   (na / 0.0 are false for a float)
            lastpp = ph[t] if not np.isnan(ph[t]) else pl[t]
            if not np.isnan(lastpp) and lastpp != 0.0:
                if np.isnan(running_center):
                    running_center = lastpp
                else:
                    running_center = (running_center * 2.0 + lastpp) / 3.0
            center[t] = running_center
        center_series = pd.Series(center, index=dataframe.index, dtype=float)
        atr = ta.pine_atr(dataframe, atr_len)
        up_band = center_series - factor * atr
        down_band = center_series + factor * atr
        up_values = up_band.to_numpy(dtype=float)
        down_values = down_band.to_numpy(dtype=float)
        close_values = close.to_numpy(dtype=float)

        trend_up = np.full(n, np.nan)
        trend_down = np.full(n, np.nan)
        trend = np.full(n, np.nan)
        for t in range(n):
            previous = t - 1
            prev_close = close_values[previous] if t >= 1 else np.nan
            prev_up = trend_up[previous] if t >= 1 else np.nan
            prev_down = trend_down[previous] if t >= 1 else np.nan
            prev_trend = trend[previous] if t >= 1 else np.nan
            # close[1] > TUp[1] ? max(Up, TUp[1]) : Up
            trend_up[t] = (
                np.fmax(up_values[t], prev_up) if prev_close > prev_up else up_values[t]
            )
            # close[1] < TDown[1] ? min(Dn, TDown[1]) : Dn
            trend_down[t] = (
                np.fmin(down_values[t], prev_down) if prev_close < prev_down else down_values[t]
            )
            # close > TDown[1] ? 1 : close < TUp[1] ? -1 : nz(Trend[1], 1)
            if close_values[t] > prev_down:
                trend[t] = 1.0
            elif close_values[t] < prev_up:
                trend[t] = -1.0
            else:
                trend[t] = 1.0 if np.isnan(prev_trend) else prev_trend

        trend_series = pd.Series(trend, index=dataframe.index, dtype=float)
        s_atr = trend_series == -1
        l_atr = trend_series == 1

        # ---- MESA/AMA "cloud" ----------------------------------------------
        source_values = src.to_numpy(dtype=float)
        # er = abs(change(src, len)) / sum(abs(change(src)), len)
        change_over_len = src - src.shift(cloud_len)
        sum_of_changes = src.diff().abs().rolling(cloud_len, min_periods=cloud_len).sum()
        er = (change_over_len.abs() / sum_of_changes).to_numpy(dtype=float)
        alpha_values = _compute_alpha(source_values, er, er * 0.1)

        mama = np.full(n, np.nan)
        fama = np.full(n, np.nan)
        kama = np.full(n, np.nan)
        for t in range(n):
            previous = t - 1
            a = alpha_values[t]
            b = a / 2.0
            prev_mama = 0.0 if (t < 1 or np.isnan(mama[previous])) else mama[previous]
            prev_fama = 0.0 if (t < 1 or np.isnan(fama[previous])) else fama[previous]
            prev_kama = 0.0 if (t < 1 or np.isnan(kama[previous])) else kama[previous]
            mama[t] = a * source_values[t] + (1.0 - a) * prev_mama
            fama[t] = b * mama[t] + (1.0 - b) * prev_fama
            kama_alpha = (er[t] * (b - a) + a) ** 2
            kama[t] = kama_alpha * source_values[t] + (1.0 - kama_alpha) * prev_kama

        kama_series = pd.Series(kama, index=dataframe.index, dtype=float)
        s_cloud = kama_series < kama_series.shift(1)
        l_cloud = kama_series > kama_series.shift(1)

        # ---- alignment conditions ------------------------------------------
        sma1 = ta.pine_sma(src, int(params["Length1"]))
        sma2 = ta.pine_sma(src, int(params["Length2"]))
        sma3 = ta.pine_sma(src, int(params["Length3"]))
        long_ma = (sma1 < close) & (sma2 < close) & (sma3 < close)
        volume_condition = volume > ta.pine_sma(volume, volume_len) * volume_mult

        bulls_on_the_control = long_ma & volume_condition & l_adx & (~s_cloud)
        close_condition = s_cloud & s_atr

        dataframe["pine_di_plus"] = di_plus
        dataframe["pine_di_minus"] = di_minus
        dataframe["pine_adx"] = adx
        dataframe["pine_trend"] = trend_series
        dataframe["pine_kama"] = kama_series
        dataframe["pine_mama"] = pd.Series(mama, index=dataframe.index, dtype=float)
        dataframe["pine_fama"] = pd.Series(fama, index=dataframe.index, dtype=float)
        dataframe["pine_l_cloud"] = l_cloud
        dataframe["pine_l_adx"] = l_adx
        dataframe["pine_long_ma"] = long_ma
        dataframe["pine_volume_condition"] = volume_condition
        dataframe["pine_l_atr"] = l_atr
        dataframe["pine_s_atr"] = s_atr
        dataframe["pine_entry_condition"] = bulls_on_the_control
        dataframe["pine_close_condition"] = close_condition
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            # `Bulls_on_the_control` is what the entry `if` spells out inline.
            "entry_condition": dataframe["pine_entry_condition"].to_numpy(),
            "close_condition": dataframe["pine_close_condition"].to_numpy(),
        }

    def pine_script(self, broker, i, ctx):
        # if Long_MA and Volume_condt and L_adx and not S_cloud
        #     strategy.entry("L", strategy.long)
        if ctx["entry_condition"][i]:
            broker.entry("L", "long")
        # strategy.close_all(when = close_condt)
        broker.close_all(when=bool(ctx["close_condition"][i]))
