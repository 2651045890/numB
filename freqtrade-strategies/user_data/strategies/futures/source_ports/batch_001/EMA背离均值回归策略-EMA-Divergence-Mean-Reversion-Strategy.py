"""Port of sources/SM_c8750b01e731bd6f.pine (batch_001/EMA背离均值回归策略-EMA-Divergence-Mean-Reversion-Strategy.md).

Pine v5, long only. A mean-reversion "buy the dip" on the 50-period EMA:

    ema20      = ta.ema(close, 50)
    diff_perct  = ((ema20 - close) / ema20) * 100     // how far BELOW the EMA
    diff_perct2 = ((high  - ema20) / ema20) * 100     // how far the high is ABOVE it

    if diff_perct > 10                          -> BuyTrigger  := true
    if diff_perct2 > 0 and strategy.openprofit > 1 -> SellTrigger := true

    notInTrade = strategy.position_size <= 0
    inTrade    = strategy.position_size >  0

    if (BuyTrigger and notInTrade)
        strategy.order("long", strategy.long, oca_name='audusdt', when=BuyTrigger,
                       limit=open, comment="buy: SUIBTC EMA Dip")
    if (SellTrigger and inTrade)
        strategy.close(id="long", qty_percent=100, comment="sell: SUIBTC EMA Dip")

THE TWO TRIGGERS ARE PER-BAR, NOT LATCHES. `BuyTrigger = input.bool(false)` is a
plain (non-`var`) declaration, so Pine re-initialises it to false on every bar;
the conditional `:= true` then only holds for the bar it fires on. The same
applies to `SellTrigger`. Modelled literally, with the input's own value as the
per-bar starting point so a `source_parameters` override still reaches the
script. Reading them as persistent latches would instead buy once and then
close every subsequent trade on its first profitable bar -- a different
strategy, and not what the source says.

The entry is a resting BUY LIMIT at the signal bar's own open (`limit = open`),
which the framework cannot express -- see the fidelity notes.

`strategy()` declares `initial_capital=100`, `default_qty_value=100`,
`default_qty_type=strategy.cash`, `process_orders_on_close=false` and
`calc_on_every_tick=false`; everything else is Pine's documented default:
commission 0%, pyramiding 0.

FIDELITY:

* The entry is a resting LIMIT order at the SIGNAL BAR'S OWN OPEN. Pine places
  it at bar t's close, so it rests from bar t+1 onward and fills at
  `min(open[t], open[t+k])` on the first bar whose low reaches `open[t]`; if no
  bar reaches it the order rests indefinitely. Freqtrade's strategy interface
  has no resting-entry expression, so the projected `enter_long` is a market
  order filling at the next bar's open. Same framework boundary as
  PINE_SEMANTICS.md section 二.11 and the batch_003 golden-cross port; the port
  reproduces the SOURCE's order and the projection is the framework's
  approximation, reported by verify_chain rather than hidden here.
* `BuyTrigger` / `SellTrigger` are non-`var` declarations, so they re-initialise
  every bar -- reproduced as a per-bar local starting from the input default,
  never carried across bars (Pine v5 documented `var` semantics).
* `strategy.order(...)` is translated with `broker.order(...)`, the engine's own
  counterpart. The `oca_name='audusdt'` argument has no counterpart in the
  broker surface; OCA grouping is not modelled by the engine at all and a single
  order forms a group of one, so nothing behavioural is dropped. Recorded rather
  than silently omitted.
* `strategy.close(id="long", qty_percent=100)` is a full market close; the
  broker's `close()` has no `qty_percent` because 100 is the whole position,
  which is what `close()` does.
* `qty_percent`, `comment=`, `title=` and the `plot()` call are display or
  metadata only and place no order.
* `src = input(open, title="Source")` and `offset = input.int(defval=5, ...)`
  are DEAD inputs: neither is read anywhere in the source. Both are declared
  here in `source_defaults` so the input surface matches, and neither is used.
* `timeSinceLastTrade_ms = time - strategy.opentrades.entry_time(0)` is computed
  and never read; it is dead code and is not reproduced (it also reads a field
  the broker surface does not expose).
* The md prose and the strategy title agree with the code on the entry (price
  >10% below the EMA); the md's step 5 calls the exit "最高价高于EMA" and
  "盈利大于1", which is exactly `diff_perct2 > 0 and strategy.openprofit > 1`.
  The variable is named `ema20` but is built with length 50; the md also says
  50. No md/source disagreement on behaviour.
* na handling: the first 49 bars have an na EMA, so both `diff_perct` terms are
  na, both comparisons are false (Pine na comparisons), and nothing fires.
* `source_initial_capital` is 100 and `qty_type` is `strategy.cash` with value
  100 -- i.e. a single order commits the WHOLE declared capital. PINE_SEMANTICS.md
  section 1.6 documents that a small declared capital turns the venue's contract
  step into a compounding drift between the engine's cash and the framework's
  wallet, and section 1.5.1 documents the min-stake veto it can end in. Both are
  properties of the source's own sizing, not of this translation, and neither is
  "fixed" by changing the declared capital.
* `process_orders_on_close=false` is Pine's default and matches the engine's
  bar-close evaluation / next-open fill. `calc_on_every_tick=false` is the
  default too, and the engine only ever evaluates once per bar.
"""
from __future__ import annotations

