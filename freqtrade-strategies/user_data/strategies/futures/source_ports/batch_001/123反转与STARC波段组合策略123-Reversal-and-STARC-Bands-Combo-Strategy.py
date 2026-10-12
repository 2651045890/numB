"""Port of sources/SM_b90dd47e73773951.pine
(batch_001/123反转与STARC波段组合策略123-Reversal-and-STARC-Bands-Combo-Strategy.md).

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

    STARC(LengthMA, LengthATR, K)                        # Stoller average range
        xMA  = sma(close, LengthMA)
        xATR = atr(LengthATR)
        pos  = close > xMA + xATR*K ? 1
             : close < xMA - xATR*K ? -1 : nz(pos[1], 0)

    pos    = posReversal123 == 1 and posSTARC == 1 ?  1
             : posReversal123 == -1 and posSTARC == -1 ? -1 : 0
    possig = reverse ? -pos : pos
    if (possig ==  1) -> strategy.entry("Long",  strategy.long)
    if (possig == -1) -> strategy.entry("Short", strategy.short)
    if (possig ==  0) -> strategy.close_all()

`strategy(title=..., shorttitle=..., overlay=true)` declares no order property,
so Pine's documented defaults apply: `default_qty_type = strategy.fixed` with
`default_qty_value = 1` contract, `initial_capital = 1000000`, commission 0%,
`pyramiding = 0`, `process_orders_on_close = false`. There is no stop / limit /
trail call anywhere, so `source_reproduce_stops` is False: a position goes flat
only when the two indicators disagree (or by reversing).

The `/*backtest` header declares `period: 45m` on Futures_Binance BTC_USDT, so
`timeframe` is "45m"; `basePeriod: 5m` is the FMZ backtester's own filling
granularity for those 45m bars, not the strategy's period.

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

    Reversal123 and STARC both assign +/-1 only on the bars their conditions
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


class SMCombo123ReversalStarc_b90dd4(PinePortBase, IStrategy):
    source_id = "SM_b90dd47e73773951"
    source_file = "123反转与STARC波段组合策略123-Reversal-and-STARC-Bands-Combo-Strategy.md"
    timeframe = "45m"
    can_short = True
    source_defaults: dict = {
        "line1": True,
        "Length": 14,
        "KSmoothing": 1,
        "DLength": 3,
        "Level": 50,
        "line2": True,
        "LengthMA": 5,
        "LengthATR": 15,
        "K": 1.33,
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
        "(`period: 45m`, Futures_Binance BTC_USDT). The header's "
        "`basePeriod: 5m` is the FMZ backtester's own fill granularity for those "
        "45m bars and is not the strategy period.",
        "`strategy(title=..., shorttitle=..., overlay=true)` names no order "
        "property, so the port carries Pine's documented defaults: fixed "
        "quantity of 1 contract, 0% commission, pyramiding 0, initial capital "
        "1000000, process_orders_on_close false.",
        "md vs source, recorded not followed: the md's argument table renders "
        "`KSmoothing` as `true` (v_input_3|true) -- the exporter's rendering of "
        "the integer 1. The source reads `input(1, minval=1)` and the port uses "
        "1; with KSmoothing = 1 the `sma(stoch(...), 1)` smoothing is the "
        "identity, which is what makes vFast equal the raw stochastic.",
        "`line1 = input(true, \"---- 123 Reversal ----\")` and `line2 = "
        "input(true, \"---- STARC Bands ----\")` are declared by the source but "
        "are never read: they only put a divider in the inputs dialog. They are "
        "carried in `source_defaults` so the declared defaults are complete, and "
        "they place no order and gate nothing.",
        "`pine_ta` has no `stoch`; the v4 formula "
        "100 * (close - lowest(low, n)) / (highest(high, n) - lowest(low, n)) is "
        "transcribed verbatim rather than replaced by a same-named library call.",
        "md vs source, prose only, recorded not followed: the md's Strategy "
        "Description says the long signal needs the 9-day slow stochastic to be "
        "BELOW 50 and the short needs the fast stochastic ABOVE 50, and words the "
        "price pattern as 'two consecutive closes above the previous close'. The "
        "source -- and the md's own code listing, which is byte-identical to it -- "
        "instead has long = `vFast < vSlow and vFast > Level` and short = "
        "`vFast > vSlow and vFast < Level` (Level defaulting to 50), over the "
        "reversal pattern `close[2] < close[1] and close > close[1]`. The code is "
        "the authority (rule 2) and the port follows it.",
        "Pine v4's `atr(LengthATR)` is documented as `rma(tr(true), length)` -- "
        "`ta.tr` with `handle_na = true`, so its first bar is high - low and not "
        "na. That is exactly what `pine_ta.pine_atr` models, so the shared "
        "function is used here; the bare-`tr` variant (handle_na false) applies "
        "to this batch's DMI source, not to this one.",
        "validate_pine reports `ran_but_never_signalled_on_synthetic_data` for "
        "this port: on its low-volatility 100-scale synthetic frame `close` "
        "never leaves the STARC bands (`close > MA5 + 1.33 * ATR(15)` fires 0 "
        "times in 3000 bars) while Reversal123 alone fires 57 long / 74 short, "
        "so the conjunction is empty. On BTC/USDT:USDT 1h 2024 the same code "
        "produces 226 sign changes. Both legs are ATR- or level-scaled exactly "
        "as the source writes them; the empty synthetic run is an artifact of "
        "the synthetic series' volatility, not a suppressed signal path.",
        "`sma` / `highest` / `lowest` return na until their window is full and na "
        "inside the window propagates (PINE_SEMANTICS section 3.2); the first "
        "Reversal123 value therefore needs Length + DLength bars and the first "
        "STARC position needs max(LengthMA, LengthATR + 1) bars.",
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

        # --- STARC(LengthMA, LengthATR, K) -----------------------------------
        x_ma = ta.pine_sma(close, int(params["LengthMA"]))
        x_atr = ta.pine_atr(dataframe, int(params["LengthATR"]))
        k = float(params["K"])
        upper = x_ma + x_atr * k
        lower = x_ma - x_atr * k
        # pos := close > xSTARCBandUp ? 1 : (close < xSTARCBandDn ? -1 : nz(pos[1], 0))
        decisive = np.where(close > upper, 1.0,
                            np.where(close < lower, -1.0, np.nan))
        pos_starc = pd.Series(_hold_last(decisive), index=dataframe.index)

        # --- combining and the reverse switch ---------------------------------
        pos = np.where(
            (pos_reversal.to_numpy() == 1) & (pos_starc.to_numpy() == 1), 1.0,
            np.where(
                (pos_reversal.to_numpy() == -1) & (pos_starc.to_numpy() == -1),
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
        dataframe["pine_starc_upper"] = upper
        dataframe["pine_starc_lower"] = lower
        dataframe["pine_starc_pos"] = pos_starc
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
