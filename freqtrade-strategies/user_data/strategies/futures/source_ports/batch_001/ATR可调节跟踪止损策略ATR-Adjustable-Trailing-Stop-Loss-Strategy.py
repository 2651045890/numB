"""Port of sources/SM_a1e9fd644f531b4a.pine (batch_001/ATR可调节跟踪止损策略ATR-Adjustable-Trailing-Stop-Loss-Strategy.md).

Pine v4, `//@version=4`, `strategy("ATR Trailing Stoploss Strategy ",
overlay=true)`. A rolling ATR-offset line over the highs, used purely as a
crossover/crossunder signal -- despite the title it arms no stop order:

    Atr  = input(defval=5,   minval=1,   maxval=500)   // Atr Period
    Hhv  = input(defval=10,  minval=1,   maxval=500)   // HHV Period
    Mult = input(defval=2.5, minval=0.1)               // Multiplier
    Barcolor = input(true)                             // Barcolor

    TS = highest(high - Mult * atr(Atr), Hhv)

    Barcolor ? Color : na                              // display-only
    plot(TS, color=Color, linewidth=3)                 // display-only

    Buy  = crossover(close, TS)
    Sell = crossunder(close, TS)

    if Buy
        strategy.entry("Buy", strategy.long, comment="Buy")
    if Sell
        strategy.entry("Sell", strategy.short, comment="Sell")

`TS` is a ROLLING `highest` over `Hhv` bars, not a ratcheting trailing stop:
it can fall as well as rise, because the window drops old highs. The source's
own markdown calls it a dynamic stop line, but no order rests at it -- it only
ever reaches the two crossings above. The engine therefore has nothing to mirror
into Freqtrade's stop machinery and `source_reproduce_stops` is False.

The source line 20 reads

    TS=highest(high-Mult*atr(Atr),Hhv),barssince(close>highest(high-Mult*atr(Atr),Hhv) and close>close)

The comma-separated second expression has no assignment target and is read by
nothing later in the script. Its own inner condition (`close>close`) is always
false, so `barssince` of it would be na on every bar even if it were bound. The
port carries `TS` alone; see FIDELITY.

`strategy()` declares only `title` / `overlay`, so Pine's documented defaults
apply and are what this port carries: `default_qty_type=fixed`, one unit per
order, `commission_value=0`, `pyramiding=0`, `process_orders_on_close=false`,
initial capital 1000000.

The `/*backtest` header declares `period: 30m` on Futures_Binance BTC_USDT, so
`timeframe` is "30m"; its `basePeriod: 15m` is the FMZ backtester's own filling
granularity for those 30m bars, not the strategy's period. There is no local 30m
futures history, so the chain verifier reports `skipped_no_local_data`.

FIDELITY:

* The unbound `barssince(...)` on the `TS=` line is dead code -- nothing reads
  it, and its condition `close>close` is always false. It is recorded, not
  reproduced. Dropping it changes no order.
* The md's prose ("止损线是动态调整的,能够跟踪价格上涨后的最高点 ... 当价格下跌时,
  止损线会保持之前的高点") describes a ratcheting line that never falls. The
  source's `highest(...)` is a rolling window: it drops old highs and therefore
  DOES fall. The source is reproduced; the prose is not.
* `atr(Atr)` is v4 `rma(tr, Atr)` with the first bar's true range taken as
  `high - low` (pine_ta.pine_atr). PINE_SEMANTICS.md section 3.7 records the
  one-bar seeding difference against `ta.tr`'s own na rule.
* `Barcolor` is a bool input used only as a bare condition (`Barcolor ? Color :
  na`), never in a numeric context, so no section-1.16 bool-as-number hazard
  applies; the port does not compare it to 0 or 1. `Color` and `barcolor(...)`
  are display-only.
* The two `strategy.entry` calls carry `comment="Buy"` / `"Sell"`, which is
  display metadata only and places no order.
* Leverage, margin, liquidation and funding are not modelled; the venue's
  contract-step rounding is not modelled either, so the framework and the
  engine can differ by a rounded quantity (measured separately by the chain
  verifier rather than treated as a signal difference).
"""
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


class SMATRAdjustableTrailingStopLoss_a1e9fd(PinePortBase, IStrategy):
    source_id = "SM_a1e9fd644f531b4a"
    source_file = "ATR可调节跟踪止损策略ATR-Adjustable-Trailing-Stop-Loss-Strategy.md"
    timeframe = "30m"
    can_short = True
    source_defaults: dict = {"Atr": 5, "Hhv": 10, "Mult": 2.5, "Barcolor": True}
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    # TS is a signal line, not a resting order; the source has no strategy.exit
    # and no strategy.close, so a position only leaves by the opposite entry
    # reversing it.
    source_reproduce_stops = False
    source_fidelity_notes = [
        "TS is a rolling ta.highest over Hhv bars, not a ratcheting trailing "
        "stop: it can fall when old highs leave the window. No order rests at "
        "it, so it only ever reaches the two crossings.",
        "The unbound `barssince(close>highest(...) and close>close)` tail on the "
        "`TS=` line is dead code -- nothing reads it and `close>close` is always "
        "false. Recorded, not reproduced; no order changes.",
        "The md describes a line that never falls on a pullback; the source's "
        "rolling highest does. Source reproduced, prose recorded.",
        "atr(Atr) is modelled as v4 rma(tr, Atr) with the first bar's range "
        "taken as high - low (pine_ta.pine_atr); PINE_SEMANTICS.md section 3.7.",
        "Barcolor is a bool input used only as a bare condition, so no "
        "section-1.16 bool-as-number hazard applies; Color/barcolor are "
        "display-only and are not reproduced.",
        "There is no exit call in the source; source_reproduce_stops is False "
        "and a position open at the end of the window stays open.",
        "comment=\"Buy\"/\"Sell\" on the entries is display metadata only.",
        "Leverage, margin, liquidation, funding and venue contract-step "
        "rounding are not modelled.",
    ]

    def pine_indicators(self, dataframe, params):
        high = dataframe["high"]
        close = dataframe["close"]
        atr_period = int(params["Atr"])
        hhv_period = int(params["Hhv"])
        mult = float(params["Mult"])

        # TS = highest(high - Mult * atr(Atr), Hhv)
        atr = ta.pine_atr(dataframe, atr_period)
        trailing_line = ta.pine_highest(high - mult * atr, hhv_period)

        dataframe["pine_atr_trailing_line"] = trailing_line
        dataframe["pine_buy_signal"] = ta.pine_crossover(close, trailing_line)
        dataframe["pine_sell_signal"] = ta.pine_crossunder(close, trailing_line)
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "buy_signal": dataframe["pine_buy_signal"].to_numpy(),
            "sell_signal": dataframe["pine_sell_signal"].to_numpy(),
        }

    def pine_script(self, broker, i, ctx):
        # if Buy
        #     strategy.entry("Buy", strategy.long, comment="Buy")
        if ctx["buy_signal"][i]:
            broker.entry("Buy", "long")
        # if Sell
        #     strategy.entry("Sell", strategy.short, comment="Sell")
        if ctx["sell_signal"][i]:
            broker.entry("Sell", "short")
