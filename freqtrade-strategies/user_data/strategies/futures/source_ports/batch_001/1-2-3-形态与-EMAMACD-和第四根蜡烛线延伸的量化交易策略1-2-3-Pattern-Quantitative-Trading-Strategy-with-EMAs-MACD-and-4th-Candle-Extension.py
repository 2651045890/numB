"""Port of sources/SM_0a0a82110800bbae.pine
(batch_001/1-2-3-形态与-EMAMACD-和第四根蜡烛线延伸的量化交易策略1-2-3-Pattern-Quantitative-Trading-Strategy-with-EMAs-MACD-and-4th-Candle-Extension.md).

Pine v5, two-sided, fixed 5 contracts per entry. The whole script:

    buy_candle1_above_open  = close[3] > open[3]
    buy_candle2_below_open  = close[2] < open[2]
    buy_candle3_above_close = close[1] > close[3]
    buy_candle4_above_close = close     > close[3]
    sell_candle1_below_open = close[3] < open[3]
    sell_candle2_above_open = close[2] > open[2]
    sell_candle3_below_close = close[1] < close[3]
    sell_candle4_below_close = close     < close[3]

    ema_9  = ta.ema(close, 9)
    ema_20 = ta.ema(close, 20)
    [macd_line, signal_line, _] = ta.macd(close, 12, 26, 9)

    if (buy AND strategy.opentrades == 0 and close > ema_9 and close > ema_20
            and macd_line > signal_line)
        strategy.entry("Buy", strategy.long, qty=5)
    if (close < open and strategy.opentrades > 0)
        strategy.close("Buy", qty=5)
    if (sell AND strategy.opentrades == 0 and close < ema_9 and close < ema_20
            and macd_line < signal_line)
        strategy.entry("Sell", strategy.short, qty=5)
    if (close > open and strategy.opentrades > 0)
        strategy.close("Sell", qty=5)

THE SOURCE HAS NO INPUTS AT ALL, so `source_defaults` is empty and every length
(9 / 20 / 12 / 26 / 9) and the `qty=5` are literals in the source.

THE EXITS ARE NOT SYMMETRIC WITH THE ENTRY DIRECTION. Each `strategy.close` is
gated only on `strategy.opentrades > 0` and the candle's colour, never on the
position's sign, and it names one entry id. Pine scopes `strategy.close(id)` to
that id, so `strategy.close("Buy")` while a short is open closes nothing, and the
engine models that (`_close_entries` matches on `from_entry`). Reproduced by
naming the same ids through `broker.close`, so the no-op stays a no-op.

`qty=5` on the close equals the whole position because the entry gate
`strategy.opentrades == 0` and `pyramiding=0` keep the position at exactly 5
contracts whenever it is open; the broker's `close()` closes the whole position
bound to that id, which is the same thing. On the entry side `qty=5` is passed
through verbatim.

`strategy()` declares only `overlay=true`, so everything else is Pine's
documented default: `default_qty_type=strategy.fixed`, `default_qty_value` 1,
commission 0%, pyramiding 0, initial capital 1000000. The explicit `qty=5` on
every entry makes the default quantity inert, but the declaration is still the
source's and is recorded as such.

The `/*backtest` header declares `period: 1h` on Futures_Binance BTC_USDT, so
`timeframe` is "1h"; its `basePeriod: 15m` is the FMZ backtester's fill
granularity, not the strategy's period.

FIDELITY:

* The md's prose mis-describes the pattern by one candle: it says "the third
  candle's close is above the first candle's close, and the fourth candle's close
  is above the third candle's close". The code tests `close[1] > close[3]` and
  `close > close[3]` -- both compared against `close[3]`, and the bar indexed [2]
  never appears in any of the four buy legs. The code is followed; the md
  sentence is recorded as a disagreement.
* The md also says positions close "when the opposite signal appears", but the
  code's close conditions do not test the 1-2-3 pattern, the EMAs or MACD at all
  -- only the candle's colour plus `strategy.opentrades > 0`.
* `close[3]` / `open[3]` etc. are na for the first three bars, and an na in a
  Pine comparison is false, so no signal can fire before bar 3. `pine_ema`'s seed
  choice is the shared layer's (PINE_SEMANTICS.md 3.1).
* `_ta.macd` returns `[macdLine, signalLine, histLine]`; the third element is
  discarded by the source and is not computed into any condition here.
* md and source agree on the indicator periods (EMA 9 / EMA 20 / MACD 12-26-9)
  and on the 5-contract quantity.
* Leverage, margin, liquidation, funding and the venue's contract-step rounding
  are not modelled by the engine (PINE_SEMANTICS.md 二.4, 1.6); the chain
  verifier measures the rounding separately.
"""
from __future__ import annotations

import pandas as pd
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


