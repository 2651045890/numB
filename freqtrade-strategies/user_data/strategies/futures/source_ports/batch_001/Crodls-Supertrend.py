"""Port of sources/SM_cb7fb20985dab404.pine (batch_001/Crodls-Supertrend.md).

Pine v5. The file declares an INDICATOR -- `indicator("Crodl's Supertrend",
overlay=true, timeframe="", timeframe_gaps=true)` -- and a converter tool
appended an order block to it (PINE_SEMANTICS.md 1.17). Pine v5 does not compile
`strategy.entry` inside an `indicator()`, so the "original strategy" is the
indicator PLUS the appended block, and the trading behaviour it defines is
entry-only:

    if long
        strategy.entry("Enter Long", strategy.long)
    else if short
        strategy.entry("Enter Short", strategy.short)

The indicator stacks three SuperTrends, a 200 EMA, a signed volume-delta sum
and a stochastic:

    [supertrend1, direction1] = ta.supertrend(3.0, 12)
    [supertrend2, direction2] = ta.supertrend(2.0, 11)
    [supertrend3, direction3] = ta.supertrend(1.0, 10)
    out = ta.ema(close, 200)
    t = math.sum(close > close[1] ? volume*(close-close[1])
                 : close < close[1] ? volume*(close-close[1]) : 0, 13)
    k = ta.sma(ta.stoch(close, high, low, 14), 1)
    d = ta.sma(k, 3)
    stochbuy  = float(k) < 30 and ta.crossover(k, d)
    stochsell = float(k) > 70 and ta.crossover(d, k)

    long  = ((((direction1<0 and direction2<0) or (direction2<0 and direction3<0)
               and (direction1<0 or direction3<0)) and open > out) and t > 0)
            and stochbuy
    short = the same with every `<` flipped to `>`, `t > 0` to `t < 0`, and
            stochbuy to stochsell

`direction` is -1 in an up trend and +1 in a down trend, and `out` is the 200
EMA, so the long wants at least two of the three SuperTrends up with the third
not against it, price above the EMA, net positive volume delta, and a
stochastic crossing up from below 30. The `else if` is kept as `elif` to mirror
Pine's short-circuit even though the two conditions cannot both hold.

There is NO exit of any kind in the source -- no `strategy.close`, no
`strategy.exit`, and not even a commented-out one. A position is therefore only
ever left by the opposite entry, which the engine models as a reversal.
`pyramiding` keeps Pine's default of 0, so a repeated signal while already
positioned that way is ignored.

FIDELITY:

* `ta.supertrend` is a Pine built-in whose internals TradingView does not
  execute under our control. This port reproduces the equivalent implementation
  published in the Pine v5 Reference (src = hl2, bands = hl2 +- factor *
  ta.atr(atrPeriod), previous bands seeded with nz(), the documented direction
  recursion, and Pine's na-comparison rules), using the same local helper as
  the repository's earlier SuperTrend ports `SMSuperTrend_ad38c8` and
  `SM3SupertrendAddInThisSingleScript_127691` rather than re-deriving it. The
  SuperTrend lines and every `direction` flip are therefore a MODELLED result,
  not certified equivalence -- this is the port's dominant gap.
* `ta.stoch(close, high, low, 14)` is not in pine_ta, so it is written out from
  the Pine definition: `100 * (close - lowest(low, length)) / (highest(high,
  length) - lowest(low, length))`, built on pine_lowest/pine_highest. The
  `ta.sma(..., smoothK=1)` and `ta.sma(k, 3)` calls are kept as pine_sma with
  the source's parameters rather than folded away.
* `math.sum(..., 13)` is a rolling sum; pine_ta's `pine_sum` is used (na until
  the window is full, matching Pine's math.sum). The nested ternary is
  transcribed literally: both price branches carry the SAME expression
  `volume * (close - close[1])` (it is signed), and the fall-through is 0.
* `m = ta.sma(t, l_ma)` is computed by the source and NEVER used -- dead code.
  It is computed here too and kept as a ledger column, and likewise never read.
* `ma(source, length, type)` (the switch-based MA selector) and
  `smoothingLine = ma(out, smoothingLength, typeMA)` feed only a
  `display=display.none` plot, so they are display-only and dropped; `out`
  itself IS read by the entry conditions and is computed.
* Every `plot` / `plotshape` / `fill` / `alertcondition` call (the SuperTrend
  lines, the hidden `bodyMiddle` plots, the EMA, the smoothing line, the signal
  labels, the alerts) is display- or alert-only and carries no trade meaning;
  dropped. `offset` exists only to displace those plots and places no order.
* `ta.atr` is `ta.rma(ta.tr(true), atrPeriod)` with pine_ta's documented Wilder
  seeding (SMA of the first `atrPeriod` true ranges), an unpublished
  TradingView rule; PINE_SEMANTICS.md 3.7 records that pine_ta's `pine_tr`
  gives the first bar `high-low` where Pine's default `ta.tr` is na, shifting
  the ATR seed -- and hence every SuperTrend band -- by one bar. Recorded, not
  corrected. It cannot move a signal here: `out` is a 200-bar EMA, so nothing
  can fire in the affected region.
* The `ta.ema` seed is the modelled first-observation seed (PINE_SEMANTICS.md
  3.1); TradingView does not publish its own.
* The source declares `indicator(...)`, so no strategy() properties exist and
  Pine's documented defaults apply: fixed size 1, 0% commission, pyramiding 0,
  initial capital 1000000 USD.
* MD-vs-SOURCE: the md front matter names the author as "ChaoZhang"; the
  source file's own header is the vendor banner "Visit Crodl.com for our
  Premium Indicators". The md records the fmz uploader, the source the
  indicator vendor. No effect on behaviour; recorded, not reconciled. The md
  argument table matches the source's inputs exactly (Factor3 default `true`
  in the table is the boolean-coerced 1.0 the source declares). The md's
  embedded source block is verbatim identical to the .pine source.
* The header's backtest window (2022-05-05 to 2022-05-11) is extraction
  metadata, not an `input.time` filter, so no data is trimmed. The header's
  `basePeriod: 15m` is the host's intrabar granularity for filling 30m bars,
  not the strategy's period; the header's `period: 30m` is what `timeframe`
  uses.
* No stop, limit or trail exit exists, so `source_reproduce_stops` is False.
* Leverage, margin, liquidation, funding and the venue's contract-step rounding
  are not modelled (PINE_SEMANTICS.md 1.6 measures the rounding separately).
"""
import numpy as np
import pandas as pd
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


