"""Port of sources/SM_637e7121535cfeaa.pine (batch_001/AK双RSI突破策略AK-Dual-RSI-Breakout-Strategy.md).

Pine v2. RSI(2) against a 5/200 SMA pair, with `close_all` on the short MA:

    RS   = rsi(close, 2)
    ma5  = sma(close, 5)
    ma200= sma(close, 200)
    longCondition  = close > ma200 and close < ma5 and RS < 5
    shortCondition = close < ma200 and close > ma5 and RS > 90

    if longCondition
        strategy.entry("My Long Entry Id", strategy.long)
    strategy.close_all(when = close > ma5)
    if shortCondition
        strategy.entry("My Short Entry Id", strategy.short)
    strategy.close_all(when = close < ma5)

`strategy()` sets only `title` and `overlay`, so every property is Pine's
documented default: `strategy.fixed` / 1 contract, initial capital 1000000,
commission 0%, pyramiding 0, `process_orders_on_close=false`. The `/*backtest`
header declares `period: 1h` on Futures_Binance BTC_USDT, so `timeframe` is
"1h"; `basePeriod: 15m` is the FMZ backtester's own granularity, not the
strategy's period.

THE TWO `close_all` CALLS ARE NOT SYMMETRIC, and the asymmetry decides which
side can hold a position at all. `strategy.close_all` takes no entry id, so it
closes whatever is open when it fills; both calls are re-issued on every bar
whose condition holds, and they fill at the NEXT bar's open together with any
entry placed on the same bar. The engine fills a bar's pending orders in
creation order, i.e. in source order. Therefore:

* A bar with `longCondition` also has `close < ma5` (the condition requires it),
  so the FIRST `close_all` (when = close > ma5) does not fire but the SECOND
  one does -- and it is issued AFTER the long entry. At the next open the long
  entry fills and the `close_all` issued behind it closes it at the same price:
  a zero-length round trip.
* A bar with `shortCondition` also has `close > ma5`, so the FIRST `close_all`
  fires, and it is issued BEFORE the short entry. At the next open it closes
  whatever was open and the short entry then opens.

So the long side is opened and closed on the same bar's open, and only the
short side can carry. Every close_all is re-issued per bar, so the position is
also flattened on the first bar after `close < ma5` / `close > ma5` flips.

WHAT THE PROJECTION DOES WITH THAT, and why this port verifies as
`one_sided_trades` rather than `match`: the projected signals come from orders
PLACED, not from the position's net change, so the 171 zero-length round trips
reach Freqtrade as 171 `enter_long` bars with `exit_long` never set anywhere
(the flatten happens inside one bar's fill pass, so no bar can carry its exit).
The framework opens a long at the first of them and can never signal its exit.
Measured: engine 410 trades (171 long + 239 short, the 171 all zero-length,
`profit_abs == 0.0`), engine `pine_position != 0` on 239 bars only, projected
`enter_long` 171 / `exit_short` 239 / `exit_long` 0, overlap between
`enter_short` and `exit_short` (and the other two pairs) all 0 -- so this is not
a framework entry gate. The framework's one trade is a force_exit long held from
2024-01-09 22:00 to the window end, and under a single-pair whitelist
`max_open_trades` resolves to 1, so that uncloseable long occupies the only slot
and the 239 short signals are never evaluated at all. Setting `enter_long` to 0
and changing nothing else reproduces all 239 shorts exactly. See
PINE_SEMANTICS.md 1.13 / 1.14 and PROGRESS.md section 五.

FIDELITY:

* The within-bar fill ORDER above -- pending orders filled in creation order --
  is the engine's modelled rule, not a published one. TradingView does not
  document the emulator's same-bar tie-break. The alternative model (a
  `close_all` captures the entries open at CREATION time, so a call issued
  while flat creates nothing) would let the long side survive, which is a
  materially different strategy. The engine's model is used as-is; this is
  recorded rather than silently resolved, and the source cannot settle it.
* `strategy.close_all(when = ...)`: Pine v2's `close_all` takes its condition as
  the trailing/`when` argument; the semantics used are "issue a close-all when
  the condition is true on this bar".
* No stop or limit exit exists (only `close_all`), so `source_reproduce_stops`
  is False.
* `sma(close, 200)` is na until bar 199 and na anywhere in the window
  propagates, so both conditions are false before then; `rsi(close,2)` is na
  until its Wilder seed completes. Neither is special-cased.
* The md's prose says the ma5 break "平仓止盈" and that there is no stop loss;
  the code matches on the exit side (close_all only) but the prose does not
  mention the long side's same-bar round trip, which the code produces.
* Leverage, margin, liquidation, funding and the venue's contract-step rounding
  are not modelled.
"""
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


