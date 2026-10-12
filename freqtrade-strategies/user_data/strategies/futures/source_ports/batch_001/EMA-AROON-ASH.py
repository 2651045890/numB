"""Port of sources/SM_90aa8e71878ddd46.pine (batch_001/EMA-AROON-ASH.md).

Pine v5. A three-indicator conjunction (200 EMA + Aroon cross + jiehonglim's
Absolute Strength Histogram v2), long/short, with an OCA stop/take-profit
anchored to a rolling low/high:

    EMA         = ta.ema(EMA_src, EMA_length)                        # 200, close
    Aroon_upper = 100 * (ta.highestbars(high, Aroon_length + 1) + Aroon_length) / Aroon_length
    Aroon_lower = 100 * (ta.lowestbars(low,   Aroon_length + 1) + Aroon_length) / Aroon_length

    Price1 = _MA('SMA', ASH_src, 1)            # == ASH_src
    Price2 = _MA('SMA', ASH_src[1], 1)         # == ASH_src[1]
    Bulls0 = 0.5 * (math.abs(Price1 - Price2) + Price1 - Price2)   # up move
    Bears0 = 0.5 * (math.abs(Price1 - Price2) - (Price1 - Price2)) # down move
    Bulls1 = Price1 - ta.lowest(Price1, ASH_Length)
    Bears1 = ta.highest(Price1, ASH_Length) - Price1
    Bulls2 = 0.5 * (math.abs(high - high[1]) + high - high[1])
    Bears2 = 0.5 * (math.abs(low[1] - low) + low[1] - low)
    Bulls  = ASH_Mode == 'RSI' ? Bulls0 : ASH_Mode == 'STOCHASTIC' ? Bulls1 : Bulls2
    Bears  = ASH_Mode == 'RSI' ? Bears0 : ASH_Mode == 'STOCHASTIC' ? Bears1 : Bears2
    AvgBulls  = _MA(ASH_ma_type, Bulls, ASH_Length)     # WMA, 9
    SmthBulls = _MA(ASH_ma_type, AvgBulls, ASH_Smooth)  # WMA, 3
    (AvgBears / SmthBears the same)

    long_conditions  = close > EMA       and ta.crossover(Aroon_upper, Aroon_lower)
                                          and SmthBulls > SmthBears
    short_conditions = close < EMA       and ta.crossunder(Aroon_upper, Aroon_lower)
                                          and SmthBulls < SmthBears

    entrar_en_LONG  = P_permitir_LONGS  and long_conditions
                      and vela_en_fecha and not posicion_abierta
    entrar_en_SHORT = P_permitir_SHORTS and short_conditions
                      and vela_en_fecha and not posicion_abierta

    psl = ta.lowest(TPSL_TP_pivot_lookback)          # rolling low over 20 bars
    psh = ta.highest(TPSL_TP_pivot_lookback)         # rolling high over 20 bars

    if (entrar_en_LONG)
        LONG_stop_loss   := psl - close*0.001
        LONG_take_profit := close + ((close - LONG_stop_loss) * TPSL_SL_mult)
        strategy.entry("+ Long", strategy.long)
        strategy.exit("- Long", "+ Long", limit=LONG_take_profit, stop=LONG_stop_loss)

    if (entrar_en_SHORT)
        SHORT_stop_loss   := psh + close*0.001
        SHORT_take_profit := close - ((SHORT_stop_loss - close) * TPSL_SL_mult)
        strategy.entry("+ Short", strategy.short)
        strategy.exit("- Short", "+ Short", limit=SHORT_take_profit, stop=SHORT_stop_loss)

`not posicion_abierta` is a hard one-position gate, so the two branches are
mutually exclusive (a bar cannot be both above and below the EMA anyway) and
there is never a reversal in flight. `strategy.entry` is written BEFORE
`strategy.exit` inside each branch, and the port keeps that order: Pine's own
write order is the engine's fill priority, and the exit must be resting on the
entry's own fill bar (PINE_SEMANTICS.md 1.9).

`timeframe` is "3m" from the `/*backtest` header (`period: 3m`); its
`basePeriod: 1m` is the FMZ backtester's own fill granularity, not the
strategy's period.

`strategy()` IS COMMENTED OUT (source line 31). A commented-out line declares
nothing -- the same rule PINE_SEMANTICS.md 1.17 applies to commented-out exit
lines -- so Pine's documented defaults are in force: `strategy.fixed` / 1
contract, initial capital 1000000, commission 0%, `pyramiding = 0`,
`process_orders_on_close = false`. The commented line asks for something
different (initial_capital 10000, `percent_of_equity` / 10,
`commission_value = 0.00075`, `max_bars_back = 1000`) and it is recorded in
source_fidelity_notes rather than applied.

The source is NOT a converter-appended order block, despite its tier_reason.
It declares no `indicator()` and no `study()`, its only `strategy()` line is
commented out, and both order pairs are the author's own active code with a
live `strategy.exit` beside each `strategy.entry`. The tier_reason's "declares
indicator()/study(), tool appended strategy.entry pair; NO exits" is false on
all three counts; the source is followed.

FIDELITY -- translation choices and source/md mismatches:

1. ORDER OF `strategy.entry` / `strategy.exit` is preserved verbatim (entry
   first, then the exit that names it), so the stop and the take-profit are
   already resting while the entry's own fill bar trades -- the engine records
   those levels for exactly that bar (PINE_SEMANTICS.md 1.9) and both legs are
   reproduced: `stop=` through the engine's stop level and the port's
   `custom_stoploss`, `limit=` through the engine's limit level and the port's
   ROI hooks. `source_reproduce_stops` is True.
2. `LONG_stop_loss` / `LONG_take_profit` / `SHORT_stop_loss` /
   `SHORT_take_profit` are `var` floats in the source, but they are written and
   read inside the SAME branch on the SAME bar, so nothing crosses a bar: the
   only other readers are the display-only `plot`/`fill` calls at the bottom of
   the file. They are computed as locals here; the `var` persistence is not
   modelled because no order depends on it.
3. `ta.highestbars` / `ta.lowestbars` are NOT in `pine_ta` and are implemented
   here from their Pine definition: the offset to the window extreme, as a
   NEGATIVE number (0 = this bar, -(length-1) = the oldest bar in the window),
   na until the window is full and na if the window holds an na. Ties resolve to
   the MOST RECENT occurrence, which is what a backwards scan from the current
   bar yields; TradingView does not document the tie-break, so it is an
   equivalence risk of the PINE_SEMANTICS.md section 三 kind. Same helper and
   same convention as this batch's Bollinger带震荡型突破策略 port.
4. `ta.lowest(TPSL_TP_pivot_lookback)` / `ta.highest(TPSL_TP_pivot_lookback)`
   are called with ONE argument. The v5 signature is `ta.lowest(source,
   length)`, and a single integer argument is the v4 `lowest(length)` idiom,
   which reads the rolling extreme of `low` / `high`; the commented-out
   `ta.pivotlow` / `ta.pivothigh` pair on the two lines above shows that the
   author's intent is a rolling extreme, not a pivot. Implemented as
   `pine_lowest(low, n)` / `pine_highest(high, n)`. `psh` feeds only the SHORT
   stop; `psl` feeds only the LONG stop.
5. `psl` / `psh` are na for the first 19 bars; the entry can never fire there
   because it also needs a 200-period EMA, a 21-bar Aroon window and an 11-bar
   ASH window, so no order is placed on a na stop level.
6. `_MA(type, src, len)` is transcribed in FULL -- all six selectable types
   (SMA, EMA, WMA, SMMA, HMA, ALMA) -- so overriding `ASH_ma_type` cannot
   silently fall through to some other average. The declared default is WMA,
   which is the only branch the source's own settings exercise.
   * `SMMA` is transcribed literally, including the fact that its `w[1]` is the
     PREVIOUS BAR'S `ta.wma(src, len)` value and not its own previous output
     (`result` is not `var`, so it does not recurse on itself). That makes it a
     one-step blend of a WMA, not Wilder smoothing -- which is what the source
     writes.
   * `HMA`'s `len / 2` is treated as INTEGER division, the convention already
     recorded by this corpus's 72s-Adaptive-Hull-Moving-Average and
     2-Moving-Average-Color-Direction-Detection ports; TradingView's `/` on two
     integers returns a float and `ta.wma`'s length is a `series int`, so the
     two readings differ and only the original platform can settle it.
   * `ALMA` is transcribed from TradingView's published sample implementation
     (`m = floor(offset*(len-1))`, `s = len/sigma`, weights
     `exp(-(i-m)^2 / (2*s^2))` normalised, applied oldest-to-newest), because
     `pine_ta` has no `ta.alma`. A non-positive sigma makes it na, as Pine's
     division by zero does.
7. The `ASH_Mode` selector: all three branches (RSI / STOCHASTIC / ADX) are
   computed, and `Bulls1` / `Bears1` / `Bulls2` / `Bears2` are materialised even
   though the RSI default reads none of them. Dead code is kept, not deleted.
   The nested ternary is Pine's
   `mode == 'RSI' ? Bulls0 : mode == 'STOCHASTIC' ? Bulls1 : Bulls2`.
8. `difference = math.abs(SmthBulls - SmthBears)` is computed by the source and
   read by nothing; it is reproduced as a column and not used.
9. `vela_en_fecha = true` is a bare literal in the source; the
   `fecha_inicio = input.time(...)` line above it is COMMENTED OUT, so there is
   no date window at all and every bar is eligible. The port carries
   `vela_en_fecha` as the constant True rather than dropping the conjunct.
10. `close` in `close > EMA`, `close < EMA` and in `psl - close*0.001` is the
    bar's raw `close`, NOT `EMA_src` / `ASH_src`: overriding either source
    selector moves the indicator but not this comparison. Reproduced as
    written.
11. `EMA_src` and `ASH_src` are two separate `input(close)` selectors, both
    defaulting to `close`; they are kept as separate parameters so an override
    of one does not move the other.
12. MD/SOURCE MISMATCH (timeframe): the md's personal note recommends 5-minute
    charts and says 4H "shows to be the best"; the `/*backtest` header of the
    same file declares `period: 3m`, and the FMZ backtest this port reproduces
    ran on 3m. The header is followed.
13. MD/SOURCE MISMATCH (rendered defaults): the md's argument table renders
    `v_input_1_close` / `v_input_4_close` (the two `input(close)` source
    selectors) as `0`, the string selectors `v_input_string_1` /
    `v_input_string_2` as `0`, and `v_input_float_2` as `0.85` with no group.
    The source's real defaults are `close`, `'RSI'`, `'WMA'` and `0.85`
    respectively, and are what is declared here.
14. `pyramiding = 0` (Pine's default, and also what the commented line asks
    for): a same-direction entry while a position is open is ignored entirely,
    so the `not posicion_abierta` gate is the only thing that lets an entry
    through and the two can never disagree.
15. EMA seeding is the modelled choice recorded in PINE_SEMANTICS.md 3.1 (first
    non-na value), where TradingView's `ta.ema` is generally believed to seed
    with the SMA of the first `length` values. The 200-period EMA gates every
    entry, so the first ~200 bars are a known, un-eliminated early-trade
    equivalence risk for this port in particular.
16. The `/*backtest` header's exchange is `Futures_Binance` / `BTC_USDT`; the
    repo's chain verification uses `BTC/USDT:USDT`. That is a venue mapping, not
    a source property. Leverage, margin, liquidation, funding and the venue's
    contract-step rounding are not modelled; the step rounding is measured
    separately by the chain verifier (PINE_SEMANTICS.md 1.6).
17. `max_bars_back = 1000` (commented line) and the 200-period EMA: this engine
    has no bar-history limit, so nothing is truncated, but the declaration is
    inert anyway.
18. `bgcolor`, `plot`, `fill`, the colour constants and the title are
    display-only and are not reproduced.
"""
import numpy as np
import pandas as pd
from numpy.lib.stride_tricks import sliding_window_view

