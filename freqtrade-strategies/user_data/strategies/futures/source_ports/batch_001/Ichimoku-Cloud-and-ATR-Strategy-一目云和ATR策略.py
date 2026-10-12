"""Port of sources/SM_02478f46120a9432.pine
(batch_001/Ichimoku-Cloud-and-ATR-Strategy-一目云和ATR策略.md).

Pine v4. Ichimoku lines built from a plain `sma`, cloud-relative signals, and
a resting stop that is both the entry's trigger and its protective exit.
Reproduced call for call, in the source's own order:

    conversion = sma((high + low) / 2, conversionPeriod)          // 9
    base       = sma((high + low) / 2, basePeriod)                // 26
    leadSpanA  = avg(conversion, base)
    leadSpanB  = sma(high + low + close, leadSpanBPeriod) / 3     // 52
    atr        = atr(atrPeriod)                                   // 14
    atrStop    = atr * atrMultiplier                              // 2

    aboveCloud = close > leadSpanA and close > leadSpanB
    belowCloud = close < leadSpanA and close < leadSpanB
    longSignal  = aboveCloud  and (close > high[1] or high > high[1])
    shortSignal = belowCloud and (close < low[1]  or low  < low[1])

    if longSignal
        strategy.entry("Buy",  strategy.long,  stop=leadSpanA - atrStop)
    if shortSignal
        strategy.entry("Sell", strategy.short, stop=leadSpanA + atrStop)

    strategy.exit("Exit", "Buy",  stop=leadSpanA - atrStop)
    strategy.exit("Exit", "Sell", stop=leadSpanA + atrStop)

Both entries are STOP orders, which is the framework boundary of
PINE_SEMANTICS.md 2.11 and is recorded rather than papered over: the engine
models a resting order that fills on a later bar when the price reaches the
level, while `run_pine` can only project it as a next-open market entry on the
bar it was PLACED. The two coincide only when the next bar's open is at or
through the level. Note the two arms are not symmetric in the source either:
`leadSpanA - atrStop` sits BELOW the market on a long signal, so the buy stop
is reached at (or immediately after) the next open and usually behaves like a
market order, whereas `leadSpanA + atrStop` sits ABOVE the market on a short
signal, so the sell stop genuinely rests until price rallies into it.

The two `strategy.exit` calls carry the SAME order id ("Exit") and differ only
in `from_entry`, and both are unconditional (no `when=`). The engine keeps one
resting order per id for `kind == 'exit'`, so the second call replaces the
first and only the "Sell"-bound arm ever rests; while a long is open that arm's
`from_entry` is not, so it is a no-op and the engine publishes no stop for the
long. This is the engine's settled reading of Pine's one-order-per-id rule
(PINE_SEMANTICS.md 3.6), recorded on this port rather than worked around: the
source text is transcribed as written, in order, without adding position guards
that would let the long arm rest and change the strategy.

FIDELITY:

* The Ichimoku lines are NOT the standard ones: the source uses
  `sma((high + low) / 2, n)` where TradingView's `ta.ichimoku` uses a rolling
  MIDPOINT (`(highest(high, n) + lowest(low, n)) / 2`), and `leadSpanB` is an
  `sma` of `high + low + close` divided by 3 rather than the 52-bar midpoint of
  `high` / `low`. The source's formulas are followed exactly and no library
  Ichimoku is substituted (rule 3).
* `leadSpanA` / `leadSpanB` are used RAW: the source never shifts them forward
  (`offset` / `senkou` displacement), so there is no future-data reference and
  no repaint introduced by this port. If the author intended the classical
  26-bar forward displacement, the source does not ask for it and the port does
  not add it.
* `longSignal`'s second clause `(close > high[1] or high > high[1])` is a
  union, not a conjunction: since `high >= close` on a bar, `high > high[1]`
  alone is enough, so the close-based clause is nearly dead. It is reproduced
  as written, both clauses.
* `atr()` in Pine v4 is `rma(tr, length)`, and v4's `tr` is defined with the
  first bar's `close[1]` treated as the bar itself, so the ATR is seeded on bar
  0. `pine_ta.pine_atr` models that (`handle_na=True`); PINE_SEMANTICS.md 3.7
  records that v5's default `ta.tr` instead returns na on the first bar and
  that the resulting one-bar seeding offset is a public-layer boundary, not a
  port choice. The ATR here feeds the stop levels, so the note is live.
* `strategy()` declares only `title` and `overlay`, so every property is Pine's
  documented default: strategy.fixed / 1 contract, initial capital 1000000,
  commission 0%, pyramiding 0, `process_orders_on_close=false`. Neither entry
  passes a `qty`, and neither exit passes `qty` / `qty_percent` either.
* No `strategy.close` and no leg-less `strategy.exit` exists, so
  PINE_SEMANTICS.md 1.15 does not apply.
* `plot()` is display-only and is not reproduced.
* The `/*backtest` header's `basePeriod: 1h` is the FMZ backtester's own
  granularity for filling the 1d bars, not the strategy's period.
* Leverage, margin, liquidation, funding and the venue's contract-step rounding
  are not modelled; the chain verifier measures the last one separately
  (PINE_SEMANTICS.md 1.6).
"""
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


