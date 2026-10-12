"""Port of sources/SM_ba06df93d7b4447b.pine
(batch_001/DEMA交叉趋势追踪策略DEMA-Crossover-Trend-Following-Strategy.md).

Pine v4. A double-exponential-MA fast/slow cross, optionally gated by a third
DEMA's own direction, entered outright and managed by ONE OCA exit call that
carries both a stop and a take-profit:

    DEMA(series, length) => length > 0 ? 2*ema(s,length) - ema(ema(s,length),length) : na

    demaCrossover  = (len2>0 and len3>0) ? crossover(d1,d2) and d3 >  d3[1]
                   : (len2>0 and len3==0) ? crossover(d1,d2)
                   : (len3>0 and len2==0) ? crossover(d1,d3)
                   :                        crossover(close, d1)
    demaCrossunder = the same cascade with crossunder / the reversed comparisons

    longStopPrice   = strategy.position_avg_price * (1 - stopPerlong)
    shortStopPrice  = strategy.position_avg_price * (1 + stopPershort)
    longTake1Price  = strategy.position_avg_price * (1 + take1Perlong)
    shortTake1Price = strategy.position_avg_price * (1 - take1Pershort)

    if (_inDateRange)
        if demaCrossover  -> strategy.entry("LONG",  strategy.long)
        if demaCrossunder -> strategy.entry("SHORT", strategy.short)
        if strategy.position_size > 0 -> strategy.exit("TP/SL", "LONG",  stop=longStop,  limit=longTake1Price)
        if strategy.position_size < 0 -> strategy.exit("TP/SL", "SHORT", stop=shortStop, limit=shortTake1Price)
    if (not _inDateRange) -> strategy.close_all()

`strategy()` declares the source's own properties, NOT Pine's defaults:

    commission_value = 0.063, commission_type = strategy.commission.percent
    initial_capital  = 100
    default_qty_value = 90, default_qty_type = strategy.percent_of_equity
    pyramiding       = not declared -> Pine's default 0
    process_orders_on_close = true   <-- NOT reproducible, see FIDELITY

The `/*backtest` header declares `period: 1h` on Futures_Binance BTC_USDT, so
`timeframe` is "1h"; its `basePeriod: 15m` is the FMZ backtester's own fill
granularity for those 1h bars, not the strategy's period.

FIDELITY (what is kept, what is a modelling choice, what cannot be done):

* `process_orders_on_close=true` is NOT reproduced. It makes the original
  platform execute a market order at the CLOSE of the bar the order was placed
  on; the shared engine (`pine_engine.run_pine`) always models "script is
  evaluated at bar `t`'s close, the order fills at bar `t+1`'s open", which is
  the `process_orders_on_close=false` convention. The two differ by one bar in
  timing and by `close[t]` vs `open[t+1]` in price. This is a shared-layer
  modelling choice, recorded here rather than worked around -- compensating for
  it in the port would mean emitting the entry one bar early, which would move
  every fill by one bar relative to the engine that verifies this port.
* The `_inDateRange` window (inputs 2018-01-01 .. 2031-12-31) is reproduced from
  the bar timestamps against UTC, per PINE_SEMANTICS.md 3.4. With the source's
  defaults it is true for every bar in any local dataset, so the trailing
  `strategy.close_all()` never fires; it is kept so that an override of the
  window behaves as the source would.
* `strategy.position_avg_price` is na while flat and the engine returns nan
  there, so `longStop`/`shortStop`/`longTake1Price`/`shortTake1Price` are only
  ever read while a position is open (the source reads them under
  `position_size > 0` / `< 0`, which is mirrored here).
* `a` (`Usar Trailing Stop?`, default false) selects between the fixed
  average-price stop and a recursive trailing stop that ratchets the close
  against its own previous value. It is reproduced as written, including the
  `max`/`min` recursion whose na handling matches Pine's (`max(x, na) -> na`),
  so overriding the input to `true` behaves as the source does.
* The source declares no `mintick`; BTC/USDT:USDT quotes in 0.1, which is the
  value used (`source_mintick`). Only `syminfo.mintick`-scaled arithmetic would
  be affected and this source has none in its orders.
* `strategy.exit(...)` is issued every bar while the position is held, so the
  engine replaces the same-id resting order each bar (Pine keeps one order per
  id). That is the engine's documented behaviour and is left alone.
* Plots, `fill()`, `label.new`/`label.delete`, the alert strings (`resultadoL`,
  `_alertMessage*`, `comment=`) are display/alert only and are not reproduced.
* `percent_of_equity` sizing is taken from the engine's own recorded fill
  notional, not re-derived from the live wallet (PINE_SEMANTICS.md 1.4).
* Leverage, margin, liquidation, funding and the venue's contract-step rounding
  are not modelled (PINE_SEMANTICS.md 1.6 / 二.4-5). The source's initial
  capital of 100 is in the small-capital regime that section flags, so the
  framework's wallet and the engine's cash can drift apart on rounding alone.
"""
import numpy as np
import pandas as pd
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


