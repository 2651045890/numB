"""Port of sources/SM_2d9a4d013af374bb.pine (batch_001/Follow-Line-Indicator.md).

The file is Dreadblitz's "Follow Line Indicator" (`//@version=4`,
`study(shorttitle="FLI", ...)`) with a converter-appended order block at the
end. A `study()` cannot host `strategy.entry` (Pine v4/v5 both reject it), so
the original script has no trades: the trading behaviour IS the appended block.

    BBUpper = sma(close, 21) + stdev(close, 21) * 1.00
    BBLower = sma(close, 21) - stdev(close, 21) * 1.00
    BBSignal = close > BBUpper ? 1 : close < BBLower ? -1 : 0
    TrendLine := low  - atr(5)   while BBSignal == 1 and UseATRfilter   (ratchet)
    TrendLine := high + atr(5)   while BBSignal == -1 and UseATRfilter  (ratchet)
    TrendLine := TrendLine[1]    while BBSignal == 0  and UseATRfilter
    (a second, identical trio uses low / high with no ATR when UseATRfilter
     is false)
    iTrend := iTrend[1]; 1 if TrendLine > TrendLine[1]; -1 if <
    buy  = iTrend[1] == -1 and iTrend == 1 ? 1 : na
    sell = iTrend[1] ==  1 and iTrend == -1 ? 1 : na

    if buy == 1 and hl == false
       strategy.entry("buy", strategy.long)
    else if sell == 1 and hl == false
        strategy.entry("sell", strategy.short)

There is NO exit anywhere in the file -- not as a live call and not as a
commented-out one -- so a position is only ever replaced by an opposite entry,
and one still open at the end of the window stays open.

FIDELITY:

* `UseATRfilter` is `input(defval=true, type=input.bool)` and the source tests
  it as `UseATRfilter == 1` / `== 0`. In Pine v4 a bool in a numeric context is
  1 / 0, so `== 1` means "true" and `== 0` means "false". Python's `bool` is an
  `int` subclass, so the literal translation would happen to agree, but the port
  branches on `if use_atr:` / `else:` instead of copying the comparison, which
  cannot be mis-read as the `!= 0` trap of PINE_SEMANTICS.md section 1.16.
* `hl == false` gates BOTH entries ("Hide Labels" also hides the arrows). It is
  reproduced as an entry gate, not as a display flag: with `hl` true the source
  really does place no order (it takes the `else if` branch, which is also
  guarded). Modelled as `not hl`; for a bool input that is exactly `hl == false`.
* `buy` / `sell` are assigned `1 : na`, i.e. na on every non-signal bar, so the
  port keeps them as NaN and tests `== 1`, which is false for NaN -- the same
  reading `if buy == 1` has in Pine.
* The state machine (`TrendLine` ratchet, `iTrend` flip) is sequential and is
  replayed bar by bar. `TrendLine[1]` on bar 0 is na and an na comparison is
  false in Pine, so the port's `nan < nan` / `nan > nan` (both False) match.
  `iTrend := iTrend[1]` therefore propagates na into the warm-up bars; `buy`
  cannot fire until a real `iTrend` exists.
* `stdev` is Pine's `ta.stdev`, i.e. the POPULATION deviation (ddof=0), which is
  what pine_ta.pine_stdev computes.
* `atr` is pine_ta.pine_atr. pine_atr seeds `ta.tr` with `high - low` on bar 0
  (handle_na=True) while Pine's own ta.tr returns na there (PINE_SEMANTICS.md
  section 3.7), so the ATR seeding can be one bar early and the whole ATR series
  can carry that offset during warm-up. Recorded, not corrected.
* `ema` is not used. `plot`, `plotshape`, `bgcolor`, `alertcondition` and the
  `atr(8)` used only by the two label offsets are display/alert-only and are not
  reproduced; none of them feeds an order.
* No `strategy()` declaration exists anywhere -- the file is a `study()` -- so
  every trade property is Pine's own default: `default_qty_type` fixed, 1
  contract, 1000000 initial capital, 0% commission, pyramiding 0,
  `process_orders_on_close` false (signals placed on the close fill at the next
  open, which is the engine's model).
* `/*backtest` declares `period: 4h` on Futures_Binance BTC_USDT, so timeframe
  is "4h"; its `basePeriod: 15m` is the FMZ backtester's fill granularity, not
  the strategy's period.
* Leverage, margin, liquidation and funding are not modelled, and the venue's
  contract-step rounding is not reproduced (the chain verifier measures that
  separately).
"""
import numpy as np
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


