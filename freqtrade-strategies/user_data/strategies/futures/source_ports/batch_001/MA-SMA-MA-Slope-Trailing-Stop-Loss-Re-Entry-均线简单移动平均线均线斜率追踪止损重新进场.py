"""Port of sources/SM_d90e2f2e2bfbe34b.pine (batch_001/MA-SMA-MA-Slope-Trailing-Stop-Loss-Re-Entry-均线简单移动平均线均线斜率追踪止损重新进场.md).

Pine v5. A 150-bar SMA traded on its own slope, with a percentage stop that is
re-armed every bar and a conditional re-entry latch:

    windowSize = input.int(10)             // Window Size
    maLength   = input.int(150)            // Moving Average Length
    minSlope   = input.float(0.001)        // Minimum Slope
    trailingStopPercentage = input.float(2.8) / 100
    reEntryPercentage      = input.float(4.2) / 100

    ma         = ta.sma(close, maLength)
    previousMa = ta.sma(close[windowSize], maLength)
    slopeMa    = (ma - previousMa) / windowSize
    isAboveMinSlope = slopeMa > minSlope
    isAboveMa       = close > ma

    var bool  stopLossOccurred = false
    var float trailStopPrice   = na
    buyCondition = isAboveMinSlope and isAboveMa
        and ((not stopLossOccurred) or (stopLossOccurred and low < ma * (1 + reEntryPercentage)))

    if (buyCondition and strategy.opentrades == 0)
        if (stopLossOccurred and close < ma * (1 + reEntryPercentage))
            strategy.entry("Long", strategy.long)
            stopLossOccurred := false
        else if (not stopLossOccurred)
            strategy.entry("Long", strategy.long)

    if (strategy.opentrades == 1)
        trailStopPrice := close * (1 - trailingStopPercentage)
        strategy.exit("Trail Stop", "Long", stop = close * (1 - trailingStopPercentage))

    sellCondition = ta.crossunder(close, ma)
    if (sellCondition and strategy.opentrades == 1)
        strategy.close("Long")

    if (strategy.closedtrades > 0)
        lastExitPrice = strategy.closedtrades.exit_price(strategy.closedtrades - 1)
        if (not na(trailStopPrice) and lastExitPrice <= trailStopPrice)
            stopLossOccurred := true

    if (ta.crossunder(close, ma))
        stopLossOccurred := false

The stop is named "Trail Stop" but is a plain `stop=` level recomputed from
this bar's close and re-placed on every bar the position is open; the engine
replaces a same-id exit order rather than stacking a copy, so the level in
force is always the newest one (PINE_SEMANTICS.md 1.9 / 3.6).

`strategy()` declares `overlay=true` and `calc_on_every_tick=true` besides the
title, so the order/trade properties are Pine's documented defaults:
`strategy.fixed` / 1 contract, initial capital 1000000, commission 0%,
`pyramiding 0`. `process_orders_on_close` is not set, so it stays false.

The `/*backtest` header declares `period: 1h` on Futures_Binance BTC_USDT, so
`timeframe` is "1h"; its `basePeriod: 15m` is the FMZ backtester's own
granularity for filling those 1h bars, not the strategy's period.

No short entry exists anywhere, so `can_short` is False. The source DOES place
a stop exit, so `source_reproduce_stops` is True and the engine's stop level is
mirrored into `custom_stoploss` for the framework.

FIDELITY:

* `calc_on_every_tick=true` is NOT modelled. The source asks the platform to
  recompute the script inside the bar and on every tick; the shared engine runs
  the script once per bar, at its close (PINE_SEMANTICS.md section 二.5 records
  the same limitation for `varip`). Every state read (`strategy.opentrades`,
  `strategy.closedtrades`, `stopLossOccurred`, `trailStopPrice`) therefore
  advances once per bar here. On a realtime feed the source could enter and be
  stopped inside one bar; this port cannot. Imported limitation, not new.
* The two `var` variables (`stopLossOccurred`, `trailStopPrice`) live in the
  run's own context dict, so they reset per run and reproduce Pine's
  bar-to-bar persistence within one run. They are deliberately not stored on
  the strategy instance: `populate_indicators` is called repeatedly on
  truncated prefixes by the causality check, and instance state would leak
  across those calls.
* `previousMa = ta.sma(close[windowSize], maLength)` is the SMA of the series
  shifted back by `windowSize`, not a window of `maLength + windowSize`; the
  port shifts first and then smooths, which is what the source's `close[n]`
  argument means.
* `strategy.closedtrades.exit_price(strategy.closedtrades - 1)` is the exit
  price of the most recently closed trade, mapped to the engine's last booked
  trade. Pine evaluates it at this bar's close, after the bar's own fills, and
  so does the engine (`mark()` runs before the script), so a stop that filled
  at this bar's open is already included.
* The stop level uses `close * (1 - p)`, computed from the SIGNAL bar's close
  and resting from the next bar on, which is what the engine does with a
  `strategy.exit` placed at bar `t`. Because the level is derived from a
  percentage rather than quoted on the venue's grid it can sit between grid
  points, so the framework's one-sided price rounding may move it by up to a
  tick (PINE_SEMANTICS.md 1.11); the chain verifier reports that separately from
  a real price error.
* The re-entry latch is asymmetric in the source and is reproduced as written:
  the outer test accepts a re-entry when `low` dips below the band, but the
  inner branch still requires `close` to be below it, so a bar that only
  wicked under the band enters nothing and leaves the latch set.
* `stopLossOccurred` is cleared by the entry branch and again by the trailing
  `if (ta.crossunder(close, ma))` at the bottom; both are reproduced, in the
  source's own order, because the later clears can affect the next bar.
* The stop re-placement is gated on `strategy.opentrades == 1`, and the last
  block on `strategy.closedtrades > 0`; both are read as the engine's
  `open_trades` / `closed_trades` counts, which count open entry legs and
  booked round trips exactly as Pine does with `pyramiding 0`.
* The md prose matches the code, including the re-entry rule. Its step 6
  ("re-enters when price retraces below the SMA by a specific percentage")
  understates the code, which additionally requires the slope and the
  `close`-vs-band test.
* `plot` and `overlay` are display-only and are not reproduced.
* Leverage, margin, liquidation, funding and contract-step rounding are not
  modelled; the venue's rounding can differ from the engine's float quantity,
  which the chain verifier measures separately.
"""
import numpy as np

