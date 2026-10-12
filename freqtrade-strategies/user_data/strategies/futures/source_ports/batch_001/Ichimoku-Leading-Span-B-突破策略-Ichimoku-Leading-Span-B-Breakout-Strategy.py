"""Port of sources/SM_ceee755d569fa5ea.pine (batch_001/Ichimoku-Leading-Span-B-突破策略-Ichimoku-Leading-Span-B-Breakout-Strategy.md).

Pine v5. Close crossing the Ichimoku Leading Span B, long only:

    conversionPeriods   = 9   (input, "Dönüşüm Periyodu")
    basePeriods         = 26  (input, "Taban Periyodu")
    laggingSpan2Periods = 52  (input, "Gecikme Span 2 Periyodu")
    displacement        = 26  (input, "Kaydırma")

    tenkanSen   = (ta.highest(high, conversionPeriods)   + ta.lowest(low, conversionPeriods))   / 2
    kijunSen    = (ta.highest(high, basePeriods)         + ta.lowest(low, basePeriods))         / 2
    senkouSpanA = (tenkanSen + kijunSen) / 2
    senkouSpanB = (ta.highest(high, laggingSpan2Periods) + ta.lowest(low, laggingSpan2Periods)) / 2

    buy_signal  = ta.crossover(close, senkouSpanB[displacement])   -> strategy.entry("Alım", strategy.long)
    sell_signal = ta.crossunder(close, senkouSpanB[displacement])  -> strategy.close("Alım")

`strategy("Ichimoku Leading Span B Alım/Satım Stratejisi", overlay=true)`
declares ONLY title and overlay, so `strategy.fixed` / 1 contract, initial
capital 1000000, commission 0%, pyramiding 0 and
`process_orders_on_close=false` are Pine's documented defaults rather than
source-given values.

THE DISPLACEMENT IS A LOOKBACK HERE, NOT THE CUSTOMARY FORWARD SHIFT, and this
is the part a reader is most likely to get wrong. `plot(senkouSpanB, ...,
offset=displacement)` shifts the PLOT 26 bars to the right, the usual Ichimoku
presentation; the signal, however, tests `senkouSpanB[displacement]`, which is
the Span B value of 26 bars AGO. The signal is therefore `close` crossing the
52-bar midpoint from 26 bars earlier -- no future data is read, and the two
crosses are taken against that one shifted series.

FIDELITY:

* `senkouSpanB[displacement]` is a 26-bar historical reference on the span, not
  an offset applied to the comparison; the port shifts the series and tests
  against the shifted value, matching the source.
* `senkouSpanA` is computed by the source and never read by it; it is kept as a
  ledger column rather than deleted. `tenkanSen` and `kijunSen` are read only
  through `senkouSpanA` and are kept too.
* Long only: the source never calls `strategy.entry` with `strategy.short`, so
  `can_short` is False; "Alım/Satım" in the title is buy/sell, and the sell half
  is a `strategy.close`.
* `strategy.close("Alım")` fires on the crossunder regardless of position and is
  a no-op when nothing is bound to that entry id (PINE_SEMANTICS.md 1.12).
* `ta.highest` / `ta.lowest` return na until their window is full and na
  propagates through the window (PINE_SEMANTICS.md 3.2), so Span B -- and with
  it the 26-bar-ago series the signals compare against -- starts only after 52 +
  26 bars; both conditions are false while any term is na.
* `pine_ta.pine_crossover` / `pine_crossunder` implement Pine's `a > b and a[1]
  <= b[1]` / `a < b and a[1] >= b[1]`.
* There is no stop, limit or trailing exit in the source -- the crossunder is the
  only way out -- so `source_reproduce_stops` is False and a position still open
  at the end of the window stays open.
* `plot` / `plotshape` and their colour and size arguments are display-only.
* The prose in the md describes a standard Ichimoku cloud breakout (price above
  or below the cloud, the span plotted forward); the code, per the point above,
  is a cross against a 26-bar-old Span B. The code is followed and the
  disagreement recorded rather than reconciled.
* The `/*backtest` header declares `period: 1d` on Futures_Binance BTC_USDT, so
  `timeframe` is "1d"; its `basePeriod: 1h` is the FMZ backtester's own filling
  granularity, not the strategy's period.
* Leverage, margin, liquidation, funding and the venue's contract-step rounding
  are not modelled.
"""
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


