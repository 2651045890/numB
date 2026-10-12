"""Port of sources/SM_57812f4b0c8af2b3.pine (batch_001/Chandelier-Exit.md).

Pine v4. The file is Alex Orekhov's (everget) "Chandelier Exit" INDICATOR --
`study("Chandelier Exit", shorttitle="CE", overlay=true)` -- the ATR trailing
stop, with a converter-appended order block at the end:

    atr      = mult * atr(length)
    longStop = (useClose ? highest(close, length) : highest(length)) - atr
    shortStop= (useClose ? lowest(close, length)  : lowest(length))  + atr
    (both legs ratchet: they only ever move in the position's favour)
    var int dir = 1
    dir := close > shortStopPrev ? 1 : close < longStopPrev ? -1 : dir
    buySignal  = dir == 1  and dir[1] == -1
    sellSignal = dir == -1 and dir[1] == 1

    if buySignal
        strategy.entry("Enter Long", strategy.long)
    else if sellSignal
        strategy.entry("Enter Short", strategy.short)

`study()` cannot host `strategy.entry`, so the trading behaviour IS that block.
There is NO exit anywhere in the file: the Chandelier lines are drawn, never
used as `strategy.exit`, so a position is closed only by the opposite signal
reversing it and one still open at the end of the window stays open
(`source_reproduce_stops = False`).

The state machine is sequential and is replayed bar by bar. Two Pine subtleties
drive the loop:

  * `longStopPrev = nz(longStop[1], longStop)`: `longStop[1]` is the PREVIOUS
    bar's FINAL value (after that bar's `:=`), while the second argument is the
    CURRENT bar's raw expression -- so on the first bar, or any bar whose window
    is not full, the two collapse into the raw value.
  * `longStop := close[1] > longStopPrev ? max(longStop, longStopPrev) :
    longStop`: `longStop` inside the ternary is still this bar's raw value, so
    the ratchet is `max(raw, prev)`.
  * `dir` holds when neither branch triggers (it is a `var`, and the third arm
    of the ternary reads `dir` itself), so the direction persists across bars
    until one of the two stop levels is crossed.

FIDELITY:

* `highest(length)` / `lowest(length)` are the pre-v4 one-argument forms: they
  operate on `high` / `low`. The source only reaches them through
  `useClose ? ... : ...`; `useFromClose` defaults true, so the default path is
  `highest(close, length)`. Both arms are implemented.
* `atr(length)` is pine_ta.pine_atr = rma(tr(true), length), which is exactly
  Pine's `ta.atr` (its `ta.tr` seed on bar 0 is `high - low`). PINE_SEMANTICS.md
  section 3.7 is about the OTHER convention (`ta.tr` with handle_na=false) and
  does not apply to `atr`.
* na handling: `longStopPrev` / `shortStopPrev` are na while the `highest` /
  `lowest` / `atr` windows are not yet full, and Pine treats an na comparison as
  false, so `dir` simply keeps its previous value through the warm-up (starting
  at its `var` initial value 1) and no signal can fire -- `dir[1]` is na on bar
  0, which makes both signals false there. The loop reproduces that with
  `np.isnan` guards and `np.maximum` / `np.minimum`, which propagate na the way
  Pine's `max` / `min` do.
* `dir` is an `int` in the source; the port keeps it as a float column only so
  na-free history slicing is uniform, and compares it against 1.0 / -1.0.
* `showLabels`, `highlightState`, `longColor` / `shortColor`, every `plot`,
  `plotshape`, `fill` and `alertcondition` (including `changeCond`) are display
  or alert only; none of them reaches an order and none is reproduced. The
  three `alertcondition` calls are alerts on the same signals the entries use.
* No `strategy()` call exists -- the top-level declaration is a `study()` -- so
  every trade property is Pine's documented default: `default_qty_type` fixed,
  `default_qty_value` 1 CONTRACT (not 100% of equity), `initial_capital`
  1000000, commission 0%, `pyramiding` 0, `process_orders_on_close` false.
* The `/*backtest` header declares `period: 30m` on Futures_Binance BTC_USDT, so
  `timeframe` is "30m"; its `basePeriod: 15m` is the FMZ backtester's fill
  granularity.
* Leverage, margin, liquidation, funding and the venue's contract-step rounding
  are not modelled.
"""
import numpy as np
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


