"""Port of sources/SM_9d9fc78355e67b44.pine (batch_001/CVD背离量化交易策略CVD-Divergence-Quantitative-Trading-Strategy.md).

Pine v5, both sides. mmattman's CVD divergence strategy: a Bull/Bear balance
oscillator (Vadim Gimelfarb's "Bull & Bear Balance") is cumulated into a CVD,
and four pivot-based divergence conditions are read off it. A `strategy.exit`
OCA with a 5% stop and a 10% take-profit rides on top.

    // Bull & Bear Balance -> bullPower / bearPower (iff_1 .. iff_18)
    bullVolume = bullPower / (bullPower + bearPower) * volume
    bearVolume = bearPower / (bullPower + bearPower) * volume
    delta = bullVolume - bearVolume
    cvd   = ta.cum(delta)
    osc   = cvd

    plFound = not na(ta.pivotlow(osc, 7, 3))
    phFound = not na(ta.pivothigh(osc, 7, 3))
    _inRange(cond) => bars = ta.barssince(cond == true)
                      rangeLower <= bars and bars <= rangeUpper      // 5 .. 60

    oscHL = osc[3] > ta.valuewhen(plFound, osc[3], 1) and _inRange(plFound[1])
    priceLL = low[3] < ta.valuewhen(plFound, low[3], 1)
    bullCondAlert = priceLL and oscHL and plFound          // regular bullish

    oscLL = osc[3] < ta.valuewhen(plFound, osc[3], 1) and _inRange(plFound[1])
    priceHL = low[3] > ta.valuewhen(plFound, low[3], 1)
    hiddenBullCondAlert = priceHL and oscLL and plFound    // hidden bullish

    oscLH = osc[3] < ta.valuewhen(phFound, osc[3], 1) and _inRange(phFound[1])
    priceHH = high[3] > ta.valuewhen(phFound, high[3], 1)
    bearCondAlert = priceHH and oscLH and phFound          // regular bearish

    oscHH = osc[3] > ta.valuewhen(phFound, osc[3], 1) and _inRange(phFound[1])
    priceLH = high[3] < ta.valuewhen(phFound, high[3], 1)
    hiddenBearCondAlert = priceLH and oscHH and phFound    // hidden bearish

    le = bullCondAlert or hiddenBullCondAlert
    se = bearCondAlert or hiddenBearCondAlert
    ltp = se
    stp = le

    if le -> strategy.entry("Long",  strategy.long)
    if se -> strategy.entry("Short", strategy.short)
    if ltp -> strategy.close("Long")
    if stp -> strategy.close("Short")

    stopPer = input.float(5.0) / 100 ;  takePer = input.float(10.0) / 100
    longStop  = strategy.position_avg_price * (1 - stopPer)
    longTake  = strategy.position_avg_price * (1 + takePer)
    shortStop = strategy.position_avg_price * (1 + stopPer)
    shortTake = strategy.position_avg_price * (1 - takePer)
    if strategy.position_size > 0 -> strategy.exit("Close Long",  "Long",  stop=longStop,  limit=longTake)
    if strategy.position_size < 0 -> strategy.exit("Close Short", "Short", stop=shortStop, limit=shortTake)

THE `iff_*` TERNARY CHAIN IS REPRODUCED LITERALLY. `close[1]` is na on bar 0, so
Pine's `na < open` / `na > open` are false and the ELSE branch is taken; Python's
NaN comparisons are false in exactly the same way, and `np.maximum` (not the
builtin `max`) is used because Pine's `math.max` returns na if ANY argument is
na while Python's `max(nan, x)` silently returns whichever operand wins the
comparison. Only bar 0 is affected, and solely through the additive level of
`cvd`, which no condition reads (every condition compares two `cvd` samples).

THE EXITS ARE A RESTING OCA, NOT A TRAILING STOP. Both `stop=` and `limit=` are
given to one `strategy.exit` call, and the levels are anchored to
`strategy.position_avg_price` -- the live average entry price, re-read every bar
the position is held. They reach the framework through `pine_stop_level` /
`pine_limit_level` (custom_stoploss + the ROI override, PINE_SEMANTICS.md 1.8);
a port carrying only the stop leg would silently lose the take-profit.

`strategy()` declares only `title` / `shorttitle` / `overlay`, so every order
property is Pine's documented default: `strategy.fixed` quantity of 1 contract,
initial capital 1000000, commission 0%, pyramiding 0, `process_orders_on_close`
false. The `/*backtest` header declares `period: 1d` on Futures_Binance
BTC_USDT, so `timeframe` is "1d"; `basePeriod: 1h` is the FMZ backtester's own
fill granularity.

FIDELITY:

* The md claims PYRAMIDING UP TO 3 POSITIONS ("金字塔加仓:策略最多允许3个仓位的
  金字塔加仓" / "The strategy supports pyramiding with multiple positions") and
  a TRAILING stop. The code declares neither: `strategy()` sets no
  `pyramiding` (so 0, Pine's default) and the exit is a fixed-percent OCA with
  no `trail_points` / `trail_offset`. Code followed; both disagreements
  recorded (铁律 2).
* The md describes hidden bullish divergence as price making a higher HIGH in
  the Chinese text ("价格创新高") while the English says "higher low", and the
  code compares LOWS (`low[lbR] > valuewhen(plFound, low[lbR], 1)`). Code
  followed; the md text is internally inconsistent here.
* `le` / `se` use the ALERT conditions (`bullCondAlert` / `hiddenBullCondAlert`
  / `bearCondAlert` / `hiddenBearCondAlert`), NOT the `plot`-gated `bullCond` /
  `hiddenBullCond` / `bearCond` / `hiddenBearCond`. Every `plot*` input
  therefore changes only a line colour and no order; they are still carried in
  `source_defaults` because they are `input()` defaults.
* The commented-out `and (close > ema200)` / `or (close < ema200)` guards are
  commented out and place no condition; they are NOT restored.
* `ta.pivotlow` / `ta.pivothigh` use pine_ta's modelled definition (`length` on
  each side, strict uniqueness of the extreme, na inside the window suppresses
  the pivot). Pine does not publish its exact tie-breaking rule, so a bar whose
  extreme is tied with a neighbour is where the two could differ.
* `ta.valuewhen(cond, source, 1)` is the SECOND-most-recent occurrence, and on a
  bar where `cond` is true that is the previous pivot, not this one; that is what
  makes the comparison a pivot-to-pivot one.
* `ta.barssince` returns na before its condition has ever been true, and
  `rangeLower <= na` is false in Pine; pine_ta returns NaN and the comparisons
  are false. The `_inRange(plFound[1])` argument is the condition shifted ONE
  bar, i.e. the gap is measured to the pivot BEFORE the one under test.
* `ta.cum` is modelled with na treated as 0 (pine_ta.pine_cum), which is the one
  place bar 0's na `delta` could shift the whole CVD series; no condition reads
  the level itself, only differences of two samples, so an additive offset
  cancels.
* `bullPower / (bullPower + bearPower)` -- a zero denominator is masked to na
  rather than inf, matching Pine, which returns na for x/0.
* `plot` / `plotshape` / `fill` / `hline` / the commented `alertcondition`s and
  the colour variables are display-only and place no order.
* `ta.sma(cvd, periodMa)` is pine_ta.pine_sma: na until the window is full, na
  inside the window propagates. `cvdMa` feeds only the `cvd > cvdMa` line
  colour and `plotMa`, never an order.
* Leverage, margin, liquidation, funding and contract-step rounding are not
  modelled; the chain verifier measures the rounding separately.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


def _pmax(a, b):
    """Pine `math.max`: na if ANY argument is na (unlike Python's builtin)."""
    return np.maximum(a, b)


class SMCvdDivergence_9d9fc7(PinePortBase, IStrategy):
    source_id = "SM_9d9fc78355e67b44"
    source_file = "CVD背离量化交易策略CVD-Divergence-Quantitative-Trading-Strategy.md"
    timeframe = "1d"
    can_short = True
    source_defaults: dict = {
        "periodMa": 20,
        "plotMa": False,
        "lbR": 3,
        "lbL": 7,
        "rangeUpper": 60,
        "rangeLower": 5,
        "plotBull": True,
        "plotHiddenBull": True,
        "plotBear": True,
        "plotHiddenBear": True,
        "stopPer": 5.0,
        "takePer": 10.0,
    }
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    source_reproduce_stops = True
    source_mintick = 0.1
    source_fidelity_notes = [
        "The md claims pyramiding up to 3 positions ('金字塔加仓:策略最多允许3个仓位的"
        "金字塔加仓') and a trailing stop. The code declares neither: `strategy()` "
        "sets no `pyramiding` (Pine's default 0) and the exit is a fixed-percent "
        "OCA with no trail_points/trail_offset. Code followed, both disagreed "
        "with, nothing silently changed (铁律 2).",
        "The md's Chinese text calls hidden bullish divergence a higher HIGH "
        "('价格创新高') while its English text and the code both use the LOW "
        "(`low[lbR] > valuewhen(plFound, low[lbR], 1)`). Code followed; the md is "
        "internally inconsistent.",
        "The orders use the ALERT conditions (bullCondAlert / hiddenBullCondAlert "
        "/ bearCondAlert / hiddenBearCondAlert), not the plot-gated bullCond / "
        "hiddenBullCond / bearCond / hiddenBearCond. Every plot* input therefore "
        "changes only a line colour, never an order; they are still carried in "
        "source_defaults because they are input() defaults.",
        "The commented-out `and (close > ema200)` / `or (close < ema200)` guards "
        "are commented out and place no condition; they are NOT restored.",
        "Both legs of the OCA exit are reproduced (stop= 5%, limit= 10%, anchored "
        "to strategy.position_avg_price); a stop-only port would silently drop "
        "the take-profit (PINE_SEMANTICS.md 1.8).",
        "The levels are re-read from the LIVE average entry price on every bar "
        "the position is held, so the engine re-places the same-id exit each bar "
        "and Pine's same-id replacement applies (PINE_SEMANTICS.md 1.12/3.6).",
        "`iff_1 .. iff_18` are reproduced literally, including the na branches: "
        "close[1] is na on bar 0, Pine's na comparisons are false so the ELSE "
        "branch is taken, and Python's NaN comparisons are false in the same "
        "way. np.maximum is used instead of the builtin max because Pine's "
        "math.max returns na if ANY argument is na. Only bar 0 is affected, and "
        "only through the additive level of cvd, which no condition reads.",
        "`bullPower / (bullPower + bearPower)` masks a zero denominator to na "
        "rather than inf, matching Pine's x/0 -> na.",
        "ta.pivotlow/ta.pivothigh use pine_ta's modelled definition (length on "
        "each side, strict uniqueness of the extreme, na in the window suppresses "
        "the pivot); Pine does not publish its tie-breaking rule.",
        "ta.valuewhen(cond, source, 1) is the SECOND-most-recent occurrence; on a "
        "bar where cond is true that is the previous pivot, which is what makes "
        "the comparison pivot-to-pivot.",
        "ta.barssince is na before its condition is ever true and `rangeLower <= "
        "na` is false in Pine; the modelled NaN comparisons are false. The "
        "_inRange argument is plFound[1] / phFound[1], i.e. the pivot BEFORE the "
        "one under test.",
        "ta.cum treats na as 0 (pine_ta.pine_cum). That is the only place bar 0's "
        "na delta can shift the series, and it is an additive offset that cancels "
        "in every difference the conditions take.",
        "`strategy()` declares only title/shorttitle/overlay, so qty_type=fixed, "
        "qty_value=1 contract, commission=0%, pyramiding=0 and "
        "initial_capital=1000000 are Pine's documented defaults.",
        "plot / plotshape / fill / hline / the commented alertconditions and the "
        "colour variables are display-only and place no order.",
        "Leverage, margin, liquidation, funding and contract-step rounding are "
        "not modelled; the chain verifier measures the rounding separately.",
    ]

    def pine_indicators(self, dataframe, params):
        open_ = dataframe["open"]
        high = dataframe["high"]
        low = dataframe["low"]
        close = dataframe["close"]
        volume = dataframe["volume"]
        prev_close = close.shift(1)

        # close[1] < open / close[1] > open. na compares false, as in Pine.
        below = prev_close < open_
        above = prev_close > open_

        # --- Bull power / bear power (Vadim Gimelfarb Bull & Bear Balance) ---
        iff_1 = _pmax(high - prev_close, close - low).where(
            below, _pmax(high - open_, close - low)
        )
        iff_2 = (high - low).where(above, _pmax(open_ - prev_close, high - low))
        iff_3 = _pmax(high - prev_close, close - low).where(below, high - open_)
        iff_4 = (high - low).where(above, _pmax(open_ - prev_close, high - low))
        iff_5 = _pmax(open_ - prev_close, high - low).where(below, high - low)
        iff_6 = _pmax(high - open_, close - low).where(above, iff_5)
        iff_7 = iff_4.where(high - close < close - low, iff_6)
        iff_8 = iff_3.where(high - close > close - low, iff_7)
        iff_9 = iff_2.where(close > open_, iff_8)
        bull_power = iff_1.where(close < open_, iff_9)

        iff_10 = _pmax(prev_close - open_, high - low).where(above, high - low)
        iff_11 = _pmax(prev_close - low, high - close).where(
            above, _pmax(open_ - low, high - close)
        )
        iff_12 = _pmax(prev_close - open_, high - low).where(above, high - low)
        iff_13 = _pmax(prev_close - low, high - close).where(above, open_ - low)
        iff_14 = _pmax(open_ - low, high - close).where(below, high - low)
        iff_15 = _pmax(prev_close - open_, high - low).where(above, iff_14)
        iff_16 = iff_13.where(high - close < close - low, iff_15)
        iff_17 = iff_12.where(high - close > close - low, iff_16)
        iff_18 = iff_11.where(close > open_, iff_17)
        bear_power = iff_10.where(close < open_, iff_18)

        # --- Bull & bear pressure volume / delta / CVD ---
        # A zero denominator is na in Pine, so mask it rather than divide by 0.
        denominator = (bull_power + bear_power).replace(0.0, np.nan)
        bull_volume = (bull_power / denominator) * volume
        bear_volume = (bear_power / denominator) * volume
        delta = bull_volume - bear_volume
        cvd = ta.pine_cum(delta)
        cvd_ma = ta.pine_sma(cvd, int(params["periodMa"]))

        lb_r = int(params["lbR"])
        lb_l = int(params["lbL"])
        range_upper = float(params["rangeUpper"])
        range_lower = float(params["rangeLower"])

        osc = cvd
        pl_found = ta.pine_pivotlow(osc, lb_l, lb_r).notna()
        ph_found = ta.pine_pivothigh(osc, lb_l, lb_r).notna()

        # _inRange(cond) => bars = ta.barssince(cond == true)
        #                  rangeLower <= bars and bars <= rangeUpper
        bars_since_pl = ta.pine_barssince(pl_found.shift(1).fillna(False))
        bars_since_ph = ta.pine_barssince(ph_found.shift(1).fillna(False))
        in_range_pl = (bars_since_pl >= range_lower) & (bars_since_pl <= range_upper)
        in_range_ph = (bars_since_ph >= range_lower) & (bars_since_ph <= range_upper)

        osc_lag = osc.shift(lb_r)
        low_lag = low.shift(lb_r)
        high_lag = high.shift(lb_r)

        # --- Regular bullish: osc higher low, price lower low ---
        osc_prev_low = ta.pine_valuewhen(pl_found, osc_lag, 1)
        low_prev_low = ta.pine_valuewhen(pl_found, low_lag, 1)
        osc_hl = (osc_lag > osc_prev_low) & in_range_pl
        price_ll = low_lag < low_prev_low
        bull_cond_alert = price_ll & osc_hl & pl_found

        # --- Hidden bullish: osc lower low, price higher low ---
        osc_ll = (osc_lag < osc_prev_low) & in_range_pl
        price_hl = low_lag > low_prev_low
        hidden_bull_cond_alert = price_hl & osc_ll & pl_found

        # --- Regular bearish: osc lower high, price higher high ---
        osc_prev_high = ta.pine_valuewhen(ph_found, osc_lag, 1)
        high_prev_high = ta.pine_valuewhen(ph_found, high_lag, 1)
        osc_lh = (osc_lag < osc_prev_high) & in_range_ph
        price_hh = high_lag > high_prev_high
        bear_cond_alert = price_hh & osc_lh & ph_found

        # --- Hidden bearish: osc higher high, price lower high ---
        osc_hh = (osc_lag > osc_prev_high) & in_range_ph
        price_lh = high_lag < high_prev_high
        hidden_bear_cond_alert = price_lh & osc_hh & ph_found

        dataframe["pine_cvd"] = cvd
        dataframe["pine_cvd_ma"] = cvd_ma
        dataframe["pine_pl_found"] = pl_found
        dataframe["pine_ph_found"] = ph_found
        dataframe["pine_bull_cond_alert"] = bull_cond_alert
        dataframe["pine_hidden_bull_cond_alert"] = hidden_bull_cond_alert
        dataframe["pine_bear_cond_alert"] = bear_cond_alert
        dataframe["pine_hidden_bear_cond_alert"] = hidden_bear_cond_alert
        # le / se -- the alert conditions, not the plot-gated ones.
        dataframe["pine_le"] = bull_cond_alert | hidden_bull_cond_alert
        dataframe["pine_se"] = bear_cond_alert | hidden_bear_cond_alert
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "le": dataframe["pine_le"].to_numpy(dtype=bool),
            "se": dataframe["pine_se"].to_numpy(dtype=bool),
            # stopPer = input.float(5.0) / 100 ; takePer = input.float(10.0) / 100
            "stop_per": float(params["stopPer"]) / 100.0,
            "take_per": float(params["takePer"]) / 100.0,
        }

    def pine_script(self, broker, i, ctx):
        stop_per = ctx["stop_per"]
        take_per = ctx["take_per"]
        le = bool(ctx["le"][i])
        se = bool(ctx["se"][i])
        # ltp = se ; stp = le
        ltp = se
        stp = le

        # if (le) strategy.entry("Long", strategy.long)
        if le:
            broker.entry("Long", "long")
        # if (se) strategy.entry("Short", strategy.short)
        if se:
            broker.entry("Short", "short")
        # if (ltp) strategy.close("Long")
        if ltp:
            broker.close("Long")
        # if (stp) strategy.close("Short")
        if stp:
            broker.close("Short")

        # longStop / longTake / shortStop / shortTake are anchored to
        # strategy.position_avg_price, read at this point in the script.
        avg_price = broker.avg_price
        # if strategy.position_size > 0
        if broker.position > 0:
            broker.exit(
                "Close Long",
                "Long",
                stop=avg_price * (1 - stop_per),
                limit=avg_price * (1 + take_per),
            )
        # if strategy.position_size < 0
        if broker.position < 0:
            broker.exit(
                "Close Short",
                "Short",
                stop=avg_price * (1 + stop_per),
                limit=avg_price * (1 - take_per),
            )
