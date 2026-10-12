"""Port of sources/SM_f8329c9d22715579.pine (batch_001/EMA交叉策略与RSI背离30分钟趋势识别和价格竭尽-EMA-Cross-Strategy-with-RSI-Divergence-30-Minute-Trend-Identification-and-Price-Exhaustion.md).

Pine v5. Three independent signal blocks sharing one EMA/RSI set:

    EMA5 = ta.ema(close, 5) ; EMA10 = ta.ema(close, 10)     # "30 min" in the prose
    EMA13 = ta.ema(close, 13) ; EMA26 = ta.ema(close, 26)
    rsi = ta.rsi(close, 7)

    crossUp   = ta.crossover(EMA13, EMA26)
    crossDown = ta.crossunder(EMA13, EMA26)
    bullishDivergence = ta.crossunder(close, EMA13) and ta.crossunder(rsi, 30)
    bearishDivergence = ta.crossover(close, EMA13)  and ta.crossover(rsi, 70)
    entrySignal = crossUp ? 1 : (crossDown ? -1 : 0)

    block 1:  if (entrySignal == 1) entry("Long", long)
              else if (entrySignal == -1) entry("Short", short)
              if (entrySignal == 1 and ta.crossover(close, EMA26)) close("Long")
              else if (entrySignal == -1 and ta.crossunder(close, EMA26)) close("Short")

    block 2:  if (bullishDivergence) entry("Bullish Divergence", long)
              if (bearishDivergence) entry("Bearish Divergence", short)

    block 3:  buySignal  = crossUp   and close > EMA13 and close > EMA26
              sellSignal = crossDown and close < EMA13 and close < EMA26
              isUptrend30min   = close > EMA5  and close > EMA10
              isDowntrend30min = close < EMA5  and close < EMA10
              isOversold = rsi < 30 ; isOverbought = rsi > 70
              if (buySignal and isUptrend30min and isOversold)   entry("Buy",  long)
              if (sellSignal and isDowntrend30min and isOverbought) entry("Sell", short)

There is not a single `input()` in the source, so `source_defaults` is empty and
every parameter is a literal.

`strategy(title, overlay=true)` declares only `title` and `overlay`, so every
property is Pine's documented default: `strategy.fixed` / 1 contract per entry,
initial capital 1000000, commission 0%, pyramiding 0,
`process_orders_on_close=false`.

The `/*backtest` header declares `period: 2h` on Futures_Binance BTC_USDT, so
`timeframe` is "2h"; its `basePeriod: 15m` is the FMZ backtester's own
granularity for filling those 2h bars, not the strategy's period.

FIDELITY:

* The prose is written in terms of a "30-minute" trend (the EMA5/EMA10 pair is
  named `*_30min`), but the source reads no second timeframe: those EMAs are
  computed on the chart's own series, and the header declares `period: 2h`.
  There is no `request.security` and no resampling anywhere. `timeframe` is
  taken from the header and the "30 minute" naming is recorded as prose only.
* `bullishDivergence` / `bearishDivergence` are NOT divergences: each is a
  same-bar CONJUNCTION of two crossing events (price crossing the 13-EMA and
  the RSI crossing its 30/70 line). Nothing in the source compares a price
  pivot with an indicator pivot. Reproduced literally; the prose's description
  is recorded, not implemented.
* `entrySignal` is an integer 1 / -1 / 0, compared with `== 1` / `== -1`. The
  integer form is kept rather than rewritten as booleans (PINE_SEMANTICS.md
  1.17 is the same family of trap).
* Block 1's close sits inside `if (entrySignal == 1 and ...)`: `entrySignal == 1`
  already requires `crossUp` ON THIS BAR, so the close needs the 13/26 cross
  and the close-vs-EMA26 cross on one and the same bar. Reproduced as written;
  it is not "close whenever price is above EMA26".
* Block 3 re-uses the same `crossUp` / `crossDown` values as block 1, so its
  `buySignal` / `sellSignal` can only be true on a bar that block 1 already
  entered on. With `pyramiding = 0` the second entry of the same direction is
  blocked by the engine at order-creation time, which is Pine's behaviour.
* Six distinct order ids exist ("Long", "Short", "Bullish Divergence",
  "Bearish Divergence", "Buy", "Sell") and the two `strategy.close` calls name
  only the first two, so block 2's and block 3's entries are never closed by a
  `strategy.close`; they are only reversed by an opposite entry. Reproduced.
* `strategy.close(id)` is a no-op when that id is not held (the engine's
  `from_entry` matching honours this, PINE_SEMANTICS.md 1.12).
* No stop / limit / profit / loss / trail exit exists anywhere in the source,
  so `source_reproduce_stops` is False and a position open at the window's end
  stays open.
* `ta.rsi(close, 7)` is Pine's own RSI and is modelled by `pine_ta.pine_rsi`;
  it returns 100 when the window had no losses and is na until its average is
  formed (PINE_SEMANTICS.md 3.3).
* `ta.ema`'s seeding rule is NOT published by TradingView: `pine_ta.pine_ema`
  seeds the recursion with the first non-na observation and lets an na
  observation pass through without advancing it. Every condition in this source
  is an EMA cross or an EMA level test, so this source is exactly the case
  PINE_SEMANTICS.md 3.1 records as a load-bearing early-history risk -- the
  modelled seeding has these EMAs defined from the first bar, while a
  SMA-seeded platform would have them na for the first `length-1` bars. Late
  history converges; the opening trades may differ.
* The call order is preserved block by block, and within a block line by line:
  entry before close, both divergence entries, then the two block-3 entries.
  All calls are written unconditionally in the source and in this port.
* Leverage, margin, liquidation, funding and the venue's contract-step rounding
  are not modelled; the step can only be read off the exchange object at run
  time, so the framework and the engine may differ by a rounded quantity, which
  the chain verifier measures separately rather than treating as a signal
  difference.
"""
import numpy as np
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


