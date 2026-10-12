"""Port of sources/SM_4a1cd608a3534363.pine
(batch_001/HALFTREND-HEMA-SMA-FALSE-SIGNALs-STRATEGY.md).

Pine v5, `//@version=5`, declaring `indicator(...)` -- NOT a strategy. The
conversion station appended the order block, and it is the whole trade
behaviour (PINE_SEMANTICS.md 1.17):

    if long
        strategy.entry("Enter Long", strategy.long)
    else if short
        strategy.entry("Enter Short", strategy.short)

There is no `strategy.close` / `strategy.exit` / stop anywhere: entries never
exit except by an opposing entry netting them.

The three indicators the signals combine (each credited in the source to a
different author) are transcribed exactly:

    sma  = ta.sma(src, len)                                  # len = 150
    hema = 3 * ta.wma(close, length / 2) - 2 * ta.ema(close, length / 2)
                                                             # length = 50
    Halftrend (everget) -- the full var-state machine below
    min = ESTRATEGIA_vela_completa_fuera_hema ? low  : math.min(open, close)
    max = ESTRATEGIA_vela_completa_fuera_hema ? high : math.max(open, close)
    long  = hema > sma and buySignal  and (min > hema and max > hema)
    short = hema < sma and sellSignal and (min < hema and max < hema)

The Halftrend block is a bar-by-bar state machine over `trend`, `nextTrend`,
`maxLowPrice`, `minHighPrice`, `up`, `down` (Pine `var`, so carried across
bars), reading `trend[1]`, `up[1]`, `down[1]`. It is reproduced as an explicit
sequential loop here, in the source's own statement order, because a vectorised
rewrite would reorder the state updates. `pine_ta` has no `highestbars` /
`lowestbars`, so those are expanded from their definitions (see
`_highest_bars_back`).

`strategy()` is absent from the source, so every `source_*` property below is
Pine's DOCUMENTED DEFAULT: fixed / 1 contract, initial capital 1000000,
commission 0%, pyramiding 0, `process_orders_on_close=false`.

The `/*backtest` header declares `period: 5m` on Futures_Binance BTC_USDT, so
`timeframe` is "5m"; its `basePeriod: 1m` is the host backtester's own
granularity for filling those 5m bars, not the strategy's period.

FIDELITY:

* md-vs-source: the md's "Strategy Arguments" table lists `Amplitude` with a
  default of `true` (`|v_input_2|true|`), while the code is
  `amplitude = input(title='Amplitude', defval=1)`. The code's `1` is followed
  (it is consumed as a length by `ta.sma(high, amplitude)` and
  `ta.highestbars(amplitude)`), and `1` and `true` are the same value to both
  of those calls, so the table's `true` is a rendering artifact rather than a
  behaviour difference. Recorded, not reconciled.
* `ta.highestbars(amplitude)` / `ta.lowestbars(amplitude)` are called with ONE
  argument, so the source series is the implicit `high` / `low`. TradingView
  does not publish the tie-break for a repeated extreme; the port takes the
  NEAREST occurrence (smallest offset). With the source's default
  `amplitude = 1` the window holds one bar and every reading is offset 0, so
  the tie-break is unreachable in the source's own configuration.
* `hema`'s `length / 2` is Pine's automatic float-to-int cast (50 -> 25); it is
  not a rounding choice made here.
* `ta.wma` and `ta.ema` are pine_ta's modelled forms. `ta.ema` is seeded with
  the first non-na observation (PINE_SEMANTICS.md 3.1, TradingView's rule is
  unpublished), so `hema` differs from the original platform's until the EMA
  converges. `ta.atr(100)` is `rma(tr(true), 100)`, Pine's own definition of
  `ta.atr`.
* `min` / `max` shadow Pine's `math.min` / `math.max` as variable names; they
  are the candle body's low/high bound (default) or the full candle range (when
  the `ESTRATEGIA_vela_completa_fuera_hema` option is on).
* The `offset` input (6) is consumed only by `plot(sma, ..., offset=offset)`;
  it is display-only and changes no order.
* `buyColor`/`sellColor`, `htColor`, `sma_color`, `hema_color`, `color_fondo`,
  `bgcolor`, `fill`, `plotshape`, `plot` and the two `alertcondition` calls are
  display/alert-only and place no order.
* na propagation is Pine's: comparisons against na are false, so every
  condition is false during warmup. `sma` needs 150 bars, `hema` needs 25,
  `ta.atr(100)` needs 100, and `arrowUp`/`arrowDown` exist only on a trend-flip
  bar -- with `atr2` still na, `arrowUp := up - atr2` is na and `buySignal`
  false, so no signal can fire before 100 bars.
* No exit of any kind exists, so `source_reproduce_stops` is False and a
  position open at the end of the window stays open.
* Leverage, margin, liquidation, funding and the venue's contract-step
  rounding are not modelled.
"""
import numpy as np
import pandas as pd
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


