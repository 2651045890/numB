"""Port of sources/SM_ee5ff9901362a297.pine (batch_001/Fukuiz-Octa-EMA-Ichimoku.md).

Pine v5 (`//@version=5`). An 8-EMA ribbon plus an Ichimoku, with a conversion
tool's order block appended -- the pattern PINE_SEMANTICS.md 1.17 records:

    fukuiz   = math.avg(ema2, ema8)
    white    = ema2 > ema8
    Tenkan   = middleDonchian(9)      Kijun  = middleDonchian(26)
    SenkouA  = middleDonchian(52)     SenkouB = (Tenkan[26] + Kijun[26]) / 2
    buy2     = white and fukuiz > SenkouA[26] and fukuiz > SenkouB
    sell2    = ema2 < ema8

    if buy2
        strategy.entry("Enter Long", strategy.long)
    else if sell2
        strategy.entry("Enter Short", strategy.short)

`strategy.entry` does not compile inside `indicator()`, so the trading
behaviour of this source is what the appended block does: enter on `buy2` /
`sell2` and NEVER exit. No exit call of any kind exists in the file.

THE APPENDED BLOCK DOES NOT USE THE AUTHOR'S SIGNALS. The file also computes
`buycond` / `sellcond` / `bullish` / `bearish` / `buy` / `sell`, and the md's
prose describes entries in those terms ("Buy = All Ema (color) above the
cloud"), but the appended block calls `buy2` / `sell2` instead. `buy` and
`sell` -- and everything that feeds only them -- are dead code here and are not
reproduced, because they reach no order. Two consequences are worth stating:

* `sell2 = ema2 < ema8` carries NO cloud filter, so once the EMA ribbon is
  bearish the SHORT side fires on its own, including from the very start of the
  frame; `buy2` is the side that waits for the cloud (`SenkouA[26]` is na until
  bar 77 on a full-length frame). The strategy is therefore short-biased at the
  open of any window, which is a property of the appended block, not of the
  author's design.
* `buycond` contains `white[1] == 0` -- a bool compared against the integer 0,
  the PINE_SEMANTICS 1.16 shape. It is inside `buycond`, which reaches only the
  unused `bullish` / `buy`, so it has no effect on trading and is not
  implemented here. It is recorded rather than silently "fixed".

THE DECLARATION IS COMMENTED OUT. The only `strategy(...)` in the file -- with
`process_orders_on_close=true`, `default_qty_type=strategy.cash`,
`default_qty_value=1000`, `initial_capital=10000` and
`commission_value=0.25` -- is commented out, and there is no active
`indicator()` either. Commented-out code places no order and configures
nothing (the same rule that makes a commented-out `strategy.exit` not an exit),
so the source declares NO strategy() at all and Pine's documented defaults
apply: `fixed` / 1 contract, initial capital 1000000, commission 0%,
`pyramiding 0`, `process_orders_on_close=false`. Adopting the commented-out
values instead would restate every result on a sizing basis the running source
never had -- and at `cash` / 1000 on a 10000 initial capital it would also walk
straight into the venue-minimum-stake trap of PINE_SEMANTICS 1.5.1.

FIDELITY:

* Converter-appended order block (PINE_SEMANTICS 1.17): the file's declaration
  is commented out and the trailing if / else-if entry pair is what the tool
  added; the port reproduces that block's actual behaviour.
* NO exit call exists in the source -- not even commented out -- so
  `source_reproduce_stops` is False and a position is only ever ended by the
  opposite entry reversing it.
* MD / SOURCE DISCREPANCY: the md's "How to use" says "or you can use the exit
  setup", and its "Condition" says buy = all EMAs above the cloud, sell = all
  EMAs gray. Neither is what the code does: there is no exit setup anywhere in
  the file, and the appended block keys only on `ema2` vs `ema8` (two of the
  eight EMAs) plus the cloud for the long side. The source is authoritative
  (rule 2); the prose is recorded, not implemented.
* MD / SOURCE DISCREPANCY: the md argument table lists the start/end date
  inputs, and the source defines `start`, `end` and a `period()` function from
  them -- but `period()` is NEVER CALLED, so the date window is inert. It is
  not reproduced (PINE_SEMANTICS 2.8 records that `input.time` window limiting
  is not modelled anyway).
* `middleDonchian` is the source's own: `math.avg(ta.highest(len),
  ta.lowest(len))`, where the single-argument `ta.highest(length)` /
  `ta.lowest(length)` overloads default to `high` / `low`. The port uses
  pine_highest / pine_lowest on those same columns.
* `SenkouB` here is `(Tenkan[26] + Kijun[26]) / 2` -- the author's own variant,
  not the textbook 52-period span shifted forward -- and `SenkouA[26]` is a
  BACKWARD history reference (a past Donchian), not a forward displacement.
  Both are reproduced exactly as written.
* `white` / `gray` are strict inequalities, so an exact `ema2 == ema8` leaves
  both false and the bar can fire neither side.
* An na `SenkouA[26]` / `SenkouB` makes the corresponding comparison false
  (Pine treats na comparisons as false; numpy NaN comparisons are false too),
  which is what holds `buy2` off until bar 77 on a full-length frame.
* `pine_ema` seeds with the first observation and does not advance on na -- a
  modelled choice (PINE_SEMANTICS 3.1), not a certified one. It matters here:
  the EMAs are never na, so the ribbon is defined from bar 0 and `sell2` can
  fire immediately.
* The `showRibbon` / `switch1` / `switch2` / `switch3` inputs, all the `plot` /
  `fill` / colour statements, `ribbonDir`, `xChikou`, `HLcolor`-style colour
  ternaries and the unused `buy` / `sell` chain are display-only and are not
  reproduced. The eight EMA lengths and the four Ichimoku periods ARE inputs
  that reach the entries and are carried in `source_defaults`.
* `/*backtest` declares `period: 10m` on Futures_Binance BTC_USDT, so
  `timeframe` is "10m"; `basePeriod: 1m` is the FMZ backtester's own fill
  granularity, not the strategy's period.
* No `security()` call, no `barstate.isrealtime` branch, no repainting, no
  `strategy.risk.*` rule.
* Leverage, margin, liquidation, funding and the venue's contract-step
  rounding of order quantities are not modelled.
"""
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


