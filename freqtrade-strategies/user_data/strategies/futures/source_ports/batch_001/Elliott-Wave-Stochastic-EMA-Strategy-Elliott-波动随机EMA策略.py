"""Port of sources/SM_be79ce0de8205f58.pine (batch_001/Elliott-Wave-Stochastic-EMA-Strategy-Elliott-波动随机EMA策略.md).

Pine v5. The title and the md's prose advertise an "Elliott wave + stochastic +
EMAs" system, but the SOURCE's order logic is a single-EMA cross of the close:

    length = input.int(14, title="Length")
    ema1 = ta.ema(close, 5)
    ema2 = ta.ema(close, 10)
    ema3 = ta.ema(close, 20)
    ema4 = ta.ema(close, 50)
    ema5 = ta.ema(close, 200)

    buySignal  = ta.crossover(close, ema1)
    sellSignal = ta.crossunder(close, ema1)

    k = ta.sma(ta.stoch(close, high, low, 14), 3)
    d = ta.sma(k, 3)
    stoch = k

    if (buySignal)
        strategy.entry("Buy", strategy.long)
    if (sellSignal)
        strategy.entry("Sell", strategy.short)

Only `close` and `ema1` reach the entries. The four longer EMAs, the
stochastic `k` / `d` and the `stoch` alias are computed and plotted but are
never read by a condition -- they are reproduced as columns and left unread,
exactly as the source leaves them. The declared `length` input feeds NOTHING:
`ta.stoch` is called with the literal 14, not with `length`. It is kept in
`source_defaults` because the input exists, and the literal 14 governs.

`strategy()` declares only `title` and `overlay`, so every property is Pine's
documented default: `strategy.fixed` / 1 contract, initial capital 1000000,
commission 0%, `pyramiding 0`, `process_orders_on_close=false`. Neither entry
passes `qty`, so the default quantity supplies it.

The `/*backtest` header declares `period: 3h` on Futures_Binance BTC_USDT, so
`timeframe` is "3h". That period has no local history in this repository, so the
chain comparison cannot run for this port and lands as `skipped_no_local_data`
(tier 5); the port itself is complete.

There is no `strategy.close` / `strategy.exit` and no stop or limit in the
source, so `source_reproduce_stops` is False: a position is only closed by the
opposite entry reversing it, and a position open at the end of the window stays
open.

FIDELITY:

* `ta.stoch` is not exposed by the shared layer, so it is written out from its
  documented definition -- `100 * (source - lowest(low, n)) /
  (highest(high, n) - lowest(low, n))` -- as the unsmoothed %K the source then
  feeds to its own `ta.sma(k, 3)`. A zero-width high/low window makes the ratio
  divide by zero; the port yields na there (the layer's convention for Pine's
  float division by zero) rather than letting an inf/nan escape.
* `ta.crossover(close, ema1)` is `close > ema1 and close[1] <= ema1[1]`; na on
  either side is false, as Pine treats na comparisons, which is what
  `pine_ta.pine_crossover` does.
* `ta.ema` is `pine_ta.pine_ema`, seeded with the first non-na observation and
  with na observations not advancing the recursion. TradingView does not publish
  its seeding rule; PINE_SEMANTICS.md 3.1 records this as a parity risk rather
  than a certified equivalence.
* `plot` / `plotshape` calls, the colours and the `size` argument are
  display-only and place no condition.
* Both `if` blocks are independent (not `else if`) and are kept in the source's
  written order. `buySignal` and `sellSignal` are mutually exclusive
  (crossover / crossunder of the same pair), so at most one fires per bar.
* The md reproduces the source verbatim (the prose is a description of it, not a
  second specification); the only discrepancy is that the md's prose credits the
  stochastic and the longer EMAs with a role the code does not give them. The
  source governs; the prose was NOT followed.
* Leverage, margin, liquidation, funding and the venue's contract-step rounding
  are not modelled; the chain verifier measures the rounding separately.
"""
import numpy as np
import pandas as pd
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


