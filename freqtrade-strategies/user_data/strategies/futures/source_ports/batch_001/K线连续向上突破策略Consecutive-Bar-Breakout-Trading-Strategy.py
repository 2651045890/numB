"""Port of sources/SM_85269b628e379dd3.pine
(batch_001/K线连续向上突破策略Consecutive-Bar-Breakout-Trading-Strategy.md).

Pine v4 (`//@version=4`). One bullish-bar test and one bearish-bar test, each
arming a RESTING `stop=` entry:

    BarsUp = input(1)      BarsDown = input(1)
    time_cond = true

    if (close > open and open > close[BarsUp]) and time_cond
        strategy.entry("BarUp", strategy.long,  stop = high + syminfo.mintick, ...)
    if (close < open and open < close[BarsDown]) and time_cond
        strategy.entry("BarDn", strategy.short, stop = low  + syminfo.mintick, ...)

There is NO exit of any kind -- no `strategy.exit`, no `strategy.close`, no
`strategy.close_all`, and nothing commented out that could have been one -- so
the position changes only when the next entry nets against it (PINE_SEMANTICS.md
1.1). `source_reproduce_stops` is False because there is no stop/limit/trail
EXIT leg for the engine to mirror; the `stop=` arguments here are on the ENTRY
side and are forwarded to `broker.entry` verbatim.

BOTH ENTRIES ARE RESTING STOP ORDERS, NOT MARKET ORDERS. The long rests at
`high + mintick` (a buy-stop above the signal bar's own high) and the short at
`low + mintick` (a sell-stop at the signal bar's own low), and each fills on a
LATER bar -- at the stop price, or at the open when the bar gaps through it --
not at the next bar's open. PINE_SEMANTICS.md section 2.11 records that such an
entry cannot be projected onto a framework whose only entry is a next-open
market order: the projection can only emit `enter_long` / `enter_short` on the
bar the order was CREATED, and Freqtrade then fills at the next open. The
engine's own ledger fills them at the right bar and the right price; the
projected signal columns are structurally not equivalent.

THIS FILE IS NOT A CONVERTER-APPENDED ORDER BLOCK, despite its tier_reason.
It declares no `indicator()` and no `study()`; its only `strategy(...)` line
(source line 10) is COMMENTED OUT; and the two `strategy.entry` calls are the
author's own active code, carrying an `alert_message=` argument and a `stop=`
level -- nothing a converter template appends. The tier_reason's "declares
indicator()/study(), tool appended strategy.entry pair; NO exits" is false on
the first two counts (the "NO exits" part is true). Rule 2: the source is
followed.

`strategy()` IS COMMENTED OUT, so it declares nothing and Pine's documented
defaults are in force: `strategy.fixed` / 1 contract, initial capital 1000000,
commission 0%, `pyramiding = 0`, `process_orders_on_close = false`. The
commented line asks for something else (initial_capital = 10000, all-in cash
sizing) and that is recorded in the notes rather than applied -- the same rule
PINE_SEMANTICS.md 1.17 applies to commented-out exit lines.

FIDELITY:

* `close[BarsUp]` / `close[BarsDown]` are history references driven by the
  inputs (default 1), not hard-coded shifts.
* `time_cond` is a bare literal `true` (source line 19). The `startDate` /
  `finishDate` `input.time` values above it are read by NOTHING, so there is no
  date window. The conjunct is carried as the constant `True` rather than
  dropped, and both timestamps stay in `source_defaults` so the inputs are not
  silently lost.
* `syminfo.mintick` is a venue property, not a source constant; TradingView
  reads it off the symbol, so it is carried as `source_mintick` (0.1 for
  BTC/USDT:USDT) and added to the level at signal time.
* `alert_message=` and the two message inputs are trading-irrelevant
  (PINE_SEMANTICS.md section 2.7) and are not forwarded to the engine; the
  inputs are kept for provenance.
* The two conditions are independent `if`s in source order (long first), not
  an `else if`; the engine fills pending orders in creation order.
* Leverage, margin, liquidation, funding and the venue's contract-step
  rounding are not modelled (PINE_SEMANTICS.md section 2 and 1.6).
"""
import pandas as pd

from freqtrade.strategy import IStrategy

from pine_port_base import PinePortBase


