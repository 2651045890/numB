"""Port of sources/SM_336d270d68c41d55.pine (batch_001/DEMA波动率指标策略DEMA-Volatility-Index-Strategy.md).

Pine v2 (`//@version= 2`). `strategy("DEMA of DPD Strategy ", shorttitle="DPD%
DEMA ", overlay=false)` declares only title/shorttitle/overlay, so every other
property is Pine's default: `default_qty_type=strategy.fixed`,
`default_qty_value=1`, commission 0%, `pyramiding=0`,
`process_orders_on_close=false`, `initial_capital=1000000`.

The signal is a DEMA-of-DPD oscillator crossed against two fixed thresholds:

    e1 = ema(close, demalen) ; e2 = ema(e1, demalen) ; demaprice = 2*e1 - e2
    demadifper = ((close - demaprice) / close) * 100
    demaofdpd  = ema(demadifper, demalen2)
    demaofdpd2 = ema(demaofdpd, demalen2)
    resultstrategy = 2*demaofdpd - demaofdpd2

    if crossover(resultstrategy, buyper)        # buyper = -2
        strategy.entry("BUY", strategy.long, stop=close, oca_name="TREND")
    else
        strategy.cancel(id="BUY")

    if crossunder(resultstrategy, sellper)      # sellper = 2
        strategy.entry("SELL", strategy.short, stop=close, oca_name="TREND")
    else
        strategy.cancel(id="SELL")

Both legs are STOP entries whose stop is the SIGNAL BAR's `close` -- an absolute
price, not a tick distance -- so nothing is scaled by `mintick`. The engine
rests them and fills on a later bar that reaches the level. PINE_SEMANTICS.md
section 2 item 11: a resting entry cannot be projected onto Freqtrade's
interface, so the framework's leg of this port enters at the next open of the
placement bar instead.

FIDELITY:

* The source's six calendar inputs (`yearfrom` 2018, `yearuntil` 2019,
  `monthfrom` 6, `monthuntil` 12, `dayfrom` 1, `dayuntil` 31) are DECLARED BUT
  NEVER USED: neither entry condition references `year`, `month` or
  `dayofmonth`. They are carried in `source_defaults` so the parameter surface
  stays visible, and no calendar gate is applied to either condition. (Had the
  source used them, its default window 2018-06-01..2019-12-30 would have
  silenced the whole local data range.)
* `OverDemaPer` (1) and `UnderDemaPer` (-1) exist only as the two `hline`s and
  the `fill` between them; they are band styling, are not part of
  `resultstrategy`, and no condition reads them.
* Both entry calls sit in an `if`/`else` whose else branch is
  `strategy.cancel(id=...)`; the ids "BUY" and "SELL" and the call order are
  reproduced verbatim.
* `ema`, `crossover`, `crossunder` are the bare v2 builtins, matching
  `pine_ta.pine_ema` / `pine_crossover` / `pine_crossunder`. The `ta.ema`
  seeding choice is PINE_SEMANTICS.md section 3.1 -- seeded from the first
  observation, so `resultstrategy` is defined from bar 0 in this model and
  there is no warmup window.
* `buyper` / `sellper` are CONSTANTS (-2 and 2), not series: the cross is
  against a fixed level each bar, which `pine_crossover` / `pine_crossunder`
  handle as a scalar right-hand side.
* SOURCE-vs-md: the md argument table renders `OverDemaPer` (source
  `input(1, ...)`) as `true` and `dayfrom` (source `input(1)`) as `true`; both
  are the FMZ table's rendering of the numeric default 1. The source's numeric
  values are used.
* There is no `strategy.exit` / `strategy.close`, so `source_reproduce_stops` is
  False: a position is only closed by the opposite entry reversing it.
* The `/*backtest` header declares `period: 1d` on Futures_Binance BTC_USDT, so
  `timeframe` is "1d". Its `basePeriod: 1h` is the FMZ backtester's own
  granularity for filling those daily bars, not the strategy's period.
* Leverage, margin, liquidation, funding and contract-step rounding are not
  modelled; the chain verifier measures the rounding separately.
"""
from __future__ import annotations

from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


