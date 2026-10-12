"""Port of sources/SM_6f0ee03cfdaac232.pine (batch_001/EMA-TREND-CLOUD.md).

Pine v5. The file declares `indicator(...)`, NOT `strategy(...)`: the
`if Bull / else if Bear` block at the bottom is an order block APPENDED to the
indicator by the converter site that published it (the md's Detail link names
fmz.com/strategy/364037). Pine v5 does not compile `strategy.entry` inside
`indicator()`, so the "original strategy" is the indicator PLUS that appended
block, and the trading behaviour it defines is entry-only.

    fastEMA = ta.ema(close, fastLen)
    slowEMA = ta.ema(close, slowLen)
    Bull    = ta.crossover(fastEMA, slowEMA)
    Bear    = ta.crossunder(fastEMA, slowEMA)

    if Bull
        strategy.entry("Enter Long", strategy.long)
    else if Bear
        strategy.entry("Enter Short", strategy.short)

The `else if` is kept as `elif` to mirror Pine's short-circuit (the two
conditions are mutually exclusive anyway, so no bar can place two orders).

There is NO exit of any kind in the source -- no `strategy.close`, no
`strategy.exit`, not even a commented-out one. A position is therefore only
ever left by the opposite entry, which the engine models as a reversal.
`pyramiding` keeps Pine's default of 0, so a repeated signal while already
positioned that way is ignored.

FIDELITY:

* Both entry conditions are plain booleans (`ta.crossover` / `ta.crossunder`
  return bool), so nothing here depends on Pine's integer truthiness and there
  is no `? -1 : 0` form in the source.
* `ta.ema` is seeded with the first non-na observation (pine_ta's documented
  choice); TradingView does not publish its seeding rule, so the early EMA
  values -- and therefore the first cross -- are a MODELLED result
  (PINE_SEMANTICS.md 3.1).
* The `alert(...)` calls on Bull/Bear are notifications, not orders
  (PINE_SEMANTICS.md, section 2 item 7); they are dropped.
* The two `plotshape(...)` calls, the two `plot(...)` calls, the `fill(...)`
  cloud, the title and `overlay` are display-only and carry no trade meaning;
  they are dropped.
* The `/*backtest` header's `args: [["v_input_1",10],["v_input_2",18]]` records
  the argument values the host RAN its published backtest with (fast 10, slow
  18), while the source's `input()` defaults -- and the md's own Strategy
  Arguments table -- declare 9 and 20. The port carries the declared defaults
  9/20 (they are what `input()` says, and the brief defines `source_defaults` as
  the `input()` defaults); the host's override is recorded here rather than
  applied, and `source_parameters` can supply 10/18 if that run is what a
  comparison needs.
* The header's `period: 30m` is the strategy's timeframe; `basePeriod: 15m` is
  the host's intrabar granularity for filling those 30m bars, not a second
  timeframe. The header's backtest window (2022-04-17 to 2022-05-16) is
  extraction metadata, not an `input.time` filter, so no data is trimmed.
* The source declares `indicator(...)`, not `strategy(...)`, so it carries no
  strategy() properties; Pine's documented defaults are what the `source_*`
  attributes record (fixed size 1, 0% commission, pyramiding 0, initial capital
  1000000). On TradingView `strategy.entry` inside an indicator does not
  compile; the host named by the source's header and the md's Detail link is
  what ran the appended block, and that platform's Pine dialect -- not
  TradingView -- is the behaviour this port reproduces.
* No stop, limit or trail exit exists, so `source_reproduce_stops` is False.
* Leverage, margin, liquidation, funding and the venue's contract-step rounding
  are not modelled (PINE_SEMANTICS.md 1.6, 2.4).
"""
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


