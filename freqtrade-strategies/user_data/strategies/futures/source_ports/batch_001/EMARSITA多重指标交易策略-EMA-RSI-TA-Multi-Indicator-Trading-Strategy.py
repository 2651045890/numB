"""Port of sources/SM_0b7f4597edf96f20.pine (batch_001/EMARSITA多重指标交易策略-EMA-RSI-TA-Multi-Indicator-Trading-Strategy.md).

Pine v4. Three EMAs and an RSI: a 4/12 crossover is bought when RSI is below
the overbought level and price is above the 48 EMA, and sold short when the
same crossover goes the other way with RSI above oversold and price below the
48 EMA:

    shortEma    = ema(close, 4)
    longEma     = ema(close, 12)
    longTermEma = ema(close, 48)
    rsi         = rsi(close, 14)

    buySignal  = crossover(shortEma, longEma)  and rsi < 70 and close > longTermEma
    sellSignal = crossunder(shortEma, longEma) and rsi > 30 and close < longTermEma

    if (buySignal)
        strategy.entry("Buy", strategy.long)
    if (sellSignal)
        strategy.entry("Sell", strategy.short)

The three EMA lengths (4, 12, 48), the RSI length (14) and the two thresholds
(70, 30) are the source's only `input()` calls, and all six defaults are
carried in `source_defaults`.

`strategy()` declares `title` / `shorttitle` / `overlay`, so every property is
Pine's documented default: `strategy.fixed` / 1 contract, initial capital
1000000, commission 0%, pyramiding 0, `process_orders_on_close=false`. Neither
entry passes a `qty=`, so the default quantity of 1 is what the source sizes
with.

There is no exit call of any kind: a position is only ever closed or reversed
by the opposite entry's netting, so `source_reproduce_stops` is False and a
position still open at the end of the window stays open. Both directions are
entered, so `can_short` is True.

FIDELITY:

* md-vs-source: there is no argument table in the md for this source at all,
  yet the source declares six `input()`s; the six defaults are taken from the
  source's own `input(...)` calls.
* md-vs-source: the strategy's own `title` says "with 200 EMA" and the
  `plot(longTermEma, ..., title="200 EMA")` label matches, but
  `longTermEmaLength` defaults to 48 and the md prose also says 48 (长期(默认为
  48)). The code's 48 is used; the "200" in the title and the plot label is the
  author's stale naming, reproduced in the note rather than in the port.
* The source is annotated `//@version=4` twice (a duplicated line). It calls
  only v4 builtins (`ema`, `rsi`, `crossover`, `crossunder`), so the version
  question changes nothing here.
* md-vs-source: the md's step 3 says the buy signal needs "RSI not in the
  overbought area" and step 4 "RSI not in the oversold area", which matches the
  code's `rsi < overbought` / `rsi > oversold` (strict inequalities, and the
  sell filter is the opposite of what an "oversold" reading might suggest --
  `rsi > 30` is the permissive direction). Strict directions preserved.
* `ema` follows pine_ta's documented first-value seeding (PINE_SEMANTICS.md
  3.1); `rsi` returns 100 when there were no losses in the window and na until
  the averages exist (PINE_SEMANTICS.md 3.3).
* `crossover` / `crossunder` are `a > b and a[1] <= b[1]` and its mirror; na on
  either side is false, and the RSI comparison against its threshold is
  likewise false while the RSI is na.
* `plot` / `plotshape` are display-only and place no condition.
* The `/*backtest` header declares `period: 1d`; its `basePeriod: 1h` is the
  FMZ backtester's own granularity for filling those 1d bars.
* Leverage, margin, liquidation, funding and the venue's contract-step rounding
  are not modelled; the chain verifier measures the rounding separately.
"""
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


class SMEmarsi200_0b7f45(PinePortBase, IStrategy):
    source_id = "SM_0b7f4597edf96f20"
    source_file = "EMARSITA多重指标交易策略-EMA-RSI-TA-Multi-Indicator-Trading-Strategy.md"
    timeframe = "1d"
    can_short = True
    source_defaults: dict = {
        "shortEmaLength": 4,
        "longEmaLength": 12,
        "longTermEmaLength": 48,
        "rsiLength": 14,
        "overbought": 70,
        "oversold": 30,
    }
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    source_reproduce_stops = False
    source_fidelity_notes = [
        "No exit call exists: a position is closed or reversed only by the "
        "opposite entry's netting, so source_reproduce_stops is False and a "
        "position open at the window end stays open.",
        "md-vs-source: the md carries NO argument table for this source, while "
        "the source declares six input()s; the six defaults are read from the "
        "source's own input() calls.",
        "md-vs-source: the source's title (\"EMA & RSI Strategy with 200 EMA\") "
        "and its plot label (\"200 EMA\") say 200, but longTermEmaLength "
        "defaults to 48 and the md prose also says 48. The code's 48 is used.",
        "Strict inequality directions preserved: buy needs rsi < overbought and "
        "close > longTermEma; sell needs rsi > oversold and close < "
        "longTermEma.",
        "The source duplicates its //@version=4 annotation; it calls only v4 "
        "builtins (ema, rsi, crossover, crossunder), so the version question "
        "changes nothing.",
        "ema uses pine_ta's first-value seeding (PINE_SEMANTICS.md 3.1); rsi "
        "returns 100 when the window had no losses and na until its averages "
        "exist (PINE_SEMANTICS.md 3.3).",
        "crossover/crossunder are false while either operand is na, and each "
        "threshold comparison is false while the RSI is na, so nothing fires "
        "during warm-up.",
        "plot/plotshape are display-only and place no condition.",
        "Leverage, margin, liquidation, funding and venue contract-step "
        "rounding are not modelled; the chain verifier measures the rounding "
        "separately.",
    ]

    def pine_indicators(self, dataframe, params):
        close = dataframe["close"]
        short_ema = ta.pine_ema(close, int(params["shortEmaLength"]))
        long_ema = ta.pine_ema(close, int(params["longEmaLength"]))
        long_term_ema = ta.pine_ema(close, int(params["longTermEmaLength"]))
        rsi = ta.pine_rsi(close, int(params["rsiLength"]))
        overbought = float(params["overbought"])
        oversold = float(params["oversold"])
        dataframe["pine_short_ema"] = short_ema
        dataframe["pine_long_ema"] = long_ema
        dataframe["pine_long_term_ema"] = long_term_ema
        dataframe["pine_rsi"] = rsi
        dataframe["pine_buy_signal"] = (
            ta.pine_crossover(short_ema, long_ema)
            & (rsi < overbought)
            & (close > long_term_ema)
        ).fillna(False)
        dataframe["pine_sell_signal"] = (
            ta.pine_crossunder(short_ema, long_ema)
            & (rsi > oversold)
            & (close < long_term_ema)
        ).fillna(False)
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "buy_signal": dataframe["pine_buy_signal"].to_numpy(),
            "sell_signal": dataframe["pine_sell_signal"].to_numpy(),
        }

    def pine_script(self, broker, i, ctx):
        # if (buySignal)
        #     strategy.entry("Buy", strategy.long)
        if ctx["buy_signal"][i]:
            broker.entry("Buy", "long")
        # if (sellSignal)
        #     strategy.entry("Sell", strategy.short)
        if ctx["sell_signal"][i]:
            broker.entry("Sell", "short")
