"""Port of sources/SM_cbc975209e58467b.pine (batch_001/Demark-Reversal-Points.md).

Pine v5. The file's own `indicator('Demark Reversal Points [CC]')` call is
COMMENTED OUT and the two `strategy.entry` calls at the bottom are an order
block APPENDED to the indicator by the converter site that published it
(fmz.com/strategy/361719, named in the md's Detail link). Pine v5 does not
compile `strategy.entry` inside `indicator()`, so the "original strategy" is
the indicator PLUS that appended block, and the trading behaviour it defines is
entry-only:

    if ta.crossover(drp, 0)
        strategy.entry("Enter Long", strategy.long)
    else if ta.crossunder(drp, 0)
        strategy.entry("Enter Short", strategy.short)

The indicator is cheatcountry's Tom DeMark REVERSAL-point counter:

    src    = request.security(syminfo.tickerid, res, inp[0])[1]
    uCount = count of i in [0, length-1] with nz(src[i]) > nz(src[i + lbLength])
    dCount = count of i in [0, length-1] with nz(src[i]) < nz(src[i + lbLength])
    drp    = dCount == length ? 1 : uCount == length ? -1 : 0

i.e. a full `length`-window of strictly rising closes (each measured against
the close `lbLength` bars earlier) gives +1, a full window of strictly falling
closes gives -1, anything else gives 0. The ORDER placed is driven by
`ta.crossover(drp, 0)` / `ta.crossunder(drp, 0)` -- the bar on which `drp`
switches in or out of the fully-aligned state, which for a series that only
ever takes {-1, 0, +1} means "the bar drp becomes +1 having been <= 0" and "the
bar drp becomes -1 having been >= 0".

There is NO exit of any kind in the source -- no `strategy.close`, no
`strategy.exit`, and no commented-out exit line either (the two commented lines
are `barcolor` and two `plotshape` calls). A position is therefore only ever
left by the opposite entry, which the engine models as a reversal.
`pyramiding` keeps Pine's default of 0, so a repeated signal while already
positioned that way is ignored.

FIDELITY:

* `request.security()` is NOT modelled by the engine (PINE_SEMANTICS.md
  section 2.1). The source calls it as
  `request.security(syminfo.tickerid, res, inp[0])[1]` with `res` declared
  `input.int(title='Resolution', defval='18000')` -- a STRING handed to
  `input.int`, which does not type-check on TradingView, so the file does not
  compile there. The port models the call as the chart's OWN timeframe, which
  is the only resolution the offline engine can reproduce (it does not
  resample). This is a MODELLING CHOICE and it is also a BLOCKER: see the
  fidelity notes and the port's `source_fidelity_notes` entry on `res`. The
  same author's v4 sibling source (`SM_8083bb3fa74b541d`, "Demark Setup
  Indicator [CC]") declares the same input with `defval=""`, i.e. the chart's
  own timeframe, and that sibling port reproduces it the same way.
* The outer `[1]` is hardcoded in the source (it does not depend on `rep`), so
  `src` is the source series lagged exactly one bar.
* `nz(src[i])` turns an out-of-range or na history reference into 0, which is
  what makes the warmup bars compare 0 against 0 -- neither greater nor less --
  so uCount = dCount = 0 and drp = 0 there. The port shifts AFTER applying nz
  semantics (an out-of-range reference becomes 0, not NaN).
* `-1` is produced by `drp` but is never tested as a bare condition: the source
  compares it (`drp > 0`, `drp < 0`) and feeds it to `ta.crossover(drp, 0)` /
  `ta.crossunder(drp, 0)`. The PINE_SEMANTICS.md 1.17 trap (rewriting `? -1 :
  0` into `== 1`) therefore does not arise here; the port keeps the integer.
* `sig` / `drpColor` are computed by the source but feed only the COMMENTED-OUT
  `barcolor` line -- they place no order. Dropped as display-only; the port
  drives the entries off `drp`, which is what the appended block uses.
* `plotshape` / `alertcondition` are display- or alert-only and place no order.
* The source declares `indicator(...)` (commented out), so no strategy()
  properties exist and Pine's documented defaults apply (fixed size 1, 0%
  commission, pyramiding 0, initial capital 1000000).
* The header's backtest window (2022-02-06 to 2022-05-06) is extraction
  metadata, not an `input.time` filter, so no data is trimmed. Its
  `basePeriod: 15m` is the host's intrabar granularity for filling 2h bars,
  not the strategy's period.
* The md's argument table lists `v_input_int_1 = 18000` for Resolution, which
  matches the source literal; the md and the source agree on every default.
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


class SMDemarkReversalPoints_cbc975(PinePortBase, IStrategy):
    source_id = "SM_cbc975209e58467b"
    source_file = "Demark-Reversal-Points.md"
    timeframe = "2h"
    can_short = True
    # Input defaults exactly as written in the source. `res` keeps the source's
    # literal (a string handed to input.int) so the record is not silently
    # normalised; how the port interprets it is documented below.
    source_defaults: dict = {
        "inp": "close",
        "res": "18000",
        "rep": False,
        "bar": True,
        "length": 9,
        "lbLength": 4,
    }
    # The source declares indicator(...) (commented out), not strategy(...), so
    # no strategy() properties exist and Pine's documented defaults apply:
    # market orders of `fixed` size 1 contract, initial capital 1000000,
    # commission 0%, pyramiding 0, process_orders_on_close=false.
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    # No strategy.close / strategy.exit / stop / limit / trail anywhere, and no
    # commented-out exit line either.
    source_reproduce_stops = False
    source_mintick = 0.1
    source_fidelity_notes = [
        "The file's indicator('Demark Reversal Points [CC]') declaration is "
        "COMMENTED OUT and the strategy.entry pair at the bottom is an order "
        "block appended by the converter site (fmz.com/strategy/361719 per the "
        "md's Detail link). The port reproduces the indicator PLUS that "
        "appended block, i.e. entry-only behaviour.",
        "BLOCKER -- request.security is not modelled (PINE_SEMANTICS.md 2.1): "
        "the source reads its series as `request.security(syminfo.tickerid, "
        "res, inp[0])[1]` with `res = input.int(title='Resolution', "
        "defval='18000')`. That literal is a STRING passed to input.int, which "
        "does not type-check on TradingView, so the source does not compile "
        "there and '18000' is not a resolution string the platform would "
        "produce. The port models the call as the chart's OWN timeframe, the "
        "only resolution the offline engine can reproduce because it does not "
        "resample. If '18000' is meant as a genuine higher resolution the port "
        "CANNOT follow it and the resulting signals would differ (a coarser "
        "step function makes src[i] == src[i+lbLength] far more often, so "
        "drp would rarely reach +-1). Recorded, not hidden.",
        "The same author's v4 sibling source (SM_8083bb3fa74b541d, 'Demark "
        "Setup Indicator [CC]') declares the same Resolution input as "
        "`defval=\"\"` -- the chart's own timeframe -- and that sibling port "
        "reproduces it the same way. That is the basis for the chart-timeframe "
        "reading used here, but it is an inference about the converter's "
        "output, not something the source itself states.",
        "The outer `[1]` is hardcoded and does not depend on the `rep` input, "
        "so src is exactly the source series lagged one bar. `rep` and `bar` "
        "are therefore DEAD inputs in this source: `rep` is referenced "
        "nowhere, and `bar` appears only inside the commented-out barcolor "
        "line. Both are kept in source_defaults (the source declares them) but "
        "neither affects behaviour.",
        "nz(src[i]) makes an out-of-range or na history reference 0, so warmup "
        "bars compare 0 against 0 -- neither > nor < -- and uCount = dCount = "
        "0 with drp = 0. The port applies nz to the REFERENCE (out-of-range "
        "becomes 0), not to the series before shifting, which would instead "
        "smear NaN through the window.",
        "drp can be -1, but the source never tests it as a bare condition: it "
        "compares it (drp > 0 / drp < 0) and passes it to ta.crossover(drp, 0) "
        "/ ta.crossunder(drp, 0). The PINE_SEMANTICS.md 1.17 trap does not "
        "arise, and the port keeps drp's integer values unchanged.",
        "uCount/dCount are the source's own `+=` accumulation over `for i = 0 "
        "to length - 1 by 1`; the port sums the same length comparisons "
        "vectorised, keeping the offsets i and i + lbLength and the loop "
        "bounds unchanged. The stray `dCount` expression inside the loop body "
        "(line 27) is a no-op in Pine and places nothing.",
        "The source computes `sig` and `drpColor`, but they feed only the "
        "COMMENTED-OUT barcolor line -- display-only, no order. The appended "
        "entry block uses `drp`, so the port drops sig/drpColor and drives the "
        "entries off drp.",
        "`inp` is an input.source (default close) resolved through "
        "pine_ta.pine_source, so close/high/low/open/hl2/hlc3/hlcc4/ohlc4 are "
        "all selectable without changing the port's logic.",
        "The source has no exit of any kind: no strategy.close, no "
        "strategy.exit, no stop or limit order, and no commented-out exit "
        "line. A position is only left by the opposite entry, which the engine "
        "models as a reverse fill. source_reproduce_stops is False "
        "accordingly.",
        "The source declares indicator(...) (commented out), so no strategy() "
        "properties exist and Pine's documented defaults are used: "
        "default_qty_type fixed, default_qty_value 1, commission 0%, "
        "pyramiding 0, initial capital 1000000 USD.",
        "The md's argument table (v_input_1_close Source, v_input_int_1 18000 "
        "Resolution, v_input_2 false Allow Repainting?, v_input_3 true Allow "
        "Bar Color Change?, v_input_int_2 9 Length, v_input_int_3 4 LbLength) "
        "and its embedded source block are verbatim identical to the .pine "
        "source -- including the '18000' literal. No md-vs-source conflict.",
        "The header's backtest window is extraction metadata, not an "
        "input.time filter, so the port runs on whatever range the caller "
        "supplies; basePeriod: 15m is the host's intrabar fill granularity, "
        "not the strategy's period.",
        "Leverage, margin, liquidation, funding and the venue's contract-step "
        "rounding are not modelled (PINE_SEMANTICS.md 1.6).",
    ]

    def pine_indicators(self, dataframe, params):
        length = int(params["length"])
        lb_length = int(params["lbLength"])

        # src = request.security(syminfo.tickerid, res, inp[0])[1]; with res
        # modelled as the chart's own timeframe this is the chart's series
        # lagged one bar (see FIDELITY on `res`).
        source_series = ta.pine_source(dataframe, str(params["inp"]))
        src = source_series.shift(1).to_numpy(dtype=float)

        u_count = np.zeros(len(src), dtype=float)
        d_count = np.zeros(len(src), dtype=float)
        # for i = 0 to length - 1 by 1
        for i in range(length):
            left = _nz_reference(src, i)
            right = _nz_reference(src, i + lb_length)
            u_count += (left > right).astype(float)
            d_count += (left < right).astype(float)

        # drp = dCount == length ? 1 : uCount == length ? -1 : 0
        drp = pd.Series(
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
        dataframe["pine_drp"] = drp
        # if ta.crossover(drp, 0) / else if ta.crossunder(drp, 0)
        dataframe["pine_long_condition"] = ta.pine_crossover(drp, 0)
        dataframe["pine_short_condition"] = ta.pine_crossunder(drp, 0)
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "drp": dataframe["pine_drp"].to_numpy(),
            "long_condition": dataframe["pine_long_condition"].to_numpy(),
            "short_condition": dataframe["pine_short_condition"].to_numpy(),
        }

    def pine_script(self, broker, i, ctx):
        # if ta.crossover(drp, 0)
        #     strategy.entry("Enter Long", strategy.long)
        # else if ta.crossunder(drp, 0)
        #     strategy.entry("Enter Short", strategy.short)
        if ctx["long_condition"][i]:
            broker.entry("Enter Long", "long")
        elif ctx["short_condition"][i]:
            broker.entry("Enter Short", "short")
