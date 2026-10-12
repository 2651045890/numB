"""Port of sources/SM_d53b33d1c568d7f7.pine (batch_001/Linear-Regression.md).

Pine v4. The file declares `study("Linear Regression ++ [Lucem Anb]", ...)`,
NOT `strategy(...)`: the two `strategy.entry` calls at the bottom are an order
block APPENDED to the indicator by the converter site that published it
(fmz.com/strategy/365345, named in the md's Detail link). Pine does not compile
`strategy.entry` inside `study()`, so the "original strategy" is the indicator
PLUS that appended block, and the trading behaviour it defines is entry-only:

    if buy
        strategy.entry("Enter Long", strategy.long)
    else if sell
        strategy.entry("Enter Short", strategy.short)

The indicator is LucemAnb's linear-regression channel:

    linreg      = data(linreg(source, length, offset))
    linreg_p    = data(linreg(source, length, offset + 1))
    slope       = linreg - linreg_p
    intercept   = linreg - bar_index * slope
    deviation   = sqrt( sum_{i=0..length-1}
                        pow(source[i] - (slope*(bar_index-i) + intercept), 2) / length )
    dm_current  = -deviation*dev + linreg          # lower channel
    dp_current  =  deviation*dev + linreg          # upper channel
    buy         = crossunder(close, dm_current)
    sell        = crossover(close, dp_current)

with `data(x) = sma(security(syminfo.tickerid, mtf_val != "" ? mtf_val :
timeframe.period, x), smoothing)`. So the orders buy when the close crosses
below the LOWER regression channel and sell when it crosses above the UPPER
one -- the mean-reversion reading the md's prose describes ("Use this for
BreakOuts and Reversals", "this script is the likes of Bollinger bands").

There is NO exit of any kind in the source -- no `strategy.close`, no
`strategy.exit`, and no commented-out exit line either (only `plot` /
`plotshape` calls). A position is therefore only ever left by the opposite
entry, which the engine models as a reversal. `pyramiding` keeps Pine's default
of 0, so a repeated signal while already positioned that way is ignored.

FIDELITY:

* `request.security()` is not modelled by the engine (PINE_SEMANTICS.md 2.1),
  but `mtf_val` is an `input.resolution` whose default is the EMPTY string, so
  `data()` falls back to `timeframe.period` -- the chart's own timeframe -- and
  the call degrades to the chart's own series. That is what the port
  reproduces. Overriding `mtf_val` with a real resolution CANNOT be followed:
  the engine does not resample and the result would be wrong, so `mtf_val` is
  recorded in `source_defaults` but not modelled beyond "".
* `smoothing` is applied as `sma(x, smoothing)` by `data()`, and with the
  default of 1 that is the identity; the port applies it around both regression
  series so an override behaves as the source would.
* `deviationSum` is the source's own `:=` accumulation over `for i = 0 to
  length-1`, i.e. a per-bar loop of `length` iterations, not a running series
  across bars. The port runs the same per-bar loop. Because
  `intercept = linreg - bar_index*slope`, the residual
  `source[i] - (slope*(bar_index-i) + intercept)` reduces to
  `source[i] - linreg + slope*i`, so the absolute bar index cancels and the
  loop's result does not depend on where the frame starts -- which is what
  makes it reproducible without Pine's `bar_index`.
* Pine's `/` on a zero denominator yields na, so `deviation` is na whenever the
  loop produced na (warmup). The port leaves those bars na rather than
  substituting a value.
* `updating = goto <= 0 or x < goto` is computed by the source and read by
  NOTHING -- it gates no plot and no order. Not reproduced as behaviour; `goto`
  is kept in `source_defaults` because the source declares it.
* `x1`, `x2`, `y1` are computed by the source and unused; only `y2` (= linreg)
  is read, by the two channel lines.
* `cc()`, `p`, `q`, `line_thick`, `signals` and the `plot`/`plotshape` calls
  are display-only and place no order. `show_last=signals == "All" ? ... :
  length` only limits how many markers are drawn.
* The md's argument table shows `v_input_3` (offset) as `false` and
  `v_input_5` (smoothing) as `true` because the host rendered the numeric
  literals 0 and 1 as booleans; the source's literals are `0` and `1` and those
  are what the port carries. No behavioural conflict.
* The source declares `study(...)`, so no strategy() properties exist and
  Pine's documented defaults apply: market orders of `fixed` size 1 contract,
  initial capital 1000000, commission 0%, pyramiding 0,
  process_orders_on_close=false.
* The header's backtest window (2022-04-23 to 2022-05-22) is extraction
  metadata, not an `input.time` filter, so no data is trimmed. Its
  `basePeriod: 5m` is the host's intrabar granularity for filling 45m bars,
  not the strategy's period.
* Leverage, margin, liquidation, funding and the venue's contract-step rounding
  are not modelled (PINE_SEMANTICS.md 1.6 measures the rounding separately).
"""
import math

