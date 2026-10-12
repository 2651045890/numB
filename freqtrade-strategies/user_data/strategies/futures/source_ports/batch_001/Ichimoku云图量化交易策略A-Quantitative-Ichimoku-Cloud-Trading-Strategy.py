"""Port of sources/SM_7dfe079f8297b167.pine (batch_001/Ichimoku云图量化交易策略A-Quantitative-Ichimoku-Cloud-Trading-Strategy.md).

Pine v3. The standard Ichimoku cloud, with six entry rules that pair the base
line, the conversion line and price against the displaced cloud edges:

    donchian(len) => avg(lowest(len), highest(len))
    conversionLine = donchian(9)
    baseLine       = donchian(26)
    leadLine1      = avg(conversionLine, baseLine)
    leadLine2      = donchian(52)
    maxlead = max(leadLine1, leadLine2)
    minlead = min(leadLine1, leadLine2)

    A = baseLine > maxlead[26]          B = crossover(baseLine, maxlead[26])
    C = baseLine < minlead[26]          D = crossunder(baseLine, minlead[26])
    E = conversionLine > maxlead[26]    F = crossover(conversionLine, maxlead[26])
    G = conversionLine < minlead[26]    H = crossunder(conversionLine, minlead[26])
    I = close > maxlead[52]             J = crossover(close, maxlead[52])
    K = close < minlead[52]             L = crossunder(close, minlead[52])

    if A and E: strategy.entry("Buy",  strategy.long,  when = J)
    if A and I: strategy.entry("Buy",  strategy.long,  when = F)
    if E and I: strategy.entry("Buy",  strategy.long,  when = B)
    if C and G: strategy.entry("Sell", strategy.short, when = L)
    if C and K: strategy.entry("Sell", strategy.short, when = H)
    if G and K: strategy.entry("Sell", strategy.short, when = D)

`strategy()` declares `default_qty_type = strategy.cash`,
`default_qty_value = 100000` and `initial_capital = 100000`; the rest is Pine's
documented default (commission 0%, pyramiding 0, process_orders_on_close false).
No `qty=` is passed, so the 100000-cash default sizes every entry.

FIDELITY -- what is preserved and what is a modelling choice:

* `donchian(len) => avg(lowest(len), highest(len))` uses the v3 one-argument
  forms of `lowest` / `highest`, whose source defaults to the bar's `low` /
  `high`. That is the Donchian channel the conversion and base lines are defined
  on, and it is what the port computes: `lowest(low, len)` / `highest(high, len)`.
* The cloud comparisons use HISTORY references (`maxlead[displacement]`,
  `maxlead[2 * displacement]`), not the `offset=displacement` of the two `plot`
  calls. The offsets are display-only; the shifts are reproduced with `.shift()`.
* All six entries share the id "Buy" / "Sell" and are emitted in the SOURCE's
  order, each keeping its own nested `if A` / `if E` gate and its own `when=`
  cross. More than one of the three long rules can be true on one bar; they are
  left as three separate calls rather than merged into one condition, so the
  order the engine places them in is the source's.
* `pyramiding` is not declared, so it is Pine's default 0: a same-direction
  entry while a position is already open is ignored, and there is no `qty=`
  anywhere, so every entry is the 100000-cash default.
* There is NO exit call of any kind in the source -- no `strategy.close`, no
  `strategy.exit`. A position is only ever reversed by an opposite entry, so
  `source_reproduce_stops` is False and a position still open at the end of the
  window stays open.
* `plot` / `fill` / the two cloud plots are display-only and place no order.
* `currency = currency.USD` is not modelled: pine_engine has no exchange rate
  and keeps the account in the venue's quote currency. Relative behaviour is
  unchanged; the currency translation is not reproduced.
* The md PROSE describes the Ichimoku rules in general terms ("云图上下突破")
  and does not restate the six code rules; nothing in it contradicts the code,
  so there is no md-vs-code difference to record beyond that.
* The `/*backtest` header's `basePeriod: 15m` is the FMZ backtester's own
  granularity for filling the 1h bars, not the strategy's period.
* Leverage, margin, liquidation, funding and the venue's contract-step rounding
  are not modelled; the chain verifier measures the last of those separately.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


def _donchian(dataframe: pd.DataFrame, length: int) -> pd.Series:
    """`donchian(len) => avg(lowest(len), highest(len))` on low/high."""
    return ta.pine_avg(
        ta.pine_lowest(dataframe["low"], length),
        ta.pine_highest(dataframe["high"], length),
    )


class SMIchimokuCloud_7dfe07(PinePortBase, IStrategy):
    source_id = "SM_7dfe079f8297b167"
    source_file = "Ichimoku云图量化交易策略A-Quantitative-Ichimoku-Cloud-Trading-Strategy.md"
    timeframe = "1h"
    can_short = True
    source_defaults: dict = {
        "conversionPeriods": 9,
        "basePeriods": 26,
        "laggingSpan2Periods": 52,
        "displacement": 26,
    }
    source_qty_type = "cash"
    source_qty_value = 100000.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 100000.0
    source_reproduce_stops = False
    source_fidelity_notes = [
        "`lowest(len)` / `highest(len)` are v3's one-argument forms, whose "
        "source defaults to the bar's low / high; the port computes "
        "lowest(low, len) and highest(high, len), i.e. a Donchian channel.",
        "The cloud comparisons use history references (maxlead[displacement] and "
        "maxlead[2 * displacement]), reproduced with .shift(); the plots' "
        "`offset = displacement` is display-only and is not a shift of the data.",
        "All six entries keep the source's nested `if` gates, their own `when=` "
        "cross and the source's order; several can be true on one bar and they "
        "are not merged into one condition.",
        "There is no exit call at all -- no strategy.close and no strategy.exit "
        "-- so a position is closed only by an opposite entry reversing it, "
        "source_reproduce_stops is False, and a position open at the end of the "
        "window stays open.",
        "pyramiding is not declared, so it is Pine's default 0: a repeat entry "
        "in a direction already open is ignored.",
        "No `qty=` is passed anywhere, so every entry is sized by the declared "
        "`strategy.cash` / 100000 default.",
        "`currency = currency.USD` is not modelled; the engine keeps the account "
        "in the venue's quote currency.",
        "plot / fill / the cloud plots are display-only.",
        "The /*backtest header's `basePeriod: 15m` is the FMZ backtester's own "
        "filling granularity, not the strategy's period.",
        "Leverage, margin, liquidation, funding and venue contract-step rounding "
        "are not modelled; the chain verifier measures the last separately.",
    ]

    def pine_indicators(self, dataframe, params):
        conversion_periods = int(params["conversionPeriods"])
        base_periods = int(params["basePeriods"])
        lagging2_periods = int(params["laggingSpan2Periods"])
        displacement = int(params["displacement"])

        conversion_line = _donchian(dataframe, conversion_periods)
        base_line = _donchian(dataframe, base_periods)
        lead_line1 = ta.pine_avg(conversion_line, base_line)
        lead_line2 = _donchian(dataframe, lagging2_periods)
        max_lead = ta.pine_max(lead_line1, lead_line2)
        min_lead = ta.pine_min(lead_line1, lead_line2)

        max_lead_displaced = max_lead.shift(displacement)
        min_lead_displaced = min_lead.shift(displacement)
        max_lead_2x = max_lead.shift(2 * displacement)
        min_lead_2x = min_lead.shift(2 * displacement)
        close = dataframe["close"]

        a = base_line > max_lead_displaced
        b = ta.pine_crossover(base_line, max_lead_displaced)
        c = base_line < min_lead_displaced
        d = ta.pine_crossunder(base_line, min_lead_displaced)
        e = conversion_line > max_lead_displaced
        f = ta.pine_crossover(conversion_line, max_lead_displaced)
        g = conversion_line < min_lead_displaced
        h = ta.pine_crossunder(conversion_line, min_lead_displaced)
        i_ = close > max_lead_2x
        j = ta.pine_crossover(close, max_lead_2x)
        k = close < min_lead_2x
        l_ = ta.pine_crossunder(close, min_lead_2x)

        dataframe["pine_conversion_line"] = conversion_line
        dataframe["pine_base_line"] = base_line
        dataframe["pine_lead_line1"] = lead_line1
        dataframe["pine_lead_line2"] = lead_line2
        dataframe["pine_a"] = a
        dataframe["pine_b"] = b
        dataframe["pine_c"] = c
        dataframe["pine_d"] = d
        dataframe["pine_e"] = e
        dataframe["pine_f"] = f
        dataframe["pine_g"] = g
        dataframe["pine_h"] = h
        dataframe["pine_i"] = i_
        dataframe["pine_j"] = j
        dataframe["pine_k"] = k
        dataframe["pine_l"] = l_
        return dataframe

    def pine_context(self, dataframe, params):
        flags = ("a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l")
        return {
            name: dataframe[f"pine_{name}"].to_numpy(dtype=bool)
            for name in flags
        }

    def pine_script(self, broker, i, ctx):
        a, b, c, d = (ctx[n][i] for n in ("a", "b", "c", "d"))
        e, f, g, h = (ctx[n][i] for n in ("e", "f", "g", "h"))
        i_flag, j, k, l = (ctx[n][i] for n in ("i", "j", "k", "l"))

        # if A
        #     if E
        #         strategy.entry("Buy", strategy.long, when= J)
        if a and e:
            broker.entry("Buy", "long", when=bool(j))
        # if A
        #     if I
        #         strategy.entry("Buy", strategy.long, when= F)
        if a and i_flag:
            broker.entry("Buy", "long", when=bool(f))
        # if E
        #     if I
        #         strategy.entry("Buy", strategy.long, when= B)
        if e and i_flag:
            broker.entry("Buy", "long", when=bool(b))

        # if C
        #     if G
        #         strategy.entry("Sell", strategy.short, when=L)
        if c and g:
            broker.entry("Sell", "short", when=bool(l))
        # if C
        #     if K
        #         strategy.entry("Sell", strategy.short, when=H)
        if c and k:
            broker.entry("Sell", "short", when=bool(h))
        # if G
        #     if K
        #         strategy.entry("Sell", strategy.short, when=D)
        if g and k:
            broker.entry("Sell", "short", when=bool(d))
