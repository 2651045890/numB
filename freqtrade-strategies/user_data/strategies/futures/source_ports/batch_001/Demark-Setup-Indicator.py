"""Port of sources/SM_8083bb3fa74b541d.pine (batch_001/Demark-Setup-Indicator.md).

Pine v4. The file declares `study("Demark Setup Indicator [CC]")`, NOT
`strategy(...)`: the two `strategy.entry` calls at the bottom are an order
block APPENDED to the indicator by the converter site that published it
(fmz.com/strategy/366947, named in the md's Detail link). Pine does not compile
`strategy.entry` inside `study()`, so the "original strategy" is the indicator
PLUS that appended block, and the trading behaviour it defines is entry-only:

    if crossover(dsi, 0)
        strategy.entry("Enter Long", strategy.long)
    else if crossunder(dsi, 0)
        strategy.entry("Enter Short", strategy.short)

The indicator is cheatcountry's Tom DeMark Setup counter:

    src    = security(syminfo.tickerid, res, inp[...])[...]
    uCount = count of i in [0, length-1] with nz(src[i]) > nz(src[i+length])
    dCount = count of i in [0, length-1] with nz(src[i]) < nz(src[i+length])
    dsi    = dCount == length ? 1 : uCount == length ? -1 : 0

i.e. a full `length`-window of strictly rising closes (measured against the
close `length` bars earlier) gives +1, a full window of strictly falling closes
gives -1, anything else gives 0. The ORDER placed is driven by `crossover(dsi,
0)` / `crossunder(dsi, 0)` -- the bar on which the setup switches in or out of
the fully-aligned state.

There is NO exit of any kind in the source -- no `strategy.close`, no
`strategy.exit`, and not even a commented-out one. A position is therefore only
ever left by the opposite entry, which the engine models as a reversal.
`pyramiding` keeps Pine's default of 0, so a repeated signal while already
positioned that way is ignored.

FIDELITY:

* `security()` is not modelled by the engine (PINE_SEMANTICS.md section 2.1,
  request.security multi-timeframe data). The source calls it with
  `res = input(..., defval="")` -- an EMPTY resolution, i.e. the chart's own
  timeframe -- so the call degrades to the chart's own series and the whole
  expression collapses to a plain history reference. That is what the port
  reproduces. If `res` is overridden with a real resolution the port CANNOT
  follow it: the engine does not resample, and the result would be wrong.
  `res` is therefore recorded in source_defaults, not modelled beyond "".
* `src = security(...)[rep ? 0 : barstate.isrealtime ? 0 : 1]` with the inner
  index `rep ? 0 : barstate.isrealtime ? 1 : 0`. Offline every bar is
  historical (`barstate.isrealtime` is False), so with the default `rep=false`
  the net expression is `close[1]` and with `rep=true` it is `close`. The port
  reproduces exactly those two branches from the `rep` input. The
  `barstate.isrealtime` arms cannot arise offline and are not modelled.
* `nz(src[i])` turns an out-of-range or na history reference into 0, which is
  what makes the warmup bars compare 0 against 0 -- neither greater nor less --
  so uCount = dCount = 0 and dsi = 0 there. The port shifts AFTER applying nz
  semantics (an out-of-range reference becomes 0, not NaN), rather than filling
  the series first and then shifting, which would smear NaN into the window.
* `uCount` / `dCount` are the source's own running `:=` accumulation over the
  `for i = 0 to length - 1` loop; the port sums the same `length` comparisons
  vectorised. The loop bounds and the offsets `i` and `i + length` are kept
  as-is.
* `sig` / `dsiColor` are computed by the source but feed only `barcolor()` and
  nothing else -- they place no order. They are display-only and are dropped;
  the port drives the entries off `dsi`, which is what the appended block uses.
* `inp` is an `input.source` (default close) and is resolved through
  `pine_ta.pine_source`, so any of close/high/low/open/hl2/hlc3/hlcc4/ohlc4 can
  be selected without touching the port's logic.
* The source declares `study(...)`, so no strategy() properties exist and
  Pine's documented defaults apply (fixed size 1, 0% commission, pyramiding 0,
  initial capital 1000000).
* `plotshape` / `barcolor` / `alertcondition` are display- or alert-only and
  place no order; dropped.
* The header's backtest window (2022-04-30 to 2022-05-29) is extraction
  metadata, not an `input.time` filter, so no data is trimmed. The header's
  `basePeriod: 15m` is the host's intrabar granularity for filling 30m bars,
  not the strategy's period.
* No stop, limit or trail exit exists, so `source_reproduce_stops` is False.
  `length` is declared with `minval=1`, but the appended block reads only
  `dsi`, so no warmup guard beyond `length` bars is needed.
* Leverage, margin, liquidation, funding and the venue's contract-step rounding
  are not modelled (PINE_SEMANTICS.md 1.6 measures the rounding separately).
"""
import numpy as np
import pandas as pd
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


def _nz_reference(values: np.ndarray, offset: int) -> np.ndarray:
    """Pine `nz(src[offset])`: out-of-range or na history references become 0."""
    out = np.zeros(len(values), dtype=float)
    if offset < len(values):
        if offset == 0:
            out[:] = values
        else:
            out[offset:] = values[: len(values) - offset]
    return np.nan_to_num(out, nan=0.0)


