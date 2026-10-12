"""Port of sources/SM_4fabc038b8fb382c.pine
(batch_001/BVs-ICHIMOKU-CLOUD-All-Signals.md).

Pine v4, "BV's ICHIMOKU CLOUD SIGNAL TESTER" (c) vuagnouxb. An Ichimoku signal
selector plus an ATR money-management exit:

    donchian(len) => avg(lowest(len), highest(len))

    conversionLine = donchian(conversionPeriods)     // donchian uses low/high
    baseLine       = donchian(basePeriods)
    leadLine1      = avg(conversionLine, baseLine)
    leadLine2      = donchian(laggingSpan2Periods)

    kumoHigh = max(leadLine1[displacement-1], leadLine2[displacement-1])
    kumoLow  = min(leadLine1[displacement-1], leadLine2[displacement-1])

    continuationSignalLong / Short = one of eight branches selected by
    `signalChoice` (default "Tenkan/Kijun" -> crossover/crossunder of
    conversionLine vs baseLine)

    ATR = atr(14) * pipAdjuster                 // 100000, or 1000 for a JPY pair
    SL  = ATR * SLmultiplier ; TP = ATR * TPmultiplier

    timeFilter = (year > 2020 - YearOfTesting)

    if (longCondition  and timeFilter) strategy.entry("Long",  strategy.long)
    if (shortCondition and timeFilter) strategy.entry("Short", strategy.short)

    strategy.exit("ATR", from_entry="Long",  profit=TP, loss=SL)
    strategy.exit("ATR", from_entry="Short", profit=TP, loss=SL)

`strategy("BV's ICHIMOKU CLOUD SIGNAL TESTER", overlay=true)` declares no
sizing or cost properties, so Pine's documented defaults are in force and
carried here: fixed / 1 contract / initial_capital 1000000 / commission 0% /
pyramiding 0 / process_orders_on_close false.

The `/*backtest` header declares `period: 1h` on Futures_Binance BTC_USDT;
its `basePeriod: 15m` is the FMZ backtester's own fill granularity, not the
strategy's period, so `timeframe` is "1h".

FIDELITY:

* `donchian(len)` is `avg(lowest(len), highest(len))` -- `lowest`/`highest`
  default to `low`/`high`, so the band is `(lowest(low, len) + highest(high, len))
  / 2` and NOT a close-based midpoint. It is written out explicitly.
* `profit=` / `loss=` are in TICKS in Pine, and the engine applies its
  `mintick` (0.1 for BTC/USDT:USDT, which is what `source_mintick` carries) when
  it turns them into prices: `loss = avg_price - side*loss*tick`,
  `profit = avg_price + side*profit*tick`. The port therefore passes TP / SL
  through unconverted, exactly as the source spells them.
* The ATR is scaled by `pipAdjuster` = 100000 (1000 for a JPY pair), so on BTC
  data the stop and target are ~5 orders of magnitude away from the price and
  will not trigger inside a realistic backtest. That is the SOURCE's arithmetic
  (it was written for a pip-denominated FX pair) and it is reproduced rather
  than "fixed": leaving the exit effectively inert is the source's behaviour.
* ORDER-ID REPLACEMENT: the port keeps the ORDER of the two exit calls because
  Pine replaces a resting order that reuses the same id. Both calls use the id
  "ATR", so the SECOND one ("Short") replaces the first ("Long") and only the
  short entry carries a live exit. The engine models the same replace-by-id
  rule, so the port states the calls literally instead of inventing a
  disambiguated behaviour the source does not have. Recorded, not "corrected".
* `year` in Pine is the EXCHANGE's timezone (PINE_SEMANTICS.md 3.4); the local
  data is UTC and the port reads the index year, so a non-UTC exchange would
  shift bars near a year boundary.
* `JPYPair` is an `input.bool` used as a TERNARY CONDITION
  (`JPYPair ? 1000 : 100000`), never in a `!= 0` / `+` / `*` numeric context, so
  PINE_SEMANTICS.md 1.16 does not apply; the port tests it for truth directly.
* `atr(14)` is `rma(tr, 14)`; `pine_ta.pine_atr` is that, with its first-bar
  `tr` = high-low (PINE_SEMANTICS.md 3.7 records that Pine's `ta.tr` means na
  there, which can move the rma seed by one bar). Public-layer boundary.
* MD/SOURCE MISMATCH: the md argument table renders `v_input_8` (ATR Take Profit
  Multiplier) as `true`; the source declares `defval = 1.0`. The source's 1.0 is
  carried.
* `plot()` / `fill()` (and the `offset=` arguments on them) are display-only and
  are not reproduced.
* Leverage, margin, liquidation and funding are not modelled, and neither is
  the venue's contract-step rounding (measured separately by the chain
  verifier).
"""
import numpy as np
import pandas as pd
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase

