"""Port of sources/SM_d607f9cccc745372.pine
(batch_001/Dual-SMA-Momentum-Strategy双SMA动量策略.md).

Pine v5. Close against a fast and a slow SMA, both crossed at once:

    fast_sma = ta.sma(close, 9)
    slow_sma = ta.sma(close, 45)
    buy_condition  = ta.crossover(close, fast_sma)  and ta.crossover(close, slow_sma)
    sell_condition = ta.crossunder(close, fast_sma) and ta.crossunder(close, slow_sma)

    prev_low  = request.security(syminfo.tickerid, "1D", low[1],  lookahead=barmerge.lookahead_on)
    prev_high = request.security(syminfo.tickerid, "1D", high[1], lookahead=barmerge.lookahead_on)

    long_stop_loss  = sell_condition ? prev_low  : na
    short_stop_loss = buy_condition  ? prev_high : na

    strategy.exit("Long Exit",  from_entry="Long",  when=sell_condition, stop=long_stop_loss)
    strategy.exit("Short Exit", from_entry="Short", when=buy_condition,  stop=short_stop_loss)
    strategy.entry("Long",  strategy.long,  when=buy_condition)
    strategy.entry("Short", strategy.short, when=sell_condition)

`strategy()` declares only `title` and `overlay`, so every property is Pine's
documented default: `strategy.fixed` / 1 contract, initial capital 1000000,
commission 0%, pyramiding 0, `process_orders_on_close=false`. The `/*backtest`
header declares `period: 1d` on Futures_Binance BTC_USDT, so `timeframe` is
"1d"; its `basePeriod: 1h` is the FMZ backtester's own granularity for filling
those daily bars, not the strategy's period.

The order calls are reproduced in the source's writing order (both exits before
both entries), which is what decides which of two orders created on one bar is
filled first by the engine -- see PINE_SEMANTICS 1.13.

FIDELITY:

* `request.security(syminfo.tickerid, "1D", low[1], lookahead=barmerge.lookahead_on)`:
  the requested timeframe is the strategy's own ("1d" per the backtest header),
  so the call degenerates to the chart series' `low[1]` -- the previous daily
  bar's low. `lookahead_on` is the future-data marker when the requested
  timeframe is HIGHER than the chart's; here the value read is the previous,
  already-closed bar's low, so nothing future is consumed and the read is
  modelled as `low.shift(1)`. Recorded rather than rewritten (rule 2): the
  `lookahead` argument is left as the source wrote it.
* PINE_SEMANTICS 2.1: the engine does not resample and does not model
  `request.security`. This is not a dependency of the port -- the two reads
  collapse to same-timeframe history references, which are supplied directly.
* Both exits are STOP orders, so `source_reproduce_stops` is True and the
  engine's resting level reaches Freqtrade through `custom_stoploss`. The level
  is `na` on every bar except the one that fires the exit condition, and the
  exit is only CREATED on that bar (`when=sell_condition`); a `na` stop that was
  created anyway would still be a resting order with no trigger price, which is
  why the port passes `nan` rather than `None` for the inactive leg -- `None`
  would make `run_pine` read the order as a legless `strategy.exit` and project
  it as a market exit (PINE_SEMANTICS 1.15).
* `strategy.exit(id, from_entry=...)` is a Pine no-op while the named entry is
  not open -- the engine keeps it resting but neither fills nor publishes it
  (PINE_SEMANTICS 1.12), so `Long Exit` issued on a bar where the position is
  short cannot take the short out.
* `strategy.entry` reverses: an opposing entry closes the old position and opens
  the new one in a single fill (PINE_SEMANTICS 1.1).
* `plotshape` / `overlay` / the strategy title are display-only and place no
  condition; they are not reproduced.
* PINE_SEMANTICS 3.1 (modelled choice): `ta.ema` -- not used here, but `ta.sma`
  returns na until its window is full and na inside the window propagates
  (3.2), which is what `pine_ta.pine_sma` does; the 45-bar SMA therefore gates
  the first signal.
* PINE_SEMANTICS 1.6 / 5.1: the venue's contract-step rounding and non-zero
  taker fees are not modelled. The source declares 0% commission, which is the
  cost basis the port carries.
* Leverage, margin, liquidation and funding are not modelled.
"""
from freqtrade.strategy import IStrategy

import numpy as np

import pine_ta as ta
from pine_port_base import PinePortBase


