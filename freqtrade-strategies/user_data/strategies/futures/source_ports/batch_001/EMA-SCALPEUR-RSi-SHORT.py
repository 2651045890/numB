"""Port of sources/SM_aa7c868aceb979b3.pine (batch_001/EMA-SCALPEUR-RSi-SHORT.md).

Pine v5, FUTURES_BINANCE BTC_USDT, 4h chart. A short-only EMA/RSI scalp:

    RSI  = ta.rsi(close, RSI1)
    EMA1 = ta.ema(close, EMA_L)     EMA2 = ta.ema(close, EMA_L2)
    EMA3 = ta.ema(close, EMA_S)     EMA4 = ta.ema(close, EMA_S2)

    sell     = ta.crossunder(EMA1, EMA2) and RSI > 40
    sellexit = ta.crossover(EMA3, EMA4)

    strategy.entry("short", strategy.short, when = sell,   comment = "ENTER-SHORT")
    strategy.close("short",                 when = sellexit, comment = "EXIT-SHORT")

The source's two commented-out lines (`//buy = ...`, `//buyexit = ...`) place no
condition and are not restored: there is no long entry and no `buyexit` exit.

The `/*backtest` header declares `period: 4h`, so `timeframe` is "4h"; its
`basePeriod: 15m` is the FMZ backtester's own fill granularity for those 4h
bars, not the strategy's period.

`strategy()` declares only `title`, `overlay` and `initial_capital = 1000`, so
every other property is Pine's documented default: `default_qty_type =
strategy.fixed`, `default_qty_value = 1`, commission 0%, `pyramiding = 0`,
`process_orders_on_close = false`. Initial capital is 1000, NOT Pine's 1000000
default -- the source states it.

FIDELITY (see `source_fidelity_notes` for the full list):

* The four `plot()` calls at the top (`shortest`/`short`/`longer`/`longest` =
  `ta.ema(close, 9/26/100/55)`) are display-only duplicates of EMA1..EMA4 at
  their default lengths, and `plot(close)` is the price itself. They are not
  read by any order call and are not reproduced.
* `ta.rsi`'s boundary behaviour follows `pine_ta.pine_rsi` (100 when the window
  had no losses, na until both averages exist), which is Pine's documented
  behaviour but has not been compared bar by bar against the platform
  (PINE_SEMANTICS.md 3.3).
* `ta.ema`'s seeding rule is unpublished; this port inherits the shared layer's
  "first non-na value" seed (PINE_SEMANTICS.md 3.1).
* No stop, limit or trail exit exists -- the only exit is the market
  `strategy.close` -- so `source_reproduce_stops` is False.
* Leverage, margin, liquidation and funding are not modelled; the venue's
  contract-step rounding is not modelled either, and `verify_chain` measures it
  separately (PINE_SEMANTICS.md 1.6). The source's 1000-unit starting capital
  against a fixed order size of 1 whole BTC makes that measurement binding
  here: the engine can book the order, the framework's wallet cannot fund it
  (PINE_SEMANTICS.md 1.5/1.5.1), so the chain verdict is expected to report the
  engine side only.
"""
from __future__ import annotations

from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


class SMEmascalpeurRsiShort_aa7c86(PinePortBase, IStrategy):
    source_id = "SM_aa7c868aceb979b3"
    source_file = "EMA-SCALPEUR-RSi-SHORT.md"
    timeframe = "4h"
    # Only short entries exist in the source; there is no long entry at all.
    can_short = True
    source_defaults: dict = {
        "EMA_L": 9,
        "EMA_L2": 26,
        "EMA_S": 100,
        "EMA_S2": 55,
        "RSI1": 5,
    }
    # strategy(title=..., overlay=true, initial_capital=1000): the remaining
    # properties are Pine's documented defaults.
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1000.0
    source_reproduce_stops = False
    source_fidelity_notes = [
        "Short-only source: `strategy.entry(\"short\", strategy.short, ...)` is "
        "the only entry, so can_short is True and no long entry exists.",
        "The commented-out `//buy = ...` and `//buyexit = ...` lines place no "
        "condition and are not restored; in particular there is no "
        "`crossunder(EMA3, EMA4)` exit alongside the crossover exit.",
        "EMA_S (100) drives EMA3 and EMA_S2 (55) drives EMA4 -- the input "
        "names do not follow the long/short ordering, so they are kept paired "
        "exactly as the source writes them.",
        "The four top `plot()` EMAs (lengths 9/26/100/55) duplicate EMA1..EMA4 "
        "at their defaults and are display-only; they are not computed.",
        "`initial_capital = 1000` is the source's own value, not Pine's "
        "1000000 default; default_qty_type/value, commission and pyramiding "
        "fall back to Pine's documented defaults (fixed / 1 / 0% / 0).",
        "No stop/limit/trail exit exists, only the market `strategy.close`, so "
        "source_reproduce_stops is False.",
        "The 1000-unit starting capital against a fixed size of one whole BTC "
        "is a PINE_SEMANTICS.md 1.5/1.5.1 exposure: the engine books the order "
        "and the framework's wallet cannot fund it. That is measured by "
        "verify_chain, not corrected here.",
        "`ta.ema` seeding (3.1) and `ta.rsi` boundary behaviour (3.3) are the "
        "shared layer's modelled choices.",
    ]

    def pine_indicators(self, dataframe, params):
        close = dataframe["close"].astype(float)
        ema1 = ta.pine_ema(close, int(params["EMA_L"]))
        ema2 = ta.pine_ema(close, int(params["EMA_L2"]))
        ema3 = ta.pine_ema(close, int(params["EMA_S"]))
        ema4 = ta.pine_ema(close, int(params["EMA_S2"]))
        rsi = ta.pine_rsi(close, int(params["RSI1"]))
        # sell = ta.crossunder(EMA1, EMA2) and RSI > 40
        # A na comparison is false in Pine's boolean context, which is also how
        # pandas compares against NaN.
        dataframe["pine_short_entry"] = ta.pine_crossunder(ema1, ema2) & (rsi > 40)
        # sellexit = ta.crossover(EMA3, EMA4)
        dataframe["pine_short_exit"] = ta.pine_crossover(ema3, ema4)
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "short_entry": dataframe["pine_short_entry"].to_numpy(),
            "short_exit": dataframe["pine_short_exit"].to_numpy(),
        }

    def pine_script(self, broker, i, ctx):
        # strategy.entry ("short", strategy.short, when = sell, comment = "ENTER-SHORT")
        if ctx["short_entry"][i]:
            broker.entry("short", "short")
        # strategy.close ("short", when = sellexit, comment = "EXIT-SHORT")
        if ctx["short_exit"][i]:
            broker.close("short")
