"""Port of sources/SM_f86de0125ecdb87f.pine (batch_001/Fukuiz-Trend.md).

Pine v5. The file declares `indicator(title='Fukuiz Trend', ...)`, NOT
`strategy(...)`: the two `strategy.entry` calls at the bottom are an order block
APPENDED to the indicator by the converter site that published it
(fmz.com/strategy/363980, named in the md's Detail link). Pine v5 does not
compile `strategy.entry` inside `indicator()`, so the "original strategy" is the
indicator PLUS that appended block, and the trading behaviour it defines is
entry-only:

    if bullCond
        strategy.entry("Enter Long", strategy.long)
    else if bearCond
        strategy.entry("Enter Short", strategy.short)

The indicator is Fukuiz's two-period RSI with a divergence detector. The two
RSIs are written out by hand rather than with `ta.rsi`, and the ALERT series
(`osc`) is a third call to `ta.rsi` on the same input:

    up    = ta.rma(math.max(ta.change(src), 0), len)      # len  = 24
    down  = ta.rma(-math.min(ta.change(src), 0), len)
    rsi   = down == 0 ? 100 : up == 0 ? 0 : 100 - 100 / (1 + up / down)
    rsi2  = the same with len2 = 100
    osc   = ta.rsi(src, len)

`Bullish` / `Bearish` (the two RSI lines crossing, and the colouring of the
plots) are computed by the source but NEVER read by the appended block; the
orders are driven by the divergence conditions instead. The divergence:

    plFound = na(ta.pivotlow(osc, lbL, lbR))  ? false : true
    phFound = na(ta.pivothigh(osc, lbL, lbR)) ? false : true
    _inRange(cond) =>
        bars = ta.barssince(cond == true)
        rangeLower <= bars and bars <= rangeUpper

    oscHL   = osc[lbR] > ta.valuewhen(plFound, osc[lbR], 1) and _inRange(plFound[1])
    priceLL = low[lbR] < ta.valuewhen(plFound, low[lbR], 1)
    bullCond = plotBull and priceLL and oscHL and plFound

    oscLH   = osc[lbR] < ta.valuewhen(phFound, osc[lbR], 1) and _inRange(phFound[1])
    priceHH = high[lbR] > ta.valuewhen(phFound, high[lbR], 1)
    bearCond = plotBear and priceHH and oscLH and phFound

i.e. a confirmed pivot low whose RSI is higher than the previous pivot low's RSI
while the price low is lower (regular bullish divergence), and its mirror.

There is NO exit of any kind in the source -- no `strategy.close`, no
`strategy.exit`, no stop / limit / trail, and not even a commented-out exit
line. A position is only ever left by the opposite entry, which the engine
models as a reversal. `pyramiding` keeps Pine's default of 0, so a repeated
signal while already positioned that way is ignored.

FIDELITY:

* The md's PROSE and the source disagree about what trades. The md says
  "Crossover = Bullish trend / Crossunder = Bearish trend" -- the crossing of
  the two RSIs -- and its argument table labels the two divergence switches
  "rsi>rsi2 Divergence" / "rsi<rsi2 Divergence". The APPENDED block ignores
  the crossings entirely and trades `bullCond` / `bearCond`, the pivot
  DIVERGENCE conditions, whose inputs the source itself titles 'Bullish
  Divergence' / 'Bearish Divergence'. Per rule 2 the source is authoritative:
  the port reproduces the divergence entries, and `Bullish` / `Bearish` are
  computed but unused (exactly as in the source).
* `rsi` and `osc` are the same number computed twice in the source (`ta.rsi`
  is defined as `100 - 100/(1 + rma(gain,len)/rma(loss,len))`, and the manual
  expression adds only the two documented edge cases `down == 0 -> 100` and
  `up == 0 -> 0`, which the library form reproduces). The port computes it once
  and uses that series for both names; the identity is exact, not approximate.
* `math.max(ta.change(src), 0)` is na on the first bar (Pine's math.max
  propagates na / Python's np.maximum keeps NaN), and `ta.rma` skips na
  without advancing the recursion, so both RSI warm-ups start at bar 1. The
  port keeps the na rather than zero-filling it.
* `ta.pivotlow` / `ta.pivothigh` report the pivot value only `lbR` bars AFTER
  the pivot bar; `pine_ta.pine_pivotlow` / `pine_pivothigh` model exactly that
  (`out[i + right] = values[i]`). Nothing in the port reads a bar that had not
  closed -- the divergence compares the pivot bar's own values, reached through
  `[lbR]`.
* `ta.barssince(cond == true)` counts bars since the last true; it is na until
  the first true, and Pine's `rangeLower <= na` is false, so `_inRange` is
  false before the first pivot. The port feeds it the SHIFTED `plFound[1]` /
  `phFound[1]` series, whose first element is na -- `na == true` is false in
  Pine, which is what the port's `fillna(False)` reproduces.
* `ta.valuewhen(cond, source, occurrence)` is the occurrence-th most recent
  value of `source` on a true `cond` (`1` = the one before the latest); it is
  na until that many occurrences exist. `pine_ta.pine_valuewhen` models it.
* `offset=-lbR` on the two `plot()` and two `plotshape()` calls moves the
  DRAWN label `lbR` bars into the past; it is a display offset only and does
  not shift the order, which the port places on the signal bar.
* The colour series (`Fukuizcolor*`, `bullColor`, `bearColor`,
  `hiddenBullColor`, `hiddenBearColor`, `textColor`, `noneColor`), the two
  `plot()` calls, the three `hline()` calls, the two `fill()` calls and the two
  `plotshape()` calls are display-only and are not reproduced.
* There is no `? -1 : 0` anywhere in this source, so the PINE_SEMANTICS.md 1.17
  trap does not arise; `bullCond` / `bearCond` are ordinary Pine booleans.
* `src` is an input.source defaulting to `open` (not close), so the RSIs run on
  the open price; `pine_ta.pine_source` resolves the whole selectable list.
* The source declares `indicator(...)`, so no `strategy()` properties exist and
  Pine's documented defaults apply: market orders of `fixed` size 1 contract,
  initial capital 1000000, commission 0%, pyramiding 0,
  process_orders_on_close=false.
* There is no exit call of any kind, so `source_reproduce_stops` is False and a
  position still open at the end of the window stays open.
* md-vs-source on defaults: the md's argument table matches the source for
  every numeric default (24, 100, open, 5, 5, 60, 5, true, true); only the two
  labels differ ('RSI>RSI2 Divergence' vs 'Bullish Divergence').
* The header's backtest window (2022-04-17 to 2022-05-16) is extraction
  metadata, not an `input.time` filter, so no data is trimmed. Its
  `basePeriod: 1m` is the host's intrabar granularity for filling 10m bars.
* Leverage, margin, liquidation, funding and the venue's contract-step rounding
  are not modelled (PINE_SEMANTICS.md 1.6 measures the rounding separately).
"""
import numpy as np
import pandas as pd
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


