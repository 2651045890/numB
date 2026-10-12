"""Port of sources/SM_9d97f2fa8d0691d2.pine
(batch_001/EMA-SMA-CCI-ATR-均线完美排列策略与趋势魔法指标自动交易系统-
EMA-SMA-CCI-ATR-Perfect-Order-Moving-Average-Strategy-with-Trend-Magic-
Indicator-Auto-Trading-System.md).

Pine v5, "Trend Magic with EMA, SMA, and Auto-Trading" (c) PakunFX. A colour
change of the Trend Magic line, gated by a moving-average "perfect order",
opens a position; the exit is a stop at the SMA90 of the entry bar with a
take-profit at 1.5x the risk:

    ATR = ta.sma(ta.tr, AP)                 // NOTE: sma of tr, not ta.atr
    upT   = low  - ATR * coeff
    downT = high + ATR * coeff
    var MagicTrend = 0.0
    MagicTrend := ta.cci(src, period) >= 0
                  ? (upT   < nz(MagicTrend[1]) ? nz(MagicTrend[1]) : upT)
                  : (downT > nz(MagicTrend[1]) ? nz(MagicTrend[1]) : downT)

    ema45 = ta.ema(close, 45) ; sma90 = ta.sma(close, 90) ; sma180 = ta.sma(close, 180)
    bullishPerfectOrder = ema45 > sma90 and sma90 > sma180
    bearishPerfectOrder = ema45 < sma90 and sma90 < sma180

    trendMagicTurnedBlue = ta.crossover(isBlueFloat, isRedFloat)    // 1 / 0 floats
    trendMagicTurnedRed  = ta.crossunder(isBlueFloat, isRedFloat)

    longCondition  = bullishPerfectOrder and trendMagicTurnedBlue
    shortCondition = bearishPerfectOrder and trendMagicTurnedRed

    if (longCondition)
        strategy.entry("Buy", strategy.long) ; longSma90 := sma90
    if (shortCondition)
        strategy.entry("Sell", strategy.short) ; shortSma90 := sma90

    if (longCondition and not na(longSma90))
        longRisk = close - longSma90
        strategy.exit("Take Profit/Stop Loss", "Buy",
                      stop=longSma90, limit=close + longRisk * riskRewardRatio)
    if (shortCondition and not na(shortSma90))
        shortRisk = shortSma90 - close
        strategy.exit("Take Profit/Stop Loss", "Sell",
                      stop=shortSma90, limit=close - shortRisk * riskRewardRatio)

`strategy(..., overlay=true, format=format.price, precision=2)` declares no
sizing or cost properties, so Pine's documented defaults are in force and
carried here: fixed / 1 contract / initial_capital 1000000 / commission 0% /
pyramiding 0 / process_orders_on_close false.

The `/*backtest` header declares `period: 5m` on Futures_Binance BTC_USDT, so
`timeframe` is "5m"; `basePeriod: 5m` agrees.

FIDELITY:

* `ATR` is `ta.sma(ta.tr, AP)` -- a SIMPLE mean of the true range, NOT
  `ta.atr` (which is Wilder's rma). Using pine_ta.pine_atr here would change
  every upT/downT/level; the source's own formula is used.
* `ta.cci` is not in pine_ta, so it is implemented from Pine's definition:
  `(source - ta.sma(source, length)) / (0.015 * ta.dev(source, length))`, where
  `ta.dev` is the MEAN ABSOLUTE DEVIATION of the window about its own SMA --
  `(1/length) * sum(|source[i] - sma|)` over the last `length` bars, with the
  CURRENT bar's sma as the single reference. The formula is written in
  `_pine_cci`. A flat window makes `dev` 0 and the quotient na in Pine; that
  case is masked to NaN (so `cci >= 0` is false, as Pine's na comparison is).
* The `MagicTrend` recursion is Pine `var` state and is replayed bar by bar.
  On the first bar `nz(MagicTrend[1])` is `nz(na)` = 0.0, which is the seed.
  An na `upT`/`downT` (the ATR warm-up) leaves the comparison false and the
  value is set to the na operand -- Pine's `na < x` is na, and a na ternary
  condition takes the false branch -- so the line can be na and `nz` restores
  the 0.0 reference on the next bar, exactly as in the source.
* `nz(...)` (1-argument form) replaces na with 0 and is applied to
  `MagicTrend[1]`, as in the source; it is NOT applied to `upT`/`downT`.
* `trendMagicTurnedBlue` / `trendMagicTurnedRed` are `ta.crossover` /
  `ta.crossunder` of the two 1/0 float flags, i.e. on a bar where the CCI
  crosses zero. They are kept as the source writes them (as crosses of the
  float conversions) rather than rewritten as `isBlue and not isBlue[1]`.
* `longSma90` / `shortSma90` are `var float` stores written INSIDE the entry
  `if` blocks; Pine evaluates the statements in order, so by the time the exit
  `if` runs on the same bar the store already holds this bar's `sma90`. The
  port materialises the same store and reads it on the same bars, so the
  `not na(...)` guard and the stop/limit values are those of the ENTRY bar -
  the stop is fixed at entry, as the source intends.
* The exit is therefore placed only on entry bars (the `if` includes
  `longCondition`), and since the id is reused, the engine's replace-by-id rule
  leaves the entry-bar levels resting while the position lives.
* `longRisk` can be negative (nothing forces `close > sma90` on a bullish
  perfect order). The source then asks for a take-profit BELOW the entry, and
  the engine fills such a resting limit on the next bar; reproduced as written.
* `ta.tr` in v5 defaults to `handle_na=false`, i.e. na on the first bar, while
  `pine_ta.pine_tr` yields `high - low` there (PINE_SEMANTICS.md 3.7). That can
  move the SMA seed by one bar. Public-layer boundary; recorded, not patched.
* `color1`, `isBlue` / `isRed` (beyond their use as the 1/0 floats), `plot()`
  and the three `alertcondition()` calls are display/alert-only and are not
  reproduced.
* `src = input(close)` is resolved through pine_ta.pine_source so a non-default
  source still works; it feeds the CCI only.
* Leverage, margin, liquidation and funding are not modelled, and neither is
  the venue's contract-step rounding (measured separately by the chain
  verifier).
"""
import numpy as np
import pandas as pd
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