def _nz(value: float) -> float:
    """Pine `nz`: an na value becomes 0."""
    return 0.0 if value is None or np.isnan(value) else float(value)


def _pine_gt(left: float, right: float) -> bool:
    """Pine `>`: a comparison with an na operand is false."""
    if np.isnan(left) or np.isnan(right):
        return False
    return bool(left > right)


def _pine_lt(left: float, right: float) -> bool:
    """Pine `<`: a comparison with an na operand is false."""
    if np.isnan(left) or np.isnan(right):
        return False
    return bool(left < right)


def pine_supertrend(dataframe: pd.DataFrame, factor: float, atr_period: int):
    """Pine `ta.supertrend(factor, atrPeriod)` -> (supertrend, direction).

    The equivalent implementation from the Pine v5 Reference, reproduced with
    Pine's na rules. `direction` is -1 in an up trend and +1 in a down trend.
    Same modelled helper as SMSuperTrend_ad38c8; kept local to the port because
    the shared pine_ta module is frozen.
    """
    src = (dataframe["high"] + dataframe["low"]) / 2.0
    atr = ta.pine_atr(dataframe, atr_period)
    raw_upper = (src + factor * atr).to_numpy(dtype=float)
    raw_lower = (src - factor * atr).to_numpy(dtype=float)
    atr_values = atr.to_numpy(dtype=float)
    close = dataframe["close"].to_numpy(dtype=float)

    size = len(dataframe)
    upper = np.full(size, np.nan)
    lower = np.full(size, np.nan)
    supertrend = np.full(size, np.nan)
    direction = np.ones(size, dtype=float)

    for i in range(size):
        previous_close = close[i - 1] if i >= 1 else np.nan
        prev_lower = _nz(lower[i - 1]) if i >= 1 else 0.0
        prev_upper = _nz(upper[i - 1]) if i >= 1 else 0.0

        lower[i] = (
            raw_lower[i]
            if _pine_gt(raw_lower[i], prev_lower) or _pine_lt(previous_close, prev_lower)
            else prev_lower
        )
        upper[i] = (
            raw_upper[i]
            if _pine_lt(raw_upper[i], prev_upper) or _pine_gt(previous_close, prev_upper)
            else prev_upper
        )

        prev_supertrend = supertrend[i - 1] if i >= 1 else np.nan
        if i == 0 or np.isnan(atr_values[i - 1]):
            current = 1.0
        elif not np.isnan(prev_supertrend) and prev_supertrend == prev_upper:
            current = -1.0 if _pine_gt(close[i], upper[i]) else 1.0
        else:
            current = 1.0 if _pine_lt(close[i], lower[i]) else -1.0

        direction[i] = current
        supertrend[i] = lower[i] if current == -1.0 else upper[i]

    return (
        pd.Series(supertrend, index=dataframe.index, dtype=float),
        pd.Series(direction, index=dataframe.index, dtype=float),
    )


