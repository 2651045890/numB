"""Port of sources/SM_dd4dabf98f22dbdf.pine (batch_001/Easy-stock.md).

Pine v4 (`//@version=4`, `study(...)` by © RafaelZioni), and the file declares a
STUDY, not a `strategy(...)`: the two `strategy.entry` calls at the bottom are
an order block APPENDED to the study by the converter site that published it
(fmz.com/strategy/352918, named in the md's Detail link). Pine v4 does not
compile `strategy.entry` inside `study()`, so the "original strategy" is the
study PLUS that appended block, and the trading behaviour it defines is
entry-only:

    linear_reg = linreg(close, 100, 0)          # a 100-bar least-squares line
    b          = security(syminfo.tickerid, "W", hma3(close, 24)[1])

    buy  = crossover(linear_reg, b)
    sell = crossunder(linear_reg, b)

    if buy
        strategy.entry("buy", strategy.long)
    else if sell
        strategy.entry("sell", strategy.short)

So the system is a cross of a 100-bar regression line of the chart close
against a WEEKLY Hull-type average (`hma3`) of the weekly close, lagged by the
"Shift" input. The two conditions are mutually exclusive on a bar, so the
`else if` ordering changes no fill; it is kept as if/elif for faithfulness.

The study computes a second higher-timeframe series, `a =
security(syminfo.tickerid, tf10, hma(close, length))`, and `plot(a, gray)`: `a`
is read by NOTHING else -- not by the entries, not by the alerts -- so it and
the `hma()` function that exists only to build it are dropped (see FIDELITY).
`b` is the only higher-timeframe series in the trading path.

There is NO exit of any kind in the source: no `strategy.close`, no
`strategy.exit`, not even a commented-out one. So `source_reproduce_stops` is
False and a position is only ever left by the opposite entry, which the engine
models as a reverse fill.

`study(...)` carries no strategy() properties, so Pine's documented defaults
apply: `default_qty_type` fixed, `default_qty_value` 1, commission 0%,
`pyramiding` 0, `initial_capital` 1000000 USD.

FIDELITY:

* Converter-appended source (PINE_SEMANTICS.md 1.17). `buy` / `sell` are
  `crossover` / `crossunder` calls -- plain booleans, NOT the `? -1 : 0` shape
  -- so 1.17's "-1 is truthy, never rewrite it as == 1" trap does not arise.
* `hma3(_src, _length)` IGNORES its arguments: its body reads the GLOBALS
  `length` and `close`, not `_src` / `_length`. Transcribed as such -- the
  weekly HMA is built from the weekly close with the global `length` (24):
  `p = length/2` (Pine integer division for two integer operands -> 12), then
  `wma(wma(close,p/3)*3 - wma(close,p/2) - wma(close,p), p)` with p/3 -> 4 and
  p/2 -> 6, i.e. `wma(wma(c,4)*3 - wma(c,6) - wma(c,12), 12)`. Passing `_src` /
  `_length` through instead would silently change the indicator.
* `hma3` is NOT the textbook Hull MA: it is `wma(3*wma(c,p/3) - wma(c,p/2) -
  wma(c,p), p)`, with all three inner WMAs on the same `p`-derived lengths.
  Reproduced literally rather than replaced by pine_ta.pine_hma, which
  implements the different `hma()` formula.
* `a` (and `hma()`, used only by it) is dropped: `plot(a)` is its only reader,
  and neither the entries nor the alertconditions touch it. Dropping it also
  keeps the port from having to model a second, unshifted higher-timeframe
  alignment.
* The higher-timeframe alignment of `b` is a MODELLING CHOICE, not something
  the source states. `security(syminfo.tickerid, "W", hma3(close, length)[1])`
  with Pine v4's default `barmerge.lookahead_off` returns, for a chart bar
  inside week W, the expression evaluated on the last COMPLETED weekly bar,
  which is week W-1; the `[1]` inside the request then takes one further weekly
  bar back. The port therefore aligns `hma3` of the frame's weekly closes
  shifted by `1 + shift` weekly bars. Both the one-bar boundary question (does
  the value update on the last chart bar of the week?) and the alternative
  reading (that `[1]` merely cancels lookahead_off's own lag, giving week W-1)
  differ by a single weekly bar; the choice is recorded as a blocker.
* Weekly bars are formed with `pandas`' W-SUN grouping, i.e. Monday 00:00 to
  Sunday 24:00 UTC, which is the `"W"` boundary Pine uses on a crypto symbol.
  `PINE_SEMANTICS.md` 3.4 lists the exchange's weekly boundary as a parity
  risk; on Futures_Binance BTC_USDT it is UTC midnight.
* The weekly closes are formed from THIS frame's closes (the 4h chart), not
  from a separate weekly feed, so the weekly bar for the final, still-open week
  is partial. It never reaches `b`: the shift of `1 + shift` weekly bars keeps
  the current week out of every value, which is also what makes the series
  causal (`b[t]` depends only on weekly closes strictly before week W).
* `pine_ta.pine_linreg` implements `linreg(close, len, 0)`: the least-squares
  line over the last `len` bars, evaluated at the current bar (offset 0). Its
  na-in-window rule is pine_ta's documented model.
* The source's `len` input shadows nothing in Pine but would shadow the Python
  builtin, so the value is read out of `params` into a differently named local
  before any `len(...)` call.
* `plot` / `plotshape` / `alertcondition` and `close_price = close[0]` are
  display-only; `close_price` is a plain alias for `close` and is transcribed
  as such into the regression source.
* The `/*backtest` header declares period 4h on Futures_Binance BTC_USDT; its
  `basePeriod: 15m` is the host's intrabar granularity for filling 4h bars, and
  its date window is extraction metadata, not an `input.time` filter, so no
  data is trimmed.
* Leverage, margin, liquidation, funding and the venue's contract-step rounding
  are not modelled (PINE_SEMANTICS.md 1.6 measures the rounding separately).
"""
import numpy as np
import pandas as pd
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


