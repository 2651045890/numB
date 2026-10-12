"""Port of sources/SM_5a0b0398d404f3c1.pine
(batch_001/EMA均线交叉策略EMA-Crossover-Strategy.md).

Pine v4. A long-only EMA cross system whose "fast" leg is literally an EMA of
length 1 -- i.e. the close itself -- so both signals are the close crossing a
slow EMA:

    emaFast = 1                                  // literal, not an input
    slowEMABuy  = input(defval=20)
    slowEMASell = input(defval=30)

    fastEMA           = ema(close, emaFast)      // == close
    slowEMABuyValue   = ema(close, slowEMABuy)
    slowEMASellValue  = ema(close, slowEMASell)

    buyCondition  = crossunder(slowEMABuyValue,  fastEMA)   // close crosses UP over EMA20
    sellCondition = crossover(slowEMASellValue, fastEMA)    // close crosses DOWN under EMA30

    if (buyCondition and inDateRange)
        strategy.entry("Buy", strategy.long)
    if (sellCondition and inDateRange)
        strategy.close("Buy")
    if (strategy.position_size > 0 and sellCondition)
        strategy.close("Sell")
    if (strategy.position_size < 0 and buyCondition)
        strategy.close("Sell")

All four order statements are preserved in order. The last two are no-ops on
this source: no `strategy.entry("Sell", strategy.short)` exists anywhere, so
`strategy.position_size` is never negative and the id "Sell" is never open --
`strategy.close("Sell")` therefore closes nothing, in the engine exactly as in
Pine. The port keeps them rather than deleting them, so the call sequence and
the projection stage see what the source actually issues.

`can_short` is False for the same reason: the `tradeDirection` input offers
"Short" and "Both", but its value is only ever assigned to the dead `longOK` /
`shortOK` locals -- no order statement consults it, so no mode of this source
can open a short.

`strategy(...)` declares only `title` and `overlay`, so every other property is
Pine's documented default: `fixed` sizing of 1 contract, 0% commission,
`pyramiding = 0`, initial capital 1000000.

The /*backtest header declares `period: 1h` on Futures_Binance BTC_USDT, hence
`timeframe = "1h"` (its `basePeriod: 15m` is the FMZ backtester's intrabar fill
granularity, not the strategy's period).

FIDELITY -- translation choices and source/original mismatches:

1. `inDateRange` IS A LITERAL `true` in the source: the two `input.time` values
   (`startDate` / `endDate`) are declared and then never referenced. The port
   keeps the conjunct as an always-true flag rather than dropping the `and`
   clause, and declares both inputs as dead defaults.
2. `ema(close, 1)` has smoothing factor 2/(1+1) = 1, so the series equals
   `close` on every bar from the first. pine_ta.pine_ema with length 1 and the
   first-value seed reproduces that exactly; it is not replaced by the raw
   `close` column, so the two cannot diverge if the seeding rule is revisited
   (Pine_SEMANTICS.md 3.1).
3. The md's argument table lists `v_input_3` as `0` for a "Trade Direction:
   Both|Short|Long" selector; the source's own default is the string "Both"
   (the table's `0` is the option index). The port declares "Both", as the
   source does -- and records that the value has no effect either way.
4. `strategy.close("Buy")` can be issued on the same bar as the entry when a
   single close crosses above EMA20 and below EMA30 at once. Both are market
   orders placed on the same bar, so the engine fills them in creation order on
   the next open -- entry first, then the close -- producing a zero-length
   round trip. Pine_SEMANTICS.md section 1.13 records the same-bar sequencing
   as a modelling choice, not a verified platform rule; it is not "fixed" here.
5. `longOK` / `shortOK` are computed by the source and then never referenced.
   They are not reproduced as anything, since nothing reads them.
6. An na comparison is falsy in Pine, so both cross conditions are False during
   the EMAs' warm-up; pine_crossover / pine_crossunder do the same.
7. plot() calls are display-only and are not reproduced.
8. Leverage, margin, liquidation, funding and the venue's contract-step
   rounding are not modelled; the chain verifier measures the step rounding
   separately instead of treating it as a signal difference.
"""
import numpy as np  # noqa: F401  (kept for symmetry with the other ports)

from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


