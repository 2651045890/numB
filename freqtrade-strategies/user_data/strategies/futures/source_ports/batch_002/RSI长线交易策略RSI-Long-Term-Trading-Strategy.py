"""Port of sources/SM_fcd1b3a2f0b55047.pine (batch_002/RSI长线交易策略RSI-Long-Term-Trading-Strategy.md).

Pine v2. "RSI Long Term": a 20-period RSI computed over the SUM of the close and
open series gates a bar-body momentum test over the last three bars, against a
stale three-bar body test at lags 4/5/6:

    RSI           = rsi(sum(close, 20) + sum(open, 20), 20)
    Sum_OF_3_Both = sum((close - open) * 100000, 3)
    Up_Move       = ((close - open) * 100000) < 35
    Down_Move     = ((close[6]-open[6])*100000 + (close[5]-open[5])*100000
                     + (close[4]-open[4])*100000) < -400

    if Sum_OF_3_Both > 350 and Up_Move:
        strategy.entry("Bar Up Buy", strategy.long)
    if Sum_OF_3_Both < -200 and Down_Move and RSI > 30.1:
        strategy.entry("Bar Down Sell ", strategy.short)

`sum(source, length)` is Pine v2's rolling sum (the later `math.sum`); `pine_ta.
pine_sum` supplies it. `rsi` is Pine's Wilder-smoothed ta.rsi -- `pine_ta.
pine_rsi` -- and NOT a simple average, so the RSI here is the same function the
KST port uses, not a re-derivation.

The `* 100000` scaling is part of the source's own arithmetic and its thresholds
are read on that scale, so it is kept literally: on a 1d BTC bar the scale makes
the thresholds near-degenerate (a 100 USDT body is 1e7 on this scale, against a
threshold of 350), and the conditions therefore reduce mostly to the SIGN of the
three-bar body sum plus the two colour tests. That is what the source says, and
simplifying it would be a different strategy.

`strategy()` declares only `title`, `overlay`, `default_qty_type =
strategy.percent_of_equity` and `default_qty_value = 10`, so everything else is
Pine's documented default: initial capital 1000000, commission 0%, pyramiding 0,
`process_orders_on_close=false`.

There is NO exit call. A position is closed only by the opposite entry reversing
it, so `source_reproduce_stops` is False and a position open at the end of the
window stays open.

FIDELITY:

* `strategy.risk.max_intraday_loss(maxIdLossPcnt, strategy.percent_of_equity)` is
  COMMENTED OUT in the source and is not restored; `strategy.risk.*` is in any
  case not modelled by the engine (PINE_SEMANTICS.md section 二.3). The
  `maxIdLossPcnt` input it referenced is still declared by the source, so it is
  carried in `source_defaults` and read by nothing.
* The short entry's id is `"Bar Down Sell "` WITH A TRAILING SPACE. Kept
  verbatim: the id is the source's own string and nothing here renames it.
* The md prose puts the RSI filter on the LONG leg ("上涨趋势同时RSI大于30时做
  多"). The code applies `RSI > 30.1` to the SHORT leg and tests no RSI on the
  long leg at all. Code followed, disagreement recorded.
* The md calls the 3-bar test a test of "收盘价变动" (close changes) and the
  thresholds 350 / -200; the code accumulates `(close - open) * 100000`, i.e.
  bar BODIES, and the short leg additionally re-tests the bodies at lags 4, 5 and
  6, which the md never mentions. Code followed, both recorded.
* `Up_Move` carries an explicit `close[0]` / `open[0]`: index zero is the current
  bar, not a one-bar back reference. Read as the current bar's body.
* `[4]` / `[5]` / `[6]` are true history references, so the first three values
  of `Down_Move` are na and the short leg cannot fire before bar 6.
* `sum` returns na until its window is full, and `sum(close, 20) + sum(open, 20)`
  is therefore na before bar 19. `rsi` then needs its own Wilder warm-up, so the
  short leg cannot fire before roughly bar 39 (PINE_SEMANTICS.md section 3.3
  records the RSI boundary as a modelled choice, not a certified one).
* No stop, limit or take-profit order exists anywhere in the source, so
  `source_reproduce_stops` is False; the md's "未考虑止损策略" is a plain
  description of the code.
* Pine's `strategy.entry` SETS the position to the order's quantity, so an
  opposite entry reverses in one order (`qty + |position|`); the engine models
  that (PINE_SEMANTICS.md 1.1).
* `percent_of_equity` / 10 is sized from the engine's own recorded fill notional
  rather than re-derived from the live wallet (PINE_SEMANTICS.md 1.4, 1.5).
* The `/*backtest` header declares `period: 1d` on Futures_Binance BTC_USDT, so
  `timeframe` is "1d"; its `basePeriod: 1h` is the FMZ backtester's granularity
  for filling those 1d bars, not the strategy's period, and the header's
  `start` / `end` window is not applied (PINE_SEMANTICS.md section 二.8).
* The `// use with eurusd h1 , gbpusd h1` comment is a free-text note, not a
  period declaration; the header's `period: 1d` is what the source was run on.
* Leverage, margin, liquidation, funding and the venue's contract-step rounding
  are not modelled (PINE_SEMANTICS.md 二.4, 1.6).
"""
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


