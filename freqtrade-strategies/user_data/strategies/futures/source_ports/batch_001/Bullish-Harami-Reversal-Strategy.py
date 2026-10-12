"""Port of sources/SM_be6b5133f37af815.pine (batch_001/Bullish-Harami-Reversal-Strategy.md).

Pine v3, long only. A Bullish Harami candle pattern drives a single state
variable, `posprice`, which is the entry price of the trade the script believes
it is holding; `pos` is its boolean (or rather 1/0) shadow:

    barcolor(abs(close - open) >= minSizeBody ? open[1] > close[1] ? close > open
             ? close <= open[1] ? close[1] <= open ? close - open < open[1] - close[1]
             ? yellow : na : na : na : na : na : na)                       // display only

    pos = 0.0
    posprice = 0.0
    posprice := abs(close - open) >= minSizeBody
                ? open[1] > close[1] ? close > open ? close <= open[1]
                  ? close[1] <= open ? close - open < open[1] - close[1]
                    ? close : nz(posprice[1], 0) : nz(posprice[1], 0)
                  : nz(posprice[1], 0) : nz(posprice[1], 0)
                : nz(posprice[1], 0) : nz(posprice[1], 0)
    pos := iff(posprice > 0, 1, 0)

    if (pos == 0) strategy.close_all()
    if (pos == 1) strategy.entry("Long", strategy.long)

    posprice := iff(low  <= posprice - stopLossPips and posprice > 0, 0, nz(posprice, 0))
    posprice := iff(high >= posprice + takePips     and posprice > 0, 0, nz(posprice, 0))

The pattern is the six-way AND of the nested ternary: a body of at least
`minSizeBody`, a bearish previous candle, a bullish current candle, the current
close inside the previous body and not above the current open, and a current
body strictly smaller than the previous one.

TWO THINGS ABOUT THE ORDER OF THE LAST TWO LINES. They run AFTER the entry /
close calls, so the stop and the take-profit are evaluated against the SAME bar
whose close just latched the entry price -- i.e. a signal bar whose low is more
than `stopLossPips` under its own close latches the entry and immediately
cancels the state, so the entry (placed that bar, filled the next) is closed
again on the following bar. And the second line reads the value the FIRST line
just assigned, so once the stop has zeroed the state the take-profit branch
sees `posprice > 0` as false.

`posprice` is a plain (non-`var`) global that reads its own `[1]`, which is the
ordinary Pine v3 carry idiom: the value referenced at bar t is the one the
previous bar ended with. Only bar 0's `posprice[1]` is na, and `nz` makes it 0.
Since the variable depends on candles alone -- never on `strategy.position_size`
-- the whole thing is a pure series and lives in `pine_indicators`.

`strategy(title=..., overlay=true)` declares nothing else, so every property is
Pine's documented default: `strategy.fixed` / 1 contract, initial capital
1000000, commission 0%, pyramiding 0, `process_orders_on_close=false`.

FIDELITY:

* The exits are `strategy.close_all()` MARKET closes, not resting stop orders:
  the stop / take-profit only zero `posprice`, and the framework-visible exit is
  a market close on the NEXT bar. So `source_reproduce_stops` is False and no
  stop level is ever published; the engine's own `close_all` fills at the next
  open, matching the framework's next-open market exit.
* `strategy.close_all()` is called on EVERY bar where `posprice == 0` -- i.e. on
  every flat bar of the whole run. While flat the engine skips it (no position),
  and `run_pine` projects nothing for it, so the flood of no-ops is faithful and
  inert.
* `strategy.entry("Long", strategy.long)` is re-issued on every bar where
  `posprice > 0`, which is every bar the position is held. With `pyramiding=0`
  the engine blocks the repeat (an entry that cannot move the position is not
  projected as a signal), which is what Pine does with the same id.
* `input(60, ...)` / `input(18, ...)` are used by the source as RAW price
  distances (`posprice - input_stoploss`), despite being titled "pip". They are
  reproduced as raw price distances; on BTC the md's "pip" reading would be a
  different number, and the code is what is followed.
* The md carries no prose beyond the pattern description, so there is no md /
  source disagreement to record beyond the "pip" wording in the input titles.
* `barcolor(...)` and the second `barcolor(nz(pos[1], 0) == ...)` are display
  only -- they place no order and nothing reads them; `pos[1]` there is the only
  use of `pos` as a series (the script reads it as a scalar), so `pos` is carried
  as a 0/1 column and its `[1]` is not needed.
* na handling: while any shifted operand is na (the first bar, and any bar whose
  previous candle is na) the comparison chain is false, so the carry is taken.
  `nz` maps the bar-0 na to 0 exactly as the source does.
* `strategy.close_all()` on a bar with no position, and the whole first-bar
  warmup, produce no trades; the run starts trading once a full pattern exists.
* Leverage, margin, liquidation, funding and contract-step rounding are not
  modelled; the chain verifier measures the rounding separately.
"""
from __future__ import annotations

import numpy as np
from freqtrade.strategy import IStrategy

from pine_port_base import PinePortBase


