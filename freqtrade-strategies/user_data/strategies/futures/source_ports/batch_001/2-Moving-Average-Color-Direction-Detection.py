"""Port of sources/SM_dd3397c876fc2469.pine (batch_001/2-Moving-Average-Color-Direction-Detection.md).

Pine v3 (`//@version=3`, `study(...)`), and the file declares a STUDY, not a
`strategy(...)`: the two `strategy.entry` calls at the bottom are an order
block APPENDED to the study by the converter site that published it
(fmz.com/strategy/364535, named in the md's Detail link). Pine v3 does not
compile `strategy.entry` inside `study()`, so the "original strategy" is the
study PLUS that appended block, and the trading behaviour it defines is
entry-only.

Two moving averages of the same close, each selected independently by type,
length and source, and an entry on the two orderings of THEIR cross:

    ma_series   = variant(ma_type,   ma_src,   ma_len)      # default SMA(20)
    ma_series_b = variant(ma_type_b, ma_src_b, ma_len_b)    # default SMA(8)

    if crossunder(ma_series, ma_series_b)
        strategy.entry("Enter Long", strategy.long)
    else if crossunder(ma_series_b, ma_series)
        strategy.entry("Enter Short", strategy.short)

which is a reversal system: `crossunder(a, b)` is `a < b and a[1] >= b[1]`, so
the LONG side fires when the 1-MA crosses BELOW the 2-MA and the SHORT side
when it crosses above. The two conditions exclude each other on a given bar (a
bar cannot have `ma < ma_b` and `ma_b < ma` at once), so the `else if` ordering
changes no fill; it is kept as if/elif for faithfulness.

`variant(type, src, len)` is transcribed in full -- all eleven selectable types
(SMA, EMA, WMA, VWMA, SMMA, DEMA, TEMA, HullMA, ZEMA, TMA, SSMA) plus the
source's fall-through to `sma`. The defaults select SMA for both averages, but
a caller overriding ma_type would otherwise silently get SMA.

There is NO exit of any kind in the source: no `strategy.close`, no
`strategy.exit`, not even a commented-out one. So `source_reproduce_stops` is
False and a position is only ever left by the opposite entry, which the engine
models as a reverse fill.

`study(...)` carries no strategy() properties, so Pine's documented defaults
apply: `default_qty_type` fixed, `default_qty_value` 1, commission 0%,
`pyramiding` 0, `initial_capital` 1000000 USD.

FIDELITY:

* Converter-appended source (PINE_SEMANTICS.md 1.17). The appended conditions
  are `crossunder(...)` calls, i.e. plain booleans, NOT the `? -1 : 0` shape:
  the "-1 is truthy, never rewrite it as == 1" trap does not arise here and no
  integer-valued column is involved. (The study itself does build a `direction`
  series that can be -1, but nothing in the trading path reads it -- see below.)
* `direction`, `direction_b`, `change_direction`, `pcol`, the `fill(...)` call
  and the seven `alertcondition(...)` calls are display-only: `direction` only
  colours the plots, and `reaction_ma_1` / `reaction_ma_2` are read by nothing
  else. They are dropped, which also removes any dependence on Pine v3's
  `rising()` / `falling()` builtins. `ma_1`, `ma_2` and `filling` gate only the
  plots and the fill; the corresponding defaults are therefore not carried in
  `source_defaults`, which holds exactly the inputs the entries read.
* `SMMA` is `variant_smoothed`, transcribed literally: `v5 := na(v5[1]) ?
  sma(src, len) : (v5[1]*(len-1) + src)/len` over a NON-`var` local whose
  `v5[1]` history is na on the first bar and stays na while `sma` is na, so it
  only starts recursing once the SMA window is full. That is Wilder's
  smoothing seeded with that first SMA -- the same recursion as
  pine_ta.pine_rma, but it is written out here because the source writes it out
  and because the na-in-window behaviour is then identical by construction.
* `SSMA` is Ehlers' SuperSmoother, transcribed with Pine's `nz()` on `src[1]`,
  `v9[1]` and `v9[2]`, so the first two bars are seeded with zeros exactly as
  the source seeds them.
* `HullMA` is `wma(2*wma(src, len/2) - wma(src, len), round(sqrt(len)))`. `len/2`
  is Pine's INTEGER division for two integer operands (the convention already
  recorded by this corpus's 72s-Adaptive-Hull-Moving-Average port), so len=20
  uses 10 and len=8 uses 4; `round(sqrt(len))` is pine_ta.pine_round, i.e. half
  away from zero, giving 4 for len=20 and 3 for len=8. TradingView does not
  publish the int-division rule in a form that can be checked against output,
  so the round-off is recorded here rather than hidden; with the default
  lengths (20 and 8, both even) the two readings coincide.
* `ema` / `wma` / `vwma` / `sma` are the pine_ta functions, whose na-in-window
  and (for `ema`) seeding rules are the documented parity risks of
  PINE_SEMANTICS.md 3.1/3.2. `VWMA` needs the volume series, which the port
  attaches to the source before calling pine_ta.pine_vwma.
* Every type arm is evaluated through the same window semantics, so the first
  `len` bars of `ma_series` are na and `crossunder` is false there (na compared
  with na is false in Pine, and `pine_crossunder` fills those bars with False).
* The file has NO `/*backtest` header, so it states no period at all. The
  corpus convention for the 91 header-less sources is the Freqtrade default
  `1h` (5 of them already have ports and all 5 declare "1h"); that is what this
  port declares, and it is a modelling choice, not something the source says.
* Leverage, margin, liquidation, funding and the venue's contract-step rounding
  are not modelled (PINE_SEMANTICS.md 1.6 measures the rounding separately).
"""
import math

