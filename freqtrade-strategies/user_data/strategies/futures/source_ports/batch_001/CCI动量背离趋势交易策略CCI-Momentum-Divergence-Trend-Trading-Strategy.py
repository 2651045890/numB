"""Port of sources/SM_603aa5907a8edfe4.pine
(batch_001/CCI动量背离趋势交易策略CCI-Momentum-Divergence-Trend-Trading-Strategy.md).

Pine v5. One entry call per direction and NO exit call of any kind, so a
position is only ever closed by the opposite entry reversing it:

    source    = entrySignalSource == "Momentum" ? close - close[ccimomLength]
                                                : ta.cci(close, ccimomLength)
    crossUp   = ta.cross(source, 0)
    crossDown = ta.cross(0, source)

    rsi        = ta.rsi(close, rsiLength)
    oversold   = rsi <= rsiOversold or rsi[1] <= rsiOversold
                 or rsi[2] <= rsiOversold or rsi[3] <= rsiOversold
    overbought = rsi >= rsiOverbought or rsi[1] >= rsiOverbought
                 or rsi[2] >= rsiOverbought or rsi[3] >= rsiOverbought

    bullishDivergence = rsi[0] > rsi[1] and rsi[1] < rsi[2]
    bearishDivergence = rsi[0] < rsi[1] and rsi[1] > rsi[2]

    longEntryCondition  = crossUp   and oversold   and (not useDivergence or bullishDivergence)
    shortEntryCondition = crossDown and overbought and (not useDivergence or bearishDivergence)

    strategy.entry("Buy",  strategy.long,  when=longEntryCondition)
    strategy.entry("Sell", strategy.short, when=shortEntryCondition)

`strategy("bayush", overlay=true)` declares only a title and `overlay`, so
every property is Pine's documented default: `default_qty_type = fixed`,
`default_qty_value = 1`, initial capital 1000000, commission 0%, `pyramiding
= 0`, `process_orders_on_close = false`. The port carries those, and no
stop/limit/trail exit exists to reproduce, so `source_reproduce_stops` is
False and a position open at the end of the window stays open.

The `/*backtest` header declares `period: 1h` on Futures_Binance BTC_USDT, so
`timeframe` is "1h"; its `basePeriod: 15m` is the FMZ backtester's own fill
granularity for those 1h bars, not the strategy's period.

FIDELITY:

* `ta.cross(a, b)` is SYMMETRIC in its arguments -- it is `crossover(a, b) or
  crossunder(a, b)`, and `crossunder(a, b)` is `crossover(b, a)` -- so the
  source's `crossUp = ta.cross(source, 0)` and `crossDown = ta.cross(0,
  source)` are the SAME boolean series. Every zero crossing of `source`
  therefore raises both `crossUp` and `crossDown`; the direction is decided
  only by which of the RSI filters (`oversold` / `overbought`) is satisfied.
  This is very likely not what the author intended (the usual shape is
  `ta.crossover` / `ta.crossunder`), but the source is the authority on the
  trading behaviour, so the port reproduces it verbatim rather than
  "correcting" it to a directional cross.
* `ta.cci(source, length)` is computed on `close` (not the typical price),
  exactly as the source passes `close`. Formula reproduced locally:
  `(source - ta.sma(source, length)) / (0.015 * ta.dev(source, length))`,
  where `ta.dev` is the mean absolute deviation of the window's values from
  that window's mean. `pine_ta` ships no `cci`/`dev`, and iron rule 3 forbids
  swapping in a library function of the same name, so both are spelled out.
* `ta.dev` divides by `length` and is built from the SAME window whose mean
  is `ta.sma(source, length)`, so it is the textbook mean absolute deviation.
  A window with zero deviation yields a numpy inf/nan rather than Pine's na;
  the condition it feeds is then false either way.
* The md's English text describes the divergence test as "price making higher
  lows while RSI makes lower lows", but the CODE never looks at price: it is
  `rsi[0] > rsi[1] and rsi[1] < rsi[2]`, i.e. a plain RSI trough. Recorded,
  not "fixed" -- the code is what trades.
* `oversold` / `overbought` look back four bars with a non-strict `<=` /
  `>=`, so they stay true for four bars after the extreme. Reproduced with
  the same lag chain; an na comparison is false, as it is in Pine.
* `entrySignalSource` is a string input defaulting to "CCI"; the "Momentum"
  branch is `close - close[ccimomLength]` and is kept selectable.
* Leverage, margin, liquidation and funding are not modelled, and the venue's
  contract-step rounding is not modelled either, so the framework and the
  engine can differ by a rounded quantity (the chain verifier measures that
  separately rather than treating it as a signal difference).
"""
import numpy as np
import pandas as pd
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


def _pine_dev(source: pd.Series, length: int) -> pd.Series:
    """Pine `ta.dev`: mean absolute deviation from the window's own mean."""
    return source.rolling(length, min_periods=length).apply(
        lambda window: float(np.mean(np.abs(window - window.mean()))), raw=True
    )


