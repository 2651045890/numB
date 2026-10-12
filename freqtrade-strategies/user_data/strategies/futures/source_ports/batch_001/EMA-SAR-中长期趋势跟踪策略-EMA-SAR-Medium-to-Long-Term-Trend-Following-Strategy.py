"""Port of sources/SM_3f97fff9ea6a1671.pine (batch_001/EMA-SAR-中长期趋势跟踪策略-EMA-SAR-Medium-to-Long-Term-Trend-Following-Strategy.md).

Pine v5. A 20/60 EMA crossover, gated by two SAR conditions, entered with a
resting STOP order at the previous bar's extreme:

    ema_20 = ta.ema(close, 20)
    ema_60 = ta.ema(close, 60)
    sar    = ta.sar(0.02, 0.2, 0.2)
    is_trend_up = sar[1] > sar[2] ? true : false

    buy_condition  = ta.crossover(ema_20, ema_60)  and (sar < ema_20) and is_trend_up
    sell_condition = ta.crossunder(ema_20, ema_60) and (sar > ema_20) and not is_trend_up

    entry_time = time + 180000
    strategy.entry("Buy",  strategy.long,  when=buy_condition,
                   comment="Buy Signal",  stop=high[1])
    strategy.entry("Sell", strategy.short, when=sell_condition,
                   comment="Sell Signal", stop=low[1], when=entry_time)

`strategy()` declares only `title` and `overlay`, so every property is Pine's
documented default: `strategy.fixed` / 1 contract, initial capital 1000000,
commission 0%, pyramiding 0, `process_orders_on_close=false`. Neither entry
passes `qty`, so the default quantity supplies it.

THE "Sell" CALL IS SYNTACTICALLY INVALID IN THE SOURCE: `when=` appears twice on
line 32 (`when=sell_condition` and `when=entry_time`). Pine v5 rejects duplicate
named arguments -- the script cannot compile as written -- so no single literal
translation exists and one of the two must be chosen. The port keeps
`when=sell_condition`, because that is the reading consistent with both the
md's Strategy Principle (which describes the three-part sell_condition as the
short trigger) and the strategy's long/short symmetry; the discarded reading,
`when=entry_time` with `entry_time = time + 180000`, is a numeric timestamp and
therefore always truthy, which would leave one resting short-stop below the
market on EVERY bar and make `sell_condition` dead code. Both readings are
recorded; see `source_fidelity_notes` and the report's blockers. This is a
judgement forced by the source, not a "fix".

BOTH ENTRIES ARE RESTING STOP ORDERS (`stop=high[1]` / `stop=low[1]`). Pine
places them at bar t's close, so they rest from bar t+1 and fill when a bar's
high/low reaches the level -- possibly many bars later, or never. Freqtrade's
strategy interface has no resting-entry expression, so the projected signal is a
next-open market order. This is the framework boundary recorded in
PINE_SEMANTICS.md section 二.11 (and the reason this source is tier 2, not tier
1): a `mismatch` verdict is the expected result rather than a port defect.

FIDELITY:

* `pine_ta` has no `sar`, so the port carries Wilder's recursion locally
  (`_pine_sar`). Pine does not publish `ta.sar`'s seeding rule; the port models
  the standard one (trend starts up, SAR = low[0], EP = high[0], AF = start),
  which can only differ during warm-up. The source first reads `sar` at bar 1
  (`sar[1] > sar[2]`), i.e. inside that warm-up window, and the EMAs' own 60-bar
  warm-up keeps both conditions false well past it.
* `ta.sar(0.02, 0.2, 0.2)` is start=0.02, inc=0.2, max=0.2 -- the ACCELERATION
  INCREMENT is 0.2, not Pine's 0.02 default, so the factor jumps to the cap
  after the first new extreme. Passed through verbatim.
* `is_trend_up` compares SAR to SAR two bars back (`sar[1] > sar[2]`), not SAR
  against price, and it is used as a plain boolean AND term.
* `ta.ema`'s seed is not published by Pine; `pine_ta.pine_ema` seeds with the
  first non-na value and does not advance on na (PINE_SEMANTICS.md 3.1). That is
  the shared layer's modelled choice, inherited here.
* `ta.crossover` / `ta.crossunder` use `pine_ta`'s modelled definition (`a > b`
  and `a[1] <= b[1]`), and na comparisons evaluate false, matching Pine's `if`.
* `entry_time` is computed by the source and, under the reading this port
  adopts, never used -- dead code. It is documented rather than materialised as
  a column; see the blocker.
* `plot`/`plotshape`/`alertcondition` are display-only and place no condition.
* There is no `strategy.close` / `strategy.exit`, so `source_reproduce_stops` is
  False; the only exits are the reverse entries. Both directions are entered, so
  `can_short` is True.
* Leverage, margin, liquidation, funding and contract-step rounding are not
  modelled; the chain verifier measures the rounding separately.
"""
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
    source does not take a signal there.
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


