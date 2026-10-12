"""Port of sources/SM_68926f3c4e9f631d.pine
(batch_001/Dual-Moving-Average-Indicators-Fusion-Strategy.md).

Pine v5, HPotter's "combo" template: two sub-indicators each return a sticky
position (-1 / 0 / +1), the two must AGREE for an entry, and any disagreement
closes everything:

    EMA20(Length)                      # `close` vs a 2-bar high/low breakout
        xXA = ta.ema(close, Length)
        nHH = max(high, high[1]); nLL = min(low, low[1])
        nXS = (nLL > xXA or nHH < xXA) ? nLL : nHH
        pos = nXS > close[1] ? -1 : (nXS < close[1] ? 1 : nz(pos[1], 0))

    APO(LengthShortEMA, LengthLongEMA)  # absolute price oscillator
        xAPO = ta.ema(close, LengthShortEMA) - ta.ema(close, LengthLongEMA)
        pos  = xAPO > 0 ? 1 : (xAPO < 0 ? -1 : nz(pos[1], 0))

    StartTrade = time > timestamp(y, m, d, 00, 00)
    pos     = posEMA20 == 1  and prePosAPO == 1  and StartTrade ?  1
              : posEMA20 == -1 and prePosAPO == -1 and StartTrade ? -1 : 0
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

The `/*backtest` header declares `period: 12h` on Futures_Binance BTC_USDT, so
`timeframe` is "12h"; `basePeriod: 15m` is the FMZ backtester's own filling
granularity for those 12h bars, not the strategy's period.

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


class SMCombo220EmaApo_68926f(PinePortBase, IStrategy):
    source_id = "SM_68926f3c4e9f631d"
    source_file = "Dual-Moving-Average-Indicators-Fusion-Strategy.md"
    timeframe = "12h"
    can_short = True
    source_defaults: dict = {
        "Length": 14,
        "LengthShortEMA": 10,
        "LengthLongEMA": 20,
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
        "`timeframe` is taken from the source's `/*backtest` header "
        "(`period: 12h`, Futures_Binance BTC_USDT). The header's "
        "`basePeriod: 15m` is the FMZ backtester's own fill granularity for "
        "those 12h bars and is not the strategy period.",
        "`strategy(title=..., shorttitle=..., overlay=true)` names no order "
        "property, so the port carries Pine's documented defaults: fixed "
        "quantity of 1 contract, 0% commission, pyramiding 0, initial capital "
        "1000000, process_orders_on_close false.",
        "The title calls this the `2/20 EMA` but the EMA length input defaults "
        "to 14; the `20` in the source is LengthLongEMA. The md's argument "
        "table agrees with the source (v_input_int_1 = 14), so the port uses 14.",
        "md vs source, recorded not followed: the md's argument table renders "
        "`d` (From Day) and `m` (From Month) as `true` -- the exporter's "
        "rendering of the integer 1 in `v_input_int_4` / `v_input_int_5`. The "
        "source reads `input.int(1, minval=1, maxval=31)` and "
        "`input.int(1, minval=1, maxval=12)`; the port uses 1 for both.",
        "The md's prose describes the combination loosely ('exits occur when "
        "the two issue opposite signals'). The source is narrower: `pos` is 0 "
        "whenever the two sub-positions are not BOTH +1 or BOTH -1, and 0 "
        "triggers `close_all()`. The port follows the source.",
        "The two EMAs are seeded with their first observation "
        "(pine_ta.pine_ema's documented modelling choice); TradingView's exact "
        "seeding rule is not public, so during the first bars the APO is not "
        "certified equal to the platform's (PINE_SEMANTICS section 3.1). Because "
        "APO is the DIFFERENCE of two EMAs and both share the same seed, the "
        "first bar has xAPO == 0 exactly, which the source resolves to "
        "`nz(pos[1], 0)` -- the port reproduces that too.",
        "Pine treats na in a boolean context as false, so every comparison here "
        "is na -> false on the bars where its operand is na and the sticky "
        "position carries through the warm-up window.",
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

        # --- APO(LengthShortEMA, LengthLongEMA) ------------------------------
        short_ema = ta.pine_ema(close, int(params["LengthShortEMA"]))
        long_ema = ta.pine_ema(close, int(params["LengthLongEMA"]))
        apo = short_ema - long_ema
        # iff_1 = xAPO < 0 ? -1 : nz(pos[1], 0)
        # pos   = xAPO > 0 ? 1 : iff_1
        values = apo.to_numpy()
        decisive = np.where(values > 0.0, 1.0,
                            np.where(values < 0.0, -1.0, np.nan))
        pos_apo = pd.Series(_hold_last(decisive), index=dataframe.index)

        # --- combining, gating and the reverse switch -------------------------
        start_trade = _start_trade_mask(dataframe, params)
        long_pos = ((pos_ema.to_numpy() == 1)
                    & (pos_apo.to_numpy() == 1)
                    & start_trade)
        short_pos = ((pos_ema.to_numpy() == -1)
                     & (pos_apo.to_numpy() == -1)
                     & start_trade)
        pos = np.where(long_pos, 1.0, np.where(short_pos, -1.0, 0.0))

        reverse = bool(params["reverse"])
        # iff_2 = reverse and pos == -1 ? 1 : pos
        # possig = reverse and pos == 1 ? -1 : iff_2
        after_reverse = np.where(reverse & (pos == -1.0), 1.0, pos)
        possig = np.where(reverse & (pos == 1.0), -1.0, after_reverse)

        dataframe["pine_ema_pos"] = pos_ema
        dataframe["pine_apo"] = apo
        dataframe["pine_apo_pos"] = pos_apo
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
