"""Port of sources/SM_da3f53c1c96ae64a.pine

(batch_001/G趋势EMA-ATR智能交易策略G-Trend-EMA-ATR-Intelligent-Trading-Strategy.md).

Pine v4. AlexGrover's G-Channel supplies the trend state, an EMA supplies a
contrarian price filter, and 2x / 4x ATR supply the stop and take-profit.
Reproduced call for call, in the source's own order:

    var float a = na
    var float b = na
    a := max(src, nz(a[1])) - (nz(a[1] - b[1]) / length)
    b := min(src, nz(b[1])) + (nz(a[1] - b[1]) / length)

    crossup = b[1] < close[1] and b > close
    crossdn = a[1] < close[1] and a > close
    bullish = barssince(crossdn) <= barssince(crossup)

    emaValue = ema(close, emaLength)
    atrValue = atr(atrLength)

    buyCondition  = bullish and close < emaValue
    sellCondition = not bullish and close > emaValue

    if (buyCondition)
        strategy.entry("Buy", strategy.long)
        strategy.exit("Sell", "Buy", stop=close - 2*atrValue,
                                    limit=close + 4*atrValue)
    if (sellCondition)
        strategy.entry("Sell", strategy.short)
        strategy.exit("Cover", "Sell", stop=close + 2*atrValue,
                                     limit=close - 4*atrValue)

The G-Channel recurses on its own previous values, so it is written out as the
source's two `var float` state variables advanced one bar at a time, with
`nz(x)` = 0 for an na. On the FIRST bar both state variables are na, so
`a = max(src, 0) - 0` and `b = min(src, 0) + 0`: for a positive price that is
`a = src` and `b = 0`, which is what the source computes and not something to
"fix" -- it decays out of the recursion within a few bars, but it is the
source's own warmup.

`barssince` returns na until its condition has been true once, and Pine treats
an na comparison as false, so `bullish` is FALSE while neither cross has
happened -- which makes `sellCondition` (its negation) the live branch during
warmup, exactly as in the source. `pine_barssince` reproduces that na, and the
port's `<=` on two nans is False, matching Pine.

`strategy()` declares only `title` / `shorttitle` / `overlay`, so every property
is Pine's documented default: `strategy.fixed` / 1 contract, initial capital
1000000, commission 0%, pyramiding 0, `process_orders_on_close=false`. Neither
entry passes a `qty`.

FIDELITY:

* `length`, `src`, `showcross`, `emaLength` and `atrLength` are the source's
  five `input()` calls and are carried in `source_defaults` by their own names.
  `showcross` gates only the two `plotshape` labels, so it places no order; it
  is kept because it is an input, not because the strategy reads it.
* `avg = (a + b) / 2` and both `plotshape` / `plot` / `fill` calls are
  display-only and are not reproduced. `avg` feeds no condition.
* The exit id of the long arm is the same string as the short ENTRY id
  ("Sell"), which the source writes deliberately enough; entry and exit ids are
  separate namespaces in Pine and the port keeps the source's ids verbatim.
* `crossup` / `crossdn` compare against the built-in `close`, NOT against the
  `src` input, even though `src` defaults to close. The port keeps that split,
  so overriding `src` moves the G-Channel without moving the crosses.
* Both `strategy.exit` calls are written next to their `strategy.entry`, so the
  exit is already live on the bar the entry fills and a zero-length round trip
  is reachable (PINE_SEMANTICS.md 1.9). Both OCA legs are reproduced; a port
  carrying only the stop would silently lose the take-profit
  (PINE_SEMANTICS.md 1.8).
* `ema(close, emaLength)` / `atr(atrLength)` are v4's bare spellings of
  `ta.ema` / `ta.atr`. `ta.atr` is `rma(tr(true), length)`, i.e. the first bar's
  true range is `high - low` rather than na; `pine_ta.pine_atr` implements that
  (PINE_SEMANTICS.md 3.7 records the one-bar seeding offset this creates against
  a source that writes `rma(tr, n)` by hand -- this source uses `atr()`).
* The `ta.ema` seed is unresolved in Pine; the engine seeds with the first
  non-na observation, so the two EMAs are defined from bar 0 here while the
  original platform's `ema` may be na for its first `length-1` bars
  (PINE_SEMANTICS.md 3.1). `buyCondition` / `sellCondition` compare `close`
  against that EMA, so an early-bar difference is a known, unremoved parity
  risk on this port.
* The `/*backtest` header's `basePeriod: 15m` is the FMZ backtester's own
  granularity for filling the 2h bars, not the strategy's period; the engine
  evaluates on bar close and fills at the next open.
* Leverage, margin, liquidation, funding and the venue's contract-step rounding
  are not modelled; the chain verifier measures the last one separately.
"""
import numpy as np
import pandas as pd
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