from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


def _extreme_offset(values, length: int, highest: bool) -> np.ndarray:
    """Pine `ta.highestbars` / `ta.lowestbars`: offset (<= 0) to the extreme.

    Pine returns the offset as a negative number -- 0 for the current bar,
    -(length-1) for the oldest bar in the window -- and na until `length` bars
    have elapsed or when the window holds an na. Ties resolve to the MOST RECENT
    occurrence: a backwards scan from the current bar stops at the first match.
    TradingView does not document the tie-break, so this is recorded as an
    equivalence risk rather than a certified rule (cf. PINE_SEMANTICS.md
    section 三).
    """
    values = np.asarray(values, dtype=float)
    length = int(length)
    out = np.full(values.shape[0], np.nan)
    if length < 1 or values.shape[0] < length:
        return out
    windows = sliding_window_view(values, length)
    finite = ~np.isnan(windows)
    complete = finite.all(axis=1)
    filled = np.where(finite, windows, -np.inf if highest else np.inf)
    extreme = filled.max(axis=1) if highest else filled.min(axis=1)
    equal = (windows == extreme[:, None]) & complete[:, None]
    # Reversing makes argmax return the SMALLEST reversed index, i.e. the newest
    # matching bar; the Pine offset is `-r` for that reversed index.
    block = -np.argmax(equal[:, ::-1], axis=1).astype(float)
    block[~complete] = np.nan
    out[length - 1:] = block
    return out


