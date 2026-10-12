"""Port of sources/SM_bbd4852df0442d50.pine (batch_001/DAKELAX-XRPUSDT-波尔带回归均线策略DAKELAX-XRPUSDT-Bollinger-Band-Mean-Reversion-Strategy.md).

Pine v3. A one-sided Bollinger mean reversion: buy a fixed 20 contracts once
`close` falls below an ASYMMETRIC lower band, and unwind everything once
`close` rises above the upper band.

    out2       = sma(src2, len2)                     // src2 = input(close), len2 = 20
    dev        = stdev(src2, len2)                   // population stdev (ddof = 0)
    upper_BB   = out2 + 1.5 * dev
    lower_BB   = out2 - 2.2 * dev
    contraction = (upper_BB - lower_BB) / out2

    closesBelowLowerBB = close < lower_BB
    closesAboveUpperBB = close > upper_BB

    if closesBelowLowerBB
        strategy.order('Buy', strategy.long, buyAmount)   // buyAmount = input(20, minval=1)
    if closesAboveUpperBB
        strategy.close_all()

THE TWO MULTIPLIERS ARE NOT THE SAME: the upper band is 1.5 deviations out and
the lower band 2.2, so the channel is deliberately lopsided and the entry is a
much rarer event than the exit. Reproduced exactly.

WHAT IS **NOT** TRADED, and is still reproduced into the frame so the
translation is on the record: `fastMA`/`slowMA` (7/18 EMA) and their
`crossUp`/`crossDown`, the `buySignal`/`shortSignal` that combine them with
`low > slowMA` / `high < slowMA`, `signalBuy`/`signalSell`, the alternating
`test := not test[1]`, `contraction_value` / `contraction_value2`,
`isInRed` / `isInYellow`, `bgColour` and `tmptext`. Every one of them is
computed by the source and then never read by an order call -- the md's prose
("双均线交叉回撤买入") describes an MA-crossover strategy that this code does
not trade. The code is followed; the disagreement is recorded, not reconciled.

There is no short entry anywhere in the source and no stop / limit / trail
exit, so `can_short` is False and `source_reproduce_stops` is False.

`strategy()` declares only `title` and `overlay`, so every property is Pine's
default: `strategy.fixed` / 1 contract, commission 0%, pyramiding 0,
`process_orders_on_close=false`. It declares no `initial_capital`; v3 does not
publish one in the source, and this harness's convention for an undeclared
capital is 1000000, which is what `source_initial_capital` carries. It cannot
change a trade here beyond the framework's wallet size, because every order
passes `qty=buyAmount` (20) explicitly and `default_qty_type` never applies.

FIDELITY:

* The buy is `strategy.order`, not `strategy.entry`. `strategy.order` is the
  unconditional order form and does not carry the entry id semantics
  `strategy.entry` does; the engine's `order()` is routed through `entry()`,
  which is where Pine's own netting behaviour lives, so the translation matches
  for a one-directional source such as this one.
* `strategy.order` is re-issued on EVERY bar the condition holds, but Pine's
  `pyramiding` default of 0 refuses any additional entry in the same direction
  while one is held. The engine models that at order-CREATION time
  (`_can_add` / `entry_will_fill`), so the repeated orders neither fill nor
  become framework signals. Without that gate this source would stack 20
  contracts per bar.
* `closesAboveUpperBB -> strategy.close_all()` closes every open entry, which
  is what `broker.close_all` does. `close_all` is unconditional in the engine
  when no position is held, matching Pine's no-op there.
* `stdev` in Pine v3 is the population standard deviation, which
  `pine_ta.pine_stdev` computes with `ddof=0`. Using a sample stdev
  (`ddof=1`) would widen both bands by ~2.6% at len 20 and change which bars
  signal.
* `contraction` divides by `out2`, which is na for the first `len2 - 1` bars;
  that propagates na into the fill colour, which is display-only and not
  reproduced. The two `isInRed` / `isInYellow` flags derive from the same
  contraction and are likewise never read.
* The source's own name and comment call the instrument XRPUSDT
  ("Tradebotler DAKELAX Binance:XRPUSDT"), but the `/*backtest` header declares
  `currency: BTC_USDT` and that is what the chain verifier trades. Recorded,
  not changed.
* `timeframe` is the header's `period: 1d`, not the `basePeriod: 1h`, which is
  the FMZ backtester's own fill granularity.
* No `request.security`, no barstate branch, no `varip`, no `strategy.risk.*`,
  no pyramiding and no leverage in the source.
* Leverage, margin, liquidation, funding and the venue's contract-step rounding
  are not modelled; the chain verifier measures the step rounding separately
  (PINE_SEMANTICS.md 1.6).
"""
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


