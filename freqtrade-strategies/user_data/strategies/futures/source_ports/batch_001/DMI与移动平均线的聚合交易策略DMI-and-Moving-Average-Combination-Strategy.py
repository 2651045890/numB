"""Port of sources/SM_a3f1fda9218d27ee.pine
(batch_001/DMI与移动平均线的聚合交易策略DMI-and-Moving-Average-Combination-Strategy.md).

Pine v4 (`//@version=4`), HPotter's "combo" template: two sub-indicators each
return a sticky position (-1 / 0 / +1), the two must AGREE for an entry, and any
disagreement closes everything.

    Reversal123(Length, KSmoothing, DLength, Level)      # 123 / Jensen reversal
        vFast = sma(stoch(close, high, low, Length), KSmoothing)
        vSlow = sma(vFast, DLength)
        pos = close[2] < close[1] and close > close[1] and vFast < vSlow
              and vFast > Level                                     ?  1
            : close[2] > close[1] and close < close[1] and vFast > vSlow
              and vFast < Level                                     ? -1
            : nz(pos[1], 0)

    DMIMA(Length_MA, Length_DMI)                         # DMI cross + MA cross
        xMA  = sma(close, Length_MA)
        up   = change(high);  down = -change(low)
        trur = rma(tr, Length_DMI)
        xPDI = fixnan(100 * rma(up > down and up > 0     ? up   : 0, Length_DMI) / trur)
        xNDI = fixnan(100 * rma(down > up and down > 0   ? down : 0, Length_DMI) / trur)
        bMDILong  = nPDI > nNDI and nPDI[1] < nNDI[1]
        bMDIShort = nPDI < nNDI and nPDI[1] > nNDI[1]
        bMALong   = close > nMA and close[1] < nMA[1]
        bMAShort  = close < nMA and close[1] > nMA[1]
        pos = bMDILong and bMALong ? 1 : (bMDIShort and bMAShort ? -1 : nz(pos[1], 0))

    pos    = posReversal123 == 1 and posDMIMA == 1 ?  1
             : posReversal123 == -1 and posDMIMA == -1 ? -1 : 0
    possig = reverse ? -pos : pos
    if possig ==  1 -> strategy.entry("Long",  strategy.long)
    if possig == -1 -> strategy.entry("Short", strategy.short)
    if possig ==  0 -> strategy.close_all()

`strategy(title=..., shorttitle=..., overlay=true)` declares no order property,
so Pine's documented defaults apply: `default_qty_type = strategy.fixed` with
`default_qty_value = 1` contract, `initial_capital = 1000000`, commission 0%,
`pyramiding = 0`, `process_orders_on_close = false`. There is no stop / limit /
trail call anywhere, so `source_reproduce_stops` is False: a position goes flat
only when the two indicators disagree (or by reversing).

The `/*backtest` header declares `period: 10m` on Futures_Binance BTC_USDT, so
`timeframe` is "10m"; `basePeriod: 1m` is the FMZ backtester's own filling
granularity for those 10m bars, not the strategy's period.

FIDELITY: see source_fidelity_notes.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


def _hold_last(decisive: np.ndarray) -> np.ndarray:
    """Pine's `nz(pos[1], 0)` carry: hold the last decisive value, 0 before any.

    Reversal123 and DMIMA both assign +/-1 only on the bars their conditions
    fire and otherwise carry the previous bar's value, so the carry is part of
    the signal, not an implementation detail. `nz` is why the seed is 0.
    """
    out = np.zeros(len(decisive), dtype=float)
    state = 0.0
    for i, value in enumerate(decisive):
        if not np.isnan(value):
            state = value
        out[i] = state
    return out


def _pine_stoch(close: pd.Series, high: pd.Series, low: pd.Series,
                length: int) -> pd.Series:
    """Pine v4 `stoch(source, high, low, length)`.

    100 * (source - lowest(low, length)) / (highest(high, length) - lowest(low, length))

    `pine_ta` has no `stoch`, so the formula is transcribed here verbatim. A zero
    denominator is Pine's na (the platform evaluates x/0 to na), so inf is folded
    back to na before the smoothing that consumes it.
    """
    lowest_low = ta.pine_lowest(low, length)
    highest_high = ta.pine_highest(high, length)
    value = 100.0 * (close - lowest_low) / (highest_high - lowest_low)
    return value.replace([np.inf, -np.inf], np.nan)


def _bare_tr(dataframe: pd.DataFrame) -> pd.Series:
    """Pine v4's bare `tr` variable, i.e. `ta.tr` with `handle_na = false`.

    max(high - low, |high - close[1]|, |low - close[1]|), na on the FIRST bar
    because close[1] does not exist there. `pine_ta.pine_tr` returns the first
    bar's high - low instead (it models `ta.tr(true)`, which is what `pine_atr`
    needs), so the bare-`tr` series is built here -- the difference is a one-bar
    offset in the seeding point of any `rma` over it (PINE_SEMANTICS section 3.7,
    where this boundary is recorded as a public-layer item that was not fixed).
    """
    high, low, close = dataframe["high"], dataframe["low"], dataframe["close"]
    previous_close = close.shift(1)
    value = pd.concat(
        [
            (high - low).abs(),
            (high - previous_close).abs(),
            (low - previous_close).abs(),
        ],
        axis=1,
    ).max(axis=1)
    # `tr` propagates the missing close[1]: the first bar is na, not high - low.
    return value.where(previous_close.notna())


def _fixnan(series: pd.Series) -> pd.Series:
    """Pine v4 `fixnan`: replace na with the most recent non-na value."""
    return series.ffill()


class SMCombo123ReversalDmiMa_a3f1fd(PinePortBase, IStrategy):
    source_id = "SM_a3f1fda9218d27ee"
    source_file = "DMI与移动平均线的聚合交易策略DMI-and-Moving-Average-Combination-Strategy.md"
    timeframe = "10m"
    can_short = True
    source_defaults: dict = {
        "Length": 14,
        "KSmoothing": 1,
        "DLength": 3,
        "Level": 50,
        "Length_MA": 30,
        "Length_DMI": 14,
        "reverse": False,
    }
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    source_reproduce_stops = False
    source_fidelity_notes = [
        "`timeframe` is taken from the source's `/*backtest` header "
        "(`period: 10m`, Futures_Binance BTC_USDT). The header's "
        "`basePeriod: 1m` is the FMZ backtester's own fill granularity for those "
        "10m bars and is not the strategy period.",
        "`strategy(title=..., shorttitle=..., overlay=true)` names no order "
        "property, so the port carries Pine's documented defaults: fixed "
        "quantity of 1 contract, 0% commission, pyramiding 0, initial capital "
        "1000000, process_orders_on_close false.",
        "md vs source, recorded not followed: the md's argument table renders "
        "`KSmoothing` as `true` (v_input_2|true) -- the exporter's rendering of "
        "the integer 1. The source reads `input(1, minval=1)` and the port uses "
        "1; with KSmoothing = 1 the `sma(stoch(...), 1)` smoothing is the "
        "identity, which is what makes vFast equal the raw stochastic.",
        "The source defines `fFilter(xSeriesSum, xSeriesV, Filter)` and never "
        "calls it. It is dead code and is not reproduced; it places no order and "
        "computes no value any signal reads.",
        "md vs source, prose only, recorded not followed: the md's Strategy "
        "Description says the long trigger needs the 9-day slow stochastic to be "
        "BELOW 50 and the short needs the fast stochastic ABOVE 50, and words the "
        "price pattern as 'two consecutive closes above the previous close'. The "
        "source -- and the md's own code listing, which is byte-identical to it -- "
        "instead has long = `vFast < vSlow and vFast > Level` and short = "
        "`vFast > vSlow and vFast < Level` (Level defaulting to 50), over the "
        "reversal pattern `close[2] < close[1] and close > close[1]`. The code is "
        "the authority (rule 2) and the port follows it.",
        "md vs source, prose only: the md frames the strategy as three "
        "independent legs, but the source combines exactly two sticky "
        "sub-positions -- Reversal123, and DMIMA, which already contains both the "
        "DMI cross and the MA cross. The port reproduces the two-sub-position "
        "structure the code has.",
        "Pine v4's bare `tr` (used for `trur`) is `ta.tr` with `handle_na = "
        "false`, so it is na on the first bar; `pine_ta.pine_tr` models "
        "`ta.tr(true)` and returns high - low there. The bare-`tr` semantics are "
        "transcribed locally so that the `rma` seed lands on the bar Pine seeds "
        "it on (PINE_SEMANTICS section 3.7).",
        "`pine_ta` has no `stoch`; the v4 formula "
        "100 * (close - lowest(low, n)) / (highest(high, n) - lowest(low, n)) is "
        "transcribed verbatim rather than replaced by a same-named library call.",
        "`fixnan` is not part of `pine_ta`; it is Pine's 'replace na with the "
        "latest non-na value' and is reproduced as a forward fill. Division by "
        "zero is Pine's na, so inf from the numpy division is folded back to na "
        "BEFORE the fixnan, exactly as the source nests it.",
        "`up > down and up > 0 ? up : 0` is na -> false -> 0 on the first bar "
        "(where `change(high)` is na), so the two DM series start at 0 rather "
        "than na; the port reproduces that instead of letting the na propagate.",
        "`sma` / `highest` / `lowest` return na until their window is full and na "
        "inside the window propagates (PINE_SEMANTICS section 3.2); the first "
        "Reversal123 value therefore needs Length + DLength bars and the first "
        "DMIMA value needs Length_DMI + 1 bars.",
        "The EMA seed question (PINE_SEMANTICS section 3.1) does not arise: this "
        "source uses only `sma` / `rma`, both of which the shared layer seeds "
        "with a full-window mean.",
        "There is no exit call of any kind, so `source_reproduce_stops` is "
        "False: `strategy.close_all()` is a market order placed on the bar the "
        "two indicators disagree and filling on the next bar's open, and a "
        "position still open at the end of the window stays open.",
        "`barcolor(...)` is display-only and is not reproduced.",
        "Leverage, margin, liquidation and funding are not modelled; the venue's "
        "contract-step rounding is not modelled either (PINE_SEMANTICS sections "
        "2.4 and 1.6), so the framework and the engine can differ by a rounded "
        "quantity. That is measured separately by the chain verifier.",
    ]

    def pine_indicators(self, dataframe: pd.DataFrame, params: dict) -> pd.DataFrame:
        close = dataframe["close"]
        high = dataframe["high"]
        low = dataframe["low"]

        # --- Reversal123(Length, KSmoothing, DLength, Level) -----------------
        stochastic = _pine_stoch(close, high, low, int(params["Length"]))
        v_fast = ta.pine_sma(stochastic, int(params["KSmoothing"]))
        v_slow = ta.pine_sma(v_fast, int(params["DLength"]))
        level = float(params["Level"])
        c1 = close.shift(1)
        c2 = close.shift(2)
        # na comparisons are false, as Pine's are.
        long_cond = (c2 < c1) & (close > c1) & (v_fast < v_slow) & (v_fast > level)
        short_cond = (c2 > c1) & (close < c1) & (v_fast > v_slow) & (v_fast < level)
        decisive = np.where(long_cond, 1.0, np.where(short_cond, -1.0, np.nan))
        pos_reversal = pd.Series(_hold_last(decisive), index=dataframe.index)

        # --- DMIMA(Length_MA, Length_DMI) ------------------------------------
        length_dmi = int(params["Length_DMI"])
        x_ma = ta.pine_sma(close, int(params["Length_MA"]))
        up = ta.pine_change(high)
        down = -ta.pine_change(low)
        trur = ta.pine_rma(_bare_tr(dataframe), length_dmi)
        # `up > down and up > 0 ? up : 0` -- the na first bar resolves to 0.
        plus_dm = up.where((up > down) & (up > 0.0), 0.0)
        minus_dm = down.where((down > up) & (down > 0.0), 0.0)
        raw_pdi = 100.0 * ta.pine_rma(plus_dm, length_dmi) / trur
        raw_ndi = 100.0 * ta.pine_rma(minus_dm, length_dmi) / trur
        pdi = _fixnan(raw_pdi.replace([np.inf, -np.inf], np.nan))
        ndi = _fixnan(raw_ndi.replace([np.inf, -np.inf], np.nan))

        # nPDI_1 / nNDI_1 / nMA_1 are the [1] of the (already fixnan'd) series.
        b_mdi_long = (pdi > ndi) & (pdi.shift(1) < ndi.shift(1))
        b_mdi_short = (pdi < ndi) & (pdi.shift(1) > ndi.shift(1))
        b_ma_long = (close > x_ma) & (close.shift(1) < x_ma.shift(1))
        b_ma_short = (close < x_ma) & (close.shift(1) > x_ma.shift(1))
        decisive = np.where(b_mdi_long & b_ma_long, 1.0,
                            np.where(b_mdi_short & b_ma_short, -1.0, np.nan))
        pos_dmima = pd.Series(_hold_last(decisive), index=dataframe.index)

        # --- combining and the reverse switch ---------------------------------
        pos = np.where(
            (pos_reversal.to_numpy() == 1) & (pos_dmima.to_numpy() == 1), 1.0,
            np.where(
                (pos_reversal.to_numpy() == -1) & (pos_dmima.to_numpy() == -1),
                -1.0, 0.0,
            ),
        )
        reverse = bool(params["reverse"])
        # possig = reverse and pos == 1 ? -1 : (reverse and pos == -1 ? 1 : pos)
        after_reverse = np.where(reverse & (pos == -1.0), 1.0, pos)
        possig = np.where(reverse & (pos == 1.0), -1.0, after_reverse)

        dataframe["pine_stoch"] = stochastic
        dataframe["pine_vfast"] = v_fast
        dataframe["pine_vslow"] = v_slow
        dataframe["pine_reversal_pos"] = pos_reversal
        dataframe["pine_pdi"] = pdi
        dataframe["pine_ndi"] = ndi
        dataframe["pine_ma"] = x_ma
        dataframe["pine_dmima_pos"] = pos_dmima
        dataframe["pine_pos"] = pos
        dataframe["pine_possig"] = possig
        return dataframe

    def pine_context(self, dataframe: pd.DataFrame, params: dict) -> dict:
        return {"possig": dataframe["pine_possig"].to_numpy()}

    def pine_script(self, broker, i: int, ctx: dict) -> None:
        possig = ctx["possig"][i]
        # if (possig == 1)
        #     strategy.entry("Long", strategy.long)
        if possig == 1:
            broker.entry("Long", "long")
        # if (possig == -1)
        #     strategy.entry("Short", strategy.short)
        if possig == -1:
            broker.entry("Short", "short")
        # if (possig == 0)
        #     strategy.close_all()
        if possig == 0:
            broker.close_all()
