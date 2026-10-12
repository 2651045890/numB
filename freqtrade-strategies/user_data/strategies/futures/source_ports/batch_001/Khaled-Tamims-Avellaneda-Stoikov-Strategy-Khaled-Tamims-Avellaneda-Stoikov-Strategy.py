"""Port of sources/SM_06086d678826e654.pine (batch_001/Khaled-Tamims-Avellaneda-Stoikov-Strategy-Khaled-Tamims-Avellaneda-Stoikov-Strategy.md).

Pine v5. Khaled Tamim's Avellaneda-Stoikov market-making quotes, reduced by
the source to a two-sided deviation trigger on the mid price:

    avellanedaStoikov(src, gamma, sigma, T, k, M) =>
        midPrice  = (src + src[1]) / 2
        sqrtTerm  = gamma * sigma * sigma * T
        fee       = 0                          // 0.1% fee
        bidQuote  = midPrice - k * sqrtTerm - (midPrice * fee)
        askQuote  = midPrice + k * sqrtTerm + (midPrice * fee)
        [bidQuote, askQuote]

    [bidQuote, askQuote] = avellanedaStoikov(close, gamma, sigma, T, k, M)
    longCondition  = close < bidQuote - M
    shortCondition = close > askQuote + M

    if longCondition  -> strategy.entry("Buy",  strategy.long)
    if shortCondition -> strategy.entry("Sell", strategy.short)

The helper's own local `longCondition` / `shortCondition` are computed inside
its body and thrown away -- only `[bidQuote, askQuote]` is returned. The caller
recomputes the same two expressions against `close`, which is the `src` it
passed, so the values are identical; the port computes the caller's copies,
which are the ones the orders read.

`strategy()` declares only `title` and `overlay`, so every property is Pine's
documented default: `strategy.fixed` / 1 contract, initial capital 1000000,
commission 0%, `pyramiding 0`, `process_orders_on_close=false`.

There is no exit call anywhere in the source: a position is closed only by the
opposite `strategy.entry` reversing it, so `source_reproduce_stops` is False
and a position still open at the end of the window stays open.

The `/*backtest` header declares `period: 4h` on Futures_Binance BTC_USDT, so
`timeframe` is "4h"; its `basePeriod: 15m` is the FMZ backtester's own
granularity for filling those 4h bars, not the strategy's period.

FIDELITY:

* With the source's defaults the quote arithmetic collapses to a plain
  deviation band: `sqrtTerm = 2 * 8 * 8 * 0.0833 = 10.6624`, so
  `bidQuote = mid - 5 * 10.6624 = mid - 53.312` and the long trigger
  `close < bidQuote - 0.5` is exactly `close < close[1] - 107.624`. The port
  reproduces the formula rather than the collapsed band, so a reader can change
  a parameter and still be reading the source's model.
* The md prose says the strategy "同时考虑交易费用" / "takes into account the
  impact of transaction costs". The source does not: `fee = 0` and the only
  fee line is commented out (`// 0.1% fee`). The code is followed; the
  disagreement is recorded rather than reconciled.
* The md's argument table (Gamma 2, Sigma 8, T 0.0833, k 5, M 0.5) matches the
  five `input.float` calls exactly.
* `src[1]` is na on the first bar, so `midPrice` is na, both quote levels are
  na and both comparisons are na -- falsy in Pine. The port's `close.shift(1)`
  gives NaN there and a NaN comparison is False, which is the same outcome.
* `plotshape` / `plot` (including `plot(strategy.netprofit, ...)`, which is
  display-only here) are not reproduced.
* Leverage, margin, liquidation and funding are not modelled, and neither is
  the venue's contract-step rounding, so the framework and the engine may
  differ by a rounded quantity; the chain verifier measures that separately.
"""
import pandas as pd

from freqtrade.strategy import IStrategy

from pine_port_base import PinePortBase


class SMKhaledAvellanedaStoikov_06086d(PinePortBase, IStrategy):
    source_id = "SM_06086d678826e654"
    source_file = (
        "Khaled-Tamims-Avellaneda-Stoikov-Strategy-"
        "Khaled-Tamims-Avellaneda-Stoikov-Strategy.md"
    )
    timeframe = "4h"
    can_short = True
    source_defaults: dict = {
        "Gamma": 2.0,
        "Sigma": 8.0,
        "T": 0.0833,
        "k": 5.0,
        "M": 0.5,
    }
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    source_reproduce_stops = False
    source_fidelity_notes = [
        "The md prose claims the strategy accounts for transaction costs; the "
        "source sets `fee = 0` and leaves the 0.1% fee line commented out. The "
        "code is followed, the disagreement recorded.",
        "The helper's local longCondition / shortCondition are dead code -- only "
        "[bidQuote, askQuote] is returned. The caller recomputes the identical "
        "expressions against `close`, and those are the copies the orders read.",
        "With the source's defaults the quote band collapses to "
        "`close < close[1] - 107.624` (long) / `close > close[1] + 107.624` "
        "(short), but the port reproduces the formula, not the collapsed band.",
        "`src[1]` is na on the first bar, so both conditions are na (falsy) "
        "there; the port's NaN comparison is False, the same outcome.",
        "No exit call exists: a position is closed only by an opposite entry "
        "reversing it, so source_reproduce_stops is False and a position open "
        "at the end of the window stays open.",
        "plotshape / plot calls are display-only and are not reproduced.",
        "Leverage, margin, liquidation, funding and contract-step rounding are "
        "not modelled; the venue's rounding can differ from the engine's float "
        "quantity, which the chain verifier measures separately.",
    ]

    def pine_indicators(self, dataframe, params):
        close = dataframe["close"].astype(float)
        gamma = float(params["Gamma"])
        sigma = float(params["Sigma"])
        horizon = float(params["T"])
        sensitivity = float(params["k"])
        threshold = float(params["M"])

        # midPrice = (src + src[1]) / 2
        mid_price = (close + close.shift(1)) / 2.0
        # sqrtTerm = gamma * sigma * sigma * T
        sqrt_term = gamma * sigma * sigma * horizon
        # fee = 0 in the source (the 0.1% line is commented out)
        fee = 0.0
        # bidQuote = midPrice - k * sqrtTerm - (midPrice * fee)
        bid_quote = mid_price - sensitivity * sqrt_term - (mid_price * fee)
        # askQuote = midPrice + k * sqrtTerm + (midPrice * fee)
        ask_quote = mid_price + sensitivity * sqrt_term + (mid_price * fee)

        dataframe["pine_mid_price"] = mid_price
        dataframe["pine_sqrt_term"] = sqrt_term
        dataframe["pine_bid_quote"] = bid_quote
        dataframe["pine_ask_quote"] = ask_quote
        dataframe["pine_long_condition"] = close < bid_quote - threshold
        dataframe["pine_short_condition"] = close > ask_quote + threshold
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "long_condition": dataframe["pine_long_condition"].to_numpy(),
            "short_condition": dataframe["pine_short_condition"].to_numpy(),
        }

    def pine_script(self, broker, i, ctx):
        # if (longCondition)
        #     strategy.entry("Buy", strategy.long)
        if ctx["long_condition"][i]:
            broker.entry("Buy", "long")
        # if (shortCondition)
        #     strategy.entry("Sell", strategy.short)
        if ctx["short_condition"][i]:
            broker.entry("Sell", "short")
