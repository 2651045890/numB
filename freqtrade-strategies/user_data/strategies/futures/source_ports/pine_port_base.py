"""Shared mixin for ports of Pine Script sources.

A port supplies only the Pine translation:

    class SMxxxx(PinePortBase, IStrategy):
        source_id = "SM_xxxxxxxxxxxxxxxx"
        source_file = "<original markdown file name>"
        timeframe = "1h"
        source_defaults = {...}

        def pine_indicators(self, dataframe, params): ...   # ta.* / bare builtins
        def pine_script(self, broker, i, ctx): ...          # strategy.* calls

Everything else -- Pine order timing, sizing, commission, pyramiding, stop
reproduction, the offline/live guard -- lives here so that a port cannot
silently diverge from the modelled engine by re-implementing plumbing.

`PinePortBase` deliberately does NOT inherit IStrategy: the batch runner
discovers strategies by looking for a direct IStrategy base, so a mixin keeps
the base class out of the inventory while every port stays discoverable via
`class Port(PinePortBase, IStrategy)`.
"""
from __future__ import annotations

import logging
from datetime import datetime

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

from pine_engine import (
    QTY_CASH,
    QTY_FIXED,
    QTY_PERCENT_OF_EQUITY,
    PineBrokerConfig,
    run_pine,
)

__all__ = ["PinePortBase", "source_qty_type_name"]


def source_qty_type_name(value: str) -> str:
    """Map a Pine `default_qty_type` expression onto the engine's constant."""
    text = str(value).strip()
    if text.endswith("percent_of_equity"):
        return QTY_PERCENT_OF_EQUITY
    if text.endswith("cash"):
        return QTY_CASH
    if text.endswith("fixed"):
        return QTY_FIXED
    raise ValueError(f"unrecognised default_qty_type {value!r}")


def _stake_schedule(entry_fills: list, index) -> dict:
    """Map each entry fill onto the candle time it filled at.

    Keys are tz-aware UTC so they compare equal to the `current_time` Freqtrade
    passes in, which `_pine_entry_notional` normalises the same way.
    """
    schedule: dict = {}
    for fill in entry_fills:
        bar = fill.get("bar")
        if bar is None or bar < 0 or bar >= len(index):
            continue
        stamp = pd.Timestamp(index[bar])
        if stamp.tzinfo is None:
            stamp = stamp.tz_localize("UTC")
        schedule.setdefault(stamp, float(fill["notional"]))
    return schedule


