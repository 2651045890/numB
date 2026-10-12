"""Port of sources/SM_3a389ea847c0a043.pine
(batch_001/Keltner-Channels-EMA-ATR-Strategy-Keltner通道EMA-ATR策略.md).

Pine v5. A Keltner-channel long-only strategy driven by an explicit state flag:

    length = 21, mult = 2, atrLength = 13
    ema        = ta.ema(close, length)
    atr        = ta.atr(atrLength)
    upper_band = ema + mult * atr
    lower_band = ema - mult * atr

    var float entry_price = na
    var bool  in_trade    = false

    if (not in_trade and close < lower_band)     // buy the lower-band break
        strategy.entry("Long", strategy.long)
        entry_price := close
        in_trade := true
    if (in_trade and open > upper_band)          // sell the upper-band break
        strategy.close("Long")
        in_trade := false

    strategy("Keltner Channel Strategy", overlay=true,
             default_qty_type=strategy.percent_of_equity, default_qty_value=10)

Both conditions are written as separate `if` blocks and are evaluated in that
order, so the second one reads `in_trade` AFTER the first has already set it to
true. On a bar whose close is below the lower band AND whose open is above the
upper band (a gap-up open followed by a collapse), the source therefore places
BOTH the entry and the close on the same bar. The port keeps that ordering
rather than restructuring it into `if/else`, because the same-bar pair changes
which trades exist (Pine_SEMANTICS.md section 1.13).

The exit is a `strategy.close`, i.e. a market order -- there is no stop, limit
or trail leg anywhere in the source -- so `source_reproduce_stops` is False.

The /*backtest header declares `period: 1h` on Futures_Binance BTC_USDT, hence
`timeframe = "1h"` (its `basePeriod: 15m` is the FMZ backtester's intrabar fill
granularity, not the strategy's period).

FIDELITY -- translation choices and source/original mismatches:

1. `in_trade` and `entry_price` are `var` state, not per-bar expressions. The
   port carries them in a per-run mutable dict handed to the script through
   `pine_context`, so they persist across bars within one run and are reset
   between runs, exactly as a Pine run does. They are deliberately NOT replaced
   by `strategy.position_size`: `in_trade` is set on the bar the order is
   PLACED, one bar before the fill, so the two disagree for exactly one bar
   after every entry and every exit -- long enough to change the signals.
2. `entry_price` is assigned by the source and then never read again: it feeds
   no order and no plot. The port carries it in the same state dict and reads
   it nowhere.
3. `strategy(...)` is declared at the END of the source, after the orders.
   Pine hoists the declaration's properties, so position in the file has no
   behavioural effect; the port has no equivalent ordering to preserve.
4. `close < lower_band` and `open > upper_band` are both comparisons against
   the CURRENT bar's band values (the bands are not lagged or offset). The
   script is evaluated at bar close, so the bar's own open and close are both
   known and no future data is read.
5. `ta.ema` seeding is the modelled first-value seed (Pine_SEMANTICS.md 3.1),
   and `ta.atr` is `ta.rma(ta.tr(true), length)` (Pine_SEMANTICS.md 3.7).
   Both are warm-up-sensitive for the first ~13/21 bars.
6. plot() calls are display-only and are not reproduced.
7. `percent_of_equity` sizing is reproduced from the engine's own recorded fill
   notional rather than re-derived from the live wallet (Pine_SEMANTICS.md 1.4).
   With qty_value 10 the stake is 10% of the engine's equity as of the signal
   bar's close; the two wallets are reconciled per fill instead of drifting.
8. Leverage, margin, liquidation, funding and the venue's contract-step
   rounding are not modelled; the chain verifier measures the step rounding
   separately instead of treating it as a signal difference.
"""
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


