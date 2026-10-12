"""Port of sources/SM_1dbd847b34675d31.pine (batch_001/BRAHMASTRA.md).

Pine v4. The file declares `study("BRAHMASTRA", ...)`, NOT `strategy(...)`: the
two `strategy.entry` calls at the bottom are an order block APPENDED to the
indicator by the converter site that published it (fmz.com/strategy/362870,
named in the md's Detail link). Pine does not compile `strategy.entry` inside
`study()`, so the "original strategy" is the indicator PLUS that appended block,
and the trading behaviour it defines is entry-only.

The indicator is capissimo's two-module script. Only the HMA-Kahlman trend
module feeds the appended entries; the Trendlines module draws lines and is
order-free:

    hma(x, p) => wma((2 * wma(x, p / 2)) - wma(x, p), round(sqrt(p)))
    hma3()    => p = length/2,
                 wma(wma(close, p/3)*3 - wma(close, p/2) - wma(close, p), p)

    kahlman(x, g) =>
        kf = 0.0
        dk = x - nz(kf[1], x)
        smooth = nz(kf[1],x) + dk*sqrt(g*2)
        velo = 0.0
        velo := nz(velo[1],0) + (g*dk)
        kf := smooth+velo

    a = k ? kahlman(hma(price, length), gain) : hma(price, length)
    b = k ? kahlman(hma3(),            gain) : hma3()
    crossup = b > a and b[1] < a[1]
    crossdn = a > b and a[1] < b[1]

    if crossup
        strategy.entry("Enter Long", strategy.long)
    else if crossdn
        strategy.entry("Enter Short", strategy.short)

`a` and `b` are the Kahlman-filtered fast and slow Hull-type averages; the
entries are the two crossings of them on the closed bar. The two conditions
cannot both hold on one bar (`b > a` cannot coexist with `a > b`), so the
`else if` chain places at most one order per bar; it is kept as `elif` to
mirror Pine's short-circuit.

The returned value of `kahlman(x, g)` is the last assignment, `kf`. Each call
site keeps its own history for `kf[1]` / `velo[1]`, so `a` and `b` are
independent recursions even though they share the function.

There is NO exit of any kind in the source -- no `strategy.close`, no
`strategy.exit`, not even a commented-out one. A position is therefore only
ever left by the opposite entry, which the engine models as a reversal.
`pyramiding` keeps Pine's default of 0, so a repeated signal while already
positioned that way is ignored.

FIDELITY:

* `length = input(22)` is an INPUT int, and Pine v4 divides an input int by a
  const int as a FLOAT (`length/2` is 11.0, not 11). The two fractional lengths
  in `hma3()` -- `p/3` and `p/2` -- are therefore 3.6667 and 5.5, which Pine
  must cast back to an int for `wma`'s `length`. That cast's direction is not
  published, so this port uses round-half-away-from-zero (`_pine_int`), the
  convention the repository already fixed in SMOptimizedMultiTimeframeHma_64f8cf
  for the same HMA-family formula; truncation would give 3 and 5 instead of
  4 and 6. This is a MODELLED CHOICE and the port's largest fidelity risk --
  it changes `b`, and with it possibly which bars cross.
* `round(sqrt(p))` in `hma()` is explicit in the source and is reproduced as
  such (round(4.6904) = 5).
* `nz(kf[1], x)` / `nz(velo[1], 0)` are reproduced with Pine's semantics: na
  becomes the replacement, and if the replacement is itself na the recursion
  stays na. The Hull averages are na until their wma windows fill, so `a` and
  `b` are na -- and both crossings false -- over the warmup.
* The first bar's `f[1]` is na on both sides of every crossing test, and Pine
  makes a comparison with na false; pandas does the same.
* `k` (input, default true) really does switch between the Kahlman-filtered and
  the raw Hull series, so the port honours it rather than hardcoding the
  Kahlman branch.
* The source declares `study(...)`, not `strategy(...)`, so it carries no
  strategy() properties; Pine's documented defaults are what the source_*
  attributes record (fixed size 1, 0% commission, pyramiding 0, initial
  capital 1000000). On TradingView strategy.entry inside a study does not
  compile; the host named by the source's /*backtest header and the md's Detail
  link (fmz.com/strategy/362870) is what ran the appended block, and that
  platform's Pine dialect -- not TradingView -- is the behaviour this port
  reproduces.
* The whole Trendlines module (`trendline()`, `pivot()`, `pivot(...)`,
  `line.new/delete`, `slope_high1` / `slope_low1` and their `plot` calls) is
  reproduced as no code: its outputs are read only by `plot()` and by the
  colour ternaries, never by the entry conditions, and it places no order. It
  is computed by the source, so this is a deliberately recorded omission.
* `hkmod` (default true) is assigned and never read; the `labels`, `o`, `tlmod`
  and `l1` inputs drive plotshape/plot decoration only. None of them can change
  a trade. All are still recorded in `source_defaults`.
* No stop, limit or trail exit exists, so `source_reproduce_stops` is False.
* The header's backtest window (2022-04-12 to 2022-05-11) is extraction
  metadata, not an `input.time` filter, so no data is trimmed. The header's
  `basePeriod: 15m` is the host's intrabar granularity for filling 2h bars, not
  the strategy's period.
* Leverage, margin, liquidation, funding and the venue's contract-step rounding
  are not modelled.
"""
import math