class SMEmaCrossRsiDivergence_f8329c(PinePortBase, IStrategy):
    source_id = "SM_f8329c9d22715579"
    source_file = (
        "EMA交叉策略与RSI背离30分钟趋势识别和价格竭尽-"
        "EMA-Cross-Strategy-with-RSI-Divergence-30-Minute-Trend-Identification-"
        "and-Price-Exhaustion.md"
    )
    timeframe = "2h"
    can_short = True
    # The source declares no input() at all; every parameter is a literal.
    source_defaults: dict = {}
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    source_reproduce_stops = False
    source_fidelity_notes = [
        "The source declares no input() at all, so source_defaults is empty and "
        "every parameter below is a literal.",
        "strategy() declares only title and overlay, so fixed qty 1, initial "
        "capital 1000000, commission 0%, pyramiding 0 and "
        "process_orders_on_close=false are Pine's documented defaults.",
        "The EMA5/EMA10 pair is named *_30min and the prose speaks of a "
        "'30-minute trend', but the source reads no second timeframe: there is "
        "no request.security and no resampling, and the header declares "
        "period: 2h. Reproduced on the 2h series; the naming is prose only.",
        "bullishDivergence / bearishDivergence are NOT divergences -- each is a "
        "same-bar conjunction of a price/EMA cross and an RSI level cross. "
        "Reproduced literally; the prose's description is recorded, not "
        "implemented.",
        "entrySignal is the integer 1 / -1 / 0 and is compared with == 1 / "
        "== -1; the integer form is kept (PINE_SEMANTICS.md 1.17 family of "
        "traps).",
        "Block 1's close is guarded by `entrySignal == 1`, which already "
        "requires the 13/26 cross on that same bar, so the close needs both "
        "crosses on one bar. Reproduced as written.",
        "Block 3 re-uses block 1's crossUp/crossDown, so its buy/sell signal can "
        "only be true on a bar block 1 already entered on; with pyramiding 0 the "
        "second same-direction entry is blocked at order-creation time.",
        "Six order ids exist and only 'Long'/'Short' are ever closed by "
        "strategy.close, so block 2's and block 3's entries are only reversed by "
        "an opposite entry, never closed outright.",
        "No stop/limit/profit/loss/trail exit exists, so source_reproduce_stops "
        "is False and a position open at the window's end stays open.",
        "ta.rsi(close,7) is modelled by pine_ta.pine_rsi (100 when the window "
        "had no losses; na until its average forms) -- PINE_SEMANTICS.md 3.3.",
        "Every condition here is an EMA cross or EMA level test, so this port is "
        "exactly the load-bearing case of PINE_SEMANTICS.md 3.1: pine_ta.pine_ema "
        "seeds with the first non-na observation, so its EMAs are defined from "
        "the first bar where a SMA-seeded platform would be na for length-1 "
        "bars. Late history converges; the opening trades may not.",
        "The source's call order is preserved line by line; all calls are "
        "written unconditionally in the source and in this port.",
        "Leverage, margin, liquidation, funding and contract-step rounding are "
        "not modelled; the venue's rounding can differ from the engine's float "
        "quantity, which the chain verifier measures separately.",
    ]

    def pine_indicators(self, dataframe, params):
        close = dataframe["close"]

        ema5 = ta.pine_ema(close, 5)
        ema10 = ta.pine_ema(close, 10)
        ema13 = ta.pine_ema(close, 13)
        ema26 = ta.pine_ema(close, 26)
        rsi = ta.pine_rsi(close, 7)

        cross_up = ta.pine_crossover(ema13, ema26)
        cross_down = ta.pine_crossunder(ema13, ema26)
        bullish_divergence = ta.pine_crossunder(close, ema13) & ta.pine_crossunder(rsi, 30)
        bearish_divergence = ta.pine_crossover(close, ema13) & ta.pine_crossover(rsi, 70)

        # entrySignal = crossUp ? 1 : (crossDown ? -1 : 0). Integer semantics
        # kept (PINE_SEMANTICS.md 1.17).
        entry_signal = np.where(
            cross_up.to_numpy(), 1, np.where(cross_down.to_numpy(), -1, 0)
        )

        close_ema26_up = ta.pine_crossover(close, ema26)
        close_ema26_down = ta.pine_crossunder(close, ema26)

        buy_signal = cross_up & (close > ema13) & (close > ema26)
        sell_signal = cross_down & (close < ema13) & (close < ema26)

        is_uptrend_30min = (close > ema5) & (close > ema10)
        is_downtrend_30min = (close < ema5) & (close < ema10)
        is_oversold = rsi < 30
        is_overbought = rsi > 70

        dataframe["pine_ema5"] = ema5
        dataframe["pine_ema10"] = ema10
        dataframe["pine_ema13"] = ema13
        dataframe["pine_ema26"] = ema26
        dataframe["pine_rsi"] = rsi
        dataframe["pine_entry_signal"] = entry_signal
        dataframe["pine_bullish_divergence"] = bullish_divergence
        dataframe["pine_bearish_divergence"] = bearish_divergence
        dataframe["pine_buy_signal"] = buy_signal
        dataframe["pine_sell_signal"] = sell_signal
        dataframe["pine_is_uptrend_30min"] = is_uptrend_30min
        dataframe["pine_is_downtrend_30min"] = is_downtrend_30min
        dataframe["pine_is_oversold"] = is_oversold
        dataframe["pine_is_overbought"] = is_overbought
        dataframe["pine_close_ema26_up"] = close_ema26_up
        dataframe["pine_close_ema26_down"] = close_ema26_down
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "entry_signal": dataframe["pine_entry_signal"].to_numpy(),
            "close_ema26_up": dataframe["pine_close_ema26_up"].to_numpy(),
            "close_ema26_down": dataframe["pine_close_ema26_down"].to_numpy(),
            "bullish_divergence": dataframe["pine_bullish_divergence"].to_numpy(),
            "bearish_divergence": dataframe["pine_bearish_divergence"].to_numpy(),
            "buy_signal": dataframe["pine_buy_signal"].to_numpy(),
            "sell_signal": dataframe["pine_sell_signal"].to_numpy(),
            "is_uptrend_30min": dataframe["pine_is_uptrend_30min"].to_numpy(),
            "is_downtrend_30min": dataframe["pine_is_downtrend_30min"].to_numpy(),
            "is_oversold": dataframe["pine_is_oversold"].to_numpy(),
            "is_overbought": dataframe["pine_is_overbought"].to_numpy(),
        }

    def pine_script(self, broker, i, ctx):
        entry_signal = int(ctx["entry_signal"][i])

        # if (entrySignal == 1)
        #     strategy.entry("Long", strategy.long)
        # else if (entrySignal == -1)
        #     strategy.entry("Short", strategy.short)
        if entry_signal == 1:
            broker.entry("Long", "long")
        elif entry_signal == -1:
            broker.entry("Short", "short")

        # if (entrySignal == 1 and ta.crossover(close, EMA26))
        #     strategy.close("Long")
        # else if (entrySignal == -1 and ta.crossunder(close, EMA26))
        #     strategy.close("Short")
        if entry_signal == 1 and ctx["close_ema26_up"][i]:
            broker.close("Long")
        elif entry_signal == -1 and ctx["close_ema26_down"][i]:
            broker.close("Short")

        # if (bullishDivergence)
        #     strategy.entry("Bullish Divergence", strategy.long)
        if ctx["bullish_divergence"][i]:
            broker.entry("Bullish Divergence", "long")
        # if (bearishDivergence)
        #     strategy.entry("Bearish Divergence", strategy.short)
        if ctx["bearish_divergence"][i]:
            broker.entry("Bearish Divergence", "short")

        # if (buySignal and isUptrend30min and isOversold)
        #     strategy.entry("Buy", strategy.long)
        if ctx["buy_signal"][i] and ctx["is_uptrend_30min"][i] and ctx["is_oversold"][i]:
            broker.entry("Buy", "long")
        # if (sellSignal and isDowntrend30min and isOverbought)
        #     strategy.entry("Sell", strategy.short)
        if (
            ctx["sell_signal"][i]
            and ctx["is_downtrend_30min"][i]
            and ctx["is_overbought"][i]
        ):
            broker.entry("Sell", "short")
