"""Port of sources/SM_e2bf0f2daa3d8372.pine (batch_001/Gann-High-Low.md).

Pine v5 (`//@version=5`). Zer3192's "Gann High Low": two SMAs bracket the close,
a direction register flips between them, and the close crossing the resulting
line is the signal. A conversion tool's order block is appended at the end --
the pattern PINE_SEMANTICS.md 1.17 records:

    iff_1 = close < nz(ta.sma(low, LPeriod))[1] ? -1 : 0
    HLd   = close > nz(ta.sma(high, HPeriod))[1] ? 1 : iff_1
    HLv   = ta.valuewhen(HLd != 0, HLd, 0)
    sma_1 = ta.sma(high, HPeriod)
    sma_2 = ta.sma(low, LPeriod)
    HiLo  = HLv == -1 ? sma_1 : sma_2

    buySignal  = ta.crossover(close, HiLo)
    sellSignal = ta.crossunder(close, HiLo)
    if buySignal
        strategy.entry("buy", strategy.long)
    else if sellSignal
        strategy.entry("sell", strategy.short)

`strategy.entry` does not compile inside `indicator()`, so the trading
behaviour of this source is what the appended block does: enter on the cross,
and NEVER exit. No exit call of any kind exists in the file -- there is not
even a commented-out `strategy.exit` line -- so a position is only ever ended
by the opposite entry reversing it.

`HLd` is the source's own `? -1 : 0` register (the shape 1.17 warns about), but
it is NOT used as a bare condition anywhere: it appears in `HLd != 0` (an int
comparison, which means the same thing in Pine and Python) and `HLv` appears in
`HLv == -1`. The port therefore keeps the register as an integer series with -1
and 1 preserved, and never coerces it to bool.

`HiLo` looks like the two arms are swapped -- `HLv == -1` (the bearish register,
set by the test against the SMA of LOWS) selects `sma_1`, the SMA of HIGHS --
but that is what the source says, and it is in fact the classic Gann HiLo
Activator: in a downtrend the line trails above price at the high average, and
in an uptrend it trails below at the low average. It is reproduced verbatim.

There is no `strategy(...)` call, so the Pine defaults apply: `fixed` /
1 contract, initial capital 1000000, commission 0%, `pyramiding 0`,
`process_orders_on_close=false`.

FIDELITY:

* Converter-appended order block (PINE_SEMANTICS 1.17): the file declares
  `indicator()` and the trailing if / else-if entry pair is what the tool
  added. The port reproduces that block's actual behaviour -- enter on the
  cross, never exit.
* NO exit call exists in the source, not even a commented-out one, so
  `source_reproduce_stops` is False and a position is only ever ended by the
  opposite entry reversing it.
* `? -1 : 0` is present but is never used as a bare condition (see above), so
  the 1.17 trap does not bite; the integer register stays an integer and the
  if / else-if order (buy first) is preserved in `pine_script`.
* `nz(x)[1]` is the history of the nz'd series, not `nz(x[1])`, so bar 0 is
  still na rather than 0. The port writes `ta.nz(series).shift(1)` to keep that
  order; the difference is unobservable here because the only use is
  `close < prev`, and a close is never negative.
* An na `HLv` (before the first non-zero `HLd`) makes `HLv == -1` false, so
  `HiLo` falls to `sma_2` (the low average) during the warmup; Pine treats an
  na comparison as false and numpy's `nan == -1` is false too.
* `ta.crossover` is Pine's `a > b and a[1] <= b[1]` (pine_ta.pine_crossover),
  and na on either side reads as false, so no cross can fire while `HiLo` is
  still na -- i.e. until `sma_low` (21 bars) is available.
* `pine_sma` returns na until the window is full and na inside the window
  propagates (PINE_SEMANTICS 3.2); that is what delays the first non-zero
  `HLd`.
* `alertcondition` calls, `plot(HiLo, ...)` and the `HLcolor` ternary are
  display/alert-only and are not reproduced.
* `/*backtest` declares `period: 4h` on Futures_Binance BTC_USDT, so
  `timeframe` is "4h"; `basePeriod: 15m` is the FMZ backtester's own fill
  granularity, not the strategy's period.
* No `security()` call, no `barstate.isrealtime` branch, no repainting, no
  `strategy.risk.*` rule.
* Leverage, margin, liquidation, funding and the venue's contract-step
  rounding of order quantities are not modelled.
"""
import numpy as np
import pandas as pd
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


