"""Port of sources/SM_01529415185eee52.pine (batch_001/Alpha-Beast-...md).

Pine v6, 1d Futures_Binance BTC_USDT. Three confirmations gate each entry -- a
SuperTrend direction, an RSI threshold and a volume expansion -- and the entry
arms an OCA exit in the same `if`, whose stop sits 1.2 ATR from the signal
bar's close and whose take-profit is 2.5x that distance:

    [_, direction] = ta.supertrend(3.0, 10)
    isUpTrend   = direction < close
    isDownTrend = direction > close
    volBoost    = volume > ta.sma(volume, 20) * 1.5
    longCond    = isUpTrend and rsi > 60 and volBoost
    shortCond   = isDownTrend and rsi < 40 and volBoost
    if longCond
        strategy.entry("Long", strategy.long)
        strategy.exit("Long Exit", from_entry="Long",
                      stop=close - atr * 1.2, limit=close + atr * 1.2 * 2.5)
    if shortCond
        strategy.entry("Short", strategy.short)
        strategy.exit("Short Exit", from_entry="Short",
                      stop=close + atr * 1.2, limit=close - atr * 1.2 * 2.5)

`strategy()` declares only `percent_of_equity` / 20, so Pine's documented
defaults apply for commission (0%), pyramiding (0) and initial capital
(1000000). Both exits carry a `stop=` and a `limit=`, so the engine's resting
levels reach the framework through `pine_stop_level` / `pine_limit_level`
(`source_reproduce_stops = True`).

READ THE COMPARISON BEFORE THE CODE -- it decides this port's whole behaviour.
`ta.supertrend` returns `[supertrend, direction]` and `direction` is the TREND
SIGN (-1 in an uptrend, +1 in a downtrend; the same convention the Pine v5
reference states and that `batch_011/超级趋势策略SuperTrend.py` already ports),
not a price. The source discards the line (`[_, direction] = ...`) and compares
the sign against `close` -- a price in the tens of thousands. So
`direction < close` is unconditionally TRUE, `direction > close` unconditionally
FALSE, `isUpTrend` never constrains anything and the short branch is
unreachable in the source itself. The two comparisons are reproduced literally
(iron rules 1/2/6: record a source-level defect, never "fix" it into a
different strategy); see `source_fidelity_notes` for the consequences and for
the md's conflicting prose.
"""
import numpy as np
import pandas as pd

from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


def _finite(value) -> bool:
    return value is not None and bool(np.isfinite(value))


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

    `ta.supertrend` is a Pine built-in whose internals are not executed here, so
    this is the equivalent implementation published in the Pine v5 Reference
    (src = hl2, bands = hl2 +/- factor * ta.atr(atrPeriod), previous bands
    seeded with nz(), direction flipped on close against the ratcheted band),
    reproduced with Pine's na rules. `direction` is -1 in an up trend and +1 in
    a down trend. Same modelled choice as batch_011/超级趋势策略SuperTrend.py,
    kept identical so the two ports cannot disagree about the same built-in.
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