def g_channel(src: pd.Series, length: int) -> tuple[pd.Series, pd.Series]:
    """The source's two `var float` state variables, advanced bar by bar.

        var float a = na
        var float b = na
        a := max(src, nz(a[1])) - (nz(a[1] - b[1]) / length)
        b := min(src, nz(b[1])) + (nz(a[1] - b[1]) / length)

    `nz(x)` is 0 for an na, which is what makes the first bar evaluate at all.
    Both series are returned; only `a` and `b` (and not their average) are read
    by a trading condition.
    """
    values = src.to_numpy(dtype=float)
    a_values = np.full(len(values), np.nan)
    b_values = np.full(len(values), np.nan)
    previous_a = np.nan
    previous_b = np.nan
    for i, value in enumerate(values):
        carried_a = 0.0 if np.isnan(previous_a) else float(previous_a)
        carried_b = 0.0 if np.isnan(previous_b) else float(previous_b)
        spread = 0.0 if np.isnan(previous_a) or np.isnan(previous_b) else (
            float(previous_a) - float(previous_b)
        )
        current_a = max(float(value), carried_a) - spread / length
        current_b = min(float(value), carried_b) + spread / length
        a_values[i] = current_a
        b_values[i] = current_b
        previous_a, previous_b = current_a, current_b
    return (
        pd.Series(a_values, index=src.index, dtype=float),
        pd.Series(b_values, index=src.index, dtype=float),
    )


