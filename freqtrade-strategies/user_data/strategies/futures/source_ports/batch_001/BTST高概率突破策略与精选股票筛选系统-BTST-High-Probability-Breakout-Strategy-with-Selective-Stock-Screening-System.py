"""Port of sources/SM_ba44acf0e3bffe0e.pine (batch_001/BTST高概率突破策略与精选股票筛选系统-BTST-High-Probability-Breakout-Strategy-with-Selective-Stock-Screening-System.md).

Pine v5. A stock-screening "buy tomorrow, sell tomorrow" (BTST) template whose
trading half is two statements:

    buySignal  = bullishPattern and isSelectedStock and not avoidOverExtendedStocks
    if buySignal
        strategy.entry("Buy", strategy.long)

    sellSignal = breakoutAboveResistance and not avoidOverExtendedStocks
    if sellSignal
        strategy.close("Buy")

with the supporting expressions exactly as written in the source:

    is3pm              = (hour == 15 and minute == 0)
    priceChangePct     = (close - close[1]) / close[1] * 100
    isSelectedStock    = is3pm and priceChangePct >= 2 and priceChangePct <= 3
    bullishEngulfing   = close > open and open[1] > close[1] and close > open[1]
                         and open < close[1]
    morningStar        = close[2] < open[2] and close[1] < open[1] and close > open
                         and close[1] > open[1]
    threeWhiteSoldiers = close > open and close[1] > open[1] and close[2] > open[2]
                         and close > close[1] and close[1] > close[2]
    bullishPattern     = bullishEngulfing or morningStar or threeWhiteSoldiers
    var float resistanceLevel = na
    if (minute == 30 or minute == 0)
        resistanceLevel := high
    breakoutAboveResistance = close > resistanceLevel
    percentageGain     = (close - open) / open * 100
    avoidOverExtended  = percentageGain > 5 or percentageGain < -10

`strategy("BTST Strategy", overlay=true)` declares ONLY title and overlay, so
`strategy.fixed` / 1 contract, initial capital 1000000, commission 0%,
pyramiding 0 and `process_orders_on_close=false` are Pine's documented defaults
rather than source-given values.

TWO STRUCTURAL FACTS OF THE SOURCE, reproduced rather than corrected:

1. `resistanceLevel` is assigned THIS BAR'S OWN `high` at line 38-39, before
   `breakoutAboveResistance = close > resistanceLevel` is evaluated at line 42.
   Pine executes statements in written order, so the comparison is always against
   the bar's own high -- and a bar's close is never above its own high. On a 1h
   series `minute` is 0 on every bar, so the assignment runs every bar and
   `breakoutAboveResistance` is FALSE on every bar of the whole history. The
   `sellSignal` therefore never fires: the source's only exit is dead, and a
   position opened by `buySignal` is held to the end of the window.
2. `avoidOverExtendedStocks` is also computed on the intraday move from the
   bar's own open, and `is3pm` selects a single bar per day, so `isSelectedStock`
   can hold on at most one bar per day (the 15:00 bar) and then only when the bar
   gained 2-3% versus the previous close.

The port keeps fact 1 in the order the source writes it, so the dead exit stays
dead. Implementing `resistanceLevel` as "the previous bar's high" would look
more like the source's comment ("Capture the highest point every 30 minutes")
and would produce a DIFFERENT, exiting strategy; the code is followed, not the
comment.

FIDELITY:

* `hour` / `minute` are Pine's bar-time builtins read in the EXCHANGE's
  timezone. The port reads them off the frame's UTC index, which is the same
  thing for the Binance/OKX futures data this corpus was extracted against
  (PINE_SEMANTICS.md 3.4).
* `var float resistanceLevel` is reproduced with the assignment-then-test order
  above, i.e. the ledger column already carries this bar's assignment when
  `breakoutAboveResistance` is computed -- not a one-bar lagged snapshot.
* `watchlistCondition`, `gapUpOpening` and `hold15Min` are computed by the
  source and never read by it; they place no condition and are reproduced as
  ledger columns rather than deleted.
* `alertcondition(...)` is notification-only and places no order
  (PINE_SEMANTICS.md 二.7).
* Long only: the source never calls `strategy.entry` with `strategy.short`, so
  `can_short` is False.
* No stop, limit or trailing exit exists and the one close condition is
  unreachable (fact 1), so `source_reproduce_stops` is False.
* `plotshape` and its colour/text arguments are display-only.
* The source is written for equities ("stocks", pre-market, watchlists) but is
  backtested here on the crypto futures pair named in its own header; only the
  trading conditions above are reproduced, and the equity-market prose in the md
  places no condition.
* The `/*backtest` header declares `period: 1h` on Futures_Binance ETH_USDT, so
  `timeframe` is "1h"; its `basePeriod: 1h` is the FMZ backtester's filling
  granularity.
* Leverage, margin, liquidation, funding and the venue's contract-step rounding
  are not modelled.
"""
import numpy as np
import pandas as pd
from freqtrade.strategy import IStrategy

from pine_port_base import PinePortBase


