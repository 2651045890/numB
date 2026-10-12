"""Port of sources/SM_feb52c291f66a042.pine (batch_001/Bollinger-Band-Breakout-strategy.md).

Pine v4. A long-only Bollinger breakout: buy when the close crosses above the
upper band, and close the position when it falls back through the basis:

    source = close
    basis  = sma(source, 20)
    dev    = 1.5 * stdev(source, 20)
    upper  = basis + dev
    lower  = basis - dev

    if (crossover(source, upper))
        strategy.entry("Long", strategy.long)
    if (crossunder(source, basis))
        strategy.close("Long")

Both calls are always evaluated and are written in this order: the entry first,
then the close. `lower` is computed by the source but never read by either
condition -- it is drawn (and filled against `upper`) only -- so it places no
order and is kept here as a column for text fidelity.

`strategy(title=..., shorttitle=..., default_qty_type = strategy.percent_of_equity,
default_qty_value = 100, overlay=true)` declares NO other property, so Pine's
documented defaults apply for everything else: commission 0%, pyramiding 0,
`process_orders_on_close=false`, initial capital 1000000. `percent_of_equity`
with value 100 means every entry is sized as the whole of `strategy.equity` as
of the bar the order was PLACED (Pine evaluates the script at that bar's close,
so the quantity is frozen before the next bar opens) -- not 100 contracts, and
not 100 units of cash.

The `/*backtest` header declares `period: 1d` on Futures_Binance BTC_USDT, so
`timeframe` is "1d"; its `basePeriod: 1h` is the FMZ backtester's own
granularity for filling those daily bars, not the strategy's period.

FIDELITY:

* Only `strategy.entry("Long", strategy.long)` is ever called, so `can_short`
  is False.
* No stop / limit / profit / loss / trail exit exists anywhere in the source --
  the only exit is `strategy.close("Long")` -- so `source_reproduce_stops` is
  False and a position open at the end of the window stays open.
* `stdev` in Pine is the POPULATION standard deviation (Pine's `ta.stdev` is
  documented with `biased = true` by default, i.e. it divides by N and not by
  N-1). pine_ta.pine_stdev models exactly that (ddof=0).
* `crossover` / `crossunder` are Pine's own definitions -- `a > b and a[1] <= b[1]`
  and `a < b and a[1] >= b[1]` -- supplied by pine_ta.pine_crossover /
  pine_crossunder. na on either side makes the comparison na, which is false in
  a boolean context, so no condition fires while any term is na.
* `sma` / `stdev` return na until their window is full, so the first possible
  signal needs 20 bars of history; na propagates within the window and neither
  condition fires before then.
* Both conditions are evaluated on the SAME bar's close (Pine's
  close-of-bar evaluation), and both are written unconditionally: on a bar where
  both happen to hold, the entry fills at the next bar's open and the close then
  closes that just-opened position -- a zero-length round trip. The order is
  preserved (entry call first, close call second) so the engine's same-bar
  fill sequence matches the source's call sequence
  (PINE_SEMANTICS.md section 1.13).
* `plot` / `fill` / the titles and `overlay` are display-only and are not
  reproduced; `lower` is kept as a column because it is part of the source's
  band arithmetic, but it is never read by the script body.
* `percent_of_equity` sizing is reproduced from the engine's own recorded fill
  notional, not re-derived from the live wallet (PINE_SEMANTICS.md section 1.4).
* Leverage, margin, liquidation, funding and the venue's contract-step rounding
  are not modelled; the step can only be read off the exchange object at run
  time, so the framework and the engine may differ by a rounded quantity, which
  the chain verifier measures separately rather than treating as a signal
  difference.
"""
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


class SMBollingerBandBreakoutStrategy_feb52c(PinePortBase, IStrategy):
    source_id = "SM_feb52c291f66a042"
    source_file = "Bollinger-Band-Breakout-strategy.md"
    timeframe = "1d"
    can_short = False
    source_defaults: dict = {"length": 20, "mult": 1.5}
    source_qty_type = "percent_of_equity"
    source_qty_value = 100.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    source_reproduce_stops = False
    source_fidelity_notes = [
        "strategy() declares only title/shorttitle/default_qty_type/"
        "default_qty_value/overlay, so commission 0%, pyramiding 0 and initial "
        "capital 1000000 are Pine's documented defaults rather than the "
        "source's own values.",
        "default_qty_type = strategy.percent_of_equity with default_qty_value = "
        "100: each entry is sized as the whole of strategy.equity as of the bar "
        "the order was placed, not as 100 contracts or 100 units of cash.",
        "Only strategy.entry(\"Long\", strategy.long) is called, so can_short is "
        "False; the only exit is strategy.close(\"Long\"), so "
        "source_reproduce_stops is False and a position open at the window's end "
        "stays open.",
        "stdev is the POPULATION standard deviation (Pine's ta.stdev defaults to "
        "biased = true, dividing by N), which pine_ta.pine_stdev models with "
        "ddof=0.",
        "crossover/crossunder use Pine's definitions (a > b and a[1] <= b[1]; a < "
        "b and a[1] >= b[1]) via pine_ta; na comparisons are false, so nothing "
        "fires while sma/stdev are still na (the first 19 bars).",
        "Both conditions are evaluated on the same bar and both calls are written "
        "unconditionally in source order (entry then close), so on a bar where "
        "both hold the engine opens at the next open and closes at that same "
        "price. Reproduced as written rather than guarded; see "
        "PINE_SEMANTICS.md section 1.13 for the projection limit this shares.",
        "`lower` is computed and plotted by the source but read by no condition; "
        "it is kept as a column for fidelity and is not used by the script body.",
        "plot/fill/titles/overlay are display-only and are not reproduced.",
        "The md's prose describes a SHORT entry on a break below the lower band "
        "and names both \"做多\" and \"做空\"; the code has no short call at all -- "
        "its only exit is the close on a cross below the basis. The code is "
        "authoritative, so can_short is False. Recorded, not reconciled.",
        "The /*backtest header's `period: 1d` is the strategy's timeframe; its "
        "`basePeriod: 1h` is the FMZ backtester's own granularity for filling "
        "daily bars, not a second timeframe read by the script.",
        "percent_of_equity sizing is reproduced from the engine's own recorded "
        "fill notional, not re-derived from the live wallet.",
        "Leverage, margin, liquidation, funding and contract-step rounding are "
        "not modelled; the venue's rounding can differ from the engine's float "
        "quantity, which the chain verifier measures separately.",
    ]

    def pine_indicators(self, dataframe, params):
        source = dataframe["close"]
        length = int(params["length"])
        basis = ta.pine_sma(source, length)
        dev = float(params["mult"]) * ta.pine_stdev(source, length)
        upper = basis + dev
        lower = basis - dev
        dataframe["pine_basis"] = basis
        dataframe["pine_upper"] = upper
        # Computed and plotted by the source, never read by a condition.
        dataframe["pine_lower"] = lower
        dataframe["pine_long_condition"] = ta.pine_crossover(source, upper)
        dataframe["pine_close_condition"] = ta.pine_crossunder(source, basis)
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "long_condition": dataframe["pine_long_condition"].to_numpy(),
            "close_condition": dataframe["pine_close_condition"].to_numpy(),
        }

    def pine_script(self, broker, i, ctx):
        # if (crossover(source, upper))
        #     strategy.entry("Long", strategy.long)
        if ctx["long_condition"][i]:
            broker.entry("Long", "long")
        # if(crossunder(source, basis))
        #     strategy.close("Long")
        if ctx["close_condition"][i]:
            broker.close("Long")