def _pine_stoch(source: pd.Series, high: pd.Series, low: pd.Series,
                length: int) -> pd.Series:
    """Pine `ta.stoch(source, high, low, length)` -- the raw, unsmoothed %K.

        stoch = 100 * (source - lowest(low, length))
                     / (highest(high, length) - lowest(low, length))

    No smoothing: `ta.stoch` returns %K itself, which is why the source feeds it
    to its own `ta.sma(k, 3)` for %D. A zero-width window is Pine's float
    division by zero, which the layer models as na, so that case is masked out
    instead of letting an inf or a 0/0 nan escape.
    """
    lowest = ta.pine_lowest(low, length)
    highest = ta.pine_highest(high, length)
    span = highest - lowest
    with np.errstate(divide="ignore", invalid="ignore"):
        value = 100.0 * (source - lowest) / span
    return value.where(span != 0.0)


class SMElliottWaveStochasticEma_be79ce(PinePortBase, IStrategy):
    source_id = "SM_be79ce0de8205f58"
    source_file = "Elliott-Wave-Stochastic-EMA-Strategy-Elliott-波动随机EMA策略.md"
    timeframe = "3h"
    can_short = True
    source_defaults: dict = {"length": 14}
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    source_reproduce_stops = False
    source_fidelity_notes = [
        "The declared `length` input feeds NOTHING: `ta.stoch` is called with "
        "the literal 14, not with `length`. The input default is kept because "
        "the input exists, and the literal 14 governs, exactly as in the "
        "source.",
        "Only `close` and `ema1` (ta.ema(close, 5)) reach the entries; ema2.. "
        "ema5 and the stochastic k / d are computed and plotted but never read, "
        "so they are reproduced as columns and left unread.",
        "ta.stoch is not in the shared layer and is written out from its "
        "documented definition as the unsmoothed %K; a zero-width high/low "
        "window is na (Pine's float division by zero).",
        "ta.ema is pine_ta.pine_ema, seeded with the first non-na observation "
        "(an unpublished TradingView rule; PINE_SEMANTICS.md 3.1).",
        "ta.crossover / ta.crossunder treat na as false, as Pine does.",
        "The source has no strategy.close / strategy.exit and no stop or limit, "
        "so source_reproduce_stops is False and the only exit is the opposite "
        "entry reversing the position.",
        "plot / plotshape are display-only and are not reproduced.",
        "The md's prose credits the stochastic and the longer EMAs with a role "
        "the code does not give them; the source governs and the prose was NOT "
        "followed (recorded, not 'corrected').",
        "The period is 3h, which the project has no local candles for, so the "
        "chain comparison cannot run (skipped_no_local_data); this is a data "
        "gap, not a port defect.",
        "Leverage, margin, liquidation, funding and contract-step rounding are "
        "not modelled.",
    ]

    def pine_indicators(self, dataframe, params):
        close = dataframe["close"].astype(float)
        high = dataframe["high"].astype(float)
        low = dataframe["low"].astype(float)

        # ema1 = ta.ema(close, 5) ... ema5 = ta.ema(close, 200)
        ema1 = ta.pine_ema(close, 5)
        ema2 = ta.pine_ema(close, 10)
        ema3 = ta.pine_ema(close, 20)
        ema4 = ta.pine_ema(close, 50)
        ema5 = ta.pine_ema(close, 200)
        dataframe["pine_ema1"] = ema1
        dataframe["pine_ema2"] = ema2
        dataframe["pine_ema3"] = ema3
        dataframe["pine_ema4"] = ema4
        dataframe["pine_ema5"] = ema5

        # buySignal = ta.crossover(close, ema1)
        # sellSignal = ta.crossunder(close, ema1)
        buy_signal = ta.pine_crossover(close, ema1)
        sell_signal = ta.pine_crossunder(close, ema1)

        # k = ta.sma(ta.stoch(close, high, low, 14), 3) -- 14 is a literal here,
        # NOT the declared `length` input.
        k = ta.pine_sma(_pine_stoch(close, high, low, 14), 3)
        d = ta.pine_sma(k, 3)
        stoch = k
        dataframe["pine_stoch_k"] = stoch
        dataframe["pine_stoch_d"] = d

        dataframe["pine_buy_signal"] = buy_signal
        dataframe["pine_sell_signal"] = sell_signal
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "buy_signal": dataframe["pine_buy_signal"].to_numpy(dtype=bool),
            "sell_signal": dataframe["pine_sell_signal"].to_numpy(dtype=bool),
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