def _level(value) -> float | None:
    """A price, or None when Pine would have na there (no resting leg)."""
    value = float(value)
    return value if np.isfinite(value) else None


class SMDemaCrossoverTrendFollowing_ba06df(PinePortBase, IStrategy):
    source_id = "SM_ba06df93d7b4447b"
    source_file = "DEMA交叉趋势追踪策略DEMA-Crossover-Trend-Following-Strategy.md"
    timeframe = "1h"
    can_short = True
    # Input defaults, exactly as written in the source.
    source_defaults: dict = {
        "srcData": "close",
        "len1": 8,
        "len2": 24,
        "len3": 0,
        "a": False,
        "stopPerlong": 9.0,
        "stopPershort": 6.0,
        "take1Perlong": 25.0,
        "take1Pershort": 6.0,
        "_startDate": 1,
        "_startMonth": 1,
        "_startYear": 2018,
        "_endDate": 31,
        "_endMonth": 12,
        "_endYear": 2031,
    }
    # strategy(title=..., commission_value=0.063,
    #          commission_type=strategy.commission.percent, initial_capital=100,
    #          default_qty_value=90, default_qty_type=strategy.percent_of_equity,
    #          overlay=true, process_orders_on_close=true)
    source_qty_type = "percent_of_equity"
    source_qty_value = 90.0
    source_commission_percent = 0.063
    source_pyramiding = 0
    source_initial_capital = 100.0
    # strategy.exit(stop=..., limit=...): both legs rest inside the bar.
    source_reproduce_stops = True
    source_mintick = 0.1
    source_fidelity_notes = [
        "`process_orders_on_close=true` in the source is NOT reproduced: the "
        "shared engine always fills at the next bar's open "
        "(PINE_SEMANTICS.md 一), while the source fills at the signal bar's "
        "close. Timing differs by one bar and price by close[t] vs open[t+1]; "
        "this is a shared-layer modelling choice, not something the port can "
        "express without moving every fill.",
        "`strategy()` declares initial_capital=100 and "
        "percent_of_equity/90, i.e. the small-capital regime of "
        "PINE_SEMANTICS.md 1.6 where the venue's contract step is no longer "
        "noise; a chain mismatch is expected there and is not a port error.",
        "commission is `strategy.commission.percent` at 0.063, carried as "
        "source_commission_percent, so Freqtrade's exchange-metadata fee does "
        "not overwrite the source's own cost basis (PINE_SEMANTICS.md 5.1).",
        "The `_inDateRange` guard is reproduced from bar timestamps against "
        "UTC with the source's 2018-01-01..2031-12-31 defaults; it is true on "
        "every bar of any local dataset, so `strategy.close_all()` never fires "
        "in practice but stays reachable if the window inputs are overridden.",
        "`a` (Usar Trailing Stop?, default false) is reproduced with the "
        "source's recursive `max`/`min` ratchet, including Pine's na "
        "propagation, so overriding it to true behaves as the source does.",
        "The two `strategy.exit` calls share the id \"TP/SL\"; Pine keeps one "
        "order per id and the engine replaces same-id exits, so only the arm "
        "that matches the live position is ever resting.",
        "`plot` / `fill` / `label.new` / `label.delete` and every alert string "
        "are display-only and are not reproduced.",
        "mintick is not declared by the source; BTC/USDT:USDT quotes in 0.1, "
        "which is the value carried (no order in this source is mintick-scaled).",
    ]

    # ---- indicators --------------------------------------------------------
    def pine_indicators(self, dataframe, params):
        close = dataframe["close"]
        source = ta.pine_source(dataframe, str(params["srcData"]))

        len1, len2, len3 = int(params["len1"]), int(params["len2"]), int(params["len3"])

        def dema(series, length):
            # DEMA(series, length) => if (length > 0) 2*ema - ema(ema) else na
            if length <= 0:
                return pd.Series(np.nan, index=series.index, dtype=float)
            first = ta.pine_ema(series, length)
            return 2.0 * first - ta.pine_ema(first, length)

        dema_val1 = dema(source, len1)
        dema_val2 = dema(source, len2)
        dema_val3 = dema(source, len3)

        # The source's cascade, evaluated in the source's own order.
        if len2 > 0 and len3 > 0:
            crossover = ta.pine_crossover(dema_val1, dema_val2) & (
                dema_val3 > dema_val3.shift(1)
            )
            crossunder = ta.pine_crossunder(dema_val1, dema_val2) & (
                dema_val3 < dema_val3.shift(1)
            )
        elif len2 > 0 and len3 == 0:
            crossover = ta.pine_crossover(dema_val1, dema_val2)
            crossunder = ta.pine_crossunder(dema_val1, dema_val2)
        elif len3 > 0 and len2 == 0:
            crossover = ta.pine_crossover(dema_val1, dema_val3)
            crossunder = ta.pine_crossunder(dema_val1, dema_val3)
        else:
            crossover = ta.pine_crossover(close, dema_val1)
            crossunder = ta.pine_crossunder(close, dema_val1)

        index = dataframe.index
        if not isinstance(index, pd.DatetimeIndex) and "date" in dataframe.columns:
            index = pd.DatetimeIndex(dataframe["date"])
        times = pd.DatetimeIndex(index)
        if times.tz is None:
            times = times.tz_localize("UTC")
        # timestamp(syminfo.timezone, y, m, d, 0, 0) with the exchange in UTC.
        window_start = pd.Timestamp(
            year=int(params["_startYear"]), month=int(params["_startMonth"]),
            day=int(params["_startDate"]), tz="UTC",
        )
        window_end = pd.Timestamp(
            year=int(params["_endYear"]), month=int(params["_endMonth"]),
            day=int(params["_endDate"]), tz="UTC",
        )

        dataframe["pine_dema1"] = dema_val1
        dataframe["pine_dema2"] = dema_val2
        dataframe["pine_dema3"] = dema_val3
        dataframe["pine_crossover"] = crossover.fillna(False).astype(bool)
        dataframe["pine_crossunder"] = crossunder.fillna(False).astype(bool)
        dataframe["pine_in_date_range"] = np.asarray(
            (times >= window_start) & (times < window_end), dtype=bool
        )
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "close": dataframe["close"].to_numpy(dtype=float),
            "crossover": dataframe["pine_crossover"].to_numpy(dtype=bool),
            "crossunder": dataframe["pine_crossunder"].to_numpy(dtype=bool),
            "in_date_range": dataframe["pine_in_date_range"].to_numpy(dtype=bool),
            "use_trailing": bool(params["a"]),
            "stop_per_long": float(params["stopPerlong"]) / 100.0,
            "stop_per_short": float(params["stopPershort"]) / 100.0,
            "take_per_long": float(params["take1Perlong"]) / 100.0,
            "take_per_short": float(params["take1Pershort"]) / 100.0,
            # longStopPriceTrail / shortStopPriceTrail are self-referencing
            # series (`x[1]`), so their carried value lives beside the frame.
            # `max(x, na) -> na` in Pine, hence the nan seed for the long leg;
            # the short leg's `else` branch is the literal 999999.
            "trail": {"long": float("nan"), "short": float("nan")},
        }

    # ---- orders ------------------------------------------------------------
    def pine_script(self, broker, i, ctx):
        close = float(ctx["close"][i])
        state = ctx["trail"]
        stop_long_pct = ctx["stop_per_long"]
        stop_short_pct = ctx["stop_per_short"]

        # --- lines 78-81, read off the position that is open at this bar ---
        avg_price = broker.position_avg_price
        long_stop_price = avg_price * (1.0 - stop_long_pct)
        short_stop_price = avg_price * (1.0 + stop_short_pct)
        long_take1_price = avg_price * (1.0 + ctx["take_per_long"])
        short_take1_price = avg_price * (1.0 - ctx["take_per_short"])

        # --- lines 85-100, the two recursive trailing series ---
        # longStopPriceTrail := if (strategy.position_size > 0)
        #     max(close * (1 - stopPerlong), longStopPriceTrail[1]) else 0
        if broker.position_size > 0:
            long_trail = np.maximum(close * (1.0 - stop_long_pct), state["long"])
        else:
            long_trail = 0.0
        state["long"] = float(long_trail)

        # shortStopPriceTrail := if (strategy.position_size < 0)
        #     min(close * (1 + stopPershort), shortStopPriceTrail[1]) else 999999
        if broker.position_size < 0:
            short_trail = np.minimum(close * (1.0 + stop_short_pct), state["short"])
        else:
            short_trail = 999999.0
        state["short"] = float(short_trail)

        # --- lines 103-104: longStop = a ? longStopPriceTrail : longStopPrice ---
        if ctx["use_trailing"]:
            long_stop, short_stop = long_trail, short_trail
        else:
            long_stop, short_stop = long_stop_price, short_stop_price

        if ctx["in_date_range"][i]:
            # if (demaCrossover) strategy.entry("LONG", strategy.long, ...)
            if ctx["crossover"][i]:
                broker.entry("LONG", "long")
            # if (demaCrossunder) strategy.entry("SHORT", strategy.short, ...)
            if ctx["crossunder"][i]:
                broker.entry("SHORT", "short")
            # if strategy.position_size > 0 -> strategy.exit("TP/SL", "LONG", ...)
            if broker.position_size > 0:
                broker.exit(
                    "TP/SL", from_entry="LONG",
                    stop=_level(long_stop), limit=_level(long_take1_price),
                )
            # if strategy.position_size < 0 -> strategy.exit("TP/SL", "SHORT", ...)
            if broker.position_size < 0:
                broker.exit(
                    "TP/SL", from_entry="SHORT",
                    stop=_level(short_stop), limit=_level(short_take1_price),
                )
        else:
            # if (not _inDateRange) strategy.close_all()
            broker.close_all()
