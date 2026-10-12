"""Port of sources/SM_1276915b72e4d84c.pine (batch_001/3-Supertrend-Add-In-This-Single-Script.md).

Pine v5. The file declares `indicator(...)`, NOT `strategy(...)`: the two
`strategy.entry` calls at the bottom are an order block APPENDED to the
indicator by the converter site that published it (fmz.com/strategy/362457,
named in the md's Detail link). Pine v5 does not compile `strategy.entry`
inside `indicator()`, so the "original strategy" is the indicator PLUS that
appended block, and the trading behaviour it defines is entry-only.

Three SuperTrends on the same series, differing only in (factor, ATR length):

    [supertrend_1, direction_1] = ta.supertrend(1.0, 21)
    [supertrend_2, direction_2] = ta.supertrend(2.0, 14)
    [supertrend_3, direction_3] = ta.supertrend(3.0,  7)

    if direction_1 < 0 and direction_2 < 0 and direction_3 < 0
        strategy.entry("Enter Long", strategy.long)
    else if direction_1 > 0 and direction_2 > 0 and direction_3 > 0
        strategy.entry("Enter Short", strategy.short)

`direction` is -1 in an up trend and +1 in a down trend, so the long entry
needs all three SuperTrends pointing up and the short needs all three pointing
down; any disagreement places no order. The `else if` is kept as `elif` to
mirror Pine's short-circuit even though the two conditions cannot both hold.

There is NO exit of any kind in the source -- no `strategy.close`, no
`strategy.exit`, not even a commented-out one. A position is therefore only
ever left by the opposite entry, which the engine models as a reversal.
`pyramiding` keeps Pine's default of 0, so a repeated signal while already
positioned that way is ignored.

FIDELITY:

* `ta.supertrend` is a Pine built-in whose internals TradingView does not
  execute under our control. This port reproduces the equivalent implementation
  published in the Pine v5 Reference (src = hl2, bands = hl2 +- factor *
  ta.atr(atrPeriod), previous bands seeded with nz(), the documented direction
  recursion, and Pine's na-comparison rules), using the same local helper as
  the repository's earlier SuperTrend port `SMSuperTrend_ad38c8`
  (batch_011/超级趋势策略SuperTrend.py) rather than re-deriving it. The
  SuperTrend line and the bars on which the three directions flip are therefore
  a MODELLED result, not certified equivalence -- this is the port's dominant
  gap.
* `ta.atr` is `ta.rma(ta.tr(true), atrPeriod)` with pine_ta's documented Wilder
  seeding (SMA of the first `atrPeriod` true ranges), an unpublished
  TradingView rule (PINE_SEMANTICS.md 3.1/3.2).
* The source declares indicator(...), not strategy(...), so it carries no
  strategy() properties; Pine's documented defaults are what the source_*
  attributes record (fixed size 1, 0% commission, pyramiding 0, initial
  capital 1000000). On TradingView strategy.entry inside an indicator does not
  compile; the host named by the source's /*backtest header and the md's Detail
  link (fmz.com/strategy/362457) is what ran the appended block, and that
  platform's Pine dialect -- not TradingView -- is the behaviour this port
  reproduces.
* Every `plot(...)` and `fill(...)` call (the three SuperTrend lines, the three
  hidden `bodyMiddle` plots and the six fills) is display-only and carries no
  trade meaning; they are dropped.
* The header's backtest window (2022-05-03 to 2022-05-09) is extraction
  metadata, not an `input.time` filter, so no data is trimmed. The header's
  `basePeriod: 15m` is the host's intrabar granularity for filling 30m bars,
  not the strategy's period.
* No stop, limit or trail exit exists, so `source_reproduce_stops` is False.
* Leverage, margin, liquidation, funding and the venue's contract-step rounding
  are not modelled.
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


class SM3SupertrendAddInThisSingleScript_127691(PinePortBase, IStrategy):
    source_id = "SM_1276915b72e4d84c"
    source_file = "3-Supertrend-Add-In-This-Single-Script.md"
    timeframe = "30m"
    can_short = True
    # Input defaults exactly as written: (ATR Length, Factor) for each of the
    # three SuperTrends, in source order.
    source_defaults: dict = {
        "NEW1_atrPeriod": 21,
        "NEW1_factor": 1.0,
        "NEW2_atrPeriod": 14,
        "NEW2_factor": 2.0,
        "NEW3_atrPeriod": 7,
        "NEW3_factor": 3.0,
    }
    # indicator(...), not strategy(...): Pine's documented defaults apply.
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
        "ta.supertrend is a Pine built-in whose internals are not executed here. "
        "The port reproduces the equivalent implementation published in the Pine "
        "v5 Reference (src = hl2, bands = hl2 +- factor * ta.atr(atrPeriod), "
        "previous bands seeded with nz(), direction flipped on close vs the "
        "ratcheted band), reusing the same modelled helper as the repository's "
        "earlier SuperTrend port SMSuperTrend_ad38c8 rather than re-deriving it. "
        "All three SuperTrend lines and the bars on which their directions flip "
        "are therefore a modelled result, not certified equivalence; this is the "
        "port's dominant gap.",
        "The direction recursion's `prevSuperTrend == prevUpperBand` test and all "
        "band comparisons use Pine's na semantics (an na operand makes the "
        "comparison false, nz() replaces na with 0), which is what makes the "
        "bands defined from the first bar; a port that propagated na would flip "
        "on different bars.",
        "ta.atr is ta.rma(ta.tr(true), atrPeriod) with pine_ta's documented "
        "Wilder seeding (SMA of the first atrPeriod true ranges), listed in "
        "PINE_SEMANTICS.md as an unverified-against-platform choice.",
        "The source declares indicator(...), not strategy(...), so no strategy() "
        "properties exist and Pine's documented defaults are used: "
        "default_qty_type fixed, default_qty_value 1, commission 0%, pyramiding "
        "0, initial capital 1000000 USD. On TradingView strategy.entry inside an "
        "indicator does not compile; the host named by the source's /*backtest "
        "header and the md's Detail link (fmz.com/strategy/362457) is what ran "
        "the appended block, and that platform's Pine dialect -- not "
        "TradingView -- is the original behaviour this port reproduces.",
        "The source has no exit of any kind: no strategy.close, no "
        "strategy.exit, no stop or limit order, and no commented-out exit line. "
        "A position is only left by the opposite entry, which the engine models "
        "as a reverse fill (close the old side, open the new one). "
        "source_reproduce_stops is False accordingly.",
        "The three conditions live in one `if / else if` chain in source order, "
        "reproduced as if/elif so a bar can only ever place one order. The two "
        "conditions are mutually exclusive anyway (all three directions -1 "
        "cannot coexist with all three +1), so the ordering is not load-bearing "
        "for the fills -- only for faithfulness.",
        "The three pairs of plot/fill calls and the three hidden bodyMiddle "
        "plots are display-only and place no order; they are dropped.",
        "The backtest header declares period: 30m with basePeriod: 15m "
        "(intrabar data). The engine evaluates at bar close and fills at the "
        "next open, so intrabar path differences are not modelled.",
        "The backtest window in the header (2022-05-03 to 2022-05-09) is "
        "extraction metadata, not an input.time filter, so the port runs on "
        "whatever range the caller supplies.",
        "Leverage, margin, liquidation, funding and the venue's contract-step "
        "rounding are not modelled; the chain verifier measures the rounding "
        "separately (PINE_SEMANTICS.md 1.6).",
    ]

    def pine_indicators(self, dataframe, params):
        supertrend_1, direction_1 = pine_supertrend(
            dataframe, float(params["NEW1_factor"]), int(params["NEW1_atrPeriod"])
        )
        supertrend_2, direction_2 = pine_supertrend(
            dataframe, float(params["NEW2_factor"]), int(params["NEW2_atrPeriod"])
        )
        supertrend_3, direction_3 = pine_supertrend(
            dataframe, float(params["NEW3_factor"]), int(params["NEW3_atrPeriod"])
        )
        dataframe["pine_supertrend_1"] = supertrend_1
        dataframe["pine_direction_1"] = direction_1
        dataframe["pine_supertrend_2"] = supertrend_2
        dataframe["pine_direction_2"] = direction_2
        dataframe["pine_supertrend_3"] = supertrend_3
        dataframe["pine_direction_3"] = direction_3
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "direction_1": dataframe["pine_direction_1"].to_numpy(),
            "direction_2": dataframe["pine_direction_2"].to_numpy(),
            "direction_3": dataframe["pine_direction_3"].to_numpy(),
        }

    def pine_script(self, broker, i, ctx):
        # if direction_1 < 0 and direction_2 < 0 and direction_3 < 0
        #     strategy.entry("Enter Long", strategy.long)
        # else if direction_1 > 0 and direction_2 > 0 and direction_3 > 0
        #     strategy.entry("Enter Short", strategy.short)
        one = ctx["direction_1"][i]
        two = ctx["direction_2"][i]
        three = ctx["direction_3"][i]
        if one < 0 and two < 0 and three < 0:
            broker.entry("Enter Long", "long")
        elif one > 0 and two > 0 and three > 0:
            broker.entry("Enter Short", "short")
