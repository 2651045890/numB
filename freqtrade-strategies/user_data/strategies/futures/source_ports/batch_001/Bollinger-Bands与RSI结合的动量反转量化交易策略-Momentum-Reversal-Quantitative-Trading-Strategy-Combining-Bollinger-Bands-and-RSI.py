"""Port of sources/SM_d6bf7147be773796.pine (batch_001/Bollinger-Bands与RSI结合的动量反转量化交易策略-Momentum-Reversal-Quantitative-Trading-Strategy-Combining-Bollinger-Bands-and-RSI.md).

Pine v5. Bollinger Bands gated by RSI, with the MIDDLE band as the exit:

    length = input.int(20, "Bollinger Bands Length")
    src    = input(close, "Source")
    mult   = input.float(2.0, "Bollinger Bands Multiplier")
    basis      = ta.sma(src, length)
    dev        = mult * ta.stdev(src, length)
    upper_band = basis + dev
    lower_band = basis - dev
    rsi_length = input.int(14, "RSI Length")
    rsi        = ta.rsi(src, rsi_length)

    buy_condition  = ta.crossover(close, lower_band)  and rsi < 30
    sell_condition = ta.crossunder(close, upper_band) and rsi > 70
    exit_condition = ta.cross(close, basis)

and then, in this order:

    if buy_condition  -> strategy.entry("Buy",  strategy.long)
    if sell_condition -> strategy.entry("Sell", strategy.short)
    if exit_condition -> strategy.close("Buy")
                         strategy.close("Sell")

The two band tests run the "wrong" way round relative to a textbook breakout
(buy on a cross ABOVE the LOWER band, sell on a cross BELOW the UPPER band), and
the source says so twice -- in the code and in the md's prose. It is reproduced
as written; see FIDELITY.

`strategy()` declares only `title` / `overlay`, so every property is Pine's
documented default: `strategy.fixed` / 1 contract, initial capital 1000000,
commission 0%, pyramiding 0, `process_orders_on_close=false`. The three `plot()`
calls and the two `hline()` calls are display-only.

FIDELITY:

* `rsi < 30` / `rsi > 70` are LITERALS in the source, not inputs: the md's prose
  describes thresholds of 30/70 and the code hard-codes them (`rsi_length` is
  the only RSI input). They stay literals here.
* The two entry tests are evaluated in source order and are independent `if`
  statements, not an if/else chain, so both can fire on one bar and the source's
  chosen order (Buy first, Sell second) is preserved. With default inputs they
  cannot both be true on one bar: `buy` needs `close` above the lower band and
  `sell` needs it below the upper band, and the bands cannot cross.
* The exit is a single `if` block containing TWO close calls, in the source's
  order: `close("Buy")` then `close("Sell")` (PINE_SEMANTICS.md 1.12 -- a close
  naming an entry that is not held is a no-op).
* `ta.cross` is `crossover or crossunder`, reproduced by `pine_ta.pine_cross`;
  `ta.stdev` is Pine's POPULATION standard deviation (`ddof=0`).
* `src` feeds the bands AND the RSI, while the entry crosses test `close`
  directly -- the source mixes the two, so the port keeps `src` and `close`
  distinct instead of collapsing them onto the default value.
* `ta.crossover` / `ta.crossunder` against an na operand are false in Pine, which
  `pine_ta` models; `pine_ta.pine_rsi` returns na until its Wilder windows have
  formed, and an na RSI makes both entry conditions false rather than raising.
* No stop / limit / trail exit exists: the only exits are the two
  `strategy.close` calls, so `source_reproduce_stops` is False. A position left
  open at the end of the window stays open, as in the source.
* md/source divergence recorded, not acted on: the md's prose calls the middle
  band a STOP-LOSS level ("使用布林带中轨作为止损位置" / "The middle Bollinger Band
  is used as a stop-loss position"). The code places no stop: it closes on a
  `ta.cross(close, basis)` signal, i.e. a market exit on the bar the close
  crosses the middle band, which is evaluated at the bar close and filled at the
  next open. The code is followed and the wording is recorded rather than
  reconciled. The md's pinescript block is otherwise byte-identical to the
  extracted source, and its argument table is absent.
* `/*backtest` header: `period: 1h` on Binance BNB_USDT, hence `timeframe = "1h"`.
  The exchange/currency differ from the BTC_USDT futures pairs the rest of the
  batch declares, but the header is extraction metadata, not a strategy property
  -- `timeframe` is the only field it contributes. `basePeriod: 1h` agrees. Its
  window (2024-07-15 .. 2025-02-18) is not an `input.time` filter, so no data is
  trimmed.
* Leverage, margin, liquidation, funding and the venue's contract-step rounding
  are not modelled (PINE_SEMANTICS.md section 2).
"""
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