class SMGannHighLow_e2bf0f(PinePortBase, IStrategy):
    source_id = "SM_e2bf0f2daa3d8372"
    source_file = "Gann-High-Low.md"
    timeframe = "4h"
    can_short = True
    source_defaults: dict = {"HPeriod": 13, "LPeriod": 21}
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    source_reproduce_stops = False
    source_fidelity_notes = [
        "Converter-appended order block (PINE_SEMANTICS 1.17): the file declares "
        "indicator() and the trailing if / else-if entry pair is what the tool "
        "added. The port reproduces that block's actual behaviour -- enter on "
        "the crossover / crossunder of close and HiLo, never exit.",
        "NO exit call exists in the source, not even a commented-out one, so "
        "source_reproduce_stops is False and a position is only ever ended by "
        "the opposite entry reversing it.",
        "? -1 : 0 IS present (iff_1 / HLd) but is never used as a bare "
        "condition: HLd appears in `HLd != 0` and HLv in `HLv == -1`, both int "
        "comparisons that mean the same in Pine and Python. The register is "
        "kept as an integer series with -1 preserved; it is never coerced to "
        "bool and never rewritten as `== 1`.",
        "HiLo's arms look swapped (the bearish register selects the SMA of "
        "highs) but that is the classic Gann HiLo Activator layout and is "
        "reproduced verbatim.",
        "nz(x)[1] is written as ta.nz(series).shift(1), keeping Pine's order "
        "of operations; unobservable here because the only use is `close < "
        "prev`.",
        "An na HLv (before the first non-zero HLd) makes `HLv == -1` false, so "
        "HiLo falls to the low SMA during warmup; NaN comparisons are false in "
        "numpy as they are in Pine.",
        "ta.crossover is Pine's `a > b and a[1] <= b[1]`; na on either side "
        "reads as false, so no cross fires while HiLo is na (until the 21-bar "
        "low SMA exists).",
        "pine_sma returns na until its window is full (PINE_SEMANTICS 3.2), "
        "which is what delays the first non-zero HLd.",
        "alertcondition / plot / HLcolor are display and alert only and are "
        "not reproduced.",
        "/*backtest declares period: 4h on Futures_Binance BTC_USDT; "
        "basePeriod: 15m is the FMZ backtester's fill granularity, not the "
        "strategy's period.",
        "No security() call, no barstate.isrealtime branch, no repainting, no "
        "strategy.risk.* rule.",
        "Leverage, margin, liquidation, funding and the venue's contract-step "
        "rounding of order quantities are not modelled.",
    ]

    def pine_indicators(self, dataframe, params):
        h_period = int(params["HPeriod"])
        l_period = int(params["LPeriod"])
        high = dataframe["high"]
        low = dataframe["low"]
        close = dataframe["close"]

        sma_1 = ta.pine_sma(high, h_period)
        sma_2 = ta.pine_sma(low, l_period)

        # iff_1 = close < nz(ta.sma(low, LPeriod))[1] ? -1 : 0
        prev_low_ma = ta.nz(sma_2).shift(1)
        iff_1 = np.where((close < prev_low_ma).to_numpy(dtype=bool), -1, 0)
        # HLd = close > nz(ta.sma(high, HPeriod))[1] ? 1 : iff_1
        prev_high_ma = ta.nz(sma_1).shift(1)
        hld = np.where((close > prev_high_ma).to_numpy(dtype=bool), 1, iff_1)

        hld_series = pd.Series(hld.astype(float), index=dataframe.index)
        # HLv = ta.valuewhen(HLd != 0, HLd, 0) -- the register carries forward.
        hlv = ta.pine_valuewhen(hld_series != 0, hld_series, 0)

        # HiLo = HLv == -1 ? sma_1 : sma_2
        hilo = pd.Series(
            np.where(hlv.to_numpy() == -1, sma_1.to_numpy(), sma_2.to_numpy()),
            index=dataframe.index,
            dtype=float,
        )

        long_condition = ta.pine_crossover(close, hilo)
        short_condition = ta.pine_crossunder(close, hilo)

        dataframe["pine_hld"] = hld_series
        dataframe["pine_hlv"] = hlv
        dataframe["pine_hilo"] = hilo
        dataframe["pine_long_condition"] = long_condition.to_numpy()
        dataframe["pine_short_condition"] = short_condition.to_numpy()
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "hilo": dataframe["pine_hilo"].to_numpy(),
            "long_condition": dataframe["pine_long_condition"].to_numpy(),
            "short_condition": dataframe["pine_short_condition"].to_numpy(),
        }

    def pine_script(self, broker, i, ctx):
        # if buySignal
        #     strategy.entry("buy", strategy.long)
        # else if sellSignal
        #     strategy.entry("sell", strategy.short)
        if ctx["long_condition"][i]:
            broker.entry("buy", "long")
        elif ctx["short_condition"][i]:
            broker.entry("sell", "short")