class SMConsecutiveBarBreakout_85269b(PinePortBase, IStrategy):
    source_id = "SM_85269b628e379dd3"
    source_file = "K线连续向上突破策略Consecutive-Bar-Breakout-Trading-Strategy.md"
    timeframe = "3h"
    # The source's active code holds strategy.entry("BarDn", strategy.short, ...)
    # in addition to the long one, so the port can hold a short.
    can_short = True
    source_defaults: dict = {
        # BarsUp = input(1)   -- integer input (the md renders it `true`)
        "BarsUp": 1,
        # BarsDown = input(1)
        "BarsDown": 1,
        # startDate = input(timestamp("2021-01-01T00:00:00"), type=input.time)
        # READ BY NOTHING: `time_cond` is the bare literal `true` (line 19), so
        # there is no date window and every bar is eligible. Kept so the input
        # is not silently dropped.
        "startDate": "2021-01-01T00:00:00",
        # finishDate = input(timestamp("2021-12-31T00:00:00"), type=input.time)
        "finishDate": "2021-12-31T00:00:00",
        # message_buy = input("{{strategy.order.alert_message}}", title="Buy message")
        "message_buy": "{{strategy.order.alert_message}}",
        # message_sell = input("{{strategy.order.alert_message}}", title="Sell message")
        "message_sell": "{{strategy.order.alert_message}}",
    }
    # The ONLY strategy() declaration in the file (line 10) is commented out, so
    # it declares nothing: Pine's documented defaults apply. The commented line
    # asks for initial_capital = 10000, default_qty_type = strategy.cash and
    # default_qty_value = 10000; none of that is in force.
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    # No EXIT call of any kind exists in the source -- no stop, limit or trail
    # leg for the engine to mirror, and no market close either.
    source_reproduce_stops = False
    source_fidelity_notes = [
        "NO EXITS AT ALL. The source is two strategy.entry calls and nothing "
        "else: no strategy.exit, no strategy.close, no strategy.close_all, and "
        "no commented-out exit line either. The only way the position ever "
        "changes is the next entry netting against it (PINE_SEMANTICS.md 1.1). "
        "source_reproduce_stops is False because there is no stop/limit/trail "
        "EXIT leg to mirror; the two `stop=` arguments are on the ENTRY side "
        "and are forwarded to broker.entry verbatim.",
        "NOT a converter-appended order block, despite its tier_reason. The "
        "file declares no indicator() and no study(), its only strategy() line "
        "(line 10) is COMMENTED OUT, and the two strategy.entry calls are the "
        "author's own active code carrying an alert_message= argument and a "
        "stop= level -- nothing a converter template appends. The "
        "tier_reason's 'declares indicator()/study(), tool appended "
        "strategy.entry pair; NO exits' is false on the first two counts (the "
        "NO exits part is true). The source is followed.",
        "The file's only strategy() declaration is COMMENTED OUT (line 10), so "
        "Pine's documented defaults are in force: default_qty_type fixed / 1 "
        "contract, initial_capital 1000000, commission 0%, pyramiding 0, "
        "process_orders_on_close false. RECORDED BUT NOT APPLIED: the commented "
        "line asks for initial_capital = 10000, default_qty_type = "
        "strategy.cash with default_qty_value = 10000 -- an all-in stake of "
        "10000 cash per entry on a 10000 account, a completely different sizing "
        "rule from 1 contract. PINE_SEMANTICS.md 1.6 makes initial_capital "
        "load-bearing (it decides how much the venue's contract step eats), so "
        "the fork is recorded rather than quietly resolved.",
        "BOTH ENTRIES ARE RESTING STOP ORDERS, not market orders. The long "
        "rests at high + mintick (a buy-stop ABOVE the signal bar's own high) "
        "and the short at low + mintick (a sell-stop AT the signal bar's own "
        "low); each fills on a LATER bar at the stop price, or at the open when "
        "the bar gaps through it. PINE_SEMANTICS.md section 2.11 records that "
        "such an entry cannot be projected onto the framework: the projection "
        "can only emit enter_long / enter_short on the bar the order was "
        "CREATED, and Freqtrade then fills at the next open. The engine's "
        "ledger is faithful; the projected signal columns are not, "
        "structurally. This is a framework boundary, not a translation gap.",
        "PINE_SEMANTICS.md 1.12 records, as a still-open public-layer "
        "uncertainty, that _place replaces only kind == 'exit' orders on a "
        "same-id re-issue, so stop/limit ENTRY orders ACCUMULATE instead of "
        "being replaced (Pine keeps one order per id). This source re-issues "
        "the same two ids ('BarUp' / 'BarDn') on every signal bar, so the "
        "engine can carry several resting BarUp orders at once while Pine would "
        "hold at most one. The note's measured example "
        "(SM20LevelBreakout_113b6a) is exactly this shape. No module is "
        "changed here (rule 9): the behaviour is recorded and left as it is.",
        "MD/SOURCE MISMATCH (stops): the md says '设置止损线,避免亏损扩大' / 'Use "
        "stops to limit loss'. The source's `stop=` is on the ENTRY -- a "
        "breakout stop above the high (long) or at the low (short) -- not a "
        "protective loss stop on an open position. The source has no protective "
        "exit at all.",
        "MD/SOURCE MISMATCH (lookback): the md's 策略原理 says the comparison "
        "is 'K线与固定周期前的K线比较,如5周期前' / 'bars from fixed lookback, "
        "e.g. 5 bars ago'. The source's declared defaults are BarsUp = 1 and "
        "BarsDown = 1, i.e. one bar, and the inputs are forwarded so a different "
        "lookback can be set; 1 is what is carried.",
        "MD/SOURCE MISMATCH (rendered defaults): the md's argument table renders "
        "v_input_1 and v_input_2 (the two `input(1)` calls) as `true`. An "
        "integer literal in Pine v4 makes an integer input, so the declared "
        "defaults are the integers 1 and 1 as carried here; the difference is "
        "invisible at runtime because `open > close[1]` and `open > close[true]` "
        "agree, but the declared types differ.",
        "MD/SOURCE MISMATCH (backtest window): the md lists startDate / "
        "finishDate under '可自定义历史回测周期,优化参数' / 'Customizable backtest "
        "period'. Both inputs exist, but `time_cond = true` is a bare literal "
        "(line 19) and neither timestamp is read anywhere, so nothing is "
        "filtered by date. PINE_SEMANTICS.md section 2.8 records that input.time "
        "windows are not applied by this layer; here it does not matter, "
        "because the source never applies it either. Both inputs are still "
        "carried in source_defaults.",
        "syminfo.mintick is a venue property, not a source constant; "
        "TradingView reads it off the symbol. BTC/USDT:USDT quotes in 0.1, so "
        "source_mintick = 0.1 and the two levels are high + 0.1 and low + 0.1. "
        "A different mintick would move both levels.",
        "alert_message = message_buy / message_sell, and the two "
        "alert-message string inputs themselves, are trading-irrelevant "
        "(PINE_SEMANTICS.md section 2.7) and are not forwarded to the engine; "
        "they are carried in source_defaults for provenance only.",
        "The two entries are independent `if`s in source order (long first, "
        "then short), not an if/else if. The two conditions cannot both hold on "
        "one bar (one needs close > open, the other close < open), so the order "
        "is immaterial here; it is preserved anyway because source order is the "
        "engine's fill priority (PINE_SEMANTICS.md 1.13).",
        "pyramiding = 0 (Pine's default): the engine refuses a same-direction "
        "entry at CREATION time, so while a long is open a second `BarUp` order "
        "is not placed, is not projected and never fills; the opposite "
        "direction is still allowed and reverses (PINE_SEMANTICS.md 1.1).",
        "The /*backtest header declares `period: 3h` on Futures_Binance "
        "BTC_USDT, hence timeframe = '3h'; its basePeriod: 15m is the FMZ "
        "backtester's own intrabar fill granularity, not the strategy period. "
        "The header's start/end window is the recorded run's window, not a "
        "source property, and is not applied.",
        "Leverage, margin, liquidation, funding and the venue's contract-step "
        "rounding are not modelled; the chain verifier measures the step "
        "rounding separately (PINE_SEMANTICS.md 1.6) instead of treating it as "
        "a signal difference.",
    ]

    def pine_indicators(self, dataframe: pd.DataFrame, params: dict) -> pd.DataFrame:
        bars_up = int(params["BarsUp"])
        bars_down = int(params["BarsDown"])
        close = dataframe["close"]
        open_ = dataframe["open"]
        # close[BarsUp] / close[BarsDown] -- history references driven by the
        # inputs; on the first bars the shifted value is na and Pine compares
        # na as false, which the fillna(False) below reproduces.
        dataframe["pine_close_barsup"] = close.shift(bars_up)
        dataframe["pine_close_barsdown"] = close.shift(bars_down)

        # if (close > open and open > close[BarsUp]) and time_cond
        dataframe["pine_long_condition"] = (
            (close > open_) & (open_ > close.shift(bars_up))
        ).fillna(False)
        # if (close < open and open < close[BarsDown]) and time_cond
        dataframe["pine_short_condition"] = (
            (close < open_) & (open_ < close.shift(bars_down))
        ).fillna(False)
        return dataframe

    def pine_context(self, dataframe: pd.DataFrame, params: dict) -> dict:
        return {
            "long_condition": dataframe["pine_long_condition"].to_numpy(dtype=bool),
            "short_condition": dataframe["pine_short_condition"].to_numpy(dtype=bool),
            "high": dataframe["high"].to_numpy(dtype=float),
            "low": dataframe["low"].to_numpy(dtype=float),
            # syminfo.mintick -- a venue property, declared once on the port.
            "mintick": float(self.source_mintick),
        }

    def pine_script(self, broker, i: int, ctx: dict) -> None:
        # if (close > open and open > close[BarsUp]) and time_cond
        #     strategy.entry("BarUp", strategy.long, stop = high + syminfo.mintick, ...)
        if ctx["long_condition"][i]:
            broker.entry(
                "BarUp", "long", stop=float(ctx["high"][i]) + ctx["mintick"]
            )
        # if (close < open and open < close[BarsDown]) and time_cond
        #     strategy.entry("BarDn", strategy.short, stop = low + syminfo.mintick, ...)
        if ctx["short_condition"][i]:
            broker.entry(
                "BarDn", "short", stop=float(ctx["low"][i]) + ctx["mintick"]
            )
