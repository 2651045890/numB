"""Port of sources/SM_76aab2711534142a.pine (batch_001/Chande-Kroll止损动态ATR趋势跟踪策略-Chande-Kroll-Stop-Dynamic-ATR-Trend-Following-Strategy.md).

Pine v5. A one-sided trend follower built on the Chande-Kroll stop band:

    atr      = ta.atr(10)
    highStop = ta.highest(high, 21) - 3 * atr
    lowStop  = ta.lowest(low, 21) + 3 * atr
    sma21    = ta.sma(close, 21)

    longCondition    = ta.crossover(close, lowStop) and close > sma21
    exitLongCondition = close < highStop

    calc_qty(mode, riskMultiplier) =>
        lowestClose = ta.lowest(close, 1560)
        if mode == "Exponential"
            qty = riskMultiplier / lowestClose * 1000 * strategy.equity / strategy.initial_capital
        else
            qty = riskMultiplier / lowestClose * 1000

    if (longCondition)
        strategy.entry("Long", strategy.long, qty=qty)
    if (exitLongCondition)
        strategy.close("Long")

`strategy()` declares `initial_capital = 1000`, commission 0.01% (percent
commission of 0.01, i.e. one basis point), `slippage = 3` and nothing else, so
`default_qty_type` is Pine's documented `strategy.fixed`, `default_qty_value`
its documented 1, and `pyramiding` its documented 0. Both are live here because
the entry's `qty` is this source's own na-capable expression: Pine documents
`strategy.entry`'s `qty` as "The number of contracts... The default value is
NaN", and an na quantity falls back to the default order size. The engine models
that same fallback (`_try_fill_pending`: an unset or non-finite `qty` is sized
by `_size_for`), so passing na through reproduces the source's arithmetic rather
than a framework default chosen here.

The header declares `period: 1d` on Futures_Binance BTC_USDT, so `timeframe` is
"1d". The exit is `strategy.close`, a MARKET close, so there is no stop / limit /
trail leg for the engine to mirror and `source_reproduce_stops` is False. There
is no short entry anywhere in the source, so `can_short` is False.

FIDELITY:

* `slippage = 3` (three ticks of slippage on market orders) is not modelled by
  pine_engine, which fills at the bar's open with no slippage.
* `ta.atr(10)` is `pine_ta.pine_atr`, i.e. `rma(tr, 10)` with `ta.tr`'s
  `handle_na=true` first bar. PINE_SEMANTICS.md 3.7 records that Pine's own
  `ta.tr` defaults to `handle_na=false` and therefore returns na on the FIRST
  bar, while `pine_ta.pine_tr` returns `high - low` there. That moves the RMA
  seed one bar earlier, after which the two converge. Not corrected in the port
  (the public layer is frozen); recorded here.
* `qty` is computed per bar inside `pine_script` from `broker.equity`, which is
  the engine's `strategy.equity` as of the signal bar's close -- the same instant
  Pine evaluates the script. `strategy.initial_capital` is the source's declared
  1000, so the Exponential branch's `* 1000 / initial_capital` factor is
  `equity / 1000`.
* The source's 1560-bar lookback is far longer than the backtest windows this
  repo verifies on (BTC/USDT:USDT 1d, 2024, 367 bars), so `ta.lowest(close, 1560)`
  is na on every verified bar and `qty` is na throughout: the engine then applies
  Pine's documented na-quantity fallback (one contract). The source's own chart on
  TradingView carries years of daily history, so the ORIGINAL platform completes
  the window and sizes by the formula. The formula is reproduced faithfully; the
  difference is the available history, and no data outside the verified frame is
  pulled in to paper over it. See source_fidelity_notes.
* `alert(...)`, `plotshape`, `plot` and `overlay=true` are display-only and place
  no condition; they are not reproduced.
* `ta.sma` / `ta.highest` / `ta.lowest` are na-propagating and return na until
  their window is full, which is Pine's behaviour and what pine_ta implements, so
  both conditions are false through the warm-up.
* Leverage, margin, liquidation, funding and the venue's contract-step rounding
  are not modelled; the chain verifier measures the rounding separately.
"""
from __future__ import annotations

import numpy as np
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase

# Literal in the source: `lowestClose = ta.lowest(close, 1560)`.
LOWEST_CLOSE_LENGTH = 1560
# Literal in the source's qty formula.
QTY_SCALE = 1000.0


