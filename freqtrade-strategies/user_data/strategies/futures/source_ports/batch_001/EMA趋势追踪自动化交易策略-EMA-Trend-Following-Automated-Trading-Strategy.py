"""Port of sources/SM_203e9d2b8ef6c32e.pine (batch_001/EMA趋势追踪自动化交易策略-EMA-Trend-Following-Automated-Trading-Strategy.md).

Pine v5. A 50-period EMA on close, both sides, entered with a resting
STOP-LIMIT order and sized from a risk percentage:

    emaValue = ta.ema(close, emaLength)

    getStopLoss(direction, barsBack) =>
        if direction == 1
            lowSwing = ta.lowest(low, barsBack)
            lowSwing - stopLossPips * syminfo.mintick
        else
            highSwing = ta.highest(high, barsBack)
            highSwing + stopLossPips * syminfo.mintick

    riskAmount = strategy.equity * (defaultRiskPercentage / 100)
    var qty = 0

    if ta.crossover(close, emaValue)
        stopLoss   = getStopLoss(-1, lookbackBars)
        takeProfit = close + takeProfitPips * syminfo.mintick
        qty := math.floor(riskAmount / (close - stopLoss) / syminfo.pointvalue)
        if qty < 1
            qty := 1
        strategy.entry("Buy",  strategy.long,  stop=stopLoss, limit=takeProfit, qty=qty)

    if ta.crossunder(close, emaValue)
        stopLoss   = getStopLoss(1, lookbackBars)
        takeProfit = close - takeProfitPips * syminfo.mintick
        qty := math.floor(riskAmount / (stopLoss - close) / syminfo.pointvalue)
        if qty < 1
            qty := 1
        strategy.entry("Sell", strategy.short, stop=stopLoss, limit=takeProfit, qty=qty)

`strategy()` declares only `title` and `overlay`, so every property is Pine's
documented default: `strategy.fixed` / 1 contract, initial capital 1000000,
commission 0%, `pyramiding 0`, `process_orders_on_close=false`. `qty` is passed
explicitly, so `default_qty_type` never comes into play.

THE DIRECTION ARGUMENT OF `getStopLoss` IS INVERTED IN THE SOURCE, and this is
reproduced, not repaired. The buy path calls `getStopLoss(-1, ...)`, and `-1` is
not `1`, so it takes the helper's ELSE branch and returns
`ta.highest(high, lookbackBars) + stopLossPips * mintick` -- a level ABOVE the
signal bar's close, not the "lowest low" the md's prose describes. The sell path
calls `getStopLoss(1, ...)` and symmetrically gets
`ta.lowest(low, lookbackBars) - stopLossPips * mintick`. Both are then handed to
`strategy.entry`'s `stop=` / `limit=` parameters, which for an ENTRY are the
order's own activation prices (a stop-limit order), NOT a protective stop-loss;
Pine has no way to attach a protective stop to an entry, that is `strategy.exit`'s
job. So the source's two entry orders are:

    Buy : buy  stop-limit, stop = highest(high, 10) + 0.5, limit = close + 2.0
    Sell: sell stop-limit, stop = lowest(low, 10)  - 0.5, limit = close - 2.0

The md's prose ("dynamic stop-loss = the recent lowest low / highest high plus
points", "lookback validation") describes the *intent*; the code puts the level
on the wrong side and `lookbackBars` is used for nothing but that swing window.
The code is followed.

`qty` evaluates to 1 on every signal. For the buy, `close - stopLoss` is
`close - highest(high, 10) - 0.5 <= -0.5`, so the quotient is negative and
`math.floor` of a negative is `<= -1 < 1`, forcing `qty := 1`; for the sell the
same happens with `stopLoss - close`. The risk sizing therefore never binds, and
the port reproduces the arithmetic rather than hard-coding 1.

The header declares `period: 1d` on Futures_Binance BTC_USDT, so `timeframe` is
"1d"; `basePeriod: 1h` is the FMZ backtester's own granularity for filling those
daily bars, not the strategy's period.

FIDELITY:

* The entry is a STOP-LIMIT order, i.e. a resting entry (PINE_SEMANTICS.md
  section 二.11): the engine fills it on the first later bar whose high reaches
  the stop (`max(stop, open)`, i.e. the open when the bar gaps through), while
  the projected `enter_long` / `enter_short` is a next-open MARKET order for the
  framework. Timing and price can therefore differ, and the engine can refuse to
  enter at all where the framework enters unconditionally.
* The engine's entry fill path (`_price_order_fill`) checks the STOP leg only;
  when an entry order carries both `stop=` and `limit=` the limit leg is not
  applied. For this source the stop is met on nearly every later bar, so the
  limit would rarely bind; recorded as a shared-layer limitation, not repaired.
* The `stop=` price is usually already satisfied at placement time (a buy stop
  BELOW the market for the Sell side, above it for the Buy side). The original
  platform triggers such an order at once; the engine triggers it on the first
  later bar with `high >= stop` (long) / `low <= stop` (short), which is the same
  bar's OPEN in the normal case, but rests the order if that whole bar trades
  beyond the stop. Recorded, not repaired (shared layer).
* `qty = na` cannot be passed as literal na: the port maps a non-finite
  `math.floor` result to `None`, and the engine then sizes with the source's
  declared default -- `strategy.fixed` / 1 contract, which is what Pine does with
  `qty = na`. `na` can only arise while `lookbackBars`' window is still filling.
* `math.floor(na)` is na in Pine; a zero denominator is treated the same way.
  Neither is reachable from a real signal bar (the swing window is always full
  once a cross of the EMA can fire on data with a finite EMA) but the mapping is
  written out rather than assumed.
* `syminfo.mintick` is the symbol's minimum increment, which the engine has to be
  told: `source_mintick = 0.1` (BTC/USDT quotes in 0.1), so the 5/20 "pips" are
  0.5 and 2.0 in price. `syminfo.pointvalue` is 1 for BINANCE:BTCUSDT and is
  carried as the literal 1.0; it only scales a quantity that is forced to 1.
* The md's prose claims a "lookback validation" step (that the last 10 bars'
  prices stayed below the EMA before a buy). No such condition exists in the
  code -- `lookbackBars` is the swing window only. Recorded, not restored.
* `plot()` and the two `alertcondition()` calls are display/alert-only and are
  not reproduced.
* The entry is projected to the framework through `enter_long` / `enter_short`
  (and, when the engine reverses, the opposing `exit_*`), and the engine's own
  fill notional is what sizes the framework's order.
* Leverage, margin, liquidation and funding are not modelled; the venue's
  contract-step rounding is not modelled either, so the framework and the engine
  can differ by a rounded quantity (the chain verifier measures that separately).
"""
from __future__ import annotations

