"""Port of sources/SM_53f51981b2747503.pine
(batch_001/CCI双均线交叉回撤买入策略-CCI-MA-Crossover-Pullback-Buy-Strategy.md).

Pine v5 (`//@version=5`). TradeDots' CCI + MA crossover pullback strategy:

    ma(source, length, type) =>
        type == "SMA"         ? ta.sma(source[1],  length) :
        type == "EMA"         ? ta.ema(source[1],  length) :
        type == "SMMA (RMA)"  ? ta.rma(source[1],  length) :
        type == "WMA"         ? ta.wma(source[1],  length) :
        type == "VWMA"        ? ta.vwma(source[1], length) : na

    cci_ma = ma(hlc3, 20, "EMA")                 // = ta.ema(hlc3[1], 20)
    cci    = (hlc3 - cci_ma) / (0.015 * ta.dev(hlc3, 20))

    fastma = ma(close, 10, "EMA")                // = ta.ema(close[1], 10)
    slowma = ma(close, 30, "EMA")                // = ta.ema(close[1], 30)

    if fastma > slowma and close[1] < fastma and close > open and cci < -cci_threshold
        strategy.entry("Long",  strategy.long)

    if fastma < slowma and close[1] > fastma and close < open and cci > cci_threshold
        strategy.entry("Short", strategy.short)

The local `ma()` helper smooths the PREVIOUS bar's source (`source[1]`), so both
moving averages and the CCI centre line are one bar stale by construction; the
port preserves that shift instead of smoothing the current bar.

`ta.dev(source, length)` is Pine's mean absolute deviation, documented as
`sma(abs(source - sma(source, length)), length)`; the shared layer has no
`pine_dev`, so the formula is written out in `_pine_dev` below. It uses the
UNSHIFTED source, unlike the local `ma()` helper.

There is no exit call: the position is closed only when the opposite entry
reverses it, so `source_reproduce_stops` is False. `strategy(...)` declares no
sizing, so the Pine defaults apply -- `fixed` 1 contract, initial capital
1000000, 0% commission, `pyramiding 0`, `process_orders_on_close=false`.

FIDELITY:

* The `if bullish_crossover and input_crossover_labels` / `else if
  bearish_crossover` block is COMMENTED OUT in the source (as are the
  `strategy.opentrades` label blocks inside both entry branches). Commented code
  places no condition, so nothing is restored from it. `bullish_crossover` /
  `bearish_crossover` are therefore computed but never read by an order call.
* The local `ma()`'s `VWMA` branch is implemented as
  `sma(source[1] * volume, length) / sma(volume, length)` -- only the source
  argument is shifted, `volume` is not, matching `ta.vwma(source[1], length)`.
  It is unreachable under the source's defaults (both types are "EMA") but is
  reproduced so a parameter override lands on the same formula.
* `input.string("EMA", ...)` compares by exact string in Pine; the port compares
  the same strings and falls through to `na` for an unrecognised type, as the
  source does.
* Pine treats an na comparison as false, which is what makes the first bars
  (and the warmup of `cci`) emit nothing; numpy comparisons against NaN behave
  the same way, so no explicit na handling is added.
* `bgcolor`, `plot`, `label.new` and `line.new` are display-only and are not
  reproduced.
* `cci_soruce` is spelled that way in the source and is kept as the parameter
  name so the source's `input()` names line up one-for-one.
* The color inputs (`fastma_color`, `slowma_color`) are display-only and are
  carried in `source_defaults` only because they are `input()` declarations.
* `/*backtest` declares `period: 1h` on Futures_Binance BTC_USDT, so `timeframe`
  is "1h"; `basePeriod: 15m` is the FMZ backtester's own fill granularity.
* Leverage, margin, liquidation and funding are not modelled, and neither is
  the venue's contract-step rounding of order quantities.
"""
import numpy as np
import pandas as pd
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


def _pine_dev(source: pd.Series, length: int) -> pd.Series:
    """Pine `ta.dev`: sma(abs(source - sma(source, length)), length)."""
    return ta.pine_sma((source - ta.pine_sma(source, length)).abs(), length)


def _ma(source: pd.Series, length: int, kind: str, volume: pd.Series) -> pd.Series:
    """The source's local `ma()` helper: smooths `source[1]`, not `source`."""
    previous = source.shift(1)
    if kind == "SMA":
        return ta.pine_sma(previous, length)
    if kind == "EMA":
        return ta.pine_ema(previous, length)
    if kind == "SMMA (RMA)":
        return ta.pine_rma(previous, length)
    if kind == "WMA":
        return ta.pine_wma(previous, length)
    if kind == "VWMA":
        return ta.pine_sma(previous * volume, length) / ta.pine_sma(volume, length)
    return pd.Series(np.nan, index=source.index, dtype=float)


