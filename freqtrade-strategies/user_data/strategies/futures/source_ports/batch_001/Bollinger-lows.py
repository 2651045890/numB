"""Port of sources/SM_7b53b103c46d7bfc.pine (batch_001/Bollinger-lows.md).

Pine v4 (`//@version=4`), RafaelZioni's "Bollinger lows" (study(), overlay),
with a conversion tool's order block appended -- the pattern PINE_SEMANTICS.md
1.17 records:

    if low1
       strategy.entry("Alert on Bottom", strategy.long)
    else if high1
        strategy.entry("Alert on Top", strategy.short)

`strategy.entry` does not compile inside `study()`, so the trading behaviour of
this source is what the appended block does: enter on the cross, and NEVER exit.
No exit call of any kind exists in the file -- not even a commented-out one --
so a position is only ever ended by the opposite entry reversing it.

The source computes, in this order:

    len5 = input(30) ; src = input(close) ; multi = input(2)
    mean = ema(src, len5) ; stddev = multi * stdev(src, len5)
    b = mean + stddev ; s = mean - stddev
    long  := crossover(src, s) ; short := crossunder(src, b)
    last_open_long  := long  ? close : nz(last_open_long[1])
    last_open_short := short ? close : nz(last_open_short[1])
    highb = highest(last_open_short, 100)   # r = 100, a literal
    lowb  = lowest(last_open_long, 100)
    hilow = (high - low) * 100 ; openclose = (close - open) * 100
    vol = src / hilow                      # computed, never used
    spreadvol = openclose * src
    VPT = spreadvol + cum(spreadvol)       # computed, never used
    price_spread = stdev(high - low, 28)   # window_len = 28, a literal
    vp = spreadvol + cum(spreadvol)
    smooth = sma(vp, 14)                   # v_len = 14, a literal
    v_spread = stdev(vp - smooth, 28)
    shadow = (vp - smooth) / v_spread * price_spread
    out = shadow > 0 ? high + shadow : low + shadow
    yp = ema(out, input(20))
    up = yp - (1 * atr(input(20))) ; dn = yp + (1 * atr(input(20)))

and then a SuperTrend-style ratchet over `up` / `dn` whose state (`hb`, `hl`,
`lb`, `l1`, `c`, `trend`) is carried bar to bar, ending in

    v = trend == 1 ? hb : trend == -1 ? lb : na
    low1  = crossover(v, lowb)
    high1 = crossunder(v, highb)

The ratchet is walked bar by bar in `pine_indicators`, keeping the source's
statement order. The `hb = 0.00 , hb := nz(hb[1])` idiom (several statements on
one line) is the source's way of making a state variable out of a non-`var`
declaration: `hb` is initialised to 0 each bar and then immediately overwritten
with the previous bar's final value, so the port carries `hb` across bars with
na collapsing to 0.

`strategy(...)` is never called, so the Pine defaults apply: `fixed` /
1 contract, initial capital 1000000, commission 0%, `pyramiding 0`,
`process_orders_on_close=false`.

FIDELITY:

* `highest` / `lowest` with `r = 100` return na until 100 bars have elapsed,
  which `pine_ta.pine_highest` / `pine_lowest` reproduce.
* `last_open_long` / `last_open_short` are `var` and seed with na, so
  `nz(...[1])` makes them 0.0 on the first bar and they stay 0.0 until the
  first cross. `highest(0-series, 100)` is therefore 0.0, and `crossover(v, 0)`
  needs `v[1] <= 0`, which a real price never satisfies -- reproduced as is.
* `if barstate.isfirst` is `i == 0`; it runs BEFORE `if c == 1`, so `c` is 0 and
  the `c == 1` branch is skipped on the first bar, exactly as in the source.
* `x >= hb[1]`, `n < hb[1] - hb[1] * factor`, `trend[1] > 0` and the other
  `[1]` reads are the source's. The `hb[1]` / `hl[1]` / `lb[1]` / `l1[1]` /
  `trend[1]` / `c[1]` reads are the PREVIOUS BAR'S final values, kept in
  separate variables here because the carry-forward idiom replaces an na
  history with 0.0 and the two are not the same value.
* Early bars really are na-driven: on bar 0 the `barstate.isfirst` block stores
  `up[0]` / `dn[0]` which are still na (the ATR window is not full), so bar 1's
  `nz(hb[1])` is 0.0 and `x >= hb[1]` is a comparison against na, hence false.
  The source therefore sets `trend = -1` on bar 1. Reproduced, not tidied.
* Pine's `max(na, x)` / `min(na, x)` are na; numpy's maximum/minimum propagate
  NaN the same way.
* `ema(src, len5)` and `ema(out, len)` use `pine_ta.pine_ema`, whose seeding
  rule is the shared layer's documented choice (PINE_SEMANTICS.md 3.1: first
  non-na observation seeds, na does not advance the recursion). TradingView
  does not publish its own seeding rule.
* `atr(period)` is `pine_ta.pine_atr`, i.e. `rma(tr(handle_na=true), period)`.
  Pine's `ta.atr` is defined that way, so no first-bar boundary applies here --
  this source uses `ta.atr`, not a bare `ta.tr` (contrast PINE_SEMANTICS 3.7).
* `stdev` is the population standard deviation (ddof = 0), as Pine's `stdev`.
* `cum(spreadvol)` sums from the first bar, which is `pine_ta.pine_cum`.
* `vol` and `VPT` are computed by the source and never used; they cannot affect
  any signal and are not carried into the port. They are named here so the
  omission is visible.
* `shadow > 0` takes the `else` leg when `shadow` is na (Pine treats an na
  condition as false), yielding `low + na = na`; numpy does the same, so `out`
  is na through the warmup.
* There is no `? -1 : 0` construct in this source, and `low1` / `high1` are
  plain booleans; the if / else-if order (long first) is preserved.
* No exit call exists: `source_reproduce_stops` is False.
* Both `plot` / `plotshape` calls are display-only; the second `plotshape` is
  commented out in the source and is not restored. `showcross = true` gates
  only the marker, never the entry.
* No `security()` call, no `barstate.isrealtime` branch, no repainting.
* The `/*backtest` header declares `period: 4h` on Binance BTC_USDT, so
  `timeframe` is "4h"; `basePeriod: 15m` is the FMZ backtester's own fill
  granularity, not the strategy's period.
* Leverage, margin, liquidation, funding and the venue's contract-step
  rounding of order quantities are not modelled.
"""
import numpy as np
import pandas as pd
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


