"""Port of sources/SM_30bec85b45dc9833.pine (batch_001/DPD-RSI-BB量化策略DPD-RSI-BB-Quantitative-Strategy.md).

Pine v2 (`//@version= 2`, so every `input(...)` uses the v2 signature and
`ema` / `sma` / `stdev` / `rsi` / `crossover` / `crossunder` are bare builtins).
`strategy("DPD+RSI+BB ", overlay=true)` declares only title/overlay, so every
other property is Pine's default: `default_qty_type=strategy.fixed`,
`default_qty_value=1`, commission 0%, `pyramiding=0`,
`process_orders_on_close=false`, `initial_capital=1000000`.

Three indicator blocks plus a calendar gate:

    e1 = ema(close, 50) ; e2 = ema(e1, 50) ; demaprice = 2*e1 - e2
    demadifper = ((close - demaprice) / close) * 100        # "DPD" percentage

    vrsi = rsi(close, 6)

    basisup = basislow = sma(close, 50)
    devup = multup*stdev(close, 50) ; devlow = multlow*stdev(close, 50)
    upperbb = basisup + devup ; lowerbb = basislow - devlow

    if (demadifper < buyper) and crossover(vrsi, overSold) and (close < upperbb)
       and year >= yearfrom and year <= yearuntil
       and month >= monthfrom and month <= monthuntil
       and dayofmonth >= dayfrom and dayofmonth < dayuntil
        strategy.entry("BUY", strategy.long, stop=close, oca_name="TREND")
    else
        strategy.cancel(id="BUY")

    if close > upperbb and vrsi > overBought and demadifper > sellper
       and <the same six calendar terms>
        strategy.entry("SELL", strategy.short, stop=close, oca_name="TREND")
    else
        strategy.cancel(id="SELL")

Both legs are STOP entries whose stop is the SIGNAL BAR's `close` -- an absolute
price, not a tick distance -- so nothing is scaled by `mintick`. The engine
rests them and fills on a later bar whose high (long) / low (short) reaches that
level, filling at `max(stop, open)` / `min(stop, open)`. PINE_SEMANTICS.md
section 2 item 11: that resting entry cannot be projected on Freqtrade's
interface, so the framework's leg of this port enters at the next open of the
placement bar instead.

`lowerbb` / `devlow` / `multlow` are drawn by `plot`/`fill` and never appear in
either condition; they are computed anyway so the source's indicator set stays
complete, and nothing trades on them.

FIDELITY:

* `year`, `month`, `dayofmonth` are the BARE v2/v3 calendar builtins, read off
  the bar's timestamp. Pine resolves them in the EXCHANGE timezone; the local
  Binance/OKX frames are UTC, so UTC is used (PINE_SEMANTICS.md section 3.4).
  `dayofmonth < dayuntil` is a STRICT `<`, exactly as written.
* The six calendar terms are evaluated per bar as a column, not folded into a
  constant: with the source's defaults (year 2018-2039, month 6-12, day
  1..30) the gate is true for essentially all local data, but the port must not
  special-case that.
* `rsi(price, lengthrsi)` is v2's Wilder RSI. `pine_ta.pine_rsi` is that same
  recursion, so it is used rather than re-inlined.
* `ema` / `sma` / `stdev` are the bare v2 builtins, matching
  `pine_ta.pine_ema` / `pine_sma` / `pine_stdev` (population stdev, ddof=0).
  The `ta.ema` seeding choice is PINE_SEMANTICS.md section 3.1: the running
  value starts at the first observation, so `demadifper` is defined from bar 0
  in this model rather than after a warmup.
* SOURCE-vs-md: the md argument table lists `sellper` (`v_input_2`) as `false`
  and `dayfrom` (`v_input_14`) as `true`. The SOURCE declares `sellper =
  input(0, step=0.1)` and `dayfrom = input(1)`; 0 and 1 are what the FMZ table
  renders as false/true. The source's numeric values are used.
* Both entry calls sit in an `if`/`else` whose else branch is
  `strategy.cancel(id=...)`, and the two ids are "BUY" and "SELL"; the order
  and the ids are reproduced verbatim.
* There is no `strategy.exit` / `strategy.close`, so `source_reproduce_stops` is
  False: a position is only closed by the opposite entry reversing it.
* The `/*backtest` header declares `period: 1m` on Futures_Binance BTC_USDT, so
  `timeframe` is "1m". Its `basePeriod: 1m` is the FMZ backtester's own
  granularity for filling those bars, not the strategy's period.
* Leverage, margin, liquidation, funding and contract-step rounding are not
  modelled; the chain verifier measures the rounding separately.
"""
from __future__ import annotations

from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


