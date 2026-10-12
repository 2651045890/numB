"""Port of sources/SM_7259c740c959dfb5.pine
(batch_001/ARGO波段突破策略ARGO-Range-Breakout-Strategy.md).

Pine v2 (`//@version=2`). A channel breakout around the highest high / lowest low
of the last `length` bars, with the channel shifted inward by a small tolerance:

    upBound        = highest(high, length)
    downBound      = lowest(low, length)
    point, tol     = 1, 1000
    limitBoundUp   = highest(high, length) * (point - dev/tol)
    limitBoundDown = downBound / (point - dev/tol)
    buy       = crossover(close, limitBoundUp)
    closebuy  = cross(high[past], upBound[0])
    sell      = crossunder(close, limitBoundDown)
    closesell = cross(low[past], downBound[0])

    if not na(close[length]) and buy
        strategy.entry("ChBrkLE", strategy.long, stop=limitBoundUp - syminfo.mintick)
    strategy.close("ChBrkLE", when=closebuy)
    if not na(close[length]) and sell
        strategy.entry("ChBrkSE", strategy.short, stop=limitBoundDown + syminfo.mintick)
    strategy.close("ChBrkSE", when=closesell)
    strategy.exit("Out Short", "ChBrkSE", qty_percent=100, profit=na, loss=900, trail_points=400)
    strategy.exit("Out Long",  "ChBrkLE", qty_percent=100, profit=na, loss=900, trail_points=400)

The two entries are STOP orders, not market orders: `stop=` makes each one rest
until price reaches the level. `Target`/`Stop`/`Trailing` are the raw inputs
(0 / 90 / 40) multiplied by 10 in the source, then turned into tick counts for
`strategy.exit`: `Target > 0` is false at the default, so `profit` is na (there
is no take-profit leg); `Stop` gives `loss = 900` ticks and `Trailing` gives
`trail_points = 400` ticks. With `syminfo.mintick` = 0.1 on BTC/USDT:USDT those
are 90.0 and 40.0 in price.

`strategy()` is COMMENTED OUT (`// strategy("ARGO_BAND-STRATEGY", overlay=true,
default_qty_value=10000, scale=true, initial_capital=100, currency=currency.USD)`)
and no other declaration of execution properties exists, so commented code is
read as absent and Pine's documented defaults apply: fixed sizing, qty 1,
initial capital 1000000, commission 0%, `pyramiding=0`. The commented values are
recorded verbatim in `source_fidelity_notes`; they are not adopted (among other
reasons, `default_qty_value=10000` with no `default_qty_type` would mean 10000
whole contracts per entry on a 100-unit account, which cannot fund a single
order).

FIDELITY:

* The exit calls are written SHORT-then-LONG in the source and are re-placed on
  every bar, so the port issues them in that order every bar; the engine keeps
  one order per id and replaces it.
* `trail_points = 400` is passed with NO `trail_offset` (the source gives
  `trail_points=TSP` and never sets `trail_offset`, so it is na). Pine documents
  the trailing order as the PAIR `trail_offset` + (`trail_price` |
  `trail_points`), so an unpaired `trail_points` does not define a trailing exit
  level; the port passes it literally and the engine requires both legs before a
  trail exists, leaving the trail inert. Recorded as an equivalence risk in
  `source_fidelity_notes` and in the blockers -- only the `loss=900` leg is
  modelled as a stop.
* `qty_percent=100` closes the whole entry, which is what the engine's `exit()`
  does (it has no partial-exit parameter); 100 is the whole position, so nothing
  is dropped.
* The stop ENTRY cannot be expressed to Freqtrade: a framework strategy has no
  way to rest a stop entry order, so the projection fires `enter_long` /
  `enter_short` on the bar the order is PLACED and the framework fills it at the
  next open, while the engine rests it until price reaches the level (possibly
  many bars later, at the level). See PINE_SEMANTICS.md section 2 item 11.
* `risk`, `stopBound`, `stopbuy`, `mezzalinea` are computed and never read: dead
  code, declared in `source_defaults` where they are inputs and otherwise not
  reproduced. `colo` / `coloS`, the `plot()` and `fill()` calls and `overlay`
  are display-only.
* `cross(a, b)` is Pine's crossover-or-crossunder; `pine_ta.pine_cross` is used.
* `not na(close[length])` is a warmup guard: no entry before bar `length`
  (default 47). The engine's `close_series` has no na, so the port tests
  `i >= length`.
* Leverage, margin, liquidation and funding are not modelled, and the venue's
  contract-step rounding is not modelled either (the chain verifier measures
  that separately rather than treating it as a signal difference).
"""
import numpy as np
import pandas as pd