class SMDemarkSetupIndicator_8083bb(PinePortBase, IStrategy):
    source_id = "SM_8083bb3fa74b541d"
    source_file = "Demark-Setup-Indicator.md"
    timeframe = "30m"
    can_short = True
    # Input defaults exactly as written. `res` is "" (the chart's own timeframe)
    # and is the only value the port can reproduce -- see FIDELITY.
    source_defaults: dict = {
        "inp": "close",
        "res": "",
        "rep": False,
        "bar": True,
        "length": 4,
    }
    # study(...), not strategy(...): Pine's documented defaults apply.
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
        "(fmz.com/strategy/366947 per the md's Detail link). The port reproduces "
        "the indicator PLUS that appended block, i.e. entry-only behaviour.",
        "request.security is not modelled (PINE_SEMANTICS.md 2.1). The source "
        "calls it with res = '' -- an empty resolution, i.e. the chart's own "
        "timeframe -- so it degrades to the chart's own series and the whole "
        "expression is a plain history reference; that is what the port "
        "reproduces. Overriding res with a real resolution CANNOT be followed: "
        "the engine does not resample and the result would be wrong.",
        "The security() lag: the inner index is `rep ? 0 : barstate.isrealtime "
        "? 1 : 0` and the outer is `rep ? 0 : barstate.isrealtime ? 0 : 1`. "
        "Offline barstate.isrealtime is always false, so the net source is "
        "close[1] when rep=false (the default) and close when rep=true. The "
        "port implements exactly those two branches. The realtime arms cannot "
        "arise offline and are not modelled.",
        "nz(src[i]) makes an out-of-range or na history reference 0, so warmup "
        "bars compare 0 against 0 -- neither > nor < -- and uCount = dCount = 0 "
        "with dsi = 0. The port applies nz to the REFERENCE (out-of-range "
        "becomes 0), not to the series before shifting, which would instead "
        "smear NaN through the window.",
        "uCount/dCount are the source's own `:=` accumulation over `for i = 0 to "
        "length - 1`; the port sums the same length comparisons vectorised, "
        "keeping the offsets i and i + length unchanged.",
        "The source computes `sig` and `dsiColor`, but they feed only "
        "barcolor()/plotshape() -- display-only, no order. The appended entry "
        "block uses `dsi`, so the port drops sig/dsiColor and drives the "
        "entries off dsi.",
        "`inp` is an input.source (default close) resolved through "
        "pine_ta.pine_source, so close/high/low/open/hl2/hlc3/hlcc4/ohlc4 are "
        "all selectable without changing the port's logic.",
        "The source has no exit of any kind: no strategy.close, no "
        "strategy.exit, no stop or limit order, and no commented-out exit line. "
        "A position is only left by the opposite entry, which the engine models "
        "as a reverse fill. source_reproduce_stops is False accordingly.",
        "The source declares study(...), so no strategy() properties exist and "
        "Pine's documented defaults are used: default_qty_type fixed, "
        "default_qty_value 1, commission 0%, pyramiding 0, initial capital "
        "1000000 USD.",
        "The md's argument table (v_input_1 close Source, v_input_2 '' "
        "Resolution, v_input_3 false Allow Repainting, v_input_4 true Allow Bar "
        "Color Change, v_input_5 4 Length) and its embedded source block are "
        "verbatim identical to the .pine source.",
        "MD-vs-SOURCE: the md front matter names the author as 'ChaoZhang', "
        "while the source file's own header reads 'Copyright (c) 2019-present, "
        "Franklin Moormann (cheatcountry)' -- '[CC]' in the title is "
        "cheatcountry. The md records the fmz uploader, the source the original "
        "author. No effect on behaviour; recorded, not reconciled.",
        "The header's backtest window is extraction metadata, not an input.time "
        "filter, so the port runs on whatever range the caller supplies; "
        "basePeriod: 15m is the host's intrabar fill granularity, not the "
        "strategy's period.",
        "Leverage, margin, liquidation, funding and the venue's contract-step "
        "rounding are not modelled (PINE_SEMANTICS.md 1.6).",
    ]

    def pine_indicators(self, dataframe, params):
        length = int(params["length"])
        # src = security(syminfo.tickerid, res, inp[...])[...]; with res == ""
        # this is the chart's own series, lagged by the outer index.
        source_series = ta.pine_source(dataframe, str(params["inp"]))
        lag = 0 if params["rep"] else 1
        src = source_series.shift(lag).to_numpy(dtype=float)

        u_count = np.zeros(len(src), dtype=float)
        d_count = np.zeros(len(src), dtype=float)
        # for i = 0 to length - 1
        for i in range(length):
            left = _nz_reference(src, i)
            right = _nz_reference(src, i + length)
            u_count += (left > right).astype(float)
            d_count += (left < right).astype(float)

        # dsi = dCount == length ? 1 : uCount == length ? -1 : 0
        dsi = pd.Series(
            np.where(
                d_count == length,
                1.0,
                np.where(u_count == length, -1.0, 0.0),
            ),
            index=dataframe.index,
        )

        dataframe["pine_src"] = src
        dataframe["pine_ucount"] = u_count
        dataframe["pine_dcount"] = d_count
        dataframe["pine_dsi"] = dsi
        # if crossover(dsi, 0) / else if crossunder(dsi, 0)
        dataframe["pine_long_condition"] = ta.pine_crossover(dsi, 0)
        dataframe["pine_short_condition"] = ta.pine_crossunder(dsi, 0)
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "dsi": dataframe["pine_dsi"].to_numpy(),
            "long_condition": dataframe["pine_long_condition"].to_numpy(),
            "short_condition": dataframe["pine_short_condition"].to_numpy(),
        }

    def pine_script(self, broker, i, ctx):
        # if crossover(dsi, 0)
        #     strategy.entry("Enter Long", strategy.long)
        # else if crossunder(dsi, 0)
        #     strategy.entry("Enter Short", strategy.short)
        if ctx["long_condition"][i]:
            broker.entry("Enter Long", "long")
        elif ctx["short_condition"][i]:
            broker.entry("Enter Short", "short")
