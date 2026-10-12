"""Port of sources/SM_ea624c7ee89d6288.pine (batch_001/Bollinger-Bands-Stochastic-Oscillator-Strategy-布林带随机振荡器策略.md).

Pine v5. A two-sided Bollinger-band breakout that reverses on the opposite
band touch:

    bbBasis = ta.sma(priceData, bbLength)          # priceData = close
    bbDev   = ta.stdev(priceData, bbLength)
    bbUpper = bbBasis + bbMultiplier * bbDev
    bbLower = bbBasis - bbMultiplier * bbDev

    enterLong  = ta.crossover(priceData, bbUpper)
    enterShort = ta.crossunder(priceData, bbLower)

    if (enterLong)  strategy.entry("Long",  strategy.long)
    if (enterShort) strategy.entry("Short", strategy.short)
    if (enterShort) strategy.close("Long")
    if (enterLong)  strategy.close("Short")

`strategy("Unique Bollinger Bands Strategy", overlay=true)` declares only
`title` and `overlay`, so every property is Pine's documented default:
`strategy.fixed` / 1 contract per entry, initial capital 1000000, commission
0%, pyramiding 0, `process_orders_on_close=false`.

The `/*backtest` header declares `period: 1d` on Futures_Binance BTC_USDT, so
`timeframe` is "1d"; its `basePeriod: 1h` is the FMZ backtester's own
granularity for filling those daily bars, not the strategy's period.

FIDELITY:

* The md's title and prose describe a "Bollinger Bands + Stochastic Oscillator"
  strategy in which entries are filtered by %K crossing %D. The CODE contains
  NO stochastic oscillator at all: there is no `stoch` / `%K` / `%D` anywhere
  in the source, and the prose's description of the signals ("price breaks the
  upper band AND %K crosses above %D") is not what the code does. The code is
  authoritative (铁律 2) and is what this port implements: a plain
  band-touch cross with an immediate opposite-side close. Recorded, not
  reconciled.
* The md's argument table lists the four band inputs with the SAME defaults the
  code carries (34 / 2 / 34 / 2), so there is no disagreement there.
* There are TWO complete Bollinger-band computations in the source. The first
  (`src = input(close)`, `length`, `mult`) is only ever passed to `plot` /
  `fill`. The second (`bbLength`, `bbMultiplier`, `priceData = close`) is the
  one the four order calls read. Both are computed here and both are kept as
  columns; only the second drives the orders. With the declared defaults the
  two are the same series (`src` defaults to `close`, `priceData` is `close`
  literally, 34/2 both), but they are separate inputs and are carried
  separately in `source_defaults`.
* `ta.stdev` is the POPULATION standard deviation (Pine's `biased = true`
  default, dividing by N), which pine_ta.pine_stdev models with ddof=0.
* `sma` / `stdev` return na until their window is full and na propagates inside
  the window, so neither cross can fire before 34 bars of history.
* The four calls are written unconditionally and in source order. `enterLong`
  and `enterShort` are mutually exclusive (a bar cannot cross UP through the
  upper band and DOWN through the lower band at once), so on a signal bar the
  effect is an exact reversal: enter on the crossed side, then `strategy.close`
  the opposite id. The close is a no-op unless that id is actually held, which
  the engine's `from_entry` matching already honours (PINE_SEMANTICS.md 1.12).
* No stop / limit / profit / loss / trail exit exists anywhere in the source --
  the only exits are the two `strategy.close` calls -- so
  `source_reproduce_stops` is False and a position open at the window's end
  stays open.
* `plot`, `fill`, `colorBasis` and the strategy title are display-only and are
  not reproduced; `colorBasis` is a `color` value, not a condition, and places
  no order.
* `ta.ema` is not used here; no EMA seeding risk applies.
* Leverage, margin, liquidation, funding and the venue's contract-step rounding
  are not modelled; the step can only be read off the exchange object at run
  time, so the framework and the engine may differ by a rounded quantity, which
  the chain verifier measures separately rather than treating as a signal
  difference.
"""
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


