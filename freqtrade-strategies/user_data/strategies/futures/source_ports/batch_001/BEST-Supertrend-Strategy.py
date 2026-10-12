"""Port of sources/SM_089cda094755be19.pine
(batch_001/BEST-Supertrend-Strategy.md).

Pine v4, 2-hour chart, long AND short, by Daveatt / "BEST Supertrend Strategy".
A higher-timeframe SuperTrend filter combined with an SMA cross regime:

    f_supertrend(Factor, Pd) =>
        Up = hl2 - Factor*atr(Pd) ; Dn = hl2 + Factor*atr(Pd)
        TrendUp   := close[1] > TrendUp[1]   ? max(Up, TrendUp[1])   : Up
        TrendDown := close[1] < TrendDown[1] ? min(Dn, TrendDown[1]) : Dn
        Trend     := close > TrendDown[1] ? 1 : close < TrendUp[1] ? -1 : nz(Trend[1], 1)
        Tsl        = Trend == 1 ? TrendUp : TrendDown

    st_tsl = f_supertrend(Factor, Pd)                      # on the CHART bars
    [st_daily, ...] = f_securitys(syminfo.tickerid, st_tsl)
        # each = security(tickerid, <res>, st_tsl[1], lookahead=true)

    sma_fast = sma(close, fastLength)
    sma_slow = sma(close, slowLength)
    long_exit  = crossunder(sma_fast, sma_slow)
    short_exit = crossover(sma_fast, sma_slow)

    curr = 0 - barssince(long_exit) + barssince(short_exit)
    cross_buy  = curr < 0 ?  1 : 0
    cross_sell = curr > 0 ?  1 : 0

    bull = close >= st_tsl_TF and cross_buy
    bear = close <= st_tsl_TF and cross_sell

    if isLong
        strategy.entry("Long", 1, when=bull)
        strategy.close("Long", when=long_exit)
    if isShort
        strategy.entry("Short", 0, when=bear)
        strategy.close("Short", when=short_exit)

FOUR ORDERS, in that exact written order, and the order is preserved here because
it is the engine's fill priority on a bar where more than one fires. `"Long"` is
a long entry and `"Short"` is a short entry: in Pine v4 the second positional
argument of `strategy.entry` is the `long` FLAG (true = long, false = short), so
the literal `1` means long and the literal `0` means SHORT -- it is not a
quantity, and v5's `direction` enum does not exist in v4. Both entry ids use the
default quantity, and both exits are `strategy.close`, i.e. market orders.

THIS SOURCE IS NOT A CONVERTER-APPENDED ORDER BLOCK, and the two claims its
tier_reason makes are both false, so they are recorded here rather than followed:

* "declares indicator()/study()" -- the file declares NOTHING active. Its only
  strategy declaration (line 13, `// strategy(title="BEST Supertrend Strategy",
  ..., pyramiding=0, default_qty_value=100, precision=7, currency=currency.USD,
  commission_value=0.2, ... initial_capital=1000000)`) has been commented out by
  the extraction/conversion step, and there is no `indicator()` or `study()` call
  anywhere.
* "NO exits" -- there ARE exits, and they are active code, not comments:
  `strategy.close("Long", when=long_exit)` and
  `strategy.close("Short", when=short_exit)`.

The order block at the end of the file is the author's own, uncommented Pine v4
strategy code. What the commented-out declaration removes is the SIZING and the
commission, so those fall back to Pine's documented defaults -- `strategy.fixed`
of 1 contract, initial capital 1000000, commission 0%, `pyramiding = 0`,
`process_orders_on_close = false` -- exactly as a commented-out exit would not
place an exit (PINE_SEMANTICS.md 1.17). The commented values are recorded in
source_fidelity_notes; the author's `pyramiding=0` happens to agree with the
default anyway.

FIDELITY -- translation choices and source/md mismatches:

1. `security()` IS REPRODUCED, not dropped. PINE_SEMANTICS.md section 二.1 says a
   port that depends on `request.security` must either annotate it or supply the
   aligned series itself, and the second option is available here because every
   requested resolution is a whole multiple of the chart's, so the higher-
   timeframe bars can be rebuilt EXACTLY from the 2h bars (open = first 2h open,
   high = max, low = min, close = last 2h close). The five `security()` calls run
   the SuperTrend on those rebuilt bars -- see (2) -- and `st_tsl[1]` with
   `lookahead=true` is the previous COMPLETED higher-timeframe bar's value,
   delivered to every 2h bar of the current one.
2. `security()` evaluates its expression in a separate instance of the script
   running on the requested timeframe, so `st_tsl` inside it means the SuperTrend
   computed from the HIGHER timeframe's own OHLC -- not the 2h `st_tsl` sampled at
   a daily close. The port follows that reading, which is also what makes the
   source's own info panel meaningful (five different numbers for the five
   timeframes) and what the `Supertrend timeframe` input is for. If the original
   platform instead sampled the chart-timeframe series, the port would differ;
   that cannot be settled offline, so it is recorded as a risk.
3. `lookahead=true` is `barmerge.lookahead_on`, which PINE_SEMANTICS.md section 四
   lists as a future-data pattern not to be "fixed". Combined with the `[1]`
   offset it is the standard NON-repainting higher-timeframe idiom: the value it
   yields is the previous completed higher-timeframe bar's, so the port is causal
   and the prefix check confirms it. Flagged, not altered.
4. The `TF` input's option list spells the quarter as "quartly" while
   `IS_QUARTERLY` tests for "quarterly". The two can never be equal, so the
   QUARTERLY BRANCH IS UNREACHABLE and selecting that option falls through the
   `iff` chain to its final else, `st_daily`. Reproduced exactly: the option is
   kept spelled "quartly", the quarterly series is still computed (the source
   computes it), and it is unreachable.
5. MD/SOURCE MISMATCH (exit): the md says a long is exited "when the price breaks
   below the Supertrend line" and a short "when the price breaks above" it. The
   source exits on `crossunder(sma_fast, sma_slow)` / `crossover(sma_fast,
   sma_slow)` -- a fast/slow SMA cross, with no SuperTrend comparison in either
   exit. The source is followed.
6. MD/SOURCE MISMATCH (entry): the md says the entry is "when the price breaks
   above the Supertrend line". The source also requires `cross_buy` -- the SMA
   pair's most recent cross must have been a bullish one -- so the price test
   alone is not sufficient. The source is followed.
7. MD/SOURCE MISMATCH (risk): the md claims the strategy "uses stop losses to
   limit losses" and advises "use stop losses". There is no stop, no
   `strategy.exit` and no `trail` anywhere in the file; the only exits are the two
   market closes. Nothing in the port invents one.
8. MD/SOURCE MISMATCH (Argument table): it renders `v_input_1 = 0` and
   `v_input_6 = 0` for the two string-option inputs (0 being the index of
   "Longs+Shorts" and of "daily") and lists `v_input_4 = 3` for `[ST] Factor`.
   The `/*backtest` header beside it carries `args: [["v_input_4", 2]]`, i.e. the
   recorded FMZ backtest ran Factor = 2. The port keeps the Pine/md default of 3
   and does NOT adopt backtest-run state, the same way it does not adopt the
   header's `start:`/`end:` window; flipping `source_defaults["Factor"]` to 2.0
   is the whole change if the other reading is wanted. `period: 2h` IS taken from
   the header -- it is the only statement of the timeframe anywhere in the pair,
   and a port has to declare one.
9. `curr` uses `barssince`, which is na until its condition has fired at least
   once, and na propagates into `curr`, so BOTH `cross_buy` and `cross_sell` are
   0 until BOTH an SMA crossover and an SMA crossunder have happened at least
   once -- no entry of either side is possible before then. Kept.
10. `cross_buy` / `cross_sell` are INTEGERS (1 / 0) consumed by Pine's `and`.
   Pine's `and` coerces its operands to bool, so 0 is false and 1 is true; the
   port keeps the integer column verbatim and applies that coercion at the `and`
   (`astype(bool)`), rather than rewriting the source into `== 1`.
11. `Trend` is an int (1 / -1) and `Trend == 1` selects the band; the na case at
   the first bar is `nz(Trend[1], 1)` = 1, reproduced.
12. `entry_price = valuewhen(bull or bear, close, 0)` is computed by the source
   and read by nothing -- not by any order, not even by a plot. Kept as a ledger
   column so the dead code stays visible.
13. `atr(Pd)` is `rma(tr, Pd)`; pine_ta.pine_atr seeds the RMA one bar earlier
   than Pine's `ta.tr` default would (PINE_SEMANTICS.md 3.7), a difference that
   decays but is not zero. Recorded, not corrected -- it is a shared-layer
   boundary.
14. The md's prose ("higher factor and period" than the standard SuperTrend) is
   not treated as a specification; the numbers come from the declarations.
15. plot / plotshape / label / `f_draw_infopanel` are display-only and are not
   reproduced.
16. Leverage, margin, liquidation, funding and the venue's contract-step rounding
   are not modelled; the chain verifier measures the step rounding separately.
"""
import numpy as np
import pandas as pd

