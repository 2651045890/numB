"""Port of sources/SM_770f77e7cb60b335.pine (batch_001/Bollinger-Bands-EMA-9.md).

Pine v5. A long-only Bollinger-band mean-reversion entry filtered out by a
9-period EMA:

    ema9  = ta.ema(close, 9)
    basis = ta.sma(src, 20)
    dev   = 2.0 * ta.stdev(src, 20)
    upper = basis + dev
    lower = basis - dev

    Exit = close >= ema9
    Long = (close[1] < lower)
    strategy.entry("Long", strategy.long, 1, when = Long)
    strategy.close("Long", when = Exit)

The entry asks whether the PREVIOUS close was below the lower band while `lower`
is the CURRENT bar's lower band -- `close[1] < lower`, not `close[1] < lower[1]`
and not `close < lower`. It is reproduced literally. Both calls are written
unconditionally and in this order (entry first, then close), and both read the
bar's own close, so the conditions may hold together on one bar.

`strategy("Bollinger Bands + EMA 9", overlay=true)` is called with a title and
`overlay` and nothing else, so every property is Pine's documented default:
`strategy.fixed` / 1 contract per entry, commission 0%,
`process_orders_on_close=false`, pyramiding 0, initial capital 1000000. The
explicit `qty=1` on the entry is the same quantity the default supplies.

The `/*backtest` header declares `period: 1d` on Futures_Binance BTC_USDT, so
`timeframe` is "1d"; its `basePeriod: 1h` is the FMZ backtester's own
granularity for filling those daily bars, not the strategy's period.

FIDELITY:

* Only `strategy.entry("Long", ...)` is ever called, so `can_short` is False.
* No stop / limit / profit / loss / trail exit exists anywhere in the source --
  the only exit is `strategy.close("Long", when = Exit)` -- so
  `source_reproduce_stops` is False and a position open at the end of the window
  stays open.
* The md's prose quotes the entry as `strategy.entry("Long",strategy.long, 1000,
  when =Long)` and the close as `strategy.close("Long", when=add)`. The code says
  `1` and `when = Exit`. The CODE is authoritative and is what this port
  implements; both prose disagreements are recorded rather than reconciled, and
  `add` is not a variable the source ever defines.
* The md's argument table lists `v_input_int_2 | false | Offset`; the code's
  `input.int(0, "Offset", minval = -500, maxval = 500)` defaults to 0. The code
  is followed.
* `offset` shifts only the two PLOTTED bands; both trading conditions read the
  unshifted `lower` / `ema9` series. It therefore places no order, and the port
  reproduces the orders rather than shifting the plotted lines. The input is
  kept in `source_defaults` so the source's parameter list stays on the record.
* `ta.stdev` is the POPULATION standard deviation (Pine's `biased = true`
  default, dividing by N), which pine_ta.pine_stdev models with ddof=0.
* `ta.ema`'s seeding rule is NOT published by TradingView. pine_ta.pine_ema
  seeds the recursion with the first non-na observation and lets an na
  observation pass through without advancing it; PINE_SEMANTICS.md section 3.1
  records this as a parity risk rather than a certified equivalence.
* `sma` / `stdev` return na until their window is full and na propagates within
  the window, so the first possible entry needs 20 bars of history; na
  comparisons are false, so neither condition fires before then. `ta.ema`
  returns a value from the first bar under the modelled seeding.
* Both conditions are evaluated on the same bar's close and both calls are
  written unconditionally in source order (entry then close). On a bar where
  `Long` and `Exit` hold together the engine opens at the next bar's open and
  the same-bar close order then closes that just-opened position at the same
  price -- a zero-length round trip. The call order is preserved so the engine's
  fill sequence matches the source's call sequence; see PINE_SEMANTICS.md
  section 1.13 for the projection limit this shares (the framework is told about
  the entry but cannot be told about a close whose entry is not yet open).
* `plot` / `fill` and the strategy title are display-only and are not
  reproduced. `upper` places no order either and is kept as a column for
  fidelity.
* The `/*backtest` header's `basePeriod: 1h` is the FMZ backtester's own
  granularity, not the strategy's period.
* Leverage, margin, liquidation, funding and the venue's contract-step rounding
  are not modelled; the step can only be read off the exchange object at run
  time, so the framework and the engine may differ by a rounded quantity, which
  the chain verifier measures separately rather than treating as a signal
  difference.
"""
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


