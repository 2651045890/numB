"""Port of sources/SM_4f0e3ccbdf436170.pine (batch_001/Low-finder.md).

Pine v4. The file is RafaelZioni's "Low finder" INDICATOR -- `study(title =
"Low finder ", overlay=true)` -- an oscillator built from an RSI and an EMA of
that RSI:

    p     = close
    vrsi  = rsi(p, length)
    pp    = ema(vrsi, length)
    d     = (vrsi - pp) * 5
    cc    = (vrsi + d + pp) / 2      # = 3*vrsi - 2*pp
    bb    = (vrsi - d + pp) / 2      # = 3*pp   - 2*vrsi
    low1  = crossover(cc, 0)
    high1 = crossunder(bb, 90)

A converter appended an order block at the end of the file. `study()` cannot
host `strategy.entry` in Pine v4, so the trading behaviour IS that block:

    if low1
       strategy.entry("buy", strategy.long)
    else if  high1
        strategy.entry("sell", strategy.short)

There is NO exit anywhere in the file -- neither a live call nor a commented-out
one -- so a position is only ever replaced by an opposite entry, and one still
open at the end of the window stays open (`source_reproduce_stops = False`).

THE TRAP IN THIS FILE: `Highdetector = input(false)` gates ONLY the `plotshape`
that draws the "High" label --

    plotshape(Highdetector and high1, title="High", ...)

-- it does NOT appear in the appended order block, which tests `high1` bare. So
the default `Highdetector=false` hides the arrow and still lets the SHORT entry
fire. A port that reproduced `Highdetector and high1` in the entry condition
would silently disable every short in the source. The input is kept (and
defaults to false, as declared) but is not read by any order.

FIDELITY:

* The appended block is `if low1 ... else if high1`, and `low1`/`high1` are
  mutually exclusive in practice but not by construction; the port keeps the
  `if` / `elif` shape and the source's order, which is also the engine's fill
  priority order (rule 4).
* Order ids are the source's own: `buy` and `sell`.
* No `qty` is passed anywhere, so the engine sizes both entries from
  `default_qty_type` / `default_qty_value`.
* No `strategy()` call exists in the file -- it declares a `study()` -- so every
  trade property is Pine's own documented default: `default_qty_type` fixed,
  `default_qty_value` 1 CONTRACT (not 1 unit of currency and not 100% of
  equity), `initial_capital` 1000000, commission 0%, `pyramiding` 0,
  `process_orders_on_close` false. That is what the absent declaration means,
  and it is preserved rather than guessed.
* `rsi` is pine_ta.pine_rsi (Wilder rma of the up/down moves; 100 when there
  were no losses -- PINE_SEMANTICS.md section 3.3) and `ema` is
  pine_ta.pine_ema, which seeds on the first non-na observation
  (PINE_SEMANTICS.md section 3.1 -- Pine does not publish its seed rule).
* na handling: `vrsi` is na until the RSI's Wilder seed is complete, `pp` is
  na until its own first observation, and Pine compares na as false, so
  `low1` / `high1` cannot fire before both are defined. The pandas comparisons
  and `pine_crossover` / `pine_crossunder` behave the same way (both
  `fillna(False)` their na comparisons).
* `p = close` is an alias, `plotshape` / `alertcondition` / the `study()` title
  are display or alert only, and nothing else in the file reaches an order.
* The `/*backtest` header declares `period: 4h` on Binance BTC_USDT, so
  `timeframe` is "4h"; its `basePeriod: 15m` is the FMZ backtester's fill
  granularity for those 4h bars, not the strategy's period. The exchange is a
  SPOT pair, but the appended block places a short, so `can_short` is True --
  the block is the authority on what trades.
* Leverage, margin, liquidation, funding and the venue's contract-step
  rounding are not modelled.
"""
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


