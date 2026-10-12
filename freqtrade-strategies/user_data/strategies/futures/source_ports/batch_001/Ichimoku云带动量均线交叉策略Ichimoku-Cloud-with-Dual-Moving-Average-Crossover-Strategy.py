"""Port of sources/SM_01d3f0cbc7236f46.pine (batch_001/Ichimoku云带动量均线交叉策略Ichimoku-Cloud-with-Dual-Moving-Average-Crossover-Strategy.md).

Pine v3, daily chart, long AND short, by ChaoZhang ("13/21 EMA + Ichimoku Kinko
Hyo Strategy", shorttitle "EMI"). An Ichimoku cloud whose four lines are all
Donchian midpoints, filtered by two EMAs and by a lagging close:

    donchian(len) => avg(lowest(len), highest(len))
    TenkanSen   = donchian(TenkanSenPeriods)      // default 9
    KijunSen    = donchian(KijunSenPeriods)       // default 26
    SenkouSpanA = avg(TenkanSen, KijunSen)
    SenkouSpanB = donchian(SenkouSpanBPeriods)    // default 52
    ChikouSpan  = close[displacement-1]           // default close[25]

    Sema  = ema(close, 13)
    Mema  = ema(close, 21)
    Lema  = ema(close, 89)
    XLema = ema(close, 233)

    longCondition  = close>ChikouSpan and Sema>KijunSen and Sema>Mema and SenkouSpanA>SenkouSpanB
    shortCondition = close<ChikouSpan and Sema<KijunSen and Sema<Mema and SenkouSpanA<SenkouSpanB

    strategy.entry("Long",  strategy.long,  when = longCondition)
    strategy.close("Long",  when = (close<KijunSen and close<ChikouSpan and Sema<Mema))
    strategy.entry("Short", strategy.short, when = shortCondition)
    strategy.close("Short", when = (close>KijunSen and close>ChikouSpan and Sema>Mema))

FOUR ORDERS, in that exact written order, and the order is preserved here because
it is the engine's fill priority on a bar where more than one fires. No `qty=`
is passed to either entry, so every entry is the script's
`default_qty_type = strategy.percent_of_equity` / `default_qty_value = 100`
sizing. `strategy.entry("Short", strategy.short, ...)` is an ACTIVE short entry,
so `can_short` is True.

FIDELITY -- translation choices and source/md mismatches:

1. `donchian(len) => avg(lowest(len), highest(len))` uses Pine v3's
   ONE-ARGUMENT `lowest` / `highest`, whose source defaults to the bar's `low` /
   `high` (the two-argument form takes an explicit source). That is the Donchian
   channel the Ichimoku lines are defined on, and it is what the port computes:
   `avg(lowest(low, len), highest(high, len))`. The function's own name
   corroborates the reading, and it is the same one the other Ichimoku port in
   this batch takes (`batch_001/BVs-ICHIMOKU-CLOUD-All-Signals.py`, whose
   `donchian` is `(pine_lowest(low, n) + pine_highest(high, n)) / 2`). Pine v3's
   signature list is the only evidence available offline and the original
   platform was not consulted.
2. `ChikouSpan = close[displacement-1]` is a HISTORY reference -- `close[25]`
   with the default displacement of 26 -- and is reproduced with `.shift(25)`.
   The three `plot(..., offset=...)` calls that draw the cloud and the lagging
   line shifted forward are display-only: no `offset` enters any condition, so
   no future data reaches the signals.
3. `Lema = ema(close, 89)` and `XLema = ema(close, 233)` are computed by the
   source and read by NOTHING but their own `plot` calls. They are kept as
   ledger columns because the source computes them.
4. The source's EIGHT `plot(...)` calls and its one `fill(...)` are display-only
   and are not reproduced. The `fill`'s colour reads `SenkouSpanA >
   SenkouSpanB` but places no order. There is no `barcolor` call anywhere in the
   source (checked by grep over the .pine, not inferred).
5. MD/SOURCE MISMATCH (long entry): the md's English prose says the long entry
   requires "price within cloud" and the Chinese prose says 价格位于云带之上
   ("price above the cloud"). The source has NO price-versus-cloud test at all;
   its fourth conjunct is `SenkouSpanA > SenkouSpanB` -- cloud line A above
   cloud line B. The source is followed and no price/cloud comparison is
   invented.
6. MD/SOURCE MISMATCH (indicator inventory): the md describes only the 13 and 21
   EMAs ("双均线部分由13周期与21周期指数移动平均线组成"). The source also
   computes two more EMAs, 89 and 233, which no condition reads (see 3).
7. `ta.ema` is pine_ta.pine_ema, seeded with the first non-na observation (an
   unpublished TradingView rule; see PINE_SEMANTICS.md 3.1). Every condition
   here is built on EMAs, so -- as PINE_SEMANTICS.md 3.1 records for the
   SM_c5893b39f3d0f147 port -- the earliest trades are expected to differ from
   the original platform's and the port does not claim bar-for-bar agreement in
   the warmup. `pine_lowest` / `pine_highest` return na until their window
   fills, so `SenkouSpanB` is na for the first 51 bars and `ChikouSpan` for the
   first 25, which makes both entry conditions false there; the longest computed
   window is 233 bars (XLema), which is longer than any gating window.
8. The source declares no `commission_type` / `commission_value`, so Pine's
   documented default 0% applies; `initial_capital` is not declared either, so
   Pine's documented default 1000000 USD is used. `max_bars_back=1000` is not
   modelled -- the engine sees the whole frame.
9. `calc_on_order_fills=true` and `calc_on_every_tick=true` are declared. What
   they do to a BACKTEST on the original platform is unpublished, and this
   engine evaluates the script once per CLOSED bar and fills market orders at
   the next bar's open. The intrabar recalculation is therefore NOT modelled;
   the manifest flags this source `intrabar_recalculation` for that reason.
10. The `/*backtest` header's `period: 1d` IS taken as the timeframe -- it is the
    only statement of the chart's period in the pair. `basePeriod: 1h` is the
    FMZ backtester's own intrabar granularity, not the strategy's period, and the
    header's start:/end: window is not applied: the port runs on whatever range
    the caller supplies.
11. The md's Strategy Arguments table lists v_input_1..v_input_4 as 9 / 26 / 52 /
    26, matching the four declarations. The 13/21/89/233 EMA lengths are
    literals in the source and stay literals here (they are not inputs).
12. There is no stop, take-profit, trail or order-cancellation call anywhere in
    the source: the only exits are the two market `strategy.close` calls, so
    `source_reproduce_stops` is False.
13. Leverage, margin, liquidation, funding and the venue's contract-step
    rounding are not modelled; the chain verifier measures the last of those
    separately.
"""
from __future__ import annotations

