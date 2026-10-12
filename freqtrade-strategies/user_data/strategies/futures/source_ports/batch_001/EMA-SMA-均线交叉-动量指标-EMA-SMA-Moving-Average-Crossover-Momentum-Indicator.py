"""Port of sources/SM_5cd85a117800a5b3.pine
(batch_001/EMA-SMA-均线交叉-动量指标-EMA-SMA-Moving-Average-Crossover-Momentum-Indicator.md).

Pine v5. A 9-period EMA of close against a 30-period SMA for the entry, and
against either the 30- or the 50-period SMA for the exit:

    emaValue   = ta.ema(close, 9)
    sma30Value = ta.sma(close, 30)
    sma50Value = ta.sma(close, 50)
    sma200Value = ta.sma(close, 200)
    sma325Value = ta.sma(close, 325)

    buySignal  = ta.crossover(emaValue, sma30Value)
    sellSignal = ta.crossunder(emaValue, sma30Value) or ta.crossunder(emaValue, sma50Value)

    if (buySignal)
        strategy.entry("Buy", strategy.long)
    if (sellSignal)
        strategy.close("Buy")

`strategy()` declares only `title` and `overlay`, so every property is Pine's
documented default: `strategy.fixed` / 1 contract, initial capital 1000000,
commission 0%, pyramiding 0, `process_orders_on_close=false`. The `/*backtest`
header declares `period: 1d` on Futures_Binance BTC_USDT, so `timeframe` is
"1d"; its `basePeriod: 1h` is the FMZ backtester's own granularity for filling
those daily bars, not the strategy's period.

`sma200Value` and `sma325Value` are plotted but never read by either signal, so
they cannot affect an order; they are computed here anyway because the source
computes them, and they are marked display-only below. The md's prose calls the
MAs "long-term ... to determine major market trends", which is a description of
the plots, not of a filter in the code -- the code applies no 200/325
condition, and none is added here.

The source has no short entry -- only `strategy.entry(..., strategy.long)` and
`strategy.close("Buy")` -- so `can_short` is False, and there is no stop, limit,
trail or cancel call, so `source_reproduce_stops` is False and a position open
at the end of the window stays open.

FIDELITY:

* The md's prose and its embedded Pine block agree with the source file; there
  is no md-vs-source disagreement to record.
* The md's English prose says the entry is "A buy signal is triggered when the
  9-period EMA crosses above the 30-period SMA, while a sell signal is
  triggered when the 9-period EMA crosses below either the 30-period SMA or the
  50-period SMA". That matches the code exactly, including the asymmetry that
  the 50-period SMA participates only on the exit side. No divergence to
  reconcile.
* `sellSignal` is an `or` of two `ta.crossunder` calls; it is not a crossunder
  of the EMA against the LOWER of the two SMAs, and it is not evaluated
  sequentially as two separate `strategy.close` calls -- one bar can carry two
  distinct cross-unders and still yields a single close.
* `sma200Value` / `sma325Value` are read by `plot` calls only, never by a
  signal; they are computed because the source computes them and are dead with
  respect to the orders.
* The `plot`, `plotshape` and `alertcondition` calls are display-only and place
  no condition.
* PINE_SEMANTICS 3.1 (modelled choice): `ta.ema` is seeded with the first non-na
  observation and an na observation does not advance the recursion.
  TradingView does not publish its seeding rule.
* PINE_SEMANTICS 3.2 (modelled choice): `ta.sma` returns na until its window is
  full and na inside the window propagates, so `sma30Value` and `sma50Value`
  are na for the first 29 / 49 bars and every comparison against them is false
  there.
* PINE_SEMANTICS 1.6 / 5.1: the venue's contract-step rounding and non-zero
  taker fees are not modelled. The source declares 0% commission, which is the
  cost basis the port carries.
* PINE_SEMANTICS 二.2 (not modelled): the intrabar path. Both orders here are
  market orders, so no in-bar stop/limit resolution is involved.
* Leverage, margin, liquidation and funding are not modelled.
"""
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


