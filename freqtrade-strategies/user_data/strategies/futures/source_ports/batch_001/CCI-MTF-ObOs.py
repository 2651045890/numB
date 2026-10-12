"""Port of sources/SM_f703ce8fc5a054cb.pine (batch_001/CCI-MTF-ObOs.md).

Pine v5. The file declares `indicator("CCI MTF Ob+Os")`, NOT `strategy(...)`:
the two `strategy.entry` calls at the bottom are an order block APPENDED to the
indicator by the converter site that published it (fmz.com/strategy/363582,
named in the md's Detail link). Pine v5 does not compile `strategy.entry`
inside `indicator()`, so the "original strategy" is the indicator PLUS that
appended block, and the trading behaviour it defines is entry-only:

    if cciOb
        strategy.entry("Enter Long", strategy.long)
    else if cciOs
        strategy.entry("Enter Short", strategy.short)

The indicator (thakon33's "CCI MTF Ob+Os") computes the CCI on up to five
selectable resolutions and reports overbought / oversold only when EVERY
enabled resolution agrees:

    Fsec(Sym, Tf, Exp) =>
        request.security(Sym, Tf, Exp[barstate.isrealtime ? 1 : 0],
                         barmerge.gaps_off, barmerge.lookahead_off)
                         [barstate.isrealtime ? 0 : 1]
    cci1..cci5 = Fsec(syminfo.tickerid, cciTf1..cciTf5, ta.cci(cciSrc, cciLength))

    cciK_Ob = not cciTfK_E or cciK >= cciOverbought
    cciK_Os = not cciTfK_E or cciK <= cciOversold
    cciOb   = cci1_Ob and cci2_Ob and cci3_Ob and cci4_Ob and cci5_Ob
    cciOs   = cci1_Os and cci2_Os and cci3_Os and cci4_Os and cci5_Os

On historical bars `barstate.isrealtime` is false, so the `[barstate.isrealtime
? 1 : 0]` inside the call is `[0]` (the expression itself) and the trailing
`[barstate.isrealtime ? 0 : 1]` is `[1]`: the returned security value is lagged
exactly one bar. The port reproduces that lag.

There is NO exit of any kind in the source -- no `strategy.close`, no
`strategy.exit`, no stop / limit / trail, and not even a commented-out exit
line. A position is only ever left by the opposite entry, which the engine
models as a reversal. `pyramiding` keeps Pine's default of 0, so a repeated
signal while already positioned that way is ignored.

FIDELITY -- read the two items below before using this port's numbers:

* BLOCKER: `request.security()` is NOT modelled by the engine
  (PINE_SEMANTICS.md 2.1). The source's five series are computed on
  `input.timeframe` values 15 / 30 / 60 / 120 / 240 minutes, i.e. on bars
  FINER than the 12h chart the port runs on, and the offline engine neither
  resamples nor holds finer data. The port therefore models each
  `request.security(syminfo.tickerid, Tf, ta.cci(...))` as the CCI on the
  CHART's OWN timeframe -- the only resolution the engine can reproduce, the
  same modelling choice the batch's other `request.security` port
  (`SMDemarkReversalPoints_cbc975`) records. The impact is large and is NOT
  hidden: with one resolution substituted for five, `cci1..cci5` become the
  same series, so the five-way conjunction degenerates to a single
  `cci >= cciOverbought` / `cci <= cciOversold`, and the port fires on many
  more bars than the source (which needs five independent CCI readings to
  align). The requested resolutions remain recorded in `source_defaults`.
* md-vs-source CONFLICT (recorded, not silently resolved): the md's Strategy
  Description says "Green Background is 'Oversold', looking for 'Long'. Red
  Background is 'Overbought', looking for 'Short'." The APPENDED block does the
  OPPOSITE -- `cciOb` (overbought) enters LONG and `cciOs` (oversold) enters
  SHORT. Per rule 2 the source's own statements are authoritative, so the port
  reproduces the appended block as written (overbought -> long) and does NOT
  "fix" it to the author's described intent.

Other notes:

* `ta.cci(src, length)` is `(src - ta.sma(src, length)) / (0.015 * ta.dev(src,
  length))` with `ta.dev` the mean absolute deviation from that SMA. `pine_ta`
  has no `cci`, so the port implements exactly that formula locally.
* `not cciTfK_E or cciK >= threshold` uses Pine v5's proper boolean `not`, so
  the direct Python translation (`if not enabled: term = True`) is correct. The
  PINE_SEMANTICS.md 1.16 trap is about v2/v3 booleans compared numerically,
  which does not arise here.
* There is no `? -1 : 0` anywhere in this source, so 1.17 does not arise
  either.
* The five `plot()` calls, the two `hline()` calls, the two `bgcolor()` calls
  and the two `alertcondition()` calls are display- or alert-only and place no
  order: not reproduced.
* The source declares `indicator(...)`, so no `strategy()` properties exist and
  Pine's documented defaults apply: market orders of `fixed` size 1 contract,
  initial capital 1000000, commission 0%, pyramiding 0,
  process_orders_on_close=false.
* There is no exit call of any kind, so `source_reproduce_stops` is False and a
  position still open at the end of the window stays open.
* The md's argument table matches the source's input defaults exactly (hlc3,
  20, 100, -100, "15"/"30"/"60"/"120"/"240", five times true).
* The header's backtest window (2022-04-15 to 2022-05-14) is extraction
  metadata, not an `input.time` filter, so no data is trimmed. Its
  `basePeriod: 15m` is the host's intrabar granularity for filling 12h bars.
* Leverage, margin, liquidation, funding and the venue's contract-step rounding
  are not modelled (PINE_SEMANTICS.md 1.6 measures the rounding separately).
"""
import numpy as np
import pandas as pd
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


