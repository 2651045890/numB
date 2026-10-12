"""Port of sources/SM_dfbb9ca7a67d17b8.pine (batch_001/Internal-Bar-Strength-Indicator-Reversion-system.md).

Pine v2. A mean-reversion system on the Internal Bar Strength -- where the
close sits inside the bar's own range:

    src = close
    ibs = (close - low) / (high - low) * 100

    longCondition = ibs < 5
    if (longCondition)
        strategy.entry("My Long Entry Id", strategy.long)

    //shortCondition = close > high[1]
    shortCondition = ibs > 99
    if (shortCondition)
        strategy.entry("My Short Entry Id", strategy.short)

    p = close * 0.01 * 10
    strategy.exit("exit", "My Long Entry Id",profit = 10, loss=2)
    strategy.exit("exit", "My Short Entry Id",profit = 10, loss=2)

Both conditions are plain `<` / `>` tests -- there is no `? -1 : 0` shape here,
so PINE_SEMANTICS.md 1.17's minus-truthiness trap does not arise and nothing was
rewritten into `== 1` / `> 0`.

The two exits ARE live (they are not commented out) and they are the reason
`source_reproduce_stops` is True: `profit=10` / `loss=2` are TICK distances
(PINE_SEMANTICS.md 3.5), resolved by the engine against the entry's average
price with `mintick = 0.1`, i.e. +1.0 / -0.2 price units. They rest inside the
bar, so the port passes the tick counts through unchanged and never turns them
into a next-open market exit.

Both calls use the SAME order id, "exit". Pine keeps one order per id and a
later `strategy.exit` with an id that is already resting REPLACES it, so the
second call -- the one bound to "My Short Entry Id" -- always wins; the long
arm's stop/target is replaced away on every bar of the source. The port does
not "fix" that: it calls both, in source order, and lets the engine apply the
same one-order-per-id rule (PINE_SEMANTICS.md 1.12 for the `from_entry` filter
that keeps the surviving order from being read as the long's stop).

`p = close * 0.01 * 10` is dead code: `p` is never read by anything in the file.

FIDELITY:

* The `strategy(...)` declaration is COMMENTED OUT in the source
  (`// strategy("IBS", initial_capital=10000, overlay=false, pyramiding=5,
  default_qty_value=100, currency="USD")`), and so is `//strategy.risk.
  allow_entry_in(strategy.direction.long)`. Commented code is not a
  declaration, so Pine's documented defaults apply to an undeclared strategy:
  `default_qty_type` fixed, 1 unit, 1000000 initial capital, 0% commission,
  pyramiding 0. The commented line's own numbers (initial_capital=10000,
  pyramiding=5, default_qty_value=100, currency="USD") are recorded here rather
  than used; note that `pyramiding=5` could not be reproduced by the framework
  even if it were restored (PINE_SEMANTICS.md section 2, item 10).
* The md text describes the exits as "a profit of 10% or a loss of 2%". The
  source says `profit = 10, loss = 2`, which Pine reads as ticks, not percent.
  The md is wrong; the source is reproduced.
* `ibs` is a plain pandas division. `high == low` makes the numerator and the
  denominator both 0, and pandas gives NaN for 0/0, which is Pine's na; the
  comparison `na < 5` is false in both languages, so no signal can come out of
  such a bar.
* Bar 0 carries no history reference at all, so nothing is lost at the start of
  the window.
* `/*backtest` declares `period: 1h` on Futures_Binance BTC_USDT, so timeframe
  is "1h"; `basePeriod: 15m` is the FMZ backtester's fill granularity.
* Leverage, margin, liquidation, funding and the venue's contract-step rounding
  are not modelled.
"""
import pandas as pd

from freqtrade.strategy import IStrategy

from pine_port_base import PinePortBase

# strategy.exit("exit", ..., profit = 10, loss = 2) -- TICK distances, passed
# through as written; the engine resolves them with source_mintick (0.1).
PROFIT_TICKS = 10
LOSS_TICKS = 2