class SMBollingerStochOsc_ea624c(PinePortBase, IStrategy):
    source_id = "SM_ea624c7ee89d6288"
    source_file = "Bollinger-Bands-Stochastic-Oscillator-Strategy-布林带随机振荡器策略.md"
    timeframe = "1d"
    can_short = True
    source_defaults: dict = {
        # src = input(close); length = input.int(34, minval=1);
        # mult = input.float(2.0, minval=0.001, maxval=50)
        "src": "close",
        "length": 34,
        "mult": 2.0,
        # bbLength = input.int(34, title="Length", minval=1)
        # bbMultiplier = input.float(2.0, title="Multiplier", ...)
        "bbLength": 34,
        "bbMultiplier": 2.0,
    }
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    source_reproduce_stops = False
    source_fidelity_notes = [
        "strategy() declares only title and overlay, so fixed qty 1, initial "
        "capital 1000000, commission 0%, pyramiding 0 and "
        "process_orders_on_close=false are Pine's documented defaults.",
        "The source contains NO stochastic oscillator, although the md's title "
        "and prose describe the signals as a Bollinger-band break FILTERED by "
        "%K crossing %D. There is no stoch/%K/%D expression anywhere in the "
        "code; the entries are plain `ta.crossover(close, bbUpper)` / "
        "`ta.crossunder(close, bbLower)`. Code followed; the prose disagreement "
        "is recorded rather than reconciled.",
        "There are two full Bollinger-band computations. The first (src/length/"
        "mult) is only ever plotted and filled between; the second (bbLength/"
        "bbMultiplier, priceData = close) is what the four order calls read. "
        "Both are computed and kept as columns; only the second drives orders. "
        "The md's argument table agrees with the code on all four defaults.",
        "ta.stdev is the POPULATION standard deviation (Pine's biased=true "
        "default, dividing by N), modelled by pine_ta.pine_stdev with ddof=0.",
        "sma/stdev are na until their window is full and na propagates within "
        "the window, so no cross can fire before 34 bars of history.",
        "The four calls are written unconditionally and in source order. "
        "enterLong and enterShort are mutually exclusive, so a signal bar "
        "reverses exactly: entry on the crossed side first, then "
        "strategy.close of the opposite id. The close is a no-op when that id "
        "is not held (PINE_SEMANTICS.md 1.12).",
        "No stop/limit/profit/loss/trail exit exists; the only exits are the two "
        "strategy.close calls, so source_reproduce_stops is False and a "
        "position open at the window's end stays open.",
        "plot/fill, colorBasis (a color value, not a condition) and the "
        "strategy title are display-only and are not reproduced.",
        "No ta.ema is used, so the unpublished EMA seeding rule of "
        "PINE_SEMANTICS.md 3.1 does not apply here.",
        "The /*backtest header's `period: 1d` is the strategy's timeframe; its "
        "`basePeriod: 1h` is the FMZ backtester's own granularity for filling "
        "daily bars, not a second timeframe read by the script.",
        "Leverage, margin, liquidation, funding and contract-step rounding are "
        "not modelled; the venue's rounding can differ from the engine's float "
        "quantity, which the chain verifier measures separately.",
    ]

    def pine_indicators(self, dataframe, params):
        src = ta.pine_source(dataframe, params["src"])
        close = dataframe["close"]
        length = int(params["length"])
        mult = float(params["mult"])
        bb_length = int(params["bbLength"])
        bb_multiplier = float(params["bbMultiplier"])

        # First band set: plotted and filled between, read by no order.
        basis = ta.pine_sma(src, length)
        deviation = ta.pine_stdev(src, length)
        dataframe["pine_basis"] = basis
        dataframe["pine_upper1"] = basis + deviation
        dataframe["pine_lower1"] = basis - deviation
        dataframe["pine_upper2"] = basis + mult * deviation
        dataframe["pine_lower2"] = basis - mult * deviation

        # Second band set: the one the order calls read. `priceData = close` is
        # a literal in the source, not the `src` input.
        bb_basis = ta.pine_sma(close, bb_length)
        bb_deviation = ta.pine_stdev(close, bb_length)
        bb_upper = bb_basis + bb_multiplier * bb_deviation
        bb_lower = bb_basis - bb_multiplier * bb_deviation
        dataframe["pine_bb_basis"] = bb_basis
        dataframe["pine_bb_upper"] = bb_upper
        dataframe["pine_bb_lower"] = bb_lower

        dataframe["pine_enter_long"] = ta.pine_crossover(close, bb_upper)
        dataframe["pine_enter_short"] = ta.pine_crossunder(close, bb_lower)
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "enter_long": dataframe["pine_enter_long"].to_numpy(),
            "enter_short": dataframe["pine_enter_short"].to_numpy(),
        }

    def pine_script(self, broker, i, ctx):
        # if (enterLong)
        #     strategy.entry("Long", strategy.long)
        if ctx["enter_long"][i]:
            broker.entry("Long", "long")
        # if (enterShort)
        #     strategy.entry("Short", strategy.short)
        if ctx["enter_short"][i]:
            broker.entry("Short", "short")
        # if (enterShort)
        #     strategy.close("Long")
        if ctx["enter_short"][i]:
            broker.close("Long")
        # if (enterLong)
        #     strategy.close("Short")
        if ctx["enter_long"][i]:
            broker.close("Short")