class SMFukuizOctaEmaIchimoku_ee5ff9(PinePortBase, IStrategy):
    source_id = "SM_ee5ff9901362a297"
    source_file = "Fukuiz-Octa-EMA-Ichimoku.md"
    timeframe = "10m"
    can_short = True
    source_defaults: dict = {
        "ema1Len": 5,
        "ema2Len": 11,
        "ema3Len": 15,
        "ema4Len": 18,
        "ema5Len": 21,
        "ema6Len": 24,
        "ema7Len": 28,
        "ema8Len": 34,
        "conversionPeriods": 9,
        "basePeriods": 26,
        "laggingSpan2Periods": 52,
        "displacement": 26,
    }
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    source_reproduce_stops = False
    source_fidelity_notes = [
        "Converter-appended order block (PINE_SEMANTICS 1.17): the file's only "
        "declaration is commented out, and the trailing if / else-if entry "
        "pair is what the tool added. The port reproduces that block's actual "
        "behaviour -- enter on buy2 / sell2, never exit.",
        "The source's `//strategy(...)` line is COMMENTED OUT (and there is no "
        "active indicator() either), so it declares no strategy() at all and "
        "Pine's defaults apply: fixed / 1 contract, initial capital 1000000, "
        "commission 0%, pyramiding 0, process_orders_on_close=false. The "
        "commented-out line's process_orders_on_close=true, cash/1000, "
        "initial_capital=10000 and 0.25% commission are NOT adopted -- a "
        "commented-out line configures nothing, by the same rule that makes a "
        "commented-out strategy.exit not an exit.",
        "NO exit call exists in the source, not even commented out, so "
        "source_reproduce_stops is False and a position is only ever ended by "
        "the opposite entry reversing it.",
        "MD / SOURCE DISCREPANCY: the md's 'How to use' mentions an exit setup "
        "and its 'Condition' describes buy/sell in terms of all eight EMAs. "
        "Neither is what the code does -- there is no exit setup, and the "
        "appended block keys on ema2 vs ema8 plus the cloud (long side only).",
        "MD / SOURCE DISCREPANCY: the appended block calls buy2 / sell2, NOT "
        "the author's buy / sell. buycond / sellcond / bullish / bearish / "
        "buy / sell are dead code here and are not reproduced; only buy2 / "
        "sell2 reach an order.",
        "sell2 = ema2 < ema8 has NO cloud filter, so the short side fires on "
        "its own (including early in the frame), while buy2 waits for "
        "SenkouA[26] / SenkouB, which are na until bar 77. That asymmetry is "
        "the appended block's, reproduced as written.",
        "buycond contains `white[1] == 0` -- a bool compared against integer 0, "
        "the PINE_SEMANTICS 1.16 shape. It feeds only the unused bearish / buy "
        "chain, so it places no order and is not implemented; recorded rather "
        "than silently rewritten.",
        "The start/end date inputs and the `period()` function are defined but "
        "period() is NEVER CALLED, so the date window is inert; not reproduced "
        "(PINE_SEMANTICS 2.8).",
        "middleDonchian is reproduced as math.avg(ta.highest(len), "
        "ta.lowest(len)); the single-argument overloads default to high / low.",
        "SenkouB = (Tenkan[26] + Kijun[26]) / 2 is the author's own variant, "
        "and SenkouA[26] is a BACKWARD history reference, not the textbook "
        "forward displacement; both reproduced as written.",
        "white / gray are strict inequalities, so ema2 == ema8 exactly leaves "
        "both false and no side fires.",
        "An na SenkouA[26] / SenkouB makes its comparison false (na "
        "comparisons are false in Pine and NaN comparisons are false in "
        "numpy), which is what holds buy2 off during the warmup.",
        "pine_ema seeds with the first observation (PINE_SEMANTICS 3.1, a "
        "modelled choice); the EMAs are therefore never na and sell2 can fire "
        "from bar 0.",
        "showRibbon / switch1..3, the plot / fill / colour statements, "
        "ribbonDir and xChikou are display-only and are not reproduced. The "
        "eight EMA lengths and the four Ichimoku periods reach the entries and "
        "are carried in source_defaults.",
        "/*backtest declares period: 10m on Futures_Binance BTC_USDT; "
        "basePeriod: 1m is the FMZ backtester's fill granularity, not the "
        "strategy's period.",
        "No security() call, no barstate.isrealtime branch, no repainting, no "
        "strategy.risk.* rule.",
        "Leverage, margin, liquidation, funding and the venue's contract-step "
        "rounding of order quantities are not modelled.",
    ]

    def pine_indicators(self, dataframe, params):
        close = dataframe["close"]
        high = dataframe["high"]
        low = dataframe["low"]

        # f_emaRibbon(close, ema1Len .. ema8Len)
        ema1 = ta.pine_ema(close, int(params["ema1Len"]))
        ema2 = ta.pine_ema(close, int(params["ema2Len"]))
        ema8 = ta.pine_ema(close, int(params["ema8Len"]))

        # Middle Donchian: math.avg(ta.highest(len), ta.lowest(len)).
        def middle_donchian(length):
            upper = ta.pine_highest(high, length)
            lower = ta.pine_lowest(low, length)
            return (upper + lower) / 2.0

        conversion = int(params["conversionPeriods"])
        base_periods = int(params["basePeriods"])
        lagging = int(params["laggingSpan2Periods"])
        displacement = int(params["displacement"])

        tenkan = middle_donchian(conversion)
        kijun = middle_donchian(base_periods)
        senkou_a = middle_donchian(lagging)
        senkou_b = (tenkan.shift(base_periods) + kijun.shift(base_periods)) / 2.0

        # Buy and sell signals -- the two the appended block actually calls.
        fukuiz = (ema2 + ema8) / 2.0
        white = ema2 > ema8
        gray = ema2 < ema8
        cloud_a = senkou_a.shift(displacement)
        buy2 = white & (fukuiz > cloud_a) & (fukuiz > senkou_b)
        sell2 = gray

        dataframe["pine_fukuiz"] = fukuiz
        dataframe["pine_senkou_a"] = senkou_a
        dataframe["pine_senkou_b"] = senkou_b
        dataframe["pine_long_condition"] = buy2.fillna(False).to_numpy()
        dataframe["pine_short_condition"] = sell2.fillna(False).to_numpy()
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "fukuiz": dataframe["pine_fukuiz"].to_numpy(),
            "long_condition": dataframe["pine_long_condition"].to_numpy(),
            "short_condition": dataframe["pine_short_condition"].to_numpy(),
        }

    def pine_script(self, broker, i, ctx):
        # if buy2
        #     strategy.entry("Enter Long", strategy.long)
        # else if sell2
        #     strategy.entry("Enter Short", strategy.short)
        if ctx["long_condition"][i]:
            broker.entry("Enter Long", "long")
        elif ctx["short_condition"][i]:
            broker.entry("Enter Short", "short")
