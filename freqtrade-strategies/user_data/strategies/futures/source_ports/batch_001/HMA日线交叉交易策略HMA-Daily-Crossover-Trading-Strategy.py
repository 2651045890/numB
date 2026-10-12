"""Port of sources/SM_a29d85adb0c8b732.pine
(batch_001/HMA日线交叉交易策略HMA-Daily-Crossover-Trading-Strategy.md).

Pine v4 (`//@version=4`). A Hull moving average on `price` (default `open`) and
a daily series requested with `security()` drive two raw orders, and a dollar
threshold on `strategy.openprofit` closes everything:

    SL = input(defval=-0.05, ...)      TP = input(defval=0.05, ...)
    price  = input(type=input.source, defval=open)
    Period = input(14, minval=1)
    hma = wma(2*wma(price, Period/2) - wma(price, Period), round(sqrt(Period)))
    s1  = security(syminfo.tickerid, timeframe.period, price, gaps_off, lookahead_off)
    s2  = security(syminfo.tickerid, "D", price, gaps_off, lookahead_off)

    closeall = strategy.openprofit < SL or strategy.openprofit > TP
    if closeall
        strategy.close_all(comment = "Close All")
    if (hma>hma[1] and s1>s2 and s2[1]>s2[2] and s1>s2[1])
        strategy.order("Buy", strategy.long)
    if (hma<hma[1] and s1<s2 and s2[1]<s2[2] and s1<s2[1])
        strategy.order("Sell", strategy.short)

TWO THINGS ABOUT THIS FILE ARE NOT WHAT ITS TIER CLAIMS.

1. It is NOT a converter-appended order block. The file declares no
   `indicator()` and no `study()` at all, and there is no appended
   `? -1 : 0` / `strategy.entry` template pair. Its only `strategy(...)` line
   (source line 11) is COMMENTED OUT, and the two `strategy.order` calls plus
   the `strategy.close_all` are the author's own active code carrying
   `strategy.openprofit` logic and a title comment naming the author. The
   tier_reason's "declares indicator()/study(), tool appended strategy.entry
   pair; NO exits" is false on all three counts -- this source DOES have an
   exit (the close_all). Rule 2: the source is followed.

2. `strategy()` IS COMMENTED OUT, so it declares nothing -- the same rule
   PINE_SEMANTICS.md 1.17 applies to commented-out exit lines. Pine's
   documented defaults are therefore in force: `strategy.fixed` / 1 contract,
   initial capital 1000000, commission 0%, `pyramiding = 0`,
   `process_orders_on_close = false`. What the commented line asks for is
   recorded in `source_fidelity_notes` and NOT applied; it would change the
   strategy out of recognition (see note 3 there -- `currency="BTC"` would
   re-denominate `strategy.openprofit`, which is the threshold variable).

`SL` / `TP` ARE NOT PRICE LEVELS. They are compared against
`strategy.openprofit`, whose unit is the account currency, and the inputs'
own titles say so ("StopLoss $", "TargetPoint $"). With the declared
-0.05 / +0.05 they are FIVE CENTS of open profit, so on a 1-contract BTC
position the close_all arm is live on essentially every bar a position is
held: the position is opened on one bar's open and closed on the next bar's
open. The md's prose ("set fixed stop-loss/take-profit points; close when the
price TOUCHES them") describes price levels and is a mis-description of the
source; see the mismatch notes in `source_fidelity_notes`.

`s2` DEPENDS ON `request.security()` MULTI-TIMEFRAME DATA, which
PINE_SEMANTICS.md section 2.1 records as NOT modelled by the engine (it does
not resample). That section's remedy -- "or the port supplies the aligned
series itself" -- is what `_previous_completed_day` does, under the
documented `lookahead_off` rule and a UTC calendar day. The rule is stated in
that helper's docstring and in the fidelity notes, and it is a MODELLED
CHOICE, not a certified equivalence: get the merge rule wrong and the entry
bar moves.

FIDELITY:

* `wma` is pine_ta.pine_wma (weights 1..length, heaviest newest). `Period/2`
  is INTEGER division, which is what Pine v4 does with two integer operands,
  so the declared 14 gives 7; `round(sqrt(Period))` gives 4. Both lengths are
  derived from the input rather than hard-coded.
* `price` is resolved through pine_ta.pine_source so a non-default
  `input.source` works; the declared default is `open`.
* `strategy.order("Buy", strategy.long)` is a MARKET order with no `stop=` /
  `limit=`, so it is projected as a next-open market entry exactly as the
  engine fills it. `broker.order` is used (not `broker.entry`) because that is
  the source's call; the engine maps the two onto the same order type, which
  is a public-layer choice recorded in the notes rather than worked around.
* The close_all is placed BEFORE the two orders, and the two orders are
  separate `if`s (not an `else if`), so all three can be placed on one bar.
  That source order is the fill-priority order and is preserved verbatim.
* `source_reproduce_stops` is False: there is no `strategy.exit`, no `stop=`,
  `limit=`, `profit=` or `loss=` anywhere in the file for the engine to
  mirror. The only exit is a market `close_all`.
* No future-data pattern is present: both `security()` calls carry
  `barmerge.lookahead_off` explicitly, so nothing here repaints.
* Leverage, margin, liquidation, funding and the venue's contract-step
  rounding are not modelled (PINE_SEMANTICS.md section 2 and 1.6).
"""
import math