import numpy as np
import pandas as pd
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


def _pine_int(value: float) -> int:
    """Pine's implicit float -> int cast: round half away from zero.

    Same convention (and same wording) as SMOptimizedMultiTimeframeHma_64f8cf,
    which had to settle the identical `length/2`, `length/3` question for the
    HMA family. It is a modelling choice, not a published rule.
    """
    return int(math.floor(abs(value) + 0.5)) * (1 if value >= 0 else -1)


def _kahlman(source: pd.Series, gain: float) -> pd.Series:
    """Pine `kahlman(x, g)` from the source, returning `kf`.

    One instance per call site, which is what Pine does for a function's local
    series: `nz(kf[1], x)` is the previous bar's filter value, or this bar's `x`
    when that is na (including on the first bar), `nz(velo[1], 0)` the previous
    bar's velocity, or 0. An na `x` propagates through the whole recursion.
    """
    values = source.to_numpy(dtype=float)
    out = np.full(len(values), np.nan)
    previous_kf = np.nan
    previous_velo = np.nan
    root = math.sqrt(gain * 2.0)
    for i, value in enumerate(values):
        base = previous_kf if not np.isnan(previous_kf) else value
        dk = value - base
        smooth = base + dk * root
        velo = (previous_velo if not np.isnan(previous_velo) else 0.0) + gain * dk
        kf = smooth + velo
        out[i] = kf
        previous_kf = kf
        previous_velo = velo
    return pd.Series(out, index=source.index, dtype=float)


