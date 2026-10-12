"""Port of sources/SM_d27c01b97b6a94f6.pine (batch_001/EMA动态趋势追踪交易策略-EMA-Dynamic-Trend-Following-Trading-Strategy.md).

Pine v5, `strategy("buy sell Trend", overlay=true)`. An ATR-scaled channel
around an EMA of the Donchian midline, with a separate high-based sell line:

    atr     = ta.atr(atr_length)
    highest = ta.highest(highest_length)
    lowest  = ta.lowest(lowest_length)

    f_atr      = atr * 2.382
    ema_hl     = ta.ema((highest[1] + lowest[1]) / 2, 14)
    ema_highest = ema_hl + f_atr
    ema_lowest  = ema_hl - f_atr
    ema_mid     = (ema_highest + ema_lowest) / 2

    bs_hi     = ta.highest(highest_s_length)
    f_atr2    = atr * 5.618
    sell_line = ta.ema(bs_hi[1] + f_atr2, sell_l_length)

    buy_cond  = ta.crossover(ema_lowest, lowest) and close < ema_mid
    sell_cond = (ta.crossunder(ema_highest, highest) and close > ema_mid)
                or high >= sell_line

    if buy_cond
        strategy.entry('BUY', strategy.long)
    if sell_cond
        strategy.entry('SELL', strategy.short)

The one-argument `ta.highest(length)` / `ta.lowest(length)` overloads read the
built-in `high` / `low` series (the same overload the corpus's Ichimoku ports
rely on for `math.avg(ta.lowest(n), ta.highest(n))`); they are written here as
pine_highest(dataframe["high"], ...) and pine_lowest(dataframe["low"], ...)
rather than taking the default `source`-style argument, which would have read
`close`.

Note the two history references on the raw rolling extremes: `highest[1]` /
`lowest[1]` feed `ema_hl`, and `bs_hi[1]` feeds `sell_line`, so both channels
lag the extreme by one bar before the EMA is applied.

`ema_mid` is computed with the source's own expression,
`(ema_highest + ema_lowest) / 2`, rather than being folded to `ema_hl`, so the
arithmetic performed is the source's.

`2.382` and `5.618` are plain assignments, not `input()`s, so they are not
parameters and stay literals. The `14` in `ta.ema(..., 14)` is likewise a
literal, while `sell_l_length` (default 55) is an input. `ta.atr`, `ta.ema`,
`ta.highest` and `ta.lowest` are all na until their window is full, so nothing
can fire during warmup.

`strategy()` declares only `title` / `overlay`, so Pine's documented defaults
apply and are what this port carries: `default_qty_type=fixed`, one unit per
order, `commission_value=0`, `pyramiding=0`, `process_orders_on_close=false`.
Initial capital is unset in the source, hence Pine's documented default
1000000.

The `/*backtest` header declares `period: 1d` on Futures_Binance BTC_USDT, so
`timeframe` is "1d"; its `basePeriod: 1h` is the FMZ backtester's own
granularity for filling those 1d bars, not the strategy's period.

There is no exit call in the source -- not `strategy.close`, not
`strategy.exit` -- so a position is closed only by the opposite entry
reversing it: `source_reproduce_stops` is False and a position still open at
the end of the window stays open.

FIDELITY:

* `ta.atr(atr_length)` is `ta.rma(ta.tr(true), length)`. pine_ta.pine_atr is
  exactly that, so it carries PINE_SEMANTICS §3.7's known boundary: Pine's
  `ta.tr` with the default `handle_na=false` returns na on the very first bar
  while pine_ta.pine_tr gives `high - low` there, which advances the rma
  seeding by one bar. The difference decays and is not corrected here --
  §3.7 records it as a shared-layer boundary, and changing it would mean
  reimplementing a public-layer function inside a port.
* `ta.ema`'s seeding is Pine's unpublished choice; pine_ta.pine_ema seeds with
  the first non-na observation and does not advance the recursion on na
  (PINE_SEMANTICS §3.1). The na `(highest[1] + lowest[1]) / 2` of the warmup
  therefore holds the EMA at na rather than starting it at bar 0.
* `ta.highest` / `ta.lowest` return na until their window is full and
  propagate na within it (pine_ta.pine_highest / pine_lowest).
* `ta.crossover` / `ta.crossunder` are `a > b and a[1] <= b[1]` /
  `a < b and a[1] >= b[1]`; an na operand makes the comparison na, which Pine
  evaluates as false and numpy/pandas reproduce as false.
* The markdown has no Strategy Arguments table for this source, so its input
  defaults (14 / 60 / 60 / 30 / 55) come from the source lines alone.
* The markdown prose matches the code's direction on every rule (buy on an
  upward cross of ema_lowest through lowest while close is below ema_mid,
  sell on a downward cross of ema_highest through highest while close is above
  ema_mid, or on high reaching sell_line), so prose and source agree here.
* `plot` / `plotshape` / the commented-out `plot(ema_mid)` / `title` /
  `overlay` carry no orders and are not reproduced.
* Leverage, margin, liquidation and funding are not modelled; the venue's
  contract-step rounding is not modelled either, so the framework and the
  engine can differ by a rounded quantity (the chain verifier measures that
  separately rather than treating it as a signal difference).
"""
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


