"""Port of sources/SM_4da0d3580260dd6b.pine
(batch_001/KP移动平均趋势策略Heyping-Moving-Average-Trend-Strategy.md).

Pine v5, multi-timeframe. Two `request.security()` reads feed two EMAs, and the
crossover between them is the whole order logic:

    ha_close  = request.security(syminfo.tickerid, "D", close[hshift])
    mha_close = request.security(syminfo.tickerid, "W", close[mhshift])

    fma = ta.ema(mha_close[test], fama)     // fama = 10, EMA of the WEEKLY close
    sma = ta.ema(ha_close[slomas], sloma)   // sloma = 100, EMA of the DAILY close

    golong   = ta.crossover(fma, sma)
    exitLong = ta.crossunder(fma, sma)

    if (golong)
        strategy.entry("Buy", strategy.long)
    if (exitLong)
        strategy.close("Buy")

`strategy()` declares only `title` and `shorttitle`, so every property is Pine's
documented default: `strategy.fixed` / 1 contract, initial capital 1000000,
commission 0%, pyramiding 0, `process_orders_on_close=false`. The `/*backtest`
header declares `period: 1d` on Futures_Binance BTC_USDT, so `timeframe` is
"1d"; its `basePeriod: 1h` is the FMZ backtester's own granularity for filling
those daily bars, not the strategy's period.

MULTI-TIMEFRAME -- READ THIS BEFORE TRUSTING THE SERIES (PINE_SEMANTICS 2.1).
The engine does not resample, so both `request.security` reads are supplied by
this port instead of by the layer, and that supply is an INTERPRETATION, not a
verified equivalence. On a 1d chart the `"D"` read is the chart's own timeframe:
at the close of daily bar `d`, the last CLOSED daily bar is `d` itself, so
`ha_close == close` (with `hshift = 0`). The `"W"` read is the one that needs a
rule, and this port uses the documented historical-bar behaviour of
`barmerge.lookahead_off` -- the value of the last COMPLETED higher-timeframe bar
-- so a daily bar in week W reads the weekly close of week W-1, forward-filled
across the week. The alternative reading (the still-forming weekly bar's running
close, which is what a realtime bar sees) would make `mha_close` equal to the
daily close and turn this into a plain EMA(10)/EMA(100) crossover on daily bars
-- a materially different strategy, not a refinement of this one. The source
carries no `lookahead` argument, so the platform default applies; that default
is documented behaviour and not evidence about what FMZ's own Pine runtime
does. This is the single largest fidelity risk in the port and is the reason it
is a PARTIAL port rather than a verified one.

The remaining pieces of the block are transcribed as written, including the
dead ones: `ha_t` is assigned from a third `request.security` call and never
read; `stoploss` is an input that no order call consults (so there is no stop to
reproduce); `showplots` only gates the two `plot` calls; and `res` / `res1` are
the timeframe strings themselves, which no expression reads back.

FIDELITY:

* The md's "Strategy Arguments" table shows `false` for the four shift inputs
  that the source declares as `input(0, ...)` (`hshift`, `mhshift`, `test`,
  `slomas`) and for `logtransform`. The source is authoritative: those four are
  the integer 0 (a zero shift), not the boolean false. The port uses 0 and
  records the table as a rendering artefact of the md exporter.
* PINE_SEMANTICS 2.1 (explicitly unmodelled): `request.security()` is supplied
  here as an explicitly aligned series. See the block above for the rule used
  and for the alternative that was NOT chosen. This is a modelling choice, not
  a verified reproduction.
* The weekly alignment keys weeks by the calendar week ending Sunday (ISO weeks,
  Monday start) in UTC, because the source's exchange is Futures_Binance
  BTC_USDT and the local candles are UTC. PINE_SEMANTICS 3.4: Pine's calendar
  functions use the exchange's timezone, which is modelled here as UTC.
* The variable named `sma` is an EMA (`ta.ema(ha_close[slomas], sloma)`), not a
  simple moving average, and it is the SLOW leg despite being named after one.
  The variable named `fma` is the fast leg. Both are reproduced with
  `pine_ema`; the names carry no formula.
* `ha_t = request.security(syminfo.tickerid, res, expression=hlc3)` is dead
  code -- assigned and never read by the source. It is NOT computed here; there
  is no way for it to affect an order, and materialising a third `security`
  series would only add an unverified number to the ledger.
* `stoploss = input(true, ...)` is never consulted by any order call in the
  source; there is no `strategy.exit`, `stop`, `limit`, `trail` or `cancel`
  anywhere, so `source_reproduce_stops` is False and a position open at the end
  of the window stays open. The input is declared because the source declares
  it.
* `logtransform` is honoured: when true, both `request.security` expressions
  read `math.log(close[...])` and the port takes the log of the (shifted) close
  before the EMA. For positive prices a crossover of `log(a)` and `log(b)` is
  the same event as a crossover of `a` and `b`, but the two EMAs themselves are
  not related by a monotone transform, so the branch is implemented rather than
  argued away. The plots' `math.exp` inverse transform is display-only.
* `hshift`, `mhshift`, `test` and `slomas` all default to 0, so they are
  no-ops on the data this port is verified against and nothing below depends on
  how they are placed. For non-default values the port applies `hshift` /
  `mhshift` to the daily close BEFORE the resample and `test` / `slomas` to the
  post-`security` series. `test` / `slomas` are unambiguous (the shifted series
  is the `security` result, which lives on the chart's timeframe). `hshift` /
  `mhshift` are NOT: `request.security` evaluates its expression in the
  requested timeframe's own context, so a non-zero `mhshift` may mean "shift the
  weekly close by N weeks" rather than "shift the daily close by N days before
  resampling". The two agree at 0 and the port does not guess which holds
  otherwise.
* PINE_SEMANTICS 3.1 (modelled choice): `ta.ema` is seeded with the first non-na
  observation and an na observation does not advance the recursion. The weekly
  series is na for its first week, so the weekly EMA is seeded one week later
  than the daily one.
* The `plot` calls and `overlay=false` are display-only and place no condition.
* PINE_SEMANTICS 1.6 / 5.1: the venue's contract-step rounding and non-zero
  taker fees are not modelled. The source declares 0% commission, which is the
  cost basis the port carries.
* PINE_SEMANTICS 二.2 (not modelled): the intrabar path. Both orders here are
  market orders, so no in-bar stop/limit resolution is involved.
* Leverage, margin, liquidation and funding are not modelled.
"""
from freqtrade.strategy import IStrategy