def _nz(value):
    """Pine `nz`: na collapses to 0."""
    return 0.0 if value is None or np.isnan(value) else value


class SMBollingerLows_7b53b1(PinePortBase, IStrategy):
    source_id = "SM_7b53b103c46d7bfc"
    source_file = "Bollinger-lows.md"
    timeframe = "4h"
    can_short = True
    source_defaults: dict = {
        "len5": 30,
        "src": "close",
        "multi": 2,
        "len": 20,
        "period": 20,
    }
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    source_reproduce_stops = False
    source_fidelity_notes = [
        "Converter-appended order block (PINE_SEMANTICS 1.17): the file "
        "declares study() and the trailing `if low1 / else if high1` block is "
        "what the tool added. The port reproduces that block's actual "
        "behaviour -- enter on the cross, never exit.",
        "NO exit call exists in the source, not even a commented-out one, so "
        "source_reproduce_stops is False and a position is only ever ended by "
        "the opposite entry reversing it.",
        "No `? -1 : 0` construct is present, so the 1.17 integer-truthiness "
        "trap does not apply; low1/high1 are plain booleans and the "
        "if / else-if order is preserved.",
        "The `hb = 0.00 , hb := nz(hb[1])` one-liners are the source's way of "
        "building state out of non-var declarations; the port carries hb/hl/"
        "lb/l1/c/trend across bars with na collapsing to 0.",
        "The `X[1]` reads inside the ratchet are the previous bar's FINAL "
        "values, which are not the same as the carried-forward value when the "
        "history was na; both are tracked separately.",
        "Early bars are na-driven: the barstate.isfirst block stores still-na "
        "up[0]/dn[0], so bar 1 compares against na and the source takes the "
        "trend = -1 leg. Reproduced verbatim, not tidied.",
        "Pine's max(na, x) / min(na, x) return na; numpy's maximum/minimum "
        "propagate NaN identically.",
        "ema seeding is the shared layer's documented choice "
        "(PINE_SEMANTICS 3.1); TradingView does not publish its own rule.",
        "ta.atr is pine_ta.pine_atr = rma(tr(handle_na=true), period), which "
        "is Pine's own ta.atr definition, so the 3.7 first-bar boundary does "
        "not apply to this source (it uses ta.atr, not a bare ta.tr).",
        "stdev is the population standard deviation (ddof=0), as Pine's "
        "stdev; cum sums from the first bar.",
        "The source's `vol` and `VPT` are computed and never used, so they "
        "cannot affect a signal; they are deliberately not carried.",
        "highest/lowest with r = 100 are na until 100 bars have elapsed, which "
        "pine_highest/pine_lowest reproduce.",
        "plot/plotshape are display-only; the second plotshape is commented "
        "out in the source and is not restored. showcross = true gates only "
        "the marker.",
        "/*backtest declares period: 4h on Binance BTC_USDT; basePeriod: 15m "
        "is the FMZ backtester's fill granularity, not the strategy's period.",
        "No security() call, no barstate.isrealtime branch, no repainting.",
        "md/source check: the md's embedded PineScript block is line-for-line "
        "identical to sources/SM_7b53b103c46d7bfc.pine, and its five argument "
        "rows (len5 / src / Multiplier / len / Period) match the five input() "
        "defaults. It renders v_input_2_close's default as the index 0 rather "
        "than the label `close`, and omits the minval/maxval on multi and "
        "period.",
        "Leverage, margin, liquidation, funding and the venue's contract-step "
        "rounding of order quantities are not modelled.",
    ]

    def pine_indicators(self, dataframe, params):
        len5 = int(params["len5"])
        multiplier = float(params["multi"])
        ema_len = int(params["len"])
        atr_period = int(params["period"])
        src = ta.pine_source(dataframe, str(params["src"]))

        # mean = ema(src, len5) ; stddev = multi * stdev(src, len5)
        mean = ta.pine_ema(src, len5)
        stddev = multiplier * ta.pine_stdev(src, len5)
        b = mean + stddev
        s = mean - stddev

        # long := crossover(src, s) ; short := crossunder(src, b)
        long_signal = ta.pine_crossover(src, s)
        short_signal = ta.pine_crossunder(src, b)

        close = dataframe["close"]
        size = len(dataframe)

        # var float last_open_long = na
        # last_open_long := long ? close : nz(last_open_long[1])
        last_open_long = np.full(size, np.nan)
        last_open_short = np.full(size, np.nan)
        previous_long = np.nan
        previous_short = np.nan
        for i in range(size):
            if long_signal.iat[i]:
                current_long = float(close.iat[i])
            else:
                current_long = _nz(previous_long)
            if short_signal.iat[i]:
                current_short = float(close.iat[i])
            else:
                current_short = _nz(previous_short)
            last_open_long[i] = current_long
            last_open_short[i] = current_short
            previous_long = current_long
            previous_short = current_short

        entry_value = pd.Series(last_open_long, index=dataframe.index)
        entry_value1 = pd.Series(last_open_short, index=dataframe.index)

        # r = 100
        highb = ta.pine_highest(entry_value1, 100)
        lowb = ta.pine_lowest(entry_value, 100)

        high = dataframe["high"]
        open_ = dataframe["open"]

        # vol = src / hilow and VPT are computed by the source and never used.
        openclose = (close - open_) * 100.0
        spreadvol = openclose * src

        # window_len = 28 ; v_len = 14
        price_spread = ta.pine_stdev(high - dataframe["low"], 28)
        vp = spreadvol + ta.pine_cum(spreadvol)
        smooth = ta.pine_sma(vp, 14)
        v_spread = ta.pine_stdev(vp - smooth, 28)
        with np.errstate(divide="ignore", invalid="ignore"):
            shadow = (vp - smooth) / v_spread * price_spread
        # out = shadow > 0 ? high + shadow : low + shadow
        out = pd.Series(
            np.where(
                (shadow > 0).to_numpy(),
                high.to_numpy(dtype=float) + shadow.to_numpy(dtype=float),
                dataframe["low"].to_numpy(dtype=float) + shadow.to_numpy(dtype=float),
            ),
            index=dataframe.index,
        )

        yp = ta.pine_ema(out, ema_len)
        # mult = 1 (a literal, not an input)
        up = yp - ta.pine_atr(dataframe, atr_period)
        dn = yp + ta.pine_atr(dataframe, atr_period)

        up_values = up.to_numpy(dtype=float)
        dn_values = dn.to_numpy(dtype=float)
        close_values = close.to_numpy(dtype=float)
        factor = 0.001

        # hb/hl/lb/l1/c/trend carried across bars; na histories collapse to 0.
        hb_previous = np.nan
        hl_previous = np.nan
        lb_previous = np.nan
        l1_previous = np.nan
        trend_previous = np.nan
        c_previous = np.nan

        trend_values = np.zeros(size, dtype=float)
        v_values = np.full(size, np.nan)

        for i in range(size):
            hb = _nz(hb_previous)
            hl = _nz(hl_previous)
            lb = _nz(lb_previous)
            l1 = _nz(l1_previous)
            trend = _nz(trend_previous)
            c = _nz(c_previous) + 1
            x = up_values[i]
            n = dn_values[i]
            c5 = close_values[i]

            # if barstate.isfirst
            if i == 0:
                c = 0
                lb = n
                hb = x
                l1 = c5
                hl = c5

            # if c == 1
            if c == 1:
                if x >= hb_previous:
                    hb = x
                    hl = c5
                    trend = 1
                else:
                    lb = n
                    l1 = c5
                    trend = -1

            # if c > 1
            if c > 1:
                if trend_previous > 0:
                    hl = np.maximum(hl_previous, c5)
                    if x >= hb_previous:
                        hb = x
                    else:
                        if n < hb_previous - hb_previous * factor:
                            lb = n
                            l1 = c5
                            trend = -1
                else:
                    l1 = np.minimum(l1_previous, c5)
                    if n <= lb_previous:
                        lb = n
                    else:
                        if x > lb_previous + lb_previous * factor:
                            hb = x
                            hl = c5
                            trend = 1

            trend_values[i] = trend
            # v = trend == 1 ? hb : trend == -1 ? lb : na
            if trend == 1:
                v_values[i] = hb
            elif trend == -1:
                v_values[i] = lb
            else:
                v_values[i] = np.nan

            hb_previous = hb
            hl_previous = hl
            lb_previous = lb
            l1_previous = l1
            trend_previous = trend
            c_previous = c

        line = pd.Series(v_values, index=dataframe.index)
        # low1 = crossover(v, lowb) ; high1 = crossunder(v, highb)
        long_condition = ta.pine_crossover(line, lowb)
        short_condition = ta.pine_crossunder(line, highb)

        dataframe["pine_v"] = line
        dataframe["pine_trend"] = trend_values
        dataframe["pine_highb"] = highb
        dataframe["pine_lowb"] = lowb
        dataframe["pine_long_condition"] = long_condition.to_numpy()
        dataframe["pine_short_condition"] = short_condition.to_numpy()
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "v": dataframe["pine_v"].to_numpy(),
            "long_condition": dataframe["pine_long_condition"].to_numpy(),
            "short_condition": dataframe["pine_short_condition"].to_numpy(),
        }

    def pine_script(self, broker, i, ctx):
        # if low1
        #    strategy.entry("Alert on Bottom", strategy.long)
        # else if high1
        #     strategy.entry("Alert on Top", strategy.short)
        if ctx["long_condition"][i]:
            broker.entry("Alert on Bottom", "long")
        elif ctx["short_condition"][i]:
            broker.entry("Alert on Top", "short")