def _pine_cci(source: pd.Series, length: int) -> pd.Series:
    """Pine `ta.cci(source, length)`.

        ta.cci = (source - ta.sma(source, length)) / (0.015 * ta.dev(source, length))

    `ta.dev` is the mean absolute deviation of the window about its simple
    moving average -- for each bar, the mean of |source[i] - sma| taken over the
    same `length` bars the sma covers. A flat window gives dev == 0 and Pine
    returns na for the 0/0 quotient, so that case is masked to NaN.
    """
    ma = ta.pine_sma(source, length)

    def _mean_abs_deviation(window: np.ndarray) -> float:
        if np.isnan(window).any():
            return np.nan
        return float(np.abs(window - window.mean()).mean())

    dev = source.rolling(int(length), min_periods=int(length)).apply(
        _mean_abs_deviation, raw=True
    )
    with np.errstate(divide="ignore", invalid="ignore"):
        cci = (source - ma) / (0.015 * dev)
    return cci.where(dev != 0.0)


class SMEmaSmaCciAtrPerfectOrder_9d97f2(PinePortBase, IStrategy):
    source_id = "SM_9d97f2fa8d0691d2"
    source_file = (
        "EMA-SMA-CCI-ATR-均线完美排列策略与趋势魔法指标自动交易系统-"
        "EMA-SMA-CCI-ATR-Perfect-Order-Moving-Average-Strategy-with-Trend-Magic-"
        "Indicator-Auto-Trading-System.md"
    )
    timeframe = "5m"
    can_short = True
    source_defaults: dict = {
        "period": 21,
        "coeff": 1.0,
        "AP": 7,
        "riskRewardRatio": 1.5,
        "src": "close",
    }
    # strategy(title/shorttitle/overlay/format/precision) only: Pine defaults.
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    source_reproduce_stops = True
    source_fidelity_notes = [
        "ATR is ta.sma(ta.tr, AP) -- a simple mean of true range, NOT ta.atr "
        "(Wilder rma). The source's own formula is used.",
        "ta.cci is implemented from Pine's definition in _pine_cci: "
        "(source - sma) / (0.015 * mean absolute deviation of the window about "
        "its own sma); dev == 0 is masked to na, as Pine returns na for it.",
        "The MagicTrend `var` recursion is replayed bar by bar; nz(MagicTrend[1]) "
        "seeds it with 0.0 on the first bar.",
        "trendMagicTurnedBlue/Red are kept as ta.crossover/crossunder of the 1/0 "
        "float flags, exactly as written.",
        "longSma90 / shortSma90 are `var float` stores written inside the entry "
        "blocks; read on the same bar, so the stop/limit use the ENTRY bar's "
        "sma90 and close.",
        "The exit is placed only on entry bars (its `if` repeats the entry "
        "condition), and reuses one id, so the entry-bar levels rest for the "
        "life of the position.",
        "longRisk can be negative (close need not be above sma90), giving a "
        "take-profit on the wrong side; reproduced as written.",
        "ta.tr first-bar handling: pine_ta.pine_tr gives high-low where Pine v5's "
        "ta.tr is na (PINE_SEMANTICS.md 3.7); the SMA seed can shift by one bar. "
        "Public-layer boundary, recorded not patched.",
        "color1 / isBlue / isRed (beyond the 1/0 floats), plot() and the three "
        "alertcondition() calls are display/alert-only and are not reproduced.",
        "src = input(close) is resolved through pine_ta.pine_source; it feeds the "
        "CCI only.",
        "Pine's strategy() declares no sizing/cost properties here, so fixed / 1 "
        "contract / 1000000 / 0% / pyramiding 0 are in force and "
        "process_orders_on_close is false.",
        "Leverage, margin, liquidation, funding and contract-step rounding are "
        "not modelled.",
    ]

    def pine_indicators(self, dataframe, params):
        period = int(params["period"])
        coeff = float(params["coeff"])
        atr_period = int(params["AP"])
        risk_reward = float(params["riskRewardRatio"])
        src = ta.pine_source(dataframe, str(params["src"]))

        low, high, close = dataframe["low"], dataframe["high"], dataframe["close"]

        # ATR = ta.sma(ta.tr, AP)
        atr = ta.pine_sma(ta.pine_tr(dataframe), atr_period)

        # upT = low - ATR * coeff ; downT = high + ATR * coeff
        up_t = (low - atr * coeff).to_numpy(dtype=float)
        down_t = (high + atr * coeff).to_numpy(dtype=float)

        # var MagicTrend = 0.0
        # MagicTrend := ta.cci(src, period) >= 0
        #     ? (upT   < nz(MagicTrend[1]) ? nz(MagicTrend[1]) : upT)
        #     : (downT > nz(MagicTrend[1]) ? nz(MagicTrend[1]) : downT)
        cci = _pine_cci(src, period).to_numpy(dtype=float)
        magic = np.full(len(cci), np.nan)
        # `ref` is nz(MagicTrend[1]): the previous bar's stored value, or 0.0
        # when that value was na (which is the first bar, and any bar the
        # recursion left na). `na >= 0` is na in Pine and a na ternary condition
        # takes the false branch, so a missing CCI value goes down the else arm.
        ref = 0.0
        for i in range(len(cci)):
            if cci[i] >= 0:
                magic[i] = ref if up_t[i] < ref else up_t[i]
            else:
                magic[i] = ref if down_t[i] > ref else down_t[i]
            ref = 0.0 if not np.isfinite(magic[i]) else magic[i]

        # isBlueFloat / isRedFloat = isBlue ? 1 : 0 / isRed ? 1 : 0
        is_blue = cci >= 0  # na -> false -> 0
        is_red = cci < 0
        is_blue_float = pd.Series(np.where(is_blue, 1.0, 0.0), index=dataframe.index)
        is_red_float = pd.Series(np.where(is_red, 1.0, 0.0), index=dataframe.index)

        # ema45 / sma90 / sma180
        ema45 = ta.pine_ema(close, 45)
        sma90 = ta.pine_sma(close, 90)
        sma180 = ta.pine_sma(close, 180)

        bullish = (ema45 > sma90) & (sma90 > sma180)
        bearish = (ema45 < sma90) & (sma90 < sma180)

        turned_blue = ta.pine_crossover(is_blue_float, is_red_float)
        turned_red = ta.pine_crossunder(is_blue_float, is_red_float)

        long_condition = (bullish & turned_blue).fillna(False)
        short_condition = (bearish & turned_red).fillna(False)

        # var float longSma90 = na / shortSma90 = na, written inside the entry
        # blocks: the store carries the last entry bar's sma90 forward.
        long_sma90 = np.full(len(dataframe), np.nan)
        short_sma90 = np.full(len(dataframe), np.nan)
        last_long = np.nan
        last_short = np.nan
        for i in range(len(dataframe)):
            if long_condition.iloc[i]:
                last_long = float(sma90.iloc[i])
            if short_condition.iloc[i]:
                last_short = float(sma90.iloc[i])
            long_sma90[i] = last_long
            short_sma90[i] = last_short

        dataframe["pine_magic_trend"] = magic
        dataframe["pine_cci"] = cci
        dataframe["pine_ema45"] = ema45
        dataframe["pine_sma90"] = sma90
        dataframe["pine_sma180"] = sma180
        dataframe["pine_long_condition"] = long_condition
        dataframe["pine_short_condition"] = short_condition
        dataframe["pine_long_stop"] = long_sma90
        dataframe["pine_short_stop"] = short_sma90
        # longTakeProfit = close + (close - longSma90) * riskRewardRatio
        dataframe["pine_long_take_profit"] = close + (
            close - pd.Series(long_sma90, index=dataframe.index)
        ) * risk_reward
        # shortTakeProfit = close - (shortSma90 - close) * riskRewardRatio
        dataframe["pine_short_take_profit"] = close - (
            pd.Series(short_sma90, index=dataframe.index) - close
        ) * risk_reward
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "long_condition": dataframe["pine_long_condition"].to_numpy(),
            "short_condition": dataframe["pine_short_condition"].to_numpy(),
            "long_stop": dataframe["pine_long_stop"].to_numpy(),
            "short_stop": dataframe["pine_short_stop"].to_numpy(),
            "long_take_profit": dataframe["pine_long_take_profit"].to_numpy(),
            "short_take_profit": dataframe["pine_short_take_profit"].to_numpy(),
        }

    def pine_script(self, broker, i, ctx):
        # if (longCondition)
        #     strategy.entry("Buy", strategy.long)
        #     longSma90 := sma90
        if ctx["long_condition"][i]:
            broker.entry("Buy", "long")

            # if (longCondition and not na(longSma90))
            #     longStopLoss = longSma90 ; longRisk = close - longSma90
            #     strategy.exit("Take Profit/Stop Loss", "Buy",
            #                   stop=longStopLoss,
            #                   limit=close + longRisk * riskRewardRatio)
            if np.isfinite(ctx["long_stop"][i]):
                broker.exit(
                    "Take Profit/Stop Loss",
                    "Buy",
                    stop=float(ctx["long_stop"][i]),
                    limit=float(ctx["long_take_profit"][i]),
                )

        # if (shortCondition)
        #     strategy.entry("Sell", strategy.short)
        #     shortSma90 := sma90
        if ctx["short_condition"][i]:
            broker.entry("Sell", "short")

            # if (shortCondition and not na(shortSma90))
            #     shortStopLoss = shortSma90 ; shortRisk = shortSma90 - close
            #     strategy.exit("Take Profit/Stop Loss", "Sell",
            #                   stop=shortStopLoss,
            #                   limit=close - shortRisk * riskRewardRatio)
            if np.isfinite(ctx["short_stop"][i]):
                broker.exit(
                    "Take Profit/Stop Loss",
                    "Sell",
                    stop=float(ctx["short_stop"][i]),
                    limit=float(ctx["short_take_profit"][i]),
                )