def _highest_bars_back(values: np.ndarray, i: int, length: int) -> float:
    """Pine `ta.highestbars(high, length)` at bar `i`: bars back to the high.

    Pine reports the offset to the highest value over the last `length` bars as
    a negative number or zero, which is why the source wraps it in
    `math.abs(...)` before indexing. na anywhere in the window makes the result
    na. On a repeated extreme the NEAREST occurrence is taken (TradingView does
    not publish its tie-break; see the port docstring).
    """
    start = i - length + 1
    if start < 0:
        return np.nan
    window = values[start:i + 1]
    if not np.all(np.isfinite(window)):
        return np.nan
    return float(int(np.argmax(window[::-1])))


def _lowest_bars_back(values: np.ndarray, i: int, length: int) -> float:
    """Pine `ta.lowestbars(low, length)` at bar `i`; mirror of the above."""
    start = i - length + 1
    if start < 0:
        return np.nan
    window = values[start:i + 1]
    if not np.all(np.isfinite(window)):
        return np.nan
    return float(int(np.argmin(window[::-1])))


class SMHalftrendHemaSmaFalseSignals_4a1cd6(PinePortBase, IStrategy):
    source_id = "SM_4a1cd608a3534363"
    source_file = "HALFTREND-HEMA-SMA-FALSE-SIGNALs-STRATEGY.md"
    timeframe = "5m"
    can_short = True
    source_defaults: dict = {
        "ESTRATEGIA_vela_completa_fuera_hema": False,
        "len": 150,
        "src": "close",
        "offset": 6,
        "length": 50,
        "amplitude": 1,
        "channelDeviation": 2,
        "showArrows": True,
        "showChannels": False,
    }
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    source_reproduce_stops = False
    source_fidelity_notes = [
        "The file is an `indicator()` plus an order block APPENDED by the "
        "conversion station: `if long -> strategy.entry(\"Enter Long\", long) "
        "else if short -> strategy.entry(\"Enter Short\", short)` is the whole "
        "trade behaviour, and there is no exit call anywhere "
        "(PINE_SEMANTICS.md 1.17).",
        "The Halftrend state machine (everget's) is reproduced as an explicit "
        "bar-by-bar loop in the source's own statement order, because the "
        "updates of trend/nextTrend/maxLowPrice/minHighPrice/up/down and the "
        "reads of trend[1]/up[1]/down[1] are order-dependent and a vectorised "
        "rewrite would reorder them.",
        "`pine_ta` has no highestbars/lowestbars, so they are expanded from "
        "their definitions here. The source calls them with ONE argument, so "
        "the series is the implicit high/low. TradingView does not publish the "
        "tie-break for a repeated extreme; the port takes the nearest "
        "occurrence. With the source's default amplitude = 1 the window is one "
        "bar and the offset is always 0, so this is unreachable as configured.",
        "md-vs-source: the md's argument table lists Amplitude as `true` while "
        "the code is `input(title='Amplitude', defval=1)`. The code is "
        "followed; 1 and true are the same value to ta.sma/ta.highestbars, so "
        "this is a rendering artifact of the table, recorded not reconciled.",
        "`hema = 3*wma(close, length/2) - 2*ema(close, length/2)`; the "
        "`length/2` is Pine's automatic float-to-int cast (50 -> 25), not a "
        "rounding choice made here.",
        "`min`/`max` shadow math.min/math.max as variable names: they are the "
        "candle body's bounds by default, or the full high/low range when the "
        "`ESTRATEGIA_vela_completa_fuera_hema` option is enabled.",
        "`offset` (6) is consumed only by `plot(sma, ..., offset=offset)`; it "
        "is display-only and changes no order.",
        "colors, bgcolor, fill, plotshape, plot and the two alertcondition "
        "calls are display/alert-only and place no order.",
        "ta.ema is seeded with the first non-na observation (pine_ta's "
        "documented model); TradingView's seeding rule is unpublished, so "
        "`hema` differs from the original platform's until the EMA converges "
        "(PINE_SEMANTICS.md 3.1).",
        "ta.atr(100) is rma(tr(true), 100), Pine's own definition of ta.atr, "
        "and it is na for the first 100 bars; because arrowUp/arrowDown are "
        "computed as `up +- atr2`, no signal can fire before then even if the "
        "trend flips.",
        "na propagation is Pine's: na comparisons are false, so every "
        "condition is false during warmup (sma needs 150 bars, hema 25, "
        "atr(100) 100).",
        "No exit exists, so source_reproduce_stops is False and a position "
        "open at the window's end stays open; only an opposing entry nets it "
        "(PINE_SEMANTICS.md 1.1).",
        "Leverage, margin, liquidation, funding and contract-step rounding are "
        "not modelled; the venue's rounding can differ from the engine's float "
        "quantity, which the chain verifier measures separately.",
    ]

    def pine_indicators(self, dataframe: pd.DataFrame, params: dict) -> pd.DataFrame:
        close = dataframe["close"].to_numpy(dtype=float)
        open_ = dataframe["open"].to_numpy(dtype=float)
        high = dataframe["high"].to_numpy(dtype=float)
        low = dataframe["low"].to_numpy(dtype=float)
        bars = len(dataframe)

        full_body = bool(params["ESTRATEGIA_vela_completa_fuera_hema"])
        amplitude = int(params["amplitude"])
        channel_deviation = float(params["channelDeviation"])

        # sma = ta.sma(src, len)
        src = ta.pine_source(dataframe, str(params["src"]))
        sma = ta.pine_sma(src, int(params["len"])).to_numpy(dtype=float)

        # hema = 3 * ta.wma(close, length / 2) - 2 * ta.ema(close, length / 2)
        hema_length = int(int(params["length"]) / 2)
        hema = (
            3.0 * ta.pine_wma(dataframe["close"], hema_length)
            - 2.0 * ta.pine_ema(dataframe["close"], hema_length)
        ).to_numpy(dtype=float)

        # atr2 = ta.atr(100) / 2; dev = channelDeviation * atr2
        atr2 = (ta.pine_atr(dataframe, 100) / 2.0).to_numpy(dtype=float)
        dev = channel_deviation * atr2

        # ---- Halftrend state machine ----------------------------------------
        trend = 0
        next_trend = 0
        max_low_price = np.nan
        min_high_price = np.nan
        up = 0.0
        down = 0.0
        trend_prev = np.nan
        up_prev = np.nan
        down_prev = np.nan

        ht = np.full(bars, np.nan)
        atr_high = np.full(bars, np.nan)
        atr_low = np.full(bars, np.nan)
        buy_signal = np.zeros(bars, dtype=bool)
        sell_signal = np.zeros(bars, dtype=bool)

        for i in range(bars):
            # var float maxLowPrice = nz(low[1], low)  (evaluated on bar 0 only)
            # var float minHighPrice = nz(high[1], high)
            if i == 0:
                max_low_price = low[0]
                min_high_price = high[0]

            low_1 = low[i - 1] if i >= 1 else np.nan
            high_1 = high[i - 1] if i >= 1 else np.nan
            low_1 = low[i] if np.isnan(low_1) else low_1
            high_1 = high[i] if np.isnan(high_1) else high_1

            # highPrice = high[math.abs(ta.highestbars(amplitude))]
            # lowPrice  = low[math.abs(ta.lowestbars(amplitude))]
            high_offset = _highest_bars_back(high, i, amplitude)
            low_offset = _lowest_bars_back(low, i, amplitude)
            high_price = np.nan if np.isnan(high_offset) else high[i - int(high_offset)]
            low_price = np.nan if np.isnan(low_offset) else low[i - int(low_offset)]

            # highma = ta.sma(high, amplitude); lowma = ta.sma(low, amplitude)
            if i + 1 >= amplitude:
                highma = float(np.mean(high[i - amplitude + 1:i + 1]))
                lowma = float(np.mean(low[i - amplitude + 1:i + 1]))
            else:
                highma = np.nan
                lowma = np.nan

            if next_trend == 1:
                max_low_price = max(low_price, max_low_price)
                if highma < max_low_price and close[i] < low_1:
                    trend = 1
                    next_trend = 0
                    min_high_price = high_price
            else:
                min_high_price = min(high_price, min_high_price)
                if lowma > min_high_price and close[i] > high_1:
                    trend = 0
                    next_trend = 1
                    max_low_price = low_price

            arrow_up = np.nan
            arrow_down = np.nan
            if trend == 0:
                if (not np.isnan(trend_prev)) and trend_prev != 0:
                    up = down if np.isnan(down_prev) else down_prev
                    arrow_up = up - atr2[i]
                else:
                    up = max_low_price if np.isnan(up_prev) else max(max_low_price, up_prev)
                atr_high[i] = up + dev[i]
                atr_low[i] = up - dev[i]
            else:
                if (not np.isnan(trend_prev)) and trend_prev != 1:
                    down = up if np.isnan(up_prev) else up_prev
                    arrow_down = down + atr2[i]
                else:
                    down = min_high_price if np.isnan(down_prev) else min(min_high_price, down_prev)
                atr_high[i] = down + dev[i]
                atr_low[i] = down - dev[i]

            ht[i] = up if trend == 0 else down
            # buySignal  = not na(arrowUp)  and trend == 0 and trend[1] == 1
            # sellSignal = not na(arrowDown) and trend == 1 and trend[1] == 0
            buy_signal[i] = (not np.isnan(arrow_up)) and trend == 0 and trend_prev == 1
            sell_signal[i] = (not np.isnan(arrow_down)) and trend == 1 and trend_prev == 0

            trend_prev = float(trend)
            up_prev = up
            down_prev = down

        # min = ESTRATEGIA_... ? low  : math.min(open, close)
        # max = ESTRATEGIA_... ? high : math.max(open, close)
        min_body = low if full_body else np.minimum(open_, close)
        max_body = high if full_body else np.maximum(open_, close)
        long_vela = (min_body > hema) & (max_body > hema)
        short_vela = (min_body < hema) & (max_body < hema)

        long_condition = (hema > sma) & buy_signal & long_vela
        short_condition = (hema < sma) & sell_signal & short_vela

        dataframe["pine_sma"] = sma
        dataframe["pine_hema"] = hema
        dataframe["pine_halftrend"] = ht
        dataframe["pine_atr_high"] = atr_high
        dataframe["pine_atr_low"] = atr_low
        dataframe["pine_buy_signal"] = buy_signal
        dataframe["pine_sell_signal"] = sell_signal
        dataframe["pine_long_condition"] = pd.Series(long_condition, index=dataframe.index)
        dataframe["pine_short_condition"] = pd.Series(short_condition, index=dataframe.index)
        return dataframe

    def pine_context(self, dataframe: pd.DataFrame, params: dict) -> dict:
        return {
            "long_condition": dataframe["pine_long_condition"].to_numpy(),
            "short_condition": dataframe["pine_short_condition"].to_numpy(),
        }

    def pine_script(self, broker, i: int, ctx: dict) -> None:
        # if long
        #     strategy.entry("Enter Long", strategy.long)
        # else if short
        #     strategy.entry("Enter Short", strategy.short)
        if ctx["long_condition"][i]:
            broker.entry("Enter Long", "long")
        elif ctx["short_condition"][i]:
            broker.entry("Enter Short", "short")