class SMKeltnerChannelEmaAtr_3a389e(PinePortBase, IStrategy):
    source_id = "SM_3a389ea847c0a043"
    source_file = (
        "Keltner-Channels-EMA-ATR-Strategy-Keltner通道EMA-ATR策略.md"
    )
    timeframe = "1h"
    # Long only: the sole order calls are `strategy.entry("Long", strategy.long)`
    # and `strategy.close("Long")`.
    can_short = False
    source_defaults: dict = {
        # input.int(21, title="EMA Length")
        "length": 21,
        # input.float(2, title="ATR Multiplier")
        "mult": 2.0,
        # input.int(13, title="ATR Length")
        "atrLength": 13,
    }
    # strategy("Keltner Channel Strategy", overlay=true,
    #          default_qty_type=strategy.percent_of_equity, default_qty_value=10)
    # The remaining properties are Pine's documented defaults: 0% commission,
    # pyramiding 0, initial capital 1000000, process_orders_on_close=false.
    source_qty_type = "percent_of_equity"
    source_qty_value = 10.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    # No stop / limit / trail leg exists in the source; the only exit is a
    # market `strategy.close("Long")`.
    source_reproduce_stops = False
    source_fidelity_notes = [
        "`var bool in_trade` / `var float entry_price` are per-run mutable state "
        "carried through pine_context, NOT derived from strategy.position_size: "
        "in_trade flips on the bar the order is PLACED, a bar before the fill, "
        "so substituting the live position would shift every signal by one bar.",
        "entry_price is assigned and never read again by the source; the port "
        "carries it and reads it nowhere.",
        "The two `if` blocks are evaluated in written order and the second reads "
        "in_trade AFTER the first may have set it true. A bar with both "
        "close < lower_band and open > upper_band places the entry and the "
        "close together; that pairing is preserved, not restructured to if/else "
        "(Pine_SEMANTICS 1.13 models the same-bar fill order as a choice, not a "
        "verified platform rule).",
        "The exit is a market strategy.close -- the source has no stop, limit or "
        "trail leg, hence source_reproduce_stops = False.",
        "strategy(...) is declared at the end of the source; Pine hoists its "
        "properties, so file position has no behavioural effect.",
        "Both band comparisons use the CURRENT bar's ema/atr; the script is "
        "evaluated at bar close, so the bar's own open and close are known and "
        "no future data is read.",
        "ta.ema uses the first-non-na seed and ta.atr is rma(tr(true)) "
        "(Pine_SEMANTICS 3.1 / 3.7); the first ~21 bars are warm-up.",
        "percent_of_equity sizing is reproduced from the engine's recorded fill "
        "notional (Pine_SEMANTICS 1.4), not re-derived from the live wallet.",
        "plot() calls are display-only and are not reproduced.",
    ]

    def pine_indicators(self, dataframe, params):
        close = dataframe["close"]
        # ema = ta.ema(close, length); atr = ta.atr(atrLength)
        ema = ta.pine_ema(close, int(params["length"]))
        atr = ta.pine_atr(dataframe, int(params["atrLength"]))
        mult = float(params["mult"])
        # upper_band = ema + mult * atr; lower_band = ema - mult * atr
        dataframe["pine_keltner_ema"] = ema
        dataframe["pine_keltner_atr"] = atr
        dataframe["pine_upper_band"] = ema + mult * atr
        dataframe["pine_lower_band"] = ema - mult * atr
        # not in_trade and close < lower_band   (in_trade is per-run state)
        dataframe["pine_below_lower"] = close < dataframe["pine_lower_band"]
        # in_trade and open > upper_band
        dataframe["pine_open_above_upper"] = (
            dataframe["open"] > dataframe["pine_upper_band"]
        )
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "close": dataframe["close"].to_numpy(dtype=float),
            "below_lower": dataframe["pine_below_lower"].to_numpy(dtype=bool),
            "open_above_upper": dataframe["pine_open_above_upper"].to_numpy(dtype=bool),
            # `var float entry_price = na` / `var bool in_trade = false`
            "state": {"entry_price": float("nan"), "in_trade": False},
        }

    def pine_script(self, broker, i, ctx):
        state = ctx["state"]
        in_trade = bool(state["in_trade"])

        # if (not in_trade and close < lower_band)
        #     strategy.entry("Long", strategy.long)
        #     entry_price := close
        #     in_trade := true
        if (not in_trade) and ctx["below_lower"][i]:
            broker.entry("Long", "long")
            state["entry_price"] = float(ctx["close"][i])
            in_trade = True
            state["in_trade"] = True

        # if (in_trade and open > upper_band)
        #     strategy.close("Long")
        #     in_trade := false
        # Evaluated after the block above, so it sees the freshly-set in_trade.
        if in_trade and ctx["open_above_upper"][i]:
            broker.close("Long")
            in_trade = False
            state["in_trade"] = False
