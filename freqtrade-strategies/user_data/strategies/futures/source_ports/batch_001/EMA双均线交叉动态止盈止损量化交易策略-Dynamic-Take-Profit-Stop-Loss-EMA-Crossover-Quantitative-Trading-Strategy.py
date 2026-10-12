"""Port of sources/SM_425f0f3bc4f64d1e.pine (batch_001/EMA双均线交叉动态止盈止损量化交易策略-Dynamic-Take-Profit-Stop-Loss-EMA-Crossover-Quantitative-Trading-Strategy.md).

Pine v5, both sides. A 10/26 EMA cross with a fixed tick target and stop, and
an `inTrade` flag that keeps the strategy to one signal at a time:

    pip_value       = syminfo.mintick * 10
    target_value    = 30 * pip_value
    stoploss_value  = 10 * pip_value

    ema10 = ta.ema(close, 10)
    ema26 = ta.ema(close, 26)
    longCondition  = ta.crossover(ema10, ema26)
    shortCondition = ta.crossunder(ema10, ema26)

    var bool  inTrade = false
    var float long_take_profit  = na   // and long_stop_loss, short_take_profit,
    var float long_stop_loss    = na   // short_stop_loss, long_entry_price,
                                       // short_entry_price

    if (inTrade)
        if (not na(long_take_profit)  and close >= long_take_profit)  -> inTrade := false,
            clear the long levels, strategy.close("Long")
        if (not na(long_stop_loss)    and close <= long_stop_loss)    -> idem
        if (not na(short_take_profit) and close <= short_take_profit) -> inTrade := false,
            clear the short levels, strategy.close("Short")
        if (not na(short_stop_loss)   and close >= short_stop_loss)   -> idem

    if (not inTrade)
        if (longCondition)   long levels := close +/- target/stop;
                             strategy.entry("Long", strategy.long);
                             strategy.exit("Take Profit/Stop Loss", "Long",
                                           limit=long_take_profit, stop=long_stop_loss)
                             inTrade := true
        if (shortCondition)  short levels := close -/+ target/stop;
                             strategy.entry("Short", strategy.short);
                             strategy.exit("Take Profit/Stop Loss", "Short",
                                           limit=short_take_profit, stop=short_stop_loss)
                             inTrade := true

THERE ARE TWO EXIT PATHS AND THEY ARE NOT THE SAME ONE. `strategy.exit` is a
RESTING OCA order with both a `limit` (take-profit) and a `stop`, live inside
the bar; the `if (inTrade)` block above it is a separate, CLOSE-PRICE test that
issues a `strategy.close` -- a MARKET order filling at the next bar's open. Both
are reproduced. The resting legs reach the framework through `pine_stop_level` /
`pine_limit_level` (custom_stoploss + the ROI override); the `strategy.close`
calls are projected as ordinary exit signals.

The levels are anchored to the SIGNAL BAR'S CLOSE, not to the fill price. The
entry actually fills at the next bar's open, so the realised reward:risk is only
nominally 3:1. That is the source's own arithmetic, reproduced as written.

The whole thing is stateful (`inTrade` and the four `var float` levels), so the
state is a per-run dict handed to the script through `pine_context`. A run-local
container is what keeps the causality check meaningful: every
`populate_indicators` call -- full frame or truncated prefix -- starts a fresh
run and therefore fresh `var` state, exactly as a Pine run does.

`strategy(title=..., overlay=true)` declares nothing else, so every property is
Pine's documented default: `strategy.fixed` / 1 contract, initial capital
1000000, commission 0%, pyramiding 0, `process_orders_on_close=false`.

FIDELITY:

* Two distinct exit mechanisms, both reproduced: the resting `strategy.exit`
  OCA (stop + limit) and the `strategy.close` market exit driven by the close
  price. They can both be reachable on the same bar; the resting leg is checked
  first (it is live during the bar) and the market close is a no-op if the
  resting leg already flattened the position, which is what the engine's
  `_close_entries(from_entry=...)` does.
* `pip_value = syminfo.mintick * 10`. TradingView reads the tick size off the
  symbol and the source does not state it; `source_mintick` is 0.1 (the
  BTC/USDT:USDT increment this corpus uses), so pip_value is 1.0 and the target
  / stop are 30.0 and 10.0 price units (PINE_SEMANTICS.md 3.5). The comment in
  the source ("1 pip = 0.0001 for forex") does not apply to this instrument.
* The md's own title says "30 Pips Target & 15 Pips Stop-Loss" while the code
  uses `stoploss_in_pips = 10`. The code is followed; the disagreement is
  recorded, not reconciled.
* `var float long_entry_price` / `short_entry_price` are assigned on every entry
  and never read. They are carried in the state as written and, like the source,
  never used.
* `if (not inTrade)` reads `inTrade` AFTER the exit block may have cleared it,
  so a stop or take-profit bar can also open a fresh trade on the same bar. The
  two inner `if`s do not re-test `inTrade` between them (the source does not
  either); `ta.crossover` and `ta.crossunder` are mutually exclusive, so at most
  one can fire.
* The exit block resets only the levels of the side it fired on. The other
  side's levels keep their last value and their `close`-vs-level test keeps
  being evaluated on later bars; reproduced literally.
* `strategy.exit` re-uses ONE id ("Take Profit/Stop Loss") for both sides, so
  Pine's same-id replacement applies; the engine's `_place` replaces same-id
  `exit` orders, and each is additionally bound by `from_entry` so a long-bound
  exit publishes nothing while only a short is open (PINE_SEMANTICS.md 1.12).
* The stop / take-profit are computed from the signal bar's close, so on the
  entry's fill bar they are a fixed distance from a price the position did not
  fill at. That is the source's arithmetic, not a translation choice.
* `plot(...)` and `plotshape(...)` are display-only and place no orders; they
  are not reproduced beyond the levels they would have drawn.
* na handling: the EMA pair is na for the first ~25 bars, so neither cross can
  fire (Pine na comparisons are false). The four level variables start na on
  bar 0 and `not na(...)` gates every test on them.
* Both legs of the OCA exit are reproduced; a port carrying only the stop leg
  would silently lose the take-profit (PINE_SEMANTICS.md 1.8).
* Leverage, margin, liquidation, funding and contract-step rounding are not
  modelled; the chain verifier measures the rounding separately.
"""
from __future__ import annotations

