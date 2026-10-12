"""Port of sources/SM_5a59af968c5a9395.pine (batch_001/Ichimoku-Cloud-Smooth-Oscillator.md).

Pine v4. The file is ChaoZhang's "Ichimoku Cloud Smooth Oscillator" INDICATOR --
`study(title="Ichimoku Cloud Smooth Oscillator")` -- an Ichimoku Cloud whose
lines are replaced by Tim Tillson's T3 smoothing, plotted as a signed distance
from the (displaced) cloud:

    b  = 0.7
    c1 = -b^3                c2 = 3b^2 + 3b^3
    c3 = -6b^2 - 3b - 3b^3   c4 = 1 + 3b + b^3 + 3b^2
    t3n(source, len) = c1*ema^6 + c2*ema^5 + c3*ema^4 + c4*ema^3
                       (the exponents are the number of nested ema() calls)

    conversionLine = t3n(close, conversionPeriods)      # 9
    baseLine       = t3n(close, basePeriods)            # 26
    leadLine1      = avg(conversionLine, baseLine)[displacement]   # [26]
    leadLine2      = t3n(close, laggingSpan2Periods)[displacement] # [26]
    middleLine     = avg(leadLine1, leadLine2)
    cloudHeight    = leadLine1 - leadLine2
    conversionDistance = conversionLine - middleLine

    var conversionCloudDistance = 0.0
    if conversionDistance > 1/2*abs(cloudHeight) or conversionDistance < -1/2*abs(cloudHeight)
        conversionCloudDistance := conversionDistance - abs(cloudHeight) / 2
    else
        conversionCloudDistance := 0

and a converter-appended order block at the end:

    if conversionCloudDistance > 0
        strategy.entry("Enter Long", strategy.long)
    else if conversionCloudDistance < 0
        strategy.entry("Enter Short", strategy.short)

`study()` cannot host `strategy.entry`, so the trading behaviour IS that block.
There is NO exit anywhere in the file -- live or commented out -- so a position
is only ever replaced by an opposite entry, and one still open at the end of the
window stays open (`source_reproduce_stops = False`).

FIDELITY:

* The `[displacement]` history reference is a reference to the PAST
  (`x[26]` = 26 bars ago), which is how the source is written: it is not the
  usual +/-26 forward plot offset of an Ichimoku cloud. The port therefore uses
  `.shift(displacement)` (down, i.e. lagging) and NOT a negative shift. This
  means the source reads no future data anywhere.
* `conversionCloudDistance` is a `var` whose `if` / `else` assigns both arms,
  so it has no recursion and the port computes it vectorised. When
  `cloudHeight` is na (the 26 displaced bars at the start), both comparisons are
  false in Pine and the else arm stores 0; `np.where` reproduces that.
* The entry conditions are re-evaluated on every bar, and `conversionCloudDistance`
  stays on one side of zero for long stretches, so a same-direction entry is
  placed while that direction is already open. With `pyramiding=0` (Pine's
  default, and this file declares no `strategy()`) Pine ignores such an entry at
  creation, and the engine models that; so the real trades are the
  sign flips of the oscillator, and each flip is a reversal.
* `pivotPeriods` is an `input(52)` that the source NEVER uses -- it appears in no
  expression and in no order. It is kept in `source_defaults` because it is a
  declared default of the source, not because the port reads it.
* `avg(a, b)` is Pine's two-argument average, `(a + b) / 2`; `1/2` is float
  division (0.5).
* `t3n` is reproduced as written -- six/five/four/three NESTED `ema` calls with
  the source's own coefficients -- rather than calling any library T3, so the
  smoothing, its nesting depth and its seeding are the source's. Each `ema` is
  pine_ta.pine_ema (seeded on the first non-na observation; Pine does not
  publish its seed rule -- PINE_SEMANTICS.md section 3.1).
* `cloudColor`, `conversionColor`, `p1`, `p2`, `plot(0, ...)` and the `study()`
  title are display only; nothing in them reaches an order.
* No `strategy()` call exists (the file declares a study), so every trade
  property is Pine's documented default: `default_qty_type` fixed,
  `default_qty_value` 1 CONTRACT (not 100% of equity), `initial_capital`
  1000000, commission 0%, `pyramiding` 0, `process_orders_on_close` false.
* The `/*backtest` header declares `period: 2h` on Futures_Binance BTC_USDT, so
  `timeframe` is "2h"; its `basePeriod: 15m` is the FMZ backtester's fill
  granularity.
* Leverage, margin, liquidation, funding and the venue's contract-step rounding
  are not modelled.
"""
import numpy as np
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase

