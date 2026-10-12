"""Port of sources/SM_a1ff735f33295732.pine (batch_001/DEMA趋势追踪策略The-DEMA-Trend-Following-Strategy.md).

Pine v2. The percentage difference between the close and its DEMA, taken
against two fixed strength levels; both entries are resting STOP orders at the
signal bar's close and are cancelled again on any bar their cross did not occur:

    buyper   = input(-1)
    sellper  = input(1)
    demalen  = input(50, title="Dema Length")

    e1 = ema(close, demalen)
    e2 = ema(e1, demalen)
    demaprice  = 2 * e1 - e2
    demadifper = ((close - demaprice) / close) * 100

    if (crossover(demadifper, buyper))
        strategy.entry("BUY",  strategy.long,  stop=close, oca_name="TREND")
    else
        strategy.cancel(id="BUY")

    if (crossunder(demadifper, sellper))
        strategy.entry("SELL", strategy.short, stop=close, oca_name="TREND")
    else
        strategy.cancel(id="SELL")

`OverDemaPer`, `UnderDemaPer`, `yearfrom`, `yearuntil`, `monthfrom`,
`monthuntil`, `dayfrom` and `dayuntil` are declared as inputs and are used ONLY
by the `hline` / `fill` plotting block -- no `if`, no date arithmetic, nothing.
They are carried in `source_defaults` because they are inputs, and they reach no
decision.

`strategy()` declares only `title`, `shorttitle` and `overlay`, so Pine's
documented defaults apply: `default_qty_type = strategy.fixed`,
`default_qty_value = 1`, `commission_value = 0`, `pyramiding = 0`, initial
capital 1000000 and `process_orders_on_close = false`. The `/*backtest` header
declares `period: 30m` on Futures_Binance BTC_USDT, so `timeframe` is "30m"; its
`basePeriod: 15m` is the FMZ backtester's own granularity for filling those
bars, not the strategy's period.

FIDELITY:

* The md's principle section claims a date-range filter ("策略还设置了年月日范围
  作为过滤条件,只有在指定的日期内才会产生交易信号"). The source NEVER reads those
  variables -- the only statements they appear in are the `input()` calls
  themselves -- so there is no date filtering anywhere in the trading logic.
  The source wins; recorded, not corrected (also PINE_SEMANTICS §二-8, which
  notes `input.time` window limiting is not modelled).
* The md's argument table renders `sellper`, `OverDemaPer` and `dayfrom` with a
  default of "true". Their `input()` calls are `input(1)` / `input(1)` /
  `input(1)`: the values are the number 1, and "true" is the md generator's
  rendering of it. The port carries 1, from the source.
* `demaprice = 2 * e1 - e2` is written out as the source writes it; it is not
  replaced by a library DEMA (whose normalisation often differs by a factor,
  and which would change `demadifper`).
* `ema` is Pine's builtin. Pine does not publish its seeding rule; `pine_ta`
  seeds with the first observation and does not advance the recursion on na
  (PINE_SEMANTICS §3.1). `e2 = ema(e1, demalen)` is an EMA OF AN EMA, so the
  two are chained in that order, not collapsed into one smoother.
* `crossover` / `crossunder` are Pine's event forms and are false whenever
  either operand is na.
* `stop=close` is a resting STOP entry priced at the SIGNAL bar's close, which
  a Freqtrade strategy cannot place (PINE_SEMANTICS §二-11): `run_pine` projects
  it as a next-open market entry on the bar it was PLACED, while the engine
  fills it inside a later bar when the price first reaches the level, and drops
  it unfilled when the `else` branch cancels it on the next bar. The engine
  ledger is the faithful reproduction; the framework side is a projection with
  that known limit. Framework boundary, not a port defect.
* `oca_name="TREND"` groups the two entries in the source. It is passed through
  to `broker.entry`, but the engine stores `oca_group` and never acts on it, so
  an OCA cancellation between the BUY and SELL entries is NOT modelled. The two
  are opposite-direction stop entries at the same price, and each is cancelled
  by its own `else` branch on the next bar, so the resting set is normally one
  order either way; recorded rather than assumed equivalent.
* `strategy.cancel(id=...)` runs on every bar its cross did not occur, so each
  stop order normally rests one bar. `broker.cancel` reproduces it and never
  touches the position.
* `plot(demadifper)`, `hline`, `fill`, `zeroline` are display-only and are not
  reproduced.
* There is no exit call in the source: a position is closed only by the opposite
  entry reversing it, so `source_reproduce_stops` is False and a position open
  at the end of the window stays open.
* Contract-step rounding, leverage, margin, liquidation and funding are not
  modelled (PINE_SEMANTICS §1.6, §二-4).
"""
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


