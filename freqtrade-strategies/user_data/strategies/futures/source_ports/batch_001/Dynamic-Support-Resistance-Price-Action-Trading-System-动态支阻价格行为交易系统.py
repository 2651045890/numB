"""Port of sources/SM_efc3361c421d5ef4.pine
(batch_001/Dynamic-Support-Resistance-Price-Action-Trading-System-动态支阻价格行为交易系统.md).

Pine v5, two-sided, one position at a time, percentage stop/target off the
POSITION'S AVERAGE PRICE. The whole script:

    length      = input.int(16, "Support and Resistance Length")
    sensitivity = input.float(0.018, "Sensitivity")
    stop_loss_pct   = input.float(16,   "Stop Loss percentage",   minval=0.1) / 100
    take_profit_pct = input.float(9.5,  "Take Profit percentage", minval=0.1) / 100

    isHammer() => body = close - open; lower_shadow = open - low
                  upper_shadow = high - close
                  body > 0 and lower_shadow > body * 2
                  and upper_shadow < body * 0.5 and (high - low) > 0
    isShootingStar() => body = open - close; lower_shadow = close - low
                  upper_shadow = high - open
                  body > 0 and upper_shadow > body * 2
                  and lower_shadow < body * 0.5 and (high - low) > 0
    isDoji() => math.abs(close - open) < (high - low) * 0.1
    isPinBar() => body = close - open; lower_shadow = open - low
                  upper_shadow = high - close
                  (upper_shadow > body*2 and lower_shadow < body*0.5)
                  or (lower_shadow > body*2 and upper_shadow < body*0.5)

    support    = ta.lowest(low, length)
    resistance = ta.highest(high, length)

    long_condition  = (isHammer() or isDoji() or isPinBar())
                      and close <= support * (1 + sensitivity)
    short_condition = (isShootingStar() or isDoji() or isPinBar())
                      and close >= resistance * (1 - sensitivity)

    if (long_condition and strategy.opentrades == 0)
        strategy.entry("Buy", strategy.long)

    if (short_condition and strategy.opentrades == 0)
        strategy.entry("Sell", strategy.short)

    if (strategy.opentrades > 0)
        if (strategy.position_size > 0)
            [s, t] = calculate_levels(strategy.position_size,
                                      strategy.position_avg_price,
                                      stop_loss_pct, take_profit_pct)
            strategy.exit("Exit Long", from_entry="Buy", stop=s, limit=t)
        if (strategy.position_size < 0)
            [s, t] = calculate_levels_short(strategy.position_size,
                                            strategy.position_avg_price,
                                            stop_loss_pct, take_profit_pct)
            strategy.exit("Exit Short", from_entry="Sell", stop=s, limit=t)

with, in the long branch, `s = avg * (1 - stop_loss_pct)` /
`t = avg * (1 + take_profit_pct)`, and in the short branch
`s = avg * (1 + stop_loss_pct)` / `t = avg * (1 - take_profit_pct)`.

TWO DETAILS THAT MATTER AND ARE EASY TO "SIMPLIFY" AWAY:

1. The `input.float(...) / 100` division happens AT THE INPUT DECLARATION, so
   the two percentages are read as 16 and 9.5 and used as 0.16 / 0.095. The raw
   defaults live in `source_defaults` and the `/100.0` is applied where the
   source applies it.
2. The exits are placed on EVERY bar the position is held, not once at the
   entry. The levels are recomputed from `strategy.position_avg_price` each bar,
   which is constant for a single entry, so the resting OCA pair is repeatedly
   replaced with the same two prices. Reproduced by re-issuing the exit each bar.

`strategy()` declares only `overlay=true`, so everything else is Pine's
documented default: `default_qty_type=strategy.fixed`, `default_qty_value` 1,
commission 0%, pyramiding 0, initial capital 1000000. Neither entry passes a
`qty`, so each order is 1 contract.

The `/*backtest` header declares `period: 1h` on Futures_Binance BTC_USDT, so
`timeframe` is "1h" (`basePeriod` is 1h here too).

FIDELITY:

* `label.new(...)` (the pattern name drawn on the chart) and the two `plot()`
  calls for support/resistance are display-only and place no order; not
  reproduced. The pattern string expression inside `label.new` re-invokes
  isHammer/isDoji/isPinBar, so removing the label changes nothing behavioural.
* `calculate_levels` / `calculate_levels_short` take `position_size` and ignore
  it; the parameter is kept in the port's comments but the computation uses only
  `avg_price`, as the source does.
* `strategy.exit` is called with stop= AND limit= (one OCA pair). Both legs are
  handed to the broker so neither the stop nor the take-profit is silently
  dropped (PINE_SEMANTICS.md 1.8).
* The exit is bound to a named entry (`from_entry="Buy"` / `"Sell"`), so while a
  long is open the short-bound `strategy.exit` is never reached anyway (the
  `position_size < 0` branch), and vice versa. The engine's from_entry scoping
  (PINE_SEMANTICS.md 1.12) keeps that true.
* `support` / `resistance` use `ta.lowest(low, length)` / `ta.highest(high,
  length)` -- both na until `length` bars have elapsed, so nothing fires in the
  warmup. `pine_lowest` / `pine_highest` match that.
* `math.abs(body) < (price_range * 0.1)` in `isDoji()` has NO `price_range > 0`
  guard, unlike the other three patterns; a flat bar gives `0 < 0` = false. Kept
  as written rather than normalised.
* The md's description matches the code behaviourally (16-period levels, 1.8%
  sensitivity, 16% stop, 9.5% target, patterns within the band). The md's
  "使用35%的资金管理规则" / "每笔交易的风险在账户总额的5.6%" is NOT in the source -- the
  source declares no position sizing at all beyond Pine's fixed/1 default, and no
  `strategy()` risk argument. Recorded as an md claim with no code behind it.
* Leverage, margin, liquidation, funding and the venue's contract-step rounding
  are not modelled by the engine (PINE_SEMANTICS.md 二.4, 1.6).
"""
from __future__ import annotations