class SMDakelaxXrpusdt_bbd485(PinePortBase, IStrategy):
    source_id = "SM_bbd4852df0442d50"
    source_file = "DAKELAX-XRPUSDT-波尔带回归均线策略DAKELAX-XRPUSDT-Bollinger-Band-Mean-Reversion-Strategy.md"
    timeframe = "1d"
    can_short = False
    source_defaults: dict = {
        "buyAmount": 20,
        "len2": 20,
        "src2": "close",
    }
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    source_reproduce_stops = False
    source_fidelity_notes = [
        "The 7/18 EMA cross, its `buySignal` / `shortSignal`, `signalBuy` / "
        "`signalSell`, `test := not test[1]`, `contraction_value` / "
        "`contraction_value2`, `isInRed` / `isInYellow`, `bgColour` and "
        "`tmptext` are all computed by the source and NEVER read by an order "
        "call. They are recomputed here as frame columns so the translation is "
        "on the record, and are NOT wired to any order. The md's prose "
        "describes an MA-crossover entry; the code trades the Bollinger bands "
        "instead. Code followed, disagreement recorded.",
        "The channel is asymmetric on purpose: upper = out2 + 1.5*dev, "
        "lower = out2 - 2.2*dev. Not normalised to a symmetric band.",
        "`stdev` is Pine v3's population standard deviation; pine_stdev is "
        "ddof=0. A sample stdev would widen both bands and move the signals.",
        "The buy is re-issued every bar the condition holds. Pine's pyramiding "
        "default of 0 refuses the repeated same-direction entries; the engine "
        "models that refusal at order-creation time (PINE_SEMANTICS.md 1.12 "
        "records that same-id stop/limit entries accumulate, but this source "
        "places MARKET orders, which are decided by `_can_add` and dropped).",
        "`strategy.close_all()` is unconditional in the engine when flat, which "
        "matches Pine's no-op. Nothing is netted against a short, because the "
        "source never opens one -- `can_short` is False.",
        "Orders pass `qty=buyAmount` (20) explicitly, so `default_qty_type` / "
        "`default_qty_value` never apply. `source_qty_type` is recorded as "
        "Pine v3's default (`strategy.fixed`, 1) for provenance only.",
        "`strategy()` declares no `initial_capital`. 1000000 is this harness's "
        "convention for an undeclared capital; the source publishes no v3 "
        "default. It can only change the framework's wallet, not a trade.",
        "The md's title and the source's own comment name the instrument "
        "XRPUSDT, but the `/*backtest` header declares `currency: BTC_USDT`, "
        "which is what the verifier trades.",
        "No short entry and no stop/limit/trail exit exist, so can_short is "
        "False and source_reproduce_stops is False.",
        "`sma` and `stdev` are na until `len2` bars have elapsed, and na "
        "comparisons are false, so `close < lower_BB` / `close > upper_BB` "
        "cannot fire in the first 19 bars.",
        "Leverage, margin, liquidation, funding and contract-step rounding are "
        "not modelled; the venue's rounding is measured by the chain verifier "
        "rather than hidden here.",
    ]

    def pine_indicators(self, dataframe, params):
        close = dataframe["close"]
        src2 = close  # src2 = input(close): the default is the close series
        len2 = int(params["len2"])

        out2 = ta.pine_sma(src2, len2)
        dev = ta.pine_stdev(src2, len2)
        upper_bb = out2 + 1.5 * dev
        lower_bb = out2 - 2.2 * dev
        contraction = (upper_bb - lower_bb) / out2

        closes_below_lower = close < lower_bb
        closes_above_upper = close > upper_bb

        # Computed by the source and never read by an order call. Reproduced so
        # the translation is on the record; NOT wired to any order below.
        fast_ma = ta.pine_ema(close, 7)
        slow_ma = ta.pine_ema(close, 18)
        cross_up = ta.pine_crossover(fast_ma, slow_ma)
        cross_down = ta.pine_crossunder(fast_ma, slow_ma)
        # `crossUp[1]` / `crossDown[1]` are na on the first bar, and an na in a
        # boolean context is false, so the shifted term is filled False.
        cross_up_lag = cross_up.shift(1, fill_value=False).astype(bool)
        cross_down_lag = cross_down.shift(1, fill_value=False).astype(bool)
        buy_signal = (cross_up | cross_up_lag) & (dataframe["low"] > slow_ma)
        short_signal = (cross_down | cross_down_lag) & (dataframe["high"] < slow_ma)
        contraction_value = 1.3
        contraction_value2 = 0.1
        is_in_red = (contraction < contraction_value) & (contraction >= contraction_value2)
        is_in_yellow = (contraction < contraction_value) & (contraction < contraction_value2)

        dataframe["pine_out2"] = out2
        dataframe["pine_dev"] = dev
        dataframe["pine_upper_bb"] = upper_bb
        dataframe["pine_lower_bb"] = lower_bb
        dataframe["pine_contraction"] = contraction
        dataframe["pine_closes_below_lower_bb"] = closes_below_lower
        dataframe["pine_closes_above_upper_bb"] = closes_above_upper
        # unused by the order stream -- see the fidelity notes
        dataframe["pine_fast_ma"] = fast_ma
        dataframe["pine_slow_ma"] = slow_ma
        dataframe["pine_cross_up"] = cross_up
        dataframe["pine_cross_down"] = cross_down
        dataframe["pine_buy_signal"] = buy_signal
        dataframe["pine_short_signal"] = short_signal
        dataframe["pine_is_in_red"] = is_in_red
        dataframe["pine_is_in_yellow"] = is_in_yellow
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "below_lower": dataframe["pine_closes_below_lower_bb"].to_numpy(),
            "above_upper": dataframe["pine_closes_above_upper_bb"].to_numpy(),
            "buy_amount": float(params["buyAmount"]),
        }

    def pine_script(self, broker, i, ctx):
        # if ( closesBelowLowerBB )
        #     strategy.order('Buy', strategy.long, buyAmount)
        if ctx["below_lower"][i]:
            broker.order("Buy", "long", qty=ctx["buy_amount"])
        # if ( closesAboveUpperBB )
        #     strategy.close_all()
        if ctx["above_upper"][i]:
            broker.close_all()
