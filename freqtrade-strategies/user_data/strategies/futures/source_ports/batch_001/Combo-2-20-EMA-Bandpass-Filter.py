"""Port of sources/SM_4251450e4419c3f9.pine (batch_001/Combo-2-20-EMA-Bandpass-Filter.md).

Pine v5, HPotter's "combo" template: two sub-indicators each return a sticky
position (-1 / 0 / +1), the two must AGREE for an entry, and any disagreement
closes everything:

    EMA20(Length)                      # `close` vs a 2-bar high/low breakout
        xXA = ta.ema(close, Length)
        nHH = max(high, high[1]); nLL = min(low, low[1])
        nXS = (nLL > xXA or nHH < xXA) ? nLL : nHH
        pos = nXS > close[1] ? -1 : (nXS < close[1] ? 1 : nz(pos[1], 0))

    BPF(LengthBPF, Delta, SellZone, BuyZone)     # Ehlers bandpass filter on hl2
        beta  = cos(3.14 * (360 / LengthBPF) / 180)
        gamma = 1 / cos(3.14 * (720 * Delta / LengthBPF) / 180)
        alpha = gamma - sqrt(gamma * gamma - 1)
        BP = 0.5*(1-alpha)*(hl2 - hl2[2]) + beta*(1+alpha)*nz(BP[1]) - alpha*nz(BP[2])
        pos = BP > SellZone ? 1 : (BP <= BuyZone ? -1 : nz(pos[1], 0))

    StartTrade = time > timestamp(y, m, d, 00, 00)
    pos     = posEMA20 == 1  and prePosBPF == 1  and StartTrade ?  1
              : posEMA20 == -1 and prePosBPF == -1 and StartTrade ? -1 : 0
    possig  = reverse ? -pos : pos
    if possig ==  1 -> strategy.entry('Long',  strategy.long)
    if possig == -1 -> strategy.entry('Short', strategy.short)
    if possig ==  0 -> strategy.close_all()

`strategy(title=..., shorttitle=..., overlay=true)` declares no order property,
so Pine's documented defaults apply: `default_qty_type = strategy.fixed` with
`default_qty_value = 1` contract, `initial_capital = 1000000`, commission 0%,
`pyramiding = 0`, `process_orders_on_close = false`. There is no stop / limit /
trail call anywhere, so `source_reproduce_stops` is False: a position goes flat
only when the two indicators disagree (or by reversing).

FIDELITY: see source_fidelity_notes.
"""
from __future__ import annotations

import math

import numpy as np
import pandas as pd
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


def _hold_last(decisive: np.ndarray) -> np.ndarray:
    """Pine's `nz(pos[1], 0)` carry: hold the last decisive value, 0 before any.

    Both sub-indicators assign +/-1 only on the bars their comparison fires and
    otherwise carry the previous bar's value, so the carry is part of the
    signal, not an implementation detail. `nz` is why the seed is 0 and not na.
    """
    out = np.zeros(len(decisive), dtype=float)
    state = 0.0
    for i, value in enumerate(decisive):
        if not np.isnan(value):
            state = value
        out[i] = state
    return out


def _start_trade_mask(dataframe: pd.DataFrame, params: dict) -> np.ndarray:
    """Pine `time > timestamp(y, m, d, 00, 00)`.

    Pine builds `timestamp(y, m, d, 00, 00)` in the exchange's timezone and
    compares it against the bar's opening `time`. The shared layer's data is UTC
    (PINE_SEMANTICS section 3.4), so the comparison is made in UTC.
    """
    index = dataframe.index
    if not isinstance(index, pd.DatetimeIndex):
        raise ValueError("Pine `time` needs a DatetimeIndex; got a range index")
    stamp = index if index.tz is not None else index.tz_localize("UTC")
    start = pd.Timestamp(
        year=int(params["y"]), month=int(params["m"]), day=int(params["d"])
    ).tz_localize("UTC")
    # A DatetimeIndex comparison already yields the per-bar boolean array.
    return np.asarray(stamp > start)


