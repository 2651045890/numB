"""Port of sources/SM_a7610041ccedb427.pine (batch_001/Bollinger带与K线并用策略Bollinger-Bands-and-K-line-Combined-Strategy.md).

Pine v4, `strategy("BB策略", overlay=true)`. Bollinger Bands plus two
candlestick patterns gate a pair of STOP-entry orders, and each side is closed
by its own cross of a band:

    basis = sma(src, length)
    dev   = mult * stdev(src, length)
    upper = basis + dev
    lower = basis - dev

    bullishEngulfing = open <= close[1] and open < open[1] and close > open[1]
    C_LongUpperShadowBearish   = C_UpShadow  > C_Range/100 * 75
    C_LongLowerShadowBullish1  = C_DnShadow1 > C_Range1/100 * 75
        where C_UpShadow  = high - max(close, open)
              C_DnShadow1 = min(close, open) - low
              C_Range     = high - low

    if (bullishEngulfing or C_LongLowerShadowBullish1) and inDateRange
           and cross(low, lower)
        strategy.entry("L", strategy.long, qty=1, stop=low[1])
    if crossunder(close, upper * 0.9985)
        strategy.close("L", qty_percent=1)
    if ((bullishEngulfing == 0) or C_LongUpperShadowBearish) and inDateRange
           and cross(close, upper)
        strategy.entry("S", strategy.short, qty=1, stop=high[1])
    if crossunder(lower * 1.0015, close)
        strategy.close("S", qty_percent=1)

`cross(x, y)` is Pine's either-direction crossing, i.e. `crossover(x, y) or
crossunder(x, y)`; pine_ta.pine_cross implements exactly that.

The two entry orders carry `stop=`, so they are RESTING buy-stop / sell-stop
orders evaluated on later bars, not next-open market orders. The engine models
that (`_price_order_fill`), but Freqtrade's strategy interface has no way to
express a resting entry order -- the signal projection can only fire
`enter_long` / `enter_short` on the bar the order was PLACED, and the framework
then fills it at the next open. PINE_SEMANTICS.md section 2.11 records this as a
framework boundary; it is the reason this port cannot be reported as
behaviourally equivalent to the source.

`strategy()` declares only `title` / `overlay`, so Pine's documented defaults
apply and are what this port carries: `default_qty_type=fixed`, one unit per
order, `commission_value=0`, `pyramiding=0`, `process_orders_on_close=false`,
initial capital 1000000.

The `/*backtest` header declares `period: 3m` on Futures_Binance BTC_USDT, so
`timeframe` is "3m". There is no local 3m futures history, so the chain
verifier reports `skipped_no_local_data` for this port.

FIDELITY:

* `strategy.close(..., qty_percent=1)` closes ONE PERCENT of the position, not
  all of it. The shared engine's `PineBroker.close` has no partial-close
  concept -- it closes every entry matching the id -- so the port can only
  place the full close. Where the source would bleed out 1% per bar while its
  exit condition holds, the port exits in one go. Recorded as a blocker; the
  port does not pretend to reproduce the partial close.
* `inDateRange` is hard-coded `true` in the source. The six `startDate` /
  `startMonth` / ... / `endYear` inputs are declared but never referenced by
  any condition, so no date filter exists. They are carried in
  `source_defaults` for completeness and change nothing; the source's own
  header comment ("Look if the close time of the current bar falls inside the
  date range") describes an intent the code does not implement.
* `bearishEngulfing` is computed but appears only in commented-out
  `plotshape` / `alertcondition` lines, so it places no order and is not
  reproduced.
* The whole `C_*` candlestick block is defined twice (`C_Len` and `C_Len1`
  families) with identical literals; only two of its outputs reach an order --
  `C_LongLowerShadowBullish1` and `C_LongUpperShadowBearish`. `C_BodyAvg`,
  `C_SmallBody`, `C_LongBody`, `C_HasUpShadow`, `C_HasDnShadow`, `C_WhiteBody`,
  `C_BlackBody`, `C_IsInsideBar`, `C_BodyMiddle`, `C_ShadowEquals`,
  `C_IsDojiBody`, `C_Doji`, `C_Factor`, `C_Len` and the `atr(30)`-based
  `patternLabelPosLow` / `patternLabelPosHigh` (both families) are computed and
  never read by an order or by any series an order reads, so they have no
  trading effect and are not carried. The `ema(C_Body, 14)` inside that block
  is likewise inert.
* The commented-out `strategy.close("L", when=cross(basis, close),
  qty_percent=50)` / `"S"` lines place no order and are not restored.
* `offset` is a plot-only argument; `diff`, `fill`, `plot` and the commented
  `plot(upper*0.9985, ...)` / `plot(lower*1.0015, ...)` lines are display-only.
  The two multipliers `0.9985` / `1.0015` ARE part of the order conditions and
  are reproduced verbatim.
* `stdev` is Pine's population standard deviation (ddof=0), which is what
  pine_ta.pine_stdev computes.
* A `stop=` whose value is na places no order on the original platform; the
  port guards the same way rather than passing nan into the engine.
* Slippage, leverage, margin, liquidation and funding are not modelled; the
  venue's contract-step rounding is not modelled either, so the framework and
  the engine can differ by a rounded quantity (measured separately by the chain
  verifier rather than treated as a signal difference).
"""
import numpy as np