class SMLowFinder_4f0e3c(PinePortBase, IStrategy):
    source_id = "SM_4f0e3ccbdf436170"
    source_file = "Low-finder.md"
    timeframe = "4h"
    can_short = True
    source_defaults: dict = {"length": 21, "Highdetector": False}
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
        "Converter-appended source: the file declares an INDICATOR (`study("
        "\"Low finder \", overlay=true)`) and a tool appended the block `if "
        "low1 / strategy.entry(\"buy\", strategy.long) else if high1 / "
        "strategy.entry(\"sell\", strategy.short)`. Pine v4 cannot call "
        "strategy.entry from a study, so the port reproduces exactly what the "
        "appended block does: entries only.",
        "`Highdetector = input(false)` gates ONLY the `plotshape(Highdetector "
        "and high1, ...)` label; the appended block tests `high1` bare. The "
        "input is therefore declared with its default but is not read by any "
        "order, so shorts DO fire with the default false. Reproducing "
        "`Highdetector and high1` in the entry would have silently disabled "
        "every short.",
        "NO exit exists in the source -- there is not even a commented-out "
        "one. A position is closed only by an opposite entry reversing it, so "
        "source_reproduce_stops is False and a position open at the end of the "
        "window stays open.",
        "No `strategy()` call exists (the file is a study), so trade properties "
        "are Pine's documented defaults: fixed sizing, qty 1, initial capital "
        "1000000, commission 0%, pyramiding 0, process_orders_on_close=false.",
        "Entries pass no `qty`, so the engine sizes them from "
        "default_qty_type / default_qty_value.",
        "`rsi` is pine_ta.pine_rsi (Wilder rma of up/down moves) and `ema` is "
        "pine_ta.pine_ema, which seeds on the first non-na value; Pine does not "
        "publish its EMA seed rule (PINE_SEMANTICS.md section 3.1), so the "
        "warm-up of `pp` is a modelling choice that converges thereafter.",
        "`cc` and `bb` are algebraically 3*vrsi-2*pp and 3*pp-2*vrsi; the port "
        "keeps the source's own `d` intermediate instead of simplifying, so "
        "the arithmetic matches term for term.",
        "plotshape / alertcondition / the study() title and `overlay` are "
        "display or alert only and are not reproduced.",
        "The /*backtest header says `period: 4h` (Binance BTC_USDT spot, "
        "`basePeriod: 15m` is the FMZ fill granularity); the appended block "
        "places a short, so can_short is True.",
        "md-vs-source inconsistency (provenance only, no behavioural effect): "
        "the md's Author field says Zer3192 while the source's own header "
        "comment is `// © RafaelZioni`. The code in the two is identical.",
        "Leverage, margin, liquidation and funding are not modelled; the "
        "venue's contract-step rounding is not modelled either (the chain "
        "verifier measures that separately).",
    ]

    def pine_indicators(self, dataframe, params):
        length = int(params["length"])
        close = dataframe["close"]
        # vrsi = rsi(p, length)
        vrsi = ta.pine_rsi(close, length)
        # pp = ema(vrsi, length)
        pp = ta.pine_ema(vrsi, length)
        # d = (vrsi - pp) * 5
        d = (vrsi - pp) * 5
        # cc = (vrsi + d + pp) / 2
        cc = (vrsi + d + pp) / 2
        # bb = (vrsi - d + pp) / 2
        bb = (vrsi - d + pp) / 2
        dataframe["pine_vrsi"] = vrsi
        dataframe["pine_pp"] = pp
        dataframe["pine_cc"] = cc
        dataframe["pine_bb"] = bb
        # low1 = crossover(cc, 0)
        dataframe["pine_low1"] = ta.pine_crossover(cc, 0)
        # high1 = crossunder(bb, 90)
        dataframe["pine_high1"] = ta.pine_crossunder(bb, 90)
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "low1": dataframe["pine_low1"].to_numpy(),
            "high1": dataframe["pine_high1"].to_numpy(),
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