import pandas as pd

from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


def _previous_completed_day(price: pd.Series) -> pd.Series:
    """`request.security(syminfo.tickerid, "D", price, gaps_off, lookahead_off)`.

    PINE_SEMANTICS.md section 2.1 records that the engine does not resample and
    that a port which depends on `request.security()` must either flag it or
    supply the aligned series itself. This supplies it, under the rule
    `barmerge.lookahead_off` documents:

    * the daily bar of a calendar day holds `price` at that day's FIRST bar
      (for this source `price` is `open`, so that is the daily open);
    * at intraday bar `t` the request returns the value of the most recently
      COMPLETED daily bar -- the day before the one `t` sits in. The current
      day's daily bar is still forming and `lookahead_off` forbids reading it,
      which is exactly why an intraday request for "D" lags by one day;
    * `barmerge.gaps_off` carries the value across days with no data, which the
      reindex does by leaving a missing day NaN only where the whole day is
      absent from the frame.

    Calendar days are UTC. PINE_SEMANTICS.md 3.4 records that the port layer
    defaults to UTC, which is the timezone of the local OKX/Binance history
    this repo backtests against; a venue whose daily bars start elsewhere would
    move the boundary and therefore the bars on which `s2` steps.

    This is a MODELLED CHOICE, not a certified equivalence. `s2` is a step
    function that changes once per day, so the source's `s2[1] > s2[2]` test
    (indexed by BAR, as Pine indexes it) can only hold on the bar right after a
    step -- see the fidelity notes.
    """
    index = pd.DatetimeIndex(price.index)
    day = index.normalize()
    daily = price.groupby(day).first()
    return pd.Series(
        daily.shift(1).reindex(day).to_numpy(dtype=float), index=price.index
    )