class SMBollingerBandsRsiMomentum_d6bf71(PinePortBase, IStrategy):
    source_id = "SM_d6bf7147be773796"
    source_file = (
        "Bollinger-Bands与RSI结合的动量反转量化交易策略-"
        "Momentum-Reversal-Quantitative-Trading-Strategy-Combining-"
        "Bollinger-Bands-and-RSI.md"
    )
    timeframe = "1h"
    can_short = True
    source_defaults: dict = {
        "length": 20,
        "src": "close",
        "mult": 2.0,
        "rsi_length": 14,
    }
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    source_reproduce_stops = False
    source_fidelity_notes = [
        "rsi < 30 / rsi > 70 are literals in the source, not inputs; they stay "
        "literals. rsi_length (14) is the only RSI input.",
        "src feeds the bands AND the RSI while the entry crosses test close "
        "directly; the port keeps src and close distinct rather than collapsing "
        "them onto the default value.",
        "The band tests run the 'wrong' way round for a breakout -- buy on a cross "
        "above the LOWER band, sell on a cross below the UPPER band -- and both the "
        "code and the md's prose say so. Reproduced as written.",
        "Both entries are independent `if` statements in source order (Buy, then "
        "Sell); neither can fire on the same bar with the default inputs, because "
        "the sell test needs close below the upper band and the buy test needs it "
        "above the lower band.",
        "The exit is one `if` block holding TWO close calls in source order, "
        "close(\"Buy\") then close(\"Sell\"); a close naming an entry that is not "
        "held is a no-op (PINE_SEMANTICS.md 1.12).",
        "ta.cross is crossover or crossunder (pine_ta.pine_cross); ta.stdev is "
        "Pine's population standard deviation (ddof=0).",
        "ta.crossover / ta.crossunder against an na operand are false in Pine; an na "
        "RSI (before the Wilder windows form) makes both entry conditions false "
        "rather than raising.",
        "No stop / limit / trail exit exists -- the only exits are the two "
        "strategy.close calls -- so source_reproduce_stops is False and a position "
        "open at the window end stays open.",
        "md/source divergence recorded, not acted on: the md's prose calls the "
        "middle band a stop-loss level, while the code places no stop and instead "
        "closes on a ta.cross(close, basis) signal next open. The code is followed.",
        "strategy() declares only title / overlay, so Pine's documented defaults "
        "apply: strategy.fixed / 1 contract, initial capital 1000000, 0% commission, "
        "pyramiding 0, process_orders_on_close=false.",
        "The header declares Binance BNB_USDT rather than the BTC_USDT futures pair "
        "the rest of the batch uses; only its period: 1h is used, as `timeframe`. Its "
        "window is extraction metadata, not an input.time filter, so no data is "
        "trimmed.",
        "plot() / hline() calls are display-only and are not reproduced.",
        "Leverage, margin, liquidation, funding and the venue's contract-step "
        "rounding are not modelled.",
    ]

    def pine_indicators(self, dataframe, params):
        close = dataframe["close"]
        src = ta.pine_source(dataframe, params["src"])
        length = int(params["length"])
        mult = float(params["mult"])
        rsi_length = int(params["rsi_length"])

        # basis = ta.sma(src, length)
        # dev   = mult * ta.stdev(src, length)
        basis = ta.pine_sma(src, length)
        deviation = mult * ta.pine_stdev(src, length)
        upper_band = basis + deviation
        lower_band = basis - deviation
        rsi = ta.pine_rsi(src, rsi_length)

        dataframe["pine_basis"] = basis
        dataframe["pine_upper_band"] = upper_band
        dataframe["pine_lower_band"] = lower_band
        dataframe["pine_rsi"] = rsi

        # Pine's na comparisons are false: an unformed RSI places no order.
        dataframe["pine_buy_condition"] = (
            ta.pine_crossover(close, lower_band) & (rsi < 30)
        ).fillna(False)
        dataframe["pine_sell_condition"] = (
            ta.pine_crossunder(close, upper_band) & (rsi > 70)
        ).fillna(False)
        dataframe["pine_exit_condition"] = ta.pine_cross(close, basis).fillna(False)
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "buy_condition": dataframe["pine_buy_condition"].to_numpy(),
            "sell_condition": dataframe["pine_sell_condition"].to_numpy(),
            "exit_condition": dataframe["pine_exit_condition"].to_numpy(),
        }

    def pine_script(self, broker, i, ctx):
        # if buy_condition
        #     strategy.entry("Buy", strategy.long)
        broker.entry("Buy", "long", when=bool(ctx["buy_condition"][i]))
        # if sell_condition
        #     strategy.entry("Sell", strategy.short)
        broker.entry("Sell", "short", when=bool(ctx["sell_condition"][i]))
        # if exit_condition
        #     strategy.close("Buy")
        #     strategy.close("Sell")
        if ctx["exit_condition"][i]:
            broker.close("Buy")
            broker.close("Sell")
