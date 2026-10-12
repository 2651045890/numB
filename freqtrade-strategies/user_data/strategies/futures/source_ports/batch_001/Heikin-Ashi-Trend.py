"""Port of sources/SM_22e076970ea13e42.pine (batch_001/Heikin-Ashi-Trend.md).

Pine v5. The file declares an ALERT indicator, not a strategy:

    indicator("Heikin-Ashi Trend Alert", overlay=true)

and a trading order block was appended to it by the conversion station:

    var trend = false
    trend := heikinashi_close_smooth >= heikinashi_open_smooth
    if trend
        strategy.entry("Enter Long", strategy.long)
    else
        strategy.entry("Enter Short", strategy.short)

`strategy.entry` cannot compile inside `indicator()`, so the "original strategy"
IS the indicator plus that block, and its trading behaviour is exactly what the
block does: enter whenever the condition holds, NEVER exit. The file contains no
`strategy()`, no `strategy.close`, no `strategy.exit` and no commented-out exit
line -- so every `strategy()` property is Pine's documented default (fixed / 1
contract, initial capital 1000000, commission 0%, pyramiding 0,
process_orders_on_close=false) and `source_reproduce_stops` is False.

The indicator, reproduced literally:

    ema_open  = ta.ema(open,  77)                  // 77 = input "EMA"
    ema_close = ta.ema(close, 77)
    ha_open/ha_close from the standard Heikin-Ashi transform
    heikinashi_open  = request.security(ticker.heikinashi(tickerid),
                                        timeframe.period, ema_open)
    heikinashi_close = request.security(..., ema_close)
    heikinashi_open_smooth  = ta.ema(heikinashi_open,  21)   // 21 = input
    heikinashi_close_smooth = ta.ema(heikinashi_close, 21)   //      "EMA Smoothing"
    trend = heikinashi_close_smooth >= heikinashi_open_smooth

`if trend` is a genuine boolean: this source is NOT one of the conversion
station's `x = ... ? -1 : 0` shapes, so the minus-truthiness trap of
PINE_SEMANTICS.md 1.17 does not apply here. On the early bars where both smoothed
series are still na the comparison is na, and Pine reads an na condition as
false -> the `else` arm runs (a short entry). The numpy comparison of two NaN
values is likewise False, so the port reproduces that without special-casing.

`var last_trend = trend` is dead code in the source (never read) and is not
reproduced.
"""
import numpy as np
import pandas as pd
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


class SMHeikinAshiTrend_22e076(PinePortBase, IStrategy):
    source_id = "SM_22e076970ea13e42"
    source_file = "Heikin-Ashi-Trend.md"
    timeframe = "4h"
    can_short = True
    source_defaults: dict = {"ema_input": 77, "ema_smoothing": 21}
    # No `strategy()` call exists in the source, so Pine's documented defaults
    # apply: fixed / 1 contract, 1000000 initial capital, 0% commission,
    # pyramiding 0, process_orders_on_close = false.
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    source_reproduce_stops = False
    source_mintick = 0.1
    source_fidelity_notes = [
        "The source is an `indicator()`, not a `strategy()`: the trading order "
        "block appended by the conversion station is the whole trading "
        "behaviour (entry on the condition, no exit). No `strategy()` "
        "declaration exists, so fixed/1, 1000000 capital, 0% commission and "
        "pyramiding 0 are Pine's documented defaults rather than declarations.",
        "NO exit exists in the source -- no `strategy.close`, no "
        "`strategy.exit`, not even a commented-out one. A position is closed "
        "only by the opposite entry reversing it, and a position still open at "
        "the end of the window stays open.",
        "`request.security(ticker.heikinashi(syminfo.tickerid), "
        "timeframe.period, expr)` is on the CHART's own timeframe, so it is not "
        "a multi-timeframe request: it is the deterministic Heikin-Ashi "
        "transform of the same bars. The port computes the HA bars directly "
        "instead of resampling, which PINE_SEMANTICS.md section 2.1 does not "
        "model but which is exact here because no resampling is involved.",
        "MODELLING CHOICE (parity risk): the first Heikin-Ashi bar is seeded "
        "`haOpen = (open + close) / 2`, the documented formula. TradingView "
        "does not publish the seed used by the `ticker.heikinashi` built-in; "
        "any difference decays geometrically (factor 1/2 per bar), so it can "
        "only affect the warm-up bars.",
        "MODELLING CHOICE (parity risk): `ta.ema` is seeded with the first "
        "non-na value (pine_ta.pine_ema), the same choice PINE_SEMANTICS.md "
        "3.1 records for every EMA-based port.",
        "na propagates through the comparison: `heikinashi_close_smooth >= "
        "heikinashi_open_smooth` is na while either EMA is warming up, and "
        "Pine evaluates an na condition as false, i.e. the short arm runs. "
        "pandas `>=` on NaN is likewise False, so no special-casing is added.",
        "Display-only statements are not reproduced: the `overlay`, the "
        "`shouldShowDebugInfo` input (group DEVELOPER) and the alert wiring.",
        "`var last_trend = trend` is never read in the source and is dropped.",
        "Leverage, margin, liquidation, funding and the venue's contract-step "
        "rounding are not modelled (PINE_SEMANTICS.md section 2).",
    ]

    def pine_indicators(self, dataframe, params):
        open_ = dataframe["open"].to_numpy(dtype=float)
        high = dataframe["high"].to_numpy(dtype=float)
        low = dataframe["low"].to_numpy(dtype=float)
        close = dataframe["close"].to_numpy(dtype=float)

        # Heikin-Ashi transform, as `ticker.heikinashi` builds it:
        #   haClose = (open + high + low + close) / 4
        #   haOpen  = (haOpen[1] + haClose[1]) / 2
        ha_close = (open_ + high + low + close) / 4.0
        ha_open = np.full(len(dataframe), np.nan, dtype=float)
        previous_open = np.nan
        previous_close = np.nan
        for t in range(len(dataframe)):
            if np.isfinite(previous_open) and np.isfinite(previous_close):
                ha_open[t] = (previous_open + previous_close) / 2.0
            else:
                # First bar: Pine's documented HA seed.
                ha_open[t] = (open_[t] + close[t]) / 2.0
            previous_open = ha_open[t]
            previous_close = ha_close[t]

        ha_open = pd.Series(ha_open, index=dataframe.index, dtype=float)
        ha_close = pd.Series(ha_close, index=dataframe.index, dtype=float)

        # ema_open / ema_close are re-evaluated inside the security context, so
        # the `open` / `close` they smooth are the Heikin-Ashi ones.
        heikinashi_open = ta.pine_ema(ha_open, int(params["ema_input"]))
        heikinashi_close = ta.pine_ema(ha_close, int(params["ema_input"]))
        smoothing = int(params["ema_smoothing"])
        open_smooth = ta.pine_ema(heikinashi_open, smoothing)
        close_smooth = ta.pine_ema(heikinashi_close, smoothing)

        trend = (close_smooth >= open_smooth).fillna(False)
        dataframe["pine_trend"] = trend.astype(bool)
        return dataframe

    def pine_context(self, dataframe, params):
        return {"trend": dataframe["pine_trend"].to_numpy(dtype=bool)}

    def pine_script(self, broker, i, ctx):
        # if trend
        #     strategy.entry("Enter Long", strategy.long)
        # else
        #     strategy.entry("Enter Short", strategy.short)
        if ctx["trend"][i]:
            broker.entry("Enter Long", "long")
        else:
            broker.entry("Enter Short", "short")
