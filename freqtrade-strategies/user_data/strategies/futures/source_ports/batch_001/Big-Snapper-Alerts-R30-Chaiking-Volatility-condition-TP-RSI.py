"""Port of sources/SM_ac16020afeaad1dd.pine (batch_001/Big-Snapper-Alerts-R30-Chaiking-Volatility-condition-TP-RSI.md).

Pine v5. JustUncleL/Bannos "Big Snapper" alert indicator (R3.0) with the
Chaikin-volatility gate and the RSI take-profit block the FMZ wrapper appended.
The whole trade behaviour is the FOUR calls at the very end of the script:

    strategy.entry('longe',  strategy.long,  when = up)
    strategy.entry('shorte', strategy.short, when = down)
    strategy.close('longe',  when = closelong)
    strategy.close('shorte', when = closeshort)

`up` / `down` / `closelong` / `closeshort` come from a state machine built on top
of the indicator section; nothing else in the file places an order (every
`plot` / `plotshape` / `fill` / `alertcondition` / `hline` is display-only, and
two variables -- `pos` from the Chaikin block and `SLfactor` -- are dead).

THE INDICATOR SECTION (source order, all of it reproduced)

* `variant(type, src, len)` -- an eleven-way MA formula selector, called four
  times: `ma_coloured` (HullMA 18), `ma_fast` (EMA 21), `ma_medium` (EMA 55),
  `ma_slow` (EMA 89). `_ma_variant` below reproduces every one of the eleven
  branches so that overriding a type stays faithful; Pine evaluates all eleven
  `vN` each bar and returns exactly one, and they are pure, so computing only the
  selected branch returns the identical series.
* `clrdirection`: `+1` while `ta.rising(ma_coloured, 2)`, `-1` while
  `ta.falling(ma_coloured, 2)`, otherwise the previous value (`nz(..., 1)`, so
  bar 0's fallback is +1).
* `madirection`: the 3xMA ordering test plus the six `disable*Filter` overrides,
  applied in source order.
* `STrendUp` / `STrendDown` / `STrend`: the classic manual SuperTrend recursion
  (`hl2 -/+ SFactor * ta.atr(SPd)`, ratcheted on `close[1]`, direction carried
  with `nz(..., 1)`), and `Tsl = STrend == 1 ? STrendUp : STrendDown`.
* Bollinger/Keltner bands over `ma_src` with `bbLength` / `bbStddev`. The source
  hardcodes `uKC = false` (the input is commented out), so the stdev branch is
  the live one; the ternary is kept with the literal so the dead branch is
  visible.
* `noiupper` / `noilower` from `ta.highestbars(oiLength)` / `ta.lowestbars(...)`
  and the two `oiMACross*` Outside-In flags, which look back a DYNAMIC number of
  bars (`upper[noiupper]`).
* Fifteen filter counters, each a "count while the condition holds, else reset to
  0" recursion, and the `long` / `short` / `along` / `ashort` selections they
  feed. With the default `filterOption = 'SuperTrend'` only `stbuy` / `stsell`
  reach an order; every other counter is still computed, as in the source.

THE STATE MACHINE (source order, reproduced bar by bar)

    if sellRsi: tampon_overbought := 1        (rsi > overbought)
    if buyRsi:  tampon_oversold   := 1        (rsi < oversold)
    if entryvalueup > 0 and low < SLup: SL := 1
    closelong  = tampon_overbought == 1 and rsi < 63.8 or shorte or SL == 1
    closeshort = tampon_oversold   == 1 and rsi > 36.2 or longe  or SL == 1
    if closelong:  up := 0, longe := 0, tampon_overbought := 0,
                   triggerlong := 0, SL := 0, entryvalueup := 0
    if closeshort: down := 0, shorte := 0, tampon_oversold := 0,
                   triggershort := 0, SL := 0, entryvaluedown := 0
    if close < ma_medium: triggerlong := 0, triggershort := 1
    if close > ma_medium: triggershort := 0, triggerlong := 1
    if long or along:  longbuffer := 1
    if short or ashort: shortbuffer := 1
    longe  := longbuffer and triggerlong  and xROC_EMA > 3.5
    shorte := shortbuffer and triggershort and xROC_EMA > 3.5
    if longe == 1 and close > open:  up := 1, down := 0, entryvalueup := close,
        SLup := close - 0.7 * (high - low), SLdown := 0, longbuffer := 0
    if shorte == 1 and close < open: down := 1, up := 0, entryvaluedown := close,
        SLdown := close + 0.7 * (high - low), SLup := 0, shortbuffer := 0

Everything here is `var` state (the manifest flags this source
`persistent_state`). Note the ONE-BAR LAG ON `longe` / `shorte` inside
`closelong` / `closeshort`: those two lines run BEFORE `longe` / `shorte` are
reassigned, so the test reads the previous bar's value -- the port carries them
in loop state rather than recomputing them, which is what makes the lag
faithful.

`xROC_EMA = ta.roc(ta.ema(high - low, Length), ROCLength)`, and the `> 3.5`
gate on it is a hardcoded literal, not the `Trigger` input (which is read only by
the dead `pos` variable).

FIDELITY:

* `up` / `down` are set only in the two entry blocks and cleared only by the two
  close blocks, so `when = up` is true on EVERY bar of the window between an
  entry and its close, i.e. the entry is re-issued each bar, not only on the flip
  bar. The port passes the same per-bar flag to `broker.entry`, so with
  `pyramiding = 0` the repeats are ignored exactly as Pine ignores them.
* A bar CAN carry `up = 1` and `closelong = 1` together, so a same-bar
  entry+close is possible and the port's run confirms it happens. The path is
  the `triggerlong` reset: `closelong` clears `triggerlong`, but the
  `if close > ma_medium` line runs AFTER it and can set it straight back to 1
  while `longbuffer` is still 1, so `longe` -- and therefore `up` -- is re-armed
  on the very bar the close fires. On such a bar the engine fills in placement
  order (entry then close) and `pyramiding = 0` blocks the entry while the close
  goes through, which is what Pine's pyramiding rule does too; but the intra-bar
  sequencing between an entry and a close submitted on the same bar is
  PINE_SEMANTICS.md 1.13's unverified modelling choice, and here it is also
  UNMEASURABLE, because the 2h timeframe has no local data to verify against.
* Pine v5 `bool` compared with `1` (`if longe == 1`) is true for `true`, and
  Python's `True == 1` agrees, so this comparison is translated literally. This
  is the safe direction of PINE_SEMANTICS.md 1.16 (whose trap is `!= 0`, where
  Python's `True != 0` is False and Pine's is true); no `!= 0` / `== 0` form
  occurs in this source.
* `ta.rising` / `ta.falling` are not exposed by `pine_ta` and are translated
  here from Pine's definition -- strictly higher (lower) on EACH of the last
  `length` steps, consecutive, equality breaking the run, na comparisons false --
  the same reading already used by batch_001/3EMA.py and by the Hull port. The
  alternative reading ("greater than any of the previous `length` values") is
  recorded as unresolved, not resolved.
* `ta.highestbars(oiLength)` / `ta.lowestbars(oiLength)` / `ta.highest(oiLength)`
  / `ta.lowest(oiLength)` are called with ONE argument. Pine v5's documented
  one-argument overloads use `high` for the highest-side and `low` for the
  lowest-side functions; that is the reading used. The offset is returned as a
  NEGATIVE bars-back value (0 .. -(oiLength-1)) and the source takes `math.abs`,
  so the lookback lands on a bar in the same window. Selection among EQUAL
  extremes inside a window is not documented by TradingView; this port takes the
  OLDEST of the ties (`argmax` on the window), and the choice can only reach an
  order through `OutsideIn:*` filter options, which the default never selects.
* `ta.tr` here is the bare `ta.tr` (handle_na = false), so bar 0 is na and the
  Keltner `rangema` window carries that na; `ta.atr(SPd)` is `ta.rma(ta.tr(true),
  SPd)` with `pine_ta`'s documented Wilder seeding. PINE_SEMANTICS.md 3.7 records
  the first-bar difference this creates and the offset it puts into every ATR/DI
  series afterwards; unresolved at the shared layer.
* The SuperTrend recursion is the source's own code, not `ta.supertrend`, so it
  is transcribed directly rather than mapped onto the modelled built-in. On the
  bars where a band is still na the comparisons are false and the else branch is
  taken, which is Pine's na rule and the same convention `pine_ta` uses.
* `strategy()` declares only `title` / `shorttitle` / `overlay`, so every
  property is Pine's documented default: `strategy.fixed` / 1 contract, initial
  capital 1000000, commission 0%, pyramiding 0, `process_orders_on_close=false`.
* md/source divergence recorded, not acted on: the md's `/*backtest` header
  declares `balance: 500000`, while `strategy()` declares no `initial_capital`
  and therefore runs on Pine's documented 1000000. The header's balance is the
  FMZ wrapper's own setting (like its `basePeriod`), not a Pine strategy
  property, so `source_initial_capital` is 1000000 and 500000 is NOT used.
* md/source divergence recorded, not acted on: the md's argument table renders
  each `input.string` option list with its DEFVAL moved to the front (e.g.
  `HullMA|EMA|WMA|VWMA|SMMA|DEMA|TEMA|SMA|ZEMA|TMA|SSMA`, while the source's
  `options` array is `['SMA','EMA',...,'HullMA','ZEMA','TMA','SSMA']`). Same
  option set, same default; a rendering artifact of the table generator.
* md/source divergence recorded, not acted on: the md's prose describes the
  SuperTrend filter and the Bollinger Outside-In filter at length but says
  nothing about the appended Bannos block, the Chaikin gate or the RSI
  take-profit -- the block that actually trades. The code is the authority.
* Dead code is reproduced, not deleted: `pos` (assigned in the Chaikin block,
  never read), `SLfactor` (declared, never read), `Tsl` (plotted only),
  `entryvaluedown` / `SLdown` (only ever reset and re-set, never read), and the
  eleven `vN` branches `_ma_variant` does not select.
* `alertcondition(...)` and `alert()` are not trading calls and are not
  reproduced (PINE_SEMANTICS.md 二.7); `plot` / `plotshape` / `fill` / `hline` /
  `bgcolor`-style display calls are likewise omitted, including the `plot` of
  `entryvalueup` / `SLup` / `entryvaluedown` / `SLdown` / `xROC_EMA`.
* No stop / limit / trail ORDER exists -- `SL` is an internal flag that routes
  into `closelong` / `closeshort`, which are `strategy.close` calls -- so
  `source_reproduce_stops` is False. There is no resting order to mirror.
* `/*backtest` header: `period: 2h` on Futures_Binance BTC_USDT, hence
  `timeframe = "2h"`; `basePeriod: 15m` is the FMZ backtester's own fill
  granularity for those 2h bars, not the strategy's period. Its window
  (2022-04-08 .. 2022-05-07) is extraction metadata, not an `input.time` filter,
  so no data is trimmed.
* PINE_SEMANTICS.md 1.13's same-bar fill ordering does not arise here: the entry
  and its close are mutually exclusive on one bar (see above), and all four
  calls are market orders on separate ids.
* Leverage, margin, liquidation, funding and the venue's contract-step rounding
  are not modelled (PINE_SEMANTICS.md section 2).
"""
import numpy as np
import pandas as pd

