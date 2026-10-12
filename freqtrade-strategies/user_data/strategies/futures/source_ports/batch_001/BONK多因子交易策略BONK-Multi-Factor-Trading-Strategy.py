"""Port of sources/SM_159ab3e64c5a3ccc.pine (batch_001/BONK多因子交易策略BONK-Multi-Factor-Trading-Strategy.md).

Pine v5. Four filters ANDed into one entry condition on each side:

    emaShort = ta.ema(close, emaShortLength)          // 9
    emaLong  = ta.ema(close, emaLongLength)           // 20
    [macdLine, signalLine, _] = ta.macd(close, 12, 26, 9)
    rsi      = ta.rsi(close, rsiLength)               // 14
    volumeMA = ta.sma(volume, 20)

    buyCondition  = ta.crossover(emaShort, emaLong)   and (macdLine > signalLine)
                    and (rsi < rsiOverbought)         and (volume > volumeMA)
    sellCondition = ta.crossunder(emaShort, emaLong)  and (macdLine < signalLine)
                    and (rsi > rsiOversold)           and (volume > volumeMA)

    longStopLoss   = close * 0.95
    longTakeProfit = close * 1.05
    shortStopLoss  = close * 1.05
    shortTakeProfit = close * 0.95

    if (buyCondition)
        strategy.entry("Buy",  strategy.long,  stop=longStopLoss,  limit=longTakeProfit)
    if (sellCondition)
        strategy.entry("Sell", strategy.short, stop=shortStopLoss, limit=shortTakeProfit)

The `stop=` / `limit=` arguments belong to the ENTRY ORDER, not to an exit.
Pine's `strategy.entry` documents them as the entry's own stop / limit prices
("stop-limit only when the limit parameter is also specified"), so this source
places a stop-limit ENTRY, not a bracket with a 5% stop and a 5% target. There
is no `strategy.exit` / `strategy.close` anywhere: a position is only ever
closed or reversed by the opposite entry, so `source_reproduce_stops` is False
and a position open at the end of the window stays open.

Placement is reproduced exactly (`stop=` and `limit=` both forwarded); what the
shared engine then does with a stop-limit entry is recorded under FIDELITY.

`strategy("BONK Trading Bot ...", overlay=true)` declares only `title` and
`overlay`, so qty type `strategy.fixed` / 1 contract, initial capital 1000000,
commission 0%, `pyramiding` 0 and `process_orders_on_close=false` are Pine's
documented defaults.

The `/*backtest` header declares `period: 1d` on Futures_Binance BTC_USDT;
`basePeriod: 1h` is the FMZ backtester's own fill granularity for those daily
bars, not the strategy's period.

FIDELITY:

* md-vs-source: the md prose says the strategy "sets stop loss and take profit
  levels ... for longs the stop is 95% of the entry and the target 105%", i.e.
  an exit bracket. The code passes those two prices to `strategy.entry`, where
  they are ENTRY-order parameters. The code is what is reproduced; the prose is
  recorded, not reconciled.
* MODELLED CHOICE (shared engine, not this port): `PineBroker.entry` classifies
  an entry carrying both `stop` and `limit` as kind `"stop"` and
  `_price_order_fill` reads only the stop leg, so the fill is
  `max(stop, open)` for a long. Pine's own semantics for a stop-limit entry are
  a two-leg order (the stop arms it, the limit caps its price), which the
  engine does not model. For this source the long stop sits 5% BELOW the
  placement close, so it is already breached before the next bar opens and the
  engine fills at that bar's open -- the same price a plain market entry
  projected to the next open would get. That coincidence makes the two sides
  agree here, but it is a property of these levels, not a demonstration that
  the stop-limit model is equivalent. Recorded, not corrected.
* PINE_SEMANTICS.md 2.11 (resting stop/limit entries cannot be projected to
  Freqtrade) covers the general case; the specific stop-and-limit-entry shape
  above is the one this source uses.
* `volumeMA` is `ta.sma(volume, 20)` over the CURRENT bar and the 19 before it;
  it is not shifted. The comparison is `volume > volumeMA`, strictly greater,
  and the current bar's volume is part of the average it is compared against.
* `ta.macd` returns three series; the source discards the histogram (`_`) and
  re-derives `macdHist = macdLine - signalLine` for plotting only. The port
  keeps the same two series and never reads the histogram for a condition.
* `rsi < rsiOverbought` / `rsi > rsiOversold` are the two guards; the side that
  would be "overbought" blocks the LONG and the "oversold" level blocks the
  SHORT, i.e. the levels filter out the side they would normally warn about.
  Reproduced as written.
* No `input(type=bool)` value is compared numerically, so
  PINE_SEMANTICS.md 1.16 does not apply.
* `ta.ema` follows pine_ta's first-value seeding, and `ta.rsi` pine_ta's RMA
  seeding; both are listed as parity risks (PINE_SEMANTICS.md 3.1, 3.3).
* `plot` / `hline` / `plotshape` are display-only and place no condition.
* Leverage, margin, liquidation, funding and the venue's contract-step
  rounding are not modelled; the chain verifier measures the rounding
  separately.
"""
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