class SMRsiLongTerm_fcd1b3(PinePortBase, IStrategy):
    source_id = "SM_fcd1b3a2f0b55047"
    source_file = "RSI长线交易策略RSI-Long-Term-Trading-Strategy.md"
    timeframe = "1d"
    can_short = True
    source_defaults: dict = {"maxIdLossPcnt": 10.0}
    source_qty_type = "percent_of_equity"
    source_qty_value = 10.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    source_reproduce_stops = False
    source_fidelity_notes = [
        "strategy.risk.max_intraday_loss is COMMENTED OUT in the source and is "
        "not restored; strategy.risk.* is unmodelled anyway (PINE_SEMANTICS.md "
        "section 二.3). The maxIdLossPcnt input it referenced is declared and "
        "read by nothing.",
        "The short entry's id is \"Bar Down Sell \" with a TRAILING SPACE; kept "
        "verbatim.",
        "The md puts the RSI filter on the LONG leg; the code applies RSI > 30.1 "
        "to the SHORT leg and tests no RSI on the long leg. Code followed, "
        "disagreement recorded.",
        "The md calls the 3-bar test a test of close changes; the code "
        "accumulates (close - open) * 100000 -- bar BODIES -- and the short leg "
        "re-tests the bodies at lags 4/5/6, which the md omits. Code followed.",
        "close[0] / open[0] are the CURRENT bar, not a one-bar back reference.",
        "lags [4]/[5]/[6] are true history references, so the short leg cannot "
        "fire before bar 6; sum(close,20)+sum(open,20) is na before bar 19 and "
        "rsi's own Wilder warm-up pushes the short leg to roughly bar 39.",
        "The * 100000 scale is the source's own arithmetic and its thresholds "
        "350 / -200 / -400 / 35 are read on that scale; kept literally rather "
        "than rescaled into price units.",
        "No stop / limit / take-profit order exists, so source_reproduce_stops is "
        "False and a position open at the end of the window stays open.",
        "Pine's entry SETS the position to the order quantity, so a reversal "
        "fills qty + |position| in one order (PINE_SEMANTICS.md 1.1).",
        "percent_of_equity / 10 is reproduced from the engine's recorded fill "
        "notional rather than re-derived from the live wallet (1.4, 1.5).",
        "The /*backtest header's period:1d sets the timeframe; basePeriod:1h is "
        "the FMZ backtester's fill granularity and the header's start/end window "
        "is not applied (PINE_SEMANTICS.md section 二.8). The "
        "`// use with eurusd h1, gbpusd h1` comment is a free-text note, not a "
        "period declaration.",
        "Leverage, margin, liquidation, funding and the venue's contract-step "
        "rounding are not modelled (PINE_SEMANTICS.md 二.4, 1.6).",
    ]

    def pine_indicators(self, dataframe, params):
        close = dataframe["close"]
        open_ = dataframe["open"]
        body = (close - open_) * 100000.0
        # RSI = (rsi(sum(close , 20) + sum(open ,20) , 20))
        combined = ta.pine_sum(close, 20) + ta.pine_sum(open_, 20)
        rsi = ta.pine_rsi(combined, 20)
        # Sum_OF_3_Both = sum((close - open)*100000 , 3)
        sum_of_3_both = ta.pine_sum(body, 3)
        # Up_Move = ((close[0] - open[0])*100000) < 35
        up_move = body < 35.0
        # Down_Move = ((close[6]-open[6])*100000) + ((close[5]-open[5])*100000)
        #             + ((close[4]-open[4])*100000) < -400
        down_move = (
            ((close.shift(6) - open_.shift(6)) * 100000.0)
            + ((close.shift(5) - open_.shift(5)) * 100000.0)
            + ((close.shift(4) - open_.shift(4)) * 100000.0)
        ) < -400.0
        dataframe["pine_rsi_sum"] = rsi
        dataframe["pine_sum_of_3_both"] = sum_of_3_both
        dataframe["pine_up_move"] = up_move
        dataframe["pine_down_move"] = down_move
        dataframe["pine_long_condition"] = (sum_of_3_both > 350.0) & up_move
        dataframe["pine_short_condition"] = (
            (sum_of_3_both < -200.0) & down_move & (rsi > 30.1)
        )
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "rsi": dataframe["pine_rsi_sum"].to_numpy(),
            "sum_of_3_both": dataframe["pine_sum_of_3_both"].to_numpy(),
            "long_condition": dataframe["pine_long_condition"].to_numpy(),
            "short_condition": dataframe["pine_short_condition"].to_numpy(),
        }

    def pine_script(self, broker, i, ctx):
        # if (Sum_OF_3_Both > 350 and Up_Move )
        #     strategy.entry("Bar Up Buy", strategy.long)
        if ctx["long_condition"][i]:
            broker.entry("Bar Up Buy", "long")
        # if (Sum_OF_3_Both < -200  and Down_Move and RSI > 30.1  )
        #     strategy.entry("Bar Down Sell ", strategy.short)
        if ctx["short_condition"][i]:
            broker.entry("Bar Down Sell ", "short")
