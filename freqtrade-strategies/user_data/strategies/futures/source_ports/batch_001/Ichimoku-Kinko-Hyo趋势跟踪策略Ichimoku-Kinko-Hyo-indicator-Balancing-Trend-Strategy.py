"""Port of sources/SM_eb5534d162b49443.pine (batch_001/Ichimoku-Kinko-Hyo趋势跟踪策略Ichimoku-Kinko-Hyo-indicator-Balancing-Trend-Strategy.md).

Pine v4. An Ichimoku Kinko Hyo trend filter combined with a hand-rolled RSI, a
momentum (Chikou) confirmation and a volatility floor:

    middle(len) => avg(lowest(len), highest(len))
    tenkan  = middle(ts_bars)                       # 22
    kijun   = middle(ks_bars)                       # 60
    senkouA = avg(tenkan, kijun)
    senkouB = middle(ssb_bars)                      # 120

    ss_high = max(senkouA[ss_offset-1], senkouB[ss_offset-1])   # [29]
    ss_low  = min(senkouA[ss_offset-1], senkouB[ss_offset-1])

    change = change(close); gain = change>=0 ? change : 0; loss = change<0 ? -change : 0
    avgGain = rma(gain,14); avgLoss = rma(loss,14); rs = avgGain/avgLoss
    rsi = 100 - 100/(1 + rs)

    Difference = abs((close - open)/((close + open)/2) * 100)
    highvolatility = sma(Difference, vollength) > voltarget

    bullish = tenkan > kijun and mom(close, cs_offset-1) > 0 and
              close > ss_high and rsi > 50 and highvolatility
    bearish = tenkan < kijun and mom(close, cs_offset-1) < 0 and
              close < ss_low and rs < 50 and highvolatility

    strategy.entry("Long",  strategy.long,  when=bullish and long_entry  and time_cond)
    strategy.entry("Short", strategy.short, when=bearish and short_entry and time_cond)
    strategy.close("Long",  when=bearish and not short_entry and time_cond)
    strategy.close("Short", when=bullish and not long_entry  and time_cond)

`strategy(...)` declares only `title` and `overlay`, so every property is Pine's
documented default: `strategy.fixed` / 1 contract per entry, initial capital
1000000, commission 0%, pyramiding 0, `process_orders_on_close=false`.

The `/*backtest` header declares `period: 3m` on Futures_Binance BTC_USDT, so
`timeframe` is "3m"; its `basePeriod: 1m` is the FMZ backtester's own
granularity for filling those 3m bars, not the strategy's period.

FIDELITY:

* `rsi_bearish` reads `rs`, NOT `rsi` -- `rsi_bearish = rs < 50` where
  `rs = avgGain / avgLoss` is the un-normalised RATIO (1.0 when gains and
  losses balance). It is almost always below 50, so it filters almost nothing
  and it is emphatically not "RSI below 50" as the md's prose claims. This is a
  source bug and it is reproduced literally, not corrected (铁律 2/6).
  `rsi_bullish = rsi > 50` does read the normalised RSI.
* `change(close)` is v4's one-argument `change` = `close - close[1]` (na on the
  first bar). `mom(close, cs_offset-1)` is `close - close[cs_offset-1]`, i.e.
  `close - close[29]`, not a crossing event and not a "Chikou span crossover"
  as the md's prose describes it. Both are reproduced as the code writes them.
* `middle(len)` calls v4's ONE-argument `lowest(len)` / `highest(len)`, whose
  undocumented source defaults are `low` and `high` respectively -- this is the
  standard Ichimoku mid-point. It is NOT `lowest(close, len)`; using close
  would give a different series.
* `senkouA` / `senkouB` are only ever plotted with `offset = ss_offset-1`; the
  trade conditions read them shifted BACK by `ss_offset-1 = 29` bars
  (`senkouA[29]`, `senkouB[29]`). The plotted offset and the read offset are
  different things and only the read matters here; the port reads
  `ss_offset - 1` back, exactly as written.
* The source computes `rs` as `avgGain / avgLoss` and Pine's float division by
  zero yields na, so a window with no losses at all makes `rs`, `rsi` and
  `rsi_bearish` na -> false. The port models that explicitly. This differs from
  Pine's own `ta.rsi`, which returns 100 in that situation; the source does NOT
  call `ta.rsi`, it re-implements the formula, so `pine_ta.pine_rsi` is
  deliberately not used for it.
* `rma` seeds with the SMA of the first `length` observations, which
  `pine_ta.pine_rma` implements.
* `time_cond` is the literal `true`; the `fromDay` / `fromMonth` / `fromYear` /
  `toDay` / `toMonth` / `toYear` inputs only feed `startDate` / `finishDate`,
  which no condition ever reads. The date filter is therefore dead code and the
  port folds `time_cond` away as always true while keeping all six inputs in
  `source_defaults` so the source's parameter list stays on the record.
* The md's argument table lists `From Day` / `From Month` as defaulting to
  `true`; the code says `input(defval = 1, ...)` and
  `input(defval = 1, ...)`. Code followed, md table artifact recorded.
* The md's prose says entry 3 is "Chikou Span crossover upward" and entry 6 is
  "RSI below 50". The code's Chikou test is `mom(close, 29) > 0` and its
  bearish RSI test is `rs < 50` (see above). Recorded, not reconciled.
* `long_entry` and `short_entry` both default to true, so both `strategy.close`
  calls are dead with the declared defaults (`bearish and not short_entry` is
  false). They are still written, and they do fire if either input is
  overridden, so the parameter is carried rather than folded away. With both
  true, a position is only ever reversed by the opposite entry.
* No stop / limit / profit / loss / trail exit exists anywhere in the source --
  the only exits are the two `strategy.close` calls -- so
  `source_reproduce_stops` is False and a position open at the window's end
  stays open.
* `ta.rma`'s seeding and `ta.sma`'s na propagation (PINE_SEMANTICS.md 3.2/3.3)
  apply to the RSI and to the volatility average; no `ta.ema` is used, so the
  unpublished EMA seeding rule of 3.1 does not apply.
* `plot` / `fill` and the strategy title are display-only and are not
  reproduced.
* The source calls itself "ETH 3h" in its title, but the header declares
  `period: 3m` on BTC_USDT. The header is the backtest's own declaration and is
  what `timeframe` is taken from; the title is not a parameter of the backtest.
* Leverage, margin, liquidation, funding and the venue's contract-step rounding
  are not modelled; the step can only be read off the exchange object at run
  time, so the framework and the engine may differ by a rounded quantity, which
  the chain verifier measures separately rather than treating as a signal
  difference.
"""
import numpy as np
import pandas as pd
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


