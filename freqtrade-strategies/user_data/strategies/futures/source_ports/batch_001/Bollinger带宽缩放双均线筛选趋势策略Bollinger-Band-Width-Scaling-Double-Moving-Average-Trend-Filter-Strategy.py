"""Port of sources/SM_778e026eaa285a65.pine (batch_001/Bollinger带宽缩放双均线筛选趋势策略Bollinger-Band-Width-Scaling-Double-Moving-Average-Trend-Filter-Strategy.md).

Pine v2 (`//@version=2`, bare builtins). A Bollinger scalper on the chart
period with a higher-resolution trend filter:

    len           = 20          mult = 4          trendTimeFrame = 60
    out           = sma(src, len)
    stdOut        = stdev(close, len)
    bbUpper/bbLower      = out +/- stdOut*mult
    bbUpper2/bbLower2    = out +/- stdOut*(mult/2)
    bbUpperX2/bbLowerX2  = out +/- stdOut*mult*2
    bbWidth              = (bbUpper - bbLower) / out
    closeLongTerm = request.security(syminfo.tickerid, "60", close)
    smaLongTerm   = request.security(syminfo.tickerid, "60", sma(close, 20))
    trendUp   = useTrendFilter ? (closeLongTerm > smaLongTerm) : true
    trendDown = useTrendFilter ? (closeLongTerm < smaLongTerm) : true

    bearish = ((cross(close, bbUpper2) == 1) or (cross(close, out) == 1))
              and (close[1] > close) and trendDown
    bullish = ((cross(close, bbLower2) == 1) or (cross(close, out) == 1))
              and (close[1] < close) and trendUp

    closeBuy  = (high[1] > bbUpper[1]) and (close < bbUpper) and (close < open)
                and trendUp
    closeSell = (((low[1] < bbLower[1]) and (close > bbLower))
                 or ((low[2] < bbLower[2]) and (close[1] > bbLower[1])))
                and (close > open) and trendDown
    cutLossBuy  = iff(bbWidth > 0.005, low < bbLower and low[1] > bbLower[1],
                                     low < bbLowerX2 and low[1] > bbLowerX2[1])
                  and trendUp
    cutLossSell = iff(bbWidth > 0.005, high > bbUpper and high[1] < bbUpper[1],
                                     high > bbUpperX2 and high[1] < bbUpperX2[1])
                  and trendDown

    if (bullish) -> strategy.entry("Buy", strategy.long, comment="Buy")
    if (bearish) -> strategy.entry("Sell", strategy.short, comment="Sell")
    strategy.close("Buy", closeBuy or cutLossBuy)
    strategy.close("Sell", closeSell or cutLossSell)

The `strategy()` call declares only `title` and `overlay`, so Pine's documented
defaults apply and the port carries them explicitly: `strategy.fixed` / 1
contract, initial capital 1000000, commission 0%, pyramiding 0,
process_orders_on_close=false.

The `/*backtest` header declares `period: 1d` on Futures_Binance BTC_USDT, so
`timeframe` is "1d"; its `basePeriod: 1h` is the FMZ backtester's own
granularity for filling those daily bars, not the strategy's period.

`cross(a, b)` here is compared with `== 1`, which selects the cross-OVER arm
under either published reading of the helper (a 1/-1/0 integer, or the
boolean `crossover`), so the condition is unambiguous and is read as
`crossover`. See FIDELITY.

FIDELITY (the full list is in `source_fidelity_notes` below):

* `request.security(syminfo.tickerid, tostring(60), ...)` needs the same
  symbol's 60-MINUTE series (Pine's minute string "60" is Freqtrade's "1h").
  The Pine engine does not resample (PINE_SEMANTICS.md section 二.1), so the
  port supplies the aligned series itself through the data provider, exactly as
  batch_011/跨周期均线交易multiple-timeframe-trading.py does. When no 60-minute
  data is reachable the requested series stays na, which under Pine's
  na-compares-false rule makes trendUp/trendDown false and the source emits
  nothing; no hourly values are invented.
* The `iff(bbWidth > 0.005, A, B)` selector treats an na `bbWidth` (warmup) as
  false and takes branch B, as Pine's ternary does.
* The md prose describes a 20/60 double moving-average trend filter, a cross of
  short above long, and a stop "narrowed to half the lower band" when the band
  is narrow. The code has no 60-length MA at all, tests a level
  (`closeLongTerm > smaLongTerm`) rather than a cross, and narrows nothing --
  it *widens* the stop to `bbLowerX2` (2x mult) when `bbWidth <= 0.005`. The
  code is followed; the disagreements are recorded, not reconciled.
* The prose's "止损" (stop loss) items describe these band tests as stops. The
  code places no stop-loss order anywhere: cutLossBuy/cutLossSell feed
  `strategy.close`, i.e. a market close filled at the NEXT bar's open, not a
  protective resting level. Both close calls are evaluated every bar and simply
  re-place the same-id order (PINE_SEMANTICS.md 1.12).
* `comment="Buy"` / `comment="Sell"` are order metadata the engine does not
  model; they place no condition.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase

# Bar durations, used only to compare a requested bar's CLOSE with a chart
# bar's close. Pine's minute strings are the keys so the mapping stays legible.
_TIMEFRAME_SECONDS = {
    "1m": 60, "3m": 180, "5m": 300, "15m": 900, "30m": 1800,
    "1h": 3600, "2h": 7200, "4h": 14400, "6h": 21600, "8h": 28800, "12h": 43200,
    "1d": 86400, "3d": 259200, "1w": 604800,
}


def _bar_close_ns(index, seconds: int) -> np.ndarray:
    """Bar OPEN times shifted to their CLOSE, as UTC nanoseconds.

    Freqtrade timestamps a candle by its open. Normalising the unit and the
    timezone here lets two series loaded from different files compare; a
    tz-naive index is read as UTC.
    """
    stamps = pd.DatetimeIndex(index)
    if stamps.tz is not None:
        stamps = stamps.tz_convert("UTC").tz_localize(None)
    return np.asarray(stamps, dtype="datetime64[ns]") + np.timedelta64(seconds, "s")


class SMBollingerBandWidthScalingDoubleMovingAverageTrendFilter_778e02(PinePortBase, IStrategy):
    source_id = "SM_778e026eaa285a65"
    source_file = (
        "Bollinger带宽缩放双均线筛选趋势策略"
        "Bollinger-Band-Width-Scaling-Double-Moving-Average-Trend-Filter-Strategy.md"
    )
    timeframe = "1d"
    can_short = True
    source_defaults: dict = {
        "len": 20,
        "multiplier": 4,
        "trendTimeFrame": 60,
        "useTrendFilter": True,
        "src": "close",
    }
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    # No strategy.exit and no stop/limit leg on any order: both exits are
    # market closes projected as next-open signals, so there is no intrabar
    # level for custom_stoploss to mirror.
    source_reproduce_stops = False
    source_fidelity_notes = [
        "request.security(syminfo.tickerid, tostring(trendTimeFrame), close) and "
        "... , sma(close, 20)) need the same symbol's 60-MINUTE series (trendTimeFrame "
        "defaults to 60, and Pine's minute string '60' is Freqtrade's '1h'). The Pine "
        "engine does not resample (PINE_SEMANTICS.md section two.1), so the port "
        "supplies the aligned series itself through the data provider "
        "(informative_pairs pair+\"1h\" -> dp.get_pair_dataframe), the same way "
        "batch_011/跨周期均线交易multiple-timeframe-trading.py does.",
        "When no 60-minute data is reachable (no data provider, or no stored 1h "
        "candles for the pair) both requested series stay na, so trendUp/trendDown "
        "are false under Pine's na-compares-false rule and NEITHER entry can fire. "
        "That is the source's own behaviour with an unresolved request; no hourly "
        "values are invented. It is why the synthetic validate_pine frame (which has "
        "no data provider) reports no signals.",
        "Alignment is modelled as 'the most recent requested bar that had already "
        "closed at this chart bar's close', i.e. request.security's default "
        "barmerge.lookahead_off merge; Freqtrade timestamps bars by their OPEN, so "
        "both series are compared on their CLOSE times. The platform's merge instant "
        "for a LOWER-than-chart resolution request is not verified against its output.",
        "The 60-minute SMA is seeded from the first 60-minute bar the data provider "
        "returns, so early chart bars can carry a differently-seeded warmup value "
        "(startup_candle_count is 0).",
        "md prose disagreement 1: the prose says the trend filter is a 20-period and "
        "a 60-period moving average whose cross decides the trend. The code has no "
        "60-length MA; it compares the requested timeframe's CLOSE against a 20-bar "
        "SMA of that same requested timeframe, and it tests a LEVEL, not a cross.",
        "md prose disagreement 2: the prose says the stop is 'narrowed to half the "
        "lower band' when the band is narrow. The code's narrow-band branch uses "
        "bbLowerX2 = out - stdOut*multiplier*2, i.e. a stop TWICE as far away, not "
        "half. The code is followed; the prose is not reconciled.",
        "md prose disagreement 3: the prose says the entry triggers when price "
        "touches the lower band (long) or the upper band (short). The code's "
        "`cross(x, y) == 1` selects the cross-OVER arm only, and it tests the "
        "half-multiplier bands (bbLower2/bbUpper2) and the middle band, not the "
        "multiplier bands the prose describes.",
        "md prose disagreement 4: the prose's exit condition is 'touching the upper "
        "band or the short MA' for a long. The code's closeBuy is not a touch: it "
        "needs the previous bar's HIGH above the upper band, this bar's close back "
        "BELOW that band, a down candle, and the trend filter; and the 'short MA' "
        "(which is the middle band, sma(src, 20)) appears only in the ENTRY cross, "
        "never in closeBuy. closeSell is the mirrored one- or two-bar pattern.",
        "md prose disagreement 5: the prose calls the band tests in its items 3 and "
        "6 '止损' (stop loss). The code places NO stop-loss order anywhere: "
        "cutLossBuy/cutLossSell feed `strategy.close`, a MARKET close evaluated on "
        "the same bar and filled at the next bar's open, not a protective level "
        "resting in the market. There is no strategy.exit, so source_reproduce_stops "
        "is False and nothing is mirrored by custom_stoploss.",
        "`cross(a, b) == 1` is read as `crossover(a, b)`. Pine v2's helper returns "
        "1 for a cross over (and -1 for a cross under) under the integer reading, "
        "and is the boolean crossover under the alias reading; `== 1` selects the "
        "same bar under both, so no ambiguity reaches the signal. Same convention as "
        "batch_001/Hull-移动平均趋势跟踪策略...py.",
        "`iff(bbWidth > 0.005, A, B)` with an na bbWidth (warmup, because stdev/sma "
        "return na until their window is full) takes branch B, which is what Pine's "
        "ternary does with a false/na condition.",
        "stdev is Pine's population standard deviation (ddof=0); pine_ta.pine_stdev "
        "implements exactly that. sma/stdev are na until `len` bars have elapsed, and "
        "na anywhere in the window propagates.",
        "Both close statements are evaluated on EVERY bar (they are not inside an "
        "`if`), so the engine re-places the same-id close order each bar; a close "
        "whose entry id is not currently held is a Pine no-op and is not projected "
        "(PINE_SEMANTICS.md 1.12).",
        "comment=\"Buy\" / comment=\"Sell\" are order metadata only and carry no "
        "condition; they are not reproduced.",
        "Leverage, margin, liquidation, funding and the venue's contract-step "
        "rounding are not modelled; the rounding can differ from the engine's float "
        "quantity, which the chain verifier measures separately.",
    ]

    # `request.security(syminfo.tickerid, tostring(trendTimeFrame), ...)`.
    REQUESTED_TIMEFRAME = "1h"
    # Length of the requested-timeframe SMA, a literal in the source.
    REQUESTED_SMA_LENGTH = 20
    _requested_pair = ""

    # ---- request.security(syminfo.tickerid, "60", ...) --------------------
    def informative_pairs(self):
        """Ask the data provider for the same pair's 60-minute candles."""
        dp = getattr(self, "dp", None)
        if dp is None:
            return []
        try:
            pairs = dp.current_whitelist()
        except Exception:  # noqa: BLE001 - the request degrades to na
            return []
        return [(pair, self.REQUESTED_TIMEFRAME) for pair in pairs]

    def populate_indicators(self, dataframe, metadata):
        # pine_indicators receives no metadata, so the pair is stashed here for
        # the requested-series lookup; the base does everything else.
        self._requested_pair = (metadata or {}).get("pair", "")
        return super().populate_indicators(dataframe, metadata)

    def _requested_pair_name(self) -> str:
        """The symbol the requested series is for.

        The framework path carries it in `metadata`; an offline caller (the
        chain verifier) constructs the port without metadata, so the single
        whitelisted pair is used as the fallback. Both sides then resolve the
        SAME series instead of one of them silently running on na.
        """
        if self._requested_pair:
            return self._requested_pair
        dp = getattr(self, "dp", None)
        if dp is None:
            return ""
        try:
            pairs = dp.current_whitelist()
        except Exception:  # noqa: BLE001 - the request degrades to na
            return ""
        return pairs[0] if pairs else ""

    def _requested_frame(self):
        """The 60-minute candles of this symbol, or None when unavailable."""
        dp = getattr(self, "dp", None)
        pair = self._requested_pair_name()
        if dp is None or not pair:
            return None
        try:
            frame = dp.get_pair_dataframe(pair, self.REQUESTED_TIMEFRAME)
        except Exception:  # noqa: BLE001 - no stored candles: the request is na
            return None
        if frame is None or len(frame) == 0:
            return None
        return frame

    def _requested_series(self, dataframe) -> tuple:
        """(closeLongTerm, smaLongTerm) merged onto the chart bars.

        The requested expressions are evaluated ON the 60-minute series
        (`close`, and `sma(close, 20)` of the 60-minute closes), then merged
        onto each chart bar at that bar's close -- the newest 60-minute bar
        that had already closed. na before the requested series starts, or
        entirely when no 60-minute data is reachable.
        """
        na_series = pd.Series(np.nan, index=dataframe.index, dtype=float)
        chart_seconds = _TIMEFRAME_SECONDS.get(self.timeframe)
        if chart_seconds is None or not isinstance(dataframe.index, pd.DatetimeIndex):
            return na_series, na_series
        frame = self._requested_frame()
        if frame is None:
            return na_series, na_series
        try:
            if "date" in frame.columns:
                frame = frame.set_index("date")
            frame = frame.sort_index()
            requested_close_values = frame["close"].astype(float)
            requested_sma_values = ta.pine_sma(requested_close_values, self.REQUESTED_SMA_LENGTH)
            requested_close_ns = _bar_close_ns(
                frame.index, _TIMEFRAME_SECONDS[self.REQUESTED_TIMEFRAME]
            )
            chart_close_ns = _bar_close_ns(dataframe.index, chart_seconds)
            position = np.searchsorted(requested_close_ns, chart_close_ns, side="right") - 1
            found = position >= 0
            out = {}
            for name, values in (
                ("close", requested_close_values.to_numpy(dtype=float)),
                ("sma", requested_sma_values.to_numpy(dtype=float)),
            ):
                merged = np.full(len(dataframe), np.nan, dtype=float)
                merged[found] = values[position[found]]
                out[name] = pd.Series(merged, index=dataframe.index, dtype=float)
            return out["close"], out["sma"]
        except Exception:  # noqa: BLE001 - an unalignable frame degrades to na
            return na_series, na_series

    # ---- ta.* / bare builtins --------------------------------------------
    def pine_indicators(self, dataframe, params):
        close = dataframe["close"].astype(float)
        open_ = dataframe["open"].astype(float)
        high = dataframe["high"].astype(float)
        low = dataframe["low"].astype(float)
        length = int(params["len"])
        mult = float(params["multiplier"])
        use_trend_filter = bool(params["useTrendFilter"])

        # out = sma(src, len) -- src is an input.source defaulting to close.
        src = ta.pine_source(dataframe, params["src"]).astype(float)
        out = ta.pine_sma(src, length)
        # stdOut = stdev(close, len) -- always the CLOSE, not `src`.
        std_out = ta.pine_stdev(close, length)
        bb_upper = out + std_out * mult
        bb_lower = out - std_out * mult
        bb_upper2 = out + std_out * (mult / 2.0)
        bb_lower2 = out - std_out * (mult / 2.0)
        bb_upper_x2 = out + std_out * mult * 2.0
        bb_lower_x2 = out - std_out * mult * 2.0
        # bbWidth = (bbUpper - bbLower) / out
        bb_width = (bb_upper - bb_lower) / out

        close_long_term, sma_long_term = self._requested_series(dataframe)
        if use_trend_filter:
            trend_up = close_long_term > sma_long_term
            trend_down = close_long_term < sma_long_term
        else:
            trend_up = pd.Series(True, index=dataframe.index, dtype=bool)
            trend_down = pd.Series(True, index=dataframe.index, dtype=bool)

        # cross(close, X) == 1 -> the cross-over arm (see FIDELITY).
        cross_bb_upper2 = ta.pine_crossover(close, bb_upper2)
        cross_bb_lower2 = ta.pine_crossover(close, bb_lower2)
        cross_out = ta.pine_crossover(close, out)
        previous_close = close.shift(1)

        bearish = (
            (cross_bb_upper2 | cross_out)
            & (previous_close > close).fillna(False)
            & trend_down.fillna(False)
        )
        bullish = (
            (cross_bb_lower2 | cross_out)
            & (previous_close < close).fillna(False)
            & trend_up.fillna(False)
        )

        close_buy = (
            (high.shift(1) > bb_upper.shift(1)).fillna(False)
            & (close < bb_upper)
            & (close < open_)
            & trend_up.fillna(False)
        )
        close_sell = (
            (((low.shift(1) < bb_lower.shift(1)) & (close > bb_lower))
             | ((low.shift(2) < bb_lower.shift(2)) & (previous_close > bb_lower.shift(1))))
            .fillna(False)
            & (close > open_)
            & trend_down.fillna(False)
        )

        # cutLossBuy / cutLossSell: iff(bbWidth > 0.005, tight band, 2x band)
        wide_band = bb_width > 0.005
        cut_loss_buy_tight = (
            (low < bb_lower) & (low.shift(1) > bb_lower.shift(1)).fillna(False)
        )
        cut_loss_buy_wide = (
            (low < bb_lower_x2) & (low.shift(1) > bb_lower_x2.shift(1)).fillna(False)
        )
        cut_loss_buy = (
            cut_loss_buy_tight.where(wide_band, cut_loss_buy_wide).fillna(False)
            & trend_up.fillna(False)
        )
        cut_loss_sell_tight = (
            (high > bb_upper) & (high.shift(1) < bb_upper.shift(1)).fillna(False)
        )
        cut_loss_sell_wide = (
            (high > bb_upper_x2) & (high.shift(1) < bb_upper_x2.shift(1)).fillna(False)
        )
        cut_loss_sell = (
            cut_loss_sell_tight.where(wide_band, cut_loss_sell_wide).fillna(False)
            & trend_down.fillna(False)
        )

        dataframe["pine_out"] = out
        dataframe["pine_std_out"] = std_out
        dataframe["pine_bb_upper"] = bb_upper
        dataframe["pine_bb_lower"] = bb_lower
        dataframe["pine_bb_upper2"] = bb_upper2
        dataframe["pine_bb_lower2"] = bb_lower2
        dataframe["pine_bb_upper_x2"] = bb_upper_x2
        dataframe["pine_bb_lower_x2"] = bb_lower_x2
        dataframe["pine_bb_width"] = bb_width
        dataframe["pine_close_long_term"] = close_long_term
        dataframe["pine_sma_long_term"] = sma_long_term
        dataframe["pine_trend_up"] = trend_up.fillna(False)
        dataframe["pine_trend_down"] = trend_down.fillna(False)
        dataframe["pine_bullish"] = bullish
        dataframe["pine_bearish"] = bearish
        dataframe["pine_close_buy_or_cut"] = (close_buy | cut_loss_buy).fillna(False)
        dataframe["pine_close_sell_or_cut"] = (close_sell | cut_loss_sell).fillna(False)
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "bullish": dataframe["pine_bullish"].to_numpy(),
            "bearish": dataframe["pine_bearish"].to_numpy(),
            "close_buy": dataframe["pine_close_buy_or_cut"].to_numpy(),
            "close_sell": dataframe["pine_close_sell_or_cut"].to_numpy(),
        }

    def pine_script(self, broker, i, ctx):
        # if (bullish)
        #     strategy.entry("Buy", strategy.long, comment="Buy")
        if ctx["bullish"][i]:
            broker.entry("Buy", "long")
        # if (bearish)
        #     strategy.entry("Sell", strategy.short, comment="Sell")
        if ctx["bearish"][i]:
            broker.entry("Sell", "short")
        # strategy.close("Buy", closeBuy or cutLossBuy)
        broker.close("Buy", when=bool(ctx["close_buy"][i]))
        # strategy.close("Sell", closeSell or cutLossSell)
        broker.close("Sell", when=bool(ctx["close_sell"][i]))
