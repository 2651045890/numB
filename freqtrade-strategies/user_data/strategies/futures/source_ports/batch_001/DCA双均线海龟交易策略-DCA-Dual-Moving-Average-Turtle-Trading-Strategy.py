"""Port of sources/SM_1a341203cacb7bab.pine (batch_001/DCA双均线海龟交易策略-DCA-Dual-Moving-Average-Turtle-Trading-Strategy.md).

Pine v5. A 14/28 SMA crossover with an explicit quantity on the long side only:

    sma_fast   = input(14,  "Hızlı SMA Dönemi")
    sma_slow   = input(28,  "Yavaş SMA Dönemi")
    dca_amount = input(100, "DCA Miktarı")
    dca_interval = input(14, "DCA Aralığı (Gün)")

    fast_sma = ta.sma(close, sma_fast)
    slow_sma = ta.sma(close, sma_slow)

    var float dca_average_price = na
    var int   dca_count         = na
    if (bar_index % dca_interval == 0)
        dca_count         := nz(dca_count, 0) + 1
        dca_average_price := nz(dca_average_price, close) * (dca_count - 1) + close
        dca_average_price /= dca_count

    longCondition  = ta.crossover(fast_sma, slow_sma)
    shortCondition = ta.crossunder(fast_sma, slow_sma)

    if (longCondition)
        strategy.entry("Alım", strategy.long, qty=dca_amount)
    if (shortCondition)
        strategy.entry("Satım", strategy.short)

The two orders are asymmetric and the port keeps them that way: the long passes
`qty=dca_amount` (100 contracts, a literal quantity), the short passes no `qty`
and therefore sizes with the script's `default_qty_type` / `default_qty_value`.
`strategy("DCA YSMA HSMA Stratejisi", overlay=true, calc_on_every_tick=true)`
declares neither, so the short is `strategy.fixed` / 1 contract while the long
is 100 -- a 100x difference between the two sides that is in the source, not an
artefact of the port.

`dca_average_price` / `dca_count` are accumulated but read by nothing: no
condition, no order and not even a `plot` uses them. They are still reproduced
bar for bar (they are `var` state, so they carry across bars) so the port's
derived series is the source's, but they cannot influence a fill.

`strategy.entry` places a market order with no stop/limit/trail, and there is no
exit call in the source, so `source_reproduce_stops` is False and a position
open at the end of the window stays open. Both ids exist, so `can_short` is
True even though the short is only ever reached through a crossunder.

The `/*backtest` header declares `period: 10m` on Futures_Binance BTC_USDT;
`basePeriod: 1m` is the FMZ backtester's own fill granularity for those 10m
bars, not the strategy's period.

FIDELITY:

* md-vs-source: the md prose says "when the fast SMA crosses below the slow
  SMA, the strategy sells ALL holdings" (卖出所有持仓). The code calls
  `strategy.entry("Satım", strategy.short)` -- a SHORT entry, which on a netted
  position reverses it and, with no long open, opens a short outright. The code
  is reproduced; the prose is recorded, not reconciled.
* md-vs-source: the md prose describes a DCA leg that "buys an additional fixed
  amount every 14 days to lower the average holding cost". The code only
  accumulates `dca_average_price` / `dca_count`; it never turns them into an
  order, so no DCA leg exists on the platform. Reproduced as the code writes it.
* `calc_on_every_tick=true` is declared by the source. The shared engine
  evaluates the script once per bar close and does not model intrabar
  recalculation (PINE_SEMANTICS.md 2.5, for `varip`); the declaration changes
  nothing here because no order depends on intrabar state, but it is recorded
  rather than silently ignored.
* `bar_index % dca_interval == 0` uses Pine's `bar_index`, which is the
  0-based index of the bar on the chart; the port uses the frame's own bar
  position `i`, which is the same number for a frame that starts at the series
  start. The DCA block is order-irrelevant (see above).
* `nz(dca_count, 0)` and `nz(dca_average_price, close)` are the 2-argument
  forms: the replacement is 0 and `close` respectively, NOT the default 0 for
  both. Reproduced with those two replacements.
* `qty=dca_amount` is 100 CONTRACTS, not 100 units of cash, and the short uses
  the 1-contract default. No `input(type=bool)` exists, so
  PINE_SEMANTICS.md 1.16 does not apply.
* `ta.sma` returns na until its window is full and na inside the window
  propagates (PINE_SEMANTICS.md 3.2); `ta.crossover` / `ta.crossunder` are
  false while either side is na, so nothing fires during the 28-bar warm-up.
* `alertcondition` places no order and is ignored (PINE_SEMANTICS.md 2.7);
  `plot` is display-only.
* Leverage, margin, liquidation, funding and the venue's contract-step
  rounding are not modelled; the chain verifier measures the rounding
  separately.
"""
import numpy as np
import pandas as pd
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


