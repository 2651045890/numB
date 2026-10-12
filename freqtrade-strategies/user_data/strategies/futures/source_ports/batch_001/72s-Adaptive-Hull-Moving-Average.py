"""Port of sources/SM_3b423ab7a4b2ceb2.pine (batch_001/72s-Adaptive-Hull-Moving-Average.md).

Pine v4. An adaptive Hull moving average whose period walks between a minimum
and a maximum according to a "charger" (volatility or volume), plus a slope
reading of that average in degrees:

    highVolatility = atr(14) > atr(46)
    rsivol         = rsi(volume, 14)
    osc            = hma(rsivol, 10)          # built-in hma
    volBreak       = osc > 49
    plugged        = charger == "Volume" ? volBreak : highVolatility   # default: volatility

    var float dynamicLength = avg(minLength, maxLength)      # (172+233)/2
    var float minorLength   = avg(minorMin, minorMax)        # (89+121)/2
    dynamicLength := iff(plugged, max(minLength, dynamicLength*(1-adaptPct)),
                                  min(maxLength, dynamicLength*(1+adaptPct)))
    minorLength   := iff(plugged, max(minorMin,   minorLength*(1-adaptPct)),
                                  min(minorMax,   minorLength*(1+adaptPct)))
    adaptPct = 0.03141                                        # a literal, not an input

    xhma(src, length) => wma(2 * wma(src, length/2) - wma(src, length),
                             floor(sqrt(length)))
    dynamicHMA = xhma(close, int(dynamicLength))

    slope_period = 34, range = 25, pi = atan(1) * 4
    highestHigh = highest(slope_period), lowestLow = lowest(slope_period)
    slope_range = range / (highestHigh - lowestLow) * lowestLow
    calcslope(ma) => dt = (ma[2] - ma) / close * slope_range
                     xAngle = round(180 * acos(1 / sqrt(1 + dt*dt)) / pi)
                     iff(dt > 0, -xAngle, xAngle)
    _slope  = calcslope(dynamicHMA)
    _upSig  = _slope >= flat and plugged
    _dnSig  = _slope <= -flat and plugged
    buy     = _upSig and not _upSig[1]
    sell    = _dnSig and not _dnSig[1]

and the order block appended at the end of the file:

    if buy
        strategy.entry("Enter Long", strategy.long)
    else if sell
        strategy.entry("Enter Short", strategy.short)

The `fastExits` / `warningSigns` section of the source raises ALERTS only (the
fast minor HMA is never traded) and is not an order.

The file declares `study(...)`, not `strategy(...)` (PINE_SEMANTICS.md 1.17), so
no strategy() properties exist: Pine's documented defaults are recorded in the
source_* attributes -- fixed 1-unit sizing, 0% commission, pyramiding 0,
initial capital 1000000 USD. There is no exit call anywhere, so a position is
only left by the opposite entry reversing it.

FIDELITY:

* The two adaptive periods are a running `var` state seeded once at the average
  of their bounds and multiplied every bar, so they are computed with a
  bar-by-bar loop; each bar's HMA then uses THAT bar's integer length, which is
  why even the outer `wma` has a per-bar length and the whole indicator is
  evaluated per bar rather than as a rolling window.
* `int(dynamicLength)` truncates toward zero (the values are positive, so this
  is floor). `_length / 2` inside `xhma` is Pine's integer division, so a
  length of 203 uses 101 (see the note below on the alternative).
* `highest(slope_period)` / `lowest(slope_period)` are v3/v4's ONE-argument
  forms, whose source defaults to the bar's high / low -- the convention already
  used by the Ichimoku port in this corpus. So highestHigh is
  `pine_highest(high, 34)` and lowestLow is `pine_lowest(low, 34)`.
* `_upSig and not _upSig[1]`: `not` of an na is na and na in a boolean context
  is false, so a bar whose predecessor had no reading cannot fire. The NaN runs
  of `_slope` (and therefore of `_upSig`) are contiguous prefixes -- the HMA
  window bound, the 34-bar channel and the `[2]` history all open at bar 0 --
  so treating a missing predecessor as "not previously true" cannot manufacture
  a signal that Pine would have suppressed.
* `p2`-style truthiness does not arise here: `buy` and `sell` are booleans. The
  appended `? -1 : 0` shape of PINE_SEMANTICS.md 1.17 does not apply to this
  particular source -- its conditions are already boolean -- but the reading
  would be the same either way (non-zero is true).
* The `alert()` calls, `plot`, `plotchar`, `bgcolor`, `fill`, the distance-zone
  envelope (`upperTL` / `topTL` / `stopupperTL` and friends, which only feed
  plots and the `warningSigns` alert) and the commented-out static-HMA study are
  not orders and are not reproduced.
* Adaptive lengths, HMA and the slope formula are computed in this file rather
  than through pine_ta because pine_ta's window functions take a FIXED length;
  `_wma_at` reproduces pine_ta.pine_wma's weights and na rule exactly (weights
  1..length with the newest heaviest, na if any value in the window is na, na
  until the window is full).
* No exit call exists, so `source_reproduce_stops` is False.
"""
import math

