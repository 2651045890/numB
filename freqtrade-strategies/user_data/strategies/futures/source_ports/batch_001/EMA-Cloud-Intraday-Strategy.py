"""Port of sources/SM_664f4e3aa15d720d.pine (batch_001/EMA-Cloud-Intraday-Strategy.md).

Pine v5. Two EMAs form the "cloud"; a long is taken while price is above a
green cloud, a short while it is below a red one, and each side is closed when
the PREVIOUS bar's close is on the wrong side of the fast EMA:

    fastEMA = ta.ema(close, fastLen)          # fastLen default 7
    slowEMA = ta.ema(close, slowLen)          # slowLen default 20
    longCondition  = close > fastEMA and fastEMA > slowEMA
    longExit       = close[1] < fastEMA
    shortCondition = close < fastEMA and fastEMA < slowEMA
    shortExit      = close[1] > fastEMA

    if longCondition  -> strategy.entry("Long_Entry",  strategy.long)
    if longExit       -> strategy.close("Long_Entry",  when=longExit)
    if shortCondition -> strategy.entry("Short_Entry", strategy.short)
    if shortExit      -> strategy.close("Short_Entry", when=shortExit)

That if/close ordering (long entry, long close, short entry, short close) is the
source's own order and is reproduced verbatim; both an entry and its close can
be evaluated on one bar, because the entry condition requires `close > fastEMA`
while the exit condition only looks at `close[1]`.

`strategy()` declares `margin_long=100, margin_short=100` (100% margin, i.e.
no leverage -- the engine models an unlevered cash flow) and
`process_orders_on_close=true`. It declares NO sizing, so Pine's documented
defaults apply: `default_qty_type=strategy.fixed`, `default_qty_value=1`,
commission 0%, `pyramiding=0`, initial capital 1000000.

The single `input.int(10, "Trade Quantity")` is declared and NEVER USED: every
`strategy.entry` call passes no `qty`, so the orders are one unit each. The
input is carried in `source_defaults` for visibility only.

The `/*backtest` header declares `period: 1d` on Futures_Binance BTC_USDT, so
`timeframe` is "1d"; its `basePeriod: 1h` is the FMZ backtester's own filling
granularity for those daily bars, not the strategy's period.

There is no stop / limit / trail call in the source (the two `strategy.exit`
lines carrying `trail_points`/`trail_offset` are commented out), so
`source_reproduce_stops` is False and both sides are closed by `strategy.close`.

FIDELITY:

* `process_orders_on_close=true` is NOT modelled. The engine fills a market
  order on the NEXT bar's open, which is Pine's default and what every other
  port in this corpus assumes; the source asks for the signal bar's own close.
  Every entry and every close therefore books one bar later than the source
  would, at a different price. This is a shared-engine gap, not something the
  port can express -- recorded, not worked around.
* md vs source: the md's prose says the cloud is built from the "9 and 20
  period" EMAs, but the source's `Fast EMA Length` default is 7 and the md's own
  argument table agrees with the source (7). The prose is not used.
* md vs source: the md's prose says "closes all trades by the end of the trading
  day". The source contains no session/time-based close of any kind; the exits
  are exactly the two `strategy.close` calls above. Not restored.
* The commented-out `strategy.exit("exit", "My Long/Short Entry Id",
  trail_points=1.5, trail_offset=0)` lines place nothing and are not restored.
* `plot` / `fill` / the `strategy()` title and `overlay` are display-only.
* `ta.ema` is a modelled seeding choice (first non-na value seeds the
  recursion); PINE_SEMANTICS.md section 3.1 records the parity risk and the
  SMA-seeded alternative.
* Leverage, margin, liquidation, funding and contract-step rounding are not
  modelled; the chain verifier measures the rounding separately.
"""
from __future__ import annotations

from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


