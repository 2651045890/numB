"""Port of sources/SM_2bcc670117bbadd3.pine (batch_001/Demark-Reversal-Points-CC.md).

Pine v5. The file declares `indicator('Demark Reversal Points [CC]',
max_bars_back=3000, overlay=true)` -- cheatcountry's Demark counter display --
and the conversion station appended:

    buy  = ta.crossover(drp, 0),
    sell = ta.crossunder(drp, 0)
    if buy
       strategy.entry("buy", strategy.long)
    else if sell
        strategy.entry("sell", strategy.short)

`strategy.entry` cannot compile inside `indicator()`, so the "original strategy"
IS the indicator plus that block, and its trading behaviour is exactly what the
block does: enter on the reversal, NEVER exit. There is no `strategy()`
declaration and no `strategy.close` / `strategy.exit` in the file, so every
`strategy()` property is Pine's documented default (fixed / 1 contract, initial
capital 1000000, 0% commission, pyramiding 0, process_orders_on_close=false) and
`source_reproduce_stops` is False.

`drp` does carry a `-1` (`drp = dCount == length ? 1 : uCount == length ? -1 :
0`), but it is never used as a bare condition: both order-block conditions wrap
it in `ta.crossover(drp, 0)` / `ta.crossunder(drp, 0)`, i.e. explicit comparisons
against 0. The minus-truthiness trap of PINE_SEMANTICS.md 1.17 does not apply to
this source -- and the port does not "normalise" `drp` either; it reproduces the
1 / -1 / 0 values and the crossover on top of them.

The counting, reproduced literally:

    for i = 0 to length - 1 by 1
        uCount += (nz(src[i]) > nz(src[i + lbLength]) ? 1 : 0)
        dCount += (nz(src[i]) < nz(src[i + lbLength]) ? 1 : 0)
    drp = dCount == length ? 1 : uCount == length ? -1 : 0

`uCount` / `dCount` are re-declared `= 0` every bar, so they are per-bar sums.
The bare `dCount` statement at the end of the loop body is a no-op.

`src` is the non-repainting form of a same-symbol request:

    res = input.timeframe(defval='')                      -> the chart timeframe
    src = request.security(tickerid, res,
                           inp[rep ? 0 : barstate.isrealtime ? 1 : 0])
          [rep ? 0 : barstate.isrealtime ? 0 : 1]

With the default `rep = false` and on historical bars (`barstate.isrealtime`
false) the inner offset is 0 and the outer offset is 1, so `src = close[1]`.
`res = ''` means the request is at the CHART's own timeframe, i.e. no resampling
is involved and the transform is exactly a one-bar lag -- which is what the port
computes. The `sig`, `drpColor`, `barcolor`, `alertcondition` and `plotshape`
lines are display/alerts only.
"""
import numpy as np
import pandas as pd
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


