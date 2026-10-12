"""Port of sources/SM_eec77b430f7e2f35.pine (batch_001/GM-8-ADX-双均线策略-GM-8-ADX-Dual-Moving-Average-Strategy.md).

Pine v5. A moving-average cross filtered by a hand-rolled directional-index
reading and by a second, much longer EMA:

    adx(high, low, close, length) =>        # note: NOT ta.dmi
        sum_truerange = 0.0; sum_plusDM = 0.0; sum_minusDM = 0.0
        for i = 1 to length                 # bars [t-length .. t-1], NOT bar t
            tr = max(high[i]-low[i], high[i]-close[i-1], low[i]-close[i-1])
            plusDM  = (high[i]-high[i-1] > low[i-1]-low[i]) and
                      (high[i]-high[i-1] > 0) ? high[i]-high[i-1] : 0
            minusDM = (low[i-1]-low[i] > high[i]-high[i-1]) and
                      (low[i-1]-low[i] > 0) ? low[i-1]-low[i] : 0
        plusDI = sum_plusDM/sum_truerange*100; minusDI = sum_minusDM/sum_truerange*100
        adx_value = 100 * (plusDI - minusDI) / (plusDI+minusDI == 0 ? 1 : plusDI+minusDI)

    gm_8       = ta.sma(close, gm_period)          # 15, despite the "GM-8" naming
    second_ema = ta.ema(close, second_ema_period)  # 59

    buy_condition  = ta.crossover(close, gm_8)  and close > gm_8 and
                     close > second_ema and adx_value > adx_threshold
    sell_condition = ta.crossunder(close, gm_8) and close < gm_8 and
                     close < second_ema and adx_value > adx_threshold

    if buy_condition  -> strategy.entry("Buy",  strategy.long,  qty=lot_size)
    if sell_condition -> strategy.entry("Sell", strategy.short, qty=lot_size)

    exit_buy_condition  = ta.crossunder(close, gm_8) and close < gm_8
    exit_sell_condition = ta.crossover(close, gm_8)  and close > gm_8

    if exit_buy_condition  -> strategy.close("Buy")
    if exit_sell_condition -> strategy.close("Sell")

`strategy("GM-8 and ADX Strategy with Second EMA", overlay=true)` declares only
`title` and `overlay`, so every property is Pine's documented default:
`strategy.fixed` / 1 contract, initial capital 1000000, commission 0%,
pyramiding 0, `process_orders_on_close=false`. Both entries pass an explicit
`qty=lot_size`, so `default_qty_value` is never read; it is kept as Pine's
default 1 in `source_qty_value` for the record.

The `/*backtest` header declares `period: 1d` on Futures_Binance BTC_USDT, so
`timeframe` is "1d"; its `basePeriod: 1h` is the FMZ backtester's own
granularity for filling those daily bars, not the strategy's period.

FIDELITY:

* The `adx()` helper is NOT an ADX and not a DI pair either: it is a plain
  directional index `100*(plusDI-minusDI)/(plusDI+minusDI)`, computed from
  BULK SUMS over the window (not Wilder-smoothed), and the loop runs
  `for i = 1 to length`, so it reads bars `t-1 .. t-length` and NEVER bar `t`.
  All three of those are reproduced literally rather than replaced by
  `pine_ta.pine_atr` / a library ADX -- the values differ.
* The helper's output is SIGNED: `100*(plusDI-minusDI)/(plusDI+minusDI)` ranges
  over [-100, 100], not over [0, 100] like a real ADX. Both the buy and the
  SELL condition test the SAME comparison `adx_value > adx_threshold`, so a
  short requires a strongly POSITIVE (bullish) directional reading. The
  short side is therefore much rarer than a symmetric reading would make it.
  Reproduced literally; it looks like the author intended an unsigned strength
  measure and it is not corrected (铁律 2/6).
* The helper's true-range triple has no `abs()`: `max(high[i]-low[i],
  high[i]-close[i-1], low[i]-close[i-1])`. On a gap-down bar (previous close
  above the current high) both difference terms are negative and the expression
  collapses to `high-low`, where the textbook TR would be `close[1]-low`. That
  is a divergence from standard TR, and it is reproduced rather than corrected.
  The comparisons are Pine ternaries, so an na operand selects the other branch
  (it does not poison the result) -- written with `Series.where`, not
  `np.maximum`, so the first bars behave the same way.
* Plus/minus DM use `and` of two comparisons, and Pine's na comparison is
  false, so the earliest bars contribute 0 to those sums rather than na -- which
  is why `sum_truerange` becomes complete one bar before the DM sums do.
* The md's prose calls the short-horizon average "GM-8" and the strategy
  "GM-8 and ADX"; the input is `input(15, title="GM-15 Period")` and feeds
  `ta.sma(close, 15)`. The code is followed; both namings are recorded.
* `second_ema = ta.ema(close, 59)`. TradingView does not publish its EMA
  seeding rule; pine_ta.pine_ema seeds with the first non-na observation and
  does not advance on na. PINE_SEMANTICS.md 3.1 records this as an unresolved
  parity risk, not certified equivalence.
* The four calls are written unconditionally and in source order:
  entry Buy, entry Sell, close Buy, close Sell. `buy_condition` and
  `sell_condition` are mutually exclusive (a cross above and a cross below the
  same line cannot both hold), and the exits require the opposite cross, so no
  enter/exit pair can collide on one bar.
* The `strategy.close` calls name entry ids ("Buy" / "Sell") and are no-ops
  when that id is not held, which the engine's `from_entry` matching honours
  (PINE_SEMANTICS.md 1.12).
* No stop / limit / profit / loss / trail exit exists anywhere in the source --
  the only exits are the two `strategy.close` calls -- so
  `source_reproduce_stops` is False and a position open at the window's end
  stays open.
* `sma` is na until its window is full and na propagates inside the window;
  na comparisons are false, so nothing fires before 15 bars have elapsed, and
  the DX needs 10 bars of its own.
* The `for` loop and its accumulator variables are re-initialised on every bar
  (they are function locals), which is what the vectorised form here does too.
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


class SMGm8AdxDualMa_eec77b(PinePortBase, IStrategy):
    source_id = "SM_eec77b430f7e2f35"
    source_file = "GM-8-ADX-双均线策略-GM-8-ADX-Dual-Moving-Average-Strategy.md"
    timeframe = "1d"
    can_short = True
    source_defaults: dict = {
        "gm_period": 15,
        "second_ema_period": 59,
        "adx_period": 8,
        "adx_threshold": 34,
        "lot_size": 0.4,
    }
    source_qty_type = "fixed"
    # Not declared by strategy(), so Pine's default 1. Never read: both entries
    # pass an explicit qty=lot_size.
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    source_reproduce_stops = False
    source_fidelity_notes = [
        "strategy() declares only title and overlay, so fixed qty, initial "
        "capital 1000000, commission 0%, pyramiding 0 and "
        "process_orders_on_close=false are Pine's documented defaults. Both "
        "entries pass an explicit qty=lot_size, so default_qty_value=1 is never "
        "read; it is kept in source_qty_value for the record.",
        "The source's adx() helper is not an ADX (no Wilder smoothing) and not a "
        "DI pair: it is 100*(plusDI-minusDI)/(plusDI+minusDI) from bulk sums "
        "over the window. Reproduced literally instead of using a library ATR/DX.",
        "The helper loops `for i = 1 to length`, so it sums bars t-1 .. t-length "
        "and never includes bar t. Off-by-one reproduced as written.",
        "The helper's output is SIGNED, ranging over [-100, 100] rather than "
        "[0, 100]. Buy and sell both test the SAME `adx_value > adx_threshold`, "
        "so a short needs a strongly POSITIVE (bullish) directional reading and "
        "the short side is far rarer than a symmetric reading would make it. "
        "Reproduced literally, not corrected; it looks like the author intended "
        "an unsigned strength measure.",
        "The true-range triple has no abs(): max(high[i]-low[i], "
        "high[i]-close[i-1], low[i]-close[i-1]). On gap-down bars this collapses "
        "to high-low where the textbook TR would give close[1]-low. Reproduced, "
        "not corrected. Pine ternaries select the other branch on na, so the "
        "port uses Series.where rather than np.maximum.",
        "Pine's na comparison is false, so the earliest bars contribute 0 to the "
        "plusDM/minusDM sums while sum_truerange is already complete -- the DM "
        "sums are one bar behind the TR sum.",
        "The md calls the short average 'GM-8' but the code is "
        "input(15, title=\"GM-15 Period\") feeding ta.sma(close, 15). Code "
        "followed; both namings recorded.",
        "ta.ema's seeding is unpublished by TradingView: pine_ta.pine_ema seeds "
        "with the first non-na observation and does not advance on na "
        "(PINE_SEMANTICS.md 3.1, unresolved parity risk).",
        "The four calls are written unconditionally in source order (entry Buy, "
        "entry Sell, close Buy, close Sell); the entry pair and the exit pair "
        "are each mutually exclusive by construction, so no pair collides on a "
        "bar. strategy.close names an entry id and is a no-op when it is not "
        "held (PINE_SEMANTICS.md 1.12).",
        "No stop/limit/profit/loss/trail exit exists; the only exits are the two "
        "strategy.close calls, so source_reproduce_stops is False and a position "
        "open at the window's end stays open.",
        "sma is na until its window is full and na comparisons are false, so "
        "nothing fires before 15 bars; the DX needs 10 bars of its own.",
        "The Pine for-loop's accumulators are function locals re-initialised on "
        "every bar, which the vectorised form here also does.",
        "Leverage, margin, liquidation, funding and contract-step rounding are "
        "not modelled; the venue's rounding can differ from the engine's float "
        "quantity, which the chain verifier measures separately.",
    ]

    @staticmethod
    def _directional_index(high, low, close, length):
        """The source's own `adx()` helper, reproduced term for term.

        Returns `100 * (plusDI - minusDI) / (plusDI + minusDI)` where both DIs
        are bulk sums over bars `t-1 .. t-length` (bar `t` is never read).
        """
        index = close.index
        sum_tr = pd.Series(0.0, index=index)
        sum_plus = pd.Series(0.0, index=index)
        sum_minus = pd.Series(0.0, index=index)
        for i in range(1, length + 1):
            hi = high.shift(i)
            li = low.shift(i)
            hi_prev = high.shift(i - 1)
            li_prev = low.shift(i - 1)
            close_prev = close.shift(i - 1)

            # truerange_calc, then two ternaries -- NOT max() with abs().
            tr = hi - li
            tr = (hi - close_prev).where((hi - close_prev) > tr, tr)
            tr = (li - close_prev).where((li - close_prev) > tr, tr)
            sum_tr = sum_tr + tr

            up = hi - hi_prev
            down = li_prev - li
            sum_plus = sum_plus + up.where((up > down) & (up > 0), 0.0)
            sum_minus = sum_minus + down.where((down > up) & (down > 0), 0.0)

        # Pine's float division by zero is na.
        tr_denominator = sum_tr.where(sum_tr != 0, np.nan)
        plus_di = sum_plus / tr_denominator * 100.0
        minus_di = sum_minus / tr_denominator * 100.0
        sum_di = plus_di + minus_di
        # `sumDI == 0 ? 1 : sumDI`; an na sumDI is not == 0, so it stays na.
        denominator = sum_di.where(sum_di != 0, 1.0)
        return 100.0 * (plus_di - minus_di) / denominator

    def pine_indicators(self, dataframe, params):
        high = dataframe["high"]
        low = dataframe["low"]
        close = dataframe["close"]
        gm_period = int(params["gm_period"])
        second_ema_period = int(params["second_ema_period"])
        adx_period = int(params["adx_period"])
        adx_threshold = float(params["adx_threshold"])

        gm_8 = ta.pine_sma(close, gm_period)
        second_ema = ta.pine_ema(close, second_ema_period)
        adx_value = self._directional_index(high, low, close, adx_period)

        buy_condition = (
            ta.pine_crossover(close, gm_8)
            & (close > gm_8)
            & (close > second_ema)
            & (adx_value > adx_threshold)
        )
        sell_condition = (
            ta.pine_crossunder(close, gm_8)
            & (close < gm_8)
            & (close < second_ema)
            & (adx_value > adx_threshold)
        )
        exit_buy_condition = ta.pine_crossunder(close, gm_8) & (close < gm_8)
        exit_sell_condition = ta.pine_crossover(close, gm_8) & (close > gm_8)

        dataframe["pine_gm_8"] = gm_8
        dataframe["pine_second_ema"] = second_ema
        dataframe["pine_adx_value"] = adx_value
        dataframe["pine_buy_condition"] = buy_condition
        dataframe["pine_sell_condition"] = sell_condition
        dataframe["pine_exit_buy_condition"] = exit_buy_condition
        dataframe["pine_exit_sell_condition"] = exit_sell_condition
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "buy_condition": dataframe["pine_buy_condition"].to_numpy(),
            "sell_condition": dataframe["pine_sell_condition"].to_numpy(),
            "exit_buy_condition": dataframe["pine_exit_buy_condition"].to_numpy(),
            "exit_sell_condition": dataframe["pine_exit_sell_condition"].to_numpy(),
            "lot_size": float(params["lot_size"]),
        }

    def pine_script(self, broker, i, ctx):
        # if (buy_condition)
        #     strategy.entry("Buy", strategy.long, qty=lot_size)
        if ctx["buy_condition"][i]:
            broker.entry("Buy", "long", qty=ctx["lot_size"])
        # if (sell_condition)
        #     strategy.entry("Sell", strategy.short, qty=lot_size)
        if ctx["sell_condition"][i]:
            broker.entry("Sell", "short", qty=ctx["lot_size"])
        # if (exit_buy_condition)
        #     strategy.close("Buy")
        if ctx["exit_buy_condition"][i]:
            broker.close("Buy")
        # if (exit_sell_condition)
        #     strategy.close("Sell")
        if ctx["exit_sell_condition"][i]:
            broker.close("Sell")