from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase

# Pine's `security()` resolution strings, mapped onto pandas period codes.
# "quartly" is the source's own spelling of the option value, and it is the one
# `IS_QUARTERLY` can never match.
_TF_PERIODS = {
    "daily": "D",
    "weekly": "W",
    "monthly": "M",
    "quartly": "Q",
    "yearly": "Y",
}


def _pine_max2(a: float, b: float) -> float:
    """Pine `math.max`; na wins, as it does in Pine."""
    if np.isnan(a) or np.isnan(b):
        return np.nan
    return a if a >= b else b


def _pine_min2(a: float, b: float) -> float:
    """Pine `math.min`; na wins, as it does in Pine."""
    if np.isnan(a) or np.isnan(b):
        return np.nan
    return a if a <= b else b


def _supertrend(frame: pd.DataFrame, factor: float, length: int):
    """Pine `f_supertrend(Factor, Pd)` -- returns (Tsl, Trend) as Series.

    The four assignments are Pine's recursive `:=` pattern, evaluated bar by bar.
    `TrendUp[1]` / `TrendDown[1]` / `Trend[1]` are na on the first bar, which
    makes both comparisons false and sends `Trend` through `nz(Trend[1], 1)`.
    """
    factor = float(factor)
    length = int(length)
    high = frame["high"].to_numpy(dtype=float)
    low = frame["low"].to_numpy(dtype=float)
    close = frame["close"].to_numpy(dtype=float)
    hl2 = (high + low) / 2.0
    atr = ta.pine_atr(frame, length).to_numpy(dtype=float)
    up = hl2 - factor * atr
    dn = hl2 + factor * atr

    size = len(frame)
    trend_up = np.full(size, np.nan)
    trend_down = np.full(size, np.nan)
    trend = np.full(size, np.nan)
    tsl = np.full(size, np.nan)
    prev_up = np.nan
    prev_down = np.nan
    prev_trend = np.nan
    prev_close = np.nan
    for i in range(size):
        # TrendUp := close[1] > TrendUp[1] ? max(Up, TrendUp[1]) : Up
        if prev_close > prev_up:
            trend_up[i] = _pine_max2(up[i], prev_up)
        else:
            trend_up[i] = up[i]
        # TrendDown := close[1] < TrendDown[1] ? min(Dn, TrendDown[1]) : Dn
        if prev_close < prev_down:
            trend_down[i] = _pine_min2(dn[i], prev_down)
        else:
            trend_down[i] = dn[i]
        # Trend := close > TrendDown[1] ? 1 : close < TrendUp[1] ? -1 : nz(Trend[1], 1)
        if close[i] > prev_down:
            trend[i] = 1.0
        elif close[i] < prev_up:
            trend[i] = -1.0
        else:
            trend[i] = 1.0 if np.isnan(prev_trend) else prev_trend
        # Tsl = Trend == 1 ? TrendUp : TrendDown
        tsl[i] = trend_up[i] if trend[i] == 1.0 else trend_down[i]
        prev_up = trend_up[i]
        prev_down = trend_down[i]
        prev_trend = trend[i]
        prev_close = close[i]
    return (
        pd.Series(tsl, index=frame.index, dtype=float),
        pd.Series(trend, index=frame.index, dtype=float),
    )