_SIGNAL_CHOICES = (
    "Tenkan/Kijun",
    "Tenkan/Kijun+Kumo",
    "Price/Tenkan",
    "Price/Tenkan+Kumo",
    "Price/Kijun",
    "Price/Kijun+Kumo",
    "Price/Kumo",
    "Kumo Color",
)


class SMBvsIchimokuCloud_4fabc0(PinePortBase, IStrategy):
    source_id = "SM_4fabc038b8fb382c"
    source_file = "BVs-ICHIMOKU-CLOUD-All-Signals.md"
    timeframe = "1h"
    can_short = True
    source_defaults: dict = {
        "signalChoice": "Tenkan/Kijun",
        "JPYPair": False,
        "conversionPeriods": 9,
        "basePeriods": 26,
        "laggingSpan2Periods": 52,
        "displacement": 26,
        "SLmultiplier": 1.5,
        "TPmultiplier": 1.0,
        "YearOfTesting": 3,
    }
    # strategy(title, overlay) only: Pine defaults.
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    source_reproduce_stops = True
    source_fidelity_notes = [
        "donchian(len) = avg(lowest(len), highest(len)) uses low/high, not close; "
        "written out explicitly.",
        "profit= / loss= are ticks; the engine applies mintick (0.1 here) when "
        "converting them to prices, so TP/SL are passed through unconverted.",
        "The ATR is multiplied by 100000 (pipAdjuster), so stop and target are "
        "orders of magnitude away and will not trigger on BTC data. This is the "
        "source's own arithmetic (it targets a pip-quoted FX pair) and is "
        "reproduced, not corrected.",
        "Both strategy.exit calls reuse the id 'ATR', and Pine replaces a resting "
        "order that reuses an id -- so the 'Short' call replaces the 'Long' one "
        "and only the short entry has a live exit. The port states both calls "
        "literally; the engine models the same replace-by-id rule.",
        "`year` is the exchange timezone in Pine (PINE_SEMANTICS.md 3.4); the "
        "port uses the UTC index year of the local data.",
        "JPYPair is a bool used only as a ternary condition, not in a numeric "
        "comparison, so PINE_SEMANTICS.md 1.16 does not apply.",
        "atr(14) = rma(tr, 14) via pine_ta.pine_atr, whose first-bar tr is "
        "high-low (PINE_SEMANTICS.md 3.7 records Pine's ta.tr as na there, which "
        "can move the rma seed by one bar). Public-layer boundary.",
        "MD/SOURCE MISMATCH: the md argument table shows the ATR Take Profit "
        "Multiplier default as `true`; the source says 1.0. Source followed.",
        "plot() / fill() are display-only and are not reproduced.",
        "Leverage, margin, liquidation, funding and contract-step rounding are "
        "not modelled.",
    ]

    def _choice_series(self, choice, conversion, base, lead1, lead2, close,
                       kumo_high, kumo_low):
        """The source's nested ternary chain, branch by branch."""
        false = pd.Series(False, index=close.index)
        if choice == "Tenkan/Kijun":
            long_sig = ta.pine_crossover(conversion, base)
            short_sig = ta.pine_crossunder(conversion, base)
        elif choice == "Tenkan/Kijun+Kumo":
            long_sig = ta.pine_crossover(conversion, base) & (close > kumo_high)
            short_sig = ta.pine_crossunder(conversion, base) & (close < kumo_low)
        elif choice == "Price/Tenkan":
            long_sig = ta.pine_crossover(close, conversion)
            short_sig = ta.pine_crossunder(close, conversion)
        elif choice == "Price/Tenkan+Kumo":
            long_sig = ta.pine_crossover(close, conversion) & (close > kumo_high)
            short_sig = ta.pine_crossunder(close, conversion) & (close < kumo_low)
        elif choice == "Price/Kijun":
            long_sig = ta.pine_crossover(close, base)
            short_sig = ta.pine_crossunder(close, base)
        elif choice == "Price/Kijun+Kumo":
            long_sig = ta.pine_crossover(close, base) & (close > kumo_high)
            short_sig = ta.pine_crossunder(close, base) & (close < kumo_low)
        elif choice == "Price/Kumo":
            long_sig = ta.pine_crossover(close, kumo_high)
            short_sig = ta.pine_crossunder(close, kumo_low)
        elif choice == "Kumo Color":
            long_sig = ta.pine_crossover(lead1, lead2)
            short_sig = ta.pine_crossunder(lead1, lead2)
        else:
            long_sig = false
            short_sig = false
        return long_sig.fillna(False), short_sig.fillna(False)

    def pine_indicators(self, dataframe, params):
        choice = str(params["signalChoice"])
        if choice not in _SIGNAL_CHOICES:
            raise ValueError(f"unsupported signalChoice {choice!r}")
        conversion_periods = int(params["conversionPeriods"])
        base_periods = int(params["basePeriods"])
        lagging_span2_periods = int(params["laggingSpan2Periods"])
        displacement = int(params["displacement"])
        sl_multiplier = float(params["SLmultiplier"])
        tp_multiplier = float(params["TPmultiplier"])
        year_of_testing = int(params["YearOfTesting"])

        low, high = dataframe["low"], dataframe["high"]
        close = dataframe["close"]

        # donchian(len) => avg(lowest(len), highest(len))
        def donchian(length):
            return (ta.pine_lowest(low, length) + ta.pine_highest(high, length)) / 2.0

        conversion_line = donchian(conversion_periods)
        base_line = donchian(base_periods)
        lead_line1 = (conversion_line + base_line) / 2.0  # avg(conversionLine, baseLine)
        lead_line2 = donchian(lagging_span2_periods)

        # kumoHigh = max(leadLine1[displacement-1], leadLine2[displacement-1])
        shift = displacement - 1
        lead1_shifted = lead_line1.shift(shift)
        lead2_shifted = lead_line2.shift(shift)
        kumo_high = pd.concat([lead1_shifted, lead2_shifted], axis=1).max(axis=1)
        kumo_low = pd.concat([lead1_shifted, lead2_shifted], axis=1).min(axis=1)
        # Pine's max/min are na-propagating in the sense that a missing operand
        # makes the comparison na -> the whole expression false downstream; a
        # window that has not formed yet is represented as NaN here so the
        # `close > kumoHigh` legs stay false.
        kumo_high = kumo_high.where(lead1_shifted.notna() & lead2_shifted.notna())
        kumo_low = kumo_low.where(lead1_shifted.notna() & lead2_shifted.notna())

        long_sig, short_sig = self._choice_series(
            choice, conversion_line, base_line, lead_line1, lead_line2, close,
            kumo_high, kumo_low,
        )

        # ATR = atr(14) * pipAdjuster ; SL = ATR * SLmultiplier ; TP = ATR * TPmultiplier
        pip_adjuster = 1000 if params["JPYPair"] else 100000
        atr = ta.pine_atr(dataframe, 14) * float(pip_adjuster)
        sl_ticks = atr * sl_multiplier
        tp_ticks = atr * tp_multiplier

        # timeFilter = (year > 2020 - YearOfTesting)
        index = dataframe.index
        if isinstance(index, pd.DatetimeIndex):
            bar_year = pd.Series(index.year, index=index)
        else:
            bar_year = pd.Series(np.zeros(len(index), dtype=int), index=index)
        time_filter = bar_year > (2020 - year_of_testing)

        dataframe["pine_conversion_line"] = conversion_line
        dataframe["pine_base_line"] = base_line
        dataframe["pine_lead_line1"] = lead_line1
        dataframe["pine_lead_line2"] = lead_line2
        dataframe["pine_kumo_high"] = kumo_high
        dataframe["pine_kumo_low"] = kumo_low
        dataframe["pine_long_signal"] = long_sig
        dataframe["pine_short_signal"] = short_sig
        dataframe["pine_sl_ticks"] = sl_ticks
        dataframe["pine_tp_ticks"] = tp_ticks
        # if (longCondition and timeFilter) / if (shortCondition and timeFilter)
        dataframe["pine_long_condition"] = (long_sig & time_filter).fillna(False)
        dataframe["pine_short_condition"] = (short_sig & time_filter).fillna(False)
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "long_condition": dataframe["pine_long_condition"].to_numpy(),
            "short_condition": dataframe["pine_short_condition"].to_numpy(),
            "sl_ticks": dataframe["pine_sl_ticks"].to_numpy(),
            "tp_ticks": dataframe["pine_tp_ticks"].to_numpy(),
        }

    def pine_script(self, broker, i, ctx):
        # if (longCondition and timeFilter) strategy.entry("Long", strategy.long)
        if ctx["long_condition"][i]:
            broker.entry("Long", "long")

        # if (shortCondition and timeFilter) strategy.entry("Short", strategy.short)
        if ctx["short_condition"][i]:
            broker.entry("Short", "short")

        # strategy.exit("ATR", from_entry="Long",  profit=TP, loss=SL)
        broker.exit(
            "ATR",
            from_entry="Long",
            profit=float(ctx["tp_ticks"][i]),
            loss=float(ctx["sl_ticks"][i]),
        )

        # strategy.exit("ATR", from_entry="Short", profit=TP, loss=SL)
        # (same order id: per Pine's replace-by-id rule this one supersedes the
        #  Long exit above; the source is spelled out literally)
        broker.exit(
            "ATR",
            from_entry="Short",
            profit=float(ctx["tp_ticks"][i]),
            loss=float(ctx["sl_ticks"][i]),
        )
