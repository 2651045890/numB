"""Port of sources/SM_ae7e29ef2210debc.pine (batch_001/10SMA与MACD双重趋势跟踪交易策略-10SMA-and-MACD-Dual-Trend-Following-Trading-Strategy.md).

Pine v5. A 10-bar SMA and a MACD that must cross on the SAME bar, long only:

    length             = 10  (input)
    macdFastLength     = 12  (input)
    macdSlowLength     = 26  (input)
    macdSignalSmoothing= 9   (input)
    sma10 = ta.sma(close, length)
    [macdLine, signalLine, _] = ta.macd(close, macdFastLength, macdSlowLength,
                                        macdSignalSmoothing)
    longCondition  = ta.crossover(close, sma10) and ta.crossover(macdLine, signalLine)
    shortCondition = ta.crossunder(close, sma10) and ta.crossunder(macdLine, signalLine)

    if longCondition  -> strategy.entry("Long", strategy.long)
    if shortCondition -> strategy.close("Long")

`strategy("10SMA and MACD Strategy", overlay=true)` declares ONLY title and
overlay, so `strategy.fixed` / 1 contract, initial capital 1000000, commission
0%, pyramiding 0 and `process_orders_on_close=false` are Pine's documented
defaults rather than source-given values.

The two crosses are CONJUNCTIVE, not alternatives: both `crossover(close, sma10)`
and `crossover(macdLine, signalLine)` must hold on one bar. Every term is a
per-bar cross comparison, and `ta.macd` is Pine's `ema(close, fast) -
ema(close, slow)` with the signal line as `ema(macdLine, signal)`, which is what
`pine_ta.pine_macd` computes.

FIDELITY:

* `shortCondition` does NOT open a short -- it calls `strategy.close("Long")`.
  The source never calls `strategy.entry` with `strategy.short`, so `can_short`
  is False; the `SELL` chart label marks the close, not a short entry.
* `strategy.close("Long")` is issued on every bar the condition holds,
  regardless of position, and is a no-op when no "Long" entry is open
  (PINE_SEMANTICS.md 1.12 -- the engine's `from_entry` matching and the signal
  projector's matching guard both honour this).
* `ta.macd`'s two EMAs and its signal EMA are seeded by `pine_ta.pine_ema` with
  the first non-na observation; TradingView's exact seeding is unspecified
  (PINE_SEMANTICS.md 3.1), so this is a modelled choice.
* `ta.sma` returns na until its 10-bar window is full and na anywhere in the
  window propagates (PINE_SEMANTICS.md 3.2); the MACD line needs 26 bars and the
  signal line needs those plus 9, so the first evaluable longCondition is well
  after that and both conditions are false while any term is na.
* The destructured third MACD output (the histogram, `_`) is computed by
  `ta.macd` and discarded; it is not used as a condition.
* There is no stop, limit or trailing exit in the source -- the only exit is the
  close on `shortCondition` -- so `source_reproduce_stops` is False and a
  position still open at the end of the window stays open.
* `plot` / `plotshape` and their colour and text arguments are display-only.
* The md renders the strategy as a "dual trend following" system and its prose
  emphasises trend alignment; the code's requirement is a same-bar double cross,
  which is what is reproduced.
* The `/*backtest` header declares `period: 1d` on Futures_Binance BTC_USDT, so
  `timeframe` is "1d"; its `basePeriod: 1h` is the FMZ backtester's own filling
  granularity, not the strategy's period.
* Leverage, margin, liquidation, funding and the venue's contract-step rounding
  are not modelled.
"""
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


class SM10SmaAndMacdDualTrendFollowing_ae7e29(PinePortBase, IStrategy):
    source_id = "SM_ae7e29ef2210debc"
    source_file = (
        "10SMA与MACD双重趋势跟踪交易策略-10SMA-and-MACD-Dual-Trend-Following-Trading-Strategy.md"
    )
    timeframe = "1d"
    can_short = False
    source_defaults: dict = {
        "length": 10,
        "macdFastLength": 12,
        "macdSlowLength": 26,
        "macdSignalSmoothing": 9,
    }
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    source_reproduce_stops = False
    source_fidelity_notes = [
        "`strategy()` declares only title and overlay, so fixed/1 contract, "
        "initial capital 1000000, commission 0% and pyramiding 0 are Pine's "
        "documented defaults rather than values the source states.",
        "`shortCondition` closes the long (`strategy.close(\"Long\")`) rather "
        "than opening a short, so can_short is False; the SELL chart label is "
        "an annotation on the close.",
        "Both crosses are required on the SAME bar (AND, not OR): "
        "`crossover(close, sma10) and crossover(macdLine, signalLine)`.",
        "`ta.macd` is Pine's ema(fast) - ema(slow) with an ema(signal) of that "
        "line; the histogram (third output) is discarded by the source.",
        "EMA seeding is unspecified by TradingView; pine_ta.pine_ema's "
        "first-non-na seed is the modelled choice (PINE_SEMANTICS.md 3.1).",
        "`strategy.close(\"Long\")` is issued regardless of position and is a "
        "no-op when nothing is bound to that entry id (PINE_SEMANTICS.md 1.12).",
        "No stop / limit / trail exit exists, so source_reproduce_stops is False "
        "and a position open at the end of the window stays open.",
        "plot / plotshape and their colour and text arguments are display-only.",
        "The header's `basePeriod: 1h` is the FMZ backtester's filling "
        "granularity, not the strategy's period; `period: 1d` is.",
        "Leverage, margin, liquidation, funding and venue contract-step rounding "
        "are not modelled.",
    ]

    def pine_indicators(self, dataframe, params):
        close = dataframe["close"]
        sma10 = ta.pine_sma(close, int(params["length"]))
        macd = ta.pine_macd(
            close,
            int(params["macdFastLength"]),
            int(params["macdSlowLength"]),
            int(params["macdSignalSmoothing"]),
        )
        macd_line = macd["macd"]
        signal_line = macd["signal"]
        long_condition = ta.pine_crossover(close, sma10) & ta.pine_crossover(
            macd_line, signal_line
        )
        short_condition = ta.pine_crossunder(close, sma10) & ta.pine_crossunder(
            macd_line, signal_line
        )
        dataframe["pine_sma10"] = sma10
        dataframe["pine_macd_line"] = macd_line
        dataframe["pine_macd_signal"] = signal_line
        dataframe["pine_long_condition"] = long_condition
        dataframe["pine_short_condition"] = short_condition
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "long_condition": dataframe["pine_long_condition"].to_numpy(),
            "short_condition": dataframe["pine_short_condition"].to_numpy(),
        }

    def pine_script(self, broker, i, ctx):
        # if (longCondition)
        #     strategy.entry("Long", strategy.long)
        if ctx["long_condition"][i]:
            broker.entry("Long", "long")
        # if (shortCondition)
        #     strategy.close("Long")
        if ctx["short_condition"][i]:
            broker.close("Long")
