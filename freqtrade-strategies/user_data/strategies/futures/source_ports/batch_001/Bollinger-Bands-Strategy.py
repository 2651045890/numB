"""Port of sources/SM_8d4d5174a8736957.pine (Bollinger-Bands-Strategy.md).

Pine v5. Straight Bollinger setup: basis = sma(close, 22),
dev = mult * stdev(close, 22), bands = basis +/- dev. The two trading rules are
STOP entries, not market entries:

    if ta.crossover(close, lower)  -> strategy.entry("BBandLE", long,  stop=lower, oca_name="BollingerBands")
    if ta.crossunder(close, upper) -> strategy.entry("BBandSE", short, stop=upper, oca_name="BollingerBands")

Because close has just crossed back inside the band, the resting stop sits on
the same side as the fresh price move, so the order usually fills on the next
bar at max(stop, open) (long) / min(stop, open) (short). The engine models that:
`broker.entry(..., stop=...)` rests a stop order which `_try_fill_pending`
resolves against the next bar's high/low, filling at the stop price unless the
bar gaps better. Nothing is ever cancelled or exited by the source -- it calls
no strategy.close/exit/cancel -- so a resting entry can stay pending until price
touches it, exactly as on the original platform.

`buyEntry` / `sellEntry` are assigned in the source but never read (the `if`
blocks re-call ta.crossover/ta.crossunder). They are reproduced as columns for
text fidelity and are not used by the script body.

The source declares no input() other than `length` and `mult`, and no
strategy() properties, so Pine's documented defaults apply: initial_capital
1000000 USD, default_qty_type strategy.fixed, default_qty_value 1, 0%
commission, pyramiding 0.

FIDELITY: `ta.stdev` is the population standard deviation (ddof=0), as pine_ta
models it. Entry-side `oca_name` grouping is not modelled by pine_engine (it
models OCA for strategy.exit only); see source_fidelity_notes.
"""
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


class SMBollingerBandsStrategy_8d4d51(PinePortBase, IStrategy):
    source_id = "SM_8d4d5174a8736957"
    source_file = "Bollinger-Bands-Strategy.md"
    timeframe = "2h"
    can_short = True
    source_defaults = {"length": 22, "mult": 2.0}
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    source_fidelity_notes = [
        "Source declares no strategy() properties; Pine's documented defaults "
        "(fixed qty 1, 0% commission, pyramiding 0, initial_capital 1000000) are used.",
        "Entry-side oca_name='BollingerBands' is recorded on the order but the "
        "engine does not model OCA cancellation/reduction between resting entry "
        "orders (PINE_SEMANTICS.md lists exit-side OCA only). The two entries rest "
        "on opposite sides only if both signals fire before either fills.",
        "`comment=` on the entries is display-only and is dropped.",
        "The unused buyEntry / sellEntry assignments are reproduced as columns but "
        "are not read by the script body, as in the source.",
    ]

    def pine_indicators(self, dataframe, params):
        source = dataframe["close"]
        length = params["length"]
        basis = ta.pine_sma(source, length)
        dev = params["mult"] * ta.pine_stdev(source, length)
        lower = basis - dev
        upper = basis + dev
        dataframe["basis"] = basis
        dataframe["upper"] = upper
        dataframe["lower"] = lower
        # Assigned in the source and never read; kept so the port mirrors the text.
        dataframe["buyEntry"] = ta.pine_crossover(source, lower)
        dataframe["sellEntry"] = ta.pine_crossunder(source, upper)
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "buyEntry": dataframe["buyEntry"].to_numpy(),
            "sellEntry": dataframe["sellEntry"].to_numpy(),
            "upper": dataframe["upper"].to_numpy(),
            "lower": dataframe["lower"].to_numpy(),
        }

    def pine_script(self, broker, i, ctx):
        # if (ta.crossover(source, lower))
        if ctx["buyEntry"][i]:
            broker.entry("BBandLE", "long", stop=float(ctx["lower"][i]),
                         oca_name="BollingerBands")
        # if (ta.crossunder(source, upper))
        if ctx["sellEntry"][i]:
            broker.entry("BBandSE", "short", stop=float(ctx["upper"][i]),
                         oca_name="BollingerBands")
