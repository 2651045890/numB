"""Port of sources/SM_349a25b49423175d.pine (batch_001/FTL-Range-Filter-X2-EMA-UO.md).

jwelmac's "FTL - Range Filter X2 + EMA + UO" (`//@version=5`,
`indicator(title='FTL - Range Filter X2 + EMA + UO', overlay=true)`) is an
INDICATOR: two DonovanWall range filters, a 144 EMA and the Ultimate Oscillator,
with buy/sell labels and alerts. A converter appended an order block at the end
of the file -- `indicator()` cannot host `strategy.entry`, so the block is the
whole of the trading behaviour:

    longCond  = src > filt2 and src > src[1] and upward2 > 0
             or src > filt2 and src < src[1] and upward2 > 0
    shortCond = src < filt2 and src < src[1] and downward2 > 0
             or src < filt2 and src > src[1] and downward2 > 0
    CondIni   := longCond ? 1 : shortCond ? -1 : CondIni[1]

    longCondition  = longCond  and CondIni[1] == -1
    overBought     = uoLevel > 60
    if (longCondition and longWhenNotOverbought)
        longCondition := not overBought
    if (longCondition and longOnlyAboveEma)
        longCondition := closeAboveEma
    (shortCondition mirrored with 40 / closeBelowEma)

    if longCondition
        strategy.entry("Enter Long", strategy.long)
    else if shortCondition
        strategy.entry("Enter Short", strategy.short)

EXITS: the source contains NO live exit. The only exit-looking calls are inside
the author's own "For use like Strategy" comment block near the bottom, where
both lines are commented out and the author tells the reader to uncomment them:

    //strategy.entry( id = "Long", long = true, when = longCondition )
    //strategy.close( id = "Long", when = shortCondition )

A commented-out call does not execute, so there is no exit. A position is only
closed by an opposite entry reversing it.

FIDELITY:

* `src` / `src2` / `src4` are `input.source`; they are resolved through
  pine_ta.pine_source against the source defaults hl2 / ohlc4 / close, so a
  different source selection still works.
* `smoothrng` and `rngfilter` are Pine FUNCTIONS whose local variables carry
  history across bars (`rngfilt[1]`, `upward[1]`); both are replayed in one
  forward pass with `nz()` applied exactly as written rather than seeded with an
  SMA or a rolling extreme. `rngfilt = x` at the top of the body is the
  per-bar re-initialisation; `rngfilt[1]` is the PREVIOUS bar's final value,
  which is what makes the published filter a ratchet.
* `upward` / `downward` are the two direction counters; they are mirrored from
  `filt`, and `upward2` / `downward2` from `filt2`.
* `uo()` declares its three inputs inside the function body; the inputs are
  still read once at the top of the script by TradingView, so their defaults
  7/14/28 apply (inputs declared at global scope before the function is
  called).
* `math.max(high, close[1])` / `math.min(low, close[1])` propagate na, so `bp`
  and `tr_` are na on bar 0 and `math.sum` (pine_ta.pine_sum, which propagates
  na through its window, PINE_SEMANTICS.md section 3.2) keeps `uoLevel` na until
  bar 28. A COMPARISON against an na operand is false in Pine, so `overBought`
  is false during that warm-up and `not overBought` is TRUE, which lets
  `longCondition` survive the `if (longCondition and longWhenNotOverbought)`
  assignment on bars 2..27. That reading is a MODELLING CHOICE: Pine v5's bool
  is documented as three-state, so `not na` could instead be na (also falsy,
  but it would leave `longCondition` na and suppress those entries). Recorded,
  not hidden -- it only touches the bars before the Ultimate Oscillator forms.
* `ta.ema` is pine_ta.pine_ema; Pine does not publish its seeding rule
  (PINE_SEMANTICS.md section 3.1).
* `barcolor`, `filtcolor` / `filtcolor2`, every `plot` / `plotshape`, the
  `previousCross` / `pullback` / `isUptrendPullback` / `isDowntrendPullback`
  machinery, `didEmaCrossover` / `didEmaCrossunder` and all `alertcondition`
  calls are display or alert only and reach no order; they are not reproduced.
  `uptrendCrossoverOnly` / `downtrendCrossunderOnly` are carried as parameters
  because they are real inputs, but they only gate those display features.
* No `strategy()` call exists anywhere, so every trade property is Pine's own
  default: `default_qty_type` fixed, 1 contract, 1000000 initial capital, 0%
  commission, pyramiding 0, `process_orders_on_close` false.
* `/*backtest` declares `period: 2h` on Futures_Binance BTC_USDT, so timeframe
  is "2h"; `basePeriod: 15m` is the FMZ backtester's fill granularity.
* Leverage, margin, liquidation, funding and the venue's contract-step rounding
  are not modelled.
"""
import numpy as np
import pandas as pd
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


