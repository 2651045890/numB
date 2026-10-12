"""Port of sources/SM_cfef84a6ac3fd8d3.pine (batch_001/Bollinger-Bands与RSI组合交易策略Bollinger-Bands-and-RSI-Combination-Trading-Strategy.md).

Pine v4. Bollinger Bands and RSI as two filters on one pair of reversal
signals:

    basis = sma(source, length)
    dev   = mult * stdev(source, length)
    upper = basis + dev
    lower = basis - dev

    rsi = rsi(rsi_source, rsi_length)

    buy_signal  = crossover(close, lower) and rsi < rsi_oversold
    sell_signal = crossunder(close, upper) and rsi > rsi_overbought

    if (buy_signal)
        strategy.entry("Buy", strategy.long)
    if (sell_signal)
        strategy.entry("Sell", strategy.short)

The Pine body is character-for-character the same as
SM_c6c8ec8071e7d12f's (the two differ only in the `/*backtest` header's
`start` / `end` / `period`), so the translation below is the same translation.
Neither item may be inferred from the other: both were read from their own
source file, and this one's header declares `period: 1d`, which is what its
`timeframe` carries.

Note which series each half of the signal reads: the bands are built from
`source` (an `input(close)`, so a non-default price column still feeds the
bands) while the crossover itself is always evaluated on the literal `close`.
The two are kept separate here instead of collapsing to one series.

Both signal expressions are evaluated on every bar, unconditionally, and the
two `if` blocks are independent: on a bar where both hold, the long entry is
placed first and the short entry second, and the engine fills them in that
order (each `strategy.entry` sets the position TO its own quantity, so the
second reverses the first).

`strategy()` declares only `title` / `overlay`, so Pine's documented defaults
apply and are what this port carries: `default_qty_type=fixed`, one unit per
order, `commission_value=0`, `pyramiding=0`, `process_orders_on_close=false`.
Initial capital is unset in the source, hence Pine's documented default
1000000. `minval` / `maxval` on the four inputs only bound the UI widget and
change no computation, so `source_defaults` records the `defval`s.

The `/*backtest` header declares `period: 1d` on Futures_Binance BTC_USDT, so
`timeframe` is "1d"; its `basePeriod: 1h` is the FMZ backtester's own
granularity for filling those 1d bars, not the strategy's period.

There is no exit call in the source -- not `strategy.close`, not
`strategy.exit` -- so a position is closed only by the opposite entry
reversing it: `source_reproduce_stops` is False and a position still open at
the end of the window stays open.

FIDELITY:

* `stdev` is Pine's population standard deviation (divide by N, not N-1);
  pine_ta.pine_stdev computes exactly that (ddof=0).
* v4's bare `rsi()` is Wilder's RMA-based RSI, which is what
  pine_ta.pine_rsi implements (100 - 100/(1 + rma(gain)/rma(loss))). It is NOT
  the SMA-ratio variant.
* v4's bare `crossover` / `crossunder` are `a > b and a[1] <= b[1]` /
  `a < b and a[1] >= b[1]`, which is what pine_ta.pine_crossover /
  pine_crossunder implement. An na operand makes the comparison na, which Pine
  evaluates as false; the pandas/numpy NaN comparisons used here are false for
  the same reason.
* `sma` and `stdev` return na until their window is full and na anywhere in
  the window propagates, so the first `lower` / `upper` values need `length`
  bars -- Pine's behaviour, and pine_ta's.
* The markdown's argument table transcribes `v_input_3` (the standard
  deviation multiplier) as `2`; the source line is `input(2.0, ...)`, so the
  port carries the float 2.0. The comparison `mult * stdev` is float either
  way, so the rendered value is identical and nothing is changed on that
  account.
* The markdown prose says "if the closing price is lower than the Bollinger
  Bands lower rail, a buy signal is generated" / "...higher than ... upper
  rail, a sell signal", i.e. a level comparison, whereas the source uses
  `crossover` / `crossunder`, i.e. a one-bar crossing event. The source is
  authoritative; the prose is a loose paraphrase. Recorded, not acted on.
* `plot` / `title` / `overlay` carry no orders and are not reproduced.
* Leverage, margin, liquidation and funding are not modelled; the venue's
  contract-step rounding is not modelled either, so the framework and the
  engine can differ by a rounded quantity (the chain verifier measures that
  separately rather than treating it as a signal difference).
"""
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