class SMEmaSmaMaCrossoverMomentum_5cd85a(PinePortBase, IStrategy):
    source_id = "SM_5cd85a117800a5b3"
    source_file = "EMA-SMA-均线交叉-动量指标-EMA-SMA-Moving-Average-Crossover-Momentum-Indicator.md"
    timeframe = "1d"
    can_short = False
    source_defaults: dict = {
        "emaLength": 9,
        "sma30Length": 30,
        "sma50Length": 50,
        "sma200Length": 200,
        "sma325Length": 325,
    }
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    source_reproduce_stops = False
    source_fidelity_notes = [
        "The md's prose and its embedded Pine block agree with the source file; "
        "no md-vs-source disagreement to record.",
        "The entry/exit asymmetry is the source's: the 30-SMA gates both sides, "
        "the 50-SMA participates on the EXIT side only, and the 200/325 SMAs "
        "gate nothing. The md's English prose states the same, so there is "
        "nothing to reconcile.",
        "sellSignal is an `or` of two ta.crossunder calls, evaluated on the same "
        "bar; it is not a crossunder against the lower of the two SMAs.",
        "sma200Value and sma325Value are read by plot calls only, never by a "
        "signal. They are computed because the source computes them, and are "
        "dead with respect to the orders.",
        "PINE_SEMANTICS 3.2 (modelled choice): ta.sma is na until its window is "
        "full and na inside the window propagates, so sma30Value / sma50Value "
        "are na for the first 29 / 49 bars and every comparison against them is "
        "false there.",
        "PINE_SEMANTICS 3.1 (modelled choice): ta.ema is seeded with the first "
        "non-na observation and an na observation does not advance the "
        "recursion; TradingView does not publish its seeding rule.",
        "The plot / plotshape / alertcondition calls are display-only and place "
        "no condition.",
        "No short entry and no stop/limit/trail exit exist, so can_short is "
        "False and source_reproduce_stops is False; a position open at the end "
        "of the window stays open.",
        "PINE_SEMANTICS 1.6 / 5.1: the venue's contract-step rounding and "
        "non-zero taker fees are not modelled. The source declares 0% "
        "commission, which is the cost basis the port carries.",
        "Leverage, margin, liquidation and funding are not modelled.",
    ]

    def pine_indicators(self, dataframe, params):
        close = dataframe["close"]

        # emaValue = ta.ema(close, emaLength)
        ema_value = ta.pine_ema(close, int(params["emaLength"]))
        # sma30Value / sma50Value / sma200Value / sma325Value
        sma30 = ta.pine_sma(close, int(params["sma30Length"]))
        sma50 = ta.pine_sma(close, int(params["sma50Length"]))
        sma200 = ta.pine_sma(close, int(params["sma200Length"]))
        sma325 = ta.pine_sma(close, int(params["sma325Length"]))

        # buySignal  = ta.crossover(emaValue, sma30Value)
        # sellSignal = ta.crossunder(emaValue, sma30Value)
        #              or ta.crossunder(emaValue, sma50Value)
        dataframe["pine_ema"] = ema_value
        dataframe["pine_sma30"] = sma30
        dataframe["pine_sma50"] = sma50
        # Display-only in the source (plot calls), kept so the formula is on the
        # record and never read by the script below.
        dataframe["pine_sma200"] = sma200
        dataframe["pine_sma325"] = sma325
        dataframe["pine_buy_signal"] = ta.pine_crossover(ema_value, sma30)
        dataframe["pine_sell_signal"] = (
            ta.pine_crossunder(ema_value, sma30)
            | ta.pine_crossunder(ema_value, sma50)
        )
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "buy_signal": dataframe["pine_buy_signal"].to_numpy(),
            "sell_signal": dataframe["pine_sell_signal"].to_numpy(),
        }

    def pine_script(self, broker, i, ctx):
        # if (buySignal)
        #     strategy.entry("Buy", strategy.long)
        if ctx["buy_signal"][i]:
            broker.entry("Buy", "long")
        # if (sellSignal)
        #     strategy.close("Buy")
        if ctx["sell_signal"][i]:
            broker.close("Buy")