def _hma3(weekly_close: pd.Series, length: int) -> pd.Series:
    """The source's `hma3` over weekly closes, using the global `length`.

    `p = length/2` is Pine integer division for two integer operands; the three
    inner lengths are then p/3, p/2 and p, each also integer-divided.
    """
    p = length // 2
    inner_lengths = (p // 3, p // 2, p)
    if min(inner_lengths) < 1:
        return pd.Series(np.full(len(weekly_close), np.nan), index=weekly_close.index)
    inner = (
        ta.pine_wma(weekly_close, inner_lengths[0]) * 3
        - ta.pine_wma(weekly_close, inner_lengths[1])
        - ta.pine_wma(weekly_close, inner_lengths[2])
    )
    return ta.pine_wma(inner, p)


class SMEasyStock_dd4dab(PinePortBase, IStrategy):
    source_id = "SM_dd4dabf98f22dbdf"
    source_file = "Easy-stock.md"
    timeframe = "4h"
    can_short = True
    source_defaults: dict = {"tf10": "W", "length": 24, "shift": 1, "len": 100}
    # study(...), not strategy(...): Pine's documented defaults apply.
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    # No strategy.close / strategy.exit / stop / limit / trail anywhere in the
    # source -- not even a commented-out one.
    source_reproduce_stops = False
    source_mintick = 0.1
    source_fidelity_notes = [
        "Converter-appended order block (PINE_SEMANTICS.md 1.17): the file declares "
        "study(), and the two strategy.entry calls at the end are an appended block "
        "added by the publishing host (fmz.com/strategy/352918). It does not compile "
        "on TradingView; the host's Pine dialect is the behaviour reproduced here.",
        "`buy`/`sell` are crossover/crossunder calls -- plain booleans, not the "
        "`? -1 : 0` shape -- so no integer truthiness needed preserving and nothing "
        "was rewritten as `== 1`. `if / else if` is kept as if/elif; the two "
        "conditions are mutually exclusive, so it changes no fill.",
        "hma3 ignores its own arguments: its body reads the globals `length` and "
        "`close`. It is transcribed that way, so changing the Shift/Period inputs "
        "affects it exactly as in the source.",
        "hma3 is not the textbook Hull MA (it uses p/3, p/2 and p in the inner WMAs, "
        "not the hma() two-WMA form); it is reproduced literally rather than replaced "
        "by pine_ta.pine_hma.",
        "`a = security(syminfo.tickerid, tf10, hma(close, length))` and its hma() are "
        "dropped: plot(a) is their only reader, and neither the entries nor the "
        "alertconditions read either of them.",
        "The weekly alignment of `b` is a modelling choice, not a source statement: "
        "security() with Pine v4's default barmerge.lookahead_off exposes, inside week "
        "W, the expression evaluated on the last COMPLETED weekly bar (week W-1), and "
        "the source's `[shift]` then steps one further weekly bar back; the port "
        "aligns hma3 of the frame's weekly closes shifted by `1 + shift` weekly bars. "
        "See blockers: the boundary bar and the alternative reading of the shift "
        "differ by one weekly bar.",
        "Weekly bars use pandas' W-SUN grouping (Monday 00:00 to Sunday 24:00 UTC), "
        "the `\"W\"` boundary Pine uses on Futures_Binance BTC_USDT; the weekly "
        "boundary is itself a parity risk (PINE_SEMANTICS.md 3.4).",
        "The weekly closes are formed from this frame's own closes, so the final, "
        "still-open week is partial; the `1 + shift` alignment keeps it out of every "
        "value of `b`, which is also what keeps `b[t]` causal.",
        "linreg(close, 100, 0) is pine_ta.pine_linreg (last `len` bars, offset 0, "
        "endpoint value); its na-in-window rule is pine_ta's documented model.",
        "The input named `len` would shadow the Python builtin, so it is read into a "
        "differently named local before any len(...) call; the input name is kept in "
        "source_defaults for traceability.",
        "There is no exit of any kind -- no strategy.close, no strategy.exit, not "
        "even a commented-out one -- so source_reproduce_stops is False and a "
        "position is left only by the opposite entry (a reverse fill).",
        "The `/*backtest` header's period 4h is the strategy timeframe; its "
        "basePeriod: 15m is the host's intrabar granularity and its date window is "
        "extraction metadata, not an input.time filter, so no data is trimmed.",
        "Leverage, margin, liquidation, funding and the venue's contract-step "
        "rounding are not modelled (PINE_SEMANTICS.md 1.6 measures the rounding "
        "separately).",
    ]

    def pine_indicators(self, dataframe, params):
        close = dataframe["close"]
        # `len` is the source's input name; keep it out of the builtin's way.
        regression_length = int(params["len"])
        weekly_length = int(params["length"])
        weekly_shift = int(params["shift"])

        linear_reg = ta.pine_linreg(close, regression_length, 0)

        # `b = security(syminfo.tickerid, tf10, hma3(close, length)[shift])`
        index = pd.DatetimeIndex(dataframe.index)
        if index.tz is not None:
            # Pine's weekly boundary on Futures_Binance BTC_USDT is UTC midnight;
            # to_period would otherwise drop the offset (and emit a warning).
            index = index.tz_convert("UTC").tz_localize(None)
        weeks = index.to_period("W-SUN")
        weekly_close = close.groupby(weeks).last()
        weekly_hma3 = _hma3(weekly_close, weekly_length)
        # lookahead_off exposes the last completed weekly bar inside week W, and
        # the source's [shift] steps one further weekly bar back.
        aligned = weekly_hma3.shift(1 + weekly_shift).reindex(weeks).to_numpy()
        series_b = pd.Series(aligned, index=dataframe.index, dtype=float)

        dataframe["pine_linear_reg"] = linear_reg
        dataframe["pine_b"] = series_b
        dataframe["pine_long_condition"] = ta.pine_crossover(linear_reg, series_b)
        dataframe["pine_short_condition"] = ta.pine_crossunder(linear_reg, series_b)
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "long_condition": dataframe["pine_long_condition"].to_numpy(),
            "short_condition": dataframe["pine_short_condition"].to_numpy(),
        }

    def pine_script(self, broker, i, ctx):
        # if buy
        #     strategy.entry("buy", strategy.long)
        # else if sell
        #     strategy.entry("sell", strategy.short)
        if ctx["long_condition"][i]:
            broker.entry("buy", "long")
        elif ctx["short_condition"][i]:
            broker.entry("sell", "short")