from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


def _rising(series: pd.Series, length: int) -> pd.Series:
    """Pine `ta.rising`: strictly higher on each of the last `length` steps.

    Pine's documented test is "is now rising for `length` bars long" --
    source[i] > source[i+1] for every i in 0..length-1 -- so the steps are
    CONSECUTIVE and equality breaks the run. na on either side of a comparison
    makes it false, as Pine treats na comparisons.
    """
    rising = pd.Series(True, index=series.index)
    for step in range(int(length)):
        rising &= series.shift(step) > series.shift(step + 1)
    return rising.fillna(False)


def _falling(series: pd.Series, length: int) -> pd.Series:
    """Pine `ta.falling`: strictly lower on each of the last `length` steps."""
    falling = pd.Series(True, index=series.index)
    for step in range(int(length)):
        falling &= series.shift(step) < series.shift(step + 1)
    return falling.fillna(False)


def _pine_gt(left: float, right: float) -> bool:
    """Pine `>`: a comparison with an na operand is false."""
    if left is None or right is None or np.isnan(left) or np.isnan(right):
        return False
    return bool(left > right)


def _pine_lt(left: float, right: float) -> bool:
    """Pine `<`: a comparison with an na operand is false."""
    if left is None or right is None or np.isnan(left) or np.isnan(right):
        return False
    return bool(left < right)