class SMHmaDailyCrossover_a29d85(PinePortBase, IStrategy):
    source_id = "SM_a29d85adb0c8b732"
    source_file = "HMA日线交叉交易策略HMA-Daily-Crossover-Trading-Strategy.md"
    timeframe = "1h"
    # The source holds strategy.order("Sell", strategy.short) as well as the
    # long one, so the port can hold a short.
    can_short = True
    source_defaults: dict = {
        # SL = input(defval=-0.05, title="StopLoss $", type=input.float, step=0.01, maxval=-0.01)
        "SL": -0.05,
        # TP = input(defval=0.05, title="TargetPoint $", type=input.float, step=0.01, minval=0.01)
        "TP": 0.05,
        # price = input(title="Source", type=input.source, defval=open)
        "price": "open",
        # Period = input(14, minval=1)
        "Period": 14,
    }
    # The ONLY strategy() declaration in the file (line 11) is commented out, so
    # it declares nothing and Pine's documented defaults apply. The commented
    # line asks for currency="BTC", initial_capital=1,
    # default_qty_type=strategy.percent_of_equity with default_qty_value=1 and
    # commission_value=0.25; none of that is in force (see note 3).
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    # No strategy.exit / stop= / limit= / profit= / loss= leg exists anywhere in
    # the file; the only exit is a market strategy.close_all.
    source_reproduce_stops = False
    source_fidelity_notes = [
        "NOT a converter-appended order block, despite its tier_reason. The "
        "file declares no indicator() and no study(), its only strategy() line "
        "(line 11) is COMMENTED OUT, and the two strategy.order calls plus "
        "strategy.close_all are the author's own active code (the header "
        "comment names the author and describes the intent). The tier_reason's "
        "'declares indicator()/study(), tool appended strategy.entry pair; NO "
        "exits' is false on all three counts: this source DOES have an exit. "
        "The source is followed.",
        "THE EXIT IS A DOLLAR THRESHOLD, NOT A PRICE LEVEL. "
        "closeall = strategy.openprofit < SL or strategy.openprofit > TP, with "
        "SL = -0.05 and TP = +0.05 and the inputs titled 'StopLoss $' / "
        "'TargetPoint $'. strategy.openprofit is denominated in the account "
        "currency (Pine's default currency.NONE = the instrument's quote "
        "currency here, since the currency= argument is inside the commented "
        "line), so the two arms are FIVE CENTS of open profit. On the "
        "1-contract position the defaults size, any bar whose close differs "
        "from the entry by more than $0.05 -- i.e. essentially every bar -- "
        "places the close_all, and the trade is closed at the next bar's open. "
        "The md's prose ('设置固定止损止盈点,当价格触及止损或止盈价格则平仓' / "
        "'close positions when the price touches the stop or take-profit') "
        "describes price levels; the source tests open PROFIT IN CURRENCY. The "
        "source is followed, the md is not.",
        "The file's only strategy() declaration is COMMENTED OUT (line 11), so "
        "Pine's documented defaults are in force: default_qty_type fixed / 1 "
        "contract, initial_capital 1000000, commission 0%, pyramiding 0, "
        "process_orders_on_close false. RECORDED BUT NOT APPLIED, the commented "
        "line asks for currency='BTC', initial_capital=1, "
        "default_qty_type=strategy.percent_of_equity with default_qty_value=1 "
        "and commission_type=percent / commission_value=0.25. Three of those "
        "are load-bearing: currency='BTC' would re-denominate "
        "strategy.openprofit (the threshold variable) into BTC, making the "
        "0.05 threshold two orders of magnitude different in dollar terms; "
        "initial_capital=1 with 1% of equity sizes a stake of 0.01 USDT, which "
        "is below the venue's minimum order and would be vetoed by the "
        "framework on every entry (PINE_SEMANTICS.md 1.5.1); and the 0.25% "
        "commission changes every trade's net. The declared state is Pine's "
        "default, and the fork is recorded rather than quietly resolved.",
        "request.security() MULTI-TIMEFRAME IS NOT MODELLED (PINE_SEMANTICS.md "
        "section 2.1). s2 = security(syminfo.tickerid, 'D', price, gaps_off, "
        "lookahead_off) is supplied by the port as an explicitly aligned series "
        "(_previous_completed_day) rather than left as a hole, which is the "
        "remedy section 2.1 offers. The rule used is the documented "
        "lookahead_off one: a bar sees the value of the most recently COMPLETED "
        "daily bar, i.e. the day BEFORE the intraday bar's own day, with the "
        "daily bar's value taken at its first bar ('price' is the source's "
        "input.source, default open). Days are UTC (PINE_SEMANTICS.md 3.4). "
        "UNVERIFIED against the original platform, and load-bearing: it decides "
        "which bars can carry a signal at all.",
        "CONSEQUENCE OF THE s2 MODEL, worth stating because it looks surprising. "
        "s2 is a step function: it holds one value for a whole calendar day and "
        "changes at the day's first bar. Pine's s2[1] / s2[2] index that merged "
        "series BY BAR, so s2[1] > s2[2] can hold only on the bar immediately "
        "after a step -- that is, on the SECOND bar of a day (01:00 on 1h bars) "
        "-- and only when the previous day's value exceeded the one before it. "
        "On every other bar of the day the two terms are equal and the test is "
        "False. So this strategy can only enter at that one bar per day; the "
        "engine reproduces exactly that, because it shifts the merged series by "
        "bars exactly as Pine does.",
        "s1 = security(syminfo.tickerid, timeframe.period, price, gaps_off, "
        "lookahead_off) requests the chart's OWN timeframe and is modelled as "
        "the identity on price (the current bar's value). That is the observed "
        "behaviour of a same-timeframe request.security -- with no higher "
        "timeframe there is no unfinished bar to wait for -- but it is a "
        "MODELLED CHOICE: if the original platform instead returned the last "
        "CLOSED bar of the same timeframe (price[1]), the two conditions that "
        "read s1 would be one bar behind and the entry bar would move. Not "
        "verified against the platform.",
        "MD/SOURCE MISMATCH (entry rule): the md says the long signal is 'HMA "
        "crossing above the previous daily close, with price higher than the "
        "previous day's price'. The source compares hma against its OWN "
        "previous value (hma[1]) -- not a cross with s2 -- and separately "
        "requires price above BOTH s2 and s2[1]. No cross of hma with the "
        "daily series exists in the code. The source is followed.",
        "MD/SOURCE MISMATCH (exit rule): see note 2 -- the md's 'fixed "
        "stop-loss/take-profit price levels' is a dollar threshold on "
        "strategy.openprofit.",
        "MD/SOURCE MISMATCH (arguments): the md's table renders v_input_3 with "
        "the value 0 ('v_input_3_open|0|Source'). The source's input.source "
        "default is the built-in `open`, which is what source_defaults carries. "
        "The md's other three defaults (-0.05, 0.05, 14) agree with the source.",
        "MD/SOURCE MISMATCH (optimisation prose): the md lists 'use a trailing "
        "stop', 'add trend-strength filters' and 'dynamic stops instead of "
        "fixed levels' under 策略优化方向 / Improvements. None of that is in the "
        "source; it is the md author's suggestion list, not code, and nothing "
        "from it is implemented here.",
        "strategy.order vs strategy.entry: the source uses strategy.order, "
        "which reaches the engine as the same order type as strategy.entry "
        "(pine_engine.PineBroker.order delegates to entry), so the engine's "
        "creation-time pyramiding gate applies to it. Whether Pine's "
        "strategy.order is subject to the pyramiding limit the same way "
        "strategy.entry is has NOT been verified; the public layer models them "
        "as one, and that model is used rather than worked around.",
        "The entry conditions are two independent `if`s, not an if/else if, and "
        "the close_all precedes them. All three can therefore be placed on one "
        "bar, and the engine fills them in that (source) order on the next bar. "
        "When a long is already open, closeall fires and the same bar's Buy is "
        "blocked by the pyramiding gate at creation, so the position closes and "
        "is not re-opened; the Sell arm can still fire and reverse.",
        "ta.wma returns na until its window is full and propagates na "
        "(PINE_SEMANTICS.md 3.2), so hma is na for the first Period-1 bars and "
        "no signal can be produced there. 2*wma(price, Period/2) - wma(price, "
        "Period) is transcribed literally; the intermediate is not simplified.",
        "Period/2 is INTEGER division because Pine v4 divides two integers as "
        "integers; the declared 14 gives 7, and an odd Period would truncate. "
        "round(sqrt(Period)) is pine_ta.pine_round (half away from zero), which "
        "gives 4 for 14. Neither length is hard-coded.",
        "The /*backtest header declares `period: 1h` on Futures_Binance "
        "BTC_USDT, hence timeframe = '1h'; its basePeriod: 15m is the FMZ "
        "backtester's own intrabar fill granularity, not the strategy period. "
        "The header's start/end window is the recorded run's window, not a "
        "source property, and is not applied (PINE_SEMANTICS.md section 2.8).",
        "plot() / fill() calls, and the `cp` colour ternary, are display-only "
        "and are not reproduced.",
        "Leverage, margin, liquidation, funding and the venue's contract-step "
        "rounding are not modelled; the chain verifier measures the step "
        "rounding separately (PINE_SEMANTICS.md 1.6) instead of treating it as "
        "a signal difference.",
    ]

    def pine_indicators(self, dataframe: pd.DataFrame, params: dict) -> pd.DataFrame:
        period = int(params["Period"])
        # price = input(type=input.source, defval=open) -- resolved through
        # pine_ta.pine_source so a non-default source name works.
        price = ta.pine_source(dataframe, str(params["price"]))

        # hma = wma(2*wma(price, Period/2) - wma(price, Period), round(sqrt(Period)))
        # Period/2 is Pine v4 integer division (7 for the declared 14);
        # round(sqrt(14)) = 4.
        half = period // 2
        root = int(ta.pine_round(math.sqrt(period)))
        hma = ta.pine_wma(
            2.0 * ta.pine_wma(price, half) - ta.pine_wma(price, period), root
        )

        # s1 = security(syminfo.tickerid, timeframe.period, price, gaps_off, lookahead_off)
        s1 = price
        # s2 = security(syminfo.tickerid, "D", price, gaps_off, lookahead_off)
        s2 = _previous_completed_day(price)

        dataframe["pine_hma"] = hma
        dataframe["pine_s1"] = s1
        dataframe["pine_s2"] = s2

        # if (hma>hma[1] and s1>s2 and s2[1]>s2[2] and s1>s2[1])
        #     strategy.order("Buy", strategy.long)
        dataframe["pine_long_condition"] = (
            (hma > hma.shift(1))
            & (s1 > s2)
            & (s2.shift(1) > s2.shift(2))
            & (s1 > s2.shift(1))
        ).fillna(False)
        # if (hma<hma[1] and s1<s2 and s2[1]<s2[2] and s1<s2[1])
        #     strategy.order("Sell", strategy.short)
        dataframe["pine_short_condition"] = (
            (hma < hma.shift(1))
            & (s1 < s2)
            & (s2.shift(1) < s2.shift(2))
            & (s1 < s2.shift(1))
        ).fillna(False)
        return dataframe

    def pine_context(self, dataframe: pd.DataFrame, params: dict) -> dict:
        return {
            "long_condition": dataframe["pine_long_condition"].to_numpy(dtype=bool),
            "short_condition": dataframe["pine_short_condition"].to_numpy(dtype=bool),
            # SL / TP are compared against strategy.openprofit, in the account
            # currency -- NOT against price.
            "SL": float(params["SL"]),
            "TP": float(params["TP"]),
        }

    def pine_script(self, broker, i: int, ctx: dict) -> None:
        # closeall = strategy.openprofit < SL or strategy.openprofit > TP
        # if closeall
        #     strategy.close_all(comment = "Close All")
        # (first in source order; broker.open_profit is the same quantity the
        # engine marks to market at this bar's close, before the script runs)
        if broker.open_profit < ctx["SL"] or broker.open_profit > ctx["TP"]:
            broker.close_all()
        # if (hma>hma[1] and s1>s2 and s2[1]>s2[2] and s1>s2[1])
        #     strategy.order("Buy", strategy.long)
        if ctx["long_condition"][i]:
            broker.order("Buy", "long")
        # if (hma<hma[1] and s1<s2 and s2[1]<s2[2] and s1<s2[1])
        #     strategy.order("Sell", strategy.short)
        if ctx["short_condition"][i]:
            broker.order("Sell", "short")
