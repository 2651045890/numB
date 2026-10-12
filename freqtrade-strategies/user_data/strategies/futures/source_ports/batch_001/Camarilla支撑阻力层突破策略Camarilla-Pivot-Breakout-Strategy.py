"""Port of sources/SM_a8379a6f67d4b703.pine
(batch_001/Camarilla支撑阻力层突破策略Camarilla-Pivot-Breakout-Strategy.md).

Pine v2 (`//@version=2`, "Created by CristianD"). The script computes the
Camarilla pivot ladder from the CHART bar's own OHLC, asks for the DAILY value
of two of those levels one daily bar back, and trades a break of them:

    h4 = close + (high - low) * 1.1 / 2.0
    l4 = close - (high - low) * 1.1 / 2.0
    dtime_h4 = request.security(syminfo.tickerid, 'D', h4[1])
    dtime_l4 = request.security(syminfo.tickerid, 'D', l4[1])
    if close > dtime_h4
        strategy.entry("My Long Entry Id",  strategy.long)
    if close < dtime_l4
        strategy.entry("My Short Entry Id", strategy.short)

Everything the source computes besides `dtime_h4` / `dtime_l4` is dead code:
`EMA`, `pivot`, `range`, `h1..h6`, `l1..l6` and the eleven other `request.
security` lines are read only by commented-out `plot()` calls. They are still
computed here so the port carries the source's whole indicator set, but the
script reads only the two levels.

The source declares no `strategy()` properties beyond the title, so Pine's
documented defaults apply: initial_capital 1000000 USD, default_qty_type
`strategy.fixed`, default_qty_value 1, commission 0%, pyramiding 0,
process_orders_on_close=false. `can_short` is True: there IS a short entry.

FIDELITY (see `source_fidelity_notes` for the full list):

* `request.security` (PINE_SEMANTICS.md 2.1) is not something the engine
  resamples, so the port supplies the aligned daily series itself through the
  data provider, as the other multi-timeframe ports do.
* The source is v2, and Pine v2's `security()` has no `lookahead` argument
  because `barmerge.lookahead_on` IS its default (TradingView's migration
  guide: lookahead_on "is the default for Pine Script version 2"). So the
  requested expression is published for the whole of the daily bar it belongs
  to, starting at that bar's open -- and because the requested expression is
  itself `h4[1]`, a chart bar inside day D reads **h4 of day D-1**. That is the
  ordinary non-repainting `expr[1]` + lookahead_on idiom, and it is why the
  level is a completed day's level rather than one from the still-forming day.
* The daily ladder is built from the daily candles themselves, so the daily
  bar's own high/low/close enter the formula, not the chart bar's.
* No exit call of any kind exists in the source: a position is only ever
  closed by the opposite entry reversing it, so `source_reproduce_stops` is
  False and a position open at the end of the window stays open.
* Leverage, margin, liquidation and funding are not modelled; the venue's
  contract-step rounding is not modelled either, and `verify_chain` measures
  that separately rather than treating it as a signal difference.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase

# Bar durations in seconds, used only to compare a requested bar's OPEN with a
# chart bar's open. Pine's own strings are the keys so the mapping stays legible.
_TIMEFRAME_SECONDS = {
    "1m": 60, "3m": 180, "5m": 300, "15m": 900, "30m": 1800,
    "1h": 3600, "2h": 7200, "4h": 14400, "6h": 21600, "8h": 28800, "12h": 43200,
    "1d": 86400, "3d": 259200, "1w": 604800,
}


def _open_ns(index) -> np.ndarray:
    """Bar OPEN times as UTC nanoseconds.

    Freqtrade timestamps a candle by its open, which is the instant
    `barmerge.lookahead_on` publishes a higher-timeframe bar's value at. The
    conversion normalises the unit (pandas 2 can hand back us or ns) and the
    timezone, so two series loaded from different files still compare; a
    tz-naive index is read as UTC.
    """
    stamps = pd.DatetimeIndex(index)
    if stamps.tz is not None:
        stamps = stamps.tz_convert("UTC").tz_localize(None)
    return np.asarray(stamps, dtype="datetime64[ns]")


class SMCamarillaPivotBreakout_a8379a(PinePortBase, IStrategy):
    source_id = "SM_a8379a6f67d4b703"
    source_file = "Camarilla支撑阻力层突破策略Camarilla-Pivot-Breakout-Strategy.md"
    timeframe = "5m"
    can_short = True
    # The only `input()` in the file (`sd`) is commented out, so the source
    # has no parameters at all.
    source_defaults: dict = {}
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    # No strategy.exit / strategy.close / stop= / limit= anywhere: the only
    # order calls are the two market entries.
    source_reproduce_stops = False
    source_fidelity_notes = [
        "request.security(syminfo.tickerid, 'D', h4[1]) needs the same symbol's "
        "daily candles; the Pine engine does not resample (PINE_SEMANTICS.md 2.1), "
        "so the port supplies the aligned daily series itself through the data "
        "provider (informative_pairs pair+\"1d\" -> dp.get_pair_dataframe).",
        "The source is //@version=2, and Pine v2's security() has no `lookahead` "
        "argument because barmerge.lookahead_on is its default (TradingView Pine "
        "migration guide: lookahead_on is 'the default for Pine Script version 2'). "
        "lookahead_on publishes a daily bar's value for that entire day, starting at "
        "its open, so combining it with the source's own `[1]` offset means a chart "
        "bar inside day D reads h4 of day D-1 -- a completed day, not the forming "
        "one. Under lookahead_off the same source would read day D-2 instead; that "
        "reading is NOT what v2 does and is deliberately not used.",
        "The daily ladder is computed on the daily candles (that day's own high/"
        "low/close), then shifted one daily bar per the source's `[1]`. The original "
        "platform's merge instant is modelled from the documented rule, not verified "
        "against its output.",
        "Daily bars are the exchange's own daily candles as stored for the pair "
        "(UTC); PINE_SEMANTICS.md 3.4 records that a non-UTC exchange would shift "
        "the day boundary and this port does not compensate for it.",
        "The daily series preferred is the pair's stored 1d candles, which extend "
        "beyond the chart window and therefore cover the requested value for the "
        "window's first day. When no daily store is reachable -- validate_pine runs "
        "the port with no data provider at all -- the daily bars are derived from the "
        "chart frame itself (same series for every fully covered day); nothing is "
        "invented for a day the chart data does not cover, and a bar with no daily "
        "level places no order because Pine's na comparison is false.",
        "The first chart bars of the window can carry a differently-seeded daily "
        "series: the requested daily frame is whatever the store holds, but a chart "
        "bar in the very first day of the chart window still resolves to day D-1, "
        "which is present, so no boundary is invented. startup_candle_count is 0, "
        "as in the shared base.",
        "EMA / pivot / range / h1..h3 / h5 / h6 / l1..l3 / l5 / l6 and the eleven "
        "other request.security lines are dead code in the source -- every reader of "
        "them is a commented-out plot(). They are computed here for completeness "
        "only; the script reads just dtime_h4 and dtime_l4.",
        "No exit call exists anywhere in the source: a position is closed only by "
        "the opposite entry reversing it, so source_reproduce_stops is False and a "
        "position open at the end of the data stays open.",
        "ta.ema seeding follows pine_ta's documented first-value model, but the EMA "
        "is dead code here so no trade behaviour depends on it.",
        "The source declares no strategy() properties beyond title/shorttitle/"
        "overlay, so Pine's documented defaults are used: fixed / 1 contract, "
        "initial capital 1000000, commission 0%, pyramiding 0.",
        "Leverage, margin, liquidation and funding are not modelled; the venue's "
        "contract-step rounding is not modelled either and is measured separately "
        "by verify_chain.",
    ]

    # `request.security(syminfo.tickerid, 'D', ...)`: the same pair's daily series.
    REQUESTED_TIMEFRAME = "1d"
    _requested_pair = ""

    # ---- request.security(syminfo.tickerid, 'D', ...) ---------------------
    def informative_pairs(self):
        """Ask the data provider for the same pair's daily candles."""
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
        # the requested-series lookup. Everything else stays with the base.
        self._requested_pair = (metadata or {}).get("pair", "")
        return super().populate_indicators(dataframe, metadata)

    def _stored_daily(self):
        """The same pair's stored daily candles, or None when unreachable.

        The pair comes from `populate_indicators` when the framework called it,
        and otherwise from the data provider's whitelist -- the engine side runs
        `pine_indicators` directly (verify_chain.engine_trades) and never calls
        `populate_indicators`, so relying on the stash alone would leave the
        engine's requested series na while the framework's was real, and the two
        sides would disagree by construction.
        """
        dp = getattr(self, "dp", None)
        if dp is None:
            return None
        pair = self._requested_pair
        if not pair:
            try:
                whitelist = dp.current_whitelist()
            except Exception:  # noqa: BLE001 - no whitelist: the request is na
                whitelist = []
            pair = whitelist[0] if whitelist else ""
        if not pair:
            return None
        try:
            frame = dp.get_pair_dataframe(pair, self.REQUESTED_TIMEFRAME)
        except Exception:  # noqa: BLE001 - no stored candles: the request is na
            return None
        if frame is None or len(frame) == 0:
            return None
        if "date" in frame.columns:
            frame = frame.set_index("date")
        return frame.sort_index()

    def _requested_frame(self, dataframe):
        """The daily series `request.security(..., 'D', ...)` reads.

        The stored daily candles are preferred: they are the platform's own
        daily series and they extend beyond the chart window, which is what the
        requested value for the window's FIRST day needs. When no daily store is
        reachable -- `validate_pine` runs the port with no data provider at all
        -- the daily bars are derived from the chart frame itself, which is the
        same series for every day the window fully covers. Only that first
        (partial) day can differ, and nothing is invented for a day the chart
        data does not cover.
        """
        stored = self._stored_daily()
        if stored is not None:
            return stored
        if not isinstance(dataframe.index, pd.DatetimeIndex) or len(dataframe) == 0:
            return None
        try:
            day = pd.DatetimeIndex(dataframe.index).normalize()
        except (TypeError, ValueError):
            return None
        bars = dataframe.copy()
        bars.index = day
        daily = bars.resample("1D").agg(
            {"open": "first", "high": "max", "low": "min", "close": "last",
             "volume": "sum"}
        )
        return daily.dropna(subset=["open", "high", "low", "close"])

    def _daily_shifted(self, dataframe, level):
        """`request.security(syminfo.tickerid, 'D', level([1]))` on the chart bars.

        `level` is called on the DAILY frame. The result is shifted one daily bar
        -- the source's `[1]` -- and then merged onto the chart bars under
        `barmerge.lookahead_on`: a chart bar whose open falls inside daily bar D
        reads the value as of D, i.e. the shifted level at D. na where the daily
        series has no value yet, or entirely when daily data is unreachable.
        """
        na_series = pd.Series(np.nan, index=dataframe.index, dtype=float)
        if self.timeframe not in _TIMEFRAME_SECONDS:
            return na_series
        if not isinstance(dataframe.index, pd.DatetimeIndex):
            return na_series
        daily = self._requested_frame(dataframe)
        if daily is None:
            return na_series
        try:
            values = level(daily).shift(1).to_numpy(dtype=float)
            daily_open = _open_ns(daily.index)
            chart_open = _open_ns(dataframe.index)
            # The daily bar containing this chart bar. lookahead_on publishes a
            # daily bar's value from that bar's open, so containment (not the
            # most recent CLOSED bar) is the right lookup.
            position = np.searchsorted(daily_open, chart_open, side="right") - 1
            out = np.full(len(dataframe), np.nan, dtype=float)
            found = position >= 0
            out[found] = values[position[found]]
            return pd.Series(out, index=dataframe.index, dtype=float)
        except Exception:  # noqa: BLE001 - an unalignable frame degrades to na
            return na_series

    # ---- ta.* / bare builtins ---------------------------------------------
    def pine_indicators(self, dataframe, params):
        high = dataframe["high"].astype(float)
        low = dataframe["low"].astype(float)
        close = dataframe["close"].astype(float)
        span = high - low

        # EMA = ema(close,3)  -- computed by the source, read by nothing.
        dataframe["pine_ema3"] = ta.pine_ema(close, 3)

        # Camarilla ladder, on the chart bar's own OHLC.
        #   pivot = (high + low + close) / 3.0
        #   range = high - low
        #   h5 = (high / low) * close ; h4 = close + range * 1.1 / 2.0
        #   h3 = close + range * 1.1 / 4.0 ; h2 = close + range * 1.1 / 6.0
        #   h1 = close + range * 1.1 / 12.0
        #   l1 = close - range * 1.1 / 12.0 ; l2 = close - range * 1.1 / 6.0
        #   l3 = close - range * 1.1 / 4.0  ; l4 = close - range * 1.1 / 2.0
        #   h6 = h5 + 1.168 * (h5 - h4)
        #   l5 = close - (h5 - close)       ; l6 = close - (h6 - close)
        dataframe["pine_pivot"] = (high + low + close) / 3.0
        dataframe["pine_range"] = span
        h5 = (high / low) * close
        h4 = close + span * 1.1 / 2.0
        h3 = close + span * 1.1 / 4.0
        h2 = close + span * 1.1 / 6.0
        h1 = close + span * 1.1 / 12.0
        l1 = close - span * 1.1 / 12.0
        l2 = close - span * 1.1 / 6.0
        l3 = close - span * 1.1 / 4.0
        l4 = close - span * 1.1 / 2.0
        h6 = h5 + 1.168 * (h5 - h4)
        dataframe["pine_h5"] = h5
        dataframe["pine_h4"] = h4
        dataframe["pine_h3"] = h3
        dataframe["pine_h2"] = h2
        dataframe["pine_h1"] = h1
        dataframe["pine_l1"] = l1
        dataframe["pine_l2"] = l2
        dataframe["pine_l3"] = l3
        dataframe["pine_l4"] = l4
        dataframe["pine_h6"] = h6
        dataframe["pine_l5"] = close - (h5 - close)
        dataframe["pine_l6"] = close - (h6 - close)

        # The daily ladder. Every one of the source's thirteen request.security
        # lines is reproduced; only dtime_h4 / dtime_l4 are ever read.
        daily_levels = {
            "dtime_pivot": lambda d: (d["high"] + d["low"] + d["close"]) / 3.0,
            "dtime_h6": lambda d: (
                (d["high"] / d["low"]) * d["close"]
                + 1.168 * ((d["high"] / d["low"]) * d["close"]
                           - (d["close"] + (d["high"] - d["low"]) * 1.1 / 2.0))
            ),
            "dtime_h5": lambda d: (d["high"] / d["low"]) * d["close"],
            "dtime_h4": lambda d: d["close"] + (d["high"] - d["low"]) * 1.1 / 2.0,
            "dtime_h3": lambda d: d["close"] + (d["high"] - d["low"]) * 1.1 / 4.0,
            "dtime_h2": lambda d: d["close"] + (d["high"] - d["low"]) * 1.1 / 6.0,
            "dtime_h1": lambda d: d["close"] + (d["high"] - d["low"]) * 1.1 / 12.0,
            "dtime_l1": lambda d: d["close"] - (d["high"] - d["low"]) * 1.1 / 12.0,
            "dtime_l2": lambda d: d["close"] - (d["high"] - d["low"]) * 1.1 / 6.0,
            "dtime_l3": lambda d: d["close"] - (d["high"] - d["low"]) * 1.1 / 4.0,
            "dtime_l4": lambda d: d["close"] - (d["high"] - d["low"]) * 1.1 / 2.0,
            "dtime_l5": lambda d: d["close"] - (
                ((d["high"] / d["low"]) * d["close"]) - d["close"]
            ),
            "dtime_l6": lambda d: d["close"] - (
                (
                    (d["high"] / d["low"]) * d["close"]
                    + 1.168 * ((d["high"] / d["low"]) * d["close"]
                               - (d["close"] + (d["high"] - d["low"]) * 1.1 / 2.0))
                ) - d["close"]
            ),
        }
        for name, level in daily_levels.items():
            dataframe[f"pine_{name}"] = self._daily_shifted(dataframe, level)

        # longCondition = close > dtime_h4 ; shortCondition = close < dtime_l4
        dataframe["pine_long_condition"] = (
            close > dataframe["pine_dtime_h4"]
        ).fillna(False)
        dataframe["pine_short_condition"] = (
            close < dataframe["pine_dtime_l4"]
        ).fillna(False)
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "close": dataframe["close"].to_numpy(dtype=float),
            "dtime_h4": dataframe["pine_dtime_h4"].to_numpy(dtype=float),
            "dtime_l4": dataframe["pine_dtime_l4"].to_numpy(dtype=float),
            "long_condition": dataframe["pine_long_condition"].to_numpy(),
            "short_condition": dataframe["pine_short_condition"].to_numpy(),
        }

    # ---- strategy.* -------------------------------------------------------
    def pine_script(self, broker, i, ctx):
        # longCondition = close > dtime_h4
        # if (longCondition)
        #     strategy.entry("My Long Entry Id", strategy.long)
        if ctx["long_condition"][i]:
            broker.entry("My Long Entry Id", "long")
        # shortCondition = close < dtime_l4
        # if (shortCondition)
        #     strategy.entry("My Short Entry Id", strategy.short)
        if ctx["short_condition"][i]:
            broker.entry("My Short Entry Id", "short")
