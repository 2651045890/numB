"""Port of sources/SM_cff24c6c3fbd9b88.pine (batch_001/Fisher变换动态阈值趋势跟踪策略-Fisher-Transform-Dynamic-Threshold-Trend-Following-Strategy.md).

Pine v5, `strategy("Qiuboneminer -  Fisher Transform", overlay=true)`. A
stateful Fisher Transform of `hl2`, with the recursive state carried in `var`
locals, and a fixed symmetric threshold of 2.6:

    fish(Length, timeMultiplier) =>
        var float nValue1 = na
        var float nFish   = na
        xHL2  = hl2
        xMaxH = ta.highest(xHL2, Length * timeMultiplier)
        xMinL = ta.lowest(xHL2, Length * timeMultiplier)
        nValue1 := 0.33 * 2 * ((xHL2 - xMinL) / (xMaxH - xMinL) - 0.5)
                   + 0.67 * nz(nValue1[1])
        nValue2 = if nValue1 > 0.99
            0.999
        else if nValue1 < -0.99
            -0.999
        else
            nValue1
        nFish := 0.5 * math.log((1 + nValue2) / (1 - nValue2))
                 + 0.5 * nz(nFish[1])
        nFish

    Fisher1 = fish(Len, mult1)

    longCondition  = Fisher1 > nz(Fisher1[1]) and nz(Fisher1[1]) <= nz(Fisher1[2])
                     and Fisher1 < -threshold
    shortCondition = Fisher1 < nz(Fisher1[1]) and nz(Fisher1[1]) >= nz(Fisher1[2])
                     and Fisher1 > threshold

    if (longCondition)
        strategy.entry("Long", strategy.long)
    if (shortCondition)
        strategy.entry("Short", strategy.short)

The two recursive locals cannot be expressed with a rolling call: `nValue1`
feeds itself with weight 0.67 through `nz(nValue1[1])`, and `nFish` likewise
with weight 0.5 through `nz(nFish[1])`. Both are therefore carried in an
explicit bar loop, which is also what fixes their initialisation -- `var`
starts them at na, `nz(...)` folds na to 0 in the feedback term only, and the
value itself stays na until the `ta.highest` / `ta.lowest` window has filled
(their raw ratio is na before then, and na propagates through the whole
expression).

`nz` appears in the conditions too, but only on the *history* references:
`Fisher1` itself is compared unguarded, so while it is na every comparison is
na and Pine evaluates that as false.

`threshold = 2.6` is a plain assignment, NOT an `input()`, so it is not a
parameter and stays a literal here. `Len` and `mult1` are the only two inputs,
and `minval=1` bounds the widget only.

`strategy()` declares only `title` / `overlay`, so Pine's documented defaults
apply and are what this port carries: `default_qty_type=fixed`, one unit per
order, `commission_value=0`, `pyramiding=0`, `process_orders_on_close=false`.
Initial capital is unset in the source, hence Pine's documented default
1000000.

The `/*backtest` header declares `period: 1h` on Futures_Binance BTC_USDT, so
`timeframe` is "1h"; its `basePeriod: 15m` is the FMZ backtester's own
granularity for filling those 1h bars, not the strategy's period.

There is no exit call in the source -- not `strategy.close`, not
`strategy.exit` -- so a position is closed only by the opposite entry
reversing it: `source_reproduce_stops` is False and a position still open at
the end of the window stays open.

FIDELITY:

* The markdown prose calls the threshold "dynamic" and claims it is adjusted
  from the historical volatility of the Fisher value. The source's threshold
  is the constant 2.6 and there is no adaptive term anywhere; the prose
  describes an intent the code does not implement. The source is
  authoritative; recorded, not acted on.
* The markdown prose also says the signal is a crossing of the Fisher value
  through the threshold ("由下往上穿越负阈值"), whereas the source's condition
  is `Fisher1` above its own previous value with the previous value already at
  or below the value before that, AND the current value still on the far side
  of the threshold -- a local-turn confirmation, not a level crossing. The
  source is authoritative; recorded, not acted on.
* `ta.highest` / `ta.lowest` return na until their window is full and
  propagate na within it (pine_ta.pine_highest / pine_lowest); that na then
  propagates through `nValue1` and `nFish` exactly as Pine's would.
* Division by a zero range (`xMaxH == xMinL`, i.e. a flat `hl2` window) is
  modelled as na, which is what Pine's float division by zero yields. It
  cannot fire on real or synthetic OHLC data but is not silently turned into
  an infinity.
* `nz` in the feedback terms is modelled as Pine's 2-arg form with the default
  replacement 0 (`pine_ta.nz`), applied to the history reference only, so the
  state is not reset -- `nFish` keeps its accumulated value once it exists.
* `math.log` is the natural logarithm, as numpy's `log` is.
* `plot` / `hline` / the plot color ternary / `title` / `overlay` carry no
  orders and are not reproduced.
* Leverage, margin, liquidation and funding are not modelled; the venue's
  contract-step rounding is not modelled either, so the framework and the
  engine can differ by a rounded quantity (the chain verifier measures that
  separately rather than treating it as a signal difference).
"""
import numpy as np
import pandas as pd
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