import numpy as np
import pandas as pd
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


def _nan_series(index) -> pd.Series:
    return pd.Series(np.full(len(index), np.nan), index=index, dtype=float)


def _with_volume(source: pd.Series, volume: pd.Series) -> pd.Series:
    """pine_ta.pine_vwma reads its volume off `source.attrs['volume']`."""
    out = pd.Series(source.to_numpy(dtype=float), index=source.index, dtype=float)
    out.attrs["volume"] = pd.Series(
        volume.to_numpy(dtype=float), index=source.index, dtype=float
    )
    return out


def _variant_smoothed(source: pd.Series, length: int) -> pd.Series:
    """`variant_smoothed`: v5 := na(v5[1]) ? sma(src,len) : (v5[1]*(len-1)+src)/len."""
    smoothed = ta.pine_sma(source, length).to_numpy(dtype=float)
    values = source.to_numpy(dtype=float)
    out = np.full(len(values), np.nan)
    previous = np.nan  # v5[1] on the first bar: no history, hence na
    for i in range(len(values)):
        if np.isnan(previous):
            out[i] = smoothed[i]
        else:
            out[i] = (previous * (length - 1) + values[i]) / length
        previous = out[i]
    return pd.Series(out, index=source.index, dtype=float)


def _variant_supersmoother(source: pd.Series, length: int) -> pd.Series:
    """`variant_supersmoother`: Ehlers' SuperSmoother, with Pine's nz() seeding."""
    a1 = math.exp(-1.414 * 3.14159 / length)
    b1 = 2 * a1 * math.cos(1.414 * 3.14159 / length)
    c2 = b1
    c3 = (-a1) * a1
    c1 = 1 - c2 - c3
    values = source.to_numpy(dtype=float)
    out = np.full(len(values), np.nan)

    def _nz(value):
        return 0.0 if np.isnan(value) else float(value)

    for i in range(len(values)):
        source_previous = values[i - 1] if i >= 1 else np.nan
        ninth_previous = out[i - 1] if i >= 1 else np.nan
        ninth_previous_2 = out[i - 2] if i >= 2 else np.nan
        out[i] = (
            c1 * (values[i] + _nz(source_previous)) / 2
            + c2 * _nz(ninth_previous)
            + c3 * _nz(ninth_previous_2)
        )
    return pd.Series(out, index=source.index, dtype=float)


