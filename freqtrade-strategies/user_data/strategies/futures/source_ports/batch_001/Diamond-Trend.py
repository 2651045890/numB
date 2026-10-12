"""Port of sources/SM_f6ab36d8ce0c110a.pine (batch_001/Diamond-Trend.md).

Pine v4. The file declares `study(title="PSAR x", overlay=true)`, NOT
`strategy(...)`: the two `strategy.entry` calls at the bottom are an order block
APPENDED to the indicator by the converter site that published it
(fmz.com/strategy/362178, named in the md's Detail link). Pine does not compile
`strategy.entry` inside `study()`, so the "original strategy" is the indicator
PLUS that appended block, and the trading behaviour it defines is entry-only:

    if buy
        strategy.entry("Enter Long", strategy.long)
    else if sell
        strategy.entry("Enter Short", strategy.short)

The indicator (meer2019's "PSAR x") measures the scatter of a Parabolic SAR
around its own linear-regression line and trades the crossing of close through
an SAR displaced by that scatter:

    psar   = sar(start, increment, maximum)
    lreg   = linreg(psar, len, 0)
    lreg_x = linreg(psar, len, 1)
    s      = lreg - lreg_x                       # the regression slope
    intr   = lreg - bar_index * s
    dS     = sum over i in [0, len-1] of (psar[i] - (s*(bar_index-i) + intr))^2
    de     = sqrt(dS / len)                      # RMS residual
    up     = -de*dev + psar
    down   =  de*dev + psar

    up_t   := close[1] >  up_t[1] ? max(up,  up_t[1]) : up
    down_t := close[1] <  down_t[1] ? min(down, down_t[1]) : down
    trend  := close > down_t[1] ? 1 : close < up_t[1] ? -1 : nz(trend[1], 1)
    r_line = trend == 1 ? up_t : down_t

    buy  = crossover(close, r_line)
    sell = crossunder(close, r_line)

`up_t` / `down_t` are one-sided ratchets: they only ever move in the direction
that follows the SAR, and reset to the raw displaced SAR whenever the previous
close stops justifying the ratchet. `trend` is a sticky regime flag whose
default when neither condition holds is `nz(trend[1], 1)`, i.e. the previous
value, or 1 on the first bar.

There is NO exit of any kind in the source -- no `strategy.close`, no
`strategy.exit`, no stop / limit / trail, and not even a commented-out exit
line. A position is only ever left by the opposite entry, which the engine
models as a reversal. `pyramiding` keeps Pine's default of 0, so a repeated
signal while already positioned that way is ignored.

FIDELITY:

* `sar(start, increment, maximum)` is Pine's built-in Parabolic SAR. `pine_ta`
  has no `sar`, so the port carries Wilder's recursion locally (`_pine_sar`),
  matching the two other ports in this batch that needed it. Pine does not
  publish `sar`'s seeding rule; the modelled initial state (trend = up,
  SAR = low[0], EP = high[0], AF = start) is a MODELLING CHOICE, and the
  warm-up bars are the only place it can diverge. The source's first read of
  `psar` is inside the 100-bar linreg window, so early bars are discarded by
  the na propagation below anyway.
* `bar_index` cancels algebraically out of the residual sum. With
  `intr = lreg - bar_index * s`, the fitted line at `i` bars back is
  `s*(bar_index-i) + intr = lreg - s*i`, which contains no `bar_index`. The
  port still writes the expression literally (via a `bar_index` column), but
  the value does NOT depend on where the series starts -- so the port's choice
  of bar origin cannot move a signal, and the causal-truncation check is not
  affected by it.
* The loop's `psar[i]` is an out-of-range history reference during the first
  `len-1` bars, which Pine yields na; `dS` then sums an na and becomes na, so
  `de`, `up` and `down` are na there. The port reproduces that ("reference
  before the start is NaN"), which is why nothing can fire before bar `len-1`.
  Together with `linreg`'s own full-window requirement the practical warm-up is
  `len` = 100 bars.
* Pine's `math.max` / `math.min` return na if EITHER argument is na. The port's
  ratchets use that guarded form rather than Python's `max`, whose result
  depends on argument order when a NaN is involved.
* `up_t = 0.0`, `down_t = 0.0`, `trend = 0` are the v3-style declaration lines
  that are immediately overwritten by the `:=` on the following line; only the
  `:=` value is read back through `[1]`. On the first bar every `[1]` reference
  is na, so the ratchets take their `else` branch and `nz(trend[1], 1)` yields
  the port's initial 1.
* `trend` can take the value -1, but it is never tested as a bare condition:
  the source compares it (`trend == 1`). The PINE_SEMANTICS.md 1.17 trap
  (`? -1 : 0` used as a naked condition) does not arise here, and the port
  keeps the integer values unchanged.
* The source's `off` is a plain literal (`off= 0`), not an input, so only
  `len` and `dev` are inputs; `off` and `off+1` stay literals in the port.
* `plot(r_line)` is display-only and is not reproduced.
* The source declares `study(...)`, so no `strategy()` properties exist and
  Pine's documented defaults apply: market orders of `fixed` size 1 contract,
  initial capital 1000000, commission 0%, pyramiding 0,
  process_orders_on_close=false.
* There is no exit call of any kind, so `source_reproduce_stops` is False and a
  position still open at the end of the window stays open.
* md-vs-source: the md's argument table (start 0.02, increment 0.02,
  maximum 0.2, len 100, Deviation 1.9) matches the source's input defaults
  exactly, and its embedded source block is verbatim identical to the .pine.
  The md's DISPLAY NAME ("Diamond-Trend") differs from the source's own study
  title ("PSAR x"), and its one-line prose description trades nothing; neither
  affects behaviour. No behavioural md-vs-source conflict.
* The header's backtest window (2022-04-09 to 2022-05-08) is extraction
  metadata, not an `input.time` filter, so no data is trimmed. Its
  `basePeriod: 5m` is the host's intrabar granularity for filling 15m bars.
* Leverage, margin, liquidation, funding and the venue's contract-step rounding
  are not modelled (PINE_SEMANTICS.md 1.6 measures the rounding separately).
"""
import numpy as np
import pandas as pd
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


