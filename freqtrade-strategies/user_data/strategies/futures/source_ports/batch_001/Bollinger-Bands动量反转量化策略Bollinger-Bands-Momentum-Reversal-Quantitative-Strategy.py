"""Port of sources/SM_3a48379e9abeba32.pine
(batch_001/Bollinger-Bands动量反转量化策略Bollinger-Bands-Momentum-Reversal-Quantitative-Strategy.md).

Pine v5. Bollinger Bands on a 34-period SMA with a 2-sigma multiplier, traded
as a band re-entry reversal:

    price      = input.source(close, "Source")
    period     = input.int(34,   "Period")
    multiplier = input.float(2.0,"Multiplier")
    middle_band = ta.sma(price, period)
    deviation   = ta.stdev(price, period)
    upper_band2 = middle_band + multiplier * deviation
    lower_band2 = middle_band - multiplier * deviation

    var bool is_long  = false
    var bool is_short = false

    if (ta.crossover(price, lower_band2))
        strategy.entry("Buy", strategy.long); is_long := true; is_short := false
    if (ta.crossunder(price, upper_band2))
        strategy.entry("Sell", strategy.short); is_long := false; is_short := true

    stop_loss_level_long  = lower_band2
    stop_loss_level_short = upper_band2
    if (is_long)
        strategy.exit("Exit Long",  "Buy",  stop=stop_loss_level_long)
    if (is_short)
        strategy.exit("Exit Short", "Sell", stop=stop_loss_level_short)

`strategy()` declares only title/shorttitle/overlay, so Pine's documented
defaults are in force and carried here: `default_qty_type` fixed, `qty_value`
1 contract, initial_capital 1000000, commission 0%, pyramiding 0,
process_orders_on_close false.

The `/*backtest` header declares `period: 45m` on Futures_Binance BTC_USDT, so
`timeframe` is "45m".

FIDELITY:

* `is_long` / `is_short` are Pine `var` flags: they are set by the SIGNAL bars
  (a long signal clears `is_short`, a short signal clears `is_long`) and are NOT
  cleared when a position exits. The port materialises the same state machine
  over the signal series in `pine_indicators` -- the flags are a pure function
  of the two signal series up to bar `i`, so the value read at bar `i` is the
  value Pine's `var` holds at bar `i`. The two `if` blocks are evaluated in
  source order, so a bar that produced both a crossover and a crossunder (they
  are against two different bands and can in principle co-occur) leaves the
  short flag set, exactly as the source's statement order does.
* Because the flags persist past the exit, `strategy.exit` keeps being re-placed
  on every later bar with the CURRENT band as its stop -- for a position that
  already closed this is a Pine no-op (there is no matching entry to close), and
  the engine models it as such: it records the level but acts on nothing while
  the position is flat, and the projection layer drops it because its
  `from_entry` is not open. The band therefore trails the stop while the
  position lives, which is what the source asks for.
* `ta.stdev` is Pine's BIASED (population) standard deviation -- `biased=true`
  is the v5 default -- so it divides by `length`; that is what
  `pine_ta.pine_stdev` computes (ddof=0). pandas' default ddof=1 would widen
  every band and move every crossing.
* `price` is an `input.source` and is resolved through `pine_ta.pine_source`, so
  a non-default source (hl2, ohlc4, ...) still works instead of silently
  falling back to close. It feeds the SMA, the stdev AND both comparison legs
  of the crossovers.
* `upper_band1` / `lower_band1` (1-sigma) are computed in the source and used
  nowhere: no signal, no stop, no plot. They are not reproduced; nothing reads
  them. Only `middle_band`, `upper_band2` and `lower_band2` are plotted, and
  plotting is display-only.
* MD/SOURCE NOTE: the md prose (both languages) says the long stop sits "below
  the lower band" (在下轨之下). The source sets it exactly AT `lower_band2`
  (the stop is passed `stop_loss_level_long = lower_band2`). The source is
  followed; the prose is a looser description of the same level.
* The stop is a real resting price level, so `source_reproduce_stops` is True
  and the engine's level is mirrored into `custom_stoploss`.
* Leverage, margin, liquidation and funding are not modelled, and neither is
  the venue's contract-step rounding (the chain verifier measures that
  separately rather than treating it as a signal difference).
"""
import numpy as np
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