class SMCombo220EmaBandpass_425145(PinePortBase, IStrategy):
    source_id = "SM_4251450e4419c3f9"
    source_file = "Combo-2-20-EMA-Bandpass-Filter.md"
    timeframe = "1h"
    can_short = True
    source_defaults: dict = {
        "Length": 14,
        "LengthBPF": 20,
        "Delta": 0.5,
        "SellZone": 5.0,
        "BuyZone": -5.0,
        "reverse": False,
        "d": 1,
        "m": 1,
        "y": 2005,
    }
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    source_reproduce_stops = False
    source_fidelity_notes = [
        "The source carries no `/*backtest` header at all, so it declares no "
        "period; the port uses this repository's mandated 1h fallback for "
        "headerless sources (the same fallback batch_001/Chande-Kroll-Stop.py "
        "and batch_001/Exit-from-specific-entries.py record). The bars are "
        "therefore hourly even though the source may have been authored on "
        "another period.",
        "`strategy(title=..., shorttitle=..., overlay=true)` names no order "
        "property, so the port carries Pine's documented defaults: fixed "
        "quantity of 1 contract, 0% commission, pyramiding 0, initial capital "
        "1000000, process_orders_on_close false.",
        "The title calls this the `2/20 EMA` but the EMA length input defaults "
        "to 14 and the only 20 in the source is LengthBPF; the md's argument "
        "table agrees with the source (v_input_int_1 = 14), so the port uses 14.",
        "md vs source, recorded not followed: the md's argument table renders "
        "`d` (From Day) and `m` (From Month) as `true` -- the exporter's "
        "rendering of the integer 1 in `v_input_int_3` / `v_input_int_4`. The "
        "source reads `input.int(1, minval=1, maxval=31)` and "
        "`input.int(1, minval=1, maxval=12)`; the port uses 1 for both.",
        "`3.14` is written literally in the source (not `math.pi`) and is kept "
        "literally here: the bandpass coefficients beta/gamma/alpha are computed "
        "from 3.14 exactly as the source computes them.",
        "`SellZone` / `BuyZone` (default +5 / -5) are compared against the "
        "bandpass value in PRICE units, not as a percentage or a normalised "
        "oscillator. Nothing is re-scaled here because the source compares "
        "absolutely, but the consequence is that the bandpass leg is 0 on any "
        "instrument whose filtered 2-bar move stays inside +/-5: on "
        "validate_pine's synthetic 100-scale frame the filter's whole range is "
        "[-2.16, 3.09], so both legs stay 0 and the strategy never opens "
        "(`ran_but_never_signalled_on_synthetic_data`), while on BTC/USDT:USDT "
        "1h 2024 the same code gives 2012 long and 2475 short bars. The zero-signal "
        "synthetic run is a price-scale artifact, not a suppressed signal path.",
        "The bandpass recursion uses `nz(BP[1])` / `nz(BP[2])`, so on the first "
        "two bars -- where hl2[2] is not yet available and BP itself is na -- "
        "the memory terms read as 0 and BP stays na; the port reproduces that "
        "instead of seeding BP with a number.",
        "Pine treats na in a boolean context as false. Every comparison here "
        "(`nXS > close[1]`, `BP > SellZone`, `nXS < close[1]`) is therefore na "
        "-> false on the bars where its operand is na, which is why the sticky "
        "position simply carries through the warm-up window.",
        "The EMA is seeded with the first observation (pine_ta.pine_ema's "
        "documented modelling choice); TradingView's exact seeding rule is not "
        "public, so the first bars of the EMA/bandpass series are an unresolved "
        "parity risk rather than a certified match (PINE_SEMANTICS section 3.1).",
        "`pine_highest` / `pine_lowest` are not used here -- nHH/nLL are only "
        "2-bar maxima of the raw high/low -- so the sma/highest na-window "
        "question (PINE_SEMANTICS section 3.2) does not arise.",
        "There is no exit call of any kind, so `source_reproduce_stops` is "
        "False: `strategy.close_all()` is a market order placed on the bar the "
        "two indicators disagree and filling on the next bar's open, and a "
        "position still open at the end of the window stays open.",
        "Leverage, margin, liquidation and funding are not modelled; the venue's "
        "contract-step rounding is not modelled either (PINE_SEMANTICS sections "
        "2.4 and 1.6), so the framework and the engine can differ by a rounded "
        "quantity. That is measured separately by the chain verifier.",
    ]

    def pine_indicators(self, dataframe: pd.DataFrame, params: dict) -> pd.DataFrame:
        close = dataframe["close"]
        high = dataframe["high"]
        low = dataframe["low"]

        # --- EMA20(Length): a 2-bar breakout either side of an EMA -----------
        length = int(params["Length"])
        x_xa = ta.pine_ema(close, length)
        # math.max / math.min propagate na, so both legs are na on the first bar.
        n_hh = ta.pine_max(high, high.shift(1))
        n_ll = ta.pine_min(low, low.shift(1))
        # nLL > xXA or nHH < xXA ? nLL : nHH   (na comparisons are false)
        n_xs = pd.Series(
            np.where((n_ll > x_xa) | (n_hh < x_xa), n_ll, n_hh),
            index=dataframe.index, dtype=float,
        )
        previous_close = close.shift(1).to_numpy()
        xs = n_xs.to_numpy()
        # pos := nXS > close[1] ? -1 : (nXS < close[1] ? 1 : nz(pos[1], 0))
        decisive = np.where(xs > previous_close, -1.0,
                            np.where(xs < previous_close, 1.0, np.nan))
        pos_ema = pd.Series(_hold_last(decisive), index=dataframe.index)

        # --- BPF(LengthBPF, Delta, SellZone, BuyZone): Ehlers bandpass --------
        length_bpf = int(params["LengthBPF"])
        delta = float(params["Delta"])
        beta = math.cos(3.14 * (360.0 / length_bpf) / 180.0)
        gamma = 1.0 / math.cos(3.14 * (720.0 * delta / length_bpf) / 180.0)
        alpha = gamma - math.sqrt(gamma * gamma - 1.0)

        hl2 = (high + low) / 2.0
        x_price = hl2.to_numpy()
        bp = np.full(len(dataframe), np.nan)
        for i in range(len(dataframe)):
            # nz(BP[1]) / nz(BP[2]): a missing bar and an na value both read 0.
            memory_1 = bp[i - 1] if i >= 1 else 0.0
            memory_2 = bp[i - 2] if i >= 2 else 0.0
            memory_1 = 0.0 if np.isnan(memory_1) else memory_1
            memory_2 = 0.0 if np.isnan(memory_2) else memory_2
            # xPrice[2] is genuinely missing for the first two bars -> na.
            x_lag = x_price[i - 2] if i >= 2 else np.nan
            bp[i] = (0.5 * (1.0 - alpha) * (x_price[i] - x_lag)
                     + beta * (1.0 + alpha) * memory_1
                     - alpha * memory_2)
        sell_zone = float(params["SellZone"])
        buy_zone = float(params["BuyZone"])
        # pos := BP > SellZone ? 1 : (BP <= BuyZone ? -1 : nz(pos[1], 0))
        decisive = np.where(bp > sell_zone, 1.0,
                            np.where(bp <= buy_zone, -1.0, np.nan))
        pos_bpf = pd.Series(_hold_last(decisive), index=dataframe.index)

        # --- combining, gating and the reverse switch -------------------------
        start_trade = _start_trade_mask(dataframe, params)
        long_pos = ((pos_ema.to_numpy() == 1)
                    & (pos_bpf.to_numpy() == 1)
                    & start_trade)
        short_pos = ((pos_ema.to_numpy() == -1)
                     & (pos_bpf.to_numpy() == -1)
                     & start_trade)
        pos = np.where(long_pos, 1.0, np.where(short_pos, -1.0, 0.0))

        reverse = bool(params["reverse"])
        # iff_2 = reverse and pos == -1 ? 1 : pos
        # possig = reverse and pos == 1 ? -1 : iff_2
        after_reverse = np.where(reverse & (pos == -1.0), 1.0, pos)
        possig = np.where(reverse & (pos == 1.0), -1.0, after_reverse)

        dataframe["pine_ema_pos"] = pos_ema
        dataframe["pine_bpf_pos"] = pos_bpf
        dataframe["pine_pos"] = pos
        dataframe["pine_possig"] = possig
        return dataframe

    def pine_context(self, dataframe: pd.DataFrame, params: dict) -> dict:
        return {"possig": dataframe["pine_possig"].to_numpy()}

    def pine_script(self, broker, i: int, ctx: dict) -> None:
        possig = ctx["possig"][i]
        # if possig == 1
        #     strategy.entry('Long', strategy.long)
        if possig == 1:
            broker.entry("Long", "long")
        # if possig == -1
        #     strategy.entry('Short', strategy.short)
        if possig == -1:
            broker.entry("Short", "short")
        # if possig == 0
        #     strategy.close_all()
        if possig == 0:
            broker.close_all()
