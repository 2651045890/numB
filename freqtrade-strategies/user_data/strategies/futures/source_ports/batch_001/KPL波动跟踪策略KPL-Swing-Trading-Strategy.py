"""Port of sources/SM_2de0df0b0305bcf5.pine (batch_001/KPL波动跟踪策略KPL-Swing-Trading-Strategy.md).

Pine v4, © ceyhun. A Donchian box picks a trailing line (`tsl`) which the close
has to cross: the box's lower edge while the box is being pushed up, its upper
edge after the box has been broken down.

    no  = input(20)
    res = highest(high, no)
    sup = lowest(low, no)
    avd = iff(close > res[1], 1, iff(close < sup[1], -1, 0))
    avn = valuewhen(avd != 0, avd, 1)
    tsl = iff(avn == 1, sup, res)
    sl  = iff(close > tsl, highest(lowest(low, no / 2), no / 2),
                           lowest(highest(high, no / 2), no / 2))

    if crossover(close, tsl)
        strategy.entry("Long", strategy.long, comment="Long")
    if crossunder(close,tsl)
        strategy.entry("Short", strategy.short, comment="Short")

The state that drives `tsl` is `avn`, the value of `avd` one occurrence back, so
it is only the SECOND-most-recent break of the box that selects the side. That
is what `valuewhen(..., 1)` means and it is carried through
`pine_ta.pine_valuewhen(..., 1)`; the `occurrence` argument is NOT dropped to 0.
Before `avd` has ever been non-zero, `avn` is na, `avn == 1` is false, and `tsl`
therefore takes `res`.

Both entries are plain market entries and there is no exit call at all: a
position is only ever closed by the opposite entry reversing it. The port
therefore declares `source_reproduce_stops = False`, and a position still open
at the end of the window stays open. The `comment="Long"` / `comment="Short"`
arguments are display-only and have no order-side equivalent in `pine_engine`.

`strategy("KPL Swing Strategy", overlay=true)` declares only `title` and
`overlay`, so Pine's documented defaults apply: `default_qty_type =
strategy.fixed`, `default_qty_value = 1`, `commission_value = 0`,
`pyramiding = 0`, initial capital 1000000 and `process_orders_on_close = false`.
The `/*backtest` header declares `period: 2d` on Futures_Binance BTC_USDT, so
`timeframe` is "2d"; its `basePeriod: 1d` is the FMZ backtester's own granularity
for filling those 2-day bars, not the strategy's period. There is no local OKX
futures history at 2d, so the chain verifier can only report this port as
`skipped_no_local_data`.

FIDELITY:

* `avd` is a plain per-bar value here, NOT a recursive one: its innermost branch
  is the literal `0`, not `nz(avd[1], 0)`. Only `tsl` inherits state, and it
  inherits it through `valuewhen`, which is reproduced with the same history
  semantics (`pine_ta.pine_valuewhen`). Neither is seeded or approximated.
* `valuewhen(avd != 0, avd, 1)` asks for the one-before-most-recent occurrence,
  so on the bar a break happens `avn` still names the PREVIOUS break. Reading it
  as occurrence 0 (the current break) would flip `tsl` one break early; the
  argument is transcribed as written.
* On the warm-up bars `res` / `sup` are na (`highest` / `lowest` are na until the
  window is full, and `avd`'s comparisons against `res[1]` / `sup[1]` are false
  for an na operand, as Pine's series comparisons are), so `avd` is 0, `avn` is
  na, `avn == 1` is false and `tsl` is `res` -- which is itself na, so
  `crossover(close, tsl)` is false and no order is placed. Reproduced by letting
  the na comparison yield False in float64.
* `no / 2` is Pine v4 float division (20 / 2 = 10.0), and it is passed to
  `lowest` / `highest` as an integer-valued float; `pine_ta` accepts it as a
  length. The nesting is kept exactly: `highest(lowest(low, no/2), no/2)` and
  `lowest(highest(high, no/2), no/2)`, i.e. a 10-bar low smoothed by a 10-bar
  high, not a single 10-bar extreme.
* `sl` is computed by the source and reaches only `plot(sl, ...)`; it is carried
  in the frame for completeness but reaches no decision.
* `bgcolor(abs(close - tsl[1]) > close ? color.white : close < tsl ? color.red :
  color.green, 90, offset=0)` is display-only and is not reproduced.
* A repeated same-direction entry while that direction is already open is
  refused by Pine's `pyramiding` default of 0, which `pine_engine` reproduces by
  blocking same-direction stacking.
* The `/*backtest` window (2022-09-20..2023-09-20) belongs to the FMZ backtester;
  the chain verifier's window is its own choice and is not driven by this header.
* Contract-step rounding, leverage, margin, liquidation and funding are not
  modelled (PINE_SEMANTICS §1.6, §二-4).
"""
import numpy as np
import pandas as pd

from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


