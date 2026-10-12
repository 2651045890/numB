"""Port of sources/SM_1067d9fa52a83c04.pine
(batch_001/Ichimoku云图量化策略Ichimoku-Cloud-Quant-Strategy.md).

Pine v4, LONG ONLY. The trend filter is the Ichimoku cloud, and two optional
filters (a 24/90 EMA pair and a Stochastic RSI) gate the entry:

    donchian(len) => avg(lowest(len), highest(len))
    conversionLine = donchian(9)
    baseLine       = donchian(26)
    leadLine1      = avg(conversionLine, baseLine)
    leadLine2      = donchian(52)

    ema1 = ema(close, len1)        // len1 = 24
    ema2 = ema(close, len2)        // len2 = 90

    rsi1 = rsi(src, lengthRSI)     // src = close, lengthRSI = 14
    k = sma(stoch(rsi1, rsi1, rsi1, lengthStoch), smoothK)   // 14, 3
    d = sma(k, smoothD)                                      // 3

    crossup          = k[0] > d[0] and k[1] <= d[1]
    ichigreenabovered = leadLine1 > leadLine2
    ichimokulong      = close > leadLine1
    greencandle       = close > open
    redcandle         = close < open
    emacond           = ema1 > ema2
    longcondition     = ichigreenabovered and ichimokulong and greencandle

    ichimokuexit = close < leadLine1
    exitcondition = ichimokuexit and redcandle

    if (enablestochrsi == false) and (enableema == false) and longcondition and afterStartDate and (strategy.opentrades < 1)
        strategy.entry("Long", strategy.long)
    if (enablestochrsi == true)  and (enableema == false) and longcondition and crossup and afterStartDate and (strategy.opentrades < 1)
        strategy.entry("Long", strategy.long)
    if (enableema == true) and (enablestochrsi == false) and longcondition and emacond and afterStartDate and (strategy.opentrades < 1)
        strategy.entry("Long", strategy.long)
    if (enableema == true) and (enablestochrsi == true)  and longcondition and emacond and crossup and afterStartDate and (strategy.opentrades < 1)
        strategy.entry("Long", strategy.long)

    if (afterStartDate)
        strategy.close(id = "Long", when = exitcondition)

`strategy()` declares `pyramiding = 0`, `commission_type =
strategy.commission.percent` with `commission_value = 0`,
`default_qty_type = strategy.percent_of_equity`, `default_qty_value = 100` and
`initial_capital = 10000`; `calc_on_order_fills = false` is Pine's own default,
so the order timing is the engine's usual "evaluate at the bar's close, fill at
the next bar's open". No `qty=` is passed anywhere, so every entry is the
100%-of-equity default. `strategy.opentrades < 1` is read at RUN time from the
broker, not precomputed, because it changes as fills arrive.

MEASURED, 2024-01-01..2025-01-01 BTC/USDT:USDT 1d (`verify_chain.py --port
SM_1067d9fa52a83c04`): `mismatch_framework_veto`. The engine books 12 trades,
Freqtrade 11, with one `SOURCE_STAKE_VETO` at the 2024-03-18 fill (required
12666.17 against a 12664.85 maximum). The dumped trade lists show ONE trade
missing -- the engine's long that opened 2024-03-18 and closed 2024-03-20,
which the framework never opened -- and every other trade matches on open date,
close date, direction and open/close price exactly; the reported 10
"mismatches" are that single missing trade shifting the pairing by one. The
cause is the source's own sizing
(`percent_of_equity` / 100, i.e. the whole equity per entry) meeting the
framework's contract-step rounding, documented in PINE_SEMANTICS.md 1.4/1.5/1.6.

FIDELITY:

* All four entry blocks are kept, in the source's order, each with its own
  two-file switch combination and its own `afterStartDate` and
  `strategy.opentrades < 1` guards. With the source's defaults
  (`enableema = true`, `enablestochrsi = false`) only the third block can ever
  fire; the other three are reproduced so that changing a switch changes the
  port the same way it changes the source, not so that they are reachable.
* `lowest(len)` / `highest(len)` are the v3-style ONE-ARGUMENT forms. The
  source is v4 here and FMZ's Pine reference gives highest's default source as
  High and states that ta.lowest uses low, so the port computes
  lowest(low, len) / highest(high, len) -- the standard Donchian channel.
  Same reading and same wording as the sibling port SMIchimokuCloud_7dfe07;
  unverified against the platform.
* `stoch(rsi1, rsi1, rsi1, lengthStoch)` passes the RSI as source, high AND low,
  so it is `100 * (rsi1 - lowest(rsi1, n)) / (highest(rsi1, n) - lowest(rsi1, n))`
  over the RSI series, not over price. A zero range makes the denominator 0 and
  Pine yields na; the port guards that explicitly rather than emitting an inf.
* `crossup` is the source's own two-bar form (`k > d` and `k[1] <= d[1]`), which
  is `ta.crossover`'s definition; the port writes it out as the source does.
* `displacement = input(1, ...)` is read ONLY by the two `plot(offset = ...)`
  calls, which are display-only; the live comparisons use leadLine1 / leadLine2
  undelayed. The input is kept in `source_defaults` for that reason, and the
  cloud shift is NOT applied to the conditions.
* `window()=>true` is defined by the source and never called -- dead code,
  reproduced nowhere because it produces no value and no order; the live gate
  is `afterStartDate`, which the port does reproduce.
* `afterStartDate` is INCLUSIVE at both ends (`time >= start and time <=
  finish`), with start = timestamp(2017,1,1,0,0) and finish =
  timestamp(9999,1,1,23,59) by default, so it is true on every bar of any
  realistic backtest window. The bounds are built as Python datetimes because
  9999 overflows pandas' nanosecond Timestamp. The comparison uses the bar's
  OPENING time in UTC, the exchange timezone for BTC/USDT
  (PINE_SEMANTICS.md 3.4).
* `emasrc = close,` carries a trailing comma in the source; the value handed to
  ema() is `close` either way, and the port uses close.
* ta.ema is seeded with the first non-na observation (pine_ta's modelled
  choice); TradingView's seeding rule is unpublished, so ema1 / ema2 -- and
  `emacond` -- are a named parity risk until the recursion converges. See
  PINE_SEMANTICS.md 3.1. `stoch`/`sma` warm up on top of that, so k / d are na
  through the early bars and `crossup` cannot be true there.
* MD-vs-CODE, recorded not reconciled, four places. The prose says the lead
  lines and the close CROSS each other ("上穿"); the code tests levels
  (`leadLine1 > leadLine2`, `close > leadLine1`). It says the EMA filter needs a
  fast/slow CROSS ("快线上穿慢线"); the code tests `ema1 > ema2`. It says the
  position is closed when price "跌破先导线1"; the code additionally requires a
  red candle (`close < open`). And its argument table renders the numeric-1
  defaults (FromMonth, FromDay, ToMonth, ToDay, Ichi Displacement) as `true`,
  the FMZ exporter's rendering of 1; the code's `1` is used.
* The md's argument table lists 19 rows and the source has 19 `input()` calls;
  the defaults in `source_defaults` are the code's.
* There is no stop, no `strategy.exit`, no take-profit and no trailing stop, so
  `source_reproduce_stops` is False; `strategy.close(id="Long")` is a market
  close, which the engine fills at the next bar's open.
* can_short is False: the only entry in the source is `strategy.long`.
* `plot` / `fill` (the two EMAs and the shaded cloud) are display-only.
* The /*backtest header declares period: 1d on Futures_Binance BTC_USDT, so
  `timeframe` is "1d"; `basePeriod: 1h` is the FMZ backtester's own granularity.
* Leverage, margin, liquidation, funding and the venue's contract-step rounding
  are not modelled. Freqtrade's own stoploss backstop and forced exit at the end
  of a backtest have no counterpart in the source.
"""
from __future__ import annotations