class SMInternalBarStrength_dfbb9c(PinePortBase, IStrategy):
    source_id = "SM_dfbb9ca7a67d17b8"
    source_file = "Internal-Bar-Strength-Indicator-Reversion-system.md"
    timeframe = "1h"
    can_short = True
    # Pine evaluates the script from the first bar of the window.
    startup_candle_count = 0
    # The source has no input() call at all.
    source_defaults: dict = {}
    # The only strategy() line in the file is commented out (and sets
    # pyramiding=5, default_qty_value=100, currency="USD"), so it declares
    # nothing and Pine's documented defaults apply.
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    # strategy.exit(profit=...) / strategy.exit(loss=...) rest inside the bar.
    source_reproduce_stops = True
    # `profit=` / `loss=` are ticks; BTC/USDT:USDT futures quote in 0.1.
    source_mintick = 0.1
    source_fidelity_notes = [
        "The exits are LIVE: `strategy.exit(\"exit\", \"My Long Entry Id\", "
        "profit = 10, loss=2)` and the same for \"My Short Entry Id\" are not "
        "commented out, so source_reproduce_stops is True (unlike the sibling "
        "converter-appended sources whose exit lines were commented away).",
        "`profit=10` / `loss=2` are TICK distances (PINE_SEMANTICS.md 3.5) and "
        "are passed to broker.exit unchanged, so the engine resolves them "
        "against the position's average price with mintick 0.1: +1.0 / -0.2 "
        "price units.",
        "The md glosses the exits as 'a profit of 10% or a loss of 2%'. The "
        "source's `profit = 10, loss = 2` are ticks, not percent; the source is "
        "reproduced and the md's reading is recorded here as incorrect.",
        "Consequence of that reading, for whoever reads the ledger: on a "
        "BTC/USDT:USDT contract (mintick 0.1) the surviving short-arm exit sits "
        "1.0 / 0.2 price units from the entry's average price, so a short is "
        "almost always stopped out on the very next bar -- one-bar trades with "
        "tiny P&L are the source's own parameters, not a port defect. The md's "
        "'10% / 2%' reading would have produced something else entirely, and it "
        "is the md, not the source, that is wrong.",
        "Both `strategy.exit` calls share the order id \"exit\". Pine keeps one "
        "order per id, so the later call (bound to \"My Short Entry Id\") "
        "REPLACES the earlier one on every bar; the long arm's stop/target is "
        "therefore replaced away each bar and a long is exited only by an "
        "opposite entry. The port calls both in source order and does not "
        "restore the clobbered leg by inventing a distinct id.",
        "The `strategy(...)` declaration is commented out, so it declares "
        "nothing and Pine's defaults apply (fixed 1 unit, initial capital "
        "1000000, 0% commission, pyramiding 0). The commented line's own "
        "numbers -- initial_capital=10000, pyramiding=5, default_qty_value=100, "
        "currency=\"USD\" -- are NOT used; restoring them would be reading "
        "commented code as code, and pyramiding=5 is not implementable in the "
        "framework anyway (PINE_SEMANTICS.md section 2 item 10).",
        "`p = close * 0.01 * 10` is dead code -- `p` is read by nothing -- and "
        "is therefore not reproduced.",
        "`ibs = (close - low) / (high - low) * 100` is a plain division; a bar "
        "with high == low gives 0/0 = NaN, which is Pine's na, and `na < 5` / "
        "`na > 99` are false in both languages, so no signal is emitted there.",
        "The conditions are plain booleans -- no `? -1 : 0` shape -- so "
        "PINE_SEMANTICS.md 1.17's minus-truthiness trap does not arise and "
        "nothing was normalised into `== 1` / `> 0`.",
        "`//shortCondition = close > high[1]` and `//strategy.risk."
        "allow_entry_in(strategy.direction.long)` are comments and place no "
        "order / impose no filter.",
        "Venue contract-step rounding, leverage, margin, liquidation and "
        "funding are not modelled.",
    ]

    def pine_indicators(self, dataframe: pd.DataFrame, params: dict) -> pd.DataFrame:
        high = dataframe["high"]
        low = dataframe["low"]
        close = dataframe["close"]

        # ibs = (close - low) / (high - low) * 100
        dataframe["pine_ibs"] = (close - low) / (high - low) * 100.0

        # longCondition = ibs < 5
        dataframe["pine_long_condition"] = dataframe["pine_ibs"] < 5
        # shortCondition = ibs > 99
        dataframe["pine_short_condition"] = dataframe["pine_ibs"] > 99
        return dataframe

    def pine_context(self, dataframe: pd.DataFrame, params: dict) -> dict:
        return {
            "long_condition": dataframe["pine_long_condition"].to_numpy(),
            "short_condition": dataframe["pine_short_condition"].to_numpy(),
        }

    def pine_script(self, broker, i: int, ctx: dict) -> None:
        # if (longCondition)
        #     strategy.entry("My Long Entry Id", strategy.long)
        if ctx["long_condition"][i]:
            broker.entry("My Long Entry Id", "long")
        # if (shortCondition)
        #     strategy.entry("My Short Entry Id", strategy.short)
        if ctx["short_condition"][i]:
            broker.entry("My Short Entry Id", "short")
        # strategy.exit("exit", "My Long Entry Id",profit = 10, loss=2)
        broker.exit("exit", "My Long Entry Id", profit=PROFIT_TICKS, loss=LOSS_TICKS)
        # strategy.exit("exit", "My Short Entry Id",profit = 10, loss=2)
        broker.exit("exit", "My Short Entry Id", profit=PROFIT_TICKS, loss=LOSS_TICKS)
