"""Port of sources/SM_7a17d10efa7c3fb9.pine
(batch_001/8周期和21周期的移动平均线策略Dual-Moving-Average-Strategy.md).

Pine v4. Two SMAs of `close` (8 and 21), filtered by the slope of the slow
one, expressed as an angle in degrees and normalised by ATR:

    ma1 = sma(close, 8)
    ma2 = sma(close, 21)

    f_angle(_src, _lookback, _atrPeriod) =>
        rad2degree = 180 / 3.141592653589793238462643
        rad2degree * atan((_src[0] - _src[_lookback]) / atr(_atrPeriod) / _lookback)
    _angle = f_angle(ma2, i_lookback=2, i_atrPeriod=10)

    crosso = crossover(ma1, ma2)
    crossu = crossunder(ma1, ma2)

    f_somethingHappened(_cond, _lookback) =>   // _lookback = 15 (literal)
        bool _crossed = false
        for i = 1 to _lookback
            if _cond[i]
                _crossed := true
        _crossed
    longcrossed  = f_somethingHappened(crosso, 15)
    shortcrossed = f_somethingHappened(crossu, 15)

    long  = longcrossed  and _angle >  angleCriteria
    short = shortcrossed and _angle < -angleCriteria

    if long  -> strategy.entry("Long",  strategy.long)
    if short -> strategy.entry("short", strategy.short)

`f_somethingHappened` looks at `_cond[1] .. _cond[15]`, NOT at `_cond[0]`: a
cross on bar `t` arms the entry for bars `t+1 .. t+15`, and the cross bar
itself can never fire (its own `crosso[1..15]` window is still empty of it).
Reproduced through a 15-bar rolling any over the one-bar-shifted cross series.

There is no exit call, so a position is only closed by the opposite entry
reversing it: `source_reproduce_stops` is False.

`strategy(title="Dual Moving Average", initial_capital=10000, overlay=true)`
sets only the initial capital; `default_qty_type` / `default_qty_value` /
commission / `pyramiding` all stay at Pine's defaults, i.e. `fixed` / 1
contract, commission 0%, `pyramiding 0`, `process_orders_on_close false`.
The 10000 capital is small relative to a venue's contract step, which
PINE_SEMANTICS section 1.6 records as a systematic source of framework-vs-
engine drift; it is carried as declared, not enlarged to chase a match.

The `/*backtest` header declares `period: 10m` on Futures_Binance BTC_USDT,
so `timeframe` is "10m"; its `basePeriod: 1m` is the FMZ backtester's own fill
granularity for those 10m bars.

FIDELITY:

* `i_maSource` (`input(close, "MA Source", input.source)`) and `i_angleLevel`
  (default 6) are declared but NEVER read by the source -- `ma1` / `ma2` are
  hard-coded to `close`. Both are carried as declared inputs and nothing else.
* `atr(_atrPeriod)` is v4's `rma(tr, length)` with `tr` at its default
  `handle_na = true` (first bar = high - low), which is exactly
  `pine_ta.pine_atr`.
* The division chain is `((_src[0] - _src[_lookback]) / atr) / _lookback`,
  left to right, and is reproduced in that order. A zero ATR would divide by
  zero; numpy returns inf/nan there and Pine returns na -- `atan` then
  saturates either way, and a zero ATR does not occur on a traded series.
* `rad2degree = 180 / pi` and `atan` are the v4 bare builtins; numpy's
  `arctan` and the same constant are used.
* Leverage, margin, liquidation and funding are not modelled, and the venue's
  contract-step rounding is not modelled either.
"""
import numpy as np
import pandas as pd
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase

_RAD2DEG = 180.0 / 3.141592653589793238462643


class SMDualMovingAverage_7a17d1(PinePortBase, IStrategy):
    source_id = "SM_7a17d10efa7c3fb9"
    source_file = "8周期和21周期的移动平均线策略Dual-Moving-Average-Strategy.md"
    timeframe = "10m"
    can_short = True
    source_defaults: dict = {
        "angleCriteria": 7,
        "i_lookback": 2,
        "i_atrPeriod": 10,
        "i_angleLevel": 6,
        "i_maSource": "close",
    }
    # strategy(title, initial_capital=10000, overlay) -- Pine defaults elsewhere.
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 10_000.0
    source_reproduce_stops = False
    source_fidelity_notes = [
        "`f_somethingHappened` scans `_cond[1] .. _cond[15]`, never "
        "`_cond[0]`, so a cross arms the entry from the NEXT bar and the cross "
        "bar itself can never fire. Reproduced as a 15-bar rolling any of the "
        "one-bar-shifted cross.",
        "`i_maSource` and `i_angleLevel` are declared inputs the source never "
        "reads: `ma1`/`ma2` are hard-coded to `close`.",
        "`atr(_atrPeriod)` is v4 `rma(tr, length)` with `tr`'s default "
        "handle_na=true (first bar = high - low), i.e. pine_ta.pine_atr.",
        "Division chain kept left-to-right: ((_src - _src[_lookback]) / atr) / "
        "_lookback.",
        "initial_capital=10000 is declared by the source and kept; section 1.6 "
        "of PINE_SEMANTICS records that a capital this small relative to the "
        "venue's contract step is a systematic cause of framework-vs-engine "
        "drift, not a port error.",
        "No exit call exists: a position is closed only by the opposite entry "
        "reversing it, so source_reproduce_stops is False.",
        "`default_qty_type`/`default_qty_value`/commission/pyramiding are not "
        "declared, so Pine's defaults apply: fixed / 1 contract, 0% "
        "commission, pyramiding 0, process_orders_on_close false.",
        "Leverage, margin, liquidation, funding and venue contract-step "
        "rounding are not modelled.",
    ]

    def pine_indicators(self, dataframe, params):
        close = dataframe["close"]
        ma1 = ta.pine_sma(close, 8)
        ma2 = ta.pine_sma(close, 21)

        lookback = int(params["i_lookback"])
        atr = ta.pine_atr(dataframe, int(params["i_atrPeriod"]))
        with np.errstate(divide="ignore", invalid="ignore"):
            angle = _RAD2DEG * np.arctan(
                ((ma2 - ma2.shift(lookback)) / atr / lookback).to_numpy(dtype=float)
            )
        angle = pd.Series(angle, index=dataframe.index, dtype=float)

        crosso = ta.pine_crossover(ma1, ma2)
        crossu = ta.pine_crossunder(ma1, ma2)
        # for i = 1 to 15: if _cond[i] -> true
        long_crossed = crosso.shift(1).rolling(15, min_periods=1).max().fillna(0.0) > 0
        short_crossed = crossu.shift(1).rolling(15, min_periods=1).max().fillna(0.0) > 0

        threshold = float(params["angleCriteria"])
        dataframe["pine_angle"] = angle
        dataframe["pine_long_condition"] = (long_crossed & (angle > threshold)).fillna(False)
        dataframe["pine_short_condition"] = (short_crossed & (angle < -threshold)).fillna(False)
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "long_condition": dataframe["pine_long_condition"].to_numpy(),
            "short_condition": dataframe["pine_short_condition"].to_numpy(),
        }

    def pine_script(self, broker, i, ctx):
        # if(long)
        #     strategy.entry("Long", strategy.long)
        if ctx["long_condition"][i]:
            broker.entry("Long", "long")
        # if(short)
        #     strategy.entry("short", strategy.short)
        if ctx["short_condition"][i]:
            broker.entry("short", "short")
