"""Port of sources/SM_8023ed176c868aac.pine (batch_001/MACD-ATR-EMA-多重指标动态趋势跟踪策略-MACD-ATR-EMA-Multi-Indicator-Dynamic-Trend-Following-Strategy.md).

Pine v5, `strategy("[ROOT] MACD, ATR, & EMA Strategy", overlay = true)`. A MACD
cross against its signal line, filtered by two EMAs, an ATR threshold and the
sign of both MACD lines, with an ATR-or-swing stop handed to the entry and a
market close on the fast EMA:

    MACD   = ta.ema(close, 12) - ta.ema(close, 26)
    signal = ta.ema(MACD, 9)
    slow_ema = ta.ema(close, 200)
    fast_ema = ta.ema(close, 50)
    atr_value = ta.atr(14)
    recent_swing_high = ta.highest(high, 10)     // swing_lookback
    recent_swing_low  = ta.lowest(low, 10)

    var float long_stop_loss  = na
    var float short_stop_loss = na
    if (stop_loss_type == "Swing Low/High")
        long_stop_loss  := recent_swing_low  - (stop_loss_buffer * atr_value)
        short_stop_loss := recent_swing_high + (stop_loss_buffer * atr_value)
    else if (stop_loss_type == "ATR-Based")
        long_stop_loss  := close - (stop_loss_buffer * atr_value)
        short_stop_loss := close + (stop_loss_buffer * atr_value)

    capital_to_use = strategy.equity * (risk_per_trade / 100)
    position_size  = capital_to_use / close

    atr_filter      = atr_value > min_atr_threshold
    long_condition  = atr_filter and ta.crossover(MACD, signal) and close > slow_ema
                      and close > fast_ema and MACD < 0 and signal < 0
    short_condition = atr_filter and ta.crossunder(MACD, signal) and close < slow_ema
                      and close < fast_ema and MACD > 0 and signal > 0
    no_open_trades  = (strategy.opentrades == 0)

    if (long_condition  and barstate.isconfirmed and no_open_trades)
        strategy.entry("Long",  strategy.long,  qty=position_size, stop=long_stop_loss)
    if (short_condition and barstate.isconfirmed and no_open_trades)
        strategy.entry("Short", strategy.short, qty=position_size, stop=short_stop_loss)

    long_exit_condition  = close < fast_ema
    short_exit_condition = close > fast_ema
    if (long_exit_condition  and barstate.isconfirmed) -> strategy.close("Long")
    if (short_exit_condition and barstate.isconfirmed) -> strategy.close("Short")

Order of operations is preserved: the four order calls run exits LAST, in the
source's own sequence (two entries, then two closes).

`risk_per_trade` defaults to 100.0, i.e. `risk_per_trade / 100 == 1.0`, so
`position_size = strategy.equity / close`: the entry asks for the WHOLE equity
as notional on every signal. That is the source's own sizing and is not
moderated here; PINE_SEMANTICS.md 1.4/1.5 explain why a whole-equity request can
be vetoed by the framework's wallet once the two books drift apart by the
venue's contract-step rounding. The framework is handed the engine's recorded
fill notional rather than a re-derived approximation.

`barstate.isconfirmed` is TRUE on every historical bar -- the engine evaluates
the script once per bar, at its close, which is exactly the confirmed state --
so the conjunct places no condition. It is kept in the port's conditions so the
source's shape is on the record.

THE STOP LEG: `stop=` on a `strategy.entry` is the order's ACTIVATION price, not
a protective stop (Pine attaches those with `strategy.exit`). Both levels here
sit on the far side of the price from the order -- `recent_swing_low - buffer*atr`
is BELOW the close for the long, `recent_swing_high + buffer*atr` is ABOVE it
for the short -- so the stop is already satisfied when the order is placed. The
engine triggers it on the first later bar that reaches it and returns that bar's
OPEN when the level is already through, which is the same price the framework's
projected next-open market entry fills at. When that whole bar trades beyond the
level the engine keeps the order resting instead of entering; the original
platform triggers an already-satisfied stop at once. Recorded, not repaired
(shared layer).

The header declares `period: 1h` on Futures_Binance BTC_USDT, so `timeframe` is
"1h".

FIDELITY:

* `ta.ema` is the modelled first-observation-seeded recursion
  (PINE_SEMANTICS.md 3.1). The 200-period `slow_ema` is therefore defined from
  the second bar here, where the original platform's rule (generally believed to
  be an SMA seed, hence na for the first 199 bars) would hold the long/short
  conditions false for far longer. Historical bars converge, but the early trade
  sequence can differ; this is a recorded equivalence risk, not corrected at the
  port level. Every condition in this source is filtered by `slow_ema`, so the
  effect touches BOTH sides.
* `var float long_stop_loss = na` / `:=` inside the branch: `stop_loss_type` is
  an `input.string` with exactly two options, so one branch always assigns on
  every bar and the `na` initial value is unreachable from the declared options.
  The carry is reproduced anyway (a third value would leave the var at its
  previous bar's value).
* An na stop (only reachable while `swing_lookback` / the ATR window is filling)
  maps to None, i.e. the entry degrades to the market order Pine's na price
  means, rather than an order that rests forever.
* `strategy.opentrades == 0` is read as `broker.open_trades == 0`; the engine
  evaluates it after the bar's fills, as Pine does at the bar's close.
* `label.new(...)` calls on both entry branches are display-only.
* No `strategy.exit` exists and the two exits are market closes, so
  `source_reproduce_stops` is False and the stop levels reach the framework only
  as the entry order's own activation price -- which the projection cannot
  express (PINE_SEMANTICS.md 二.11).
* `alertcondition()` calls are alert-only and are not reproduced.
* Leverage, margin, liquidation and funding are not modelled; the venue's
  contract-step rounding is not modelled either, so the framework and the engine
  can differ by a rounded quantity (the chain verifier measures that separately).
"""
from __future__ import annotations

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


