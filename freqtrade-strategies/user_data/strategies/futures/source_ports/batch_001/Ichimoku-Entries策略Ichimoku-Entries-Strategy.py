"""Port of sources/SM_0df736cf39d1d231.pine (batch_001/Ichimoku-Entries策略Ichimoku-Entries-Strategy.md).

Pine v5. Reproduced call for call, in the source's own order:

    tenkan  = ta.sma(high + low, 9)  / 2
    kijun   = ta.sma(high + low, 26) / 2
    senkouA = (tenkan + kijun) / 2
    senkouB = ta.sma(high + low, 52) / 2

    basis   = ta.sma(close, bbLength)                       // 20
    upperBB = basis + bbMultiplier * ta.stdev(close, bbLength)
    lowerBB = basis - bbMultiplier * ta.stdev(close, bbLength)
    rsiValue = ta.rsi(close, rsiLength)                     // 14

    ma       = ta.sma(close, length)                        // 14
    std_dev  = ta.stdev(close, length)
    upper_band = ma + multiplier * std_dev
    lower_band = ma - multiplier * std_dev
    distance_upper = close - upper_band
    distance_lower = lower_band - close
    atr_value = ta.atr(atr_length)                          // 14
    threshold = atr_value * threshold_percentage            // 1.5
    oscillator = distance_upper - distance_lower

    longCondition  = close > upperBB  and tenkan > kijun and
                     ta.crossover(close, basis)  and rsiValue < 70
    shortCondition = close < lowerBB  and tenkan < kijun and
                     ta.crossunder(close, basis) and rsiValue > 30

    strategy.entry("Long",  strategy.long,  when = longCondition)
    strategy.entry("Short", strategy.short, when = shortCondition)

    longExitCondition  = close < upperBB and ta.crossover(oscillator, 0)
    shortExitCondition = close > lowerBB and ta.crossunder(oscillator, 0)

    strategy.exit("Take Profit/Stop Loss", from_entry="Long",
                  loss=close - close*stopLossPct/100,
                  profit=close + close*takeProfitPct/100, when = longExitCondition)
    strategy.exit("Take Profit/Stop Loss", from_entry="Short",
                  loss=close + close*stopLossPct/100,
                  profit=close - close*takeProfitPct/100, when = shortExitCondition)

Two things about the exits matter and are easy to get wrong:

1. `loss=` / `profit=` are TICK distances in Pine, not prices
   (PINE_SEMANTICS.md 3.5), and the source fills them with PRICE differences
   (`close - close*1/100`). The source's own arithmetic is therefore taken as a
   tick count and handed to the engine as one: the engine resolves it against
   the position's average entry price with `source_mintick`, exactly as
   TradingView would. Converting the number to a price first would silently
   invent a 1% / 2% stop the source never asked for. Recorded, not "fixed".
2. Both calls share the SAME order id ("Take Profit/Stop Loss") and differ only
   in `from_entry`, so on a bar where both `when=` guards hold the second call
   replaces the first -- Pine keeps one resting order per id, and the engine's
   `_place` mirrors that for `kind == 'exit'`. A false `when=` creates no order
   at all, so it does not cancel the resting one either.

`senkouA`, `senkouB` and `threshold` are computed by the source but read by no
order call (they are only plotted / dead); they are carried for provenance and
cannot affect trading. `tenkan` / `kijun` are used as a trend filter only --
the Ichimoku cloud itself is never part of a condition.

FIDELITY:

* The md's argument table lists `v_input_4` (Stop Loss Percentage) with default
  `true`; the source declares `input(1, title="Stop Loss Percentage")`. The
  source is followed; the md table is wrong.
* The md's title ("Ichimoku Entries") and prose present the Ichimoku cloud as
  the trend engine. In the code the cloud is only plotted: the fishnet is
  reduced to `tenkan > kijun` / `tenkan < kijun`, and `close > upperBB` /
  `close < lowerBB` is a Bollinger-band condition, not a cloud condition.
* `strategy()` declares only `title` and `overlay`, so every property is Pine's
  documented default: `strategy.fixed` / 1 contract, initial capital 1000000,
  commission 0%, pyramiding 0, `process_orders_on_close=false`. Neither entry
  passes a `qty`.
* Both entries are `when=`-guarded and use distinct ids; both exits are
  `when=`-guarded and share one id. The exits carry price legs
  (`profit=` / `loss=` are resting legs too), so they reach Freqtrade through
  `custom_stoploss` and the ROI override rather than as projected next-open
  market exits (PINE_SEMANTICS.md 1.9).
* `ta.atr` / `ta.stdev` / `ta.rsi` / `ta.sma` warmup: na propagates and Pine
  treats an na comparison as false, so a signal cannot appear before every
  series its condition reads is defined. The LONGEST window computed is not
  that gate: `senkouB`'s 52 bars are only ever `plot()`ed and no condition
  reads it, so its window gates nothing. What gates are `kijun`'s 26 bars (the
  entries' `tenkan > kijun` filter; first non-na at bar 25) and `basis`'s 20
  bars (`upperBB` / `lowerBB`, read by both sides, and `crossover(close,
  basis)`; upperBB first non-na at bar 19, so the exits are computable from bar
  20). Measured on BTC/USDT:USDT 1d 2024 (367 bars) with this port's own
  `pine_indicators`: `senkouB` first turns non-na at bar 51, but the first true
  `pine_exit_long` is bar 25 and the engine really places its first exit order
  on bar 25 -- 26 bars before the `senkouB` window completes. `ta.tr`'s
  first-bar na is PINE_SEMANTICS.md 3.7; it only shifts the ATR seeding, and the
  ATR reaches no order call.
* Leverage, margin, liquidation, funding and the venue's contract-step rounding
  are not modelled; the chain verifier measures the last one separately.
* The `/*backtest` header's `basePeriod: 1h` is the FMZ backtester's own
  granularity for filling the 1d bars, not the strategy's period.
"""
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase

