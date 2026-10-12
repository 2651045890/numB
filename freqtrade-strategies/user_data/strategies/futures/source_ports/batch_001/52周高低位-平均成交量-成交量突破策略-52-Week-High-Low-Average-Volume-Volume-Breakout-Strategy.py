"""Port of sources/SM_2ace7bb458896a8c.pine (52周高低位-平均成交量-成交量突破策略).

Pine v5, long only, daily. Three conditions must hold on the same bar:

    highestHigh       = ta.highest(close, 52 * 5)          // 260 bars
    percentFromHigh   = 100 * (highestHigh - close) / highestHigh
    avgVolume         = ta.sma(volume, 50)
    volumeRise        = volume > avgVolume * 1.5
    dailyPriceChange  = 100 * (close - open) / open
    priceChangeLimit  = 10 when the chart is weekly/monthly, else 3
    entryCondition    = percentFromHigh <= 10 and volumeRise
                        and dailyPriceChange <= priceChangeLimit

`strategy.entry("Buy", strategy.long)` is placed whenever `entryCondition` is
true. There is no exit anywhere in the source: the position is opened once and
held to the end of the window. Because `pyramiding` is Pine's default 0, the
entry signals that keep arriving while the position is open are refused BY PINE
at order-creation time, so they are not fills that were missed -- they never
became orders. The engine models that (PineBroker._can_add / blocked_bar) and
projects no signal for them, so the framework sees one entry, not a stream.

The "52-week" window is 52 * 5 = 260 BARS, i.e. the source assumes a 5-day
trading week; it is not 52 calendar weeks of the chart's own timeframe.

The source declares a title and nothing else in `strategy()`, so Pine's
documented defaults apply: initial_capital 1000000 USD, default_qty_type
strategy.fixed, default_qty_value 1, commission 0%, pyramiding 0.

FIDELITY:
* `lowestLow = ta.lowest(close, length)` is computed by the source and never
  referenced again (its only would-be consumers are commented out). It is
  carried for completeness; it cannot change a trade.
* `priceChangeLimit` is chosen from `timeframe.isweekly or timeframe.ismonthly`.
  Pine resolves that against the CHART's timeframe, which the source fixes at
  `period: 1d` in its backtest header, so the branch taken is always the `else`
  -> 3. The port reproduces the branch from its own declared `timeframe` rather
  than hard-coding 3, so a re-filed copy on a weekly chart would still branch
  the way Pine would; at `timeframe = "1d"` the weekly/monthly arm is dead code
  and is never exercised here.
* `ta.highest` / `ta.lowest` return na until `length` bars have elapsed
  (pine_ta's documented model), so the first 259 bars cannot signal. That is the
  source's own warm-up: on the 2024 verification window (366 daily bars) only
  the last ~106 bars are tradeable, and on a truncated window it can leave the
  strategy with no signal at all. Not a port defect, but it does bound what the
  window can show.
* The source's `line.new` / `label.new` blocks are commented out and are visual
  only; nothing in the order stream depends on them.
* Pine's documented default initial capital is 100000 USD, but this harness's
  convention is 1000000 (the value the source's own account must have had to be
  reported in its units). It cannot change a trade here: sizing is fixed 1 and
  commission is 0%.
* The backtest header declares `basePeriod: 1d`, so there is no intrabar path to
  model: the engine evaluates at bar close and fills at the next bar's open,
  which is where Pine fills a `strategy.entry` market order.
"""
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase

# Pine's `timeframe.isweekly` / `timeframe.ismonthly` for the timeframe strings
# Freqtrade can hand a strategy. Case matters: "1M" is a month, "1m" a minute.
_WEEKLY_OR_MONTHLY = {"1w", "3w", "1M", "3M", "6M", "12M"}


class SM52WeekHighLow_2ace7b(PinePortBase, IStrategy):
    source_id = "SM_2ace7bb458896a8c"
    source_file = (
        "52周高低位-平均成交量-成交量突破策略-52-Week-High-Low-Average-Volume-"
        "Volume-Breakout-Strategy.md"
    )
    timeframe = "1d"
    can_short = False
    source_defaults: dict = {"percentFromHigh": 10, "volumeMultiplier": 1.5}
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    source_fidelity_notes = [
        "lowestLow = ta.lowest(close, 260) is computed by the source and never "
        "used (its only consumers are commented out); carried for completeness.",
        "priceChangeLimit is 10 only when timeframe.isweekly or "
        "timeframe.ismonthly. The source's header fixes the chart at 1d, so the "
        "else branch (3) is what runs; the port derives the branch from its own "
        "timeframe attribute, which makes the weekly/monthly arm dead code here.",
        "ta.highest/ta.lowest are na until `length` (260) bars elapse, so the "
        "first 259 bars carry no signal. On the 2024 window (366 bars) that "
        "leaves only ~106 tradeable bars.",
        "No exit exists in the source: the entry is placed once and held to the "
        "end of the window. Repeated entry signals while long are refused by "
        "Pine's pyramiding=0 at order creation, which the engine models, so they "
        "are not projected as signals.",
        "strategy() declares no initial_capital; 1000000 is the harness "
        "convention (Pine's reference documents 100000). It cannot change a "
        "trade: sizing is fixed 1 and commission is 0%.",
    ]

    def pine_indicators(self, dataframe, params):
        # weeks = 52, daysPerWeek = 5
        length = 52 * 5
        percent_from_high_limit = params["percentFromHigh"]
        volume_multiplier = params["volumeMultiplier"]
        average_volume_period = 50

        close = dataframe["close"]
        highest_high = ta.pine_highest(close, length)
        # Computed by the source; unused downstream (see fidelity notes).
        dataframe["pine_lowest_low"] = ta.pine_lowest(close, length)

        dataframe["pine_highest_high"] = highest_high
        dataframe["pine_percent_from_high"] = (
            100.0 * (highest_high - close) / highest_high
        )
        dataframe["pine_avg_volume"] = ta.pine_sma(
            dataframe["volume"], average_volume_period
        )
        volume_rise = (
            dataframe["volume"]
            > dataframe["pine_avg_volume"] * volume_multiplier
        )
        dataframe["pine_volume_rise"] = volume_rise
        dataframe["pine_daily_price_change"] = (
            100.0 * (close - dataframe["open"]) / dataframe["open"]
        )

        price_change_limit = (
            10.0 if self.timeframe in _WEEKLY_OR_MONTHLY else 3.0
        )
        dataframe["pine_price_change_limit"] = price_change_limit

        # Pine's na compares false, which is what the pandas comparisons below
        # already yield, so an un-warmed window produces no signal rather than a
        # signal on a missing value.
        dataframe["pine_entry_condition"] = (
            (dataframe["pine_percent_from_high"] <= percent_from_high_limit)
            & volume_rise
            & (dataframe["pine_daily_price_change"] <= price_change_limit)
        )
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "entry_condition": dataframe["pine_entry_condition"].to_numpy(),
        }

    def pine_script(self, broker, i, ctx):
        # if (entryCondition)
        #     strategy.entry("Buy", strategy.long)
        if ctx["entry_condition"][i]:
            broker.entry("Buy", "long")