class SMEmaSar_3f97ff(PinePortBase, IStrategy):
    source_id = "SM_3f97fff9ea6a1671"
    source_file = "EMA-SAR-中长期趋势跟踪策略-EMA-SAR-Medium-to-Long-Term-Trend-Following-Strategy.md"
    timeframe = "1h"
    can_short = True
    source_defaults: dict = {}
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    source_reproduce_stops = False
    source_fidelity_notes = [
        "BLOCKER / forced choice: the source's second strategy.entry passes "
        "`when=` TWICE (`when=sell_condition` and `when=entry_time`). Pine v5 "
        "rejects duplicate named arguments, so the script as written cannot "
        "compile and no literal translation exists. This port keeps "
        "`when=sell_condition`; the alternative (`when=entry_time`, where "
        "entry_time = time + 180000 is a numeric timestamp and therefore always "
        "truthy) is recorded but not implemented. Under the alternative, "
        "sell_condition would be dead code and a short stop would rest below the "
        "market on every bar. See the report's blockers.",
        "Both entries are resting STOP orders (stop=high[1] / stop=low[1]). "
        "Freqtrade has no resting-entry expression, so the projected signal is a "
        "next-open market order and the engine fills inside a later bar at the "
        "stop level (or never). PINE_SEMANTICS.md section 二.11; this is why the "
        "source is tier 2 and a mismatch is the expected verdict.",
        "pine_ta has no `sar`, so the port carries Wilder's recursion locally "
        "(_pine_sar). Pine does not publish ta.sar's seeding rule; the initial "
        "state (up trend, SAR=low[0], EP=high[0], AF=start) is this port's model "
        "and can only differ during warm-up, which the source does not trade.",
        "ta.sar(0.02, 0.2, 0.2) is start=0.02, inc=0.2, max=0.2: the increment is "
        "0.2, NOT Pine's 0.02 default, so AF jumps to the 0.2 cap after the "
        "first new extreme. Passed through verbatim.",
        "is_trend_up is `sar[1] > sar[2]` -- SAR against its own value two bars "
        "back, not SAR against price -- and is used as a plain AND term.",
        "pine_ta.pine_ema seeds with the first non-na value and does not advance "
        "on na; Pine does not publish its own EMA seeding rule "
        "(PINE_SEMANTICS.md 3.1). Shared-layer modelling choice, inherited.",
        "ta.crossover / ta.crossunder use pine_ta's modelled definition and "
        "evaluate na comparisons as false, matching Pine's `if`.",
        "`entry_time = time + 180000` is computed by the source and unused under "
        "the adopted reading -- dead code, documented rather than deleted.",
        "plot / plotshape / alertcondition are display-only and place no "
        "condition.",
        "No strategy.close / strategy.exit exists, so source_reproduce_stops is "
        "False; both directions are entered, so can_short is True.",
        "Leverage, margin, liquidation, funding and contract-step rounding are "
        "not modelled; the venue's rounding can differ from the engine's float "
        "quantity, which the chain verifier measures separately.",
    ]

    def pine_indicators(self, dataframe, params):
        close = dataframe["close"]
        ema_20 = ta.pine_ema(close, 20)
        ema_60 = ta.pine_ema(close, 60)
        # ta.sar(0.02, 0.2, 0.2): start / increment / maximum.
        sar = pd.Series(
            _pine_sar(dataframe["high"], dataframe["low"], 0.02, 0.2, 0.2),
            index=dataframe.index,
        )
        sar_previous = sar.shift(1)
        sar_previous_two = sar.shift(2)
        is_trend_up = (sar_previous > sar_previous_two).fillna(False).astype(bool)

        buy_condition = (
            ta.pine_crossover(ema_20, ema_60).astype(bool)
            & (sar < ema_20).fillna(False)
            & is_trend_up
        )
        sell_condition = (
            ta.pine_crossunder(ema_20, ema_60).astype(bool)
            & (sar > ema_20).fillna(False)
            & (~is_trend_up)
        )

        dataframe["pine_ema_20"] = ema_20
        dataframe["pine_ema_60"] = ema_60
        dataframe["pine_sar"] = sar
        dataframe["pine_is_trend_up"] = is_trend_up
        dataframe["pine_buy_condition"] = buy_condition
        dataframe["pine_sell_condition"] = sell_condition
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "buy_condition": dataframe["pine_buy_condition"].to_numpy(dtype=bool),
            "sell_condition": dataframe["pine_sell_condition"].to_numpy(dtype=bool),
            "high_previous": dataframe["high"].shift(1).to_numpy(dtype=float),
            "low_previous": dataframe["low"].shift(1).to_numpy(dtype=float),
        }

    def pine_script(self, broker, i, ctx):
        # strategy.entry("Buy", strategy.long, when=buy_condition,
        #                comment="Buy Signal", stop=high[1])
        if ctx["buy_condition"][i]:
            broker.entry("Buy", "long", stop=float(ctx["high_previous"][i]))
        # strategy.entry("Sell", strategy.short, when=sell_condition,
        #                comment="Sell Signal", stop=low[1], when=entry_time)
        if ctx["sell_condition"][i]:
            broker.entry("Sell", "short", stop=float(ctx["low_previous"][i]))