def _pine_max(left: float, right: float) -> float:
    """Pine `math.max`: na in, na out."""
    if np.isnan(left) or np.isnan(right):
        return np.nan
    return float(max(left, right))


def _pine_min(left: float, right: float) -> float:
    """Pine `math.min`: na in, na out."""
    if np.isnan(left) or np.isnan(right):
        return np.nan
    return float(min(left, right))


def _nz(value: float, replacement: float = 0.0) -> float:
    """Pine `nz(value, replacement)`."""
    return replacement if value is None or np.isnan(value) else float(value)


def _highestbars(values: np.ndarray, length: int) -> np.ndarray:
    """Pine `ta.highestbars(high, length)` -> bars back to the window's high.

    Returns a NEGATIVE offset (0 .. -(length-1)) as Pine does, or na while the
    window is not full. Ties resolve to the OLDEST bar of the window, a choice
    TradingView does not document; it can only reach an order through an
    `OutsideIn:*` filter option, which the default never selects.
    """
    out = np.full(len(values), np.nan)
    for i in range(len(values)):
        if i + 1 < length:
            continue
        window = values[i - length + 1: i + 1]
        if np.isnan(window).any():
            continue
        out[i] = float(int(np.argmax(window)) - (length - 1))
    return out


def _lowestbars(values: np.ndarray, length: int) -> np.ndarray:
    """Pine `ta.lowestbars(low, length)` -> bars back to the window's low."""
    out = np.full(len(values), np.nan)
    for i in range(len(values)):
        if i + 1 < length:
            continue
        window = values[i - length + 1: i + 1]
        if np.isnan(window).any():
            continue
        out[i] = float(int(np.argmin(window)) - (length - 1))
    return out


def _lookback(values: np.ndarray, offsets: np.ndarray) -> np.ndarray:
    """`series[offset]` for a per-bar, possibly-na offset (Pine dynamic index)."""
    out = np.full(len(values), np.nan)
    for i in range(len(values)):
        offset = offsets[i]
        if np.isnan(offset):
            continue
        position = i - int(offset)
        if position < 0 or position >= len(values):
            continue
        out[i] = values[position]
    return out


def _window_extreme(values: np.ndarray, length: int, kind: str) -> np.ndarray:
    """Pine `ta.highest(high, length)` / `ta.lowest(low, length)`."""
    if kind == "high":
        out = np.full(len(values), np.nan)
        for i in range(len(values)):
            if i + 1 < length:
                continue
            window = values[i - length + 1: i + 1]
            if np.isnan(window).any():
                continue
            out[i] = float(np.max(window))
        return out
    out = np.full(len(values), np.nan)
    for i in range(len(values)):
        if i + 1 < length:
            continue
        window = values[i - length + 1: i + 1]
        if np.isnan(window).any():
            continue
        out[i] = float(np.min(window))
    return out


