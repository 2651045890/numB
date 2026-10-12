"""Port of sources/SM_5a22b601b595c3a5.pine (1-3-1-红绿K线反转策略1-3-1-Red-Green-Candlestick-Reversal-Strategy.md).

Pine v5, long only. A pure candlestick-pattern setup on the 1h chart:

    redCandle    = close[3] < open[3] and low[3] < low[2] and low[3] < low[1] and low[3] < low
    greenCandles = close > open and close[1] > open[1] and close[2] > open[2]
    higherClose  = close > close[1] and close[1] > close[2]
    setup        = redCandle and greenCandles and higherClose

i.e. a red candle three bars back, undercut by every one of the three bars
since, followed by three green candles with rising closes. On that bar, and
only while flat, the script latches `stopLossPrice = low[3]`, derives
`takeProfitPrice = close + (close - stopLossPrice)`, and places
`strategy.entry("Long", strategy.long)` -- a MARKET order, so it fills at the
next bar's open. The exit is a single OCA
`strategy.exit("Take Profit/Stop Loss", stop=stopLossPrice, limit=takeProfitPrice)`
placed on the bar after the fill (the source guards it with
`strategy.position_size > 0`, which is only observable once the entry has
filled), resting both legs until one of them is touched.

`stopLossPrice` and `takeProfitPrice` are `var float` -- initialised to na on
the first bar and carried forward after that. `stopLossPrice` is NEVER reset:
once any setup has fired it stays non-na for the rest of the run, so
`takeProfitPrice` keeps being recomputed on every FLAT bar after the first
signal (`close + (close - stopLossPrice)` off the last latched stop). While a
position is open both are frozen, and on a fresh setup bar the stop is
re-assigned before the take-profit is derived from it, so the levels the exit
actually rests at are always the ones latched on the entry's own signal bar.

The source declares `default_qty_type = strategy.percent_of_equity` with
`default_qty_value = 100` -- a full-equity position. Everything else is Pine's
documented default: initial capital 1000000 USD, commission 0%, pyramiding 0.

FIDELITY:

* The two `var float` state variables are modelled explicitly, as a per-run
  mutable state dict handed to the script through `pine_context`. A run-local
  container is what keeps the causality check meaningful: every
  `populate_indicators` call (full frame or truncated prefix) starts a fresh
  run and therefore fresh `var` state, exactly as a Pine run does.
* `close[3]` / `low[3]` history references are pandas shifts. Pine returns na
  where the shift is unavailable and treats na comparisons as false, so the
  setup column is False (not na) for the first three bars -- identical in the
  only place it is read, the `if` of the script body.
* The take-profit is anchored to the SIGNAL BAR'S CLOSE, not to the fill price
  (`close + (close - stopLossPrice)`), while the entry actually fills on the
  next bar's open. That is the source's own arithmetic and is reproduced as
  written; the reward:risk of a filled trade is therefore only nominally 1:1.
* `strategy.exit` carries no `from_entry`, so it applies to the whole position;
  the engine's `from_entry=None` closes every open entry, which here is the
  single long.
* `stopLossPriceD` / `takeProfitPriceD` and the `plotshape` / `plot` calls are
  display-only: nothing reads them and they place no orders, so they are not
  reproduced. The two `plotshape` calls are byte-identical duplicates in the
  source.
* `can_short` is False: no path in the source ever enters short.
"""
from __future__ import annotations

import numpy as np
from freqtrade.strategy import IStrategy

from pine_port_base import PinePortBase