def _alma(source: pd.Series, length: int, offset: float, sigma: float) -> pd.Series:
    """Pine `ta.alma`, from TradingView's published sample implementation.

    `m = floor(offset * (len - 1))`, `s = len / sigma`, weights
    `exp(-(i - m)^2 / (2 * s^2))` normalised over `i = 0..len-1`, applied to
    `series[len - i - 1]` (oldest first). A non-positive sigma divides by zero,
    which is na in Pine, so the whole average is na.
    """
    values = source.to_numpy(dtype=float)
    length = int(length)
    out = np.full(values.shape[0], np.nan)
    if length < 1 or values.shape[0] < length or float(sigma) <= 0:
        return pd.Series(out, index=source.index, dtype=float)
    m = int(np.floor(float(offset) * (length - 1)))
    s = length / float(sigma)
    weights = np.exp(-((np.arange(length) - m) ** 2) / (2.0 * s * s))
    weights = weights / weights.sum()
    windows = sliding_window_view(values, length)
    complete = ~np.isnan(windows).any(axis=1)
    out[length - 1:] = np.where(complete, windows @ weights, np.nan)
    return pd.Series(out, index=source.index, dtype=float)


def _ma(kind, source, length: int, alma_offset: float = 0.85,
        alma_sigma: float = 6.0) -> pd.Series:
    """The source's `_MA(type, src, len)`, all six branches transcribed.

    The single-value function returns `result`, assigned in exactly one of the
    (non-`var`) if-blocks, so it is a plain selector: no branch recurses on its
    own output.
    """
    kind = str(kind).strip().upper()
    length = int(length)
    if kind == "SMA":
        return ta.pine_sma(source, length)
    if kind == "EMA":
        return ta.pine_ema(source, length)
    if kind == "WMA":
        return ta.pine_wma(source, length)
    if kind == "SMMA":
        # w = ta.wma(src, len)
        # result := na(w[1]) ? ta.sma(src, len) : (w[1] * (len - 1) + src) / len
        wma = ta.pine_wma(source, length)
        previous = wma.shift(1)
        blended = (previous * (length - 1) + source) / length
        return blended.where(previous.notna(), ta.pine_sma(source, length))
    if kind == "HMA":
        # ta.wma(2 * ta.wma(src, len / 2) - ta.wma(src, len), math.round(math.sqrt(len)))
        inner = 2 * ta.pine_wma(source, length // 2) - ta.pine_wma(source, length)
        return ta.pine_wma(inner, int(round(np.sqrt(length))))
    if kind == "ALMA":
        return _alma(source, length, alma_offset, alma_sigma)
    raise ValueError(f"unrecognised _MA type {kind!r}")


class SMEmaAroonAsh_90aa8e(PinePortBase, IStrategy):
    source_id = "SM_90aa8e71878ddd46"
    source_file = "EMA-AROON-ASH.md"
    timeframe = "3m"
    # Both a `strategy.entry(..., strategy.long)` and a
    # `strategy.entry(..., strategy.short)` are in the source.
    can_short = True
    source_defaults: dict = {
        # input.bool(title="¿LONGS?", group="Positions", defval=true)
        "P_permitir_LONGS": True,
        # input.bool(title="¿SHORTS?", group="Positions", defval=true)
        "P_permitir_SHORTS": True,
        # input.int("• SL lookback for pivot / Mult. TP", defval=20, minval=1)
        "TPSL_TP_pivot_lookback": 20,
        # input.float("", defval=2.0, minval=0.1, step=0.2)
        "TPSL_SL_mult": 2.0,
        # input.int(200, minval=1, title="Length", group="EMA")
        "EMA_length": 200,
        # input(close, title="Source", group="EMA") -- source selector.
        "EMA_src": "close",
        # input.int("• Length", group="Aroon", defval=20, minval=1)
        "Aroon_length": 20,
        # input(9, title='Period of Evaluation', group="Absolute Strength Histogram v2 | jh")
        "ASH_Length": 9,
        # input(3, title='Period of Smoothing', group=...)
        "ASH_Smooth": 3,
        # input(close, title='Source') -- source selector.
        "ASH_src": "close",
        # input.string(defval='RSI', options=['RSI', 'STOCHASTIC', 'ADX'])
        "ASH_Mode": "RSI",
        # input.string(defval='WMA', options=['ALMA','EMA','WMA','SMA','SMMA','HMA'])
        "ASH_ma_type": "WMA",
        # input.float(defval=0.85, minval=0, step=0.01) -- ALMA only.
        "ASH_alma_offset": 0.85,
        # input.int(defval=6, minval=0) -- ALMA only.
        "ASH_alma_sigma": 6,
    }
    # The ONLY strategy() declaration in the file (line 31) is commented out, so
    # it declares nothing: Pine's documented defaults apply -- `strategy.fixed`
    # / 1 contract, initial capital 1000000, commission 0%, pyramiding 0,
    # process_orders_on_close false. The commented line asks for
    # initial_capital=10000, default_qty_type=strategy.percent_of_equity,
    # default_qty_value=10 and commission_value=0.00075; none of it is in force.
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    # Each entry is paired with a live `strategy.exit(stop=..., limit=...)`.
    source_reproduce_stops = True
    source_fidelity_notes = [
        "NOT a converter-appended order block, despite its tier_reason: the "
        "file declares no indicator() and no study(), its only strategy() line "
        "(line 31) is COMMENTED OUT, and both order pairs are the author's own "
        "active code -- strategy.entry with a live strategy.exit(stop=, limit=) "
        "beside it on the same branch. The tier_reason's 'declares "
        "indicator()/study(), tool appended strategy.entry pair; NO exits' is "
        "false on all three counts. The source is followed.",
        "The file's only strategy() declaration is COMMENTED OUT (line 31), so "
        "it declares nothing and Pine's documented defaults apply: "
        "default_qty_type fixed / 1 contract, initial_capital 1000000, "
        "commission 0%, pyramiding 0, process_orders_on_close false. A "
        "commented-out line is inert -- the same rule PINE_SEMANTICS.md 1.17 "
        "applies to commented-out exit lines.",
        "RECORDED BUT NOT APPLIED (commented out): the declaration asks for "
        "initial_capital=10000, default_qty_type=strategy.percent_of_equity with "
        "default_qty_value=10, commission_type=strategy.commission.percent with "
        "commission_value=0.00075, max_labels_count=500 and max_bars_back=1000. "
        "None of it is in force. Worth flagging because initial_capital is the "
        "variable that decides how much the venue's contract step eats "
        "(PINE_SEMANTICS.md 1.6): 10000 would have been far more exposed than "
        "the 1000000 that is actually in force.",
        "ORDER: strategy.entry is written BEFORE the strategy.exit that names "
        "it, inside the same `if` branch, and the port keeps that order. The "
        "exit therefore rests while the entry's own fill bar trades, which is "
        "the same-bar-stop case PINE_SEMANTICS.md 1.9 describes; both the stop "
        "leg (custom_stoploss + pine_stop_level) and the limit leg (ROI hooks + "
        "pine_limit_level) are reproduced.",
        "LONG_stop_loss / LONG_take_profit / SHORT_stop_loss / SHORT_take_profit "
        "are `var` floats in the source, but each is written and read inside the "
        "same branch on the same bar and its only other readers are the "
        "display-only plot/fill calls, so the port computes them as locals. No "
        "order depends on their persistence.",
        "ta.highestbars / ta.lowestbars are not in pine_ta and are implemented "
        "here from the Pine definition (negative offset to the window extreme, "
        "na until the window is full). Ties resolve to the MOST RECENT "
        "occurrence, which TradingView does not document -- an equivalence risk "
        "of the PINE_SEMANTICS.md section 三 kind. Same helper and convention as "
        "this batch's Bollinger带震荡型突破策略 port.",
        "ta.lowest(TPSL_TP_pivot_lookback) / ta.highest(TPSL_TP_pivot_lookback) "
        "are called with ONE argument: the v5 signature is ta.lowest(source, "
        "length), so the single integer is the v4 lowest(length) idiom reading "
        "`low` / `high`, which the commented-out ta.pivotlow / ta.pivothigh pair "
        "on the lines above confirms was the author's intent. Implemented as "
        "pine_lowest(low, 20) / pine_highest(high, 20).",
        "_MA(type, src, len) is transcribed in FULL -- all six selectable types "
        "(SMA, EMA, WMA, SMMA, HMA, ALMA) -- so an override of ASH_ma_type "
        "cannot silently fall through to a different average. The declared "
        "default is WMA, which is the only branch the source's own settings "
        "exercise.",
        "SMMA is transcribed literally: its w[1] is the PREVIOUS bar's "
        "ta.wma(src, len), not its own previous output (result is not `var`), "
        "so it is a one-step blend of a WMA rather than Wilder smoothing. That "
        "is what the source writes.",
        "HMA's `len / 2` is treated as INTEGER division, the convention already "
        "recorded by this corpus's 72s-Adaptive-Hull-Moving-Average and "
        "2-Moving-Average-Color-Direction-Detection ports. TradingView's `/` on "
        "two integers yields a float and ta.wma takes a series int, so the two "
        "readings differ and only the original platform can settle it.",
        "ALMA is transcribed from TradingView's published sample implementation "
        "(m = floor(offset*(len-1)), s = len/sigma, normalised "
        "exp(-(i-m)^2/(2*s^2)) weights applied oldest-first) because pine_ta has "
        "no ta.alma. A non-positive sigma divides by zero, which is na in Pine, "
        "so the average is na.",
        "The ASH_Mode selector: all three branches (RSI / STOCHASTIC / ADX) are "
        "computed and Bulls1 / Bears1 / Bulls2 / Bears2 are materialised even "
        "though the RSI default reads none of them. Dead code is kept, not "
        "deleted. The nested ternary is Pine's "
        "mode == 'RSI' ? Bulls0 : mode == 'STOCHASTIC' ? Bulls1 : Bulls2.",
        "difference = math.abs(SmthBulls - SmthBears) is computed by the source "
        "and read by nothing; reproduced as a column and unused.",
        "vela_en_fecha = true is a bare literal; the "
        "`//fecha_inicio = input.time(timestamp(\"1 Jan 2000\"), ...)` line "
        "above it is COMMENTED OUT, so there is no date window and every bar is "
        "eligible. The port carries the conjunct as the constant True rather "
        "than dropping it.",
        "`close` in `close > EMA`, `close < EMA` and in `psl - close*0.001` is "
        "the bar's raw close, NOT EMA_src / ASH_src: overriding either source "
        "selector moves the indicator but not this comparison. Reproduced as "
        "written. EMA_src and ASH_src are two separate input(close) selectors "
        "and are kept as separate parameters.",
        "MD/SOURCE MISMATCH (timeframe): the md's personal note recommends "
        "5-minute charts and says 4H shows to be the best; the /*backtest header "
        "of the same file declares `period: 3m`, which is the period the FMZ "
        "backtest ran on. The header is followed.",
        "MD/SOURCE MISMATCH (rendered defaults): the md's argument table renders "
        "both input(close) source selectors as 0, the two input.string selectors "
        "as 0, and labels ASH_alma_offset without a group. The source's real "
        "defaults are close / close / 'RSI' / 'WMA' / 0.85 and are what is "
        "declared here.",
        "pyramiding = 0 (Pine's default, and also what the commented line asks "
        "for): a same-direction entry while a position is open is ignored "
        "outright by the engine at creation time, so the source's "
        "`not posicion_abierta` gate and the engine's pyramiding rule can never "
        "disagree.",
        "EMA seeding is the modelled choice in PINE_SEMANTICS.md 3.1 (first "
        "non-na value), where TradingView's ta.ema is generally believed to seed "
        "with the SMA of the first `length` values. The 200-period EMA gates "
        "every entry, so the first ~200 bars are a known, un-eliminated "
        "early-trade equivalence risk for this port.",
        "The /*backtest header names Futures_Binance / BTC_USDT while the repo's "
        "chain verification uses BTC/USDT:USDT -- a venue mapping, not a source "
        "property. Leverage, margin, liquidation, funding and the venue's "
        "contract-step rounding are not modelled (PINE_SEMANTICS.md 1.6 "
        "measures the step rounding separately).",
        "max_bars_back = 1000 (commented line) and the 200-period EMA: this "
        "engine has no bar-history limit, so nothing is truncated, and the "
        "declaration is inert anyway.",
        "bgcolor / plot / fill, the colour constants and the title are "
        "display-only and are not reproduced.",
    ]

    def pine_indicators(self, dataframe, params):
        close = dataframe["close"]
        high = dataframe["high"]
        low = dataframe["low"]
        ema_source = ta.pine_source(dataframe, str(params["EMA_src"]))
        ash_source = ta.pine_source(dataframe, str(params["ASH_src"]))

        # EMA = ta.ema(EMA_src, EMA_length)
        ema = ta.pine_ema(ema_source, int(params["EMA_length"]))

        # Aroon_upper = 100 * (ta.highestbars(high, Aroon_length+1) + Aroon_length) / Aroon_length
        # Aroon_lower = 100 * (ta.lowestbars(low,   Aroon_length+1) + Aroon_length) / Aroon_length
        aroon_length = int(params["Aroon_length"])
        aroon_upper = pd.Series(
            100.0 * (_extreme_offset(high, aroon_length + 1, True) + aroon_length)
            / aroon_length,
            index=dataframe.index, dtype=float,
        )
        aroon_lower = pd.Series(
            100.0 * (_extreme_offset(low, aroon_length + 1, False) + aroon_length)
            / aroon_length,
            index=dataframe.index, dtype=float,
        )

        # Absolute Strength Histogram v2 | jh
        ash_length = int(params["ASH_Length"])
        ash_smooth = int(params["ASH_Smooth"])
        mode = str(params["ASH_Mode"])
        ma_type = str(params["ASH_ma_type"])
        alma_offset = float(params["ASH_alma_offset"])
        alma_sigma = float(params["ASH_alma_sigma"])

        price1 = _ma("SMA", ash_source, 1)
        price2 = _ma("SMA", ash_source.shift(1), 1)

        # RSI
        spread = price1 - price2
        bulls0 = 0.5 * (spread.abs() + spread)
        bears0 = 0.5 * (spread.abs() - spread)
        # STOCHASTIC
        bulls1 = price1 - ta.pine_lowest(price1, ash_length)
        bears1 = ta.pine_highest(price1, ash_length) - price1
        # ADX
        high_move = high - high.shift(1)
        low_move = low.shift(1) - low
        bulls2 = 0.5 * (high_move.abs() + high_move)
        bears2 = 0.5 * (low_move.abs() + low_move)

        bulls = bulls0 if mode == "RSI" else (bulls1 if mode == "STOCHASTIC" else bulls2)
        bears = bears0 if mode == "RSI" else (bears1 if mode == "STOCHASTIC" else bears2)
        avg_bulls = _ma(ma_type, bulls, ash_length, alma_offset, alma_sigma)
        avg_bears = _ma(ma_type, bears, ash_length, alma_offset, alma_sigma)
        smth_bulls = _ma(ma_type, avg_bulls, ash_smooth, alma_offset, alma_sigma)
        smth_bears = _ma(ma_type, avg_bears, ash_smooth, alma_offset, alma_sigma)
        difference = (smth_bulls - smth_bears).abs()

        # psl = ta.lowest(TPSL_TP_pivot_lookback)
        # psh = ta.highest(TPSL_TP_pivot_lookback)
        lookback = int(params["TPSL_TP_pivot_lookback"])
        psl = ta.pine_lowest(low, lookback)
        psh = ta.pine_highest(high, lookback)

        dataframe["pine_ema"] = ema
        dataframe["pine_aroon_upper"] = aroon_upper
        dataframe["pine_aroon_lower"] = aroon_lower
        dataframe["pine_bulls0"] = bulls0
        dataframe["pine_bears0"] = bears0
        dataframe["pine_bulls1"] = bulls1
        dataframe["pine_bears1"] = bears1
        dataframe["pine_bulls2"] = bulls2
        dataframe["pine_bears2"] = bears2
        dataframe["pine_avg_bulls"] = avg_bulls
        dataframe["pine_avg_bears"] = avg_bears
        dataframe["pine_smth_bulls"] = smth_bulls
        dataframe["pine_smth_bears"] = smth_bears
        dataframe["pine_difference"] = difference
        dataframe["pine_psl"] = psl
        dataframe["pine_psh"] = psh

        # EMA_alcista = close > EMA ; EMA_bajista = close < EMA
        ema_alcista = close > ema
        ema_bajista = close < ema
        # Aroon_cruce_alcista = ta.crossover(Aroon_upper, Aroon_lower)
        # Aroon_cruce_bajista = ta.crossunder(Aroon_upper, Aroon_lower)
        aroon_cruce_alcista = ta.pine_crossover(aroon_upper, aroon_lower)
        aroon_cruce_bajista = ta.pine_crossunder(aroon_upper, aroon_lower)
        # ASH_alcista = SmthBulls > SmthBears ; ASH_bajista = SmthBulls < SmthBears
        ash_alcista = smth_bulls > smth_bears
        ash_bajista = smth_bulls < smth_bears

        # long_conditions  = EMA_alcista  and Aroon_cruce_alcista  and ASH_alcista
        # short_conditions = EMA_bajista  and Aroon_cruce_bajista and ASH_bajista
        dataframe["pine_long_conditions"] = (
            ema_alcista & aroon_cruce_alcista & ash_alcista
        ).fillna(False)
        dataframe["pine_short_conditions"] = (
            ema_bajista & aroon_cruce_bajista & ash_bajista
        ).fillna(False)
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "close": dataframe["close"].to_numpy(dtype=float),
            "long_conditions": dataframe["pine_long_conditions"].to_numpy(dtype=bool),
            "short_conditions": dataframe["pine_short_conditions"].to_numpy(dtype=bool),
            "psl": dataframe["pine_psl"].to_numpy(dtype=float),
            "psh": dataframe["pine_psh"].to_numpy(dtype=float),
            # input.bool inputs: constant for the whole run.
            "permitir_long": bool(params["P_permitir_LONGS"]),
            "permitir_short": bool(params["P_permitir_SHORTS"]),
            "sl_mult": float(params["TPSL_SL_mult"]),
            # vela_en_fecha = true (the input.time line above it is commented out)
            "vela_en_fecha": True,
        }

    def pine_script(self, broker, i, ctx):
        # posicion_abierta = strategy.position_size != 0
        posicion_abierta = broker.position_size != 0

        # if (entrar_en_LONG)
        if (ctx["permitir_long"] and ctx["long_conditions"][i]
                and ctx["vela_en_fecha"] and not posicion_abierta):
            close = float(ctx["close"][i])
            # LONG_stop_loss   := psl - close*0.001
            long_stop_loss = float(ctx["psl"][i]) - close * 0.001
            # LONG_take_profit := close + ((close - LONG_stop_loss) * TPSL_SL_mult)
            long_take_profit = close + ((close - long_stop_loss) * ctx["sl_mult"])
            # strategy.entry("+ Long", strategy.long)
            broker.entry("+ Long", "long")
            # strategy.exit("- Long", "+ Long", limit=LONG_take_profit, stop=LONG_stop_loss)
            broker.exit("- Long", "+ Long", limit=long_take_profit, stop=long_stop_loss)

        # if (entrar_en_SHORT)
        if (ctx["permitir_short"] and ctx["short_conditions"][i]
                and ctx["vela_en_fecha"] and not posicion_abierta):
            close = float(ctx["close"][i])
            # SHORT_stop_loss   := psh + close*0.001
            short_stop_loss = float(ctx["psh"][i]) + close * 0.001
            # SHORT_take_profit := close - ((SHORT_stop_loss - close) * TPSL_SL_mult)
            short_take_profit = close - ((short_stop_loss - close) * ctx["sl_mult"])
            # strategy.entry("+ Short", strategy.short)
            broker.entry("+ Short", "short")
            # strategy.exit("- Short", "+ Short", limit=SHORT_take_profit, stop=SHORT_stop_loss)
            broker.exit("- Short", "+ Short", limit=short_take_profit, stop=short_stop_loss)
