"""Port of sources/SM_c1865c57b267b918.pine (batch_001/200均线VWAPMFI趋势跟踪策略-200-EMA-VWAP-MFI-Trend-Following-Strategy.md).

Pine v5, a five-way conjunction on each side:

    buffer            = input.float(0.2, title="EMA Buffer Percentage", step=0.1) / 100
    higherTimeframe   = input.timeframe("15", title="Higher Timeframe")
    mfiBuyThreshold   = input(60, title="MFI Buy Threshold")
    mfiSellThreshold  = input(40, title="MFI Sell Threshold")
    consecutiveCloses = input.int(1, title="Consecutive Closes for Confirmation")

    ema200         = ta.ema(close, 200)
    emaBufferedHigh = ema200 * (1 + buffer)
    emaBufferedLow  = ema200 * (1 - buffer)
    emaHigher      = request.security(syminfo.tickerid, higherTimeframe, ta.ema(close, 200))

    vwap = ta.vwap(hlc3)
    mfi  = ta.mfi(close, 14)                 // 14 is a literal, not an input

    isUpTrend   = ta.rising(close, consecutiveCloses)
    isDownTrend = ta.falling(close, consecutiveCloses)

    longCondition  = close > emaBufferedHigh and close > vwap
                     and mfi > mfiBuyThreshold and close > emaHigher and isUpTrend
    shortCondition = close < emaBufferedLow  and close < vwap
                     and mfi < mfiSellThreshold and close < emaHigher and isDownTrend

    if (longCondition)
        strategy.entry("Buy", strategy.long)
    if (shortCondition)
        strategy.entry("Sell", strategy.short)

`strategy()` declares `overlay=true, pyramiding=0`, so the port carries
`source_pyramiding = 0` (which is also Pine's default) and Pine's documented
defaults for everything else: `strategy.fixed` / 1 contract, initial capital
1000000, commission 0%, `process_orders_on_close=false`. Neither entry passes
`qty`, so the default quantity supplies it.

The `/*backtest` header declares `period: 1d` on Futures_Binance BTC_USDT, so
`timeframe` is "1d".

There is no `strategy.close` / `strategy.exit` and no stop or limit in the
source, so `source_reproduce_stops` is False: a position is only closed by the
opposite entry reversing it, and a position open at the end of the window stays
open.

`REQUEST.SECURITY` IS THE PART THE SHARED ENGINE DOES NOT RESAMPLE
(PINE_SEMANTICS.md 2.1), so this port supplies the aligned series itself, the
way a `request.security` port is required to (tier 4). `higherTimeframe`
defaults to "15" -- fifteen MINUTES, i.e. a LOWER timeframe than the 1d chart --
so the value cannot be aggregated out of the chart's own bars the way a
higher-timeframe request can: it is read from the same symbol's stored 15-minute
candles through the data provider (`informative_pairs` + `dp.get_pair_dataframe`).
The expression is evaluated ON the requested series (`ta.ema(close, 200)` over
15-minute closes) and merged onto the chart bars at their CLOSE, which is
`request.security`'s default `barmerge.lookahead_off` merge: the newest requested
bar that had already closed. No 15-minute value is invented when the data is
unreachable -- the series is na, the comparison is false under Pine's
na-compares-false rule, and the corresponding entry simply does not fire.

FIDELITY:

* `ta.vwap` is not exposed by the shared layer and is session-anchored, which
  the offline engine does not model as a feature of its own. It is written out
  from its definition -- the volume-weighted average of `hlc3` accumulated from
  the start of the current session -- with the session taken as the UTC calendar
  day. On a 1d chart each session holds exactly one bar, so the accumulated
  average IS that bar's `hlc3`; the general form is kept so the column means the
  same thing if the port is ever run on an intraday frame. The session boundary
  and the exchange's session definition are platform behaviour that is modelled,
  not certified.
* `ta.mfi` is likewise not in the shared layer and is written out from the
  documented equivalent code (the same `_pine_mfi` used by the other batch_001
  AlphaTrend ports). A window whose turnover sums to zero yields 50 rather than
  a 0/0 nan; a window with no negative money flow gives `upper/lower = inf` and
  therefore 100. Pine's own float-division-by-zero convention is not published
  and this choice is recorded as a modelling choice, not as certified equality.
* `ta.rising` / `ta.falling` are not exposed by pine_ta and are translated from
  Pine's definition: source[i] > source[i+1] (resp. <) for every i in
  0..length-1, so the steps are CONSECUTIVE and equality breaks the run, with na
  comparisons false as Pine treats them. With the declared
  `consecutiveCloses = 1` each is a single `close > close[1]` /
  `close < close[1]` test.
* `ema200` is `pine_ta.pine_ema`, seeded with the first non-na observation and
  with na observations not advancing the recursion. TradingView does not publish
  its seeding rule; PINE_SEMANTICS.md 3.1 records this as a parity risk rather
  than a certified equivalence. It also means the 200-bar warm-up starts at the
  first bar of the frame the backtest loads, so the first entries can only occur
  around bar 200 of the window.
* The 15-minute EMA200 is seeded from the first 15-minute bar the data provider
  hands over, so early chart bars can carry a differently-seeded `emaHigher`;
  the request is only reachable in practice once the daily 200-EMA warm-up is
  over, by which point a 200-bar 15-minute EMA (about 50 hours) has converged.
* `buffer` is `input.float(0.2, ...) / 100`: the raw input default 0.2 is what
  `source_defaults` carries, and the port applies the same `/100` conversion.
* Every comparison is a Pine na-aware one: `close > x` on an na `x` is false, to
  which pandas' NaN comparisons agree. Both `if` blocks are independent (not
  `else if`) and are kept in the source's written order.
* The md reproduces the source verbatim (the prose restates the same five
  conditions); no md/source disagreement was found.
* Leverage, margin, liquidation, funding and the venue's contract-step rounding
  are not modelled; the chain verifier measures the rounding separately.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase

# Bar durations, used only to compare a requested bar's CLOSE with a chart
# bar's close. Keys are the Freqtrade timeframe names the provider uses.
_TIMEFRAME_SECONDS = {
    "1m": 60, "3m": 180, "5m": 300, "15m": 900, "30m": 1800,
    "1h": 3600, "2h": 7200, "4h": 14400, "6h": 21600, "8h": 28800, "12h": 43200,
    "1d": 86400, "3d": 259200, "1w": 604800,
}


def _pine_timeframe_minutes(value) -> int | None:
    """A Pine `input.timeframe` string as minutes, or None when unrepresentable.

    Pine spells sub-hour timeframes as bare minutes ('15', '60'), and coarser
    ones with a unit suffix ('1D', '1W'). Anything else (seconds, months) is
    left to the dataprovider, which is asked for the string as written.
    """
    text = str(value).strip().upper()
    if not text:
        return None
    if text.isdigit():
        return int(text)
    unit, number = text[-1], text[:-1]
    number = int(number) if number.isdigit() else 1
    if unit == "S":
        return max(1, number // 60)
    if unit == "H":
        return number * 60
    if unit == "D":
        return number * 1440
    if unit == "W":
        return number * 10080
    return None


def _freqtrade_timeframe(minutes: int | None) -> str | None:
    """The Freqtrade name for a minute count ('15' -> '15m', '60' -> '1h')."""
    if minutes is None or minutes <= 0:
        return None
    if minutes % 1440 == 0:
        return f"{minutes // 1440}d"
    if minutes % 60 == 0:
        return f"{minutes // 60}h"
    return f"{minutes}m"


def _bar_close_ns(index, seconds: int) -> np.ndarray:
    """Bar OPEN times shifted to their CLOSE, as UTC nanoseconds.

    Freqtrade timestamps a candle by its open. Normalising the unit and the
    timezone lets two series loaded from different files compare; a tz-naive
    index is read as UTC.
    """
    stamps = pd.DatetimeIndex(index)
    if stamps.tz is not None:
        stamps = stamps.tz_convert("UTC").tz_localize(None)
    return np.asarray(stamps, dtype="datetime64[ns]") + np.timedelta64(seconds, "s")


def _pine_vwap(source: pd.Series, volume: pd.Series, index) -> pd.Series:
    """Pine `ta.vwap(source)`: the session-anchored volume-weighted average price.

        vwap = sum(source * volume) / sum(volume)   since the session started

    The session is taken as the UTC calendar day, which is the exchange's own
    trading day for the 24/7 crypto pairs this corpus trades. On a 1d chart a
    session holds exactly one bar, so the result is that bar's `hlc3`; the
    accumulation is kept general so the column keeps its meaning on an intraday
    frame.
    """
    stamps = pd.DatetimeIndex(index)
    session = stamps.floor("1D")
    turnover = (source.astype(float) * volume.astype(float))
    volume = volume.astype(float)
    numerator = turnover.groupby(session).cumsum()
    denominator = volume.groupby(session).cumsum()
    with np.errstate(divide="ignore", invalid="ignore"):
        value = numerator / denominator
    return value.where(denominator != 0.0)


def _pine_mfi(source: pd.Series, volume: pd.Series, length: int) -> pd.Series:
    """Pine `ta.mfi(source, length)`, from the documented equivalent code.

    Shared verbatim with the batch_001 AlphaTrend ports so that one `ta.mfi`
    reading serves the whole batch. A bar whose `ta.change(source)` is na (the
    first bar) fails both comparisons, so Pine's ternary takes its false branch
    and the bar's turnover is counted on BOTH sides -- matched here by numpy's
    False for a NaN comparison. A window whose turnover sums to zero is 50
    (the documented convention in this batch); a window with no negative money
    flow leaves `upper/lower` at inf and therefore 100.
    """
    change = source.diff()
    values = source.to_numpy(dtype=float)
    volume = volume.to_numpy(dtype=float)
    upper_term = np.where((change <= 0).to_numpy(), 0.0, values) * volume
    lower_term = np.where((change >= 0).to_numpy(), 0.0, values) * volume
    rolling = {"min_periods": length}
    upper = pd.Series(upper_term, index=source.index).rolling(length, **rolling).sum()
    lower = pd.Series(lower_term, index=source.index).rolling(length, **rolling).sum()
    with np.errstate(divide="ignore", invalid="ignore"):
        ratio = upper / lower
        value = 100.0 - 100.0 / (1.0 + ratio)
    return value.where(upper + lower != 0.0, 50.0)


def _rising(series: pd.Series, length: int) -> pd.Series:
    """Pine `ta.rising`: strictly higher on each of the last `length` steps.

    Pine's documented test is "is now rising for `length` bars long" --
    source[i] > source[i+1] for every i in 0..length-1 -- so the steps are
    CONSECUTIVE and equality breaks the run. na on either side of a comparison
    makes it false, as Pine treats na comparisons.
    """
    rising = pd.Series(True, index=series.index)
    for step in range(int(length)):
        rising &= series.shift(step) > series.shift(step + 1)
    return rising


def _falling(series: pd.Series, length: int) -> pd.Series:
    """Pine `ta.falling`: strictly lower on each of the last `length` steps."""
    falling = pd.Series(True, index=series.index)
    for step in range(int(length)):
        falling &= series.shift(step) < series.shift(step + 1)
    return falling


class SM200EmaVwapMfi_c1865c(PinePortBase, IStrategy):
    source_id = "SM_c1865c57b267b918"
    source_file = "200均线VWAPMFI趋势跟踪策略-200-EMA-VWAP-MFI-Trend-Following-Strategy.md"
    timeframe = "1d"
    can_short = True
    source_defaults: dict = {
        "buffer": 0.2,
        "higherTimeframe": "15",
        "mfiBuyThreshold": 60,
        "mfiSellThreshold": 40,
        "consecutiveCloses": 1,
    }
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    # `strategy(..., pyramiding=0)` -- declared in the source, Pine's default too.
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    source_reproduce_stops = False
    source_fidelity_notes = [
        "request.security(syminfo.tickerid, higherTimeframe, ta.ema(close, 200)) "
        "requests 15-MINUTE data onto the 1d chart -- a LOWER timeframe, so it "
        "cannot be aggregated out of the chart's own bars. The port reads the "
        "same symbol's stored 15-minute candles through the data provider "
        "(informative_pairs -> dp.get_pair_dataframe), evaluates ta.ema(close, "
        "200) ON that series, and merges it onto the chart bars at their CLOSE "
        "(request.security's default barmerge.lookahead_off merge): the newest "
        "requested bar that had already closed.",
        "When no 15-minute data is reachable (no data provider, or no stored "
        "15-minute candles for the pair) emaHigher stays na, the comparison is "
        "false under Pine's na-compares-false rule, and the entry does not "
        "fire. No 15-minute value is invented.",
        "The engine harness calls pine_indicators() without metadata, so the "
        "pair is taken from metadata when present and otherwise from the data "
        "provider's whitelist; both paths ask for the same pair, and the "
        "whitelist holds exactly one pair in this project's single-pair runs.",
        "ta.vwap is session-anchored and is not in the shared layer; it is "
        "written out from its definition with the session taken as the UTC "
        "calendar day. On a 1d chart every session holds one bar, so the column "
        "is that bar's hlc3. The session boundary is modelled, not certified.",
        "ta.mfi is not in the shared layer; _pine_mfi is the same reading used "
        "by the batch_001 AlphaTrend ports. A zero-turnover window yields 50; a "
        "window with no negative money flow leaves upper/lower at inf and "
        "yields 100. Pine's own float-division-by-zero convention is not "
        "published -- recorded as a modelling choice.",
        "ta.rising / ta.falling are translated from Pine's definition "
        "(consecutive strict steps; equality breaks the run; na compares "
        "false). With consecutiveCloses = 1 each is a single close > close[1] / "
        "close < close[1] test.",
        "ta.ema is pine_ta.pine_ema, seeded with the first non-na observation "
        "(an unpublished TradingView rule; PINE_SEMANTICS.md 3.1). The daily "
        "200-EMA therefore needs 200 bars of the loaded frame before any entry "
        "can fire.",
        "The 15-minute EMA200 is seeded from the first 15-minute bar the "
        "provider hands over, so early chart bars can carry a differently-seeded "
        "emaHigher; a 200-bar 15-minute EMA (about 50 hours) has converged long "
        "before the daily warm-up ends.",
        "The synthetic harness (validate_pine) installs no data provider, so "
        "there is no 15-minute series to request and the port reports "
        "ran_but_never_signalled_on_synthetic_data -- the honest consequence of "
        "the na rule above, not a defect. With the provider the chain harness "
        "installs (LocalDataProvider over the stored 15-minute candles) "
        "pine_ema_higher is populated on every bar, the metadata path and the "
        "whitelist fallback produce identical values, and the port trades.",
        "buffer is input.float(0.2, ...)/100: source_defaults carries the raw "
        "input default 0.2 and the port applies the same /100 conversion. "
        "mfiLength (14) is a literal in the source, not an input, and stays a "
        "literal here.",
        "The source has no strategy.close / strategy.exit and no stop or limit, "
        "so source_reproduce_stops is False and the only exit is the opposite "
        "entry reversing the position.",
        "plot / plotshape / hline(50) are display-only and are not reproduced.",
        "The md reproduces the source verbatim and restates the same five "
        "conditions; no md/source disagreement.",
        "Leverage, margin, liquidation, funding and contract-step rounding are "
        "not modelled.",
    ]

    # ---- request.security(syminfo.tickerid, higherTimeframe, ...) ---------
    REQUESTED_TIMEFRAME = "15m"
    _requested_pair = ""

    def informative_pairs(self):
        """Ask the data provider for the same pair's 15-minute candles."""
        dp = getattr(self, "dp", None)
        if dp is None:
            return []
        try:
            minutes = _pine_timeframe_minutes(
                self.source_parameters().get("higherTimeframe", "15")
            )
            timeframe = _freqtrade_timeframe(minutes)
            if timeframe is None:
                return []
            pairs = dp.current_whitelist()
        except Exception:  # noqa: BLE001 - the request degrades to na
            return []
        return [(pair, timeframe) for pair in pairs]

    def populate_indicators(self, dataframe, metadata):
        # pine_indicators receives no metadata, so the pair is stashed here for
        # the requested-series lookup. Everything else stays with the base.
        self._requested_pair = (metadata or {}).get("pair", "")
        return super().populate_indicators(dataframe, metadata)

    def _requested_frame(self):
        """The requested timeframe's candles of this symbol, or None."""
        dp = getattr(self, "dp", None)
        if dp is None:
            return None
        pair = self._requested_pair
        if not pair:
            # The offline engine calls pine_indicators() without metadata, but
            # installs a provider whose whitelist names the pair being run.
            try:
                whitelist = dp.current_whitelist()
            except Exception:  # noqa: BLE001
                return None
            pair = whitelist[0] if whitelist else ""
        if not pair:
            return None
        minutes = _pine_timeframe_minutes(
            self.source_parameters().get("higherTimeframe", "15")
        )
        timeframe = _freqtrade_timeframe(minutes)
        if timeframe is None:
            return None
        try:
            frame = dp.get_pair_dataframe(pair, timeframe)
        except Exception:  # noqa: BLE001 - no stored candles: the request is na
            return None
        if frame is None or len(frame) == 0:
            return None
        return frame, timeframe

    def _requested_ema(self, dataframe, length):
        """`request.security(syminfo.tickerid, higherTimeframe, ta.ema(close, 200))`.

        The expression is evaluated ON the 15-minute closes and merged onto the
        chart bars at their close (lookahead_off), i.e. the newest 15-minute bar
        that had already closed when the daily bar closed. na where the
        requested series has no value yet, or entirely when the 15-minute data
        is unavailable.
        """
        na_series = pd.Series(np.nan, index=dataframe.index, dtype=float)
        chart_seconds = _TIMEFRAME_SECONDS.get(self.timeframe)
        if chart_seconds is None or not isinstance(dataframe.index, pd.DatetimeIndex):
            return na_series
        found = self._requested_frame()
        if found is None:
            return na_series
        frame, timeframe = found
        requested_seconds = _TIMEFRAME_SECONDS.get(timeframe)
        if requested_seconds is None:
            return na_series
        try:
            if "date" in frame.columns:
                frame = frame.set_index("date")
            frame = frame.sort_index()
            ema = ta.pine_ema(frame["close"].astype(float), length)
            requested_close = _bar_close_ns(frame.index, requested_seconds)
            chart_close = _bar_close_ns(dataframe.index, chart_seconds)
            # The most recent requested bar that had already closed: na before
            # the requested series starts, which is what request.security gives.
            position = np.searchsorted(requested_close, chart_close, side="right") - 1
            out = np.full(len(dataframe), np.nan, dtype=float)
            values = ema.to_numpy(dtype=float)
            available = position >= 0
            out[available] = values[position[available]]
            return pd.Series(out, index=dataframe.index, dtype=float)
        except Exception:  # noqa: BLE001 - unalignable frame degrades to na
            return na_series

    # ---- ta.* / bare builtins ---------------------------------------------
    def pine_indicators(self, dataframe, params):
        close = dataframe["close"].astype(float)
        volume = dataframe["volume"].astype(float)
        # buffer = input.float(0.2, ...) / 100
        buffer = float(params["buffer"]) / 100.0
        buy_threshold = float(params["mfiBuyThreshold"])
        sell_threshold = float(params["mfiSellThreshold"])
        consecutive = int(params["consecutiveCloses"])

        ema200 = ta.pine_ema(close, 200)
        dataframe["pine_ema200"] = ema200
        dataframe["pine_ema_buffered_high"] = ema200 * (1 + buffer)
        dataframe["pine_ema_buffered_low"] = ema200 * (1 - buffer)

        # emaHigher = request.security(syminfo.tickerid, higherTimeframe,
        #                              ta.ema(close, 200))
        dataframe["pine_ema_higher"] = self._requested_ema(dataframe, 200)

        # vwap = ta.vwap(hlc3) -- hlc3 is Pine's default source for ta.vwap.
        vwap = _pine_vwap(ta.pine_source(dataframe, "hlc3"), volume, dataframe.index)
        dataframe["pine_vwap"] = vwap

        # mfi = ta.mfi(close, 14) -- 14 is a literal in the source.
        dataframe["pine_mfi"] = _pine_mfi(close, volume, 14)

        is_up_trend = _rising(close, consecutive)
        is_down_trend = _falling(close, consecutive)
        dataframe["pine_is_up_trend"] = is_up_trend
        dataframe["pine_is_down_trend"] = is_down_trend

        ema_high = dataframe["pine_ema_buffered_high"]
        ema_low = dataframe["pine_ema_buffered_low"]
        mfi = dataframe["pine_mfi"]
        higher = dataframe["pine_ema_higher"]
        # longCondition = close > emaBufferedHigh and close > vwap
        #                 and mfi > mfiBuyThreshold and close > emaHigher
        #                 and isUpTrend
        # shortCondition = close < emaBufferedLow and close < vwap
        #                 and mfi < mfiSellThreshold and close < emaHigher
        #                 and isDownTrend
        # Each comparison is na-aware the Pine way: an na operand compares false.
        long_condition = (
            (close > ema_high) & (close > vwap) & (mfi > buy_threshold)
            & (close > higher) & is_up_trend
        )
        short_condition = (
            (close < ema_low) & (close < vwap) & (mfi < sell_threshold)
            & (close < higher) & is_down_trend
        )
        dataframe["pine_long_condition"] = long_condition.fillna(False).astype(bool)
        dataframe["pine_short_condition"] = short_condition.fillna(False).astype(bool)
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "long_condition": dataframe["pine_long_condition"].to_numpy(dtype=bool),
            "short_condition": dataframe["pine_short_condition"].to_numpy(dtype=bool),
        }

    def pine_script(self, broker, i, ctx):
        # if (longCondition)
        #     strategy.entry("Buy", strategy.long)
        if ctx["long_condition"][i]:
            broker.entry("Buy", "long")
        # if (shortCondition)
        #     strategy.entry("Sell", strategy.short)
        if ctx["short_condition"][i]:
            broker.entry("Sell", "short")