class SMChandeKrollStop_76aab2(PinePortBase, IStrategy):
    source_id = "SM_76aab2711534142a"
    source_file = (
        "Chande-Kroll止损动态ATR趋势跟踪策略-"
        "Chande-Kroll-Stop-Dynamic-ATR-Trend-Following-Strategy.md"
    )
    timeframe = "1d"
    can_short = False
    source_defaults = {
        "calcMode": "Exponential",
        "riskMultiplier": 5,
        "atrPeriod": 10,
        "atrMultiplier": 3,
        "stopLength": 21,
        "smaLength": 21,
    }
    # `strategy()` declares no default_qty_type / default_qty_value, so Pine's
    # documented `strategy.fixed` / 1 applies -- and it is what an na `qty` falls
    # back to, which is the branch that runs on the verified windows.
    source_qty_type = "fixed"
    source_qty_value = 1.0
    # commission_type = strategy.commission.percent, commission_value = 0.01.
    source_commission_percent = 0.01
    source_pyramiding = 0
    source_initial_capital = 1000.0
    # The only exit is `strategy.close("Long")` -- a market close, not a resting
    # leg -- so there is no stop / limit / trail level to mirror.
    source_reproduce_stops = False
    source_fidelity_notes = [
        "slippage = 3 is declared by the source and is not modelled; pine_engine "
        "fills market orders at the bar's open with zero slippage.",
        "ta.atr(10) is pine_ta.pine_atr, i.e. rma(tr, 10) with ta.tr's "
        "handle_na=true first bar. Pine's ta.tr defaults to handle_na=false and "
        "returns na on the first bar, so the RMA seed lands one bar earlier here "
        "(PINE_SEMANTICS.md 3.7). The public layer is not modified; recorded.",
        "The source's qty is an na-capable expression and Pine documents "
        "strategy.entry's qty default as NaN with an na quantity falling back to "
        "the default order size. The engine models the same fallback, so an na "
        "qty is passed through rather than replaced here.",
        "ta.lowest(close, 1560) never completes on the windows this repo verifies "
        "(367 daily bars), so qty is na on every verified bar and the fallback "
        "sizes the entry at one contract. The source's TradingView chart carries "
        "years of daily history and would complete the window, so the ORIGINAL "
        "platform sizes by the formula. The formula itself is reproduced verbatim; "
        "the difference is the available history. No data outside the verified "
        "frame is pulled in to hide it, and source_initial_capital is NOT raised.",
        "The Exponential branch multiplies by strategy.equity / "
        "strategy.initial_capital, evaluated at the signal bar's close; the port "
        "reads the engine's broker.equity at that same instant. strategy.equity "
        "and strategy.initial_capital are both the source's own values.",
        "alert(), plotshape(), plot() and overlay=true are display-only and place "
        "no condition.",
        "can_short is False: the source only ever places `strategy.entry(\"Long\", "
        "strategy.long, ...)`; there is no short entry.",
        "The exit is `strategy.close(\"Long\")`, a market close, so there is no "
        "resting stop / limit / trail leg and source_reproduce_stops is False.",
        "Leverage, margin, liquidation, funding and the venue's contract-step "
        "rounding are not modelled; the chain verifier measures that rounding "
        "separately rather than treating it as a signal difference.",
    ]

    def pine_indicators(self, dataframe, params):
        high = dataframe["high"].astype(float)
        low = dataframe["low"].astype(float)
        close = dataframe["close"].astype(float)

        atr = ta.pine_atr(dataframe, int(params["atrPeriod"]))
        atr_multiplier = float(params["atrMultiplier"])
        # highStop = ta.highest(high, stopLength) - atrMultiplier * atr
        high_stop = ta.pine_highest(high, int(params["stopLength"])) - atr_multiplier * atr
        # lowStop = ta.lowest(low, stopLength) + atrMultiplier * atr
        low_stop = ta.pine_lowest(low, int(params["stopLength"])) + atr_multiplier * atr
        sma = ta.pine_sma(close, int(params["smaLength"]))

        # longCondition = ta.crossover(close, lowStop) and close > sma21
        long_condition = ta.pine_crossover(close, low_stop) & (close > sma)
        # exitLongCondition = close < highStop
        exit_long_condition = close < high_stop

        # lowestClose = ta.lowest(close, 1560) -- the sizing denominator.
        lowest_close = ta.pine_lowest(close, LOWEST_CLOSE_LENGTH)

        dataframe["pine_atr"] = atr
        dataframe["pine_high_stop"] = high_stop
        dataframe["pine_low_stop"] = low_stop
        dataframe["pine_sma21"] = sma
        dataframe["pine_lowest_close"] = lowest_close
        dataframe["pine_long_condition"] = long_condition.astype(bool)
        dataframe["pine_exit_long_condition"] = exit_long_condition.astype(bool)
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "lowest_close": dataframe["pine_lowest_close"].to_numpy(dtype=float),
            "long_condition": dataframe["pine_long_condition"].to_numpy(),
            "exit_long_condition": dataframe["pine_exit_long_condition"].to_numpy(),
            # Inputs are read through source_parameters(), so they are broadcast
            # per bar and read in pine_script like any other Pine series.
            "risk_multiplier": np.full(len(dataframe), float(params["riskMultiplier"])),
            "calc_mode": np.full(len(dataframe), str(params["calcMode"]), dtype=object),
        }

    def pine_script(self, broker, i, ctx):
        # if (longCondition)
        #     strategy.entry("Long", strategy.long, qty=qty)
        if ctx["long_condition"][i]:
            broker.entry("Long", "long", qty=self._calc_qty(broker, i, ctx))
        # if (exitLongCondition)
        #     strategy.close("Long")
        if ctx["exit_long_condition"][i]:
            broker.close("Long")

    def _calc_qty(self, broker, i, ctx) -> float:
        """`calc_qty(calcMode, riskMultiplier)`, evaluated at bar `i`'s close.

        An na `lowestClose` propagates through the division, exactly as it does
        in Pine, and the engine applies Pine's documented default-size fallback.
        """
        lowest_close = ctx["lowest_close"][i]
        risk = ctx["risk_multiplier"][i]
        if lowest_close is None or not np.isfinite(lowest_close):
            # Pine: riskMultiplier / na -> na, and an na qty means "default size".
            return float("nan")
        if str(ctx["calc_mode"][i]) == "Exponential":
            return (
                risk / lowest_close * QTY_SCALE
                * broker.equity / float(self.source_initial_capital)
            )
        return risk / lowest_close * QTY_SCALE
