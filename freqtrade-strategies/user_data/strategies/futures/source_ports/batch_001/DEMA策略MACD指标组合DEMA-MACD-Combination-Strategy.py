"""Port of sources/SM_555efb29e6b2bba6.pine
(batch_001/DEMA策略MACD指标组合DEMA-MACD-Combination-Strategy.md).

Pine v1 (`//@version=1`). A double-EMA level filter against close, with an
optional MACD-histogram gate on the long side:

    DemaLength  = input(21, minval=1)
    MacdControl = input(false, "Control 'MACD Histogram is positive?' when Buy condition")

    e1    = ema(close, DemaLength)
    e2    = ema(e1, DemaLength)
    dema1 = 2 * e1 - e2
    pos   = close > dema1 ? 1 : 0

    [macdLine, signalLine, histLine] = macd(close, 12, 26, 9)
    macdCond = MacdControl ? histLine[0] > 0 ? true : false : true

    strategy.entry("BUY",  strategy.long,  when = window() and pos == 1 and macdCond)
    strategy.entry("SELL", strategy.short, when = window() and pos == 0)

`pos` is a LEVEL, not a crossover: the long entry is live on every bar whose
close is above the DEMA, and the short entry on every bar whose close is at or
below it, so the position is flipped by the first bar that crosses the line. The
source's `window()` is `=> true`, so the From/To date inputs are evaluated into
`start`/`finish` and never used; the port emits as the source does.

There is no exit call, so `source_reproduce_stops` is False and a position is
closed only when the opposite entry reverses it.

`strategy("DEMA Strategy with MACD", overlay=true)` declares no sizing, so the
Pine defaults apply: `fixed` 1 contract, initial capital 1000000, 0% commission,
`pyramiding 0`, `process_orders_on_close=false`.

FIDELITY:

* `MacdControl` defaults to false, which makes `macdCond` a constant true and
  the MACD block inert. It is still computed and applied, so overriding the
  parameter reproduces the gated variant rather than silently ignoring it.
* The source is annotated `//@version=1`, where `macd()` is the built-in that
  returns `[macdLine, signalLine, histLine]` -- `ema(close,12) - ema(close,26)`,
  its `ema(...,9)`, and their difference. `pine_ta.pine_macd` computes exactly
  that; the bar references (`histLine[0]`) are the current bar.
* `ema` seeding is the shared layer's named modelling choice (first observation
  as the seed, na observations not advancing the recursion); PINE_SEMANTICS
  §3.1 records that TradingView does not publish its rule. Not corrected here.
* `window()` is `=> true`: the From/To date inputs are unused. Their defaults
  are still carried in `source_defaults` because they are `input()` statements.
* The two commented-out `strategy.opentrades`-style guards do not exist in this
  source; the only comments are the section banners.
* `barcolor(pos == 0 ? red : pos == 1 ? green : blue)` and `plot(dema1)` are
  display-only and are not reproduced.
* `/*backtest` declares `period: 1d` on Futures_Binance BTC_USDT, so `timeframe`
  is "1d"; `basePeriod: 1h` is the FMZ backtester's own fill granularity.
* Leverage, margin, liquidation and funding are not modelled, and neither is the
  venue's contract-step rounding of order quantities.
"""
import numpy as np
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


class SMDemaMacdCombination_555efb(PinePortBase, IStrategy):
    source_id = "SM_555efb29e6b2bba6"
    source_file = "DEMA策略MACD指标组合DEMA-MACD-Combination-Strategy.md"
    timeframe = "1d"
    can_short = True
    source_defaults: dict = {
        "DemaLength": 21,
        "MacdControl": False,
        "FromMonth": 1,
        "FromDay": 1,
        "FromYear": 2020,
        "ToMonth": 1,
        "ToDay": 1,
        "ToYear": 9999,
    }
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    source_reproduce_stops = False
    source_fidelity_notes = [
        "`pos` is a level condition, not a crossover: the long (short) entry is "
        "live on every bar with close above (at or below) the DEMA.",
        "`window()` is `=> true`: the From/To date inputs are unused; entries "
        "fire unconditionally, as in the source.",
        "MacdControl defaults to false, making macdCond a constant true; the "
        "MACD block is still computed so a parameter override behaves.",
        "The source is //@version=1: `macd()` is the built-in returning "
        "[macdLine, signalLine, histLine], which pine_ta.pine_macd reproduces.",
        "ema seeding is the shared layer's modelling choice (PINE_SEMANTICS "
        "3.1: TradingView does not publish its rule). Not corrected here.",
        "No exit call exists: the position is closed only by the opposite "
        "entry reversing it, so source_reproduce_stops is False.",
        "barcolor/plot are display-only and are not reproduced.",
        "Initial capital is unset in the source, hence Pine's default 1000000.",
    ]

    def pine_indicators(self, dataframe, params):
        dema_length = int(params["DemaLength"])
        close = dataframe["close"]

        # e1 = ema(close, DemaLength); e2 = ema(e1, DemaLength)
        e1 = ta.pine_ema(close, dema_length)
        e2 = ta.pine_ema(e1, dema_length)
        dema1 = 2.0 * e1 - e2
        # pos = close > dema1 ? 1 : 0
        pos = (close > dema1).to_numpy(dtype=float)

        # [macdLine, signalLine, histLine] = macd(close, 12, 26, 9)
        macd = ta.pine_macd(close, 12, 26, 9)
        hist = macd["hist"]
        # macdCond = MacdControl ? histLine[0] > 0 ? true : false : true
        if bool(params["MacdControl"]):
            macd_condition = (hist > 0).to_numpy()
        else:
            macd_condition = np.ones(len(dataframe), dtype=bool)

        is_positive = pos == 1.0
        is_zero = pos == 0.0
        dataframe["pine_dema"] = dema1
        dataframe["pine_macd_hist"] = hist
        dataframe["pine_long_condition"] = is_positive & macd_condition
        dataframe["pine_short_condition"] = is_zero
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "long_condition": dataframe["pine_long_condition"].to_numpy(),
            "short_condition": dataframe["pine_short_condition"].to_numpy(),
        }

    def pine_script(self, broker, i, ctx):
        # strategy.entry("BUY", strategy.long, when = window() and pos == 1 and macdCond)
        if ctx["long_condition"][i]:
            broker.entry("BUY", "long")
        # strategy.entry("SELL", strategy.short, when = window() and pos == 0)
        if ctx["short_condition"][i]:
            broker.entry("SELL", "short")
