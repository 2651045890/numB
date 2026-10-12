"""Port of sources/SM_7d4ce4b1445d3ef3.pine (SuperTrend-Dual-Moving-Average-Crossover).

Pine v5. Despite the "SuperTrend" title the script contains no SuperTrend; it
trades the crossover of two double EMAs (DEMA):

    ema5 = ta.ema(close, 5)                    # chart timeframe
    ema2 = ta.ema(close, 2)
    demaFast = request.security(syminfo.tickerid, "30", 2 * ema5 - ta.ema(ema5, 5))
    demaSlow = request.security(syminfo.tickerid, "30", 2 * ema2 - ta.ema(ema2, 2))

    buy  = ta.crossover(demaSlow, demaFast)    # fast crosses above the slow one
    sell = ta.crossunder(demaSlow, demaFast)

    strategy.entry("BUY",  strategy.long,  1, when = buy)
    strategy.entry("SELL", strategy.short, 1, when = sell)

`2 * e - ta.ema(e, n)` is DEMA(close, n), so the source is DEMA(5) vs DEMA(2).

Both entries are unconditional market orders with an explicit qty of 1, so an
opposite signal while a position is open nets against it and reverses -- the
engine models Pine's netting. The script never calls strategy.close/exit, so the
position only ever changes through a new entry. `pyramiding` is not set, so
Pine's default of 0 applies and a repeated BUY while already long is ignored.

The source declares no input(), and its strategy() call sets only title /
shorttitle, so Pine's documented defaults apply: initial_capital 1000000 USD,
default_qty_type strategy.fixed, default_qty_value 1, commission 0%,
pyramiding 0.

FIDELITY: the two `request.security(..., "30", ...)` calls CANNOT be honoured --
the engine does not resample and a port only ever receives bars at the strategy
timeframe, so no 30-minute series exists to evaluate the expression on. The
DEMA expressions are therefore evaluated on the strategy's own bars, which
preserves the script's structure (DEMA5 vs DEMA2 crossover, netting entries,
fixed qty 1) but not its crossing bars: the original crosses on 30-minute
samples and this port crosses on the strategy-timeframe samples. Every signal
time may differ; this is the port's dominant fidelity gap and is repeated in
source_fidelity_notes. The `lookahead` argument is left at Pine's default
barmerge.lookahead_off, so the source itself introduces no future data.

`plotchar((2 * ema5 - ta.ema(ema5, 5)), ...)` is plot-only with no trade meaning
and is dropped.
"""
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


class SMSuperTrendDualMaCross_7d4ce4(PinePortBase, IStrategy):
    source_id = "SM_7d4ce4b1445d3ef3"
    source_file = "SuperTrend双均线交叉策略SuperTrend-Dual-Moving-Average-Crossover-Strategy.md"
    timeframe = "1d"
    can_short = True
    source_defaults = {}
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    source_fidelity_notes = [
        "request.security(syminfo.tickerid, \"30\", ...) is not reproducible: the "
        "engine does not resample and a port receives only strategy-timeframe bars, "
        "so the 30-minute series the expression is evaluated on does not exist here. "
        "demaFast/demaSlow are computed from the same expressions on the strategy's "
        "own bars, so the crossing bars (and therefore the entries) differ from the "
        "original. This is the port's dominant gap.",
        "request.security uses Pine's default lookahead=barmerge.lookahead_off, so the "
        "source introduces no future data; the port is likewise causal.",
        "plotchar() of the chart-timeframe DEMA is plot-only and dropped.",
        "The source has no input(); the lengths 5 and 2 and the entry qty 1 are "
        "literals reproduced verbatim, not exposed as parameters.",
        "EMA (and the DEMA built from it) follows pine_ta's documented first-value "
        "seeding, listed in PINE_SEMANTICS.md as a parity risk.",
        "strategy() sets no properties beyond title/shorttitle, so Pine's documented "
        "defaults are used (fixed qty 1, 0% commission, pyramiding 0, 1000000 capital).",
    ]

    def pine_indicators(self, dataframe, params):
        close = dataframe["close"]
        ema5 = ta.pine_ema(close, 5)
        ema2 = ta.pine_ema(close, 2)
        # demaFast = request.security(syminfo.tickerid, "30", 2 * ema5 - ta.ema(ema5, 5))
        dema_fast = 2 * ema5 - ta.pine_ema(ema5, 5)
        # demaSlow = request.security(syminfo.tickerid, "30", 2 * ema2 - ta.ema(ema2, 2))
        dema_slow = 2 * ema2 - ta.pine_ema(ema2, 2)
        dataframe["demaFast"] = dema_fast
        dataframe["demaSlow"] = dema_slow
        dataframe["buy"] = ta.pine_crossover(dema_slow, dema_fast)
        dataframe["sell"] = ta.pine_crossunder(dema_slow, dema_fast)
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "buy": dataframe["buy"].to_numpy(),
            "sell": dataframe["sell"].to_numpy(),
        }

    def pine_script(self, broker, i, ctx):
        # The source's two `when=` guards are independent statements in source
        # order; both are market orders with qty 1.
        if ctx["buy"][i]:
            broker.entry("BUY", "long", 1)
        if ctx["sell"][i]:
            broker.entry("SELL", "short", 1)
