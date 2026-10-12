"""Port of sources/SM_7a5e8f6c513e5984.pine (Gooners BTC Weekly RSI Hack Strategy).

Pine v5. A plain RSI mean-reversion trigger on the 4h series: `rsi = ta.rsi(close, 14)`,
and on bars where the RSI is not na the script enters long on `ta.crossover(rsi, buylevel)`
and closes the "RsiLE" entry on `ta.crossunder(rsi, selllevel)`. Both buylevel and
selllevel default to 52, so the two thresholds coincide; the source is NOT changed here.

`strategy.close` is a market close, so the engine fills it at the next bar's open, which
is what the source's `strategy.close` does. There is no short side at all: `can_short`
is False.

`strategy()` declares default_qty_value = 100 with default_qty_type =
strategy.percent_of_equity, initial_capital = 1000000. No commission_type /
commission_value is given, so Pine's documented 0% commission applies; pyramiding
is not declared, so Pine's documented default of 0 applies.

FIDELITY: the `comment=` strings are trace metadata only and have no trade effect, so
they are dropped. The RSI seeding follows pine_ta.pine_rsi (Wilder rma seeded with the
SMA of the first `length` deltas), which is documented there as an unresolved parity
risk against TradingView's internal seeding.
"""
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


class SMGoonersBtcWeeklyRsiHack_7a5e8f(PinePortBase, IStrategy):
    source_id = "SM_7a5e8f6c513e5984"
    source_file = "Gooners-BTC-Weekly-RSI-Hack-Strategy.md"
    timeframe = "4h"
    can_short = False
    source_defaults = {"length": 14, "buylevel": 52, "selllevel": 52}
    source_qty_type = "percent_of_equity"
    source_qty_value = 100.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    source_fidelity_notes = [
        "strategy.entry/close comment= strings are trace metadata with no trade "
        "effect and are not carried into the port.",
        "ta.rsi seeding follows pine_ta.pine_rsi's documented Wilder rma model; "
        "TradingView's internal seeding is not publicly specified and remains a "
        "parity risk.",
    ]

    def pine_indicators(self, dataframe, params):
        price = dataframe["close"]
        rsi = ta.pine_rsi(price, params["length"])
        dataframe["rsi"] = rsi
        # Pine evaluates both cross helpers on every bar; na rsi propagates to
        # na, which the source's `not na(rsi)` guard then suppresses.
        dataframe["co"] = ta.pine_crossover(rsi, params["buylevel"]).astype(int)
        dataframe["cu"] = ta.pine_crossunder(rsi, params["selllevel"]).astype(int)
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "rsi": dataframe["rsi"].to_numpy(),
            "co": dataframe["co"].to_numpy(),
            "cu": dataframe["cu"].to_numpy(),
        }

    def pine_script(self, broker, i, ctx):
        rsi, co, cu = ctx["rsi"][i], ctx["co"][i], ctx["cu"][i]
        # `if (not na(rsi))` -- a bar with an undefined RSI places nothing.
        if rsi != rsi:
            return
        if co:
            broker.entry("RsiLE", "long")
        if cu:
            broker.close("RsiLE")
