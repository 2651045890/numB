"""Port of sources/SM_1f17677b8658e8cb.pine (batch_001/G-Channel与EMA结合的趋势跟踪策略G-Channel-and-EMA-Trend-Following-Strategy.md).

Pine v4. Guppy's G-Channel (a recursive ratchet, not a rolling high/low) with a
9-EMA filter, long only:

    length = input(100)
    src    = input(close)

    a = 0.0
    b = 0.0
    a := max(src, nz(a[1])) - nz(a[1] - b[1]) / length
    b := min(src, nz(b[1])) + nz(a[1] - b[1]) / length
    avg = avg(a, b)

    emaLength = input(9, title="EMA Length")
    ema = ema(close, emaLength)

    crossup = b[1] < close[1] and b > close
    crossdn = a[1] < close[1] and a > close
    bullish = barssince(crossdn) <= barssince(crossup)

    buySignal  = bullish and close < ema
    sellSignal = not bullish and close > ema

    strategy.entry("Buy", strategy.long, when=buySignal)
    strategy.close("Buy", when=sellSignal)

`a` and `b` are stateful: each bar's value depends on the PREVIOUS bar's two
values, so they are computed in a single forward pass, exactly as written --
`nz()` is applied to each lag (a lag of na becomes 0) rather than the recursion
being seeded with an SMA or a rolling extreme.

`strategy()` declares only `title`, `shorttitle` and `overlay`, so Pine's
documented defaults apply: `default_qty_type = strategy.fixed`,
`default_qty_value = 1`, `commission_value = 0`, `pyramiding = 0`, initial
capital 1000000 and `process_orders_on_close = false`. The `/*backtest` header
declares `period: 1d` on Futures_Binance BTC_USDT, so `timeframe` is "1d"; its
`basePeriod: 1h` is the FMZ backtester's own granularity for filling those
daily bars, not the strategy's period.

FIDELITY:

* The source is LONG ONLY. There is no `strategy.entry` with
  `strategy.short`, so `can_short` is False; the "SELL" labels on the chart
  mark `sellSignal`, which only closes the long.
* The md describes the G-Channel as "上轨连接近期价格的最高点,下轨连接近期价格的最低点"
  and the trend as "收盘价向上突破上轨" / "向下突破下轨". The source computes a
  RECURSIVE ratchet instead -- `a := max(src, a[1]) - (a[1]-b[1])/length` and
  the mirror for `b` -- and `crossdn` is `a[1] < close[1] and a > close`, i.e.
  the close crossing DOWN through the upper band, not up through it. The source
  wins on both counts; recorded, not corrected.
* `bullish = barssince(crossdn) <= barssince(crossup)` makes the state named
  "bullish" true when the DOWN-cross (`crossdn`) is the more recent of the two,
  i.e. the name reads the opposite way round from the md's trend description.
  The expression is transcribed as written and is not renamed or flipped.
* `barssince` is na until its condition has occurred at least once (0 on the bar
  it occurs). `bullish` is therefore na over the leading window, and Pine treats
  that na as falsy in `and` / `not`. The port evaluates the comparison in
  float64, where a na operand yields False, which gives the same truth value for
  `buySignal`. For `sellSignal` the two readings (`not na` = na vs. `not na` =
  true) can differ, but ONLY on bars where `bullish` is na -- that is, before
  either cross has ever occurred -- and no position can exist on those bars,
  because entering requires `bullish` to have been true. `strategy.close` on a
  flat book is a no-op in both the engine and the projection, so the choice is
  invisible in the order stream. Recorded because it is a modelling choice, not
  a derivation.
* `avg = avg(a, b)` is computed by the source and used only by `plot(avg, ...)`;
  it is not carried, since it reaches no decision.
* `ema` is Pine's builtin. Pine does not publish its seeding rule; `pine_ta`
  seeds with the first observation and does not advance the recursion on na
  (PINE_SEMANTICS §3.1). It is not swapped for a library EMA.
* `src = input(close)` is carried as a parameter (`"src": "close"`) and resolved
  through `pine_ta.pine_source`, so the channel's input series stays selectable
  and defaults to close as the source does. The frame's price series carries no
  na, which the `max` / `min` in the recursion rely on (Pine would propagate a
  na `src`).
* `plot`, `plotshape`, `location`, the label text and colours are display-only
  and are not reproduced.
* `strategy.entry(..., when=buySignal)` is a plain market entry; a repeated
  signal while already long is refused by Pine's `pyramiding` default of 0,
  which `pine_engine` reproduces by blocking same-direction stacking.
* Contract-step rounding, leverage, margin, liquidation and funding are not
  modelled (PINE_SEMANTICS §1.6, §二-4).
"""
import numpy as np
import pandas as pd

from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


