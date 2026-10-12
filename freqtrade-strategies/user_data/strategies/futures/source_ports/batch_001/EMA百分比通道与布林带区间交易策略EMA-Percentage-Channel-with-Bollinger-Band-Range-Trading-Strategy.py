"""Port of sources/SM_0887e31f334ffc4c.pine
(batch_001/EMA百分比通道与布林带区间交易策略EMA-Percentage-Channel-with-Bollinger-Band-Range-Trading-Strategy.md).

Pine v4 ("[mdeacey] EMA% Channel + BB Range Strategy"). A 200-period EMA with a
percentage channel around it bounds the trades; a 20-period Bollinger band
supplies the entries, and both are exited either by the channel edge crossing
back or by an ATR-scaled stop:

    ema1      = ema(srce, len)                       # len = 200
    valuee    = (percent*ema1)/100                   # percent = 1
    upperbande= ema1 + valuee
    lowerbande= ema1 - valuee

    MA2   = sma(src, length)                         # length = 20
    dev   = mult * stdev(src, length)                # mult = 2.0
    upper = MA2 + dev
    lower = MA2 - dev

    strategy.entry("Long",  true,  when = crossover(close, lower)  and close < upperbande and close > lowerbande)
    strategy.close("Long",  when = crossunder(close, lowerbande))
    strategy.entry("Short", false, when = crossunder(close, upper) and close < upperbande and close > lowerbande)
    strategy.close("Short", when = crossover(close, upperbande))

    pine_rma(x, y) =>
        sum := (x + (y - 1) * nz(sum[1])) / y        # local Wilder RMA, y = atrPeriod
    true_range() => max(high - low, max(abs(high - close[1]), abs(low - close[1])))

    strategy.exit("Exit Long",  "Long",  limit=upper, stop=low  - pine_rma(true_range()*multiplierPeriod, atrPeriod))
    strategy.exit("eExit Short", "Short", limit=lower, stop=high + pine_rma(true_range()*multiplierPeriod, atrPeriod))

`strategy()` declares only `title` / `shorttitle` / `overlay`, so every property
is Pine's documented default: `strategy.fixed` / 1 contract, initial capital
1000000, commission 0%, pyramiding 0, `process_orders_on_close=false`.

The `/*backtest` header declares `period: 3m` on Futures_Binance BTC_USDT, so
`timeframe` is "3m"; `basePeriod: 1m` is the FMZ backtester's fill granularity.

FIDELITY (what is kept, what is a modelling choice, what cannot be done):

* The source defines its OWN `pine_rma(x, y)`: `sum := (x + (y-1)*nz(sum[1]))/y`
  over a `sum = 0.0` declaration, i.e. it seeds from `nz(na) = 0` on the first
  bar that has data and does NOT wait `length` bars for an SMA seed. That is
  NOT `pine_ta.pine_rma` (which seeds with the SMA of the first `length`
  observations), so it is implemented verbatim here as `_local_rma` rather
  than swapped for the library function with the same name.
* `true_range()` at bar 0 is na (its `close[1]` is na and Pine's `max`
  propagates na), which makes the RMA na there too and re-seeds from bar 1
  with `nz(sum[1]) = 0`. Reproduced by letting nan propagate in the same way.
* `pine_ta.pine_stdev` (ddof=0, Pine's population standard deviation) is used
  for `stdev(src, length)`, and `pine_ta.pine_lowest` / `pine_lowest`-style
  warm-up rules apply: the bands are na until their windows fill.
* `strategy.exit` is issued unconditionally on every bar; the engine keeps one
  order per id and ignores an exit whose `from_entry` is not open
  (PINE_SEMANTICS.md 1.12), and the two ids here are distinct.
* The stop legs use the raw `low - rma` / `high + rma` levels, which are not on
  the venue's price grid; PINE_SEMANTICS.md 1.11 records that such levels can
  land up to one tick off after the framework's one-sided rounding.
* `plot` / `barcolor` / `fill` and `signalColor` are display-only and are not
  reproduced.
* Leverage, margin, liquidation, funding and the venue's contract-step rounding
  are not modelled. `3m` has no local history, so the chain check reports
  `skipped_no_local_data` for this port (PINE_SEMANTICS.md 五).
"""
import numpy as np
import pandas as pd
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