class SMEmaCloudIntraday_664f4e(PinePortBase, IStrategy):
    source_id = "SM_664f4e3aa15d720d"
    source_file = "EMA-Cloud-Intraday-Strategy.md"
    timeframe = "1d"
    can_short = True
    source_defaults: dict = {"i_trdQty": 10, "fastLen": 7, "slowLen": 20}
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    source_reproduce_stops = False
    source_fidelity_notes = [
        "`process_orders_on_close=true` is declared by the source and is NOT "
        "modelled by the shared engine: market orders here fill at the next "
        "bar's open (Pine's default) instead of at the signal bar's close, so "
        "every fill is one bar later and at a different price than the source "
        "would produce. Recorded as a shared-engine gap, not worked around.",
        "`i_trdQty` (`input.int(10, 'Trade Quantity')`) is DECLARED BUT NEVER "
        "USED: all four strategy.* calls pass no qty, so Pine's default "
        "fixed/1 sizing applies. The input is carried in source_defaults for "
        "visibility only.",
        "md vs source: the md prose describes a 9/20 EMA cloud, the source's "
        "Fast EMA Length default is 7 (and the md's own argument table lists "
        "7). The source governs.",
        "md vs source: the md prose says trades are closed by the end of the "
        "trading day. The source has no session or time-based close; the only "
        "exits are the two strategy.close calls. Not restored.",
        "The two `strategy.exit(..., trail_points=1.5, trail_offset=0)` lines "
        "are commented out in the source and place nothing, so "
        "source_reproduce_stops is False.",
        "margin_long/margin_short = 100 (100% margin, i.e. no leverage); the "
        "engine models an unlevered cash flow.",
        "The source declares no sizing/commission/capital properties, so Pine's "
        "documented defaults apply: fixed/1, 0% commission, pyramiding 0, "
        "initial capital 1000000.",
        "`ta.ema` seeding is the modelled 'first non-na value' choice "
        "(PINE_SEMANTICS.md section 3.1), a parity risk versus TradingView.",
        "plot/fill, the strategy title and `overlay` are display-only.",
        "Leverage, margin, liquidation, funding and contract-step rounding are "
        "not modelled; the chain verifier measures the rounding separately.",
    ]

    def pine_indicators(self, dataframe, params):
        close = dataframe["close"]
        fast = ta.pine_ema(close, int(params["fastLen"]))
        slow = ta.pine_ema(close, int(params["slowLen"]))
        # `close[1]`: na on the first bar, and a comparison with na is false in
        # Pine, which is what a NaN comparison gives in pandas.
        previous_close = close.shift(1)

        dataframe["pine_fast_ema"] = fast
        dataframe["pine_slow_ema"] = slow
        # longCondition = (close > fastEMA and fastEMA > slowEMA)
        dataframe["pine_long_condition"] = (close > fast) & (fast > slow)
        # longExit = close[1] < fastEMA
        dataframe["pine_long_exit"] = previous_close < fast
        # shortCondition = (close < fastEMA and fastEMA < slowEMA)
        dataframe["pine_short_condition"] = (close < fast) & (fast < slow)
        # shortExit = close[1] > fastEMA
        dataframe["pine_short_exit"] = previous_close > fast
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "long_condition": dataframe["pine_long_condition"].to_numpy(),
            "long_exit": dataframe["pine_long_exit"].to_numpy(),
            "short_condition": dataframe["pine_short_condition"].to_numpy(),
            "short_exit": dataframe["pine_short_exit"].to_numpy(),
        }

    def pine_script(self, broker, i, ctx):
        # The source's own call order: long entry, long close, short entry,
        # short close.
        if ctx["long_condition"][i]:
            broker.entry("Long_Entry", "long")
        # if (longExit)
        #     strategy.close("Long_Entry", when=longExit)
        if ctx["long_exit"][i]:
            broker.close("Long_Entry", when=True)
        if ctx["short_condition"][i]:
            broker.entry("Short_Entry", "short")
        # if (shortExit)
        #     strategy.close("Short_Entry", when=shortExit)
        if ctx["short_exit"][i]:
            broker.close("Short_Entry", when=True)
