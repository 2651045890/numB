"""Port of sources/SM_e50146df6030bed6.pine (batch_001/44-SMA和9-EMA交叉策略结合RSI过滤及止盈止损-44-SMA-and-9-EMA-Crossover-Strategy-with-RSI-Filter-and-TP-SL.md).

Pine v5 (`//@version=5`). A 44-SMA / 9-EMA cross, confirmed by price being on
the same side of BOTH averages, by the candle's colour and by RSI, entered with
a stop-limit order whose two legs are fixed point distances:

    smaLength = input(44) ; emaLength = input(9)
    profitTarget = input(35) ; stopLoss = input(35)
    rsiLength = input(14) ; rsiOverbought = input(70) ; rsiOversold = input(30)

    sma = ta.sma(close, smaLength)
    ema = ta.ema(close, emaLength)
    rsi = ta.rsi(close, rsiLength)

    longCondition  = ta.crossover(sma, ema) and close > sma and close > ema
                     and close > open and rsi < rsiOverbought
    shortCondition = ta.crossunder(sma, ema) and close < sma and close < ema
                     and close < open and rsi > rsiOversold

    if (longCondition)
        strategy.entry("Buy",  strategy.long,  stop=low - stopLoss,     limit=close + profitTarget)
    if (shortCondition)
        strategy.entry("Sell", strategy.short, stop=high + stopLoss,    limit=close - profitTarget)

BOTH entries are RESTING STOP-LIMIT ENTRY ORDERS, and the stop sits on the
MARKETABLE side of the bar: the buy stop is `low - 35`, below the signal bar,
and the sell stop is `high + 35`, above it. The limit is on the marketable side
of the trigger as well (`close + 35` above a buy stop, `close - 35` below a
sell stop), so once the stop triggers the limit fills at the trigger and the
engine resolves the order through its stop leg (`_price_order_fill`).

That is the framework boundary PINE_SEMANTICS.md section 2.11 records, but on
this source it is expected NOT to bite, for the same structural reason the port
of `SM_87942f41e2081e52` records: because the trigger is already satisfied when
the next bar arrives (`high >= low[t] - 35` on the long side, `low <= high[t] +
35` on the short), the engine fills at `max(stop, open)` / `min(stop, open)`,
i.e. at the next bar's open -- the same bar and the same price Freqtrade uses.
The divergence case is a bar that GAPS through the level, where the engine
fills at the level and the framework at the open. That case is data-dependent
and this port could NOT measure it: the source is 1m and there is no local 1m
history, so the chain verifier reports `skipped_no_local_data`. The claim that
the boundary does not bite is therefore structural, not measured here.

`profitTarget` / `stopLoss` are in POINTS, not ticks -- the inputs are titled
"(Points)" and the source writes `low - stopLoss`, an absolute price offset.
No mintick conversion applies here: `source_mintick` is only what Pine's
`profit=` / `loss=` arguments on `strategy.exit` are counted in, and this
source has no `strategy.exit`.

`strategy()` declares only `title` / `overlay`, so Pine's documented defaults
apply and are what this port carries: `default_qty_type=fixed`, one unit per
order, `commission_value=0`, `pyramiding=0`, `process_orders_on_close=false`,
initial capital 1000000.

The `/*backtest` header declares `period: 1m` on Futures_Binance BTC_USDT, so
`timeframe` is "1m"; its `basePeriod: 1m` is the FMZ backtester's own filling
granularity, which is the same period. The header's window is only about a week
(2024-07-18 to 2024-07-25), which is why this source is tier 5 in the corpus:
there is no local 1m history for the batch verifier to run against, so the
chain check reports `skipped_no_local_data`.

FIDELITY:

* The two entries are resting stop-limit orders, which Freqtrade cannot be
  handed; the projection fires on the placement bar and the framework fills at
  the next open. PINE_SEMANTICS.md section 2.11. On this source the stop sits
  on the MARKETABLE side of the bar (buy stop = low - 35, i.e. already
  triggered when the next bar arrives), so the engine fills at that bar's open
  too -- the same bar and price as the framework, except on a bar that gaps
  through the level. That exception is data-dependent and was NOT measurable
  here (no local 1m history); the expectation is structural, not measured.
* `stopLoss` / `profitTarget` are point offsets applied to `low` / `high` /
  `close`, NOT tick counts, so no `mintick` multiplication is applied. Only
  `strategy.exit(profit=..., loss=...)` counts in ticks and the source has
  none.
* The md's prose says only that a 35-point take-profit and stop-loss are set
  "at entry"; it does not say the TP/SL are the two legs of a stop-limit ENTRY
  order, which is what the code writes. The code is followed and the
  description is recorded as incomplete rather than read as a market entry.
* `ta.rsi` follows the v5 definition `100 - 100 / (1 + rma(gain) / rma(loss))`,
  returns 100 when there were no losses in the window, and is na while either
  average is undeveloped; pine_ta.pine_rsi reproduces all three
  (PINE_SEMANTICS.md section 3.3).
* `ta.ema` seeding is a modelled choice (PINE_SEMANTICS.md section 3.1).
* `ta.sma` is na until its 44-bar window is full and na anywhere in the window
  propagates, so the first long signal cannot arrive before bar 44.
* `crossover` / `crossunder` against an na operand are false.
* The `plot` / `hline` calls, the two `plotshape` arrows, the title and the two
  `alertcondition` calls are display/alerting only and are not reproduced;
  `alertcondition` places no order.
* There is no `strategy.exit` / `strategy.close` / `strategy.cancel` anywhere
  in the source: a position is only ever closed by the opposite entry
  reversing it, so `source_reproduce_stops` is False and a position open at the
  end of the window stays open. The TP/SL live on the ENTRY order, not on an
  exit.
* Leverage, margin, liquidation, funding and the venue's contract-step
  rounding are not modelled; the framework and the engine can differ by a
  rounded quantity (measured separately by the chain verifier).
"""
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