class SMGChannelEmaTrendFollowing_1f1767(PinePortBase, IStrategy):
    source_id = "SM_1f17677b8658e8cb"
    source_file = "G-Channel与EMA结合的趋势跟踪策略G-Channel-and-EMA-Trend-Following-Strategy.md"
    timeframe = "1d"
    can_short = False
    source_defaults: dict = {"length": 100, "src": "close", "emaLength": 9}
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    source_reproduce_stops = False
    source_fidelity_notes = [
        "The source is long only -- there is no strategy.entry with "
        "strategy.short -- so can_short is False; the SELL labels on the chart "
        "mark sellSignal, which only closes the long.",
        "The md describes a rolling highest/rolling lowest G-Channel and 'close "
        "breaking UP through the upper band'. The source computes a recursive "
        "ratchet (a := max(src, a[1]) - (a[1]-b[1])/length, b mirrored) and its "
        "crossdn is a[1] < close[1] and a > close, i.e. the close crossing "
        "DOWN through the upper band. The source wins; recorded, not corrected.",
        "bullish = barssince(crossdn) <= barssince(crossup) is transcribed as "
        "written; its name reads the opposite way round from the md's trend "
        "description, and it is neither renamed nor flipped.",
        "barssince is na until its condition has occurred; bullish is na over "
        "the leading window and Pine treats that na as falsy. The comparison is "
        "evaluated in float64 where a na operand yields False, which matches the "
        "buySignal outcome. For sellSignal the two readings of `not na` could "
        "differ, but only on bars where no position can exist (entering needs "
        "bullish to have been true), and strategy.close on a flat book is a "
        "no-op in both the engine and the projection. Recorded as a modelling "
        "choice.",
        "a and b are stateful across bars, so they are computed in one forward "
        "pass with the nz() lags applied exactly as written rather than being "
        "seeded with an SMA or a rolling extreme.",
        "avg = avg(a, b) is computed by the source and reaches only plot() in "
        "the source, so it is not carried.",
        "ema uses pine_ta.pine_ema; Pine does not publish its EMA seeding rule "
        "(PINE_SEMANTICS §3.1). It is not swapped for a library EMA.",
        "src = input(close) is carried as a parameter resolved through "
        "pine_ta.pine_source, defaulting to close as the source does. The "
        "recursion's max/src and min/src rely on src carrying no na.",
        "plot / plotshape / location / label colours are display-only and are "
        "not reproduced.",
        "A repeated buy signal while already long is refused by Pine's "
        "pyramiding default of 0, which pine_engine reproduces by blocking "
        "same-direction stacking.",
        "strategy() declares only title/shorttitle/overlay, so Pine's defaults "
        "apply: qty_type fixed, qty_value 1, commission 0, pyramiding 0, "
        "initial capital 1000000, process_orders_on_close false.",
        "Contract-step rounding, leverage, margin, liquidation and funding are "
        "not modelled (PINE_SEMANTICS §1.6, §二-4).",
    ]

    def pine_indicators(self, dataframe, params):
        length = int(params["length"])
        src = ta.pine_source(dataframe, str(params["src"]))
        close = dataframe["close"]
        src_values = src.to_numpy(dtype=float)
        count = len(src_values)

        # a := max(src, nz(a[1])) - nz(a[1] - b[1]) / length
        # b := min(src, nz(b[1])) + nz(a[1] - b[1]) / length
        # Both are stateful, so the recursion runs once, forward, in order.
        a_values = np.full(count, np.nan)
        b_values = np.full(count, np.nan)
        a_lag = np.nan
        b_lag = np.nan
        for i in range(count):
            a_nz = 0.0 if np.isnan(a_lag) else a_lag      # nz(a[1])
            b_nz = 0.0 if np.isnan(b_lag) else b_lag      # nz(b[1])
            spread = a_lag - b_lag                        # a[1] - b[1]
            spread_nz = 0.0 if np.isnan(spread) else spread  # nz(a[1] - b[1])
            a_now = max(src_values[i], a_nz) - spread_nz / length
            b_now = min(src_values[i], b_nz) + spread_nz / length
            a_values[i] = a_now
            b_values[i] = b_now
            a_lag, b_lag = a_now, b_now

        a = pd.Series(a_values, index=close.index, dtype=float)
        b = pd.Series(b_values, index=close.index, dtype=float)
        ema = ta.pine_ema(close, int(params["emaLength"]))

        # crossup = b[1] < close[1] and b > close
        crossup = (b.shift(1) < close.shift(1)) & (b > close)
        # crossdn = a[1] < close[1] and a > close
        crossdn = (a.shift(1) < close.shift(1)) & (a > close)
        crossup = crossup.fillna(False).astype(bool)
        crossdn = crossdn.fillna(False).astype(bool)

        # bullish = barssince(crossdn) <= barssince(crossup)
        bs_down = ta.pine_barssince(crossdn)
        bs_up = ta.pine_barssince(crossup)
        bullish = bs_down <= bs_up

        dataframe["pine_g_channel_a"] = a
        dataframe["pine_g_channel_b"] = b
        dataframe["pine_ema"] = ema
        dataframe["pine_bullish"] = bullish.fillna(False).astype(bool)
        # buySignal  = bullish and close < ema
        dataframe["pine_buy_signal"] = (
            dataframe["pine_bullish"] & (close < ema)
        ).fillna(False).astype(bool)
        # sellSignal = not bullish and close > ema
        dataframe["pine_sell_signal"] = (
            (~dataframe["pine_bullish"]) & (close > ema)
        ).fillna(False).astype(bool)
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "buy_signal": dataframe["pine_buy_signal"].to_numpy(dtype=bool),
            "sell_signal": dataframe["pine_sell_signal"].to_numpy(dtype=bool),
        }

    def pine_script(self, broker, i, ctx):
        # strategy.entry("Buy", strategy.long, when=buySignal)
        if ctx["buy_signal"][i]:
            broker.entry("Buy", "long")
        # strategy.close("Buy", when=sellSignal)
        if ctx["sell_signal"][i]:
            broker.close("Buy")
