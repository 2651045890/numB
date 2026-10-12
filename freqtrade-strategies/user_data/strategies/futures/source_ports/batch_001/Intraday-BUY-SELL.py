"""Port of sources/SM_66f1648cb19ae4c1.pine (batch_001/Intraday-BUY-SELL.md).

Pine v4 (`//@version=4`) with `study(...)`, NOT `strategy(...)`: the
`if BUY / else if SELL` block at the bottom is an order block APPENDED to the
indicator by the converter site that published it (the md's Detail link names
fmz.com/strategy/365706). Pine does not compile `strategy.entry` inside
`study()`, so the "original strategy" is the indicator PLUS that appended block,
and the trading behaviour it defines is entry-only.

Only two of the indicator's many series reach that block:

    sma1 = sma(close, 50)
    BUY  = crossover(close[1], sma1) and close[1] > open[1]
           and high[0] > high[1] and close[0] > open[0]
    SELL = crossunder(low[1], sma1) and close[1] < open[1]
           and low[0] < low[1] and close[0] < open[0]

    if BUY
        strategy.entry("Enter Long", strategy.long)
    else if SELL
        strategy.entry("Enter Short", strategy.short)

`crossover(close[1], sma1)` is Pine's `a > b and a[1] <= b[1]` applied to the
SHIFTED series `a = close[1]`, i.e. `close[1] > sma1 and close[2] <= sma1[1]`.
The port passes `close.shift(1)` into the shared `pine_crossover`, which applies
the same one-bar lookback to its arguments, so the extra shift is preserved
rather than collapsed. `[0]` is the current bar.

`rs = rsi(close, 14)` is computed by the source but never read by the order
block (it feeds only `mycolor`, the `rev*` reversal flags and the two
`alertcondition` calls, none of which place an order). The same is true of
`gaps`, `gapb`, `chartgap`, `gap1`, `gapvalue`, `gapp`, `gapp2`, `bull`, `bear`,
`buycall`, `sellcall`, `hlrev_s`, `llrev_b` and every `rev*` flag.

There is NO exit of any kind in the source -- no `strategy.close`, no
`strategy.exit`, not even a commented-out one. A position is only ever left by
the opposite entry, which the engine models as a reversal. `pyramiding` keeps
Pine's default of 0, so a repeated signal while already positioned that way is
ignored.

FIDELITY:

* The `else if` is kept as `elif` to mirror Pine's short-circuit. The two
  conditions are mutually exclusive (`close[0] > open[0]` cannot coexist with
  `close[0] < open[0]`), so the ordering is not load-bearing for the fills --
  only for faithfulness.
* `BUY` / `SELL` are booleans, so there is no integer-truthiness question and no
  `? -1 : 0` form anywhere in the source.
* `rsi(close, Rsi_value)` is a documented Pine built-in; `pine_ta.pine_rsi`
  implements the documented `100 - 100/(1 + rma(gain)/rma(loss))`. It is not on
  the order path here (see above), so its boundary behaviour does not move any
  fill.
* `barstate.isconfirmed` appears once, inside `rev3`, which is unused; it is a
  no-op for this port (PINE_SEMANTICS.md, section 4).
* `study(...)` declares no strategy properties, so Pine's documented defaults
  are what the `source_*` attributes record (fixed size 1, 0% commission,
  pyramiding 0, initial capital 1000000).
* The missing/na head of every `[n]` reference is handled by Pine's rule that a
  comparison with na is false; pandas evaluates `NaN > NaN` (and every other
  comparison against NaN) as False, so the two agree on the warm-up bars.
* The md's description says the technique is "best ... on 3 min timeframe on
  Crude Oil Futures" and the source's `shorttitle` is "CRUDE Scalp |3 Min", but
  the extracted source's `/*backtest` header declares `period: 4h` on
  BTC_USDT:USDT. The port takes the header's `period: 4h`, which is the
  timeframe the extracted file was actually run on; the title strings are
  display-only. `basePeriod: 15m` is the host's intrabar granularity for filling
  those 4h bars, not a second timeframe.
* The backtest window in the header (2022-04-24 to 2022-05-23) is extraction
  metadata, not an `input.time` filter, so the port runs on whatever range the
  caller supplies.
* No stop, limit or trail exit exists, so `source_reproduce_stops` is False.
* Leverage, margin, liquidation, funding and the venue's contract-step rounding
  are not modelled (PINE_SEMANTICS.md 1.6, 2.4).
"""
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


