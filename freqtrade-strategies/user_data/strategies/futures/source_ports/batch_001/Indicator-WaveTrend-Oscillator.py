"""Port of sources/SM_fe3585f9c7599f2f.pine
(batch_001/Indicator-WaveTrend-Oscillator.md).

Pine v3 (the file carries no `//@version`, and `study(title=..., shorttitle=...)`
is the v3 form; the `ta.` namespace inside it is v5 syntax, see FIDELITY 1).
LazyBear's WaveTrend oscillator, with the converter station's appended order
block at the end:

    n1 = input(10, "Channel Length")
    n2 = input(21, "Average Length")
    obLevel1 = input(60, ...)   obLevel2 = input(53, ...)
    osLevel1 = input(-60, ...)  osLevel2 = input(-53, ...)
    ap  = hlc3
    esa = ta.ema(ap, n1)
    d   = ta.ema(math.abs(ap - esa), n1)
    ci  = (ap - esa) / (0.015 * d)
    tci = ta.ema(ci, n2)
    wt1 = tci
    wt2 = ta.sma(wt1, 4)

    if wt1 > obLevel1
        strategy.entry("entry short", strategy.short)
    else if wt1 < osLevel1
        strategy.entry("entry long", strategy.long)

`study()` cannot host `strategy.entry`, so the trading behaviour IS the appended
block: a SHORT when the oscillator is above the overbought level, a LONG when it
is below the oversold level, and nothing else. There is NO exit anywhere in the
file -- no `strategy.close`, `close_all` or `exit`, live or commented out -- so a
position is closed only by the opposite entry reversing it, and one still open at
the end of the window stays open (`source_reproduce_stops` is False).

FIDELITY:

1. `study(...)` is v3 and `ta.ema(...)` is v5/v6 spellings side by side. The two
   are the same functions as v3's bare `ema` / `sma` / `abs`, and no
   v3-vs-v5 semantic difference applies to any call this source uses, so the port
   reproduces what the calls mean rather than a namespace the compiler would
   have to reconcile.
2. `hlc3` is Pine's built-in `(high + low + close) / 3`, resolved through
   pine_ta.pine_source, not re-derived.
3. `math.abs` is Pine's absolute value (pine_ta.pine_abs); `0.015` is a literal
   in the source and stays a literal.
4. `wt2 = ta.sma(wt1, 4)` is computed because the source computes it (it is
   plotted as the signal line), but NOTHING in the appended block reads it: the
   entries test `wt1` against the two levels only. It is kept as a column so the
   source's arithmetic is complete, and it gates no order.
5. `obLevel2` / `osLevel2` (-53) appear only in `plot(...)` calls. They are
   declared in `source_defaults` (they are the source's inputs) and place no
   order.
6. MD/SOURCE MISMATCH (signal shape): the md's Strategy Description says "When
   the oscillator is above the overbought band (red lines) and crosses down the
   signal (dotted line), it is usually a good SELL signal. Similarly, when the
   oscillator crosses above the signal when below the Oversold band ... a good
   BUY signal." That describes a CROSS of wt1 against wt2. The executable
   appended block has no cross in it: it is a bare level test (`wt1 > obLevel1`,
   `wt1 < osLevel1`). The source is followed; no cross is invented.
7. MD/SOURCE MISMATCH (arguments): the `/*backtest` header beside the source
   carries `args: [["v_input_3", 40]]`, i.e. the recorded FMZ backtest ran
   `obLevel1 = 40` instead of the declared 60. The port keeps the DECLARED
   default (60), the same way it does not adopt the header's start:/end: window;
   setting `source_defaults["obLevel1"]` to 40 is the entire change if the other
   reading is wanted. The md's own argument table lists 60, agreeing with the
   declaration.
8. `ci = (ap - esa) / (0.015 * d)` divides by `d`, which is 0 on a bar where
   `ap == esa` exactly; Pine yields na/inf there and so does this division. It is
   kept as written rather than guarded, which is the source's own behaviour.
9. No `strategy()` call exists in the file (the declaration is a `study`), so
   every trade property is Pine's documented default: `default_qty_type` fixed,
   `default_qty_value` 1 CONTRACT, `initial_capital` 1000000, commission 0%,
   `pyramiding` 0, `process_orders_on_close` false. Notably NOT a percentage of
   equity, and NOT the 10000-cash sizing an eye might read off the md's table.
10. `ta.ema` uses pine_ta's modelled seeding (first non-na observation; na does
    not advance the recursion), which PINE_SEMANTICS.md 3.1 records as an
    unresolved parity risk: this port can evaluate from the first bars while the
    original platform's series may be na until the window fills. No formula,
    length or lookback is changed here.
11. `ta.sma` returns na until its window is full and propagates na (section 3.2);
    `wt2` is therefore na for the first three bars. It gates no order.
12. The `/*backtest` header declares `period: 1h` on Futures_Binance BTC_USDT,
    hence `timeframe = "1h"`; its `basePeriod: 15m` is the FMZ backtester's
    intrabar fill granularity, not the strategy's period.
13. `plot(...)` calls are display-only and are not reproduced.
14. Leverage, margin, liquidation, funding and the venue's contract-step
    rounding are not modelled; the chain verifier measures the step rounding
    separately instead of treating it as a signal difference.
"""
import pandas as pd