class SMBonkMultiFactorTradingStrategy_159ab3(PinePortBase, IStrategy):
    source_id = "SM_159ab3e64c5a3ccc"
    source_file = "BONK多因子交易策略BONK-Multi-Factor-Trading-Strategy.md"
    timeframe = "1d"
    can_short = True
    source_defaults: dict = {
        "emaShortLength": 9,
        "emaLongLength": 20,
        "macdFastLength": 12,
        "macdSlowLength": 26,
        "macdSignalSmoothing": 9,
        "rsiLength": 14,
        "rsiOverbought": 70,
        "rsiOversold": 30,
    }
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    source_reproduce_stops = False
    source_fidelity_notes = [
        "The stop=/limit= arguments sit on strategy.entry, so this source places "
        "a stop-limit ENTRY, not a 5% stop / 5% target bracket. There is no "
        "strategy.exit or strategy.close, hence source_reproduce_stops is False "
        "and a position open at the window end stays open.",
        "md-vs-source: the md prose describes an exit stop loss at 95% and take "
        "profit at 105% of the entry. The code passes those prices to "
        "strategy.entry, where they are entry-order parameters. The code is "
        "reproduced; the prose is recorded, not reconciled.",
        "MODELLED CHOICE (shared engine, not this port): an entry carrying both "
        "stop and limit is classified kind='stop' and only its stop leg is read, "
        "so the long fills at max(stop, open). Pine models a stop-limit as two "
        "legs. Here the long stop sits 5% BELOW the placement close and is "
        "already breached, so the engine fills at the next open -- the same "
        "price a projected market entry gets -- which is why the two sides "
        "agree, not evidence that the stop-limit model is equivalent.",
        "PINE_SEMANTICS.md 2.11 (resting stop/limit entries cannot be projected) "
        "covers the general case of this order shape.",
        "volumeMA is ta.sma(volume, 20) over the current bar and the 19 before "
        "it -- not shifted -- and the test is a strict `volume > volumeMA`.",
        "ta.macd's histogram output is discarded by the source and re-derived "
        "for plotting only; no condition reads it.",
        "The RSI guards filter the side they would normally warn about: "
        "`rsi < rsiOverbought` gates the LONG and `rsi > rsiOversold` gates the "
        "SHORT. Reproduced as written.",
        "No input(type=bool) is compared numerically, so PINE_SEMANTICS.md 1.16 "
        "does not apply.",
        "ta.ema uses pine_ta's first-value seeding (PINE_SEMANTICS.md 3.1) and "
        "ta.rsi its RMA seeding (3.3); both are recorded parity risks.",
        "plot/hline/plotshape are display-only and place no condition.",
        "Leverage, margin, liquidation, funding and the venue's contract-step "
        "rounding are not modelled; the chain verifier measures the rounding "
        "separately.",
    ]

    def pine_indicators(self, dataframe, params):
        close = dataframe["close"]
        ema_short = ta.pine_ema(close, int(params["emaShortLength"]))
        ema_long = ta.pine_ema(close, int(params["emaLongLength"]))
        macd = ta.pine_macd(
            close,
            int(params["macdFastLength"]),
            int(params["macdSlowLength"]),
            int(params["macdSignalSmoothing"]),
        )
        macd_line = macd["macd"]
        signal_line = macd["signal"]
        rsi = ta.pine_rsi(close, int(params["rsiLength"]))
        volume_ma = ta.pine_sma(dataframe["volume"], 20)

        volume_ok = (dataframe["volume"] > volume_ma).fillna(False)
        dataframe["pine_ema_short"] = ema_short
        dataframe["pine_ema_long"] = ema_long
        dataframe["pine_macd_line"] = macd_line
        dataframe["pine_macd_signal"] = signal_line
        dataframe["pine_rsi"] = rsi
        dataframe["pine_volume_ma"] = volume_ma
        dataframe["pine_long_condition"] = (
            ta.pine_crossover(ema_short, ema_long)
            & (macd_line > signal_line).fillna(False)
            & (rsi < float(params["rsiOverbought"])).fillna(False)
            & volume_ok
        ).fillna(False)
        dataframe["pine_short_condition"] = (
            ta.pine_crossunder(ema_short, ema_long)
            & (macd_line < signal_line).fillna(False)
            & (rsi > float(params["rsiOversold"])).fillna(False)
            & volume_ok
        ).fillna(False)
        # The entry order's own stop / limit legs, as the source computes them.
        dataframe["pine_long_entry_stop"] = close * 0.95
        dataframe["pine_long_entry_limit"] = close * 1.05
        dataframe["pine_short_entry_stop"] = close * 1.05
        dataframe["pine_short_entry_limit"] = close * 0.95
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "long_condition": dataframe["pine_long_condition"].to_numpy(),
            "short_condition": dataframe["pine_short_condition"].to_numpy(),
            "long_stop": dataframe["pine_long_entry_stop"].to_numpy(),
            "long_limit": dataframe["pine_long_entry_limit"].to_numpy(),
            "short_stop": dataframe["pine_short_entry_stop"].to_numpy(),
            "short_limit": dataframe["pine_short_entry_limit"].to_numpy(),
        }

    def pine_script(self, broker, i, ctx):
        # if (buyCondition)
        #     strategy.entry("Buy", strategy.long, stop=longStopLoss, limit=longTakeProfit)
        if ctx["long_condition"][i]:
            broker.entry("Buy", "long", stop=ctx["long_stop"][i],
                         limit=ctx["long_limit"][i])
        # if (sellCondition)
        #     strategy.entry("Sell", strategy.short, stop=shortStopLoss, limit=shortTakeProfit)
        if ctx["short_condition"][i]:
            broker.entry("Sell", "short", stop=ctx["short_stop"][i],
                         limit=ctx["short_limit"][i])
