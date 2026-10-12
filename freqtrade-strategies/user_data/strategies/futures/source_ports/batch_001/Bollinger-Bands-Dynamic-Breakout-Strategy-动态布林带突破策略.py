"""Port of sources/SM_b00fdb702e0865bd.pine (batch_001/Bollinger-Bands-Dynamic-Breakout-Strategy-动态布林带突破策略.md).

Pine v5. Bollinger Bands breakout with the BANDS themselves as the exit levels
-- a long is taken off when the close crosses back UNDER the upper band, and a
short when it crosses back OVER the lower band:

    src    = close
    length = input.int(34, "Length", minval=1)
    mult   = input.float(2.0, "Multiplier", minval=0.001, maxval=50)
    basis = ta.sma(src, length)
    dev   = ta.stdev(src, length)
    upperBand = basis + mult * dev
    lowerBand = basis - mult * dev

and then, in this order:

    if ta.crossover(src, upperBand)   -> strategy.entry("Long",  strategy.long)
    if ta.crossunder(src, lowerBand)  -> strategy.entry("Short", strategy.short)
    if ta.crossunder(src, upperBand)  -> strategy.close("Long")
    if ta.crossover(src, lowerBand)   -> strategy.close("Short")

This is the "dynamic" variant of the same breakout: the exit tests the SAME band
the entry broke, so a long armed by an upper-band breakout is unwound by the
first close back below that band, and the middle band never places an order.

`strategy()` declares only `title` / `shorttitle` / `overlay`, so every property
is Pine's documented default: `strategy.fixed` / 1 contract, initial capital
1000000, commission 0%, pyramiding 0, `process_orders_on_close=false`. The two
`fill()` and three `plot()` calls are display-only.

FIDELITY:

* `dev` is `ta.stdev(src, length)` and the multiplier is applied at the band, so
  `upperBand = basis + mult * dev` -- the multiplier is NOT folded into `dev`
  before the second band. The two are algebraically identical, but the port
  keeps the source's grouping so an overridden `mult` cannot reach the two bands
  by a different route.
* `ta.stdev` is Pine's POPULATION standard deviation (`ddof=0`), reproduced by
  `pine_ta.pine_stdev`.
* `ta.crossover` / `ta.crossunder` against an na operand are false in Pine,
  which `pine_ta` models; the band needs 34 bars, so bars before index 33 cannot
  signal.
* No stop / limit / trail exit exists -- the only exits are the two
  `strategy.close` calls -- so `source_reproduce_stops` is False. A position left
  open at the end of the window stays open, as in the source.
* The four `if` statements are independent and keep the source's order (entry
  long, entry short, close long, close short); a close naming an entry that is
  not held is a no-op (PINE_SEMANTICS.md 1.12). Note that on a bar where the
  close crosses under the upper band the exit-long and the entry-short tests look
  at DIFFERENT bands, so they do not collapse into the same condition.
* md/source divergence recorded, not acted on: the md's prose says the exit is
  "price crosses below the upper band" for longs and "above the lower band" for
  shorts, which is exactly what the code does. The md's argument table is absent
  (this md carries no `Strategy Arguments` section), so the two `input()` defaults
  are read from the code alone: `length = 34`, `mult = 2.0`.
* `/*backtest` header: `period: 1h` on Futures_Binance BTC_USDT, hence
  `timeframe = "1h"`; `basePeriod: 15m` is the FMZ backtester's own fill
  granularity for those 1h bars, not the strategy's period. The header's window
  (2024-04-01 .. 2024-04-30) is extraction metadata, not an `input.time` filter,
  so no data is trimmed.
* Leverage, margin, liquidation, funding and the venue's contract-step rounding
  are not modelled (PINE_SEMANTICS.md section 2).
"""
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


