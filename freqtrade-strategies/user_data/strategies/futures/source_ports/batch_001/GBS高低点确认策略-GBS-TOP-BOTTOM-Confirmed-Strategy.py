"""Port of sources/SM_5e1b79318509a194.pine
(batch_001/GBS高低点确认策略-GBS-TOP-BOTTOM-Confirmed-Strategy.md).

Pine v5 (`//@version=5`, `strategy("GBS TOP BOTTOM Confirmed", overlay=true)`).
A swing-level strategy with no indicator at all: two `var` levels persist across
bars and are refreshed whenever a three-bar high/low pattern confirms.

    var float entryHigh = na
    var line entryLine = na
    entryCondition = high < high[1] and high[1] > high[2]
    if (entryCondition)
        entryHigh := high[1]

    buyCondition = not na(entryHigh) and high > entryHigh and open < entryHigh

    var float exitLow = na
    var line exitLine = na
    exitCondition = low > low[1] and low[1] < low[2]
    if (exitCondition)
        exitLow := low[1]

    sellCondition = not na(exitLow) and low < exitLow and open > exitLow

    strategy.entry("Buy", strategy.long, when = buyCondition)
    strategy.close("Buy", when = sellCondition)

The two `entryHigh` / `exitLow` assignments run BEFORE the two conditions are
evaluated on the same bar, so a confirmed level is live on the bar that
confirmed it. That is harmless here (see FIDELITY) but the port keeps the same
order rather than shifting the level by a bar.

`strategy()` declares only `title` and `overlay`, so every other property is
Pine's documented default: `default_qty_type=strategy.fixed`, `default_qty_value`
1 contract, initial capital 1000000, commission 0%, `pyramiding=0`,
`process_orders_on_close=false`, `margin_long`/`margin_short` unset.

The `/*backtest` header declares `period: 1d` on Futures_Binance BTC_USDT, so
`timeframe` is "1d"; `basePeriod: 1h` is the FMZ backtester's own fill
granularity for those daily bars, not the strategy's period.

`can_short` is False: the source has exactly one entry, and it is
`strategy.long`. `strategy.close` is a flat-only exit and does not make it
short. There is no stop / limit / trail anywhere, so `source_reproduce_stops` is
False and a position open at the window's end stays open.

FIDELITY:

* The `open < entryHigh` / `open > exitLow` guards read the CURRENT bar's open,
  while the order itself fills on the next bar's open (Pine evaluates the script
  at the close of bar t and the market order fills at the open of bar t+1). The
  engine models both halves; the port does not collapse them into one bar.
* On the bar that confirms a level, the level is set to `high[1]` / `low[1]`
  and evaluated in the same bar. It can never fire there: `entryCondition`
  requires `high < high[1] == entryHigh`, which contradicts `high > entryHigh`;
  symmetrically for the low side. The same-bar update is therefore a no-op for
  the order stream, and the port reproduces the source's order (assign, then
  test) instead of leaning on that argument.
* `high[2]` / `low[2]` are na on the first two bars. Pine v5 treats an na
  comparison as false in a boolean context; pandas yields False for the same
  comparisons, so bars 0 and 1 simply cannot confirm a level.
* `var line entryLine` / `var line exitLine` and the two `line.new(...)` calls
  are commented out in the source, and the four `plotshape(...)` calls are
  display-only. Neither is reproduced; `plotshape` places no order.
* The source never states `process_orders_on_close`, so its default (false)
  applies: signal at bar t's close, fill at bar t+1's open. The engine's order
  timing is exactly that.
* Leverage, margin, liquidation and funding are not modelled by the engine, and
  the venue's contract-step quantity rounding is not modelled either -- the
  chain verifier measures that rounding separately instead of absorbing it into
  a tolerance.
"""
from freqtrade.strategy import IStrategy

from pine_port_base import PinePortBase


class SMGbsTopBottomConfirmed_5e1b79(PinePortBase, IStrategy):
    source_id = "SM_5e1b79318509a194"
    source_file = "GBS高低点确认策略-GBS-TOP-BOTTOM-Confirmed-Strategy.md"
    timeframe = "1d"
    can_short = False
    # `strategy("GBS TOP BOTTOM Confirmed", overlay=true)` declares no input()
    # at all, so there is nothing to expose as source_defaults.
    source_defaults: dict = {}
    # Pine's documented defaults for the properties the source leaves unset.
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    # No stop / limit / trail leg exists in the source.
    source_reproduce_stops = False
    source_fidelity_notes = [
        "strategy() declares only title/overlay; qty_type=fixed, qty_value=1, "
        "initial_capital=1000000, commission=0%, pyramiding=0 and "
        "process_orders_on_close=false are Pine's defaults, not stated by the source.",
        "entryCondition/buyCondition and exitCondition/sellCondition read the "
        "CURRENT bar's open, while strategy.entry/close are market orders that "
        "fill on the NEXT bar's open. Both halves are kept distinct.",
        "entryHigh/exitLow are `var` levels refreshed by the same-bar assignment "
        "before the condition is tested; the port keeps that order. The "
        "same-bar case cannot fire (the confirm bar requires high < high[1]).",
        "The commented-out `line.new(...)` calls and `var line` declarations, "
        "and the four display-only plotshape() calls, are not reproduced.",
        "can_short is False: the only entry is strategy.long. strategy.close is "
        "a flat-only exit, not a short entry.",
        "No stop/limit/trail exists, so a position open at the end of the "
        "window stays open and source_reproduce_stops is False.",
        "Contract-step quantity rounding and leverage/margin/funding are not "
        "modelled; the chain verifier measures the rounding separately.",
    ]

    def pine_indicators(self, dataframe, params):
        high = dataframe["high"]
        low = dataframe["low"]
        open_ = dataframe["open"]

        # entryCondition = high < high[1] and high[1] > high[2]
        # exitCondition  = low  > low[1]  and low[1]  < low[2]
        prev_high = high.shift(1)
        prev_low = low.shift(1)
        entry_condition = (high < prev_high) & (prev_high > high.shift(2))
        exit_condition = (low > prev_low) & (prev_low < low.shift(2))

        # `if (entryCondition) entryHigh := high[1]` -- a var that keeps its last
        # assignment, i.e. a forward fill of high[1] over the confirming bars.
        # Before the first confirmation it stays na, which `not na(entryHigh)`
        # then reads as "no level yet".
        entry_high = prev_high.where(entry_condition).ffill()
        exit_low = prev_low.where(exit_condition).ffill()

        # buyCondition  = not na(entryHigh) and high > entryHigh and open < entryHigh
        # sellCondition = not na(exitLow)  and low  < exitLow  and open > exitLow
        buy_condition = entry_high.notna() & (high > entry_high) & (open_ < entry_high)
        sell_condition = exit_low.notna() & (low < exit_low) & (open_ > exit_low)

        dataframe["pine_entry_high"] = entry_high
        dataframe["pine_exit_low"] = exit_low
        dataframe["pine_buy_condition"] = buy_condition.fillna(False)
        dataframe["pine_sell_condition"] = sell_condition.fillna(False)
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "buy_condition": dataframe["pine_buy_condition"].to_numpy(dtype=bool),
            "sell_condition": dataframe["pine_sell_condition"].to_numpy(dtype=bool),
        }

    def pine_script(self, broker, i, ctx):
        # strategy.entry("Buy", strategy.long, when = buyCondition)
        if ctx["buy_condition"][i]:
            broker.entry("Buy", "long")
        # strategy.close("Buy", when = sellCondition)
        if ctx["sell_condition"][i]:
            broker.close("Buy")
