"""Port of sources/SM_b2631f95f4cad846.pine (batch_001/EMA交叉与布林带双重入场策略结合趋势跟踪与波动突破的量化交易系统EMA-Crossover-with-Bollinger-Bands-Double-Entry-Strategy-A-Quantitative-Trading-System-Combining-Trend-Following-and-Volatility-Breakout.md).

Pine v5. An EMA(12/26) crossover with an optional second entry on a Bollinger
band breakout, a risk-percent position size, and an ATR (or N-day-low) stop:

    fastEMA = ta.ema(close, 12)      slowEMA = ta.ema(close, 26)
    atr     = ta.atr(14)
    bbBasis = ta.sma(close, 55)      bbDev = 0.9 * ta.stdev(close, 55)
    bbUpper = bbBasis + bbDev        bbLower = bbBasis - bbDev
    longCondition  = ta.crossover(fastEMA, slowEMA)
    shortCondition = ta.crossunder(fastEMA, slowEMA)
    bullish = fastEMA > slowEMA      bearish = fastEMA < slowEMA
    bbBreakout = close > bbUpper and close[1] <= bbUpper[1]
    lowestLow  = ta.lowest(low, 5)

    entryConditions = (longCondition or (bbBreakout and bullish))
                      and (not useBBPauseResume or close > bbBasis)
                      and not pauseTrading
    if entryConditions and not inPosition:
        stopLoss := useATRStopLoss ? close - atr * atrMultiplier : lowestLow
        riskAmount   = strategy.equity * (riskPerTrade / 100)
        positionSize = riskAmount / (close - stopLoss)
        strategy.entry("Long", strategy.long, qty=positionSize)
        inPosition := true; pauseTrading := false

    if inPosition and bbBreakout and bullish and (not useBBPauseResume or close > bbBasis):
        bbPositionSize = strategy.equity * (bbRiskPerTrade / 100) / (close - stopLoss)
        strategy.entry("Long_BB", strategy.long, qty=bbPositionSize)

    if shortCondition or (useBBPauseResume and inPosition and close < bbBasis):
        ...  strategy.close_all(...) ...
    if strategy.position_size > 0:
        strategy.exit("Stop Loss", "Long",    stop=stopLoss)
        strategy.exit("Stop Loss", "Long_BB", stop=stopLoss)

`strategy()` declares `initial_capital = 1000`, `default_qty_type = strategy.cash`
and `default_qty_value = 100`; the rest is Pine's documented default (commission
0%, pyramiding 0, process_orders_on_close false). The `cash`/100 default never
sizes anything here -- both entries pass an explicit `qty=`.

FIDELITY -- what is preserved and what is a modelling choice:

* `positionSize` is sized off `strategy.equity`, which is engine state, not a
  function of price, so it is computed in `pine_script` from `broker.equity`
  (the engine's mark-to-market at that bar's close, which is what Pine's
  `strategy.equity` is when the script is evaluated at bar close). It is NOT
  re-derived from Freqtrade's wallet: the port hands the framework the notional
  the engine actually committed, per PinePortBase.custom_stake_amount.
* `useBBPauseResume` defaults to False, so the pause/resume machinery and the
  second `close_all` branch are inert; all of it is still implemented, so an
  override through `source_parameters` stays faithful.
* `pyramiding` is not declared, so it is Pine's default 0. The `Long_BB` entry
  is therefore always a same-direction add on an open position and Pine ignores
  it -- the "double entry" never actually stacks. Reproduced as written rather
  than promoted to pyramiding=1, which the source does not declare.
* `strategy.exit("Stop Loss", "Long", ...)` and
  `strategy.exit("Stop Loss", "Long_BB", ...)` share ONE order id, and Pine
  keeps one order per id: the second call replaces the first. The port issues
  both calls in order and lets pine_engine's same-id replacement do the same
  (PINE_SEMANTICS 1.12 / 3.6). Both arms use the same level, so only the
  `from_entry` binding differs.
* `strategy.exit` is only reached under `if strategy.position_size > 0`, and the
  engine evaluates it at that bar's close, so the stop is not in force on the
  entry's own fill bar -- it first rests on the bar after. `used_exit_levels`
  reflects exactly that.
* On the bar a `close_all` fires, `position_size` is still the old position
  (the close fills at the next open), so the `strategy.exit` below it runs with
  `stopLoss` already set to na. Pine passes `stop = na`, a no-leg exit that does
  nothing; the port passes no stop, matching.
* `entryPrice` is a `var float` that is assigned and never read, and `bearish`
  is computed and never used; neither can place an order. They are not
  reproduced (noted rather than invented).
* `startDate` / `endDate` are `input(timestamp(...))` values that nothing reads
  -- there is no date gate in the code -- so the backtest window is whatever the
  caller passes, not 2020-01-01..9999-12-31. They stay in `source_defaults`.
* `useATRStopLoss` defaults to True, so the stop is `close - atr * 1.0`; the
  `lowestLow` branch (`ta.lowest(low, 5)`) is implemented and inert.
* The md PROSE describes the same dual-entry design as the code and mentions no
  parameter the code lacks, so there is no md-vs-code difference to record.
* `alert()` / `alertcondition()` and the `plot` calls are alert- and
  display-only and place no order.
* If the computed `qty` is na (only reachable if `atr` were na while a signal
  fired, which the 55-bar Bollinger warmup rules out), pine_engine falls back to
  the declared `cash`/100 default. Noted, not patched.
* Leverage, margin, liquidation, funding and the venue's contract-step rounding
  are not modelled; the contract step matters here because the declared capital
  is only 1000 USDT, which PINE_SEMANTICS 1.6 lists as the band where step
  rounding can drift the two wallets apart. The chain verifier measures it.
"""
from __future__ import annotations