class SMBrahmastra_1dbd84(PinePortBase, IStrategy):
    source_id = "SM_1dbd847b34675d31"
    source_file = "BRAHMASTRA.md"
    timeframe = "2h"
    can_short = True
    # Input defaults, exactly as written in the source.
    source_defaults: dict = {
        "price": "hl2",
        "hkmod": True,
        "length": 22,
        "k": True,
        "gain": 0.7,
        "labels": True,
        "o": True,
        "tlmod": True,
        "l1": 2,
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
        "Fractional wma lengths. `length = input(22)` is an INPUT int, and Pine "
        "v4 divides an input int by a const int as a float, so hma3()'s `p/3` "
        "and `p/2` are 3.6667 and 5.5 -- values Pine must cast back to int for "
        "wma's `length`. The cast's direction is unpublished; this port uses "
        "round-half-away-from-zero (_pine_int), the convention already fixed in "
        "SMOptimizedMultiTimeframeHma_64f8cf for the same HMA-family formula. "
        "Truncation would give 3 and 5 instead of 4 and 6, changing `b` and "
        "possibly which bars cross. MODELLED CHOICE, unresolved without platform "
        "comparison -- the port's largest fidelity risk.",
        "`round(sqrt(p))` inside hma() is explicit in the source (22 -> 5) and is "
        "reproduced as such.",
        "kahlman() is a recursive filter over the Hull output, and the port "
        "reproduces Pine's nz() semantics literally: `nz(kf[1], x)` takes the "
        "previous bar's kf, or this bar's x when that is na (first bar, or any "
        "bar whose x is na); `nz(velo[1], 0)` takes the previous velocity or 0. "
        "An na x propagates, so a and b are na over the wma warmup and both "
        "crossings are false there.",
        "Each kahlman() call site keeps its own history, which is how Pine "
        "scopes a function's local series; the port creates one recursion per "
        "call, so `a` and `b` do not share state.",
        "`k` (input, default true) switches between the Kahlman-filtered and the "
        "raw Hull series; the port honours the input instead of hardcoding the "
        "default branch.",
        "The whole Trendlines module is reproduced as no code. Its outputs "
        "(high_point1, low_point1, slope_high1, slope_low1) are read only by "
        "plot() and by colour ternaries -- never by the entry conditions -- and "
        "it places no order. Computed by the source, deliberately omitted here.",
        "`hkmod` (default true) is assigned and never read by the source; "
        "`labels`, `o`, `tlmod` and `l1` only drive plotshape/plot decoration. "
        "None can change a trade; all are still recorded in source_defaults.",
        "The two crossing tests use `[1]` (the previous bar), and Pine makes a "
        "comparison with na false; pandas behaves the same, so the first bar "
        "never signals.",
        "The source declares study(...), not strategy(...), so no strategy() "
        "properties exist and Pine's documented defaults are used: "
        "default_qty_type fixed, default_qty_value 1, commission 0%, pyramiding "
        "0, initial capital 1000000 USD. On TradingView strategy.entry inside a "
        "study does not compile; the host named by the source's /*backtest "
        "header and the md's Detail link (fmz.com/strategy/362870) is what ran "
        "the appended block, and that platform's Pine dialect -- not "
        "TradingView -- is the original behaviour this port reproduces.",
        "The source has no exit of any kind: no strategy.close, no "
        "strategy.exit, no stop or limit order, and no commented-out exit line. "
        "A position is only left by the opposite entry, which the engine models "
        "as a reverse fill (close the old side, open the new one). "
        "source_reproduce_stops is False accordingly.",
        "The md's prose describes a trend-line selection process (strength by "
        "touch count, one line per direction). None of that is in the trading "
        "path: the file's own `line.*` calls only draw, and the appended block "
        "enters on the HMA-Kahlman crossings. The code is followed.",
        "The backtest window in the header (2022-04-12 to 2022-05-11) is "
        "extraction metadata, not an input.time filter, so the port runs on "
        "whatever range the caller supplies.",
        "Leverage, margin, liquidation, funding and the venue's contract-step "
        "rounding are not modelled; the chain verifier measures the rounding "
        "separately (PINE_SEMANTICS.md 1.6).",
    ]

    @staticmethod
    def _hma(source: pd.Series, length: float) -> pd.Series:
        # wma((2 * wma(x, p / 2)) - wma(x, p), round(sqrt(p)))
        inner = 2.0 * ta.pine_wma(source, _pine_int(length / 2)) - ta.pine_wma(
            source, _pine_int(length)
        )
        return ta.pine_wma(inner, _pine_int(math.sqrt(length)))

    @staticmethod
    def _hma3(close: pd.Series, length: float) -> pd.Series:
        # p = length/2; wma(wma(close, p/3)*3 - wma(close, p/2) - wma(close, p), p)
        p = length / 2.0
        inner = (
            ta.pine_wma(close, _pine_int(p / 3.0)) * 3.0
            - ta.pine_wma(close, _pine_int(p / 2.0))
            - ta.pine_wma(close, _pine_int(p))
        )
        return ta.pine_wma(inner, _pine_int(p))

    def pine_indicators(self, dataframe, params):
        price = ta.pine_source(dataframe, str(params["price"]))
        gain = float(params["gain"])
        length = params["length"]
        use_kahlman = bool(params["k"])

        raw_a = self._hma(price, length)
        raw_b = self._hma3(dataframe["close"], length)
        a = _kahlman(raw_a, gain) if use_kahlman else raw_a
        b = _kahlman(raw_b, gain) if use_kahlman else raw_b

        dataframe["pine_a"] = a
        dataframe["pine_b"] = b
        # crossdn = a > b and a[1] < b[1]
        dataframe["pine_crossdn"] = (a > b) & (a.shift(1) < b.shift(1))
        # crossup = b > a and b[1] < a[1]
        dataframe["pine_crossup"] = (b > a) & (b.shift(1) < a.shift(1))
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "crossup": dataframe["pine_crossup"].to_numpy(),
            "crossdn": dataframe["pine_crossdn"].to_numpy(),
        }

    def pine_script(self, broker, i, ctx):
        # if crossup
        #     strategy.entry("Enter Long", strategy.long)
        # else if crossdn
        #     strategy.entry("Enter Short", strategy.short)
        if ctx["crossup"][i]:
            broker.entry("Enter Long", "long")
        elif ctx["crossdn"][i]:
            broker.entry("Enter Short", "short")
