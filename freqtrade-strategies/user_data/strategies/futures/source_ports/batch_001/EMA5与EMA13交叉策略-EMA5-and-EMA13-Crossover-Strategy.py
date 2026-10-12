"""Port of sources/SM_aae7257dfb9a9050.pine
(batch_001/EMA5与EMA13交叉策略-EMA5-and-EMA13-Crossover-Strategy.md).

Pine v5, FUTURES_BINANCE BTC_USDT, 2d chart. Despite the title and the markdown
description ("EMA5 crosses above EMA13 -> long"), the SOURCE trades one
direction only, and on a level comparison rather than on the cross:

    expo = ta.ema(close, ema1)          // 5
    ma   = ta.ema(close, ema2)          // 13
    longCondition  = ta.crossover(expo, ma)     // computed, never used
    shortCondition = ta.crossunder(expo, ma)    // computed, never used

    if testPeriod()
        strategy.entry('Short', strategy.short, when = expo < ma)
    strategy.close('Short', expo > ma, comment = 'SL hit')

`testPeriod() => true` is a literal `true`, so the guard never blocks the entry;
the entry is `expo < ma`, evaluated on every bar, not `crossunder(expo, ma)`.
The source's own `//strategy.entry('Long', strategy.long, when=longCondition)`
is commented out, so `can_short` is True and there is NO long entry -- the
markdown summary is wrong about this and the source wins (iron rule 2).

The `/*backtest` header declares `period: 2d`, so `timeframe` is "2d"; its
`basePeriod: 1d` is the FMZ backtester's fill granularity, not the period.

`strategy('5-13 EMA by Naimesh ver04', overlay=true)` declares nothing else, so
Pine's documented defaults apply: `default_qty_type = strategy.fixed`,
`default_qty_value = 1`, initial capital 1000000, commission 0%,
`pyramiding = 0`, `process_orders_on_close = false`. The `qty = input(1, 'Buy
quantity')` input is never read by any order call, so it does not size
anything: the order size stays Pine's `default_qty_value` of 1.

FIDELITY (see `source_fidelity_notes` for the full list):

* `request.security` is not used, but the port is tier 5 because the 2d
  timeframe has no local candles, so `verify_chain` can only report
  `skipped_no_local_data`.
* The full backtest-window machinery (`testStartYear`..`testStopDay`,
  `testPeriodBackground`, `testPeriodBackgroundColor`, `fill`, `plot`) is
  display-only in effect: `testPeriod()` returns the literal `true`, and the
  background colour uses `time >= testPeriodStart and time <= testPeriodStop`.
  It places no order and no data restriction, so it is not reproduced.
* `ta.ema`'s seeding rule is unpublished and the port inherits the shared
  layer's "first non-na value" seed (PINE_SEMANTICS.md 3.1); with both lengths
  short (5 and 13) the warmup difference is confined to the first bars.
* No stop/limit/trail exit exists -- the only exit is the market
  `strategy.close` -- so `source_reproduce_stops` is False.
* Leverage, margin, liquidation and funding are not modelled, and neither is
  the venue's contract-step rounding (PINE_SEMANTICS.md 1.6).
"""
from __future__ import annotations

from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


class SMEma5Ema13Crossover_aae725(PinePortBase, IStrategy):
    source_id = "SM_aae7257dfb9a9050"
    source_file = "EMA5与EMA13交叉策略-EMA5-and-EMA13-Crossover-Strategy.md"
    timeframe = "2d"
    # The only entry is `strategy.entry('Short', strategy.short, ...)`.
    can_short = True
    source_defaults: dict = {
        "qty": 1,
        "testStartYear": 2021,
        "testStartMonth": 1,
        "testStartDay": 1,
        "testStartHour": 0,
        "testStartMin": 0,
        "testStopYear": 2099,
        "testStopMonth": 1,
        "testStopDay": 30,
        "testPeriodBackground": True,
        "ema1": 5,
        "ema2": 13,
    }
    # strategy('5-13 EMA by Naimesh ver04', overlay=true) only: everything else
    # is Pine's documented default.
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    source_reproduce_stops = False
    source_fidelity_notes = [
        "The markdown description says EMA5/EMA13 cross generates long AND "
        "short signals; the source's only live entry is "
        "`strategy.entry('Short', strategy.short, when = expo < ma)` and the "
        "long entry is commented out. The source wins: no long entry, and "
        "can_short is True.",
        "The entry condition is `expo < ma`, NOT `crossunder(expo, ma)`: "
        "`shortCondition` is computed and never read.",
        "`if testPeriod()` guards the entry, and `testPeriod() => true` is a "
        "literal true, so the guard never blocks it.",
        "`strategy.close('Short', expo > ma, ...)`: the second positional "
        "argument of `strategy.close` is `when`, so the exit is `expo > ma`; "
        "the comment 'SL hit' is only a comment -- no stop order exists.",
        "`qty = input(1, 'Buy quantity')` is declared and never read by an "
        "order call; the order size is Pine's default_qty_value of 1.",
        "The backtest-window inputs (testStart*/testStop*) and the background "
        "colour are display/plot-only and place no orders; not reproduced.",
        "No stop/limit/trail exit exists, so source_reproduce_stops is False.",
        "`ta.ema` seeding (PINE_SEMANTICS.md 3.1) is the shared layer's "
        "modelled choice; no other indicator is used.",
        "The 2d timeframe has no local candles, so the chain comparison is "
        "expected to be reported as skipped_no_local_data rather than run.",
    ]

    def pine_indicators(self, dataframe, params):
        close = dataframe["close"].astype(float)
        # expo = ta.ema(close, ema1)   ma = ta.ema(close, ema2)
        expo = ta.pine_ema(close, int(params["ema1"]))
        ma = ta.pine_ema(close, int(params["ema2"]))
        # `expo < ma` / `expo > ma`: a na comparison is false in Pine, and the
        # same is true of a pandas comparison against NaN.
        dataframe["pine_short_entry"] = expo < ma
        dataframe["pine_short_exit"] = expo > ma
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "short_entry": dataframe["pine_short_entry"].to_numpy(),
            "short_exit": dataframe["pine_short_exit"].to_numpy(),
        }

    def pine_script(self, broker, i, ctx):
        # if testPeriod()
        #     strategy.entry('Short', strategy.short, when=expo<ma)
        if ctx["short_entry"][i]:
            broker.entry("Short", "short")
        # strategy.close("Short", expo>ma, comment= 'SL hit')
        if ctx["short_exit"][i]:
            broker.close("Short")