from datetime import datetime, timezone

import numpy as np
import pandas as pd
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


def _donchian(dataframe: pd.DataFrame, length: int) -> pd.Series:
    """`donchian(len) => avg(lowest(len), highest(len))` on low / high."""
    return ta.pine_avg(
        ta.pine_lowest(dataframe["low"], length),
        ta.pine_highest(dataframe["high"], length),
    )


def _stoch(source: pd.Series, length: int) -> pd.Series:
    """Pine `stoch(source, high, low, length)` with all three args the same.

    100 * (source - lowest(low, n)) / (highest(high, n) - lowest(low, n)).
    Pine yields na when the denominator is 0 (the source's own division rule);
    the port applies the same guard instead of letting an inf through.
    """
    lowest = ta.pine_lowest(source, length)
    highest = ta.pine_highest(source, length)
    span = highest - lowest
    span = span.where(span != 0.0)
    return 100.0 * (source - lowest) / span


def _time_window(index, start: datetime, end: datetime) -> np.ndarray:
    """Pine `time >= start and time <= end` on the bar's OPENING time.

    Inclusive at both ends, as the source writes it. Bounds are Python
    datetimes because this source's ToYear is 9999, which overflows pandas'
    nanosecond Timestamp; `time` is the bar's opening time in the exchange
    timezone, which the frame records in UTC.
    """
    times = pd.DatetimeIndex(index)
    if times.tz is None:
        times = times.tz_localize("UTC")
    return np.fromiter(
        (start <= t.to_pydatetime() <= end for t in times),
        dtype=bool, count=len(times),
    )


