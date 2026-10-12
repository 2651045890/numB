"""Port of sources/SM_dd03873fb06d28c8.pine (batch_001/Fibonacci-Progression-With-Breaks.md).

Pine v5 (`//@version=5`), and the file declares an INDICATOR, not a
`strategy(...)`: the two `strategy.entry` calls at the bottom are an order
block APPENDED to the indicator by the converter site that published it
(fmz.com/strategy/363749, named in the md's Detail link). Pine v5 does not
compile `strategy.entry` inside `indicator()`, so the "original strategy" is the
indicator PLUS that appended block, and the trading behaviour it defines is
entry-only.

The indicator walks a central level `avg` and a Fibonacci-scaled distance
`dist`; a bar whose close deviates from `avg` by more than `dist` advances the
Fibonacci multiplier, and a deviation past the end of the sequence resets the
central level onto the close:

    var fib = array.from(1, 1)                    # extended on barstate.isfirst
    if barstate.isfirst
        for i = 1 to max                          # max = "Sequence Length"
            array.push(fib, array.get(fib, i-1) + array.get(fib, i))
    # per bar, in this order:
    dist  := method == 'Atr' ? ta.atr(200)*size*array.get(fib, fib_n)
                             : size*array.get(fib, fib_n)
    fib_n := math.abs(src-avg) > dist ? fib_n+1 : fib_n
    avg   := nz(fib_n > max+1 ? src : avg[1], src)
    fib_n := fib_n > max+1 ? 1 : fib_n

    buy  = avg > avg[1]
    sell = avg < avg[1]
    os  := buy ? 1 : sell ? 0 : os

    if buy
        strategy.entry("Enter Long", strategy.long)
    else if sell
        strategy.entry("Enter Short", strategy.short)

The appended block reads ONLY `buy` / `sell`, i.e. "the central level rose /
fell this bar". The bands the indicator also computes -- `tp` / `sl` (upper and
lower extremities of the central level, `avg +/- dist`) -- are fed to
`plot(tp, 'Target', ...)` and `plot(sl, 'Stop', ...)` ONLY. They are labelled
Target/Stop but they are not orders: there is no `strategy.exit`, no
`strategy.close` and no commented-out one anywhere in the file. So the strategy
has NO exits and `source_reproduce_stops` is False; a position is only ever
left by the opposite entry, which the engine models as a reverse fill.

`indicator(...)` carries no strategy() properties, so Pine's documented
defaults apply: `default_qty_type` fixed, `default_qty_value` 1, commission 0%,
`pyramiding` 0, `initial_capital` 1000000 USD.

FIDELITY:

* Converter-appended source (PINE_SEMANTICS.md 1.17). Neither `buy` nor `sell`
  has the `? -1 : 0` shape -- both are plain boolean comparisons -- so the
  "-1 is truthy, never rewrite it as == 1" trap does not arise here. The `if /
  else if` is kept as if/elif; `buy` and `sell` cannot both hold on one bar
  (`avg > avg[1]` and `avg < avg[1]` are exclusive), so the ordering is not
  load-bearing for the fills, only for faithfulness.
* `fib` is a `var` array built once on `barstate.isfirst`: for max=3 it becomes
  [1, 1, 2, 3, 5], and `array.get(fib, fib_n)` indexes it with the running
  multiplier. The port builds the identical list up front.
* The indicator is inherently path-dependent (`var dist/avg/fib_n/os` mutated
  with `:=` in a fixed order, `avg[1]` read back), so it is evaluated in a
  bar-by-bar Python loop, not as a rolling window. The ORDER of the four
  statements is preserved exactly: `dist` is computed with the multiplier from
  the PREVIOUS bar's end, the increment is applied before `avg` is updated, and
  the reset to 1 happens after `avg`, which is why a break bar takes `src` into
  `avg` and only then restarts the sequence.
* `avg[1]` is the previous bar's final `avg`, na on bar 0 (no history exists
  before the first bar, even though the `var` was initialised to 0). `nz(...,
  src)` therefore puts the close into `avg` on that bar, and `buy`/`sell` are
  false there because a comparison against na is false in Pine -- which is also
  what a NaN comparison does in numpy.
* `ta.atr(200)` is na until its Wilder warm-up completes (pine_ta.pine_atr,
  seeding recorded as a parity risk in PINE_SEMANTICS.md 3.1/3.2/3.7). With
  `method = 'Atr'` (the default) `dist` is na over that warm-up, and
  `math.abs(src-avg) > na` is na, which Pine treats as FALSE in a conditional:
  the multiplier does NOT advance during the warm-up, and the port reproduces
  that (a NaN comparison is false). Only the ATR's seasoning is affected -- the
  multiplier, `avg` and the signals all behave from bar 0 under `method =
  'Manual'`.
* `plot`, `plotshape`, `fill`, the `css` colour, `n = bar_index`, `os` and
  `tp`/`sl` are display-only and place no order; they are dropped. `os` is kept
  out of the port entirely because nothing in the trading path reads it -- note
  that `os` is a 1/0 series, not the `-1`/0 shape of 1.17 either.
* The `/*backtest` header declares period 5m on Futures_Binance BTC_USDT; its
  `basePeriod: 1m` is the host's intrabar granularity for filling 5m bars, not
  the strategy's period. The header's window (2022-04-10 to 2022-05-07) is
  extraction metadata, not an `input.time` filter, so no data is trimmed.
* `max` is an input name that shadows Pine's `max()` builtin; the source only
  calls `math.abs` / `math.max`-free code after it, so no shadowing semantic is
  involved. The port keeps the name for traceability.
* Leverage, margin, liquidation, funding and the venue's contract-step rounding
  are not modelled (PINE_SEMANTICS.md 1.6 measures the rounding separately).
"""
import numpy as np
import pandas as pd
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


