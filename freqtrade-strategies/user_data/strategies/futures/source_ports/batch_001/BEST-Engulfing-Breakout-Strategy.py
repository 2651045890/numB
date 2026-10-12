"""Port of sources/SM_0a5ae58e59c095ab.pine (batch_001/BEST-Engulfing-Breakout-Strategy.md).

Pine v4, 30-minute chart, long AND short, by Daveatt ("BEST Engulfing + MA").
A two-candle engulfing pattern and a price-versus-moving-average cross must
AGREE, and the resulting state machine is then read off two `barssince`
distances:

    GreenCandle = close > open ; RedCandle = close < open ; NoBody = close==open
    Body = abs(close-open)

    isBullishEngulfing1/2  -> isBullishEngulfing
    isBearishEngulfing1/2  -> isBearishEngulfing

    Engulf_curr = 0 - barssince(isBearishEngulfing) + barssince(isBullishEngulfing)
    Engulf_Buy  = Engulf_curr < 0 ? 1 : 0
    Engulf_Sell = Engulf_curr > 0 ? 1 : 0

    MA = ma(typeofMA, source_ma, length_ma)
    macrossover / macrossunder = crossover / crossunder(source_ma, MA)
    macross_curr   = 0 - barssince(macrossunder) + barssince(macrossover)
    bullish_MA_cond = macross_curr < 0 ? 1 : 0
    bearish_MA_cond = macross_curr > 0 ? 1 : 0

    posUp = (Engulf_Buy  ? 1 : 0) + (bullish_MA_cond ? 1 : 0)
    posDn = (Engulf_Sell ? 1 : 0) + (bearish_MA_cond ? 1 : 0)
    conditionUP = posUp == 2 and posUp[1] < 2
    conditionDN = posDn == 2 and posDn[1] < 2

    nUP = crossunder(barssince(conditionUP), barssince(conditionDN))
    nDN = crossover (barssince(conditionUP), barssince(conditionDN))
    buy_trend  = barssince(nDN) > barssince(nUP)
    sell_trend = barssince(nDN) < barssince(nUP)

    tp = buy_trend ? long_entry_price  + input_tp_pips : short_entry_price - input_tp_pips
    sl = buy_trend ? long_entry_price  - input_sl_pips : short_entry_price + input_sl_pips

    if testPeriod()                                   // testPeriod() => true
        strategy.entry("Long",  1, when=isLong)       // 1 == strategy.long
        strategy.close("Long",  when=longClose)
        strategy.exit("XL", "Long", limit=tp, when=buy_trend, stop=sl)
    if testPeriod()
        strategy.entry("Short", 0, when=isShort)      // 0 == strategy.short
        strategy.close("Short", when=shortClose)
        strategy.exit("XS", "Short", when=sell_trend, limit=tp, stop=sl)

SIX order calls, in that exact written order, and the order is preserved here
because it is the engine's fill priority on a bar where more than one fires.

FIDELITY -- translation choices and source/md mismatches:

1. `ma(smoothing, src, length)` is a hand-written if/else-if chain over TWELVE
   smoothing names (RMA, SMA, EMA, WMA, VWMA, SMMA, HullMA, LSMA, KMA, TMA,
   DEMA, TEMA) plus a final `src` fallback. EVERY branch is implemented,
   including the ones the default `typeofMA = "SMA"` can never reach, so a
   `source_parameters` override of `typeofMA` selects the source's own formula.
   All thirteen outcomes were EXECUTED against a probe series while this port
   was audited, not merely read: none raises.
   Two of them are quirky and are reproduced as written, not "corrected":
   `TMA` is `sma(sma(close, length), length)` -- it reads the BAR'S `close`, not
   the function's `src` parameter -- and `DEMA` / `TEMA` are the one- and
   two-term expressions the source writes, which are not the textbook DEMA/TEMA.
2. `"LSMA"` is tested by the chain but is NOT in the input's option list, so it
   is unreachable from the input while still being reachable code; the final
   `else -> src` is likewise unreachable from the option list. Both are kept.
3. `smma(src, len)` is `na(smma[1]) ? sma(src, len) : (smma[1]*(len-1)+src)/len`
   with `smma` declared `0.0` -- so it stays na until `sma` produces its first
   value and then recurses. It is NOT `pine_rma` (which seeds by averaging the
   first window into the same recursion) and is written out in `_smma`.
4. `KMA`'s block is indented inconsistently in the extracted source (8 tabs plus
   4 spaces for the `if`, then a run of 40 spaces for the body). It is
   reproduced as ONE block inside the KMA branch, which is the only reading under
   which the following `else` chain is well-formed. Whether the original platform
   parsed it that way is UNVERIFIED, and the branch is unreachable at the default
   `typeofMA = "SMA"` in any case.
5. MD/SOURCE MISMATCH (argument table): the md renders `v_input_5` and
   `v_input_6` as `true` for `StartMonth` / `StartDay` -- they are `input(1)`
   integers, and `true` is a boolean rendering. It also renders `v_input_2` as
   `0` with the options listed "SMA|RMA|EMA|..." while the SOURCE's option list
   is ["RMA", "SMA", "EMA", ...]. The source's explicit `defval="SMA"` is what is
   used; the md's reordered list happens to agree with that default.
6. `testPeriod() => true`, so both `if testPeriod()` blocks always execute.
   `testPeriodStart` and `testPeriodStop` (and the six year/month/day inputs that
   build them) are computed and NEVER READ -- not even by `testPeriod()`. Kept as
   ledger columns. Pine's `timestamp()` without an explicit timezone converts in
   the EXCHANGE's timezone; the port builds them in UTC, which is a modelling
   choice for dead code only.
7. `includeEngulfing = true` and `includeMA = true` are declared and never read,
   and `NoBody = close == open` likewise. Kept.
8. `long_TP_exit = buy_trend and high >= tp` and `short_TP_exit = sell_trend and
   low <= tp` are computed and never read: no order and no plot consumes them.
   Kept as ledger columns. Both compare against `tp` and NEITHER reads `sl`, so
   the source has no stop-exit variable at all; each is the take-profit test for
   its own regime (`tp` is the long target while `buy_trend`, the short target
   while `sell_trend`). Nothing reads either one.
9. `tp` / `sl` are PRICE levels built from `long_entry_price` /
   `short_entry_price` -- which are `valuewhen(nUP, close, 0)` /
   `valuewhen(nDN, close, 0)`, i.e. the close of the signal bar, NOT the fill
   price -- plus the two "in USD" inputs. They are passed to `broker.exit` as
   `limit=` / `stop=` verbatim, including when they are na (na levels rest inert
   and publish no framework level, which is what na legs do on the original
   platform too).
10. `testPeriod()` is a constant, so the two blocks collapse to unconditional
    execution; the port keeps the written order Long entry / Long close / Long
    exit, then Short entry / Short close / Short exit.
11. `strategy.entry("Long", 1, ...)` and `strategy.entry("Short", 0, ...)`:
    Pine v4's second positional argument is the `long` FLAG (true = long,
    false = short), so the literals 1 and 0 mean long and SHORT -- they are not
    quantities, and v5's `direction` enum does not exist in v4.
12. `barssince` is na until its condition first fires, and na propagates through
    `0 - barssince(a) + barssince(b)`, so `bullish_MA_cond` / `bearish_MA_cond`
    are both 0 until BOTH a crossover and a crossunder have happened; the same
    applies down the chain to `conditionUP` / `conditionDN`, `nUP` / `nDN` and
    `buy_trend` / `sell_trend`. Kept as the source has it.
13. `Engulf_Buy` / `Engulf_Sell` / `bullish_MA_cond` / `bearish_MA_cond` are
    INTEGERS (1 / 0), summed arithmetically into `posUp` / `posDn` and compared
    with `== 2` / `< 2`; they are kept as integer columns rather than rewritten
    into booleans.
14. `strategy()` declares `pyramiding=2`, `default_qty_value=500`,
    `precision=7`, `currency=currency.USD`, `commission_value=0.2` percent and
    `initial_capital=10000`, and declares NO `default_qty_type`, so Pine's
    documented default `strategy.fixed` applies. `precision` and `currency` are
    display/accounting settings the engine does not model.
15. `pyramiding=2` allows up to three stacked same-direction entries in the
    engine's ledger, while the framework is structurally limited to one entry
    (`PinePortBase.position_adjustment_enable = False`, PINE_SEMANTICS.md 二.10).
    Not fixed; recorded. 500 fixed contracts against a 10000 initial capital is
    also a notional far larger than the account, so the framework may veto
    entries that the engine funds (PINE_SEMANTICS.md 1.5): a
    `mismatch_framework_veto` verdict here is that boundary, not a port defect.
16. `plot(MA, ...)` and the two `barcolor(...)` calls are display-only.
17. The `/*backtest` header's `period: 30m` IS taken as the timeframe --
    `basePeriod: 15m` is the FMZ backtester's intrabar fill granularity, and the
    header's start:/end: window is not applied: the port runs on whatever range
    the caller supplies.
18. `ta.ema` (used by the EMA / DEMA / TEMA / KMA branches) is
    pine_ta.pine_ema, seeded with the first non-na observation -- an unpublished
    TradingView rule (PINE_SEMANTICS.md 3.1). Not reachable at the default
    `typeofMA = "SMA"`.
19. Leverage, margin, liquidation, funding and the venue's contract-step
    rounding are not modelled; the chain verifier measures the step rounding
    separately.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


def _smma(src: pd.Series, length: int) -> pd.Series:
    """`smma(src, len)`:

        smma = 0.0
        smma := na(smma[1]) ? sma(src, len) : (smma[1] * (len - 1) + src) / len

    So the recursion only starts once `sma` has produced its first value; before
    that `na(smma[1])` is true and the result is `sma` itself, na included. This
    is deliberately NOT pine_rma, which averages the first window into the same
    recursion instead of taking the SMA as its seed.
    """
    length = int(length)
    seed = ta.pine_sma(src, length).to_numpy(dtype=float)
    values = src.to_numpy(dtype=float)
    out = np.full(len(values), np.nan)
    state = np.nan
    for i, value in enumerate(values):
        if np.isnan(state):
            state = seed[i]
        else:
            state = (state * (length - 1) + value) / length
        out[i] = state
    return pd.Series(out, index=src.index, dtype=float)


def _kma(src: pd.Series, length: int) -> pd.Series:
    """The source's `"KMA"` branch, transcribed line for line.

        xPrice  = src
        xvnoise = abs(xPrice - xPrice[1])
        nsignal = abs(xPrice - xPrice[length])
        nnoise  = sum(xvnoise, length)
        nefratio = iff(nnoise != 0, nsignal / nnoise, 0)
        nsmooth  = pow(nefratio * (0.666 - 0.0645) + 0.0645, 2)
        nAMA := nz(nAMA[1]) + nsmooth * (xPrice - nz(nAMA[1]))

    `nAMA` is declared 0.0, so the recursion is seeded at zero and bar 0 is
    `nsmooth[0] * xPrice[0]`, not `xPrice[0]`. `nnoise != 0` is na (hence false)
    while `sum` is still filling its window, so `nefratio` is 0 there.
    """
    length = int(length)
    x_price = src
    xvnoise = (x_price - x_price.shift(1)).abs()
    nsignal = (x_price - x_price.shift(length)).abs().to_numpy(dtype=float)
    nnoise = ta.pine_sum(xvnoise, length).to_numpy(dtype=float)
    # iff(nnoise != 0, nsignal / nnoise, 0); na compares false in Pine, so an
    # unfilled window (na) takes the 0 branch rather than numpy's `nan != 0`.
    valid = ~np.isnan(nnoise) & (nnoise != 0)
    with np.errstate(divide="ignore", invalid="ignore"):
        nefratio = np.where(valid, nsignal / nnoise, 0.0)
    nsmooth = (nefratio * (0.666 - 0.0645) + 0.0645) ** 2
    prices = x_price.to_numpy(dtype=float)
    out = np.full(len(prices), np.nan)
    state = np.nan
    for i in range(len(prices)):
        base = 0.0 if np.isnan(state) else state
        state = base + nsmooth[i] * (prices[i] - base)
        out[i] = state
    return pd.Series(out, index=src.index, dtype=float)


def _pine_ma(smoothing: str, src: pd.Series, length: int,
             close: pd.Series) -> pd.Series:
    """`ma(smoothing, src, length)`, the source's full if/else-if chain.

    Every branch is implemented so that an override of `typeofMA` runs the
    source's own formula. `close` is passed separately because the `"TMA"`
    branch reads the bar's `close` rather than the function's `src`.
    """
    if smoothing == "RMA":
        return ta.pine_rma(src, length)
    if smoothing == "SMA":
        return ta.pine_sma(src, length)
    if smoothing == "EMA":
        return ta.pine_ema(src, length)
    if smoothing == "WMA":
        return ta.pine_wma(src, length)
    if smoothing == "VWMA":
        return ta.pine_vwma(src, length)
    if smoothing == "SMMA":
        return _smma(src, length)
    if smoothing == "HullMA":
        # wma(2 * wma(src, length / 2) - wma(src, length), round(sqrt(length)))
        inner = 2 * ta.pine_wma(src, length / 2) - ta.pine_wma(src, length)
        return ta.pine_wma(inner, ta.pine_round(np.sqrt(length)))
    if smoothing == "LSMA":
        return src
    if smoothing == "KMA":
        return _kma(src, length)
    if smoothing == "TMA":
        # The source reads `close` here, not `src`.
        return ta.pine_sma(ta.pine_sma(close, length), length)
    if smoothing == "DEMA":
        return 2 * src - ta.pine_ema(src, length)
    if smoothing == "TEMA":
        return 3 * (src - ta.pine_ema(src, length)) + ta.pine_ema(
            ta.pine_ema(src, length), length
        )
    return src


class SMBestEngulfing_0a5ae5(PinePortBase, IStrategy):
    source_id = "SM_0a5ae58e59c095ab"
    source_file = "BEST-Engulfing-Breakout-Strategy.md"
    # /*backtest ... period: 30m, basePeriod: 15m
    timeframe = "30m"
    # strategy.entry("Short", 0, when=isShort) is active code.
    can_short = True
    source_defaults = {
        # source_ma = input(title="Source Price vs MA", type=input.source, defval=close)
        "source_ma": "close",
        # typeofMA = input(title="Type of MA", defval="SMA", options=[...])
        "typeofMA": "SMA",
        # length_ma = input(32, title="MA Length", type=input.integer)
        "length_ma": 32,
        # StartYear / StartMonth / StartDay = input(2017 / 1 / 1, ...)
        "StartYear": 2017,
        "StartMonth": 1,
        "StartDay": 1,
        # StopYear / StopMonth / StopDay = input(2020 / 12 / 31, ...)
        "StopYear": 2020,
        "StopMonth": 12,
        "StopDay": 31,
        # input_tp_pips = input(2000, "Backtest Profit Goal (in USD)", minval=0)
        "input_tp_pips": 2000,
        # input_sl_pips = input(200, "Backtest STOP Goal (in USD)", minval=0)
        "input_sl_pips": 200,
    }
    # strategy(...) declares no default_qty_type -> Pine's documented default
    # strategy.fixed; default_qty_value=500 is declared.
    source_qty_type = "fixed"
    source_qty_value = 500.0
    # commission_type=strategy.commission.percent, commission_value=0.2
    source_commission_percent = 0.2
    # pyramiding=2
    source_pyramiding = 2
    # initial_capital=10000
    source_initial_capital = 10000.0
    # Both strategy.exit calls carry stop= / limit= price legs.
    source_reproduce_stops = True
    source_fidelity_notes = [
        "ma(smoothing, src, length) is a hand-written if/else-if chain over "
        "TWELVE smoothing names (RMA, SMA, EMA, WMA, VWMA, SMMA, HullMA, LSMA, "
        "KMA, TMA, DEMA, TEMA) plus a final `src` fallback. EVERY branch is "
        "implemented, including those the default typeofMA='SMA' never reaches, "
        "so a source_parameters override runs the source's own formula. All "
        "thirteen outcomes were EXECUTED against a probe series during this "
        "port's audit, not merely read -- none raises, including the VWMA branch, "
        "whose volume reaches pine_vwma through source_ma.attrs. Two branches are "
        "quirky and are reproduced as written, not corrected: TMA is "
        "sma(sma(close, length), length) -- it reads the BAR'S close, not the "
        "function's src parameter -- and DEMA / TEMA are the one- and two-term "
        "expressions the source writes, which are not the textbook DEMA / TEMA.",
        "\"LSMA\" is tested by the chain but is NOT in the input's option list, so "
        "it is unreachable from the input while remaining reachable code; the "
        "final `else -> src` is likewise unreachable from the option list. Both "
        "are kept.",
        "smma(src, len) is na(smma[1]) ? sma(src, len) : (smma[1]*(len-1)+src)/len "
        "with smma declared 0.0, so it stays na until sma produces its first value "
        "and only then recurses. It is NOT pine_rma (which averages the first "
        "window into the same recursion); written out in _smma.",
        "KMA's block is indented inconsistently in the extracted source (8 tabs "
        "plus 4 spaces for the `if`, then a run of 40 spaces for the body). It is "
        "reproduced as ONE block inside the KMA branch, the only reading under "
        "which the following else chain is well-formed. Whether the original "
        "platform parsed it that way is UNVERIFIED; the branch is unreachable at "
        "the default typeofMA='SMA' in any case.",
        "MD/SOURCE MISMATCH (argument table): the md renders v_input_5 and "
        "v_input_6 as `true` for StartMonth / StartDay, which are input(1) "
        "integers -- `true` is a boolean rendering. It renders v_input_2 as 0 with "
        "the options listed 'SMA|RMA|EMA|...' while the SOURCE's option list is "
        "['RMA', 'SMA', 'EMA', ...]; the source's explicit defval='SMA' is what is "
        "used, and the md's reordered list agrees with that default.",
        "testPeriod() => true, so both `if testPeriod()` blocks always execute. "
        "testPeriodStart and testPeriodStop -- and the six year/month/day inputs "
        "that build them -- are computed and NEVER READ, not even by testPeriod(). "
        "Kept as ledger columns: 1483228800000 and 1609372800000 at the defaults "
        "(measured). Pine's timestamp() without an explicit timezone converts in "
        "the EXCHANGE's timezone, so the port pins tz='UTC' explicitly instead of "
        "leaving pandas to read a naive Timestamp as local time. A modelling "
        "choice that affects dead code only.",
        "includeEngulfing = true, includeMA = true and NoBody = close == open are "
        "declared and never read. Kept.",
        "long_TP_exit = buy_trend and high >= tp and short_TP_exit = sell_trend "
        "and low <= tp are computed and never read -- no order and no plot "
        "consumes them. Kept as ledger columns. Both compare against tp and "
        "NEITHER reads sl, so the source declares no stop-exit variable at all; "
        "each is the take-profit test for its own regime (tp is the long target "
        "while buy_trend, the short target while sell_trend). Nothing reads either "
        "one.",
        "LEDGER COMPLETENESS: every name the source computes has a pine_* column, "
        "including the ones no later expression reads -- the four 1/2 engulfing "
        "sub-conditions, Engulf_curr, since_ma_buy / since_ma_sell, macross_curr, "
        "sinceUP / sinceDN, sinceNUP / sinceNDN, testPeriodStart / testPeriodStop, "
        "includeEngulfing, includeMA and NoBody. The intermediates all feed the "
        "chain below them, so dropping them would change no order, but the source "
        "computes them and the ledger has to let an auditor see that the port does "
        "too.",
        "tp / sl are PRICE levels built from long_entry_price / short_entry_price, "
        "which are valuewhen(nUP, close, 0) / valuewhen(nDN, close, 0) -- the "
        "CLOSE OF THE SIGNAL BAR, not the fill price -- plus the two 'in USD' "
        "inputs. They are passed to broker.exit as limit= / stop= verbatim, "
        "including when na. MEASURED on the engine: a NaN leg is never a fill "
        "(nan comparisons are False), and NaN stop / limit are filtered out of "
        "pine_stop_level / pine_limit_level, so an na leg rests inert and "
        "publishes no framework level. Whether the original platform likewise "
        "reads an na numeric argument as 'this leg was not supplied' is "
        "UNPUBLISHED and was not consulted; the engine's model is the one this "
        "port relies on, and it is the only defensible one -- the alternative "
        "reading (na = a leg at price na) has no coherent fill rule.",
        "strategy.entry('Long', 1, when=isLong) and strategy.entry('Short', 0, "
        "when=isShort): Pine v4's second positional argument is the `long` FLAG "
        "(true = long, false = short), so the literals 1 and 0 mean long and "
        "SHORT. They are not quantities, and v5's direction enum does not exist "
        "in v4. MEASURED, not recalled: this corpus is FMZ-converted and writes "
        "the flag as a bare literal. Across source_migration/sources, when the "
        "flag is written NUMERICALLY -- the same form this file uses -- the id "
        "'Short'/'short'/'SHORT' is paired with 0 in 57 calls and with 1 in 3, "
        "and 'Long'/'long'/'LONG' is paired with 1 in 69 calls and with 0 in 1. "
        "The bare-boolean form is consistent with that (298 `false`, 355 `true`, "
        "short-named ids dominating the `false` group). The reading is "
        "corroborated inside THIS file: tp / sl use `short_entry_price - "
        "input_tp_pips` and `short_entry_price + input_sl_pips`, signs that are "
        "only coherent if 'Short' is a short position, and longClose / shortClose "
        "close the two sides against opposite sides of MA.",
        "barssince is na until its condition first fires, and na propagates "
        "through 0 - barssince(a) + barssince(b), so bullish_MA_cond / "
        "bearish_MA_cond are both 0 until BOTH a crossover and a crossunder have "
        "happened; the same applies down the chain to conditionUP / conditionDN, "
        "nUP / nDN and buy_trend / sell_trend. Kept as the source has it.",
        "Engulf_Buy / Engulf_Sell / bullish_MA_cond / bearish_MA_cond are INTEGERS "
        "(1 / 0), summed arithmetically into posUp / posDn and compared with == 2 "
        "/ < 2; they are kept as integer columns rather than rewritten into "
        "booleans.",
        "strategy() declares pyramiding=2, default_qty_value=500, precision=7, "
        "currency=currency.USD, commission_value=0.2 percent and "
        "initial_capital=10000, and declares NO default_qty_type, so Pine's "
        "documented default strategy.fixed applies. precision and currency are "
        "display/accounting settings the engine does not model.",
        "pyramiding=2 allows up to three stacked same-direction entries in the "
        "engine's ledger, while the framework is structurally limited to one "
        "entry (position_adjustment_enable = False, PINE_SEMANTICS.md 二.10). Not "
        "fixed; recorded. 500 fixed contracts against a 10000 initial capital is "
        "also a notional far larger than the account, so the framework may veto "
        "entries the engine funds (PINE_SEMANTICS.md 1.5): a "
        "mismatch_framework_veto verdict here is that boundary, not a port defect.",
        "The six order calls are reproduced in the source's written order (Long "
        "entry, Long close, Long exit, Short entry, Short close, Short exit), "
        "which is the engine's fill priority on a bar where more than one fires.",
        "plot(MA, ...) and the two barcolor(...) calls are display-only and are "
        "not reproduced.",
        "period: 30m IS taken from the /*backtest header. basePeriod: 15m is the "
        "FMZ backtester's own intrabar fill granularity, and the header's "
        "start:/end: window is not applied: the port runs on whatever range the "
        "caller supplies.",
        "ta.ema (used by the EMA / DEMA / TEMA / KMA branches) is "
        "pine_ta.pine_ema, seeded with the first non-na observation -- an "
        "unpublished TradingView rule (PINE_SEMANTICS.md 3.1). Not reachable at "
        "the default typeofMA='SMA'.",
        "Leverage, margin, liquidation, funding and the venue's contract-step "
        "rounding are not modelled; the chain verifier measures the step rounding "
        "separately.",
    ]

    def pine_indicators(self, dataframe, params):
        close = dataframe["close"]
        open_ = dataframe["open"]
        high = dataframe["high"]
        low = dataframe["low"]

        # includeEngulfing = true ; includeMA = true  (declared, never read)
        include_engulfing = True
        include_ma = True

        # ---- candle components ---------------------------------------------
        green_candle = close > open_
        red_candle = close < open_
        # NoBody = close == open  (declared, never read)
        no_body = close == open_
        body = (close - open_).abs()

        # ---- engulfing ------------------------------------------------------
        # Pine's max(close[1], open[1]) is na when EITHER input is na, so these
        # use np.maximum / np.minimum (nan-propagating) rather than pandas'
        # skipna-aware max(axis=1).
        previous_high_body = np.maximum(close.shift(1), open_.shift(1))
        previous_low_body = np.minimum(close.shift(1), open_.shift(1))
        current_high_body = np.maximum(close, open_)
        current_low_body = np.minimum(close, open_)
        previous_green = green_candle.shift(1, fill_value=False)
        previous_red = red_candle.shift(1, fill_value=False)

        is_bullish_engulfing1 = (
            (previous_high_body < current_high_body)
            & (previous_low_body > current_low_body)
            & (body > body.shift(1))
            & green_candle
            & previous_red
        )
        is_bullish_engulfing2 = (
            (previous_high_body < current_high_body)
            & (previous_low_body <= current_low_body)
            & (body > body.shift(1))
            & green_candle
            & previous_red
        )
        is_bearish_engulfing1 = (
            (previous_high_body < current_high_body)
            & (previous_low_body > current_low_body)
            & (body > body.shift(1))
            & red_candle
            & previous_green
        )
        is_bearish_engulfing2 = (
            (previous_high_body >= current_high_body)
            & (previous_low_body > current_low_body)
            & (body > body.shift(1))
            & red_candle
            & previous_green
        )
        is_bullish_engulfing = is_bullish_engulfing1 | is_bullish_engulfing2
        is_bearish_engulfing = is_bearish_engulfing1 | is_bearish_engulfing2

        # Engulf_curr = 0 - barssince(isBearishEngulfing) + barssince(isBullishEngulfing)
        engulf_curr = (
            -ta.pine_barssince(is_bearish_engulfing)
            + ta.pine_barssince(is_bullish_engulfing)
        )
        # Engulf_Buy = Engulf_curr < 0 ? 1 : 0 ; Engulf_Sell = Engulf_curr > 0 ? 1 : 0
        engulf_buy = np.where((engulf_curr < 0).to_numpy(dtype=bool), 1, 0)
        engulf_sell = np.where((engulf_curr > 0).to_numpy(dtype=bool), 1, 0)

        # ---- price versus MA -------------------------------------------------
        # source_ma = input.source (default close); MA = ma(typeofMA, source_ma, length_ma)
        source_name = str(params["source_ma"])
        source_ma = ta.pine_source(dataframe, source_name).copy()
        # pine_vwma reads the chart's volume off the source's attrs, as Pine's
        # vwma() uses the bar's own volume.
        source_ma.attrs["volume"] = dataframe["volume"]
        length_ma = int(params["length_ma"])
        ma = _pine_ma(str(params["typeofMA"]), source_ma, length_ma, close)

        macrossover = ta.pine_crossover(source_ma, ma)
        macrossunder = ta.pine_crossunder(source_ma, ma)
        # since_ma_buy = barssince(macrossover) ; since_ma_sell = barssince(macrossunder)
        since_ma_buy = ta.pine_barssince(macrossover)
        since_ma_sell = ta.pine_barssince(macrossunder)
        # macross_curr = 0 - since_ma_sell + since_ma_buy
        macross_curr = -since_ma_sell + since_ma_buy
        # bullish_MA_cond = macross_curr < 0 ? 1 : 0 (na compares false -> 0)
        bullish_ma_cond = np.where((macross_curr < 0).to_numpy(dtype=bool), 1, 0)
        bearish_ma_cond = np.where((macross_curr > 0).to_numpy(dtype=bool), 1, 0)

        # posUp = (Engulf_Buy ? 1 : 0) + (bullish_MA_cond ? 1 : 0)
        pos_up = np.where(engulf_buy != 0, 1, 0) + np.where(bullish_ma_cond != 0, 1, 0)
        pos_dn = np.where(engulf_sell != 0, 1, 0) + np.where(bearish_ma_cond != 0, 1, 0)
        pos_up_series = pd.Series(pos_up, index=close.index)
        pos_dn_series = pd.Series(pos_dn, index=close.index)

        # conditionUP = posUp == 2 and posUp[1] < 2
        condition_up = (pos_up_series == 2) & (pos_up_series.shift(1) < 2)
        condition_dn = (pos_dn_series == 2) & (pos_dn_series.shift(1) < 2)

        # sinceUP = barssince(conditionUP) ; sinceDN = barssince(conditionDN)
        since_up = ta.pine_barssince(condition_up)
        since_dn = ta.pine_barssince(condition_dn)
        # nUP = crossunder(sinceUP, sinceDN) ; nDN = crossover(sinceUP, sinceDN)
        n_up = ta.pine_crossunder(since_up, since_dn)
        n_dn = ta.pine_crossover(since_up, since_dn)

        # buy_trend = sinceNDN > sinceNUP ; sell_trend = sinceNDN < sinceNUP
        since_nup = ta.pine_barssince(n_up)
        since_ndn = ta.pine_barssince(n_dn)
        buy_trend = (since_ndn > since_nup).fillna(False)
        sell_trend = (since_ndn < since_nup).fillna(False)

        # isLong = nUP ; isShort = nDN
        is_long = n_up
        is_short = n_dn
        # long_entry_price = valuewhen(nUP, close, 0) ; short_entry_price = valuewhen(nDN, close, 0)
        long_entry_price = ta.pine_valuewhen(n_up, close, 0)
        short_entry_price = ta.pine_valuewhen(n_dn, close, 0)
        # longClose = close[1] < MA ; shortClose = close[1] > MA
        long_close = close.shift(1) < ma
        short_close = close.shift(1) > ma

        # ---- tp / sl ---------------------------------------------------------
        tp_pips = float(params["input_tp_pips"])
        sl_pips = float(params["input_sl_pips"])
        buy_trend_values = buy_trend.to_numpy(dtype=bool)
        # tp = buy_trend ? long_entry_price + input_tp_pips : short_entry_price - input_tp_pips
        tp = np.where(
            buy_trend_values,
            (long_entry_price + tp_pips).to_numpy(dtype=float),
            (short_entry_price - tp_pips).to_numpy(dtype=float),
        )
        # sl = buy_trend ? long_entry_price - input_sl_pips : short_entry_price + input_sl_pips
        sl = np.where(
            buy_trend_values,
            (long_entry_price - sl_pips).to_numpy(dtype=float),
            (short_entry_price + sl_pips).to_numpy(dtype=float),
        )

        # long_TP_exit = buy_trend and high >= tp  (computed, never read)
        long_tp_exit = buy_trend & (high >= pd.Series(tp, index=close.index))
        # short_TP_exit = sell_trend and low <= tp  (computed, never read)
        short_tp_exit = sell_trend & (low <= pd.Series(tp, index=close.index))

        # ---- backtest period selector (computed, never read) -----------------
        # testPeriodStart = timestamp(StartYear, StartMonth, StartDay, 0, 0)
        # Pine's timestamp() without a timezone argument resolves in the
        # EXCHANGE's timezone (UTC on Binance), and `time` is ms since epoch in
        # UTC, so the conversion is pinned to UTC here rather than left to
        # pandas' local-time default for a naive Timestamp.
        test_period_start = int(
            pd.Timestamp(
                int(params["StartYear"]), int(params["StartMonth"]),
                int(params["StartDay"]), tz="UTC",
            ).timestamp()
            * 1000
        )
        # testPeriodStop = timestamp(StopYear, StopMonth, StopDay, 0, 0)
        test_period_stop = int(
            pd.Timestamp(
                int(params["StopYear"]), int(params["StopMonth"]),
                int(params["StopDay"]), tz="UTC",
            ).timestamp()
            * 1000
        )

        dataframe["pine_include_engulfing"] = include_engulfing
        dataframe["pine_include_ma"] = include_ma
        dataframe["pine_green_candle"] = green_candle
        dataframe["pine_red_candle"] = red_candle
        dataframe["pine_no_body"] = no_body
        dataframe["pine_body"] = body
        dataframe["pine_is_bullish_engulfing1"] = is_bullish_engulfing1
        dataframe["pine_is_bullish_engulfing2"] = is_bullish_engulfing2
        dataframe["pine_is_bearish_engulfing1"] = is_bearish_engulfing1
        dataframe["pine_is_bearish_engulfing2"] = is_bearish_engulfing2
        dataframe["pine_is_bullish_engulfing"] = is_bullish_engulfing
        dataframe["pine_is_bearish_engulfing"] = is_bearish_engulfing
        dataframe["pine_engulf_curr"] = engulf_curr
        dataframe["pine_engulf_buy"] = engulf_buy
        dataframe["pine_engulf_sell"] = engulf_sell
        dataframe["pine_ma"] = ma
        dataframe["pine_macrossover"] = macrossover
        dataframe["pine_macrossunder"] = macrossunder
        dataframe["pine_since_ma_buy"] = since_ma_buy
        dataframe["pine_since_ma_sell"] = since_ma_sell
        dataframe["pine_macross_curr"] = macross_curr
        dataframe["pine_bullish_ma_cond"] = bullish_ma_cond
        dataframe["pine_bearish_ma_cond"] = bearish_ma_cond
        dataframe["pine_pos_up"] = pos_up
        dataframe["pine_pos_dn"] = pos_dn
        dataframe["pine_condition_up"] = condition_up
        dataframe["pine_condition_dn"] = condition_dn
        dataframe["pine_since_up"] = since_up
        dataframe["pine_since_dn"] = since_dn
        dataframe["pine_n_up"] = n_up
        dataframe["pine_n_dn"] = n_dn
        dataframe["pine_since_nup"] = since_nup
        dataframe["pine_since_ndn"] = since_ndn
        dataframe["pine_buy_trend"] = buy_trend
        dataframe["pine_sell_trend"] = sell_trend
        dataframe["pine_long_entry_price"] = long_entry_price
        dataframe["pine_short_entry_price"] = short_entry_price
        dataframe["pine_long_close"] = long_close
        dataframe["pine_short_close"] = short_close
        dataframe["pine_tp"] = tp
        dataframe["pine_sl"] = sl
        dataframe["pine_long_tp_exit"] = long_tp_exit
        dataframe["pine_short_tp_exit"] = short_tp_exit
        dataframe["pine_test_period_start"] = test_period_start
        dataframe["pine_test_period_stop"] = test_period_stop
        return dataframe

    def pine_context(self, dataframe, params):
        del params
        return {
            "is_long": dataframe["pine_n_up"].to_numpy(dtype=bool),
            "is_short": dataframe["pine_n_dn"].to_numpy(dtype=bool),
            "long_close": dataframe["pine_long_close"].to_numpy(dtype=bool),
            "short_close": dataframe["pine_short_close"].to_numpy(dtype=bool),
            "buy_trend": dataframe["pine_buy_trend"].to_numpy(dtype=bool),
            "sell_trend": dataframe["pine_sell_trend"].to_numpy(dtype=bool),
            "tp": dataframe["pine_tp"].to_numpy(dtype=float),
            "sl": dataframe["pine_sl"].to_numpy(dtype=float),
        }

    def pine_script(self, broker, i, ctx):
        # testPeriod() => true, so both blocks below always execute. The written
        # order is the fill priority and is preserved: Long entry, Long close,
        # Long exit, then Short entry, Short close, Short exit.
        #
        # if testPeriod()
        #     strategy.entry("Long", 1, when=isLong)     -- 1 == strategy.long
        broker.entry("Long", "long", when=bool(ctx["is_long"][i]))
        #     strategy.close("Long", when=longClose)
        broker.close("Long", when=bool(ctx["long_close"][i]))
        #     strategy.exit("XL","Long", limit=tp, when=buy_trend, stop=sl)
        broker.exit(
            "XL",
            from_entry="Long",
            limit=float(ctx["tp"][i]),
            when=bool(ctx["buy_trend"][i]),
            stop=float(ctx["sl"][i]),
        )
        #
        # if testPeriod()
        #     strategy.entry("Short", 0, when=isShort)   -- 0 == strategy.short
        broker.entry("Short", "short", when=bool(ctx["is_short"][i]))
        #     strategy.close("Short", when=shortClose)
        broker.close("Short", when=bool(ctx["short_close"][i]))
        #     strategy.exit("XS","Short", when=sell_trend, limit=tp, stop=sl)
        broker.exit(
            "XS",
            from_entry="Short",
            when=bool(ctx["sell_trend"][i]),
            limit=float(ctx["tp"][i]),
            stop=float(ctx["sl"][i]),
        )