class SMBollingerBandsMomentumReversal_3a4837(PinePortBase, IStrategy):
    source_id = "SM_3a48379e9abeba32"
    source_file = "Bollinger-Bands动量反转量化策略Bollinger-Bands-Momentum-Reversal-Quantitative-Strategy.md"
    timeframe = "45m"
    can_short = True
    source_defaults: dict = {"price": "close", "period": 34, "multiplier": 2.0}
    # strategy(title/shorttitle/overlay) only: Pine defaults.
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    source_reproduce_stops = True
    source_fidelity_notes = [
        "is_long / is_short are Pine `var` flags set by signal bars and NOT "
        "cleared on exit; they are materialised as a causal state machine over "
        "the two signal series (long signal wins on a tie, because it is "
        "written first in the source).",
        "The exit keeps being re-placed every bar while the flag is set, with "
        "the CURRENT band as the stop; for a flat position that is a Pine no-op "
        "and is modelled as one (engine acts on nothing, the projection drops "
        "it because from_entry is not open).",
        "ta.stdev is the biased (population) deviation -- pine_ta.pine_stdev, "
        "ddof=0 -- which is Pine's v5 default.",
        "`price` is an input.source resolved through pine_ta.pine_source; it "
        "feeds the SMA, the stdev and both crossover legs.",
        "upper_band1 / lower_band1 (1 sigma) are computed and never read in the "
        "source; not reproduced. plot/fill are display-only.",
        "MD/SOURCE NOTE: the md prose says the long stop is 'below the lower "
        "band'; the source uses the lower band itself as the stop price. The "
        "source is followed.",
        "Pine's strategy() here declares no sizing/cost properties, so fixed / "
        "1 contract / 1000000 / 0% / pyramiding 0 are in force; "
        "process_orders_on_close is false (fills on the next bar's open).",
        "The /*backtest header's period: 45m sets the timeframe; there is no "
        "local 45m history, so the chain comparison is expected to report "
        "skipped_no_local_data rather than a trading difference.",
        "Leverage, margin, liquidation, funding and the venue's contract-step "
        "rounding are not modelled; the chain verifier measures the last one "
        "separately.",
    ]

    def pine_indicators(self, dataframe, params):
        price = ta.pine_source(dataframe, str(params["price"]))
        period = int(params["period"])
        multiplier = float(params["multiplier"])

        # middle_band = ta.sma(price, period)
        # deviation   = ta.stdev(price, period)
        middle_band = ta.pine_sma(price, period)
        deviation = ta.pine_stdev(price, period)
        upper_band2 = middle_band + multiplier * deviation
        lower_band2 = middle_band - multiplier * deviation

        # if (ta.crossover(price, lower_band2))  -> entry Buy / is_long := true
        # if (ta.crossunder(price, upper_band2)) -> entry Sell / is_short := true
        cross_up = ta.pine_crossover(price, lower_band2)
        cross_down = ta.pine_crossunder(price, upper_band2)

        # `var bool is_long` / `var bool is_short`, replayed in source order.
        up = cross_up.to_numpy()
        down = cross_down.to_numpy()
        is_long = np.zeros(len(up), dtype=bool)
        is_short = np.zeros(len(up), dtype=bool)
        state = 0  # 0 = neither, 1 = long flag, -1 = short flag
        for i in range(len(up)):
            if up[i]:
                state = 1
            if down[i]:
                state = -1
            is_long[i] = state == 1
            is_short[i] = state == -1

        dataframe["pine_upper_band2"] = upper_band2
        dataframe["pine_lower_band2"] = lower_band2
        dataframe["pine_cross_up"] = cross_up
        dataframe["pine_cross_down"] = cross_down
        dataframe["pine_is_long"] = is_long
        dataframe["pine_is_short"] = is_short
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "cross_up": dataframe["pine_cross_up"].to_numpy(),
            "cross_down": dataframe["pine_cross_down"].to_numpy(),
            "upper_band2": dataframe["pine_upper_band2"].to_numpy(),
            "lower_band2": dataframe["pine_lower_band2"].to_numpy(),
            "is_long": dataframe["pine_is_long"].to_numpy(),
            "is_short": dataframe["pine_is_short"].to_numpy(),
        }

    def pine_script(self, broker, i, ctx):
        # if (ta.crossover(price, lower_band2))
        #     strategy.entry("Buy", strategy.long)
        if ctx["cross_up"][i]:
            broker.entry("Buy", "long")

        # if (ta.crossunder(price, upper_band2))
        #     strategy.entry("Sell", strategy.short)
        if ctx["cross_down"][i]:
            broker.entry("Sell", "short")

        # stop_loss_level_long = lower_band2 ; stop_loss_level_short = upper_band2
        # if (is_long)  strategy.exit("Exit Long",  "Buy",  stop=stop_loss_level_long)
        if ctx["is_long"][i]:
            broker.exit("Exit Long", "Buy", stop=float(ctx["lower_band2"][i]))

        # if (is_short) strategy.exit("Exit Short", "Sell", stop=stop_loss_level_short)
        if ctx["is_short"][i]:
            broker.exit("Exit Short", "Sell", stop=float(ctx["upper_band2"][i]))
