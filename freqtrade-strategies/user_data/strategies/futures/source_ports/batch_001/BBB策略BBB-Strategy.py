"""Port of sources/SM_22763dd46eb336b9.pine (batch_001/BBB策略BBB-Strategy.md).

Pine v5. A Bollinger %B oscillator traded at its extremes:

    basis = ta.sma(src, 21)
    dev   = 2.0 * ta.stdev(src, 21)
    upper = basis + dev
    lower = basis - dev
    bbr   = (src - lower) / (upper - lower)

    if bbr <  os       and strategy.position_size == 0
        strategy.entry("L", strategy.long)
    if bbr >= os_close and strategy.position_size >  0
        strategy.close_all()
    if bbr >  ob       and strategy.position_size == 0
        strategy.entry("S", strategy.short)
    if bbr <= ob_close and strategy.position_size <  0
        strategy.close_all()

with the declared defaults os = -0.2, os_close = 0.2, ob = 1.2, ob_close = 1.0.
The four calls are written in exactly that order and the port keeps it: Pine's
write order is the engine's fill priority (PINE_SEMANTICS.md 1.9 and 1.13).

All four are MARKET calls: the two entries have no stop/limit, and `close_all`
is a market close. So every trade fills at the NEXT bar's open, which is what
the engine models (PINE_SEMANTICS.md section 一) and what the signal projection
carries, so the chain comparison has no resting-order gap to bridge here.

The two entry conditions both require `strategy.position_size == 0` and the two
exit conditions require the position to be on the matching side, so a signal
bar is either an entry or an exit, never both, and the exit can only fire while
its own side is held. The conditions do overlap ACROSS the write order in one
place worth naming: a flat bar with bbr > 1.2 places "S", and the same bar's
`bbr <= 1.0` is false, so nothing cancels it -- there is no `strategy.cancel`
in the file.

`strategy()` IS COMMENTED OUT (source line 10). A commented-out line declares
nothing -- the same rule PINE_SEMANTICS.md 1.17 applies to commented-out exit
lines -- so Pine's documented defaults are in force: `strategy.fixed` / 1
contract, initial capital 1000000, commission 0%, `pyramiding = 0`,
`process_orders_on_close = false`. The commented line asks for
`default_qty_type = strategy.percent_of_equity` with `default_qty_value = 20`;
that is recorded in `source_fidelity_notes`, not applied.

MD/SOURCE MISMATCH (recorded, source followed): the md's prose (both the Chinese
and the English half) describes the exits as "BB%B crosses above 1.0" /
"crosses below 0.2". The source's code compares `bbr >= os_close` and
`bbr <= ob_close` -- plain comparisons on the current bar's value, not
`ta.crossover` / `ta.crossunder`. The source is followed.
"""
import numpy as np

from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


