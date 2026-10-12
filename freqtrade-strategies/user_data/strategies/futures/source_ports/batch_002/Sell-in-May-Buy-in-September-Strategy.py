"""Port of sources/SM_0cb464caf364cceb.pine (Sell-in-May-Buy-in-September-Strategy.md).

Pine v5. Enters long in September, closes in May. The source declares no
strategy() properties beyond the title, so Pine's documented defaults apply:
initial_capital 1000000 USD, default_qty_type strategy.fixed, default_qty_value
1, commission 0%, pyramiding 0.

FIDELITY: `month` is the bar's month in the exchange timezone. The local data
is UTC and Binance is UTC, so no offset is applied; a source on another
exchange would need its timezone.
"""
from freqtrade.strategy import IStrategy

from pine_port_base import PinePortBase


class SMSellInMay_0cb464(PinePortBase, IStrategy):
    source_id = "SM_0cb464caf364cceb"
    source_file = "Sell-in-May-Buy-in-September-Strategy.md"
    timeframe = "1d"
    can_short = False
    source_defaults: dict = {}
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    source_fidelity_notes = [
        "Pine `month` uses the exchange timezone; modelled as UTC (Binance is UTC).",
    ]

    def pine_indicators(self, dataframe, params):
        dataframe["pine_month"] = dataframe.index.month
        return dataframe

    def pine_context(self, dataframe, params):
        return {"month": dataframe["pine_month"].to_numpy()}

    def pine_script(self, broker, i, ctx):
        # longCondition = month == 9 ; closecondition = month == 5
        if ctx["month"][i] == 9:
            broker.entry("long", "long")
        if ctx["month"][i] == 5:
            broker.close("long")
