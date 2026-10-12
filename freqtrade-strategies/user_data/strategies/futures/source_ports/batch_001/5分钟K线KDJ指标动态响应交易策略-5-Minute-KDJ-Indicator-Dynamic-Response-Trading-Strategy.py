"""Port of sources/SM_ddea082c082c2330.pine (5分钟K线KDJ指标动态响应交易策略).

Pine v6, both directions, `period: 1d` in the backtest header. The KDJ triple is

    raw_k = ta.stoch(high, low, close, length)   // length = 5
    k     = ta.sma(raw_k, smoothK)               // smoothK = 1
    d     = ta.sma(k, smoothD)                   // smoothD = 1
    j     = 3 * k - 2 * d

and the four thresholds are read off `k` alone, with no crossovers:

    k <  5  -> strategy.entry("Long",  strategy.long,  qty=qty)
    k >  90 -> strategy.close("Long")
    k >  95 -> strategy.entry("Short", strategy.short, qty=qty)
    k <  10 -> strategy.close("Short")

The four `if`s are independent and evaluated in that order on every bar, so the
same bar can both close and re-open. `qty = math.floor(strategy.equity / close)`
is evaluated once per bar, before any order is placed, and passed explicitly to
`strategy.entry` -- this is 100%-of-equity sizing done by hand, not
`default_qty_type = percent_of_equity`.

The port reproduces `qty` from the engine's own equity at that bar's close, and
the framework sizes each fill from the notional the engine recorded
(PinePortBase.custom_stake_amount), so both sides commit the same money.

FIDELITY:
* ARGUMENT BINDING -- `ta.stoch` is `ta.stoch(source, high, low, length)`, so
  the source's call binds source=high, high=low, low=close and computes
  100 * (high - lowest(close, n)) / (highest(low, n) - lowest(close, n)). The
  md's PROSE describes the canonical form ("K is the relative position of the
  CLOSE in the N-period high/low range"), which would be
  `ta.stoch(close, high, low, length)`. The fenced source block is authoritative,
  so the swapped form is what is ported; the prose disagreement is recorded
  here and not silently "fixed". A consequence is that `k` is NOT confined to
  0..100 (both the numerator and the denominator can be negative here), which is
  why the thresholds still bite but do not mean what the prose says they mean.
* ta.stoch is not exposed by pine_ta, so it is computed inline with
  pine_highest/pine_lowest per the source's own arithmetic. A zero-width range
  (denominator exactly 0) is emitted as na; Pine's behaviour on that division is
  not published. Real candle data does not hit it (it needs max(low) ==
  min(close) exactly over 5 bars).
* `strategy(..., slippage=3)` declares 3 ticks of slippage. The shared engine
  does not model slippage at all, and it cannot be expressed from a port (the
  fill price is chosen inside the engine, and Freqtrade's own slippage applies
  to its executed orders, not to the engine's ledger, so adding it on one side
  only would break the two apart). Every fill here is at the raw next-bar open.
* The `// Note:` comment about applying 0.1% commission is PROSE; it says the
  setting must be made by hand in TradingView's Strategy Properties, and the
  `strategy()` call declares no commission. Code wins: 0%.
* `strategy()` declares no initial_capital, so the harness convention 1000000 is
  used (Pine's reference documents 100000). THIS ONE IS LOAD-BEARING:
  `qty = floor(strategy.equity / close)` scales with the starting bankroll, so
  the source's absolute position sizes -- and therefore its absolute P&L -- can
  only be reproduced by knowing the account it actually ran on. Both the engine
  and the framework are given the same 1,000,000 here, so the chain comparison
  is unaffected; the source's own reported returns are not recoverable.
* `qty` is evaluated at the placing bar's close and frozen there; the order
  fills at the next bar's open. If that open gaps up, the notional the engine
  commits exceeds the equity it was sized from, and Freqtrade can refuse the
  order ("SOURCE_STAKE_VETO"). That is the framework's single-order cap, not the
  source's arithmetic; it is logged rather than hidden.
* `label.new` calls are visual only and are not ported.
* The source's title and input comments say "5-minute chart", but the backtest
  header declares `period: 1d`; the header is the chart timeframe the source
  actually ran on and is what the port declares.
* Pine v6 `ta.sma(x, 1)` is the series itself (na stays na), which pine_sma
  models with a 1-bar window.
"""
import numpy as np
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