class SMBollingerBandsEma9_770f77(PinePortBase, IStrategy):
    source_id = "SM_770f77e7cb60b335"
    source_file = "Bollinger-Bands-EMA-9.md"
    timeframe = "1d"
    can_short = False
    source_defaults: dict = {"length": 20, "src": "close", "mult": 2.0, "offset": 0}
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    source_reproduce_stops = False
    source_fidelity_notes = [
        "strategy() declares only title and overlay, so fixed qty 1, commission "
        "0%, pyramiding 0 and initial capital 1000000 are Pine's documented "
        "defaults. The entry's explicit qty=1 is the same quantity.",
        "Only strategy.entry(\"Long\", ...) is called, so can_short is False; the "
        "only exit is strategy.close(\"Long\", when = Exit), so "
        "source_reproduce_stops is False and a position open at the window's end "
        "stays open.",
        "The md's prose quotes the entry as `strategy.entry(\"Long\", "
        "strategy.long, 1000, when=Long)` and the close as `when=add`; the code "
        "says `1` and `when = Exit`. Code is authoritative and is what is "
        "implemented; `add` is never defined by the source. Recorded, not "
        "reconciled.",
        "The md's argument table gives Offset a default of `false`; the code's "
        "input.int(0, ...) defaults to 0. Code followed.",
        "`offset` shifts only the plotted bands -- both conditions read the "
        "unshifted lower/ema9 series -- so it places no order and is not applied "
        "to the trading series. Kept in source_defaults so the source's "
        "parameter list stays on the record.",
        "`Long = (close[1] < lower)` compares the PREVIOUS close against the "
        "CURRENT bar's lower band (not `lower[1]`, not `close < lower`). "
        "Reproduced literally.",
        "ta.stdev is the POPULATION standard deviation (Pine's biased = true "
        "default, dividing by N), modelled by pine_ta.pine_stdev with ddof=0.",
        "ta.ema's seeding is unpublished by TradingView: pine_ta.pine_ema seeds "
        "with the first non-na observation and does not advance on na. Listed as "
        "an unresolved parity risk in PINE_SEMANTICS.md section 3.1, not as "
        "certified equivalence.",
        "sma/stdev are na until their window is full and na comparisons are "
        "false, so no entry fires before 20 bars of history.",
        "Both conditions are evaluated on the same bar and both calls are written "
        "unconditionally in source order (entry then close); a bar where Long and "
        "Exit hold together yields a zero-length round trip in the engine. See "
        "PINE_SEMANTICS.md section 1.13 for the projection limit this shares.",
        "plot/fill and the strategy title are display-only and are not "
        "reproduced; `upper` places no order and is kept as a column only.",
        "The /*backtest header's `period: 1d` is the strategy's timeframe; its "
        "`basePeriod: 1h` is the FMZ backtester's own granularity for filling "
        "daily bars, not a second timeframe read by the script.",
        "Leverage, margin, liquidation, funding and contract-step rounding are "
        "not modelled; the venue's rounding can differ from the engine's float "
        "quantity, which the chain verifier measures separately.",
    ]

    def pine_indicators(self, dataframe, params):
        src = ta.pine_source(dataframe, params["src"])
        close = dataframe["close"]
        length = int(params["length"])
        ema9 = ta.pine_ema(close, 9)
        basis = ta.pine_sma(src, length)
        dev = float(params["mult"]) * ta.pine_stdev(src, length)
        upper = basis + dev
        lower = basis - dev
        dataframe["pine_ema9"] = ema9
        dataframe["pine_basis"] = basis
        # Plotted and filled between by the source, but read by no condition.
        dataframe["pine_upper"] = upper
        dataframe["pine_lower"] = lower
        # Long = (close[1] < lower): previous close against THIS bar's lower band.
        dataframe["pine_long_condition"] = close.shift(1) < lower
        dataframe["pine_exit_condition"] = close >= ema9
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "long_condition": dataframe["pine_long_condition"].to_numpy(),
            "exit_condition": dataframe["pine_exit_condition"].to_numpy(),
        }

    def pine_script(self, broker, i, ctx):
        # strategy.entry("Long",strategy.long, 1, when = Long)
        broker.entry("Long", "long", qty=1.0, when=bool(ctx["long_condition"][i]))
        # strategy.close("Long", when = Exit)
        broker.close("Long", when=bool(ctx["exit_condition"][i]))