class SM123PatternQuant_0a0a82(PinePortBase, IStrategy):
    source_id = "SM_0a0a82110800bbae"
    source_file = (
        "1-2-3-形态与-EMAMACD-和第四根蜡烛线延伸的量化交易策略"
        "1-2-3-Pattern-Quantitative-Trading-Strategy-with-EMAs-MACD-and-4th-Candle-Extension.md"
    )
    timeframe = "1h"
    can_short = True
    # The source declares no input() at all: every length and the qty=5 are
    # literals.
    source_defaults: dict = {}
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    source_reproduce_stops = False
    source_fidelity_notes = [
        "The md describes the 1-2-3 pattern with an off-by-one candle index: it "
        "says candle 3 closes above candle 1 and candle 4 above candle 3, while "
        "the code compares bars [1] and [0] against close[3] and never reads bar "
        "[2] in any buy leg. The code is followed.",
        "The md says a position closes 'when the opposite signal appears', but "
        "the code's close conditions test only the candle's colour and "
        "strategy.opentrades > 0 -- not the pattern, the EMAs or MACD.",
        "Each strategy.close names a single entry id and is not gated on the "
        "position's sign, so close('Buy') while short is a Pine no-op; the "
        "engine's from_entry-scoped close reproduces that (PINE_SEMANTICS.md "
        "1.12).",
        "qty=5 is passed verbatim on every entry. The close's qty=5 equals the "
        "whole position (opentrades==0 gate plus pyramiding=0 pin the position at "
        "5), so the broker's whole-position close() is equivalent.",
        "The source has no input(): every length and quantity is a literal, so "
        "source_defaults is empty.",
        "ta.macd's third return value (histLine) is discarded by the source and "
        "is not used in any condition here.",
        "close[3]/open[3] are na for the first three bars and na comparisons are "
        "false, so nothing can fire before bar 3.",
        "pine_ema's seed is the shared layer's modelled choice "
        "(PINE_SEMANTICS.md 3.1); ports do not re-seed it.",
        "Leverage, margin, liquidation, funding and contract-step rounding are "
        "not modelled by the engine.",
    ]

    def pine_indicators(self, dataframe, params):
        close = dataframe["close"]
        source_open = dataframe["open"]

        close_3 = close.shift(3)
        open_3 = source_open.shift(3)
        close_2 = close.shift(2)
        open_2 = source_open.shift(2)
        close_1 = close.shift(1)

        # Buy legs of the 1-2-3 pattern.
        buy_candle1_above_open = (close_3 > open_3).astype(bool) # 阳线
        buy_candle2_below_open = (close_2 < open_2).astype(bool) # 阴线 
        buy_candle3_above_close = (close_1 > close_3).astype(bool) 
        buy_candle4_above_close = (close > close_3).astype(bool)

        # Sell legs: the exact mirror.
        sell_candle1_below_open = (close_3 < open_3).astype(bool)
        sell_candle2_above_open = (close_2 > open_2).astype(bool)
        sell_candle3_below_close = (close_1 < close_3).astype(bool)
        sell_candle4_below_close = (close < close_3).astype(bool)

        # ema_9 = ta.ema(close, 9) / ema_20 = ta.ema(close, 20)
        ema_9 = ta.pine_ema(close, 9)
        ema_20 = ta.pine_ema(close, 20)
        # [macd_line, signal_line, _] = ta.macd(close, 12, 26, 9)
        macd = ta.pine_macd(close, 12, 26, 9)
        macd_line = macd["macd"]
        signal_line = macd["signal"]

        dataframe["pine_ema9"] = ema_9
        dataframe["pine_ema20"] = ema_20
        dataframe["pine_macd"] = macd_line
        dataframe["pine_macd_signal"] = signal_line

        # The pattern + indicator conjunction, everything except the
        # strategy.opentrades gate (which must be read live in pine_script).
        dataframe["pine_buy_condition"] = (
            buy_candle1_above_open & buy_candle2_below_open
            & buy_candle3_above_close & buy_candle4_above_close
            & (close > ema_9) & (close > ema_20) & (macd_line > signal_line)
        )

        dataframe["pine_sell_condition"] = (
            sell_candle1_below_open & sell_candle2_above_open
            & sell_candle3_below_close & sell_candle4_below_close
            & (close < ema_9) & (close < ema_20) & (macd_line < signal_line)
        ) 

        # if (close < open and ...) / if (close > open and ...)
        dataframe["pine_bearish_candle"] = (close < source_open).astype(bool)
        dataframe["pine_bullish_candle"] = (close > source_open).astype(bool)
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "buy_condition": dataframe["pine_buy_condition"].to_numpy(dtype=bool),
            "sell_condition": dataframe["pine_sell_condition"].to_numpy(dtype=bool),
            "bearish_candle": dataframe["pine_bearish_candle"].to_numpy(dtype=bool),
            "bullish_candle": dataframe["pine_bullish_candle"].to_numpy(dtype=bool),
        }

    def pine_script(self, broker, i, ctx):
        # if (buy pattern AND strategy.opentrades == 0 AND close > ema_9 AND
        #     close > ema_20 AND macd_line > signal_line)
        #     strategy.entry("Buy", strategy.long, qty=5)
        if ctx["buy_condition"][i] and broker.open_trades == 0: # broker.open_trades 无持仓买入
            broker.entry("Buy", "long", qty=5)# 最多五张

        # if (close < open and strategy.opentrades > 0)
        #     strategy.close("Buy", qty=5)
        if ctx["bearish_candle"][i] and broker.open_trades > 0:
            broker.close("Buy")

        # if (sell pattern AND strategy.opentrades == 0 AND close < ema_9 AND
        #     close < ema_20 AND macd_line < signal_line)
        #     strategy.entry("Sell", strategy.short, qty=5)
        if ctx["sell_condition"][i] and broker.open_trades == 0:
            broker.entry("Sell", "short", qty=5) # 开空五张

        # if (close > open and strategy.opentrades > 0)
        #     strategy.close("Sell", qty=5)
        if ctx["bullish_candle"][i] and broker.open_trades > 0:
            broker.close("Sell")
