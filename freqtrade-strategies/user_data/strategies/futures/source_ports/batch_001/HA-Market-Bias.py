"""Port of sources/SM_633c03fe598de8e6.pine (batch_001/HA-Market-Bias.md).

Pine v5. The file declares `indicator(...)`, NOT `strategy(...)`: the
`if o2 > c2 / else if o2 < c2` block at the bottom is an order block APPENDED to
the indicator by the converter site that published it (the md's Detail link
names fmz.com/strategy/361996). Pine v5 does not compile `strategy.entry` inside
`indicator()`, so the "original strategy" is the indicator PLUS that appended
block, and the trading behaviour it defines is entry-only.

The appended block reads exactly two series, the two smoothed Heikin-Ashi
"candle" edges:

    o  = ta.ema(open,  ha_len)        c  = ta.ema(close, ha_len)
    h  = ta.ema(high,  ha_len)        l  = ta.ema(low,   ha_len)
    haclose  = (o + h + l + c) / 4
    xhaopen  = (o + c) / 2
    haopen   = na(xhaopen[1]) ? (o + c) / 2 : (xhaopen[1] + haclose[1]) / 2
    o2 = ta.ema(haopen,  ha_len2)
    c2 = ta.ema(haclose, ha_len2)

    if o2 > c2
        strategy.entry("Enter Long", strategy.long)
    else if o2 < c2
        strategy.entry("Enter Short", strategy.short)

`haopen` LOOKS recursive but is not: both of its branches feed off `xhaopen` and
`haclose`, neither of which reads `haopen`. Only the first bar takes the
`(o + c) / 2` branch (on bar 0 `xhaopen[1]` is na), and every later bar is
`(xhaopen[1] + haclose[1]) / 2`. The port reproduces exactly that.

The threshold is an inequality between two EMAs of the same three-hundred-bar
smoothed HA series, so on nearly every bar after warm-up one of the two branches
fires; with `pyramiding` at Pine's default 0 a repeat in the direction already
held is ignored, so the source behaves as a continuous flip between long and
short rather than as an occasional signal.

There is NO exit of any kind in the source -- no `strategy.close`, no
`strategy.exit`, not even a commented-out one. A position is only ever left by
the opposite entry, which the engine models as a reversal.

FIDELITY:

* `ha_htf` is the empty string, so every `tf(ha_htf, expr, 0)` call is
  `request.security(syminfo.tickerid, '', expr)` -- the symbol and resolution of
  the chart itself. That resolves to the same bar of the same series, so the
  wrapper is the IDENTITY here and the port drops it. This is a MODELLED choice:
  the engine does not resample and `request.security` is not modelled
  (PINE_SEMANTICS.md, section 2 item 1), but with the chart's own symbol and
  resolution no resampling is being asked for. The `gaps_on == 0` argument
  selects the first of the function's three branches, which is the one that
  leaves gaps and lookahead at their defaults; it does not change the
  resolution. If the host resolved an empty resolution to na instead, every
  branch below would be na and the source would place no orders at all -- the
  identity reading is the only one under which the source trades, and it is what
  the md's published backtest implies.
* `o2 > c2` / `o2 < c2` are plain float comparisons, so there is no
  integer-truthiness question in the appended block and no `? -1 : 0` form in
  the source.
* `osc_bias`, `osc_smooth`, `sigcolor`, `ha_avg`, `h2`, `l2` and `col` are
  computed by the source but no order call reads them: they feed the colouring
  and the three hidden `display=display.none` plots. `hahigh` / `halow` exist
  only to feed `h2` / `l2`. The port computes only the series the order block
  reads (o, c, h, l, haclose, xhaopen, haopen, o2, c2).
* `ta.ema` is seeded with the first non-na observation (pine_ta's documented
  choice); TradingView does not publish its seeding rule, so the early values of
  all nine EMA chains -- and therefore the first flip -- are a MODELLED result
  (PINE_SEMANTICS.md 3.1). It compounds here: `o`, `c`, `h`, `l` are EMAs, and
  `o2` / `c2` are EMAs OF those, so a seeding difference in the first stage
  propagates into the second.
* The source declares `indicator(...)`, not `strategy(...)`, so Pine's
  documented defaults are what the `source_*` attributes record (fixed size 1,
  0% commission, pyramiding 0, initial capital 1000000).
* No stop, limit or trail exit exists, so `source_reproduce_stops` is False.
* Leverage, margin, liquidation, funding and the venue's contract-step rounding
  are not modelled (PINE_SEMANTICS.md 1.6, 2.4).
"""
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