class SMAkRsi2_637e71(PinePortBase, IStrategy):
    source_id = "SM_637e7121535cfeaa"
    source_file = "AK双RSI突破策略AK-Dual-RSI-Breakout-Strategy.md"
    timeframe = "1h"
    can_short = True
    source_defaults: dict = {}
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    source_reproduce_stops = False
    source_fidelity_notes = [
        "The two `strategy.close_all` calls are issued on opposite sides of the "
        "short entry; the engine fills a bar's pending orders in creation "
        "(source) order, so the long entry is filled and then closed at the same "
        "open while the short entry is preceded by its close_all. A bar with "
        "longCondition always also has close < ma5, so this is the path the "
        "source takes on every long signal.",
        "TradingView does not document the emulator's same-bar tie-break. The "
        "alternative model -- a close_all captures the entries open at creation "
        "time, so a call issued while flat creates nothing -- would let the long "
        "side survive, which is a different strategy. The source cannot settle "
        "it; this is recorded, not resolved.",
        "Only `close_all` exits exist (no strategy.exit / stop / limit), so "
        "source_reproduce_stops is False.",
        "The engine's 171 long round trips are zero-length (open==close, profit "
        "0.0) and the projected signals carry no `exit_long`, so Freqtrade opens "
        "one long it can never close. This port therefore verifies as "
        "`one_sided_trades`, not `match`: the framework's trade list is not "
        "comparable to the engine's. Whether the underlying within-bar fill "
        "order is TradingView's is unverified (PINE_SEMANTICS.md 1.13); the "
        "shared projection layer is NOT changed for it -- see PROGRESS.md "
        "section 六之二.",
        "MA and RSI warm-up is left as na propagation: sma(200) is na until bar "
        "199 and rsi(2) is na until its Wilder seed completes, and both "
        "conditions are false while any term is na.",
        "pine_ta.pine_rma seeds with the SMA of the first `length` non-na "
        "observations; TradingView's seeding rule is unspecified, so the first "
        "bars of rsi(2) are a modelled choice.",
        "Leverage, margin, liquidation, funding and contract-step rounding are "
        "not modelled.",
    ]

    def pine_indicators(self, dataframe, params):
        close = dataframe["close"]
        rs = ta.pine_rsi(close, 2)
        ma5 = ta.pine_sma(close, 5)
        ma200 = ta.pine_sma(close, 200)
        dataframe["pine_rs"] = rs
        dataframe["pine_ma5"] = ma5
        dataframe["pine_ma200"] = ma200
        dataframe["pine_long_condition"] = (
            (close > ma200) & (close < ma5) & (rs < 5)
        )
        dataframe["pine_short_condition"] = (
            (close < ma200) & (close > ma5) & (rs > 90)
        )
        dataframe["pine_close_above_ma5"] = close > ma5
        dataframe["pine_close_below_ma5"] = close < ma5
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "long_condition": dataframe["pine_long_condition"].to_numpy(),
            "short_condition": dataframe["pine_short_condition"].to_numpy(),
            "close_above_ma5": dataframe["pine_close_above_ma5"].to_numpy(),
            "close_below_ma5": dataframe["pine_close_below_ma5"].to_numpy(),
        }

    def pine_script(self, broker, i, ctx):
        # if (longCondition)
        #     strategy.entry("My Long Entry Id", strategy.long)
        if ctx["long_condition"][i]:
            broker.entry("My Long Entry Id", "long")
        # strategy.close_all(when = close > ma5)
        broker.close_all(when=bool(ctx["close_above_ma5"][i]))
        # if (shortCondition)
        #     strategy.entry("My Short Entry Id", strategy.short)
        if ctx["short_condition"][i]:
            broker.entry("My Short Entry Id", "short")
        # strategy.close_all(when = close < ma5)
        broker.close_all(when=bool(ctx["close_below_ma5"][i]))
