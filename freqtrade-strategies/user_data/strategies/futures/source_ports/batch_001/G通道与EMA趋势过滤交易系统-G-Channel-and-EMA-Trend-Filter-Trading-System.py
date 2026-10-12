"""Port of sources/SM_291871f4ed0afcd7.pine (batch_001/G通道与EMA趋势过滤交易系统-G-Channel-and-EMA-Trend-Filter-Trading-System.md).

Pine v5. Guppy's G-Channel as a recursive ratchet, filtered by a long EMA, and
unlike its batch sibling `SMGChannelEmaTrendFollowing_1f1767` this one is
BI-DIRECTIONAL: the "sell" side opens a short rather than closing a long.

    length = input.int(100, title="G-Channel Length")
    src    = input(close, title="Source")

    var float a = na
    var float b = na
    a := math.max(src, nz(a[1])) - (nz(a[1]) - nz(b[1])) / length
    b := math.min(src, nz(b[1])) + (nz(a[1]) - nz(b[1])) / length
    avg = (a + b) / 2

    crossup = ta.crossover(close, b)
    crossdn = ta.crossunder(close, a)
    bullish = ta.barssince(crossdn) <= ta.barssince(crossup)

    emaLength = input.int(200, title="EMA Length")
    ema = ta.ema(close, emaLength)

    buySignal  = bullish and close < ema
    sellSignal = not bullish and close > ema

    if (buySignal)
        strategy.entry("Buy", strategy.long)
    if (sellSignal)
        strategy.entry("Sell", strategy.short)

`a` and `b` are stateful: each bar depends on the PREVIOUS bar's two values
exactly as written, so they are computed in a single forward pass, with `nz()`
applied to each lag separately (`nz(a[1]) - nz(b[1])`, not `nz(a[1] - b[1])`)
and no SMA / rolling-extreme seeding. Both assignments read `a[1]` / `b[1]`, so
the just-updated `a` is NOT what `b`'s update sees.

Both entries are plain market entries and there is no exit call at all: a
position is only ever closed by the opposite entry reversing it. The port
therefore declares `source_reproduce_stops = False`, and a position still open
at the end of the window stays open.

`strategy()` declares only `title` and `overlay`, so Pine's documented defaults
apply: `default_qty_type = strategy.fixed`, `default_qty_value = 1`,
`commission_value = 0`, `pyramiding = 0`, initial capital 1000000 and
`process_orders_on_close = false`. The `/*backtest` header declares `period: 1h`
on Futures_Binance BTC_USDT, so `timeframe` is "1h" (its `basePeriod: 1h` is the
same, i.e. the header's fill granularity agrees).

FIDELITY:

* The manifest flags this source `persistent_state`, which is the `var float a` /
  `var float b` pair. Reproduced as one forward pass; the recursion is not
  approximated with a library channel.
* `src = input(close)` is carried as a parameter (`"src": "close"`) and resolved
  through `pine_ta.pine_source`, so the channel's input series stays selectable
  and defaults to close as the source does. The `math.max` / `math.min` of the
  recursion rely on the price series carrying no na; Pine would propagate an na
  `src`.
* `bullish = ta.barssince(crossdn) <= ta.barssince(crossup)` is transcribed as
  written, including its reversed-sounding name: it is true when the DOWN-cross
  through the upper band (`crossdn`) is the more recent of the two. Not renamed
  and not flipped.
* na handling of that comparison is a real modelling choice and it MATTERS here,
  because `not bullish` opens a SHORT. `ta.barssince` is na until its condition
  has occurred at least once, so `bullish` is na over the leading window. Pine's
  comparison operators on series yield false when an operand is na (v3 Operators
  reference: "Comparing against na values still returns a series filled with
  booleans true or false"; `2 < na` -> false), so `bullish` is FALSE there and
  `not bullish` is TRUE -- a short CAN fire before the first crossup. The port
  evaluates the comparison in float64, where a na operand likewise yields False,
  matching that reading. It is the same reading the batch sibling
  `SMGChannelEmaTrendFollowing_1f1767` applies to the identical expression; the
  opposite reading (`na <= x` -> na, `not na` -> na, so no early short) is what
  would follow from the "comparison yields na" formulation, and TradingView's
  own references disagree with each other on it. Recorded rather than resolved
  silently.
* `ta.crossover` / `ta.crossunder` are used with their own definition
  (`a > b and a[1] <= b[1]` / `a < b and a[1] >= b[1]`) and direction, i.e. the
  close crossing above `b` and below `a`. This is NOT the same shape as the v4
  sibling port's hand-written `b[1] < close[1] and b > close`; the source's own
  v5 calls are what is reproduced here.
* `avg = (a + b) / 2` is computed by the source and reaches only `plot(avg, ...)`;
  it is not carried, since it reaches no decision.
* `ema` is Pine's builtin. TradingView does not publish its seeding rule;
  `pine_ta.pine_ema` seeds with the first observation and does not advance the
  recursion on na (PINE_SEMANTICS §3.1). It is not swapped for a library EMA.
* `plot`, `plotshape`, `location`, the label text and colours are display-only
  and are not reproduced.
* A repeated same-direction entry while that direction is already open is
  refused by Pine's `pyramiding` default of 0, which `pine_engine` reproduces by
  blocking same-direction stacking.
* `input(close, title="Source")` is the v5 legacy `input()` form (still
  documented) rather than `input.source()`; both produce a source input.
* Contract-step rounding, leverage, margin, liquidation and funding are not
  modelled (PINE_SEMANTICS §1.6, §二-4).
"""
import numpy as np
import pandas as pd

