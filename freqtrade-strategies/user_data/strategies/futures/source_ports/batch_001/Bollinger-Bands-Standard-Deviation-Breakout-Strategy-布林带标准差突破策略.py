"""Port of sources/SM_20d281a98a67c687.pine
(batch_001/Bollinger-Bands-Standard-Deviation-Breakout-Strategy-布林带标准差突破策略.md).

Pine v5 "Bollinger Bands" (Madrid, 2014-09-14), used as a breakout system: the
1st standard-deviation band arms the entries and the basis closes them.

    basis  = ta.sma(src, length)
    dev    = ta.stdev(src, length)
    upper1 = basis + dev
    lower1 = basis - dev

    long_condition  = ta.crossover(close, upper1)
    short_condition = ta.crossunder(close, lower1)

    if long_condition
        strategy.entry("Long", strategy.long)
    if short_condition
        strategy.entry("Short", strategy.short)

    exit_long_condition  = ta.crossunder(close, basis)
    exit_short_condition = ta.crossover(close, basis)

    if exit_long_condition
        strategy.close("Long")
    if exit_short_condition
        strategy.close("Short")

`strategy()` declares only `title` / `shorttitle` / `overlay`, so every property
is Pine's documented default: `strategy.fixed` / 1 contract, initial capital
1000000, commission 0%, pyramiding 0, `process_orders_on_close=false`. The
`/*backtest` header declares `period: 1h` on Futures_Binance BTC_USDT, so
`timeframe` is "1h"; `basePeriod: 15m` is the FMZ backtester's own granularity
for filling 1h bars, not the strategy's period.

THE CALL ORDER IS THE SOURCE'S: both entries are issued before both closes, and
the engine fills a bar's pending orders in that creation order. The port issues
`entry("Long")`, `entry("Short")`, `close("Long")`, `close("Short")` in exactly
that sequence. In practice a same-bar entry-then-close cannot happen -- an entry
needs `close > upper1` while its close needs `close < basis`, and an entry in
one direction excludes the close of the other -- so the ordering is carried for
fidelity rather than because a bar exercises it.

`strategy.close("Long")` names an ENTRY id; the port passes it through as
`broker.close("Long")`, which matches the `Long` / `Short` entry ids the engine
records, and is a no-op when that entry is not open (PINE_SEMANTICS.md 1.12).

FIDELITY:

* `src` is `input(close)`, i.e. the default `close`, and is used for the basis
  and the deviation. `long_condition` / `short_condition` compare `close`
  against the bands; with the default source the two series coincide, but the
  port keeps them distinct so an override of `src` behaves as the source would.
* Only the 1st-deviation bands (`upper1` / `lower1`) drive orders. `upper2` /
  `lower2` and the `fill()` calls are display-only and are not reproduced.
* `ta.stdev` is Pine's population standard deviation (the default `biased=true`,
  divide by N), which is what `pine_ta.pine_stdev` computes (ddof=0).
* `ta.crossover` / `ta.crossunder` are `a > b and a[1] <= b[1]` /
  `a < b and a[1] >= b[1]`, including the `<=` on the previous bar -- the port
  uses `pine_crossover` / `pine_crossunder` rather than a strict two-bar
  comparison, which would drop the bars that open ON the band.
* na handling is Pine's: comparisons against na are false, and `sma` / `stdev`
  are na until their window fills, so no signal can exist before bar `length`
  and `pine_crossover` returns na-as-false over that stretch.
* md vs code (recorded, code followed): the md's prose describes a
  two-standard-deviation breakout system with "re-entry on a second touch" and
  a "stop" that never appears in the code. The code's entries fire on a
  ONE-deviation band crossing and its only exits are the basis crossings.
* md vs code (recorded, code followed): the md's argument table lists
  `v_input_1_close = 0` for `src`, but the source declares `input(close)`, i.e.
  the close series. The source wins.
* md vs code (recorded): the md does not mention that the exits are
  `strategy.close` on the named entry (so a long is closed by a basis cross
  DOWN, which is also the condition that would open nothing) rather than a
  reversal through `strategy.entry`.
* There is no stop / limit / trail / `strategy.exit` anywhere, so
  `source_reproduce_stops` is False.
* `can_short` is True: the source has a real `strategy.entry("Short",
  strategy.short)`.
* Leverage, margin, liquidation, funding, `request.security` and the venue's
  contract-step rounding are not modelled.
"""
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


