"""Port of sources/SM_91c72be2b4dbb6cf.pine (batch_001/Hilo-Activator-MACD-动态止盈止损交易策略-Hilo-Activator-MACD-Dynamic-Stop-Loss-Take-Profit-Trading-Strategy.md).

Pine v5, `//@version=5`, `strategy("Hilo MACD Strategy with SL/TP",
overlay=true)`. A MACD cross gated by the Hilo Activator's colour:

    hiloPeriod      = input.int(4)
    hiloHigh        = ta.highest(high, hiloPeriod)
    hiloLow         = ta.lowest(low, hiloPeriod)
    hiloActivator   = ta.valuewhen(close > hiloHigh[1] and close[1] < hiloHigh[2],
                                   hiloHigh, hiloPeriod)
    hiloActivator  := na(hiloActivator)
                      ? ta.valuewhen(close < hiloLow[1] and close[1] > hiloLow[2],
                                     hiloLow, hiloPeriod)
                      : hiloActivator
    hiloActivator  := na(hiloActivator)
                      ? ta.valuewhen(close[1] > hiloHigh[1] and close < hiloLow[1],
                                     hiloLow, hiloPeriod)
                      : hiloActivator
    hiloColor       = hiloActivator > close ? color.red : color.green

    [macdLine, signalLine, _] = ta.macd(close, 12, 26, 9)

    stopLoss   = input.float(1)
    takeProfit = input.float(2)
    atrValue   = ta.atr(14)

    longCondition  = ta.crossover(macdLine, signalLine) and hiloColor == color.green
    shortCondition = ta.crossunder(macdLine, signalLine) and hiloColor == color.red

    if (longCondition)
        strategy.entry("Long", strategy.long, stop=close - stopLoss * atrValue,
                                             limit=close + takeProfit * atrValue)
    if (shortCondition)
        strategy.entry("Short", strategy.short, stop=close + stopLoss * atrValue,
                                               limit=close - takeProfit * atrValue)

`ta.valuewhen(condition, source, occurrence)`'s third argument is an OCCURRENCE
COUNT, not a period. The source passes `hiloPeriod` (4), so it asks for the
value of `hiloHigh` at the FOURTH most recent occurrence of the condition -- not
the most recent one, which is what a "period" reading would give. That is
reproduced verbatim; substituting `0` would be a functional rewrite.

Both entries carry `stop=` and `limit=`, so they are RESTING stop-limit ENTRY
orders: the long triggers `1*atr` BELOW the signal bar's close and the short
`1*atr` ABOVE it. This is the framework boundary PINE_SEMANTICS.md section 2.11
records: the signal projection can only fire `enter_long` / `enter_short` on the
bar the order was PLACED, and a framework with no resting entry orders fills it
at the next open. Here the boundary happens not to bite, and the reason is worth
stating rather than assuming: the trigger sits on the MARKETABLE side of the
close, so on the very next bar `_price_order_fill` finds `high >= stop` and
fills at `max(stop, open_)`, which is that bar's open -- the same bar and the
same price Freqtrade uses. Measured on the local BTC/USDT:USDT 1h history: all
1900 stop-limit entries, 651 of which filled, filled on exactly the next bar and
at exactly that bar's open. The boundary is still structural -- it bites when
the offset puts the trigger beyond the current price, as it does in section
2.11's own measurement -- so `match` here is a property of this source's
offset, not a claim that resting entry orders are expressible in Freqtrade.

There is no `strategy.exit` / `strategy.close` in the source -- the "SL/TP" in
its title are the two ENTRY legs, not an exit -- so `source_reproduce_stops` is
False and a position is only ever closed by the opposite entry reversing it.

`strategy()` declares only `title` / `overlay`, so Pine's documented defaults
apply and are what this port carries: `default_qty_type=fixed`, one unit per
order, `commission_value=0`, `pyramiding=0`, `process_orders_on_close=false`,
initial capital 1000000.

The `/*backtest` header declares `period: 1h` on Futures_Binance BTC_USDT, so
`timeframe` is "1h"; its `basePeriod: 15m` is the FMZ backtester's own filling
granularity for those 1h bars, not the strategy's period.

FIDELITY:

* The md's prose says the Hilo Activator "使用用户定义的周期（默认为4）计算最高价
  和最低价" and calls `ta.valuewhen`'s third argument a period. The source passes
  `hiloPeriod` into the OCCURRENCE slot, which is a different (and much rarer)
  selection. The source is reproduced; the prose is not.
* The md says the stop-loss is "入场价格的 1 倍 ATR" / "1x ATR from the entry
  price". The source anchors both legs to the signal bar's `close`, which is not
  the entry price when the resting order later fills. Reproduced as written.
* `hiloActivator > close` is na while the Hilo line is still na (the first 49
  bars of the 1h window). Pine leaves the ternary's behaviour on an na condition
  unspecified; the port takes the else branch (green), which is the direct
  reading of `a > b ? x : y` with Pine's "na is falsy in a boolean context"
  rule. The alternative (na propagates, so neither colour matches) changes 3 of
  the 788 long signals on the local 1h history, all inside that warm-up window.
  Recorded as a modelling choice.
* `ta.highest` / `ta.lowest` return na until their window is full and propagate
  na inside it; pine_ta.pine_highest / pine_lowest reproduce that, so
  `hiloHigh[2]` needs 6 bars and no condition can fire before then.
* `ta.atr(14)` is v5 `ta.rma(ta.tr, 14)`, whose first true range is na;
  pine_ta.pine_atr takes the first bar's range as `high - low` instead.
  PINE_SEMANTICS.md section 3.7 records the one-bar seeding shift.
* `plot(...)` of the Hilo Activator and the MACD lines, and the strategy title
  and overlay, are display-only and are not reproduced.
* Leverage, margin, liquidation and funding are not modelled; the venue's
  contract-step rounding is not modelled either, so the framework and the
  engine can differ by a rounded quantity (measured separately by the chain
  verifier rather than treated as a signal difference).
"""
import numpy as np

