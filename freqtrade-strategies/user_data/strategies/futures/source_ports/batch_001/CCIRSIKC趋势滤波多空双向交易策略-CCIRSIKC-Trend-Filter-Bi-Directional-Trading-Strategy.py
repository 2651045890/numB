"""Port of sources/SM_cd8d23061c199c35.pine (batch_001/CCIRSIKC趋势滤波多空双向交易策略-CCIRSIKC-Trend-Filter-Bi-Directional-Trading-Strategy.md).

Pine v5. A Keltner channel / CCI / RSI triple filter, gated by an optional
moving-average trend filter and by two `var` state flags:

    typicalPrice = hlc3
    middleLine   = ta.sma(typicalPrice, 30)
    range_1      = 0.7 * ta.atr(30)
    upperChannel = middleLine + range_1
    lowerChannel = middleLine - range_1
    cci = ta.cci(close, 5)
    rsi = ta.rsi(close, 30)
    volCondition = volume > ta.sma(volume, 50) * volumeMultiplier

    longCondition  := longCondition  and cci < -75 and low  < lowerChannel
                       and rsi < 60 and volCondition and not isLongOpen
    shortCondition := shortCondition and cci >  75 and high > upperChannel
                       and rsi > 60 and volCondition and not isShortOpen
    if longCondition:  strategy.entry('Long',  strategy.long);  isLongOpen  := true
    if shortCondition: strategy.entry('Short', strategy.short); isShortOpen := true
    if cci > 0 and isLongOpen:   strategy.close('Long');  isLongOpen  := false
    if cci < 0 and isShortOpen:  strategy.close('Short'); isShortOpen := false

`strategy()` declares `default_qty_type = strategy.cash`,
`default_qty_value = 50000`, `commission_value = 0.0005` (PERCENT, i.e. 0.0005%),
`slippage = 2` and `initial_capital = 10000`; the rest is Pine's documented
default (pyramiding 0, process_orders_on_close false). No `qty=` is passed, so
the 50000-cash default sizes every entry.

FIDELITY -- what is preserved and what is a modelling choice:

* All six `maType` branches of the source are implemented (OFF / SMA / EMA /
  SMMA / CMA / TMA), including the two STATEFUL ones -- SMMA and CMA recur on
  `maValue[1]` and are seeded with `ta.sma(close, maLength)` on the first bar
  where that SMA exists -- so an override through `source_parameters` stays
  faithful rather than silently falling back. The default is 'OFF', under which
  `var float maValue = na` is never assigned and the trend filter is inert, which
  is why the `and`/`or` chain in `longCondition` reduces to `allowLong`.
* Pine's operator precedence is reproduced: `and` binds tighter than `or`, and
  the source's own parentheses around the three `trendFilterMethod` tests are
  kept, so `trendFilterMethod == 'OFF'` short-circuits the absent `maValue`.
* `ta.cci(close, 5)` is `(close - sma(close, 5)) / (0.015 * ta.dev(close, 5))`
  where `ta.dev` is the mean ABSOLUTE deviation from the window's own SMA --
  not `ta.stdev`. `pine_ta` does not expose `ta.dev`, so it is written out here
  with the na-in-window propagation the other window functions use.
* `ta.rsi(close, 30)` and `ta.atr(30)` (= `ta.rma(ta.tr(true), 30)`) go through
  pine_ta, which is the library form of those builtins; `ta.sma` likewise.
* `ta.rsi`'s `rsiOverbought` and `rsiOversold` inputs BOTH default to 60, so the
  RSI leg is `rsi < 60` for the long and `rsi > 60` for the short. That is the
  source's own default, not a typo introduced here.
* `volumeMultiplier` defaults to 0, so `volCondition` is `volume > 0` -- true on
  every real bar. Kept as the expression, not folded away.
* `isLongOpen` / `isShortOpen` are `var bool`, so they persist across bars and
  are only ever cleared by their own exit branch -- a reversal does NOT clear the
  other side's flag. The flags are reproduced as per-run state driven by the
  signals (the source drives them from the signal, not from the fill), and the
  exit branches run AFTER the entries on the same bar, exactly as written.
* `slippage = 2` (two ticks of slippage on market orders) is NOT modelled:
  pine_engine fills at the bar's open or at the resting level with no slippage.
* `commission_value = 0.0005` is TradingView's PERCENT field and is carried as
  `source_commission_percent = 0.0005`, i.e. 0.0005% per side.
* `alert()` calls are alert-only and place no order.
* `plot` / `hline` are display-only.
* The md PROSE says the strategy trades the AUDNZD / GBPNZD FX pairs in the
  title, while the `/*backtest` header is Futures_Binance BTC_USDT and the
  `alert()` strings hardcode "AUDNZD". The md's ticker is not authoritative for
  this port; the header's pair is what the harness backtests.
* The md PROSE also calls the trend filter "趋势确认", which matches the code;
  no contradiction to record there.
* Leverage, margin, liquidation, funding and the venue's contract-step rounding
  are not modelled; the chain verifier measures the last of those separately.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


def _mean_absolute_deviation(source: pd.Series, length: int) -> pd.Series:
    """Pine `ta.dev`: the mean absolute deviation from the window's own SMA.

    Not `ta.stdev` -- that is the standard deviation the Keltner bands would
    use. na inside a window propagates, matching pine_ta's window convention.
    """

    def _dev(window: np.ndarray) -> float:
        if np.isnan(window).any():
            return np.nan
        return float(np.abs(window - window.mean()).mean())

    return source.rolling(length, min_periods=length).apply(_dev, raw=True)


def _pine_cci(source: pd.Series, length: int) -> pd.Series:
    """`ta.cci(source, length)`: (src - sma) / (0.015 * ta.dev(src, length))."""
    basis = ta.pine_sma(source, length)
    deviation = _mean_absolute_deviation(source, length)
    return (source - basis) / (0.015 * deviation)


def _trend_ma(source: pd.Series, kind: str, length: int) -> pd.Series:
    """The source's own `maValue` switch, every branch it implements.

    SMMA and CMA recur on `maValue[1]`; `var float maValue = na` seeds them
    with `ta.sma(close, maLength)` on the first bar where that SMA is not na,
    which is exactly `na(maValue[1]) ? initialSMMA : ...` evaluated in order.
    """
    length = int(length)
    if kind == "OFF":
        return pd.Series(np.nan, index=source.index, dtype=float)
    if kind == "SMA":
        return ta.pine_sma(source, length)
    if kind == "EMA":
        return ta.pine_ema(source, length)
    if kind == "TMA":
        half = int(ta.pine_round(length / 2))
        return ta.pine_sma(ta.pine_sma(source, half), half + 1)
    if kind == "SMMA":
        initial = ta.pine_sma(source, length)
        values = source.to_numpy(dtype=float)
        seeds = initial.to_numpy(dtype=float)
        out = np.full(len(values), np.nan)
        for i in range(len(values)):
            previous = out[i - 1] if i > 0 else np.nan
            out[i] = seeds[i] if np.isnan(previous) else (
                previous * (length - 1) + values[i]
            ) / length
        return pd.Series(out, index=source.index, dtype=float)
    if kind == "CMA":
        # `firstSMA` and `secondSMA` are both `ta.sma(close, maLength)`, so the
        # recursion is (2 * sma - maValue[1]) / 2.
        basis = ta.pine_sma(source, length)
        values = basis.to_numpy(dtype=float)
        out = np.full(len(values), np.nan)
        for i in range(len(values)):
            previous = out[i - 1] if i > 0 else np.nan
            out[i] = values[i] if np.isnan(previous) else (2.0 * values[i] - previous) / 2.0
        return pd.Series(out, index=source.index, dtype=float)
    raise ValueError(f"unsupported MA type {kind!r}")


class SMCciRsiKcTrendFilter_cd8d23(PinePortBase, IStrategy):
    source_id = "SM_cd8d23061c199c35"
    source_file = "CCIRSIKC趋势滤波多空双向交易策略-CCIRSIKC-Trend-Filter-Bi-Directional-Trading-Strategy.md"
    timeframe = "2h"
    can_short = True
    source_defaults: dict = {
        "allowLong": True,
        "allowShort": True,
        "maType": "OFF",
        "trendFilterMethod": "OFF",
        "maLength": 14,
        "lengthKC": 30,
        "multKC": 0.7,
        "lengthCCI": 5,
        "overboughtCCI": 75,
        "oversoldCCI": -75,
        "rsiPeriod": 30,
        "rsiOverbought": 60,
        "rsiOversold": 60,
        "volumeMultiplier": 0.0,
    }
    source_qty_type = "cash"
    source_qty_value = 50000.0
    source_commission_percent = 0.0005
    source_pyramiding = 0
    source_initial_capital = 10000.0
    source_reproduce_stops = False
    source_fidelity_notes = [
        "All six maType branches (OFF / SMA / EMA / SMMA / CMA / TMA) are "
        "implemented, including the stateful SMMA and CMA recursions seeded "
        "from ta.sma(close, maLength). The default 'OFF' leaves `var float "
        "maValue = na` unassigned, so the trend-filter leg is inert.",
        "Pine's precedence is kept (and binds tighter than or) together with the "
        "source's own parentheses around the trendFilterMethod tests.",
        "ta.cci is (src - sma) / (0.015 * ta.dev): the denominator is the mean "
        "ABSOLUTE deviation from the window's own SMA, not ta.stdev; pine_ta has "
        "no ta.dev, so it is written out here.",
        "`rsiOverbought` and `rsiOversold` both default to 60 in the source, so "
        "the RSI leg is rsi < 60 long / rsi > 60 short. Not altered.",
        "volumeMultiplier defaults to 0, making volCondition `volume > 0`; kept "
        "as the expression rather than folded away.",
        "isLongOpen / isShortOpen are `var bool`: they persist across bars, are "
        "cleared only by their own exit branch, and are NOT cleared by a "
        "reversal. Entries run before exits on the same bar, as in the source.",
        "The state flags are driven by the SIGNALS, as in the source, not by the "
        "engine's fills.",
        "`slippage = 2` is not modelled: pine_engine fills at the bar's open or "
        "the resting level with no slippage.",
        "`commission_value = 0.0005` is TradingView's percent field, carried as "
        "0.0005% per side.",
        "There is no stop/take-profit of any kind: exits are market "
        "`strategy.close` calls only, so source_reproduce_stops is False.",
        "`alert()` calls and `plot` / `hline` are alert- and display-only.",
        "The md PROSE / title name the AUDNZD and GBPNZD FX pairs while the "
        "/*backtest header and the backtester target Futures_Binance BTC_USDT; "
        "the header is what the harness backtests.",
        "Leverage, margin, liquidation, funding and venue contract-step rounding "
        "are not modelled; the chain verifier measures the last separately.",
    ]

    def pine_indicators(self, dataframe, params):
        close = dataframe["close"]
        typical_price = (dataframe["high"] + dataframe["low"] + close) / 3.0
        middle_line = ta.pine_sma(typical_price, int(params["lengthKC"]))
        range_1 = float(params["multKC"]) * ta.pine_atr(dataframe, int(params["lengthKC"]))
        upper_channel = middle_line + range_1
        lower_channel = middle_line - range_1

        cci = _pine_cci(close, int(params["lengthCCI"]))
        rsi = ta.pine_rsi(close, int(params["rsiPeriod"]))
        vol_condition = dataframe["volume"] > (
            ta.pine_sma(dataframe["volume"], 50) * float(params["volumeMultiplier"])
        )
        ma_value = _trend_ma(close, str(params["maType"]), int(params["maLength"]))

        trend = str(params["trendFilterMethod"])
        long_trend = (
            (trend != "Normal") | (close > ma_value)
        ) & ((trend != "Reversed") | (close < ma_value))
        short_trend = (
            (trend != "Normal") | (close < ma_value)
        ) & ((trend != "Reversed") | (close > ma_value))
        # trendFilterMethod == 'OFF' makes the whole parenthesised chain true, so
        # the `and`/`or` collapse to "the off-branch wins" whenever it is 'OFF'.
        off = trend == "OFF"
        long_setup = bool(params["allowLong"]) & (off | long_trend)
        short_setup = bool(params["allowShort"]) & (off | short_trend)

        dataframe["pine_middle_line"] = middle_line
        dataframe["pine_upper_channel"] = upper_channel
        dataframe["pine_lower_channel"] = lower_channel
        dataframe["pine_cci"] = cci
        dataframe["pine_rsi"] = rsi
        dataframe["pine_vol_condition"] = vol_condition
        dataframe["pine_ma_value"] = ma_value
        dataframe["pine_long_setup"] = long_setup
        dataframe["pine_short_setup"] = short_setup
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "long_setup": dataframe["pine_long_setup"].to_numpy(dtype=bool),
            "short_setup": dataframe["pine_short_setup"].to_numpy(dtype=bool),
            "cci": dataframe["pine_cci"].to_numpy(),
            "rsi": dataframe["pine_rsi"].to_numpy(),
            "low": dataframe["low"].to_numpy(),
            "high": dataframe["high"].to_numpy(),
            "lower_channel": dataframe["pine_lower_channel"].to_numpy(),
            "upper_channel": dataframe["pine_upper_channel"].to_numpy(),
            "vol_condition": dataframe["pine_vol_condition"].to_numpy(dtype=bool),
            "overbought_cci": float(params["overboughtCCI"]),
            "oversold_cci": float(params["oversoldCCI"]),
            "rsi_overbought": float(params["rsiOverbought"]),
            "rsi_oversold": float(params["rsiOversold"]),
            # `var bool isLongOpen` / `var bool isShortOpen`, persistent state.
            "state": {"is_long_open": False, "is_short_open": False},
        }

    def pine_script(self, broker, i, ctx):
        state = ctx["state"]
        cci = ctx["cci"][i]
        rsi = ctx["rsi"][i]

        long_condition = (
            ctx["long_setup"][i]
            and cci < ctx["oversold_cci"]
            and ctx["low"][i] < ctx["lower_channel"][i]
            and rsi < ctx["rsi_oversold"]
            and ctx["vol_condition"][i]
            and not state["is_long_open"]
        )
        short_condition = (
            ctx["short_setup"][i]
            and cci > ctx["overbought_cci"]
            and ctx["high"][i] > ctx["upper_channel"][i]
            and rsi > ctx["rsi_overbought"]
            and ctx["vol_condition"][i]
            and not state["is_short_open"]
        )

        # if longCondition
        #     strategy.entry('Long', strategy.long)
        if long_condition:
            broker.entry("Long", "long")
            state["is_long_open"] = True
        # if shortCondition
        #     strategy.entry('Short', strategy.short)
        if short_condition:
            broker.entry("Short", "short")
            state["is_short_open"] = True

        # longExitCondition = cci > 0      shortExitCondition = cci < 0
        # if (longExitCondition and isLongOpen):  strategy.close('Long');  isLongOpen := false
        if cci > 0 and state["is_long_open"]:
            broker.close("Long")
            state["is_long_open"] = False
        # if (shortExitCondition and isShortOpen): strategy.close('Short'); isShortOpen := false
        if cci < 0 and state["is_short_open"]:
            broker.close("Short")
            state["is_short_open"] = False
