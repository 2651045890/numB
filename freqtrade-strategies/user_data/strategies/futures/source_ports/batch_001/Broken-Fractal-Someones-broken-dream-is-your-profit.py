"""Port of sources/SM_fdfcf11b92b19475.pine (batch_001/Broken-Fractal-Someones-broken-dream-is-your-profit.md).

Pine v4. makuchaku's "Broken Fractal" is written as an INDICATOR --
`study("Broken Fractal", overlay=true)`. It tracks the last 5-bar fractal on
either side of the market (`n = 2`, so the pivot sits `n` bars back and the
fractal is only confirmed two bars after that pivot) and remembers the two
pivot levels:

    var fractalCounter = 0
    var highAtDownFractal = 0.0
    var lowAtUpFractal = 0.0

    downFractal = (n == 2 ? (high[n-2] < high[n]) and (high[n-1] < high[n])
                            and (high[n+1] < high[n]) and (high[n+2] < high[n])
                          : (high[1] > high[0]) and (high[1] > high[2]))
    if downFractal
        if fractalCounter > 0
            fractalCounter := 0
        highAtDownFractal := high[n]
        fractalCounter := fractalCounter - 1

    upFractal = (n == 2 ? (low[n-2] > low[n]) and (low[n-1] > low[n])
                          and (low[n+1] > low[n]) and (low[n+2] > low[n])
                        : (low[1] < low[0]) and (low[1] < low[2]))
    if upFractal
        if fractalCounter < 0
            fractalCounter := 0
        lowAtUpFractal := low[n]
        fractalCounter := fractalCounter + 1

    sellSignal = (fractalCounter < 0) and (open > lowAtUpFractal) and (close < lowAtUpFractal)
    buySignal  = (fractalCounter >= 1) and crossover(close, highAtDownFractal)

A converter then appended the order block at the end of the file -- `study()`
cannot host `strategy.entry` in Pine v4, so that block is the whole of the
trading behaviour:

    if buySignal
        strategy.entry("Enter Long", strategy.long)
    else if sellSignal
        strategy.entry("Enter Short", strategy.short)

There is NO exit anywhere in the file -- nothing live and nothing commented out
(the only commented-out calls are the `plotchar` / `bgcolor` / `box.new` /
`line.new` drawing helpers, `//bgcolor(...)`, `//box.new(...)` etc., none of
which is an order) -- so a position is closed only when an opposite entry
reverses it.

FIDELITY:

* `fractalCounter`, `highAtDownFractal` and `lowAtUpFractal` are Pine `var`s:
  they persist across bars and are only assigned inside the `if` block of their
  fractal. The port therefore replays the state bar by bar (it cannot be
  vectorised) and records the post-update value of each level per bar, because
  `crossover(close, highAtDownFractal)` compares this bar's close against THIS
  bar's level and the previous close against the PREVIOUS bar's level.
* The initial values are Pine's literals, not na: `highAtDownFractal = 0.0` and
  `lowAtUpFractal = 0.0`. They matter only until the first fractal of that side
  fires -- a crossover against 0.0 can never be true for a positive price, and
  `close < 0.0` is false.
* The `n == 1` branch is transcribed as written (`(high[1] > high[0]) and
  (high[1] > high[2])`), even though the default is `n = 2`.
* `high[n]` is Pine's history reference: `high.shift(n)`. On the first `n` bars
  it is na, so no fractal can be confirmed there (a comparison against na is
  false).
* Bar 0 has no previous close / level, so `crossover` cannot fire there;
  pine_ta.pine_crossover (had it been usable on a scalar level) and the explicit
  comparison in the port both treat na as false.
* The block is `if buySignal ... else if sellSignal ...`: a bar where both fire
  emits only the LONG entry, and the port keeps that precedence.
* The two drawing inputs `bgColor` / `drawBoxes` and the two signal-flag inputs
  `showBullishSignal` / `showBearishSignal` only gate `bgcolor()` / `box.new()`
  calls, and every one of those calls is commented out in the source. They are
  carried in `source_defaults` for completeness and are read by nothing.
* The conditions are plain booleans -- the source has no `? -1 : 0` shape --
  so PINE_SEMANTICS.md 1.17's "-1 is truthy, never rewrite it as == 1" trap
  does not arise here. Nothing was normalised.
* No `strategy()` call exists anywhere in the file, so every trade property is
  Pine's own default: `default_qty_type` fixed, 1 contract, 1000000 initial
  capital, 0% commission, pyramiding 0, `process_orders_on_close` false.
* `/*backtest` declares `period: 1h` on Futures_Binance BTC_USDT, so timeframe
  is "1h"; `basePeriod: 15m` is the FMZ backtester's fill granularity.
* Leverage, margin, liquidation, funding and the venue's contract-step rounding
  are not modelled.
"""
import numpy as np

