"""Port of sources/SM_17d5f9d7a6c27d32.pine (Simple-EMA20-Strategy-Stochastic).

Pine v5, long only. `k` is a raw `ta.stoch` smoothed by `smoothK`; `d` is the
`periodD` SMA of `k`. A long market entry is placed when the bar's low holds
above `ta.ema(close, 20)` and that EMA is above its own value 20 bars earlier
and `k > d`. `strategy.close("long")` is placed whenever the close prints below
the EMA.

Both orders are market orders, so the engine fills them at the next bar's open,
which is where Pine fills them too.

The `strategy()` declaration carries no sizing or cost properties (only
margin_long/margin_short = 100, i.e. unlevered), so Pine's documented defaults
apply: fixed sizing of 1, 0% commission, pyramiding 0.

FIDELITY: see source_fidelity_notes for the items this port could not reproduce
exactly.
"""
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


class SMSimpleEma20Strat_17d5f9(PinePortBase, IStrategy):
    source_id = "SM_17d5f9d7a6c27d32"
    source_file = "Simple-EMA20-Strategy-Stochastic.md"
    timeframe = "4h"
    can_short = False
    source_defaults = {"periodK": 14, "smoothK": 1, "periodD": 3}
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    source_fidelity_notes = [
        "ta.ema is seeded with the first non-na observation (pine_ta's documented "
        "model); TradingView's seeding rule is unpublished, so the EMA differs "
        "until the recursion converges.",
        "ta.stoch is not exposed by pine_ta, so it is computed inline as "
        "100*(close - ta.lowest(low, periodK)) / (ta.highest(high, periodK) - "
        "ta.lowest(low, periodK)); a window with zero range (highest == lowest) "
        "yields na. Pine's behaviour on that zero division is not published.",
        "The backtest header declares basePeriod: 15m (intrabar data). The engine "
        "evaluates at bar close and fills at the next open, so intrabar path "
        "differences are not modelled.",
        "strategy() declares no initial_capital; 1000000 is used per the harness "
        "convention (Pine's reference documents 100000). It does not affect trade "
        "outcomes here: sizing is fixed 1 and commission is 0%.",
    ]

    def pine_indicators(self, dataframe, params):
        period_k = params["periodK"]
        smooth_k = params["smoothK"]
        period_d = params["periodD"]

        lowest_low = ta.pine_lowest(dataframe["low"], period_k)
        highest_high = ta.pine_highest(dataframe["high"], period_k)
        span = highest_high - lowest_low
        # Pine ta.stoch = 100 * (source - lowest(low, n)) / (highest(high, n) - lowest(low, n))
        raw_stoch = 100.0 * (dataframe["close"] - lowest_low) / span.where(span != 0.0)

        k = ta.pine_sma(raw_stoch, smooth_k)
        d = ta.pine_sma(k, period_d)

        ema = ta.pine_ema(dataframe["close"], 20)
        ema_lagged = ema.shift(20)

        dataframe["k"] = k
        dataframe["d"] = d
        dataframe["ema20"] = ema
        # Pine's `na` compares false, so every na operand makes the condition
        # false; pandas comparisons give the same result.
        dataframe["entry_ok"] = (
            (dataframe["low"] > ema) & (k > d) & (ema > ema_lagged)
        )
        dataframe["close_ok"] = dataframe["close"] < ema
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "entry_ok": dataframe["entry_ok"].to_numpy(),
            "close_ok": dataframe["close_ok"].to_numpy(),
        }

    def pine_script(self, broker, i, ctx):
        if ctx["entry_ok"][i]:
            broker.entry("long", "long")
        if ctx["close_ok"][i]:
            broker.close("long")