class SMAlphaBeast_015294(PinePortBase, IStrategy):
    source_id = "SM_01529415185eee52"
    source_file = (
        "Alpha-Beast-高级量化交易策略多指标协同动态风控系统-Alpha-Beast-Advanced-"
        "Quantitative-Trading-Strategy-Multi-Indicator-Synergistic-Dynamic-Risk-"
        "Control-System.md"
    )
    timeframe = "1d"
    # The source contains a `strategy.entry("Short", strategy.short)` call, so
    # the short side exists in the source; its condition is unreachable (see the
    # module docstring), which is reported rather than edited away.
    can_short = True
    source_defaults: dict = {
        "rsiLen": 14,
        "rsiThreshold": 60,
        "atrLen": 14,
        "atrMultSL": 1.2,
        "rr": 2.5,
        "supertrendFactor": 3.0,
        "supertrendLen": 10,
        "volMult": 1.5,
    }
    source_qty_type = "percent_of_equity"
    source_qty_value = 20.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    source_reproduce_stops = True
    source_fidelity_notes = [
        "SOURCE-LEVEL DEFECT, REPRODUCED NOT CORRECTED: `ta.supertrend` returns "
        "`[supertrend, direction]` with `direction` being the trend SIGN (-1 up, "
        "+1 down), but the source compares it against `close` "
        "(`isUpTrend = direction < close`, `isDownTrend = direction > close`). A "
        "sign is always below a price, so isUpTrend is unconditionally true, "
        "isDownTrend unconditionally false, and longCond reduces to "
        "`rsi > 60 and volume > sma(volume,20)*1.5`. The port reproduces those "
        "two comparisons literally; changing them to `direction < 0` would be "
        "porting a different strategy (iron rules 1/2/6).",
        "Consequence of the above: the source's short branch "
        "(`strategy.entry(\"Short\", ...)` + `strategy.exit(\"Short Exit\", ...)`) "
        "can never be reached, so an OCA short exit is never armed and "
        "`pine_limit_level` / `pine_stop_level` only ever mirror the long side. "
        "This is a property of the source, not of the port.",
        "md-vs-source: the md's prose says the SuperTrend \"determines market "
        "trend direction\" and that the short condition is \"Supertrend downward "
        "+\" RSI < 40 -- i.e. the md describes the strategy the author intended. "
        "The md's own entry-condition line, however, translates the comparison "
        "literally (\"方向指标低于收盘价\" / \"direction indicator below closing "
        "price\"), which matches the code. Recorded; the source logic is left "
        "untouched, per iron rule 2.",
        "md-vs-source: measured by exact substring count over the declared "
        "source md (the only Alpha-Beast md), 'Bollinger', '布林', 'band', "
        "'Band', '通道', '上轨', '下轨', 'Upper' and 'Lower' each occur 0 times, "
        "while SuperTrend/超级趋势 and RSI recur throughout. The md's title and "
        "both overviews (概述 / English Overview) name only SuperTrend, RSI and "
        "volume. The md and the Pine source agree -- the source has no "
        "Bollinger-band call -- so no Bollinger-band component is ported because "
        "neither side contains one.",
        "`ta.supertrend` is a Pine built-in whose internals are not executed "
        "here: the port uses the Pine v5 Reference equivalent implementation "
        "(src = hl2, bands = hl2 +/- factor * ta.atr(atrPeriod), nz()-seeded "
        "previous bands, documented direction recursion) with Pine's na rules, "
        "identical to the one already in "
        "batch_011/超级趋势策略SuperTrend.py. The line and its flip bars are "
        "therefore a modelled result, not certified equivalence -- the port's "
        "dominant modelled gap. Note it is second-order here: `direction` enters "
        "only through comparisons that are constant in the source.",
        "ta.atr = ta.rma(ta.tr(true), atrLen) with pine_ta's documented Wilder "
        "seeding (SMA of the first atrLen true ranges), listed in "
        "PINE_SEMANTICS.md section 3 as an unverified-against-platform choice.",
        "The exits are placed with explicit `stop=`/`limit=` levels taken from "
        "the SIGNAL bar's close, as the source writes them -- not re-anchored to "
        "the fill price. The engine rests them from the entry's fill bar on, and "
        "`used_exit_levels` exports exactly those levels (PINE_SEMANTICS.md 1.9).",
        "The exit order ids are `Long Exit` / `Short Exit` (distinct), so Pine's "
        "one-order-per-id replacement never cross-cancels the two sides.",
        "On the bar where either entry condition holds, atr and rsi are always "
        "defined: volBoost needs ta.sma(volume, 20), so no entry can fire before "
        "bar 19 while atr(14)/rsi(14) resolve by bar 13. The port still guards "
        "the exit placement on the levels being finite, which mirrors Pine "
        "treating an na stop/limit as no leg at all.",
        "Sizing is percent_of_equity(20) reproduced from the engine's own "
        "recorded fill notional rather than re-derived from the live wallet "
        "(PINE_SEMANTICS.md 1.4); the venue's contract-step rounding is not "
        "modelled (1.6/2.6) and is measured by verify_chain instead.",
        "strategy() declares only default_qty_type/default_qty_value, so Pine's "
        "documented defaults hold: 0% commission, pyramiding 0, initial capital "
        "1000000.",
        "The /*backtest header window is extraction metadata, not an input.time "
        "filter in the script, so no data is trimmed by the port.",
    ]

    def pine_indicators(self, dataframe, params):
        close = dataframe["close"]
        volume = dataframe["volume"]
        rsi_length = int(params["rsiLen"])
        rsi_threshold = float(params["rsiThreshold"])
        atr_length = int(params["atrLen"])
        atr_mult = float(params["atrMultSL"])
        reward_risk = float(params["rr"])
        vol_mult = float(params["volMult"])

        rsi = ta.pine_rsi(close, rsi_length)
        atr = ta.pine_atr(dataframe, atr_length)
        vol_sma = ta.pine_sma(volume, 20)
        supertrend, direction = pine_supertrend(
            dataframe, float(params["supertrendFactor"]), int(params["supertrendLen"])
        )

        # isUpTrend = direction < close / isDownTrend = direction > close.
        # Literal translation: `direction` is the +/-1 trend sign (see the module
        # docstring), so the first is constantly true and the second constantly
        # false. pandas yields False wherever either operand is na, which is
        # Pine's boolean rule for a comparison with an na operand.
        is_up_trend = direction < close
        is_down_trend = direction > close

        vol_boost = volume > vol_sma * vol_mult

        long_condition = is_up_trend & (rsi > rsi_threshold) & vol_boost
        short_condition = is_down_trend & (rsi < (100.0 - rsi_threshold)) & vol_boost

        # === SL & TP, from the SIGNAL bar's close, exactly as written.
        dataframe["rsi"] = rsi
        dataframe["atr"] = atr
        dataframe["volSMA"] = vol_sma
        dataframe["supertrend"] = supertrend
        dataframe["direction"] = direction
        dataframe["longCondition"] = long_condition.fillna(False)
        dataframe["shortCondition"] = short_condition.fillna(False)
        dataframe["longSL"] = close - atr * atr_mult
        dataframe["longTP"] = close + atr * atr_mult * reward_risk
        dataframe["shortSL"] = close + atr * atr_mult
        dataframe["shortTP"] = close - atr * atr_mult * reward_risk
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "longCondition": dataframe["longCondition"].to_numpy(),
            "shortCondition": dataframe["shortCondition"].to_numpy(),
            "longSL": dataframe["longSL"].to_numpy(),
            "longTP": dataframe["longTP"].to_numpy(),
            "shortSL": dataframe["shortSL"].to_numpy(),
            "shortTP": dataframe["shortTP"].to_numpy(),
        }

    def pine_script(self, broker, i, ctx):
        # if (longCond)
        #     strategy.entry("Long", strategy.long)
        #     strategy.exit("Long Exit", from_entry="Long", stop=longSL, limit=longTP)
        if ctx["longCondition"][i]:
            broker.entry("Long", "long")
            stop = ctx["longSL"][i]
            take = ctx["longTP"][i]
            if _finite(stop) and _finite(take):
                broker.exit("Long Exit", from_entry="Long", stop=stop, limit=take)

        # if (shortCond)
        #     strategy.entry("Short", strategy.short)
        #     strategy.exit("Short Exit", from_entry="Short", stop=shortSL, limit=shortTP)
        if ctx["shortCondition"][i]:
            broker.entry("Short", "short")
            stop = ctx["shortSL"][i]
            take = ctx["shortTP"][i]
            if _finite(stop) and _finite(take):
                broker.exit("Short Exit", from_entry="Short", stop=stop, limit=take)