def pine_stoch(source: pd.Series, high: pd.Series, low: pd.Series,
               length: int) -> pd.Series:
    """Pine `ta.stoch(source, high, low, length)`.

    `100 * (source - lowest(low, length)) / (highest(high, length) -
    lowest(low, length))`. Written out because pine_ta has no ta.stoch.
    """
    lowest = ta.pine_lowest(low, length)
    highest = ta.pine_highest(high, length)
    return 100.0 * (source - lowest) / (highest - lowest)


class SMCrodlsSupertrend_cb7fb2(PinePortBase, IStrategy):
    source_id = "SM_cb7fb20985dab404"
    source_file = "Crodls-Supertrend.md"
    timeframe = "30m"
    can_short = True
    # Input defaults exactly as written. `src` is Pine's `input.source`; the
    # string name is the default the source declares and is resolved through
    # pine_ta.pine_source. `offset` and `typeMA`/`smoothingLength` only drive
    # display plots and place no order.
    source_defaults: dict = {
        "atrPeriod1": 12, "factor1": 3.0,
        "atrPeriod2": 11, "factor2": 2.0,
        "atrPeriod3": 10, "factor3": 1.0,
        "len": 200, "src": "close", "offset": 0,
        "l": 13, "l_ma": 7,
        "periodK": 14, "smoothK": 1, "periodD": 3,
        "typeMA": "SMA", "smoothingLength": 5,
    }
    # indicator(...), not strategy(...): Pine's documented defaults apply.
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    # No strategy.close / strategy.exit / stop / limit / trail anywhere.
    source_reproduce_stops = False
    source_mintick = 0.1
    source_fidelity_notes = [
        "Converter-appended source: the file declares an indicator "
        "(`indicator(\"Crodl's Supertrend\", ...)`) and the tool appended `if "
        "long / strategy.entry(\"Enter Long\", strategy.long) else if short / "
        "strategy.entry(\"Enter Short\", strategy.short)`. The port reproduces "
        "the indicator PLUS that appended block, i.e. entry-only behaviour "
        "(PINE_SEMANTICS.md 1.17).",
        "The appended block's conditions are explicit boolean comparisons "
        "(`direction1 < 0 and ...`), not the `? -1 : 0` integer this family "
        "usually carries: the -1/+1 values are compared, never used as a bare "
        "truth value, so the 1.17 truthiness trap does not apply.",
        "ta.supertrend is a Pine built-in. This port uses the Pine v5 "
        "Reference's equivalent implementation (hl2, +- factor*ta.atr, "
        "nz-seeded previous bands, the documented direction recursion, Pine na "
        "rules), copied from the repository's SMSuperTrend_ad38c8 helper. The "
        "three SuperTrend lines and every direction flip are a MODELLED "
        "result, not certified equivalence -- the port's dominant gap.",
        "ta.stoch is not in pine_ta, so it is written out from the Pine "
        "definition `100*(source - lowest(low,length))/(highest(high,length) - "
        "lowest(low,length))` on pine_lowest/pine_highest. The smoothing calls "
        "ta.sma(stoch, smoothK) and ta.sma(k, periodD) are kept as pine_sma "
        "with the source's parameter values.",
        "math.sum(..., 13) is a rolling sum; pine_ta's pine_sum is used (na "
        "until the window is full, as Pine's math.sum is). The nested ternary "
        "is transcribed literally -- both price branches carry the same signed "
        "expression volume*(close-close[1]), and the fall-through is 0.",
        "m = ta.sma(t, l_ma) is DEAD CODE: the source computes it and never "
        "reads it. Computed here too and kept as a ledger column, likewise "
        "never read.",
        "The `ma()` switch helper and `smoothingLine = ma(out, "
        "smoothingLength, typeMA)` feed only a display=display.none plot and "
        "are dropped; `out` itself is read by the entry conditions and is "
        "computed. `offset` only displaces display plots.",
        "No exit of any kind exists: no strategy.close, no strategy.exit, no "
        "stop or limit, no commented-out exit line. A position is only left by "
        "the opposite entry (a reverse fill); source_reproduce_stops is False.",
        "The source declares indicator(...), so no strategy() properties exist "
        "and Pine's documented defaults are used: default_qty_type fixed, "
        "default_qty_value 1, commission 0%, pyramiding 0, initial capital "
        "1000000 USD.",
        "ta.atr is ta.rma(ta.tr(true), atrPeriod) with pine_ta's Wilder "
        "seeding; PINE_SEMANTICS.md 3.7 records that pine_tr differs from "
        "Pine's default ta.tr on the first bar (high-low instead of na), "
        "shifting the ATR seed and every SuperTrend band by one bar. Recorded, "
        "not corrected; it cannot move a signal here because `out` is a "
        "200-bar EMA, so nothing fires inside the affected region.",
        "The ta.ema seed is the modelled first-observation seed "
        "(PINE_SEMANTICS.md 3.1); TradingView does not publish its own.",
        "MD-vs-SOURCE: the md names the author 'ChaoZhang'; the source header "
        "is the vendor banner 'Visit Crodl.com for our Premium Indicators'. "
        "Recorded, not reconciled.",
        "`plot` / `plotshape` / `alertcondition` are display- or alert-only "
        "and place no order; dropped.",
        "The header's backtest window is extraction metadata, not an "
        "input.time filter, so the port runs on whatever range the caller "
        "supplies; basePeriod: 15m is the host's intrabar fill granularity, "
        "not the strategy's period.",
        "Leverage, margin, liquidation, funding and the venue's contract-step "
        "rounding are not modelled (PINE_SEMANTICS.md 1.6).",
    ]

    def pine_indicators(self, dataframe, params):
        close = dataframe["close"]
        open_ = dataframe["open"]
        high = dataframe["high"]
        low = dataframe["low"]
        volume = dataframe["volume"]

        _, direction1 = pine_supertrend(
            dataframe, float(params["factor1"]), int(params["atrPeriod1"])
        )
        _, direction2 = pine_supertrend(
            dataframe, float(params["factor2"]), int(params["atrPeriod2"])
        )
        _, direction3 = pine_supertrend(
            dataframe, float(params["factor3"]), int(params["atrPeriod3"])
        )

        # out = ta.ema(src, len); src defaults to close.
        out = ta.pine_ema(ta.pine_source(dataframe, str(params["src"])), int(params["len"]))

        # t = math.sum(close > close[1] ? volume*(close-close[1])
        #              : close < close[1] ? volume*(close-close[1]) : 0, l)
        change = close - close.shift(1)
        signed_volume = volume * change
        term = np.where(
            close > close.shift(1),
            signed_volume,
            np.where(close < close.shift(1), signed_volume, 0.0),
        )
        term = pd.Series(term, index=dataframe.index, dtype=float)
        t = ta.pine_sum(term, int(params["l"]))
        # m = ta.sma(t, l_ma) -- dead, computed for the record only.
        m = ta.pine_sma(t, int(params["l_ma"]))

        # k = ta.sma(ta.stoch(close, high, low, periodK), smoothK); d = ta.sma(k, periodD)
        stoch_raw = pine_stoch(close, high, low, int(params["periodK"]))
        k = ta.pine_sma(stoch_raw, int(params["smoothK"]))
        d = ta.pine_sma(k, int(params["periodD"]))

        # stochbuy = float(k) < 30 and ta.crossover(k, d)
        # stochsell = float(k) > 70 and ta.crossover(d, k)
        stochbuy = (k < 30.0) & ta.pine_crossover(k, d)
        stochsell = (k > 70.0) & ta.pine_crossover(d, k)

        # long = ((((direction1<0 and direction2<0) or (direction2<0 and
        #          direction3<0) and (direction1<0 or direction3<0)) and
        #          open > out) and t > 0) and stochbuy
        # `and` binds tighter than `or` in Pine, exactly as `&` does in Python,
        # so the grouping below is the source's own.
        long_cond = (
            (
                ((direction1 < 0) & (direction2 < 0))
                | ((direction2 < 0) & (direction3 < 0) & ((direction1 < 0) | (direction3 < 0)))
            )
            & (open_ > out)
            & (t > 0)
            & stochbuy
        )
        short_cond = (
            (
                ((direction1 > 0) & (direction2 > 0))
                | ((direction2 > 0) & (direction3 > 0) & ((direction1 > 0) | (direction3 > 0)))
            )
            & (open_ < out)
            & (t < 0)
            & stochsell
        )

        dataframe["pine_direction_1"] = direction1
        dataframe["pine_direction_2"] = direction2
        dataframe["pine_direction_3"] = direction3
        dataframe["pine_ema200"] = out
        dataframe["pine_t"] = t
        dataframe["pine_m"] = m
        dataframe["pine_k"] = k
        dataframe["pine_d"] = d
        dataframe["pine_stochbuy"] = stochbuy.fillna(False)
        dataframe["pine_stochsell"] = stochsell.fillna(False)
        dataframe["pine_long_condition"] = long_cond.fillna(False)
        dataframe["pine_short_condition"] = short_cond.fillna(False)
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "long_condition": dataframe["pine_long_condition"].to_numpy(),
            "short_condition": dataframe["pine_short_condition"].to_numpy(),
        }

    def pine_script(self, broker, i, ctx):
        # if long
        #     strategy.entry("Enter Long", strategy.long)
        # else if short
        #     strategy.entry("Enter Short", strategy.short)
        if ctx["long_condition"][i]:
            broker.entry("Enter Long", "long")
        elif ctx["short_condition"][i]:
            broker.entry("Enter Short", "short")
