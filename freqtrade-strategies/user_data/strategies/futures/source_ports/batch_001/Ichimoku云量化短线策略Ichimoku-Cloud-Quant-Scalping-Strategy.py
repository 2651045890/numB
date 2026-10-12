"""Port of sources/SM_c7f6d19e3f936d92.pine (batch_001/Ichimoku云量化短线策略Ichimoku-Cloud-Quant-Scalping-Strategy.md).

Pine v2. A 7/26/52 Ichimoku conversion-line scalper gated by a hand-written
ADX and by a trading session:

    f_donchian(_len) => avg(lowest(_len), highest(_len))
    conversionLine = f_donchian(7)
    baseLine       = f_donchian(26)
    leadLine1      = avg(conversionLine, baseLine)
    leadLine2      = f_donchian(52)

    TrueRange = max(max(high - low, abs(high - nz(close[1]))), abs(low - nz(close[1])))
    DirectionalMovementPlus  = high - nz(high[1]) > nz(low[1]) - low ? max(high - nz(high[1]), 0) : 0
    DirectionalMovementMinus = nz(low[1]) - low > high - nz(high[1]) ? max(nz(low[1]) - low, 0) : 0
    SmoothedTrueRange = nz(SmoothedTrueRange[1]) - nz(SmoothedTrueRange[1]) / len + TrueRange
    SmoothedDirectionalMovementPlus  = ... same recursion ...
    SmoothedDirectionalMovementMinus = ... same recursion ...
    DIPlus  = SmoothedDirectionalMovementPlus  / SmoothedTrueRange * 100
    DIMinus = SmoothedDirectionalMovementMinus / SmoothedTrueRange * 100
    DX  = abs(DIPlus - DIMinus) / (DIPlus + DIMinus) * 100
    ADX = sma(DX, 14)

    istradingsession = not USE_TRADESESSION ? false : not na(time('1', trade_session))

    buy_icloud_signal = open < conversionLine and close > conversionLine
    buy_adx_signal    = DIPlus > 20
    buy_signal        = istradingsession and buy_icloud_signal and buy_adx_signal
    sel_icloud_signal = open > conversionLine and close < conversionLine
    sel_adx_signal    = DIMinus > 20
    sel_signal        = istradingsession and sel_icloud_signal and sel_adx_signal

    strategy.order('buy', long=true, qty=trade_size, comment='buy', when=buy_signal)
    strategy.order('sel', long=false, qty=trade_size, comment='sel', when=sel_signal)
    strategy.exit('exit buy', from_entry='buy', profit=take_profit_in_ticks, loss=stop_loss_in_ticks)
    strategy.exit('exit sel', from_entry='sel', profit=take_profit_in_ticks, loss=stop_loss_in_ticks)

The two `strategy.exit` calls carry NO `when`, so they are re-issued on every
bar and Pine keeps one order per id -- the engine's `_place` replaces same-id
exit orders, which is the same rule. `profit=` / `loss=` are TICK distances, so
they become prices only once the entry has filled: the engine resolves them
against the position's average entry price with `source_mintick`, which is
Pine's `syminfo.mintick`. 200 / 150 ticks at 0.1 is +20 / -15 price units.

`strategy()` declares `title`, `shorttitle`, `overlay`, `initial_capital=100000`
and `currency=currency.USD`, so sizing is Pine v2's default `strategy.fixed` /
1 contract, commission 0%, pyramiding 0, `process_orders_on_close=false`. Both
order calls pass `qty=trade_size` (= 1) explicitly, so the default quantity
never applies.

FIDELITY:

* `time('1', trade_session)` is Pine's session filter: the bar's own time when
  the bar falls inside the session, na otherwise. It is modelled here as a
  time-of-day window on the candle's opening timestamp, `0400-1500` being
  `[04:00, 15:00)` so a bar opening exactly at 15:00 is OUT. Pine resolves a
  session in the EXCHANGE's timezone; the header's venue is Binance Futures,
  whose exchange timezone is UTC, and the port reads the frame's timestamps as
  UTC (PINE_SEMANTICS.md 3.4). A non-UTC venue would need an explicit timezone
  here.
* The two smoothed directional sums use the source's OWN seed of 0 (via
  `nz(...[1])`), not `pine_ta.pine_rma`, which seeds with the SMA of the first
  `length` observations. The two agree only asymptotically, and the whole
  DIPlus/DIMinus/DX/ADX chain inherits the difference, so the recursion is
  written out rather than delegated.
* `nz(close[1])`, `nz(high[1])`, `nz(low[1])` are na on the first bar and
  become 0, which is why the first bar's TrueRange is `high`, its
  DirectionalMovementPlus is `high` and its DirectionalMovementMinus is 0.
  Reproduced literally; a plain `shift(1)` without the nz would make the whole
  first-bar row na and shift the ADX warm-up.
* Division by zero is not published for Pine v2. `0 / 0` is modelled as na and
  `x / 0` as na, so a flat window leaves DIPlus/DIMinus/DX/ADX na and the
  comparison in `buy_adx_signal` / `sel_adx_signal` is false -- the same
  direction as Pine treating an na condition as false. Modelled, not verified
  against the original platform.
* `ta.pine_sma` propagates na (a window containing na cannot reach its
  `min_periods`), so ADX stays na until 14 consecutive DX values exist.
* `th = input(title="threshold", defval=20)` is declared and never read: the
  ADX thresholds are the bare literals 20 in `DIPlus > 20` / `DIMinus > 20`.
  The literal is used, `th` is carried in `source_defaults` for provenance.
* `basePeriods`, `laggingSpan2Periods` and `displacement` are plain assignments
  (their `input(...)` forms are commented out), so they are NOT in
  `source_defaults`. `displacement` is only used by the commented-out plots.
* `f_donchian` averages `lowest(low, n)` with `highest(high, n)`; Pine's bare
  `lowest(n)` / `highest(n)` default to `low` / `high`. No displacement is
  applied to the conversion line, so the cloud's forward shift never enters a
  condition.
* `plot(...)` and `bgcolor(...)` calls are display-only and place no condition.
* No `request.security`, no `varip`, no `strategy.risk.*`, no trailing stop and
  no pyramiding in the source.
* Leverage, margin, liquidation, funding and the venue's contract-step rounding
  are not modelled; the chain verifier measures the step rounding separately
  (PINE_SEMANTICS.md 1.6).
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


def _wilders_seeded_zero(values: np.ndarray, length: int) -> np.ndarray:
    """The source's `nz(x[1]) - nz(x[1]) / len + value` recursion, seeded 0.

    Pine's `ta.rma` has the same body but seeds with the SMA of the first
    `length` observations; this source writes the recursion by hand with
    `nz(x[1])`, and `nz(na)` is 0, so the very first bar already carries a
    value. Substituting `pine_rma` here would move the whole ADX warm-up.
    """
    out = np.empty(len(values), dtype=float)
    state = 0.0
    for i, value in enumerate(values):
        state = state - state / length + float(value)
        out[i] = state
    return out


def _safe_div(numerator: np.ndarray, denominator: np.ndarray) -> np.ndarray:
    """Elementwise division whose zero denominator yields na, as Pine's does."""
    with np.errstate(divide="ignore", invalid="ignore"):
        out = numerator / denominator
    return np.where(denominator != 0, out, np.nan)


