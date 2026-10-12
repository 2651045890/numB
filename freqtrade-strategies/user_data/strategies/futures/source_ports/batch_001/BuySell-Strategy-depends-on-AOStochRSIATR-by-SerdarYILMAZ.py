"""Port of sources/SM_ebd25e3080bef60c.pine

(batch_001/BuySell-Strategy-depends-on-AOStochRSIATR-by-SerdarYILMAZ.md).

Pine v4. Serdar YILMAZ's teaching strategy: three independent filters must
agree before either arm fires. Reproduced call for call, in the source's own
order:

    awesome = (sma(hl2, fast) - sma(hl2, slow)) * 1000      // AO x 1000
    k = sma(stoch(close, high, low, K), D)
    d = sma(k, smooth)                                      // plotted only
    rsi = rsi(rsisource, rsilength)
    atrvalue = rma(tr, atrlen)

    LongCondition  = k < 20 and rsi < 30 and awesome > awesome[1]
    ShortCondition = k > 80 and rsi > 70 and awesome < awesome[1]

    if (LongCondition)
        stoploss = low - atrvalue
        takeprofit = close + atrvalue
        strategy.entry("Long Position", strategy.long)
        strategy.exit("TP/SL", stop=stoploss, limit=takeprofit)
    if (ShortCondition)
        stoploss = high + atrvalue
        takeprofit = close - atrvalue
        strategy.entry("Short Position", strategy.short)
        strategy.exit("TP/SL", stop=stoploss, limit=takeprofit)

`stoch` is v4's built-in `stoch(source, high, low, length)`, and is NOT exposed
by `pine_ta`, so it is written out literally as
`100 * (source - lowest(low, n)) / (highest(high, n) - lowest(low, n))` with
`source = close` and `n = K`. `rma(tr, atrlen)` uses the bare v4 `tr` built-in
(na on the first bar, i.e. `ta.tr(false)`), NOT `atr()` -- which would be
`rma(tr(true), n)` -- so the port passes `handle_na=False` to `pine_tr`.
`hl2` comes from the shared Pine source mapping.

`strategy()` declares only `title` / `shorttitle`, so every property is Pine's
documented default: `strategy.fixed` / 1 contract, initial capital 1000000,
commission 0%, pyramiding 0, `process_orders_on_close=false`. Neither entry
passes a `qty`, so the default order size supplies the 1 contract.

Both `strategy.exit` calls use the SAME id ("TP/SL") and pass NO `from_entry`,
so each call replaces the previous one (Pine keeps one resting order per id) and
the order it leaves rests against whatever position is open -- which is why the
two arms cannot leave stale exits behind. Both OCA legs are reproduced; a port
carrying only the stop would silently lose the take-profit.

FIDELITY:

* `fast`, `slow`, `K`, `D`, `smooth`, `rsisource`, `rsilength` and `atrlen` are
  the source's eight `input()` calls and are carried in `source_defaults` under
  their own names, matching the md's argument table.
* `d = sma(k, smooth)` is computed by the source and then used by nothing: the
  only `plot(k, color=color.blue)` draws K, and `d` feeds no condition. It is
  reproduced for completeness and does not reach an order.
* `awesome` is the Awesome Oscillator scaled by 1000, and `awesome > awesome[1]`
  is a rising-AO test, not a zero test. The md's prose does not describe it.
* The md's prose is a disclaimer ("This strategy is just for training ... Don't
  make buy or sell decision"), not a specification; nothing in it contradicts
  the code and none of it is used as a spec.
* `stoch`, like every `lowest` / `highest` window here, is na until its window
  is full and na compares false, so nothing fires before K + D bars.
* `tr` is the bare v4 built-in, so its first bar is na. `pine_ta.pine_tr`
  computes its row maximum with pandas' skipna default and therefore returns
  `high - low` on bar 0 even for `handle_na=False`; the divergence is one bar of
  rma seeding (PINE_SEMANTICS.md 3.7). It is a shared-layer boundary, reported
  rather than worked around, and it does not move any signal on this source
  because the first signal needs far more history than the ATR window.
* The exits sit next to their entries, so they are live on the entry's own fill
  bar and a zero-length round trip is reachable (PINE_SEMANTICS.md 1.9).
* The `/*backtest` header's `basePeriod: 15m` is the FMZ backtester's own
  granularity for filling the 4h bars, not the strategy's period; the engine
  evaluates on bar close and fills at the next open.
* Leverage, margin, liquidation, funding and the venue's contract-step rounding
  are not modelled; the chain verifier measures the last one separately.
"""
import numpy as np
import pandas as pd
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


def pine_stoch(source: pd.Series, high: pd.Series, low: pd.Series,
               length: int) -> pd.Series:
    """Pine v4 `stoch(source, high, low, length)`.

        100 * (source - lowest(low, length)) /
              (highest(high, length) - lowest(low, length))

    A window whose range is zero divides by zero; Pine does not publish the
    result, so it is left as the na pandas produces rather than being given an
    arbitrary value.
    """
    lowest_low = ta.pine_lowest(low, length)
    highest_high = ta.pine_highest(high, length)
    span = highest_high - lowest_low
    return 100.0 * (source - lowest_low) / span.where(span != 0.0)


