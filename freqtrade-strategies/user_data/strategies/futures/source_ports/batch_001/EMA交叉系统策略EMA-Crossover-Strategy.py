"""Port of sources/SM_58562ef472b7954d.pine (batch_001/EMA交叉系统策略EMA-Crossover-Strategy.md).

Pine v4 ("Crossing Ema 20:9 by Sedkur"). A 9/20 EMA cross, long on the cross
above and short on the cross below, gated by a calendar year test:

    src    = close
    ema20  = ema(src, 20)
    ema9   = ema(src, 9)
    bullish = cross(ema9, ema20) and (ema9  > ema20) ? true : false
    bearish = cross(ema9, ema20) and (ema20 > ema9 ) ? true : false

    if (bullish) strategy.entry("buy",  strategy.long,  comment="al",  when = year > 2016)
    if (bearish) strategy.entry("sell", strategy.short, comment="sat", when = year > 2016)

`strategy(title=..., overlay=false)` declares nothing else, so every order
property is Pine's documented default: `strategy.fixed` quantity of 1 contract,
initial capital 1000000, commission 0%, pyramiding 0,
`process_orders_on_close=false`. There is no exit call of any kind: a position
goes flat only when the opposite entry reverses it, so `source_reproduce_stops`
is False and a position still open at the end of the window stays open.

`cross(a, b)` is v4's deprecated both-ways cross alias. ANDed with the level test
it degenerates to one direction each: `cross(...) and a > b` is exactly
`crossover(a, b)`, and `cross(...) and b > a` is exactly `crossunder(a, b)`. The
port keeps the two-factor form as written rather than collapsing it, so the
source's structure stays visible; the values are identical either way.

`when = year > 2016` is `strategy.entry`'s `when` argument, and `year` is the
current BAR's year (Pine's builtin), so the gate is a calendar test on the bar's
own timestamp, not on the run date. The declared backtest window is 2022-09-21
to 2023-09-27, over which it is always true, and it is reproduced as written so a
caller running an earlier window gets the source's behaviour.

FIDELITY:

* `ta.ema` is pine_ta.pine_ema, whose seed is the modelled first-non-na choice
  (PINE_SEMANTICS.md 3.1): TradingView does not publish v4 `ema`'s seeding rule.
  Both averages share it, so only a cross falling inside the warm-up is at risk.
* The md's prose describes `bullish` as being set when ema9 > ema20 OR on a
  cross -- two independent triggers, "dual validation ... to avoid missing
  signals". The code ANDs them (`cross(...) and (ema9 > ema20)`), which is a
  single condition equal to the crossover. Code followed; the prose is not.
  The source also carries the original author's commented-out line
  `//bullish = (ema9>ema20)?true:false`, which is what the prose still
  describes -- it is commented out and places no condition.
* `year` is read off the bar's own timestamp (the base class guarantees the frame
  is indexed by candle time, PINE_SEMANTICS.md 1.2), and the comparison is
  strict, `year > 2016`.
* `plot(ema20)` / `plot(ema9)` / `plot(strategy.equity)` / the two `plotshape`
  markers / `alertcondition` / `overlay` are display or alert only and place no
  order.
* No `strategy.close` and no `strategy.exit` exists, so `source_reproduce_stops`
  is False and the only exits are the reverse entries. Both directions are
  entered, so `can_short` is True.
* The `/*backtest` header declares `period: 4d` on Futures_Binance BTC_USDT, so
  `timeframe` is "4d"; `basePeriod: 1d` is the FMZ backtester's own fill
  granularity. The verification harness has no local 4d series, so
  `verify_chain` is expected to report `skipped_no_local_data`.
* Leverage, margin, liquidation, funding and contract-step rounding are not
  modelled; the chain verifier measures the rounding separately.
"""
from __future__ import annotations

import pandas as pd
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


