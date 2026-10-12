"""Port of sources/SM_9422376dd4adeac2.pine (batch_001/CM-Sling-Shot-System.md).

Pine v3 (`study("CM_SlingShotSystem", overlay=true)`, the file carries no
`//@version`). Two EMAs and the "conservative entry" of ChrisMoody's SlingShot
method -- price crossing back over the fast EMA in the direction of the fast/
slow spread:

    emaSlow = ta.ema(close, 62)
    emaFast = ta.ema(close, 38)
    entryUpTrend = emaFast > emaSlow and close[1] < emaFast and close > emaFast ? 1 : 0
    entryDnTrend = emaFast < emaSlow and close[1] > emaFast and close < emaFast ? 1 : 0
    codiff  = entryUpTrend == 1 ? entryUpTrend : 0
    codiff2 = entryDnTrend == 1 ? entryDnTrend : 0

THE TRADING BEHAVIOUR IS THE APPENDED BLOCK, not the indicator's author intent.
The file declares an INDICATOR -- `study(...)`, which cannot call
`strategy.entry` -- and the converter appended this pair at the end:

    if sl and codiff
        strategy.entry("SELL", strategy.short)
    else if sl and codiff2
        strategy.entry("BUY", strategy.long)

`sl` is the source's own input `sl = input(true, title="Show 'B'-'S' Letters?")`,
default TRUE, so the guard is live and both arms are reachable. Note the SIDE
each arm takes: the up-trend condition drives `strategy.short` and the
down-trend condition drives `strategy.long`. That is the opposite of what the
condition names suggest and it is what the source does, so it is transcribed as
written rather than "corrected" (rule 2: the source is the authority).

There is NO exit in the source -- no `strategy.close`, `close_all` or `exit`
anywhere in the file, and nothing commented out that could have been one -- so a
position is closed only by the opposite entry reversing it and a position open
at the end of the window stays open (`source_reproduce_stops` is False).

`study()` is not a strategy declaration and the file contains no `strategy()`
call at all, live or commented, so Pine's documented defaults apply:
`default_qty_type=strategy.fixed` with `default_qty_value=1`, initial capital
1000000, commission 0%, `pyramiding=0`, `process_orders_on_close=false`.

The `/*backtest` header declares `period: 15m` on Futures_Binance BTC_USDT, so
`timeframe` is "15m"; its `basePeriod: 5m` is the FMZ backtester's own intrabar
fill granularity, not the strategy's period.

FIDELITY:

* Only `sl` reaches an order call. `sae`, `sce`, `st`, `def` and `pa` are
  transcribed into `source_defaults` (they are the source's inputs, all default
  `true` except `def`) but gate nothing: in the source they only decide which
  plots are drawn (`pullbackUpT` / `pullbackDnT` / `upTrend` / `downTrend` /
  `col` feed `plot` and a commented-out `fill`).
* The appended block is an `if` / `else if`, so at most one arm can fire on a
  bar. The two conditions are in fact mutually exclusive anyway -- `entryUpTrend`
  requires `emaFast > emaSlow` and `entryDnTrend` requires `emaFast < emaSlow` --
  so the port's `if` / `elif` in source order is exactly the source's structure.
* §1.17 DOES NOT BITE HERE, but the integer semantics are kept anyway: this
  source's converter block is `? 1 : 0`, not `? -1 : 0`, so `codiff`/`codiff2`
  are 0/1 and `if sl and codiff` is true exactly when the condition held. The
  columns stay integer (`-1` would also have stayed `-1`, per §1.17: `if x` on a
  non-zero integer is the source's meaning and normalising it to `== 1` would
  silently switch a whole side off).
* `codiff = entryUpTrend == 1 ? entryUpTrend : 0` is a no-op on a 0/1 value and
  is reproduced literally rather than simplified away.
* On bar 0 `close[1]` is na and Pine compares na as false, so neither condition
  can hold; the pandas comparison on the shifted column does the same.
* `emaSlow` / `emaFast` use `ta.ema`, whose seeding rule TradingView does not
  publish (§3.1): `pine_ta.pine_ema` seeds with the first non-na observation, so
  this port can evaluate from the first bars while the original platform's
  series may be na until the window fills. Early-bar trades are a known,
  un-eliminated equivalence risk; no formula, length or lookback is changed here.
* `plot(emaSlow, ...)`, `plot(emaFast, ...)`, the colour ternary, the
  commented-out `fill(...)` and the commented-out function bodies
  (`pullbackUpT` / `pullbackDnT` / `entryUpT` / `entryDnT`) are display-only and
  place no order.
* Leverage, margin, liquidation and funding are not modelled, and the venue's
  contract-step rounding is not modelled either (the chain verifier measures
  that separately rather than treating it as a signal difference).
"""
import numpy as np
import pandas as pd

