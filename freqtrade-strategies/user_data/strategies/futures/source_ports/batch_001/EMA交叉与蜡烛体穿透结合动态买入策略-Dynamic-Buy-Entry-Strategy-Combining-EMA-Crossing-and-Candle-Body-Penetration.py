"""Port of sources/SM_101963c3b4dbe964.pine (batch_001/EMA交叉与蜡烛体穿透结合动态买入策略-Dynamic-Buy-Entry-Strategy-Combining-EMA-Crossing-and-Candle-Body-Penetration.md).

Pine v5 long-only entry filter. Five conditions must hold on the same bar and
the only order in the source is a bare market long:

    ema_length       = input.int(14, title="EMA Length")
    ema_14           = ta.ema(close, ema_length)
    is_green_candle  = close > open
    crossing_ema     = ta.crossover(close, ema_14)
    body_crossed_ema = (close - open) * 0.5 <= (close - ema_14) and close > ema_14
    wick_percent     = ((high - close) + (open - low)) / (high - low)
    valid_wick       = wick_percent <= 0.4
    buy_condition    = is_green_candle and crossing_ema and body_crossed_ema
                       and valid_wick

    if buy_condition
        strategy.entry("Buy", strategy.long)

`ema_length` (14) is the only input. `strategy()` declares only `title` and
`overlay`, so Pine's documented defaults apply: `default_qty_type = fixed`,
`default_qty_value = 1`, `commission_value = 0`, `pyramiding = 0`, initial
capital 1000000 and `process_orders_on_close = false`. The `/*backtest`
header declares `period: 1d` on Futures_Binance BTC_USDT, so `timeframe` is
"1d"; its `basePeriod: 1d` matches.

FIDELITY:

* The source's `body`, `upper_wick`, `lower_wick` and `total_candle_length`
  variables are reproduced literally: `lower_wick` is `open - low` (NOT
  `min(open, close) - low`), which is what the source writes, and
  `total_candle_length` is `high - low`.
* `ta.ema` is `pine_ta.pine_ema`: alpha = 2/(length+1), seeded with the first
  non-na observation, na observations not advancing the recursion. TradingView
  does not publish its seeding rule, so this is the shared modelled choice
  (PINE_SEMANTICS §3.1), not a certified equivalence.
* `ta.crossover` is false whenever either operand is na, which is what Pine's
  na comparison yields; `pine_ta.pine_crossover` fills those as False. The
  `close > ema_14` and `wick_percent <= 0.4` comparisons follow the same rule.
* There is no exit call and no stop anywhere in the source. A long is opened
  once and then held: with `pyramiding = 0` every later `strategy.entry("Buy",
  strategy.long)` while the position is open is refused at order creation
  (Pine's own rule), so the source can hold at most one long for the whole
  window. `source_reproduce_stops` is therefore False and a position still open
  at the end of the window stays open.
* `plot` and `plotshape` are display-only and are not reproduced.
* Leverage, margin, liquidation and funding are not modelled
  (PINE_SEMANTICS §二-4); contract-step rounding is not applied
  (PINE_SEMANTICS §1.6).
"""
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


class SMDynamicBuyEntry_101963(PinePortBase, IStrategy):
    source_id = "SM_101963c3b4dbe964"
    source_file = (
        "EMA交叉与蜡烛体穿透结合动态买入策略-Dynamic-Buy-Entry-Strategy-"
        "Combining-EMA-Crossing-and-Candle-Body-Penetration.md"
    )
    timeframe = "1d"
    can_short = False
    source_defaults: dict = {"ema_length": 14}
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    source_reproduce_stops = False
    source_fidelity_notes = [
        "lower_wick is `open - low` as the source writes it, not "
        "`min(open, close) - low`; total_candle_length is `high - low`.",
        "ta.ema uses the shared modelled seeding (first non-na observation, na "
        "not advancing the recursion). TradingView's exact seeding is "
        "unpublished -- PINE_SEMANTICS §3.1 records this as a parity risk.",
        "ta.crossover and every other comparison against an na operand are "
        "false, matching Pine's na-in-boolean rule.",
        "The source has no exit call and no stop. With pyramiding=0 every later "
        "same-direction entry is refused at creation, so at most one long can "
        "ever be open; source_reproduce_stops is False and a position open at "
        "the window's end stays open.",
        "strategy() declares only title/overlay, so Pine's defaults apply: "
        "qty_type fixed, qty_value 1, commission 0, pyramiding 0, initial "
        "capital 1000000, process_orders_on_close false.",
        "plot / plotshape are display-only and are not reproduced.",
        "Contract-step rounding, leverage, margin, liquidation and funding are "
        "not modelled (PINE_SEMANTICS §1.6, §二-4).",
    ]

    def pine_indicators(self, dataframe, params):
        close, open_ = dataframe["close"], dataframe["open"]
        high, low = dataframe["high"], dataframe["low"]

        ema_14 = ta.pine_ema(close, int(params["ema_length"]))
        dataframe["pine_ema_14"] = ema_14

        # body = close - open (declared by the source; used only inline below)
        body = close - open_
        # upper_wick = high - close ; lower_wick = open - low
        wick_percent = ((high - close) + (open_ - low)) / (high - low)

        is_green_candle = close > open_
        crossing_ema = ta.pine_crossover(close, ema_14)
        body_crossed_ema = (body * 0.5 <= (close - ema_14)) & (close > ema_14)
        valid_wick_condition = wick_percent <= 0.4

        dataframe["pine_buy_condition"] = (
            is_green_candle & crossing_ema & body_crossed_ema & valid_wick_condition
        ).fillna(False).astype(bool)
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "buy_condition": dataframe["pine_buy_condition"].to_numpy(),
        }

    def pine_script(self, broker, i, ctx):
        # if (buy_condition)
        #     strategy.entry("Buy", strategy.long)
        if ctx["buy_condition"][i]:
            broker.entry("Buy", "long")