class SMBBBStrategy_22763d(PinePortBase, IStrategy):
    source_id = "SM_22763dd46eb336b9"
    source_file = "BBB策略BBB-Strategy.md"
    timeframe = "4h"
    # strategy.entry("S", strategy.short) is in the source.
    can_short = True
    source_defaults: dict = {
        # length = input.int(21, minval=1)
        "length": 21,
        # src = input(close, title="Source") -- a source selector.
        "src": "close",
        # mult = input.float(2.0, minval=0.001, maxval=50, title="StdDev")
        "mult": 2.0,
        # ob = input.float(1.2, "Overbought Line", step=0.1)
        "ob": 1.2,
        # ob_close = input.float(1.0, "Overbought Close", step=0.1)  (md renders `true`)
        "ob_close": 1.0,
        # os = input.float(-0.2, "Oversold Line", step=0.1)
        "os": -0.2,
        # os_close = input.float(0.2, "Oversold Close", step=0.1)
        "os_close": 0.2,
    }
    # The ONLY strategy() declaration in the file (line 10) is commented out, so
    # it declares nothing: Pine's documented defaults apply. The commented line
    # asks for default_qty_type=strategy.percent_of_equity, default_qty_value=20
    # and a price format/precision; none of that is in force.
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    # No stop / limit / trail leg anywhere: the only exits are strategy.close_all().
    source_reproduce_stops = False
    source_fidelity_notes = [
        "NOT a converter-appended order block, despite its tier_reason. The "
        "file declares no indicator() and no study(), its only strategy() line "
        "(line 10) is COMMENTED OUT, and all four order calls are the author's "
        "own active code, including two live strategy.close_all() exits. The "
        "tier_reason's 'declares indicator()/study(), tool appended "
        "strategy.entry pair; NO exits' is false on all three counts. This is "
        "the plain BB%B strategy the md describes. The source is followed.",
        "The file's only strategy() declaration is COMMENTED OUT (line 10), so "
        "Pine's documented defaults are in force: default_qty_type fixed / 1 "
        "contract, initial_capital 1000000, commission 0%, pyramiding 0, "
        "process_orders_on_close false. RECORDED BUT NOT APPLIED: the commented "
        "line asks for default_qty_type = strategy.percent_of_equity with "
        "default_qty_value = 20. On a 1000000 account that is a 200000 stake "
        "per entry instead of 1 contract -- a different strategy in money "
        "terms, and the kind of fork PINE_SEMANTICS.md 1.4/1.5.1 shows is "
        "load-bearing for the framework comparison.",
        "MD/SOURCE MISMATCH (exits): the md's prose says the exit fires when "
        "BB%B 'crosses above 1.0' (long) / 'crosses below 0.2' (short). The "
        "source compares bbr >= os_close and bbr <= ob_close -- plain "
        "comparisons against the current bar's value, with no ta.crossover / "
        "ta.crossunder anywhere in the file. The source is followed: a bar "
        "whose bbr lands past the level exits even if the previous bar was "
        "already past it.",
        "MD/SOURCE MISMATCH (rendered defaults): the md's argument table "
        "renders v_input_float_3 (ob_close) as `true` and shows the two float "
        "lines without groups. The source's real defaults are 1.0 and the "
        "values carried here (21 / 2.0 / 1.2 / 1.0 / -0.2 / 0.2).",
        "ta.stdev is Pine's BIASED (population) standard deviation -- "
        "`biased = true` is the v5 default -- so it divides by `length`, which "
        "is what pine_ta.pine_stdev computes (ddof=0). Using pandas' default "
        "ddof=1 here would shift every band and therefore every threshold "
        "crossing.",
        "`src` is a source selector (input(close)) and is used for the SMA, the "
        "stdev AND the numerator of bbr, while `close` appears nowhere else in "
        "the arithmetic. Overriding it moves the whole oscillator; it is kept "
        "as a parameter so an override does not silently fall back to close.",
        "bbr divides by (upper - lower). When the window is flat that "
        "denominator is 0, which is na in Pine; the port maps the resulting "
        "inf/-inf to na as well, so the comparisons stay false instead of "
        "becoming true on an infinite value. A modelling choice, not a "
        "documented Pine rule.",
        "Entries and exits are ALL market orders (no stop=, no limit=), so they "
        "fill at the next bar's open -- the case the engine models exactly "
        "(PINE_SEMANTICS.md section 一). Unlike a resting stop/limit entry "
        "(section 二 11) there is no projection gap to record here.",
        "Both entry conditions carry `strategy.position_size == 0` and both "
        "exit conditions require the matching side, so the four ifs cannot "
        "contradict each other. The source keeps no `strategy.cancel`, so a "
        "pending entry is never withdrawn; the port does not add one.",
        "`plot`, `hline`, `fill`, `bgcolor`, the colour constants and the "
        "titles are display-only and are not reproduced.",
        "The /*backtest header names Futures_Binance / BTC_USDT while the repo's "
        "chain verification uses BTC/USDT:USDT -- a venue mapping, not a source "
        "property. Leverage, margin, liquidation, funding and the venue's "
        "contract-step rounding are not modelled (PINE_SEMANTICS.md 1.6 "
        "measures the step rounding separately). The header's `basePeriod: 15m` "
        "is the FMZ backtester's own fill granularity, not the strategy period.",
    ]

    def pine_indicators(self, dataframe, params):
        src = ta.pine_source(dataframe, str(params["src"]))
        length = int(params["length"])
        mult = float(params["mult"])

        # basis = ta.sma(src, length)
        basis = ta.pine_sma(src, length)
        # dev = mult * ta.stdev(src, length)
        dev = mult * ta.pine_stdev(src, length)
        upper = basis + dev
        lower = basis - dev
        # bbr = (src - lower) / (upper - lower)
        with np.errstate(divide="ignore", invalid="ignore"):
            bbr = (src - lower) / (upper - lower)
        # Pine yields na where the denominator is 0 (a flat window), so an
        # infinite ratio must not survive into the comparisons below.
        bbr = bbr.replace([np.inf, -np.inf], np.nan)

        dataframe["pine_basis"] = basis
        dataframe["pine_dev"] = dev
        dataframe["pine_upper"] = upper
        dataframe["pine_lower"] = lower
        dataframe["pine_bbr"] = bbr
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "bbr": dataframe["pine_bbr"].to_numpy(dtype=float),
            "ob": float(params["ob"]),
            "ob_close": float(params["ob_close"]),
            "os": float(params["os"]),
            "os_close": float(params["os_close"]),
        }

    def pine_script(self, broker, i, ctx):
        bbr = float(ctx["bbr"][i])

        # if bbr < os and strategy.position_size == 0
        if bbr < ctx["os"] and broker.position_size == 0:
            # strategy.entry("L", strategy.long)
            broker.entry("L", "long")
        # if bbr >= os_close and strategy.position_size > 0
        if bbr >= ctx["os_close"] and broker.position_size > 0:
            # strategy.close_all()
            broker.close_all()

        # if bbr > ob and strategy.position_size == 0
        if bbr > ctx["ob"] and broker.position_size == 0:
            # strategy.entry("S", strategy.short)
            broker.entry("S", "short")
        # if bbr <= ob_close and strategy.position_size < 0
        if bbr <= ctx["ob_close"] and broker.position_size < 0:
            # strategy.close_all()
            broker.close_all()
