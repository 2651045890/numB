"""Port of sources/SM_a52b9a91bb7941ae.pine

(batch_001/EMA双均线固定风险止损止盈-EMA-Dual-Crossover-Fixed-Risk-Stop-Loss-Take-Profit.md).

Pine v5. A 65/240 EMA crossover gated by a raw volume threshold, with a fixed
price-distance stop and take-profit, reproduced call for call in the source's
own order:

    ema_fast = ta.ema(close, 65)
    ema_slow = ta.ema(close, 240)
    bullish_crossover = ta.crossover(ema_fast, ema_slow)
    bearish_crossover = ta.crossunder(ema_fast, ema_slow)

    if (bullish_crossover and volume > volume_threshold)
        strategy.entry("Buy", strategy.long, qty=position_size)
        strategy.exit("Exit", "Buy", stop=close - stop_loss_distance,
                                  limit=close + take_profit_distance)
    if (bearish_crossover and volume > volume_threshold)
        strategy.entry("Sell", strategy.short, qty=position_size)
        strategy.exit("Exit", "Sell", stop=close + stop_loss_distance,
                                   limit=close - take_profit_distance)

The source has NO `input()` calls: 65 / 240 / 1000 / 0.5 / 100 / 1500 are all
literals, so `source_defaults` is empty and the port carries them as module
constants.

`strategy()` declares only `overlay=true`, `currency="USD"` and
`initial_capital=100`. It declares no `default_qty_type` / `default_qty_value`,
so Pine's documented defaults apply (`strategy.fixed` / 1); neither is ever read
because both entries pass `qty=` explicitly. No `commission_value` is declared,
so the source's cost basis is 0%; `pyramiding` is unset, hence Pine's default 0;
`process_orders_on_close=false`.

`position_size = risk_per_trade / syminfo.mintick / stop_loss_distance`, i.e.
0.5 / 0.1 / 100 = 0.05 contracts. TradingView reads the tick size off the
symbol; the source never states it and 0.1 is BTC/USDT:USDT's increment (the
project's convention, PINE_SEMANTICS.md 3.5), so the port derives the size from
its own `source_mintick` instead of hard-coding a second copy of it.

FIDELITY:

* The md prose calls the risk amount "$10" (three times) while the code says
  `risk_per_trade = 0.5`, whose own trailing comment also says "$10 USD". The
  code is followed; the disagreement is recorded, not reconciled.
* `volume_threshold = 1000` is a LITERAL in the source, not an `input()`, and
  the test is a strict `>` (`volume > volume_threshold`), not `>=`.
* The md describes the stop as "$100 below the entry" and the take-profit as
  "$1500 above"; the code measures both from the SIGNAL BAR's close
  (`close - stop_loss_distance`), not from the fill price, so on the fill bar
  the levels sit 100 / 1500 away from the signal bar's close exactly as written.
* `strategy.exit` carries an OCA stop AND an OCA limit leg, and both are
  reproduced; a port carrying only the stop leg would silently lose the
  take-profit (PINE_SEMANTICS.md 1.8).
* Both `strategy.exit` calls happen inside the entry's `if` block, so the exit
  is placed on the signal bar and is already live on the bar the entry fills --
  a zero-length round trip is reachable (PINE_SEMANTICS.md 1.9), and the levels
  reach the framework through `custom_stoploss` / the ROI override rather than
  as projections.
* `initial_capital=100` against a 0.05-contract order at BTC prices commits a
  notional far larger than the account. PINE_SEMANTICS.md 1.6 records that a
  source whose capital is small relative to the venue's contract step makes the
  framework's wallet diverge from the engine's cash; the port keeps the
  source's capital and reports the difference rather than retuning it.
* `currency="USD"` sets the Pine account currency. The engine is an unlevered
  cash simulation in the quote currency, so the declaration has no modelled
  effect and is not reproduced.
* `plot()` / `hline()` output is display-only and is not reproduced.
* Leverage, margin, liquidation, funding and the venue's contract-step rounding
  are not modelled; the chain verifier measures the last one separately.
"""
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase

# Literals in the source, not inputs -- see FIDELITY.
EMA_LENGTH_FAST = 65
EMA_LENGTH_SLOW = 240
VOLUME_THRESHOLD = 1000.0
RISK_PER_TRADE = 0.5
STOP_LOSS_DISTANCE = 100.0
TAKE_PROFIT_DISTANCE = 1500.0


