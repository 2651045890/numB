"""Port of sources/SM_d9c9f47c6eea3499.pine (batch_001/EMA均线动态突破与反转策略-Dynamic-EMA-Breakthrough-and-Reversal-Strategy.md).

Pine v6 (`//@version=6`). Two independent EMA objects, a candle-shape filter on
the long side and a previous-bar filter on the short side:

    ema14   = ta.ema(close, 14)          // literal 14 -- used by the SELL side
    ema_length = input.int(14, title="EMA Length")
    ema_14  = ta.ema(close, ema_length)  // input-driven -- used by the BUY side

    body = close - open ; upper_wick = high - close ; lower_wick = open - low
    total_candle_length = high - low
    is_green_candle = close > open
    crossing_ema = ta.crossover(close, ema_14)
    body_crossed_ema = (close - open) * 0.5 <= (close - ema_14) and close > ema_14
    wick_percent = (upper_wick + lower_wick) / total_candle_length
    valid_wick_condition = wick_percent <= 0.4
    buy_condition = is_green_candle and crossing_ema and body_crossed_ema
                    and valid_wick_condition

    candleIsRed    = close < open
    priceBelowEMA  = close < ema14
    prevLowAboveEMA = low[1] > ema14[1]
    wickTooLarge = (low - math.min(open, close)) / (high - low) <= 0.2
    sellSignal = priceBelowEMA and candleIsRed and prevLowAboveEMA and wickTooLarge

    if (buy_condition)
        strategy.entry("Buy", strategy.long)
    if (sellSignal)
        strategy.entry("Sell", strategy.short)

Both entries are MARKET orders, so they fill at the next bar's open in the
engine -- the same bar and the same price Freqtrade uses. There is no stop,
limit, exit, close or cancel anywhere in the source: a position is closed only
by the opposite entry reversing it.

`strategy()` declares only `title` / `overlay`, so Pine's documented defaults
apply and are what this port carries: `default_qty_type=fixed`, one unit per
order, `commission_value=0`, `pyramiding=0`, `process_orders_on_close=false`,
initial capital 1000000.

The `/*backtest` header declares `period: 1h` on Futures_Binance BTC_USDT, so
`timeframe` is "1h"; its `basePeriod: 1h` is the FMZ backtester's own filling
granularity for those 1h bars, which is the same period here.

FIDELITY:

* There are TWO EMA objects and they are NOT the same series when the input is
  changed. The buy side uses `ema_14` (driven by `ema_length`); the sell side
  uses `ema14`, a literal 14. Both are computed and kept as separate columns
  (iron rule 3: the formula is read, not assumed from the name).
* `body_crossed_ema` is reproduced as written: `(close - open) * 0.5 <=
  (close - ema_14)`. Algebraically that is `ema_14 <= (close + open) / 2`, the
  EMA at or below the body's midpoint, which is what the md means by "at least
  50% of the body". The literal form from the source is kept rather than the
  rewritten one.
* `wick_percent` mixes `upper_wick = high - close` and `lower_wick = open - low`,
  which for a green candle are the true upper and lower wicks; the port keeps
  the source's expressions rather than substituting `math.max`/`math.min`.
* `total_candle_length` and `high - low` can be zero, in which case Pine
  propagates na and the comparison is false. The port divides with pandas
  floats so a zero denominator yields inf/na rather than raising, and the
  `<=` test is false in both cases, matching Pine.
* `math.min(open, close)` is Pine's v5/v6 `math.*` namespace; `pine_ta.pine_min`
  is the same elementwise minimum.
* `ta.ema` seeding is a modelled choice (PINE_SEMANTICS.md section 3.1): the
  first non-na observation seeds the recursion, and an na observation does not
  advance it. TradingView does not document its own seeding rule.
* `ta.crossover` against an na operand is false, which pine_ta.pine_crossover
  reproduces, so the first buy signal cannot arrive before the EMA exists.
* `plot(ema14, ...)`, the two `plotshape` arrows and the title are display-only
  and are not reproduced.
* There is no exit call in the source, so `source_reproduce_stops` is False: a
  position is closed only by the opposite entry reversing it, and a position
  open at the end of the window stays open.
* Leverage, margin, liquidation, funding and the venue's contract-step
  rounding are not modelled; the framework and the engine can differ by a
  rounded quantity (measured separately by the chain verifier).
"""
import numpy as np

from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


