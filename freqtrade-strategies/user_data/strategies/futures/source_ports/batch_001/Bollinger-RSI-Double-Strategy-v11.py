"""Port of sources/SM_aa440045fdd93443.pine
(batch_001/Bollinger-RSI-Double-Strategy-v11.md).

Pine v2 -- ChartArt's "Bollinger + RSI, Double Strategy" v1.1. Both indicators
must be in the same overbought/oversold condition on the same bar before an
entry is placed, and the entry itself is a RESTING STOP ORDER parked at the
band, not a market order:

    vrsi    = rsi(close, RSIlength)
    BBbasis = sma(close, BBlength)
    BBdev   = 2 * stdev(close, BBlength)      // BBmult = 2, literal
    BBupper = BBbasis + BBdev
    BBlower = BBbasis - BBdev

    if not na(vrsi)
        if crossover(vrsi, 50)   and crossover(close, BBlower)
            strategy.entry("RSI_BB_L", strategy.long,  stop=BBlower, comment="RSI_BB_L")
        if crossunder(vrsi, 50) and crossunder(close, BBupper)
            strategy.entry("RSI_BB_S", strategy.short, stop=BBupper, comment="RSI_BB_S")

`RSIoverSold` / `RSIoverBought` are both 50 and are literals in the source, not
inputs. `BBmult` is 2: its `input(2.0, ...)` is commented out.

The `stop=` arguments are the part that does NOT survive the framework trip
(PINE_SEMANTICS.md 2.11): a Pine stop entry rests until a later bar trades
through the level, while Freqtrade's strategy interface can only place a market
entry on the next open. The engine models the resting order correctly, so what
`verify_chain` compares is the engine's fill against the framework's projected
next-open fill -- the difference is expected and is a framework boundary, not a
port defect. The `stop` is passed through to `broker.entry` unchanged so the
engine's own behaviour is the source's.

There is no exit call of any kind, so `source_reproduce_stops` is False: a
position is only ever closed by the opposite entry reversing it, and one held at
the end of the data stays open. `can_short` is True.

The source declares no `strategy()` properties beyond title/shorttitle/overlay,
so Pine's documented defaults apply: initial_capital 1000000 USD,
default_qty_type `strategy.fixed`, default_qty_value 1, commission 0%,
pyramiding 0. `switch1` / `switch2` are `input(true)` but their only readers are
commented-out `barcolor` / `bgcolor` calls, so they are carried as parameters
and used by nothing.
"""
from __future__ import annotations

from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