class SMBbDynamicBreakout_b00fdb(PinePortBase, IStrategy):
    source_id = "SM_b00fdb702e0865bd"
    source_file = "Bollinger-Bands-Dynamic-Breakout-Strategy-动态布林带突破策略.md"
    timeframe = "1h"
    can_short = True
    source_defaults: dict = {"length": 34, "mult": 2.0}
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    source_reproduce_stops = False
    source_fidelity_notes = [
        "dev = ta.stdev(src, length) and the bands are basis +/- mult * dev, with "
        "the source's own grouping kept (`upperBand = basis + mult * dev`).",
        "ta.stdev is Pine's population standard deviation (ddof=0); pine_ta's "
        "pine_stdev implements exactly that.",
        "ta.crossover / ta.crossunder against an na operand are false in Pine, which "
        "pine_ta models; the band needs 34 bars, so no signal before bar 33.",
        "Exits are the bands themselves (close under the upper band exits a long, "
        "close over the lower band exits a short); the middle band never places an "
        "order.",
        "No stop / limit / trail exit exists -- the only exits are the two "
        "strategy.close calls -- so source_reproduce_stops is False and a position "
        "open at the window end stays open.",
        "The four `if` statements are independent and keep source order (entry long, "
        "entry short, close long, close short); a close naming an entry that is not "
        "held is a no-op (PINE_SEMANTICS.md 1.12).",
        "strategy() declares only title / shorttitle / overlay, so Pine's documented "
        "defaults apply: strategy.fixed / 1 contract, initial capital 1000000, 0% "
        "commission, pyramiding 0, process_orders_on_close=false.",
        "The md carries no argument table, so both defaults (length = 34, "
        "mult = 2.0) are read from the code alone; its prose agrees with the code.",
        "The header's basePeriod: 15m is the FMZ backtester's own fill granularity, "
        "not the strategy's period, and its window is extraction metadata rather "
        "than an input.time filter, so no data is trimmed.",
        "plot() / fill() calls are display-only and are not reproduced.",
        "Leverage, margin, liquidation, funding and the venue's contract-step "
        "rounding are not modelled.",
    ]

    def pine_indicators(self, dataframe, params):
        close = dataframe["close"]
        length = int(params["length"])
        mult = float(params["mult"])

        # basis     = ta.sma(src, length)
        # dev       = ta.stdev(src, length)
        # upperBand = basis + mult * dev
        # lowerBand = basis - mult * dev
        basis = ta.pine_sma(close, length)
        deviation = ta.pine_stdev(close, length)
        upper_band = basis + mult * deviation
        lower_band = basis - mult * deviation

        dataframe["pine_basis"] = basis
        dataframe["pine_upper_band"] = upper_band
        dataframe["pine_lower_band"] = lower_band

        dataframe["pine_long_condition"] = ta.pine_crossover(
            close, upper_band
        ).fillna(False)
        dataframe["pine_short_condition"] = ta.pine_crossunder(
            close, lower_band
        ).fillna(False)
        dataframe["pine_exit_long_condition"] = ta.pine_crossunder(
            close, upper_band
        ).fillna(False)
        dataframe["pine_exit_short_condition"] = ta.pine_crossover(
            close, lower_band
        ).fillna(False)
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "long_condition": dataframe["pine_long_condition"].to_numpy(),
            "short_condition": dataframe["pine_short_condition"].to_numpy(),
            "exit_long_condition": dataframe["pine_exit_long_condition"].to_numpy(),
            "exit_short_condition": dataframe["pine_exit_short_condition"].to_numpy(),
        }

    def pine_script(self, broker, i, ctx):
        # if (ta.crossover(src, upperBand))
        #     strategy.entry("Long", strategy.long)
        broker.entry("Long", "long", when=bool(ctx["long_condition"][i]))
        # if (ta.crossunder(src, lowerBand))
        #     strategy.entry("Short", strategy.short)
        broker.entry("Short", "short", when=bool(ctx["short_condition"][i]))
        # if (ta.crossunder(src, upperBand))
        #     strategy.close("Long")
        broker.close("Long", when=bool(ctx["exit_long_condition"][i]))
        # if (ta.crossover(src, lowerBand))
        #     strategy.close("Short")
        broker.close("Short", when=bool(ctx["exit_short_condition"][i]))