class SMDpdRsiBb_30bec8(PinePortBase, IStrategy):
    source_id = "SM_30bec85b45dc9833"
    source_file = "DPD-RSI-BB量化策略DPD-RSI-BB-Quantitative-Strategy.md"
    timeframe = "1m"
    can_short = True
    source_defaults: dict = {
        "buyper": -1.0,
        "sellper": 0.0,
        "demalen": 50,
        "lengthrsi": 6,
        "overSold": 20,
        "overBought": 60,
        "lengthbb": 50,
        "multlow": 1.5,
        "multup": 1.5,
        "yearfrom": 2018,
        "yearuntil": 2039,
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
        "Pine v2: every input/ta call is reproduced with its v2 meaning; the "
        "indicators used (ema, sma, stdev, rsi, crossover, crossunder) have no "
        "v2-vs-v5 semantic difference.",
        "Both entry legs are STOP entries with stop = the SIGNAL BAR's close, an "
        "absolute price; nothing is scaled by mintick.",
        "Resting stop entries cannot be projected onto Freqtrade's interface "
        "(PINE_SEMANTICS.md section 2 item 11): the engine fills them on a later "
        "bar that reaches the level, while signal projection can only enter at "
        "the next open of the bar the order was placed on.",
        "year / month / dayofmonth are the bare v2 calendar builtins, modelled "
        "from the bar timestamp in UTC (PINE_SEMANTICS.md section 3.4). "
        "`dayofmonth < dayuntil` keeps its strict `<`.",
        "The six calendar terms are recomputed per bar rather than folded into a "
        "constant, even though the default range makes the gate true for "
        "essentially all local data.",
        "lowerbb / devlow / multlow are plot/fill-only and never appear in a "
        "condition; they are still computed so the source's indicator set is "
        "complete.",
        "SOURCE-vs-md: the md argument table renders sellper (source input(0, "
        "step=0.1)) as `false` and dayfrom (source input(1)) as `true`. The "
        "source's numeric values 0 and 1 are used.",
        "ta.ema's seed is PINE_SEMANTICS.md section 3.1 (first observation, an "
        "unresolved parity risk), so demadifper is defined from bar 0 here.",
        "strategy() declares only title/overlay, so qty is Pine's default "
        "fixed/1, commission 0%, pyramiding 0 and initial_capital 1000000.",
        "No strategy.exit / strategy.close exists, so source_reproduce_stops is "
        "False: a position is only closed by the opposite entry reversing it.",
        "The /*backtest header's basePeriod: 1m matches the period, so no "
        "granularity gap is introduced by the header.",
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

        # vrsi = rsi(price, lengthrsi)
        vrsi = ta.pine_rsi(close, int(params["lengthrsi"]))

        # basisup = basislow = sma(close, lengthbb)
        # devup = multup * stdev(close, lengthbb) ; devlow = multlow * stdev(close, lengthbb)
        lengthbb = int(params["lengthbb"])
        basis = ta.pine_sma(close, lengthbb)
        stdev = ta.pine_stdev(close, lengthbb)
        upperbb = basis + float(params["multup"]) * stdev
        lowerbb = basis - float(params["multlow"]) * stdev

        # year/month/dayofmonth gate, strict `<` on the upper day bound.
        index = dataframe.index
        date_ok = (
            (index.year >= int(params["yearfrom"]))
            & (index.year <= int(params["yearuntil"]))
            & (index.month >= int(params["monthfrom"]))
            & (index.month <= int(params["monthuntil"]))
            & (index.day >= int(params["dayfrom"]))
            & (index.day < int(params["dayuntil"]))
        )

        long_condition = (
            (demadifper < float(params["buyper"]))
            & ta.pine_crossover(vrsi, float(params["overSold"]))
            & (close < upperbb)
            & date_ok
        )
        short_condition = (
            (close > upperbb)
            & (vrsi > float(params["overBought"]))
            & (demadifper > float(params["sellper"]))
            & date_ok
        )

        dataframe["pine_demadifper"] = demadifper
        dataframe["pine_vrsi"] = vrsi
        dataframe["pine_upperbb"] = upperbb
        dataframe["pine_lowerbb"] = lowerbb
        dataframe["pine_long_condition"] = long_condition.fillna(False)
        dataframe["pine_short_condition"] = short_condition.fillna(False)
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "close": dataframe["close"].to_numpy(dtype=float),
            "long_condition": dataframe["pine_long_condition"].to_numpy(dtype=bool),
            "short_condition": dataframe["pine_short_condition"].to_numpy(dtype=bool),
        }

    def pine_script(self, broker, i, ctx):
        # if (demadifper < buyper) and crossover(vrsi, overSold) and (price < upperbb) and <calendar>
        #     strategy.entry("BUY", strategy.long, stop=close, oca_name="TREND")
        # else
        #     strategy.cancel(id="BUY")
        if ctx["long_condition"][i]:
            broker.entry("BUY", "long", stop=float(ctx["close"][i]))
        else:
            broker.cancel("BUY")

        # if price > upperbb and vrsi > overBought and demadifper > sellper and <calendar>
        #     strategy.entry("SELL", strategy.short, stop=close, oca_name="TREND")
        # else
        #     strategy.cancel(id="SELL")
        if ctx["short_condition"][i]:
            broker.entry("SELL", "short", stop=float(ctx["close"][i]))
        else:
            broker.cancel("SELL")
