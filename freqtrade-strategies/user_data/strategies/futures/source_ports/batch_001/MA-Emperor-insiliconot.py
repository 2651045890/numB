"""Port of sources/SM_279abdf7b65dd3be.pine (batch_001/MA-Emperor-insiliconot.md).

Pine v3. The file declares `study(title="MA Emperor insiliconot", overlay=true,
precision=8)` -- a nine-moving-average display -- and the conversion station
appended:

    longCond  = crossover(ma2, ma3)
    shortCond = crossunder(ma2, ma3)
    if longCond
        strategy.entry("Enter Long", strategy.long)
    else if shortCond
        strategy.entry("Enter Short", strategy.short)

`strategy.entry` cannot compile inside `study()`, so the "original strategy" IS
the indicator plus that block, and its trading behaviour is exactly what the
block does: enter on the MA2/MA3 cross, NEVER exit. There is no `strategy()`
declaration and no `strategy.close` / `strategy.exit` in the file, so every
`strategy()` property is Pine's documented default (fixed / 1 contract, initial
capital 1000000, 0% commission, pyramiding 0, process_orders_on_close=false) and
`source_reproduce_stops` is False.

`if longCond` is a genuine boolean from `crossover` / `crossunder`; this source
is NOT one of the conversion station's `x = ... ? -1 : 0` shapes, so the
minus-truthiness trap of PINE_SEMANTICS.md 1.17 does not apply.

The two MAs the order block reads, reproduced literally:

    ma2 = variant(type, ssrc, len2)     // type="LowPass", len2=13
    ma3 = variant(type, ssrc, len3)     //               len3=21

`ssrc` resolves to `close`: the whole `ssrc := ssrc == <builtin> ? ha ? ... :
<builtin> : ssrc` ladder is conditional on the local `ha`, which is the literal
`false` and is never reassigned, so every rung returns the plain builtin it is
guarding and the first rung (`ssrc == close -> close`) wins. The port therefore
feeds `close` straight into the filter, which is what the ladder evaluates to.

The only variant reachable on the default `type="LowPass"` is the LowPass
recursion, reproduced verbatim:

    a  = 2.0 / (1.0 + len)
    LP := (a - 0.25*a*a)*sr + 0.5*a*a*nz(sr[1]) - (a - 0.75*a*a)*nz(sr[2])
          + 2.0*(1.0-a)*nz(LP[1]) - (1.0-a)*(1.0-a)*nz(LP[2])

The `LP = src` / `sr = src` statements that precede it are dead: `LP` is
reassigned before anything reads it, and on the first two bars `nz(LP[1])` /
`nz(LP[2])` are na -> 0 which is what this port's zero-initialised running
values supply.
"""
import numpy as np
import pandas as pd
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


def _nz(value: float) -> float:
    """Pine `nz` in its 1-argument form: na -> 0."""
    return 0.0 if value is None or not np.isfinite(value) else float(value)


def _low_pass(source, length):
    """variant_lowPass(src, len) -- the second-order low-pass filter, verbatim."""
    values = source.to_numpy(dtype=float)
    n = len(values)
    a = 2.0 / (1.0 + float(length))
    out = np.full(n, np.nan, dtype=float)
    for t in range(n):
        # nz(sr[1]) / nz(sr[2]): a missing lag is 0, not na.
        sr1 = _nz(values[t - 1]) if t >= 1 else 0.0
        sr2 = _nz(values[t - 2]) if t >= 2 else 0.0
        # nz(LP[1]) / nz(LP[2]): the running value starts at 0 on bars 0 and 1.
        lp1 = out[t - 1] if t >= 1 else 0.0
        lp2 = out[t - 2] if t >= 2 else 0.0
        out[t] = (
            (a - 0.25 * a * a) * _nz(values[t])
            + 0.5 * a * a * sr1
            - (a - 0.75 * a * a) * sr2
            + 2.0 * (1.0 - a) * lp1
            - (1.0 - a) * (1.0 - a) * lp2
        )
    return pd.Series(out, index=source.index, dtype=float)


def _variant(kind, source, length):
    """The source's `variant(type, src, len)` dispatcher.

    Only LowPass -- the default `type` and therefore the only branch the order
    block can reach -- is implemented. Selecting any other documented option
    (Butterworth_2Pole / DEMA / EMA / Gaussian / Geometric_Mean / McGuinley /
    SMA / Sine_WMA / Smoothed_MA / Super_Smoother / Triangular_MA / Wilders /
    Zero_Lag) raises loudly instead of being approximated.
    """
    if kind == "LowPass":
        return _low_pass(source, length)
    raise NotImplementedError(
        f"MA-Emperor port implements only the LowPass variant its default "
        f"`type` input selects; type={kind!r} is not implemented"
    )