def _pine_rsi_ternary(up, down):
    """The source's hand-written RSI: `down == 0 ? 100 : up == 0 ? 0 : ...`.

    na comparisons are false, so an na pair falls through to
    `100 - 100/(1 + na/na)`, which is na -- the same na the library form
    carries through the warm-up.
    """
    with np.errstate(divide="ignore", invalid="ignore"):
        ratio = 100.0 - 100.0 / (1.0 + up / down)
    inner = pd.Series(
        np.where((up == 0.0).to_numpy(), 0.0, ratio.to_numpy()), index=up.index
    )
    return pd.Series(
        np.where((down == 0.0).to_numpy(), 100.0, inner.to_numpy()), index=up.index
    )


class SMFukuizTrend_f86de0(PinePortBase, IStrategy):
    source_id = "SM_f86de0125ecdb87f"
    source_file = "Fukuiz-Trend.md"
    timeframe = "10m"
    can_short = True
    # Input defaults exactly as written in the source. `rangeUpper` /
    # `rangeLower` / `lbL` / `lbR` / `plotBull` / `plotBear` are the divergence
    # block's inputs.
    source_defaults: dict = {
        "len": 24,
        "len2": 100,
        "src": "open",
        "lbR": 5,
        "lbL": 5,
        "rangeUpper": 60,
        "rangeLower": 5,
        "plotBull": True,
        "plotBear": True,
    }
    # The source declares indicator(...), not strategy(...), so Pine's documented
    # defaults apply: fixed size 1, initial capital 1000000, commission 0%,
    # pyramiding 0, process_orders_on_close=false.
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    # No strategy.close / strategy.exit / stop / limit / trail anywhere, and no
    # commented-out exit line either.
    source_reproduce_stops = False
    source_fidelity_notes = [
        "The file's indicator(title='Fukuiz Trend', ...) declaration means the "
        "strategy.entry pair at the bottom is an order block APPENDED by the "
        "converter site (fmz.com/strategy/363980 per the md's Detail link). The "
        "port reproduces the indicator PLUS that appended block, i.e. "
        "entry-only behaviour: if bullCond -> long, else if bearCond -> short.",
        "md-vs-source CONFLICT (recorded, not silently resolved): the md's prose "
        "says 'Crossover = Bullish trend / Crossunder = Bearish trend' and its "
        "argument table labels the two divergence switches 'rsi>rsi2 "
        "Divergence' / 'rsi<rsi2 Divergence'. The APPENDED block ignores the RSI "
        "crossings and trades the pivot DIVERGENCE conditions, which the source "
        "itself titles 'Bullish Divergence' / 'Bearish Divergence'. Rule 2 makes "
        "the source authoritative, so the port reproduces the divergence "
        "entries; the `Bullish` / `Bearish` crossover flags are computed by the "
        "source and read by NOTHING, so the port computes no order from them.",
        "`rsi` and `osc` are the same number computed twice in the source: "
        "ta.rsi is 100 - 100/(1 + rma(gain)/rma(loss)) and the hand-written "
        "expression adds only the documented edge cases (down == 0 -> 100, "
        "up == 0 -> 0), which that form already produces. The port computes it "
        "once and uses the one series under both names; the identity is exact.",
        "math.max(ta.change(src), 0) is na on the first bar (Pine's math.max "
        "propagates na, np.maximum keeps NaN), and ta.rma skips na without "
        "advancing the recursion, so both RSI warm-ups start at bar 1. The port "
        "keeps the na instead of zero-filling it.",
        "ta.pivotlow / ta.pivothigh report the pivot value only lbR bars AFTER "
        "the pivot bar, and pine_ta.pine_pivotlow / pine_pivothigh model exactly "
        "that (out[i + right] = values[i]). Nothing here reads an unclosed bar: "
        "the divergence compares the pivot bar's OWN values, reached via [lbR].",
        "ta.barssince is na until the first true and Pine's 'rangeLower <= na' "
        "is false, so _inRange is false before the first pivot. The port feeds "
        "it the SHIFTED plFound[1] / phFound[1] series whose first element is "
        "na; Pine's 'na == true' is false, which is what fillna(False) "
        "reproduces.",
        "ta.valuewhen(cond, source, occurrence) is the occurrence-th most recent "
        "source value on a true cond (1 = the one before the latest) and is na "
        "until that many occurrences exist; pine_ta.pine_valuewhen models it.",
        "offset=-lbR on the two plot() and the two plotshape() calls moves the "
        "DRAWN label lbR bars into the past. It is a display offset only: the "
        "order is placed on the signal bar, which is what the port does.",
        "The colour series (Fukuizcolor*, bullColor, bearColor, "
        "hiddenBullColor, hiddenBearColor, textColor, noneColor), the two "
        "plot() calls, three hline() calls, two fill() calls and two "
        "plotshape() calls are display-only and are not reproduced.",
        "There is no `? -1 : 0` in this source, so the PINE_SEMANTICS.md 1.17 "
        "trap does not arise; bullCond / bearCond are ordinary Pine booleans.",
        "src is an input.source defaulting to OPEN (not close), so both RSIs run "
        "on the open price; pine_ta.pine_source resolves the whole selectable "
        "list, and the default is kept as written.",
        "There is NO exit of any kind in the source: no strategy.close, no "
        "strategy.exit, no stop/limit/trail, and no commented-out exit line. A "
        "position is only left by the opposite entry, which the engine models "
        "as a reversal. source_reproduce_stops is False accordingly.",
        "The source declares indicator(...), so no strategy() properties exist "
        "and Pine's documented defaults apply: default_qty_type fixed, "
        "default_qty_value 1, commission 0%, pyramiding 0, initial capital "
        "1000000 USD, process_orders_on_close false.",
        "md-vs-source on defaults: the md's argument table matches the source "
        "for every numeric default (24, 100, open, 5, 5, 60, 5, true, true); "
        "only the two switch LABELS differ (see the CONFLICT note above).",
        "The header's backtest window (2022-04-17 to 2022-05-16) is extraction "
        "metadata, not an input.time filter, so the port runs on whatever range "
        "the caller supplies; basePeriod: 1m is the host's intrabar fill "
        "granularity, not the strategy's period.",
        "Leverage, margin, liquidation, funding and the venue's contract-step "
        "rounding are not modelled (PINE_SEMANTICS.md 1.6).",
    ]

    def pine_indicators(self, dataframe, params):
        length = int(params["len"])
        length2 = int(params["len2"])
        lb_r = int(params["lbR"])
        lb_l = int(params["lbL"])
        range_upper = float(params["rangeUpper"])
        range_lower = float(params["rangeLower"])
        src = ta.pine_source(dataframe, str(params["src"]))

        # up / down, then the hand-written RSI (== ta.rsi for the same input).
        change = ta.pine_change(src)
        gain = ta.pine_max(change, 0.0)
        loss = -ta.pine_min(change, 0.0)
        up = ta.pine_rma(gain, length)
        down = ta.pine_rma(loss, length)
        rsi = _pine_rsi_ternary(up, down)
        up2 = ta.pine_rma(gain, length2)
        down2 = ta.pine_rma(loss, length2)
        rsi2 = _pine_rsi_ternary(up2, down2)

        # osc = ta.rsi(src, len) -- the same series, computed once (see FIDELITY).
        osc = rsi

        # Bullish / Bearish are computed by the source but read by nothing.
        bullish = rsi > rsi2
        bearish = rsi < rsi2

        # plFound / phFound
        pl_found = ta.pine_pivotlow(osc, lb_l, lb_r).notna()
        ph_found = ta.pine_pivothigh(osc, lb_l, lb_r).notna()

        def _in_range(condition):
            # bars = ta.barssince(cond == true); rangeLower <= bars <= rangeUpper
            bars = ta.pine_barssince(condition)
            return (bars >= range_lower) & (bars <= range_upper)

        # plFound[1] / phFound[1]: na on the first bar, treated as false.
        pl_found_previous = pl_found.shift(1).fillna(False).astype(bool)
        ph_found_previous = ph_found.shift(1).fillna(False).astype(bool)

        osc_lb = osc.shift(lb_r)
        low_lb = dataframe["low"].shift(lb_r)
        high_lb = dataframe["high"].shift(lb_r)

        osc_hl = (osc_lb > ta.pine_valuewhen(pl_found, osc_lb, 1)) & _in_range(
            pl_found_previous
        )
        price_ll = low_lb < ta.pine_valuewhen(pl_found, low_lb, 1)
        bull_cond = (
            (bool(params["plotBull"]) & price_ll.fillna(False))
            & osc_hl.fillna(False)
            & pl_found
        )

        osc_lh = (osc_lb < ta.pine_valuewhen(ph_found, osc_lb, 1)) & _in_range(
            ph_found_previous
        )
        price_hh = high_lb > ta.pine_valuewhen(ph_found, high_lb, 1)
        bear_cond = (
            (bool(params["plotBear"]) & price_hh.fillna(False))
            & osc_lh.fillna(False)
            & ph_found
        )

        dataframe["pine_rsi"] = rsi
        dataframe["pine_rsi_long"] = rsi2
        dataframe["pine_bullish"] = bullish.fillna(False).astype(bool)
        dataframe["pine_bearish"] = bearish.fillna(False).astype(bool)
        dataframe["pine_pl_found"] = pl_found
        dataframe["pine_ph_found"] = ph_found
        dataframe["pine_bull_cond"] = bull_cond.fillna(False).astype(bool)
        dataframe["pine_bear_cond"] = bear_cond.fillna(False).astype(bool)
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "bull_cond": dataframe["pine_bull_cond"].to_numpy(),
            "bear_cond": dataframe["pine_bear_cond"].to_numpy(),
        }

    def pine_script(self, broker, i, ctx):
        # if bullCond
        #     strategy.entry("Enter Long", strategy.long)
        # else if bearCond
        #     strategy.entry("Enter Short", strategy.short)
        if ctx["bull_cond"][i]:
            broker.entry("Enter Long", "long")
        elif ctx["bear_cond"][i]:
            broker.entry("Enter Short", "short")
