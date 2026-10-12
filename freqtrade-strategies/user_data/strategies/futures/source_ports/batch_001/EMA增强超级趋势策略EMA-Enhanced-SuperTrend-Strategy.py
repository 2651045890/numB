"""Port of sources/SM_44c611525b1ba011.pine
(batch_001/EMA增强超级趋势策略EMA-Enhanced-SuperTrend-Strategy.md).

Pine v4 (`//@version=4`). The KivancOzbilgic SuperTrend, with the indicator's
display block and a pasted-in 305-period EMA of close that nothing reads:

    Periods    = input(10, "ATR Period")
    src        = input(hl2, "Source")
    Multiplier = input(3.0, "ATR Multiplier", step=0.1)
    changeATR  = input(true, "Change ATR Calculation Method ?")
    atr2       = sma(tr, Periods)
    atr        = changeATR ? atr(Periods) : atr2
    up         = src - Multiplier * atr
    up1        = nz(up[1], up)
    up        := close[1] > up1 ? max(up, up1) : up
    dn         = src + Multiplier * atr
    dn1        = nz(dn[1], dn)
    dn        := close[1] < dn1 ? min(dn, dn1) : dn
    trend      = 1
    trend     := nz(trend[1], trend)
    trend     := trend == -1 and close > dn1 ?  1
                : trend == 1  and close < up1 ? -1 : trend
    buySignal  = trend == 1  and trend[1] == -1
    sellSignal = trend == -1 and trend[1] ==  1

    if buySignal
        strategy.entry("BUY",  strategy.long,  when = window())
    if sellSignal
        strategy.entry("SELL", strategy.short, when = window())

`up`, `dn` and `trend` are all self-referential, so the recursion is walked bar
by bar in source order. `nz(x[1], x)` is not a plain shift: on the first bar
`x[1]` is na and the fallback is the value `x` was already given ON THIS bar
(the raw `src -/+ Multiplier*atr`, or the literal `1` for `trend`), which a
vectorised `.shift().fillna()` cannot express without knowing that.

There is no exit call anywhere in the source: a position is closed only when
the opposite signal reverses it, so `source_reproduce_stops` is False and a
position open at the end of the window stays open.

`strategy("SuperTrend STRATEGY", overlay=true)` declares nothing else, so the
Pine defaults apply: `fixed` sizing of 1 contract, initial capital 1000000,
0% commission, `pyramiding 0`, `process_orders_on_close=false`.

FIDELITY:

* `window()` is `=> true` in the source -- the six From/To date inputs are
  evaluated into `start`/`finish` and then never used by the function that
  guards the entries. The port therefore emits signals unconditionally, as the
  source does, rather than inventing a date filter. The date defaults are still
  carried in `source_defaults` because they are `input()` declarations.
* `atr(Periods)` is modelled as `rma(tr(true), Periods)` (pine_ta.pine_atr),
  i.e. the first bar's true range is `high - low` rather than na. This is the
  shared layer's named modelling choice for `ta.atr`; see PINE_SEMANTICS §3.7,
  which records that the seeding point of `rma(tr, n)` is unsettled and that
  the alternative (na on bar 0) shifts the whole ATR -- and therefore `up` /
  `dn` / `trend` -- by one bar of warmup. Not corrected here.
* Pine's ternary treats an na condition as false, so on the first bars
  `close[1] > up1` / `close[1] < dn1` fall through to the raw band and `trend`
  stays 1. The port reproduces that by testing `np.isfinite(previous) and ...`,
  not by filling the shifted values.
* `ema(close, 305)` (`out3`, from a `//@version=3` study pasted into the same
  script) is computed as `pine_ema_slow` for completeness. It feeds only
  `plot(out3)` and no condition; no order call reads it.
* `plot` / `plotshape` / `fill` / `barcolor` / `barssince`-driven bar colouring
  are display-only and are not reproduced.
* The source is annotated `//@version=4` while the pasted tail carries a
  `//@version=3` comment line; the platform resolves the first annotation. No
  call used here differs between v3 and v4.
* Leverage, margin, liquidation and funding are not modelled, and neither is
  the venue's contract-step rounding of order quantities -- the chain verifier
  measures that separately instead of treating it as a signal difference.
"""
import numpy as np
import pandas as pd
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


