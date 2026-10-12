"""Port of sources/SM_9301a1bc2183841d.pine (batch_001/ChandelierExit-EMA动态止损趋势跟踪策略-ChandelierExit-EMA-Dynamic-Stop-Loss-Trend-Following-Strategy.md).

Pine v5 (everget's Chandelier Exit with a 200-EMA filter):

    length = 22          mult = 3.0        useClose = true
    atr    = mult * ta.atr(length)
    ema200 = ta.ema(close, 200)

    longStop  = (useClose ? ta.highest(close, length) : ta.highest(length)) - atr
    longStopPrev = nz(longStop[1], longStop)
    longStop  := close[1] > longStopPrev ? math.max(longStop, longStopPrev) : longStop

    shortStop = (useClose ? ta.lowest(close, length) : ta.lowest(length)) + atr
    shortStopPrev = nz(shortStop[1], shortStop)
    shortStop := close[1] < shortStopPrev ? math.min(shortStop, shortStopPrev) : shortStop

    var int dir = 1
    dir := close > shortStopPrev ? 1 : close < longStopPrev ? -1 : dir

    buySignal  = dir == 1  and dir[1] == -1
    sellSignal = dir == -1 and dir[1] == 1
    await = awaitBarConfirmation ? barstate.isconfirmed : true

    if (buySignal and await and close > ema200) -> entry("Long",  long,  stop = low  - atr*0.5)
    if (sellSignal and await and close < ema200) -> entry("Short", short, stop = high + atr*0.5)
    if (sellSignal and await) -> strategy.close("Long")
    if (buySignal  and await) -> strategy.close("Short")

`longStop`/`shortStop`/`dir` are recursive on their own previous bar (each bar
reassigns with `:=`, `dir` is `var`-initialised to 1), so they are computed in
one forward pass in `pine_indicators`; nothing vectorised replaces them.

`strategy()` declares only `title`/`shorttitle`/`overlay`, so Pine's documented
defaults apply and the port carries them explicitly: `strategy.fixed` / 1
contract, initial capital 1000000, commission 0%, pyramiding 0,
process_orders_on_close=false.

The `/*backtest` header declares `period: 1d` on Futures_Binance BTC_USDT, so
`timeframe` is "1d"; its `basePeriod: 1h` is the FMZ backtester's own
granularity for filling those daily bars, not the strategy's period.

FIDELITY (the full list is in `source_fidelity_notes` below):

* BOTH entries carry a `stop=` leg, i.e. they are RESTING stop orders, not
  market orders -- and in both cases the level is already on the wrong side of
  the market (for a long, `low - 1.5*ATR` is below the close; for a short,
  `high + 1.5*ATR` is above it), so the order is immediately triggered. The
  engine models that: `_price_order_fill` fills at `max(stop, open)` /
  `min(stop, open)`, which is the next bar's OPEN in every case except a bar
  that gaps entirely past the level. Freqtrade's interface has no
  resting-entry expression, so the projection is a next-open market order --
  the same fill, except on such a gap. PINE_SEMANTICS.md section 二.11.
* `awaitBarConfirmation` defaults to true, so `await = barstate.isconfirmed`.
  The engine evaluates the script once per CLOSED bar, where
  `barstate.isconfirmed` is true, so `await` is reproduced as a constant true.
  With the input set false the source yields true as well, so the branch does
  not change historical behaviour. No `barstate` handling is added.
* There is no `strategy.exit`, so no stop-based EXIT exists to mirror and
  `source_reproduce_stops` is False; the two `strategy.close` calls are market
  closes projected as next-open signals, and the `stop=` legs above belong to
  the ENTRY orders, which the engine handles itself.
* `ta.atr` seeds one bar earlier here than on the platform: Pine's `ta.tr`
  defaults to `handle_na = false` (first bar na), while `pine_ta.pine_atr`
  uses `pine_tr(handle_na=True)` (first bar high-low). PINE_SEMANTICS.md 3.7
  records this as an unfixed public-layer boundary; the ATR is load-bearing
  here (both stop levels and both entry stops), so the warmup offset is
  recorded rather than corrected.
* md prose disagreement: the prose says "每笔交易风险控制在账户权益的10%"
  (risk per trade capped at 10% of equity) and describes the ATR 0.5x level as
  the initial stop. The code sizes every order from Pine's default_qty
  (fixed / 1 contract) and never computes an equity-percentage risk; the
  `stop=` leg is an entry trigger, not a protective exit. The code is followed.
* `showLabels` / `highlightState` drive `label`/`barcolor` drawing only, and
  the md's "Risk" prose is not code; neither places a condition.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


class SMChandelierExitEmaDynamicStopLossTrendFollowing_9301a1(PinePortBase, IStrategy):
    source_id = "SM_9301a1bc2183841d"
    source_file = (
        "ChandelierExit-EMA动态止损趋势跟踪策略"
        "ChandelierExit-EMA-Dynamic-Stop-Loss-Trend-Following-Strategy.md"
    )
    timeframe = "1d"
    can_short = True
    source_defaults: dict = {
        "length": 22,
        "mult": 3.0,
        "useClose": True,
        "showLabels": True,
        "highlightState": True,
        "awaitBarConfirmation": True,
    }
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    # No strategy.exit anywhere: the only stop= arguments belong to the ENTRY
    # orders (resting entry triggers), and both exits are market closes. There
    # is therefore no intrabar exit level for custom_stoploss to mirror.
    source_reproduce_stops = False
    source_fidelity_notes = [
        "Both entries are RESTING STOP orders (`strategy.entry(..., stop=...)`), "
        "and in both directions the level is already on the wrong side of the "
        "market, so the order triggers at once. The engine models the stop-entry "
        "fill as max(stop, open) for a long and min(stop, open) for a short, i.e. "
        "the next bar's open except when a bar gaps entirely past the level; "
        "Freqtrade's strategy interface has no resting-entry expression, so the "
        "projected entry is a next-open market order. Divergence is possible only "
        "on such a gap. PINE_SEMANTICS.md section two.11.",
        "`awaitBarConfirmation` is true by default, hence await = "
        "barstate.isconfirmed; the engine evaluates the script once per closed "
        "bar, where that is true, so `await` is reproduced as the constant true. "
        "Setting the input false also yields true, so the reproduced historical "
        "behaviour is the same either way.",
        "No strategy.exit and no stop/limit/trail exit leg exists, so there is no "
        "stop-based exit for the engine to mirror and source_reproduce_stops is "
        "False; both exits are `strategy.close`, projected as next-open market "
        "exits.",
        "ta.atr is seeded one bar earlier than the platform's: Pine's ta.tr "
        "defaults to handle_na=false (first bar na) while pine_ta.pine_atr uses "
        "pine_tr(handle_na=True) (first bar high-low), so the rma seed shifts by "
        "one bar and the whole ATR series carries that offset before converging. "
        "PINE_SEMANTICS.md 3.7 records this as an unfixed public-layer boundary; "
        "ATR is load-bearing here (both stop levels and both entry stop prices), "
        "so the offset is recorded rather than corrected.",
        "`longStop`/`shortStop`/`dir` are recursive: each bar reassigns them with "
        "`:=` off their own previous value and `dir` is `var`-initialised to 1. "
        "They are computed in a single forward pass, not replaced by a vectorised "
        "equivalent.",
        "`nz(longStop[1], longStop)` replaces the na of the FIRST bar with the "
        "current bar's own raw value, which is what the pass below does; the na "
        "window then propagates until ta.highest/ta.lowest have `length` bars.",
        "`close[1] > longStopPrev` and the other na comparisons are false when "
        "either side is na, which is Pine's behaviour and is reproduced by plain "
        "comparisons.",
        "ta.ema uses pine_ta's documented first-value seeding (PINE_SEMANTICS.md "
        "3.1 lists ta.ema seeding as a parity risk). The 200-EMA is na-free from "
        "the model's first bar, unlike a SMA-seeded implementation which would "
        "report na for the first 199.",
        "md prose disagreement: the prose claims risk per trade is capped at 10% "
        "of account equity and calls the ATR*0.5 level the initial stop. The code "
        "never computes an equity-percentage risk (every order comes from Pine's "
        "default_qty_type/default_qty_value, i.e. fixed 1) and its `stop=` is an "
        "ENTRY trigger, not a protective exit. Code followed, prose recorded.",
        "showLabels / highlightState drive label and barcolor drawing only; they "
        "place no condition and are carried in source_defaults but never read.",
        "Leverage, margin, liquidation, funding and the venue's contract-step "
        "rounding are not modelled; the rounding can differ from the engine's "
        "float quantity, which the chain verifier measures separately.",
    ]

    def pine_indicators(self, dataframe, params):
        close = dataframe["close"].astype(float)
        high = dataframe["high"].astype(float)
        low = dataframe["low"].astype(float)
        length = int(params["length"])
        mult = float(params["mult"])
        use_close = bool(params["useClose"])

        # atr = mult * ta.atr(length)  (the SCALED atr, used for stops too)
        atr = mult * ta.pine_atr(dataframe, length)
        ema200 = ta.pine_ema(close, 200)

        # longStop  = (useClose ? ta.highest(close, length) : ta.highest(length)) - atr
        # shortStop = (useClose ? ta.lowest(close, length)  : ta.lowest(length))  + atr
        # ta.highest(length) / ta.lowest(length) default to the bar's high / low.
        long_extreme = ta.pine_highest(close, length) if use_close else ta.pine_highest(high, length)
        short_extreme = ta.pine_lowest(close, length) if use_close else ta.pine_lowest(low, length)
        long_stop_raw = long_extreme - atr
        short_stop_raw = short_extreme + atr

        close_values = close.to_numpy(dtype=float)
        raw_long = long_stop_raw.to_numpy(dtype=float)
        raw_short = short_stop_raw.to_numpy(dtype=float)
        previous_close = np.concatenate(([np.nan], close_values[:-1]))

        bars = len(dataframe)
        long_stop = np.full(bars, np.nan)
        short_stop = np.full(bars, np.nan)
        direction = np.ones(bars, dtype=float)

        for t in range(bars):
            # longStopPrev = nz(longStop[1], longStop)
            if t > 0 and np.isfinite(long_stop[t - 1]):
                long_prev = long_stop[t - 1]
            else:
                long_prev = raw_long[t]
            # longStop := close[1] > longStopPrev ? max(longStop, longStopPrev) : longStop
            if previous_close[t] > long_prev:
                long_stop[t] = np.maximum(raw_long[t], long_prev)
            else:
                long_stop[t] = raw_long[t]

            # shortStopPrev = nz(shortStop[1], shortStop)
            if t > 0 and np.isfinite(short_stop[t - 1]):
                short_prev = short_stop[t - 1]
            else:
                short_prev = raw_short[t]
            # shortStop := close[1] < shortStopPrev ? min(shortStop, shortStopPrev) : shortStop
            if previous_close[t] < short_prev:
                short_stop[t] = np.minimum(raw_short[t], short_prev)
            else:
                short_stop[t] = raw_short[t]

            # dir := close > shortStopPrev ? 1 : close < longStopPrev ? -1 : dir
            if close_values[t] > short_prev:
                direction[t] = 1.0
            elif close_values[t] < long_prev:
                direction[t] = -1.0
            elif t > 0:
                direction[t] = direction[t - 1]
            # else: `var int dir = 1`, the initial value.

        previous_direction = np.concatenate(([np.nan], direction[:-1]))
        buy_signal = (direction == 1.0) & (previous_direction == -1.0)
        sell_signal = (direction == -1.0) & (previous_direction == 1.0)

        dataframe["pine_atr"] = atr
        dataframe["pine_ema200"] = ema200
        dataframe["pine_long_stop"] = long_stop
        dataframe["pine_short_stop"] = short_stop
        dataframe["pine_dir"] = direction
        dataframe["pine_buy_signal"] = buy_signal
        dataframe["pine_sell_signal"] = sell_signal
        # stop = low - atr*0.5 for the long entry, high + atr*0.5 for the short.
        dataframe["pine_long_entry_stop"] = low.to_numpy(dtype=float) - atr.to_numpy(dtype=float) * 0.5
        dataframe["pine_short_entry_stop"] = high.to_numpy(dtype=float) + atr.to_numpy(dtype=float) * 0.5
        dataframe["pine_close_long"] = sell_signal
        dataframe["pine_close_short"] = buy_signal
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "buy_signal": dataframe["pine_buy_signal"].to_numpy(),
            "sell_signal": dataframe["pine_sell_signal"].to_numpy(),
            "close": dataframe["close"].to_numpy(dtype=float),
            "ema200": dataframe["pine_ema200"].to_numpy(dtype=float),
            "long_entry_stop": dataframe["pine_long_entry_stop"].to_numpy(dtype=float),
            "short_entry_stop": dataframe["pine_short_entry_stop"].to_numpy(dtype=float),
        }

    def pine_script(self, broker, i, ctx):
        # await = awaitBarConfirmation ? barstate.isconfirmed : true, evaluated on
        # a closed bar, is true.
        buy_signal = bool(ctx["buy_signal"][i])
        sell_signal = bool(ctx["sell_signal"][i])

        # if (buySignal and await and close > ema200)
        #     strategy.entry("Long", strategy.long, stop = low - atr * 0.5)
        if buy_signal and ctx["close"][i] > ctx["ema200"][i]:
            broker.entry("Long", "long", stop=float(ctx["long_entry_stop"][i]))
        # if (sellSignal and await and close < ema200)
        #     strategy.entry("Short", strategy.short, stop = high + atr * 0.5)
        if sell_signal and ctx["close"][i] < ctx["ema200"][i]:
            broker.entry("Short", "short", stop=float(ctx["short_entry_stop"][i]))
        # if (sellSignal and await) -> strategy.close("Long")
        broker.close("Long", when=sell_signal)
        # if (buySignal and await) -> strategy.close("Short")
        broker.close("Short", when=buy_signal)
