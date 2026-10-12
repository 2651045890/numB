"""Port of sources/SM_87942f41e2081e52.pine (batch_001/Bollinger带均值回归交易策略Bollinger-Band-Mean-Reversion-Trading-Strategy.md).

Pine v4, `//@version=4`, `strategy("Mean Reversion with Risk Management",
overlay=true)`. A Bollinger mean-reversion entry whose two legs -- the BUY
order AND its stop/limit pair -- are one call:

    length = input(20, minval=1)          // Bollinger Bands Length
    mult   = input(2.0)                   // Bollinger Bands Multiplier
    stopLossATRMult   = input(2.0)        // Stop Loss ATR Multiplier
    takeProfitATRMult = input(3.0)        // Take Profit ATR Multiplier

    src   = close
    basis = sma(src, length)
    dev   = mult * stdev(src, length)     // population stdev (ddof=0)
    upper = basis + dev
    lower = basis - dev

    atr = atr(14)                         // v4 atr = rma(tr, 14)

    longCondition  = crossover(src, lower)
    shortCondition = crossunder(src, upper)

    if (longCondition)
        sl = src - stopLossATRMult * atr
        tp = src + takeProfitATRMult * atr
        strategy.entry("Long", strategy.long, stop=sl, limit=tp)

    if (shortCondition)
        sl = src + stopLossATRMult * atr
        tp = src - takeProfitATRMult * atr
        strategy.entry("Short", strategy.short, stop=sl, limit=tp)

BOTH legs of each `strategy.entry` carry `stop=` and `limit=`, so these are
RESTING stop-limit ENTRY orders, not next-open market orders: the long is a
stop-buy whose trigger sits `2*atr` BELOW the signal bar's close and whose limit
sits `3*atr` ABOVE it. Pine triggers the stop first and the limit is then
marketable, so the order fills at the trigger, not at the limit. The engine
models that (`_price_order_fill`: a `stop` entry resolves through the stop leg;
the limit is only carried). With `stop=na` -- which is what `2.0 * atr` is while
`atr(14)` is still na -- Pine places no stop and no limit and the call degrades
to a market order; the port guards the same way.

This is the framework boundary PINE_SEMANTICS.md section 2.11 records: the
signal projection can only fire `enter_long` / `enter_short` on the bar the
order was PLACED, and a framework with no resting entry orders fills it at the
next open. Here the boundary happens not to bite, and the reason is worth
stating rather than assuming: the trigger sits on the MARKETABLE side of the
close, so on the very next bar `_price_order_fill` finds `high >= stop` and
fills at `max(stop, open_)`, which is that bar's open -- the same bar and the
same price Freqtrade uses. Measured on the local BTC/USDT:USDT 1d history: all
139 stop-limit entries, 49 of which filled, filled on exactly the next bar and
at exactly that bar's open. The boundary is still structural -- it bites when
the offset puts the trigger beyond the current price, as it does in section
2.11's own measurement -- so `match` here is a property of this source's
offset, not a claim that resting entry orders are expressible in Freqtrade.

There is no `strategy.exit` and no `strategy.close` anywhere in the source: a
position is only ever closed by the opposite entry reversing it. `atr` and the
two ATR multiples exist solely to price the two entry legs. `source_reproduce_stops`
is therefore False -- the engine has no exit order to mirror into the
framework's stop machinery.

`strategy()` declares only `title` / `overlay`, so Pine's documented defaults
apply and are what this port carries: `default_qty_type=fixed`, one unit per
order, `commission_value=0`, `pyramiding=0`, `process_orders_on_close=false`,
initial capital 1000000.

The `/*backtest` header declares `period: 1d` on Futures_Binance BTC_USDT, so
`timeframe` is "1d"; its `basePeriod: 1h` is the FMZ backtester's own filling
granularity for those daily bars, not the strategy's period.

FIDELITY:

* The md's prose says the stop is set "价格突破均线时的价格再减去2倍ATR" / "at
  price breaking the moving average minus 2 times ATR", i.e. anchored to
  `basis`. The source anchors BOTH legs to `src` (= `close`), never to `basis`.
  The source is the authority (iron rule 2); the prose discrepancy is recorded
  here and the code is not changed.
* `stdev` is Pine's population standard deviation (ddof=0), which is what
  pine_ta.pine_stdev computes. A sample stdev would widen both bands.
* `atr(14)` in v4 is `rma(tr, 14)` with the first bar's true range taken as
  `high - low`; pine_ta.pine_atr is that form. PINE_SEMANTICS.md section 3.7
  records that `ta.tr`'s own first-bar na rule differs by one bar, which shifts
  only the ATR seeding point.
* `sma` / `stdev` return na until their window is full, and `crossover` against
  an na operand is false in Pine; pine_ta.pine_sma / pine_stdev / pine_crossover
  reproduce both, so the first signal cannot arrive before bar `length`.
* `plot(upper, ...)` / `plot(lower, ...)` and the strategy title are
  display-only and are not reproduced.
* A na `stop` / `limit` places no order on the original platform, so the port
  guards identically instead of passing nan into the engine.
* Leverage, margin, liquidation and funding are not modelled; the venue's
  contract-step rounding is not modelled either, so the framework and the
  engine can differ by a rounded quantity (measured separately by the chain
  verifier rather than treated as a signal difference).
"""
import numpy as np