from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


class SMMaSlopeTrailingStopReEntry_d90e2f(PinePortBase, IStrategy):
    source_id = "SM_d90e2f2e2bfbe34b"
    source_file = (
        "MA-SMA-MA-Slope-Trailing-Stop-Loss-Re-Entry-"
        "均线简单移动平均线均线斜率追踪止损重新进场.md"
    )
    timeframe = "1h"
    can_short = False
    source_defaults: dict = {
        "windowSize": 10,
        "maLength": 150,
        "minSlope": 0.001,
        "trailingStopPercentage": 2.8,
        "reEntryPercentage": 4.2,
    }
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    source_reproduce_stops = True
    source_fidelity_notes = [
        "`calc_on_every_tick=true` is not modelled: the engine runs the script "
        "once per bar at its close, so every state read advances per bar and a "
        "realtime entry-plus-stop inside one bar cannot be reproduced "
        "(PINE_SEMANTICS.md section 二.5, same limitation as `varip`).",
        "The `var` variables stopLossOccurred / trailStopPrice live in the "
        "run's own context dict rather than on the strategy instance, because "
        "populate_indicators is re-invoked on truncated prefixes by the "
        "causality check and instance state would leak across those calls.",
        "`ta.sma(close[windowSize], maLength)` smooths the series SHIFTED by "
        "windowSize; the port shifts first, then smooths.",
        "`strategy.closedtrades.exit_price(strategy.closedtrades - 1)` is the "
        "last booked trade's exit price; the engine books fills before the "
        "script runs, so a stop that filled at this bar's open is included, as "
        "it is on the platform.",
        "The stop level `close * (1 - p)` is derived from a percentage and need "
        "not sit on the venue's price grid, so the framework's one-sided "
        "rounding may move it by up to a tick (PINE_SEMANTICS.md 1.11); the "
        "chain verifier reports that separately from a real price error.",
        "The stop is named \"Trail Stop\" but is a plain stop= level re-placed "
        "every open bar; a same-id strategy.exit REPLACES the resting order in "
        "the engine, so only the newest level is live (PINE_SEMANTICS.md "
        "1.9 / 3.6).",
        "The re-entry latch is asymmetric as written: the outer test accepts a "
        "re-entry when `low` dips under the band, while the inner branch still "
        "requires `close` to be under it, so a bar that only wicked below "
        "enters nothing and leaves the latch set. Reproduced unchanged.",
        "stopLossOccurred is cleared both by the entry branch and by the "
        "trailing `if (ta.crossunder(close, ma))` block at the bottom; both are "
        "reproduced in the source's order.",
        "No short entry exists, so can_short is False; the stop exit exists, so "
        "source_reproduce_stops is True.",
        "plot / overlay are display-only and not reproduced.",
        "Leverage, margin, liquidation, funding and contract-step rounding are "
        "not modelled; the venue's rounding can differ from the engine's float "
        "quantity, which the chain verifier measures separately.",
    ]

    def pine_indicators(self, dataframe, params):
        close = dataframe["close"]
        window_size = int(params["windowSize"])
        ma_length = int(params["maLength"])
        min_slope = float(params["minSlope"])
        # The source divides both percentages by 100 at the input.
        trailing_stop = float(params["trailingStopPercentage"]) / 100.0
        re_entry = float(params["reEntryPercentage"]) / 100.0

        # ma = ta.sma(close, maLength)
        ma = ta.pine_sma(close, ma_length)
        # previousMa = ta.sma(close[windowSize], maLength)
        previous_ma = ta.pine_sma(close.shift(window_size), ma_length)
        # slopeMa = (ma - previousMa) / windowSize
        slope_ma = (ma - previous_ma) / window_size

        # isAboveMinSlope = slopeMa > minSlope ; isAboveMa = close > ma
        is_above_min_slope = slope_ma > min_slope
        is_above_ma = close > ma

        dataframe["pine_ma"] = ma
        dataframe["pine_previous_ma"] = previous_ma
        dataframe["pine_slope_ma"] = slope_ma
        dataframe["pine_is_above_min_slope"] = is_above_min_slope
        dataframe["pine_is_above_ma"] = is_above_ma
        # The two re-entry band tests are bar-local; the latch that gates them
        # is state, and is held in the script.
        dataframe["pine_low_below_reentry"] = dataframe["low"] < ma * (1 + re_entry)
        dataframe["pine_close_below_reentry"] = close < ma * (1 + re_entry)
        # sellCondition = ta.crossunder(close, ma)
        dataframe["pine_crossunder_ma"] = ta.pine_crossunder(close, ma)
        dataframe["pine_trailing_stop_pct"] = trailing_stop
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "close": dataframe["close"].to_numpy(),
            "low": dataframe["low"].to_numpy(),
            "trailing_stop_pct": dataframe["pine_trailing_stop_pct"].to_numpy(),
            "is_above_min_slope": dataframe["pine_is_above_min_slope"].to_numpy(),
            "is_above_ma": dataframe["pine_is_above_ma"].to_numpy(),
            "low_below_reentry": dataframe["pine_low_below_reentry"].to_numpy(),
            "close_below_reentry": dataframe["pine_close_below_reentry"].to_numpy(),
            "crossunder_ma": dataframe["pine_crossunder_ma"].to_numpy(),
            # var bool stopLossOccurred = false
            # var float trailStopPrice  = na
            "state": {"stop_loss_occurred": False, "trail_stop_price": float("nan")},
        }

    def pine_script(self, broker, i, ctx):
        state = ctx["state"]
        close = float(ctx["close"][i])
        trailing_stop_pct = float(ctx["trailing_stop_pct"][i])
        is_above_min_slope = bool(ctx["is_above_min_slope"][i])
        is_above_ma = bool(ctx["is_above_ma"][i])
        low_below_reentry = bool(ctx["low_below_reentry"][i])
        close_below_reentry = bool(ctx["close_below_reentry"][i])
        sell_condition = bool(ctx["crossunder_ma"][i])

        stop_loss_occurred = state["stop_loss_occurred"]
        trail_stop_price = state["trail_stop_price"]

        # buyCondition = isAboveMinSlope and isAboveMa
        #     and ((not stopLossOccurred)
        #          or (stopLossOccurred and low < ma * (1 + reEntryPercentage)))
        buy_condition = is_above_min_slope and is_above_ma and (
            (not stop_loss_occurred)
            or (stop_loss_occurred and low_below_reentry)
        )

        # if (buyCondition and strategy.opentrades == 0)
        if buy_condition and broker.open_trades == 0:
            if stop_loss_occurred and close_below_reentry:
                # strategy.entry("Long", strategy.long)
                broker.entry("Long", "long")
                # stopLossOccurred := false
                state["stop_loss_occurred"] = False
            elif not stop_loss_occurred:
                # strategy.entry("Long", strategy.long)
                broker.entry("Long", "long")

        # Trailing stop-loss: if (strategy.opentrades == 1)
        if broker.open_trades == 1:
            # trailStopPrice := close * (1 - trailingStopPercentage)
            trail_stop_price = close * (1 - trailing_stop_pct)
            state["trail_stop_price"] = trail_stop_price
            # strategy.exit("Trail Stop", "Long",
            #               stop = close * (1 - trailingStopPercentage))
            broker.exit(
                "Trail Stop", "Long", stop=close * (1 - trailing_stop_pct)
            )

        # Exit condition: if (sellCondition and strategy.opentrades == 1)
        if sell_condition and broker.open_trades == 1:
            # strategy.close("Long")
            broker.close("Long")

        # Check if stop loss occurred
        # if (strategy.closedtrades > 0)
        if broker.closed_trades > 0:
            # lastExitPrice = strategy.closedtrades.exit_price(
            #     strategy.closedtrades - 1)
            last_exit_price = float(broker.trades[-1].exit_price)
            if (not np.isnan(trail_stop_price)) and last_exit_price <= trail_stop_price:
                # stopLossOccurred := true
                state["stop_loss_occurred"] = True

        # Reset stop loss flag if the price crosses below the MA
        # if (ta.crossunder(close, ma))
        if sell_condition:
            state["stop_loss_occurred"] = False