import numpy as np
import pandas as pd
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase

# Literals in the source, not inputs: adaptPct's `input()` is commented out, and
# the slope constants are a one-line tuple assignment.
_ADAPT_PCT = 0.03141
_SLOPE_PERIOD = 34
_SLOPE_RANGE = 25
_PI = math.atan(1) * 4


def _wma_at(values, length, position):
    """Pine `wma(source, length)` at ONE bar, for a length that varies by bar.

    Same rule as pine_ta.pine_wma (weights 1..length, newest heaviest, na if any
    value in the window is na, na until the window is full) but addressable at a
    chosen bar with a chosen length, which a fixed-window rolling mean cannot do.
    """
    if length < 1 or position + 1 < length:
        return np.nan
    window = values[position + 1 - length : position + 1]
    if np.isnan(window).any():
        return np.nan
    weights = np.arange(1, length + 1, dtype=float)
    return float(np.dot(window, weights) / weights.sum())


def _xhma(values, lengths):
    """The source's `xhma` applied per bar with that bar's own length.

        xhma(src, length) => wma(2 * wma(src, length/2) - wma(src, length),
                                 floor(sqrt(length)))

    The outer wma is taken over the series `2*wma(...) - wma(...)`, whose every
    value was produced with ITS bar's length, so the difference series is built
    first and the outer wma is applied to it afterwards -- that is what the
    nested call means, not a single fixed window.
    """
    count = len(values)
    difference = np.full(count, np.nan)
    for i in range(count):
        length = int(lengths[i])
        if length < 2:
            continue
        # Pine's integer division: an int length halved truncates.
        half = length // 2
        difference[i] = 2.0 * _wma_at(values, half, i) - _wma_at(values, length, i)

    out = np.full(count, np.nan)
    for i in range(count):
        outer = int(math.floor(math.sqrt(int(lengths[i]))))
        out[i] = _wma_at(difference, outer, i)
    return out