import pandas as pd

from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


def _donchian(low: pd.Series, high: pd.Series, length: int) -> pd.Series:
    """`donchian(len) => avg(lowest(len), highest(len))` over low / high."""
    return ta.pine_avg(ta.pine_lowest(low, length), ta.pine_highest(high, length))


class SMIchimokuCloudDualMa_01d3f0(PinePortBase, IStrategy):
    source_id = "SM_01d3f0cbc7236f46"
    source_file = (
        "Ichimoku云带动量均线交叉策略"
        "Ichimoku-Cloud-with-Dual-Moving-Average-Crossover-Strategy.md"
    )
    # /*backtest ... period: 1d, basePeriod: 1h
    timeframe = "1d"
    can_short = True
    source_defaults = {
        # input(9, minval=1, title="Tenkan Sen Periods")
        "TenkanSenPeriods": 9,
        # input(26, minval=1, title="Kijun Sen Periods")
        "KijunSenPeriods": 26,
        # input(52, minval=1, title="Senkou Span B Periods")
        "SenkouSpanBPeriods": 52,
        # input(26, minval=1, title="Displacement")
        "displacement": 26,
    }
    # strategy(... default_qty_type=strategy.percent_of_equity, default_qty_value=100 ...)
    source_qty_type = "percent_of_equity"
    source_qty_value = 100.0
    # No commission_type / commission_value is declared -> Pine's documented 0%.
    source_commission_percent = 0.0
    # pyramiding=0 is declared (and is Pine's default anyway).
    source_pyramiding = 0
    # initial_capital is not declared -> Pine's documented default.
    source_initial_capital = 1_000_000.0
    # Both exits are market `strategy.close`; no stop / limit / trail anywhere.
    source_reproduce_stops = False
    source_fidelity_notes = [
        "donchian(len) => avg(lowest(len), highest(len)) uses Pine v3's "
        "ONE-ARGUMENT lowest / highest, whose source defaults to the bar's low / "
        "high (the two-argument form takes an explicit source). That is the "
        "Donchian channel the Ichimoku lines are built from, and the port "
        "computes avg(pine_lowest(low, len), pine_highest(high, len)), matching "
        "the other Ichimoku ports in this corpus. Pine v3's signature list is the "
        "only offline evidence; the original platform was not consulted.",
        "ChikouSpan = close[displacement-1] is a HISTORY reference (close[25] at "
        "the default displacement of 26), reproduced with .shift(displacement-1). "
        "The plot() calls that draw the cloud and the lagging line with "
        "offset=displacement are display-only: no offset enters any condition, so "
        "no future data reaches the signals and no repainting occurs.",
        "Lema = ema(close, 89) and XLema = ema(close, 233) are computed by the "
        "source and read by nothing but their own plot() calls. Kept as ledger "
        "columns because the source computes them.",
        "The source's eight plot() calls and its one fill() are display-only and "
        "are not reproduced; the fill reads SenkouSpanA > SenkouSpanB but places "
        "no order. The source contains no barcolor call (grep-checked).",
        "MD/SOURCE MISMATCH (long entry): the md's English prose requires \"price "
        "within cloud\" and its Chinese prose 价格位于云带之上 (\"price above the "
        "cloud\"). The source has NO price-versus-cloud test; its fourth conjunct "
        "is SenkouSpanA > SenkouSpanB -- cloud line A above cloud line B. Source "
        "followed; no price/cloud comparison is invented.",
        "MD/SOURCE MISMATCH (indicator inventory): the md describes only the 13 "
        "and 21 EMAs. The source additionally computes ema(close, 89) and "
        "ema(close, 233), which no condition reads.",
        "ta.ema is pine_ta.pine_ema, seeded with the first non-na observation -- "
        "an UNPUBLISHED TradingView rule (PINE_SEMANTICS.md 3.1). Every condition "
        "here is derived from EMAs, so the earliest trades are a known and "
        "unremoved equivalence risk; this port does not claim bar-for-bar "
        "agreement in the warmup. pine_lowest / pine_highest in turn return na "
        "until their window fills, so SenkouSpanB is na for the first 51 bars and "
        "ChikouSpan for the first 25, making both entry conditions false there. "
        "The longest COMPUTED window is 233 bars (XLema), which is not a gating "
        "window: nothing gates on it.",
        "The source declares no commission_type / commission_value (Pine's "
        "documented default 0%) and no initial_capital (Pine's documented default "
        "1000000 USD); both are recorded as they fall out of the declarations. "
        "max_bars_back=1000 is not modelled -- the engine sees the whole frame.",
        "calc_on_order_fills=true and calc_on_every_tick=true are declared. Their "
        "effect on the ORIGINAL platform's backtest is unpublished, and this "
        "engine evaluates the script once per CLOSED bar and fills market orders "
        "at the next bar's open. Intrabar recalculation is therefore NOT modelled; "
        "the manifest flags this source intrabar_recalculation.",
        "period: 1d IS taken from the /*backtest header -- the only statement of "
        "the chart's period in the pair. basePeriod: 1h is the FMZ backtester's "
        "own intrabar fill granularity, and the header's start:/end: window is "
        "not applied: the port runs on whatever range the caller supplies.",
        "Both entries are plain market orders with no qty=, stop or limit, so the "
        "engine fills them at the next bar's open with the script's "
        "percent_of_equity / 100 sizing. There is no stop, take-profit, trail or "
        "cancellation call anywhere in the source -- the only exits are the two "
        "market strategy.close calls -- so source_reproduce_stops is False.",
        "The four order calls are reproduced in the source's written order (Long "
        "entry, Long close, Short entry, Short close), which is the engine's fill "
        "priority on a bar where more than one fires.",
        "Leverage, margin, liquidation, funding and the venue's contract-step "
        "rounding are not modelled; the chain verifier measures the step rounding "
        "separately.",
        "RE-DERIVED INDEPENDENTLY (2026-09-24, outside this file): the seven "
        "computed series above were recomputed from the .pine with plain pandas "
        "-- rolling min/max over low/high for the three Donchian lines, a "
        "first-value-seeded EMA written independently of pine_ta -- and matched "
        "the port's columns exactly on validate_pine's synthetic 1d frame (max "
        "abs difference 0.0, equal_nan). The four condition columns agree on all "
        "3000 bars (954 long-entry, 1153 long-close, 995 short-entry, 1171 "
        "short-close true). Warm-up boundaries measured on that frame: tenkan 8, "
        "kijun 25, span_a 25, chikou 25, span_b 51.",
    ]

    def pine_indicators(self, dataframe, params):
        close = dataframe["close"]
        high = dataframe["high"]
        low = dataframe["low"]
        displacement = int(params["displacement"])

        # TenkanSen = donchian(TenkanSenPeriods) ; KijunSen = donchian(KijunSenPeriods)
        tenkan_sen = _donchian(low, high, int(params["TenkanSenPeriods"]))
        kijun_sen = _donchian(low, high, int(params["KijunSenPeriods"]))
        # SenkouSpanA = avg(TenkanSen, KijunSen) ; SenkouSpanB = donchian(SenkouSpanBPeriods)
        senkou_span_a = ta.pine_avg(tenkan_sen, kijun_sen)
        senkou_span_b = _donchian(low, high, int(params["SenkouSpanBPeriods"]))
        # ChikouSpan = close[displacement-1]
        chikou_span = close.shift(displacement - 1)

        # Sema / Mema are read by the conditions; Lema / XLema are not (see notes).
        sema = ta.pine_ema(close, 13)
        mema = ta.pine_ema(close, 21)
        lema = ta.pine_ema(close, 89)
        xlema = ta.pine_ema(close, 233)

        dataframe["pine_tenkan_sen"] = tenkan_sen
        dataframe["pine_kijun_sen"] = kijun_sen
        dataframe["pine_senkou_span_a"] = senkou_span_a
        dataframe["pine_senkou_span_b"] = senkou_span_b
        dataframe["pine_chikou_span"] = chikou_span
        dataframe["pine_sema"] = sema
        dataframe["pine_mema"] = mema
        dataframe["pine_lema"] = lema
        dataframe["pine_xlema"] = xlema

        # longCondition = close>ChikouSpan and Sema>KijunSen and Sema>Mema and SenkouSpanA>SenkouSpanB
        dataframe["pine_long_condition"] = (
            (close > chikou_span)
            & (sema > kijun_sen)
            & (sema > mema)
            & (senkou_span_a > senkou_span_b)
        )
        # strategy.close("Long", when = (close<KijunSen and close<ChikouSpan and Sema<Mema))
        dataframe["pine_long_close"] = (
            (close < kijun_sen) & (close < chikou_span) & (sema < mema)
        )
        # shortCondition = close<ChikouSpan and Sema<KijunSen and Sema<Mema and SenkouSpanA<SenkouSpanB
        dataframe["pine_short_condition"] = (
            (close < chikou_span)
            & (sema < kijun_sen)
            & (sema < mema)
            & (senkou_span_a < senkou_span_b)
        )
        # strategy.close("Short", when = (close>KijunSen and close>ChikouSpan and Sema>Mema))
        dataframe["pine_short_close"] = (
            (close > kijun_sen) & (close > chikou_span) & (sema > mema)
        )
        return dataframe

    def pine_context(self, dataframe, params):
        del params
        return {
            "long_condition": dataframe["pine_long_condition"].to_numpy(dtype=bool),
            "long_close": dataframe["pine_long_close"].to_numpy(dtype=bool),
            "short_condition": dataframe["pine_short_condition"].to_numpy(dtype=bool),
            "short_close": dataframe["pine_short_close"].to_numpy(dtype=bool),
        }

    def pine_script(self, broker, i, ctx):
        # The written order below is the fill priority and is preserved:
        # Long entry, Long close, Short entry, Short close.
        # strategy.entry("Long", strategy.long, when = longCondition)
        broker.entry("Long", "long", when=bool(ctx["long_condition"][i]))
        # strategy.close("Long", when = (close<KijunSen and close<ChikouSpan and Sema<Mema))
        broker.close("Long", when=bool(ctx["long_close"][i]))
        # strategy.entry("Short", strategy.short, when = shortCondition)
        broker.entry("Short", "short", when=bool(ctx["short_condition"][i]))
        # strategy.close("Short", when = (close>KijunSen and close>ChikouSpan and Sema>Mema))
        broker.close("Short", when=bool(ctx["short_close"][i]))