class SMDemarkReversalPointsCc_2bcc67(PinePortBase, IStrategy):
    source_id = "SM_2bcc670117bbadd3"
    source_file = "Demark-Reversal-Points-CC.md"
    timeframe = "4h"
    can_short = True
    source_defaults: dict = {
        "inp": "close",
        "res": "",
        "rep": False,
        "bar": True,
        "length": 9,
        "lbLength": 4,
    }
    # No `strategy()` call exists in the source, so Pine's documented defaults
    # apply: fixed / 1 contract, 1000000 initial capital, 0% commission,
    # pyramiding 0, process_orders_on_close = false.
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    source_reproduce_stops = False
    source_mintick = 0.1
    source_fidelity_notes = [
        "The source is an `indicator()`, not a `strategy()`: the order block "
        "appended by the conversion station is the whole trading behaviour. No "
        "`strategy()` declaration exists, so fixed/1, 1000000 capital, 0% "
        "commission and pyramiding 0 are Pine's documented defaults rather "
        "than declarations.",
        "NO exit exists in the source; a position is closed only by the "
        "opposite entry reversing it, so source_reproduce_stops is False.",
        "`drp` keeps its 1 / -1 / 0 integers and is never used as a bare "
        "condition -- both entries wrap it in `ta.crossover(drp, 0)` / "
        "`ta.crossunder(drp, 0)`. PINE_SEMANTICS.md 1.17 (minus truthiness) "
        "does not apply, and `drp` is deliberately NOT normalised to a "
        "boolean anywhere in this port.",
        "MODELLING CHOICE: `request.security(syminfo.tickerid, res, ...)` with "
        "the default `res = ''` (input.timeframe defval '') requests the "
        "CHART's own timeframe, so no resampling is involved and PINE_SEMANTICS "
        "section 2.1 (multi-timeframe not modelled) does not bite. With "
        "`rep = false` both offsets collapse on historical bars (`inner 0`, "
        "`outer 1`), so the whole expression is exactly `close[1]`. The port "
        "computes that lag directly. The manifest flags this source "
        "`multi_timeframe_or_symbol`; on the default inputs it is the symbol "
        "itself at the chart's timeframe.",
        "On the realtime bar (`barstate.isrealtime` true) the offsets become "
        "`inner 1`, `outer 0`; a backtest has no realtime bar, so the port "
        "models the historical branch throughout.",
        "`uCount` / `dCount` are re-declared `= 0` on every bar in the source "
        "(no `var`), so they are per-bar sums over i = 0..length-1; the port "
        "builds them as column sums of the same shifted comparisons. The bare "
        "`dCount` statement that ends the loop body is a no-op and is dropped.",
        "`nz(src[i])` is Pine's na -> 0, which matters for the warm-up bars "
        "where `src[i]` falls off the start of the series: a missing lag is 0, "
        "not na, so the comparisons are False there rather than na. The port "
        "fills the lagged series with 0 before comparing.",
        "`sig`, `drpColor`, `barcolor`, the two `alertcondition`s and the two "
        "`plotshape`s are display/alerts only and are not reproduced. `sig` in "
        "particular is computed in the source but never referenced by the "
        "order block.",
        "The trailing comma in `buy = ta.crossover(drp, 0),` is Pine's "
        "line-continuation syntax, not a tuple; `buy` and `sell` are the two "
        "crossover series.",
        "Leverage, margin, liquidation, funding and the venue's contract-step "
        "rounding are not modelled (PINE_SEMANTICS.md section 2).",
    ]

    def pine_indicators(self, dataframe, params):
        length = int(params["length"])
        lb_length = int(params["lbLength"])

        # src = request.security(tickerid, '', inp)[1] with the default rep=false
        # and on historical bars -- i.e. the previous bar's close.
        src = dataframe["close"].shift(1)
        nz_src = src.fillna(0.0)

        u_count = pd.Series(0.0, index=dataframe.index, dtype=float)
        d_count = pd.Series(0.0, index=dataframe.index, dtype=float)
        for i in range(length):
            now = nz_src.shift(i)
            later = nz_src.shift(i + lb_length)
            u_count += (now > later).astype(float)
            d_count += (now < later).astype(float)

        drp = pd.Series(0.0, index=dataframe.index, dtype=float)
        drp = drp.mask(u_count == length, -1.0)
        drp = drp.mask(d_count == length, 1.0)

        buy = ta.pine_crossover(drp, 0.0).fillna(False)
        sell = ta.pine_crossunder(drp, 0.0).fillna(False)

        dataframe["pine_drp"] = drp
        dataframe["pine_buy"] = buy.astype(bool)
        dataframe["pine_sell"] = sell.astype(bool)
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "buy": dataframe["pine_buy"].to_numpy(dtype=bool),
            "sell": dataframe["pine_sell"].to_numpy(dtype=bool),
        }

    def pine_script(self, broker, i, ctx):
        # if buy
        #    strategy.entry("buy", strategy.long)
        # else if sell
        #     strategy.entry("sell", strategy.short)
        if ctx["buy"][i]:
            broker.entry("buy", "long")
        elif ctx["sell"][i]:
            broker.entry("sell", "short")