class SMEmaTrendCloud_6f0ee0(PinePortBase, IStrategy):
    source_id = "SM_6f0ee03cfdaac232"
    source_file = "EMA-TREND-CLOUD.md"
    timeframe = "30m"
    can_short = True
    # As written in the source: fastLen = input(defval=9), slowLen = input(defval=20).
    # The header's `args` override (10/18) is NOT applied; see the docstring.
    source_defaults: dict = {
        "fastLen": 9,
        "slowLen": 20,
        "useTextLabels": True,
    }
    # indicator(...), not strategy(...): Pine's documented defaults apply.
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    # No strategy.close / strategy.exit / stop / limit / trail anywhere.
    source_reproduce_stops = False
    source_mintick = 0.1
    source_fidelity_notes = [
        "The file declares indicator(...), not strategy(...); the two "
        "strategy.entry calls at the bottom are an order block appended to the "
        "indicator by the converter site that published it (the md's Detail link "
        "names fmz.com/strategy/364037). Pine v5 does not compile strategy.entry "
        "inside indicator(), so the original strategy is the indicator plus that "
        "appended block, and its trading behaviour is entry-only.",
        "The source has no exit of any kind: no strategy.close, no strategy.exit, "
        "no stop or limit order, and no commented-out exit line. A position is "
        "only ever left by the opposite entry, which the engine models as a "
        "reverse fill. source_reproduce_stops is False accordingly.",
        "The two conditions live in one `if / else if` chain in source order. They "
        "are mutually exclusive (a single bar cannot be both a crossover and a "
        "crossunder), so the ordering is not load-bearing for the fills -- only "
        "for faithfulness.",
        "ta.ema is seeded with the first non-na observation, pine_ta's documented "
        "choice; TradingView does not publish its seeding rule, so the early EMA "
        "values -- and therefore which bar first crosses -- are a modelled result "
        "rather than certified equivalence (PINE_SEMANTICS.md 3.1).",
        "Both appended conditions are plain booleans, so there is no integer "
        "truthiness question here and no `? -1 : 0` form in the source.",
        "The source declares indicator(...), not strategy(...), so no strategy() "
        "properties exist and Pine's documented defaults are used: "
        "default_qty_type fixed, default_qty_value 1, commission 0%, pyramiding "
        "0, initial capital 1000000 USD.",
        "The backtest header carries `args: [[\"v_input_1\",10],[\"v_input_2\",18]]` "
        "-- the values the host ran its published backtest with (fast 10, slow 18) "
        "-- while the source's own input() defaults (and the md's Strategy "
        "Arguments table) declare 9 and 20. The port carries the declared defaults "
        "9/20 and records the host override here rather than applying it; "
        "`source_parameters` can supply 10/18 when that run is the comparison "
        "target. This is the one place where the md and the source disagree.",
        "The alert(...) calls on Bull/Bear are notifications, not orders, and the "
        "plotshape/plot/fill/title/overlay calls are display-only; all are dropped.",
        "The header's basePeriod: 15m is the host's intrabar granularity for "
        "filling 30m bars, not the strategy's period; the engine evaluates at bar "
        "close and fills at the next open, so intrabar path differences are not "
        "modelled.",
        "The backtest window in the header (2022-04-17 to 2022-05-16) is extraction "
        "metadata, not an input.time filter, so the port runs on whatever range the "
        "caller supplies.",
        "Leverage, margin, liquidation, funding and the venue's contract-step "
        "rounding are not modelled; the chain verifier measures the rounding "
        "separately (PINE_SEMANTICS.md 1.6).",
    ]

    def pine_indicators(self, dataframe, params):
        close = dataframe["close"]
        # fastEMA = ta.ema(close, fastLen)
        # slowEMA = ta.ema(close, slowLen)
        fast_ema = ta.pine_ema(close, int(params["fastLen"]))
        slow_ema = ta.pine_ema(close, int(params["slowLen"]))
        dataframe["pine_fast_ema"] = fast_ema
        dataframe["pine_slow_ema"] = slow_ema
        # Bull = ta.crossover(fastEMA, slowEMA)
        # Bear = ta.crossunder(fastEMA, slowEMA)
        dataframe["pine_bull"] = ta.pine_crossover(fast_ema, slow_ema)
        dataframe["pine_bear"] = ta.pine_crossunder(fast_ema, slow_ema)
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "bull": dataframe["pine_bull"].to_numpy(),
            "bear": dataframe["pine_bear"].to_numpy(),
        }

    def pine_script(self, broker, i, ctx):
        # if Bull
        #     strategy.entry("Enter Long", strategy.long)
        # else if Bear
        #     strategy.entry("Enter Short", strategy.short)
        if ctx["bull"][i]:
            broker.entry("Enter Long", "long")
        elif ctx["bear"][i]:
            broker.entry("Enter Short", "short")
