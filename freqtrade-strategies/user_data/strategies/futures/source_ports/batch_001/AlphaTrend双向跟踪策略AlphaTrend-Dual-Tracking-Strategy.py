"""Port of sources/SM_5684dd57ea02a6fc.pine
(batch_001/AlphaTrend双向跟踪策略AlphaTrend-Dual-Tracking-Strategy.md).

Pine v5 (`//@version=5`). KivancOzbilgic's AlphaTrend:

    coeff         = input.float(1, "Multiplier", step=0.1)
    AP            = input(14, "Common Period")
    ATR           = ta.sma(ta.tr, AP)
    src           = input(close)
    showsignalsk  = input(true,  "Show Signals?")
    novolumedata  = input(false, "Change calculation (no volume data)?")

    upT   = low  - ATR * coeff
    downT = high + ATR * coeff
    AlphaTrend = 0.0
    AlphaTrend := (novolumedata ? ta.rsi(src, AP) >= 50 : ta.mfi(hlc3, AP) >= 50)
                  ? (upT   < nz(AlphaTrend[1]) ? nz(AlphaTrend[1]) : upT)
                  : (downT > nz(AlphaTrend[1]) ? nz(AlphaTrend[1]) : downT)

    buySignalk  = ta.crossover(AlphaTrend,  AlphaTrend[2])
    sellSignalk = ta.crossunder(AlphaTrend, AlphaTrend[2])
    K1 = ta.barssince(buySignalk)
    K2 = ta.barssince(sellSignalk)
    O1 = ta.barssince(buySignalk[1])
    O2 = ta.barssince(sellSignalk[1])

    longCondition  = buySignalk  and showsignalsk and O1 > K2
    shortCondition = sellSignalk and showsignalsk and O2 > K1
    if longCondition  -> strategy.entry("BUY",  strategy.long,  comment="BUY ENTRY")
    if shortCondition -> strategy.entry("SELL", strategy.short, comment="SELL ENTRY")

`AlphaTrend` is a ratchet: each bar it either holds the previous value or steps
to that bar's band, so it is walked bar by bar. The comparison it uses is
`AlphaTrend[2]`, not `AlphaTrend[1]`, which is why the crossover is between the
current line and its own two-bar lag.

`ta.mfi` is not in the shared layer and is written out in `_pine_mfi` from its
documented definition:

    upper = math.sum(volume * (ta.change(series) <= 0 ? 0 : series), length)
    lower = math.sum(volume * (ta.change(series) >= 0 ? 0 : series), length)
    mfi   = 100.0 - (100.0 / (1.0 + upper / lower))

There is no exit call: a position is closed only when the opposite entry
reverses it, so `source_reproduce_stops` is False. `strategy('AlphaTrend',
shorttitle='AT', overlay=true, format=format.price, precision=2)` declares no
sizing, so the Pine defaults apply -- `fixed` 1 contract, initial capital
1000000, 0% commission, `pyramiding 0`, `process_orders_on_close=false`.

FIDELITY:

* `ta.tr` (bare, no argument) is v5's `ta.tr` with `handle_na = false`, i.e. na
  on the first bar. `pine_ta.pine_tr(..., handle_na=False)` is the shared
  layer's model of it, but its pandas pipeline yields `high - low` on the first
  bar instead of na, which advances `ta.sma(ta.tr, AP)`'s seeding point by one
  bar and with it the whole `upT` / `downT` / `AlphaTrend` chain. This is a
  documented public-layer boundary -- PINE_SEMANTICS §3.7 -- and is recorded
  rather than patched locally.
* `ta.mfi`'s `upper / lower` when `lower == 0` (a window in which every
  `ta.change(hlc3)` is negative) is left to IEEE division, giving `mfi = 100`.
  Pine's own convention for a float division by zero is not established here;
  if the platform returns na instead, that bar would take the `downT` branch
  rather than the `upT` branch. Recorded, not guessed.
* Pine treats an na ternary condition as false, so every warmup bar (where
  `ATR`, `mfi` or `AlphaTrend[1]` is na) falls through to `downT` and
  `AlphaTrend` itself becomes na rather than 0. The port reproduces this with
  plain numpy comparisons against NaN, which are also false.
* `K1` / `K2` / `O1` / `O2` are computed exactly as the source computes them,
  including `O1 = ta.barssince(buySignalk[1])`, which is the bar count of the
  PREVIOUS bar's signal series, not of `buySignalk` itself.
* The `plotshape` and `alertcondition` lines are commented out in the source;
  nothing is restored from them. `plot`/`fill` and the `color1` expression are
  display-only and are not reproduced.
* `showsignalsk` defaults to true, so it does not gate anything under the
  defaults; it is still applied, so overriding it behaves as in the source.
* `/*backtest` declares `period: 1h` on Futures_Binance BTC_USDT, so `timeframe`
  is "1h"; `basePeriod: 15m` is the FMZ backtester's own fill granularity.
* Leverage, margin, liquidation and funding are not modelled, and neither is the
  venue's contract-step rounding of order quantities.
"""
import numpy as np
import pandas as pd
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