import numpy as np
import pandas as pd

import pine_ta as ta
from pine_port_base import PinePortBase


def _utc_weeks(index: pd.DatetimeIndex) -> pd.PeriodIndex:
    """Calendar weeks (Monday..Sunday) of `index`, in UTC."""
    if index.tz is None:
        index = index.tz_localize("UTC")
    else:
        index = index.tz_convert("UTC")
    return index.tz_localize(None).to_period("W-SUN")


class SMKpMovingAverageTrend_4da0d3(PinePortBase, IStrategy):
    source_id = "SM_4da0d3580260dd6b"
    source_file = "KP移动平均趋势策略Heyping-Moving-Average-Trend-Strategy.md"
    timeframe = "1d"
    can_short = False
    source_defaults: dict = {
        "res": "D",
        "hshift": 0,
        "res1": "W",
        "mhshift": 0,
        "fama": 10,
        "test": 0,
        "sloma": 100,
        "slomas": 0,
        "logtransform": False,
        "stoploss": True,
        "showplots": True,
    }
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    source_reproduce_stops = False
    source_fidelity_notes = [
        "PARTIAL PORT -- multi-timeframe. The source calls request.security() "
        "twice and the engine does not resample (PINE_SEMANTICS 2.1), so this "
        "port supplies both aligned series itself. The \"D\" read on a 1d chart "
        "is the chart's own timeframe and collapses to `close`; the \"W\" read "
        "is supplied as the last COMPLETED calendar week's close, "
        "forward-filled across the current week, which is the documented "
        "historical-bar behaviour of barmerge.lookahead_off.",
        "The alternative reading of lookahead_off -- the forming week's running "
        "close, which is what a realtime bar sees -- would make mha_close equal "
        "to the daily close and reduce the strategy to an EMA(10)/EMA(100) "
        "crossover on daily bars. The source passes no `lookahead` argument, so "
        "the platform default applies; that default is documented TradingView "
        "behaviour and no evidence about FMZ's own Pine runtime. This "
        "interpretation is the single largest fidelity risk in the port.",
        "Weeks are keyed Monday..Sunday in UTC, because the source's exchange is "
        "Futures_Binance BTC_USDT and the local candles are UTC "
        "(PINE_SEMANTICS 3.4: Pine calendar functions use the exchange's "
        "timezone, modelled here as UTC).",
        "The md's Strategy Arguments table renders the four shift inputs "
        "(`hshift`, `mhshift`, `test`, `slomas`) and `logtransform` as `false`. "
        "The source declares the four shifts as `input(0, ...)`, i.e. the "
        "integer 0 / a zero shift, and only `logtransform` is a boolean. The "
        "source is authoritative; the table is an md rendering artefact.",
        "`ha_t = request.security(syminfo.tickerid, res, expression=hlc3)` is "
        "dead code -- assigned and never read by the source. It is not "
        "computed here: it cannot affect an order, and materialising a third "
        "unverified security series would only add noise to the ledger.",
        "`stoploss = input(true, ...)` is consulted by no order call -- the "
        "source has no strategy.exit / stop / limit / trail / cancel at all -- "
        "so source_reproduce_stops is False and a position open at the end of "
        "the window stays open.",
        "`logtransform` is honoured: the log is taken INSIDE the security "
        "expression, i.e. on the shifted close before the weekly resample, "
        "exactly where the source applies it. A crossover of log(a) and log(b) "
        "is the same event as a crossover of a and b for positive prices, but "
        "the two EMAs are not related by a monotone transform, so the branch is "
        "implemented rather than argued away.",
        "The four shifts are applied where the source applies them: hshift / "
        "mhshift inside the security expression (on the daily series, before "
        "the resample) and test / slomas on the post-security series. All four "
        "default to 0.",
        "PINE_SEMANTICS 3.1 (modelled choice): ta.ema is seeded with the first "
        "non-na observation and an na observation does not advance the "
        "recursion. The weekly series is na over its first week, so the weekly "
        "EMA is seeded a week later than the daily one.",
        "The plot calls and `overlay=false` are display-only and place no "
        "condition.",
        "No short entry exists, so can_short is False.",
        "PINE_SEMANTICS 1.6 / 5.1: the venue's contract-step rounding and "
        "non-zero taker fees are not modelled. The source declares 0% "
        "commission, which is the cost basis the port carries.",
        "Leverage, margin, liquidation and funding are not modelled.",
    ]

    def pine_indicators(self, dataframe, params):
        index = dataframe.index
        if not isinstance(index, pd.DatetimeIndex):
            raise ValueError(
                f"{type(self).__name__} needs a DatetimeIndex to align the "
                "weekly request.security series"
            )

        hshift = int(params["hshift"])
        mhshift = int(params["mhshift"])
        test = int(params["test"])
        slomas = int(params["slomas"])
        log_transform = bool(params["logtransform"])

        close = dataframe["close"]
        # The source's `close[hshift]` / `close[mhshift]` inside the security
        # expression: a shift on the CHART's series, before any resampling.
        ha_source = close.shift(hshift) if hshift else close
        mha_source = close.shift(mhshift) if mhshift else close
        if log_transform:
            ha_source = np.log(ha_source)
            mha_source = np.log(mha_source)

        # ha_close = request.security(syminfo.tickerid, "D", ...) on a 1d chart:
        # at the close of bar d the last CLOSED daily bar is d itself.
        ha_close = ha_source

        # mha_close = request.security(syminfo.tickerid, "W", ...) with
        # lookahead_off: the last COMPLETED weekly bar's value, held across the
        # week that is still forming.
        weeks = _utc_weeks(index)
        weekly = mha_source.groupby(weeks).last()
        last_completed = weekly.shift(1)
        lookup = last_completed.to_dict()
        mha_close = pd.Series(
            [lookup.get(week, np.nan) for week in weeks],
            index=dataframe.index,
            dtype=float,
        )

        # fma = ta.ema(mha_close[test], fama)
        fma_source = mha_close.shift(test) if test else mha_close
        fma = ta.pine_ema(fma_source, int(params["fama"]))
        # sma = ta.ema(ha_close[slomas], sloma)
        sma_source = ha_close.shift(slomas) if slomas else ha_close
        sma = ta.pine_ema(sma_source, int(params["sloma"]))

        # golong   = ta.crossover(fma, sma)
        # exitLong = ta.crossunder(fma, sma)
        dataframe["pine_ha_close"] = ha_close
        dataframe["pine_weekly_close"] = mha_close
        dataframe["pine_fma"] = fma
        dataframe["pine_sma"] = sma
        dataframe["pine_golong"] = ta.pine_crossover(fma, sma)
        dataframe["pine_exit_long"] = ta.pine_crossunder(fma, sma)
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "golong": dataframe["pine_golong"].to_numpy(),
            "exit_long": dataframe["pine_exit_long"].to_numpy(),
        }

    def pine_script(self, broker, i, ctx):
        # if (golong)
        #     strategy.entry("Buy", strategy.long)
        if ctx["golong"][i]:
            broker.entry("Buy", "long")
        # if (exitLong)
        #     strategy.close("Buy")
        if ctx["exit_long"][i]:
            broker.close("Buy")
