"""Port of sources/SM_1f83e7d54024d490.pine
(batch_001/MA-MACD-BB多指标交易策略回测工具-MA-MACD-BB-Multi-Indicator-Trading-Strategy-Backtesting-Tool.md).

Pine v5. One indicator is selected at a time by an input, one direction is
selected at a time by another, and the entry size is derived from the live
equity each bar. With the source's own defaults (`which_ta="MA"`,
`which_camp="Long"`) only the MA branch is live, and it is a plain SMA(50)
crossover system; the MACD and Bollinger branches are reachable through the
inputs and are ported in full.

    which_ta   = input.string("MA",   "Select Indicator",   ["MACD","BB","MA"])
    which_camp = input.string("Long", "Select Long / Short", ["Short","Long"])
    positionSize = input.float(100.0, "Each position's capital allocation %") / 100

    int x = na
    if which_ta == "MA"        x := 1
    else if which_ta == "MACD" x := 2
    else if which_ta == "BB"   x := 3

    [macdLine, signalLine, _] = ta.macd(macd_source, 12, 26, 9)
    ma    = ta.sma(close, 50)
    basis = ta.sma(close, 20)
    dev   = 2.0 * ta.stdev(close, 20)
    upper = basis + dev
    lower = basis - dev

    buySignalMACD   = ta.crossover(macdLine, signalLine)
    buySignalMA     = ta.crossover(close, ma)
    buySignalBB     = close < lower
    sellSignalBBExit = close > basis
    sellSignalMACD  = ta.crossunder(macdLine, signalLine)
    sellSignalMA    = ta.crossunder(close, ma)
    sellSignalBB    = close > upper
    buySignalBBExit = close < basis

    accountSize        = strategy.equity
    positionSizeAmount = accountSize * positionSize
    orderSize          = math.floor(positionSizeAmount / close)

    if strategy.opentrades == 0
        if buySignalMACD and x == 2 and which_camp == "Long"
            strategy.entry("Buy MACD", strategy.long,  qty=orderSize)
        if buySignalMA   and x == 1 and which_camp == "Long"
            strategy.entry("Buy MA",   strategy.long,  qty=orderSize)
        if buySignalBB   and x == 3 and which_camp == "Long"
            strategy.entry("Buy BB",   strategy.long,  qty=orderSize)
    if strategy.opentrades == 0
        if sellSignalMACD and x == 2 and which_camp == "Short"
            strategy.entry("Sell MACD", strategy.short, qty=orderSize)
        if sellSignalMA   and x == 1 and which_camp == "Short"
            strategy.entry("Sell MA",   strategy.short, qty=orderSize)
        if sellSignalBB   and x == 3 and which_camp == "Short"
            strategy.entry("Sell BB",   strategy.short, qty=orderSize)

    if (sellSignalMACD)   and which_camp == "Long"  -> strategy.close("Buy MACD")
    if (sellSignalMA)     and which_camp == "Long"  -> strategy.close("Buy MA")
    if (sellSignalBBExit) and which_camp == "Long"  -> strategy.close("Buy BB")
    if (buySignalMACD)    and which_camp == "Short" -> strategy.close("Sell MACD")
    if (buySignalMA)      and which_camp == "Short" -> strategy.close("Sell MA")
    if (buySignalBBExit)  and which_camp == "Short" -> strategy.close("Sell BB")

Note the Bollinger exits: the long is closed by `close > basis` and the short by
`close < basis` (the MIDDLE band), while the entries are the outer-band breaks
(`close < lower` / `close > upper`). Those are the source's `sellSignalBBExit` /
`buySignalBBExit`, not `sellSignalBB` / `buySignalBB`.

`orderSize` is recomputed on EVERY bar from `strategy.equity`, and `math.floor`
truncates it to a whole number of contracts. It is evaluated once per bar and
shared by all six entry calls, exactly as the source writes it above the blocks.
When the floor lands on 0 the engine treats the entry as one that cannot move the
position and does not project it (Pine never opens a 0-contract position either);
when the equity expression is not finite the quantity is left `na`, which Pine
resolves to `default_qty_type` / `default_qty_value`.

`strategy()` declares only `overlay=true`, so everything else is Pine's
documented default: `default_qty_type=strategy.fixed`, `default_qty_value` 1,
commission 0%, pyramiding 0, initial capital 1000000. The explicit `qty=` on each
entry normally overrides the default quantity, but `fixed`/1 is still what an na
`orderSize` falls back to.

The `/*backtest` header declares `period: 1d` on Futures_Binance BTC_USDT, so
`timeframe` is "1d"; its `basePeriod: 1h` is the FMZ backtester's fill
granularity, not the strategy's period.

FIDELITY:

* `which_camp` defaults to "Long", so with no parameter override the short
  entries and the "Short" closes are unreachable. They are ported anyway because
  the source contains them and the input is part of its behaviour (rule 1: the
  source's trade behaviour, not the default run of it). `can_short` is True for
  the same reason.
* `macd_source = input.source(close, ...)` is resolved through `pine_ta`'s
  source map, so changing the input to another OHLCV field reaches `ta.macd`.
* `ta.stdev` is Pine's population standard deviation (ddof=0) and
  `pine_stdev` matches; using the sample deviation would widen every band by
  sqrt(n/(n-1)).
* `plot()`, `plotshape()` and `histogram` are display-only. The `plotshape`
  guard `strategy.opentrades == 0` is the same condition the entry blocks use, so
  it adds nothing behavioural.
* `strategy.close(id)` is scoped to a single entry id, and the source calls it on
  a `which_camp` test rather than on the position's sign, so e.g. the
  "Long"-campaign closes name `Buy *` ids only. The engine's from_entry scoping
  (PINE_SEMANTICS.md 1.12) keeps a close on a non-open id a no-op.
* Both `if strategy.opentrades == 0` blocks read the SAME live count in the
  engine as they do in Pine: the first block's entry is placed but not yet filled
  when the second block runs, so `opentrades` is still 0 in the second block.
  `broker.open_trades` is likewise the count of filled entries, not placed ones.
* md and source agree on the indicator periods and the overall design; the md
  describes the tool's behaviour at the level of prose and adds no rule the code
  does not have (it also claims "根据账户余额自动计算每笔交易的头寸大小", which is
  exactly the `orderSize` expression).
* Leverage, margin, liquidation, funding and the venue's contract-step rounding
  are not modelled by the engine (PINE_SEMANTICS.md 二.4, 1.6). `math.floor` here
  is the SOURCE's own truncation, not the venue's step rounding.
"""
from __future__ import annotations