def _pine_mfi(source: pd.Series, volume: pd.Series, length: int) -> pd.Series:
    """Pine `ta.mfi(source, length)` from its documented definition."""
    change = ta.pine_change(source)
    # Pine's `cond ? 0 : series` takes the series when `cond` is na, so the
    # weight test is written as "is cond true?" with na counting as false --
    # which is what a numpy comparison against NaN already gives.
    upper_weight = np.where((change <= 0).to_numpy(), 0.0, source.to_numpy(dtype=float))
    lower_weight = np.where((change >= 0).to_numpy(), 0.0, source.to_numpy(dtype=float))
    upper = ta.pine_sum(pd.Series(upper_weight, index=source.index) * volume, length)
    lower = ta.pine_sum(pd.Series(lower_weight, index=source.index) * volume, length)
    with np.errstate(divide="ignore", invalid="ignore"):
        money_flow = upper / lower
        return 100.0 - (100.0 / (1.0 + money_flow))


class SMAlphaTrendDualTracking_5684dd(PinePortBase, IStrategy):
    source_id = "SM_5684dd57ea02a6fc"
    source_file = "AlphaTrend双向跟踪策略AlphaTrend-Dual-Tracking-Strategy.md"
    timeframe = "1h"
    can_short = True
    source_defaults: dict = {
        "coeff": 1.0,
        "AP": 14,
        "src": "close",
        "showsignalsk": True,
        "novolumedata": False,
    }
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    source_reproduce_stops = False
    source_fidelity_notes = [
        "Bare `ta.tr` in v5 is handle_na=false (na on bar 0); pine_ta.pine_tr "
        "returns high - low there instead, moving ta.sma(ta.tr, AP)'s seeding "
        "point one bar earlier and with it the whole AlphaTrend chain. "
        "PINE_SEMANTICS 3.7 boundary: recorded, not patched locally.",
        "ta.mfi is not in the shared layer; _pine_mfi implements its documented "
        "definition (math.sum weighted by the sign of ta.change, then "
        "100 - 100/(1 + upper/lower)).",
        "ta.mfi's upper/lower with lower == 0 is left to IEEE division "
        "(mfi = 100). Pine's float-division-by-zero convention is not "
        "established here; if it returns na the branch taken differs. Recorded.",
        "The AlphaTrend ratchet compares against AlphaTrend[2], not [1]; the "
        "crossover is between the current line and its own two-bar lag.",
        "O1/O2 are ta.barssince of the SHIFTED signal series "
        "(buySignalk[1]/sellSignalk[1]), as in the source.",
        "Pine treats an na ternary condition as false, so warmup bars fall "
        "through to downT and AlphaTrend becomes na, not 0.",
        "plotshape/alertcondition lines are commented out in the source; "
        "plot/fill/color1 are display-only and not reproduced.",
        "No exit call exists: the position is closed only by the opposite "
        "entry reversing it, so source_reproduce_stops is False.",
        "Initial capital is unset in the source, hence Pine's default 1000000.",
    ]

    def pine_indicators(self, dataframe, params):
        length = int(params["AP"])
        multiplier = float(params["coeff"])

        # ATR = ta.sma(ta.tr, AP)  -- ta.tr with handle_na = false
        true_range = ta.pine_tr(dataframe, handle_na=False)
        atr = ta.pine_sma(true_range, length)

        hl3 = ta.pine_source(dataframe, "hlc3")
        source = ta.pine_source(dataframe, str(params["src"]))
        if bool(params["novolumedata"]):
            volume_gate = ta.pine_rsi(source, length) >= 50
        else:
            volume_gate = _pine_mfi(hl3, dataframe["volume"], length) >= 50

        low = dataframe["low"].to_numpy(dtype=float)
        high = dataframe["high"].to_numpy(dtype=float)
        atr_values = atr.to_numpy(dtype=float)
        gate_values = volume_gate.to_numpy(dtype=bool)

        up_t = low - atr_values * multiplier
        down_t = high + atr_values * multiplier

        size = len(dataframe)
        alpha_trend = np.full(size, np.nan)
        for i in range(size):
            # nz(AlphaTrend[1]): na collapses to 0 on the first bar.
            previous = alpha_trend[i - 1] if i >= 1 else np.nan
            reference = previous if np.isfinite(previous) else 0.0
            if gate_values[i]:
                # upT < nz(AlphaTrend[1]) ? nz(AlphaTrend[1]) : upT
                alpha_trend[i] = (
                    reference if up_t[i] < reference else up_t[i]
                )
            else:
                # downT > nz(AlphaTrend[1]) ? nz(AlphaTrend[1]) : downT
                alpha_trend[i] = (
                    reference if down_t[i] > reference else down_t[i]
                )

        line = pd.Series(alpha_trend, index=dataframe.index)
        lag_two = line.shift(2)
        buy_signal = ta.pine_crossover(line, lag_two)
        sell_signal = ta.pine_crossunder(line, lag_two)

        k1 = ta.pine_barssince(buy_signal)
        k2 = ta.pine_barssince(sell_signal)
        o1 = ta.pine_barssince(buy_signal.shift(1))
        o2 = ta.pine_barssince(sell_signal.shift(1))

        show = bool(params["showsignalsk"])
        long_condition = (buy_signal & (o1 > k2)).to_numpy() if show \
            else np.zeros(size, dtype=bool)
        short_condition = (sell_signal & (o2 > k1)).to_numpy() if show \
            else np.zeros(size, dtype=bool)

        dataframe["pine_alphatrend"] = line
        dataframe["pine_buy_signal"] = buy_signal.to_numpy()
        dataframe["pine_sell_signal"] = sell_signal.to_numpy()
        dataframe["pine_long_condition"] = long_condition
        dataframe["pine_short_condition"] = short_condition
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "alphatrend": dataframe["pine_alphatrend"].to_numpy(),
            "long_condition": dataframe["pine_long_condition"].to_numpy(),
            "short_condition": dataframe["pine_short_condition"].to_numpy(),
        }

    def pine_script(self, broker, i, ctx):
        # longCondition = buySignalk and showsignalsk and O1 > K2
        # if (longCondition) strategy.entry("BUY", strategy.long, comment = "BUY ENTRY")
        if ctx["long_condition"][i]:
            broker.entry("BUY", "long")
        # shortCondition = sellSignalk and showsignalsk and O2 > K1
        # if (shortCondition) strategy.entry("SELL", strategy.short, comment = "SELL ENTRY")
        if ctx["short_condition"][i]:
            broker.entry("SELL", "short")