class SMFisherTransformDynamicThreshold_cff24c(PinePortBase, IStrategy):
    source_id = "SM_cff24c6c3fbd9b88"
    source_file = (
        "Fisher变换动态阈值趋势跟踪策略"
        "-Fisher-Transform-Dynamic-Threshold-Trend-Following-Strategy.md"
    )
    timeframe = "1h"
    can_short = True
    source_defaults: dict = {"Len": 10, "mult1": 1}
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    source_reproduce_stops = False
    source_fidelity_notes = [
        "threshold = 2.6 is a plain assignment, not an input(), so it is a "
        "literal and not a source_default.",
        "The markdown describes the threshold as dynamic / volatility-adapted; "
        "the source uses the constant 2.6 and has no adaptive term. Recorded, "
        "not applied.",
        "The markdown describes the signals as threshold crossings; the source "
        "condition is a local turn of Fisher1 above its own [1] / [2] history "
        "while still beyond the threshold. Recorded, not applied.",
        "The two recursive locals (nValue1 with weight 0.67 of its own [1], "
        "nFish with weight 0.5 of its own [1]) are carried in an explicit bar "
        "loop; var initialises both to na and nz folds na to 0 in the feedback "
        "term only.",
        "Fisher1 is compared unguarded in the conditions and only its [1] / [2] "
        "history references are wrapped in nz, exactly as the source spells "
        "them.",
        "Division by a zero hl2 range is modelled as na (Pine float division by "
        "zero), not as an infinity.",
        "No exit call exists (no strategy.close, no strategy.exit): a position "
        "is closed only by an opposite entry reversing it, so "
        "source_reproduce_stops is False and a position open at the end of the "
        "window stays open.",
        "strategy() declares only title / overlay, so Pine's documented "
        "defaults apply: fixed quantity 1, commission 0%, pyramiding 0, "
        "process_orders_on_close=false, initial capital 1000000.",
        "plot / hline / title / overlay are display-only and are not "
        "reproduced.",
        "Leverage, margin, liquidation, funding and venue contract-step "
        "rounding are not modelled.",
    ]

    def pine_indicators(self, dataframe, params):
        length = int(params["Len"])
        time_multiplier = int(params["mult1"])
        threshold = 2.6  # literal in the source, not an input

        # xHL2  = hl2
        # xMaxH = ta.highest(xHL2, Length * timeMultiplier)
        # xMinL = ta.lowest(xHL2, Length * timeMultiplier)
        hl2 = (dataframe["high"] + dataframe["low"]) / 2.0
        window = length * time_multiplier
        x_max_h = ta.pine_highest(hl2, window).to_numpy(dtype=float)
        x_min_l = ta.pine_lowest(hl2, window).to_numpy(dtype=float)
        hl2_values = hl2.to_numpy(dtype=float)

        # nValue1 := 0.33 * 2 * ((xHL2 - xMinL) / (xMaxH - xMinL) - 0.5)
        #            + 0.67 * nz(nValue1[1])
        # nValue2 = clamp(nValue1, -0.999, 0.999) by the two comparisons
        # nFish   := 0.5 * math.log((1 + nValue2) / (1 - nValue2))
        #            + 0.5 * nz(nFish[1])
        value1_state = np.nan
        fish_state = np.nan
        n_value1_out = np.full(len(dataframe), np.nan)
        fish_out = np.full(len(dataframe), np.nan)
        for i in range(len(dataframe)):
            high_i = x_max_h[i]
            low_i = x_min_l[i]
            span = high_i - low_i
            if np.isnan(span) or span == 0.0:
                # Window not full (na propagates) or a zero range: Pine's float
                # division by zero is na, not an infinity.
                value1 = np.nan
            else:
                previous = 0.0 if np.isnan(value1_state) else value1_state
                value1 = 0.33 * 2 * ((hl2_values[i] - low_i) / span - 0.5) + 0.67 * previous

            if np.isnan(value1):
                value2 = np.nan
            elif value1 > 0.99:
                value2 = 0.999
            elif value1 < -0.99:
                value2 = -0.999
            else:
                value2 = value1

            if np.isnan(value2):
                fish = np.nan
            else:
                previous_fish = 0.0 if np.isnan(fish_state) else fish_state
                fish = (
                    0.5 * np.log((1.0 + value2) / (1.0 - value2)) + 0.5 * previous_fish
                )

            n_value1_out[i] = value1
            fish_out[i] = fish
            value1_state = value1
            fish_state = fish

        fisher_series = pd.Series(np.array(fish_out), index=dataframe.index, dtype=float)
        fisher_1 = ta.nz(fisher_series.shift(1))
        fisher_2 = ta.nz(fisher_series.shift(2))

        dataframe["pine_fisher"] = fisher_series
        dataframe["pine_n_value1"] = n_value1_out
        # longCondition  = Fisher1 > nz(Fisher1[1])
        #                  and nz(Fisher1[1]) <= nz(Fisher1[2])
        #                  and Fisher1 < -threshold
        dataframe["pine_long_condition"] = (
            (fisher_series > fisher_1) & (fisher_1 <= fisher_2) & (fisher_series < -threshold)
        )
        # shortCondition = Fisher1 < nz(Fisher1[1])
        #                  and nz(Fisher1[1]) >= nz(Fisher1[2])
        #                  and Fisher1 > threshold
        dataframe["pine_short_condition"] = (
            (fisher_series < fisher_1) & (fisher_1 >= fisher_2) & (fisher_series > threshold)
        )
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "long_condition": dataframe["pine_long_condition"].to_numpy(),
            "short_condition": dataframe["pine_short_condition"].to_numpy(),
        }

    def pine_script(self, broker, i, ctx):
        # if (longCondition)
        #     strategy.entry("Long", strategy.long)
        if ctx["long_condition"][i]:
            broker.entry("Long", "long")
        # if (shortCondition)
        #     strategy.entry("Short", strategy.short)
        if ctx["short_condition"][i]:
            broker.entry("Short", "short")
