"""Port of sources/SM_fdf10ed076574fe7.pine (batch_001/EMA均线与抛物线SAR组合策略-EMA-and-Parabolic-SAR-Combination-Strategy.md).

Pine v5, both sides. An 8/21 EMA crossover gated by the Parabolic SAR, a
stop-loss 83 ticks below/above the signal bar's close, a `strategy.close` when
price crosses back through the SAR, and a forced `strategy.close_all()` once the
bar's clock reaches 15:15:

    emaShort = ta.ema(close, 8)
    emaLong  = ta.ema(close, 21)
    sar      = ta.sar(0.02, 0.02, 0.2)

    longCondition     = ta.crossover(emaShort, emaLong)  and close > sar
    shortCondition    = ta.crossunder(emaShort, emaLong) and close < sar
    longExitCondition = close < sar
    shortExitCondition = close > sar

    if longCondition  -> strategy.entry("Long",  strategy.long)
    if shortCondition -> strategy.entry("Short", strategy.short)
    if longExitCondition  -> strategy.close("Long")
    if shortExitCondition -> strategy.close("Short")

    strategy.exit("Long Exit",  "Long",  stop=close - fixedSL * syminfo.mintick)
    strategy.exit("Short Exit", "Short", stop=close + fixedSL * syminfo.mintick)

    exitTime = timestamp(year(timenow), month(timenow), dayofmonth(timenow), 15, 15)
    if timenow >= exitTime -> strategy.close_all()

`strategy()` declares only `title` and `overlay`, so every order property is
Pine's documented default: `strategy.fixed` quantity of 1 contract, initial
capital 1000000, commission 0%, pyramiding 0, `process_orders_on_close=false`.

THE TWO `strategy.exit` CALLS ARE UNCONDITIONAL, so a resting stop is placed on
EVERY bar. `close` there is the SIGNAL bar's close, so the stop re-anchors each
bar and the level that is live is always the latest one -- the same-id
replacement `PineBroker._place` already applies. `from_entry` binds each arm to
its own entry id, so while only a long is open the short arm publishes nothing
(PINE_SEMANTICS.md 1.12).

`timenow` IS MODELLED AS THE CURRENT BAR'S TIME, not as the wall clock at run
time -- see the first `source_fidelity_notes` entry. The source runs on FMZ
(the `/*backtest` header and the fmz.com link are both FMZ), which drives the
backtest bar by bar against a simulated clock, and the md's own principle text
("该策略要求在每个交易日的15:15强制平掉所有仓位" / "the strategy requires all
positions to be closed at 15:15 on each trading day") only describes a rule that
exists if the clock follows the bars. Under the other reading -- TradingView's,
where `timenow` is the real current time -- `exitTime` would be built from
`timenow`'s own date and the test would be a constant, so `close_all` would
either fire on every bar or never; recording the choice because it decides
whether the forced exit exists at all.

FIDELITY:

* `pine_ta` has no `sar`, so the port carries Wilder's recursion locally
  (`_pine_sar`). Pine does not publish `ta.sar`'s seeding rule, so the initial
  state (trend = up, SAR = low[0], EP = high[0], AF = start) is a MODELLED
  CHOICE (same model as `SMHighLowSar`, this corpus' other SAR port). It can
  only diverge during warm-up, and the 21-bar EMA warm-up covers most of it.
* `fixedSL * syminfo.mintick` = 83 * 0.1 = 8.3 price units. The source does not
  state the symbol's tick size; `source_mintick = 0.1` is this corpus'
  BTC/USDT:USDT convention (PINE_SEMANTICS.md 3.5). The md's "Fixed Stop Loss
  (pts)" wording is about tick counts, which is what Pine's own `stop=` here
  consumes as a PRICE -- `syminfo.mintick` is what converts one to the other.
* `ta.ema` seeding is the modelled first-non-na choice (PINE_SEMANTICS.md 3.1).
  Both averages share it, so only a cross inside the warm-up would move.
* `ta.crossover` / `ta.crossunder` use `pine_ta`'s modelled definition
  (`a > b` and `a[1] <= b[1]`); na comparisons evaluate false, as in Pine's
  `if`.
* `strategy.exit` re-uses two distinct ids, so same-id replacement applies
  within each side. Both arms are placed every bar with no `when`, so they rest
  continuously; `close_all` is the only call that goes through `close_all`.
* `strategy.close_all()` is a MARKET order: the engine fills it at the next
  bar's open, one bar after the 15:15 clock test first holds.
* `plot()` calls, the title and `overlay` are display-only and place no order.
* The `/*backtest` header declares `period: 1h` on Futures_Binance BTC_USDT, so
  `timeframe` is "1h"; `basePeriod: 15m` is the FMZ backtester's own fill
  granularity, not the strategy's period.
* The md's Strategy Principles match the code for this source -- the 8/21 EMA
  cross, the SAR gate, the SAR-cross exit, the fixed stop and the 15:15 forced
  exit are all described as implemented. No disagreement to record.
* Leverage, margin, liquidation, funding and contract-step rounding are not
  modelled; the chain verifier measures the rounding separately.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


def _pine_sar(high, low, start=0.02, increment=0.02, maximum=0.2):
    """Pine `ta.sar(start, inc, max)` -- Wilder's Parabolic SAR.

    MODELLED CHOICE (parity risk, recorded in `source_fidelity_notes`): the
    recursion is the standard one -- SAR_t = SAR_(t-1) + AF * (EP - SAR_(t-1)),
    clamped so it may not penetrate the previous two bars' extremes; a bar whose
    extreme crosses the clamped SAR flips the trend, resets AF to `start` and
    re-seeds EP with that bar's extreme. Pine does not publish `ta.sar`'s
    seeding rule, so the initial state (trend = up, SAR = low[0], EP = high[0],
    AF = start) is this port's model. Only the warm-up bars can diverge, and the
    source's 21-bar EMA warm-up covers most of them.
    """
    high = np.asarray(high, dtype=float)
    low = np.asarray(low, dtype=float)
    count = len(high)
    out = np.full(count, np.nan)
    if count == 0:
        return out
    start, increment, maximum = float(start), float(increment), float(maximum)
    uptrend = True
    sar = low[0]
    extreme = high[0]
    accel = start
    out[0] = sar
    for i in range(1, count):
        bar_high, bar_low = high[i], low[i]
        sar = sar + accel * (extreme - sar)
        if uptrend:
            prior = low[i - 1] if i < 2 else min(low[i - 1], low[i - 2])
            sar = min(sar, prior)
            if bar_low < sar:
                uptrend = False
                sar = extreme
                extreme = bar_low
                accel = start
            elif bar_high > extreme:
                extreme = bar_high
                accel = min(accel + increment, maximum)
        else:
            prior = high[i - 1] if i < 2 else max(high[i - 1], high[i - 2])
            sar = max(sar, prior)
            if bar_high > sar:
                uptrend = True
                sar = extreme
                extreme = bar_high
                accel = start
            elif bar_low < extreme:
                extreme = bar_low
                accel = min(accel + increment, maximum)
        out[i] = sar
    return out


class SMEmaAndParabolicSarCombination_fdf10e(PinePortBase, IStrategy):
    source_id = "SM_fdf10ed076574fe7"
    source_file = (
        "EMA均线与抛物线SAR组合策略-EMA-and-Parabolic-SAR-Combination-Strategy.md"
    )
    timeframe = "1h"
    can_short = True
    source_defaults: dict = {
        "emaShortPeriod": 8,
        "emaLongPeriod": 21,
        "sarStart": 0.02,
        "sarIncrement": 0.02,
        "sarMaximum": 0.2,
        "fixedSL": 83,
    }
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    source_reproduce_stops = True
    source_mintick = 0.1
    # The forced flat happens at 15:15 on the BAR's own day; see the notes.
    EXIT_HOUR = 15
    EXIT_MINUTE = 15
    source_fidelity_notes = [
        "`timenow` is MODELLED AS THE CURRENT BAR'S TIME. The source runs on FMZ "
        "(the /*backtest header and the fmz.com detail link), whose backtester "
        "drives bars against a simulated clock, and the md's own principle text "
        "('close all positions at 15:15 on each trading day') only describes a "
        "rule that exists under that reading. Under TradingView's reading -- "
        "`timenow` is the real current time -- `exitTime` would be built from "
        "`timenow`'s own date and `timenow >= exitTime` would be a constant, so "
        "`strategy.close_all()` would fire on every bar or on none. The choice "
        "decides whether the forced exit exists at all, hence this note.",
        "`ta.sar` is not in pine_ta, so the port carries Wilder's recursion "
        "locally (`_pine_sar`). Pine does not publish `ta.sar`'s seeding rule; "
        "the initial state (trend up, SAR = low[0], EP = high[0], AF = start) "
        "is a MODELLED CHOICE and the warm-up bars are where it can diverge. The "
        "source first reads sar against a 21-bar EMA, whose own warm-up covers "
        "most of that window.",
        "`fixedSL * syminfo.mintick` = 83 * 0.1 = 8.3 price units. The source "
        "does not state the symbol's tick size; source_mintick = 0.1 is this "
        "corpus' BTC/USDT:USDT convention (PINE_SEMANTICS.md 3.5).",
        "Both `strategy.exit` calls are UNCONDITIONAL, so a resting stop is "
        "placed on every bar and `close` (the SIGNAL bar's close) re-anchors it "
        "each bar; the engine's same-id replacement leaves the newest one "
        "resting. `from_entry` binds each arm to its own entry, so the short arm "
        "publishes no level while only a long is open (PINE_SEMANTICS.md 1.12).",
        "`strategy.close_all()` is a MARKET order: the engine fills it at the "
        "next bar's open, i.e. one bar after the 15:15 test first holds.",
        "`ta.ema` seeding is the modelled first-non-na choice (PINE_SEMANTICS.md "
        "3.1); both averages share it, so only a cross inside the warm-up would "
        "be affected.",
        "`ta.crossover` / `ta.crossunder` use pine_ta's modelled definition "
        "(`a > b` and `a[1] <= b[1]`); na comparisons are false, as in Pine.",
        "`strategy()` declares only title/overlay, so qty_type=fixed, qty_value="
        "1 contract, commission=0%, pyramiding=0 and initial_capital=1000000 "
        "are Pine's documented defaults.",
        "The md's Strategy Principles describe this source's actual code (8/21 "
        "EMA cross, SAR gate, SAR-cross exit, fixed stop, 15:15 forced exit); "
        "no disagreement to record.",
        "plot() and the title/overlay are display-only and place no order.",
        "The /*backtest header's `period: 1h` is the strategy's timeframe; "
        "`basePeriod: 15m` is the FMZ backtester's fill granularity.",
        "Leverage, margin, liquidation, funding and contract-step rounding are "
        "not modelled; the chain verifier measures the rounding separately.",
    ]

    def pine_indicators(self, dataframe, params):
        close = dataframe["close"]
        ema_short = ta.pine_ema(close, int(params["emaShortPeriod"]))
        ema_long = ta.pine_ema(close, int(params["emaLongPeriod"]))
        sar = _pine_sar(
            dataframe["high"].to_numpy(dtype=float),
            dataframe["low"].to_numpy(dtype=float),
            params["sarStart"],
            params["sarIncrement"],
            params["sarMaximum"],
        )
        sar = pd.Series(sar, index=dataframe.index)
        dataframe["pine_ema_short"] = ema_short
        dataframe["pine_ema_long"] = ema_long
        dataframe["pine_sar"] = sar
        dataframe["pine_long_condition"] = (
            ta.pine_crossover(ema_short, ema_long) & (close > sar)
        )
        dataframe["pine_short_condition"] = (
            ta.pine_crossunder(ema_short, ema_long) & (close < sar)
        )
        dataframe["pine_long_exit"] = close < sar
        dataframe["pine_short_exit"] = close > sar
        # exitTime = timestamp(year(timenow), month(timenow), dayofmonth(timenow),
        #                       exitHour, exitMinute)   [timenow = this bar's time]
        # if timenow >= exitTime -> strategy.close_all()
        index = dataframe.index
        if isinstance(index, pd.DatetimeIndex):
            exit_time = index.normalize() + pd.Timedelta(
                hours=self.EXIT_HOUR, minutes=self.EXIT_MINUTE
            )
            dataframe["pine_close_all"] = index >= exit_time
        else:  # pragma: no cover - the base class always supplies a DatetimeIndex
            dataframe["pine_close_all"] = False
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "close": dataframe["close"].to_numpy(dtype=float),
            "long_condition": dataframe["pine_long_condition"].to_numpy(dtype=bool),
            "short_condition": dataframe["pine_short_condition"].to_numpy(dtype=bool),
            "long_exit": dataframe["pine_long_exit"].to_numpy(dtype=bool),
            "short_exit": dataframe["pine_short_exit"].to_numpy(dtype=bool),
            "close_all": dataframe["pine_close_all"].to_numpy(dtype=bool),
            # fixedSL * syminfo.mintick
            "stop_offset": float(params["fixedSL"]) * float(self.source_mintick),
        }

    def pine_script(self, broker, i, ctx):
        close = float(ctx["close"][i])
        stop_offset = ctx["stop_offset"]

        # if (longCondition)
        #     strategy.entry("Long", strategy.long)
        if ctx["long_condition"][i]:
            broker.entry("Long", "long")
        # if (shortCondition)
        #     strategy.entry("Short", strategy.short)
        if ctx["short_condition"][i]:
            broker.entry("Short", "short")
        # if (longExitCondition)
        #     strategy.close("Long")
        if ctx["long_exit"][i]:
            broker.close("Long")
        # if (shortExitCondition)
        #     strategy.close("Short")
        if ctx["short_exit"][i]:
            broker.close("Short")
        # strategy.exit("Long Exit",  "Long",  stop=close - fixedSL * syminfo.mintick)
        broker.exit("Long Exit", "Long", stop=close - stop_offset)
        # strategy.exit("Short Exit", "Short", stop=close + fixedSL * syminfo.mintick)
        broker.exit("Short Exit", "Short", stop=close + stop_offset)
        # if (timenow >= exitTime)
        #     strategy.close_all()
        if ctx["close_all"][i]:
            broker.close_all()