from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


class SMBollingerBandsAndKLineCombined_a76100(PinePortBase, IStrategy):
    source_id = "SM_a7610041ccedb427"
    source_file = "Bollinger带与K线并用策略Bollinger-Bands-and-K-line-Combined-Strategy.md"
    timeframe = "3m"
    can_short = True
    source_defaults: dict = {
        "length": 20,
        "src": "close",
        "mult": 2.0,
        "offset": 0,
        # Declared in the source but never referenced: `inDateRange` is the
        # literal `true`. Kept so the declared surface is complete.
        "startDate": 1,
        "startMonth": 1,
        "startYear": 2018,
        "endDate": 1,
        "endMonth": 11,
        "endYear": 2030,
    }
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    # No strategy.exit / stop / limit EXIT anywhere: the only exits are the two
    # strategy.close calls, which the engine books at the next open.
    source_reproduce_stops = False
    source_fidelity_notes = [
        "`strategy.close(qty_percent=1)` closes 1% of the position; the shared "
        "engine has no partial close, so the port places the full close "
        "instead. Divergence recorded as a blocker, not hidden.",
        "`inDateRange` is hard-coded true; the start/end date inputs are "
        "declared and never used, so no date filter exists.",
        "`bearishEngulfing` feeds only commented-out plot/alert lines and "
        "places no order; not reproduced.",
        "Only C_LongLowerShadowBullish1 and C_LongUpperShadowBearish of the "
        "duplicated candlestick block reach an order; the rest (body-average "
        "EMA, doji/shadow flags, atr(30) label positions) are inert and are "
        "not carried.",
        "`cross(x, y)` is either-direction crossing, modelled as "
        "pine_crossover | pine_crossunder.",
        "The 0.9985 / 1.0015 band multipliers are part of the order conditions "
        "and are reproduced verbatim; the commented-out plots that use them "
        "are not.",
        "Both entries use strategy.entry(stop=...), i.e. resting stop orders "
        "filled on a LATER bar. The engine models that, but Freqtrade cannot "
        "be handed a resting entry order, so the projection fires the entry on "
        "the placement bar and the framework fills at the next open. "
        "PINE_SEMANTICS.md section 2.11.",
        "stdev is the population form (ddof=0), as Pine ta.stdev computes it.",
        "A na stop price places no order on the original platform; the port "
        "guards identically instead of passing nan to the engine.",
        "Leverage, margin, liquidation, funding and venue contract-step "
        "rounding are not modelled.",
    ]

    def pine_indicators(self, dataframe, params):
        open_col = dataframe["open"]
        high = dataframe["high"]
        low = dataframe["low"]
        close = dataframe["close"]

        length = int(params["length"])
        mult = float(params["mult"])
        src = ta.pine_source(dataframe, str(params["src"]))

        basis = ta.pine_sma(src, length)
        dev = mult * ta.pine_stdev(src, length)
        upper = basis + dev
        lower = basis - dev

        # Engulfing candle: current open <= previous close, current open <
        # previous open, current close > previous open.
        open_previous = open_col.shift(1)
        close_previous = close.shift(1)
        bullish_engulfing = (
            (open_col <= close_previous) & (open_col < open_previous)
            & (close > open_previous)
        )

        # Long lower shadow (bullish) / long upper shadow (bearish). The source
        # defines both candle blocks twice with identical literals; these are
        # the two members that actually gate an order.
        body_hi = np.maximum(close, open_col)
        body_lo = np.minimum(close, open_col)
        candle_range = high - low
        up_shadow = high - body_hi
        dn_shadow = body_lo - low
        long_lower_shadow_bullish = dn_shadow > candle_range / 100.0 * 75.0
        long_upper_shadow_bearish = up_shadow > candle_range / 100.0 * 75.0

        cross_low_lower = ta.pine_cross(low, lower)
        cross_close_upper = ta.pine_cross(close, upper)

        # inDateRange is the literal `true`, so it drops out of both conditions.
        dataframe["pine_long_entry"] = (
            (bullish_engulfing | long_lower_shadow_bullish) & cross_low_lower
        )
        # `bullishEngulfing == 0` is the v4 bool-as-number spelling of "not
        # bullishEngulfing"; True == 1 and False == 0, so negation is exact.
        dataframe["pine_short_entry"] = (
            (~bullish_engulfing | long_upper_shadow_bearish) & cross_close_upper
        )
        dataframe["pine_close_long"] = ta.pine_crossunder(close, upper * 0.9985)
        dataframe["pine_close_short"] = ta.pine_crossunder(lower * 1.0015, close)
        dataframe["pine_stop_long"] = low.shift(1)
        dataframe["pine_stop_short"] = high.shift(1)
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "long_entry": dataframe["pine_long_entry"].to_numpy(),
            "short_entry": dataframe["pine_short_entry"].to_numpy(),
            "close_long": dataframe["pine_close_long"].to_numpy(),
            "close_short": dataframe["pine_close_short"].to_numpy(),
            "stop_long": dataframe["pine_stop_long"].to_numpy(),
            "stop_short": dataframe["pine_stop_short"].to_numpy(),
        }

    def pine_script(self, broker, i, ctx):
        # if ((bullishEngulfing or C_LongLowerShadowBullish1) and inDateRange
        #        and cross(low, lower))
        #     strategy.entry("L", strategy.long, qty=1, stop=(low[1]))
        if ctx["long_entry"][i]:
            stop = float(ctx["stop_long"][i])
            if np.isfinite(stop):
                broker.entry("L", "long", qty=1.0, stop=stop)
        # if crossunder(close, upper*0.9985)
        #     strategy.close("L", comment = "L exit", qty_percent=1)
        if ctx["close_long"][i]:
            broker.close("L")

        # if (((bullishEngulfing == 0) or C_LongUpperShadowBearish) and
        #         inDateRange and cross(close, upper))
        #     strategy.entry("S", strategy.short, qty=1, stop=(high[1]))
        if ctx["short_entry"][i]:
            stop = float(ctx["stop_short"][i])
            if np.isfinite(stop):
                broker.entry("S", "short", qty=1.0, stop=stop)
        # if crossunder(lower*1.0015, close)
        #     strategy.close("S", comment = "S exit", qty_percent=1)
        if ctx["close_short"][i]:
            broker.close("S")
