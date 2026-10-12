"""Port of sources/SM_62348c45b8a695b5.pine
(batch_001/EMA均线交叉与短期信号策略-EMA-Crossover-with-Short-term-Signals-Strategy.md).

Pine v5 (`//@version=5`,
`strategy("EMA Crossover with Short-term Signals", overlay=true)`). Five EMAs
are computed; only the two built on the bar extremes drive orders:

    shortest = ta.ema(close, 144)
    short    = ta.ema(close, 34)
    longer   = ta.ema(close, 76)

    stLong  = ta.ema(high, 30)
    stShort = ta.ema(low, 30)

    if (close > stLong)
        strategy.entry("Buy", strategy.long)
    if (close < stShort)
        strategy.close("Buy")

The 144/34/76 EMAs on close are plotted but never referenced by a trading
condition, so they are computed-and-ignored as in the source (see FIDELITY).

`strategy()` declares only `title` and `overlay`, and the source has no
`input()`, so every property is Pine's documented default:
`default_qty_type=strategy.fixed`, `default_qty_value` 1 contract, initial
capital 1000000, commission 0%, `pyramiding=0`,
`process_orders_on_close=false`. There is no stop / limit / trail, hence
`source_reproduce_stops` is False.

`can_short` is False: the sole entry is `strategy.long`; `strategy.close("Buy")`
only flattens.

The `/*backtest` header declares `period: 1d` on Futures_Binance BTC_USDT, so
`timeframe` is "1d"; `basePeriod: 1h` is the FMZ backtester's fill granularity
for those daily bars, not the strategy's period.

FIDELITY:

* The md's prose describes the 144/34/76 EMAs as the "trend" of the strategy and
  the two extreme-price EMAs as "short-term signals". That matches the code, but
  the prose implies the three trend EMAs take part in the decision -- they do
  not. They are computed and plotted and nothing else. The port keeps the
  discrepancy: the EMAs on close are not re-introduced as filters (rule 2: the
  source is the authority).
* The md also says "when the close breaks above / below" the level. The source
  tests `close > stLong` / `close < stShort` on every bar, i.e. a state test,
  not a cross. The port implements the state test; `ta.crossover` /
  `ta.crossunder` are NOT used.
* `stLong` / `stShort` are EMAs OF THE BAR HIGH / LOW series, not of close, and
  not a 30-bar highest/lowest. `ta.ema(high, 30)` and `ta.ema(low, 30)` are
  reproduced literally.
* The `fill(...)` / `clr = close > stLong ? ...` block is display-only
  (`fill` and `plot` place no orders) and is not reproduced.
* `ta.ema` is seeded with the first non-na observation (see the parity note in
  `pine_ta.pine_ema` and PINE_SEMANTICS.md §3.1); TradingView does not publish
  its seeding rule, so the first few bars of these EMAs carry a modelled choice
  rather than a verified one.
* A position open at the end of the window stays open: the source only ever
  closes it via a `close < stShort` signal.
* Contract-step quantity rounding and leverage/margin/funding are not modelled.
"""
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


class SMEmaCrossoverWithShortTermSignals_62348c(PinePortBase, IStrategy):
    source_id = "SM_62348c45b8a695b5"
    source_file = "EMA均线交叉与短期信号策略-EMA-Crossover-with-Short-term-Signals-Strategy.md"
    timeframe = "1d"
    can_short = False
    # The source declares no input(); the five EMA lengths are literals in the
    # code and stay literals here.
    source_defaults: dict = {}
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    source_reproduce_stops = False
    source_fidelity_notes = [
        "strategy() declares only title/overlay and the source has no input(); "
        "qty_type=fixed, qty_value=1, initial_capital=1000000, commission=0%, "
        "pyramiding=0, process_orders_on_close=false are Pine's defaults.",
        "The 144/34/76 EMAs on close are plotted but never referenced by a "
        "trading condition; the md's prose presents them as part of the trend "
        "logic, but the code does not use them. Not re-introduced as filters.",
        "The entry/exit tests are `close > stLong` / `close < stShort` state "
        "tests, not crossings; the md's wording ('breaks above/below') is "
        "looser than the code.",
        "stLong/stShort are EMAs of the bar HIGH / LOW series "
        "(ta.ema(high, 30) / ta.ema(low, 30)), not of close and not a "
        "30-bar highest/lowest.",
        "The `clr` / `fill(...)` block is display-only and is not reproduced.",
        "pine_ema seeds on the first non-na observation; TradingView's seeding "
        "rule is unpublished (PINE_SEMANTICS.md §3.1), so the early bars of "
        "these EMAs are a modelled choice.",
        "No stop/limit/trail: a position open at the end of the window stays "
        "open; source_reproduce_stops is False.",
        "Contract-step quantity rounding and leverage/margin/funding are not "
        "modelled.",
    ]

    def pine_indicators(self, dataframe, params):
        close = dataframe["close"]
        high = dataframe["high"]
        low = dataframe["low"]

        # shortest = ta.ema(close, 144); short = ta.ema(close, 34);
        # longer = ta.ema(close, 76) -- plotted only, no order reads them.
        shortest = ta.pine_ema(close, 144)
        short = ta.pine_ema(close, 34)
        longer = ta.pine_ema(close, 76)

        # stLong = ta.ema(high, 30); stShort = ta.ema(low, 30)
        st_long = ta.pine_ema(high, 30)
        st_short = ta.pine_ema(low, 30)

        dataframe["pine_ema_close_144"] = shortest
        dataframe["pine_ema_close_34"] = short
        dataframe["pine_ema_close_76"] = longer
        dataframe["pine_st_long"] = st_long
        dataframe["pine_st_short"] = st_short
        # if (close > stLong) -> strategy.entry("Buy", strategy.long)
        dataframe["pine_long_condition"] = (close > st_long).fillna(False)
        # if (close < stShort) -> strategy.close("Buy")
        dataframe["pine_exit_condition"] = (close < st_short).fillna(False)
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "long_condition": dataframe["pine_long_condition"].to_numpy(dtype=bool),
            "exit_condition": dataframe["pine_exit_condition"].to_numpy(dtype=bool),
        }

    def pine_script(self, broker, i, ctx):
        # if (close > stLong)
        #     strategy.entry("Buy", strategy.long)
        if ctx["long_condition"][i]:
            broker.entry("Buy", "long")
        # if (close < stShort)
        #     strategy.close("Buy")
        if ctx["exit_condition"][i]:
            broker.close("Buy")