class SMKplSwing_2de0df(PinePortBase, IStrategy):
    source_id = "SM_2de0df0b0305bcf5"
    source_file = "KPL波动跟踪策略KPL-Swing-Trading-Strategy.md"
    timeframe = "2d"
    can_short = True
    source_defaults: dict = {"no": 20}
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    source_reproduce_stops = False
    source_fidelity_notes = [
        "avd is a plain per-bar value (its innermost branch is the literal 0), "
        "not a recursive one; only tsl inherits state, through valuewhen.",
        "valuewhen(avd != 0, avd, 1) asks for the one-before-most-recent "
        "occurrence, so on the bar a break happens avn still names the PREVIOUS "
        "break. The occurrence argument is transcribed as written -- reading it "
        "as 0 would flip tsl one break early.",
        "On the warm-up bars res/sup are na, avd is 0, avn is na, avn == 1 is "
        "false and tsl is res (itself na), so crossover(close, tsl) is false and "
        "no order is placed. Reproduced by letting na comparisons yield False in "
        "float64, which is how Pine's series comparisons behave.",
        "no / 2 is Pine v4 float division (20 / 2 = 10.0) and is accepted as an "
        "integer-valued length; the nesting highest(lowest(low, no/2), no/2) / "
        "lowest(highest(high, no/2), no/2) is kept exactly, not collapsed into a "
        "single 10-bar extreme.",
        "sl is computed by the source and reaches only plot(sl); it is carried in "
        "the frame but reaches no decision.",
        "comment=\"Long\" / comment=\"Short\" on the entries are display-only and "
        "have no order-side equivalent in pine_engine.",
        "There is no exit call in the source: a position is closed only by the "
        "opposite entry reversing it, so source_reproduce_stops is False and a "
        "position open at the end of the window stays open.",
        "A repeated same-direction entry while that direction is already open is "
        "refused by Pine's pyramiding default of 0, which pine_engine reproduces "
        "by blocking same-direction stacking.",
        "strategy() declares only title/overlay, so Pine's defaults apply: "
        "qty_type fixed, qty_value 1, commission 0, pyramiding 0, initial "
        "capital 1000000, process_orders_on_close false.",
        "bgcolor / plot / titles / colours are display-only and are not "
        "reproduced.",
        "The /*backtest period is 2d and there is no local OKX futures history at "
        "that period, so the chain verifier can only report "
        "skipped_no_local_data for this port.",
        "Contract-step rounding, leverage, margin, liquidation and funding are "
        "not modelled (PINE_SEMANTICS §1.6, §二-4).",
    ]

    def pine_indicators(self, dataframe, params):
        no = int(params["no"])
        close = dataframe["close"]
        high = dataframe["high"]
        low = dataframe["low"]

        # res = highest(high, no)   /   sup = lowest(low, no)
        res = ta.pine_highest(high, no)
        sup = ta.pine_lowest(low, no)

        # avd = iff(close > res[1], 1, iff(close < sup[1], -1, 0))
        # An na res[1] / sup[1] makes both comparisons false -> avd is 0.
        above = close > res.shift(1)
        below = close < sup.shift(1)
        avd = pd.Series(
            np.where(above, 1.0, np.where(below, -1.0, 0.0)),
            index=close.index,
            dtype=float,
        )

        # avn = valuewhen(avd != 0, avd, 1)
        avn = ta.pine_valuewhen(avd != 0, avd, 1)

        # tsl = iff(avn == 1, sup, res)
        # (avn is na until the first break, and an na condition takes the else
        # branch / compares false, so tsl is res there.)
        tsl = sup.where(avn == 1, res)

        # sl = iff(close > tsl, highest(lowest(low, no / 2), no / 2),
        #                       lowest(highest(high, no / 2), no / 2))
        half = no / 2
        sl = np.where(
            close > tsl,
            ta.pine_highest(ta.pine_lowest(low, half), half),
            ta.pine_lowest(ta.pine_highest(high, half), half),
        )

        dataframe["pine_kpl_res"] = res
        dataframe["pine_kpl_sup"] = sup
        dataframe["pine_kpl_avd"] = avd
        dataframe["pine_kpl_avn"] = avn
        dataframe["pine_kpl_tsl"] = tsl
        dataframe["pine_kpl_sl"] = pd.Series(sl, index=close.index, dtype=float)
        # if crossover(close, tsl)   /   if crossunder(close, tsl)
        dataframe["pine_long_condition"] = ta.pine_crossover(close, tsl)
        dataframe["pine_short_condition"] = ta.pine_crossunder(close, tsl)
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "long_condition": dataframe["pine_long_condition"].to_numpy(dtype=bool),
            "short_condition": dataframe["pine_short_condition"].to_numpy(dtype=bool),
        }

    def pine_script(self, broker, i, ctx):
        # if crossover(close, tsl)
        #     strategy.entry("Long", strategy.long, comment="Long")
        if ctx["long_condition"][i]:
            broker.entry("Long", "long")
        # if crossunder(close,tsl)
        #     strategy.entry("Short", strategy.short, comment="Short")
        if ctx["short_condition"][i]:
            broker.entry("Short", "short")