class SMBollingerBandsRsiCombinationTrading_cfef84(PinePortBase, IStrategy):
    source_id = "SM_cfef84a6ac3fd8d3"
    source_file = (
        "Bollinger-Bands与RSI组合交易策略"
        "Bollinger-Bands-and-RSI-Combination-Trading-Strategy.md"
    )
    timeframe = "1d"
    can_short = True
    source_defaults: dict = {
        "source": "close",
        "length": 20,
        "mult": 2.0,
        "rsi_source": "close",
        "rsi_length": 14,
        "rsi_overbought": 70,
        "rsi_oversold": 30,
    }
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    source_reproduce_stops = False
    source_fidelity_notes = [
        "The Pine body is identical to SM_c6c8ec8071e7d12f's; the two sources "
        "differ only in the /*backtest header start / end / period. Both were "
        "read from their own source file and this one's period is 1d.",
        "stdev is Pine's population form (ddof=0), as pine_ta.pine_stdev "
        "computes it.",
        "v4's bare rsi() is the Wilder RMA-based RSI, not the SMA-ratio "
        "variant; pine_ta.pine_rsi implements the RMA form.",
        "The bands are built from the `source` input (default close) while the "
        "crossover is always evaluated on the literal `close`; the two series "
        "are kept separate rather than collapsed.",
        "The markdown's argument table renders the standard-deviation "
        "multiplier as `2`; the source is `input(2.0, ...)` and the port "
        "carries 2.0.",
        "The markdown prose describes a level comparison (close below the "
        "lower band, close above the upper band) where the source uses "
        "crossover / crossunder, i.e. a one-bar crossing; the source is "
        "authoritative and the prose is recorded, not applied.",
        "minval / maxval bound the input widget only and change no "
        "computation.",
        "No exit call exists (no strategy.close, no strategy.exit): a position "
        "is closed only by an opposite entry reversing it, so "
        "source_reproduce_stops is False and a position open at the end of the "
        "window stays open.",
        "strategy() declares only title / overlay, so Pine's documented "
        "defaults apply: fixed quantity 1, commission 0%, pyramiding 0, "
        "process_orders_on_close=false, initial capital 1000000.",
        "plot / title / overlay are display-only and are not reproduced.",
        "Leverage, margin, liquidation, funding and venue contract-step "
        "rounding are not modelled.",
    ]

    def pine_indicators(self, dataframe, params):
        src = ta.pine_source(dataframe, str(params["source"]))
        length = int(params["length"])
        mult = float(params["mult"])
        rsi_source = ta.pine_source(dataframe, str(params["rsi_source"]))
        rsi_length = int(params["rsi_length"])
        rsi_overbought = float(params["rsi_overbought"])
        rsi_oversold = float(params["rsi_oversold"])

        # basis = sma(source, length)
        # dev   = mult * stdev(source, length)
        # upper = basis + dev
        # lower = basis - dev
        basis = ta.pine_sma(src, length)
        dev = mult * ta.pine_stdev(src, length)
        upper = basis + dev
        lower = basis - dev

        # rsi = rsi(rsi_source, rsi_length)
        rsi = ta.pine_rsi(rsi_source, rsi_length)

        dataframe["pine_basis"] = basis
        dataframe["pine_upper"] = upper
        dataframe["pine_lower"] = lower
        dataframe["pine_rsi"] = rsi
        # buy_signal  = crossover(close, lower) and rsi < rsi_oversold
        dataframe["pine_buy_signal"] = (
            ta.pine_crossover(dataframe["close"], lower) & (rsi < rsi_oversold)
        )
        # sell_signal = crossunder(close, upper) and rsi > rsi_overbought
        dataframe["pine_sell_signal"] = (
            ta.pine_crossunder(dataframe["close"], upper) & (rsi > rsi_overbought)
        )
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "buy_signal": dataframe["pine_buy_signal"].to_numpy(),
            "sell_signal": dataframe["pine_sell_signal"].to_numpy(),
        }

    def pine_script(self, broker, i, ctx):
        # if (buy_signal)
        #     strategy.entry("Buy", strategy.long)
        if ctx["buy_signal"][i]:
            broker.entry("Buy", "long")
        # if (sell_signal)
        #     strategy.entry("Sell", strategy.short)
        if ctx["sell_signal"][i]:
            broker.entry("Sell", "short")
