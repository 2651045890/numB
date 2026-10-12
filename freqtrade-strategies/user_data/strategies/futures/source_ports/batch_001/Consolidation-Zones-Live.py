"""Port of sources/SM_7a923dea76fb2fef.pine
(batch_001/Consolidation-Zones-Live.md).

Pine v4 (`//@version=4`), LonesomeTheBlue's "Consolidation Zones - Live"
(study(), max_bars_back = 1100), with a conversion tool's order block appended
-- the pattern PINE_SEMANTICS.md 1.17 records:

    if breakoutup
        strategy.entry("Enter Long", strategy.long)
    else if breakoutdown
        strategy.entry("Enter Short", strategy.short)

`strategy.entry` does not compile inside `study()`, so the trading behaviour of
this source is what the appended block does: enter on a consolidation breakout,
and NEVER exit. No exit call of any kind exists in the file -- not even a
commented-out one -- so a position is only ever ended by the opposite entry
reversing it.

The indicator, verbatim from the source:

    prd      = input(10)   # Loopback Period
    conslen  = input(5)    # Min Consolidation Length
    hb_ = highestbars(prd) == 0 ? high : na
    lb_ = lowestbars(prd)  == 0 ? low  : na
    var int dir = 0
    dir := iff(hb_ and na(lb_), 1, iff(lb_ and na(hb_), -1, dir))
    zz := hb_ and lb_ ? (dir == 1 ? hb_ : lb_) : (hb_ ? hb_ : (lb_ ? lb_ : na))

    for x = 0 to 1000
        if na(close) or dir != dir[x]
            break
        if zz[x]
            if na(pp)
                pp := zz[x]
            else
                if dir[x] ==  1 and zz[x] > pp
                    pp := zz[x]
                if dir[x] == -1 and zz[x] < pp
                    pp := zz[x]

with `var int conscnt`, `var float condhigh/condlow` and

    if change(pp)
        if conscnt > conslen
            if pp > condhigh -> breakoutup   := true
            if pp < condlow  -> breakoutdown := true
        if conscnt > 0 and pp <= condhigh and pp >= condlow
            conscnt := conscnt + 1
        else
            conscnt := 0
    else
        conscnt := conscnt + 1

    if conscnt >= conslen
        if conscnt == conslen
            condhigh := H_ ; condlow := L_          # highest/lowest(conslen)
        else
            condhigh := max(condhigh, high) ; condlow := min(condlow, low)

`pp` is NOT a `var`, so it is rebuilt from scratch on every bar by scanning the
contiguous run of bars over which `dir` has not changed; `dir`, `conscnt`,
`condhigh` and `condlow` ARE `var` and persist. The port walks all of this bar
by bar in `pine_indicators` and keeps the source's statement order.

FIDELITY:

* `highestbars(prd) == 0` / `lowestbars(prd) == 0` are `== 0` tests, and both
  the v4 (negative offsets) and v5 (positive offsets) sign conventions agree at
  zero, so the test is convention-independent: it is true exactly when this
  bar's high (resp. low) is the extreme of the last `prd` bars. The port writes
  it as `high == highest(high, prd)`. It differs from `highestbars` only when
  the current bar TIES the window extreme and Pine's tie-breaking prefers an
  earlier bar; which occurrence `highestbars` returns on a tie is not stated in
  the reference and is not resolvable offline. Recorded, not guessed.
* `if zz[x]` is a numeric truth test on a float: na and 0 are false, everything
  else true. `zz` is only ever na or a price, so the port tests `not isnan`.
* `for x = 0 to 1000` with `dir[x]` / `zz[x]` beyond the series start: Pine
  returns na there, so `dir != dir[x]` is na -> false (no break) and `if zz[x]`
  is false (no effect). The port therefore scans only back to bar 0, which is
  the same thing.
* `change(pp)` is `pp - pp[1]`, and it is na (hence false) when either side is
  na -- so the first bar on which `pp` becomes non-na takes the `else` branch
  and increments `conscnt`.
* `max(condhigh, high)` / `min(condlow, low)` are Pine's math.max/min, which
  return na if any argument is na; numpy comparisons on NaN reproduce that.
  `condhigh` is always non-na by the time `conscnt > conslen` (the counter
  increments by one, so it passes through `== conslen` first).
* The na-guards on `pp` and the `condhigh` / `condlow` comparisons follow
  Pine's rule that an na condition is false.
* There is no `? -1 : 0` construct in this source; `breakoutup` / `breakoutdown`
  are plain non-var booleans, recomputed each bar, so the entry test at the end
  of the same bar's execution sees this bar's value. The if / else-if order
  (long first) is preserved in pine_script.
* The `fill(...)` / `plot(...)` zone painting and the commented-out
  `line.new` / `line.delete` calls are display-only and are not reproduced;
  `paintcons` and `zonecol` never enter the trading logic (they only colour the
  fill), yet they are carried in `source_defaults` for provenance.
* `alertcondition` is alert-only (PINE_SEMANTICS.md 2.7) and is not reproduced.
* No `security()` call, no `barstate.isrealtime` branch, no repainting.
* The `/*backtest` header declares `period: 45m` on Futures_Binance BTC_USDT,
  so `timeframe` is "45m"; `basePeriod: 5m` is the FMZ backtester's own fill
  granularity, not the strategy's period.
* Leverage, margin, liquidation, funding and the venue's contract-step
  rounding of order quantities are not modelled.
"""
import numpy as np
import pandas as pd
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase

