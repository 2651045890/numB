"""Port of sources/SM_b38271a8b0cb5bad.pine
(batch_001/DEMA与TEMA交叉策略Dual-and-Triple-Exponential-Moving-Average-Crossover-Strategy.md).

Pine v5. A Double EMA and a Triple EMA of the same source, long on the DEMA
crossing above the TEMA, short on the cross below:

    dema_e1 = ta.ema(dema_src, dema_length)
    dema_e2 = ta.ema(dema_e1, dema_length)
    dema    = 2 * dema_e1 - dema_e2

    tema_ema1 = ta.ema(tema_src, tema_length)
    tema_ema2 = ta.ema(tema_ema1, tema_length)
    tema_ema3 = ta.ema(tema_ema2, tema_length)
    tema    = 3 * (tema_ema1 - tema_ema2) + tema_ema3

    if ta.crossover(dema, tema)
        strategy.entry("Long", strategy.long)
    if ta.crossunder(dema, tema)
        strategy.entry("Short", strategy.short)

The EMAs are chained on their own output (an EMA of an EMA, and an EMA of an
EMA of an EMA), so the port feeds each stage's Series into the next; collapsing
the chain into one smoothed series would be a different indicator. Pine's
`ta.ema` is applied to the input series without skipping the na prefix, and each
stage is na until the stage before it produced a value, which is what
`pine_ta.pine_ema` does.

Both stages take a source input that defaults to `close`; the port resolves the
default through `pine_ta.pine_source` so an override of `dema_src` / `tema_src`
still selects a real series.

The crossover/crossunder of two na-series is false throughout the warm-up, so
the first bars place no order.

There is no exit call of any kind: a position is only ever closed by the
opposite entry reversing it, so `source_reproduce_stops` is False and a position
open at the end of the data stays open. `can_short` is True.

The source declares no `strategy()` properties beyond title/shorttitle/overlay,
so Pine's documented defaults apply: initial_capital 1000000 USD,
default_qty_type `strategy.fixed`, default_qty_value 1, commission 0%,
pyramiding 0. The `plot` / `plotshape` calls are display-only.

NOTE for verification: the source's `/*backtest` header declares `period: 2h`,
and no 2h futures history is stored locally, so `verify_chain` reports
`skipped_no_local_data` for this port rather than a verdict. The header's
`basePeriod: 15m` is the FMZ backtester's own fill granularity, not the
strategy's period.
"""
from __future__ import annotations

from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


def _as_source(dataframe, value):
    """A Pine `input.source` value: a name like 'close', or an explicit series."""
    if isinstance(value, str):
        return ta.pine_source(dataframe, value)
    return value


class SMDemaTemaCross_b38271(PinePortBase, IStrategy):
    source_id = "SM_b38271a8b0cb5bad"
    source_file = (
        "DEMA与TEMA交叉策略Dual-and-Triple-Exponential-Moving-Average-"
        "Crossover-Strategy.md"
    )
    timeframe = "2h"
    can_short = True
    # The two input.source defaults are Pine's `close`; the string form keeps the
    # value overridable through source_parameters.
    source_defaults: dict = {
        "dema_length": 10,
        "dema_src": "close",
        "tema_length": 8,
        "tema_src": "close",
    }
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    # No strategy.exit / strategy.close / stop= / limit= anywhere.
    source_reproduce_stops = False
    source_fidelity_notes = [
        "The EMAs are chained on their own output -- ta.ema(ta.ema(src, n), n) for "
        "the DEMA and three nested ta.ema calls for the TEMA -- so each stage's "
        "Series feeds the next; collapsing the chain would be a different indicator.",
        "dema_src / tema_src are input.source with the default `close`; the port "
        "carries them as the string 'close' and resolves it through "
        "pine_ta.pine_source, so an override still selects a real series.",
        "dema_length / tema_length are input.int(10) / input.int(8) with minval=1; "
        "both are carried through source_defaults unchanged.",
        "ta.ema seeding follows pine_ta's documented first-value model, which is a "
        "named parity risk (PINE_SEMANTICS.md 3.1): TradingView does not publish its "
        "seeding rule, and the alternative SMA-seeded variant would shift every EMA "
        "stage during the warm-up. The chained EMAs compound that warm-up, so the "
        "first bars of dema/tema are the least certain part of this port.",
        "crossover / crossunder of two series that are na during warm-up are false, "
        "as Pine's na-compares-false rule requires, so no order is placed before the "
        "chains produce values.",
        "No exit call exists: a position is closed only by the opposite entry "
        "reversing it, so source_reproduce_stops is False and a position open at the "
        "end of the data stays open.",
        "plot(dema, ...) / plot(tema, ...) / plotshape(...) are display-only and are "
        "not reproduced; the crossover_long / crossunder_short signals they draw ARE "
        "the trade conditions and are reproduced.",
        "The source declares no strategy() properties beyond title/shorttitle/"
        "overlay, so Pine's documented defaults are used: fixed / 1 contract, "
        "initial capital 1000000, commission 0%, pyramiding 0.",
        "The header declares period: 2h on Futures_Binance BTC_USDT; its basePeriod: "
        "15m is the FMZ backtester's own granularity for filling those 2h bars, not "
        "the strategy's period.",
        "Leverage, margin, liquidation and funding are not modelled; the venue's "
        "contract-step rounding is not modelled either and is measured separately by "
        "verify_chain.",
    ]

    # ---- ta.* / bare builtins ---------------------------------------------
    def pine_indicators(self, dataframe, params):
        dema_length = int(params["dema_length"])
        tema_length = int(params["tema_length"])
        dema_src = _as_source(dataframe, params["dema_src"])
        tema_src = _as_source(dataframe, params["tema_src"])

        # dema_e1 = ta.ema(dema_src, dema_length) ; dema_e2 = ta.ema(dema_e1, n)
        dema_e1 = ta.pine_ema(dema_src, dema_length)
        dema_e2 = ta.pine_ema(dema_e1, dema_length)
        dema = 2 * dema_e1 - dema_e2
        # tema_ema1..3 = ta.ema of the previous stage ; tema = 3*(e1-e2) + e3
        tema_ema1 = ta.pine_ema(tema_src, tema_length)
        tema_ema2 = ta.pine_ema(tema_ema1, tema_length)
        tema_ema3 = ta.pine_ema(tema_ema2, tema_length)
        tema = 3 * (tema_ema1 - tema_ema2) + tema_ema3

        dataframe["pine_dema"] = dema
        dataframe["pine_tema"] = tema
        # crossover_long = ta.crossover(dema, tema) ; crossunder_short = ta.crossunder
        dataframe["pine_long_condition"] = ta.pine_crossover(dema, tema)
        dataframe["pine_short_condition"] = ta.pine_crossunder(dema, tema)
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "long_condition": dataframe["pine_long_condition"].to_numpy(),
            "short_condition": dataframe["pine_short_condition"].to_numpy(),
        }

    # ---- strategy.* -------------------------------------------------------
    def pine_script(self, broker, i, ctx):
        # if (crossover_long)
        #     strategy.entry("Long", strategy.long)
        if ctx["long_condition"][i]:
            broker.entry("Long", "long")
        # if (crossunder_short)
        #     strategy.entry("Short", strategy.short)
        if ctx["short_condition"][i]:
            broker.entry("Short", "short")