class SMSmaEmaCrossoverRsiTpSl_e50146(PinePortBase, IStrategy):
    source_id = "SM_e50146df6030bed6"
    source_file = (
        "44-SMA和9-EMA交叉策略结合RSI过滤及止盈止损-"
        "44-SMA-and-9-EMA-Crossover-Strategy-with-RSI-Filter-and-TP-SL.md"
    )
    timeframe = "1m"
    can_short = True
    source_defaults: dict = {
        "smaLength": 44,
        "emaLength": 9,
        "profitTarget": 35,
        "stopLoss": 35,
        "rsiLength": 14,
        "rsiOverbought": 70,
        "rsiOversold": 30,
    }
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    # The TP/SL are the two legs of the ENTRY order; there is no exit call.
    source_reproduce_stops = False
    source_fidelity_notes = [
        "Both entries are resting stop-limit orders, which Freqtrade cannot be "
        "handed: the projection fires on the placement bar and the framework "
        "fills at the next open. PINE_SEMANTICS.md section 2.11. The stop is on "
        "the marketable side of the bar (buy stop = low - 35), so the engine's "
        "trigger is already satisfied on the next bar and it fills at that "
        "bar's open too -- the same bar and price as the framework, except on a "
        "bar that gaps through the level. Structural expectation, NOT measured: "
        "the source is 1m and there is no local 1m history.",
        "profitTarget / stopLoss are POINT offsets on low / high / close, not "
        "tick counts, so no mintick multiplication is applied; mintick is only "
        "what strategy.exit(profit=, loss=) counts in and this source has no "
        "strategy.exit. PINE_SEMANTICS.md section 3.5.",
        "The md describes a 35-point TP/SL set 'at entry' but not that the two "
        "legs belong to a stop-limit ENTRY order; the code is followed and the "
        "incomplete description is recorded.",
        "The long side requires ta.crossover(sma, ema) with close above BOTH "
        "averages and a green candle and rsi < rsiOverbought; the short side "
        "mirrors it with rsi > rsiOversold. All terms are reproduced as written, "
        "including the strict inequalities.",
        "ta.rsi follows the v5 rma-based definition, returns 100 when there "
        "were no losses in the window and is na while either average is "
        "undeveloped (PINE_SEMANTICS.md section 3.3).",
        "ta.ema seeding is a modelled choice (PINE_SEMANTICS.md section 3.1).",
        "ta.sma is na until its window is full, so no long signal can arrive "
        "before bar 44; crossover / crossunder against an na operand are false.",
        "The TP/SL live on the ENTRY order, so there is no exit call to mirror: "
        "source_reproduce_stops is False and a position is only closed by the "
        "opposite entry reversing it.",
        "This source is tier 5 in the corpus -- there is no local 1m history for "
        "the batch verifier, so the chain check reports skipped_no_local_data.",
        "plot / hline / plotshape / alertcondition and the title are display and "
        "alerting only and place no order.",
        "Leverage, margin, liquidation, funding and venue contract-step "
        "rounding are not modelled.",
    ]

    def pine_indicators(self, dataframe, params):
        close = dataframe["close"]
        open_ = dataframe["open"]
        high = dataframe["high"]
        low = dataframe["low"]

        sma = ta.pine_sma(close, int(params["smaLength"]))
        ema = ta.pine_ema(close, int(params["emaLength"]))
        rsi = ta.pine_rsi(close, int(params["rsiLength"]))

        long_condition = (
            ta.pine_crossover(sma, ema)
            & (close > sma)
            & (close > ema)
            & (close > open_)
            & (rsi < float(params["rsiOverbought"]))
        )
        short_condition = (
            ta.pine_crossunder(sma, ema)
            & (close < sma)
            & (close < ema)
            & (close < open_)
            & (rsi > float(params["rsiOversold"]))
        )

        stop_loss = float(params["stopLoss"])
        profit_target = float(params["profitTarget"])

        dataframe["pine_sma"] = sma
        dataframe["pine_ema"] = ema
        dataframe["pine_rsi"] = rsi
        dataframe["pine_long_condition"] = long_condition.fillna(False)
        dataframe["pine_short_condition"] = short_condition.fillna(False)
        # strategy.entry("Buy", strategy.long, stop=low - stopLoss, limit=close + profitTarget)
        dataframe["pine_buy_stop"] = low - stop_loss
        dataframe["pine_buy_limit"] = close + profit_target
        # strategy.entry("Sell", strategy.short, stop=high + stopLoss, limit=close - profitTarget)
        dataframe["pine_sell_stop"] = high + stop_loss
        dataframe["pine_sell_limit"] = close - profit_target
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "long_condition": dataframe["pine_long_condition"].to_numpy(dtype=bool),
            "short_condition": dataframe["pine_short_condition"].to_numpy(dtype=bool),
            "buy_stop": dataframe["pine_buy_stop"].to_numpy(dtype=float),
            "buy_limit": dataframe["pine_buy_limit"].to_numpy(dtype=float),
            "sell_stop": dataframe["pine_sell_stop"].to_numpy(dtype=float),
            "sell_limit": dataframe["pine_sell_limit"].to_numpy(dtype=float),
        }

    def pine_script(self, broker, i, ctx):
        # if (longCondition)
        #     strategy.entry("Buy", strategy.long, stop=low - stopLoss, limit=close + profitTarget)
        if ctx["long_condition"][i]:
            broker.entry(
                "Buy",
                "long",
                stop=float(ctx["buy_stop"][i]),
                limit=float(ctx["buy_limit"][i]),
            )
        # if (shortCondition)
        #     strategy.entry("Sell", strategy.short, stop=high + stopLoss, limit=close - profitTarget)
        if ctx["short_condition"][i]:
            broker.entry(
                "Sell",
                "short",
                stop=float(ctx["sell_stop"][i]),
                limit=float(ctx["sell_limit"][i]),
            )