class SMGTrendEmaAtr_da3f53(PinePortBase, IStrategy):
    source_id = "SM_da3f53c1c96ae64a"
    source_file = (
        "G趋势EMA-ATR智能交易策略G-Trend-EMA-ATR-Intelligent-Trading-Strategy.md"
    )
    timeframe = "2h"
    can_short = True
    source_defaults: dict = {
        "length": 100,
        "src": "close",
        "showcross": True,
        "emaLength": 50,
        "atrLength": 14,
    }
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    source_reproduce_stops = True
    source_fidelity_notes = [
        "The G-Channel is two `var float` state variables advanced one bar at a "
        "time; on the first bar both are na, so a = max(src, 0) - 0 and "
        "b = min(src, 0) + 0. That is the source's own warmup and is reproduced "
        "rather than corrected.",
        "barssince is na until its condition has been true once and Pine treats "
        "an na comparison as false, so `bullish` is false during warmup and its "
        "negation -- the short branch -- is live. Reproduced verbatim.",
        "crossup / crossdn compare against the built-in close, not against the "
        "`src` input, even though src defaults to close. The port keeps that "
        "split: overriding src moves the G-Channel without moving the crosses.",
        "showcross gates only the two plotshape labels and places no order; it is "
        "carried because it is an input(), not because the strategy reads it.",
        "avg = (a + b) / 2 and all plot / fill output are display-only and are "
        "not reproduced.",
        "The long arm's exit id is the same string as the short entry id "
        "(\"Sell\"); entry and exit ids are separate namespaces in Pine and the "
        "port keeps the source's ids verbatim.",
        "Both legs of each OCA exit (stop and take-profit) are reproduced; a port "
        "carrying only the stop would silently lose the take-profit "
        "(PINE_SEMANTICS.md 1.8).",
        "Each strategy.exit sits next to its strategy.entry, so the exit is "
        "already live on the bar the entry fills and a zero-length round trip is "
        "reachable (PINE_SEMANTICS.md 1.9). Its levels reach Freqtrade through "
        "custom_stoploss and the ROI override, not as projected exit signals.",
        "atr() is rma(tr(true), length), so the first bar's true range is "
        "high - low rather than na (PINE_SEMANTICS.md 3.7).",
        "The ta.ema seed is unpublished; the engine seeds with the first non-na "
        "observation, so the EMA exists from bar 0 here while the original "
        "platform may hold it na for the first length-1 bars. Both conditions "
        "compare close against that EMA, so an early-bar difference is a known, "
        "unremoved parity risk (PINE_SEMANTICS.md 3.1).",
        "The /*backtest header's basePeriod: 15m is the FMZ backtester's own "
        "granularity for filling the 2h bars, not the strategy's period.",
        "Leverage, margin, liquidation, funding and contract-step rounding are "
        "not modelled; the venue's rounding can differ from the engine's float "
        "quantity, which the chain verifier measures separately.",
    ]

    def pine_indicators(self, dataframe, params):
        length = int(params["length"])
        # `src = input(close, title="Source")` -- resolved through the shared
        # Pine source mapping so an override lands where the source reads it.
        src = ta.pine_source(dataframe, str(params["src"])).astype(float)
        close = dataframe["close"]
        a, b = g_channel(src, length)
        # crossup = b[1] < close[1] and b > close
        # crossdn = a[1] < close[1] and a > close
        crossup = (b.shift(1) < close.shift(1)) & (b > close)
        crossdn = (a.shift(1) < close.shift(1)) & (a > close)
        # bullish = barssince(crossdn) <= barssince(crossup); an na on either
        # side makes the comparison na, which Pine reads as false.
        bars_since_crossdn = ta.pine_barssince(crossdn)
        bars_since_crossup = ta.pine_barssince(crossup)
        bullish = (bars_since_crossdn <= bars_since_crossup).fillna(False)
        ema_value = ta.pine_ema(close, int(params["emaLength"]))
        atr_value = ta.pine_atr(dataframe, int(params["atrLength"]))
        dataframe["pine_a"] = a
        dataframe["pine_b"] = b
        dataframe["pine_bullish"] = bullish
        dataframe["pine_ema"] = ema_value
        dataframe["pine_atr"] = atr_value
        dataframe["pine_long_signal"] = bullish & (close < ema_value)
        dataframe["pine_short_signal"] = (~bullish) & (close > ema_value)
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "close": dataframe["close"].to_numpy(),
            "atr": dataframe["pine_atr"].to_numpy(),
            "long_signal": dataframe["pine_long_signal"].to_numpy(),
            "short_signal": dataframe["pine_short_signal"].to_numpy(),
        }

    def pine_script(self, broker, i, ctx):
        close = float(ctx["close"][i])
        atr_value = float(ctx["atr"][i])
        # if (buyCondition)
        if ctx["long_signal"][i]:
            #     strategy.entry("Buy", strategy.long)
            broker.entry("Buy", "long")
            #     strategy.exit("Sell", "Buy", stop=longStopLoss,
            #                   limit=longTakeProfit)
            broker.exit(
                "Sell",
                from_entry="Buy",
                stop=close - 2.0 * atr_value,
                limit=close + 4.0 * atr_value,
            )
        # if (sellCondition)
        if ctx["short_signal"][i]:
            #     strategy.entry("Sell", strategy.short)
            broker.entry("Sell", "short")
            #     strategy.exit("Cover", "Sell", stop=shortStopLoss,
            #                   limit=shortTakeProfit)
            broker.exit(
                "Cover",
                from_entry="Sell",
                stop=close + 2.0 * atr_value,
                limit=close - 4.0 * atr_value,
            )