from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


class SMBollingerBandMeanReversion_87942f(PinePortBase, IStrategy):
    source_id = "SM_87942f41e2081e52"
    source_file = "Bollinger带均值回归交易策略Bollinger-Band-Mean-Reversion-Trading-Strategy.md"
    timeframe = "1d"
    can_short = True
    source_defaults: dict = {
        "length": 20,
        "mult": 2.0,
        "stopLossATRMult": 2.0,
        "takeProfitATRMult": 3.0,
    }
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    # No strategy.exit / strategy.close in the source: the only way out of a
    # position is the opposite entry reversing it.
    source_reproduce_stops = False
    source_fidelity_notes = [
        "Both entries use strategy.entry(stop=..., limit=...) -- resting "
        "stop-limit ENTRY orders. Freqtrade cannot be handed a resting entry "
        "order, so the projection fires the entry on the placement bar and the "
        "framework fills at the next open. PINE_SEMANTICS.md section 2.11. On "
        "the local 1d history the trigger is on the marketable side of the "
        "close, so the engine fills at the same next open: 49 of 139 entries "
        "filled, all on the next bar and all at that bar's open.",
        "The md's prose anchors the stop/take-profit to the Bollinger basis "
        "('price breaking the moving average minus 2x ATR'); the source anchors "
        "both to src (= close). The source is reproduced; the discrepancy is "
        "recorded, not reconciled.",
        "For a long stop-limit, Pine triggers at the stop and then fills at the "
        "marketable limit, i.e. at the trigger; the engine resolves the order "
        "through its stop leg and carries the limit. Same fill price.",
        "stdev is the population form (ddof=0), as Pine ta.stdev computes it.",
        "atr(14) is v4 rma(tr, 14) with the first bar's range taken as "
        "high - low (pine_ta.pine_atr). PINE_SEMANTICS.md section 3.7.",
        "There is no exit call in the source; source_reproduce_stops is False "
        "and a position open at the end of the window stays open.",
        "A na stop/limit price places no order on the original platform; the "
        "port guards identically instead of passing nan to the engine.",
        "plot() calls, the strategy title and overlay are display-only and are "
        "not reproduced.",
        "Leverage, margin, liquidation, funding and venue contract-step "
        "rounding are not modelled.",
    ]

    def pine_indicators(self, dataframe, params):
        close = dataframe["close"]
        length = int(params["length"])
        mult = float(params["mult"])
        stop_mult = float(params["stopLossATRMult"])
        take_mult = float(params["takeProfitATRMult"])

        # src = close; basis = sma(src, length); dev = mult * stdev(src, length)
        basis = ta.pine_sma(close, length)
        dev = mult * ta.pine_stdev(close, length)
        upper = basis + dev
        lower = basis - dev

        # atr = atr(14)  -- v4 atr is rma(tr, 14)
        atr = ta.pine_atr(dataframe, 14)

        long_condition = ta.pine_crossover(close, lower)
        short_condition = ta.pine_crossunder(close, upper)

        # sl = src -/+ stopLossATRMult * atr ; tp = src +/- takeProfitATRMult * atr
        dataframe["pine_basis"] = basis
        dataframe["pine_upper"] = upper
        dataframe["pine_lower"] = lower
        dataframe["pine_atr"] = atr
        dataframe["pine_long_condition"] = long_condition
        dataframe["pine_short_condition"] = short_condition
        dataframe["pine_long_stop"] = close - stop_mult * atr
        dataframe["pine_long_limit"] = close + take_mult * atr
        dataframe["pine_short_stop"] = close + stop_mult * atr
        dataframe["pine_short_limit"] = close - take_mult * atr
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "long_condition": dataframe["pine_long_condition"].to_numpy(),
            "short_condition": dataframe["pine_short_condition"].to_numpy(),
            "long_stop": dataframe["pine_long_stop"].to_numpy(),
            "long_limit": dataframe["pine_long_limit"].to_numpy(),
            "short_stop": dataframe["pine_short_stop"].to_numpy(),
            "short_limit": dataframe["pine_short_limit"].to_numpy(),
        }

    def pine_script(self, broker, i, ctx):
        # if (longCondition)
        #     sl = src - stopLossATRMult * atr
        #     tp = src + takeProfitATRMult * atr
        #     strategy.entry("Long", strategy.long, stop=sl, limit=tp)
        if ctx["long_condition"][i]:
            stop = float(ctx["long_stop"][i])
            limit = float(ctx["long_limit"][i])
            if np.isfinite(stop) and np.isfinite(limit):
                broker.entry("Long", "long", stop=stop, limit=limit)
            else:
                broker.entry("Long", "long")

        # if (shortCondition)
        #     sl = src + stopLossATRMult * atr
        #     tp = src - takeProfitATRMult * atr
        #     strategy.entry("Short", strategy.short, stop=sl, limit=tp)
        if ctx["short_condition"][i]:
            stop = float(ctx["short_stop"][i])
            limit = float(ctx["short_limit"][i])
            if np.isfinite(stop) and np.isfinite(limit):
                broker.entry("Short", "short", stop=stop, limit=limit)
            else:
                broker.entry("Short", "short")
