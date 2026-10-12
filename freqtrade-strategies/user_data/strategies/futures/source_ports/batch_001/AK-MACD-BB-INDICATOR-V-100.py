"""Port of sources/SM_d6b304aeccb3e33f.pine (batch_001/AK-MACD-BB-INDICATOR-V-100.md).

Pine v4. The file declares `study("AK MACD BB v 1.00")`, NOT `strategy(...)`:
the two `strategy.entry` calls at the bottom are an order block APPENDED to the
indicator by the converter site that published it (fmz.com/strategy/366943,
named in the md's Detail link). Pine does not compile `strategy.entry` inside
`study()`, so the "original strategy" is the indicator PLUS that appended
block, and the trading behaviour it defines is entry-only:

    if macd > Upper
        strategy.entry("Enter Long", strategy.long)
    else if macd < Lower
        strategy.entry("Enter Short", strategy.short)

The indicator is Algokid's MACD drawn inside Bollinger Bands of its own value:

    fastMA = ema(close, fastLength)
    slowMA = ema(close, slowLength)
    macd   = fastMA - slowMA
    Std    = stdev(macd, length)
    Upper  = Std * dev + sma(macd, length)
    Lower  = sma(macd, length) - Std * dev

So the orders go long while the MACD line is above the upper band of its own
sma and short while it is below the lower band -- a momentum-breakout reading
of the MACD/BB combination, which is what the two `barcolor` calls highlight.

There is NO exit of any kind in the source -- no `strategy.close`, no
`strategy.exit`, and no commented-out exit line either (only `plot` / `fill` /
`barcolor` calls). A position is therefore only ever left by the opposite
entry, which the engine models as a reversal. `pyramiding` keeps Pine's default
of 0, so a repeated signal while already positioned that way is ignored. The
comment `//needs improvments` at the end of the source precedes the appended
block and is not a statement about the orders.

FIDELITY:

* `signalLength` is declared (`input(9, minval=1)`) but never referenced: the
  source's `macd` is the raw `fastMA - slowMA` line and no signal line is
  computed. The input is kept in `source_defaults` because the source declares
  it, and the port does NOT add a signal line to use it.
* `ema` / `sma` / `stdev` are the v4 BARE builtins (not `ta.`-prefixed) and are
  routed through `pine_ta.pine_ema` / `pine_sma` / `pine_stdev`. `stdev` is
  Pine's population (biased) standard deviation, which `pine_stdev` matches
  with ddof=0.
* The EMA seeding rule is not published by TradingView; `pine_ta.pine_ema`
  documents its modelled choice (first non-na observation seeds the
  recursion). Both EMA lines -- and therefore `macd`, `Std` and both bands --
  inherit that choice (PINE_SEMANTICS.md 3.1).
* `sma` returns na until its window is full and na anywhere in the window
  propagates, so `Upper`/`Lower` are na for the first `length`+`slowLength`
  bars; Pine's comparisons against na are false, so no order is placed there.
  The port keeps that: the two comparisons yield False on na.
* `mc = macd >= Upper ? lime : red` and the two `barcolor(...)` calls are
  display-only; `zeroline`, `Band1`/`Band2` and `fill` likewise. None places an
  order.
* The source declares `study(...)`, so no strategy() properties exist and
  Pine's documented defaults apply: market orders of `fixed` size 1 contract,
  initial capital 1000000, commission 0%, pyramiding 0,
  process_orders_on_close=false.
* The md's argument table renders `v_input_2` (Deviations, source literal `1`)
  as `true`, because the host displays the numeric 1 as a boolean. The source's
  literal is the number 1 and that is what the port carries; no behavioural
  conflict.
* The header's backtest window (2022-04-30 to 2022-05-29) is extraction
  metadata, not an `input.time` filter, so no data is trimmed. Its
  `basePeriod: 5m` is the host's intrabar granularity for filling 45m bars,
  not the strategy's period.
* Leverage, margin, liquidation, funding and the venue's contract-step rounding
  are not modelled (PINE_SEMANTICS.md 1.6 measures the rounding separately).
"""
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