def _pine_cci(source: pd.Series, length: int) -> pd.Series:
    """Pine `ta.cci(source, length)`.

    (source - ta.sma(source, length)) / (0.015 * ta.dev(source, length)); na
    until the window is full, which is what both rolling windows give.
    """
    mean = source.rolling(length, min_periods=length).mean()
    with np.errstate(divide="ignore", invalid="ignore"):
        return (source - mean) / (0.015 * _pine_dev(source, length))


class SMCciMomentumDivergenceTrend_603aa5(PinePortBase, IStrategy):
    source_id = "SM_603aa5907a8edfe4"
    source_file = "CCI动量背离趋势交易策略CCI-Momentum-Divergence-Trend-Trading-Strategy.md"
    timeframe = "1h"
    can_short = True
    source_defaults: dict = {
        "entrySignalSource": "CCI",
        "ccimomLength": 10,
        "useDivergence": True,
        "rsiOverbought": 65,
        "rsiOversold": 35,
        "rsiLength": 14,
    }
    # `strategy("bayush", overlay=true)`: Pine's documented defaults.
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    source_reproduce_stops = False
    source_fidelity_notes = [
        "`ta.cross(a, b)` is symmetric, so the source's `crossUp = "
        "ta.cross(source, 0)` and `crossDown = ta.cross(0, source)` are the "
        "same boolean: every zero crossing of `source` raises both, and only "
        "the RSI filter separates long from short. Reproduced verbatim; not "
        "rewritten to a directional cross.",
        "`ta.cci` uses `close`, not the typical price, because the source "
        "passes `close`. Formula implemented locally as "
        "(source - sma(source, n)) / (0.015 * mean-absolute-deviation) "
        "because pine_ta has no cci/dev and iron rule 3 forbids substituting "
        "a same-named library function.",
        "MD text calls the divergence test a price/RSI divergence; the code "
        "only compares three consecutive RSI values. Code is authoritative, "
        "the discrepancy is recorded and not 'fixed'.",
        "No exit call exists: a position is closed only by the opposite entry "
        "reversing it, so source_reproduce_stops is False and a position open "
        "at the end of the window stays open.",
        "`strategy()` declares only title/overlay, so Pine's defaults apply: "
        "fixed / 1 contract, initial capital 1000000, commission 0%, "
        "pyramiding 0, process_orders_on_close false.",
        "plotshape/alertcondition are display/alert-only and are not "
        "reproduced.",
        "Leverage, margin, liquidation, funding and the venue's contract-step "
        "rounding are not modelled.",
    ]

    def pine_indicators(self, dataframe, params):
        close = dataframe["close"]
        length = int(params["ccimomLength"])
        if str(params["entrySignalSource"]) == "Momentum":
            # close - close[ccimomLength]
            source = close - close.shift(length)
        else:
            source = _pine_cci(close, length)

        # ta.cross(source, 0) -- one series, used for both directions.
        cross = ta.pine_cross(source, 0.0)

        rsi = ta.pine_rsi(close, int(params["rsiLength"]))
        oversold_level = float(params["rsiOversold"])
        overbought_level = float(params["rsiOverbought"])
        oversold = (
            (rsi <= oversold_level)
            | (rsi.shift(1) <= oversold_level)
            | (rsi.shift(2) <= oversold_level)
            | (rsi.shift(3) <= oversold_level)
        )
        overbought = (
            (rsi >= overbought_level)
            | (rsi.shift(1) >= overbought_level)
            | (rsi.shift(2) >= overbought_level)
            | (rsi.shift(3) >= overbought_level)
        )

        bullish_divergence = (rsi > rsi.shift(1)) & (rsi.shift(1) < rsi.shift(2))
        bearish_divergence = (rsi < rsi.shift(1)) & (rsi.shift(1) > rsi.shift(2))

        use_divergence = bool(params["useDivergence"])
        long_condition = cross & oversold
        short_condition = cross & overbought
        if use_divergence:
            long_condition = long_condition & bullish_divergence
            short_condition = short_condition & bearish_divergence

        dataframe["pine_cci_source"] = source
        dataframe["pine_rsi"] = rsi
        dataframe["pine_long_condition"] = long_condition.fillna(False)
        dataframe["pine_short_condition"] = short_condition.fillna(False)
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "long_condition": dataframe["pine_long_condition"].to_numpy(),
            "short_condition": dataframe["pine_short_condition"].to_numpy(),
        }

    def pine_script(self, broker, i, ctx):
        # strategy.entry("Buy", strategy.long, when=longEntryCondition)
        if ctx["long_condition"][i]:
            broker.entry("Buy", "long")
        # strategy.entry("Sell", strategy.short, when=shortEntryCondition)
        if ctx["short_condition"][i]:
            broker.entry("Sell", "short")