def _pine_sar(high, low, start=0.02, increment=0.02, maximum=0.2):
    """Pine v4 `sar(start, inc, max)` -- Wilder's Parabolic SAR.

    `high`/`low` are arrays. Returns an array aligned to them.

    MODELLED CHOICE (parity risk, recorded in source_fidelity_notes): the
    recursion is the standard one -- SAR_t = SAR_(t-1) + AF * (EP - SAR_(t-1)),
    clamped so it may not penetrate the previous two bars' extremes; a bar whose
    extreme crosses the clamped SAR flips the trend, resets AF to `start` and
    re-seeds EP with that bar's extreme. Pine does not publish `sar`'s seeding
    rule, so the initial state (trend = up, SAR = low[0], EP = high[0],
    AF = start) is this port's model; the warm-up bars are the only place it can
    diverge.
    """
    high = np.asarray(high, dtype=float)
    low = np.asarray(low, dtype=float)
    count = len(high)
    out = np.full(count, np.nan)
    if count == 0:
        return out
    start, increment, maximum = float(start), float(increment), float(maximum)
    uptrend = True
    sar = low[0]
    extreme = high[0]
    accel = start
    out[0] = sar
    for i in range(1, count):
        bar_high, bar_low = high[i], low[i]
        sar = sar + accel * (extreme - sar)
        if uptrend:
            prior = low[i - 1] if i < 2 else min(low[i - 1], low[i - 2])
            sar = min(sar, prior)
            if bar_low < sar:
                uptrend = False
                sar = extreme
                extreme = bar_low
                accel = start
            elif bar_high > extreme:
                extreme = bar_high
                accel = min(accel + increment, maximum)
        else:
            prior = high[i - 1] if i < 2 else max(high[i - 1], high[i - 2])
            sar = max(sar, prior)
            if bar_high > sar:
                uptrend = True
                sar = extreme
                extreme = bar_high
                accel = start
            elif bar_low < extreme:
                extreme = bar_low
                accel = min(accel + increment, maximum)
        out[i] = sar
    return out


def _pine_na_max(a, b):
    """Pine `math.max(a, b)`: na if either argument is na, else the larger."""
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    return np.where(np.isnan(a) | np.isnan(b), np.nan, np.maximum(a, b))


def _pine_na_min(a, b):
    """Pine `math.min(a, b)`: na if either argument is na, else the smaller."""
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    return np.where(np.isnan(a) | np.isnan(b), np.nan, np.minimum(a, b))