class SMEmaCrossover_5a0b03(PinePortBase, IStrategy):
    source_id = "SM_5a0b0398d404f3c1"
    source_file = "EMA均线交叉策略EMA-Crossover-Strategy.md"
    timeframe = "1h"
    # The source offers a "Short" tradeDirection but never acts on it: the only
    # entry call is strategy.entry("Buy", strategy.long), and the "Sell" id is
    # only ever named by two strategy.close calls.
    can_short = False
    source_defaults: dict = {
        # input(title="Slow EMA for Buy Signals", defval=20, minval=1, maxval=9999)
        "slowEMABuy": 20,
        # input(title="Slow EMA for Sell Signals", defval=30, minval=1, maxval=9999)
        "slowEMASell": 30,
        # input(title="Trade Direction", options=["Long","Short","Both"], defval="Both")
        "tradeDirection": "Both",
        # input(title="Start Date", type=input.time, defval=timestamp("01 Jan 2018 00:00"))
        # input(title="End Date",   type=input.time, defval=timestamp("31 Dec 2025 23:59"))
        # Declared by the source and never read -- `inDateRange` is the literal
        # `true`, so these two change nothing.
        "startDate": "2018-01-01T00:00",
        "endDate": "2025-12-31T23:59",
    }
    # strategy("EMA Cross Strategy with Custom Buy/Sell Conditions", overlay=true):
    # title and overlay only, so Pine's documented defaults apply -- fixed /
    # 1 contract, 0% commission, pyramiding 0, initial capital 1000000.
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    # No stop / limit / trail leg: every exit is a market strategy.close.
    source_reproduce_stops = False
    source_fidelity_notes = [
        "inDateRange is the LITERAL `true` in the source; the two input.time "
        "values startDate/endDate are declared and never referenced, so they "
        "filter nothing. The port keeps the conjunct as an always-true flag and "
        "declares both inputs as dead defaults.",
        "tradeDirection is also dead: it only ever feeds the local longOK / "
        "shortOK, which no order statement reads. The port therefore declares "
        "can_short = False -- no mode of this source opens a short, because no "
        "strategy.entry(..., strategy.short) exists.",
        "The two strategy.close(\"Sell\") statements are no-ops on this source "
        "(the id \"Sell\" is never opened, so position_size is never negative); "
        "they are preserved rather than deleted so the call sequence stays as "
        "written.",
        "ema(close, 1) has smoothing factor 1 and equals close from the first "
        "bar; it is produced by pine_ema(length=1) rather than substituted by "
        "the raw close column.",
        "The md's argument table shows v_input_3 as `0`; the source's default "
        "is the string \"Both\" (0 is the option index). Both are declared, and "
        "neither has an effect.",
        "When one close crosses above EMA20 and below EMA30 on the same bar, the "
        "source places the entry and the strategy.close(\"Buy\") together; the "
        "engine fills them in creation order on the next open (entry, then "
        "close), a zero-length round trip. Same-bar sequencing is a modelled "
        "choice (Pine_SEMANTICS 1.13), not corrected here.",
        "longOK / shortOK are dead locals in the source and are not reproduced.",
        "plot() calls are display-only and are not reproduced.",
    ]

    def pine_indicators(self, dataframe, params):
        close = dataframe["close"]
        # emaFast = 1; fastEMA = ema(close, emaFast)  -- alpha = 2/(1+1) = 1
        fast_ema = ta.pine_ema(close, 1)
        # slowEMABuyValue = ema(close, slowEMABuy)
        slow_ema_buy = ta.pine_ema(close, int(params["slowEMABuy"]))
        # slowEMASellValue = ema(close, slowEMASell)
        slow_ema_sell = ta.pine_ema(close, int(params["slowEMASell"]))
        dataframe["pine_fast_ema"] = fast_ema
        dataframe["pine_slow_ema_buy"] = slow_ema_buy
        dataframe["pine_slow_ema_sell"] = slow_ema_sell
        # buyCondition = crossunder(slowEMABuyValue, fastEMA)
        dataframe["pine_buy_condition"] = ta.pine_crossunder(slow_ema_buy, fast_ema)
        # sellCondition = crossover(slowEMASellValue, fastEMA)
        dataframe["pine_sell_condition"] = ta.pine_crossover(slow_ema_sell, fast_ema)
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "buy": dataframe["pine_buy_condition"].to_numpy(dtype=bool),
            "sell": dataframe["pine_sell_condition"].to_numpy(dtype=bool),
        }

    def pine_script(self, broker, i, ctx):
        buy_condition = ctx["buy"][i]
        sell_condition = ctx["sell"][i]
        # inDateRange = true (literal in the source)
        in_date_range = True

        # if (buyCondition and inDateRange)
        #     strategy.entry("Buy", strategy.long)
        if buy_condition and in_date_range:
            broker.entry("Buy", "long")

        # if (sellCondition and inDateRange)
        #     strategy.close("Buy")
        if sell_condition and in_date_range:
            broker.close("Buy")

        # if (strategy.position_size > 0 and sellCondition)
        #     strategy.close("Sell")      -- "Sell" is never an open entry
        if broker.position_size > 0 and sell_condition:
            broker.close("Sell")

        # if (strategy.position_size < 0 and buyCondition)
        #     strategy.close("Sell")      -- position_size is never negative
        if broker.position_size < 0 and buy_condition:
            broker.close("Sell")