def _fib_sequence(max_length):
    """`var fib = array.from(1,1)` extended on barstate.isfirst by `max` pushes.

    `array.push(fib, array.get(fib, i-1) + array.get(fib, i))` reads the array
    as it is being extended, so index i already exists when it is read.
    """
    fib = [1, 1]
    for i in range(1, int(max_length) + 1):
        fib.append(fib[i - 1] + fib[i])
    return fib


class SMFibonacciProgressionWithBreaks_dd0387(PinePortBase, IStrategy):
    source_id = "SM_dd03873fb06d28c8"
    source_file = "Fibonacci-Progression-With-Breaks.md"
    timeframe = "5m"
    can_short = True
    source_defaults: dict = {"method": "Atr", "size": 1.0, "max": 3}
    # indicator(...), not strategy(...): Pine's documented defaults apply.
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    # The source's `tp` / `sl` series are plot-only despite their names, and
    # there is no strategy.exit / strategy.close anywhere in the file.
    source_reproduce_stops = False
    source_mintick = 0.1
    source_fidelity_notes = [
        "Converter-appended order block (PINE_SEMANTICS.md 1.17): the file declares "
        "indicator(), and the two strategy.entry calls at the end are an appended "
        "block added by the publishing host (fmz.com/strategy/363749). It does not "
        "compile on TradingView; the host's Pine dialect is the behaviour reproduced "
        "here.",
        "Neither appended condition has the `? -1 : 0` shape of 1.17 -- `buy` and "
        "`sell` are plain boolean comparisons -- so no integer truthiness needed "
        "preserving and nothing was rewritten as `== 1`. `if / else if` is kept as "
        "if/elif; the two conditions are mutually exclusive, so it changes no fill.",
        "The central level `avg`, the multiplier `fib_n` and the distance `dist` are "
        "`var` state mutated with `:=` in a fixed order, so the indicator is "
        "evaluated bar by bar in a Python loop. The four statements of the source's "
        "per-bar block keep their exact order: the multiplier is incremented before "
        "`avg` is updated, and it is reset to 1 only after `avg` has taken `src`.",
        "`avg[1]` is the previous bar's final `avg` and is na on bar 0 (there is no "
        "history before the first bar even though the `var` was initialised to 0); "
        "`nz(..., src)` therefore seeds `avg` with the close on bar 0, exactly as the "
        "source does.",
        "`math.abs(src-avg) > na` is na and Pine treats an na condition as FALSE, so "
        "the Fibonacci multiplier does not advance while `ta.atr(200)` is still in "
        "its warm-up (the default `method` is 'Atr'). The port reproduces that with a "
        "NaN comparison, which is also false. With method='Manual' the warm-up does "
        "not apply.",
        "ta.atr's Wilder seeding is pine_ta's documented model, a parity risk listed "
        "in PINE_SEMANTICS.md 3.1/3.2/3.7 (ta.tr's first bar differs by one bar).",
        "`tp` and `sl` are named Target/Stop but are only `plot(...)`ed: no "
        "strategy.exit, strategy.close or stop/limit order reads them, and no "
        "commented-out exit line exists in the file. source_reproduce_stops is False "
        "and a position is left only by the opposite entry.",
        "`os := buy ? 1 : sell ? 0 : os`, `css`, both plotshape calls, the fill and "
        "`n = bar_index` are display-only; `os` is not carried into the port because "
        "nothing in the trading path reads it (and it is a 1/0 series, not 1.17's "
        "-1/0 shape).",
        "The `/*backtest` header's period 5m is the strategy timeframe; its "
        "basePeriod: 1m is the host's intrabar granularity and its date window is "
        "extraction metadata, not an input.time filter, so no data is trimmed.",
        "Leverage, margin, liquidation, funding and the venue's contract-step "
        "rounding are not modelled (PINE_SEMANTICS.md 1.6 measures the rounding "
        "separately).",
    ]

    def pine_indicators(self, dataframe, params):
        close = dataframe["close"].to_numpy(dtype=float)
        size = float(params["size"])
        sequence_length = int(params["max"])
        atr = ta.pine_atr(dataframe, 200).to_numpy(dtype=float)
        fib = _fib_sequence(sequence_length)

        count = len(close)
        central = np.full(count, np.nan)
        # `var dist = 0., var avg = 0., var fib_n = 1, var os = 0`
        avg = 0.0
        fib_n = 1
        for t in range(count):
            source = close[t]
            if str(params["method"]) == "Atr":
                dist = atr[t] * size * fib[fib_n]
            else:
                dist = size * fib[fib_n]
            # Pine: an na comparison is false, so the multiplier is unchanged
            # while the ATR is still na.
            if abs(source - avg) > dist:
                fib_n = fib_n + 1
            previous = central[t - 1] if t >= 1 else np.nan
            if fib_n > sequence_length + 1:
                avg = source
            elif np.isnan(previous):
                # nz(..., src): the ternary yielded na, nz replaces it with src.
                avg = source
            else:
                avg = previous
            if fib_n > sequence_length + 1:
                fib_n = 1
            central[t] = avg

        central = pd.Series(central, index=dataframe.index, dtype=float)
        buy = (central > central.shift(1)).fillna(False)
        sell = (central < central.shift(1)).fillna(False)
        dataframe["pine_central_level"] = central
        dataframe["pine_long_condition"] = buy
        dataframe["pine_short_condition"] = sell
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "long_condition": dataframe["pine_long_condition"].to_numpy(),
            "short_condition": dataframe["pine_short_condition"].to_numpy(),
        }

    def pine_script(self, broker, i, ctx):
        # if buy
        #     strategy.entry("Enter Long", strategy.long)
        # else if sell
        #     strategy.entry("Enter Short", strategy.short)
        if ctx["long_condition"][i]:
            broker.entry("Enter Long", "long")
        elif ctx["short_condition"][i]:
            broker.entry("Enter Short", "short")