def _smoothrng(source, period, multiplier):
    """Pine `smoothrng(x, t, m)`.

        wper = t * 2 - 1
        avrng = ta.ema(math.abs(x - x[1]), t)
        _smoothrng = ta.ema(avrng, wper) * m
    """
    period = int(period)
    wper = period * 2 - 1
    avrng = ta.pine_ema((source - source.shift(1)).abs(), period)
    return ta.pine_ema(avrng, wper) * float(multiplier)


def _rngfilter(source, band):
    """Pine `rngfilter(x, r)` -- the recursive range filter.

        rngfilt = x
        rngfilt := x > nz(rngfilt[1]) ? x - r < nz(rngfilt[1]) ? nz(rngfilt[1]) : x - r
                                      : x + r > nz(rngfilt[1]) ? nz(rngfilt[1]) : x + r
        rngfilt

    The function-local variable keeps history across bars, so `rngfilt[1]` is
    the previous bar's final value (nz()'d, and 0 on the first bar, where the
    history is na). An na comparison is false in Pine, which is what the plain
    numpy comparisons below give.
    """
    x = np.asarray(source, dtype=float)
    r = np.asarray(band, dtype=float)
    out = np.full(len(x), np.nan)
    previous = 0.0  # nz(rngfilt[1]) where rngfilt[1] is na
    for i in range(len(x)):
        lowered = x[i] - r[i]
        raised = x[i] + r[i]
        if x[i] > previous:
            value = previous if lowered < previous else lowered
        else:
            value = previous if raised > previous else raised
        out[i] = value
        # nz(): the level carried into the next bar, 0 when this bar is na.
        previous = 0.0 if np.isnan(value) else value
    return pd.Series(out, index=source.index, dtype=float)


def _direction_counter(values, rising):
    """Pine's `upward` / `downward` counters.

        upward := filt > filt[1] ? nz(upward[1]) + 1 : filt < filt[1] ? 0 : nz(upward[1])
        downward := filt < filt[1] ? nz(downward[1]) + 1 : filt > filt[1] ? 0 : nz(downward[1])
    """
    out = np.zeros(len(values))
    previous = 0.0  # nz(upward[1]) / nz(downward[1]) on the first bar
    for i in range(len(values)):
        if i == 0:
            advanced = receded = False
        else:
            advanced = values[i] > values[i - 1]
            receded = values[i] < values[i - 1]
        if rising:
            value = previous + 1.0 if advanced else (0.0 if receded else previous)
        else:
            value = previous + 1.0 if receded else (0.0 if advanced else previous)
        out[i] = value
        previous = value
    return out


def _ultimate_oscillator(dataframe, length1, length2, length3):
    """Pine `uo()` -- the Ultimate Oscillator, as the source writes it.

        high_ = math.max(high, close[1])
        low_  = math.min(low, close[1])
        bp = close - low_
        tr_ = high_ - low_
        average(bp, tr_, length) => math.sum(bp, length) / math.sum(tr_, length)
        100 * (4*avg7 + 2*avg14 + avg28) / 7
    """
    close = dataframe["close"]
    close_previous = close.shift(1)
    high = dataframe["high"]
    low = dataframe["low"]
    # math.max / math.min propagate na, so bar 0 is na on both sides.
    high_ = pd.Series(
        np.maximum(high.to_numpy(dtype=float), close_previous.to_numpy(dtype=float)),
        index=dataframe.index,
    )
    low_ = pd.Series(
        np.minimum(low.to_numpy(dtype=float), close_previous.to_numpy(dtype=float)),
        index=dataframe.index,
    )
    buying_pressure = close - low_
    true_range = high_ - low_

    def average(length):
        return ta.pine_sum(buying_pressure, int(length)) / ta.pine_sum(
            true_range, int(length)
        )

    return 100.0 * (4.0 * average(length1) + 2.0 * average(length2) + average(length3)) / 7.0