class SMHaMarketBias_633c03(PinePortBase, IStrategy):
    source_id = "SM_633c03fe598de8e6"
    source_file = "HA-Market-Bias.md"
    timeframe = "10m"
    can_short = True
    # As written in the source, in source order. `osc_len` is declared and used
    # only by the oscillator, which no order call reads.
    source_defaults: dict = {
        "show_ha": True,
        "ha_len": 100,
        "ha_len2": 100,
        "osc_len": 7,
    }
    # indicator(...), not strategy(...): Pine's documented defaults apply.
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    # No strategy.close / strategy.exit / stop / limit / trail anywhere.
    source_reproduce_stops = False
    source_mintick = 0.1
    source_fidelity_notes = [
        "The file declares indicator(...), not strategy(...); the strategy.entry "
        "pair at the bottom is an order block appended to the indicator by the "
        "converter site that published it (the md's Detail link names "
        "fmz.com/strategy/361996). The original strategy is the indicator plus "
        "that appended block, and its trading behaviour is entry-only.",
        "The source has no exit of any kind: no strategy.close, no strategy.exit, "
        "no stop or limit order, and no commented-out exit line. A position is "
        "only ever left by the opposite entry, which the engine models as a "
        "reverse fill. source_reproduce_stops is False accordingly.",
        "ha_htf is the empty string, so every tf(ha_htf, expr, 0) call is "
        "request.security(syminfo.tickerid, '', expr): the chart's own symbol at "
        "the chart's own resolution. That is the current bar of the current "
        "series, so the wrapper is treated as the identity and dropped. "
        "request.security is not modelled by the engine (PINE_SEMANTICS.md "
        "section 2 item 1), but no resampling is being requested here, so nothing "
        "is lost. If the host instead resolved an empty resolution to na, every "
        "downstream series would be na and the source would place no orders -- "
        "the identity reading is the only one under which the published backtest "
        "trades, but it remains a modelled choice, not a verified one.",
        "haopen is not actually recursive: both branches read xhaopen and haclose, "
        "neither of which reads haopen. Only bar 0 takes the (o + c) / 2 branch "
        "(xhaopen[1] is na there); every later bar is (xhaopen[1] + haclose[1]) / "
        "2. The port reproduces that na test with a shift-and-mask, so the "
        "warm-up bar lands on the same value.",
        "ta.ema is seeded with the first non-na observation, pine_ta's documented "
        "choice; TradingView does not publish its seeding rule, so the early "
        "values of all nine EMA chains -- and therefore the first flip -- are a "
        "modelled result rather than certified equivalence (PINE_SEMANTICS.md "
        "3.1). It compounds here: o/c/h/l are EMAs, and o2/c2 are EMAs OF those.",
        "osc_bias, osc_smooth, sigcolor, ha_avg, h2, l2 and col are computed by "
        "the source but no order call reads them (they feed the colouring and the "
        "three hidden display=display.none plots); hahigh/halow exist only to "
        "feed h2/l2. The port computes only the series the order block reads.",
        "o2 and c2 are plain floats, so the appended block raises no "
        "integer-truthiness question and the source contains no `? -1 : 0` form.",
        "The source declares indicator(...), not strategy(...), so no strategy() "
        "properties exist and Pine's documented defaults are used: "
        "default_qty_type fixed, default_qty_value 1, commission 0%, pyramiding "
        "0, initial capital 1000000 USD.",
        "The header declares period: 10m with basePeriod: 1m (intrabar data). The "
        "engine evaluates at bar close and fills at the next open, so intrabar "
        "path differences are not modelled.",
        "The backtest window in the header (2022-04-08 to 2022-05-07) is "
        "extraction metadata, not an input.time filter, so the port runs on "
        "whatever range the caller supplies.",
        "Leverage, margin, liquidation, funding and the venue's contract-step "
        "rounding are not modelled; the chain verifier measures the rounding "
        "separately (PINE_SEMANTICS.md 1.6).",
    ]

    def pine_indicators(self, dataframe, params):
        ha_len = int(params["ha_len"])
        ha_len2 = int(params["ha_len2"])
        # o = ta.ema(open, ha_len)   c = ta.ema(close, ha_len)
        # h = ta.ema(high, ha_len)   l = ta.ema(low,   ha_len)
        o = ta.pine_ema(dataframe["open"], ha_len)
        c = ta.pine_ema(dataframe["close"], ha_len)
        h = ta.pine_ema(dataframe["high"], ha_len)
        l = ta.pine_ema(dataframe["low"], ha_len)
        # haclose = tf(ha_htf, (o + h + l + c) / 4, 0)   -> identity (see docstring)
        haclose = (o + h + l + c) / 4.0
        # xhaopen = tf(ha_htf, (o + c) / 2, 0)           -> identity
        xhaopen = (o + c) / 2.0
        # haopen = na(xhaopen[1]) ? (o + c) / 2 : (xhaopen[1] + haclose[1]) / 2
        haopen = xhaopen.copy(deep=True)
        carried = xhaopen.shift(1)
        haopen[carried.notna()] = (
            carried[carried.notna()] + haclose.shift(1)[carried.notna()]
        ) / 2.0
        # o2 = tf(ha_htf, ta.ema(haopen,  ha_len2), 0)   -> identity
        # c2 = tf(ha_htf, ta.ema(haclose, ha_len2), 0)   -> identity
        o2 = ta.pine_ema(haopen, ha_len2)
        c2 = ta.pine_ema(haclose, ha_len2)
        dataframe["pine_haopen"] = haopen
        dataframe["pine_haclose"] = haclose
        dataframe["pine_o2"] = o2
        dataframe["pine_c2"] = c2
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "o2": dataframe["pine_o2"].to_numpy(),
            "c2": dataframe["pine_c2"].to_numpy(),
        }

    def pine_script(self, broker, i, ctx):
        # if o2 > c2
        #     strategy.entry("Enter Long", strategy.long)
        # else if o2 < c2
        #     strategy.entry("Enter Short", strategy.short)
        o2 = ctx["o2"][i]
        c2 = ctx["c2"][i]
        if o2 > c2:
            broker.entry("Enter Long", "long")
        elif o2 < c2:
            broker.entry("Enter Short", "short")