class SMMaEmperorInsiliconot_279abd(PinePortBase, IStrategy):
    source_id = "SM_279abdf7b65dd3be"
    source_file = "MA-Emperor-insiliconot.md"
    timeframe = "1h"
    can_short = True
    source_defaults: dict = {
        "type": "LowPass",
        "len1": 8,
        "len2": 13,
        "len3": 21,
        "len4": 55,
        "len5": 89,
        "lenrib": 120,
        "lenrib2": 121,
        "lenrib3": 200,
        "lenrib4": 221,
        "gauss_poles": 3,
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
        "The source is a `study()`, not a `strategy()`: the order block appended "
        "by the conversion station (`if longCond ... else if shortCond ...`) is "
        "the whole trading behaviour. No `strategy()` declaration exists, so "
        "fixed/1, 1000000 capital, 0% commission and pyramiding 0 are Pine's "
        "documented defaults rather than declarations.",
        "NO exit exists in the source; a position is closed only by the "
        "opposite entry reversing it, so source_reproduce_stops is False.",
        "`if longCond` / `else if shortCond` are booleans from `crossover` / "
        "`crossunder`; this source has no `? -1 : 0` construct anywhere, so "
        "PINE_SEMANTICS.md 1.17 (minus truthiness) does not apply.",
        "`ssrc` is fed to the filter as plain `close`. The seven-rung "
        "`ssrc := ssrc == <builtin> ? ha ? <ha-builtin> : <builtin> : ssrc` "
        "ladder is gated on the local `ha`, which is the literal `false` and is "
        "never reassigned anywhere in the source, so every rung returns the "
        "plain builtin and the first rung (which tests `ssrc == close`) fixes "
        "`ssrc = close` for every bar.",
        "Only the LowPass variant of the source's `variant(type, src, len)` "
        "dispatcher is implemented -- that is what the default `type` input "
        "selects. Selecting any other documented option raises "
        "NotImplementedError instead of being approximated.",
        "Only ma2 and ma3 are computed. ma1, ma4..ma9 and the nine `plot` "
        "calls are display-only (they are gated by the onOff1..onOff9 toggles) "
        "and no value the order block reads depends on them.",
        "The `LP = src` and `sr = src` statements in `variant_lowPass` are dead "
        "in the source -- `LP` is reassigned with `:=` before any read -- and "
        "the recursion's `nz(LP[1])` / `nz(LP[2])` / `nz(sr[1])` / `nz(sr[2])` "
        "are modelled as 0 on the bars where the lag is missing.",
        "Pine v3 integer-vs-float arithmetic is not exercised: the filter's only "
        "constant is `a = 2.0 / (1.0 + len)`, a float division in both "
        "languages.",
        "Display-only statements are not reproduced: the `precision`, the "
        "`plotshape` markers, the `color`/`linewidth`/`style` arguments and the "
        "`gauss_poles` input (which only the unimplemented Gaussian branch "
        "reads).",
        "The `/*backtest` header declares `period: 1h` on Futures_Binance "
        "BTC_USDT, so `timeframe` is \"1h\"; its `basePeriod: 15m` is the "
        "extractor's own bar granularity, not the strategy's period.",
        "Leverage, margin, liquidation, funding and the venue's contract-step "
        "rounding are not modelled (PINE_SEMANTICS.md section 2).",
    ]

    def pine_indicators(self, dataframe, params):
        close = dataframe["close"]
        # ma2 = variant(type, ssrc, len2); ma3 = variant(type, ssrc, len3)
        ma2 = _variant(params["type"], close, int(params["len2"]))
        ma3 = _variant(params["type"], close, int(params["len3"]))
        long_condition = ta.pine_crossover(ma2, ma3).fillna(False)
        short_condition = ta.pine_crossunder(ma2, ma3).fillna(False)
        dataframe["pine_ma2"] = ma2
        dataframe["pine_ma3"] = ma3
        dataframe["pine_long_condition"] = long_condition.astype(bool)
        dataframe["pine_short_condition"] = short_condition.astype(bool)
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "long_condition": dataframe["pine_long_condition"].to_numpy(dtype=bool),
            "short_condition": dataframe["pine_short_condition"].to_numpy(dtype=bool),
        }

    def pine_script(self, broker, i, ctx):
        # if longCond
        #     strategy.entry("Enter Long", strategy.long)
        # else if shortCond
        #     strategy.entry("Enter Short", strategy.short)
        if ctx["long_condition"][i]:
            broker.entry("Enter Long", "long")
        elif ctx["short_condition"][i]:
            broker.entry("Enter Short", "short")