class SM123RedGreen_5a22b6(PinePortBase, IStrategy):
    source_id = "SM_5a22b601b595c3a5"
    source_file = (
        "1-3-1-红绿K线反转策略1-3-1-Red-Green-Candlestick-Reversal-Strategy.md"
    )
    timeframe = "1h"
    can_short = False
    source_defaults: dict = {}
    source_qty_type = "percent_of_equity"
    source_qty_value = 100.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    source_fidelity_notes = [
        "The `var float stopLossPrice` / `var float takeProfitPrice` pair is "
        "reproduced as per-run state in pine_context, not as dataframe columns: "
        "their values depend on the engine's position at each bar, so they only "
        "exist during the run. `stopLossPrice` is never reset to na (the source "
        "only resets the two display variables `stopLossPriceD`/"
        "`takeProfitPriceD`), so after the first setup it stays non-na forever "
        "and `takeProfitPrice` is recomputed on every flat bar -- modelled as "
        "written.",
        "The take-profit level is anchored to the signal bar's close rather than "
        "to the fill price: the entry fills at the next bar's open, so a filled "
        "trade's realised reward:risk is only nominally 1:1. This is the "
        "source's arithmetic, not a translation choice.",
        "History references (`close[3]`, `low[3]`, `low[2]`, ...) are pandas "
        "shifts. Pine's na comparisons are false, so the setup condition is "
        "False -- not na -- on the first three bars, which is how the script's "
        "`if` reads it.",
        "`stopLossPriceD`, `takeProfitPriceD`, the two identical `plotshape` "
        "calls and the two `plot` calls are display-only (nothing reads them, "
        "they place no orders) and are dropped.",
        "Entry is a market order, so Pine's next-bar-open fill and Freqtrade's "
        "next-candle-open fill coincide; the exit is a resting stop+limit OCA, "
        "which is mirrored through pine_stop_level / pine_limit_level.",
        "verify_chain on BTC/USDT:USDT 1h 2024 (8785 bars): 207 closed trades "
        "engine and 207 framework, with no open_date, close_date or direction "
        "difference; exactly one price differs (largest gap 70.2, trade at "
        "2024-06-27). There the stop gapped through at the 20:00 bar (open "
        "61454.8 below the 61525.0 latched from low[3]): pine_engine fills a "
        "gapped stop at the open per Pine's rule, while Freqtrade's "
        "_get_close_rate_for_stoploss fills at the stop price unless the stop is "
        "beyond the bar's high. A framework fill-rule difference on one bar, not "
        "a port defect; the port is unchanged.",
        "No future-data reference and no repainting: the setup reads close[3] / "
        "open[3] / low[3] and earlier bars only, the entry fills on the next "
        "bar's open, and the exit rests until a level is touched.",
    ]

    def pine_indicators(self, dataframe, params):
        close = dataframe["close"]
        open_ = dataframe["open"]
        low = dataframe["low"]
        # redCandle = close[3] < open[3] and low[3] < low[2] and low[3] < low[1]
        #             and low[3] < low[0]
        low3 = low.shift(3)
        red_candle = (
            (close.shift(3) < open_.shift(3))
            & (low3 < low.shift(2))
            & (low3 < low.shift(1))
            & (low3 < low)
        )
        # greenCandles = close > open and close[1] > open[1] and close[2] > open[2]
        green_candles = (
            (close > open_)
            & (close.shift(1) > open_.shift(1))
            & (close.shift(2) > open_.shift(2))
        )
        # higherClose = close > close[1] and close[1] > close[2]
        higher_close = (close > close.shift(1)) & (close.shift(1) > close.shift(2))
        dataframe["red_candle"] = red_candle.fillna(False).astype(bool)
        dataframe["green_candles"] = green_candles.fillna(False).astype(bool)
        dataframe["higher_close"] = higher_close.fillna(False).astype(bool)
        dataframe["pine_setup"] = (
            dataframe["red_candle"]
            & dataframe["green_candles"]
            & dataframe["higher_close"]
        )
        # stopLossPrice := low[3] -- the red candle's own low.
        dataframe["pine_low3"] = low3
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "setup": dataframe["pine_setup"].to_numpy(dtype=bool),
            "low3": dataframe["pine_low3"].to_numpy(dtype=float),
            "close": dataframe["close"].to_numpy(dtype=float),
            # `var float stopLossPrice = na` / `var float takeProfitPrice = na`:
            # na until the first setup, then carried across bars.
            "state": {"stop_loss": float("nan"), "take_profit": float("nan")},
        }

    def pine_script(self, broker, i, ctx):
        state = ctx["state"]
        position = broker.position_size
        stop_loss = state["stop_loss"]
        take_profit = state["take_profit"]

        # Calcul du stop-loss
        # if (redCandle and greenCandles and higherClose) and strategy.position_size == 0
        #     stopLossPrice := low[3]
        if ctx["setup"][i] and position == 0:
            stop_loss = float(ctx["low3"][i])
            state["stop_loss"] = stop_loss

        # Calcul du take-profit
        # if (not na(stopLossPrice)) and strategy.position_size == 0
        #     takeProfitPrice := close + (close - stopLossPrice)
        if not np.isnan(stop_loss) and position == 0:
            take_profit = float(ctx["close"][i]) + (float(ctx["close"][i]) - stop_loss)
            state["take_profit"] = take_profit

        # Entrée en position long
        # if (redCandle and greenCandles and higherClose) and strategy.position_size == 0
        #     strategy.entry("Long", strategy.long)
        if ctx["setup"][i] and position == 0:
            broker.entry("Long", "long")

        # Sortie de la position
        # if (not na(stopLossPrice)) and strategy.position_size > 0
        #     strategy.exit("Take Profit/Stop Loss", stop=stopLossPrice, limit=takeProfitPrice)
        if not np.isnan(stop_loss) and position > 0:
            broker.exit(
                "Take Profit/Stop Loss",
                stop=float(stop_loss),
                limit=float(take_profit),
            )