class SMDualSmaMomentumStrategy_d607f9(PinePortBase, IStrategy):
    source_id = "SM_d607f9cccc745372"
    source_file = "Dual-SMA-Momentum-Strategy双SMA动量策略.md"
    timeframe = "1d"
    # Both directions have a real entry call in the source.
    can_short = True
    source_defaults: dict = {"fast_length": 9, "slow_length": 45}
    # strategy("SMA Crossover Strategy", overlay=true): title/overlay only.
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    # Both exits are strategy.exit(stop=...) -- resting orders, not market exits.
    source_reproduce_stops = True
    source_fidelity_notes = [
        "`request.security(syminfo.tickerid, \"1D\", low[1], "
        "lookahead=barmerge.lookahead_on)` requests the strategy's OWN timeframe "
        "(the backtest header declares period: 1d), so it degenerates to the "
        "chart series' low[1] -- the previous daily bar's low, forward-nothing. "
        "`lookahead_on` is a future-data marker only when the requested "
        "timeframe is higher than the chart's; a completed bar's low is not "
        "future data. Modelled as low.shift(1) / high.shift(1) and recorded "
        "rather than rewritten (rule 2).",
        "PINE_SEMANTICS 2.1: the engine does not model request.security. This "
        "port does not depend on it -- both reads collapse to same-timeframe "
        "history references supplied directly from the frame.",
        "The two exits are resting stop orders, so source_reproduce_stops is "
        "True and their level reaches Freqtrade through custom_stoploss. The "
        "stop level is na on every bar except the one firing the exit "
        "condition; the inactive leg is passed as nan, not None, because a "
        "None-stop exit would be read as a legless strategy.exit and projected "
        "as a market exit (PINE_SEMANTICS 1.15).",
        "strategy.exit(id, from_entry=...) is a no-op while the named entry is "
        "not open (PINE_SEMANTICS 1.12): the engine keeps the order resting but "
        "neither fills it nor publishes its levels, so the LONG arm's stop "
        "cannot exit a SHORT position and vice versa.",
        "Order calls are issued in the source's writing order -- Long Exit, "
        "Short Exit, then the two entries -- which decides the fill order of "
        "same-bar pending orders (PINE_SEMANTICS 1.13, a modelling choice).",
        "strategy.entry reverses: an opposing entry closes the old position and "
        "opens the new one in one fill (PINE_SEMANTICS 1.1).",
        "plotshape / overlay / the strategy title are display-only and place no "
        "condition.",
        "PINE_SEMANTICS 3.2 (modelled choice): ta.sma returns na until its "
        "window is full and na inside the window propagates, so the 45-bar SMA "
        "gates the first signal.",
        "PINE_SEMANTICS 1.6 / 5.1: the venue's contract-step rounding and "
        "non-zero taker fees are not modelled; the source declares 0% "
        "commission, which is the cost basis the port carries.",
        "Leverage, margin, liquidation and funding are not modelled.",
    ]

    def pine_indicators(self, dataframe, params):
        close = dataframe["close"]
        fast_sma = ta.pine_sma(close, int(params["fast_length"]))
        slow_sma = ta.pine_sma(close, int(params["slow_length"]))

        # buy_condition  = ta.crossover(close, fast_sma)  and ta.crossover(close, slow_sma)
        buy_condition = (
            ta.pine_crossover(close, fast_sma) & ta.pine_crossover(close, slow_sma)
        )
        # sell_condition = ta.crossunder(close, fast_sma) and ta.crossunder(close, slow_sma)
        sell_condition = (
            ta.pine_crossunder(close, fast_sma) & ta.pine_crossunder(close, slow_sma)
        )

        # prev_low  = request.security(syminfo.tickerid, "1D", low[1],  lookahead_on)
        # prev_high = request.security(syminfo.tickerid, "1D", high[1], lookahead_on)
        prev_low = dataframe["low"].shift(1)
        prev_high = dataframe["high"].shift(1)

        dataframe["pine_fast_sma"] = fast_sma
        dataframe["pine_slow_sma"] = slow_sma
        dataframe["pine_buy_condition"] = buy_condition
        dataframe["pine_sell_condition"] = sell_condition
        dataframe["pine_prev_low"] = prev_low
        dataframe["pine_prev_high"] = prev_high
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "buy_condition": dataframe["pine_buy_condition"].to_numpy(),
            "sell_condition": dataframe["pine_sell_condition"].to_numpy(),
            "prev_low": dataframe["pine_prev_low"].to_numpy(),
            "prev_high": dataframe["pine_prev_high"].to_numpy(),
        }

    def pine_script(self, broker, i, ctx):
        buy = bool(ctx["buy_condition"][i])
        sell = bool(ctx["sell_condition"][i])

        # long_stop_loss  = sell_condition ? prev_low  : na
        # short_stop_loss = buy_condition  ? prev_high : na
        long_stop_loss = ctx["prev_low"][i] if sell else np.nan
        short_stop_loss = ctx["prev_high"][i] if buy else np.nan

        # strategy.exit("Long Exit", from_entry="Long", when=sell_condition, stop=long_stop_loss)
        broker.exit("Long Exit", from_entry="Long", when=sell, stop=long_stop_loss)
        # strategy.exit("Short Exit", from_entry="Short", when=buy_condition, stop=short_stop_loss)
        broker.exit("Short Exit", from_entry="Short", when=buy, stop=short_stop_loss)
        # strategy.entry("Long", strategy.long, when=buy_condition)
        broker.entry("Long", "long", when=buy)
        # strategy.entry("Short", strategy.short, when=sell_condition)
        broker.entry("Short", "short", when=sell)