from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


class SMArgoRangeBreakout_7259c7(PinePortBase, IStrategy):
    source_id = "SM_7259c740c959dfb5"
    source_file = "ARGO波段突破策略ARGO-Range-Breakout-Strategy.md"
    timeframe = "3h"
    can_short = True
    startup_candle_count = 0
    source_defaults: dict = {
        "risk": 1, "length": 47, "stopBound": 10, "stopT": 5, "dev": 2,
        "past": 5, "Target": 0, "Stop": 90, "Trailing": 40,
    }
    # `// strategy(...)` is commented out; Pine's documented defaults apply.
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    # `strategy.exit(..., loss=900)` is a stop leg, mirrored through the engine's
    # stop level; `stop=` on the entries is a resting entry, not an exit.
    source_reproduce_stops = True
    # `profit` / `loss` / `trail_points` are tick counts, and `stop=` on the
    # entries is offset by one tick; BTC/USDT:USDT quotes in 0.1.
    source_mintick = 0.1
    source_fidelity_notes = [
        "The `strategy(...)` call is COMMENTED OUT and is the file's only "
        "declaration of execution properties, so it is read as absent and Pine's "
        "documented defaults apply: fixed sizing, qty 1, initial capital "
        "1000000, commission 0%, pyramiding 0. The commented values were: "
        "title='ARGO_BAND-STRATEGY', overlay=true, default_qty_value=10000, "
        "scale=true, initial_capital=100, currency=currency.USD. They are "
        "recorded, not adopted -- default_qty_value=10000 with no "
        "default_qty_type would be 10000 contracts per entry on a 100-unit "
        "account.",
        "The entries are STOP orders (`strategy.entry(..., stop=...)`), so they "
        "rest until price reaches the level. Freqtrade's strategy interface "
        "cannot rest a stop entry, so the projection emits the signal on the "
        "placement bar and the framework fills at the next open, while the "
        "engine fills later, at the level. See PINE_SEMANTICS.md section 2 "
        "item 11 -- this is a framework boundary, not an implementation gap.",
        "`trail_points=400` is passed with no `trail_offset` (the source never "
        "sets it, so it is na). Pine documents a trailing order as the PAIR "
        "trail_offset + (trail_price | trail_points); unpaired trail_points "
        "does not define a trailing level, and the engine additionally requires "
        "both to rest a trail, so the trail leg is inert on both sides. "
        "Equivalence risk: if the original platform does apply an unpaired "
        "trail_points, exits on trades that run 40.0 price units into profit "
        "would differ. Recorded, not silently corrected.",
        "`profit` is na at the default (`Target = input(0) * 10`, and "
        "`(Target > 0) ? Target : na`), so there is no take-profit leg; only "
        "`loss = 900` ticks (= 90.0 price at mintick 0.1) is a live exit leg.",
        "`qty_percent=100` is the whole position, which is what the engine's "
        "`exit()` does.",
        "Dead code, not reproduced: `risk` and `stopBound` inputs are never "
        "read, `stopbuy` is computed and never used, `mezzalinea` likewise. "
        "`colo` / `coloS`, the `plot()` and `fill()` calls, `scale` and "
        "`overlay` are display-only.",
        "`cross(high[past], upBound[0])` is Pine's crossover-or-crossunder with "
        "`past` = 5, reproduced with pine_ta.pine_cross.",
        "The source comment describes the strategy as 4-hour on gbpjpy, but the "
        "`/*backtest*/` header and the md's own backtest block both declare "
        "`period: 3h` on Futures_Binance BTC_USDT. The header is the machine-"
        "recorded period and is what the port uses (3h); the 4-hour mention is "
        "the author's original prose. Recorded as an md/source disagreement; "
        "neither was changed.",
        "`not na(close[length])` gates both entries on having `length` bars of "
        "history; the port tests `i >= length`.",
        "Leverage, margin, liquidation and funding are not modelled; the "
        "venue's contract-step rounding is not modelled either.",
    ]

    def pine_indicators(self, dataframe: pd.DataFrame, params: dict) -> pd.DataFrame:
        length = int(params["length"])
        past = int(params["past"])
        dev = float(params["dev"])
        tol = 1000.0
        point = 1.0

        high = dataframe["high"]
        low = dataframe["low"]
        close = dataframe["close"]

        up_bound = ta.pine_highest(high, length)
        down_bound = ta.pine_lowest(low, length)
        limit_bound_up = ta.pine_highest(high, length) * (point - dev / tol)
        limit_bound_down = down_bound / (point - dev / tol)

        dataframe["pine_up_bound"] = up_bound
        dataframe["pine_down_bound"] = down_bound
        dataframe["pine_limit_bound_up"] = limit_bound_up
        dataframe["pine_limit_bound_down"] = limit_bound_down
        dataframe["pine_buy"] = ta.pine_crossover(close, limit_bound_up)
        dataframe["pine_closebuy"] = ta.pine_cross(high.shift(past), up_bound)
        dataframe["pine_sell"] = ta.pine_crossunder(close, limit_bound_down)
        dataframe["pine_closesell"] = ta.pine_cross(low.shift(past), down_bound)
        # `stopbuy` is computed in the source and never read; kept for traceability.
        dataframe["pine_stopbuy"] = limit_bound_up.shift(2) / (point + float(params["stopT"]) / tol)
        dataframe["pine_warmup"] = np.arange(len(dataframe)) >= length
        return dataframe

    def pine_context(self, dataframe: pd.DataFrame, params: dict) -> dict:
        tick = float(self.source_mintick)
        return {
            "buy": dataframe["pine_buy"].to_numpy(),
            "closebuy": dataframe["pine_closebuy"].to_numpy(),
            "sell": dataframe["pine_sell"].to_numpy(),
            "closesell": dataframe["pine_closesell"].to_numpy(),
            "warmup": dataframe["pine_warmup"].to_numpy(),
            "limit_up": dataframe["pine_limit_bound_up"].to_numpy(dtype=float),
            "limit_down": dataframe["pine_limit_bound_down"].to_numpy(dtype=float),
            # Stop entries rest one tick away from the channel side.
            "entry_stop_long": dataframe["pine_limit_bound_up"].to_numpy(dtype=float) - tick,
            "entry_stop_short": dataframe["pine_limit_bound_down"].to_numpy(dtype=float) + tick,
            # strategy.exit tick arguments -> prices (mintick = 0.1)
            "loss_ticks": float(params["Stop"]) * 10.0,
            "profit_ticks": (float(params["Target"]) * 10.0
                             if float(params["Target"]) * 10.0 > 0 else None),
            "trail_points": (float(params["Trailing"]) * 10.0
                             if float(params["Trailing"]) * 10.0 > 0 else None),
        }

    def pine_script(self, broker, i: int, ctx: dict) -> None:
        # if (not na(close[length]))
        #     if (buy)
        #         strategy.entry("ChBrkLE", strategy.long, stop=limitBoundUp - syminfo.mintick, comment="Long I")
        if bool(ctx["warmup"][i]) and bool(ctx["buy"][i]):
            broker.entry("ChBrkLE", "long", stop=float(ctx["entry_stop_long"][i]))

        # strategy.close("ChBrkLE", when=closebuy)
        broker.close("ChBrkLE", when=bool(ctx["closebuy"][i]))

        # if (not na(close[length]))
        #     if (sell)
        #         strategy.entry("ChBrkSE", strategy.short, stop=limitBoundDown + syminfo.mintick, comment="Short I")
        if bool(ctx["warmup"][i]) and bool(ctx["sell"][i]):
            broker.entry("ChBrkSE", "short", stop=float(ctx["entry_stop_short"][i]))

        # strategy.close("ChBrkSE", when=closesell)
        broker.close("ChBrkSE", when=bool(ctx["closesell"][i]))

        # strategy.exit("Out Short", "ChBrkSE", qty_percent=CQ, profit=TPP, loss=SLP, trail_points=TSP)
        broker.exit("Out Short", from_entry="ChBrkSE", profit=ctx["profit_ticks"],
                    loss=ctx["loss_ticks"], trail_points=ctx["trail_points"])
        # strategy.exit("Out Long", "ChBrkLE", qty_percent=CQ, profit=TPP, loss=SLP, trail_points=TSP)
        broker.exit("Out Long", from_entry="ChBrkLE", profit=ctx["profit_ticks"],
                    loss=ctx["loss_ticks"], trail_points=ctx["trail_points"])