class SMBollingerBandsStdDev_20d281(PinePortBase, IStrategy):
    source_id = "SM_20d281a98a67c687"
    source_file = (
        "Bollinger-Bands-Standard-Deviation-Breakout-Strategy-布林带标准差突破策略.md"
    )
    timeframe = "1h"
    can_short = True
    # input() defaults: `src` is `input(close)` and is resolved through
    # pine_ta.pine_source so an override picks another OHLCV-derived series the
    # way the input's dropdown does; `length` is input.int(20), `mult` is
    # input.float(2.0).
    source_defaults: dict = {"src": "close", "length": 20, "mult": 2.0}
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    source_reproduce_stops = False
    source_fidelity_notes = [
        "The four strategy calls are issued in the source's order: entry Long, "
        "entry Short, close Long, close Short. A same-bar entry-then-close is "
        "structurally impossible here (an entry needs close beyond the "
        "1st-deviation band while its close needs close beyond the basis in the "
        "other direction), so the order is carried for fidelity.",
        "strategy.close(\"Long\") / (\"Short\") name ENTRY ids; the port passes "
        "them through to broker.close, which is a no-op when that entry is not "
        "open (PINE_SEMANTICS.md 1.12).",
        "ta.stdev is Pine's population standard deviation (biased=true, "
        "divide by N); pine_ta.pine_stdev uses ddof=0.",
        "ta.crossover / ta.crossunder are reproduced with pine_crossover / "
        "pine_crossunder, which include the `<=` / `>=` on the previous bar, so "
        "a bar that opens exactly ON the band still counts as a cross.",
        "Only the 1st-deviation bands (upper1 / lower1) drive orders; upper2 / "
        "lower2 and the fill() calls are display-only.",
        "`src` is input(close) and is resolved through pine_ta.pine_source, so "
        "an override selects another OHLCV-derived series. The basis and "
        "deviation use `src` while the entry/exit conditions compare `close` -- "
        "with the default they are the same series, but the port keeps them "
        "distinct so an override behaves as the source would.",
        "source_reproduce_stops is False: there is no strategy.exit / stop / "
        "limit / trail, only strategy.close on the basis crossings.",
        "md vs code (recorded, code followed): the md describes the bands as "
        "'the middle band plus or minus a certain multiple of the standard "
        "deviation' (and lists Multiplier = 2), but the ORDERS use upper1 / "
        "lower1 -- the +/-ONE standard-deviation bands. upper2 / lower2 and the "
        "fill() calls are plot-only. The code is followed.",
        "md vs code (recorded, code followed): the md's argument table shows "
        "v_input_1_close = 0 for src; the source declares input(close).",
        "md vs code (recorded): the md describes the exits by condition only; it "
        "does not say they are issued as strategy.close on the NAMED entry, so a "
        "basis cross closes only the entry of that name and not a position that "
        "carries the other one.",
        "Leverage, margin, liquidation, funding, request.security and "
        "contract-step rounding are not modelled.",
    ]

    def pine_indicators(self, dataframe, params):
        close = dataframe["close"]
        src = ta.pine_source(dataframe, str(params["src"]))  # input(close)
        length = int(params["length"])

        basis = ta.pine_sma(src, length)
        dev = ta.pine_stdev(src, length)
        upper1 = basis + dev
        lower1 = basis - dev

        dataframe["pine_basis"] = basis
        dataframe["pine_upper1"] = upper1
        dataframe["pine_lower1"] = lower1
        dataframe["pine_long_condition"] = ta.pine_crossover(close, upper1)
        dataframe["pine_short_condition"] = ta.pine_crossunder(close, lower1)
        dataframe["pine_exit_long_condition"] = ta.pine_crossunder(close, basis)
        dataframe["pine_exit_short_condition"] = ta.pine_crossover(close, basis)
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "long_condition": dataframe["pine_long_condition"].to_numpy(dtype=bool),
            "short_condition": dataframe["pine_short_condition"].to_numpy(dtype=bool),
            "exit_long_condition": dataframe[
                "pine_exit_long_condition"
            ].to_numpy(dtype=bool),
            "exit_short_condition": dataframe[
                "pine_exit_short_condition"
            ].to_numpy(dtype=bool),
        }

    def pine_script(self, broker, i, ctx):
        # if (long_condition)
        #     strategy.entry("Long", strategy.long)
        if ctx["long_condition"][i]:
            broker.entry("Long", "long")
        # if (short_condition)
        #     strategy.entry("Short", strategy.short)
        if ctx["short_condition"][i]:
            broker.entry("Short", "short")
        # if (exit_long_condition)
        #     strategy.close("Long")
        if ctx["exit_long_condition"][i]:
            broker.close("Long")
        # if (exit_short_condition)
        #     strategy.close("Short")
        if ctx["exit_short_condition"][i]:
            broker.close("Short")