# T3 constants (the source's own b and its four coefficients), module level so
# the nesting in _t3n reads like the source line.
_T3_B = 0.7
_T3_C1 = -_T3_B * _T3_B * _T3_B
_T3_C2 = 3 * _T3_B * _T3_B + 3 * _T3_B * _T3_B * _T3_B
_T3_C3 = -6 * _T3_B * _T3_B - 3 * _T3_B - 3 * _T3_B * _T3_B * _T3_B
_T3_C4 = 1 + 3 * _T3_B + _T3_B * _T3_B * _T3_B + 3 * _T3_B * _T3_B


def _t3n(source, length):
    """t3n(source, len) => c1*ema6 + c2*ema5 + c3*ema4 + c4*ema3, as written.

    The number after `ema` is the number of nested `ema` calls, matching the
    source's parenthesised expression one for one.
    """
    length = int(length)
    e2 = ta.pine_ema(ta.pine_ema(source, length), length)
    e3 = ta.pine_ema(e2, length)
    e4 = ta.pine_ema(e3, length)
    e5 = ta.pine_ema(e4, length)
    e6 = ta.pine_ema(e5, length)
    return _T3_C1 * e6 + _T3_C2 * e5 + _T3_C3 * e4 + _T3_C4 * e3


class SMIchimokuCloudSmoothOscillator_5a59af(PinePortBase, IStrategy):
    source_id = "SM_5a59af968c5a9395"
    source_file = "Ichimoku-Cloud-Smooth-Oscillator.md"
    timeframe = "2h"
    can_short = True
    source_defaults: dict = {
        "conversionPeriods": 9,
        "basePeriods": 26,
        "laggingSpan2Periods": 52,
        "pivotPeriods": 52,   # declared by the source and never used -- kept as declared
        "displacement": 26,
    }
    # The file declares a `study()`, not a `strategy()`, so Pine's documented
    # defaults apply -- see the docstring.
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    # The appended block places no stop, limit, target or trailing exit.
    source_reproduce_stops = False
    source_fidelity_notes = [
        "Converter-appended source: the file declares an INDICATOR (`study(title="
        "\"Ichimoku Cloud Smooth Oscillator\")`) and a tool appended the block "
        "`if conversionCloudDistance>0 / strategy.entry(\"Enter Long\", "
        "strategy.long) else if conversionCloudDistance<0 / strategy.entry("
        "\"Enter Short\", strategy.short)`. Pine v4 cannot call strategy.entry "
        "from a study, so the port reproduces what the appended block does: "
        "entries only, one per oscillator sign.",
        "NO exit exists in the source -- not even a commented-out one -- so a "
        "position is closed only by an opposite entry reversing it, "
        "source_reproduce_stops is False, and a position open at the end of the "
        "window stays open.",
        "`leadLine1` / `leadLine2` use `[displacement]`, a reference to 26 bars "
        "AGO, not the usual forward plot offset of an Ichimoku cloud. The port "
        "keeps that direction (.shift(+26), lagging); no future data is read.",
        "`pivotPeriods = input(52)` is never used by the source. It is kept in "
        "source_defaults because it is a declared input default, but no "
        "expression or order in the port reads it.",
        "No `strategy()` call exists (the file is a study), so trade properties "
        "are Pine's documented defaults: fixed sizing, qty 1, initial capital "
        "1000000, commission 0%, pyramiding 0, process_orders_on_close=false.",
        "The oscillator stays on one side of zero for long stretches while the "
        "entry is re-evaluated every bar; with pyramiding 0 Pine ignores the "
        "same-direction re-entries at creation, so the realised trades are the "
        "sign flips (each a reversal). Reproduced by the engine, not special-"
        "cased in the port.",
        "`t3n` is replayed as the source writes it -- six/five/four/three "
        "nested `ema` calls with the source's b=0.7 coefficients -- instead of "
        "any library T3. Each ema is pine_ta.pine_ema, seeded on the first "
        "non-na value; Pine does not publish its EMA seed rule "
        "(PINE_SEMANTICS.md section 3.1), so warm-up is a modelling choice that "
        "converges.",
        "When cloudHeight is na (the 26 displaced bars at the start) both "
        "comparisons are false in Pine, so the else arm stores 0 and no entry "
        "can fire; np.where reproduces that.",
        "cloudColor / conversionColor / p1 / p2 / plot(0, ...) and the study() "
        "title are display only and are not reproduced.",
        "The /*backtest header declares `period: 2h` on Futures_Binance "
        "BTC_USDT (`basePeriod: 15m` is the FMZ fill granularity).",
        "md-vs-source consistency (recorded because this wave asks for every "
        "md/source difference): the md's code block and argument table match "
        "the source line for line, and its prose ('the bold line is the "
        "signal: green indicates a buy signal while red indicates a sell "
        "signal. Gray represents a possible change in direction') matches the "
        "appended block's `> 0` / `< 0` / neither test. No difference found. "
        "The md's Author field says ChaoZhang; the source has no copyright line.",
        "Leverage, margin, liquidation and funding are not modelled; the "
        "venue's contract-step rounding is not modelled either (the chain "
        "verifier measures that separately).",
    ]

    def pine_indicators(self, dataframe, params):
        close = dataframe["close"]
        displacement = int(params["displacement"])

        # conversionLine = t3n(close, conversionPeriods)
        conversion_line = _t3n(close, params["conversionPeriods"])
        # baseLine = t3n(close, basePeriods)
        base_line = _t3n(close, params["basePeriods"])
        # leadLine1 = avg(conversionLine, baseLine)[displacement]
        lead_line1 = ((conversion_line + base_line) / 2).shift(displacement)
        # leadLine2 = t3n(close, laggingSpan2Periods)[displacement]
        lead_line2 = _t3n(close, params["laggingSpan2Periods"]).shift(displacement)
        # middleLine = avg(leadLine1, leadLine2)
        middle_line = (lead_line1 + lead_line2) / 2
        # cloudHeight = leadLine1 - leadLine2
        cloud_height = lead_line1 - lead_line2
        # conversionDistance = conversionLine - middleLine
        conversion_distance = conversion_line - middle_line

        # var conversionCloudDistance = 0.0
        # if conversionDistance > 1/2*abs(cloudHeight) or conversionDistance < -1/2*abs(cloudHeight)
        #     conversionCloudDistance := conversionDistance - abs(cloudHeight) / 2
        # else
        #     conversionCloudDistance := 0
        half_cloud = cloud_height.abs() / 2
        outside = (conversion_distance > half_cloud) | (conversion_distance < -half_cloud)
        cloud_distance = np.where(outside.to_numpy(), (conversion_distance - half_cloud).to_numpy(), 0.0)

        dataframe["pine_conversion_line"] = conversion_line
        dataframe["pine_base_line"] = base_line
        dataframe["pine_lead_line1"] = lead_line1
        dataframe["pine_lead_line2"] = lead_line2
        dataframe["pine_middle_line"] = middle_line
        dataframe["pine_cloud_height"] = cloud_height
        dataframe["pine_conversion_distance"] = conversion_distance
        dataframe["pine_conversion_cloud_distance"] = cloud_distance
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "conversion_cloud_distance": dataframe["pine_conversion_cloud_distance"].to_numpy(),
        }

    def pine_script(self, broker, i, ctx):
        cloud_distance = ctx["conversion_cloud_distance"][i]
        # if conversionCloudDistance>0
        #     strategy.entry("Enter Long", strategy.long)
        # else if conversionCloudDistance<0
        #     strategy.entry("Enter Short", strategy.short)
        if cloud_distance > 0:
            broker.entry("Enter Long", "long")
        elif cloud_distance < 0:
            broker.entry("Enter Short", "short")