class SMBtstHighProbabilityBreakout_ba44ac(PinePortBase, IStrategy):
    source_id = "SM_ba44acf0e3bffe0e"
    source_file = (
        "BTST高概率突破策略与精选股票筛选系统-BTST-High-Probability-Breakout-Strategy-"
        "with-Selective-Stock-Screening-System.md"
    )
    timeframe = "1h"
    can_short = False
    # The source has no input() at all: every parameter is a literal.
    source_defaults: dict = {}
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    source_reproduce_stops = False
    source_fidelity_notes = [
        "`strategy()` declares only title and overlay, so fixed/1 contract, "
        "initial capital 1000000, commission 0% and pyramiding 0 are Pine's "
        "documented defaults rather than values the source states.",
        "resistanceLevel is assigned this bar's OWN high before "
        "`breakoutAboveResistance = close > resistanceLevel` is evaluated, in "
        "the source's statement order. A bar's close is never above its own "
        "high, and on a 1h series `minute == 0` makes the assignment run every "
        "bar, so breakoutAboveResistance -- and therefore the sellSignal and the "
        "only exit -- is false on every bar. Reproduced as written; reading "
        "resistanceLevel as a one-bar-lagged high would be a different strategy.",
        "Long only: the source never calls `strategy.entry` with "
        "`strategy.short`, so can_short is False.",
        "`hour` / `minute` are read off the frame's UTC index; Pine reads them "
        "in the exchange timezone, which is UTC for the Binance/OKX futures data "
        "used here (PINE_SEMANTICS.md 3.4).",
        "watchlistCondition, gapUpOpening and hold15Min are computed by the "
        "source and never read; they are kept as ledger columns.",
        "alertcondition is notification-only (PINE_SEMANTICS.md section 二.7).",
        "No stop / limit / trail exit exists and the single close condition is "
        "unreachable, so source_reproduce_stops is False.",
        "The source targets equities (pre-market data, watchlists, an exchange-"
        "time screening hour); only its trading conditions are reproduced, on "
        "the futures pair its own header names.",
        "The header's `basePeriod: 1h` is the FMZ backtester's filling "
        "granularity; `period: 1h` is the strategy's period.",
        "Leverage, margin, liquidation, funding and venue contract-step rounding "
        "are not modelled.",
    ]

    def pine_indicators(self, dataframe, params):
        index = dataframe.index
        open_ = dataframe["open"]
        high = dataframe["high"]
        low = dataframe["low"]
        close = dataframe["close"]

        # Pine's `hour` / `minute` bar-time builtins, off the candle time.
        minutes = pd.Series(index.minute, index=index)
        hours = pd.Series(index.hour, index=index)

        # is3pm = (hour == 15 and minute == 0)
        is3pm = (hours == 15) & (minutes == 0)
        # priceChangePercentage = (close - close[1]) / close[1] * 100
        price_change_percentage = (close - close.shift(1)) / close.shift(1) * 100.0
        is_selected_stock = is3pm & (price_change_percentage >= 2) & (
            price_change_percentage <= 3
        )

        bullish_engulfing = (
            (close > open_)
            & (open_.shift(1) > close.shift(1))
            & (close > open_.shift(1))
            & (open_ < close.shift(1))
        )
        morning_star = (
            (close.shift(2) < open_.shift(2))
            & (close.shift(1) < open_.shift(1))
            & (close > open_)
            & (close.shift(1) > open_.shift(1))
        )
        three_white_soldiers = (
            (close > open_)
            & (close.shift(1) > open_.shift(1))
            & (close.shift(2) > open_.shift(2))
            & (close > close.shift(1))
            & (close.shift(1) > close.shift(2))
        )
        bullish_pattern = bullish_engulfing | morning_star | three_white_soldiers

        # var float resistanceLevel = na
        # if (minute == 30 or minute == 0)
        #     resistanceLevel := high
        # The assignment precedes the comparison in the source, so the level
        # tested against is the one set on THIS bar when the guard holds, and the
        # last set value otherwise.
        assign = (minutes == 30) | (minutes == 0)
        resistance_level = high.where(assign).ffill()
        breakout_above_resistance = (close > resistance_level).fillna(False)

        percentage_gain = (close - open_) / open_ * 100.0
        avoid_over_extended_stocks = (percentage_gain > 5) | (percentage_gain < -10)

        # Computed by the source, never read by it.
        watchlist_condition = (
            is_selected_stock & bullish_pattern & ~avoid_over_extended_stocks
        )
        gap_up_opening = open_ > close.shift(1) * 1.02
        hold15_min = gap_up_opening & (close > low.shift(1))

        dataframe["pine_is3pm"] = is3pm
        dataframe["pine_price_change_percentage"] = price_change_percentage
        dataframe["pine_is_selected_stock"] = is_selected_stock
        dataframe["pine_bullish_pattern"] = bullish_pattern
        dataframe["pine_resistance_level"] = resistance_level
        dataframe["pine_breakout_above_resistance"] = breakout_above_resistance
        dataframe["pine_percentage_gain"] = percentage_gain
        dataframe["pine_avoid_over_extended_stocks"] = avoid_over_extended_stocks
        dataframe["pine_watchlist_condition"] = watchlist_condition
        dataframe["pine_gap_up_opening"] = gap_up_opening
        dataframe["pine_hold15min"] = hold15_min
        dataframe["pine_buy_signal"] = (
            bullish_pattern & is_selected_stock & ~avoid_over_extended_stocks
        )
        dataframe["pine_sell_signal"] = (
            breakout_above_resistance & ~avoid_over_extended_stocks
        )
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "buy_signal": dataframe["pine_buy_signal"].to_numpy(),
            "sell_signal": dataframe["pine_sell_signal"].to_numpy(),
        }

    def pine_script(self, broker, i, ctx):
        # if buySignal
        #     strategy.entry("Buy", strategy.long)
        if bool(ctx["buy_signal"][i]):
            broker.entry("Buy", "long")
        # if sellSignal
        #     strategy.close("Buy")
        if bool(ctx["sell_signal"][i]):
            broker.close("Buy")