import math

import numpy as np
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


def _level(value) -> float | None:
    """An na level is no level: the engine wants None, not a NaN."""
    if value is None:
        return None
    value = float(value)
    return value if np.isfinite(value) else None


def _pine_div(numerator: float, denominator: float) -> float:
    """Pine's `/` with na semantics: a zero or non-finite divisor yields na."""
    if not np.isfinite(numerator) or not np.isfinite(denominator) or denominator == 0.0:
        return float("nan")
    return numerator / denominator


def _pine_floor_ratio(numerator: float, denominator: float) -> float | None:
    """Pine `math.floor(numerator / denominator)`; na in, na out.

    Pine yields na for a non-finite quotient and for a division by zero, and
    `na < 1` compares false, so the `if qty < 1` guard leaves the value as na.
    """
    if not np.isfinite(numerator) or not np.isfinite(denominator) or denominator == 0.0:
        return None
    return float(math.floor(numerator / denominator))


class SMEmaTrendFollowingAutomated_203e9d(PinePortBase, IStrategy):
    source_id = "SM_203e9d2b8ef6c32e"
    source_file = (
        "EMA趋势追踪自动化交易策略-EMA-Trend-Following-Automated-Trading-Strategy.md"
    )
    timeframe = "1d"
    can_short = True
    source_defaults: dict = {
        "emaLength": 50,
        "defaultRiskPercentage": 1.0,
        "stopLossPips": 5.0,
        "takeProfitPips": 20.0,
        "lookbackBars": 10,
    }
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    # No strategy.exit / strategy.close exists anywhere: the only price legs are
    # the ENTRY order's own stop= and limit=, which are the order's activation
    # prices rather than protective exits.
    source_reproduce_stops = False
    source_fidelity_notes = [
        "The direction argument of getStopLoss is INVERTED in the source: the buy "
        "path calls getStopLoss(-1, ...), which takes the helper's else branch and "
        "returns highest(high, lookbackBars) + pips (a level ABOVE the close), and "
        "the sell path calls getStopLoss(1, ...) for lowest(low, lookbackBars) - "
        "pips. Reproduced as written; the md's prose describes the opposite "
        "pairing and is not restored.",
        "Both entries are STOP-LIMIT orders (Pine's entry stop=/limit= are the "
        "order's activation prices, not a protective exit). As a resting entry "
        "this inherits the framework boundary of PINE_SEMANTICS.md section 二.11: "
        "the engine fills on a later bar at the stop price, the projection is a "
        "next-open market order for the framework.",
        "The engine's entry fill path applies the STOP leg only; an entry that "
        "carries both stop= and limit= does not have its limit leg checked "
        "(shared layer, recorded not repaired).",
        "A stop already satisfied at placement time (which is the usual case here) "
        "is triggered by the original platform at once; the engine triggers it on "
        "the first later bar that reaches it and otherwise keeps it resting "
        "(shared layer, recorded not repaired).",
        "qty evaluates to 1 on every signal: close - stopLoss and stopLoss - close "
        "are both <= -0.5 on the Buy and Sell paths respectively, so math.floor is "
        "negative and the `if qty < 1` guard forces 1. The arithmetic is "
        "reproduced rather than the constant hard-coded.",
        "An na qty (math.floor of a non-finite quotient -- only reachable while the "
        "lookbackBars window is filling) maps to None, and the engine then sizes "
        "with strategy.fixed / 1 contract, which is what Pine does with qty = na.",
        "syminfo.mintick is modelled as 0.1 (BTC/USDT's increment), so 5 / 20 pips "
        "are 0.5 / 2.0 in price; syminfo.pointvalue is the literal 1.0 for "
        "BINANCE:BTCUSDT and only scales a quantity that is forced to 1.",
        "The md claims a 'lookback validation' step (recent prices held below the "
        "EMA before a buy); no such condition exists in the code -- lookbackBars "
        "is only the swing window. Recorded, not restored.",
        "plot() and the two alertcondition() calls are display/alert-only.",
        "No stop/close call exists, so source_reproduce_stops is False and a "
        "position open at the end of the window stays open.",
        "The /*backtest header's basePeriod: 1h is the FMZ backtester's own "
        "granularity for filling the daily bars, not the strategy's period.",
        "Leverage, margin, liquidation, funding and the venue's contract-step "
        "rounding are not modelled; the chain verifier measures that rounding "
        "separately rather than treating it as a signal difference.",
    ]

    def pine_indicators(self, dataframe, params):
        close = dataframe["close"]
        high = dataframe["high"]
        low = dataframe["low"]
        lookback = int(params["lookbackBars"])

        ema_value = ta.pine_ema(close, int(params["emaLength"]))
        dataframe["pine_ema"] = ema_value
        dataframe["pine_cross_up"] = ta.pine_crossover(close, ema_value)
        dataframe["pine_cross_dn"] = ta.pine_crossunder(close, ema_value)
        # getStopLoss(1, n) -> lowest low minus pips; getStopLoss(-1, n) -> the
        # else branch, highest high plus pips. The Buy path uses the latter and
        # the Sell path the former (see FIDELITY).
        dataframe["pine_low_swing"] = ta.pine_lowest(low, lookback)
        dataframe["pine_high_swing"] = ta.pine_highest(high, lookback)
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "close": dataframe["close"].to_numpy(dtype=float),
            "cross_up": dataframe["pine_cross_up"].to_numpy(dtype=bool),
            "cross_dn": dataframe["pine_cross_dn"].to_numpy(dtype=bool),
            "low_swing": dataframe["pine_low_swing"].to_numpy(dtype=float),
            "high_swing": dataframe["pine_high_swing"].to_numpy(dtype=float),
            "risk_percentage": float(params["defaultRiskPercentage"]) / 100.0,
            "stop_loss_pips": float(params["stopLossPips"]),
            "take_profit_pips": float(params["takeProfitPips"]),
            "mintick": float(self.source_mintick),
            # syminfo.pointvalue for BINANCE:BTCUSDT is 1.
            "pointvalue": 1.0,
        }

    def pine_script(self, broker, i, ctx):
        close = float(ctx["close"][i])
        mintick = ctx["mintick"]
        pointvalue = ctx["pointvalue"]
        risk_amount = broker.equity * ctx["risk_percentage"]

        # if ta.crossover(close, emaValue)
        if ctx["cross_up"][i]:
            # stopLoss = getStopLoss(-1, lookbackBars)  -> the helper's ELSE
            # branch: highest high + pips.
            stop_loss = ctx["high_swing"][i] + ctx["stop_loss_pips"] * mintick
            take_profit = close + ctx["take_profit_pips"] * mintick
            # qty := math.floor(riskAmount / (close - stopLoss) / pointvalue)
            qty = _pine_floor_ratio(
                _pine_div(risk_amount, close - stop_loss), pointvalue
            )
            # if qty < 1 -- an na qty compares false and stays na.
            if qty is not None and qty < 1:
                qty = 1.0
            broker.entry(
                "Buy", "long", qty=qty,
                stop=_level(stop_loss), limit=_level(take_profit),
            )

        # if ta.crossunder(close, emaValue)
        if ctx["cross_dn"][i]:
            # stopLoss = getStopLoss(1, lookbackBars) -> lowest low - pips.
            stop_loss = ctx["low_swing"][i] - ctx["stop_loss_pips"] * mintick
            take_profit = close - ctx["take_profit_pips"] * mintick
            # qty := math.floor(riskAmount / (stopLoss - close) / pointvalue)
            qty = _pine_floor_ratio(
                _pine_div(risk_amount, stop_loss - close), pointvalue
            )
            if qty is not None and qty < 1:
                qty = 1.0
            broker.entry(
                "Sell", "short", qty=qty,
                stop=_level(stop_loss), limit=_level(take_profit),
            )
