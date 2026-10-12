"""Port of sources/SM_26f98fca9124e663.pine (SMA-Crossover-Trading-Strategy.md).

Pine v3. The script builds two SMAs of close (34 and 4) and trades the
crossover between them -- inverted relative to the usual convention:

    shortCondition = crossover(sma(close, 34), sma(close, 4))
    longCondition  = crossunder(sma(close, 34), sma(close, 4))

i.e. the SLOW SMA crossing above the FAST SMA goes short, and the slow SMA
crossing back below the fast SMA goes long. Both are market entries, so a
reversal nets against the open position, which the engine models.

The source declares no inputs and no strategy() properties beyond the title, so
Pine's documented defaults apply: initial_capital 1000000 USD, default_qty_type
strategy.fixed, default_qty_value 1, commission 0%, pyramiding 0.

FIDELITY: v3 `sma(close, n)` is ta.sma, translated by pine_ta.pine_sma (na until
`n` bars have elapsed). v3 `crossover`/`crossunder` are translated by
pine_ta.pine_crossover/pine_crossunder, preserving Pine's "na compares false"
semantics on the comparison bars.
"""
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


class SMSmaCrossover_26f98f(PinePortBase, IStrategy):
    source_id = "SM_26f98fca9124e663"
    source_file = "SMA-Crossover-Trading-Strategy.md"
    timeframe = "10m"
    can_short = True
    source_defaults: dict = {}
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    source_fidelity_notes = [
        "Pine v3 `sma`/`crossover` are the same functions pine_ta models; the "
        "indicator seeds (na until `length` bars elapse) match.",
    ]

    def pine_indicators(self, dataframe, params):
        slow = ta.pine_sma(dataframe["close"], 34)
        fast = ta.pine_sma(dataframe["close"], 4)
        dataframe["sma_slow"] = slow
        dataframe["sma_fast"] = fast
        dataframe["pine_short_condition"] = ta.pine_crossover(slow, fast)
        dataframe["pine_long_condition"] = ta.pine_crossunder(slow, fast)
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "short_condition": dataframe["pine_short_condition"].to_numpy(),
            "long_condition": dataframe["pine_long_condition"].to_numpy(),
        }

    def pine_script(self, broker, i, ctx):
        # shortCondition = crossover(sma(close, 34), sma(close, 4))
        if ctx["short_condition"][i]:
            broker.entry("Sell/Short", "short")
        # longCondition = crossunder(sma(close, 34), sma(close, 4))
        if ctx["long_condition"][i]:
            broker.entry("Buy/Long", "long")