# Pine v4's `for x = 0 to 1000`: the scan is bounded by the loop, not by the
# run of equal `dir` alone.
_MAX_LOOKBACK = 1000


class SMConsolidationZonesLive_7a923d(PinePortBase, IStrategy):
    source_id = "SM_7a923dea76fb2fef"
    source_file = "Consolidation-Zones-Live.md"
    timeframe = "45m"
    can_short = True
    source_defaults: dict = {
        "prd": 10,
        "conslen": 5,
        "paintcons": True,
        "zonecol": "color.new(color.blue, 70)",
    }
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    source_reproduce_stops = False
    source_fidelity_notes = [
        "Converter-appended order block (PINE_SEMANTICS 1.17): the file "
        "declares study() and the trailing `if breakoutup / else if "
        "breakoutdown` block is what the tool added. The port reproduces that "
        "block's actual behaviour -- enter on the breakout, never exit.",
        "NO exit call exists in the source, not even a commented-out one, so "
        "source_reproduce_stops is False and a position is only ever ended by "
        "the opposite entry reversing it.",
        "No `? -1 : 0` construct is present, so the 1.17 integer-truthiness "
        "trap does not apply; breakoutup/breakoutdown are plain non-var "
        "booleans recomputed each bar. The if / else-if order is preserved.",
        "highestbars(prd) == 0 / lowestbars(prd) == 0 are == 0 tests, so the "
        "v4 (negative) and v5 (positive) offset conventions agree; written as "
        "high == highest(high, prd). Differs from Pine only on an exact tie "
        "with the window extreme, where Pine's choice of occurrence is not "
        "documented. Recorded, not guessed.",
        "`if zz[x]` on a float: na and 0 are false, anything else true; zz is "
        "only na or a price, so the port tests `not isnan`.",
        "History references beyond the series start are na in Pine, so the "
        "`dir != dir[x]` break and the `if zz[x]` test simply do not fire "
        "there; the port scans back only to bar 0, which is equivalent.",
        "change(pp) is na (hence false) when either side is na, so the first "
        "bar on which pp becomes non-na takes the else branch and increments "
        "conscnt.",
        "pp is not a `var`, so it is rebuilt each bar by scanning the "
        "contiguous run of unchanged `dir`; dir/conscnt/condhigh/condlow are "
        "`var` and persist. The port keeps that split.",
        "pine_ta.pine_highest/pine_lowest return na until their window is "
        "full, matching Pine's `highest`/`lowest` for bars < conslen.",
        "paintcons / zonecol only colour the `fill(...)` and never enter the "
        "trading logic; they are carried in source_defaults for provenance. "
        "The fill/plot painting and the commented-out line.new/line.delete "
        "calls are display-only and are not reproduced.",
        "alertcondition is alert-only (PINE_SEMANTICS 2.7) and is not "
        "reproduced.",
        "/*backtest declares period: 45m on Futures_Binance BTC_USDT; "
        "basePeriod: 5m is the FMZ backtester's fill granularity, not the "
        "strategy's period.",
        "No security() call, no barstate.isrealtime branch, no repainting.",
        "md/source check: the md's embedded PineScript block is line-for-line "
        "identical to sources/SM_7a923dea76fb2fef.pine. Its argument table "
        "records the Zone Color default as plain `blue`, while the source's "
        "input default is color.new(color.blue, 70) (blue at 70% "
        "transparency); the table also omits minval/maxval on prd and conslen. "
        "The other three rows match.",
        "Leverage, margin, liquidation, funding and the venue's contract-step "
        "rounding of order quantities are not modelled.",
    ]

    def pine_indicators(self, dataframe, params):
        prd = int(params["prd"])
        conslen = int(params["conslen"])

        high = dataframe["high"].to_numpy(dtype=float)
        low = dataframe["low"].to_numpy(dtype=float)
        close = dataframe["close"].to_numpy(dtype=float)
        size = len(dataframe)

        # float hb_ = highestbars(prd) == 0 ? high : na
        # float lb_ = lowestbars(prd) == 0 ? low  : na
        highest_high = ta.pine_highest(dataframe["high"], prd).to_numpy(dtype=float)
        lowest_low = ta.pine_lowest(dataframe["low"], prd).to_numpy(dtype=float)
        hb_flag = np.isfinite(highest_high) & (high == highest_high)
        lb_flag = np.isfinite(lowest_low) & (low == lowest_low)
        hb_ = np.where(hb_flag, high, np.nan)
        lb_ = np.where(lb_flag, low, np.nan)

        # float H_ = highest(conslen) ; float L_ = lowest(conslen)  -- the
        # CONSLEN window, not the loopback window.
        window_high = ta.pine_highest(dataframe["high"], conslen).to_numpy(dtype=float)
        window_low = ta.pine_lowest(dataframe["low"], conslen).to_numpy(dtype=float)

        # var int dir = 0
        # dir := iff(hb_ and na(lb_), 1, iff(lb_ and na(hb_), -1, dir))
        # zz := hb_ and lb_ ? (dir == 1 ? hb_ : lb_) : (hb_ ? hb_ : (lb_ ? lb_ : na))
        dir_values = np.zeros(size, dtype=np.int64)
        zz = np.full(size, np.nan)
        current_dir = 0
        for i in range(size):
            if hb_flag[i] and not lb_flag[i]:
                current_dir = 1
            elif lb_flag[i] and not hb_flag[i]:
                current_dir = -1
            # else: dir keeps its previous bar's value (the `iff(..., dir)` leg)
            dir_values[i] = current_dir
            if hb_flag[i] and lb_flag[i]:
                zz[i] = hb_[i] if current_dir == 1 else lb_[i]
            elif hb_flag[i]:
                zz[i] = hb_[i]
            elif lb_flag[i]:
                zz[i] = lb_[i]
            else:
                zz[i] = np.nan

        # pp is not `var`: rebuilt from scratch on every bar by scanning back
        # over the contiguous run of bars whose `dir` equals this bar's.
        pp = np.full(size, np.nan)
        for i in range(size):
            value = np.nan
            reference_dir = dir_values[i]
            for x in range(0, min(i, _MAX_LOOKBACK) + 1):
                j = i - x
                if np.isnan(close[i]) or dir_values[j] != reference_dir:
                    break
                if not np.isnan(zz[j]) and zz[j] != 0.0:
                    if np.isnan(value):
                        value = zz[j]
                    else:
                        if dir_values[j] == 1 and zz[j] > value:
                            value = zz[j]
                        if dir_values[j] == -1 and zz[j] < value:
                            value = zz[j]
            pp[i] = value

        # var int conscnt = 0 ; var float condhigh = na ; var float condlow = na
        conscnt = 0
        condhigh = np.nan
        condlow = np.nan
        previous_pp = np.nan
        breakout_up = np.zeros(size, dtype=bool)
        breakout_down = np.zeros(size, dtype=bool)
        condhigh_values = np.full(size, np.nan)
        condlow_values = np.full(size, np.nan)
        conscnt_values = np.zeros(size, dtype=np.int64)

        for i in range(size):
            # change(pp) is na -> false when either side is na.
            changed = (
                not np.isnan(pp[i]) and not np.isnan(previous_pp) and pp[i] != previous_pp
            )
            if changed:
                if conscnt > conslen:
                    if not np.isnan(condhigh) and pp[i] > condhigh:
                        breakout_up[i] = True
                    if not np.isnan(condlow) and pp[i] < condlow:
                        breakout_down[i] = True
                if (
                    conscnt > 0
                    and not np.isnan(condhigh)
                    and not np.isnan(condlow)
                    and pp[i] <= condhigh
                    and pp[i] >= condlow
                ):
                    conscnt += 1
                else:
                    conscnt = 0
            else:
                conscnt += 1

            if conscnt >= conslen:
                if conscnt == conslen:
                    condhigh = window_high[i]
                    condlow = window_low[i]
                else:
                    condhigh = np.maximum(condhigh, high[i])
                    condlow = np.minimum(condlow, low[i])

            previous_pp = pp[i]
            condhigh_values[i] = condhigh
            condlow_values[i] = condlow
            conscnt_values[i] = conscnt

        dataframe["pine_dir"] = dir_values
        dataframe["pine_zz"] = zz
        dataframe["pine_pp"] = pp
        dataframe["pine_conscnt"] = conscnt_values
        dataframe["pine_condhigh"] = condhigh_values
        dataframe["pine_condlow"] = condlow_values
        dataframe["pine_long_condition"] = breakout_up
        dataframe["pine_short_condition"] = breakout_down
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "long_condition": dataframe["pine_long_condition"].to_numpy(),
            "short_condition": dataframe["pine_short_condition"].to_numpy(),
        }

    def pine_script(self, broker, i, ctx):
        # if breakoutup
        #     strategy.entry("Enter Long", strategy.long)
        # else if breakoutdown
        #     strategy.entry("Enter Short", strategy.short)
        if ctx["long_condition"][i]:
            broker.entry("Enter Long", "long")
        elif ctx["short_condition"][i]:
            broker.entry("Enter Short", "short")