class SMIchimokuCloudQuant_1067d9(PinePortBase, IStrategy):
    source_id = "SM_1067d9fa52a83c04"
    source_file = "Ichimoku云图量化策略Ichimoku-Cloud-Quant-Strategy.md"
    timeframe = "1d"
    can_short = False
    source_defaults: dict = {
        "FromMonth": 1,
        "FromDay": 1,
        "FromYear": 2017,
        "ToMonth": 1,
        "ToDay": 1,
        "ToYear": 9999,
        "enableema": True,
        "enablestochrsi": False,
        "len1": 24,
        "len2": 90,
        "smoothK": 3,
        "smoothD": 3,
        "lengthRSI": 14,
        "lengthStoch": 14,
        # src = input(close, title="RSI Source")
        "src": "close",
        "conversionPeriods": 9,
        "basePeriods": 26,
        "laggingSpan2Periods": 52,
        "displacement": 1,
    }
    source_qty_type = "percent_of_equity"
    source_qty_value = 100.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 10_000.0
    # strategy.close(id="Long") is a market close; no stop/limit/trail exists.
    source_reproduce_stops = False
    source_fidelity_notes = [
        "All four entry blocks are reproduced in source order, each with its own "
        "switch combination, its own afterStartDate guard and its own "
        "`strategy.opentrades < 1`. With the source's defaults "
        "(enableema=true, enablestochrsi=false) only the third is reachable; the "
        "other three are kept so the switches behave as the source's do.",
        "`strategy.opentrades < 1` is read from the broker at run time, not "
        "precomputed as a column: it changes as fills arrive, so a precomputed "
        "mask would not be the same condition.",
        "`lowest(len)` / `highest(len)` are the v3-style one-argument forms. "
        "FMZ's Pine reference gives highest's default source as High and states "
        "that ta.lowest uses low, so the port computes lowest(low, len) / "
        "highest(high, len). Same reading and wording as SMIchimokuCloud_7dfe07; "
        "unverified against the platform.",
        "`stoch(rsi1, rsi1, rsi1, lengthStoch)` passes the RSI as source, high "
        "and low, so the band is built on the RSI series, not on price. A zero "
        "range makes Pine's division yield na; the port applies that guard "
        "explicitly.",
        "`displacement` is read ONLY by the two display-only plot(offset=...) "
        "calls. The live comparisons use leadLine1 / leadLine2 undelayed, so the "
        "input is recorded but no shift is applied to any condition.",
        "`window()=>true` is defined and never called -- dead code. It produces "
        "no value and no order, so nothing is emitted for it; the live gate, "
        "`afterStartDate`, IS reproduced.",
        "afterStartDate is inclusive at both ends (time >= start and time <= "
        "finish). Default bounds are 2017-01-01 00:00 and 9999-01-01 23:59, so "
        "it is true on every bar of a realistic window; the bounds are built as "
        "Python datetimes because 9999 overflows pandas' nanosecond Timestamp. "
        "Evaluated on the bar's opening time in UTC, the exchange timezone for "
        "BTC/USDT (PINE_SEMANTICS.md 3.4).",
        "`emasrc = close,` carries a trailing comma in the source; ema() receives "
        "close either way and the port passes close.",
        "ta.ema is seeded with the first non-na observation (pine_ta's modelled "
        "choice); TradingView's seeding rule is unpublished, so ema1 / ema2 and "
        "therefore emacond carry that parity risk until the recursion converges "
        "(PINE_SEMANTICS.md 3.1).",
        "Warm-up measured on BTC/USDT:USDT 1d 2024 (367 bars): rsi1 is first "
        "valid at bar 14, k at 29 and d at 31, so `crossup` cannot be true "
        "before bar 31. Measured on the same window: afterStartDate is true on "
        "367 of 367 bars, which is what the default 2017-01-01..9999-01-01 "
        "bounds imply.",
        "MD-vs-CODE, four places, recorded not reconciled: (1) the prose says the "
        "lead lines and the close CROSS ('上穿') while the code tests levels "
        "(leadLine1 > leadLine2, close > leadLine1); (2) it says the EMA filter "
        "needs a fast/slow cross ('快线上穿慢线') while the code tests ema1 > "
        "ema2; (3) it says the exit is price '跌破先导线1' while the code also "
        "requires a red candle (close < open); (4) its argument table renders the "
        "numeric-1 defaults (FromMonth, FromDay, ToMonth, ToDay, Ichi "
        "Displacement) as `true` -- the FMZ exporter's rendering of 1 -- and the "
        "code's 1 is used.",
        "The md's argument table lists 19 rows and the source has 19 input() "
        "calls; the defaults recorded here are the code's.",
        "There is no stop, no strategy.exit, no take-profit and no trailing stop, "
        "so source_reproduce_stops is False. strategy.close(id=\"Long\") is a "
        "market close, which the engine fills at the next bar's open.",
        "can_short is False -- the only entry in the source is strategy.long.",
        "plot / fill (the two EMAs and the shaded cloud) are display-only.",
        "The /*backtest header declares period: 1d, so timeframe is 1d; "
        "basePeriod: 1h is the FMZ backtester's own filling granularity.",
        "Leverage, margin, liquidation, funding and venue contract-step rounding "
        "are not modelled; Freqtrade's stoploss backstop and its forced exit at "
        "the end of a backtest have no counterpart in the source.",
    ]

    def pine_indicators(self, dataframe: pd.DataFrame, params: dict) -> pd.DataFrame:
        close = dataframe["close"]
        open_ = dataframe["open"]

        # --- Ichimoku -------------------------------------------------------
        conversion_line = _donchian(dataframe, int(params["conversionPeriods"]))
        base_line = _donchian(dataframe, int(params["basePeriods"]))
        lead_line1 = ta.pine_avg(conversion_line, base_line)
        lead_line2 = _donchian(dataframe, int(params["laggingSpan2Periods"]))

        # --- EMAs -----------------------------------------------------------
        ema1 = ta.pine_ema(close, int(params["len1"]))
        ema2 = ta.pine_ema(close, int(params["len2"]))

        # --- Stochastic RSI -------------------------------------------------
        # rsi1 = rsi(src, lengthRSI) with src = input(close).
        rsi1 = ta.pine_rsi(close, int(params["lengthRSI"]))
        # k = sma(stoch(rsi1, rsi1, rsi1, lengthStoch), smoothK); d = sma(k, smoothD)
        k = ta.pine_sma(_stoch(rsi1, int(params["lengthStoch"])), int(params["smoothK"]))
        d = ta.pine_sma(k, int(params["smoothD"]))

        # --- Conditions -----------------------------------------------------
        # crossup = k[0] > d[0] and k[1] <= d[1]
        crossup = (k > d) & (k.shift(1) <= d.shift(1))
        ichigreenabovered = lead_line1 > lead_line2
        ichimokulong = close > lead_line1
        greencandle = close > open_
        redcandle = close < open_
        emacond = ema1 > ema2
        longcondition = ichigreenabovered & ichimokulong & greencandle

        ichimokuexit = close < lead_line1
        exitcondition = ichimokuexit & redcandle

        # afterStartDate = time >= start and time<=finish?true:false
        after_start_date = _time_window(
            dataframe.index,
            datetime(
                int(params["FromYear"]), int(params["FromMonth"]),
                int(params["FromDay"]), 0, 0, tzinfo=timezone.utc,
            ),
            datetime(
                int(params["ToYear"]), int(params["ToMonth"]),
                int(params["ToDay"]), 23, 59, tzinfo=timezone.utc,
            ),
        )

        dataframe["pine_conversion_line"] = conversion_line
        dataframe["pine_base_line"] = base_line
        dataframe["pine_lead_line1"] = lead_line1
        dataframe["pine_lead_line2"] = lead_line2
        dataframe["pine_ema1"] = ema1
        dataframe["pine_ema2"] = ema2
        dataframe["pine_rsi1"] = rsi1
        dataframe["pine_k"] = k
        dataframe["pine_d"] = d
        dataframe["pine_crossup"] = crossup.fillna(False)
        dataframe["pine_ichigreenabovered"] = ichigreenabovered
        dataframe["pine_ichimokulong"] = ichimokulong
        dataframe["pine_greencandle"] = greencandle
        dataframe["pine_redcandle"] = redcandle
        dataframe["pine_emacond"] = emacond
        dataframe["pine_longcondition"] = longcondition
        dataframe["pine_ichimokuexit"] = ichimokuexit
        dataframe["pine_exitcondition"] = exitcondition
        dataframe["pine_after_start_date"] = after_start_date
        return dataframe

    def pine_context(self, dataframe: pd.DataFrame, params: dict) -> dict:
        return {
            "longcondition": dataframe["pine_longcondition"].to_numpy(dtype=bool),
            "crossup": dataframe["pine_crossup"].to_numpy(dtype=bool),
            "emacond": dataframe["pine_emacond"].to_numpy(dtype=bool),
            "exitcondition": dataframe["pine_exitcondition"].to_numpy(dtype=bool),
            "after_start_date": dataframe["pine_after_start_date"].to_numpy(dtype=bool),
            "enableema": bool(params["enableema"]),
            "enablestochrsi": bool(params["enablestochrsi"]),
        }

    def pine_script(self, broker, i: int, ctx: dict) -> None:
        longcondition = bool(ctx["longcondition"][i])
        crossup = bool(ctx["crossup"][i])
        emacond = bool(ctx["emacond"][i])
        after_start_date = bool(ctx["after_start_date"][i])
        enableema = ctx["enableema"]
        enablestochrsi = ctx["enablestochrsi"]

        # if (enablestochrsi == false) and (enableema == false) and (longcondition)
        #    and (afterStartDate) and (strategy.opentrades < 1)
        #     strategy.entry("Long", strategy.long)
        if (not enablestochrsi) and (not enableema) and longcondition \
                and after_start_date and broker.open_trades < 1:
            broker.entry("Long", "long")

        # if (enablestochrsi == true) and (enableema == false) and (longcondition)
        #    and (crossup) and (afterStartDate) and (strategy.opentrades < 1)
        if enablestochrsi and (not enableema) and longcondition \
                and crossup and after_start_date and broker.open_trades < 1:
            broker.entry("Long", "long")

        # if (enableema == true) and (enablestochrsi == false) and (longcondition)
        #    and (emacond) and (afterStartDate) and (strategy.opentrades < 1)
        if enableema and (not enablestochrsi) and longcondition \
                and emacond and after_start_date and broker.open_trades < 1:
            broker.entry("Long", "long")

        # if (enableema == true) and (enablestochrsi == true) and (longcondition)
        #    and (emacond) and (crossup) and (afterStartDate)
        #    and (strategy.opentrades < 1)
        if enableema and enablestochrsi and longcondition \
                and emacond and crossup and after_start_date and broker.open_trades < 1:
            broker.entry("Long", "long")

        # if (afterStartDate)
        #     strategy.close(id = "Long", when = exitcondition)
        if after_start_date:
            broker.close("Long", when=bool(ctx["exitcondition"][i]))