def _session_mask(index, session: str) -> np.ndarray:
    """Pine `not na(time('1', session))` as a time-of-day mask on bar opens.

    TradingView resolves a session in the exchange's timezone. The header's
    venue is Binance Futures (UTC), so the frame's timestamps are read as UTC;
    a bar opening exactly at the session end is outside it.
    """
    stamps = pd.DatetimeIndex(index)
    stamps = stamps.tz_localize("UTC") if stamps.tz is None else stamps.tz_convert("UTC")
    start_text, _, end_text = session.partition("-")
    start = int(start_text[:2]) * 60 + int(start_text[2:4])
    end = int(end_text[:2]) * 60 + int(end_text[2:4])
    minutes = stamps.hour.to_numpy() * 60 + stamps.minute.to_numpy()
    if start <= end:
        return (minutes >= start) & (minutes < end)
    return (minutes >= start) | (minutes < end)


class SMIchimokuCloudQuantScalping_c7f6d1(PinePortBase, IStrategy):
    source_id = "SM_c7f6d19e3f936d92"
    source_file = "Ichimoku云量化短线策略Ichimoku-Cloud-Quant-Scalping-Strategy.md"
    timeframe = "30m"
    can_short = True
    source_defaults: dict = {
        "conversionPeriods": 7,
        "len": 14,
        "th": 20,
        "USE_TRADESESSION": True,
        "trade_session": "0400-1500",
        "trade_size": 1,
        "stop_loss_in_ticks": 150,
        "take_profit_in_ticks": 200,
    }
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 100_000.0
    source_reproduce_stops = True
    # syminfo.mintick for the header's Futures_Binance BTC_USDT contract: the
    # `profit` / `loss` tick distances resolve through it.
    source_mintick = 0.1
    source_fidelity_notes = [
        "`profit=` / `loss=` are TICK distances, so they only become prices "
        "once the entry has filled. They are passed to `broker.exit` as ticks "
        "and resolved by the engine against the position's average entry price "
        "with `source_mintick` (PINE_SEMANTICS.md 3.5). A port that anchored "
        "them to the signal bar instead would land a whole bar's move away.",
        "The two `strategy.exit` calls carry no `when`, so they are re-issued "
        "every bar. Pine keeps one order per id and the engine's `_place` "
        "replaces same-id exit orders, so the two agree; an accumulating queue "
        "would let a stale arm close the next position (PINE_SEMANTICS.md 1.12).",
        "`time('1', trade_session)` is modelled as a UTC time-of-day window "
        "`[04:00, 15:00)`. Pine resolves sessions in the EXCHANGE's timezone; "
        "the header's venue is Binance Futures (UTC). PINE_SEMANTICS.md 3.4 "
        "records that non-UTC venues need explicit handling.",
        "The smoothed directional sums use the source's own 0 seed via "
        "`nz(...[1])`, NOT `pine_ta.pine_rma` (which seeds with the first "
        "`length` observations' SMA). Both are written out here because the "
        "difference propagates through DIPlus/DIMinus/DX/ADX.",
        "`nz(close[1])` / `nz(high[1])` / `nz(low[1])` are 0 on the first bar, "
        "so its TrueRange, DirectionalMovementPlus and "
        "DirectionalMovementMinus take the degenerate values high / high / 0. "
        "Reproduced literally instead of being skipped.",
        "Division by zero is not published for Pine v2. `0/0` and `x/0` are "
        "both modelled as na, which makes the `> 20` threshold tests false -- "
        "the same direction as Pine treating an na condition as false. A "
        "modelling choice, not a documented rule.",
        "`th = input(defval=20)` is declared and NEVER read; the thresholds in "
        "`DIPlus > 20` / `DIMinus > 20` are bare literals. The literal is used "
        "and `th` is recorded for provenance only.",
        "`basePeriods=26`, `laggingSpan2Periods=52` and `displacement=26` are "
        "plain assignments whose `input(...)` forms are commented out, so they "
        "are NOT in `source_defaults`. `displacement` only feeds the "
        "commented-out plots; no condition uses a displaced series.",
        "`f_donchian(n) = avg(lowest(low, n), highest(high, n))`: Pine's bare "
        "`lowest(n)` / `highest(n)` default to low / high, and both return na "
        "until `n` bars have elapsed, so the conversion line needs 7 bars, the "
        "base line 26 and leadLine2 52.",
        "`strategy.order` is used for both directions with an explicit "
        "`qty=trade_size`, so `default_qty_type` never applies; Pine v2's "
        "default (`strategy.fixed`, 1) is recorded for provenance. Repeated "
        "same-direction orders are refused by Pine's `pyramiding` default of 0, "
        "which the engine models at order-creation time.",
        "`plot` and `bgcolor` calls, the `shorttitle`, and `currency=USD` are "
        "display or account metadata and place no condition.",
        "No `request.security`, no `varip`, no barstate branch, no trailing "
        "stop and no `strategy.risk.*` in the source.",
        "Leverage, margin, liquidation, funding and contract-step rounding are "
        "not modelled; the venue's rounding is measured by the chain verifier "
        "separately (PINE_SEMANTICS.md 1.6).",
    ]

    def pine_indicators(self, dataframe, params):
        high = dataframe["high"]
        low = dataframe["low"]
        close = dataframe["close"]
        open_ = dataframe["open"]
        length = int(params["len"])
        conversion_periods = int(params["conversionPeriods"])

        # f_donchian(_len) => avg(lowest(_len), highest(_len))
        def donchian(period: int) -> pd.Series:
            return (ta.pine_lowest(low, period) + ta.pine_highest(high, period)) / 2.0

        conversion_line = donchian(conversion_periods)
        base_line = donchian(26)
        lead_line1 = (conversion_line + base_line) / 2.0
        lead_line2 = donchian(52)

        # --- the hand-written ADX -----------------------------------------
        prev_close = close.shift(1).fillna(0.0)  # nz(close[1])
        prev_high = high.shift(1).fillna(0.0)  # nz(high[1])
        prev_low = low.shift(1).fillna(0.0)  # nz(low[1])

        true_range = np.maximum(
            np.maximum(high - low, (high - prev_close).abs()), (low - prev_close).abs()
        ).to_numpy(dtype=float)
        up_move = (high - prev_high).to_numpy(dtype=float)
        down_move = (prev_low - low).to_numpy(dtype=float)
        dm_plus_raw = np.where(up_move > down_move, np.maximum(up_move, 0.0), 0.0)
        dm_minus_raw = np.where(down_move > up_move, np.maximum(down_move, 0.0), 0.0)

        smoothed_tr = _wilders_seeded_zero(true_range, length)
        smoothed_dm_plus = _wilders_seeded_zero(dm_plus_raw, length)
        smoothed_dm_minus = _wilders_seeded_zero(dm_minus_raw, length)

        di_plus = _safe_div(smoothed_dm_plus * 100.0, smoothed_tr)
        di_minus = _safe_div(smoothed_dm_minus * 100.0, smoothed_tr)
        dx = _safe_div(np.abs(di_plus - di_minus) * 100.0, di_plus + di_minus)
        adx = ta.pine_sma(pd.Series(dx, index=dataframe.index), length)

        # --- trade session -------------------------------------------------
        use_trade_session = bool(params["USE_TRADESESSION"])
        if use_trade_session:
            in_session = _session_mask(dataframe.index, str(params["trade_session"]))
        else:
            in_session = np.zeros(len(dataframe), dtype=bool)

        buy_icloud = (open_ < conversion_line) & (close > conversion_line)
        sell_icloud = (open_ > conversion_line) & (close < conversion_line)
        buy_adx = pd.Series(di_plus, index=dataframe.index) > 20
        sell_adx = pd.Series(di_minus, index=dataframe.index) > 20
        session = pd.Series(in_session, index=dataframe.index)

        buy_signal = session & buy_icloud & buy_adx
        sell_signal = session & sell_icloud & sell_adx

        dataframe["pine_conversion_line"] = conversion_line
        dataframe["pine_base_line"] = base_line
        dataframe["pine_lead_line1"] = lead_line1
        dataframe["pine_lead_line2"] = lead_line2
        dataframe["pine_true_range"] = true_range
        dataframe["pine_di_plus"] = di_plus
        dataframe["pine_di_minus"] = di_minus
        dataframe["pine_dx"] = dx
        dataframe["pine_adx"] = adx
        dataframe["pine_is_trading_session"] = session
        dataframe["pine_buy_signal"] = buy_signal
        dataframe["pine_sell_signal"] = sell_signal
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "buy": dataframe["pine_buy_signal"].to_numpy(),
            "sell": dataframe["pine_sell_signal"].to_numpy(),
            "trade_size": float(params["trade_size"]),
            "take_profit_ticks": float(params["take_profit_in_ticks"]),
            "stop_loss_ticks": float(params["stop_loss_in_ticks"]),
        }

    def pine_script(self, broker, i, ctx):
        # strategy.order('buy', long=true, qty=trade_size, comment='buy', when=buy_signal)
        broker.order(
            "buy", "long", qty=ctx["trade_size"], when=bool(ctx["buy"][i])
        )
        # strategy.order('sel', long=false, qty=trade_size, comment='sel', when=sel_signal)
        broker.order(
            "sel", "short", qty=ctx["trade_size"], when=bool(ctx["sell"][i])
        )
        # strategy.exit('exit buy', from_entry='buy', profit=..., loss=...)
        broker.exit(
            "exit buy",
            from_entry="buy",
            profit=ctx["take_profit_ticks"],
            loss=ctx["stop_loss_ticks"],
        )
        # strategy.exit('exit sel', from_entry='sel', profit=..., loss=...)
        broker.exit(
            "exit sel",
            from_entry="sel",
            profit=ctx["take_profit_ticks"],
            loss=ctx["stop_loss_ticks"],
        )