class SMAkMacdBbIndicatorV100_d6b304(PinePortBase, IStrategy):
    source_id = "SM_d6b304aeccb3e33f"
    source_file = "AK-MACD-BB-INDICATOR-V-100.md"
    timeframe = "45m"
    can_short = True
    # Input defaults exactly as written in the source. `signalLength` is
    # declared by the source but never referenced (see FIDELITY).
    source_defaults: dict = {
        "length": 10,
        "dev": 1,
        "fastLength": 12,
        "slowLength": 26,
        "signalLength": 9,
    }
    # The source declares study(...), not strategy(...), so no strategy()
    # properties exist and Pine's documented defaults apply.
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    # No strategy.close / strategy.exit / stop / limit / trail anywhere.
    source_reproduce_stops = False
    source_mintick = 0.1
    source_fidelity_notes = [
        "The file declares study(...), not strategy(...): the strategy.entry "
        "pair at the bottom is an order block appended by the converter site "
        "(fmz.com/strategy/366943 per the md's Detail link). The port "
        "reproduces the indicator PLUS that appended block, i.e. entry-only "
        "behaviour.",
        "The appended block tests the bare comparisons `macd > Upper` / "
        "`macd < Lower`; they are mutually exclusive (Upper > Lower whenever "
        "the stdev window is defined), so `else if` / `elif` preserves Pine's "
        "'place only the long order' behaviour.",
        "signalLength is declared as input(9, minval=1) but is referenced "
        "NOWHERE in the source: macd is the raw fastMA - slowMA line and no "
        "signal line is computed. The input is declared in source_defaults "
        "because the source declares it, and the port does NOT add a signal "
        "line to make use of it.",
        "ema / sma / stdev are the v4 BARE builtins and are routed through "
        "pine_ta.pine_ema / pine_sma / pine_stdev. stdev is Pine's population "
        "(biased) standard deviation, which pine_stdev matches with ddof=0.",
        "TradingView does not publish its EMA seeding rule; pine_ta.pine_ema "
        "documents the modelled choice (the first non-na observation seeds the "
        "recursion). macd, Std and both bands inherit that unverified choice "
        "(PINE_SEMANTICS.md 3.1).",
        "sma returns na until its window is full and na anywhere in the window "
        "propagates, so Upper/Lower are na for the warmup and the comparisons "
        "against them are false there -- no order is placed, matching Pine's "
        "na-in-a-boolean-context rule.",
        "mc, the two barcolor calls, zeroline, Band1/Band2 and fill are "
        "display-only and place no order.",
        "The source has no exit of any kind: no strategy.close, no "
        "strategy.exit, no stop or limit order, and no commented-out exit "
        "line. A position is only left by the opposite entry, which the engine "
        "models as a reverse fill. source_reproduce_stops is False "
        "accordingly.",
        "The source declares study(...), so no strategy() properties exist and "
        "Pine's documented defaults are used: default_qty_type fixed, "
        "default_qty_value 1, commission 0%, pyramiding 0, initial capital "
        "1000000 USD.",
        "The md's argument table renders v_input_2 (Deviations, source literal "
        "1) as true because the host displays the numeric 1 as a boolean; the "
        "source's literal is the number 1 and that is what the port carries. "
        "The md's embedded source block is verbatim identical to the .pine "
        "source.",
        "The source's final comment '//needs improvments' sits just before the "
        "appended block and is the indicator author's note, not a statement "
        "about the orders.",
        "The header's backtest window is extraction metadata, not an "
        "input.time filter, so the port runs on whatever range the caller "
        "supplies; basePeriod: 5m is the host's intrabar fill granularity, not "
        "the strategy's period.",
        "Leverage, margin, liquidation, funding and the venue's contract-step "
        "rounding are not modelled (PINE_SEMANTICS.md 1.6).",
    ]

    def pine_indicators(self, dataframe, params):
        close = dataframe["close"]
        # fastMA = ema(close, fastLength); slowMA = ema(close, slowLength)
        fast_ma = ta.pine_ema(close, int(params["fastLength"]))
        slow_ma = ta.pine_ema(close, int(params["slowLength"]))
        # macd = fastMA - slowMA  (no signal line: signalLength is unused)
        macd = fast_ma - slow_ma

        length = int(params["length"])
        deviations = float(params["dev"])
        # Std = stdev(macd, length)
        std = ta.pine_stdev(macd, length)
        basis = ta.pine_sma(macd, length)
        # Upper = Std*dev + sma(macd, length); Lower = sma(macd, length) - Std*dev
        upper = std * deviations + basis
        lower = basis - std * deviations

        dataframe["pine_fast_ma"] = fast_ma
        dataframe["pine_slow_ma"] = slow_ma
        dataframe["pine_macd"] = macd
        dataframe["pine_std"] = std
        dataframe["pine_upper"] = upper
        dataframe["pine_lower"] = lower
        # if macd > Upper / else if macd < Lower
        dataframe["pine_long_condition"] = (macd > upper).fillna(False)
        dataframe["pine_short_condition"] = (macd < lower).fillna(False)
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "macd": dataframe["pine_macd"].to_numpy(),
            "upper": dataframe["pine_upper"].to_numpy(),
            "lower": dataframe["pine_lower"].to_numpy(),
            "long_condition": dataframe["pine_long_condition"].to_numpy(),
            "short_condition": dataframe["pine_short_condition"].to_numpy(),
        }

    def pine_script(self, broker, i, ctx):
        # if macd > Upper
        #     strategy.entry("Enter Long", strategy.long)
        # else if macd < Lower
        #     strategy.entry("Enter Short", strategy.short)
        if ctx["long_condition"][i]:
            broker.entry("Enter Long", "long")
        elif ctx["short_condition"][i]:
            broker.entry("Enter Short", "short")