class SMIchimokuCloudAndAtr_02478f(PinePortBase, IStrategy):
    source_id = "SM_02478f46120a9432"
    source_file = "Ichimoku-Cloud-and-ATR-Strategy-一目云和ATR策略.md"
    timeframe = "1d"
    can_short = True
    source_defaults: dict = {
        "conversionPeriod": 9,
        "basePeriod": 26,
        "leadSpanBPeriod": 52,
        "atrPeriod": 14,
        "atrMultiplier": 2,
    }
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    # The source's protective exits are `strategy.exit(..., stop=...)` legs, so
    # the engine publishes a resting stop level for the open position.
    source_reproduce_stops = True
    source_mintick = 0.1
    source_fidelity_notes = [
        "Both entries are STOP orders (strategy.entry(..., stop=...)), which a "
        "Freqtrade strategy cannot place: run_pine projects the order as a "
        "next-open market entry on the bar it was PLACED, while the engine fills "
        "it inside a later bar when the price reaches the level (PINE_SEMANTICS.md "
        "2.11). The engine ledger is the faithful reproduction; the framework "
        "side is a projection with that known limit. The short side is the one "
        "that really rests -- leadSpanA + atrStop is ABOVE the market on a short "
        "signal -- while the long side's stop sits below the market and is "
        "usually reached at the next open.",
        "The Ichimoku lines are not the standard ones. The source uses "
        "sma((high + low) / 2, n) for conversion / base where ta.ichimoku uses a "
        "rolling midpoint (highest + lowest) / 2, and leadSpanB is "
        "sma(high + low + close, n) / 3 rather than a 52-bar midpoint of high / "
        "low. The source's formulas are followed exactly; no library Ichimoku is "
        "substituted (rule 3).",
        "leadSpanA / leadSpanB are used raw: the source never applies the "
        "classical 26-bar forward displacement, so this port introduces no "
        "future-data reference and no repaint. If the author intended the "
        "displacement, the source does not ask for it.",
        "longSignal's second clause is a union, not a conjunction: "
        "(close > high[1] or high > high[1]). Because high >= close on a bar, "
        "the high-based clause alone almost always decides it, leaving the "
        "close-based clause nearly dead. Reproduced as written, both clauses.",
        "Both strategy.exit calls share the order id 'Exit' and differ only in "
        "from_entry, and both are unconditional. The engine keeps one resting "
        "order per id for kind == 'exit', so the second call replaces the first "
        "and only the Sell-bound arm ever rests; while a long is open that arm's "
        "from_entry is not open, so it is a no-op and the engine publishes NO "
        "stop for the long (PINE_SEMANTICS.md 3.6). The source text is "
        "transcribed as written, in order; no position guard was added, because "
        "that would let the long arm rest and change the strategy. If the "
        "original platform keys exit orders by (id, from_entry) instead, longs "
        "would carry a stop at leadSpanA - atrStop and the trade list would "
        "differ. The engine is the ledger of record; the risk is recorded, not "
        "resolved.",
        "strategy() declares only title and overlay, so every property is Pine's "
        "documented default: strategy.fixed / 1 contract, initial capital "
        "1000000, commission 0%, pyramiding 0, process_orders_on_close=false. "
        "Neither entry passes a qty and neither exit passes qty / qty_percent.",
        "atr() in Pine v4 is rma(tr, length) with the first bar's close[1] "
        "treated as the bar itself, so the ATR is seeded on bar 0; "
        "pine_ta.pine_atr models that. PINE_SEMANTICS.md 3.7 records that v5's "
        "default ta.tr returns na on the first bar instead, and that the "
        "resulting one-bar seeding offset is a public-layer boundary. The ATR "
        "here feeds the stop levels, so the note is live.",
        "There is no strategy.close and no leg-less strategy.exit, so "
        "PINE_SEMANTICS.md 1.15 does not apply. plot() is display-only and is "
        "not reproduced.",
        "The /*backtest header's basePeriod: 1h is the FMZ backtester's own "
        "granularity for filling the 1d bars, not the strategy's period.",
        "Leverage, margin, liquidation, funding and the venue's contract-step "
        "rounding are not modelled; the chain verifier measures the last one "
        "separately (PINE_SEMANTICS.md 1.6).",
    ]

    def pine_indicators(self, dataframe, params):
        high = dataframe["high"]
        low = dataframe["low"]
        close = dataframe["close"]

        midpoint = (high + low) / 2.0
        conversion = ta.pine_sma(midpoint, int(params["conversionPeriod"]))
        base = ta.pine_sma(midpoint, int(params["basePeriod"]))
        lead_span_a = (conversion + base) / 2.0
        lead_span_b = (
            ta.pine_sma(high + low + close, int(params["leadSpanBPeriod"])) / 3.0
        )
        atr_stop = ta.pine_atr(
            dataframe, int(params["atrPeriod"])
        ) * float(params["atrMultiplier"])

        above_cloud = (close > lead_span_a) & (close > lead_span_b)
        below_cloud = (close < lead_span_a) & (close < lead_span_b)
        high_1 = high.shift(1)
        low_1 = low.shift(1)
        long_signal = above_cloud & ((close > high_1) | (high > high_1))
        short_signal = below_cloud & ((close < low_1) | (low < low_1))

        dataframe["pine_conversion"] = conversion
        dataframe["pine_base"] = base
        dataframe["pine_lead_span_a"] = lead_span_a
        dataframe["pine_lead_span_b"] = lead_span_b
        dataframe["pine_atr_stop"] = atr_stop
        dataframe["pine_long_signal"] = long_signal.fillna(False)
        dataframe["pine_short_signal"] = short_signal.fillna(False)
        dataframe["pine_long_stop"] = lead_span_a - atr_stop
        dataframe["pine_short_stop"] = lead_span_a + atr_stop
        return dataframe

    def pine_context(self, dataframe, params):
        del params
        return {
            "long_signal": dataframe["pine_long_signal"].to_numpy(),
            "short_signal": dataframe["pine_short_signal"].to_numpy(),
            "long_stop": dataframe["pine_long_stop"].to_numpy(),
            "short_stop": dataframe["pine_short_stop"].to_numpy(),
        }

    def pine_script(self, broker, i, ctx):
        # if longSignal
        #     strategy.entry("Buy", strategy.long, stop=leadSpanA - atrStop, comment="Long")
        if ctx["long_signal"][i]:
            broker.entry("Buy", "long", stop=float(ctx["long_stop"][i]))
        # if shortSignal
        #     strategy.entry("Sell", strategy.short, stop=leadSpanA + atrStop, comment="Short")
        if ctx["short_signal"][i]:
            broker.entry("Sell", "short", stop=float(ctx["short_stop"][i]))
        # strategy.exit("Exit", "Buy", stop=leadSpanA - atrStop)
        broker.exit("Exit", from_entry="Buy", stop=float(ctx["long_stop"][i]))
        # strategy.exit("Exit", "Sell", stop=leadSpanA + atrStop)
        broker.exit("Exit", from_entry="Sell", stop=float(ctx["short_stop"][i]))