def _local_rma(values: pd.Series, alpha: float) -> pd.Series:
    """The source's own `pine_rma(x, y)`, transcribed.

        sum := (x + (alpha - 1) * nz(sum[1])) / alpha

    `sum` is declared as 0.0 and `sum[1]` is na on the first bar, so
    `nz(sum[1]) = 0` seeds the recursion on the first bar that has data. This
    is deliberately NOT pine_ta.pine_rma, whose SMA seed is a different rule.
    """
    source = values.to_numpy(dtype=float)
    out = np.full(len(source), np.nan)
    previous = np.nan
    for i in range(len(source)):
        carry = 0.0 if np.isnan(previous) else previous
        out[i] = (source[i] + (alpha - 1.0) * carry) / alpha
        previous = out[i]
    return pd.Series(out, index=values.index, dtype=float)


def _level(value) -> float | None:
    """A price, or None when Pine would have na there (no resting leg)."""
    value = float(value)
    return value if np.isfinite(value) else None


class SMEmaPercentageChannelBbRange_0887e3(PinePortBase, IStrategy):
    source_id = "SM_0887e31f334ffc4c"
    source_file = (
        "EMA百分比通道与布林带区间交易策略EMA-Percentage-Channel-with-Bollinger-Band-"
        "Range-Trading-Strategy.md"
    )
    timeframe = "3m"
    can_short = True
    # Input defaults, exactly as written in the source.
    source_defaults: dict = {
        "len": 200,
        "srce": "close",
        "percent": 1.0,
        "length": 20,
        "src": "close",
        "mult": 2.0,
        "atrPeriod": 14,
        "multiplierPeriod": 1.75,
    }
    # strategy(title=..., shorttitle=..., overlay=true): nothing else declared,
    # so fixed / 1 contract, 1000000 initial capital, 0% fee, pyramiding 0.
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    # strategy.exit(stop=..., limit=...): both legs rest inside the bar.
    source_reproduce_stops = True
    source_mintick = 0.1
    source_fidelity_notes = [
        "The source defines its own `pine_rma(x, y)` as "
        "`sum := (x + (y-1)*nz(sum[1]))/y` over a `sum = 0.0` declaration. It "
        "seeds from `nz(na) = 0` on the first bar with data and does NOT wait "
        "for an SMA seed, so it is NOT pine_ta.pine_rma; it is transcribed "
        "verbatim as `_local_rma`.",
        "`true_range()` is na on bar 0 (its close[1] is na and Pine's max "
        "propagates na), so the RMA re-seeds from bar 1 with nz(sum[1]) = 0; "
        "nan propagation is kept identical.",
        "`stdev(src, length)` uses pine_ta.pine_stdev, i.e. the population "
        "standard deviation (ddof=0), which is what Pine's ta.stdev computes.",
        "Both `strategy.exit` calls are issued every bar; the engine keeps one "
        "order per id and ignores an exit whose from_entry is not open "
        "(PINE_SEMANTICS.md 1.12).",
        "The stop levels `low - rma` / `high + rma` are not on the venue grid, "
        "so the framework's one-sided stop rounding can move them by up to one "
        "tick (PINE_SEMANTICS.md 1.11).",
        "The 3m period has no local history, so the chain check reports "
        "`skipped_no_local_data` for this port.",
        "`plot` / `barcolor` / `fill` / `signalColor` are display-only.",
    ]

    # ---- indicators --------------------------------------------------------
    def pine_indicators(self, dataframe, params):
        close = dataframe["close"]
        high = dataframe["high"]
        low = dataframe["low"]

        ema_source = ta.pine_source(dataframe, str(params["srce"]))
        band_source = ta.pine_source(dataframe, str(params["src"]))

        # ema1 = ema(srce, len); valuee = (percent*ema1)/100
        ema1 = ta.pine_ema(ema_source, int(params["len"]))
        valuee = (float(params["percent"]) * ema1) / 100.0
        upperbande = ema1 + valuee
        lowerbande = ema1 - valuee

        # MA2 = sma(src, length); dev = mult * stdev(src, length)
        ma2 = ta.pine_sma(band_source, int(params["length"]))
        dev = float(params["mult"]) * ta.pine_stdev(band_source, int(params["length"]))
        upper = ma2 + dev
        lower = ma2 - dev

        # true_range() = max(high - low, max(abs(high - close[1]), abs(low - close[1])))
        # Pine's max propagates na, so bar 0 (close[1] is na) is na.
        previous_close = close.shift(1)
        true_range = np.maximum(
            (high - low),
            np.maximum((high - previous_close).abs(), (low - previous_close).abs()),
        )
        true_range = pd.Series(true_range, index=dataframe.index, dtype=float)
        rma = _local_rma(
            true_range * float(params["multiplierPeriod"]), float(params["atrPeriod"])
        )
        long_stop_level = low - rma
        short_stop_level = high + rma

        dataframe["pine_ema1"] = ema1
        dataframe["pine_upperbande"] = upperbande
        dataframe["pine_lowerbande"] = lowerbande
        dataframe["pine_upper"] = upper
        dataframe["pine_lower"] = lower
        dataframe["pine_long_stop"] = long_stop_level
        dataframe["pine_short_stop"] = short_stop_level

        channel = (close < upperbande) & (close > lowerbande)
        long_entry = ta.pine_crossover(close, lower) & channel
        long_exit = ta.pine_crossunder(close, lowerbande)
        short_entry = ta.pine_crossunder(close, upper) & channel
        short_exit = ta.pine_crossover(close, upperbande)
        dataframe["pine_long_entry"] = long_entry.fillna(False).astype(bool)
        dataframe["pine_long_exit"] = long_exit.fillna(False).astype(bool)
        dataframe["pine_short_entry"] = short_entry.fillna(False).astype(bool)
        dataframe["pine_short_exit"] = short_exit.fillna(False).astype(bool)
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "long_entry": dataframe["pine_long_entry"].to_numpy(dtype=bool),
            "long_exit": dataframe["pine_long_exit"].to_numpy(dtype=bool),
            "short_entry": dataframe["pine_short_entry"].to_numpy(dtype=bool),
            "short_exit": dataframe["pine_short_exit"].to_numpy(dtype=bool),
            "upper": dataframe["pine_upper"].to_numpy(dtype=float),
            "lower": dataframe["pine_lower"].to_numpy(dtype=float),
            "long_stop": dataframe["pine_long_stop"].to_numpy(dtype=float),
            "short_stop": dataframe["pine_short_stop"].to_numpy(dtype=float),
        }

    # ---- orders ------------------------------------------------------------
    def pine_script(self, broker, i, ctx):
        # strategy.entry("Long", true, when = crossover(close, lower) and ...)
        if ctx["long_entry"][i]:
            broker.entry("Long", "long")
        # strategy.close("Long", when = crossunder(close, lowerbande))
        if ctx["long_exit"][i]:
            broker.close("Long")
        # strategy.entry("Short", false, when = crossunder(close, upper) and ...)
        if ctx["short_entry"][i]:
            broker.entry("Short", "short")
        # strategy.close("Short", when = crossover(close, upperbande))
        if ctx["short_exit"][i]:
            broker.close("Short")

        # strategy.exit("Exit Long", "Long", limit=upper, stop=low - rma(...))
        broker.exit(
            "Exit Long", from_entry="Long",
            stop=_level(ctx["long_stop"][i]), limit=_level(ctx["upper"][i]),
        )
        # strategy.exit("eExit Short", "Short", limit=lower, stop=high + rma(...))
        broker.exit(
            "eExit Short", from_entry="Short",
            stop=_level(ctx["short_stop"][i]), limit=_level(ctx["lower"][i]),
        )