class SMFtlRangeFilterX2EmaUo_349a25(PinePortBase, IStrategy):
    source_id = "SM_349a25b49423175d"
    source_file = "FTL-Range-Filter-X2-EMA-UO.md"
    timeframe = "2h"
    can_short = True
    source_defaults: dict = {
        # Range Filter (Leader)
        "src": "hl2",
        "per": 30,
        "mult": 2.6,
        # Range Filter (Trigger)
        "src2": "ohlc4",
        "per2": 48,
        "mult2": 3.4,
        # EMA
        "len4": 144,
        "src4": "close",
        # Display-only gates for the EMA arrows and the pullback markers.
        "uptrendCrossoverOnly": False,
        "downtrendCrossunderOnly": False,
        # Ultimate Oscillator
        "length1": 7,
        "length2": 14,
        "length3": 28,
        # Buy options
        "overBoughtLevel": 60.0,
        "longWhenNotOverbought": True,
        "longOnlyAboveEma": True,
        # Sell options
        "overSoldLevel": 40.0,
        "shortWhenNotOversold": True,
        "shortOnlyBelowEma": True,
    }
    # No strategy() call exists, so Pine's documented defaults apply.
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    # No live exit: only an opposite entry ever closes a position.
    source_reproduce_stops = False
    source_mintick = 0.1
    source_fidelity_notes = [
        "Converter-appended order block. The file is `indicator()` (Pine v5) "
        "and appends `if longCondition -> strategy.entry(\"Enter Long\", long)` "
        "/ `else if shortCondition -> strategy.entry(\"Enter Short\", short)`. "
        "That block is the whole of the trading behaviour.",
        "EXITS: the source has no live exit. The only strategy.close in the file "
        "is `//strategy.close( id = \"Long\", when = shortCondition )` inside the "
        "author's \"For use like Strategy\" comment block, commented out with "
        "instructions to uncomment it. A commented call does not run, so "
        "source_reproduce_stops is False and a position is only closed by an "
        "opposite entry reversing it.",
        "src / src2 / src4 are input.source and are resolved through "
        "pine_ta.pine_source with the source's own defaults hl2 / ohlc4 / close.",
        "smoothrng and rngfilter are Pine functions whose locals keep history "
        "across bars (rngfilt[1], upward[1], downward[1]); both are replayed in "
        "one forward pass with nz() applied as written, not seeded with an SMA "
        "or a rolling extreme.",
        "math.max(high, close[1]) / math.min(low, close[1]) propagate na, and "
        "math.sum propagates na through its window (PINE_SEMANTICS section 3.2), "
        "so uoLevel is na until bar 28. MODELLING CHOICE: an na comparison is "
        "taken to be a definite false, so `overBought` is false in that window "
        "and `not overBought` is true, letting entries through on bars 2..27. "
        "Pine v5's bool is three-state, so `not na` could instead be na (also "
        "falsy at the `if`, but it would leave longCondition na and suppress "
        "those entries). Only the pre-UO warm-up is affected.",
        "`if (longCondition and longOnlyAboveEma) longCondition := closeAboveEma` "
        "assigns rather than ANDs, but it only runs on bars where longCondition "
        "is already true, so the net effect is an AND; the port keeps the "
        "assignment form.",
        "ta.ema is pine_ta.pine_ema; Pine does not publish its seeding rule "
        "(PINE_SEMANTICS section 3.1).",
        "barcolor, filtcolor/filtcolor2, every plot/plotshape, the previousCross "
        "/ pullback / isUptrendPullback / isDowntrendPullback machinery, "
        "didEmaCrossover / didEmaCrossunder and every alertcondition are display "
        "or alert only and reach no order; they are not reproduced. "
        "uptrendCrossoverOnly / downtrendCrossunderOnly are carried as "
        "parameters but gate only those display features.",
        "The `bool(na)` initialisations of longCond / shortCond are overwritten "
        "on every bar (both are assigned unconditionally); they are not "
        "modelled as state.",
        "No strategy() call exists, so all trade properties are Pine's "
        "documented defaults (fixed/1, 1000000, 0%, pyramiding 0, "
        "process_orders_on_close false).",
        "Venue contract-step rounding, leverage, margin, liquidation and funding "
        "are not modelled.",
    ]

    def pine_indicators(self, dataframe, params):
        src = ta.pine_source(dataframe, str(params["src"]))
        src2 = ta.pine_source(dataframe, str(params["src2"]))
        src4 = ta.pine_source(dataframe, str(params["src4"]))
        close = dataframe["close"]

        # ---- Range Filter (Leader) ----------------------------------------
        smrng = _smoothrng(src, params["per"], params["mult"])
        filt = _rngfilter(src, smrng)
        upward = _direction_counter(filt.to_numpy(dtype=float), rising=True)
        downward = _direction_counter(filt.to_numpy(dtype=float), rising=False)

        # ---- Range Filter (Trigger) ---------------------------------------
        smrng2 = _smoothrng(src2, params["per2"], params["mult2"])
        filt2 = _rngfilter(src2, smrng2)
        upward2 = _direction_counter(filt2.to_numpy(dtype=float), rising=True)
        downward2 = _direction_counter(filt2.to_numpy(dtype=float), rising=False)

        # ---- EMA -----------------------------------------------------------
        ema = ta.pine_ema(src4, int(params["len4"]))
        close_above_ema = (close > ema).to_numpy(dtype=bool)
        close_below_ema = (close < ema).to_numpy(dtype=bool)

        # ---- Ultimate Oscillator -------------------------------------------
        uo_level = _ultimate_oscillator(
            dataframe, params["length1"], params["length2"], params["length3"]
        )

        # ---- Break-out conditions ------------------------------------------
        # longCond := src > filt2 and src > src[1] and upward2 > 0
        #          or src > filt2 and src < src[1] and upward2 > 0
        values = src.to_numpy(dtype=float)
        values_previous = np.concatenate([[np.nan], values[:-1]])
        above_filter = values > filt2.to_numpy(dtype=float)
        rising_src = values > values_previous
        falling_src = values < values_previous
        upward2_positive = upward2 > 0
        downward2_positive = downward2 > 0
        long_cond = (above_filter & rising_src & upward2_positive) | (
            above_filter & falling_src & upward2_positive
        )
        below_filter = values < filt2.to_numpy(dtype=float)
        short_cond = (below_filter & falling_src & downward2_positive) | (
            below_filter & rising_src & downward2_positive
        )

        # CondIni := longCond ? 1 : shortCond ? -1 : CondIni[1]
        count = len(dataframe)
        cond_ini = np.full(count, np.nan)
        previous = np.nan
        for i in range(count):
            if long_cond[i]:
                value = 1.0
            elif short_cond[i]:
                value = -1.0
            else:
                value = previous
            cond_ini[i] = value
            previous = value
        cond_ini_previous = np.concatenate([[np.nan], cond_ini[:-1]])

        long_condition = long_cond & (cond_ini_previous == -1)
        short_condition = short_cond & (cond_ini_previous == 1)

        # ---- UO and EMA gates ----------------------------------------------
        over_bought = (uo_level.to_numpy(dtype=float) > float(params["overBoughtLevel"]))
        over_sold = (uo_level.to_numpy(dtype=float) < float(params["overSoldLevel"]))
        if bool(params["longWhenNotOverbought"]):
            long_condition = long_condition & ~over_bought
        if bool(params["longOnlyAboveEma"]):
            long_condition = long_condition & close_above_ema
        if bool(params["shortWhenNotOversold"]):
            short_condition = short_condition & ~over_sold
        if bool(params["shortOnlyBelowEma"]):
            short_condition = short_condition & close_below_ema

        dataframe["pine_filt"] = filt
        dataframe["pine_filt2"] = filt2
        dataframe["pine_upward"] = upward
        dataframe["pine_downward"] = downward
        dataframe["pine_upward2"] = upward2
        dataframe["pine_downward2"] = downward2
        dataframe["pine_ema"] = ema
        dataframe["pine_uo"] = uo_level
        dataframe["pine_long_condition"] = long_condition
        dataframe["pine_short_condition"] = short_condition
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "long_condition": dataframe["pine_long_condition"].to_numpy(dtype=bool),
            "short_condition": dataframe["pine_short_condition"].to_numpy(dtype=bool),
        }

    def pine_script(self, broker, i, ctx):
        # if longCondition
        #     strategy.entry("Enter Long", strategy.long)
        # else if shortCondition
        #     strategy.entry("Enter Short", strategy.short)
        if ctx["long_condition"][i]:
            broker.entry("Enter Long", "long")
        elif ctx["short_condition"][i]:
            broker.entry("Enter Short", "short")