class PinePortBase:
    """Mixin that drives a Pine source port through Freqtrade's interfaces."""

    # ---- interface constants ports normally inherit unchanged -------------
    INTERFACE_VERSION = 3
    timeframe = "1h"
    can_short = True
    startup_candle_count = 0
    minimal_roi = {}
    # Freqtrade demands a finite stoploss. Pine's own exits arrive as signals
    # or as `pine_stop_level`; this is only the backstop when neither applies.
    stoploss = -0.99
    trailing_stop = False
    # Pine `strategy.exit(stop=...)` triggers inside the bar; a next-open exit
    # signal cannot express that. Routing the engine's stop level through
    # custom_stoploss is what makes those exits land on the same price.
    use_custom_stoploss = True
    process_only_new_candles = True
    use_exit_signal = True
    exit_profit_only = False
    ignore_roi_if_entry_signal = False
    position_adjustment_enable = False
    order_types = {
        "entry": "market",
        "exit": "market",
        "stoploss": "market",
        "stoploss_on_exchange": False,
    }
    order_time_in_force = {"entry": "GTC", "exit": "GTC"}

    # ---- source metadata, declared by each port ---------------------------
    source_id = ""
    source_file = ""
    source_defaults: dict = {}
    # Pine `strategy(...)` properties. Values here are the SOURCE's, not
    # Freqtrade defaults; unknown source values must remain None and be
    # reported as unmapped rather than filled in with framework defaults.
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    # The instrument's minimum price increment, which is what Pine's `profit=`
    # and `loss=` arguments are counted in. TradingView reads it off the symbol;
    # a source rarely states it, and BTC/USDT:USDT quotes in 0.1.
    source_mintick = 0.1
    source_initial_capital: float | None = None
    # Set False when the source has no stop-based exit the engine can mirror.
    source_reproduce_stops = True
    # Recorded per port: what could not be expressed, and why.
    source_fidelity_notes: list = []

    def __init__(self, config):
        from freqtrade.enums import RunMode

        runmode = config.get("runmode")
        if runmode in (RunMode.LIVE, RunMode.DRY_RUN):
            raise ValueError(
                f"{type(self).__name__} is an offline source port and refuses live/dry-run"
            )
        self._pine_stops: dict[str, pd.Series] = {}
        # The resting take-profit level, mirroring `_pine_stops`. Pine routes
        # both legs of an OCA exit through one call, so a port that reproduces
        # only the stop silently loses the profit leg.
        self._pine_takes: dict[str, pd.Series] = {}
        # Candle time -> the money the engine committed on that bar's entry.
        self._pine_stakes: dict[str, dict[pd.Timestamp, float]] = {}
        self._pine_stake_misses = 0
        self._pine_stake_shortfalls = 0
        self._pine_stake_vetoes = 0
        super().__init__(config)

    def _pine_entry_notional(self, pair: str, current_time) -> float | None:
        """The engine's committed stake for the entry filling at `current_time`."""
        stakes = self._pine_stakes.get(pair)
        if not stakes:
            return None
        timestamp = pd.Timestamp(current_time)
        if timestamp.tzinfo is None:
            timestamp = timestamp.tz_localize("UTC")
        return stakes.get(timestamp)

    # ---- parameter plumbing ----------------------------------------------
    def source_parameters(self) -> dict:
        values = dict(self.source_defaults)
        overrides = self.config.get("source_parameters", {})
        unknown = set(overrides) - set(values)
        if unknown:
            raise ValueError(f"Unknown source parameters: {sorted(unknown)}")
        values.update(overrides)
        return values

    def pine_broker_config(self, params: dict) -> PineBrokerConfig:
        if self.source_initial_capital is None:
            raise ValueError(
                f"{type(self).__name__} must declare source_initial_capital or set "
                "source_reproduce_equity=False; Freqtrade's wallet is not a substitute"
            )
        return PineBrokerConfig(
            initial_capital=float(self.source_initial_capital),
            default_qty_type=source_qty_type_name(self.source_qty_type),
            default_qty_value=float(self.source_qty_value),
            commission_percent=float(self.source_commission_percent),
            pyramiding=int(self.source_pyramiding),
            mintick=float(self.source_mintick),
        )

    # ---- contract each port implements ------------------------------------
    def pine_indicators(self, dataframe: pd.DataFrame, params: dict) -> pd.DataFrame:
        raise NotImplementedError(f"{type(self).__name__}.pine_indicators")

    def pine_context(self, dataframe: pd.DataFrame, params: dict) -> dict:
        """Columns the script reads at bar `i`. Defaults to the whole frame."""
        return {column: dataframe[column].to_numpy() for column in dataframe.columns}

    def pine_script(self, broker, i: int, ctx: dict) -> None:
        raise NotImplementedError(f"{type(self).__name__}.pine_script")

    # ---- Freqtrade driver --------------------------------------------------
    def populate_indicators(self, dataframe: pd.DataFrame, metadata: dict) -> pd.DataFrame:
        params = self.source_parameters()
        # Freqtrade's backtesting pipeline hands the frame in with a RANGE index
        # and the candle time in a `date` column, while dry-run and the strategy
        # tests pass a DatetimeIndex. Ports read Pine's `dayofweek`, `month` and
        # every `[1]`-style history reference off the index, so a range index
        # makes them compare calendar fields against 1970 epoch nanoseconds and
        # silently emit NOTHING -- a date-driven port backtests as a flat
        # strategy rather than failing loudly. Index by the real time for the
        # duration, then hand back the index the caller gave us.
        original_index = dataframe.index
        export_date = (
            not isinstance(original_index, pd.DatetimeIndex)
            and "date" in dataframe.columns
        )
        if export_date:
            dataframe = dataframe.set_index("date")
        prepared = self.pine_indicators(dataframe, params)
        ledger = run_pine(
            self.pine_broker_config(params), prepared, self.pine_script,
            self.pine_context(prepared, params),
        )
        # The engine's fills are keyed by bar POSITION, which is only meaningful
        # against this frame; map them onto candle time so custom_stake_amount --
        # which is handed a timestamp, not a row -- can find them. Two entries
        # filling on one bar collapse to the first, which is only reachable via
        # pyramiding and is not modelled yet.
        self._pine_stakes[metadata.get("pair", "")] = _stake_schedule(
            ledger.attrs.get("entry_fills") or [], prepared.index
        )
        # custom_stoploss and the ROI override resolve their level with
        # `asof(current_time)`, so these series have to be keyed by candle time,
        # not by row position. The take-profit series is built even when
        # `source_reproduce_stops` is False: that flag is about the STOP leg,
        # and a source with only a take-profit would otherwise lose it silently.
        index = prepared.index
        if isinstance(index, pd.DatetimeIndex) and index.tz is None:
            index = index.tz_localize("UTC")
        pair = metadata.get("pair", "")
        self._pine_takes[pair] = pd.Series(
            ledger["pine_limit_level"].to_numpy(), index=index
        )
        if self.source_reproduce_stops:
            self._pine_stops[pair] = pd.Series(
                ledger["pine_stop_level"].to_numpy(), index=index
            )
        result = prepared.join(ledger)
        if export_date:
            # set_index('date') consumed the column; Freqtrade still expects it.
            result = result.reset_index()
            result.index = original_index
        return result

    def populate_entry_trend(self, dataframe: pd.DataFrame, metadata: dict) -> pd.DataFrame:
        # Signals were produced by the Pine engine in populate_indicators; they
        # must not be re-derived here or the order timing would drift.
        return dataframe

    def populate_exit_trend(self, dataframe: pd.DataFrame, metadata: dict) -> pd.DataFrame:
        return dataframe

    def leverage(self, pair, current_time, current_rate, proposed_leverage,
                 max_leverage, entry_tag, side, **kwargs) -> float:
        """The engine models unlevered Pine spot-style sizing unless a port overrides."""
        return 1.0

    def _derived_stake(self, current_rate: float, leverage: float):
        """Re-derive the entry size from the live wallet, as a last resort.

        This is only correct for `fixed` and `cash` sizing, which do not depend
        on equity. `percent_of_equity` could not be reproduced this way even in
        principle -- see `custom_stake_amount`.
        """
        qty_type = source_qty_type_name(self.source_qty_type)
        if qty_type == QTY_FIXED:
            return float(self.source_qty_value) * current_rate / leverage
        if qty_type == QTY_PERCENT_OF_EQUITY:
            equity = self.wallets.get_total_stake_amount() if self.wallets else None
            if equity is None:
                return None
            return equity * float(self.source_qty_value) / 100.0
        return float(self.source_qty_value)  # QTY_CASH

    def custom_stake_amount(self, pair, current_time, current_rate, proposed_stake,
                            min_stake, max_stake, leverage, entry_tag, side, **kwargs):
        """Size the entry with the engine's own number for this fill.

        Pine sizes `percent_of_equity` off `strategy.equity` as of the bar the
        order was PLACED, and freezes the quantity before the next bar opens.
        Freqtrade instead calls this at the FILL bar and expects the strategy to
        size off the live wallet, so re-deriving the quantity here lands on a
        different basis: the two wallets drift apart, and because the drift
        compounds, a 100%-of-equity source eventually asks for more than the
        framework's wallet holds. Freqtrade answers that by skipping the entry,
        silently, and the rest of the backtest goes flat.

        The engine already computed the exact notional when it filled the order,
        so this returns that rather than an approximation of it.
        """
        required = self._pine_entry_notional(pair, current_time)
        if required is None:
            self._pine_stake_misses += 1
            required = self._derived_stake(current_rate, leverage)
            if required is None:
                return None
        if max_stake is not None and required > max_stake:
            # Freqtrade rounds every order to the venue's contract step, which
            # the engine cannot do -- the step is only known from the exchange
            # object at run time, and this method has no access to it. Each
            # round leaves the framework's wallet a hair away from the engine's
            # cash, and over a long run the gap reaches the point where the
            # engine's next order looks unfundable. Rounding that away is not
            # "hiding" a shortfall: a real one is orders of magnitude larger,
            # and is counted below instead.
            if required - max_stake <= 1e-4 * max(1.0, max_stake):
                required = max_stake
            else:
                # The engine can fund this entry and the framework cannot. That
                # is a real divergence, so count it instead of hiding it.
                self._pine_stake_shortfalls += 1
        if required > max_stake or (min_stake is not None and required < min_stake):
            # Refusing here does not fail the backtest: Freqtrade simply does
            # not open the trade, the framework's wallet and the engine's cash
            # go their separate ways, and every later fill is off. Say so on the
            # log, where the offline harness can pick it up and report the run
            # as vetoed rather than as a mysterious drift.
            self._pine_stake_vetoes += 1
            logger.warning(
                "SOURCE_STAKE_VETO t=%s required=%.8f max_stake=%s min_stake=%s",
                current_time, required, max_stake, min_stake,
            )
            return 0.0  # Never let Freqtrade fall back to its configured stake.
        return required

    def _pine_resting_time(self, current_time) -> pd.Timestamp:
        """`current_time` as a tz-aware Timestamp, the ledger's own key.

        No offset: the ledger's row for bar `t` IS bar `t`'s record, because
        the engine writes it from what it evaluated while bar `t` traded.
        """
        timestamp = pd.Timestamp(current_time)
        if timestamp.tzinfo is None:
            timestamp = timestamp.tz_localize("UTC")
        return timestamp

    def _pine_resting_level(self, series, current_time):
        """The level the engine acted on during `current_time`'s bar, or None.

        The engine records, on every bar, the exit levels it actually EVALUATED
        while that bar traded (`PineBroker.used_exit_levels`), and writes `nan`
        when it evaluated none. So the level in force is read positionally, as
        "the last bar at or before `current_time`" -- the bar's own record.

        Neither an `asof` nor a one-bar lag belongs here. `asof` skips NaN and
        returns the last *valid* value, so the bars in between two positions,
        where the source has no order at all, would quietly resurrect the
        previous position's level and take the new trade out at a price that
        belonged to a trade that had already closed (measured on
        SMDcaTakeProfit_dfa329, which closed a trade at the take-profit of the
        trade before it). A lag would instead look PAST the bar's own record,
        and miss the stops a source arms on the entry's own fill bar by writing
        `strategy.exit` next to `strategy.entry` (measured on
        SMEliEmaCross_48f1cc, whose every stop is such a same-bar stop).
        """
        if series is None or len(series) == 0:
            return None
        try:
            position = series.index.searchsorted(
                self._pine_resting_time(current_time), side="right"
            ) - 1
        except (KeyError, TypeError, ValueError):
            return None
        if position < 0:
            return None
        level = series.iloc[position]
        if level is None or not np.isfinite(level) or level <= 0:
            return None
        return float(level)

    def _pine_take_level(self, pair: str, current_time):
        """The take-profit the engine has resting at `current_time`, or None."""
        return self._pine_resting_level(self._pine_takes.get(pair), current_time)

    def _pine_roi_target(self, trade, current_time):
        """The engine's take-profit, expressed as this trade's profit ratio.

        Freqtrade decides a take-profit in two places -- whether the bar
        reached it, and what price to book -- and both are derived from a
        return ratio. `calc_profit_ratio` inverts exactly (Freqtrade's own
        `calc_close_rate_for_roi` is documented as matching it), so handing
        back the ratio the trade would have at the LEVEL makes the framework
        trigger on the level and fill AT the level, which is where the engine's
        resting limit fills.
        """
        level = self._pine_take_level(trade.pair, current_time)
        if level is None:
            return None
        # A level on the wrong side of the entry is not a take-profit; the
        # engine would have filled it on the fill bar, and treating it as an
        # ROI would exit every later bar at a locked-in loss.
        if trade.is_short:
            if level >= trade.open_rate:
                return None
        elif level <= trade.open_rate:
            return None
        try:
            return float(trade.calc_profit_ratio(level))
        except (KeyError, TypeError, ZeroDivisionError):
            return None

    def min_roi_reached_entry(self, trade, trade_dur, current_time):
        """Prefer the engine's take-profit over the (empty) `minimal_roi` table.

        `roi_entry` is deliberately `trade_dur`: the framework's
        `_get_close_rate_for_roi` treats a matching entry as a level that has
        only just come into force and, if the bar OPENED beyond it, books the
        open. That is the gap rule the engine now applies too -- a bar that
        gaps through a resting limit fills at its first tradeable price.
        """
        entry, roi = super().min_roi_reached_entry(trade, trade_dur, current_time)
        target = self._pine_roi_target(trade, current_time)
        if target is None:
            return entry, roi
        if roi is None or target < roi:
            return trade_dur, target
        return entry, roi

    def min_roi_reached(self, trade, current_profit, current_time) -> bool:
        """Trigger on the take-profit being TOUCHED, as Pine's limit order does.

        The base class compares with a strict `>`, but a resting limit fills
        when the price reaches it, not only when it passes it -- and on the bar
        whose high IS the level the two floats are equal, so `>` would drop
        exactly the bars the order should have filled on.
        """
        if super().min_roi_reached(trade, current_profit, current_time):
            return True
        target = self._pine_roi_target(trade, current_time)
        if target is None:
            return False
        return current_profit >= target

    def custom_stoploss(self, pair, trade, current_time, current_rate,
                        current_profit, after_fill, **kwargs):
        """Mirror the Pine engine's active stop so intrabar fills match.

        A Pine `strategy.exit(stop=...)` triggers inside the bar, which a
        next-open exit signal cannot reproduce. Returning the engine's stop
        level lets Freqtrade's stop machinery fire at the same price.
        """
        if not self.source_reproduce_stops:
            return None
        level = self._pine_resting_level(self._pine_stops.get(pair), current_time)
        if level is None:
            return None
        is_long = trade.is_short is False
        # Only tighten: a stop that would move against the position is ignored.
        if is_long and level >= current_rate:
            return None
        if (not is_long) and level <= current_rate:
            return None
        ratio = (level / current_rate) - 1.0
        # Freqtrade does not use this ratio as a price. `Trade.adjust_stop_loss`
        # turns it back into one with `current_rate * (1 -/+ |ratio|)` and then
        # rounds it to the venue's grid ONE-SIDEDLY -- ROUND_UP for a long,
        # ROUND_DOWN for a short, i.e. always toward the entry. The round trip
        # lands a hair (about 1e-16 relative) away from the level it started
        # from, and on a level that sits exactly on a grid point that hair is
        # enough for the rounding to step a whole tick: measured on
        # SMEliEmaCross_48f1cc, whose every stop is on the 0.1 grid and came back
        # one tick tighter than the source's. The bias below is 4e-5 of a tick at
        # BTC prices -- orders of magnitude above the float noise and far below
        # the grid -- so it can only put a value that was already ON a grid point
        # back onto it, and it does not move a level that is genuinely between
        # grid points.
        return ratio * (1.0 + 1e-9)

    # ---- provenance --------------------------------------------------------
    def source_provenance(self) -> dict:
        return {
            "source_id": self.source_id,
            "source_file": self.source_file,
            "class": type(self).__name__,
            "timeframe": self.timeframe,
            "qty_type": self.source_qty_type,
            "qty_value": self.source_qty_value,
            "commission_percent": self.source_commission_percent,
            "pyramiding": self.source_pyramiding,
            "initial_capital": self.source_initial_capital,
            "reproduce_stops": self.source_reproduce_stops,
            "fidelity_notes": list(self.source_fidelity_notes),
            "generated_at": datetime.now().isoformat(timespec="seconds"),
        }