class SMDemaTrendFollowing_a1ff73(PinePortBase, IStrategy):
    source_id = "SM_a1ff735f33295732"
    source_file = "DEMA趋势追踪策略The-DEMA-Trend-Following-Strategy.md"
    timeframe = "30m"
    can_short = True
    source_defaults: dict = {
        "buyper": -1,
        "sellper": 1,
        "demalen": 50,
        "OverDemaPer": 1,
        "UnderDemaPer": -1,
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
        "The md claims a year/month/day filter gates the signals; the source "
        "declares yearfrom/yearuntil/monthfrom/monthuntil/dayfrom/dayuntil but "
        "never reads them outside their input() calls, so no date filtering "
        "occurs. The source wins; recorded, not corrected (PINE_SEMANTICS "
        "§二-8).",
        "The md's argument table shows sellper, OverDemaPer and dayfrom with a "
        "default of 'true'; the source says input(1) for all three. 1 is the "
        "value; 'true' is the md generator's rendering.",
        "demaprice = 2 * e1 - e2 is transcribed as written rather than replaced "
        "by a library DEMA, whose normalisation factor often differs and would "
        "change demadifper.",
        "e2 is an EMA OF an EMA (ema(e1, demalen)), chained in that order, not "
        "collapsed into one smoother. Pine does not publish its EMA seeding "
        "rule; pine_ta seeds on the first observation (PINE_SEMANTICS §3.1).",
        "crossover / crossunder are Pine's event forms, false while either "
        "operand is na.",
        "The entries are resting STOP orders at the signal bar's close "
        "(PINE_SEMANTICS §二-11): run_pine projects them as next-open market "
        "entries on the placement bar, while the engine fills them in a later "
        "bar that first reaches the level and drops them when the else branch "
        "cancels them. Framework boundary, not a port defect.",
        "oca_name='TREND' is passed through to broker.entry, but the engine "
        "stores oca_group and never acts on it, so OCA cancellation between the "
        "BUY and SELL entries is not modelled. Each is cancelled by its own "
        "else branch on the next bar; recorded, not assumed equivalent.",
        "strategy.cancel(id=...) runs on every bar the matching cross did not "
        "occur, so each stop order normally rests one bar; broker.cancel "
        "reproduces it and never touches the position.",
        "OverDemaPer / UnderDemaPer / yearfrom / yearuntil / monthfrom / "
        "monthuntil / dayfrom / dayuntil are inputs used only by the hline/fill "
        "plotting block; they reach no decision. plot/hline/fill/zeroline are "
        "display-only and are not reproduced.",
        "No exit call exists: a position is closed only by the opposite entry "
        "reversing it, so source_reproduce_stops is False and a position open "
        "at the window end stays open.",
        "strategy() declares only title/shorttitle/overlay, so Pine's defaults "
        "apply: qty_type fixed, qty_value 1, commission 0, pyramiding 0, "
        "initial capital 1000000, process_orders_on_close false.",
        "Contract-step rounding, leverage, margin, liquidation and funding are "
        "not modelled (PINE_SEMANTICS §1.6, §二-4).",
    ]

    def pine_indicators(self, dataframe, params):
        close = dataframe["close"]
        demalen = int(params["demalen"])

        e1 = ta.pine_ema(close, demalen)
        e2 = ta.pine_ema(e1, demalen)
        demaprice = 2.0 * e1 - e2
        demadifper = ((close - demaprice) / close) * 100.0

        dataframe["pine_demaprice"] = demaprice
        dataframe["pine_demadifper"] = demadifper
        dataframe["pine_long_condition"] = ta.pine_crossover(
            demadifper, float(params["buyper"])
        )
        dataframe["pine_short_condition"] = ta.pine_crossunder(
            demadifper, float(params["sellper"])
        )
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "close": dataframe["close"].to_numpy(dtype=float),
            "demadifper": dataframe["pine_demadifper"].to_numpy(dtype=float),
            "long_condition": dataframe["pine_long_condition"].to_numpy(dtype=bool),
            "short_condition": dataframe["pine_short_condition"].to_numpy(dtype=bool),
        }

    def pine_script(self, broker, i, ctx):
        # if (crossover(demadifper, buyper))
        #     strategy.entry("BUY", strategy.long, stop=close, oca_name="TREND")
        if ctx["long_condition"][i]:
            broker.entry("BUY", "long", stop=float(ctx["close"][i]), oca_name="TREND")
        else:
            # strategy.cancel(id="BUY")
            broker.cancel("BUY")

        # if (crossunder(demadifper, sellper))
        #     strategy.entry("SELL", strategy.short, stop=close, oca_name="TREND")
        if ctx["short_condition"][i]:
            broker.entry("SELL", "short", stop=float(ctx["close"][i]), oca_name="TREND")
        else:
            # strategy.cancel(id="SELL")
            broker.cancel("SELL")