class SMBullishHaramiReversal_be6b51(PinePortBase, IStrategy):
    source_id = "SM_be6b5133f37af815"
    source_file = "Bullish-Harami-Reversal-Strategy.md"
    timeframe = "1d"
    can_short = False
    source_defaults: dict = {
        "TakeProfit": 60,
        "StopLoss": 18,
        "MinSizeBody": 1,
    }
    # strategy(title=..., overlay=true): Pine's documented defaults.
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    # The stop / take-profit only zero `posprice`; the framework-visible exit is
    # a `strategy.close_all()` MARKET close on the next bar, so there is no
    # resting stop for custom_stoploss to mirror.
    source_reproduce_stops = False
    source_fidelity_notes = [
        "The exits are market closes: the stop/take-profit only zero `posprice`, "
        "and the visible exit is `strategy.close_all()` on the NEXT bar. "
        "source_reproduce_stops is therefore False and no stop level is ever "
        "published; the engine's close_all fills at the next open, matching the "
        "framework's next-open market exit.",
        "`strategy.close_all()` fires on every bar where posprice == 0 -- every "
        "flat bar of the run. While flat the engine skips it and run_pine "
        "projects nothing, so the no-op flood is faithful and inert.",
        "`strategy.entry(\"Long\")` is re-issued every bar the state is held; "
        "with pyramiding=0 the engine blocks the repeat and does not project it "
        "as a signal, which is what Pine does with the same id.",
        "The stop / take-profit are applied to the state AFTER the entry and "
        "close calls of the same bar, against the SAME bar's own low/high and "
        "its own just-latched entry price. A signal bar whose low is already "
        "more than StopLoss under its own close therefore latches the entry, "
        "fills it next bar and closes it the bar after. Reproduced as written.",
        "The second stop/take line reads the value the first one just assigned, "
        "so a stop that zeroed the state also makes the take-profit branch's "
        "`posprice > 0` false on that bar.",
        "`input(60)` / `input(18)` are used as RAW price distances "
        "(`posprice - input_stoploss`), despite being titled 'pip'. Reproduced "
        "as raw price distances; the code is followed over the title.",
        "`posprice` is a non-`var` global reading its own [1] -- the Pine v3 "
        "carry idiom. Bar 0's `posprice[1]` is na and `nz` maps it to 0, exactly "
        "as the source does. Because it depends on candles only and never on "
        "strategy.position_size, it is computed as a pure series in "
        "pine_indicators, not as per-run state.",
        "`barcolor(...)` calls are display-only and place no orders; the second "
        "one's `pos[1]` is the only series use of `pos` and is not needed.",
        "The md has no behavioural prose beyond the pattern description, so "
        "there is no md/source disagreement beyond the 'pip' wording in the "
        "input titles.",
        "Leverage, margin, liquidation, funding and contract-step rounding are "
        "not modelled; the chain verifier measures the rounding separately.",
    ]

    def pine_indicators(self, dataframe, params):
        open_ = dataframe["open"]
        close = dataframe["close"]
        high = dataframe["high"]
        low = dataframe["low"]

        min_size_body = float(params["MinSizeBody"])
        stop_loss = float(params["StopLoss"])
        take_profit = float(params["TakeProfit"])

        # The nested ternary, as the six-way AND it is:
        #   abs(close - open) >= minSizeBody and open[1] > close[1] and close > open
        #   and close <= open[1] and close[1] <= open and close - open < open[1] - close[1]
        body = (close - open_).abs()
        previous_open = open_.shift(1)
        previous_close = close.shift(1)
        pattern = (
            (body >= min_size_body)
            & (previous_open > previous_close)
            & (close > open_)
            & (close <= previous_open)
            & (previous_close <= open_)
            & ((close - open_) < (previous_open - previous_close))
        ).fillna(False)

        close_values = close.to_numpy(dtype=float)
        high_values = high.to_numpy(dtype=float)
        low_values = low.to_numpy(dtype=float)
        pattern_values = pattern.to_numpy(dtype=bool)
        size = len(dataframe)

        entry_price = np.full(size, np.nan)
        state_price = np.full(size, np.nan)
        position = np.zeros(size, dtype=int)

        # posprice is carried from bar to bar; bar 0's posprice[1] is na -> nz -> 0.
        carry = np.nan
        for i in range(size):
            # posprice := <pattern> ? close : nz(posprice[1], 0)   -- line 29
            previous = 0.0 if np.isnan(carry) else float(carry)
            value = float(close_values[i]) if pattern_values[i] else previous
            entry_price[i] = value
            # pos := iff(posprice > 0, 1, 0)                       -- line 30
            position[i] = 1 if value > 0.0 else 0
            # posprice := iff(low  <= posprice - stopLoss and posprice > 0, 0, nz(posprice, 0))
            if value > 0.0 and low_values[i] <= value - stop_loss:
                value = 0.0
            # posprice := iff(high >= posprice + takePips and posprice > 0, 0, nz(posprice, 0))
            if value > 0.0 and high_values[i] >= value + take_profit:
                value = 0.0
            state_price[i] = value
            carry = value

        dataframe["pine_harami_pattern"] = pattern
        dataframe["pine_harami_entry_price"] = entry_price
        dataframe["pine_harami_state_price"] = state_price
        dataframe["pine_harami_pos"] = position
        return dataframe

    def pine_context(self, dataframe, params):
        return {"pos": dataframe["pine_harami_pos"].to_numpy(dtype=int)}

    def pine_script(self, broker, i, ctx):
        # if (pos == 0) strategy.close_all()
        if ctx["pos"][i] == 0:
            broker.close_all()
        # if (pos == 1) strategy.entry("Long", strategy.long)
        if ctx["pos"][i] == 1:
            broker.entry("Long", "long")
