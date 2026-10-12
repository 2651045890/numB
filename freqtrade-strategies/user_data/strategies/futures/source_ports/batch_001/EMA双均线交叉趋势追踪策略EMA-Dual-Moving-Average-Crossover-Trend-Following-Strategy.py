"""Port of sources/SM_5c6268455482fd1b.pine
(batch_001/EMA双均线交叉趋势追踪策略EMA-Dual-Moving-Average-Crossover-Trend-Following-Strategy.md).

Pine v5. A fast/slow EMA crossover, long only, with the two `strategy.*` calls
written as top-level statements carrying `when=` rather than as `if` blocks:

    mediaRapida = ta.ema(close, longitudRapida)
    mediaLenta  = ta.ema(close, longitudLenta)
    comprar = ta.crossover(mediaRapida, mediaLenta)
    vender  = ta.crossunder(mediaRapida, mediaLenta)

    strategy.entry("Compra", strategy.long, when=comprar)
    strategy.close("Compra", when=vender)

Both calls sit on the same script level, so the entry is evaluated before the
close on every bar. `comprar` and `vender` cannot both be true on one bar (a
series cannot cross above and below the same line on the same bar), so the
evaluation order cannot change a fill here; it is kept in the source's order
anyway.

`strategy()` declares only `title` and `overlay`, so every property is Pine's
documented default: `strategy.fixed` / 1 contract, initial capital 1000000,
commission 0%, pyramiding 0, `process_orders_on_close=false`. The `/*backtest`
header declares `period: 1h` on Futures_Binance BTC_USDT, so `timeframe` is
"1h"; its `basePeriod: 15m` is the FMZ backtester's own granularity for filling
those 1h bars, not the strategy's period.

Distinctive source detail: the script is titled "Trend Trader by Marcus Flechas
y Alertas" and its identifiers and alert messages are Spanish
(`Compra` / `Venta`) -- the md's own file name is a Chinese/English description
of the same 9/21 EMA cross, and the md's argument table lists exactly the two
inputs the source has. There is no short entry, so `can_short` is False, and no
stop, limit, trail or cancel call, so `source_reproduce_stops` is False and a
position open at the end of the window stays open.

FIDELITY:

* The md's prose and its embedded Pine block agree with the source file; there
  is no md-vs-source disagreement to record.
* `strategy.entry(..., when=comprar)` and `strategy.close(..., when=vender)`
  are the `when=` form of the same calls an `if` block would make; the port
  passes `when=` rather than branching before the call, so the call is still
  made on every bar and the engine still applies the `when` test at placement
  time.
* `colorTendencia`, the two `plot`s, the two `plotshape`s and the two
  `alertcondition`s are display-only and place no condition.
* PINE_SEMANTICS 3.1 (modelled choice): `ta.ema` is seeded with the first non-na
  observation and an na observation does not advance the recursion.
  TradingView does not publish its seeding rule, so the two EMA series -- and
  therefore the bar of the first cross -- carry this modelled choice.
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


class SMEmaDualMaCrossover_5c6268(PinePortBase, IStrategy):
    source_id = "SM_5c6268455482fd1b"
    source_file = "EMA双均线交叉趋势追踪策略EMA-Dual-Moving-Average-Crossover-Trend-Following-Strategy.md"
    timeframe = "1h"
    can_short = False
    source_defaults: dict = {"longitudRapida": 9, "longitudLenta": 21}
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    source_reproduce_stops = False
    source_fidelity_notes = [
        "The md's prose and its embedded Pine block agree with the source file; "
        "no md-vs-source disagreement to record.",
        "strategy.entry/when and strategy.close/when are the `when=` form of the "
        "same calls an `if` block would make; the port passes `when=` rather "
        "than branching, so both calls are still made on every bar.",
        "Both calls sit at the same script level with the entry first, so the "
        "entry is evaluated before the close on each bar -- kept in the "
        "source's order. The two conditions are mutually exclusive (one series "
        "cannot cross above and below the same line on one bar), so the order "
        "cannot change a fill here.",
        "The source's identifiers and alert messages are Spanish and the title "
        "is 'Trend Trader by Marcus Flechas y Alertas'; nothing about the "
        "orders depends on them.",
        "colorTendencia, the plots, plotshapes and alertconditions are "
        "display-only and place no condition.",
        "PINE_SEMANTICS 3.1 (modelled choice): ta.ema is seeded with the first "
        "non-na observation and an na observation does not advance the "
        "recursion; TradingView does not publish its seeding rule, so the bar "
        "of the first cross carries this modelled choice.",
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
        fast_length = int(params["longitudRapida"])
        slow_length = int(params["longitudLenta"])

        # mediaRapida = ta.ema(close, longitudRapida)
        media_rapida = ta.pine_ema(close, fast_length)
        # mediaLenta = ta.ema(close, longitudLenta)
        media_lenta = ta.pine_ema(close, slow_length)

        # comprar = ta.crossover(mediaRapida, mediaLenta)
        # vender  = ta.crossunder(mediaRapida, mediaLenta)
        dataframe["pine_media_rapida"] = media_rapida
        dataframe["pine_media_lenta"] = media_lenta
        dataframe["pine_comprar"] = ta.pine_crossover(media_rapida, media_lenta)
        dataframe["pine_vender"] = ta.pine_crossunder(media_rapida, media_lenta)
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "comprar": dataframe["pine_comprar"].to_numpy(),
            "vender": dataframe["pine_vender"].to_numpy(),
        }

    def pine_script(self, broker, i, ctx):
        # strategy.entry("Compra", strategy.long, when=comprar)
        broker.entry("Compra", "long", when=bool(ctx["comprar"][i]))
        # strategy.close("Compra", when=vender)
        broker.close("Compra", when=bool(ctx["vender"][i]))