class SMBigSnapperAlertsR30_ac1602(PinePortBase, IStrategy):
    source_id = "SM_ac16020afeaad1dd"
    source_file = "Big-Snapper-Alerts-R30-Chaiking-Volatility-condition-TP-RSI.md"
    timeframe = "2h"
    can_short = True
    source_defaults: dict = {
        "typeColoured": "HullMA",
        "lenColoured": 18,
        "srcColoured": "close",
        "typeFast": "EMA",
        "lenFast": 21,
        "typeMedium": "EMA",
        "lenMedium": 55,
        "typeSlow": "EMA",
        "lenSlow": 89,
        "ma_src": "close",
        "filterOption": "SuperTrend",
        "hideMALines": False,
        "hideSuperTrend": True,
        "hideBollingerBands": True,
        "hideTrendDirection": True,
        "disableFastMAFilter": False,
        "disableMediumMAFilter": False,
        "disableSlowMAFilter": False,
        "bbLength": 20,
        "bbStddev": 2.0,
        "oiLength": 8,
        "SFactor": 3.618,
        "SPd": 5,
        "buyColour_": "Green",
        "sellColour_": "Maroon",
        "overbought": 70,
        "oversold": 30,
        "Length": 10,
        "ROCLength": 12,
        "Trigger": 0,
    }
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    source_reproduce_stops = False
    source_fidelity_notes = [
        "The whole trade behaviour is the four appended calls: entry longe when=up, "
        "entry shorte when=down, close longe when=closelong, close shorte "
        "when=closeshort, in that source order.",
        "up / down stay set until a close clears them, so when=up is true on EVERY "
        "bar between an entry and its close: the entry is re-issued each bar, not "
        "only on the flip bar. Passed through as the same per-bar flag, so "
        "pyramiding=0 suppresses the repeats exactly as Pine does.",
        "A same-bar entry+close IS possible and the port's run confirms it: "
        "closelong clears triggerlong, but `if close > ma_medium` runs AFTER that "
        "reset and can set it back to 1 while longbuffer is still 1, so longe -- and "
        "up -- is re-armed on the bar the close fires. The engine then fills in "
        "placement order (entry, then close) and pyramiding=0 blocks the entry while "
        "the close goes through, matching Pine's pyramiding rule; the intra-bar "
        "sequencing itself is PINE_SEMANTICS.md 1.13's unverified modelling choice "
        "and is UNMEASURABLE here because the 2h timeframe has no local data.",
        "closelong / closeshort read `longe` / `shorte` BEFORE those are reassigned "
        "later in the same bar, so the test uses the PREVIOUS bar's value; the port "
        "carries them in loop state rather than recomputing them, which is what "
        "makes the one-bar lag faithful.",
        "`xROC_EMA > 3.5` is a hardcoded literal, not the Trigger input; Trigger is "
        "read only by the dead `pos` variable in the Chaikin block.",
        "variant(type, src, len) is an eleven-way MA selector; _ma_variant "
        "reproduces all eleven branches so overriding a type stays faithful. The "
        "defaults select HullMA(18) / EMA(21) / EMA(55) / EMA(89).",
        "Two variant branches are easy to get wrong and are transcribed literally: "
        "v10 (ZEMA) is `2 * SMA - EMA(SMA)` -- its lag term is built on the SMA, not "
        "on the EMA -- and v9 (SSMA) reads the previous BAR's SOURCE in its first "
        "term while its other two terms read the filter's own past output, each "
        "through nz, with the source's own 1.414 * 3.14159 constants rather than "
        "math.pi. Both are dead under the default types, so only an override "
        "reaches them.",
        "v5 (SMMA) is Wilder smoothing written inline (`na(v5[1]) ? sma_1 : "
        "(v5[1] * (len - 1) + src) / len`), i.e. exactly ta.rma / pine_rma's SMA "
        "seed, so it maps onto pine_rma rather than being re-derived.",
        "variant's return is a nested ternary chain whose fallback is v1 (SMA), so "
        "an unknown type string degrades to SMA; _ma_variant keeps that fallback.",
        "Pine evaluates all eleven vN and returns one; the branches are pure and "
        "none observes broker state, so computing only the selected branch returns "
        "the identical series.",
        "ta.rising / ta.falling are not exposed by pine_ta and are translated from "
        "Pine's definition -- strictly higher (lower) on EACH of the last `length` "
        "steps, consecutive, equality breaking the run, na comparisons false -- the "
        "same reading used by batch_001/3EMA.py and the Hull port. The alternative "
        "reading ('greater than any of the previous length values') remains "
        "unresolved and is recorded, not resolved.",
        "ta.highestbars / ta.lowestbars / ta.highest / ta.lowest are called with ONE "
        "argument; Pine v5's documented one-argument overloads use high for the "
        "highest side and low for the lowest side. Ties inside a window resolve to "
        "the OLDEST bar, which TradingView does not document -- it can only reach an "
        "order through the OutsideIn:* filter options, which the default never "
        "selects.",
        "The SuperTrend recursion is the source's own code (ratcheted bands on "
        "close[1], direction carried with nz(...,1)), transcribed directly rather "
        "than mapped onto the modelled ta.supertrend built-in.",
        "ta.atr(SPd) is ta.rma(ta.tr(true), SPd) with pine_ta's Wilder seeding, while "
        "the bare ta.tr used for the Keltner rangema has an na first bar "
        "(PINE_SEMANTICS.md 3.7 records the ATR/DI seeding offset this leaves; "
        "unresolved at the shared layer).",
        "uKC is hardcoded false in the source (the input is commented out), so the "
        "Bollinger stdev branch is the live one; the ternary is kept with the "
        "literal so the dead Keltner branch stays visible.",
        "The source's filter flags run eight mutually exclusive filter families; all "
        "of them and their fifteen counters are computed, so overriding filterOption "
        "stays faithful. With the default 'SuperTrend' only stbuy / stsell reach an "
        "order.",
        "md/source divergence recorded, not acted on: the md's /*backtest header "
        "declares balance: 500000 while strategy() declares no initial_capital, and "
        "Pine's documented default is 1000000. The header's balance is the FMZ "
        "wrapper's own setting (like its basePeriod), so source_initial_capital is "
        "1000000 and the 500000 is NOT used.",
        "md/source divergence recorded, not acted on: the md's argument table renders "
        "each option list with its DEFVAL moved to the front; the source's options "
        "array has the same members in a different order. Same set, same default -- a "
        "rendering artifact of the table generator.",
        "md/source divergence recorded, not acted on: the md's prose covers the "
        "SuperTrend and Bollinger Outside-In filters but never mentions the appended "
        "Bannos state machine, the Chaikin gate or the RSI take-profit -- the part "
        "that actually trades. The code is the authority.",
        "Dead code is reproduced rather than deleted: pos (assigned, never read), "
        "SLfactor (declared, never read), Tsl and entryvaluedown / SLdown (written, "
        "never read by an order).",
        "No stop / limit / trail ORDER exists: SL is an internal flag that routes "
        "into closelong / closeshort, which are strategy.close calls, so there is no "
        "resting order to mirror and source_reproduce_stops is False.",
        "strategy() declares only title / shorttitle / overlay, so Pine's documented "
        "defaults apply: strategy.fixed / 1 contract, initial capital 1000000, 0% "
        "commission, pyramiding 0, process_orders_on_close=false.",
        "Pine v5 bool compared with 1 (`if longe == 1`) agrees with Python's "
        "True == 1, so the comparison is translated literally; this source contains "
        "no `!= 0` / `== 0` form, i.e. the dangerous direction of PINE_SEMANTICS.md "
        "1.16 does not occur.",
        "The header's basePeriod: 15m is the FMZ backtester's own fill granularity, "
        "not the strategy's period (2h), and its window is extraction metadata rather "
        "than an input.time filter, so no data is trimmed.",
        "plot / plotshape / fill / hline / alertcondition / alert calls are "
        "display-only or notification-only and are not reproduced.",
        "Leverage, margin, liquidation, funding and the venue's contract-step "
        "rounding are not modelled.",
    ]

    # ---- indicator helpers -------------------------------------------------
    @classmethod
    def _supersmoother(cls, source: pd.Series, length: int) -> pd.Series:
        """Ehlers' SuperSmoother (`v9`):

            v9 := c1 * (src + nz(src[1])) / 2 + c2 * nz(v9[1]) + c3 * nz(v9[2])

        Note which history each term reads: the first term uses the previous
        BAR's SOURCE, the other two the filter's own past OUTPUT. The three `nz`
        calls make an na history read as 0 rather than na, so the recursion does
        not restart; an na `src` still makes the bar na, because `c1 * (na + x)`
        is na. The constants are the source's own (1.414 * 3.14159, not
        `np.pi`), and `b1` is carried into `c2` exactly as written.
        """
        values = source.to_numpy(dtype=float)
        size = len(values)
        out = np.full(size, np.nan)
        a1 = np.exp(-1.414 * 3.14159 / length)
        b1 = 2.0 * a1 * np.cos(1.414 * 3.14159 / length)
        c2 = b1
        c3 = -a1 * a1
        c1 = 1.0 - c2 - c3
        for i in range(size):
            if np.isnan(values[i]):
                continue
            prev_src = values[i - 1] if i >= 1 else np.nan
            prev_out = out[i - 1] if i >= 1 else np.nan
            prev_out2 = out[i - 2] if i >= 2 else np.nan
            out[i] = (
                c1 * (values[i] + _nz(prev_src)) / 2.0
                + c2 * _nz(prev_out) + c3 * _nz(prev_out2)
            )
        return pd.Series(out, index=source.index, dtype=float)

    @classmethod
    def _ma_variant(cls, kind, src: pd.Series, length: int,
                    volume: pd.Series) -> pd.Series:
        """The source's `variant(type, src, len)`, one branch per MA type."""
        length = int(length)
        simple = ta.pine_sma(src, length)                      # v1  SMA
        exponential = ta.pine_ema(src, length)                 # v2  EMA
        if kind == "EMA":
            return exponential
        if kind == "WMA":
            return ta.pine_wma(src, length)                    # v3  WMA
        if kind == "VWMA":
            weighted = src.copy()
            weighted.attrs["volume"] = volume
            return ta.pine_vwma(weighted, length)              # v4  VWMA
        if kind == "SMMA":
            return ta.pine_rma(src, length)                    # v5  SMMA
        if kind == "DEMA":
            return 2 * exponential - ta.pine_ema(exponential, length)   # v6
        if kind == "TEMA":
            double = ta.pine_ema(exponential, length)          # v7
            return 3 * (exponential - double) + ta.pine_ema(double, length)
        if kind == "HullMA":
            half = ta.pine_wma(src, int(length / 2))           # v8  Hull
            full = ta.pine_wma(src, length)
            return ta.pine_wma(2 * half - full, ta.pine_round(np.sqrt(length)))
        if kind == "TMA":
            return ta.pine_sma(simple, length)                 # v11 Triangular
        if kind == "SSMA":
            return cls._supersmoother(src, length)             # v9
        if kind == "ZEMA":
            # v10: `e = ta.ema(v1, len)` where v1 is the SMA, so ZEMA is
            # 2 * SMA - EMA(SMA) -- the zero-lag term is built on the SMA, NOT
            # on the EMA.
            return simple + simple - ta.pine_ema(simple, length)
        return simple                                          # v1  fallback

    def pine_indicators(self, dataframe, params):
        close_series = dataframe["close"]
        ma_src = ta.pine_source(dataframe, params["ma_src"])
        volume = dataframe["volume"]
        close = close_series.to_numpy(dtype=float)
        open_ = dataframe["open"].to_numpy(dtype=float)
        high = dataframe["high"].to_numpy(dtype=float)
        low = dataframe["low"].to_numpy(dtype=float)
        hl2 = (high + low) / 2.0
        size = len(dataframe)

        # ---- filter flags (source lines 152-178, in order) -----------------
        filter_option = params["filterOption"]
        fast_off = bool(params["disableFastMAFilter"])
        medium_off = bool(params["disableMediumMAFilter"])
        slow_off = bool(params["disableSlowMAFilter"])

        u_supertrend = filter_option == "SuperTrend"
        u_3xma = filter_option == "3xMATrend"
        u_both = filter_option == "SuperTrend+3xMA"
        u_oi_macross = filter_option == "OutsideIn:MACross"
        u_oi_3xma = filter_option == "OutsideIn:MACross+3xMA"
        u_oi_st = filter_option == "OutsideIn:MACross+ST"
        u_macross = filter_option == "MACross"
        u_macross_st = filter_option == "MACross+ST"
        u_macross_3xma = filter_option == "MACross+3xMA"

        disable_3xma = fast_off and medium_off and slow_off
        u_3xma = False if disable_3xma else u_3xma

        no_alerts = filter_option == "No Alerts"
        any_filter = (
            u_3xma or u_supertrend or u_both or u_oi_3xma or u_oi_st
            or u_oi_macross or u_macross or u_macross_st or u_macross_3xma
        )
        disable_all_filters = not any_filter
        if no_alerts:
            disable_all_filters = False
            u_supertrend = False
            u_3xma = False
            u_both = False
            u_oi_macross = False
            u_oi_3xma = False
            u_oi_st = False
            u_macross = False
            u_macross_st = False
            u_macross_3xma = False

        # ---- the four moving averages (source lines 219-222) ---------------
        ma_fast = self._ma_variant(params["typeFast"],
                                   ta.pine_source(dataframe, params["ma_src"]),
                                   int(params["lenFast"]), volume)
        ma_medium = self._ma_variant(params["typeMedium"],
                                     ta.pine_source(dataframe, params["ma_src"]),
                                     int(params["lenMedium"]), volume)
        ma_slow = self._ma_variant(params["typeSlow"],
                                   ta.pine_source(dataframe, params["ma_src"]),
                                   int(params["lenSlow"]), volume)
        ma_coloured = self._ma_variant(
            params["typeColoured"], ta.pine_source(dataframe, params["srcColoured"]),
            int(params["lenColoured"]), volume,
        )
        fast = ma_fast.to_numpy(dtype=float)
        medium = ma_medium.to_numpy(dtype=float)
        slow = ma_slow.to_numpy(dtype=float)
        coloured = ma_coloured.to_numpy(dtype=float)

        # ---- clrdirection (source lines 224-226) ---------------------------
        rising = _rising(ma_coloured, 2).to_numpy()
        falling = _falling(ma_coloured, 2).to_numpy()
        clrdirection = np.zeros(size, dtype=float)
        previous = np.nan
        for i in range(size):
            if rising[i]:
                value = 1.0
            elif falling[i]:
                value = -1.0
            else:
                value = _nz(previous, 1.0)
            clrdirection[i] = value
            previous = value

        # ---- madirection (source lines 228-234, in order) ------------------
        madirection = np.where(
            (fast > medium) & (medium > slow), 1.0,
            np.where((fast < medium) & (medium < slow), -1.0, 0.0),
        )
        if slow_off:
            madirection = np.where(
                fast > medium, 1.0, np.where(fast < medium, -1.0, 0.0)
            )
        if medium_off:
            madirection = np.where(
                fast > slow, 1.0, np.where(fast < slow, -1.0, 0.0)
            )
        if fast_off:
            madirection = np.where(
                medium > slow, 1.0, np.where(medium < slow, -1.0, 0.0)
            )
        if fast_off and medium_off:
            madirection = np.where(coloured > slow, 1.0, -1.0)
        if fast_off and slow_off:
            madirection = np.where(coloured > medium, 1.0, -1.0)
        if slow_off and medium_off:
            madirection = np.where(coloured > fast, 1.0, -1.0)

        # ---- SuperTrend (source lines 237-245) -----------------------------
        sfactor = float(params["SFactor"])
        atr = ta.pine_atr(dataframe, int(params["SPd"])).to_numpy(dtype=float)
        s_up = hl2 - sfactor * atr
        s_dn = hl2 + sfactor * atr
        trend_up = np.full(size, np.nan)
        trend_down = np.full(size, np.nan)
        strend = np.zeros(size, dtype=float)
        prev_up = np.nan
        prev_down = np.nan
        prev_trend = np.nan
        for i in range(size):
            prev_close = close[i - 1] if i >= 1 else np.nan
            trend_up[i] = (
                _pine_max(s_up[i], prev_up)
                if _pine_gt(prev_close, prev_up) else s_up[i]
            )
            trend_down[i] = (
                _pine_min(s_dn[i], prev_down)
                if _pine_lt(prev_close, prev_down) else s_dn[i]
            )
            if _pine_gt(close[i], prev_down):
                value = 1.0
            elif _pine_lt(close[i], prev_up):
                value = -1.0
            else:
                value = _nz(prev_trend, 1.0)
            strend[i] = value
            prev_up = trend_up[i]
            prev_down = trend_down[i]
            prev_trend = value
        tsl = np.where(strend == 1.0, trend_up, trend_down)

        # ---- Bollinger / Keltner bands (source lines 246-253) --------------
        bb_length = int(params["bbLength"])
        bb_stddev = float(params["bbStddev"])
        basis = ta.pine_sma(ma_src, bb_length)
        rangema = ta.pine_sma(ta.pine_tr(dataframe), bb_length)
        stdev_1 = ta.pine_stdev(ma_src, bb_length)
        # `uKC = false` is hardcoded in the source (its input is commented out).
        u_kc = False
        deviation = bb_stddev * rangema if u_kc else bb_stddev * stdev_1
        upper = (basis + deviation).to_numpy(dtype=float)
        lower = (basis - deviation).to_numpy(dtype=float)

        # ---- Bollinger Outside-In lookbacks (source lines 254-262) ---------
        oi_length = int(params["oiLength"])
        noiupper = np.abs(_highestbars(high, oi_length))
        noilower = np.abs(_lowestbars(low, oi_length))
        highest_oi = _window_extreme(high, oi_length, "high")
        lowest_oi = _window_extreme(low, oi_length, "low")
        upper_at_offset = _lookback(upper, noiupper)
        lower_at_offset = _lookback(lower, noilower)

        macross_up = ta.pine_crossover(ma_fast, ma_coloured).to_numpy()
        macross_down = ta.pine_crossunder(ma_fast, ma_coloured).to_numpy()
        oi_macross_upper = (
            macross_down & (noiupper > 0) & (highest_oi > upper_at_offset)
        )
        oi_macross_lower = (
            macross_up & (noilower > 0) & (lowest_oi < lower_at_offset)
        )

        # ---- the fifteen filter counters (source lines 282-328) ------------
        def _count(condition: np.ndarray, previous_value: float) -> float:
            return previous_value + 1.0 if condition else 0.0

        counters = {
            "_3xmabuy": np.zeros(size), "_3xmasell": np.zeros(size),
            "stbuy": np.zeros(size), "stsell": np.zeros(size),
            "st3xmabuy": np.zeros(size), "st3xmasell": np.zeros(size),
            "oimacrossbuy": np.zeros(size), "oimacrosssell": np.zeros(size),
            "oi3xmabuy": np.zeros(size), "oi3xmasell": np.zeros(size),
            "oistbuy": np.zeros(size), "oistsell": np.zeros(size),
            "macrossstbuy": np.zeros(size), "macrossstsell": np.zeros(size),
            "macross3xmabuy": np.zeros(size), "macross3xmasell": np.zeros(size),
            "hbuy": np.zeros(size), "hsell": np.zeros(size),
            "macrossbuy": np.zeros(size), "macrosssell": np.zeros(size),
        }
        state = {name: 0.0 for name in counters}
        for i in range(size):
            clr_up = clrdirection[i] == 1.0
            clr_down = clrdirection[i] == -1.0
            mad_up = madirection[i] == 1.0
            mad_down = madirection[i] == -1.0
            trend_up_bar = strend[i] == 1.0
            trend_down_bar = strend[i] == -1.0
            above_fast = _pine_gt(close[i], fast[i])
            below_fast = _pine_lt(close[i], fast[i])

            if clr_up and above_fast and mad_up:
                state["_3xmabuy"] = _count(True, state["_3xmabuy"])
            elif clr_up and mad_up:
                state["_3xmabuy"] = (
                    _count(True, state["_3xmabuy"]) if state["_3xmabuy"] > 0 else 0.0
                )
            else:
                state["_3xmabuy"] = 0.0

            if clr_down and below_fast and mad_down:
                state["_3xmasell"] = _count(True, state["_3xmasell"])
            elif clr_down and mad_down:
                state["_3xmasell"] = (
                    _count(True, state["_3xmasell"]) if state["_3xmasell"] > 0 else 0.0
                )
            else:
                state["_3xmasell"] = 0.0

            state["stbuy"] = (
                state["stbuy"] + 1.0 if clr_up and trend_up_bar else 0.0
            )
            state["stsell"] = (
                state["stsell"] + 1.0 if clr_down and trend_down_bar else 0.0
            )
            state["st3xmabuy"] = (
                state["st3xmabuy"] + 1.0
                if (disable_3xma or state["_3xmabuy"] > 0) and state["stbuy"] > 0
                else 0.0
            )
            state["st3xmasell"] = (
                state["st3xmasell"] + 1.0
                if (disable_3xma or state["_3xmasell"] > 0) and state["stsell"] > 0
                else 0.0
            )
            state["oimacrossbuy"] = (
                state["oimacrossbuy"] + 1.0 if oi_macross_lower[i] else 0.0
            )
            state["oimacrosssell"] = (
                state["oimacrosssell"] + 1.0 if oi_macross_upper[i] else 0.0
            )
            state["oi3xmabuy"] = (
                state["oi3xmabuy"] + 1.0
                if state["oimacrossbuy"] > 0 and (disable_3xma or mad_up)
                else 0.0
            )
            state["oi3xmasell"] = (
                state["oi3xmasell"] + 1.0
                if state["oimacrosssell"] > 0 and (disable_3xma or mad_down)
                else 0.0
            )
            state["oistbuy"] = (
                state["oistbuy"] + 1.0
                if state["oimacrossbuy"] > 0 and trend_up_bar else 0.0
            )
            state["oistsell"] = (
                state["oistsell"] + 1.0
                if state["oimacrosssell"] > 0 and trend_down_bar else 0.0
            )
            state["macrossstbuy"] = (
                state["macrossstbuy"] + 1.0
                if macross_up[i] and trend_up_bar else 0.0
            )
            state["macrossstsell"] = (
                state["macrossstsell"] + 1.0
                if macross_down[i] and trend_down_bar else 0.0
            )
            state["macross3xmabuy"] = (
                state["macross3xmabuy"] + 1.0
                if macross_up[i] and (disable_3xma or mad_up) else 0.0
            )
            state["macross3xmasell"] = (
                state["macross3xmasell"] + 1.0
                if macross_down[i] and (disable_3xma or mad_down) else 0.0
            )
            state["hbuy"] = state["hbuy"] + 1.0 if clr_up else 0.0
            state["hsell"] = state["hsell"] + 1.0 if clr_down else 0.0
            state["macrossbuy"] = (
                state["macrossbuy"] + 1.0 if macross_up[i] else 0.0
            )
            state["macrosssell"] = (
                state["macrosssell"] + 1.0 if macross_down[i] else 0.0
            )
            for name in counters:
                counters[name][i] = state[name]

        # Pine's `or` chain is elementwise on series; each term is
        # `flag and (counter == 1)`, so the selection is an OR of arrays. It is
        # built with |= rather than a Python `or`/`and` chain because a chain
        # whose every flag is False collapses to the scalar False instead of an
        # all-False array.
        long_signal = np.zeros(size, dtype=bool)
        short_signal = np.zeros(size, dtype=bool)
        for flag, buy_key, sell_key in (
            (u_3xma, "_3xmabuy", "_3xmasell"),
            (u_supertrend, "stbuy", "stsell"),
            (u_both, "st3xmabuy", "st3xmasell"),
            (u_oi_3xma, "oi3xmabuy", "oi3xmasell"),
            (u_oi_st, "oistbuy", "oistsell"),
            (u_oi_macross, "oimacrossbuy", "oimacrosssell"),
            (u_macross_st, "macrossstbuy", "macrossstsell"),
            (u_macross_3xma, "macross3xmabuy", "macross3xmasell"),
        ):
            if flag:
                long_signal |= counters[buy_key] == 1
                short_signal |= counters[sell_key] == 1
        along = np.zeros(size, dtype=bool)
        ashort = np.zeros(size, dtype=bool)
        if disable_all_filters:
            along |= counters["hbuy"] == 1
            ashort |= counters["hsell"] == 1
        if u_macross:
            along |= counters["macrossbuy"] == 1
            ashort |= counters["macrosssell"] == 1

        # ---- Chaikin volatility gate (source lines 393-412) ----------------
        x_price = high - low
        x_roc_ema = ta.pine_roc(
            ta.pine_ema(pd.Series(x_price, index=dataframe.index),
                        int(params["Length"])),
            int(params["ROCLength"]),
        ).to_numpy(dtype=float)
        trigger = float(params["Trigger"])

        # ---- RSI block (source lines 372-385) ------------------------------
        overbought = float(params["overbought"])
        oversold = float(params["oversold"])
        rsi11 = ta.pine_rsi(close_series, 11).to_numpy(dtype=float)

        # ---- the Bannos state machine (source lines 382-505) ---------------
        triggerlong = 0.0
        triggershort = 0.0
        up = 0.0
        down = 0.0
        longe = 0.0
        shorte = 0.0
        stop_loss = 0.0
        entryvalueup = 0.0
        entryvaluedown = 0.0
        slup = 0.0
        sldown = 0.0
        longbuffer = 0.0
        shortbuffer = 0.0
        tampon_overbought = 0.0
        tampon_oversold = 0.0
        pos = 0.0

        up_series = np.zeros(size)
        down_series = np.zeros(size)
        close_long = np.zeros(size, dtype=bool)
        close_short = np.zeros(size, dtype=bool)
        longe_series = np.zeros(size)
        shorte_series = np.zeros(size)
        # The remaining `var` state is recorded per bar as well: emitting the
        # loop's final value instead would broadcast the last bar over the whole
        # frame, which both misreports the bar and leaks the future into the
        # prefix-recompute causality check.
        triggerlong_series = np.zeros(size)
        triggershort_series = np.zeros(size)
        longbuffer_series = np.zeros(size)
        shortbuffer_series = np.zeros(size)
        tampon_ob_series = np.zeros(size)
        tampon_os_series = np.zeros(size)
        sl_series = np.zeros(size)
        entryvalueup_series = np.zeros(size)
        entryvaluedown_series = np.zeros(size)
        slup_series = np.zeros(size)
        sldown_series = np.zeros(size)

        for i in range(size):
            # RSI latches
            if _pine_gt(rsi11[i], overbought):
                tampon_overbought = 1.0
            if _pine_lt(rsi11[i], oversold):
                tampon_oversold = 1.0

            # close condition SL
            if _pine_gt(entryvalueup, 0.0) and _pine_lt(low[i], slup):
                stop_loss = 1.0

            # Chaikin direction flag -- assigned, never read (dead code kept)
            if _pine_lt(x_roc_ema[i], trigger):
                pos = 1.0
            if _pine_gt(x_roc_ema[i], trigger):
                pos = -1.0

            # close conditions (read longe / shorte from the PREVIOUS bar)
            closelong = (
                (tampon_overbought == 1.0 and _pine_lt(rsi11[i], 63.8))
                or shorte != 0.0
                or stop_loss == 1.0
            )
            closeshort = (
                (tampon_oversold == 1.0 and _pine_gt(rsi11[i], 36.2))
                or longe != 0.0
                or stop_loss == 1.0
            )

            if closelong:
                up = 0.0
                longe = 0.0
                tampon_overbought = 0.0
                triggerlong = 0.0
                stop_loss = 0.0
                entryvalueup = 0.0

            if closeshort:
                down = 0.0
                shorte = 0.0
                tampon_oversold = 0.0
                triggershort = 0.0
                stop_loss = 0.0
                entryvaluedown = 0.0

            # trend trigger from the medium MA
            if _pine_lt(close[i], medium[i]):
                triggerlong = 0.0
                triggershort = 1.0
            if _pine_gt(close[i], medium[i]):
                triggershort = 0.0
                triggerlong = 1.0

            if long_signal[i] or along[i]:
                longbuffer = 1.0
            if short_signal[i] or ashort[i]:
                shortbuffer = 1.0

            longe = (
                1.0 if (longbuffer != 0.0 and triggerlong != 0.0
                         and _pine_gt(x_roc_ema[i], 3.5)) else 0.0
            )
            shorte = (
                1.0 if (shortbuffer != 0.0 and triggershort != 0.0
                         and _pine_gt(x_roc_ema[i], 3.5)) else 0.0
            )

            if longe == 1.0 and _pine_gt(close[i], open_[i]):
                up = 1.0
                down = 0.0
                entryvalueup = close[i]
                slup = close[i] - 0.7 * (high[i] - low[i])
                sldown = 0.0
                longbuffer = 0.0

            if shorte == 1.0 and _pine_lt(close[i], open_[i]):
                down = 1.0
                up = 0.0
                entryvaluedown = close[i]
                sldown = close[i] + 0.7 * (high[i] - low[i])
                slup = 0.0
                shortbuffer = 0.0

            up_series[i] = up
            down_series[i] = down
            longe_series[i] = longe
            shorte_series[i] = shorte
            close_long[i] = closelong
            close_short[i] = closeshort
            triggerlong_series[i] = triggerlong
            triggershort_series[i] = triggershort
            longbuffer_series[i] = longbuffer
            shortbuffer_series[i] = shortbuffer
            tampon_ob_series[i] = tampon_overbought
            tampon_os_series[i] = tampon_oversold
            sl_series[i] = stop_loss
            entryvalueup_series[i] = entryvalueup
            entryvaluedown_series[i] = entryvaluedown
            slup_series[i] = slup
            sldown_series[i] = sldown

        # ---- ledger columns (the record, not the behaviour) ----------------
        dataframe["pine_ma_coloured"] = ma_coloured
        dataframe["pine_ma_fast"] = ma_fast
        dataframe["pine_ma_medium"] = ma_medium
        dataframe["pine_ma_slow"] = ma_slow
        dataframe["pine_clrdirection"] = clrdirection
        dataframe["pine_madirection"] = madirection
        dataframe["pine_strend"] = strend
        dataframe["pine_tsl"] = tsl
        dataframe["pine_basis"] = basis
        dataframe["pine_upper"] = upper
        dataframe["pine_lower"] = lower
        dataframe["pine_noiupper"] = noiupper
        dataframe["pine_noilower"] = noilower
        dataframe["pine_oi_macross_upper"] = oi_macross_upper
        dataframe["pine_oi_macross_lower"] = oi_macross_lower
        for name, values in counters.items():
            dataframe[f"pine_{name}"] = values
        dataframe["pine_long"] = long_signal
        dataframe["pine_short"] = short_signal
        dataframe["pine_along"] = along
        dataframe["pine_ashort"] = ashort
        dataframe["pine_xroc_ema"] = x_roc_ema
        dataframe["pine_rsi11"] = rsi11
        dataframe["pine_tampon_overbought"] = tampon_ob_series
        dataframe["pine_tampon_oversold"] = tampon_os_series
        dataframe["pine_triggerlong"] = triggerlong_series
        dataframe["pine_triggershort"] = triggershort_series
        dataframe["pine_longbuffer"] = longbuffer_series
        dataframe["pine_shortbuffer"] = shortbuffer_series
        dataframe["pine_sl"] = sl_series
        dataframe["pine_entryvalueup"] = entryvalueup_series
        dataframe["pine_entryvaluedown"] = entryvaluedown_series
        dataframe["pine_slup"] = slup_series
        dataframe["pine_sldown"] = sldown_series
        dataframe["pine_longe"] = longe_series
        dataframe["pine_shorte"] = shorte_series
        dataframe["pine_up"] = up_series
        dataframe["pine_down"] = down_series
        dataframe["pine_closelong"] = close_long
        dataframe["pine_closeshort"] = close_short
        # `pos` is dead in the source; it is kept only as the record of a
        # variable the port deliberately does not act on.
        del pos
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "up": dataframe["pine_up"].to_numpy(),
            "down": dataframe["pine_down"].to_numpy(),
            "closelong": dataframe["pine_closelong"].to_numpy(),
            "closeshort": dataframe["pine_closeshort"].to_numpy(),
        }

    def pine_script(self, broker, i, ctx):
        # strategy.entry('longe', strategy.long, when = up)
        broker.entry("longe", "long", when=bool(ctx["up"][i]))
        # strategy.entry('shorte', strategy.short, when = down)
        broker.entry("shorte", "short", when=bool(ctx["down"][i]))
        # strategy.close('longe', when = closelong)
        broker.close("longe", when=bool(ctx["closelong"][i]))
        # strategy.close('shorte', when = closeshort)
        broker.close("shorte", when=bool(ctx["closeshort"][i]))