import numpy as np
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


class SMEmaCrossoverBollingerDoubleEntry_b2631f(PinePortBase, IStrategy):
    source_id = "SM_b2631f95f4cad846"
    source_file = (
        "EMA交叉与布林带双重入场策略结合趋势跟踪与波动突破的量化交易系统"
        "EMA-Crossover-with-Bollinger-Bands-Double-Entry-Strategy-A-Quantitative-"
        "Trading-System-Combining-Trend-Following-and-Volatility-Breakout.md"
    )
    timeframe = "1d"
    can_short = False
    source_defaults: dict = {
        "fastLength": 12,
        "slowLength": 26,
        "atrPeriod": 14,
        "atrMultiplier": 1.0,
        "useATRStopLoss": True,
        "stopLossDays": 5,
        "riskPerTrade": 3.0,
        "bbRiskPerTrade": 1.5,
        "bbLength": 55,
        "bbMult": 0.9,
        "useBBPauseResume": False,
        "startDate": "2020-01-01",
        "endDate": "9999-12-31",
    }
    source_qty_type = "cash"
    source_qty_value = 100.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1000.0
    source_reproduce_stops = True
    source_fidelity_notes = [
        "`positionSize` is sized off `strategy.equity`, which is engine state, so "
        "it is computed in pine_script from `broker.equity` (the engine's "
        "mark-to-market at the bar's close, as Pine's strategy.equity is when "
        "the script is evaluated at bar close) and the framework is handed the "
        "notional the engine actually committed.",
        "pyramiding is not declared, so it is Pine's default 0 and the Long_BB "
        "add is always blocked by it: the source's 'double entry' never stacks. "
        "Reproduced as written, not promoted to pyramiding=1.",
        "The two `strategy.exit(\"Stop Loss\", ...)` calls share one order id, so "
        "Pine's one-order-per-id replacement applies; both arms use the same "
        "level and differ only in `from_entry` (PINE_SEMANTICS 1.12 / 3.6).",
        "`strategy.exit` sits under `if strategy.position_size > 0` and is "
        "evaluated at bar close, so the stop is not in force on the entry's own "
        "fill bar; used_exit_levels reflects that.",
        "On a close_all bar, position_size still holds the old position, so the "
        "`strategy.exit` below runs with stopLoss = na; the same happens on an "
        "entry taken inside the ATR warmup, where `close - atr * mult` is na "
        "(ta.atr needs 14 bars while the EMAs seed on bar 0, so this IS reachable "
        "at the start of a window). Pine's `stop = na` is an unset parameter that "
        "does nothing; it is carried through as a NaN level, which the engine "
        "treats as an untriggerable leg and never publishes, rather than as a "
        "no-leg exit the projection layer would turn into a market exit every "
        "bar (PINE_SEMANTICS 1.15). The two calls are still made in order.",
        "`entryPrice` is assigned and never read, and `bearish` is computed and "
        "never used; neither can place an order and neither is reproduced.",
        "`startDate` / `endDate` are input(timestamp(...)) values that nothing "
        "reads -- the code has no date gate -- so they are carried in "
        "source_defaults only.",
        "useATRStopLoss defaults to True, so the stop is close - atr * 1.0; the "
        "ta.lowest(low, 5) branch is implemented and inert.",
        "useBBPauseResume defaults to False, making the pause/resume machinery "
        "and the second close_all branch inert; both are implemented anyway.",
        "The declared capital is only 1000 USDT, the band PINE_SEMANTICS 1.6 "
        "flags for venue contract-step rounding; that is measured by the chain "
        "verifier, not modelled here.",
        "alert() / alertcondition() and the plot calls are alert- and "
        "display-only.",
        "Leverage, margin, liquidation, funding and venue contract-step rounding "
        "are not modelled.",
    ]

    def pine_indicators(self, dataframe, params):
        close = dataframe["close"]
        fast_ema = ta.pine_ema(close, int(params["fastLength"]))
        slow_ema = ta.pine_ema(close, int(params["slowLength"]))
        atr = ta.pine_atr(dataframe, int(params["atrPeriod"]))

        bb_length = int(params["bbLength"])
        bb_basis = ta.pine_sma(close, bb_length)
        bb_dev = float(params["bbMult"]) * ta.pine_stdev(close, bb_length)
        bb_upper = bb_basis + bb_dev
        bb_lower = bb_basis - bb_dev

        long_condition = ta.pine_crossover(fast_ema, slow_ema)
        short_condition = ta.pine_crossunder(fast_ema, slow_ema)
        bullish = fast_ema > slow_ema
        bb_breakout = (close > bb_upper) & (close.shift(1) <= bb_upper.shift(1))
        lowest_low = ta.pine_lowest(dataframe["low"], int(params["stopLossDays"]))

        dataframe["pine_fast_ema"] = fast_ema
        dataframe["pine_slow_ema"] = slow_ema
        dataframe["pine_atr"] = atr
        dataframe["pine_bb_basis"] = bb_basis
        dataframe["pine_bb_upper"] = bb_upper
        dataframe["pine_bb_lower"] = bb_lower
        dataframe["pine_long_condition"] = long_condition
        dataframe["pine_short_condition"] = short_condition
        dataframe["pine_bullish"] = bullish
        dataframe["pine_bb_breakout"] = bb_breakout
        dataframe["pine_lowest_low"] = lowest_low
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "close": dataframe["close"].to_numpy(),
            "atr": dataframe["pine_atr"].to_numpy(),
            "bb_basis": dataframe["pine_bb_basis"].to_numpy(),
            "long_condition": dataframe["pine_long_condition"].to_numpy(dtype=bool),
            "short_condition": dataframe["pine_short_condition"].to_numpy(dtype=bool),
            "bullish": dataframe["pine_bullish"].to_numpy(dtype=bool),
            "bb_breakout": dataframe["pine_bb_breakout"].to_numpy(dtype=bool),
            "lowest_low": dataframe["pine_lowest_low"].to_numpy(),
            "atr_multiplier": float(params["atrMultiplier"]),
            "use_atr_stop_loss": bool(params["useATRStopLoss"]),
            "risk_per_trade": float(params["riskPerTrade"]),
            "bb_risk_per_trade": float(params["bbRiskPerTrade"]),
            "use_bb_pause_resume": bool(params["useBBPauseResume"]),
            # `var float stopLoss = na`, `var bool inPosition = false`,
            # `var bool pauseTrading = false`, persistent across bars.
            "state": {"stop_loss": np.nan, "in_position": False, "pause_trading": False},
        }

    def pine_script(self, broker, i, ctx):
        state = ctx["state"]
        close = ctx["close"][i]
        use_pause_resume = ctx["use_bb_pause_resume"]
        above_basis = close > ctx["bb_basis"][i]
        below_basis = close < ctx["bb_basis"][i]

        # entryConditions = (longCondition or (bbBreakout and bullish))
        #                   and (not useBBPauseResume or close > bbBasis)
        #                   and not pauseTrading
        entry_conditions = (
            (ctx["long_condition"][i] or (ctx["bb_breakout"][i] and ctx["bullish"][i]))
            and (not use_pause_resume or above_basis)
            and not state["pause_trading"]
        )
        # if entryConditions and not inPosition
        if entry_conditions and not state["in_position"]:
            atr_stop_loss = close - (ctx["atr"][i] * ctx["atr_multiplier"])
            low_stop_loss = ctx["lowest_low"][i]
            state["stop_loss"] = (
                atr_stop_loss if ctx["use_atr_stop_loss"] else low_stop_loss
            )
            risk_amount = broker.equity * (ctx["risk_per_trade"] / 100.0)
            position_size = risk_amount / (close - state["stop_loss"])
            # strategy.entry("Long", strategy.long, qty=positionSize)
            broker.entry("Long", "long", qty=float(position_size))
            state["in_position"] = True
            state["pause_trading"] = False

        # if inPosition and bbBreakout and bullish and (not useBBPauseResume or close > bbBasis)
        if (
            state["in_position"]
            and ctx["bb_breakout"][i]
            and ctx["bullish"][i]
            and (not use_pause_resume or above_basis)
        ):
            bb_risk_amount = broker.equity * (ctx["bb_risk_per_trade"] / 100.0)
            bb_position_size = bb_risk_amount / (close - state["stop_loss"])
            # strategy.entry("Long_BB", strategy.long, qty=bbPositionSize)
            broker.entry("Long_BB", "long", qty=float(bb_position_size))

        # if shortCondition or (useBBPauseResume and inPosition and close < bbBasis)
        if ctx["short_condition"][i] or (
            use_pause_resume and state["in_position"] and below_basis
        ):
            if ctx["short_condition"][i]:
                # strategy.close_all(comment="EMA Crossdown")
                broker.close_all()
                state["in_position"] = False
                state["pause_trading"] = False
            elif use_pause_resume:
                # strategy.close_all(comment="Close under BB basic")
                broker.close_all()
                state["pause_trading"] = True
            state["stop_loss"] = np.nan

        # if useBBPauseResume and pauseTrading and close > bbBasis
        if use_pause_resume and state["pause_trading"] and above_basis:
            state["pause_trading"] = False

        # if strategy.position_size > 0
        if broker.position_size > 0:
            # `stopLoss` can be na here -- it is set from `close - atr * mult`
            # on the entry bar, and ta.atr needs 14 bars while the EMAs seed on
            # bar 0, so an entry inside the ATR warmup freezes stopLoss at na.
            # Pine's `stop = na` means the parameter is unset, and an exit with
            # no price parameter does nothing; the na is passed through as a NaN
            # level, which the engine treats as a leg that can never trigger and
            # never publishes (PINE_SEMANTICS 1.15: a no-leg `strategy.exit` is
            # a Pine no-op and must not become a framework market exit).
            stop_level = float(state["stop_loss"])
            # strategy.exit("Stop Loss", "Long",    stop=stopLoss)
            broker.exit("Stop Loss", from_entry="Long", stop=stop_level)
            # strategy.exit("Stop Loss", "Long_BB", stop=stopLoss)
            broker.exit("Stop Loss", from_entry="Long_BB", stop=stop_level)