def _shift_back(values: np.ndarray, offset: int) -> np.ndarray:
    """`series[offset]`: na (not data) for the bars before the series starts."""
    out = np.full(len(values), np.nan)
    if offset < len(values):
        if offset == 0:
            out[:] = values
        else:
            out[offset:] = values[: len(values) - offset]
    return out


class SMDiamondTrend_f6ab36(PinePortBase, IStrategy):
    source_id = "SM_f6ab36d8ce0c110a"
    source_file = "Diamond-Trend.md"
    timeframe = "15m"
    can_short = True
    # Input defaults exactly as written in the source. `off = 0` is a plain
    # literal in the source, not an input, so it is not listed here.
    source_defaults: dict = {
        "start": 0.02,
        "increment": 0.02,
        "maximum": 0.2,
        "len": 100,
        "dev": 1.9,
    }
    # The source declares study(...), not strategy(...), so Pine's documented
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
        "The file's study(title='PSAR x', ...) declaration means the "
        "strategy.entry pair at the bottom is an order block APPENDED by the "
        "converter site (fmz.com/strategy/362178 per the md's Detail link). The "
        "port reproduces the indicator PLUS that appended block, i.e. "
        "entry-only behaviour: if buy -> long, else if sell -> short.",
        "There is NO exit of any kind in the source: no strategy.close, no "
        "strategy.exit, no stop/limit/trail, and no commented-out exit line. A "
        "position is only left by the opposite entry, which the engine models "
        "as a reversal. source_reproduce_stops is False accordingly.",
        "BLOCKER/MODELLING CHOICE -- pine_ta has no `sar`, so the port carries "
        "Wilder's Parabolic SAR recursion locally (_pine_sar). Pine does not "
        "publish ta.sar's seeding rule, so the initial state (trend = up, "
        "SAR = low[0], EP = high[0], AF = start) is this port's model and is "
        "unverifiable without the source platform. The source only reads psar "
        "inside the 100-bar linreg window, so the practical effect is confined "
        "to the warm-up. Same model as the two other SAR ports in batch_001.",
        "bar_index cancels algebraically out of the residual sum: with "
        "intr = lreg - bar_index*s, the fitted line at i bars back is "
        "s*(bar_index-i) + intr = lreg - s*i, which is bar_index-free. The port "
        "still writes the expression literally, but the value does not depend "
        "on where the series starts, so the truncation-causality check is "
        "unaffected by the choice of bar origin.",
        "psar[i] is an OUT-OF-RANGE history reference during the first len-1 "
        "bars; Pine yields na there, so dS sums to na and de/up/down are na. "
        "The port reproduces that (reference before the start is NaN). "
        "Together with linreg's full-window requirement the warm-up is len = "
        "100 bars.",
        "Pine's math.max/math.min propagate na from EITHER argument; Python's "
        "max/min depend on argument order when a NaN is present. The up_t and "
        "down_t ratchets therefore use the guarded _pine_na_max/_pine_na_min "
        "helpers.",
        "`up_t = 0.0`, `down_t = 0.0`, `trend = 0` are v3-style declaration "
        "lines immediately overwritten by the following `:=`; only the := value "
        "is read back through [1]. On the first bar every [1] reference is na, "
        "so both ratchets take their else branch and nz(trend[1], 1) yields the "
        "port's initial 1.",
        "trend can be -1, but the source never tests it as a bare condition -- "
        "it compares (trend == 1). The PINE_SEMANTICS.md 1.17 trap (? -1 : 0 "
        "used as a naked condition) does not arise, and the port keeps the "
        "integer values unchanged.",
        "`off` is a plain literal (`off= 0`) in the source, not an input, so "
        "only len and dev are inputs; off and off+1 stay literals in the port.",
        "plot(r_line) is display-only and is not reproduced.",
        "The source declares study(...), so no strategy() properties exist and "
        "Pine's documented defaults apply: default_qty_type fixed, "
        "default_qty_value 1, commission 0%, pyramiding 0, initial capital "
        "1000000 USD, process_orders_on_close false.",
        "md-vs-source: the md's argument table (start 0.02, increment 0.02, "
        "maximum 0.2, len 100, Deviation 1.9) matches the source exactly and "
        "its embedded source block is verbatim identical. The md's display name "
        "('Diamond-Trend') differs from the source's own study title ('PSAR "
        "x'), and its prose description is one non-normative sentence. No "
        "behavioural conflict.",
        "The header's backtest window (2022-04-09 to 2022-05-08) is extraction "
        "metadata, not an input.time filter, so the port runs on whatever range "
        "the caller supplies; basePeriod: 5m is the host's intrabar fill "
        "granularity, not the strategy's period.",
        "Leverage, margin, liquidation, funding and the venue's contract-step "
        "rounding are not modelled (PINE_SEMANTICS.md 1.6).",
    ]

    def pine_indicators(self, dataframe, params):
        close = dataframe["close"]
        close_array = close.to_numpy(dtype=float)
        length = int(params["len"])
        dev_mult = float(params["dev"])
        off = 0  # `off= 0` in the source: a literal, not an input.

        # psar = sar(start, increment, maximum)
        psar = pd.Series(
            _pine_sar(
                dataframe["high"].to_numpy(dtype=float),
                dataframe["low"].to_numpy(dtype=float),
                float(params["start"]),
                float(params["increment"]),
                float(params["maximum"]),
            ),
            index=dataframe.index,
        )
        psar_array = psar.to_numpy(dtype=float)

        # lreg = linreg(cp, len, off), lreg_x = linreg(cp, len, off+1)
        lreg = ta.pine_linreg(psar, length, off)
        lreg_x = ta.pine_linreg(psar, length, off + 1)
        slope = lreg - lreg_x

        # b = bar_index; intr = lreg - b*s
        bar_index = np.arange(len(dataframe), dtype=float)
        intercept = (lreg - pd.Series(bar_index, index=dataframe.index) * slope).to_numpy(
            dtype=float
        )
        slope_array = slope.to_numpy(dtype=float)

        # dS = 0.0; for i = 0 to len-1: dS := dS + pow(cp[i] - (s*(b-i)+intr), 2)
        count = len(dataframe)
        d_s = np.zeros(count, dtype=float)
        for i in range(length):
            reference = _shift_back(psar_array, i)
            fitted = slope_array * (bar_index - i) + intercept
            d_s = d_s + (reference - fitted) ** 2
        de = np.sqrt(d_s / length)

        # up = (-de*dev) + psar; down = (de*dev) + psar
        up = -de * dev_mult + psar_array
        down = de * dev_mult + psar_array

        # up_t / down_t ratchets; every `[1]` reference is na before bar 0.
        up_t = np.full(count, np.nan)
        down_t = np.full(count, np.nan)
        for i in range(count):
            previous_close = close_array[i - 1] if i > 0 else np.nan
            previous_up_t = up_t[i - 1] if i > 0 else np.nan
            previous_down_t = down_t[i - 1] if i > 0 else np.nan
            # c[1] > up_t[1] ? max(up, up_t[1]) : up
            if previous_close > previous_up_t:
                up_t[i] = _pine_na_max(up[i], previous_up_t)
            else:
                up_t[i] = up[i]
            # c[1] < down_t[1] ? min(down, down_t[1]) : down
            if previous_close < previous_down_t:
                down_t[i] = _pine_na_min(down[i], previous_down_t)
            else:
                down_t[i] = down[i]

        # trend := c > down_t[1] ? 1 : c < up_t[1] ? -1 : nz(trend[1], 1)
        trend = np.full(count, np.nan)
        for i in range(count):
            previous_up_t = up_t[i - 1] if i > 0 else np.nan
            previous_down_t = down_t[i - 1] if i > 0 else np.nan
            previous_trend = trend[i - 1] if i > 0 else np.nan
            if close_array[i] > previous_down_t:
                trend[i] = 1.0
            elif close_array[i] < previous_up_t:
                trend[i] = -1.0
            else:
                trend[i] = 1.0 if np.isnan(previous_trend) else previous_trend

        # r_line = trend == 1 ? up_t : down_t
        r_line = pd.Series(
            np.where(trend == 1.0, up_t, down_t), index=dataframe.index
        )

        # buy = crossover(c, r_line); sell = crossunder(c, r_line)
        buy = ta.pine_crossover(close, r_line)
        sell = ta.pine_crossunder(close, r_line)

        dataframe["pine_psar"] = psar
        dataframe["pine_de"] = de
        dataframe["pine_up_t"] = up_t
        dataframe["pine_down_t"] = down_t
        dataframe["pine_trend"] = trend
        dataframe["pine_r_line"] = r_line
        dataframe["pine_buy"] = buy.fillna(False).astype(bool)
        dataframe["pine_sell"] = sell.fillna(False).astype(bool)
        return dataframe

    def pine_context(self, dataframe, params):
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
