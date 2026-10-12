"""Port of sources/SM_7e786a22719b51da.pine (batch_001/Accurate-Swing-Trading-System.md).

Pine v4. The file declares `study("Accurate Swing Trading System")`, NOT
`strategy(...)`: the two `strategy.entry` calls at the bottom are an order
block APPENDED to the indicator by the converter site that published it
(fmz.com/strategy/367565, named in the md's Detail link). Pine does not compile
`strategy.entry` inside `study()`, so the "original strategy" is the indicator
PLUS that appended block, and the trading behaviour it defines is entry-only:

    if Buy
        strategy.entry("long", strategy.long)
    else if Sell
        strategy.entry("short", strategy.short)

The indicator is a chandelier-style trailing-stop line built from the highest
high / lowest low of the last `no` bars:

    res   = highest(high, no)
    sup   = lowest(low, no)
    avd   = iff(close > res[1], 1, iff(close < sup[1], -1, 0))
    avn   = valuewhen(avd != 0, avd, 0)
    tsl   = iff(avn == 1, sup, res)
    Buy   = crossover(close, tsl)
    Sell  = crossunder(close, tsl)

`avd` latches the last breakout direction (1 = took out the previous high, -1 =
took out the previous low, 0 = inside the range), `avn` carries that direction
forward across the inside bars, and `tsl` is therefore the low of the range
while the latched state is "up" and the high of the range while it is "down".
`Buy` / `Sell` fire on the close crossing that line.

There is NO exit of any kind in the source -- no `strategy.close`, no
`strategy.exit`, and not even a commented-out one. A position is therefore only
ever left by the opposite entry, which the engine models as a reversal.
`pyramiding` keeps Pine's default of 0, so a repeated signal while already
positioned that way is ignored.

FIDELITY:

* The source declares `study(...)`, not `strategy(...)`, so it carries no
  strategy() properties; Pine's documented defaults are what the source_*
  attributes record (fixed size 1, 0% commission, pyramiding 0, initial capital
  1000000). On TradingView strategy.entry inside a study does not compile; the
  host named by the source's /*backtest header and the md's Detail link
  (fmz.com/strategy/367565) is what ran the appended block, and that platform's
  Pine dialect -- not TradingView -- is the behaviour this port reproduces.
* `iff` is Pine v4's ternary; `iff(avn == 1, sup, res)` returns `res` whenever
  the test is false OR na. `avn` is na until the first `avd != 0` bar (Pine's
  valuewhen), and `na == 1` is na, which the ternary treats as false -- so the
  early bars really do take the `res` branch. The port compares the numpy array
  directly, where a NaN compares false, which is the same branch.
* `res` / `sup` are `highest(high, no)` / `lowest(low, no)`: na until `no` bars
  have elapsed, per Pine v4. `pine_ta.pine_highest` / `pine_lowest` reproduce
  that (min_periods = length).
* `valuewhen(avd != 0, avd, 0)` is occurrence 0 = the most recent true bar, and
  it is na before the first one rather than 0; `pine_ta.pine_valuewhen` matches.
  The literal `0` in the source is the OCCURRENCE argument, not a fill value.
* `Barcolor` / `Bgcolor` are input()s that feed only `barcolor()` / `bgcolor()`,
  which are display-only; they place no order. Recorded in source_defaults and
  reproduced as unused values, not deleted. `no` ("Swing") is the only input the
  trading logic reads.
* `plot` / `plotshape` / `barcolor` / `bgcolor` / `alertcondition` are
  display- and alert-only and place no order; dropped.
* The header's backtest window (2021-05-08 to 2022-05-07) is extraction
  metadata, not an `input.time` filter, so no data is trimmed. The header's
  `basePeriod: 15m` is the host's intrabar granularity for filling 4h bars, not
  the strategy's period.
* No stop, limit or trail exit exists, so `source_reproduce_stops` is False.
* `crossover` / `crossunder` on an na operand are False (Pine treats na
  comparisons as false in a boolean context); `pine_ta` fills those to False.
* Leverage, margin, liquidation, funding and the venue's contract-step rounding
  are not modelled (PINE_SEMANTICS.md 1.6 measures the rounding separately).
"""
import numpy as np
import pandas as pd
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