def _period_key(index: pd.DatetimeIndex, code: str) -> pd.PeriodIndex:
    """The higher-timeframe bar each chart bar belongs to.

    Built from `to_period` on the UTC wall clock, in the exchange's own calendar
    (PINE_SEMANTICS.md 3.4 assumes UTC): 'D' is the UTC day, 'W' the Monday-
    Sunday ISO week, 'M' the calendar month, 'Q' the calendar quarter and 'Y'
    the calendar year -- which is what Pine's 'D', 'W', 'M', '3M' and '12M' name.
    """
    utc = index.tz_convert("UTC") if index.tz is not None else index
    return utc.tz_localize(None).to_period(code)


def _htf_supertrend(frame: pd.DataFrame, factor: float, length: int, code: str):
    """`security(tickerid, <resolution>, st_tsl[1], lookahead=true)`.

    `security()` runs its expression in a separate instance of the script on the
    requested timeframe, so `st_tsl` here is the SuperTrend of the HIGHER
    timeframe's own bars, rebuilt from the chart bars. `[1]` takes the previous
    completed higher-timeframe bar and `lookahead=true` hands it to every chart
    bar of the current one, so the result is the last COMPLETED period's Tsl.
    """
    keys = _period_key(frame.index, code)
    grouped = frame.groupby(keys)
    higher = pd.DataFrame(
        {
            "open": grouped["open"].first(),
            "high": grouped["high"].max(),
            "low": grouped["low"].min(),
            "close": grouped["close"].last(),
        }
    )
    tsl, _trend = _supertrend(higher, factor, length)
    # `[1]` on the higher timeframe: the previous period's value, na for the
    # first period because there is no previous higher-timeframe bar yet.
    prior = tsl.shift(1)
    values = prior.to_numpy(dtype=float)[prior.index.get_indexer(keys)]
    return pd.Series(values, index=frame.index, dtype=float)


