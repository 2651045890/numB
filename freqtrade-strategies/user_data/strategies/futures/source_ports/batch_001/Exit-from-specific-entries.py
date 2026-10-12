"""Port of sources/SM_2beddde08ac72b7d.pine (Exit-from-specific-entries).

Pine v4. The whole script is a calendar: `newDay` is true on the bar whose day of
month differs from the previous bar's, and four further conditions select the
weekday. On Monday's first bar `strategy.entry(id="EL 1", long=true)` is
submitted, on Tuesday's first bar `strategy.entry(id="EL 2", long=true)`, on
Thursday's first bar `strategy.close(id="EL 2")` and on Friday's first bar
`strategy.close(id="EL 1")`. `pyramiding=2` is what lets the Tuesday entry stack
on the still-open Monday entry; the two ids are what let each of the two closes
address one entry only. There is no short side anywhere in the source, so
`can_short` is False.

`strategy()` declares pyramiding=2 and close_entries_rule="ANY". It declares no
default_qty_type / default_qty_value / initial_capital / commission, so Pine's
documented defaults apply: fixed quantity 1, initial capital 1,000,000 USD, 0%
commission.

FIDELITY: see source_fidelity_notes.
"""
import numpy as np
import pandas as pd

from freqtrade.strategy import IStrategy

import pine_ta as ta  # noqa: F401  (shared library; this source uses no ta.* call)
from pine_port_base import PinePortBase

# Pine spells these `dayofweek.monday` ... `dayofweek.friday`. Pine numbers Sunday
# as 1, pandas numbers Monday as 0; the source only ever compares against the named
# members, so matching the NAME (not the integer) is what keeps this faithful.
_MONDAY = 0
_TUESDAY = 1
_THURSDAY = 3
_FRIDAY = 4


class SMExitFromSpecificEntries_2beddd(PinePortBase, IStrategy):
    source_id = "SM_2beddde08ac72b7d"
    source_file = "Exit-from-specific-entries.md"
    timeframe = "1h"
    can_short = False
    source_defaults = {}
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 2
    source_initial_capital = 1_000_000.0
    source_fidelity_notes = [
        "The source carries no backtest-period header, so the port runs the "
        "mandated 1h fallback. Its `newDay` (dayofmonth != dayofmonth[1]) is a "
        "day-rollover test, so on 1h bars an entry/exit fires on that day's first "
        "hourly bar instead of on a daily bar; the weekday conditions are "
        "unchanged, but a source backtest run on daily bars would place the same "
        "orders at the daily bar's open.",
        "Pine evaluates dayofmonth/dayofweek in the exchange timezone; this port "
        "reads them from the dataframe's timestamps, which are UTC (the shared "
        "layer's documented default). A non-UTC source exchange would shift which "
        "bar counts as the start of a day.",
        "close_entries_rule=\"ANY\" is declared by the source but has no trade "
        "effect here: both closes name their entry id, so the entry-selection "
        "rule never comes into play.",
        "Pine's `na` dayofmonth[1] on the first bar makes `newDay` na, which "
        "compares false in the `and`; the port reproduces this by never signalling "
        "on bar 0.",
    ]

    def pine_indicators(self, dataframe, params):
        index = pd.DatetimeIndex(dataframe.index)
        if index.tz is None:
            index = index.tz_localize("UTC")
        day_of_month = index.day.to_numpy()
        day_of_week = index.dayofweek.to_numpy()

        # newDay = (dayofmonth != dayofmonth[1]); bar 0's dayofmonth[1] is na,
        # and an na comparison is false in Pine's boolean context.
        new_day = np.zeros(len(index), dtype=bool)
        if len(index) > 1:
            new_day[1:] = day_of_month[1:] != day_of_month[:-1]

        dataframe["pine_new_day"] = new_day.astype(float)
        dataframe["pine_first_entry"] = (
            new_day & (day_of_week == _MONDAY)
        ).astype(float)
        dataframe["pine_second_entry"] = (
            new_day & (day_of_week == _TUESDAY)
        ).astype(float)
        dataframe["pine_first_exit"] = (
            new_day & (day_of_week == _THURSDAY)
        ).astype(float)
        dataframe["pine_second_exit"] = (
            new_day & (day_of_week == _FRIDAY)
        ).astype(float)
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "first_entry": dataframe["pine_first_entry"].to_numpy(),
            "second_entry": dataframe["pine_second_entry"].to_numpy(),
            "first_exit": dataframe["pine_first_exit"].to_numpy(),
            "second_exit": dataframe["pine_second_exit"].to_numpy(),
        }

    def pine_script(self, broker, i, ctx):
        # Submitted in source order; the four conditions are mutually exclusive
        # (Monday / Tuesday / Thursday / Friday), so no bar submits two orders.
        if ctx["first_entry"][i]:
            broker.entry("EL 1", "long")
        if ctx["second_entry"][i]:
            broker.entry("EL 2", "long")
        if ctx["first_exit"][i]:
            broker.close("EL 2")
        if ctx["second_exit"][i]:
            broker.close("EL 1")