class SMAccurateSwingTradingSystem_7e786a(PinePortBase, IStrategy):
    source_id = "SM_7e786a22719b51da"
    source_file = "Accurate-Swing-Trading-System.md"
    timeframe = "4h"
    can_short = True
    # Input defaults exactly as written; only `no` is read by the trading logic.
    source_defaults: dict = {"no": 3, "Barcolor": True, "Bgcolor": False}
    # study(...), not strategy(...): Pine's documented defaults apply.
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    # No strategy.close / strategy.exit / stop / limit / trail anywhere in the
    # source -- not even a commented-out one.
    source_reproduce_stops = False
    source_mintick = 0.1
    source_fidelity_notes = [
        "The file declares study(...), not strategy(...): the strategy.entry "
        "pair at the bottom is an order block appended by the converter site "
        "(fmz.com/strategy/367565 per the md's Detail link). The port reproduces "
        "the indicator PLUS that appended block, i.e. entry-only behaviour.",
        "No exit exists in the source: no strategy.close, no strategy.exit, no "
        "stop/limit/trail order, and no commented-out exit line. A position is "
        "only left by the opposite entry, which the engine models as a reverse "
        "fill (close the old side, open the new one). source_reproduce_stops is "
        "False accordingly.",
        "iff(avn == 1, sup, res) takes the `res` branch when avn is na, because "
        "Pine treats an na ternary test as false. The port compares the raw "
        "array, where NaN compares false, landing on the same branch -- the "
        "warmup bars are NOT special-cased.",
        "valuewhen(avd != 0, avd, 0): the trailing 0 is the OCCURRENCE argument "
        "(most recent), not a fill value. The result is na before the first "
        "avd != 0 bar, which is what pine_ta.pine_valuewhen returns.",
        "highest/lowest are na until `no` bars have elapsed (Pine v4); "
        "pine_highest/pine_lowest use min_periods = length to match.",
        "The source declares study(...), so no strategy() properties exist and "
        "Pine's documented defaults are used: default_qty_type fixed, "
        "default_qty_value 1, commission 0%, pyramiding 0, initial capital "
        "1000000 USD.",
        "Barcolor and Bgcolor feed only barcolor()/bgcolor() (display-only) and "
        "are not read by the trading logic; they are recorded in "
        "source_defaults and kept as unused values rather than deleted.",
        "plot/plotshape/barcolor/bgcolor/alertcondition are display- or "
        "alert-only and place no order; dropped.",
        "MD-vs-SOURCE: the md front matter names the author as 'Zer3192', while "
        "the source file's own header comment reads '(c) ceyhun' -- the md "
        "records the fmz uploader, the source carries the original author. No "
        "effect on behaviour; recorded, not reconciled.",
        "The md's argument table (v_input_1=3 Swing, v_input_2=true Barcolor, "
        "v_input_3=false Bgcolor) and its embedded source block are otherwise "
        "verbatim identical to the .pine source.",
        "The header's backtest window is extraction metadata, not an input.time "
        "filter, so the port runs on whatever range the caller supplies; "
        "basePeriod: 15m is the host's intrabar fill granularity, not the "
        "strategy's period.",
        "Leverage, margin, liquidation, funding and the venue's contract-step "
        "rounding are not modelled (PINE_SEMANTICS.md 1.6).",
    ]

    def pine_indicators(self, dataframe, params):
        no = int(params["no"])
        high = dataframe["high"]
        low = dataframe["low"]
        close = dataframe["close"]
        close_arr = close.to_numpy(dtype=float)

        # res = highest(high, no);  sup = lowest(low, no)
        res = ta.pine_highest(high, no)
        sup = ta.pine_lowest(low, no)

        # avd = iff(close > res[1], 1, iff(close < sup[1], -1, 0))
        # An na comparison is false, so the warmup bars fall through to 0.
        res_prev = res.shift(1).to_numpy(dtype=float)
        sup_prev = sup.shift(1).to_numpy(dtype=float)
        avd = pd.Series(
            np.where(close_arr > res_prev, 1.0, np.where(close_arr < sup_prev, -1.0, 0.0)),
            index=dataframe.index,
        )

        # avn = valuewhen(avd != 0, avd, 0)   -- occurrence 0, na before the first
        avn = ta.pine_valuewhen(avd != 0, avd, 0)

        # tsl = iff(avn == 1, sup, res)
        tsl = pd.Series(
            np.where(
                avn.to_numpy(dtype=float) == 1.0,
                sup.to_numpy(dtype=float),
                res.to_numpy(dtype=float),
            ),
            index=dataframe.index,
        )

        dataframe["pine_res"] = res
        dataframe["pine_sup"] = sup
        dataframe["pine_avd"] = avd
        dataframe["pine_avn"] = avn
        dataframe["pine_tsl"] = tsl
        dataframe["pine_long_condition"] = ta.pine_crossover(close, tsl)
        dataframe["pine_short_condition"] = ta.pine_crossunder(close, tsl)
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "tsl": dataframe["pine_tsl"].to_numpy(),
            "long_condition": dataframe["pine_long_condition"].to_numpy(),
            "short_condition": dataframe["pine_short_condition"].to_numpy(),
        }

    def pine_script(self, broker, i, ctx):
        # if Buy
        #    strategy.entry("long", strategy.long)
        # else if Sell
        #     strategy.entry("short", strategy.short)
        if ctx["long_condition"][i]:
            broker.entry("long", "long")
        elif ctx["short_condition"][i]:
            broker.entry("short", "short")