import math

from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase

# target_in_pips / stoploss_in_pips are plain literals in the source, not
# input()s, so they are not part of source_defaults.
TARGET_IN_PIPS = 30.0
STOPLOSS_IN_PIPS = 10.0


class SMDynamicTakeProfitStopLossEma_425f0f(PinePortBase, IStrategy):
    source_id = "SM_425f0f3bc4f64d1e"
    source_file = (
        "EMA双均线交叉动态止盈止损量化交易策略-Dynamic-Take-Profit-Stop-Loss-"
        "EMA-Crossover-Quantitative-Trading-Strategy.md"
    )
    timeframe = "1d"
    can_short = True
    # The source has no input() calls: target_in_pips / stoploss_in_pips are
    # plain literals.
    source_defaults: dict = {}
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    source_reproduce_stops = True
    source_mintick = 0.1
    source_fidelity_notes = [
        "pip_value = syminfo.mintick * 10. The source does not state the symbol's "
        "tick size; source_mintick = 0.1 (BTC/USDT:USDT, this corpus' convention) "
        "makes pip_value 1.0 and the target / stop 30.0 / 10.0 price units "
        "(PINE_SEMANTICS.md 3.5). The source's forex comment does not apply here.",
        "The md's own title says '15 Pips Stop-Loss' while the code uses "
        "stoploss_in_pips = 10. Code followed; disagreement recorded.",
        "TWO exit paths, both reproduced: the resting strategy.exit OCA "
        "(stop + limit, live inside the bar -> pine_stop_level / "
        "pine_limit_level) and the close-price test that issues strategy.close "
        "(a market exit -> a projected exit signal).",
        "The levels are anchored to the SIGNAL BAR'S CLOSE, not to the fill "
        "price, so the realised reward:risk is only nominally 3:1. The source's "
        "own arithmetic.",
        "`if (not inTrade)` reads inTrade AFTER the exit block may have cleared "
        "it, so a stop / take-profit bar can also open a fresh trade on the same "
        "bar. The two inner `if`s do not re-test inTrade between them, as in the "
        "source; crossover and crossunder cannot both be true.",
        "The exit block resets only the levels of the side it fired on; the "
        "other side's levels keep their last value and keep being tested. "
        "Reproduced literally.",
        "strategy.exit re-uses ONE id for both sides, so Pine's same-id "
        "replacement applies (the engine's _place replaces same-id exits), and "
        "each is bound by from_entry so a long-bound exit publishes nothing "
        "while only a short is open (PINE_SEMANTICS.md 1.12).",
        "`var float long_entry_price` / `short_entry_price` are assigned on every "
        "entry and never read; carried in the state as written, and unused.",
        "The `var` state (inTrade and the four levels) is a per-run dict from "
        "pine_context, so each populate_indicators call -- full frame or "
        "truncated prefix -- starts fresh, as a Pine run does.",
        "Both legs of the OCA exit are reproduced; a stop-only port would lose "
        "the take-profit (PINE_SEMANTICS.md 1.8).",
        "plot() / plotshape() are display-only and place no orders.",
        "na handling: the EMA pair is na for the first ~25 bars so no cross can "
        "fire, and the four levels start na on bar 0 with `not na(...)` gating "
        "every test.",
        "Leverage, margin, liquidation, funding and contract-step rounding are "
        "not modelled; the chain verifier measures the rounding separately.",
    ]

    def pine_indicators(self, dataframe, params):
        close = dataframe["close"]
        ema10 = ta.pine_ema(close, 10)
        ema26 = ta.pine_ema(close, 26)
        dataframe["pine_ema10"] = ema10
        dataframe["pine_ema26"] = ema26
        dataframe["pine_long_condition"] = ta.pine_crossover(ema10, ema26)
        dataframe["pine_short_condition"] = ta.pine_crossunder(ema10, ema26)
        return dataframe

    def pine_context(self, dataframe, params):
        # pip_value = syminfo.mintick * 10
        pip_value = float(self.source_mintick) * 10.0
        nan = float("nan")
        return {
            "close": dataframe["close"].to_numpy(dtype=float),
            "long_condition": dataframe["pine_long_condition"].to_numpy(dtype=bool),
            "short_condition": dataframe["pine_short_condition"].to_numpy(dtype=bool),
            "target_value": TARGET_IN_PIPS * pip_value,
            "stoploss_value": STOPLOSS_IN_PIPS * pip_value,
            # var bool inTrade = false / var float ... = na
            "state": {
                "in_trade": False,
                "long_entry_price": nan,
                "long_take_profit": nan,
                "long_stop_loss": nan,
                "short_entry_price": nan,
                "short_take_profit": nan,
                "short_stop_loss": nan,
            },
        }

    def pine_script(self, broker, i, ctx):
        state = ctx["state"]
        close = float(ctx["close"][i])
        in_trade = state["in_trade"]

        # if (inTrade)
        #     if (not na(long_take_profit) and close >= long_take_profit) ...
        if in_trade:
            if not math.isnan(state["long_take_profit"]) and close >= state["long_take_profit"]:
                in_trade = False
                state["long_entry_price"] = float("nan")
                state["long_take_profit"] = float("nan")
                state["long_stop_loss"] = float("nan")
                broker.close("Long")

            if not math.isnan(state["long_stop_loss"]) and close <= state["long_stop_loss"]:
                in_trade = False
                state["long_entry_price"] = float("nan")
                state["long_take_profit"] = float("nan")
                state["long_stop_loss"] = float("nan")
                broker.close("Long")

            if not math.isnan(state["short_take_profit"]) and close <= state["short_take_profit"]:
                in_trade = False
                state["short_entry_price"] = float("nan")
                state["short_take_profit"] = float("nan")
                state["short_stop_loss"] = float("nan")
                broker.close("Short")

            if not math.isnan(state["short_stop_loss"]) and close >= state["short_stop_loss"]:
                in_trade = False
                state["short_entry_price"] = float("nan")
                state["short_take_profit"] = float("nan")
                state["short_stop_loss"] = float("nan")
                broker.close("Short")

        # if (not inTrade)
        #     if (longCondition) ...
        if not in_trade:
            if ctx["long_condition"][i]:
                state["long_entry_price"] = close
                state["long_take_profit"] = close + ctx["target_value"]
                state["long_stop_loss"] = close - ctx["stoploss_value"]
                broker.entry("Long", "long")
                broker.exit(
                    "Take Profit/Stop Loss",
                    from_entry="Long",
                    limit=float(state["long_take_profit"]),
                    stop=float(state["long_stop_loss"]),
                )
                in_trade = True

            if ctx["short_condition"][i]:
                state["short_entry_price"] = close
                state["short_take_profit"] = close - ctx["target_value"]
                state["short_stop_loss"] = close + ctx["stoploss_value"]
                broker.entry("Short", "short")
                broker.exit(
                    "Take Profit/Stop Loss",
                    from_entry="Short",
                    limit=float(state["short_take_profit"]),
                    stop=float(state["short_stop_loss"]),
                )
                in_trade = True

        state["in_trade"] = in_trade