class SMIchimokuKinkoHyo_eb5534(PinePortBase, IStrategy):
    source_id = "SM_eb5534d162b49443"
    source_file = (
        "Ichimoku-Kinko-Hyo趋势跟踪策略"
        "Ichimoku-Kinko-Hyo-indicator-Balancing-Trend-Strategy.md"
    )
    timeframe = "3m"
    can_short = True
    source_defaults: dict = {
        "ts_bars": 22,
        "ks_bars": 60,
        "ssb_bars": 120,
        "cs_offset": 30,
        "ss_offset": 30,
        "long_entry": True,
        "short_entry": True,
        "vollength": 2,
        "voltarget": 0.2,
        # Only used to build startDate / finishDate, which nothing reads.
        "fromDay": 1,
        "fromMonth": 1,
        "fromYear": 2019,
        "toDay": 31,
        "toMonth": 12,
        "toYear": 2020,
    }
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    source_reproduce_stops = False
    source_fidelity_notes = [
        "strategy() declares only title and overlay, so fixed qty 1, initial "
        "capital 1000000, commission 0%, pyramiding 0 and "
        "process_orders_on_close=false are Pine's documented defaults.",
        "`rsi_bearish = rs < 50` reads the RATIO avgGain/avgLoss, not the RSI; "
        "the md's prose calls it 'RSI below 50'. Source bug reproduced "
        "literally rather than corrected.",
        "`mom(close, cs_offset-1)` is `close - close[29]`, a difference, not a "
        "crossing; the md's prose calls it 'Chikou Span crossover'.",
        "v4's one-argument lowest()/highest() default to `low`/`high`, so "
        "middle(len) is the standard Ichimoku mid-point and NOT a close-based "
        "mid-point.",
        "senkouA/senkouB are plotted with offset ss_offset-1 but the conditions "
        "read them shifted BACK by ss_offset-1 = 29 bars; only the read matters "
        "and it is reproduced as written.",
        "The source re-implements RSI with avgGain/avgLoss instead of calling "
        "ta.rsi; Pine's float division by zero yields na, so a window with no "
        "losses makes rs/rsi na and rsi_bearish false. Modelled explicitly; "
        "pine_ta.pine_rsi (which returns 100 in that case) is deliberately not "
        "used for it.",
        "`time_cond` is the literal true. The six from/to date inputs only feed "
        "startDate/finishDate, which no condition reads -- dead code. Kept in "
        "source_defaults, folded away from the conditions.",
        "The md's argument table gives From Day / From Month a default of "
        "`true`; the code's input(defval = 1) defaults to 1. Code followed.",
        "long_entry and short_entry both default to true, so both strategy.close "
        "calls are dead with the declared defaults; they are still written and "
        "do fire if either input is overridden.",
        "No stop/limit/profit/loss/trail exit exists; the only exits are the two "
        "strategy.close calls, so source_reproduce_stops is False and a position "
        "open at the window's end stays open.",
        "The source's title says 'ETH 3h' while the header declares period: 3m "
        "on BTC_USDT; the header is what timeframe is taken from.",
        "rma seeds with the SMA of the first `length` observations and sma "
        "propagates na inside its window (PINE_SEMANTICS.md 3.2/3.3). No ta.ema "
        "is used, so the seeding risk of 3.1 does not apply.",
        "plot/fill and the strategy title are display-only and are not "
        "reproduced.",
        "Leverage, margin, liquidation, funding and contract-step rounding are "
        "not modelled; the venue's rounding can differ from the engine's float "
        "quantity, which the chain verifier measures separately.",
    ]

    def pine_indicators(self, dataframe, params):
        high = dataframe["high"]
        low = dataframe["low"]
        close = dataframe["close"]
        open_ = dataframe["open"]

        ts_bars = int(params["ts_bars"])
        ks_bars = int(params["ks_bars"])
        ssb_bars = int(params["ssb_bars"])
        cs_lag = int(params["cs_offset"]) - 1
        ss_lag = int(params["ss_offset"]) - 1
        vollength = int(params["vollength"])
        voltarget = float(params["voltarget"])
        long_entry = bool(params["long_entry"])
        short_entry = bool(params["short_entry"])

        def middle(length):
            # middle(len) => avg(lowest(len), highest(len))
            # v4's bare lowest()/highest() read `low` / `high`.
            return (ta.pine_lowest(low, length) + ta.pine_highest(high, length)) / 2.0

        tenkan = middle(ts_bars)
        kijun = middle(ks_bars)
        senkou_a = (tenkan + kijun) / 2.0          # avg(tenkan, kijun)
        senkou_b = middle(ssb_bars)

        # ss_high = max(senkouA[ss_lag], senkouB[ss_lag]); ss_low = min(...)
        ss_high = np.maximum(senkou_a.shift(ss_lag), senkou_b.shift(ss_lag))
        ss_low = np.minimum(senkou_a.shift(ss_lag), senkou_b.shift(ss_lag))

        # Hand-rolled RSI (the source does not call ta.rsi).
        change = ta.pine_change(close, 1)
        # na >= 0 is falsy in Pine, so the first bar contributes 0.0, not na.
        gain = pd.Series(
            np.where(change >= 0, change.to_numpy(dtype=float), 0.0),
            index=close.index, dtype=float,
        )
        loss = pd.Series(
            np.where(change < 0, -change.to_numpy(dtype=float), 0.0),
            index=close.index, dtype=float,
        )
        avg_gain = ta.pine_rma(gain, 14)
        avg_loss = ta.pine_rma(loss, 14)
        # Pine's float division by zero is na, and an na comparison is false.
        rs = avg_gain / avg_loss.replace(0.0, np.nan)
        rsi = 100.0 - (100.0 / (1.0 + rs))

        # Volatility floor
        difference = (
            (close - open_) / ((close + open_) / 2.0) * 100.0
        ).abs()
        moving_average = ta.pine_sma(difference, vollength)
        highvolatility = moving_average > voltarget

        # Entry/exit signal terms
        tk_cross_bull = tenkan > kijun
        tk_cross_bear = tenkan < kijun
        cs_cross_bull = ta.pine_change(close, cs_lag) > 0
        cs_cross_bear = ta.pine_change(close, cs_lag) < 0
        price_above_kumo = close > ss_high
        price_below_kumo = close < ss_low
        rsi_bullish = rsi > 50
        rsi_bearish = rs < 50
        bullish = (
            tk_cross_bull & cs_cross_bull & price_above_kumo & rsi_bullish
            & highvolatility
        )
        bearish = (
            tk_cross_bear & cs_cross_bear & price_below_kumo & rsi_bearish
            & highvolatility
        )

        dataframe["pine_tenkan"] = tenkan
        dataframe["pine_kijun"] = kijun
        dataframe["pine_senkou_a"] = senkou_a
        dataframe["pine_senkou_b"] = senkou_b
        dataframe["pine_ss_high"] = ss_high
        dataframe["pine_ss_low"] = ss_low
        dataframe["pine_rs"] = rs
        dataframe["pine_rsi"] = rsi
        dataframe["pine_highvolatility"] = highvolatility
        dataframe["pine_bullish"] = bullish.fillna(False)
        dataframe["pine_bearish"] = bearish.fillna(False)

        # The four order conditions, with the entry inputs and the constant
        # `time_cond = true` folded in.
        dataframe["pine_entry_long"] = dataframe["pine_bullish"] & long_entry
        dataframe["pine_entry_short"] = dataframe["pine_bearish"] & short_entry
        dataframe["pine_close_long"] = dataframe["pine_bearish"] & (not short_entry)
        dataframe["pine_close_short"] = dataframe["pine_bullish"] & (not long_entry)
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "entry_long": dataframe["pine_entry_long"].to_numpy(),
            "entry_short": dataframe["pine_entry_short"].to_numpy(),
            "close_long": dataframe["pine_close_long"].to_numpy(),
            "close_short": dataframe["pine_close_short"].to_numpy(),
        }

    def pine_script(self, broker, i, ctx):
        # strategy.entry("Long", strategy.long, when=bullish and long_entry and time_cond)
        if ctx["entry_long"][i]:
            broker.entry("Long", "long")
        # strategy.entry("Short", strategy.short, when=bearish and short_entry and time_cond)
        if ctx["entry_short"][i]:
            broker.entry("Short", "short")
        # strategy.close("Long", when=bearish and not short_entry and time_cond)
        if ctx["close_long"][i]:
            broker.close("Long")
        # strategy.close("Short", when=bullish and not long_entry and time_cond)
        if ctx["close_short"][i]:
            broker.close("Short")
