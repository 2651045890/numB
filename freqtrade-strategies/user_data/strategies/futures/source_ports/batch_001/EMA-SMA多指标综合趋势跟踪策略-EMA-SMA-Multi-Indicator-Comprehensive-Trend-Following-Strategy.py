"""Port of sources/SM_9ab94b0d91684254.pine
(batch_001/EMA-SMA多指标综合趋势跟踪策略-EMA-SMA-Multi-Indicator-Comprehensive-Trend-Following-Strategy.md).

Pine v5, on the `/*backtest` header's 1h period. Twelve moving averages plus
five oscillators are each voted "above close" or "below close", the two counts
are subtracted, and the difference drives four threshold calls:

    ema/sma(close, 10|20|30|50|100|200)
    rsi      = ta.rsi(close, 14)
    stochK   = ta.stoch(close, high, low, 14)
    cci      = ta.cci(close, 20)
    momentum = ta.mom(close, 10)
    macdHist = ta.macd(close, 12, 26, 9).macd - .signal
    above_count = sum(12 MA votes) + (rsi > 50) + (stochK > 80) + (cci > 100)
                  + (momentum > 0) + (macdHist > 0)
    below_count = sum(12 MA votes) + (rsi < 50) + (stochK < 20) + (cci < -100)
                  + (momentum < 0) + (macdHist < 0)
    da = below_count - above_count

    if da > close_short            -> strategy.close("Sell")
    if da < close_long             -> strategy.close("Buy")
    if da > entry_long             -> strategy.entry("Buy",  strategy.long)
    if da < entry_short            -> strategy.entry("Sell", strategy.short)

with `entry_long = 12`, `entry_short = -12`, `close_long = -9`,
`close_short = 9`. The order of the four calls is the source's and is preserved:
both closes are evaluated before either entry, so on a bar that crosses a close
threshold AND an entry threshold the entry fills at the next open in the engine's
order of creation (PINE_SEMANTICS.md 1.13).

`strategy()` declares only `title` and `overlay`, so every property is Pine's
documented default: `strategy.fixed` / 1 contract, initial capital 1000000,
commission 0%, `pyramiding 0`, `process_orders_on_close=false`. `pyramiding 0`
means a repeated same-direction entry while that direction is already open is
refused outright, while the opposite entry reverses.

There is no `strategy.exit` and no stop/limit/trail argument anywhere in the
source, so `source_reproduce_stops` is False and every exit is the market
`strategy.close` above.

The `/*backtest` header's `basePeriod: 15m` is the FMZ backtester's own
granularity for filling those 1h bars, not the strategy's period.

FIDELITY:

* Every `(indicator OP close ? 1 : 0)` vote is reproduced with an na-aware
  comparison that yields False, which is Pine's rule for na in a boolean
  context. That matters for the two `sma200`-family votes: `pine_sma(close,
  200)` is na for the first 199 bars, while `pine_ema` is seeded with the first
  close and is therefore defined from bar 0 -- so the source's own asymmetry
  between `ta.ema` and `ta.sma` warmup is preserved rather than smoothed over.
* `cci` is `(src - sma(src, length)) / (0.015 * dev)` with
  `dev = sma(|src - sma(src, length)|, length)`. That is the reading already
  used by the port of the OBV+CCI source in this batch family; Pine's `ta.dev`
  reference implementation instead averages `|src[i] - sma_now|` over the
  window, so the two differ in the last `length-1` terms. Recorded as an
  unresolved equivalence risk; the formula is written out here rather than
  delegated to a library function.
* `stochK` is the source's four-argument `ta.stoch(close, high, low, 14)`:
  `100 * (close - lowest(low, 14)) / (highest(high, 14) - lowest(low, 14))`,
  computed from the passed `high` / `low` series, not from a one-argument
  stochastic builtin.
* `ta.mom(close, 10)` is `close - close[10]`, i.e. `pine_ta.pine_change`.
* `ta.macd(close, 12, 26, 9)` is reproduced through `pine_ta.pine_macd`, whose
  EMA seeding is the shared `pine_ta.pine_ema` choice (PINE_SEMANTICS.md 3.1);
  the histogram is `macdLine - signalLine`, exactly as the source writes it.
* `stochD`, `bullPower` and `bearPower` are computed by the source but never
  referenced by its vote counts (the lines that would use them are commented
  out). They are kept as columns so the formula set is on the record, but they
  cannot affect a signal; the commented-out `adx`, `ao`, `stochRsi`, `willr`
  and `uo` votes are NOT restored.
* `//@version=5` throughout, so PINE_SEMANTICS.md 1.16 (v2/v3 bool-as-number)
  does not apply.
* Leverage, margin, liquidation, funding and the venue's contract-step rounding
  are not modelled.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase

# The six moving-average periods are literals in the source, not inputs.
_MA_PERIODS = (10, 20, 30, 50, 100, 200)


def _vote(series: pd.Series, other) -> pd.Series:
    """`(series > other ? 1 : 0)` -- na compares false, so na votes 0."""
    return (series > other).fillna(False).astype(float)


def _vote_below(series: pd.Series, other) -> pd.Series:
    """`(series < other ? 1 : 0)` -- na compares false, so na votes 0."""
    return (series < other).fillna(False).astype(float)


class SMEmaSmaMultiIndicator_9ab94b(PinePortBase, IStrategy):
    source_id = "SM_9ab94b0d91684254"
    source_file = (
        "EMA-SMA多指标综合趋势跟踪策略"
        "-EMA-SMA-Multi-Indicator-Comprehensive-Trend-Following-Strategy.md"
    )
    timeframe = "1h"
    can_short = True
    source_defaults: dict = {
        "entry_long": 12,
        "entry_short": -12,
        "close_long": -9,
        "close_short": 9,
    }
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    source_reproduce_stops = False
    source_fidelity_notes = [
        "`strategy()` declares only title/overlay, so the Pine defaults stand: "
        "fixed / 1 contract, initial capital 1000000, commission 0%, "
        "pyramiding 0, process_orders_on_close=false.",
        "pyramiding 0 (Pine's default) means a repeated same-direction entry "
        "while that direction is already open is refused, while an opposite "
        "entry reverses the position.",
        "No `strategy.exit` and no stop/limit/trail argument exists in the "
        "source; every exit is a market `strategy.close`, so "
        "source_reproduce_stops is False.",
        "na in a vote comparison yields 0, Pine's rule for na in a boolean "
        "context; `pine_sma(close, 200)` is therefore inert for the first 199 "
        "bars while `pine_ema(close, 200)` is defined from bar 0 -- the "
        "source's own ema/sma warmup asymmetry is preserved.",
        "cci's `dev` is modelled as `sma(|src - sma(src, length)|, length)`, "
        "matching the OBV+CCI port already in this corpus; Pine's `ta.dev` "
        "reference averages `|src[i] - sma_now|` over the window instead, so "
        "the last length-1 terms differ. Unresolved equivalence risk.",
        "stochK is the four-argument `ta.stoch(close, high, low, 14)`, "
        "computed from the passed high/low series rather than a one-argument "
        "stochastic builtin.",
        "stochD, bullPower and bearPower are computed by the source but never "
        "read by its vote counts; they are kept as columns only. The "
        "commented-out adx/ao/stochRsi/willr/uo votes are NOT restored.",
        "TradingView's ta.ema seeding rule is unpublished; pine_ta.pine_ema "
        "seeds with the first non-na observation (PINE_SEMANTICS.md 3.1), so "
        "the EMA legs carry that modelling choice.",
        "hline/plot/linewidth/color are display-only and are not reproduced.",
        "Leverage, margin, liquidation, funding and the venue's contract-step "
        "rounding are not modelled.",
    ]

    def pine_indicators(self, dataframe, params):
        close = dataframe["close"]
        high = dataframe["high"]
        low = dataframe["low"]

        above = pd.Series(0.0, index=dataframe.index)
        below = pd.Series(0.0, index=dataframe.index)
        for period in _MA_PERIODS:
            ema = ta.pine_ema(close, period)
            sma = ta.pine_sma(close, period)
            dataframe[f"pine_ema{period}"] = ema
            dataframe[f"pine_sma{period}"] = sma
            above = above + _vote(ema, close) + _vote(sma, close)
            below = below + _vote_below(ema, close) + _vote_below(sma, close)

        # rsi = ta.rsi(close, 14)
        rsi = ta.pine_rsi(close, 14)

        # stochK = ta.stoch(close, high, low, 14)
        #   = 100 * (close - lowest(low, 14)) / (highest(high, 14) - lowest(low, 14))
        lowest_low = ta.pine_lowest(low, 14)
        highest_high = ta.pine_highest(high, 14)
        with np.errstate(divide="ignore", invalid="ignore"):
            stoch_k = 100.0 * (close - lowest_low) / (highest_high - lowest_low)
        # stochD = ta.sma(stochK, 3) -- computed by the source, never read.
        stoch_d = ta.pine_sma(stoch_k, 3)

        # cci = ta.cci(close, 20)
        #   = (close - sma(close,20)) / (0.015 * dev)
        cci_basis = ta.pine_sma(close, 20)
        cci_dev = ta.pine_sma((close - cci_basis).abs(), 20)
        with np.errstate(divide="ignore", invalid="ignore"):
            cci = (close - cci_basis) / (0.015 * cci_dev)

        # momentum = ta.mom(close, 10) = close - close[10]
        momentum = ta.pine_change(close, 10)

        # [macdLine, signalLine, _] = ta.macd(close, 12, 26, 9)
        macd = ta.pine_macd(close, 12, 26, 9)
        macd_hist = macd["macd"] - macd["signal"]

        # bullPower = high - ta.ema(close, 13) ; bearPower = low - ta.ema(close, 13)
        # -- computed by the source, never read by the vote counts.
        power_basis = ta.pine_ema(close, 13)

        above = (
            above
            + _vote(rsi, 50.0)
            + _vote(stoch_k, 80.0)
            + _vote(cci, 100.0)
            + _vote(momentum, 0.0)
            + _vote(macd_hist, 0.0)
        )
        below = (
            below
            + _vote_below(rsi, 50.0)
            + _vote_below(stoch_k, 20.0)
            + _vote_below(cci, -100.0)
            + _vote_below(momentum, 0.0)
            + _vote_below(macd_hist, 0.0)
        )

        dataframe["pine_rsi"] = rsi
        dataframe["pine_stoch_k"] = stoch_k
        dataframe["pine_stoch_d"] = stoch_d
        dataframe["pine_cci"] = cci
        dataframe["pine_momentum"] = momentum
        dataframe["pine_macd_hist"] = macd_hist
        dataframe["pine_bull_power"] = high - power_basis
        dataframe["pine_bear_power"] = low - power_basis
        dataframe["pine_above_count"] = above
        dataframe["pine_below_count"] = below
        dataframe["pine_da"] = below - above
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "da": dataframe["pine_da"].to_numpy(),
            "entry_long": float(params["entry_long"]),
            "entry_short": float(params["entry_short"]),
            "close_long": float(params["close_long"]),
            "close_short": float(params["close_short"]),
        }

    def pine_script(self, broker, i, ctx):
        da = ctx["da"][i]
        # if (below_count - above_count > close_short)
        #     strategy.close("Sell")
        if da > ctx["close_short"]:
            broker.close("Sell")
        # if (below_count - above_count < close_long)
        #     strategy.close("Buy")
        if da < ctx["close_long"]:
            broker.close("Buy")
        # if (below_count - above_count > entry_long)
        #     strategy.entry("Buy", strategy.long)
        if da > ctx["entry_long"]:
            broker.entry("Buy", "long")
        # if (below_count - above_count < entry_short)
        #     strategy.entry("Sell", strategy.short)
        if da < ctx["entry_short"]:
            broker.entry("Sell", "short")
