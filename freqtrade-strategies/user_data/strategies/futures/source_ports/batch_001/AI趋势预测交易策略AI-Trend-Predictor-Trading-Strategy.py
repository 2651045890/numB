"""Port of sources/SM_fc37d10f60665841.pine (batch_001/AI趋势预测交易策略AI-Trend-Predictor-Trading-Strategy.md).

ChaoZhang's "AI Trend Predictor". Despite the name there is no learning step:
the whole signal is a moving average of a sign, used as a bias filter on a
cross of the close against a long SMA.

    B_close     = ta.sma(close, length_B)                 // 192
    C_close     = ta.sma(B_close, length_C)               // 10  (unused)
    C_diff      = high - low
    C_avg_diff  = ta.sma(C_diff, length_C)                // unused
    correlation = ta.correlation(C_diff, C_diff[1], length_C)
    probability = correlation > 0 ? 1 : 0
    D           = ta.sma(probability, length_C)

    strategy.entry('Buy',  strategy.long,
                   when = D > 0.51 and ta.crossover(close,  B_close))
    strategy.entry('Sell', strategy.short,
                   when = D < 0.51 and ta.crossunder(close, B_close))

`D` averages ten indicators, so it takes the values 0, 0.1, ..., 1.0; the two
thresholds therefore mean "at least 6 of the last 10 windows had positive
amplitude correlation" for the long and "at most 5" for the short. Both
thresholds are strict (`> 0.51`, `< 0.51`), which is load-bearing: D can never
equal 0.51, so a bar that is neither (impossible here, since every D is either
above or below) would fire nothing.

`strategy()` declares only title / overlay, so every order property is Pine's
default: fixed quantity of 1 contract, 0% commission, pyramiding 0, initial
capital 1000000. There is no exit call and no stop: a position goes flat only
when the opposite entry reverses it, so `source_reproduce_stops` is False and a
position open at the end of the window stays open.

FIDELITY:

* `ta.correlation` is not part of `pine_ta`; see `_pine_correlation` for the
  formula (covariance / product of the two population standard deviations,
  which is TradingView's published covariance definition) and for the one
  modelling choice -- a zero denominator.
* `future_close = close[future_length]` and `probability_up = close >
  future_close ? 1 : 0` are misnamed but NOT future data: Pine's `[n]` is a
  BACKWARD history reference, so `close[5]` is five bars ago and the expression
  merely records whether price rose over the last five bars. Nothing here reads
  forward, and the causal prefix check in validate_pine would fail if it did.
  `probability_up` is plotted and never read by a condition, so it changes no
  order.
* Source computations that nothing reads are still computed and exposed as
  columns, because the source computes them: `A_close = close` (line 19),
  `C_close = sma(B_close, length_C)` (line 21), `B_diff = high - low` (line 25),
  `C_avg_diff = sma(C_diff, length_C)` (line 29) and `future_close` /
  `probability_up` (lines 41-42). `length_A = 24` is declared as an input and
  never referenced anywhere in the source, so it has no effect; it is still
  carried in `source_defaults` because the source declares it.
* `plot(D, ...)` / `plot(probability_up, ...)` and `overlay=false` are
  display-only and are not reproduced.
* `strategy.entry(..., when=...)` does nothing on a bar whose `when` is false,
  which is what `broker.entry(..., when=...)` models; the port calls the broker
  only when the conjunction holds, which is equivalent and keeps the two
  `strategy.entry` calls in the source's order.
* Leverage, margin, liquidation and funding are not modelled, and neither is
  the venue's contract-step rounding -- the chain verifier measures that
  separately rather than treating it as a signal difference.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


def _pine_correlation(source_a: pd.Series, source_b: pd.Series, length: int) -> pd.Series:
    """Pine `ta.correlation(source1, source2, length)`.

    TradingView defines covariance as `ta.sma(source1 * source2, length) -
    ta.sma(source1, length) * ta.sma(source2, length)` and correlation as
    `covariance / (ta.stdev(source1, length) * ta.stdev(source2, length))`,
    with `ta.stdev` the population (biased) standard deviation -- which is what
    `pine_ta.pine_stdev` computes (ddof=0).

    A window whose standard deviation product is zero makes the ratio
    undefined. Pine's published result for that division is not specified, so
    the port leaves it na, which makes the source's `correlation > 0 ? 1 : 0`
    take the false branch and contribute 0 -- the same treatment Pine gives an
    na in a comparison. That is a modelling choice, and it is the conservative
    one: it cannot invent a positive correlation out of a flat window.
    """
    mean_a = ta.pine_sma(source_a, length)
    mean_b = ta.pine_sma(source_b, length)
    covariance = ta.pine_sma(source_a * source_b, length) - mean_a * mean_b
    denominator = ta.pine_stdev(source_a, length) * ta.pine_stdev(source_b, length)
    with np.errstate(divide="ignore", invalid="ignore"):
        correlation = covariance / denominator
    return correlation.where(denominator != 0.0)


class SMAiTrendPredictor_fc37d1(PinePortBase, IStrategy):
    source_id = "SM_fc37d10f60665841"
    source_file = "AI趋势预测交易策略AI-Trend-Predictor-Trading-Strategy.md"
    timeframe = "1d"
    can_short = True
    source_defaults: dict = {
        "length_A": 24,
        "length_B": 192,
        "length_C": 10,
        "future_length": 5,
    }
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    source_reproduce_stops = False
    source_fidelity_notes = [
        "ta.correlation is not in pine_ta; implemented from TradingView's "
        "definition (sma(a*b) - sma(a)*sma(b), over the product of the two "
        "population standard deviations). A zero standard-deviation product is "
        "left na, so the source's `correlation > 0 ? 1 : 0` takes the false "
        "branch, matching how Pine treats an na comparison; the exact Pine "
        "division-by-zero result is not published, so that is a modelling "
        "choice.",
        "future_close = close[future_length] is misnamed but is NOT future "
        "data: Pine's [n] is a backward history reference, so close[5] is five "
        "bars ago and probability_up only says whether price rose over the last "
        "five bars. Nothing reads forward.",
        "probability_up is only plotted and never read by a condition, so it "
        "changes no order.",
        "Dead source computations, kept only as columns because the source "
        "computes them: A_close = close, B_diff = high - low, C_close = "
        "sma(B_close, length_C), C_avg_diff = sma(C_diff, length_C). length_A = "
        "24 is declared as an input and never referenced anywhere in the "
        "source, so it has no trade effect; it is still carried in "
        "source_defaults because the source declares it.",
        "The two threshold tests are strict (> 0.51 / < 0.51) and are "
        "reproduced as written; D is a 10-bar mean of a 0/1 series so it only "
        "takes multiples of 0.1 and can never sit exactly on 0.51.",
        "strategy() declares only title/overlay, so qty_type=fixed, qty_value=1, "
        "commission=0%, pyramiding=0 and initial_capital=1000000 are Pine's "
        "documented defaults.",
        "There is no exit call and no stop: a position is closed only by the "
        "opposite entry reversing it, so source_reproduce_stops is False and a "
        "position open at the end of the window stays open.",
        "plot(D)/plot(probability_up) and overlay=false are display-only and "
        "are not reproduced.",
    ]

    def pine_indicators(self, dataframe, params):
        length_c = int(params["length_C"])
        close = dataframe["close"]

        # B_close = ta.sma(close, length_B)
        b_close = ta.pine_sma(close, int(params["length_B"]))
        # C_close = ta.sma(B_close, length_C)  -- computed by the source, unused.
        c_close = ta.pine_sma(b_close, length_c)

        # A_diff / B_diff / C_diff are all `high - low` in the source; only the
        # C_diff copy is read.
        c_diff = dataframe["high"] - dataframe["low"]
        # C_avg_diff = ta.sma(C_diff, length_C)  -- computed by the source, unused.
        c_avg_diff = ta.pine_sma(c_diff, length_c)

        # correlation = ta.correlation(C_diff, C_diff[1], length_C)
        correlation = _pine_correlation(c_diff, c_diff.shift(1), length_c)
        # probability = correlation > 0 ? 1 : 0
        probability = (correlation > 0.0).astype(float)
        # D = ta.sma(probability, length_C)
        d = ta.pine_sma(probability, length_c)

        # future_close = close[future_length]; probability_up = close > future_close ? 1 : 0
        future_close = close.shift(int(params["future_length"]))
        probability_up = (close > future_close).astype(float)

        dataframe["pine_b_close"] = b_close
        dataframe["pine_c_close"] = c_close
        dataframe["pine_c_avg_diff"] = c_avg_diff
        dataframe["pine_correlation"] = correlation
        dataframe["pine_probability"] = probability
        dataframe["pine_d"] = d
        dataframe["pine_future_close"] = future_close
        dataframe["pine_probability_up"] = probability_up
        # A_close = close and B_diff = high - low are the identity/duplicate of
        # columns the frame already carries; nothing reads them.
        dataframe["pine_long_condition"] = (
            (d > 0.51) & ta.pine_crossover(close, b_close)
        )
        dataframe["pine_short_condition"] = (
            (d < 0.51) & ta.pine_crossunder(close, b_close)
        )
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "b_close": dataframe["pine_b_close"].to_numpy(),
            "d": dataframe["pine_d"].to_numpy(),
            "long_condition": dataframe["pine_long_condition"].to_numpy(),
            "short_condition": dataframe["pine_short_condition"].to_numpy(),
        }

    def pine_script(self, broker, i, ctx):
        # strategy.entry('Buy', strategy.long, when=D > 0.51 and
        #                ta.crossover(close, B_close))
        if ctx["long_condition"][i]:
            broker.entry("Buy", "long")
        # strategy.entry('Sell', strategy.short, when=D < 0.51 and
        #                ta.crossunder(close, B_close))
        if ctx["short_condition"][i]:
            broker.entry("Sell", "short")