class SMChandelierExit_57812f(PinePortBase, IStrategy):
    source_id = "SM_57812f4b0c8af2b3"
    source_file = "Chandelier-Exit.md"
    timeframe = "30m"
    can_short = True
    source_defaults: dict = {
        "length": 22,
        "mult": 3.0,
        "showLabels": True,
        "useClose": True,
        "highlightState": True,
    }
    # The file declares a `study()`, not a `strategy()`, so Pine's documented
    # defaults apply -- see the docstring.
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    # The appended block places no stop, limit, target or trailing exit, and the
    # source's own Chandelier lines are plots, not orders.
    source_reproduce_stops = False
    source_fidelity_notes = [
        "Converter-appended source: the file declares an INDICATOR (`study("
        "\"Chandelier Exit\", shorttitle=\"CE\", overlay=true)`) and a tool "
        "appended the block `if buySignal / strategy.entry(\"Enter Long\", "
        "strategy.long) else if sellSignal / strategy.entry(\"Enter Short\", "
        "strategy.short)`. The ATR trailing-stop lines the indicator draws are "
        "never used as strategy.exit, so the port reproduces the appended "
        "block: entries only, directions only.",
        "The Chandelier stop levels do NOT become exits. `longStopPlot` / "
        "`shortStopPlot` are plots, and there is no strategy.exit / "
        "strategy.close anywhere in the file, live or commented out, so "
        "source_reproduce_stops is False and a position is closed only by the "
        "opposite entry reversing it.",
        "The state machine (`longStop` / `shortStop` ratchets and `dir`) is "
        "sequential and replayed bar by bar. `longStop[1]` in "
        "`nz(longStop[1], longStop)` is the previous bar's POST-assignment "
        "value, while the second argument of nz is the current bar's raw "
        "expression; the loop reproduces both, including the collapse of the "
        "two during warm-up.",
        "`highest(length)` / `lowest(length)` are the pre-v4 one-argument "
        "forms, i.e. over high / low. Both the useClose=true and useClose=false "
        "arms are implemented, since the inputs are source defaults and may be "
        "overridden.",
        "`atr(length)` is pine_ta.pine_atr = rma(tr(true), length), which is "
        "Pine's own ta.atr (tr(true) seeds bar 0 with high - low), so "
        "PINE_SEMANTICS.md section 3.7 does not apply here.",
        "na handling: while the highest / lowest / atr windows are not full the "
        "stop levels are na; Pine compares na as false, so `dir` keeps its "
        "previous value (starting from the `var` initial value 1) and nothing "
        "signals. `dir[1]` is na on bar 0, so both signals are false there. The "
        "loop uses np.maximum / np.minimum, which propagate na as Pine's max / "
        "min do.",
        "showLabels / highlightState only gate labels and fills; the three "
        "alertcondition calls are alerts, not orders; plot / plotshape / fill "
        "are display only. None is reproduced.",
        "No `strategy()` call exists (the declaration is a study), so trade "
        "properties are Pine's documented defaults: fixed sizing, qty 1, "
        "initial capital 1000000, commission 0%, pyramiding 0, "
        "process_orders_on_close=false.",
        "The /*backtest header declares `period: 30m` on Futures_Binance "
        "BTC_USDT (`basePeriod: 15m` is the FMZ fill granularity).",
        "md-vs-source inconsistency (provenance only): the md's Author field "
        "says ChaoZhang while the source's own header says the script is "
        "(c) Alex Orekhov (everget). The code in the two is identical.",
        "md-vs-source inconsistency (reading, not behaviour): the md's Strategy "
        "Description calls this 'a trailing stop-loss based on the Average True "
        "Range (ATR)' and 'a redesign of the Chandelier Exit indicator'. The "
        "executable trade block contains no trailing stop and no exit at all -- "
        "the Chandelier levels are plots -- so the description's risk-management "
        "reading is NOT reproduced as an exit. Recorded, not 'fixed'.",
        "Leverage, margin, liquidation and funding are not modelled; the "
        "venue's contract-step rounding is not modelled either (the chain "
        "verifier measures that separately).",
    ]

    def pine_indicators(self, dataframe, params):
        length = int(params["length"])
        mult = float(params["mult"])
        use_close = bool(params["useClose"])
        close = dataframe["close"]

        # atr = mult * atr(length)
        atr = mult * ta.pine_atr(dataframe, length)
        # (useClose ? highest(close, length) : highest(length))  -- the
        # one-argument form is over high / low.
        highest = ta.pine_highest(close if use_close else dataframe["high"], length)
        lowest = ta.pine_lowest(close if use_close else dataframe["low"], length)
        long_stop_raw = (highest - atr).to_numpy(dtype=float)
        short_stop_raw = (lowest + atr).to_numpy(dtype=float)
        close_values = close.to_numpy(dtype=float)

        count = len(dataframe)
        long_stop = np.full(count, np.nan)
        short_stop = np.full(count, np.nan)
        long_stop_prev = np.full(count, np.nan)
        short_stop_prev = np.full(count, np.nan)
        direction = np.ones(count, dtype=float)

        previous_long = np.nan   # longStop[1]  -- the previous bar's final value
        previous_short = np.nan  # shortStop[1]
        previous_dir = 1.0       # var int dir = 1
        for i in range(count):
            # longStopPrev = nz(longStop[1], longStop)
            prev_long = long_stop_raw[i] if np.isnan(previous_long) else previous_long
            prev_short = short_stop_raw[i] if np.isnan(previous_short) else previous_short
            long_stop_prev[i] = prev_long
            short_stop_prev[i] = prev_short
            close_prev = close_values[i - 1] if i > 0 else np.nan

            # longStop := close[1] > longStopPrev ? max(longStop, longStopPrev) : longStop
            if not np.isnan(close_prev) and not np.isnan(prev_long) and close_prev > prev_long:
                long_stop[i] = np.maximum(long_stop_raw[i], prev_long)
            else:
                long_stop[i] = long_stop_raw[i]
            # shortStop := close[1] < shortStopPrev ? min(shortStop, shortStopPrev) : shortStop
            if not np.isnan(close_prev) and not np.isnan(prev_short) and close_prev < prev_short:
                short_stop[i] = np.minimum(short_stop_raw[i], prev_short)
            else:
                short_stop[i] = short_stop_raw[i]

            # dir := close > shortStopPrev ? 1 : close < longStopPrev ? -1 : dir
            if not np.isnan(prev_short) and close_values[i] > prev_short:
                previous_dir = 1.0
            elif not np.isnan(prev_long) and close_values[i] < prev_long:
                previous_dir = -1.0
            direction[i] = previous_dir

            previous_long = long_stop[i]
            previous_short = short_stop[i]

        # buySignal = dir == 1 and dir[1] == -1
        # sellSignal = dir == -1 and dir[1] == 1
        direction_prev = np.concatenate(([np.nan], direction[:-1]))
        dataframe["pine_long_stop"] = long_stop
        dataframe["pine_short_stop"] = short_stop
        dataframe["pine_long_stop_prev"] = long_stop_prev
        dataframe["pine_short_stop_prev"] = short_stop_prev
        dataframe["pine_dir"] = direction
        dataframe["pine_buy_signal"] = (direction == 1.0) & (direction_prev == -1.0)
        dataframe["pine_sell_signal"] = (direction == -1.0) & (direction_prev == 1.0)
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "buy_signal": dataframe["pine_buy_signal"].to_numpy(),
            "sell_signal": dataframe["pine_sell_signal"].to_numpy(),
        }

    def pine_script(self, broker, i, ctx):
        # if buySignal
        #     strategy.entry("Enter Long", strategy.long)
        # else if sellSignal
        #     strategy.entry("Enter Short", strategy.short)
        if ctx["buy_signal"][i]:
            broker.entry("Enter Long", "long")
        elif ctx["sell_signal"][i]:
            broker.entry("Enter Short", "short")
