"""Port of sources/SM_821e5ba9df6ebf39.pine
(batch_001/EMA-Trading-Strategy.md).

Pine v5 (`//@version=5`,
`strategy("EMA Strat", overlay=true, margin_long=100, margin_short=100)`).
One EMA, one long entry and one flat:

    emaInput = input(21, "Length")
    ema = ta.ema(close, emaInput)

    p = 0
    start = false
    yearInput = input(2000, "Year")
    if (time >= timestamp(2000,01,01,01,01))
        start := true

    if (close > ema and start == true)
        p += 1
        strategy.entry("Long", strategy.long, comment = "Entry")

    above = close[1] > ema[1]
    if (above)
        p += 1

    below = close < ema
    if (below)
        p := 0
        strategy.close("Long", comment = "Flat")

`p` is a NON-var int that resets to 0 every bar, is incremented by two
independent `if`s, and is read by nothing except `plot(p)`. It places no order
and is not reproduced; the source's commented-out `goLong = p[1] == 0 and
p == 1` / `flatten = p == 0` block, which would have used it, is dead code.

`yearInput` is also inert: the `if` beneath it compares against the LITERAL
`timestamp(2000,01,01,01,01)`, not against `yearInput`. Every bar of any
plausible dataset is at or after 2000-01-01 01:01, so `start` is true on every
bar; the port evaluates the literal comparison anyway rather than assuming it.

`strategy()` states `margin_long=100, margin_short=100`. Pine's `margin_*` is
the percentage of a position's value that must be covered by collateral, and
its default of 0 is documented as being interpreted as 100%; so 100/100 is
exactly the default, i.e. 1x, no leverage. The engine models an unlevered
cash-flow simulation and the port's `leverage()` returns 1.0, so the declaration
changes nothing here. It is recorded rather than silently dropped.

`strategy()` declares no other property, so `default_qty_type=strategy.fixed`,
`default_qty_value` 1 contract, initial capital 1000000, commission 0%,
`pyramiding=0` and `process_orders_on_close=false` are Pine's documented
defaults.

`can_short` is False: the sole entry is `strategy.long`.

The `/*backtest` header declares `period: 1d` on Binance BTC_USDT, so
`timeframe` is "1d"; `basePeriod: 1h` is the FMZ backtester's fill granularity.

FIDELITY:

* The md's summary says "enter long if PREVIOUS day's close is above EMA". The
  source enters on `close > ema` -- the CURRENT bar's close -- and `above =
  close[1] > ema[1]` is a separate statement that only touches the unused `p`.
  The port follows the code, not the prose.
* `p` (and therefore both of its `+= 1` statements and the `p := 0` reset) is
  not reproduced: it is display-only, and it is not a `var`, so it cannot carry
  state across bars in any case.
* The commented-out "Exit Position" / "Restablish long" blocks are dead code
  and are not restored.
* `start` is evaluated as the source writes it: a per-bar test against the
  literal `timestamp(2000,01,01,01,01)` in the exchange timezone (UTC for
  BTC/USDT; PINE_SEMANTICS.md §3.4). `yearInput` is unused by the source.
* `ta.ema` is seeded with the first non-na observation (see
  `pine_ta.pine_ema` and PINE_SEMANTICS.md §3.1); TradingView's seeding rule is
  unpublished, so the early bars carry a modelled choice.
* No stop / limit / trail exists in the source, so `source_reproduce_stops` is
  False and a position open at the end of the window stays open.
* margin_long/margin_short = 100 are the documented default (1x) and are not
  modelled as leverage; leverage/margin/liquidation/funding are outside the
  engine, and contract-step quantity rounding is measured separately by the
  chain verifier.
"""
import pandas as pd
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


class SMEmaStrat_821e5b(PinePortBase, IStrategy):
    source_id = "SM_821e5ba9df6ebf39"
    source_file = "EMA-Trading-Strategy.md"
    timeframe = "1d"
    can_short = False
    source_defaults: dict = {
        # emaInput = input(21, "Length"); yearInput = input(2000, "Year")
        "emaInput": 21,
        "yearInput": 2000,
    }
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    source_reproduce_stops = False
    source_fidelity_notes = [
        "The md says the entry uses the PREVIOUS day's close; the source uses "
        "the CURRENT bar's `close > ema`. The code is followed, not the prose.",
        "`p` is a non-var int, reset every bar, read only by plot(p). It and "
        "its two `+= 1` / one `:= 0` statements are not reproduced; they place "
        "no order.",
        "`yearInput` is inert: the `start` test compares against the literal "
        "timestamp(2000,01,01,01,01), not against the input. The literal "
        "comparison is evaluated as written.",
        "margin_long=100 / margin_short=100 is Pine's own documented default "
        "(0 is read as 100%), i.e. 1x; no leverage is modelled and none is "
        "implied by the declaration.",
        "The commented-out Exit Position / Restablish long blocks are dead "
        "code and are not restored.",
        "pine_ema seeds on the first non-na observation; TradingView's seeding "
        "rule is unpublished (PINE_SEMANTICS.md §3.1).",
        "No stop/limit/trail exists: a position open at the end of the window "
        "stays open, and source_reproduce_stops is False.",
        "strategy() declares no qty/commission/pyramiding property, so fixed / "
        "1 contract / 0% / pyramiding 0 / initial capital 1000000 are Pine's "
        "documented defaults.",
        "Contract-step quantity rounding is not modelled; the chain verifier "
        "measures it separately.",
    ]

    def pine_indicators(self, dataframe, params):
        close = dataframe["close"]

        # ema = ta.ema(close, emaInput)
        ema = ta.pine_ema(close, int(params["emaInput"]))

        # start = false
        # if (time >= timestamp(2000,01,01,01,01))
        #     start := true
        index = dataframe.index
        if not isinstance(index, pd.DatetimeIndex):
            index = pd.DatetimeIndex(dataframe["date"])
        times = pd.DatetimeIndex(index)
        if times.tz is None:
            times = times.tz_localize("UTC")
        start = times >= pd.Timestamp(2000, 1, 1, 1, 1, tz="UTC")

        # if (close > ema and start == true) -> strategy.entry("Long", long)
        dataframe["pine_ema"] = ema
        dataframe["pine_start"] = pd.Series(start, index=dataframe.index)
        dataframe["pine_long_condition"] = (
            (close > ema) & dataframe["pine_start"]
        ).fillna(False)
        # below = close < ema
        # if (below) -> strategy.close("Long", comment = "Flat")
        dataframe["pine_exit_condition"] = (close < ema).fillna(False)
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "long_condition": dataframe["pine_long_condition"].to_numpy(dtype=bool),
            "exit_condition": dataframe["pine_exit_condition"].to_numpy(dtype=bool),
        }

    def pine_script(self, broker, i, ctx):
        # if (close > ema and start == true)
        #     strategy.entry("Long", strategy.long, comment = "Entry")
        if ctx["long_condition"][i]:
            broker.entry("Long", "long")
        # below = close < ema
        # if (below)
        #     strategy.close("Long", comment = "Flat")
        if ctx["exit_condition"][i]:
            broker.close("Long")