class SMCrossingEma209Sedkur_58562e(PinePortBase, IStrategy):
    source_id = "SM_58562ef472b7954d"
    source_file = "EMA交叉系统策略EMA-Crossover-Strategy.md"
    timeframe = "4d"
    can_short = True
    source_defaults: dict = {}
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    source_reproduce_stops = False
    source_mintick = 0.1
    source_fidelity_notes = [
        "The md's prose describes `bullish` as ema9 > ema20 OR a cross -- two "
        "independent triggers ('dual validation ... to avoid missing signals'). "
        "The code ANDs them (`cross(ema9, ema20) and (ema9 > ema20)`), which is a "
        "single condition equal to the crossover; the OR form belongs to the "
        "source's commented-out line `//bullish = (ema9>ema20)?true:false`. Code "
        "followed, disagreement recorded (铁律 2).",
        "`cross(a, b)` is Pine v4's deprecated both-ways alias of `crossover`; "
        "ANDed with the level test it degenerates to one direction each "
        "(crossover for bullish, crossunder for bearish). The two-factor form is "
        "kept as written rather than collapsed; the values are identical.",
        "`when = year > 2016` tests the BAR's year (Pine's `year` builtin), not "
        "the run date; the comparison is strict. The declared 2022-2023 backtest "
        "window satisfies it on every bar, and it is reproduced as written so an "
        "earlier window would behave as the source does.",
        "`ta.ema` is pine_ta.pine_ema, whose seed is the modelled first-non-na "
        "choice (PINE_SEMANTICS.md 3.1): v4 `ema`'s seeding rule is not "
        "published. Both averages share it, so only a cross inside the warm-up "
        "is at risk.",
        "There is no strategy.close / strategy.exit: a position is closed only by "
        "the opposite entry reversing it, so source_reproduce_stops is False and "
        "a position open at the window end stays open. Both directions are "
        "entered, so can_short is True.",
        "`strategy(title=..., overlay=false)` declares nothing else, so "
        "qty_type=fixed, qty_value=1 contract, commission=0%, pyramiding=0 and "
        "initial_capital=1000000 are Pine's documented defaults.",
        "plot() / plotshape() / alertcondition() / overlay are display or alert "
        "only and place no order.",
        "The /*backtest header declares `period: 4d`; `basePeriod: 1d` is the FMZ "
        "backtester's fill granularity, not the strategy's period. No local 4d "
        "series exists in this harness, so verify_chain reports "
        "skipped_no_local_data rather than a verdict.",
        "Leverage, margin, liquidation, funding and contract-step rounding are "
        "not modelled; the chain verifier measures the rounding separately.",
    ]

    def pine_indicators(self, dataframe, params):
        close = dataframe["close"]
        ema20 = ta.pine_ema(close, 20)
        ema9 = ta.pine_ema(close, 9)
        cross = ta.pine_cross(ema9, ema20)
        dataframe["pine_ema20"] = ema20
        dataframe["pine_ema9"] = ema9
        # bullish = cross(ema9, ema20) and (ema9 > ema20) ? true : false
        dataframe["pine_bullish"] = cross & (ema9 > ema20)
        # bearish = cross(ema9, ema20) and (ema20 > ema9) ? true : false
        dataframe["pine_bearish"] = cross & (ema20 > ema9)
        # when = year > 2016 -- the BAR's year, from the candle timestamp.
        index = dataframe.index
        if isinstance(index, pd.DatetimeIndex):
            dataframe["pine_year_ok"] = index.year > 2016
        else:  # pragma: no cover - the base class always supplies a DatetimeIndex
            dataframe["pine_year_ok"] = False
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "bullish": dataframe["pine_bullish"].to_numpy(dtype=bool),
            "bearish": dataframe["pine_bearish"].to_numpy(dtype=bool),
            "year_ok": dataframe["pine_year_ok"].to_numpy(dtype=bool),
        }

    def pine_script(self, broker, i, ctx):
        when = bool(ctx["year_ok"][i])
        # if (bullish)
        #     strategy.entry("buy", strategy.long, comment="al", when = year > 2016)
        if ctx["bullish"][i]:
            broker.entry("buy", "long", when=when)
        # if (bearish)
        #     strategy.entry("sell", strategy.short, comment="sat", when = year > 2016)
        if ctx["bearish"][i]:
            broker.entry("sell", "short", when=when)