from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


class SMDynamicSupportResistance_efc336(PinePortBase, IStrategy):
    source_id = "SM_efc3361c421d5ef4"
    source_file = (
        "Dynamic-Support-Resistance-Price-Action-Trading-System-动态支阻价格行为交易系统.md"
    )
    timeframe = "1h"
    can_short = True
    source_defaults: dict = {
        # length = input.int(16, title="Support and Resistance Length")
        "length": 16,
        # sensitivity = input.float(0.018, title="Sensitivity")
        "sensitivity": 0.018,
        # stop_loss_pct = input.float(16, ...) / 100  -- the RAW input default
        "stop_loss_pct": 16,
        # take_profit_pct = input.float(9.5, ...) / 100 -- the RAW input default
        "take_profit_pct": 9.5,
    }
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    source_reproduce_stops = True
    source_fidelity_notes = [
        "stop_loss_pct / take_profit_pct are input defaults 16 and 9.5 divided "
        "by 100 AT THE DECLARATION; source_defaults holds the raw 16 / 9.5 and "
        "the /100.0 is applied where the source applies it.",
        "The exits are re-issued on every bar the position is held, recomputed "
        "from strategy.position_avg_price; for a single entry that is the same "
        "two prices each bar, but it is modelled as the per-bar replacement the "
        "source performs.",
        "label.new(...) and the two support/resistance plot() calls are "
        "display-only; the label's re-invocation of the pattern functions places "
        "no order and is not reproduced.",
        "calculate_levels / calculate_levels_short accept position_size and "
        "ignore it; the levels depend only on the average price, as in the "
        "source.",
        "strategy.exit carries stop= AND limit= (an OCA pair); both legs are "
        "passed to the broker so the take-profit leg is not dropped "
        "(PINE_SEMANTICS.md 1.8).",
        "isDoji() has no price_range > 0 guard (unlike isHammer / isShootingStar "
        "/ isPinBar); kept exactly as written.",
        "support / resistance are ta.lowest / ta.highest, na until `length` bars "
        "have elapsed, so nothing fires during warmup.",
        "The md claims a 35% equity-management rule with ~5.6% risk per trade; "
        "the source declares no sizing beyond Pine's fixed/1 default and no "
        "risk argument in strategy(). Recorded, not implemented.",
        "Leverage, margin, liquidation, funding and contract-step rounding are "
        "not modelled by the engine.",
    ]

    def pine_indicators(self, dataframe, params):
        close = dataframe["close"]
        high = dataframe["high"]
        low = dataframe["low"]
        source_open = dataframe["open"]

        length = int(params["length"])
        sensitivity = float(params["sensitivity"])
        stop_loss_pct = float(params["stop_loss_pct"]) / 100.0
        take_profit_pct = float(params["take_profit_pct"]) / 100.0

        body = close - source_open
        price_range = high - low

        # isHammer(): body > 0 and lower_shadow > body*2 and upper_shadow < body*0.5
        #             and price_range > 0
        hammer_lower_shadow = source_open - low
        hammer_upper_shadow = high - close
        is_hammer = (
            (body > 0)
            & (hammer_lower_shadow > body * 2)
            & (hammer_upper_shadow < body * 0.5)
            & (price_range > 0)
        )
        # isShootingStar(): body = open - close; lower_shadow = close - low;
        #                   upper_shadow = high - open
        star_body = source_open - close
        star_lower_shadow = close - low
        star_upper_shadow = high - source_open
        is_shooting_star = (
            (star_body > 0)
            & (star_upper_shadow > star_body * 2)
            & (star_lower_shadow < star_body * 0.5)
            & (price_range > 0)
        )
        # isDoji(): math.abs(close - open) < price_range * 0.1
        is_doji = body.abs() < (price_range * 0.1)
        # isPinBar(): (upper_shadow > body*2 and lower_shadow < body*0.5)
        #             or (lower_shadow > body*2 and upper_shadow < body*0.5)
        pin_lower_shadow = source_open - low
        pin_upper_shadow = high - close
        is_pin_bar = (
            ((pin_upper_shadow > body * 2) & (pin_lower_shadow < body * 0.5))
            | ((pin_lower_shadow > body * 2) & (pin_upper_shadow < body * 0.5))
        )

        support = ta.pine_lowest(low, length)
        resistance = ta.pine_highest(high, length)

        dataframe["pine_is_hammer"] = is_hammer.astype(bool)
        dataframe["pine_is_shooting_star"] = is_shooting_star.astype(bool)
        dataframe["pine_is_doji"] = is_doji.astype(bool)
        dataframe["pine_is_pin_bar"] = is_pin_bar.astype(bool)
        dataframe["pine_support"] = support
        dataframe["pine_resistance"] = resistance
        dataframe["pine_long_condition"] = (
            (is_hammer | is_doji | is_pin_bar)
            & (close <= support * (1 + sensitivity))
        ).astype(bool)
        dataframe["pine_short_condition"] = (
            (is_shooting_star | is_doji | is_pin_bar)
            & (close >= resistance * (1 - sensitivity))
        ).astype(bool)
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "long_condition": dataframe["pine_long_condition"].to_numpy(dtype=bool),
            "short_condition": dataframe["pine_short_condition"].to_numpy(dtype=bool),
            "stop_loss_pct": float(params["stop_loss_pct"]) / 100.0,
            "take_profit_pct": float(params["take_profit_pct"]) / 100.0,
        }

    def pine_script(self, broker, i, ctx):
        # if (long_condition and strategy.opentrades == 0)
        #     strategy.entry("Buy", strategy.long)
        if ctx["long_condition"][i] and broker.open_trades == 0:
            broker.entry("Buy", "long")

        # if (short_condition and strategy.opentrades == 0)
        #     strategy.entry("Sell", strategy.short)
        if ctx["short_condition"][i] and broker.open_trades == 0:
            broker.entry("Sell", "short")

        # if (strategy.opentrades > 0)
        if broker.open_trades > 0:
            # if (strategy.position_size > 0)
            #     calculate_levels -> avg*(1-slp), avg*(1+tpp)
            #     strategy.exit("Exit Long", from_entry="Buy", stop=, limit=)
            if broker.position_size > 0:
                average_price = broker.position_avg_price
                broker.exit(
                    "Exit Long",
                    from_entry="Buy",
                    stop=average_price * (1 - ctx["stop_loss_pct"]),
                    limit=average_price * (1 + ctx["take_profit_pct"]),
                )
            # if (strategy.position_size < 0)
            #     calculate_levels_short -> avg*(1+slp), avg*(1-tpp)
            #     strategy.exit("Exit Short", from_entry="Sell", stop=, limit=)
            if broker.position_size < 0:
                average_price = broker.position_avg_price
                broker.exit(
                    "Exit Short",
                    from_entry="Sell",
                    stop=average_price * (1 + ctx["stop_loss_pct"]),
                    limit=average_price * (1 - ctx["take_profit_pct"]),
                )