class SMIntradayBuySell_66f164(PinePortBase, IStrategy):
    source_id = "SM_66f1648cb19ae4c1"
    source_file = "Intraday-BUY-SELL.md"
    timeframe = "4h"
    can_short = True
    # As written in the source, in source order.
    source_defaults: dict = {
        "Rsi_value": 14,
        "hl": 75,
        "ll": 25,
        "sma_value": 50,
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
        "The file declares study(...), not strategy(...); the strategy.entry pair "
        "at the bottom is an order block appended to the indicator by the "
        "converter site that published it (the md's Detail link names "
        "fmz.com/strategy/365706). The original strategy is the indicator plus "
        "that appended block, and its trading behaviour is entry-only.",
        "The source has no exit of any kind: no strategy.close, no strategy.exit, "
        "no stop or limit order, and no commented-out exit line. A position is "
        "only ever left by the opposite entry, which the engine models as a "
        "reverse fill. source_reproduce_stops is False accordingly.",
        "`crossover(close[1], sma1)` is the crossover of a SHIFTED series, so its "
        "second lookback becomes close[2] <= sma1[1]. The port shifts the series "
        "before handing it to pine_crossover so the extra shift is preserved, "
        "instead of collapsing it to close[1] <= sma1.",
        "rsi(close, 14) is computed by the source but no order call reads it: it "
        "feeds only mycolor, the rev* reversal flags and the alertcondition "
        "calls. The same holds for gaps, gapb, chartgap, gap1, gapvalue, gapp, "
        "gapp2, bull, bear, buycall, sellcall, hlrev_s and llrev_b. The port "
        "computes only sma(close, 50), which both order conditions do read.",
        "BUY and SELL are booleans, so there is no integer-truthiness question "
        "here and no `? -1 : 0` form in the source.",
        "The two conditions live in one `if / else if` chain in source order, "
        "reproduced as if/elif. They are mutually exclusive (close[0] > open[0] "
        "cannot coexist with close[0] < open[0]), so the ordering is not "
        "load-bearing for the fills -- only for faithfulness.",
        "study(...) declares no strategy properties, so Pine's documented defaults "
        "are used: default_qty_type fixed, default_qty_value 1, commission 0%, "
        "pyramiding 0, initial capital 1000000 USD.",
        "The md's Strategy Description recommends a 3-minute Crude Oil chart and "
        "the source's shorttitle reads 'CRUDE Scalp |3 Min', but the extracted "
        "file's /*backtest header declares `period: 4h` on BTC_USDT:USDT. The port "
        "carries the header's 4h, which is the timeframe the extracted file was "
        "actually run on; the title strings are display-only decoration.",
        "barstate.isconfirmed appears once, inside rev3, which no order call "
        "reads; it places no condition here.",
        "The header's basePeriod: 15m is the host's intrabar granularity for "
        "filling 4h bars, not the strategy's period; the engine evaluates at bar "
        "close and fills at the next open, so intrabar path differences are not "
        "modelled.",
        "The backtest window in the header (2022-04-24 to 2022-05-23) is "
        "extraction metadata, not an input.time filter, so the port runs on "
        "whatever range the caller supplies.",
        "Leverage, margin, liquidation, funding and the venue's contract-step "
        "rounding are not modelled; the chain verifier measures the rounding "
        "separately (PINE_SEMANTICS.md 1.6).",
    ]

    def pine_indicators(self, dataframe, params):
        close = dataframe["close"]
        open_ = dataframe["open"]
        high = dataframe["high"]
        low = dataframe["low"]
        # sma1 = sma(close, sma_value)
        sma1 = ta.pine_sma(close, int(params["sma_value"]))
        dataframe["pine_sma1"] = sma1
        # BUY = crossover(close[1], sma1) and close[1] > open[1]
        #       and high[0] > high[1] and close[0] > open[0]
        buy = (
            ta.pine_crossover(close.shift(1), sma1)
            & (close.shift(1) > open_.shift(1))
            & (high > high.shift(1))
            & (close > open_)
        )
        # SELL = crossunder(low[1], sma1) and close[1] < open[1]
        #        and low[0] < low[1] and close[0] < open[0]
        sell = (
            ta.pine_crossunder(low.shift(1), sma1)
            & (close.shift(1) < open_.shift(1))
            & (low < low.shift(1))
            & (close < open_)
        )
        dataframe["pine_buy_condition"] = buy
        dataframe["pine_sell_condition"] = sell
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "buy_condition": dataframe["pine_buy_condition"].to_numpy(),
            "sell_condition": dataframe["pine_sell_condition"].to_numpy(),
        }

    def pine_script(self, broker, i, ctx):
        # if BUY
        #     strategy.entry("Enter Long", strategy.long)
        # else if SELL
        #     strategy.entry("Enter Short", strategy.short)
        if ctx["buy_condition"][i]:
            broker.entry("Enter Long", "long")
        elif ctx["sell_condition"][i]:
            broker.entry("Enter Short", "short")