def _variant_doubleema(source: pd.Series, length: int) -> pd.Series:
    """`variant_doubleema`: 2*v2 - ema(v2, len)."""
    v2 = ta.pine_ema(source, length)
    return 2 * v2 - ta.pine_ema(v2, length)


def _variant_tripleema(source: pd.Series, length: int) -> pd.Series:
    """`variant_tripleema`: 3*(v2 - ema(v2,len)) + ema(ema(v2,len),len)."""
    v2 = ta.pine_ema(source, length)
    double = ta.pine_ema(v2, length)
    return 3 * (v2 - double) + ta.pine_ema(double, length)


def _variant_zerolagema(source: pd.Series, length: int) -> pd.Series:
    """`variant_zerolagema`: ema1 + (ema1 - ema2)."""
    ema1 = ta.pine_ema(source, length)
    ema2 = ta.pine_ema(ema1, length)
    return ema1 + (ema1 - ema2)


def _variant_hullma(source: pd.Series, length: int) -> pd.Series:
    """`variant(...)`'s HullMA arm: wma(2*wma(src,len/2) - wma(src,len), round(sqrt(len)))."""
    half = length // 2  # Pine integer division for two integer operands
    outer = int(ta.pine_round(math.sqrt(length)))
    if half < 1 or outer < 1:
        return _nan_series(source.index)
    return ta.pine_wma(2 * ta.pine_wma(source, half) - ta.pine_wma(source, length), outer)


def pine_variant(source: pd.Series, kind: str, length: int, volume: pd.Series) -> pd.Series:
    """The source's `variant(type, src, len)` dispatcher, transcribed."""
    if length < 1:
        return _nan_series(source.index)
    if kind == "EMA":
        return ta.pine_ema(source, length)
    if kind == "WMA":
        return ta.pine_wma(source, length)
    if kind == "VWMA":
        return ta.pine_vwma(_with_volume(source, volume), length)
    if kind == "SMMA":
        return _variant_smoothed(source, length)
    if kind == "DEMA":
        return _variant_doubleema(source, length)
    if kind == "TEMA":
        return _variant_tripleema(source, length)
    if kind == "HullMA":
        return _variant_hullma(source, length)
    if kind == "SSMA":
        return _variant_supersmoother(source, length)
    if kind == "ZEMA":
        return _variant_zerolagema(source, length)
    if kind == "TMA":
        return ta.pine_sma(ta.pine_sma(source, length), length)
    # `type=="SMA"` and the source's fall-through arm are both sma(src, len).
    return ta.pine_sma(source, length)


