"""Port of sources/SM_1dc519ef8b89c01f.pine
(batch_001/EMA动量均线交叉策略EMA-Momentum-Moving-Average-Crossover-Strategy.md).

Pine v5. Fast / slow EMA crossed, reversal entries, and a tick stop attached to
each side. Reproduced call for call, in the source's own order:

    quantity = input(1, "Quantity")
    slPoints = input(2500, "Stoploss")
    fastEMA  = input(7, "Fast EMA")
    slowEMA  = input(21, "Slow EMA")

    fema = ta.ema(close, fastEMA)
    sema = ta.ema(close, slowEMA)
    buyCrossover  = ta.crossover(fema, sema)
    sellCrossover = ta.crossunder(fema, sema)

    if buyCrossover
        strategy.entry("Buy", strategy.long, qty = quantity)
    if sellCrossover
        strategy.entry("Sell", strategy.short, qty = quantity)

    strategy.exit("StopLoss", from_entry = "Buy",  loss = slPoints, qty = quantity)
    strategy.exit("StopLoss", from_entry = "Sell", loss = slPoints, qty = quantity)

`loss=slPoints` is a TICK distance in Pine, not a price (PINE_SEMANTICS.md 3.5),
so the input's value 2500 is handed to the engine as a tick count and resolved
against the position's average entry price with `source_mintick` (0.1 for
BTC/USDT:USDT, the project's convention). Converting it to a price first would
invent a stop the source never asked for; it is left as ticks.

The two `strategy.exit` calls carry the SAME order id ("StopLoss") and differ
only in `from_entry`, and both are unconditional (no `when=`). The engine keeps
one resting order per id for `kind == 'exit'`, so the second call replaces the
first and only the "Sell"-bound arm ever rests; while a long is open that arm's
`from_entry` is not, so it is a no-op and the engine publishes NO stop for the
long, which is then closed only by a reversal. That is the engine's settled
reading of Pine's one-order-per-id rule (PINE_SEMANTICS.md 3.6), and the source
text is transcribed as written, in order, without adding position guards that
would let the long arm rest and change the strategy. It is the single largest
open risk on this port and is recorded, not resolved -- see FIDELITY.

FIDELITY:

* `strategy.exit`'s `qty=` argument has no counterpart on the engine's
  `broker.exit` (which closes the whole entry, like `qty_percent=100`). Here the
  omission is inert: `quantity` is the same 1 contract the entry was sized to,
  so "close the whole entry" and "close `qty` contracts" name the same fill.
  Recorded because it would NOT be inert on a source whose exit qty differs from
  its entry qty.
* `quantity` sizes BOTH the entries and the exits from one input, and the entry
  passes it as `qty=` rather than relying on `default_qty_value`; the port does
  the same. `strategy()` declares only `title` and `overlay`, so the declared
  properties are Pine's documented defaults: strategy.fixed / 1 contract,
  initial capital 1000000, commission 0%, pyramiding 0,
  `process_orders_on_close=false`.
* The md's argument table lists `v_input_1` (Quantity) with default `true`; the
  source declares `input(1, "Quantity")`. The source is followed; the md table
  is wrong. (`v_input_2` (Stoploss) `2500`, `v_input_3` (Fast EMA) `7` and
  `v_input_4` (Slow EMA) `21` agree with the source.)
* The md's "Lack of stop loss mechanism" risk note contradicts its own argument
  table and the source: both `strategy.exit` calls exist and carry a `loss=`
  leg. The source is followed.
* Both `strategy.exit` calls share the order id "StopLoss" and differ only in
  `from_entry`. Under the engine's one-order-per-id rule the second replaces the
  first, so only the Sell-bound stop ever rests and a long carries no stop: it
  is closed only by a reversal (PINE_SEMANTICS.md 3.6). If the original platform
  keys exit orders by (id, from_entry), the long arm's stop at 2500 ticks would
  exist and the trade list would differ materially. No position guard was added
  -- that would let the long arm rest and change the strategy -- so the engine is
  the ledger of record and the risk is recorded, not resolved.
* `ta.ema`'s seeding is the modelled first-non-na-value rule, a parity risk
  recorded in PINE_SEMANTICS.md 3.1; Pine does not publish its own rule.
* No `strategy.close` and no leg-less `strategy.exit` exists, so
  PINE_SEMANTICS.md 1.15 does not apply. The two `plot()` calls are display-only
  and are not reproduced.
* The `/*backtest` header's `basePeriod: 1h` is the FMZ backtester's own
  granularity for filling the 1d bars, not the strategy's period.
* Leverage, margin, liquidation, funding and the venue's contract-step rounding
  are not modelled; the chain verifier measures the last one separately
  (PINE_SEMANTICS.md 1.6).
"""
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


