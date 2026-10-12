"""Port of sources/SM_b14a24dee92fb626.pine (batch_001/Bollinger-Bands-Breakout-Strategy-布林带突破策略.md).

Pine v5. A Bollinger Bands breakout, long above the upper band and short below
the lower band, with the MIDDLE band as the exit:

    length = input.int(20, "Length")
    mult   = input.float(2.0, "Multiplier")
    basis      = ta.sma(close, length)
    dev        = mult * ta.stdev(close, length)
    upper_band = basis + dev
    lower_band = basis - dev
    long_condition  = ta.crossover(close, upper_band)
    short_condition = ta.crossunder(close, lower_band)
    exit_long_condition  = ta.crossunder(close, basis)
    exit_short_condition = ta.crossover(close, basis)

and then, in this order:

    if long_condition      -> strategy.entry("Long",  strategy.long)
    if short_condition     -> strategy.entry("Short", strategy.short)
    if exit_long_condition -> strategy.close("Long")
    if exit_short_condition-> strategy.close("Short")

`strategy()` declares only `title` / `shorttitle` / `overlay`, so every property
is Pine's documented default: `strategy.fixed` / 1 contract, initial capital
1000000, commission 0%, pyramiding 0, `process_orders_on_close=false`. The three
`plot()` calls are display-only.

The internal order is the shape the whole group shares:
entry-long, entry-short, close-long, close-short. The two `if` blocks are
separate statements, not an if/else chain, so both exits can be evaluated on the
same bar and each is a no-op when its entry id is not held (PINE_SEMANTICS.md
1.12).

FIDELITY:

* `ta.stdev` is Pine's POPULATION standard deviation (`ddof=0`), reproduced by
  `pine_ta.pine_stdev`.
* `ta.crossover` / `ta.crossunder` against an na operand are false in Pine,
  which `pine_ta` models; the band needs `length` bars, so bars before index 19
  cannot signal.
* `basis` is the same SMA the bands are built from, so the exit level and the
  band centre are the identical series -- computed once here, as in the source.
* No stop / limit / trail exit exists: the only exits are the two
  `strategy.close` calls, so `source_reproduce_stops` is False. A position left
  open at the end of the window stays open, as in the source.
* Reversal is expressed as an independent entry, not as a close: a long is taken
  out by `strategy.close("Long")` on the middle band, and an opposite entry
  nets per PINE_SEMANTICS.md 1.1 if it arrives first.
* md/source divergence recorded, not acted on: the md's prose is a faithful
  description of the code (breakout entry, middle-band exit), and its
  `v_input_int_1 = 20` / `v_input_float_1 = 2` table matches the two source
  defaults. Its `period: 1d` header is reproduced as `timeframe`.
* `/*backtest` header: `period: 1d` on Futures_Binance BTC_USDT, hence
  `timeframe = "1d"`; `basePeriod: 1h` is the FMZ backtester's own fill
  granularity for those 1d bars, not the strategy's period. The header's window
  (2023-04-24 .. 2024-04-29) is extraction metadata, not an `input.time` filter,
  so no data is trimmed.
* Leverage, margin, liquidation, funding and the venue's contract-step rounding
  are not modelled (PINE_SEMANTICS.md section 2).
"""
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


class SMBollingerBandsBreakout_b14a24(PinePortBase, IStrategy):
    source_id = "SM_b14a24dee92fb626"
    source_file = "Bollinger-Bands-Breakout-Strategy-布林带突破策略.md"
    timeframe = "1d"
    can_short = True
    source_defaults: dict = {"length": 20, "mult": 2.0}
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    source_reproduce_stops = False
    source_fidelity_notes = [
        "ta.stdev is Pine's population standard deviation (ddof=0); pine_ta's "
        "pine_stdev implements exactly that.",
        "ta.crossover / ta.crossunder against an na operand are false in Pine, which "
        "pine_ta models; the band needs `length` bars, so no signal before bar 19.",
        "basis is the same SMA the bands are centred on: the exit level and the band "
        "centre are one series, computed once.",
        "No stop / limit / trail exit exists -- the only exits are the two "
        "strategy.close calls -- so source_reproduce_stops is False and a position "
        "open at the window end stays open.",
        "Both entry and both exit calls are independent `if` statements in source "
        "order (entry long, entry short, close long, close short); a close naming an "
        "entry that is not held is a no-op (PINE_SEMANTICS.md 1.12).",
        "strategy() declares only title / shorttitle / overlay, so Pine's documented "
        "defaults apply: strategy.fixed / 1 contract, initial capital 1000000, 0% "
        "commission, pyramiding 0, process_orders_on_close=false.",
        "The md's argument table (v_input_int_1 = 20, v_input_float_1 = 2) and its "
        "prose both agree with the source; no md/source divergence applies here.",
        "The header's basePeriod: 1h is the FMZ backtester's own fill granularity, "
        "not the strategy's period, and its window is extraction metadata rather "
        "than an input.time filter, so no data is trimmed.",
        "plot() calls are display-only and are not reproduced.",
        "Leverage, margin, liquidation, funding and the venue's contract-step "
        "rounding are not modelled.",
    ]

    def pine_indicators(self, dataframe, params):
        close = dataframe["close"]
        length = int(params["length"])
        mult = float(params["mult"])

        # basis = ta.sma(close, length)
        # dev   = mult * ta.stdev(close, length)
        basis = ta.pine_sma(close, length)
        deviation = mult * ta.pine_stdev(close, length)
        upper_band = basis + deviation
        lower_band = basis - deviation

        dataframe["pine_basis"] = basis
        dataframe["pine_upper_band"] = upper_band
        dataframe["pine_lower_band"] = lower_band

        long_condition = ta.pine_crossover(close, upper_band).fillna(False)
        short_condition = ta.pine_crossunder(close, lower_band).fillna(False)
        exit_long_condition = ta.pine_crossunder(close, basis).fillna(False)
        exit_short_condition = ta.pine_crossover(close, basis).fillna(False)

        dataframe["pine_long_condition"] = long_condition
        dataframe["pine_short_condition"] = short_condition
        dataframe["pine_exit_long_condition"] = exit_long_condition
        dataframe["pine_exit_short_condition"] = exit_short_condition
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "long_condition": dataframe["pine_long_condition"].to_numpy(),
            "short_condition": dataframe["pine_short_condition"].to_numpy(),
            "exit_long_condition": dataframe["pine_exit_long_condition"].to_numpy(),
            "exit_short_condition": dataframe["pine_exit_short_condition"].to_numpy(),
        }

    def pine_script(self, broker, i, ctx):
        # if (long_condition)
        #     strategy.entry("Long", strategy.long)
        broker.entry("Long", "long", when=bool(ctx["long_condition"][i]))
        # if (short_condition)
        #     strategy.entry("Short", strategy.short)
        broker.entry("Short", "short", when=bool(ctx["short_condition"][i]))
        # if (exit_long_condition)
        #     strategy.close("Long")
        broker.close("Long", when=bool(ctx["exit_long_condition"][i]))
        # if (exit_short_condition)
        #     strategy.close("Short")
        broker.close("Short", when=bool(ctx["exit_short_condition"][i]))