class SMEmaDynamicTrendFollowing_d27c01(PinePortBase, IStrategy):
    source_id = "SM_d27c01b97b6a94f6"
    source_file = (
        "EMA动态趋势追踪交易策略-EMA-Dynamic-Trend-Following-Trading-Strategy.md"
    )
    timeframe = "1d"
    can_short = True
    source_defaults: dict = {
        "atr_length": 14,
        "highest_length": 60,
        "highest_s_length": 60,
        "lowest_length": 30,
        "sell_l_length": 55,
    }
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    source_reproduce_stops = False
    source_fidelity_notes = [
        "The one-argument ta.highest(length) / ta.lowest(length) overloads read "
        "the built-in high / low series; they are expanded to "
        "pine_highest(high, ...) / pine_lowest(low, ...) explicitly.",
        "f = 2.382, f2 = 5.618 and the 14 in ta.ema(..., 14) are plain "
        "literals, not inputs, and stay literals; sell_l_length (55) is an "
        "input.",
        "ema_mid is computed as (ema_highest + ema_lowest) / 2, the source's "
        "own expression, rather than folded to ema_hl.",
        "ta.atr carries PINE_SEMANTICS 3.7's known boundary: Pine's ta.tr with "
        "the default handle_na=false is na on the first bar while "
        "pine_ta.pine_tr gives high - low, advancing the rma seeding by one "
        "bar. Not corrected (shared-layer boundary).",
        "ta.ema seeding is Pine's unpublished choice; pine_ta.pine_ema seeds "
        "from the first non-na observation (PINE_SEMANTICS 3.1).",
        "The markdown has no Strategy Arguments table for this source; the "
        "defaults come from the source lines.",
        "No exit call exists (no strategy.close, no strategy.exit): a position "
        "is closed only by an opposite entry reversing it, so "
        "source_reproduce_stops is False and a position open at the end of the "
        "window stays open.",
        "strategy() declares only title / overlay, so Pine's documented "
        "defaults apply: fixed quantity 1, commission 0%, pyramiding 0, "
        "process_orders_on_close=false, initial capital 1000000.",
        "plot / plotshape / title / overlay are display-only and are not "
        "reproduced.",
        "Leverage, margin, liquidation, funding and venue contract-step "
        "rounding are not modelled.",
    ]

    def pine_indicators(self, dataframe, params):
        atr_length = int(params["atr_length"])
        highest_length = int(params["highest_length"])
        highest_s_length = int(params["highest_s_length"])
        lowest_length = int(params["lowest_length"])
        sell_l_length = int(params["sell_l_length"])
        f = 2.382   # literal in the source, not an input
        f2 = 5.618  # literal in the source, not an input

        high = dataframe["high"]
        low = dataframe["low"]
        close = dataframe["close"]

        # atr = ta.atr(atr_length)
        atr = ta.pine_atr(dataframe, atr_length)
        # highest = ta.highest(highest_length)   -> highest of `high`
        # lowest  = ta.lowest(lowest_length)     -> lowest of `low`
        highest = ta.pine_highest(high, highest_length)
        lowest = ta.pine_lowest(low, lowest_length)

        # f_atr = atr * f
        # ema_hl = ta.ema((highest[1] + lowest[1]) / 2, 14)
        f_atr = atr * f
        ema_hl = ta.pine_ema((highest.shift(1) + lowest.shift(1)) / 2.0, 14)
        ema_highest = ema_hl + f_atr
        ema_lowest = ema_hl - f_atr
        ema_mid = (ema_highest + ema_lowest) / 2.0

        # bs_hi = ta.highest(highest_s_length)   -> highest of `high`
        # f_atr2 = atr * f2
        # sell_line = ta.ema(bs_hi[1] + f_atr2, sell_l_length)
        bs_hi = ta.pine_highest(high, highest_s_length)
        f_atr2 = atr * f2
        sell_line = ta.pine_ema(bs_hi.shift(1) + f_atr2, sell_l_length)

        dataframe["pine_atr"] = atr
        dataframe["pine_highest"] = highest
        dataframe["pine_lowest"] = lowest
        dataframe["pine_ema_highest"] = ema_highest
        dataframe["pine_ema_lowest"] = ema_lowest
        dataframe["pine_ema_mid"] = ema_mid
        dataframe["pine_sell_line"] = sell_line
        # buy_cond = ta.crossover(ema_lowest, lowest) and close < ema_mid
        dataframe["pine_buy_cond"] = ta.pine_crossover(ema_lowest, lowest) & (
            close < ema_mid
        )
        # sell_cond = (ta.crossunder(ema_highest, highest) and close > ema_mid)
        #             or high >= sell_line
        dataframe["pine_sell_cond"] = (
            ta.pine_crossunder(ema_highest, highest) & (close > ema_mid)
        ) | (high >= sell_line)
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "buy_cond": dataframe["pine_buy_cond"].to_numpy(),
            "sell_cond": dataframe["pine_sell_cond"].to_numpy(),
        }

    def pine_script(self, broker, i, ctx):
        # if buy_cond
        #     strategy.entry('BUY', strategy.long)
        if ctx["buy_cond"][i]:
            broker.entry("BUY", "long")
        # if sell_cond
        #     strategy.entry('SELL', strategy.short)
        if ctx["sell_cond"][i]:
            broker.entry("SELL", "short")