class SMBuySellAoStochRsiAtr_ebd25e(PinePortBase, IStrategy):
    source_id = "SM_ebd25e3080bef60c"
    source_file = "BuySell-Strategy-depends-on-AOStochRSIATR-by-SerdarYILMAZ.md"
    timeframe = "4h"
    can_short = True
    source_defaults: dict = {
        "fast": 5,
        "slow": 34,
        "K": 14,
        "D": 3,
        "smooth": 3,
        "rsisource": "close",
        "rsilength": 10,
        "atrlen": 14,
    }
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    source_reproduce_stops = True
    source_fidelity_notes = [
        "stoch is v4's stoch(source, high, low, length) and is not exposed by "
        "pine_ta, so it is computed inline as 100*(close - lowest(low, K)) / "
        "(highest(high, K) - lowest(low, K)); a window whose range is zero "
        "divides by zero and Pine does not publish the result, so it is left na.",
        "d = sma(k, smooth) is computed by the source and read by nothing -- the "
        "plot draws k, and d feeds no condition. It is reproduced for "
        "completeness and never reaches an order.",
        "rma(tr, atrlen) uses the bare v4 tr built-in, not atr(), so the port "
        "passes handle_na=False to pine_tr: atr() would be rma(tr(true), n).",
        "pine_ta.pine_tr takes its row maximum with pandas' skipna default and so "
        "returns high - low on bar 0 for handle_na=False as well; the source's "
        "bare tr is na there. That is one bar of rma seeding "
        "(PINE_SEMANTICS.md 3.7), a shared-layer boundary reported rather than "
        "worked around, and it does not move any signal on this source.",
        "awesome is the Awesome Oscillator x 1000 and the condition is "
        "awesome > awesome[1] (rising AO), not a comparison against zero.",
        "Both strategy.exit calls share one id and pass no from_entry, so each "
        "replaces the previous resting order and the surviving order binds to "
        "whatever position is open; the port places them with the same shape.",
        "Both legs of the OCA exit (stop and take-profit) are reproduced; a port "
        "carrying only the stop would silently lose the take-profit "
        "(PINE_SEMANTICS.md 1.8).",
        "Each strategy.exit sits next to its strategy.entry, so it is live on the "
        "entry's own fill bar and a zero-length round trip is reachable "
        "(PINE_SEMANTICS.md 1.9). Its levels reach Freqtrade through "
        "custom_stoploss and the ROI override, not as projected exit signals.",
        "The md's prose is an author disclaimer rather than a specification; it "
        "contradicts nothing in the code and is not used as a spec.",
        "The /*backtest header's basePeriod: 15m is the FMZ backtester's own "
        "granularity for filling the 4h bars, not the strategy's period.",
        "Leverage, margin, liquidation, funding and contract-step rounding are "
        "not modelled; the venue's rounding can differ from the engine's float "
        "quantity, which the chain verifier measures separately.",
    ]

    def pine_indicators(self, dataframe, params):
        close = dataframe["close"]
        fast = int(params["fast"])
        slow = int(params["slow"])
        hl2 = ta.pine_source(dataframe, "hl2")
        # awesome = (sma(hl2, fast) - sma(hl2, slow)) * 1000
        awesome = (ta.pine_sma(hl2, fast) - ta.pine_sma(hl2, slow)) * 1000.0
        # k = sma(stoch(close, high, low, K), D); d = sma(k, smooth)
        raw_stoch = pine_stoch(close, dataframe["high"], dataframe["low"],
                               int(params["K"]))
        k = ta.pine_sma(raw_stoch, int(params["D"]))
        d = ta.pine_sma(k, int(params["smooth"]))
        rsi_source = ta.pine_source(dataframe, str(params["rsisource"]))
        rsi = ta.pine_rsi(rsi_source, int(params["rsilength"]))
        # atrvalue = rma(tr, atrlen) -- the bare v4 tr, na on the first bar.
        atr_value = ta.pine_rma(
            ta.pine_tr(dataframe, handle_na=False), int(params["atrlen"])
        )
        dataframe["pine_awesome"] = awesome
        dataframe["pine_k"] = k
        dataframe["pine_d"] = d
        dataframe["pine_rsi"] = rsi
        dataframe["pine_atr"] = atr_value
        dataframe["pine_long_signal"] = (
            (k < 20.0) & (rsi < 30.0) & (awesome > awesome.shift(1))
        )
        dataframe["pine_short_signal"] = (
            (k > 80.0) & (rsi > 70.0) & (awesome < awesome.shift(1))
        )
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "close": dataframe["close"].to_numpy(),
            "high": dataframe["high"].to_numpy(),
            "low": dataframe["low"].to_numpy(),
            "atr": dataframe["pine_atr"].to_numpy(),
            "long_signal": dataframe["pine_long_signal"].to_numpy(),
            "short_signal": dataframe["pine_short_signal"].to_numpy(),
        }

    def pine_script(self, broker, i, ctx):
        # if (LongCondition)
        if ctx["long_signal"][i]:
            #     stoploss = low - atrvalue
            stoploss = float(ctx["low"][i]) - float(ctx["atr"][i])
            #     takeprofit = close + atrvalue
            takeprofit = float(ctx["close"][i]) + float(ctx["atr"][i])
            #     strategy.entry("Long Position", strategy.long)
            broker.entry("Long Position", "long")
            #     strategy.exit("TP/SL", stop=stoploss, limit=takeprofit)
            broker.exit("TP/SL", stop=stoploss, limit=takeprofit)
        # if (ShortCondition)
        if ctx["short_signal"][i]:
            #     stoploss = high + atrvalue
            stoploss = float(ctx["high"][i]) + float(ctx["atr"][i])
            #     takeprofit = close - atrvalue
            takeprofit = float(ctx["close"][i]) - float(ctx["atr"][i])
            #     strategy.entry("Short Position", strategy.short)
            broker.entry("Short Position", "short")
            #     strategy.exit("TP/SL", stop=stoploss, limit=takeprofit)
            broker.exit("TP/SL", stop=stoploss, limit=takeprofit)