from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


class SMIndicatorWaveTrendOscillator_fe3585(PinePortBase, IStrategy):
    source_id = "SM_fe3585f9c7599f2f"
    source_file = "Indicator-WaveTrend-Oscillator.md"
    timeframe = "1h"
    # The appended block's second arm is `strategy.entry("entry long", ...)`, so
    # the source trades both directions.
    can_short = True
    # Every input() of the source, exactly as declared.
    source_defaults: dict = {
        # input(10, "Channel Length")
        "n1": 10,
        # input(21, "Average Length")
        "n2": 21,
        # input(60, "Over Bought Level 1")  -- the header's args overrode this to
        # 40 for the recorded FMZ run; the declared default is kept (note 7).
        "obLevel1": 60,
        # input(53, "Over Bought Level 2")  -- plot only.
        "obLevel2": 53,
        # input(-60, "Over Sold Level 1")
        "osLevel1": -60,
        # input(-53, "Over Sold Level 2")   -- plot only.
        "osLevel2": -53,
    }
    # `study(...)` is not a strategy declaration and no strategy() call exists in
    # the file at all, so Pine's documented defaults apply. They are stated
    # explicitly because the port layer requires them rather than inheriting
    # Freqtrade's.
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    # No exit call of any kind exists in the source.
    source_reproduce_stops = False
    source_fidelity_notes = [
        "Converter-appended source: the file declares an INDICATOR "
        "(`study(title=\"WaveTrend [LazyBear]\", shorttitle=\"WT_LB\")`) and the "
        "tool appended the block `if wt1 > obLevel1 / strategy.entry(\"entry "
        "short\", strategy.short) else if wt1 < osLevel1 / strategy.entry("
        "\"entry long\", strategy.long)`. Pine cannot call strategy.entry from a "
        "study, so the original strategy IS the indicator plus that block, and "
        "the port reproduces the block's actual behaviour.",
        "NO exit exists: no strategy.close / close_all / exit appears anywhere in "
        "the file, live or commented out. source_reproduce_stops is False; a "
        "position is closed only by the opposite entry reversing it and one open "
        "at the end of the window stays open.",
        "MD/SOURCE MISMATCH (signal shape): the md's description says the signal "
        "is wt1 CROSSING DOWN the signal line above the overbought band (and "
        "crossing above it below the oversold band). The executable block has no "
        "cross in it -- it is a bare level test on wt1 (`wt1 > obLevel1` / "
        "`wt1 < osLevel1`). The source is followed; no cross is added.",
        "MD/SOURCE MISMATCH (arguments): the /*backtest header carries "
        "args: [[\"v_input_3\", 40]], so the recorded FMZ run used obLevel1 = 40. "
        "The port keeps the declared default 60 and does not adopt backtest-run "
        "state, just as it does not adopt the header's start:/end: window. "
        "Setting source_defaults['obLevel1'] to 40 is the entire change.",
        "The header's `period: 1h` IS taken from the /*backtest header -- it is "
        "the only statement of the chart's timeframe in the pair and a port must "
        "declare one. basePeriod: 15m is the FMZ backtester's intrabar fill "
        "granularity, not the strategy's period.",
        "wt2 = ta.sma(wt1, 4) is computed and kept as a column (the source "
        "computes it and plots it), but the appended block never reads it: both "
        "entries test wt1 alone. It gates no order.",
        "obLevel2 / osLevel2 (-53) are read only by plot(...) calls; they are "
        "declared in source_defaults because they are the source's inputs, and "
        "they place no order.",
        "`study(...)` is a v3 declaration while `ta.ema` / `ta.sma` are the v5 "
        "namespace spellings; they are the same functions and no v3-vs-v5 "
        "difference applies to any call this source uses.",
        "ci = (ap - esa) / (0.015 * d) divides by d, which is 0 when ap == esa; "
        "Pine yields na/inf and so does this division. Kept as written, not "
        "guarded.",
        "No strategy() declaration exists, so trade properties are Pine's "
        "documented defaults: fixed sizing, qty 1 contract, initial capital "
        "1000000, commission 0%, pyramiding 0, process_orders_on_close=false.",
        "ta.ema seeding is the modelled choice of PINE_SEMANTICS.md 3.1 (first "
        "non-na observation), so this port may evaluate earlier than the original "
        "platform, whose ta.ema is believed to be na until the window is full. "
        "Early-bar trades are a known, un-eliminated equivalence risk.",
        "plot(...) calls are display-only and are not reproduced.",
        "Leverage, margin, liquidation and funding are not modelled; the venue's "
        "contract-step rounding is not modelled either (the chain verifier "
        "measures that separately).",
    ]

    def pine_indicators(self, dataframe: pd.DataFrame, params: dict) -> pd.DataFrame:
        n1 = int(params["n1"])
        n2 = int(params["n2"])
        # ap = hlc3 -- Pine's built-in source, not re-derived.
        ap = ta.pine_source(dataframe, "hlc3")
        # esa = ta.ema(ap, n1)
        esa = ta.pine_ema(ap, n1)
        # d = ta.ema(math.abs(ap - esa), n1)
        d = ta.pine_ema(ta.pine_abs(ap - esa), n1)
        # ci = (ap - esa) / (0.015 * d)  -- 0.015 is a source literal.
        ci = (ap - esa) / (0.015 * d)
        # tci = ta.ema(ci, n2)
        tci = ta.pine_ema(ci, n2)
        # wt1 = tci ; wt2 = ta.sma(wt1, 4)
        wt1 = tci
        wt2 = ta.pine_sma(wt1, 4)

        dataframe["pine_wt1"] = wt1
        dataframe["pine_wt2"] = wt2
        # if wt1 > obLevel1      -> strategy.entry("entry short", ...)
        dataframe["pine_short_condition"] = wt1 > float(params["obLevel1"])
        # else if wt1 < osLevel1 -> strategy.entry("entry long", ...)
        dataframe["pine_long_condition"] = wt1 < float(params["osLevel1"])
        return dataframe

    def pine_context(self, dataframe: pd.DataFrame, params: dict) -> dict:
        return {
            "short_condition": dataframe["pine_short_condition"].to_numpy(dtype=bool),
            "long_condition": dataframe["pine_long_condition"].to_numpy(dtype=bool),
        }

    def pine_script(self, broker, i: int, ctx: dict) -> None:
        # if wt1 > obLevel1
        #     strategy.entry("entry short", strategy.short)
        # else if wt1 < osLevel1
        #     strategy.entry("entry long", strategy.long)
        #
        # The source order (short arm first) is the fill priority order and is
        # preserved; the arms are an if/else if, so at most one fires per bar.
        if ctx["short_condition"][i]:
            broker.entry("entry short", "short")
        elif ctx["long_condition"][i]:
            broker.entry("entry long", "long")