class SMFollowLineIndicator_2d9a4d(PinePortBase, IStrategy):
    source_id = "SM_2d9a4d013af374bb"
    source_file = "Follow-Line-Indicator.md"
    timeframe = "4h"
    can_short = True
    source_defaults: dict = {
        "BBperiod": 21,
        "BBdeviations": 1.00,
        "UseATRfilter": True,
        "ATRperiod": 5,
        "hl": False,
    }
    # No strategy() call exists in the source, so Pine's documented defaults
    # apply: fixed / 1 contract, 1000000 initial capital, 0% commission,
    # pyramiding 0, process_orders_on_close false.
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    # There is no stop, no limit and no strategy.exit in the file at all.
    source_reproduce_stops = False
    source_mintick = 0.1
    source_fidelity_notes = [
        "Converter-appended order block: the file declares `study()` (Pine v4) "
        "and appends `if buy == 1 and hl == false -> strategy.entry(...)`. The "
        "trading behaviour reproduced here is that appended block, which is the "
        "only place the source states any order at all.",
        "No exit exists in the source -- neither live nor commented out -- so a "
        "position is closed only by an opposite entry reversing it, and a "
        "position open at the end of the window stays open "
        "(source_reproduce_stops=False).",
        "`UseATRfilter == 1` / `== 0` is Pine v4's bool-as-0/1 comparison; the "
        "port branches on the boolean itself rather than copying the numeric "
        "comparison (PINE_SEMANTICS.md section 1.16).",
        "`hl == false` gates both entries -- the 'Hide Labels' switch also "
        "suppresses the orders in the source -- so it is reproduced as an entry "
        "gate.",
        "`buy` / `sell` are `1 : na`, so non-signal bars are NaN and `== 1` is "
        "the faithful test; the port keeps the NaN rather than normalising to 0.",
        "Pine v4 `stdev` is the population deviation (ddof=0); "
        "pine_ta.pine_stdev matches.",
        "pine_atr seeds ta.tr with `high - low` on bar 0 while Pine's ta.tr "
        "returns na there (PINE_SEMANTICS.md section 3.7); the ATR seed can be "
        "one bar early and the series can carry that offset through warm-up. "
        "Recorded, not corrected.",
        "The `TrendLine` ratchet and the `iTrend` flip are replayed sequentially; "
        "na comparisons are False exactly as in Pine, so `iTrend` stays na until "
        "a real trend value exists.",
        "plot / plotshape / bgcolor / alertcondition, and the `atr(8)` that only "
        "offsets the two labels, are display or alert only and are not "
        "reproduced.",
        "No `strategy()` call exists, so all trade properties are Pine's "
        "documented defaults (fixed/1, 1000000, 0%, pyramiding 0, "
        "process_orders_on_close false).",
        "Venue contract-step rounding, leverage, margin, liquidation and "
        "funding are not modelled.",
    ]

    def pine_indicators(self, dataframe, params):
        close = dataframe["close"]
        low = dataframe["low"]
        high = dataframe["high"]
        bb_period = int(params["BBperiod"])
        bb_deviations = float(params["BBdeviations"])
        atr_period = int(params["ATRperiod"])
        use_atr = bool(params["UseATRfilter"])

        # BBUpper = sma(close, BBperiod) + stdev(close, BBperiod) * BBdeviations
        bb_middle = ta.pine_sma(close, bb_period)
        bb_deviation = ta.pine_stdev(close, bb_period)
        bb_upper = bb_middle + bb_deviation * bb_deviations
        bb_lower = bb_middle - bb_deviation * bb_deviations

        # BBSignal = close>BBUpper? 1 : close<BBLower? -1 : 0
        # An na band makes both comparisons false in Pine, which lands on 0.
        close_values = close.to_numpy(dtype=float)
        upper_values = bb_upper.to_numpy(dtype=float)
        lower_values = bb_lower.to_numpy(dtype=float)
        bb_signal = np.where(
            close_values > upper_values,
            1.0,
            np.where(close_values < lower_values, -1.0, 0.0),
        )

        atr_values = ta.pine_atr(dataframe, atr_period).to_numpy(dtype=float)
        low_values = low.to_numpy(dtype=float)
        high_values = high.to_numpy(dtype=float)

        count = len(dataframe)
        trend_line = np.full(count, np.nan)
        itrend = np.full(count, np.nan)
        buy = np.full(count, np.nan)
        sell = np.full(count, np.nan)

        # `TrendLine[1]` / `iTrend[1]` are the previous bar's FINAL values.
        previous_line = np.nan
        previous_trend = np.nan
        for i in range(count):
            signal = bb_signal[i]
            # Three mutually exclusive `if` blocks per ATR-filter setting; the
            # blocks are keyed on BBSignal, so an elif chain is the same script.
            if signal == 1 and use_atr:
                line = low_values[i] - atr_values[i]
                if line < previous_line:
                    line = previous_line
            elif signal == -1 and use_atr:
                line = high_values[i] + atr_values[i]
                if line > previous_line:
                    line = previous_line
            elif signal == 0 and use_atr:
                line = previous_line
            elif signal == 1:
                line = low_values[i]
                if line < previous_line:
                    line = previous_line
            elif signal == -1:
                line = high_values[i]
                if line > previous_line:
                    line = previous_line
            else:  # signal == 0 and UseATRfilter == 0
                line = previous_line

            # iTrend := iTrend[1]; then the two comparisons, in source order.
            trend = previous_trend
            if line > previous_line:
                trend = 1.0
            if line < previous_line:
                trend = -1.0

            # buy := iTrend[1]==-1 and iTrend==1 ? 1 : na
            if previous_trend == -1 and trend == 1:
                buy[i] = 1.0
            # sell := iTrend[1]==1 and iTrend==-1 ? 1 : na
            if previous_trend == 1 and trend == -1:
                sell[i] = 1.0

            trend_line[i] = line
            itrend[i] = trend
            previous_line = line
            previous_trend = trend

        dataframe["pine_bb_upper"] = bb_upper
        dataframe["pine_bb_lower"] = bb_lower
        dataframe["pine_trend_line"] = trend_line
        dataframe["pine_itrend"] = itrend
        dataframe["pine_buy"] = buy
        dataframe["pine_sell"] = sell
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "buy": dataframe["pine_buy"].to_numpy(dtype=float),
            "sell": dataframe["pine_sell"].to_numpy(dtype=float),
            "hide_labels": bool(params["hl"]),
        }

    def pine_script(self, broker, i, ctx):
        # if buy == 1 and hl == false
        #    strategy.entry("buy", strategy.long)
        # else if sell == 1 and hl == false
        #     strategy.entry("sell", strategy.short)
        if ctx["buy"][i] == 1 and ctx["hide_labels"] is False:
            broker.entry("buy", "long")
        elif ctx["sell"][i] == 1 and ctx["hide_labels"] is False:
            broker.entry("sell", "short")