from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


class SMGChannelEmaTrendFilter_291871(PinePortBase, IStrategy):
    source_id = "SM_291871f4ed0afcd7"
    source_file = "G通道与EMA趋势过滤交易系统-G-Channel-and-EMA-Trend-Filter-Trading-System.md"
    timeframe = "1h"
    can_short = True
    source_defaults: dict = {"length": 100, "src": "close", "emaLength": 200}
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    source_reproduce_stops = False
    source_fidelity_notes = [
        "The manifest flags this source `persistent_state` (var float a / var "
        "float b); the recursion is run as one forward pass, not approximated "
        "with a library channel.",
        "a and b are stateful: each bar reads the PREVIOUS bar's a and b, so the "
        "just-updated a is not what b's update sees. nz() is applied to each lag "
        "separately (nz(a[1]) - nz(b[1])), exactly as the source writes it.",
        "bullish = barssince(crossdn) <= barssince(crossup) is transcribed as "
        "written, name and all: it is true when the DOWN-cross through the upper "
        "band is the more recent of the two.",
        "na handling of that comparison is load-bearing because `not bullish` "
        "opens a SHORT. barssince is na until its condition occurs, and Pine's "
        "series comparisons yield false for na operands (v3 Operators reference: "
        "'Comparing against na values still returns a series filled with "
        "booleans true or false', 2 < na -> false), so bullish is FALSE there and "
        "a short can fire before the first crossup. The port evaluates the "
        "comparison in float64 where a na operand is likewise False. The opposite "
        "reading (comparison -> na, not na -> na, no early short) is what the "
        "'yields na' formulation gives; TradingView's references conflict on it. "
        "Same reading as the batch sibling SMGChannelEmaTrendFollowing_1f1767 for "
        "the identical expression. Recorded, not resolved silently.",
        "ta.crossover / ta.crossunder are used with their own definition and "
        "direction (close crossing above b / below a), not the v4 sibling port's "
        "hand-written b[1] < close[1] and b > close form.",
        "avg = (a + b) / 2 is computed by the source and reaches only plot(avg), "
        "so it is not carried -- it reaches no decision.",
        "ema uses pine_ta.pine_ema; TradingView does not publish its EMA seeding "
        "rule (PINE_SEMANTICS §3.1). It is not swapped for a library EMA.",
        "src = input(close) is carried as a parameter resolved through "
        "pine_ta.pine_source, defaulting to close as the source does; the "
        "recursion's max/min rely on src carrying no na.",
        "There is no exit call in the source: a position is closed only by the "
        "opposite entry reversing it, so source_reproduce_stops is False and a "
        "position open at the end of the window stays open.",
        "A repeated same-direction entry while that direction is already open is "
        "refused by Pine's pyramiding default of 0, which pine_engine reproduces "
        "by blocking same-direction stacking.",
        "strategy() declares only title/overlay, so Pine's defaults apply: "
        "qty_type fixed, qty_value 1, commission 0, pyramiding 0, initial "
        "capital 1000000, process_orders_on_close false.",
        "plot / plotshape / location / label colours are display-only and are not "
        "reproduced.",
        "Contract-step rounding, leverage, margin, liquidation and funding are "
        "not modelled (PINE_SEMANTICS §1.6, §二-4).",
    ]

    def pine_indicators(self, dataframe, params):
        length = int(params["length"])
        ema_length = int(params["emaLength"])
        src = ta.pine_source(dataframe, str(params["src"]))
        close = dataframe["close"]
        src_values = src.to_numpy(dtype=float)
        count = len(src_values)

        # var float a = na / var float b = na
        # a := math.max(src, nz(a[1])) - (nz(a[1]) - nz(b[1])) / length
        # b := math.min(src, nz(b[1])) + (nz(a[1]) - nz(b[1])) / length
        # Both right-hand sides read the PREVIOUS bar's a and b, so the update
        # of `a` must not leak into `b`'s update within the same bar.
        a_values = np.full(count, np.nan)
        b_values = np.full(count, np.nan)
        a_lag = np.nan
        b_lag = np.nan
        for i in range(count):
            a_nz = 0.0 if np.isnan(a_lag) else a_lag          # nz(a[1])
            b_nz = 0.0 if np.isnan(b_lag) else b_lag          # nz(b[1])
            spread = a_nz - b_nz                              # nz(a[1]) - nz(b[1])
            a_values[i] = max(src_values[i], a_nz) - spread / length
            b_values[i] = min(src_values[i], b_nz) + spread / length
            a_lag = a_values[i]
            b_lag = b_values[i]

        a = pd.Series(a_values, index=close.index, dtype=float)
        b = pd.Series(b_values, index=close.index, dtype=float)
        ema = ta.pine_ema(close, ema_length)

        # crossup = ta.crossover(close, b)   /   crossdn = ta.crossunder(close, a)
        crossup = ta.pine_crossover(close, b)
        crossdn = ta.pine_crossunder(close, a)

        # bullish = ta.barssince(crossdn) <= ta.barssince(crossup)
        # A na operand makes the comparison false, as Pine's series comparisons
        # do; see the fidelity note on why that reading is chosen.
        bullish = ta.pine_barssince(crossdn) <= ta.pine_barssince(crossup)

        # buySignal  = bullish and close < ema
        # sellSignal = not bullish and close > ema
        buy_signal = bullish & (close < ema)
        sell_signal = (~bullish) & (close > ema)

        dataframe["pine_g_channel_a"] = a
        dataframe["pine_g_channel_b"] = b
        dataframe["pine_ema"] = ema
        dataframe["pine_bullish"] = bullish.fillna(False).astype(bool)
        dataframe["pine_buy_signal"] = buy_signal.fillna(False).astype(bool)
        dataframe["pine_sell_signal"] = sell_signal.fillna(False).astype(bool)
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "buy_signal": dataframe["pine_buy_signal"].to_numpy(dtype=bool),
            "sell_signal": dataframe["pine_sell_signal"].to_numpy(dtype=bool),
        }

    def pine_script(self, broker, i, ctx):
        # if (buySignal)
        #     strategy.entry("Buy", strategy.long)
        if ctx["buy_signal"][i]:
            broker.entry("Buy", "long")
        # if (sellSignal)
        #     strategy.entry("Sell", strategy.short)
        if ctx["sell_signal"][i]:
            broker.entry("Sell", "short")