def _hma(source, length):
    """The v4 built-in `hma(src, length)` used by `osc = hma(rsivol, 10)`.

    TradingView defines it as the same xhma-shaped call with
    `round(sqrt(length))`; with length 10, floor and round agree.
    """
    length = int(length)
    difference = 2.0 * ta.pine_wma(source, length // 2) - ta.pine_wma(source, length)
    return ta.pine_wma(difference, int(math.floor(math.sqrt(length))))


def _calcslope(ma, src, slope_range):
    """The source's `calcslope`: the MA's angle in degrees over two bars."""
    # dt = (ma[2] - ma) / src * slope_range
    dt = (ma.shift(2) - ma) / src * slope_range
    # c = sqrt(1 + dt*dt); xAngle = round(180 * acos(1/c) / pi)
    c = np.sqrt(1.0 + dt * dt)
    with np.errstate(invalid="ignore"):
        x_angle = ta.pine_round(180.0 * np.arccos(1.0 / c) / _PI)
    # maAngle = iff(dt > 0, -xAngle, xAngle); an na dt is not > 0 (Pine).
    return x_angle.where(dt > 0, -x_angle)


class SM72sAdaptiveHullMovingAverage_3b423a(PinePortBase, IStrategy):
    source_id = "SM_3b423ab7a4b2ceb2"
    source_file = "72s-Adaptive-Hull-Moving-Average.md"
    timeframe = "15m"
    can_short = True
    source_defaults = {
        "charger": "Volatility",  # input("Volatility", options=["Volatility","Volume"])
        "src": "close",           # input(close, title="Source:")
        "minLength": 172,         # input(172, title="Minimum period:")
        "maxLength": 233,         # input(233, title="Maximum period:")
        "flat": 17,               # input(17, title="Consolidation area is when slope below:")
        "showMinor": True,        # display-only
        "minorMin": 89,           # input(89, title="Minimum:")
        "minorMax": 121,          # input(121, title="Maximum:")
        "showZone": False,        # display-only
        "mult": 2.7,              # display-only (distance zone)
        "showSignals": True,      # display-only
        "useBg": True,            # display-only
    }
    # study(...) carries no strategy() properties, so Pine's documented defaults
    # apply: fixed 1 unit, 0% commission, pyramiding 0, initial capital 1000000.
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    source_reproduce_stops = False
    source_fidelity_notes = [
        "The source declares `study(...)`, not `strategy(...)`: the original "
        "behaviour is the indicator plus the order block appended at the end of "
        "the file (PINE_SEMANTICS.md 1.17). There is no exit call of any kind, "
        "so a position is only left by the opposite entry reversing it; "
        "source_reproduce_stops is False and a position open at the end of the "
        "window stays open.",
        "The source's `fastExits` / `warningSigns` section and both alert() "
        "chains raise alerts only and place no order; the fast minor HMA is "
        "never traded. The `Possible Exits` comment above them is not an exit "
        "call.",
        "The adaptive periods are running `var` state, so both the period loop "
        "and the HMA are computed bar by bar; each bar's HMA uses that bar's own "
        "integer length, including the outer wma, which is why the difference "
        "series is built first and the outer wma applied to it (that is what the "
        "nested call means).",
        "int(dynamicLength) truncates toward zero (the values are positive, so "
        "floor). `length / 2` inside xhma is modelled with Pine's INTEGER "
        "division, so a length of 203 uses 101 rather than 101.5 -- the source "
        "author's own note says he used plain int() instead of round() to match "
        "TradingView's built-in HMA. The alternative reading (round a fractional "
        "half-length) would shift the odd-length bars by one wma weight and is an "
        "unresolved equivalence risk.",
        "`highest(slope_period)` / `lowest(slope_period)` are the v3/v4 "
        "one-argument forms, whose source defaults to the bar's high / low; the "
        "port uses pine_highest(high, 34) / pine_lowest(low, 34), the same "
        "reading the Ichimoku port in this corpus records.",
        "`x / 0 -> na` in Pine, so slope_range is computed with a zero channel "
        "width replaced by na instead of numpy's infinity (unreachable on real "
        "bars; kept exact).",
        "`buy = _upSig and not _upSig[1]`: `not` of an na is na and na is false "
        "in a boolean context, so a bar whose predecessor has no reading cannot "
        "fire. The NaN run of _slope is a contiguous prefix (34-bar channel and "
        "HMA warmup), so treating a missing predecessor as 'not previously true' "
        "is exact here rather than a shortcut.",
        "pine_ta's window functions take a fixed length, so _wma_at reproduces "
        "pine_ta.pine_wma's rule (weights 1..length, newest heaviest, na if any "
        "value in the window is na, na until the window is full) for a "
        "per-bar length; _hma is the same construction for the built-in "
        "`hma(rsivol, 10)`.",
        "`charger` defaults to Volatility, so `plugged` is the volatility meter; "
        "the volume branch (`rsi(volume, 14)` through the built-in hma) is "
        "computed as well so both readings are on the record, but only the "
        "selected one drives the signals.",
        "plot / plotchar / bgcolor / fill, the ATR distance-zone envelope "
        "(upperTL, topTL, stopupperTL and friends) and the commented-out static "
        "HMA study are display-only and place no order.",
        "The /*backtest header declares period: 15m with basePeriod: 5m "
        "(intrabar data); the engine evaluates at bar close and fills at the "
        "next open, so intrabar path differences are not modelled. The header's "
        "start/end window is not applied -- the port runs on whatever range the "
        "caller supplies.",
    ]

    def pine_indicators(self, dataframe, params):
        close = dataframe["close"]
        high, low = dataframe["high"], dataframe["low"]

        # highVolatility = atr(14) > atr(46)
        high_volatility = (ta.pine_atr(dataframe, 14) > ta.pine_atr(dataframe, 46))
        # volBreak = hma(rsi(volume, 14), 10) > 49
        rsivol = ta.pine_rsi(dataframe["volume"], 14)
        vol_break = (_hma(rsivol, 10) > 49)
        # plugged = charger == "Volume" ? volBreak : highVolatility
        if params["charger"] == "Volume":
            plugged = vol_break.fillna(False)
        else:
            plugged = high_volatility.fillna(False)

        # ---- dynamics: the two running adaptive periods ----------------------
        min_length = float(params["minLength"])
        max_length = float(params["maxLength"])
        minor_min = float(params["minorMin"])
        minor_max = float(params["minorMax"])
        count = len(close)
        dynamic_length = np.empty(count)
        minor_length = np.empty(count)
        current_dynamic = (min_length + max_length) / 2.0   # avg(minLength, maxLength)
        current_minor = (minor_min + minor_max) / 2.0       # avg(minorMin, minorMax)
        plugged_values = plugged.to_numpy()
        for i in range(count):
            if plugged_values[i]:
                current_dynamic = max(min_length, current_dynamic * (1.0 - _ADAPT_PCT))
                current_minor = max(minor_min, current_minor * (1.0 - _ADAPT_PCT))
            else:
                current_dynamic = min(max_length, current_dynamic * (1.0 + _ADAPT_PCT))
                current_minor = min(minor_max, current_minor * (1.0 + _ADAPT_PCT))
            dynamic_length[i] = current_dynamic
            minor_length[i] = current_minor

        source_values = close.to_numpy(dtype=float)
        # dynamicHMA = xhma(close, int(dynamicLength))
        dyn_hma = pd.Series(_xhma(source_values, dynamic_length), index=dataframe.index)
        dataframe["pine_dynamic_hma"] = dyn_hma
        dataframe["pine_minor_hma"] = _xhma(source_values, minor_length)

        # ---- slope ----------------------------------------------------------
        highest_high = ta.pine_highest(high, _SLOPE_PERIOD)
        lowest_low = ta.pine_lowest(low, _SLOPE_PERIOD)
        # slope_range = range / (highestHigh - lowestLow) * lowestLow; Pine's
        # division by zero is na, not infinity.
        channel = (highest_high - lowest_low).replace(0.0, np.nan)
        slope_range = (_SLOPE_RANGE / channel) * lowest_low
        slope = _calcslope(dyn_hma, close, slope_range)
        dataframe["pine_slope"] = slope

        # ---- signals --------------------------------------------------------
        flat = float(params["flat"])
        # na comparisons are false in Pine, so a missing slope is not >= flat.
        up_signal = (slope >= flat) & plugged
        dn_signal = (slope <= -flat) & plugged
        previous_up = up_signal.shift(1).fillna(False).astype(bool)
        previous_dn = dn_signal.shift(1).fillna(False).astype(bool)
        # buy = _upSig and not _upSig[1]; sell = _dnSig and not _dnSig[1]
        dataframe["pine_buy"] = up_signal & ~previous_up
        dataframe["pine_sell"] = dn_signal & ~previous_dn
        return dataframe

    def pine_context(self, dataframe, params):
        del params
        return {
            "buy": dataframe["pine_buy"].to_numpy(),
            "sell": dataframe["pine_sell"].to_numpy(),
        }

    def pine_script(self, broker, i, ctx):
        # if buy
        #     strategy.entry("Enter Long", strategy.long)
        # else if sell
        #     strategy.entry("Enter Short", strategy.short)
        if ctx["buy"][i]:
            broker.entry("Enter Long", "long")
        elif ctx["sell"][i]:
            broker.entry("Enter Short", "short")