class SMBollingerRsiDouble_aa4400(PinePortBase, IStrategy):
    source_id = "SM_aa440045fdd93443"
    source_file = "Bollinger-RSI-Double-Strategy-v11.md"
    timeframe = "15m"
    can_short = True
    source_defaults: dict = {
        "RSIlength": 6,
        "BBlength": 200,
        "switch1": True,
        "switch2": True,
    }
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    # The two `stop=` arguments are on ENTRY orders, not on an exit leg, and the
    # source has no strategy.exit / strategy.close at all.
    source_reproduce_stops = False
    source_fidelity_notes = [
        "strategy.entry(..., stop=BBlower) / (..., stop=BBupper) are RESTING STOP "
        "ENTRY orders. The engine models them (they rest until a later bar trades "
        "through the level, PINE_SEMANTICS.md 2.11); Freqtrade's strategy interface "
        "cannot express a stop entry, so the projected signal is a next-open market "
        "order placed on the bar the order was created. The two are expected to "
        "diverge in both timing and price.",
        "The `stop=` argument is forwarded to broker.entry verbatim, so the engine's "
        "own fill behaviour is the source's, not an approximation of it.",
        "BBmult is 2: the source writes `BBmult = 2` and its input(2.0, minval=0.001, "
        "maxval=50, ...) is commented out. It stays a literal.",
        "RSIoverSold and RSIoverBought are both 50 and are plain assignments, not "
        "inputs, so they appear in no source_defaults entry and stay literals.",
        "stdev is Pine's population standard deviation (ddof=0), which is what "
        "pine_ta.pine_stdev computes -- not pandas' sample stdev.",
        "The `if (not na(vrsi))` guard is reproduced: on bars where the RSI has no "
        "value yet neither entry can be placed. Both nested conditions are also "
        "compared with `and`, so both indicators must cross on the SAME bar.",
        "The 200-bar Bollinger window means BBupper/BBlower are na for the first 199 "
        "bars, so no condition can be true there; startup_candle_count stays 0 as in "
        "the shared base.",
        "switch1 / switch2 are input(true) but only feed a TrendColor series whose "
        "readers (barcolor / bgcolor) are both commented out. They are carried as "
        "parameters and used by nothing; TrendColor itself is display-only.",
        "No exit call exists: a position is closed only by the opposite entry "
        "reversing it, so source_reproduce_stops is False and a position open at the "
        "end of the data stays open.",
        "The source declares no strategy() properties beyond title/shorttitle/"
        "overlay, so Pine's documented defaults are used: fixed / 1 contract, "
        "initial capital 1000000, commission 0%, pyramiding 0.",
        "Leverage, margin, liquidation and funding are not modelled; the venue's "
        "contract-step rounding is not modelled either and is measured separately by "
        "verify_chain.",
    ]

    # ---- ta.* / bare builtins ---------------------------------------------
    def pine_indicators(self, dataframe, params):
        close = dataframe["close"].astype(float)

        # vrsi = rsi(price, RSIlength)
        vrsi = ta.pine_rsi(close, int(params["RSIlength"]))
        # BBbasis = sma(price, BBlength) ; BBdev = BBmult * stdev(price, BBlength)
        bb_mult = 2  # source literal; the input() for it is commented out
        bb_length = int(params["BBlength"])
        basis = ta.pine_sma(close, bb_length)
        deviation = bb_mult * ta.pine_stdev(close, bb_length)
        upper = basis + deviation
        lower = basis - deviation

        dataframe["pine_rsi"] = vrsi
        dataframe["pine_bb_basis"] = basis
        dataframe["pine_bb_upper"] = upper
        dataframe["pine_bb_lower"] = lower

        rsi_over_sold = 50  # RSIoverSold, a literal
        rsi_over_bought = 50  # RSIoverBought, a literal
        # if (crossover(vrsi, RSIoverSold) and crossover(source, BBlower))
        long_condition = ta.pine_crossover(vrsi, rsi_over_sold) & ta.pine_crossover(
            close, lower
        )
        # if (crossunder(vrsi, RSIoverBought) and crossunder(source, BBupper))
        short_condition = ta.pine_crossunder(
            vrsi, rsi_over_bought
        ) & ta.pine_crossunder(close, upper)
        dataframe["pine_long_condition"] = long_condition
        dataframe["pine_short_condition"] = short_condition
        # if (not na(vrsi))
        dataframe["pine_rsi_ready"] = vrsi.notna()
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "rsi_ready": dataframe["pine_rsi_ready"].to_numpy(),
            "long_condition": dataframe["pine_long_condition"].to_numpy(),
            "short_condition": dataframe["pine_short_condition"].to_numpy(),
            "bb_lower": dataframe["pine_bb_lower"].to_numpy(dtype=float),
            "bb_upper": dataframe["pine_bb_upper"].to_numpy(dtype=float),
        }

    # ---- strategy.* -------------------------------------------------------
    def pine_script(self, broker, i, ctx):
        # if (not na(vrsi))
        if not ctx["rsi_ready"][i]:
            return
        # if (crossover(vrsi, RSIoverSold) and crossover(source, BBlower))
        #     strategy.entry("RSI_BB_L", strategy.long, stop=BBlower, comment="RSI_BB_L")
        if ctx["long_condition"][i]:
            broker.entry("RSI_BB_L", "long", stop=ctx["bb_lower"][i])
        # if (crossunder(vrsi, RSIoverBought) and crossunder(source, BBupper))
        #     strategy.entry("RSI_BB_S", strategy.short, stop=BBupper, comment="RSI_BB_S")
        if ctx["short_condition"][i]:
            broker.entry("RSI_BB_S", "short", stop=ctx["bb_upper"][i])