from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


class SMHiloActivatorMacd_91c72b(PinePortBase, IStrategy):
    source_id = "SM_91c72be2b4dbb6cf"
    source_file = (
        "Hilo-Activator-MACD-动态止盈止损交易策略-Hilo-Activator-MACD-Dynamic-"
        "Stop-Loss-Take-Profit-Trading-Strategy.md"
    )
    timeframe = "1h"
    can_short = True
    source_defaults: dict = {
        "hiloPeriod": 4,
        "fastLength": 12,
        "slowLength": 26,
        "signalSmoothing": 9,
        "stopLoss": 1.0,
        "takeProfit": 2.0,
    }
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    # No strategy.exit / strategy.close: the only way out of a position is the
    # opposite entry reversing it.
    source_reproduce_stops = False
    source_fidelity_notes = [
        "ta.valuewhen's third argument is an OCCURRENCE count; the source passes "
        "hiloPeriod (4), i.e. the 4th most recent occurrence, not the most "
        "recent. Reproduced verbatim rather than corrected.",
        "The md calls that argument a 'period' and anchors the stop to the entry "
        "price; the source selects by occurrence and anchors both legs to the "
        "signal bar's close. Source is reproduced, prose recorded.",
        "Both entries use strategy.entry(stop=..., limit=...) -- resting "
        "stop-limit ENTRY orders. Freqtrade cannot be handed a resting entry "
        "order, so the projection fires the entry on the placement bar and the "
        "framework fills at the next open. PINE_SEMANTICS.md section 2.11. On "
        "the local 1h history the trigger is on the marketable side of the "
        "close, so the engine fills at the same next open: 651 of 1900 entries "
        "filled, all on the next bar and all at that bar's open.",
        "hiloColor is green whenever `hiloActivator > close` is false, including "
        "the 49 warm-up bars where the Hilo line is na. Pine leaves a ternary on "
        "an na condition unspecified; the alternative reading changes 3 of 788 "
        "long signals, all inside that window. Recorded as a modelling choice.",
        "ta.atr(14) is modelled with the first bar's true range taken as "
        "high - low (pine_ta.pine_atr); PINE_SEMANTICS.md section 3.7 records "
        "the one-bar seeding difference against ta.tr's own na rule.",
        "There is no exit call in the source; source_reproduce_stops is False "
        "and a position open at the end of the window stays open.",
        "plot() calls, the strategy title and overlay are display-only and are "
        "not reproduced.",
        "Leverage, margin, liquidation, funding and venue contract-step "
        "rounding are not modelled.",
    ]

    def pine_indicators(self, dataframe, params):
        high = dataframe["high"]
        low = dataframe["low"]
        close = dataframe["close"]

        hilo_period = int(params["hiloPeriod"])
        fast = int(params["fastLength"])
        slow = int(params["slowLength"])
        signal_smoothing = int(params["signalSmoothing"])
        stop_mult = float(params["stopLoss"])
        take_mult = float(params["takeProfit"])

        # hiloHigh = ta.highest(high, hiloPeriod) / hiloLow = ta.lowest(low, ...)
        hilo_high = ta.pine_highest(high, hilo_period)
        hilo_low = ta.pine_lowest(low, hilo_period)

        # Pine comparisons with an na operand are na, and na is falsy in a
        # boolean context, so the three guards below are False until the rolling
        # windows are full.
        close_1 = close.shift(1)
        condition_up = ((close > hilo_high.shift(1)) & (close_1 < hilo_high.shift(2)))
        condition_dn = ((close < hilo_low.shift(1)) & (close_1 > hilo_low.shift(2)))
        condition_rev = ((close_1 > hilo_high.shift(1)) & (close < hilo_low.shift(1)))
        condition_up = condition_up.fillna(False)
        condition_dn = condition_dn.fillna(False)
        condition_rev = condition_rev.fillna(False)

        # ta.valuewhen(cond, source, occurrence=hiloPeriod).
        up_value = ta.pine_valuewhen(condition_up, hilo_high, hilo_period)
        dn_value = ta.pine_valuewhen(condition_dn, hilo_low, hilo_period)
        rev_value = ta.pine_valuewhen(condition_rev, hilo_low, hilo_period)

        # hiloActivator := na(hiloActivator) ? <fallback> : hiloActivator, twice.
        activator = up_value.where(up_value.notna(), dn_value)
        activator = activator.where(activator.notna(), rev_value)

        # hiloColor = hiloActivator > close ? color.red : color.green
        red = (activator > close).fillna(False)
        green = ~red

        macd = ta.pine_macd(close, fast, slow, signal_smoothing)
        macd_line = macd["macd"]
        signal_line = macd["signal"]

        atr_value = ta.pine_atr(dataframe, 14)

        dataframe["pine_hilo_activator"] = activator
        dataframe["pine_macd_line"] = macd_line
        dataframe["pine_macd_signal"] = signal_line
        dataframe["pine_long_condition"] = (
            ta.pine_crossover(macd_line, signal_line) & green
        )
        dataframe["pine_short_condition"] = (
            ta.pine_crossunder(macd_line, signal_line) & red
        )
        dataframe["pine_long_stop"] = close - stop_mult * atr_value
        dataframe["pine_long_limit"] = close + take_mult * atr_value
        dataframe["pine_short_stop"] = close + stop_mult * atr_value
        dataframe["pine_short_limit"] = close - take_mult * atr_value
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
        #     strategy.entry("Long", strategy.long, stop=close - stopLoss * atrValue,
        #                    limit=close + takeProfit * atrValue)
        if ctx["long_condition"][i]:
            stop = float(ctx["long_stop"][i])
            limit = float(ctx["long_limit"][i])
            if np.isfinite(stop) and np.isfinite(limit):
                broker.entry("Long", "long", stop=stop, limit=limit)
            else:
                broker.entry("Long", "long")

        # if (shortCondition)
        #     strategy.entry("Short", strategy.short, stop=close + stopLoss * atrValue,
        #                    limit=close - takeProfit * atrValue)
        if ctx["short_condition"][i]:
            stop = float(ctx["short_stop"][i])
            limit = float(ctx["short_limit"][i])
            if np.isfinite(stop) and np.isfinite(limit):
                broker.entry("Short", "short", stop=stop, limit=limit)
            else:
                broker.entry("Short", "short")