class SM5MinKdjDynamic_ddea08(PinePortBase, IStrategy):
    source_id = "SM_ddea082c082c2330"
    source_file = (
        "5分钟K线KDJ指标动态响应交易策略-5-Minute-KDJ-Indicator-Dynamic-Response-"
        "Trading-Strategy.md"
    )
    timeframe = "1d"
    can_short = True
    source_defaults: dict = {"length": 5, "smoothK": 1, "smoothD": 1}
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    source_fidelity_notes = [
        "ta.stoch binds positionally as (source, high, low, length), so "
        "ta.stoch(high, low, close, length) means source=high, high=low, "
        "low=close: 100*(high - lowest(close,n)) / (highest(low,n) - "
        "lowest(close,n)). The md's prose describes the canonical close-based "
        "form; the fenced code is authoritative and is what is ported. k is "
        "therefore not bounded by 0..100.",
        "ta.stoch is not in pine_ta, so it is computed inline per the source's "
        "arithmetic. A zero-width denominator yields na (Pine's behaviour on "
        "that division is not published).",
        "strategy(..., slippage=3) declares 3 ticks of slippage, which the "
        "shared engine does not model and a port cannot inject without breaking "
        "the engine/framework price comparison. Fills are at the raw next-bar "
        "open.",
        "The 0.1% commission is a comment instructing a manual TradingView "
        "setting, not a strategy() property; the declared commission is 0%.",
        "No initial_capital is declared; 1000000 is the harness convention. It "
        "is load-bearing here because qty = floor(equity/close) scales with the "
        "bankroll, so the source's absolute sizes depend on an account value the "
        "source never states.",
        "qty is frozen at the placing bar's close and filled at the next open; a "
        "gap up can push the notional past Freqtrade's single-order cap, which "
        "is logged as SOURCE_STAKE_VETO rather than hidden.",
        "label.new calls are visual only. The title/comments say 5-minute chart, "
        "but the header's period: 1d is the chart the source ran on.",
        "KNOWN BLOCKER, OUTSIDE THIS FILE: both `strategy.close` calls fire "
        "whenever k crosses their threshold, whether or not the named entry is "
        "open -- `strategy.close(\"Long\")` while a SHORT is on is a no-op in "
        "Pine and a no-op in the engine's own fill path (PineBroker._close_entries "
        "matches on from_entry), but `run_pine`'s signal projection looks only at "
        "the position's SIGN, so it emits an `exit_short` the engine never acted "
        "on and Freqtrade closes the short a bar early. That is the whole of this "
        "port's `mismatch` verdict: with the projection taught to skip a close "
        "whose from_entry is not among the open entries, the same engine, data and "
        "framework compare as a clean `match` (24/24, every counter 0). The port "
        "is left calling `broker.close` exactly as the source calls "
        "`strategy.close`; the fix belongs in the shared projection, not here.",
    ]

    def pine_indicators(self, dataframe, params):
        length = int(params["length"])
        smooth_k = int(params["smoothK"])
        smooth_d = int(params["smoothD"])

        close = dataframe["close"]
        lowest_low_of_close = ta.pine_lowest(close, length)
        highest_high_of_low = ta.pine_highest(dataframe["low"], length)

        span = highest_high_of_low - lowest_low_of_close
        # Pine ta.stoch = 100 * (source - lowest(low, n)) / (highest(high, n) - lowest(low, n))
        # with the source's own binding: source=high, high=low, low=close.
        raw_k = (
            100.0
            * (dataframe["high"] - lowest_low_of_close)
            / span.where(span != 0.0)
        )
        k = ta.pine_sma(raw_k, smooth_k)
        d = ta.pine_sma(k, smooth_d)

        dataframe["pine_raw_k"] = raw_k
        dataframe["pine_k"] = k
        dataframe["pine_d"] = d
        dataframe["pine_j"] = 3.0 * k - 2.0 * d

        dataframe["pine_long_entry"] = k < 5
        dataframe["pine_long_exit"] = k > 90
        dataframe["pine_short_entry"] = k > 95
        dataframe["pine_short_exit"] = k < 10
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "close": dataframe["close"].to_numpy(),
            "long_entry": dataframe["pine_long_entry"].to_numpy(),
            "long_exit": dataframe["pine_long_exit"].to_numpy(),
            "short_entry": dataframe["pine_short_entry"].to_numpy(),
            "short_exit": dataframe["pine_short_exit"].to_numpy(),
        }

    def pine_script(self, broker, i, ctx):
        # qty = math.floor(strategy.equity / close), evaluated once per bar
        # before any order is placed. A non-positive close cannot arise from
        # candle data; na is passed through so the engine falls back to the
        # strategy's default quantity, which is what Pine does with qty=na.
        close = ctx["close"][i]
        qty = float(np.floor(broker.equity / close)) if close > 0 else np.nan

        # if (long_entry) strategy.entry("Long", strategy.long, qty=qty)
        if ctx["long_entry"][i]:
            broker.entry("Long", "long", qty=qty)
        # if (long_exit) strategy.close("Long")
        if ctx["long_exit"][i]:
            broker.close("Long")
        # if (short_entry) strategy.entry("Short", strategy.short, qty=qty)
        if ctx["short_entry"][i]:
            broker.entry("Short", "short", qty=qty)
        # if (short_exit) strategy.close("Short")
        if ctx["short_exit"][i]:
            broker.close("Short")