class SMMacdAtrEmaMultiIndicator_8023ed(PinePortBase, IStrategy):
    source_id = "SM_8023ed176c868aac"
    source_file = (
        "MACD-ATR-EMA-多重指标动态趋势跟踪策略-MACD-ATR-EMA-Multi-Indicator-"
        "Dynamic-Trend-Following-Strategy.md"
    )
    timeframe = "1h"
    can_short = True
    source_defaults: dict = {
        "macd_fast_length": 12,
        "macd_slow_length": 26,
        "macd_length": 9,
        "atr_length": 14,
        "slow_ema_length": 200,
        "fast_ema_length": 50,
        "risk_per_trade": 100.0,
        "swing_lookback": 10,
        "stop_loss_type": "Swing Low/High",
        "stop_loss_buffer": 0.5,
        "min_atr_threshold": 0.1,
    }
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    # No strategy.exit / resting exit exists: the only price legs are the ENTRY
    # order's own stop= activation prices, which are not protective exits.
    source_reproduce_stops = False
    source_fidelity_notes = [
        "The stop= on each strategy.entry is the order's ACTIVATION price, not a "
        "protective stop, and it sits on the far side of the price (swing low - "
        "buffer*ATR below the close for the long, swing high + buffer*ATR above it "
        "for the short), so it is already satisfied at placement. The engine "
        "triggers it on the first later bar that reaches it, returning that bar's "
        "open when the level is already through -- the same price the framework's "
        "projected next-open market order fills at -- and rests it when that whole "
        "bar trades beyond the level, where the original platform triggers at once. "
        "Shared-layer behaviour, recorded not repaired.",
        "ta.ema is the modelled first-observation-seeded recursion "
        "(PINE_SEMANTICS.md 3.1), so the 200-period slow_ema is defined from the "
        "second bar here where an SMA-seeded original would be na for ~199 bars. "
        "Every condition in this source is filtered by slow_ema, so the timing of "
        "early entries on BOTH sides carries this recorded equivalence risk; later "
        "history converges and nothing is corrected at the port level.",
        "var float long_stop_loss = na is unreachable from the declared "
        "stop_loss_type options (both branches assign every bar); the carry is "
        "reproduced anyway so a third value behaves as Pine's var would.",
        "An na stop level (only reachable while the swing_lookback / ATR windows "
        "are filling) maps to None, i.e. the entry degrades to the market order "
        "Pine's na price means rather than resting forever.",
        "barstate.isconfirmed is modelled as True: the engine evaluates the script "
        "once per bar at its close, which is the confirmed state. The conjunct "
        "places no condition and is kept for shape.",
        "risk_per_trade defaults to 100.0, so position_size = strategy.equity / "
        "close requests the WHOLE equity as notional per entry. That is the "
        "source's own sizing; PINE_SEMANTICS.md 1.4/1.5 explain why the framework "
        "can veto it once the books drift by the venue's contract step. The "
        "framework is handed the engine's recorded fill notional.",
        "strategy.opentrades == 0 is read as broker.open_trades == 0, evaluated "
        "after the bar's fills, as Pine does at the close.",
        "No strategy.exit exists and both exits are strategy.close market orders, "
        "so source_reproduce_stops is False; the entry's stop activation price "
        "cannot be projected (PINE_SEMANTICS.md 二.11).",
        "label.new() on both entry branches and the alertcondition() calls are "
        "display/alert-only.",
        "strategy() declares only title/overlay, so strategy.fixed / 1 contract, "
        "initial capital 1000000, commission 0%, pyramiding 0 and "
        "process_orders_on_close=false are Pine's documented defaults; qty is "
        "passed explicitly so the default quantity never binds.",
        "Leverage, margin, liquidation, funding and the venue's contract-step "
        "rounding are not modelled; the chain verifier measures that rounding "
        "separately rather than treating it as a signal difference.",
    ]

    def pine_indicators(self, dataframe, params):
        close = dataframe["close"]
        high = dataframe["high"]
        low = dataframe["low"]

        fast = int(params["macd_fast_length"])
        slow = int(params["macd_slow_length"])
        signal_length = int(params["macd_length"])
        atr_length = int(params["atr_length"])
        slow_ema_length = int(params["slow_ema_length"])
        fast_ema_length = int(params["fast_ema_length"])
        swing_lookback = int(params["swing_lookback"])
        buffer = float(params["stop_loss_buffer"])

        macd = ta.pine_ema(close, fast) - ta.pine_ema(close, slow)
        signal = ta.pine_ema(macd, signal_length)
        macd_histogram = macd - signal
        slow_ema = ta.pine_ema(close, slow_ema_length)
        fast_ema = ta.pine_ema(close, fast_ema_length)
        atr_value = ta.pine_atr(dataframe, atr_length)
        recent_swing_high = ta.pine_highest(high, swing_lookback)
        recent_swing_low = ta.pine_lowest(low, swing_lookback)

        atr_filter = atr_value > float(params["min_atr_threshold"])
        long_condition = (
            atr_filter
            & ta.pine_crossover(macd, signal)
            & (close > slow_ema)
            & (close > fast_ema)
            & (macd < 0.0)
            & (signal < 0.0)
        )
        short_condition = (
            atr_filter
            & ta.pine_crossunder(macd, signal)
            & (close < slow_ema)
            & (close < fast_ema)
            & (macd > 0.0)
            & (signal > 0.0)
        )

        # The swing branch and the ATR branch, both computed as columns. Only the
        # one `stop_loss_type` names is read by the script; the other is dead for
        # a given configuration, exactly as the source's if/else if is.
        swing_long_stop = recent_swing_low - buffer * atr_value
        swing_short_stop = recent_swing_high + buffer * atr_value
        atr_long_stop = close - buffer * atr_value
        atr_short_stop = close + buffer * atr_value

        dataframe["pine_macd"] = macd
        dataframe["pine_macd_signal"] = signal
        dataframe["pine_macd_histogram"] = macd_histogram
        dataframe["pine_slow_ema"] = slow_ema
        dataframe["pine_fast_ema"] = fast_ema
        dataframe["pine_atr"] = atr_value
        dataframe["pine_recent_swing_high"] = recent_swing_high
        dataframe["pine_recent_swing_low"] = recent_swing_low
        dataframe["pine_long_condition"] = long_condition
        dataframe["pine_short_condition"] = short_condition
        dataframe["pine_long_exit_condition"] = (close < fast_ema).fillna(False)
        dataframe["pine_short_exit_condition"] = (close > fast_ema).fillna(False)
        dataframe["pine_swing_long_stop"] = swing_long_stop
        dataframe["pine_swing_short_stop"] = swing_short_stop
        dataframe["pine_atr_long_stop"] = atr_long_stop
        dataframe["pine_atr_short_stop"] = atr_short_stop
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "close": dataframe["close"].to_numpy(dtype=float),
            "long_condition": dataframe["pine_long_condition"].to_numpy(dtype=bool),
            "short_condition": dataframe["pine_short_condition"].to_numpy(dtype=bool),
            "long_exit_condition": dataframe["pine_long_exit_condition"].to_numpy(dtype=bool),
            "short_exit_condition": dataframe["pine_short_exit_condition"].to_numpy(dtype=bool),
            "swing_long_stop": dataframe["pine_swing_long_stop"].to_numpy(dtype=float),
            "swing_short_stop": dataframe["pine_swing_short_stop"].to_numpy(dtype=float),
            "atr_long_stop": dataframe["pine_atr_long_stop"].to_numpy(dtype=float),
            "atr_short_stop": dataframe["pine_atr_short_stop"].to_numpy(dtype=float),
            "stop_loss_type": str(params["stop_loss_type"]),
            "risk_fraction": float(params["risk_per_trade"]) / 100.0,
            # `var float long_stop_loss = na` / `var float short_stop_loss = na`
            "state": {"long_stop": float("nan"), "short_stop": float("nan")},
        }

    def pine_script(self, broker, i, ctx):
        close = float(ctx["close"][i])
        stop_loss_type = ctx["stop_loss_type"]
        state = ctx["state"]

        # if (stop_loss_type == "Swing Low/High") ... else if (... == "ATR-Based")
        # ... -- a var, so a value the source never assigns would carry forward.
        if stop_loss_type == "Swing Low/High":
            long_stop_loss = float(ctx["swing_long_stop"][i])
            short_stop_loss = float(ctx["swing_short_stop"][i])
        elif stop_loss_type == "ATR-Based":
            long_stop_loss = float(ctx["atr_long_stop"][i])
            short_stop_loss = float(ctx["atr_short_stop"][i])
        else:
            long_stop_loss = state["long_stop"]
            short_stop_loss = state["short_stop"]
        state["long_stop"] = long_stop_loss
        state["short_stop"] = short_stop_loss

        # capital_to_use = strategy.equity * (risk_per_trade / 100)
        # position_size  = capital_to_use / close
        position_size = broker.equity * ctx["risk_fraction"] / close

        # no_open_trades = (strategy.opentrades == 0)
        no_open_trades = broker.open_trades == 0

        # if (long_condition and barstate.isconfirmed and no_open_trades)
        #     strategy.entry("Long", strategy.long, qty=position_size, stop=long_stop_loss)
        if ctx["long_condition"][i] and no_open_trades:
            broker.entry(
                "Long", "long", qty=position_size, stop=_level(long_stop_loss)
            )

        # if (short_condition and barstate.isconfirmed and no_open_trades)
        #     strategy.entry("Short", strategy.short, qty=position_size, stop=short_stop_loss)
        if ctx["short_condition"][i] and no_open_trades:
            broker.entry(
                "Short", "short", qty=position_size, stop=_level(short_stop_loss)
            )

        # if (long_exit_condition and barstate.isconfirmed) strategy.close("Long")
        if ctx["long_exit_condition"][i]:
            broker.close("Long")
        # if (short_exit_condition and barstate.isconfirmed) strategy.close("Short")
        if ctx["short_exit_condition"][i]:
            broker.close("Short")
