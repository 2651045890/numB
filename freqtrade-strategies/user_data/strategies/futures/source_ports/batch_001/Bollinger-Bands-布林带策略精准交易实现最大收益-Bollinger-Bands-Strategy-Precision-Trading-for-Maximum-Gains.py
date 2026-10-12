"""Port of sources/SM_c2d41a852ecde2d9.pine (batch_001/Bollinger-Bands-布林带策略精准交易实现最大收益-Bollinger-Bands-Strategy-Precision-Trading-for-Maximum-Gains.md).

Pine v5, `strategy("Bollinger Bands Strategy with Long and Short",
overlay=true)`. Four separate conditions, each written out twice with a
long-side and a short-side name, then four independent `if` blocks:

    basis = ta.sma(src, length)
    dev   = mult * ta.stdev(src, length)
    upper = basis + dev
    lower = basis - dev

    buyConditionLower   = ta.crossover(src, lower)
    sellConditionUpper  = ta.crossunder(src, upper)
    buyConditionBasis   = ta.crossover(src, basis)
    sellConditionBasis  = ta.crossunder(src, basis)
    buyCondition        = buyConditionLower or buyConditionBasis
    sellCondition       = sellConditionUpper or sellConditionBasis

    shortConditionUpper = ta.crossunder(src, upper)
    coverConditionLower = ta.crossover(src, lower)
    shortConditionBasis = ta.crossunder(src, basis)
    coverConditionBasis = ta.crossover(src, basis)
    shortCondition      = shortConditionUpper or shortConditionBasis
    coverCondition      = coverConditionLower or coverConditionBasis

    if (buyCondition)
        strategy.entry("Long", strategy.long)
    if (sellCondition)
        strategy.close("Long")
    if (shortCondition)
        strategy.entry("Short", strategy.short)
    if (coverCondition)
        strategy.close("Short")

Note that `shortCondition` is textually the same disjunction as
`sellCondition`, and `coverCondition` the same as `buyCondition`. All eight
member series are nevertheless written out here exactly as the source spells
them, rather than aliased, so the port's shape matches the source line for
line. The consequence of that identity is that, on every `buyCondition` bar,
both `strategy.entry("Long")` AND `strategy.close("Short")` are placed; the
engine fills them in creation order (entry first, reversing any short, then the
close, whose entry is by then gone and which is therefore a no-op). On every
`sellCondition` bar, `strategy.close("Long")` is placed before
`strategy.entry("Short")`, so the long is closed and then the short opened.

`strategy()` declares only `title` / `overlay`, so Pine's documented defaults
apply and are what this port carries: `default_qty_type=fixed`, one unit per
order, `commission_value=0`, `pyramiding=0`, `process_orders_on_close=false`,
initial capital 1000000.

The `/*backtest` header declares `period: 2h` on Futures_Binance BTC_USDT, so
`timeframe` is "2h". There is no local 2h futures history, so the chain
verifier reports `skipped_no_local_data` for this port.

There is no stop, limit or trailing exit anywhere, so `source_reproduce_stops`
is False: exits are next-open market closes only, and a position still open at
the end of the window stays open.

FIDELITY:

* `stdev` is Pine's population standard deviation (ddof=0), which is what
  pine_ta.pine_stdev computes.
* `plot`, `p1`, `p2`, `fill`, the four `plotshape` calls and the four
  `alertcondition` calls are display-only and are not reproduced.
* `src` is an `input(close)`; the port resolves it through
  pine_ta.pine_source so a non-default source still works, rather than
  hard-coding `close`.
* The markdown's prose describes the rules in the same direction the code
  implements them (buy on an upward cross of lower or basis, sell/short on a
  downward cross of upper or basis), so prose and source agree here.
* Leverage, margin, liquidation, funding and venue contract-step rounding are
  not modelled.
"""
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


class SMBollingerBandsLongShort_c2d41a(PinePortBase, IStrategy):
    source_id = "SM_c2d41a852ecde2d9"
    source_file = (
        "Bollinger-Bands-布林带策略精准交易实现最大收益-"
        "Bollinger-Bands-Strategy-Precision-Trading-for-Maximum-Gains.md"
    )
    timeframe = "2h"
    can_short = True
    source_defaults: dict = {"length": 20, "src": "close", "mult": 2.0}
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    source_reproduce_stops = False
    source_fidelity_notes = [
        "shortCondition is textually the same disjunction as sellCondition and "
        "coverCondition the same as buyCondition; all eight member series are "
        "written out as the source spells them instead of being aliased.",
        "Because coverCondition == buyCondition, a buy bar places both "
        "entry(Long) and close(Short); the engine fills in creation order, so "
        "the entry reverses first and the close finds nothing.",
        "stdev is the population form (ddof=0), as Pine ta.stdev computes it.",
        "src is an input(close) and is resolved through pine_source rather "
        "than hard-coded.",
        "plot / fill / plotshape / alertcondition are display-only and are not "
        "reproduced.",
        "No stop / limit / trailing exit exists, so source_reproduce_stops is "
        "False and an open position at the window end stays open.",
        "Leverage, margin, liquidation, funding and venue contract-step "
        "rounding are not modelled.",
    ]

    def pine_indicators(self, dataframe, params):
        length = int(params["length"])
        mult = float(params["mult"])
        src = ta.pine_source(dataframe, str(params["src"]))

        basis = ta.pine_sma(src, length)
        dev = mult * ta.pine_stdev(src, length)
        upper = basis + dev
        lower = basis - dev

        buy_lower = ta.pine_crossover(src, lower)
        sell_upper = ta.pine_crossunder(src, upper)
        buy_basis = ta.pine_crossover(src, basis)
        sell_basis = ta.pine_crossunder(src, basis)
        short_upper = ta.pine_crossunder(src, upper)
        cover_lower = ta.pine_crossover(src, lower)
        short_basis = ta.pine_crossunder(src, basis)
        cover_basis = ta.pine_crossover(src, basis)

        dataframe["pine_buy_condition"] = buy_lower | buy_basis
        dataframe["pine_sell_condition"] = sell_upper | sell_basis
        dataframe["pine_short_condition"] = short_upper | short_basis
        dataframe["pine_cover_condition"] = cover_lower | cover_basis
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "buy": dataframe["pine_buy_condition"].to_numpy(),
            "sell": dataframe["pine_sell_condition"].to_numpy(),
            "short": dataframe["pine_short_condition"].to_numpy(),
            "cover": dataframe["pine_cover_condition"].to_numpy(),
        }

    def pine_script(self, broker, i, ctx):
        # if (buyCondition)
        #     strategy.entry("Long", strategy.long)
        if ctx["buy"][i]:
            broker.entry("Long", "long")
        # if (sellCondition)
        #     strategy.close("Long")
        if ctx["sell"][i]:
            broker.close("Long")
        # if (shortCondition)
        #     strategy.entry("Short", strategy.short)
        if ctx["short"][i]:
            broker.entry("Short", "short")
        # if (coverCondition)
        #     strategy.close("Short")
        if ctx["cover"][i]:
            broker.close("Short")