TENKAN_LENGTH = 9
KIJUN_LENGTH = 26
SENKOU_B_LENGTH = 52
RSI_OVERBOUGHT = 70.0
RSI_OVERSOLD = 30.0


class SMIchimokuEntries_0df736(PinePortBase, IStrategy):
    source_id = "SM_0df736cf39d1d231"
    source_file = "Ichimoku-Entries策略Ichimoku-Entries-Strategy.md"
    timeframe = "1d"
    can_short = True
    source_defaults: dict = {
        "rsiLength": 14,
        "bbLength": 20,
        "bbMultiplier": 2,
        "stopLossPct": 1,
        "takeProfitPct": 2,
        "length": 14,
        "multiplier": 2,
        "atr_length": 14,
        "threshold_percentage": 1.5,
    }
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    source_reproduce_stops = True
    # TradingView reads the tick size off the symbol and the source never states
    # it; 0.1 is BTC/USDT:USDT, the project's convention. It matters here
    # because the exits are tick-based (see the docstring).
    source_mintick = 0.1
    source_fidelity_notes = [
        "loss= / profit= are TICK distances in Pine (PINE_SEMANTICS.md 3.5), and "
        "the source fills them with PRICE differences (close - close*1/100). The "
        "source's own arithmetic is therefore handed to the engine as a tick "
        "count and resolved against the position's average entry price with "
        "source_mintick = 0.1, as TradingView would. It is NOT converted to a "
        "price first: that would invent a 1% / 2% stop the source never asked "
        "for. Recorded, not reconciled.",
        "Both strategy.exit calls share the order id 'Take Profit/Stop Loss' and "
        "differ only in from_entry, so on a bar where both when= guards hold the "
        "second replaces the first; a false when= creates no order and cancels "
        "nothing. Same-id replacement for kind == 'exit' is the engine's "
        "(PINE_SEMANTICS.md 3.6).",
        "The md's argument table lists the Stop Loss Percentage input as "
        "defaulting to `true`; the source declares input(1, ...). The source is "
        "followed; the md table is wrong.",
        "The md's title and prose present the Ichimoku cloud as the trend "
        "engine. In the code the cloud is only plotted: the fishnet is reduced "
        "to tenkan > kijun / tenkan < kijun, and close > upperBB is a "
        "Bollinger-band condition. Code followed, disagreement recorded.",
        "senkouA, senkouB, atr_value and threshold are computed by the source "
        "but read by no order call, so they cannot affect trading; they are "
        "carried for provenance only. tenkan / kijun enter as a trend filter, "
        "never as a cloud relation.",
        "The exits carry price legs (profit= / loss= count as resting legs), so "
        "they reach Freqtrade through custom_stoploss and the ROI override "
        "rather than as projected next-open market exits (PINE_SEMANTICS.md "
        "1.9); there is no strategy.close and no leg-less strategy.exit, so "
        "PINE_SEMANTICS.md 1.15 does not apply.",
        "strategy() declares only title and overlay, so every property is Pine's "
        "documented default: strategy.fixed / 1 contract, initial capital "
        "1000000, commission 0%, pyramiding 0, process_orders_on_close=false. "
        "Neither entry passes a qty.",
        "na handling: na propagates from ta.sma / ta.stdev / ta.rsi and Pine "
        "treats an na comparison as false, so a signal cannot appear before "
        "every series its condition reads is defined. senkouB's 52 bars are NOT "
        "that gate: senkouB is only plotted and no condition reads it, so the "
        "longest window computed gates nothing. What gates are kijun's 26 bars "
        "(the entries' tenkan > kijun filter; first non-na at bar 25) and "
        "basis's 20 bars (upperBB / lowerBB, read by both sides, and "
        "crossover(close, basis); upperBB first non-na at bar 19). Measured on "
        "BTC/USDT:USDT 1d 2024 (367 bars): senkouB first turns non-na at bar 51, "
        "the first true pine_exit_long is bar 25, and the engine places its "
        "first exit order on bar 25 -- 26 bars before the senkouB window "
        "completes. ta.tr's first-bar na (PINE_SEMANTICS.md 3.7) shifts only the "
        "ATR seeding, and the ATR reaches no order call.",
        "Leverage, margin, liquidation, funding and the venue's contract-step "
        "rounding are not modelled; the chain verifier measures the last one "
        "separately.",
        "The /*backtest header's basePeriod: 1h is the FMZ backtester's own "
        "granularity for filling the 1d bars, not the strategy's period.",
        "The long entry conjoins `close > upperBB` with `crossover(close, "
        "basis)`, which is nearly self-contradictory: crossing above the 20-bar "
        "mean on the same bar the close sits more than 2 standard deviations "
        "above it needs a single-bar jump of over 2 sigma. Measured on "
        "BTC/USDT:USDT 1d 2024 (367 bars) the two hold together on ONE bar of "
        "the 28 with `close > upperBB` and the 15 with the crossover, and that "
        "bar fails the `tenkan > kijun` / `rsi < 70` filters; the short side is "
        "the mirror. The engine therefore books 0 trades on the chain "
        "verifier's window, and its `match` is the zero-trade kind "
        "(PINE_SEMANTICS.md 5.2): it shows only that both sides agree on "
        "silence, NOT that the entries are right. The exits do fire (23 long / "
        "24 short), they just have no entry to close.",
    ]

    def pine_indicators(self, dataframe, params):
        rsi_length = int(params["rsiLength"])
        bb_length = int(params["bbLength"])
        bb_multiplier = float(params["bbMultiplier"])
        stop_loss_pct = float(params["stopLossPct"])
        take_profit_pct = float(params["takeProfitPct"])
        channel_length = int(params["length"])
        channel_multiplier = float(params["multiplier"])
        close = dataframe["close"]
        midpoint = dataframe["high"] + dataframe["low"]

        # Ichimoku components -- all three from the same (high + low) series.
        tenkan = ta.pine_sma(midpoint, TENKAN_LENGTH) / 2.0
        kijun = ta.pine_sma(midpoint, KIJUN_LENGTH) / 2.0
        senkou_a = (tenkan + kijun) / 2.0
        senkou_b = ta.pine_sma(midpoint, SENKOU_B_LENGTH) / 2.0

        # Bollinger Bands.
        basis = ta.pine_sma(close, bb_length)
        deviation = ta.pine_stdev(close, bb_length)
        upper_bb = basis + bb_multiplier * deviation
        lower_bb = basis - bb_multiplier * deviation

        rsi_value = ta.pine_rsi(close, rsi_length)

        # Trade Proximity Oscillator ("Channels").
        ma = ta.pine_sma(close, channel_length)
        std_dev = ta.pine_stdev(close, channel_length)
        upper_band = ma + channel_multiplier * std_dev
        lower_band = ma - channel_multiplier * std_dev
        distance_upper = close - upper_band
        distance_lower = lower_band - close
        # Computed by the source, read by no order call -- carried for
        # provenance only.
        atr_value = ta.pine_atr(dataframe, int(params["atr_length"]))
        threshold = atr_value * float(params["threshold_percentage"])
        oscillator = distance_upper - distance_lower

        cross_up = ta.pine_crossover(close, basis)
        cross_down = ta.pine_crossunder(close, basis)
        dataframe["pine_tenkan"] = tenkan
        dataframe["pine_kijun"] = kijun
        dataframe["pine_senkou_a"] = senkou_a
        dataframe["pine_senkou_b"] = senkou_b
        dataframe["pine_basis"] = basis
        dataframe["pine_upper_bb"] = upper_bb
        dataframe["pine_lower_bb"] = lower_bb
        dataframe["pine_rsi"] = rsi_value
        dataframe["pine_atr"] = atr_value
        dataframe["pine_threshold"] = threshold
        dataframe["pine_oscillator"] = oscillator
        dataframe["pine_entry_long"] = (
            (close > upper_bb)
            & (tenkan > kijun)
            & cross_up
            & (rsi_value < RSI_OVERBOUGHT)
        )
        dataframe["pine_entry_short"] = (
            (close < lower_bb)
            & (tenkan < kijun)
            & cross_down
            & (rsi_value > RSI_OVERSOLD)
        )
        dataframe["pine_exit_long"] = (close < upper_bb) & ta.pine_crossover(
            oscillator, 0
        )
        dataframe["pine_exit_short"] = (close > lower_bb) & ta.pine_crossunder(
            oscillator, 0
        )
        # loss= / profit= are the source's PRICE-difference expressions, handed
        # to the engine as tick counts (see the docstring).
        dataframe["pine_loss_long_ticks"] = close - close * stop_loss_pct / 100.0
        dataframe["pine_profit_long_ticks"] = close + close * take_profit_pct / 100.0
        dataframe["pine_loss_short_ticks"] = close + close * stop_loss_pct / 100.0
        dataframe["pine_profit_short_ticks"] = close - close * take_profit_pct / 100.0
        return dataframe

    def pine_context(self, dataframe, params):
        del params
        return {
            "entry_long": dataframe["pine_entry_long"].to_numpy(),
            "entry_short": dataframe["pine_entry_short"].to_numpy(),
            "exit_long": dataframe["pine_exit_long"].to_numpy(),
            "exit_short": dataframe["pine_exit_short"].to_numpy(),
            "loss_long": dataframe["pine_loss_long_ticks"].to_numpy(),
            "profit_long": dataframe["pine_profit_long_ticks"].to_numpy(),
            "loss_short": dataframe["pine_loss_short_ticks"].to_numpy(),
            "profit_short": dataframe["pine_profit_short_ticks"].to_numpy(),
        }

    def pine_script(self, broker, i, ctx):
        # strategy.entry("Long", strategy.long, when = longCondition)
        broker.entry("Long", "long", when=bool(ctx["entry_long"][i]))
        # strategy.entry("Short", strategy.short, when = shortCondition)
        broker.entry("Short", "short", when=bool(ctx["entry_short"][i]))
        # strategy.exit("Take Profit/Stop Loss", from_entry="Long",
        #               loss=close - close*stopLossPct/100,
        #               profit=close + close*takeProfitPct/100,
        #               when = longExitCondition)
        broker.exit(
            "Take Profit/Stop Loss",
            from_entry="Long",
            when=bool(ctx["exit_long"][i]),
            loss=float(ctx["loss_long"][i]),
            profit=float(ctx["profit_long"][i]),
        )
        # strategy.exit("Take Profit/Stop Loss", from_entry="Short",
        #               loss=close + close*stopLossPct/100,
        #               profit=close - close*takeProfitPct/100,
        #               when = shortExitCondition)
        broker.exit(
            "Take Profit/Stop Loss",
            from_entry="Short",
            when=bool(ctx["exit_short"][i]),
            loss=float(ctx["loss_short"][i]),
            profit=float(ctx["profit_short"][i]),
        )