from freqtrade.strategy import IStrategy

from pine_port_base import PinePortBase


class SMBrokenFractal_fdfcf1(PinePortBase, IStrategy):
    source_id = "SM_fdfcf11b92b19475"
    source_file = "Broken-Fractal-Someones-broken-dream-is-your-profit.md"
    timeframe = "1h"
    can_short = True
    # Pine evaluates the script from the first bar of the window; the fractal
    # window warms up on its own (with n = 2 the first confirmable fractal is
    # bar 4) and no signal can fire before that.
    startup_candle_count = 0
    source_defaults: dict = {
        # input(title="n==1 or 2", defval=2, type=input.integer)
        "n": 2,
        # The four below only gate commented-out drawing calls; they reach no
        # order and are never read by this port.
        "bgColor": False,
        "drawBoxes": True,
        "showBullishSignal": True,
        "showBearishSignal": True,
    }
    # `study()` is not a strategy declaration and the file has no strategy()
    # call, so Pine's documented defaults apply.
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    # No exit of any kind exists in the source.
    source_reproduce_stops = False
    source_mintick = 0.1
    source_fidelity_notes = [
        "Converter-appended order block: the file declares the indicator "
        "`study(\"Broken Fractal\", overlay=true)` (Pine v4) and the appended "
        "block is `if buySignal -> strategy.entry(\"Enter Long\", long)` / "
        "`else if sellSignal -> strategy.entry(\"Enter Short\", short)`. That "
        "block is the whole trading behaviour; the indicator's own intent (the "
        "author's md text talks about trading 'in the same direction' as the "
        "trapped traders) is not what the appended block does and is not "
        "reproduced over it.",
        "NO exit exists in this source -- neither called nor commented out. "
        "`source_reproduce_stops` is False, and a position is closed only by an "
        "opposite entry reversing it (Pine nets an opposing entry against the "
        "open position).",
        "`fractalCounter` / `highAtDownFractal` / `lowAtUpFractal` are Pine "
        "`var`s that persist across bars and are assigned only inside the `if` "
        "of the matching fractal. The port replays them bar by bar and stores "
        "the post-update level per bar, which is what `crossover(close, "
        "highAtDownFractal)` reads: this bar's close against this bar's level, "
        "and last bar's close against last bar's level.",
        "The `var` seeds are literals (0 / 0.0 / 0.0), not na. A crossover "
        "against 0.0 is false for a positive price and `close < 0.0` is false, "
        "so the seeds cannot manufacture a signal before the first fractal.",
        "The `n == 1` ternary branch is transcribed as written even though the "
        "input default is 2.",
        "`bgColor` / `drawBoxes` / `showBullishSignal` / `showBearishSignal` "
        "are carried in source_defaults for completeness; every `bgcolor()` / "
        "`box.new()` call they gate is commented out in the source, so they are "
        "read by nothing.",
        "The signals are plain booleans -- this source has no `? -1 : 0` "
        "shape -- so PINE_SEMANTICS.md 1.17's minus-truthiness trap does not "
        "arise, and nothing was rewritten into `== 1` / `> 0`.",
        "`if buySignal ... else if sellSignal` means a bar where both hold "
        "emits only the long entry; that precedence is preserved.",
        "No strategy() call exists, so all trade properties are Pine's "
        "documented defaults, including default_qty_value = 1 CONTRACT (fixed).",
        "`plotchar` / `bgcolor` / `box.new` / `line.new` are display only and "
        "are not reproduced.",
        "Venue contract-step rounding, leverage, margin, liquidation and "
        "funding are not modelled.",
    ]

    def pine_indicators(self, dataframe, params):
        n = int(params["n"])
        open_ = dataframe["open"]
        high = dataframe["high"]
        low = dataframe["low"]
        close = dataframe["close"]

        # Pine `high[n]` / `low[n]`: the series n bars back.
        def shift(series, count):
            return series.shift(int(count))

        high_n = shift(high, n)
        low_n = shift(low, n)

        # downFractal = (n == 2 ? (high[n-2] < high[n]) and (high[n-1] < high[n])
        #                        and (high[n+1] < high[n]) and (high[n+2] < high[n])
        #                      : (high[1] > high[0]) and (high[1] > high[2]))
        if n == 2:
            down_fractal = (
                (shift(high, n - 2) < high_n)
                & (shift(high, n - 1) < high_n)
                & (shift(high, n + 1) < high_n)
                & (shift(high, n + 2) < high_n)
            )
            # upFractal = (n == 2 ? (low[n-2] > low[n]) and (low[n-1] > low[n])
            #                       and (low[n+1] > low[n]) and (low[n+2] > low[n])
            #                     : (low[1] < low[0]) and (low[1] < low[2]))
            up_fractal = (
                (shift(low, n - 2) > low_n)
                & (shift(low, n - 1) > low_n)
                & (shift(low, n + 1) > low_n)
                & (shift(low, n + 2) > low_n)
            )
        else:
            down_fractal = (shift(high, 1) > shift(high, 0)) & (
                shift(high, 1) > shift(high, 2)
            )
            up_fractal = (shift(low, 1) < shift(low, 0)) & (
                shift(low, 1) < shift(low, 2)
            )

        down = down_fractal.to_numpy(dtype=bool)
        up = up_fractal.to_numpy(dtype=bool)
        pivot_high = high_n.to_numpy(dtype=float)
        pivot_low = low_n.to_numpy(dtype=float)
        opens = open_.to_numpy(dtype=float)
        closes = close.to_numpy(dtype=float)

        size = len(dataframe)
        # var fractalCounter = 0 / var highAtDownFractal = 0.0 / var lowAtUpFractal = 0.0
        fractal_counter = 0
        high_at_down_fractal = 0.0
        low_at_up_fractal = 0.0
        level_down = np.full(size, 0.0)
        level_up = np.full(size, 0.0)
        counter_series = np.zeros(size, dtype=float)
        buy_signal = np.zeros(size, dtype=bool)
        sell_signal = np.zeros(size, dtype=bool)

        for i in range(size):
            # if downFractal
            #     if fractalCounter > 0
            #         fractalCounter := 0
            #     highAtDownFractal := high[n]
            #     fractalCounter := fractalCounter - 1
            if down[i]:
                if fractal_counter > 0:
                    fractal_counter = 0
                high_at_down_fractal = pivot_high[i]
                fractal_counter = fractal_counter - 1
            # if upFractal
            #     if fractalCounter < 0
            #         fractalCounter := 0
            #     lowAtUpFractal := low[n]
            #     fractalCounter := fractalCounter + 1
            if up[i]:
                if fractal_counter < 0:
                    fractal_counter = 0
                low_at_up_fractal = pivot_low[i]
                fractal_counter = fractal_counter + 1
            # The levels are only meaningful from here on: the signals below
            # read this bar's value and the previous bar's value.
            level_down[i] = high_at_down_fractal
            level_up[i] = low_at_up_fractal
            counter_series[i] = float(fractal_counter)

            # sellSignal = (fractalCounter < 0) and (open > lowAtUpFractal)
            #              and (close < lowAtUpFractal)
            sell_signal[i] = bool(
                fractal_counter < 0
                and opens[i] > low_at_up_fractal
                and closes[i] < low_at_up_fractal
            )
            # buySignal = (fractalCounter >= 1) and crossover(close, highAtDownFractal)
            # crossover(a, b) = a > b and a[1] <= b[1]; bar 0 has no history.
            cross = False
            if i > 0:
                cross = closes[i] > high_at_down_fractal and closes[i - 1] <= level_down[i - 1]
            buy_signal[i] = bool(fractal_counter >= 1 and cross)

        dataframe["pine_fractal_counter"] = counter_series
        dataframe["pine_high_at_down_fractal"] = level_down
        dataframe["pine_low_at_up_fractal"] = level_up
        dataframe["pine_buy_signal"] = buy_signal
        dataframe["pine_sell_signal"] = sell_signal
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