class SMCCIMaCrossoverPullbackBuy_53f519(PinePortBase, IStrategy):
    source_id = "SM_53f51981b2747503"
    source_file = "CCI双均线交叉回撤买入策略-CCI-MA-Crossover-Pullback-Buy-Strategy.md"
    timeframe = "1h"
    can_short = True
    source_defaults: dict = {
        "cci_coloring": True,
        "cci_length": 20,
        "cci_ma_type": "EMA",
        "cci_soruce": "hlc3",
        "cci_threshold": 100,
        "input_crossover_labels": True,
        "fastma_type": "EMA",
        "fastma_source": "close",
        "fastma_length": 10,
        "fastma_color": "#e2fdff",
        "slowma_type": "EMA",
        "slowma_source": "close",
        "slowma_length": 30,
        "slowma_color": "#e2fdff",
    }
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    source_reproduce_stops = False
    source_fidelity_notes = [
        "The `if bullish_crossover ... else if bearish_crossover` block and the "
        "`strategy.opentrades` label blocks are commented out in the source; "
        "nothing is restored from them, so the crossover columns are unused.",
        "The local `ma()` helper smooths the PREVIOUS bar's source; both MAs "
        "and the CCI centre line are one bar stale by construction.",
        "`ta.dev` is Pine's mean absolute deviation "
        "(sma(abs(source - sma(source, length)), length)); it is written out in "
        "_pine_dev because the shared layer has no pine_dev.",
        "`ta.dev` uses the UNSHIFTED hlc3, unlike the local ma() helper.",
        "The VWMA branch is unreachable under the defaults but is implemented "
        "as sma(source[1]*volume, n)/sma(volume, n) for faithfulness.",
        "No exit call exists: the position is closed only by the opposite "
        "entry reversing it, so source_reproduce_stops is False.",
        "Color inputs are display-only; they are carried in source_defaults "
        "only because they are input() declarations.",
        "bgcolor/plot/label.new/line.new are display-only and not reproduced.",
        "Initial capital is unset in the source, hence Pine's default 1000000.",
    ]

    def pine_indicators(self, dataframe, params):
        volume = dataframe["volume"]
        cci_source = ta.pine_source(dataframe, str(params["cci_soruce"]))
        cci_length = int(params["cci_length"])
        cci_threshold = float(params["cci_threshold"])
        cci_ma = _ma(cci_source, cci_length, str(params["cci_ma_type"]), volume)
        cci = (cci_source - cci_ma) / (0.015 * _pine_dev(cci_source, cci_length))

        fastma = _ma(
            ta.pine_source(dataframe, str(params["fastma_source"])),
            int(params["fastma_length"]),
            str(params["fastma_type"]),
            volume,
        )
        slowma = _ma(
            ta.pine_source(dataframe, str(params["slowma_source"])),
            int(params["slowma_length"]),
            str(params["slowma_type"]),
            volume,
        )

        close = dataframe["close"]
        previous_close = close.shift(1)
        open_price = dataframe["open"]

        # Pine treats an na comparison as false; a numpy comparison against NaN
        # is already False, so the conjunctions need no extra na handling.
        long_condition = (
            (fastma > slowma)
            & (previous_close < fastma)
            & (close > open_price)
            & (cci < -cci_threshold)
        )
        short_condition = (
            (fastma < slowma)
            & (previous_close > fastma)
            & (close < open_price)
            & (cci > cci_threshold)
        )

        dataframe["pine_cci"] = cci
        dataframe["pine_fastma"] = fastma
        dataframe["pine_slowma"] = slowma
        dataframe["pine_long_condition"] = long_condition.to_numpy()
        dataframe["pine_short_condition"] = short_condition.to_numpy()
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "long_condition": dataframe["pine_long_condition"].to_numpy(),
            "short_condition": dataframe["pine_short_condition"].to_numpy(),
        }

    def pine_script(self, broker, i, ctx):
        # if fastma > slowma and close[1] < fastma and close > open and cci < -cci_threshold
        #     strategy.entry("Long", strategy.long)
        if ctx["long_condition"][i]:
            broker.entry("Long", "long")
        # if fastma < slowma and close[1] > fastma and close < open and cci > cci_threshold
        #     strategy.entry("Short", strategy.short)
        if ctx["short_condition"][i]:
            broker.entry("Short", "short")
