"""Pine Script `strategy.*` broker semantics, emulated bar by bar.

Purpose: a source port must reproduce Pine's *order timing*, not merely its
signals. This module models the parts of TradingView's strategy engine that
change trade outcomes:

* Market orders placed while processing bar `t` fill at the OPEN of bar `t+1`.
* Stop / limit orders rest and are checked against bar `t+1`'s high/low. A stop
  that gaps through fills at the open; otherwise at the stop price. A limit
  fills at the limit price unless the bar gaps better, then at the open.
* `strategy.entry` in the opposite direction reverses the position.
* `pyramiding=N` allows N additional entries in the same direction (Pine's
  default is 0, i.e. one entry per direction).
* `strategy.exit` is an OCA group: stop, limit, trail and profit/loss targets
  are evaluated together and the first to trigger closes the whole entry.
* Sizing follows `default_qty_type` / `default_qty_value`.
* Commission is charged in percent of turnover on both sides.

UNMODELLED (recorded per port in strategy_migration/PINE_SEMANTICS.md):
margin calls, slippage beyond the modelled fill price, bar magnifier /
lower-timeframe fills, `strategy.risk.*` rules, and strategy-calculator
rounding to a broker's contract size.

This engine is a modelled re-implementation, not TradingView's code. A port
that uses it is "implemented" and "runs"; it is NOT "certified equivalent"
until compared trade-by-trade against the original platform output.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from math import floor
from typing import Callable

import numpy as np
import pandas as pd

# Pine's default_qty_type constants, by the names sources use.
QTY_FIXED = "fixed"
QTY_PERCENT_OF_EQUITY = "percent_of_equity"
QTY_CASH = "cash"


@dataclass
class PineOrder:
    """A resting or just-filled Pine order."""

    order_id: str
    direction: str  # 'long' | 'short' | 'flat'
    kind: str  # 'market' | 'stop' | 'limit' | 'exit' | 'close'
    qty: float
    placed_bar: int
    stop: float | None = None
    limit: float | None = None
    from_entry: str | None = None
    # Pine's `profit` / `loss` arguments: distances in TICKS from the entry
    # price, so they only become a level once the entry has filled.
    profit_ticks: float | None = None
    loss_ticks: float | None = None
    trail_points: float | None = None
    trail_offset: float | None = None
    filled_bar: int | None = None
    fill_price: float | None = None
    cancelled_bar: int | None = None
    oca_group: str | None = None
    # Running best price since trailing activation, so the trail ratchets the
    # way Pine's does instead of resetting on every bar.
    trail_extreme: float | None = None
    trail_armed: bool = False
    # Set when Pine refuses the order at CREATION (pyramiding), as opposed to
    # `cancelled_bar`, which is `strategy.cancel`. A blocked order never fills.
    blocked_bar: int | None = None


@dataclass
class PineTrade:
    """A completed round trip."""

    entry_bar: int
    exit_bar: int
    entry_price: float
    exit_price: float
    qty: float
    direction: str
    profit: float
    entry_id: str


@dataclass
class PineBrokerConfig:
    initial_capital: float = 1_000_000.0
    default_qty_type: str = QTY_FIXED
    default_qty_value: float = 1.0
    commission_percent: float = 0.0
    pyramiding: int = 0
    currency_conversion: float = 1.0
    # The instrument's minimum price increment, which is what Pine's `profit`
    # and `loss` arguments are counted in. TradingView takes it from the symbol;
    # an offline engine has to be told. BTC/USDT:USDT quotes in 0.1.
    mintick: float = 0.1


@dataclass
class PineBroker:
    """Bar-driven emulation of Pine's `strategy.*` namespace.

    Usage inside a port:

        def signals(broker, i, ctx):
            if ctx["buy"][i]:
                broker.entry("Long", "long", when=True)
            ...

        ledger = run_pine(broker_config, dataframe, signals)
    """

    config: PineBrokerConfig
    position: float = 0.0  # signed size, in contracts/units
    avg_price: float = 0.0
    cash: float = 0.0
    equity: float = 0.0
    open_profit: float = 0.0
    orders: list[PineOrder] = field(default_factory=list)
    trades: list[PineTrade] = field(default_factory=list)
    # Entry fills in money terms, so a port can size the framework's order from
    # the source's own arithmetic instead of re-deriving it. See
    # _record_entry_fill.
    entry_fills: list[dict] = field(default_factory=list)
    _entry_ids: dict[str, float] = field(default_factory=dict)
    _open_entries: list[dict] = field(default_factory=list)
    _bar: int = -1
    _bar_high: float = np.nan
    _bar_low: float = np.nan
    _bar_open: float = np.nan
    _bar_close: float = np.nan
    _pending: list[PineOrder] = field(default_factory=list)
    # Orders created on the bar being processed. `run_pine` projects signals
    # from these, and cannot use a `_pending` slice: `_place` replaces same-id
    # exit orders, so the list can shrink while the bar is being processed.
    _placed_this_bar: list[PineOrder] = field(default_factory=list)
    # (stop, limit, trail) of every exit order EVALUATED on the bar being
    # processed. `used_exit_levels` reduces this to the two levels a framework
    # needs to apply during that bar.
    _levels_used: list[tuple] = field(default_factory=list)
    _position_before_bar: float = 0.0
    realized_profit: float = 0.0
    _barrier_reason: str | None = None

    def __post_init__(self) -> None:
        self.cash = self.config.initial_capital
        self.equity = self.config.initial_capital
        if self.config.default_qty_type not in (QTY_FIXED, QTY_PERCENT_OF_EQUITY, QTY_CASH):
            raise ValueError(f"unsupported default_qty_type {self.config.default_qty_type!r}")
        if self.config.pyramiding < 0:
            raise ValueError("pyramiding must be >= 0")

    # ---- sizing -----------------------------------------------------------
    def _size_for(self, price: float) -> float:
        cfg = self.config
        if not np.isfinite(price) or price <= 0:
            return 0.0
        if cfg.default_qty_type == QTY_FIXED:
            return float(cfg.default_qty_value)
        if cfg.default_qty_type == QTY_PERCENT_OF_EQUITY:
            notional = self.equity * float(cfg.default_qty_value) / 100.0
            return notional / price
        if cfg.default_qty_type == QTY_CASH:
            return float(cfg.default_qty_value) / price
        raise ValueError(cfg.default_qty_type)

    # ---- Pine API surface -------------------------------------------------
    def entry(self, order_id: str, direction: str, qty: float | None = None,
              when: bool = True, stop: float | None = None,
              limit: float | None = None, oca_name: str | None = None) -> None:
        if not when or direction not in ("long", "short", "flat"):
            return
        self._place(PineOrder(order_id, direction, "market" if stop is None and limit is None
                              else ("stop" if stop is not None else "limit"),
                              qty if qty is not None else np.nan,
                              self._bar, stop=stop, limit=limit, oca_group=oca_name))

    def order(self, order_id: str, direction: str, qty: float | None = None,
              when: bool = True, stop: float | None = None, limit: float | None = None) -> None:
        self.entry(order_id, direction, qty, when, stop, limit)

    def close(self, order_id: str, when: bool = True, comment: str | None = None) -> None:
        del comment
        if not when:
            return
        self._place(PineOrder(f"close:{order_id}", "flat", "close", np.nan, self._bar,
                              from_entry=order_id))

    def close_all(self, when: bool = True) -> None:
        if not when:
            return
        self._place(PineOrder("close_all", "flat", "close", np.nan, self._bar))

    def cancel(self, order_id: str, when: bool = True) -> None:
        if not when:
            return
        for order in self._pending:
            if order.order_id == order_id and order.cancelled_bar is None:
                order.cancelled_bar = self._bar

    def cancel_all(self, when: bool = True) -> None:
        if not when:
            return
        for order in self._pending:
            if order.cancelled_bar is None:
                order.cancelled_bar = self._bar

    def exit(self, order_id: str, from_entry: str | None = None, when: bool = True,
             stop: float | None = None, limit: float | None = None,
             profit: float | None = None, loss: float | None = None,
             trail_points: float | None = None, trail_offset: float | None = None) -> None:
        if not when:
            return
        self._place(PineOrder(order_id, "flat", "exit", np.nan, self._bar,
                              stop=stop, limit=limit, from_entry=from_entry,
                              profit_ticks=profit, loss_ticks=loss,
                              trail_points=trail_points, trail_offset=trail_offset))

    # ---- engine internals -------------------------------------------------
    def _place(self, order: PineOrder) -> None:
        if order.kind in ("market", "stop", "limit") and self._direction_of(order.direction) != 0:
            # Pine evaluates `pyramiding` when the order is CREATED: an entry
            # that would exceed it is ignored outright, so it never fills and
            # never becomes a signal. Deciding this at fill time instead let the
            # engine open a position that its own signal projection had already
            # suppressed -- measured on SMPercentageStopLossTakeProfit_4fe53d,
            # where the entry placed on a bar with a position open was projected
            # as no signal and then filled anyway, one bar later, once the
            # previous position had been closed by a resting exit. The engine
            # reported a trade the framework was never told about.
            side = self._direction_of(order.direction)
            if not self._can_add(side):
                order.blocked_bar = self._bar
        if order.kind == "exit":
            # Pine keeps ONE order per id: `strategy.exit` called again with an
            # id that is already resting REPLACES it. Queuing a fresh copy every
            # bar is not equivalent. Left to accumulate, the copies outlive the
            # position they were placed for, and on the bar a NEW entry fills --
            # the previous position having just been closed by the first copy --
            # the next copy finds a position again and closes it at the OLD
            # trade's level, booking a zero-length round trip. Measured on
            # SMDcaTakeProfit_dfa329 and SMPercentageStopLossTakeProfit_4fe53d.
            # It was also quadratic: a position held for thousands of bars left
            # thousands of copies to re-check every bar.
            #
            # A replacement starts the trailing ratchet over (`trail_extreme` /
            # `trail_armed` live on the order), so a source that re-places its
            # trail every bar never ratchets across bars -- the level is only
            # ever reachable inside one bar. Whether the original platform
            # carries the ratchet across a same-id replacement is unverified;
            # PINE_SEMANTICS.md §3.6 records the risk rather than guessing.
            self._pending = [o for o in self._pending if o.order_id != order.order_id]
        self.orders.append(order)
        self._pending.append(order)
        self._placed_this_bar.append(order)

    def _direction_of(self, direction: str) -> int:
        return {"long": 1, "short": -1, "flat": 0}[direction]

    def _can_add(self, side: int) -> bool:
        """Pyramiding limits how many entries may stack in one direction."""
        if side == 0:
            return True
        if self.position == 0 or np.sign(self.position) != side:
            return True
        open_same = sum(1 for entry in self._open_entries if np.sign(entry["qty"]) == side)
        return open_same <= self.config.pyramiding

    def _entry_delta(self, side: int, qty: float) -> float:
        """Signed fill size for a Pine entry order of `qty` in `side`.

        Pine sizes an entry so the resulting position equals the order's
        quantity. Against an opposing position that means the order first
        closes it and then opens `qty` in the new direction, so the fill is
        `qty + |position|` -- a reverse is one order, not a close plus an open.
        An entry in the SAME direction instead adds `qty` on top, which is what
        makes pyramiding stack rather than retarget an absolute size.
        """
        signed = side * abs(qty)
        if self.position != 0 and np.sign(self.position) == side:
            return signed
        return signed - self.position

    def entry_will_fill(self, order: PineOrder) -> bool:
        """Whether an entry order can actually move the position.

        An order the engine would reject must not be projected as a signal
        either. A source that passes `qty=0` literally -- several do -- would
        otherwise reach the framework as a live entry on every bar and be read
        as an always-in strategy, when the source itself never opens a position.
        The same applies to an entry the pyramiding limit blocks, which
        `_try_fill_pending` drops rather than re-queues.
        """
        if order.blocked_bar is not None:
            return False
        side = self._direction_of(order.direction)
        if side == 0 or not self._can_add(side):
            return False
        if np.isfinite(order.qty) and abs(order.qty) < 1e-12:
            return False
        return True

    def _record_entry_fill(self, bar: int, order_id: str, side: int, qty: float,
                           price: float) -> None:
        """Note what an entry order asked for, in money, at the price it fills.

        `percent_of_equity` sizes off `strategy.equity` as of the bar the order
        was PLACED -- Pine evaluates the script at that bar's close, so the
        quantity is frozen before the next bar opens. A framework that instead
        sizes at the fill bar off its own live wallet is on a different basis
        and drifts, compounding once the two wallets disagree. Recording the
        notional here lets the port hand Freqtrade the source's own number
        rather than re-deriving an approximation of it.
        """
        if not np.isfinite(price) or price <= 0 or not np.isfinite(qty):
            return
        opening = abs(qty)
        if opening < 1e-12:
            return
        self.entry_fills.append({
            "bar": bar, "id": order_id, "side": side,
            "qty": opening, "price": float(price), "notional": opening * float(price),
        })

    def _apply_fill(self, qty: float, price: float, bar: int, entry_id: str) -> None:
        """Apply a signed fill: reduce any opposite entry, then open the rest.

        Pine's engine nets an opposing order against the open position first and
        opens a new position with whatever size is left over. Commission is
        charged on each leg's turnover.
        """
        if not np.isfinite(price) or abs(qty) < 1e-12:
            return
        rate = self.config.commission_percent / 100.0
        remaining = float(qty)
        if self.position != 0 and np.sign(remaining) != np.sign(self.position):
            direction = float(np.sign(self.position))
            closing = min(abs(remaining), abs(self.position))
            gross = closing * (price - self.avg_price) * direction
            exit_fee = closing * price * rate
            self.cash += gross - exit_fee
            self.realized_profit += gross - exit_fee
            self._reduce_entries(closing, bar, price, exit_fee)
            # Reduce the existing position toward zero; the leftover below opens
            # the new direction. (Adding here would double the position.)
            self.position -= direction * closing
            if abs(self.position) < 1e-12:
                self.position = 0.0
                self.avg_price = 0.0
            remaining = remaining + direction * closing
        opening = abs(remaining)
        if opening > 1e-12:
            entry_fee = opening * price * rate
            self.cash -= entry_fee
            self.realized_profit -= entry_fee
            total = abs(self.position) + opening
            self.avg_price = (abs(self.position) * self.avg_price + opening * price) / total
            self.position += remaining
            self._open_entries.append({
                "id": entry_id, "qty": remaining, "price": price, "bar": bar,
                "fee_rate": rate,
            })
            if abs(self.position) < 1e-12:
                self.position = 0.0
                self.avg_price = 0.0

    def _book_trade(self, entry: dict, take: float, bar: int, price: float,
                    exit_fee: float) -> None:
        """Record a closed slice net of the entry and exit commission shares."""
        direction = np.sign(entry["qty"])
        gross = take * (price - entry["price"]) * direction
        entry_fee_share = take * entry["price"] * entry.get("fee_rate", 0.0)
        self.trades.append(
            PineTrade(entry["bar"], bar, entry["price"], price, take,
                      "long" if direction > 0 else "short",
                      gross - entry_fee_share - exit_fee, entry["id"])
        )

    def _reduce_entries(self, amount: float, bar: int, price: float,
                        exit_fee: float | None = None) -> None:
        """Reduce open entries FIFO by `amount`, booking each closed part."""
        rate = self.config.commission_percent / 100.0
        left = amount
        for entry in list(self._open_entries):
            if left <= 1e-12:
                break
            take = min(abs(entry["qty"]), left)
            direction = np.sign(entry["qty"])
            fee = exit_fee * (take / amount) if exit_fee is not None else take * price * rate
            self._book_trade(entry, take, bar, price, fee)
            entry["qty"] -= direction * take
            left -= take
            if abs(entry["qty"]) < 1e-12:
                self._open_entries.remove(entry)
        self._recompute_avg_price()

    def _close_entries(self, bar: int, price: float, entry_id: str | None) -> None:
        """Close every open entry, or only those matching `entry_id`."""
        rate = self.config.commission_percent / 100.0
        targets = [e for e in self._open_entries if entry_id is None or e["id"] == entry_id]
        for entry in targets:
            amount = abs(entry["qty"])
            direction = np.sign(entry["qty"])
            exit_fee = amount * price * rate
            self._book_trade(entry, amount, bar, price, exit_fee)
            self.cash += (price - entry["price"]) * entry["qty"] - exit_fee
            self.realized_profit += (price - entry["price"]) * entry["qty"] - exit_fee
            self.position -= entry["qty"]
            self._open_entries.remove(entry)
        if abs(self.position) < 1e-12:
            self.position = 0.0
            self.avg_price = 0.0
        else:
            self._recompute_avg_price()

    def _recompute_avg_price(self) -> None:
        total = sum(abs(e["qty"]) for e in self._open_entries)
        self.avg_price = (
            sum(abs(e["qty"]) * e["price"] for e in self._open_entries) / total
            if total else 0.0
        )

    def _entry_is_open(self, entry_id: str) -> bool:
        """Whether the entry an exit order names is currently held."""
        return any(entry["id"] == entry_id for entry in self._open_entries)

    def _try_fill_pending(self, bar: int, open_: float, high: float, low: float) -> None:
        """Fill or rest each pending order against this bar."""
        still_pending: list[PineOrder] = []
        for order in self._pending:
            if order.cancelled_bar is not None:
                continue
            if order.kind == "market":
                if not self.entry_will_fill(order):
                    continue
                qty = order.qty if np.isfinite(order.qty) else self._size_for(open_)
                side = self._direction_of(order.direction)
                self._record_entry_fill(bar, order.order_id, side, qty, open_)
                self._apply_fill(self._entry_delta(side, qty), open_, bar, order.order_id)
                order.filled_bar, order.fill_price = bar, open_
                continue
            if order.kind in ("stop", "limit"):
                side = self._direction_of(order.direction)
                if side == 0 or not self._can_add(side):
                    continue
                price = self._price_order_fill(order, side, open_, high, low)
                if price is None:
                    still_pending.append(order)
                    continue
                qty = order.qty if np.isfinite(order.qty) else self._size_for(price)
                self._record_entry_fill(bar, order.order_id, side, qty, price)
                self._apply_fill(self._entry_delta(side, qty), price, bar, order.order_id)
                order.filled_bar, order.fill_price = bar, price
                continue
            if order.kind == "close":
                if self.position == 0:
                    continue
                self._close_entries(bar, open_, order.from_entry)
                order.filled_bar, order.fill_price = bar, open_
                continue
            if order.kind == "exit":
                if self.position == 0:
                    continue
                # An exit names the entry it closes. One whose entry is not open
                # -- `strategy.exit(from_entry="Long")` re-issued every bar while
                # a SHORT is on, which is the ordinary shape of a two-sided
                # source -- is a no-op: `_close_entries` would match nothing. It
                # must not publish levels either, or the LONG arm's stop and
                # take-profit become the SHORT position's `pine_stop_level` /
                # `pine_limit_level` and a framework is handed an exit the engine
                # never had. `active_exit_levels` already filters this way; the
                # engine's own fill path already ignores the order.
                if order.from_entry is not None and not self._entry_is_open(order.from_entry):
                    # It keeps resting -- a source may place the exit before the
                    # entry it names -- but it is neither acted on nor published
                    # until its entry exists.
                    still_pending.append(order)
                    continue
                # What this order rests at WHILE this bar trades. Recorded
                # whether or not it fills, because a level the price did not
                # reach is still the level in force -- and because a framework
                # reading the ledger needs exactly the levels the engine acted
                # on, not a one-bar-lagged snapshot of them.
                side = int(np.sign(self.position))
                order_stop, order_limit = self._order_stop_limit(order, side)
                self._levels_used.append(
                    (side, order_stop, order_limit, self._trail_stop(order, side))
                )
                price = self._exit_fill(order, open_, high, low)
                if price is None:
                    still_pending.append(order)
                    continue
                self._close_entries(bar, price, order.from_entry)
                order.filled_bar, order.fill_price = bar, price
        self._pending = still_pending

    def _price_order_fill(self, order: PineOrder, side: int, open_: float,
                          high: float, low: float) -> float | None:
        if order.stop is not None:
            stop = float(order.stop)
            if side > 0 and high >= stop:
                return max(stop, open_)  # gap through the stop fills at the open
            if side < 0 and low <= stop:
                return min(stop, open_)
            return None
        limit = float(order.limit)
        if side > 0 and low <= limit:
            return min(limit, open_)
        if side < 0 and high >= limit:
            return max(limit, open_)
        return None

    def _order_stop_limit(self, order: PineOrder, side: int) -> tuple:
        """Resolve an exit order's two resting legs to prices.

        `profit` / `loss` are tick distances from the entry price, so they are
        only a price once the entry has filled -- which is why a port could not
        turn them into a level when it placed the order and had to anchor them
        to whatever the signal bar knew (measured on SMEliEmaCross_48f1cc, where
        the engine stopped a whole signal-bar-to-open gap away from the
        framework). Resolving here uses the position's average entry price: for
        the single entry an exit belongs to, that is the price Pine uses.

        The tighter of an explicit `stop=` and a tick `loss=` wins, since both
        are stop legs on one position.
        """
        stop, limit = order.stop, order.limit
        if self.position == 0 or not np.isfinite(self.avg_price):
            return stop, limit
        tick = float(self.config.mintick)
        if order.loss_ticks is not None and np.isfinite(order.loss_ticks):
            loss = self.avg_price - side * float(order.loss_ticks) * tick
            stop = loss if stop is None else (max(float(stop), loss) if side > 0
                                              else min(float(stop), loss))
        if order.profit_ticks is not None and np.isfinite(order.profit_ticks):
            profit = self.avg_price + side * float(order.profit_ticks) * tick
            limit = profit if limit is None else (min(float(limit), profit) if side > 0
                                                  else max(float(limit), profit))
        return stop, limit

    def _exit_fill(self, order: PineOrder, open_: float, high: float,
                   low: float) -> float | None:
        """OCA exit: the first of stop / limit / trail to trigger closes the entry.

        A bar that GAPS through the level fills at that bar's open, not at the
        level -- worse for a stop, better for a take-profit -- because the first
        tradeable price of the bar is the only one the order could have met.
        This is the same rule `_price_order_fill` applies on the entry side, and
        the same one Freqtrade applies to its own stop and ROI exits, so leaving
        it out here would put the engine a whole level away from the framework
        on every gap.
        """
        if self.position == 0:
            return None
        side = int(np.sign(self.position))
        order_stop, order_limit = self._order_stop_limit(order, side)
        # Kept apart by leg: the two legs are aggregated differently below.
        stop_fills: list[float] = []
        limit_fills: list[float] = []
        if order_stop is not None:
            stop = float(order_stop)
            if side > 0 and low <= stop:
                stop_fills.append(min(stop, open_))
            elif side < 0 and high >= stop:
                stop_fills.append(max(stop, open_))
        if order_limit is not None:
            limit = float(order_limit)
            if side > 0 and high >= limit:
                limit_fills.append(max(limit, open_))
            elif side < 0 and low <= limit:
                limit_fills.append(min(limit, open_))
        if order.trail_points is not None and order.trail_offset is not None:
            points = float(order.trail_points)
            offset = float(order.trail_offset)
            bar_extreme = high if side > 0 else low
            if order.trail_extreme is None:
                order.trail_extreme = self.avg_price
            # Whether the trail was already live when this bar opened decides
            # whether the open is a price it could have filled at. A trail that
            # ARMS inside the bar -- price ran up to the activation threshold
            # and then turned -- did not exist at the open, so a bar that
            # opened below the stop still fills at the stop on the way down.
            was_armed = order.trail_armed
            if not order.trail_armed:
                order.trail_armed = (bar_extreme - self.avg_price) * side >= points
            if order.trail_armed:
                # Ratchet: the reference only improves in the position's favour.
                order.trail_extreme = (
                    max(order.trail_extreme, bar_extreme) if side > 0
                    else min(order.trail_extreme, bar_extreme)
                )
                trail_stop = order.trail_extreme - side * offset
                if not was_armed:
                    # Armed this bar: the level is the fill, open or not.
                    if side > 0 and low <= trail_stop:
                        stop_fills.append(trail_stop)
                    elif side < 0 and high >= trail_stop:
                        stop_fills.append(trail_stop)
                elif side > 0 and low <= trail_stop:
                    stop_fills.append(min(trail_stop, open_))
                elif side < 0 and high >= trail_stop:
                    stop_fills.append(max(trail_stop, open_))
        if not stop_fills and not limit_fills:
            return None
        if not stop_fills:
            # Several limits on one position is not reachable from a Pine source
            # (one order per id), so this is the single-limit case.
            return min(limit_fills) if side > 0 else max(limit_fills)
        # Among stops, the one the price met FIRST is the tightest: a long
        # falling through 100 on its way to 90 is stopped at 100. Aggregating
        # with `min` instead would book the lower stop, which no single-level
        # framework stop can reproduce -- and the framework's `custom_stoploss`
        # hands over exactly one level per position.
        stop_fill = max(stop_fills) if side > 0 else min(stop_fills)
        if not limit_fills:
            return stop_fill
        # A stop and a limit both triggered, so the bar's range spans both and
        # the intrabar path is not knowable from OHLC. Keep the conservative
        # rule -- the worse price for the position.
        limit_fill = min(limit_fills) if side > 0 else max(limit_fills)
        return min(stop_fill, limit_fill) if side > 0 else max(stop_fill, limit_fill)

    # ---- public properties Pine scripts read ------------------------------
    @property
    def position_size(self) -> float:
        return self.position

    @property
    def position_avg_price(self) -> float:
        return self.avg_price if self.position != 0 else np.nan

    @property
    def open_trades(self) -> int:
        return len(self._open_entries)

    @property
    def closed_trades(self) -> int:
        return len(self.trades)

    def mark(self, bar: int, open_: float, high: float, low: float, close: float) -> None:
        """Advance the engine one bar: fill resting orders, then mark to market."""
        self._bar = bar
        self._placed_this_bar = []
        self._levels_used = []
        self._bar_open, self._bar_high, self._bar_low, self._bar_close = open_, high, low, close
        self._try_fill_pending(bar, open_, high, low)
        self.open_profit = sum(e["qty"] * (close - e["price"]) for e in self._open_entries)
        self.equity = self.cash + self.open_profit

    def active_exit_levels(self) -> tuple[float, float]:
        """Tightest resting stop and take-profit for the open position.

        A long position stops out at the HIGHEST resting stop (first touched on
        the way down) and takes profit at the LOWEST resting limit. Shorts are
        mirrored. An ARMED trailing stop is a stop like any other and is folded
        in at its current ratcheted level, so a source whose only stop is a
        trail still reaches the framework. Returns (nan, nan) when flat or when
        nothing rests.
        """
        if self.position == 0:
            return float("nan"), float("nan")
        side = int(np.sign(self.position))
        stops, limits = [], []
        for order in self._pending:
            if order.cancelled_bar is not None or order.kind != "exit":
                continue
            if order.from_entry and not self._entry_is_open(order.from_entry):
                continue
            order_stop, order_limit = self._order_stop_limit(order, side)
            if order_stop is not None and np.isfinite(order_stop):
                stops.append(float(order_stop))
            if order_limit is not None and np.isfinite(order_limit):
                limits.append(float(order_limit))
            trail = self._trail_stop(order, side)
            if trail is not None:
                stops.append(trail)
        stop = (max(stops) if side > 0 else min(stops)) if stops else float("nan")
        limit = (min(limits) if side > 0 else max(limits)) if limits else float("nan")
        return stop, limit

    def used_exit_levels(self) -> tuple[float, float]:
        """The stop and take-profit that were live DURING the bar just marked.

        A framework can only act on a level through its own per-candle hooks, so
        what it needs is not "what rests at the end of bar `t`" but "what the
        engine acted on while bar `t` traded". The two differ whenever an exit
        order is already pending when the position opens on it -- a source that
        places `strategy.exit` next to `strategy.entry` has its stop live on the
        entry's own fill bar, and a one-bar-lagged snapshot of the ledger would
        miss it entirely.

        Reading it off the evaluation itself also settles the opposite case, a
        source that only places the exit once `strategy.position_size > 0`: that
        order is not evaluated on the bar it is placed, so it is correctly
        absent from that bar's levels and present on the next.
        """
        if not self._levels_used:
            return float("nan"), float("nan")
        # A bar can touch more than one side -- a reversal fills the new entry
        # and closes the old one on the same bar -- and a stop and a take-profit
        # tighten in OPPOSITE directions, so the records cannot be pooled: they
        # are reduced per side, and the side the bar ends holding is the one the
        # framework needs (falling back to the last side touched when the bar
        # ends flat, which is a stop that fired on its own entry bar).
        sides = [record[0] for record in self._levels_used]
        side = int(np.sign(self.position)) or sides[-1]
        stops, limits = [], []
        for record_side, stop, limit, trail in self._levels_used:
            if record_side != side:
                continue
            if stop is not None and np.isfinite(stop):
                stops.append(float(stop))
            if limit is not None and np.isfinite(limit):
                limits.append(float(limit))
            if trail is not None and np.isfinite(trail):
                stops.append(float(trail))
        stop = (max(stops) if side > 0 else min(stops)) if stops else float("nan")
        limit = (min(limits) if side > 0 else max(limits)) if limits else float("nan")
        return stop, limit

    @staticmethod
    def _trail_stop(order: PineOrder, side: int) -> float | None:
        """The level an armed trailing stop currently rests at, else None.

        `_exit_fill` advances the ratchet while a bar is being processed, so the
        level read here is the one that will be in force on the NEXT bar -- the
        same bar the port's `custom_stoploss` is asked about.
        """
        if order.trail_offset is None or order.trail_extreme is None:
            return None
        if not order.trail_armed:
            return None
        level = float(order.trail_extreme) - side * float(order.trail_offset)
        return level if np.isfinite(level) else None

    def snapshot(self) -> dict:
        """Per-bar Pine state, named as the ledger columns the ports expose."""
        return {
            "pine_position": self.position,
            "pine_avg_price": self.avg_price,
            "pine_equity": self.equity,
            "pine_cash": self.cash,
            "pine_open_profit": self.open_profit,
            "pine_open_trades": self.open_trades,
            "pine_closed_trades": self.closed_trades,
        }


def run_pine(config: PineBrokerConfig, dataframe: pd.DataFrame,
             script: Callable[[PineBroker, int, dict], None],
             context: dict | None = None) -> pd.DataFrame:
    """Run a Pine-shaped script over `dataframe`, one bar at a time.

    `script(broker, i, context)` is called once per bar with the previous bar's
    state already marked, which matches Pine evaluating the script at bar close.
    Returns a frame with the per-bar Pine state columns plus the signal columns
    a Freqtrade strategy can project:

    * `pine_position`, `pine_equity`, `pine_open_profit`, `pine_open_trades`
    * `enter_long`, `enter_short`, `exit_long`, `exit_short` -- 1 on the bar the
      order was PLACED, so a Freqtrade market order fills on the next open,
      exactly as Pine fills it.
    * `pine_order_placed` -- order id placed on this bar, for traceability.
    """
    context = context or {}
    broker = PineBroker(config)
    rows = []
    for i in range(len(dataframe)):
        row = dataframe.iloc[i]
        broker.mark(i, row["open"], row["high"], row["low"], row["close"])
        script(broker, i, context)
        placed = list(broker._placed_this_bar)
        state = broker.snapshot()
        stop_level, limit_level = broker.used_exit_levels()
        state.update({
            "enter_long": 0, "enter_short": 0, "exit_long": 0, "exit_short": 0,
            "pine_order_placed": "",
            "pine_stop_level": stop_level,
            "pine_limit_level": limit_level,
        })
        for order in placed:
            side = broker._direction_of(order.direction)
            if order.kind in ("market", "stop", "limit"):
                # Only an entry the engine would actually fill becomes a
                # signal; see PineBroker.entry_will_fill.
                if broker.entry_will_fill(order):
                    if side > 0 and state["enter_long"] == 0:
                        state["enter_long"] = 1
                    elif side < 0 and state["enter_short"] == 0:
                        state["enter_short"] = 1
                    # Pine nets an opposing entry against the open position. A
                    # framework that only sees `enter_short` would refuse it while
                    # a long is open, so the reversal must carry its closing leg too.
                    if side > 0 and state["pine_position"] < 0:
                        state["exit_short"] = 1
                    elif side < 0 and state["pine_position"] > 0:
                        state["exit_long"] = 1
            elif order.kind in ("close", "exit"):
                # An exit whose entry is not open closes nothing -- `_close_entries`
                # matches on `from_entry`, so the engine's own ledger never acts on
                # it. Projecting it anyway turns a Pine no-op into a real framework
                # exit: a source that calls `strategy.close("Long")` on a condition
                # regardless of position (the usual shape) has its LONG-bound close
                # arrive while a SHORT is open, and the framework then closes the
                # short a bar after it opened. Measured on SM5MinKdjDynamic_ddea08:
                # engine 24 trades to the framework's 25, 15 close dates apart;
                # with this guard the same run compares 24/24 as `match`.
                if order.from_entry is not None and not broker._entry_is_open(order.from_entry):
                    continue
                # Only a market exit becomes a next-open signal. A stop or
                # limit exit fills INSIDE the bar on the original platform, so
                # it is projected through pine_stop_level / pine_limit_level
                # instead of being flattened into a next-open order. A tick
                # target (`profit=` / `loss=`) is such a resting leg too, even
                # though its price is only resolvable once the entry has
                # filled. A trailing stop is one as well: `used_exit_levels`
                # folds the armed trail in at its ratcheted level, so the
                # framework gets the same inside-the-bar exit -- flattening it
                # into a next-open market order would move the exit to the wrong
                # bar and the wrong price.
                if (order.stop is not None or order.limit is not None
                        or order.profit_ticks is not None or order.loss_ticks is not None
                        or order.trail_points is not None or order.trail_offset is not None):
                    continue
                if state["pine_position"] > 0 and state["exit_long"] == 0:
                    state["exit_long"] = 1
                elif state["pine_position"] < 0 and state["exit_short"] == 0:
                    state["exit_short"] = 1
            state["pine_order_placed"] = (
                f"{state['pine_order_placed']},{order.order_id}:{order.kind}"
                if state["pine_order_placed"] else f"{order.order_id}:{order.kind}"
            )
        rows.append(state)
    ledger = pd.DataFrame(rows, index=dataframe.index)
    # Pin dtypes: a short prefix can otherwise infer int64 where the full run
    # infers float64, which would make the causality prefix check meaningless.
    for column in ("pine_position", "pine_avg_price", "pine_equity", "pine_cash",
                   "pine_open_profit", "pine_stop_level", "pine_limit_level"):
        ledger[column] = ledger[column].astype(float)
    for column in ("pine_open_trades", "pine_closed_trades", "enter_long",
                   "enter_short", "exit_long", "exit_short"):
        ledger[column] = ledger[column].astype(int)
    ledger["pine_order_placed"] = ledger["pine_order_placed"].astype(str)
    ledger.attrs["orders"] = broker.orders
    ledger.attrs["trades"] = broker.trades
    # Entries still open at the end. A caller comparing against a framework's
    # trade list needs these: the framework reports a hold-only strategy as one
    # unclosed trade, so an empty closed-trade list is not "no trades".
    ledger.attrs["open_entries"] = list(broker._open_entries)
    ledger.attrs["entry_fills"] = list(broker.entry_fills)
    ledger.attrs["final_cash"] = broker.cash
    ledger.attrs["final_equity"] = broker.equity
    return ledger


def pine_qty_type(name: str) -> str:
    """Map a source's `default_qty_type=` expression to the engine's constant."""
    text = str(name).strip()
    if text.endswith("percent_of_equity"):
        return QTY_PERCENT_OF_EQUITY
    if text.endswith("cash"):
        return QTY_CASH
    if text.endswith("fixed"):
        return QTY_FIXED
    raise ValueError(f"unrecognised default_qty_type {name!r}")


def round_to_step(quantity: float, step: float) -> float:
    """Truncate a quantity to a broker step, as Pine's calculator does."""
    if step <= 0:
        return quantity
    return floor(quantity / step) * step