class SMDualCrossoverFixedRisk_a52b9a(PinePortBase, IStrategy):
    source_id = "SM_a52b9a91bb7941ae"
    source_file = (
        "EMA双均线固定风险止损止盈-EMA-Dual-Crossover-Fixed-Risk-Stop-Loss-"
        "Take-Profit.md"
    )
    timeframe = "3m"
    can_short = True
    # The source declares no input() call at all.
    source_defaults: dict = {}
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 100.0
    source_reproduce_stops = True
    # `syminfo.mintick`: TradingView takes it from the symbol and the source
    # never states it. BTC/USDT:USDT quotes in 0.1, the corpus convention.
    source_mintick = 0.1
    source_fidelity_notes = [
        "The md prose calls the per-trade risk amount $10 in three places while "
        "the code is `risk_per_trade = 0.5` (its own comment also says $10 USD). "
        "The code is followed and the disagreement is recorded, not reconciled.",
        "volume_threshold = 1000 is a literal in the source, not an input(), and "
        "the gate is a strict `>` (volume > volume_threshold), not `>=`.",
        "The md describes the stop as $100 below the entry and the take-profit as "
        "$1500 above it; the code measures both from the SIGNAL bar's close, not "
        "from the fill price, and the port reproduces that.",
        "Both legs of the OCA exit (stop and take-profit) are reproduced; a port "
        "with only the stop leg would silently lose the take-profit "
        "(PINE_SEMANTICS.md 1.8).",
        "strategy.exit is called inside the entry's if-block, so the exit is "
        "already live on the bar the entry fills; the levels reach Freqtrade "
        "through custom_stoploss and the ROI override rather than as projected "
        "next-open exit signals (PINE_SEMANTICS.md 1.9).",
        "position_size is derived from syminfo.mintick, which TradingView reads "
        "off the symbol. The source never states it; 0.1 (BTC/USDT:USDT) is the "
        "corpus convention, so the order size is 0.5 / 0.1 / 100 = 0.05 "
        "contracts (PINE_SEMANTICS.md 3.5).",
        "initial_capital = 100 against a 0.05-contract BTC order commits a "
        "notional far larger than the account. The source's capital is kept "
        "rather than retuned; a source whose capital is small relative to the "
        "venue's contract step is a known cause of framework-vs-engine wallet "
        "divergence (PINE_SEMANTICS.md 1.6).",
        "currency = \"USD\" declares the Pine account currency; the engine is an "
        "unlevered cash simulation in the quote currency, so it has no modelled "
        "effect and is not reproduced.",
        "plot() / hline() are display-only and are not reproduced.",
        "Leverage, margin, liquidation, funding and contract-step rounding are "
        "not modelled; the venue's rounding can differ from the engine's float "
        "quantity, which the chain verifier measures separately.",
    ]

    def pine_indicators(self, dataframe, params):
        close = dataframe["close"]
        ema_fast = ta.pine_ema(close, EMA_LENGTH_FAST)
        ema_slow = ta.pine_ema(close, EMA_LENGTH_SLOW)
        # ta.crossover / ta.crossunder: an na operand compares false, so nothing
        # fires before the slow EMA has started.
        bullish_crossover = ta.pine_crossover(ema_fast, ema_slow)
        bearish_crossover = ta.pine_crossunder(ema_fast, ema_slow)
        # `volume > volume_threshold` -- a strict comparison against a literal.
        volume_ok = dataframe["volume"] > VOLUME_THRESHOLD
        dataframe["pine_ema_fast"] = ema_fast
        dataframe["pine_ema_slow"] = ema_slow
        dataframe["pine_long_signal"] = bullish_crossover & volume_ok
        dataframe["pine_short_signal"] = bearish_crossover & volume_ok
        # position_size = risk_per_trade / syminfo.mintick / stop_loss_distance
        dataframe["pine_qty"] = (
            RISK_PER_TRADE / float(self.source_mintick) / STOP_LOSS_DISTANCE
        )
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "close": dataframe["close"].to_numpy(),
            "qty": dataframe["pine_qty"].to_numpy(),
            "long_signal": dataframe["pine_long_signal"].to_numpy(),
            "short_signal": dataframe["pine_short_signal"].to_numpy(),
        }

    def pine_script(self, broker, i, ctx):
        close = float(ctx["close"][i])
        qty = float(ctx["qty"][i])
        # if (bullish_crossover and volume > volume_threshold)
        if ctx["long_signal"][i]:
            #     strategy.entry("Buy", strategy.long, qty=position_size)
            broker.entry("Buy", "long", qty=qty)
            #     strategy.exit("Exit", "Buy", stop=close - stop_loss_distance,
            #                   limit=close + take_profit_distance)
            broker.exit(
                "Exit",
                from_entry="Buy",
                stop=close - STOP_LOSS_DISTANCE,
                limit=close + TAKE_PROFIT_DISTANCE,
            )
        # if (bearish_crossover and volume > volume_threshold)
        if ctx["short_signal"][i]:
            #     strategy.entry("Sell", strategy.short, qty=position_size)
            broker.entry("Sell", "short", qty=qty)
            #     strategy.exit("Exit", "Sell", stop=close + stop_loss_distance,
            #                   limit=close - take_profit_distance)
            broker.exit(
                "Exit",
                from_entry="Sell",
                stop=close + STOP_LOSS_DISTANCE,
                limit=close - TAKE_PROFIT_DISTANCE,
            )
