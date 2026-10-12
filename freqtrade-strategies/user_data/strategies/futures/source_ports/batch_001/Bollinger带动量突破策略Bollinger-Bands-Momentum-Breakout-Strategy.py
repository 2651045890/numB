"""Port of sources/SM_bf21aad3e4c5c95c.pine (batch_001/Bollinger带动量突破策略Bollinger-Bands-Momentum-Breakout-Strategy.md).

Pine v4, `strategy(title="NoScoobies Bollinger Bands", overlay=true)`. Price
against its own 20-period SMA, with the band exits nested INSIDE the entry
branches:

    source = close
    basis  = sma(source, length)
    dev    = mult * stdev(source, length)
    upper  = basis + dev
    lower  = basis - dev

    long        = crossover(source, basis)
    short       = crossunder(source, basis)
    close_long  = crossunder(source, upper)
    close_short = crossover(source, lower)

    if long
        strategy.entry("Long", strategy.long)
        strategy.close("Long", when = close_long)
    if short
        strategy.entry("Short", strategy.short)
        strategy.close("Short", when = close_short)

The nesting is load-bearing and is reproduced: `strategy.close("Long", ...)` is
reached ONLY on a bar where `long` is true, so it is placed only on those bars
(and then closes only if `close_long` is also true on that same bar). Placing
the close unconditionally would fire it on every bar the band exit held, which
is a different strategy.

`strategy()` declares only `title` / `overlay`, so Pine's documented defaults
apply and are what this port carries: `default_qty_type=fixed`, one unit per
order, `commission_value=0`, `pyramiding=0`, `process_orders_on_close=false`,
initial capital 1000000.

The `/*backtest` header declares `period: 1h` on Futures_Binance BTC_USDT, so
`timeframe` is "1h"; its `basePeriod: 15m` is the FMZ backtester's own filling
granularity, not the strategy's period.

There is no stop, limit or trailing exit anywhere, so `source_reproduce_stops`
is False: exits are next-open market closes only, and a position still open at
the end of the window stays open.

FIDELITY:

* `source = close` is a literal in the source, not an `input`, so the port
  reads `close` directly rather than routing it through a parameter.
* `stdev` is Pine's population standard deviation (ddof=0), which is what
  pine_ta.pine_stdev computes.
* `mult` defaults to 1.5 here, NOT the 2.0 that a "standard" 20-period
  Bollinger Band uses; the source's own comment says as much ("Use 1.5 SD for
  20 period MA"). The declared default is reproduced unchanged.
* `plot` / `fill` are display-only and are not reproduced.
* The markdown's prose claims a band breakout opens the trade ("when the price
  breaks through the upper band ... a buy signal is formed"). The source does
  the opposite: `crossover(source, basis)` enters and `crossunder(source,
  upper)` exits. The prose is not followed -- the source is authoritative.
* There is no exit call outside the two entry branches, so a position is only
  ever closed by the nested close or by the opposite entry reversing it.
* Leverage, margin, liquidation, funding and venue contract-step rounding are
  not modelled.
"""
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


class SMBollingerBandsMomentumBreakout_bf21aa(PinePortBase, IStrategy):
    source_id = "SM_bf21aad3e4c5c95c"
    source_file = "Bollinger带动量突破策略Bollinger-Bands-Momentum-Breakout-Strategy.md"
    timeframe = "1h"
    can_short = True
    source_defaults: dict = {"length": 20, "mult": 1.5}
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    source_reproduce_stops = False
    source_fidelity_notes = [
        "The two strategy.close calls are nested inside the `if long` / "
        "`if short` branches and are reached only on a crossover bar; placing "
        "them unconditionally would be a different strategy.",
        "`source = close` is a literal in the source, not an input.",
        "mult defaults to 1.5, not the 2.0 of a textbook 20-period Bollinger "
        "Band; the declared default is kept.",
        "stdev is the population form (ddof=0), as Pine ta.stdev computes it.",
        "The markdown prose says the band breakout is the entry while the "
        "source enters on the basis cross and exits on the band cross; the "
        "source wins and the discrepancy is recorded, not silently adopted.",
        "No stop / limit / trailing exit exists, so source_reproduce_stops is "
        "False and an open position at the window end stays open.",
        "plot / fill are display-only and are not reproduced.",
        "Leverage, margin, liquidation, funding and venue contract-step "
        "rounding are not modelled.",
    ]

    def pine_indicators(self, dataframe, params):
        source = dataframe["close"]
        length = int(params["length"])
        mult = float(params["mult"])

        basis = ta.pine_sma(source, length)
        dev = mult * ta.pine_stdev(source, length)
        upper = basis + dev
        lower = basis - dev

        dataframe["pine_long"] = ta.pine_crossover(source, basis)
        dataframe["pine_short"] = ta.pine_crossunder(source, basis)
        dataframe["pine_close_long"] = ta.pine_crossunder(source, upper)
        dataframe["pine_close_short"] = ta.pine_crossover(source, lower)
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "long": dataframe["pine_long"].to_numpy(),
            "short": dataframe["pine_short"].to_numpy(),
            "close_long": dataframe["pine_close_long"].to_numpy(),
            "close_short": dataframe["pine_close_short"].to_numpy(),
        }

    def pine_script(self, broker, i, ctx):
        # if long
        #     strategy.entry("Long", strategy.long)
        #     strategy.close("Long", when = close_long)
        if ctx["long"][i]:
            broker.entry("Long", "long")
            broker.close("Long", when=bool(ctx["close_long"][i]))
        # if short
        #     strategy.entry("Short", strategy.short)
        #     strategy.close("Short", when = close_short)
        if ctx["short"][i]:
            broker.entry("Short", "short")
            broker.close("Short", when=bool(ctx["close_short"][i]))