import math

import numpy as np
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


class SMMaMacdBbBacktester_1f83e7(PinePortBase, IStrategy):
    source_id = "SM_1f83e7d54024d490"
    source_file = (
        "MA-MACD-BB多指标交易策略回测工具-"
        "MA-MACD-BB-Multi-Indicator-Trading-Strategy-Backtesting-Tool.md"
    )
    timeframe = "1d"
    can_short = True
    source_defaults: dict = {
        # which_ta = input.string("MA", ...) / which_camp = input.string("Long", ...)
        "which_ta": "MA",
        "which_camp": "Long",
        # positionSize = input.float(100.0, ...) / 100 -- the RAW input default
        "positionSize": 100.0,
        # MACD inputs
        "fast_length": 12,
        "slow_length": 26,
        "signal_smoothing": 9,
        # macd_source = input.source(close, title="MACD Source")
        "macd_source": "close",
        # Moving average input
        "ma_length": 50,
        # Bollinger Band inputs
        "bb_length": 20,
        "bb_mult": 2.0,
    }
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    source_reproduce_stops = False
    source_fidelity_notes = [
        "which_camp defaults to 'Long', so the short entries and the 'Short' "
        "closes are unreachable without a parameter override; they are ported "
        "because the source contains them and can_short is True for the same "
        "reason.",
        "positionSize is an input default of 100.0 divided by 100 at the "
        "declaration; source_defaults holds the raw 100.0 and the /100.0 is "
        "applied where the source applies it.",
        "orderSize = math.floor(strategy.equity * positionSize / close) is "
        "recomputed every bar and shared by all six entry calls, exactly as the "
        "source evaluates it once above the entry blocks.",
        "A floored orderSize of 0 is dropped by the engine rather than projected "
        "as a signal, matching Pine, which cannot open a 0-contract position; a "
        "non-finite equity leaves the quantity na, which Pine resolves to "
        "default_qty_type / default_qty_value.",
        "The Bollinger exits use the MIDDLE band (close > basis for the long, "
        "close < basis for the short), i.e. the source's sellSignalBBExit / "
        "buySignalBBExit -- not sellSignalBB / buySignalBB, which are the "
        "outer-band breaks the entries use.",
        "ta.stdev is Pine's population standard deviation (ddof=0); pine_stdev "
        "matches, and a sample deviation would widen every band.",
        "macd_source = input.source(close) is resolved through pine_ta's source "
        "map so the input can be pointed at another OHLCV field.",
        "strategy.close names a single entry id and is gated on which_camp, not "
        "on the position's sign; the engine's from_entry scoping reproduces the "
        "resulting no-op (PINE_SEMANTICS.md 1.12).",
        "plot / plotshape / histogram are display-only; plotshape's "
        "strategy.opentrades == 0 guard duplicates the entry blocks' own gate.",
        "Both `if strategy.opentrades == 0` blocks see the same live count: the "
        "first block's order is placed but unfilled when the second runs, so "
        "broker.open_trades is still 0 there, as in Pine.",
        "Leverage, margin, liquidation, funding and venue contract-step rounding "
        "are not modelled; math.floor is the source's own truncation, not the "
        "venue's step rounding.",
    ]

    def pine_indicators(self, dataframe, params):
        close = dataframe["close"]

        # [macdLine, signalLine, _] = ta.macd(macd_source, fast, slow, signal)
        macd_source = ta.pine_source(dataframe, str(params["macd_source"]))
        macd = ta.pine_macd(
            macd_source,
            int(params["fast_length"]),
            int(params["slow_length"]),
            int(params["signal_smoothing"]),
        )
        macd_line = macd["macd"]
        signal_line = macd["signal"]

        # ma = ta.sma(close, ma_length)
        ma = ta.pine_sma(close, int(params["ma_length"]))

        # basis = ta.sma(close, bb_length); dev = bb_mult * ta.stdev(close, bb_length)
        basis = ta.pine_sma(close, int(params["bb_length"]))
        dev = float(params["bb_mult"]) * ta.pine_stdev(close, int(params["bb_length"]))
        upper = basis + dev
        lower = basis - dev

        dataframe["pine_macd"] = macd_line
        dataframe["pine_macd_signal"] = signal_line
        dataframe["pine_ma"] = ma
        dataframe["pine_bb_basis"] = basis
        dataframe["pine_bb_upper"] = upper
        dataframe["pine_bb_lower"] = lower

        # Signal families.
        dataframe["pine_buy_macd"] = ta.pine_crossover(macd_line, signal_line)
        dataframe["pine_buy_ma"] = ta.pine_crossover(close, ma)
        dataframe["pine_buy_bb"] = (close < lower).astype(bool)
        dataframe["pine_sell_bb_exit"] = (close > basis).astype(bool)

        dataframe["pine_sell_macd"] = ta.pine_crossunder(macd_line, signal_line)
        dataframe["pine_sell_ma"] = ta.pine_crossunder(close, ma)
        dataframe["pine_sell_bb"] = (close > upper).astype(bool)
        dataframe["pine_buy_bb_exit"] = (close < basis).astype(bool)
        return dataframe

    def pine_context(self, dataframe, params):
        # int x = na; if which_ta == "MA" x := 1 ... (the options are
        # constrained, but a value outside the three leaves x at na, i.e. no
        # branch is taken).
        which_ta = str(params["which_ta"])
        indicator = {"MA": 1, "MACD": 2, "BB": 3}.get(which_ta)
        return {
            "indicator": indicator,
            "long_camp": str(params["which_camp"]) == "Long",
            "short_camp": str(params["which_camp"]) == "Short",
            "position_size_frac": float(params["positionSize"]) / 100.0,
            "close": dataframe["close"].to_numpy(dtype=float),
            "buy_macd": dataframe["pine_buy_macd"].to_numpy(dtype=bool),
            "buy_ma": dataframe["pine_buy_ma"].to_numpy(dtype=bool),
            "buy_bb": dataframe["pine_buy_bb"].to_numpy(dtype=bool),
            "sell_macd": dataframe["pine_sell_macd"].to_numpy(dtype=bool),
            "sell_ma": dataframe["pine_sell_ma"].to_numpy(dtype=bool),
            "sell_bb": dataframe["pine_sell_bb"].to_numpy(dtype=bool),
            "sell_bb_exit": dataframe["pine_sell_bb_exit"].to_numpy(dtype=bool),
            "buy_bb_exit": dataframe["pine_buy_bb_exit"].to_numpy(dtype=bool),
        }

    def pine_script(self, broker, i, ctx):
        # accountSize = strategy.equity
        # positionSizeAmount = accountSize * positionSize
        # orderSize = math.floor(positionSizeAmount / close)
        raw_size = broker.equity * ctx["position_size_frac"] / ctx["close"][i]
        order_size = float(math.floor(raw_size)) if np.isfinite(raw_size) else float("nan")

        indicator = ctx["indicator"]
        long_camp = ctx["long_camp"]
        short_camp = ctx["short_camp"]

        # if strategy.opentrades == 0
        if broker.open_trades == 0:
            if ctx["buy_macd"][i] and indicator == 2 and long_camp:
                broker.entry("Buy MACD", "long", qty=order_size)
            if ctx["buy_ma"][i] and indicator == 1 and long_camp:
                broker.entry("Buy MA", "long", qty=order_size)
            if ctx["buy_bb"][i] and indicator == 3 and long_camp:
                broker.entry("Buy BB", "long", qty=order_size)

        # if strategy.opentrades == 0
        if broker.open_trades == 0:
            if ctx["sell_macd"][i] and indicator == 2 and short_camp:
                broker.entry("Sell MACD", "short", qty=order_size)
            if ctx["sell_ma"][i] and indicator == 1 and short_camp:
                broker.entry("Sell MA", "short", qty=order_size)
            if ctx["sell_bb"][i] and indicator == 3 and short_camp:
                broker.entry("Sell BB", "short", qty=order_size)

        # Close positions based on exit signals.
        if ctx["sell_macd"][i] and long_camp:
            broker.close("Buy MACD")
        if ctx["sell_ma"][i] and long_camp:
            broker.close("Buy MA")
        if ctx["sell_bb_exit"][i] and long_camp:
            broker.close("Buy BB")
        if ctx["buy_macd"][i] and short_camp:
            broker.close("Sell MACD")
        if ctx["buy_ma"][i] and short_camp:
            broker.close("Sell MA")
        if ctx["buy_bb_exit"][i] and short_camp:
            broker.close("Sell BB")
