"""Port of sources/SM_38647194cec8b7e8.pine (batch_001/HIGH-LOW-SAR.md).

RafaelZioni's "HIGH LOW SAR" (`//@version=4`, `study("HIGH LOW SAR ", ...)`)
is an INDICATOR: Bollinger-style bands built from a 100-bar SMA of close and of
close[100] widened by 1.618x / 4.236x ATR, a Parabolic SAR of that band system,
and a volume-weighted "VHMA" trend filter. A converter appended an order block
at the end of the file -- `study()` cannot host `strategy.entry`, so the block
is the whole of the trading behaviour:

    low1  = crossover(s1[1], s2) and s1 < bott1
    high1 = crossunder(s1[1], b) and s1 > top2 and vhma < vhma[2]

    if low1
       strategy.entry("buy", strategy.long)
    else if high1
        strategy.entry("sell", strategy.short)

There is NO exit anywhere in the file -- not live and not commented out -- so a
position is closed only by an opposite entry reversing it.

FIDELITY:

* `p(src1, len)` DOES NOT USE EITHER OF ITS ARGUMENTS. Its loop bound and its
  weights come from the global `len5` (= 100), and the series it accumulates is
  the global `src5` (= `input(close)`), not the `src1` passed in:

      p(src1, len5) =>
          n = 0.0
          s = 0.0
          for i = 0 to len5 - 1
              w = (len5 - i) * len5
              n := n + w
              s := s + src5[i] * w
          s / n

  Every call therefore returns the same number, so

      hm   = 2.0 * p(src1, floor(len5/2)) - p(src1, len5) = 2P - P = P
      vhma = p(hm, floor(sqrt(len5)))                      = P

  with P the (100 - i) * 100 weighted mean of `src5` over 100 bars. This is a
  source defect, not a simplification: it is what makes `hm` and the Hull
  construction collapse, and it is reproduced rather than corrected. The port
  replays the loop literally (weights (100 - i) * 100, newest bar heaviest) so
  the collapse stays visible; P is arithmetically the same as
  `pine_wta.pine_wma(src5, 100)`.
* `sma1 = sma(close[100], len)` is a 100-bar mean of the close series SHIFTED by
  100, i.e. `pine_sma(close.shift(100), 100)`, not `sma(close, 100)[100]` --
  identical values, but the shift comes first so the warm-up is 100 bars
  shorter for `sma1` than a nested history reference would be.
* `sar(start, increment, maximum)` is Pine's built-in Parabolic SAR, which
  pine_ta does not implement; the port carries Wilder's recursion locally
  (`_pine_sar`). Pine does not publish `sar`'s seeding rule, so the initial
  state (uptrend, SAR = low[0], EP = high[0], AF = start) is a MODELLING CHOICE
  and the warm-up bars are where it can diverge; the source reads `sar` through
  a 50-bar EMA and a 50-bar stdev before it is used, by which point the
  recursion has converged.
* `atr(len)` uses pine_ta.pine_atr, whose `ta.tr` seed on bar 0 is `high - low`
  where Pine's ta.tr is na (PINE_SEMANTICS.md section 3.7) -- a possible
  one-bar-early seed that the series carries through warm-up. Recorded.
* `ema(...)` is pine_ta.pine_ema (PINE_SEMANTICS.md section 3.1: Pine does not
  publish its seeding rule); `stdev` is the population deviation (ddof=0), as
  Pine computes it.
* `trend = input(false)` feeds only a `barstate.islast` line-drawing block, and
  `plot` / `plotshape` / `fill` / `alertcondition` are display or alert only;
  none of them reaches an order and none is reproduced.
* No `strategy()` call exists anywhere, so every trade property is Pine's own
  default: `default_qty_type` fixed, 1 contract, 1000000 initial capital, 0%
  commission, pyramiding 0, `process_orders_on_close` false. In particular
  `default_qty_value` is 1 CONTRACT, not 100% of equity -- that is what the
  absent declaration means, and it is preserved rather than guessed.
* `/*backtest` declares `period: 4h` on Binance BTC_USDT, so timeframe is
  "4h"; `basePeriod: 15m` is the FMZ backtester's fill granularity.
* Leverage, margin, liquidation, funding and the venue's contract-step rounding
  are not modelled.
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


def _source_weighted_average(source, length):
    """The source's `p()` -- reproduced literally, arguments included.

        n = 0.0
        s = 0.0
        for i = 0 to len5 - 1        // len5 is the GLOBAL 100, not `length`
            w = (len5 - i) * len5
            n := n + w
            s := s + src5[i] * w     // src5 is the GLOBAL input, not the argument
        s / n

    `length` is accepted and ignored, exactly as the source ignores it, so the
    call sites keep the shape of the original. i = 0 is the current bar, so the
    newest bar carries the heaviest weight (len5 * len5) and the oldest the
    lightest (1 * len5). The result is arithmetically pine_ta.pine_wma(src5,
    len5), but the loop is kept so the ignored parameters stay visible.
    """
    del length  # the source's function never reads its own arguments
    window_length = 100
    values = source.to_numpy(dtype=float)
    weights = (window_length - np.arange(window_length)) * float(window_length)
    total = weights.sum()
    out = np.full(len(values), np.nan)
    for i in range(window_length - 1, len(values)):
        window = values[i - window_length + 1 : i + 1][::-1]
        if np.isnan(window).any():
            continue
        out[i] = float(np.dot(window, weights) / total)
    return pd.Series(out, index=source.index, dtype=float)


class SMHighLowSar_386471(PinePortBase, IStrategy):
    source_id = "SM_38647194cec8b7e8"
    source_file = "HIGH-LOW-SAR.md"
    timeframe = "4h"
    can_short = True
    source_defaults: dict = {
        "trend": False,          # barstate.islast line drawing only
        "src5": "close",         # input(close) feeding ma / the p() loop
        "start": 0.02,
        "increment": 0.02,
        "maximum": 0.2,
        "lookBack": 50,
        "multi": 2.2,
    }
    # No strategy() call exists, so Pine's documented defaults apply: fixed
    # sizing, ONE CONTRACT per entry, 1000000 initial capital, 0% commission,
    # pyramiding 0, process_orders_on_close false.
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    # No exit exists in the source at all.
    source_reproduce_stops = False
    source_mintick = 0.1
    source_fidelity_notes = [
        "Converter-appended order block: the file is `study()` (Pine v4) and "
        "appends `if low1 -> strategy.entry(\"buy\", long)` / `else if high1 -> "
        "strategy.entry(\"sell\", short)`. That block is the whole trading "
        "behaviour.",
        "The source's `p(src1, len)` function ignores BOTH of its arguments: its "
        "loop bound and weights come from the global len5 (100) and it sums the "
        "global src5 (input(close)) rather than the src1 passed in. Every call "
        "returns the same value, so hm = 2*p - p collapses to p and vhma is that "
        "same p. Reproduced, not corrected -- it is a source defect that changes "
        "the indicator's meaning.",
        "p's result is the (100 - i) * 100 weighted mean of close over 100 bars, "
        "which is arithmetically pine_ta.pine_wma(close, 100); the literal loop "
        "is kept so the ignored parameters stay visible.",
        "pine_ta has no `sar`, so the port carries its own Wilder recursion "
        "(_pine_sar). Pine does not publish `sar`'s seeding rule; the initial "
        "state (trend up, SAR = low[0], EP = high[0], AF = start) is a MODELLING "
        "CHOICE. The source only reads sar through a 50-bar EMA and a 50-bar "
        "stdev, by which point the recursion has converged.",
        "sma1 = sma(close[100], 100) is computed as pine_sma(close.shift(100), "
        "100) -- the shift comes first, so its warm-up differs from a nested "
        "history reference even though the values agree.",
        "atr(100) uses pine_ta.pine_atr, whose ta.tr seed on bar 0 is high - low "
        "while Pine's ta.tr is na there (PINE_SEMANTICS section 3.7); the seed "
        "can be one bar early and the series carries that through warm-up.",
        "ema(...) is pine_ta.pine_ema (PINE_SEMANTICS section 3.1); stdev is the "
        "population deviation (ddof=0).",
        "trend = input(false) feeds only a barstate.islast line block; plot / "
        "plotshape / fill / alertcondition are display or alert only and reach "
        "no order, so they are not reproduced.",
        "No exit exists in the source -- it is neither called nor commented out "
        "-- so a position is closed only by an opposite entry reversing it and a "
        "position open at the end of the window stays open.",
        "No strategy() call exists, so all trade properties are Pine's "
        "documented defaults, including default_qty_value = 1 CONTRACT (fixed), "
        "not percent-of-equity.",
        "Venue contract-step rounding, leverage, margin, liquidation and funding "
        "are not modelled.",
    ]

    def pine_indicators(self, dataframe, params):
        close = dataframe["close"]
        src5 = ta.pine_source(dataframe, str(params["src5"]))
        length = 100  # len = 100 (bands) and len5 = 100 (VHMA) in the source

        # ---- bands ---------------------------------------------------------
        p1 = close
        p2 = close.shift(100)
        sma = ta.pine_sma(p1, length)
        sma1 = ta.pine_sma(p2, length)
        avg = ta.pine_atr(dataframe, length)
        fibratio1 = 1.618
        fibratio3 = 4.236
        r1 = avg * fibratio1
        r3 = avg * fibratio3
        top3 = sma + r3
        bott1 = sma - r1
        top2 = sma1 + r3
        bott2 = sma1 - r1

        # ---- VHMA ----------------------------------------------------------
        # ma = ema(src5 * volume, 100) / ema(volume, 100) is computed by the
        # source but reaches only `hm = 2*p(...) - p(...)`, and p() ignores its
        # arguments entirely (it sums src5), so `ma` never reaches a decision.
        # It is left out for that reason, not as an optimisation.
        p_full = _source_weighted_average(src5, length)          # p(src1, len5)
        p_half = _source_weighted_average(src5, length // 2)     # p(src1, 50)
        hm = 2.0 * p_half - p_full                               # = p_full
        vhma = _source_weighted_average(src5, 10)                # p(hm, 10)

        # ---- Parabolic SAR system ------------------------------------------
        s1 = pd.Series(
            _pine_sar(
                dataframe["high"],
                dataframe["low"],
                float(params["start"]),
                float(params["increment"]),
                float(params["maximum"]),
            ),
            index=dataframe.index,
        )
        look_back = int(params["lookBack"])
        mean = ta.pine_ema(s1, look_back)
        deviation = float(params["multi"]) * ta.pine_stdev(s1, look_back)
        b = mean + deviation
        s2 = mean - deviation

        # ---- signals --------------------------------------------------------
        # low1  = crossover(s1[1], s2) and s1 < bott1
        # high1 = crossunder(s1[1], b) and s1 > top2 and vhma < vhma[2]
        s1_previous = s1.shift(1)
        low1 = ta.pine_crossover(s1_previous, s2) & (s1 < bott1)
        high1 = (
            ta.pine_crossunder(s1_previous, b)
            & (s1 > top2)
            & (vhma < vhma.shift(2))
        )

        dataframe["pine_sma"] = sma
        dataframe["pine_sma1"] = sma1
        dataframe["pine_top2"] = top2
        dataframe["pine_top3"] = top3
        dataframe["pine_bott1"] = bott1
        dataframe["pine_bott2"] = bott2
        dataframe["pine_hm"] = hm
        dataframe["pine_vhma"] = vhma
        dataframe["pine_sar"] = s1
        dataframe["pine_band_mean"] = mean
        dataframe["pine_band_upper"] = b
        dataframe["pine_band_lower"] = s2
        dataframe["pine_low1"] = low1
        dataframe["pine_high1"] = high1
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "low1": dataframe["pine_low1"].to_numpy(dtype=bool),
            "high1": dataframe["pine_high1"].to_numpy(dtype=bool),
        }

    def pine_script(self, broker, i, ctx):
        # if low1
        #    strategy.entry("buy", strategy.long)
        # else if  high1
        #     strategy.entry("sell", strategy.short)
        if ctx["low1"][i]:
            broker.entry("buy", "long")
        elif ctx["high1"][i]:
            broker.entry("sell", "short")