class SM2MovingAverageColorDirectionDetection_dd3397(PinePortBase, IStrategy):
    source_id = "SM_dd3397c876fc2469"
    source_file = "2-Moving-Average-Color-Direction-Detection.md"
    # The file has no /*backtest header and so states no period; the corpus
    # convention for header-less sources is Freqtrade's default "1h".
    timeframe = "1h"
    can_short = True
    # Exactly the inputs the two entries read (ma_1 / ma_2 / filling /
    # reaction_ma_* gate only plots, fill colour and alertconditions).
    source_defaults: dict = {
        "ma_type": "SMA",
        "ma_len": 20,
        "ma_src": "close",
        "ma_type_b": "SMA",
        "ma_len_b": 8,
        "ma_src_b": "close",
    }
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
        "added by the publishing host (fmz.com/strategy/364535). The source does not "
        "compile on TradingView; the host's Pine dialect is the behaviour reproduced "
        "here.",
        "The appended conditions are crossunder(...) calls -- plain booleans, not the "
        "`? -1 : 0` shape -- so 1.17's integer-truthiness trap does not arise and "
        "nothing was rewritten as `== 1`. The if/else-if is kept as if/elif although "
        "the two crossings are mutually exclusive on a bar.",
        "The entry is a REVERSAL cross: LONG on crossunder(ma_series, ma_series_b) "
        "and SHORT on crossunder(ma_series_b, ma_series), reproduced verbatim "
        "(pine_ta.pine_crossunder: a < b and a[1] >= b[1]).",
        "`variant(type, src, len)` is transcribed in full (SMA, EMA, WMA, VWMA, SMMA, "
        "DEMA, TEMA, HullMA, ZEMA, TMA, SSMA and the fall-through) even though the "
        "defaults select SMA for both averages, so that overriding ma_type does not "
        "silently fall back to SMA.",
        "SMMA is variant_smoothed written out literally (`na(v5[1]) ? sma(src,len) : "
        "(v5[1]*(len-1)+src)/len`); it is Wilder's recursion seeded by the first full "
        "SMA, which is what pine_ta.pine_rma computes, but the literal form keeps the "
        "na-in-window behaviour identical by construction.",
        "SSMA is Ehlers' SuperSmoother with Pine's nz() on src[1] / v9[1] / v9[2], so "
        "the first bars are seeded with zeros exactly as the source seeds them.",
        "HullMA uses `len/2`, read as Pine's integer division for two integer "
        "operands (the corpus convention from 72s-Adaptive-Hull-Moving-Average), and "
        "round(sqrt(len)) via pine_ta.pine_round (half away from zero). Both default "
        "lengths are even, so the alternative float-division reading coincides with "
        "this one; the round-off is recorded rather than hidden.",
        "`direction`, `direction_b`, `change_direction`, `pcol`, `fill(...)` and the "
        "seven alertcondition calls are display-only and dropped; with them goes any "
        "dependence on Pine v3's rising()/falling() builtins, which only coloured the "
        "plots via reaction_ma_1 / reaction_ma_2.",
        "`ma_1`, `ma_2` and `filling` gate only plots and the fill colour, so they are "
        "not carried in source_defaults; the defaults carried are exactly the inputs "
        "the entries read.",
        "There is no exit of any kind -- no strategy.close, no strategy.exit, not "
        "even a commented-out one -- so source_reproduce_stops is False and a "
        "position is left only by the opposite entry (a reverse fill).",
        "The file has NO /*backtest header, hence no period at all; '1h' is the "
        "corpus convention for header-less sources (all 5 such ports already on disk "
        "declare 1h) and is a modelling choice, not a source statement.",
        "ta.ema / ta.sma / ta.wma na-in-window and EMA seeding are pine_ta's "
        "documented models (PINE_SEMANTICS.md 3.1/3.2), unverified against the "
        "platform.",
        "Leverage, margin, liquidation, funding and the venue's contract-step "
        "rounding are not modelled (PINE_SEMANTICS.md 1.6 measures the rounding "
        "separately).",
    ]

    def pine_indicators(self, dataframe, params):
        volume = dataframe["volume"]
        ma_series = pine_variant(
            ta.pine_source(dataframe, str(params["ma_src"])),
            str(params["ma_type"]),
            int(params["ma_len"]),
            volume,
        )
        ma_series_b = pine_variant(
            ta.pine_source(dataframe, str(params["ma_src_b"])),
            str(params["ma_type_b"]),
            int(params["ma_len_b"]),
            volume,
        )
        dataframe["pine_ma_series"] = ma_series
        dataframe["pine_ma_series_b"] = ma_series_b
        dataframe["pine_long_condition"] = ta.pine_crossunder(ma_series, ma_series_b)
        dataframe["pine_short_condition"] = ta.pine_crossunder(ma_series_b, ma_series)
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "long_condition": dataframe["pine_long_condition"].to_numpy(),
            "short_condition": dataframe["pine_short_condition"].to_numpy(),
        }

    def pine_script(self, broker, i, ctx):
        # if crossunder(ma_series, ma_series_b)
        #     strategy.entry("Enter Long", strategy.long)
        # else if crossunder(ma_series_b, ma_series)
        #     strategy.entry("Enter Short", strategy.short)
        if ctx["long_condition"][i]:
            broker.entry("Enter Long", "long")
        elif ctx["short_condition"][i]:
            broker.entry("Enter Short", "short")