class SMEmaDynamicBreakthroughReversal_d9c9f4(PinePortBase, IStrategy):
    source_id = "SM_d9c9f47c6eea3499"
    source_file = "EMA均线动态突破与反转策略-Dynamic-EMA-Breakthrough-and-Reversal-Strategy.md"
    timeframe = "1h"
    can_short = True
    source_defaults: dict = {"ema_length": 14}
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    # No stop / limit / exit / close in the source.
    source_reproduce_stops = False
    source_fidelity_notes = [
        "The source holds two EMA objects that differ as soon as the input "
        "changes: the buy side uses ema_14 (ta.ema(close, ema_length)) and the "
        "sell side uses ema14 (ta.ema(close, 14), a literal). Both are computed "
        "and kept as separate columns.",
        "body_crossed_ema is reproduced literally as "
        "(close - open) * 0.5 <= (close - ema_14) and close > ema_14. "
        "Algebraically that is ema_14 <= (close + open) / 2, i.e. the EMA at or "
        "below the body's midpoint, which is what the md's prose means by 'at "
        "least 50% of the body crossing the EMA'; the literal form is kept so "
        "the source's own arithmetic is on the record.",
        "wick_percent uses the source's expressions (upper_wick = high - close, "
        "lower_wick = open - low) rather than a max/min reformulation.",
        "A zero candle range (high == low) or a zero total length makes Pine's "
        "division na and the comparison false; the port divides with pandas "
        "floats so it yields inf/na instead of raising, and the <= test is "
        "false either way.",
        "ta.ema seeding is a modelled choice (PINE_SEMANTICS.md section 3.1): "
        "first non-na value seeds, na does not advance the recursion.",
        "crossover against an na operand is false, so no buy signal can arrive "
        "before the EMA exists.",
        "Both entries are market orders and fill at the next bar's open, which "
        "is what Freqtrade does too, so no entry-timing boundary applies here.",
        "No exit call exists: source_reproduce_stops is False and a position is "
        "closed only by the opposite entry reversing it.",
        "plot / plotshape arrows and the strategy title are display-only and are "
        "not reproduced.",
        "Leverage, margin, liquidation, funding and venue contract-step "
        "rounding are not modelled.",
    ]

    def pine_indicators(self, dataframe, params):
        close = dataframe["close"]
        open_ = dataframe["open"]
        high = dataframe["high"]
        low = dataframe["low"]

        # ema14 = ta.ema(close, 14) -- literal, used by the sell side.
        ema14 = ta.pine_ema(close, 14)
        # ema_14 = ta.ema(close, ema_length) -- input-driven, used by the buy side.
        ema_14 = ta.pine_ema(close, int(params["ema_length"]))

        is_green_candle = close > open_
        crossing_ema = ta.pine_crossover(close, ema_14)
        body_crossed_ema = ((close - open_) * 0.5 <= (close - ema_14)) & (close > ema_14)
        wick_percent = ((high - close) + (open_ - low)) / (high - low)
        valid_wick_condition = wick_percent <= 0.4
        buy_condition = (
            is_green_candle & crossing_ema & body_crossed_ema & valid_wick_condition
        )

        candle_is_red = close < open_
        price_below_ema = close < ema14
        prev_low_above_ema = low.shift(1) > ema14.shift(1)
        wick_too_large = (low - ta.pine_min(open_, close)) / (high - low) <= 0.2
        sell_signal = (
            price_below_ema & candle_is_red & prev_low_above_ema & wick_too_large
        )

        dataframe["pine_ema14_literal"] = ema14
        dataframe["pine_ema_input"] = ema_14
        dataframe["pine_wick_percent"] = wick_percent
        dataframe["pine_wick_too_large"] = wick_too_large
        dataframe["pine_buy_condition"] = buy_condition.fillna(False)
        dataframe["pine_sell_signal"] = sell_signal.fillna(False)
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "buy_condition": dataframe["pine_buy_condition"].to_numpy(dtype=bool),
            "sell_signal": dataframe["pine_sell_signal"].to_numpy(dtype=bool),
        }

    def pine_script(self, broker, i, ctx):
        # if (buy_condition)
        #     strategy.entry("Buy", strategy.long)
        if ctx["buy_condition"][i]:
            broker.entry("Buy", "long")
        # if (sellSignal)
        #     strategy.entry("Sell", strategy.short)
        if ctx["sell_signal"][i]:
            broker.entry("Sell", "short")
