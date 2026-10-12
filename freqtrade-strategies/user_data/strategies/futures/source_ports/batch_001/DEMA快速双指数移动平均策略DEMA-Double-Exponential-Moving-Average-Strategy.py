"""Port of sources/SM_8d81ba5de9256626.pine (batch_001/DEMA快速双指数移动平均策略DEMA-Double-Exponential-Moving-Average-Strategy.md).

Pine v5 mixed with v4 spellings (the file carries no `//@version`, yet uses
`ta.ema` / `request.security` and v4's `transp=`). A fast/slow DEMA cross, where
BOTH DEMA series are requested from a 120-minute series while the chart runs on
daily bars:

    fastPeriod = 32
    slowPeriod = 2
    res        = "120"

    demaFast = request.security(syminfo.tickerid, res,
                                2 * ta.ema(close, fastPeriod)
                                    - ta.ema(ta.ema(close, fastPeriod), fastPeriod))
    demaSlow = request.security(syminfo.tickerid, res,
                                2 * ta.ema(close, slowPeriod)
                                    - ta.ema(ta.ema(close, slowPeriod), slowPeriod))

    buy  = ta.crossover(demaSlow, demaFast)
    sell = ta.crossunder(demaSlow, demaFast)

    strategy.entry("BUY",  strategy.long,  1, when = buy)
    strategy.entry("SELL", strategy.short, 1, when = sell)

Both entries pass `qty = 1` EXPLICITLY, so the declared
`default_qty_type = strategy.percent_of_equity` / `default_qty_value = 100` is
never exercised: every entry is one contract. `pyramiding = 10` IS declared
(Pine's default is 0), so up to ten same-direction entries may stack; with no
exit call anywhere, a position is only ever reversed by the opposite entry.

`strategy()` also declares `initial_capital = 1000`, commission
(percent, 0.2), `shorttitle` and `overlay = false`. `slippage` is not declared.

The header declares `period: 1d` on Futures_Binance BTC_USDT, so `timeframe` is
"1d"; `basePeriod: 1h` is the FMZ backtester's fill granularity.

`request.security` IS NOT MODELLED BY THE ENGINE (PINE_SEMANTICS.md 2.1 -- it does
not resample), so the port supplies the aligned series itself through the data
provider, the same way the repo's other multi-timeframe port does. The 120-minute
series is taken from stored candles when it exists and otherwise BUILT from the
finest stored series by aggregating bars into 120-minute buckets aligned to the
UTC epoch (open = first, high = max, low = min, close = last, volume = sum),
which is how a 120-minute chart is constructed. The DEMA is then evaluated ON
that series and merged onto each chart bar at its close, i.e. the newest
120-minute bar that had already closed -- `request.security`'s default
`barmerge.lookahead_off`. When no 120-minute series can be built at all the two
DEMAs stay na, `ta.crossover` is false on na, and no entry is placed: na is what
the platform hands back for an unresolved request, and no values are invented.

FIDELITY:

* `slippage` is not declared by this source, so nothing is dropped there.
* The requested series starts where the stored candles start, not where the
  original platform's history starts, so early chart bars can carry a
  differently-seeded DEMA; `startup_candle_count` is 0.
* `ta.ema` seeding follows pine_ta's documented first-value model
  (PINE_SEMANTICS.md 3.1), applied here to BOTH the 120-minute closes and the
  inner EMA of the DEMA.
* `qty = 1` per entry against `initial_capital = 1000`: one BTC contract at any
  price in this window is worth far more than the declared wallet, so
  `custom_stake_amount` reports a shortfall against the venue's maximum and
  every framework entry is vetoed (`SOURCE_STAKE_VETO`, PINE_SEMANTICS.md 1.5 /
  1.6). The engine has no cash constraint and trades the source's orders; the
  divergence is a framework boundary, not a port choice, and
  `source_initial_capital` is NOT raised to hide it.
* `bgcolor(buy[1] ? ... : na, transp=0)` and the `plot()` calls are display-only
  and place no condition.
* Leverage, margin, liquidation, funding and the venue's contract-step rounding
  are not modelled; the chain verifier measures the rounding separately.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase

# Bar durations, used to compare a requested bar's CLOSE with a chart bar's
# close and to choose the aggregation bucket. Pine's own strings are the keys.
_TIMEFRAME_SECONDS = {
    "1m": 60, "3m": 180, "5m": 300, "15m": 900, "30m": 1800,
    "1h": 3600, "2h": 7200, "4h": 14400, "6h": 21600, "8h": 28800, "12h": 43200,
    "1d": 86400, "3d": 259200, "1w": 604800,
}


def _bar_close_ns(index, seconds: int) -> np.ndarray:
    """Bar OPEN times shifted to their CLOSE, as UTC nanoseconds.

    Freqtrade timestamps a candle by its open. The conversion normalises both
    the unit (pandas 2 can hand back us or ns) and the timezone, so two series
    loaded from different files still compare; a tz-naive index is read as UTC.
    """
    stamps = pd.DatetimeIndex(index)
    if stamps.tz is not None:
        stamps = stamps.tz_convert("UTC").tz_localize(None)
    return np.asarray(stamps, dtype="datetime64[ns]") + np.timedelta64(seconds, "s")


def _aggregate(frame: pd.DataFrame, target_seconds: int) -> pd.DataFrame:
    """Finest stored bars -> `target_seconds` bars, bucketed from the UTC epoch.

    A 120-minute chart's bars open at 00:00, 02:00, ... UTC, which is what
    `origin="epoch"` + `label="left"` produces. Empty buckets are dropped so a
    gap in the finer series does not become a phantom bar.
    """
    if "date" in frame.columns:
        frame = frame.set_index("date")
    frame = frame.sort_index()
    index = pd.DatetimeIndex(frame.index)
    if index.tz is None:
        index = index.tz_localize("UTC")
    frame = frame.copy()
    frame.index = index
    grouped = frame.resample(
        pd.Timedelta(seconds=target_seconds), origin="epoch", label="left", closed="left"
    )
    out = pd.DataFrame(
        {
            "open": grouped["open"].first(),
            "high": grouped["high"].max(),
            "low": grouped["low"].min(),
            "close": grouped["close"].last(),
            "volume": grouped["volume"].sum(),
        }
    )
    return out.dropna(subset=["open", "high", "low", "close"])


class SMDema_8d81ba(PinePortBase, IStrategy):
    source_id = "SM_8d81ba5de9256626"
    source_file = "DEMA快速双指数移动平均策略DEMA-Double-Exponential-Moving-Average-Strategy.md"
    timeframe = "1d"
    can_short = True
    source_defaults = {
        # fastPeriod = input(defval = 32, title = "DEMA FAST Period", minval = 2)
        "fastPeriod": 32,
        # slowPeriod = input(defval = 2, title = "DEMA SLOW Period", minval = 1)
        "slowPeriod": 2,
        # res = input(title="Resolution  - not lower than chart", defval="120")
        "res": "120",
    }
    # Both entries pass qty = 1, so this declaration is never exercised; it is
    # carried because the source declares it. Pine's default_qty_value is 1.
    source_qty_type = "percent_of_equity"
    source_qty_value = 100.0
    # commission_type = strategy.commission.percent, commission_value = 0.2.
    source_commission_percent = 0.2
    # pyramiding = 10 is declared by the source; Pine's default is 0.
    source_pyramiding = 10
    source_initial_capital = 1000.0
    # No strategy.close / strategy.exit: only the opposite entry reverses.
    source_reproduce_stops = False
    source_fidelity_notes = [
        "request.security(syminfo.tickerid, res, ...) is not modelled by the "
        "engine (PINE_SEMANTICS.md 2.1): the port supplies the aligned 120-minute "
        "series itself through the data provider, using stored 2h candles when "
        "they exist and otherwise aggregating the finest stored series into "
        "120-minute buckets aligned to the UTC epoch (open=first, high=max, "
        "low=min, close=last, volume=sum).",
        "The pair for the requested series is taken from the data provider's "
        "whitelist when no metadata is present: the chain verifier runs the engine "
        "side by wiring port.dp and calling pine_indicators directly, so metadata "
        "never arrives. Without that resolution the engine would read na while the "
        "framework resolved the series, and the two sides would disagree by "
        "construction rather than over the source's logic.",
        "The venue stores no native 120-minute candles for this pair, so the "
        "requested series is the 2h aggregation of the stored 1h candles; the "
        "source's own chart had a native 120-minute series, so the requested bars "
        "themselves are reconstructed rather than read.",
        "Merge timing: the requested value lands on a chart bar at that bar's "
        "CLOSE, i.e. the newest 120-minute bar that had already closed, matching "
        "request.security's default barmerge.lookahead_off. Freqtrade timestamps "
        "candles by their open, so both series are compared on their close times. "
        "The original platform's merge instant was not verified against its output.",
        "When no 120-minute series can be obtained the two DEMAs stay na, "
        "ta.crossover/ta.crossunder are false on na, and no entry is placed -- "
        "which is what the platform returns for an unresolved request. No "
        "120-minute values are invented from the chart timeframe.",
        "Both entries pass qty = 1 explicitly, so the declared "
        "default_qty_type=percent_of_equity / default_qty_value=100 is never "
        "exercised; every entry is one contract.",
        "qty = 1 against initial_capital = 1000: one BTC contract is worth far "
        "more than the declared wallet, so custom_stake_amount reports a "
        "shortfall against the venue's maximum and every framework entry is "
        "vetoed (SOURCE_STAKE_VETO; PINE_SEMANTICS.md 1.5 / 1.6). The engine has "
        "no cash constraint and trades the source's orders. source_initial_capital "
        "is NOT raised to paper over this.",
        "pyramiding = 10 is declared by the source (Pine's default is 0), so up "
        "to ten same-direction entries may stack.",
        "There is no exit call anywhere in the source, so "
        "source_reproduce_stops is False and a position is only reversed by the "
        "opposite entry.",
        "The requested series starts where the stored candles start, not where the "
        "platform's history starts, so early chart bars can carry a "
        "differently-seeded DEMA (startup_candle_count is 0).",
        "ta.ema seeding follows pine_ta.pine_ema (first non-na observation seeds "
        "the recursion; PINE_SEMANTICS.md 3.1), applied to the 120-minute closes "
        "and to the inner EMA of each DEMA. TradingView's seeding is unpublished.",
        "The file carries no //@version directive yet mixes v5 forms (ta.ema, "
        "request.security) with v4 ones (the bare `transp=` argument, v4-style "
        "positional strategy.entry). The calls used have no v4-vs-v5 semantic "
        "difference, so nothing turns on the annotation.",
        "bgcolor(buy[1] ? ... : na, transp=0) and the plot() calls are display-only "
        "and place no condition.",
        "Leverage, margin, liquidation, funding and the venue's contract-step "
        "rounding are not modelled; the chain verifier measures that rounding "
        "separately rather than treating it as a signal difference.",
    ]

    # `request.security(syminfo.tickerid, "120", ...)`: Pine's minutes-based
    # string for the series Freqtrade names "2h".
    REQUESTED_TIMEFRAME = "2h"
    # Finer series, best first, used only to build the requested one when the
    # venue stores no native 2h candles.
    _FALLBACK_TIMEFRAMES = ("1h", "30m", "15m", "5m")
    _requested_pair = ""

    # ---- request.security(syminfo.tickerid, res, expr) ---------------------
    def informative_pairs(self):
        """Ask the data provider for the same pair's 120-minute candles."""
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

    def _requested_frame(self):
        """The 120-minute candles of this symbol, or None when unavailable."""
        dp = getattr(self, "dp", None)
        if dp is None:
            return None
        if not self._requested_pair:
            # The chain verifier runs the engine side without metadata: it wires
            # `port.dp` and calls pine_indicators directly, so `metadata["pair"]`
            # never arrives and the requested series has to come from the
            # provider's own whitelist. Without this the engine side would read
            # na while the framework side resolved the series, and the two
            # sides would disagree by construction.
            self._requested_pair = self._whitelist_pair(dp)
        if not self._requested_pair:
            return None
        try:
            frame = dp.get_pair_dataframe(self._requested_pair, self.REQUESTED_TIMEFRAME)
        except Exception:  # noqa: BLE001 - no stored candles: the request is na
            frame = None
        if frame is not None and len(frame) > 0:
            return frame
        return self._built_frame(dp)

    @staticmethod
    def _whitelist_pair(dp) -> str:
        """The symbol this run is trading, read off the data provider."""
        try:
            pairs = dp.current_whitelist()
        except Exception:  # noqa: BLE001 - no whitelist: the request is na
            return ""
        return str(pairs[0]) if pairs else ""

    def _built_frame(self, dp):
        """Build the missing 120-minute series from the finest stored candles."""
        target = _TIMEFRAME_SECONDS[self.REQUESTED_TIMEFRAME]
        for source_timeframe in self._FALLBACK_TIMEFRAMES:
            try:
                frame = dp.get_pair_dataframe(self._requested_pair, source_timeframe)
            except Exception:  # noqa: BLE001 - try the next finer series
                continue
            if frame is None or len(frame) == 0:
                continue
            try:
                return _aggregate(frame, target)
            except Exception:  # noqa: BLE001 - an unusable frame degrades to na
                continue
        return None

    def _requested_dema(self, dataframe, length):
        """`request.security(syminfo.tickerid, "120", 2*ema(c,L) - ema(ema(c,L),L))`.

        The expression is evaluated ON the requested series, so both EMAs are
        taken over the 120-minute closes (the inner one on the outer EMA's own
        output), then merged onto the chart bars at their close. na where the
        requested series has no value yet, or entirely when it is unavailable.
        """
        na_series = pd.Series(np.nan, index=dataframe.index, dtype=float)
        chart_seconds = _TIMEFRAME_SECONDS.get(self.timeframe)
        if chart_seconds is None or not isinstance(dataframe.index, pd.DatetimeIndex):
            return na_series
        frame = self._requested_frame()
        if frame is None or len(frame) == 0:
            return na_series
        try:
            if "date" in frame.columns:
                frame = frame.set_index("date")
            frame = frame.sort_index()
            outer = ta.pine_ema(frame["close"].astype(float), length)
            dema = 2.0 * outer - ta.pine_ema(outer, length)
            requested_close = _bar_close_ns(
                frame.index, _TIMEFRAME_SECONDS[self.REQUESTED_TIMEFRAME]
            )
            chart_close = _bar_close_ns(dataframe.index, chart_seconds)
            # The most recent requested bar that had already closed: na before
            # the requested series starts, which is what request.security gives.
            position = np.searchsorted(requested_close, chart_close, side="right") - 1
            out = np.full(len(dataframe), np.nan, dtype=float)
            values = dema.to_numpy(dtype=float)
            found = position >= 0
            out[found] = values[position[found]]
            return pd.Series(out, index=dataframe.index, dtype=float)
        except Exception:  # noqa: BLE001 - unalignable frame degrades to na
            return na_series

    def pine_indicators(self, dataframe, params):
        fast_period = int(params["fastPeriod"])
        slow_period = int(params["slowPeriod"])
        dema_fast = self._requested_dema(dataframe, fast_period)
        dema_slow = self._requested_dema(dataframe, slow_period)
        dataframe["pine_dema_fast"] = dema_fast
        dataframe["pine_dema_slow"] = dema_slow
        # buy = ta.crossover(demaSlow, demaFast) / sell = ta.crossunder(...)
        dataframe["pine_buy"] = ta.pine_crossover(dema_slow, dema_fast).astype(bool)
        dataframe["pine_sell"] = ta.pine_crossunder(dema_slow, dema_fast).astype(bool)
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "buy": dataframe["pine_buy"].to_numpy(),
            "sell": dataframe["pine_sell"].to_numpy(),
        }

    def pine_script(self, broker, i, ctx):
        # strategy.entry("BUY", strategy.long, 1, when = buy)
        # `when` gates the call; the third positional argument is qty = 1.
        if ctx["buy"][i]:
            broker.entry("BUY", "long", qty=1.0)
        # strategy.entry("SELL", strategy.short, 1, when = sell)
        if ctx["sell"][i]:
            broker.entry("SELL", "short", qty=1.0)