import numpy as np
import pandas as pd
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


class SMLinearRegression_d53b33(PinePortBase, IStrategy):
    source_id = "SM_d53b33d1c568d7f7"
    source_file = "Linear-Regression.md"
    timeframe = "45m"
    can_short = True
    # Input defaults exactly as written in the source.
    source_defaults: dict = {
        "source": "close",
        "length": 100,
        "offset": 0,
        "dev": 2.0,
        "smoothing": 1,
        "mtf_val": "",
        "line_thick": 4,
        "signals": "Recent",
        "p": "Lime",
        "q": "Red",
        "goto": 0,
    }
    # The source declares study(...), not strategy(...), so no strategy()
    # properties exist and Pine's documented defaults apply.
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    # No strategy.close / strategy.exit / stop / limit / trail anywhere.
    source_reproduce_stops = False
    source_mintick = 0.1
    source_fidelity_notes = [
        "The file declares study(...), not strategy(...): the strategy.entry "
        "pair at the bottom is an order block appended by the converter site "
        "(fmz.com/strategy/365345 per the md's Detail link). The port "
        "reproduces the indicator PLUS that appended block, i.e. entry-only "
        "behaviour.",
        "request.security is not modelled (PINE_SEMANTICS.md 2.1). mtf_val is "
        "an input.resolution whose default is '', so data() uses "
        "timeframe.period -- the chart's own timeframe -- and the call "
        "degrades to the chart's own series; that is what the port reproduces. "
        "Overriding mtf_val with a real resolution CANNOT be followed: the "
        "engine does not resample and the result would be wrong.",
        "data(x) = sma(security(...), smoothing). With the default smoothing=1 "
        "the sma is the identity; the port still applies pine_sma around both "
        "regression series so an override behaves as the source would, and "
        "pine_sma(na, 1) stays na rather than inventing a value.",
        "linreg(source, length, offset) is Pine's ta.linreg / v4 linreg: the "
        "least-squares line over the last `length` bars, evaluated `offset` "
        "bars back from the newest bar. pine_ta.pine_linreg implements exactly "
        "that, so slope = linreg(offset) - linreg(offset+1) is the fitted "
        "line's per-bar slope, as the source intends.",
        "deviationSum is the source's own `:=` accumulation over `for i = 0 to "
        "length-1` -- a per-bar loop of length iterations, NOT a running "
        "series across bars. The port runs the same per-bar loop with the same "
        "bounds and offsets.",
        "The residual `source[i] - (slope*(bar_index-i) + intercept)` reduces "
        "to `source[i] - linreg + slope*i` because intercept = linreg - "
        "bar_index*slope, so the absolute bar index cancels. The port does not "
        "need to know where the chart starts; the source's own `bar_index` "
        "reads are therefore reproduced without carrying a bar counter.",
        "Pine's `/` yields na for a zero denominator, and sqrt of a negative "
        "cannot arise because the accumulation is a sum of squares. Warmup "
        "bars, where linreg is na, leave deviation na rather than substituting "
        "a value.",
        "`updating = goto <= 0 or x < goto` is computed by the source and read "
        "by nothing -- it gates no plot and no order -- so it is not "
        "reproduced as behaviour; the `goto` input is still declared. `x1`, "
        "`x2` and `y1` are likewise computed and unused; only y2 (= linreg) is "
        "read, by the two channel lines.",
        "cc(), p, q, line_thick, signals and the plot/plotshape calls are "
        "display-only and place no order. show_last only limits how many "
        "markers are drawn.",
        "The md's argument table shows v_input_3 (offset) as false and "
        "v_input_5 (smoothing) as true because the host rendered the numeric "
        "literals 0 and 1 as booleans; the source's literals are 0 and 1 and "
        "those are what the port carries. No behavioural conflict.",
        "`source` is an input.source defaulting to close, resolved through "
        "pine_ta.pine_source, so close/high/low/open/hl2/hlc3/hlcc4/ohlc4 are "
        "all selectable without changing the port's logic.",
        "The source has no exit of any kind: no strategy.close, no "
        "strategy.exit, no stop or limit order, and no commented-out exit "
        "line. A position is only left by the opposite entry, which the engine "
        "models as a reverse fill. source_reproduce_stops is False "
        "accordingly.",
        "The source declares study(...), so no strategy() properties exist and "
        "Pine's documented defaults are used: default_qty_type fixed, "
        "default_qty_value 1, commission 0%, pyramiding 0, initial capital "
        "1000000 USD.",
        "The md's prose ('Use this for BreakOuts and Reversals', 'this script "
        "is the likes of Bollinger bands') describes the indicator's intended "
        "use, not the trading rules; the appended block's crossunder/crossover "
        "of the channels is what places the orders. The md's embedded source "
        "block is verbatim identical to the .pine source.",
        "The header's backtest window is extraction metadata, not an "
        "input.time filter, so the port runs on whatever range the caller "
        "supplies; basePeriod: 5m is the host's intrabar fill granularity, not "
        "the strategy's period.",
        "Leverage, margin, liquidation, funding and the venue's contract-step "
        "rounding are not modelled (PINE_SEMANTICS.md 1.6).",
    ]

    def pine_indicators(self, dataframe, params):
        source = ta.pine_source(dataframe, str(params["source"]))
        length = int(params["length"])
        offset = int(params["offset"])
        deviation_multiplier = float(params["dev"])
        smoothing = int(params["smoothing"])

        # data(x) = sma(security(syminfo.tickerid, mtf_val != "" ? mtf_val :
        #             timeframe.period, x), smoothing); with the default mtf_val
        # of "" this is sma(x, smoothing) on the chart's own series.
        linreg = ta.pine_sma(ta.pine_linreg(source, length, offset), smoothing)
        linreg_p = ta.pine_sma(
            ta.pine_linreg(source, length, offset + 1), smoothing
        )
        slope = linreg - linreg_p

        # for i = 0 to length - 1: deviationSum += pow(source[i] -
        #     (slope*(bar_index-i) + intercept), 2)
        # intercept = linreg - bar_index*slope, so the term inside pow() is
        # `source[i] - linreg + slope*i` and bar_index cancels out.
        values = source.to_numpy(dtype=float)
        regression = linreg.to_numpy(dtype=float)
        slopes = slope.to_numpy(dtype=float)
        indices = np.arange(length - 1, -1, -1, dtype=float)
        deviation = np.full(len(values), np.nan, dtype=float)
        for bar in range(length - 1, len(values)):
            if not (np.isfinite(regression[bar]) and np.isfinite(slopes[bar])):
                continue
            window = values[bar - length + 1 : bar + 1]
            if not np.all(np.isfinite(window)):
                continue
            residual = window - regression[bar] + slopes[bar] * indices
            # sqrt(deviationSum / length); the sum of squares cannot be
            # negative, and the clamp only absorbs float noise.
            deviation[bar] = math.sqrt(
                max(float(np.sum(residual * residual)) / length, 0.0)
            )

        deviation_series = pd.Series(deviation, index=dataframe.index)
        dm_current = -deviation_series * deviation_multiplier + linreg
        dp_current = deviation_series * deviation_multiplier + linreg
        close = dataframe["close"]

        dataframe["pine_linreg"] = linreg
        dataframe["pine_linreg_p"] = linreg_p
        dataframe["pine_slope"] = slope
        dataframe["pine_deviation"] = deviation_series
        dataframe["pine_dm_current"] = dm_current
        dataframe["pine_dp_current"] = dp_current
        # buy = crossunder(close, dm_current) / sell = crossover(close, dp_current)
        dataframe["pine_long_condition"] = ta.pine_crossunder(close, dm_current)
        dataframe["pine_short_condition"] = ta.pine_crossover(close, dp_current)
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "linreg": dataframe["pine_linreg"].to_numpy(),
            "dm_current": dataframe["pine_dm_current"].to_numpy(),
            "dp_current": dataframe["pine_dp_current"].to_numpy(),
            "long_condition": dataframe["pine_long_condition"].to_numpy(),
            "short_condition": dataframe["pine_short_condition"].to_numpy(),
        }

    def pine_script(self, broker, i, ctx):
        # if buy
        #     strategy.entry("Enter Long", strategy.long)
        # else if sell
        #     strategy.entry("Enter Short", strategy.short)
        if ctx["long_condition"][i]:
            broker.entry("Enter Long", "long")
        elif ctx["short_condition"][i]:
            broker.entry("Enter Short", "short")