class SMDemaVolatilityIndex_336d27(PinePortBase, IStrategy):
    source_id = "SM_336d270d68c41d55"
    source_file = "DEMA波动率指标策略DEMA-Volatility-Index-Strategy.md"
    timeframe = "1d"
    can_short = True
    source_defaults: dict = {
        "buyper": -2,
        "sellper": 2,
        "demalen": 50,
        "OverDemaPer": 1,
        "UnderDemaPer": -1,
        "demalen2": 21,
        "yearfrom": 2018,
        "yearuntil": 2019,
        "monthfrom": 6,
        "monthuntil": 12,
        "dayfrom": 1,
        "dayuntil": 31,
    }
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    source_reproduce_stops = False
    source_fidelity_notes = [
        "The source's six calendar inputs (yearfrom 2018, yearuntil 2019, "
        "monthfrom 6, monthuntil 12, dayfrom 1, dayuntil 31) are DECLARED BUT "
        "NEVER USED: neither entry condition references year, month or "
        "dayofmonth. They are carried in source_defaults for visibility and no "
        "calendar gate is applied. Had they been applied, their default window "
        "would have silenced the whole local data range.",
        "OverDemaPer (1) / UnderDemaPer (-1) exist only as the two hlines and "
        "the fill between them; they are band styling and no condition reads "
        "them.",
        "Both entry legs are STOP entries with stop = the SIGNAL BAR's close, an "
        "absolute price; nothing is scaled by mintick.",
        "Resting stop entries cannot be projected onto Freqtrade's interface "
        "(PINE_SEMANTICS.md section 2 item 11): the engine fills them on a later "
        "bar that reaches the level, while signal projection can only enter at "
        "the next open of the bar the order was placed on.",
        "buyper / sellper are constants (-2 / 2), not series; the crosses are "
        "against a fixed level each bar.",
        "ta.ema's seed is PINE_SEMANTICS.md section 3.1 (first observation, an "
        "unresolved parity risk), so resultstrategy is defined from bar 0 here "
        "rather than after a warmup.",
        "SOURCE-vs-md: the md argument table renders OverDemaPer (source "
        "input(1)) as `true` and dayfrom (source input(1)) as `true`. The "
        "source's numeric value 1 is used.",
        "strategy() declares only title/shorttitle/overlay, so qty is Pine's "
        "default fixed/1, commission 0%, pyramiding 0 and initial_capital "
        "1000000.",
        "No strategy.exit / strategy.close exists, so source_reproduce_stops is "
        "False: a position is only closed by the opposite entry reversing it.",
        "The /*backtest header's basePeriod: 1h is the FMZ backtester's own "
        "granularity for filling the 1d bars, not the strategy's period.",
        "Leverage, margin, liquidation, funding and contract-step rounding are "
        "not modelled; the chain verifier measures the rounding separately.",
    ]

    def pine_indicators(self, dataframe, params):
        close = dataframe["close"]

        # e1 = ema(close, demalen) ; e2 = ema(e1, demalen) ; demaprice = 2*e1 - e2
        demalen = int(params["demalen"])
        e1 = ta.pine_ema(close, demalen)
        e2 = ta.pine_ema(e1, demalen)
        demaprice = 2.0 * e1 - e2
        # demadifper = ((price - demaprice) / price) * 100
        demadifper = ((close - demaprice) / close) * 100.0

        # demaofdpd = ema(demadifper, demalen2) ; demaofdpd2 = ema(demaofdpd, demalen2)
        # resultstrategy = 2*demaofdpd - demaofdpd2
        demalen2 = int(params["demalen2"])
        demaofdpd = ta.pine_ema(demadifper, demalen2)
        demaofdpd2 = ta.pine_ema(demaofdpd, demalen2)
        resultstrategy = 2.0 * demaofdpd - demaofdpd2

        dataframe["pine_demadifper"] = demadifper
        dataframe["pine_resultstrategy"] = resultstrategy
        # if crossover(resultstrategy, buyper)  -> the LONG arm
        dataframe["pine_long_condition"] = ta.pine_crossover(
            resultstrategy, float(params["buyper"])
        )
        # if crossunder(resultstrategy, sellper) -> the SHORT arm
        dataframe["pine_short_condition"] = ta.pine_crossunder(
            resultstrategy, float(params["sellper"])
        )
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "close": dataframe["close"].to_numpy(dtype=float),
            "long_condition": dataframe["pine_long_condition"].to_numpy(dtype=bool),
            "short_condition": dataframe["pine_short_condition"].to_numpy(dtype=bool),
        }

    def pine_script(self, broker, i, ctx):
        # if (crossover(resultstrategy, buyper))
        #     strategy.entry("BUY", strategy.long, stop=close, oca_name="TREND")
        # else
        #     strategy.cancel(id="BUY")
        if ctx["long_condition"][i]:
            broker.entry("BUY", "long", stop=float(ctx["close"][i]))
        else:
            broker.cancel("BUY")

        # if (crossunder(resultstrategy, sellper))
        #     strategy.entry("SELL", strategy.short, stop=close, oca_name="TREND")
        # else
        #     strategy.cancel(id="SELL")
        if ctx["short_condition"][i]:
            broker.entry("SELL", "short", stop=float(ctx["close"][i]))
        else:
            broker.cancel("SELL")
