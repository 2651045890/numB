"""Port of sources/SM_d6257a301faea511.pine (20均线趋势突破量化交易策略-EMA-20-Breakout-Trend-Following-Quantitative-Trading-Strategy.md).

Pine v5 / v6 -- see FIDELITY for the source's two conflicting `//@version=`
annotations. A daily 20-period EMA of close; a close crossing back above the EMA
buys, a close crossing back below it closes the long:

    emaLength     = 20
    ema20         = ta.ema(close, emaLength)
    longCondition = ta.crossover(close, ema20)   -> strategy.entry("Long", strategy.long)
    exitCondition = ta.crossunder(close, ema20)  -> strategy.close("Long")

`strategy.close` is a market close of the entry named "Long", so the engine
fills it at the next bar's open, exactly as Pine does. There is no short side in
the source at all, hence `can_short` is False.

The `/*backtest` header declares `period: 1d` on `Futures_Binance` BTC_USDT, so
`timeframe` is "1d".

`strategy()` declares only `overlay`, `default_qty_type=strategy.percent_of_equity`
and `default_qty_value=100`; every other property is Pine's documented default:
initial capital 1000000 USD, commission 0%, pyramiding 0.

FIDELITY:

* The source carries TWO version annotations: a bare `//@version=6` line, and
  `//@version=5` appended to a `plot(close)` line immediately above
  `strategy(...)`. Both were preserved as written. The port does not depend on
  which one the compiler resolves: `ta.ema`, `ta.crossover`, `ta.crossunder`,
  `strategy.entry` and `strategy.close` have identical semantics in v5 and v6,
  and `pine_ta` translates the v5/v6 `ta.*` namespace forms the source uses.
* `ta.ema` seeding is a documented parity risk: `pine_ta.pine_ema` seeds the
  recursion with the first non-na observation and lets na bars pass through
  without advancing it. TradingView does not publish its seeding rule.
* The win/loss block (`var float wins/losses/totalTrades`, updated when
  `strategy.position_size == 0 and strategy.opentrades > totalTrades`) only
  feeds chart-label bookkeeping and places no orders. Its result is not drawn
  either -- `label = "Win Rate: " + ...` is a string variable that shadows the
  `label.*` namespace and no `label.new` call ever exists in the source. It is
  dropped as having no trade effect.
* `emaLength = 20` is a literal constant, not an `input()`, so it stays a
  literal in the port rather than becoming a tunable parameter.
* `plot(close)` is a display call with no trade effect.
"""
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


class SMEma20Breakout_d6257a(PinePortBase, IStrategy):
    source_id = "SM_d6257a301faea511"
    source_file = (
        "20均线趋势突破量化交易策略-EMA-20-Breakout-Trend-Following-"
        "Quantitative-Trading-Strategy.md"
    )
    timeframe = "1d"
    can_short = False
    source_defaults: dict = {}
    source_qty_type = "percent_of_equity"
    source_qty_value = 100.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    source_fidelity_notes = [
        "Source has two version annotations (`//@version=6` and a `//@version=5` "
        "appended to `plot(close)`); both kept. The calls used are identical in "
        "v5/v6, so the port does not depend on which one applies.",
        "ta.ema seeding follows pine_ta.pine_ema (first non-na observation seeds "
        "the recursion); TradingView's internal seeding is not publicly specified "
        "and remains a parity risk.",
        "The win/loss statistics block drives only a chart label that the source "
        "never draws (`label` shadows the `label.*` namespace; no `label.new` is "
        "called), so it places no orders and is dropped.",
        "emaLength = 20 and the entry/exit ids are literals in the source, not "
        "`input()`s, and stay literals here.",
    ]

    def pine_indicators(self, dataframe, params):
        close = dataframe["close"]
        ema20 = ta.pine_ema(close, 20)
        dataframe["ema20"] = ema20
        dataframe["pine_long_condition"] = ta.pine_crossover(close, ema20)
        dataframe["pine_exit_condition"] = ta.pine_crossunder(close, ema20)
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "long_condition": dataframe["pine_long_condition"].to_numpy(),
            "exit_condition": dataframe["pine_exit_condition"].to_numpy(),
        }

    def pine_script(self, broker, i, ctx):
        # if longCondition
        #     strategy.entry("Long", strategy.long)
        if ctx["long_condition"][i]:
            broker.entry("Long", "long")
        # if exitCondition
        #     strategy.close("Long")
        if ctx["exit_condition"][i]:
            broker.close("Long")