class SMBestSupertrend_089cda(PinePortBase, IStrategy):
    source_id = "SM_089cda094755be19"
    source_file = "BEST-Supertrend-Strategy.md"
    timeframe = "2h"
    # `if isShort` wraps `strategy.entry("Short", 0, when=bear)`: the literal 0
    # is Pine v4's `long` FLAG set false, i.e. a short entry -- not a quantity.
    can_short = True
    source_defaults: dict = {
        # input("Longs+Shorts", options=["Longs+Shorts","LongsOnly","ShortsOnly"])
        "orderType": "Longs+Shorts",
        # input(7, title="Fast Length SMA")
        "fastLength": 7,
        # input(20, title="Slow Length SMA")
        "slowLength": 20,
        # input(3, title="[ST] Factor", minval=1, maxval=100, type=input.float)
        # The /*backtest header's `args: [["v_input_4", 2]]` overrode this to 2
        # for the recorded FMZ run; the Pine/md default 3 is kept (see notes).
        "Factor": 3.0,
        # input(3, title="[ST] PD", minval=1, maxval=100)
        "Pd": 3,
        # input("daily", options=["daily","weekly","monthly","quartly","yearly"])
        "TF": "daily",
    }
    # The only strategy() declaration is commented out (line 13), so Pine's
    # documented defaults apply: fixed / 1 contract, commission 0%, pyramiding 0,
    # initial capital 1000000, process_orders_on_close false. The commented line
    # asks for pyramiding=0 (same), default_qty_value=100, precision=7,
    # currency=USD, commission 0.2% and initial_capital=1000000.
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    # Both exits are `strategy.close`, i.e. market orders; there is no
    # stop / limit / trail leg anywhere in the file.
    source_reproduce_stops = False
    source_fidelity_notes = [
        "NOT a converter-appended order block. The file's tier_reason says it "
        "declares indicator()/study() and has NO exits; both claims are false. "
        "It declares nothing active (its only strategy() line is COMMENTED OUT) "
        "and its two `strategy.close` calls are active code. The order block is "
        "the author's own Pine v4 strategy.",
        "RECORDED BUT NOT APPLIED (commented out): strategy(title=..., "
        "pyramiding=0, default_qty_value=100, precision=7, currency=USD, "
        "commission_value=0.2, commission_type=percent, initial_capital=1000000). "
        "Being a comment it declares nothing, so Pine's documented defaults are "
        "in force: fixed / 1 contract, 0% commission, pyramiding 0, initial "
        "capital 1000000. Its pyramiding=0 agrees with the default anyway; its "
        "default_qty_value=100 and 0.2% commission do not, and are not applied.",
        "security() IS supplied, not dropped (PINE_SEMANTICS.md section 二.1 "
        "allows a port to hand over the aligned series). Every requested "
        "resolution is a whole multiple of the 2h chart, so the higher-timeframe "
        "bars are rebuilt exactly from the chart bars: open = first 2h open, "
        "high = max, low = min, close = last 2h close. The five calls are "
        "reproduced as five independent series, as the source's f_securitys "
        "does.",
        "security() runs its expression in a separate instance of the script on "
        "the requested timeframe, so st_tsl there is the SuperTrend of the "
        "HIGHER timeframe's OHLC, not the 2h series sampled at a daily close. "
        "That reading is what makes the source's info panel (five different "
        "numbers) and its `Supertrend timeframe` input mean anything. If the "
        "original platform sampled the chart series instead, the port's "
        "st_tsl_TF would differ; not settleable offline, so recorded as a risk.",
        "`lookahead=true` is barmerge.lookahead_on, which PINE_SEMANTICS.md "
        "section 四 lists as a future-data pattern to flag rather than fix. With "
        "the [1] offset it is the non-repainting higher-timeframe idiom -- the "
        "value is the previous COMPLETED higher-timeframe bar's -- so the port "
        "stays causal. Flagged, not altered.",
        "TF's option list spells the quarter \"quartly\" while IS_QUARTERLY "
        "tests for \"quarterly\", so the QUARTERLY BRANCH IS UNREACHABLE and "
        "choosing that option falls through the iff chain to its final else, "
        "st_daily. Reproduced exactly: st_quarterly is still computed (the "
        "source computes it) and is still unreachable.",
        "MD/SOURCE MISMATCH (exits): the md says a long exits when price breaks "
        "below the SuperTrend line and a short when it breaks above. The source "
        "exits on crossunder(sma_fast, sma_slow) / crossover(sma_fast, sma_slow) "
        "-- an SMA cross, with no SuperTrend test in either exit. Source "
        "followed.",
        "MD/SOURCE MISMATCH (entry): the md says the entry is a break of the "
        "SuperTrend line. The source also requires cross_buy / cross_sell, the "
        "SMA pair's most recent cross being the matching one, so the price test "
        "alone never triggers an entry. Source followed.",
        "MD/SOURCE MISMATCH (risk): the md claims the strategy 'uses stop "
        "losses to limit losses' and advises using them. The file has no stop, "
        "no strategy.exit and no trail; both exits are market strategy.close "
        "calls. Nothing is invented to match the prose.",
        "MD/SOURCE MISMATCH (arguments): the md's table renders v_input_1 and "
        "v_input_6 as 0 (the option INDICES for 'Longs+Shorts' and 'daily') and "
        "v_input_4 as 3. The /*backtest header beside it carries "
        "args: [[\"v_input_4\", 2]], so the recorded FMZ run used Factor = 2. "
        "The port keeps the declared default 3 and does not adopt backtest-run "
        "state, just as it does not adopt the header's start:/end: window. "
        "Setting source_defaults['Factor'] to 2.0 is the entire change.",
        "`period: 2h` IS taken from the /*backtest header -- it is the only "
        "statement of the chart's timeframe in the pair, and a port must declare "
        "one. basePeriod: 15m is the FMZ backtester's intrabar fill granularity, "
        "not the strategy's period.",
        "Pine v4's second positional argument of strategy.entry is the `long` "
        "FLAG, not a quantity and not v5's direction enum: `strategy.entry("
        "\"Long\", 1, ...)` is long and `strategy.entry(\"Short\", 0, ...)` is "
        "short. The call ORDER (Long entry, Long close, Short entry, Short "
        "close) is preserved verbatim, because it is the fill priority when more "
        "than one fires on a bar.",
        "cross_buy / cross_sell are INTEGERS (1 / 0) consumed by Pine's `and`, "
        "which coerces its operands to bool. The port keeps the integer columns "
        "verbatim (0 is false, 1 is true) and applies that coercion at the `and` "
        "rather than rewriting the source into `== 1`; the same discipline "
        "PINE_SEMANTICS.md 1.17 records for `? -1 : 0`.",
        "barssince is na until its condition first fires, and na propagates "
        "through `0 - barssince(long_exit) + barssince(short_exit)`, so BOTH "
        "cross_buy and cross_sell are 0 until BOTH an SMA crossover and an SMA "
        "crossunder have happened at least once -- no entry on either side is "
        "possible before then. Reproduced.",
        "`Trend := ... : nz(Trend[1], 1)` makes the first bar's direction 1, and "
        "`Trend == 1` then selects TrendUp rather than TrendDown; reproduced.",
        "entry_price = valuewhen(bull or bear, close, 0) is computed by the "
        "source and read by nothing -- no order and no plot. Kept as a column so "
        "the dead code stays visible.",
        "atr(Pd) is rma(tr, Pd); pine_ta.pine_atr seeds the RMA one bar earlier "
        "than Pine's ta.tr default would (PINE_SEMANTICS.md 3.7). Recorded, not "
        "corrected -- a shared-layer boundary.",
        "plot / plotshape / label and f_draw_infopanel are display-only and are "
        "not reproduced.",
        "Leverage, margin, liquidation, funding and the venue's contract-step "
        "rounding are not modelled; the chain verifier measures the step "
        "rounding separately.",
    ]

    def pine_indicators(self, dataframe, params):
        close = dataframe["close"]
        factor = float(params["Factor"])
        pd_len = int(params["Pd"])

        # st_tsl = f_supertrend(Factor, Pd)   -- on the chart (2h) bars.
        st_tsl, _st_trend = _supertrend(dataframe, factor, pd_len)

        # f_securitys(syminfo.tickerid, st_tsl): five `security(..., _source[1],
        # lookahead=true)` calls, one per resolution. All five are computed,
        # exactly as the source computes them, including the unreachable one.
        series = {
            name: _htf_supertrend(dataframe, factor, pd_len, code)
            for name, code in _TF_PERIODS.items()
        }

        # TF == "daily" / "weekly" / "monthly" / "quarterly" / "yearly"
        # NOTE: IS_QUARTERLY compares against "quarterly" while the input's own
        # option list spells it "quartly", so that branch can never be taken and
        # the iff chain falls through to its final else, st_daily.
        tf = str(params["TF"])
        if tf == "daily":
            st_tsl_tf = series["daily"]
        elif tf == "weekly":
            st_tsl_tf = series["weekly"]
        elif tf == "monthly":
            st_tsl_tf = series["monthly"]
        elif tf == "yearly":
            st_tsl_tf = series["yearly"]
        else:
            # "quartly" (and unreachable "quarterly") land here, on st_daily.
            st_tsl_tf = series["daily"]

        # sma_fast = sma(close, fastLength) ; sma_slow = sma(close, slowLength)
        sma_fast = ta.pine_sma(close, int(params["fastLength"]))
        sma_slow = ta.pine_sma(close, int(params["slowLength"]))
        # long_exit = crossunder(sma_fast, sma_slow)
        # short_exit = crossover(sma_fast, sma_slow)
        long_exit = ta.pine_crossunder(sma_fast, sma_slow)
        short_exit = ta.pine_crossover(sma_fast, sma_slow)

        # curr = 0 - barssince(long_exit) + barssince(short_exit)
        curr = -ta.pine_barssince(long_exit) + ta.pine_barssince(short_exit)
        # cross_buy = curr < 0 ? 1 : 0 ; cross_sell = curr > 0 ? 1 : 0
        # na compares false, so a never-fired cross leaves BOTH at 0.
        cross_buy = np.where((curr < 0).to_numpy(), 1, 0)
        cross_sell = np.where((curr > 0).to_numpy(), 1, 0)

        # bull = close >= st_tsl_TF and cross_buy
        # bear = close <= st_tsl_TF and cross_sell
        # Pine's `and` coerces to bool: 0 is false, 1 is true. The integer
        # columns are kept as they are and coerced at the `and`, never rewritten
        # into `== 1`.
        dataframe["pine_st_tsl"] = st_tsl
        dataframe["pine_st_tsl_tf"] = st_tsl_tf
        dataframe["pine_cross_buy"] = cross_buy
        dataframe["pine_cross_sell"] = cross_sell
        dataframe["pine_bull"] = (close >= st_tsl_tf) & cross_buy.astype(bool)
        dataframe["pine_bear"] = (close <= st_tsl_tf) & cross_sell.astype(bool)
        dataframe["pine_long_exit"] = long_exit
        dataframe["pine_short_exit"] = short_exit
        # entry_price = valuewhen(bull or bear, close, 0) -- computed, never read.
        dataframe["pine_entry_price"] = ta.pine_valuewhen(
            dataframe["pine_bull"] | dataframe["pine_bear"], close, 0
        )
        return dataframe

    def pine_context(self, dataframe, params):
        order_type = str(params["orderType"])
        return {
            # isLong = (orderType != "ShortsOnly") ; isShort = (!= "LongsOnly")
            "is_long": order_type != "ShortsOnly",
            "is_short": order_type != "LongsOnly",
            "bull": dataframe["pine_bull"].to_numpy(dtype=bool),
            "bear": dataframe["pine_bear"].to_numpy(dtype=bool),
            "long_exit": dataframe["pine_long_exit"].to_numpy(dtype=bool),
            "short_exit": dataframe["pine_short_exit"].to_numpy(dtype=bool),
        }

    def pine_script(self, broker, i, ctx):
        # The written order below is the fill priority and is preserved:
        # Long entry, Long close, Short entry, Short close.
        if ctx["is_long"]:
            # strategy.entry("Long", 1, when=bull)   -- 1 == strategy.long
            if ctx["bull"][i]:
                broker.entry("Long", "long")
            # strategy.close("Long", when=long_exit)
            if ctx["long_exit"][i]:
                broker.close("Long")

        if ctx["is_short"]:
            # strategy.entry("Short", 0, when=bear)  -- 0 == strategy.short
            if ctx["bear"][i]:
                broker.entry("Short", "short")
            # strategy.close("Short", when=short_exit)
            if ctx["short_exit"][i]:
                broker.close("Short")