class SMEmaMomentumMovingAverageCrossover_1dc519(PinePortBase, IStrategy):
    source_id = "SM_1dc519ef8b89c01f"
    source_file = "EMA动量均线交叉策略EMA-Momentum-Moving-Average-Crossover-Strategy.md"
    timeframe = "1d"
    can_short = True
    source_defaults: dict = {
        "quantity": 1,
        "slPoints": 2500,
        "fastEMA": 7,
        "slowEMA": 21,
    }
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    # `strategy.exit(..., loss=...)` is a stop leg, so the engine publishes a
    # resting stop level for whichever arm is bound to the open entry.
    source_reproduce_stops = True
    # TradingView reads the tick size off the symbol and the source never states
    # it; 0.1 is BTC/USDT:USDT, the project's convention. It matters here because
    # `loss=slPoints` is a tick count (PINE_SEMANTICS.md 3.5).
    source_mintick = 0.1
    source_fidelity_notes = [
        "loss=slPoints is a TICK distance in Pine (PINE_SEMANTICS.md 3.5), so the "
        "input's value 2500 is handed to the engine as a tick count and resolved "
        "against the position's average entry price with source_mintick = 0.1 "
        "(BTC/USDT:USDT). It is NOT converted to a price first -- that would "
        "invent a stop the source never asked for.",
        "Both strategy.exit calls share the order id 'StopLoss' and differ only "
        "in from_entry, and both are unconditional. The engine keeps one resting "
        "order per id for kind == 'exit', so the second replaces the first and "
        "only the Sell-bound arm ever rests; while a long is open that arm's "
        "from_entry is not open, so it is a no-op and no stop is published for "
        "the long, which is then closed only by a reversal (PINE_SEMANTICS.md "
        "3.6). The source text is transcribed as written, in order; no position "
        "guard was added, because that would let the long arm rest and change "
        "the strategy. If the original platform keys exit orders by (id, "
        "from_entry) instead, longs would carry a stop 2500 ticks below entry "
        "and the trade list would differ materially. The engine is the ledger of "
        "record; the risk is recorded, not resolved.",
        "strategy.exit's qty= has no counterpart on the engine's broker.exit, "
        "which closes the whole entry. The omission is inert here because "
        "quantity is the same 1 contract the entry was sized to; it is recorded "
        "because it would not be inert on a source whose exit qty differs from "
        "its entry qty.",
        "The md's argument table lists the Quantity input as defaulting to "
        "`true`; the source declares input(1, \"Quantity\"). The source is "
        "followed; the md table is wrong. The other three defaults agree.",
        "The md's risk note 'Lack of stop loss mechanism' contradicts the source "
        "and its own argument table: both strategy.exit calls exist and carry a "
        "loss= leg. The source is followed.",
        "strategy() declares only title and overlay, so every property is Pine's "
        "documented default: strategy.fixed / 1 contract, initial capital "
        "1000000, commission 0%, pyramiding 0, process_orders_on_close=false. "
        "Both entries pass qty=quantity explicitly, as the source does.",
        "ta.ema's seeding is the modelled first-non-na-value rule, a parity risk "
        "recorded in PINE_SEMANTICS.md 3.1; Pine does not publish its own rule.",
        "No strategy.close and no leg-less strategy.exit exists, so "
        "PINE_SEMANTICS.md 1.15 does not apply. The two plot() calls are "
        "display-only and are not reproduced.",
        "The /*backtest header's basePeriod: 1h is the FMZ backtester's own "
        "granularity for filling the 1d bars, not the strategy's period.",
        "Leverage, margin, liquidation, funding and the venue's contract-step "
        "rounding are not modelled; the chain verifier measures the last one "
        "separately (PINE_SEMANTICS.md 1.6).",
    ]

    def pine_indicators(self, dataframe, params):
        close = dataframe["close"]
        fast = ta.pine_ema(close, int(params["fastEMA"]))
        slow = ta.pine_ema(close, int(params["slowEMA"]))
        dataframe["pine_fast_ema"] = fast
        dataframe["pine_slow_ema"] = slow
        dataframe["pine_buy_crossover"] = ta.pine_crossover(fast, slow)
        dataframe["pine_sell_crossover"] = ta.pine_crossunder(fast, slow)
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "buy_crossover": dataframe["pine_buy_crossover"].to_numpy(),
            "sell_crossover": dataframe["pine_sell_crossover"].to_numpy(),
            "quantity": float(params["quantity"]),
            "loss_ticks": float(params["slPoints"]),
        }

    def pine_script(self, broker, i, ctx):
        qty = ctx["quantity"]
        # if buyCrossover
        #     strategy.entry("Buy", strategy.long, qty = quantity)
        if ctx["buy_crossover"][i]:
            broker.entry("Buy", "long", qty=qty)
        # if sellCrossover
        #     strategy.entry("Sell", strategy.short, qty = quantity)
        if ctx["sell_crossover"][i]:
            broker.entry("Sell", "short", qty=qty)
        # strategy.exit("StopLoss", from_entry = "Buy", loss = slPoints, qty = quantity)
        broker.exit("StopLoss", from_entry="Buy", loss=ctx["loss_ticks"])
        # strategy.exit("StopLoss", from_entry = "Sell", loss = slPoints, qty = quantity)
        broker.exit("StopLoss", from_entry="Sell", loss=ctx["loss_ticks"])