from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


class SMCmSlingShotSystem_942237(PinePortBase, IStrategy):
    source_id = "SM_9422376dd4adeac2"
    source_file = "CM-Sling-Shot-System.md"
    timeframe = "15m"
    # There is a short entry in the appended block, so the source trades both ways.
    can_short = True
    startup_candle_count = 0
    # Every input() of the source, exactly as declared. Only `sl` gates an order.
    source_defaults: dict = {
        # input(true, title="Show Aggressive Entry?, Or Use as Alert To Potential Conservative Entry?")
        "sae": True,
        # input(true, title="Show Conservative Entry?")
        "sce": True,
        # input(true, title="Show Trend Arrows at Top and Bottom of Screen?")
        "st": True,
        # input(false, title="Only Choose 1 - Either Conservative Entry Arrows or 'B'-'S' Letters")
        "def": False,
        # input(true, title="Show Conservative Entry Arrows?")
        "pa": True,
        # input(true, title="Show 'B'-'S' Letters?")  <- the guard of both entries
        "sl": True,
    }
    # `study(...)` is not a strategy declaration and no strategy() call exists in
    # the file (live or commented) -- see the docstring. Pine's documented
    # defaults therefore apply, and they are stated explicitly because the port
    # layer requires them rather than inheriting Freqtrade's.
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    # No close/exit/stop of any kind is present in the source.
    source_reproduce_stops = False
    source_fidelity_notes = [
        "Converter-appended source: the file declares an indicator "
        "(`study(\"CM_SlingShotSystem\", overlay=true)`) and the tool appended "
        "`if sl and codiff / strategy.entry(\"SELL\", strategy.short) else if sl "
        "and codiff2 / strategy.entry(\"BUY\", strategy.long)`. Pine v3 cannot "
        "call strategy.entry from a study, so the port reproduces the appended "
        "block's actual behaviour (entries only).",
        "The side taken is inverted relative to the condition names: the "
        "UP-trend condition (`entryUpTrend`, price crossing back above the fast "
        "EMA while emaFast > emaSlow) drives a SHORT, and the DOWN-trend "
        "condition drives a LONG. Transcribed as written (rule 2); not corrected.",
        "NO exit exists in this source: no strategy.close / close_all / exit call "
        "appears anywhere in the file, and nothing is commented out that could "
        "have been one. source_reproduce_stops is False and a position open at "
        "the end of the window stays open; only an opposite entry reverses it.",
        "No strategy() declaration exists (live or commented), so Pine's "
        "documented defaults are used: fixed sizing, qty 1, initial capital "
        "1000000, commission 0%, pyramiding 0, process_orders_on_close=false.",
        "`sl = input(true, ...)` is the guard on BOTH appended entries, and its "
        "default is true, so the block is live. The input's title is \"Show "
        "'B'-'S' Letters?\" -- in the indicator it only gated letters; the "
        "converter re-used it as the entry switch. Both readings agree on the "
        "default, so nothing is renamed or forced here.",
        "sae / sce / st / def / pa are the source's inputs too, but they gate "
        "only plot objects (the commented-out function bodies pullbackUpT / "
        "pullbackDnT / entryUpT / entryDnT, upTrend / downTrend / col and the "
        "two plot calls). They are declared in source_defaults so nothing is "
        "hidden, and they place no order.",
        "codiff / codiff2 are `? 1 : 0` integers, not `? -1 : 0`, so the §1.17 "
        "trap does not apply to this source. The columns are nevertheless kept "
        "as integers and the appended guard is written `if x` rather than "
        "`x == 1`, which is the source's meaning for both 1 and -1.",
        "ta.ema seeding is the modelled choice of PINE_SEMANTICS.md 3.1 (first "
        "non-na observation; na does not advance the recursion), so this port "
        "may evaluate earlier than the original platform, whose ta.ema is "
        "believed to be na until the window is full. Early-bar trades are a "
        "known, un-eliminated equivalence risk.",
        "The md's prose describes the SlingShot method as keeping traders on the "
        "trending side of the market with a defined stop; the source, as it "
        "stands with the appended block, has no stop and no exit at all. The md "
        "argument table (v_input_1..v_input_6 = true/true/true/false/true/true) "
        "agrees with the source's input defaults.",
        "Leverage, margin, liquidation and funding are not modelled; the venue's "
        "contract-step rounding is not modelled either (the chain verifier "
        "measures that separately).",
    ]

    def pine_indicators(self, dataframe: pd.DataFrame, params: dict) -> pd.DataFrame:
        close = dataframe["close"]
        # emaSlow = ta.ema(close, 62) / emaFast = ta.ema(close, 38); the lengths
        # are literals in the source and stay literals here.
        ema_slow = ta.pine_ema(close, 62)
        ema_fast = ta.pine_ema(close, 38)
        close_prev = close.shift(1)

        # entryUpTrend = emaFast > emaSlow and close[1] < emaFast and close > emaFast ? 1 : 0
        up_trend = (ema_fast > ema_slow) & (close_prev < ema_fast) & (close > ema_fast)
        # entryDnTrend = emaFast < emaSlow and close[1] > emaFast and close < emaFast ? 1 : 0
        dn_trend = (ema_fast < ema_slow) & (close_prev > ema_fast) & (close < ema_fast)
        entry_up_trend = np.where(up_trend.to_numpy(dtype=bool), 1, 0)
        entry_dn_trend = np.where(dn_trend.to_numpy(dtype=bool), 1, 0)
        # codiff = entryUpTrend == 1 ? entryUpTrend : 0 (a no-op on a 0/1 value,
        # reproduced literally); codiff2 likewise.
        codiff = np.where(entry_up_trend == 1, entry_up_trend, 0)
        codiff2 = np.where(entry_dn_trend == 1, entry_dn_trend, 0)

        dataframe["pine_ema_slow"] = ema_slow
        dataframe["pine_ema_fast"] = ema_fast
        dataframe["pine_codiff"] = codiff
        dataframe["pine_codiff2"] = codiff2
        return dataframe

    def pine_context(self, dataframe: pd.DataFrame, params: dict) -> dict:
        return {
            "codiff": dataframe["pine_codiff"].to_numpy(),
            "codiff2": dataframe["pine_codiff2"].to_numpy(),
            # sl = input(true, ...) -- the guard of both appended entries.
            "sl": bool(params["sl"]),
        }

    def pine_script(self, broker, i: int, ctx: dict) -> None:
        # if sl and codiff
        #     strategy.entry("SELL", strategy.short)
        # else if sl and codiff2
        #     strategy.entry("BUY", strategy.long)
        if ctx["sl"] and ctx["codiff"][i]:
            broker.entry("SELL", "short")
        elif ctx["sl"] and ctx["codiff2"][i]:
            broker.entry("BUY", "long")