def _pine_cci(source, length):
    """Pine `ta.cci`: (src - sma(src, n)) / (0.015 * mean absolute deviation).

    `ta.dev(src, n)` is the mean absolute deviation of `source` from its own
    n-bar SMA, i.e. `sma(abs(source - sma(source, n)), n)`. A zero deviation
    gives na in Pine rather than an infinity.
    """
    source = pd.Series(source, dtype=float)
    length = int(length)
    basis = ta.pine_sma(source, length)
    deviation = ta.pine_sma((source - basis).abs(), length)
    with np.errstate(divide="ignore", invalid="ignore"):
        out = (source - basis) / (0.015 * deviation)
    return out.where(deviation != 0.0)


class SMCCIMTFObOs_f703ce(PinePortBase, IStrategy):
    source_id = "SM_f703ce8fc5a054cb"
    source_file = "CCI-MTF-ObOs.md"
    timeframe = "12h"
    can_short = True
    # Input defaults exactly as written in the source. The five `input.timeframe`
    # values are kept verbatim even though the port cannot honour them: they are
    # what the source declares, and dropping them would erase the blocker.
    source_defaults: dict = {
        "cciSrc": "hlc3",
        "cciLength": 20,
        "cciOverbought": 100,
        "cciOversold": -100,
        "cciTf1": "15",
        "cciTf2": "30",
        "cciTf3": "60",
        "cciTf4": "120",
        "cciTf5": "240",
        "cciTf1_E": True,
        "cciTf2_E": True,
        "cciTf3_E": True,
        "cciTf4_E": True,
        "cciTf5_E": True,
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
        "The file's indicator('CCI MTF Ob+Os') declaration means the "
        "strategy.entry pair at the bottom is an order block APPENDED by the "
        "converter site (fmz.com/strategy/363582 per the md's Detail link). The "
        "port reproduces the indicator PLUS that appended block, i.e. "
        "entry-only behaviour: if cciOb -> long, else if cciOs -> short.",
        "BLOCKER -- request.security is not modelled (PINE_SEMANTICS.md 2.1): "
        "the source reads five series through request.security(syminfo.tickerid, "
        "Tf, ta.cci(cciSrc, cciLength)) with Tf = '15' / '30' / '60' / '120' / "
        "'240' minutes, i.e. FINER than the 12h chart the port runs on. The "
        "offline engine neither resamples nor holds finer bars, so those series "
        "are NOT reproducible. The port models each call as the CCI on the "
        "chart's OWN timeframe -- the only resolution the engine can reproduce, "
        "the same modelling choice recorded by the batch's other "
        "request.security port (SMDemarkReversalPoints_cbc975).",
        "IMPACT of the above, stated rather than hidden: substituting one "
        "resolution for five makes cci1..cci5 the SAME series, so cciOb "
        "collapses to a single 'cci >= cciOverbought' and cciOs to a single "
        "'cci <= cciOversold'. The source requires five independent CCI "
        "readings across five timescales to agree, which is far rarer; this "
        "port therefore fires on many more bars than the source. The requested "
        "resolutions stay recorded in source_defaults so the gap is visible.",
        "md-vs-source CONFLICT (recorded, not silently resolved): the md's "
        "Strategy Description states 'Green Background is Oversold, looking for "
        "Long. Red Background is Overbought, looking for Short.' The APPENDED "
        "block does the opposite -- overbought enters LONG and oversold enters "
        "SHORT. Rule 2 makes the source authoritative, so the port reproduces "
        "the appended block as written and does NOT restore the described "
        "intent.",
        "ta.cci is not in pine_ta, so the port implements the documented "
        "formula locally: (src - sma(src, n)) / (0.015 * ta.dev(src, n)), where "
        "ta.dev is sma(abs(src - sma(src, n)), n). A zero deviation yields na, "
        "as Pine's division by zero does.",
        "The trailing `[1]` on the security call applies on every historical "
        "bar (barstate.isrealtime is false in a backtest), so the value used is "
        "lagged exactly one bar; the port reproduces that lag after the "
        "chart-timeframe substitution.",
        "`not cciTfK_E or cciK >= cciOverbought` is Pine v5's proper boolean "
        "not, so the literal Python translation is correct; the "
        "PINE_SEMANTICS.md 1.16 trap (v2/v3 booleans used numerically) does not "
        "arise.",
        "There is no `? -1 : 0` in this source, so the PINE_SEMANTICS.md 1.17 "
        "trap does not arise either.",
        "The five plot() calls, two hline() calls, two bgcolor() calls and two "
        "alertcondition() calls are display- or alert-only and place no order: "
        "not reproduced.",
        "There is NO exit of any kind in the source: no strategy.close, no "
        "strategy.exit, no stop/limit/trail, and no commented-out exit line. A "
        "position is only left by the opposite entry, which the engine models "
        "as a reversal. source_reproduce_stops is False accordingly.",
        "The source declares indicator(...), so no strategy() properties exist "
        "and Pine's documented defaults apply: default_qty_type fixed, "
        "default_qty_value 1, commission 0%, pyramiding 0, initial capital "
        "1000000 USD, process_orders_on_close false.",
        "The md's argument table matches the source's input defaults exactly "
        "(hlc3, 20, 100, -100, '15'/'30'/'60'/'120'/'240', five times true); "
        "the only md-vs-source conflict is the overbought/oversold direction "
        "noted above.",
        "The header's backtest window (2022-04-15 to 2022-05-14) is extraction "
        "metadata, not an input.time filter, so the port runs on whatever range "
        "the caller supplies; basePeriod: 15m is the host's intrabar fill "
        "granularity, not the strategy's period.",
        "Leverage, margin, liquidation, funding and the venue's contract-step "
        "rounding are not modelled (PINE_SEMANTICS.md 1.6).",
    ]

    def pine_indicators(self, dataframe, params):
        cci_source = ta.pine_source(dataframe, str(params["cciSrc"]))
        cci_length = int(params["cciLength"])
        overbought = float(params["cciOverbought"])
        oversold = float(params["cciOversold"])

        # cci1..cci5 = Fsec(syminfo.tickerid, cciTf1..cciTf5,
        #                   ta.cci(cciSrc, cciLength))
        #
        # request.security is not modelled (PINE_SEMANTICS.md 2.1) and the five
        # requested resolutions are all FINER than the chart's, so the port
        # reads every one of them on the chart's own timeframe and the five
        # series coincide (see the BLOCKER/IMPACT fidelity notes). The trailing
        # [1] is the source's own historical-bar lag.
        cci = _pine_cci(cci_source, cci_length).shift(1)

        # cciK_Ob = not cciTfK_E or cciK >= cciOverbought  (and the Os mirror)
        def _ob(enabled):
            if not bool(enabled):
                return pd.Series(True, index=dataframe.index)
            return (cci >= overbought).fillna(False)

        def _os(enabled):
            if not bool(enabled):
                return pd.Series(True, index=dataframe.index)
            return (cci <= oversold).fillna(False)

        # cciOb / cciOs = conjunction over the five enabled resolutions.
        cci_ob = (
            _ob(params["cciTf1_E"])
            & _ob(params["cciTf2_E"])
            & _ob(params["cciTf3_E"])
            & _ob(params["cciTf4_E"])
            & _ob(params["cciTf5_E"])
        )
        cci_os = (
            _os(params["cciTf1_E"])
            & _os(params["cciTf2_E"])
            & _os(params["cciTf3_E"])
            & _os(params["cciTf4_E"])
            & _os(params["cciTf5_E"])
        )

        dataframe["pine_cci"] = cci
        dataframe["pine_cci_ob"] = cci_ob.astype(bool)
        dataframe["pine_cci_os"] = cci_os.astype(bool)
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "cci_ob": dataframe["pine_cci_ob"].to_numpy(),
            "cci_os": dataframe["pine_cci_os"].to_numpy(),
        }

    def pine_script(self, broker, i, ctx):
        # if cciOb
        #     strategy.entry("Enter Long", strategy.long)
        # else if cciOs
        #     strategy.entry("Enter Short", strategy.short)
        if ctx["cci_ob"][i]:
            broker.entry("Enter Long", "long")
        elif ctx["cci_os"][i]:
            broker.entry("Enter Short", "short")