class SMIchimokuLeadingSpanBBreakout_ceee75(PinePortBase, IStrategy):
    source_id = "SM_ceee755d569fa5ea"
    source_file = (
        "Ichimoku-Leading-Span-B-突破策略-Ichimoku-Leading-Span-B-Breakout-Strategy.md"
    )
    timeframe = "1d"
    can_short = False
    source_defaults: dict = {
        "conversionPeriods": 9,
        "basePeriods": 26,
        "laggingSpan2Periods": 52,
        "displacement": 26,
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
        "The signal compares close against `senkouSpanB[displacement]` -- the "
        "Span B value from 26 bars AGO -- while `plot(..., offset=displacement)` "
        "shifts only the drawing forward. The displacement is a lookback in the "
        "signal, and no future data is read.",
        "senkouSpanA (and through it tenkanSen and kijunSen) is computed by the "
        "source and never read by it; it is kept as a ledger column.",
        "Long only: the source never calls `strategy.entry` with "
        "`strategy.short`, so can_short is False; its 'Satım' half is a "
        "`strategy.close`.",
        "`strategy.close(\"Alım\")` is issued regardless of position and is a "
        "no-op when nothing is bound to that entry id (PINE_SEMANTICS.md 1.12).",
        "`ta.highest` / `ta.lowest` are na until the window is full and na "
        "propagates (PINE_SEMANTICS.md 3.2), so both conditions stay false "
        "during the 52 + 26 bar warm-up.",
        "No stop / limit / trail exit exists, so source_reproduce_stops is False "
        "and a position open at the end of the window stays open.",
        "The md prose describes a standard Ichimoku cloud breakout with the span "
        "plotted forward; the code tests a 26-bar-old Span B. The code is "
        "followed and the difference recorded.",
        "plot / plotshape and their colour and size arguments are display-only.",
        "The header's `basePeriod: 1h` is the FMZ backtester's filling "
        "granularity, not the strategy's period; `period: 1d` is.",
        "Leverage, margin, liquidation, funding and venue contract-step rounding "
        "are not modelled.",
    ]

    def pine_indicators(self, dataframe, params):
        high = dataframe["high"]
        low = dataframe["low"]
        close = dataframe["close"]
        conversion = int(params["conversionPeriods"])
        base = int(params["basePeriods"])
        span_b_periods = int(params["laggingSpan2Periods"])
        displacement = int(params["displacement"])

        tenkan_sen = (
            ta.pine_highest(high, conversion) + ta.pine_lowest(low, conversion)
        ) / 2.0
        kijun_sen = (ta.pine_highest(high, base) + ta.pine_lowest(low, base)) / 2.0
        senkou_span_a = (tenkan_sen + kijun_sen) / 2.0
        senkou_span_b = (
            ta.pine_highest(high, span_b_periods) + ta.pine_lowest(low, span_b_periods)
        ) / 2.0
        # senkouSpanB[displacement]
        shifted_span_b = senkou_span_b.shift(displacement)

        dataframe["pine_tenkan_sen"] = tenkan_sen
        dataframe["pine_kijun_sen"] = kijun_sen
        dataframe["pine_senkou_span_a"] = senkou_span_a
        dataframe["pine_senkou_span_b"] = senkou_span_b
        dataframe["pine_senkou_span_b_shifted"] = shifted_span_b
        dataframe["pine_buy_signal"] = ta.pine_crossover(close, shifted_span_b)
        dataframe["pine_sell_signal"] = ta.pine_crossunder(close, shifted_span_b)
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "buy_signal": dataframe["pine_buy_signal"].to_numpy(),
            "sell_signal": dataframe["pine_sell_signal"].to_numpy(),
        }

    def pine_script(self, broker, i, ctx):
        # if (buy_signal)
        #     strategy.entry("Alım", strategy.long)
        if ctx["buy_signal"][i]:
            broker.entry("Alım", "long")
        # if (sell_signal)
        #     strategy.close("Alım")
        if ctx["sell_signal"][i]:
            broker.close("Alım")