from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


class SMEmaDivergenceMeanReversion_c8750b(PinePortBase, IStrategy):
    source_id = "SM_c8750b01e731bd6f"
    source_file = (
        "EMA背离均值回归策略-EMA-Divergence-Mean-Reversion-Strategy.md"
    )
    timeframe = "1h"
    can_short = False
    source_defaults: dict = {
        # BuyTrigger = input.bool(false) / SellTrigger = input.bool(false)
        "BuyTrigger": False,
        "SellTrigger": False,
        # src = input(open, title="Source") / offset = input.int(defval=5, ...)
        "Source": "open",
        "Offset": 5,
    }
    source_qty_type = "cash"
    source_qty_value = 100.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 100.0
    source_reproduce_stops = False
    source_fidelity_notes = [
        "BuyTrigger / SellTrigger are non-`var` declarations: Pine re-initialises "
        "them to the input value on EVERY bar and the conditional `:= true` only "
        "holds for that bar. Reproduced per bar, never latched across bars.",
        "The entry is a resting LIMIT order at the signal bar's own open "
        "(`limit = open`). Freqtrade has no resting-entry expression, so the "
        "projected entry is a next-open market order: the engine fills at "
        "min(open[t], open[t+k]) once a bar's low reaches open[t] (possibly bars "
        "later, or never) while the framework fills at the next open "
        "unconditionally. Same boundary as PINE_SEMANTICS.md 二.11.",
        "`oca_name='audusdt'` has no counterpart in the broker surface and OCA "
        "grouping is not modelled by the engine; a single order is a group of "
        "one, so nothing behavioural is lost. Recorded, not silently dropped.",
        "`qty_percent=100` on strategy.close matches the broker's whole-position "
        "close(); `comment=` / `title=` / `plot()` are display-only.",
        "`src = input(open)` and `offset = input.int(defval=5)` are DEAD inputs -- "
        "neither is read by the source. Declared in source_defaults to match the "
        "input surface; neither is used.",
        "`timeSinceLastTrade_ms = time - strategy.opentrades.entry_time(0)` is "
        "computed and never read (and reads a field the broker does not expose); "
        "dead code, not reproduced.",
        "strategy.openprofit is the engine's per-bar mark-to-market at the bar's "
        "close, which is what Pine's strategy.openprofit is at bar close.",
        "The first 49 bars have an na EMA, so both comparisons are false and "
        "nothing fires (Pine na comparisons).",
        "source_initial_capital=100 with default_qty_type=strategy.cash value=100 "
        "commits the WHOLE declared capital per order. PINE_SEMANTICS.md 1.6 "
        "documents the venue contract-step drift this causes, and 1.5.1 the "
        "min-stake veto it can end in; both follow from the source's own sizing "
        "and are not corrected here.",
        "Leverage, margin, liquidation, funding and contract-step rounding are not "
        "modelled; the chain verifier measures the rounding separately.",
    ]

    def pine_indicators(self, dataframe, params):
        close = dataframe["close"]
        high = dataframe["high"]
        # ema20 = ta.ema(close, 50) -- named ema20 in the source, length 50.
        ema50 = ta.pine_ema(close, 50)
        dataframe["pine_ema50"] = ema50
        # diff_perct  = ((ema20 - close) / ema20) * 100
        dataframe["pine_diff_perct"] = ((ema50 - close) / ema50) * 100.0
        # diff_perct2 = ((high - ema20) / ema20) * 100
        dataframe["pine_diff_perct2"] = ((high - ema50) / ema50) * 100.0
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "diff_perct": dataframe["pine_diff_perct"].to_numpy(dtype=float),
            "diff_perct2": dataframe["pine_diff_perct2"].to_numpy(dtype=float),
            "open": dataframe["open"].to_numpy(dtype=float),
            # input.bool defaults; a non-`var` declaration restarts from these
            # on every bar.
            "buy_default": bool(params["BuyTrigger"]),
            "sell_default": bool(params["SellTrigger"]),
        }

    def pine_script(self, broker, i, ctx):
        # BuyTrigger = input.bool(false) ... if (diff_perct > 10) BuyTrigger := true
        buy_trigger = ctx["buy_default"]
        if ctx["diff_perct"][i] > 10.0:
            buy_trigger = True

        # SellTrigger = input.bool(false)
        # ... if (diff_perct2 > 0 and strategy.openprofit > 1) SellTrigger := true
        sell_trigger = ctx["sell_default"]
        if ctx["diff_perct2"][i] > 0.0 and broker.open_profit > 1.0:
            sell_trigger = True

        # notInTrade = strategy.position_size <= 0 / inTrade = ... > 0
        not_in_trade = broker.position_size <= 0
        in_trade = broker.position_size > 0

        # if (BuyTrigger and notInTrade)
        #     strategy.order("long", strategy.long, oca_name='audusdt',
        #                    when=BuyTrigger, limit=open)
        if buy_trigger and not_in_trade:
            broker.order(
                "long",
                "long",
                when=buy_trigger,
                limit=float(ctx["open"][i]),
            )

        # if (SellTrigger and inTrade)
        #     strategy.close(id="long", qty_percent=100)
        if sell_trigger and in_trade:
            broker.close("long")