class SMEnhancedSuperTrend_44c611(PinePortBase, IStrategy):
    source_id = "SM_44c611525b1ba011"
    source_file = "EMA增强超级趋势策略EMA-Enhanced-SuperTrend-Strategy.md"
    timeframe = "6h"
    can_short = True
    source_defaults: dict = {
        "Periods": 10,
        "src": "hl2",
        "Multiplier": 3.0,
        "changeATR": True,
        "showsignals": False,
        "highlighting": True,
        "barcoloring": True,
        "FromMonth": 9,
        "FromDay": 1,
        "FromYear": 2018,
        "ToMonth": 1,
        "ToDay": 1,
        "ToYear": 9999,
        "len3": 305,
        "src3": "close",
    }
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    source_reproduce_stops = False
    source_fidelity_notes = [
        "`window()` is `=> true`: the From/To date inputs are evaluated into "
        "`start`/`finish` and never used, so entries fire unconditionally. The "
        "date defaults are still carried in source_defaults.",
        "`atr(Periods)` is modelled as rma(tr(true), Periods) via pine_ta."
        "pine_atr; the alternative seeding (na on bar 0) would shift the whole "
        "ATR/band/trend chain by one bar (PINE_SEMANTICS 3.7).",
        "`nz(x[1], x)` falls back to the CURRENT bar's raw value on the first "
        "bar, not to a plain shift; the recursion is walked bar by bar.",
        "Pine treats an na ternary condition as false, so the first bars take "
        "the raw band and trend stays 1 until the ATR is warm.",
        "`ema(close, 305)` (out3, pasted from a //@version=3 study) is computed "
        "as pine_ema_slow; it is plot-only and no order call reads it.",
        "No exit call exists: the position is closed only by the opposite "
        "entry reversing it, so source_reproduce_stops is False.",
        "plot/plotshape/fill/barcolor are display-only and are not reproduced.",
        "Initial capital is unset in the source, hence Pine's default 1000000; "
        "sizing is `fixed` 1 contract, 0% commission, pyramiding 0.",
    ]

    def pine_indicators(self, dataframe, params):
        periods = int(params["Periods"])
        multiplier = float(params["Multiplier"])
        source = ta.pine_source(dataframe, str(params["src"]))
        close = dataframe["close"]

        # atr2 = sma(tr, Periods); atr = changeATR ? atr(Periods) : atr2
        atr2 = ta.pine_sma(ta.pine_tr(dataframe, handle_na=False), periods)
        atr = ta.pine_atr(dataframe, periods) if bool(params["changeATR"]) else atr2

        src_values = source.to_numpy(dtype=float)
        close_values = close.to_numpy(dtype=float)
        atr_values = atr.to_numpy(dtype=float)
        size = len(dataframe)

        up = np.full(size, np.nan)
        dn = np.full(size, np.nan)
        up1 = np.full(size, np.nan)
        dn1 = np.full(size, np.nan)
        trend = np.full(size, np.nan)

        for i in range(size):
            raw_up = src_values[i] - multiplier * atr_values[i]
            # up1 = nz(up[1], up) -- `up` here is this bar's raw value already.
            previous_up = up[i - 1] if i >= 1 else np.nan
            up1[i] = raw_up if not np.isfinite(previous_up) else previous_up
            # up := close[1] > up1 ? max(up, up1) : up
            previous_close = close_values[i - 1] if i >= 1 else np.nan
            if np.isfinite(previous_close) and previous_close > up1[i]:
                up[i] = max(raw_up, up1[i])
            else:
                up[i] = raw_up

            raw_dn = src_values[i] + multiplier * atr_values[i]
            previous_dn = dn[i - 1] if i >= 1 else np.nan
            dn1[i] = raw_dn if not np.isfinite(previous_dn) else previous_dn
            # dn := close[1] < dn1 ? min(dn, dn1) : dn
            if np.isfinite(previous_close) and previous_close < dn1[i]:
                dn[i] = min(raw_dn, dn1[i])
            else:
                dn[i] = raw_dn

            # trend = 1; trend := nz(trend[1], trend); then the flip test.
            previous_trend = trend[i - 1] if i >= 1 else np.nan
            current = 1.0 if not np.isfinite(previous_trend) else previous_trend
            if current == -1.0 and np.isfinite(close_values[i]) and close_values[i] > dn1[i]:
                current = 1.0
            elif current == 1.0 and np.isfinite(close_values[i]) and close_values[i] < up1[i]:
                current = -1.0
            trend[i] = current

        trend_series = pd.Series(trend, index=dataframe.index)
        up_trend = trend_series == 1.0
        down_trend = trend_series == -1.0
        previous_up_trend = up_trend.shift(1).fillna(False)
        previous_down_trend = down_trend.shift(1).fillna(False)

        dataframe["pine_supertrend_up"] = up
        dataframe["pine_supertrend_down"] = dn
        dataframe["pine_supertrend_trend"] = trend
        # Pasted-in display-only study: ema(close, 305), never read by an order.
        dataframe["pine_ema_slow"] = ta.pine_ema(
            ta.pine_source(dataframe, str(params["src3"])), int(params["len3"])
        )
        dataframe["pine_long_condition"] = (up_trend & previous_down_trend).to_numpy()
        dataframe["pine_short_condition"] = (down_trend & previous_up_trend).to_numpy()
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "trend": dataframe["pine_supertrend_trend"].to_numpy(),
            "long_condition": dataframe["pine_long_condition"].to_numpy(),
            "short_condition": dataframe["pine_short_condition"].to_numpy(),
        }

    def pine_script(self, broker, i, ctx):
        # longCondition = buySignal
        # if (longCondition) strategy.entry("BUY", strategy.long, when = window())
        if ctx["long_condition"][i]:
            broker.entry("BUY", "long")
        # shortCondition = sellSignal
        # if (shortCondition) strategy.entry("SELL", strategy.short, when = window())
        if ctx["short_condition"][i]:
            broker.entry("SELL", "short")