def _dca_state(close: pd.Series, interval: int) -> tuple[pd.Series, pd.Series]:
    """The source's `var` DCA accumulators, replayed bar by bar.

        var float dca_average_price = na
        var int   dca_count         = na
        if (bar_index % dca_interval == 0)
            dca_count         := nz(dca_count, 0) + 1
            dca_average_price := nz(dca_average_price, close) * (dca_count - 1) + close
            dca_average_price /= dca_count

    `var` state persists across bars and is only written on interval bars, so
    the series is carried forward between them. Neither series reaches an
    order; they are reproduced because the source computes them.
    """
    values = close.to_numpy(dtype=float)
    count = np.full(len(values), np.nan)
    average = np.full(len(values), np.nan)
    running_count = np.nan
    running_average = np.nan
    for i in range(len(values)):
        if i % interval == 0:
            running_count = (0.0 if np.isnan(running_count) else running_count) + 1.0
            previous = values[i] if np.isnan(running_average) else running_average
            running_average = previous * (running_count - 1.0) + values[i]
            running_average = running_average / running_count
        count[i] = running_count
        average[i] = running_average
    return (
        pd.Series(count, index=close.index, dtype=float),
        pd.Series(average, index=close.index, dtype=float),
    )


class SMDcaDualMovingAverageTurtle_1a3412(PinePortBase, IStrategy):
    source_id = "SM_1a341203cacb7bab"
    source_file = "DCA双均线海龟交易策略-DCA-Dual-Moving-Average-Turtle-Trading-Strategy.md"
    timeframe = "10m"
    can_short = True
    source_defaults: dict = {
        "sma_fast": 14,
        "sma_slow": 28,
        "dca_amount": 100,
        "dca_interval": 14,
    }
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    source_reproduce_stops = False
    source_fidelity_notes = [
        "The two orders are asymmetric in the source: the long passes "
        "qty=dca_amount (100 contracts), the short passes no qty and sizes with "
        "strategy()'s defaults, which the source never declares -- so "
        "strategy.fixed / 1 contract. Reproduced as written; the 100x gap "
        "between the sides is the source's, not the port's.",
        "md-vs-source: the md prose says a crossunder 'sells all holdings'. The "
        "code calls strategy.entry('Satım', strategy.short), a SHORT entry that "
        "reverses a long or opens a short outright. The code is reproduced; the "
        "prose is recorded, not reconciled.",
        "md-vs-source: the prose describes a DCA leg buying every 14 days. The "
        "code only accumulates dca_average_price / dca_count and never places an "
        "order from them, so no DCA order exists on the platform.",
        "calc_on_every_tick=true is declared by the source; the shared engine "
        "evaluates once per bar close and does not model intrabar "
        "recalculation. Recorded rather than ignored; no order here depends on "
        "intrabar state.",
        "dca_average_price / dca_count are reproduced bar for bar as `var` state "
        "carried across bars, but they are read by nothing -- no condition, no "
        "order, no plot -- so they cannot influence a fill.",
        "nz is used in its 2-argument form with DIFFERENT replacements: "
        "nz(dca_count, 0) and nz(dca_average_price, close), not the default 0 "
        "for both.",
        "bar_index in the modulus is Pine's 0-based chart bar index; the port "
        "uses the frame's bar position, the same number.",
        "strategy() declares only title/overlay/calc_on_every_tick, so "
        "qty_type=fixed, qty_value=1, commission=0, pyramiding=0 and "
        "initial_capital=1000000 are Pine's documented defaults.",
        "No exit call exists, so source_reproduce_stops is False and a position "
        "open at the window end stays open.",
        "No input(type=bool) exists, so PINE_SEMANTICS.md 1.16 does not apply.",
        "ta.sma is na until its window is full and na propagates inside it "
        "(PINE_SEMANTICS.md 3.2); crossover/crossunder are false while either "
        "side is na, so nothing fires during the 28-bar warm-up.",
        "alertcondition places no order (PINE_SEMANTICS.md 2.7); plot is "
        "display-only.",
        "Leverage, margin, liquidation, funding and the venue's contract-step "
        "rounding are not modelled; the chain verifier measures the rounding "
        "separately.",
    ]

    def pine_indicators(self, dataframe, params):
        close = dataframe["close"]
        interval = int(params["dca_interval"])
        fast_sma = ta.pine_sma(close, int(params["sma_fast"]))
        slow_sma = ta.pine_sma(close, int(params["sma_slow"]))
        dca_count, dca_average_price = _dca_state(close, interval)

        dataframe["pine_fast_sma"] = fast_sma
        dataframe["pine_slow_sma"] = slow_sma
        dataframe["pine_dca_count"] = dca_count
        dataframe["pine_dca_average_price"] = dca_average_price
        dataframe["pine_long_condition"] = ta.pine_crossover(fast_sma, slow_sma)
        dataframe["pine_short_condition"] = ta.pine_crossunder(fast_sma, slow_sma)
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "long_condition": dataframe["pine_long_condition"].to_numpy(),
            "short_condition": dataframe["pine_short_condition"].to_numpy(),
            "dca_amount": float(params["dca_amount"]),
        }

    def pine_script(self, broker, i, ctx):
        # if (longCondition)
        #     strategy.entry("Alım", strategy.long, qty=dca_amount)
        if ctx["long_condition"][i]:
            broker.entry("Alım", "long", qty=ctx["dca_amount"])
        # if (shortCondition)
        #     strategy.entry("Satım", strategy.short)
        if ctx["short_condition"][i]:
            broker.entry("Satım", "short")
