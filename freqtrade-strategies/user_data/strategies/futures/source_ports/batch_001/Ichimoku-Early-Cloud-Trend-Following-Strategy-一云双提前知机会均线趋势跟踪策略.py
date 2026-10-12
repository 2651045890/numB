"""Port of sources/SM_3dca6615c95e29c0.pine (batch_001/Ichimoku-Early-Cloud-Trend-Following-Strategy-一云双提前知机会均线趋势跟踪策略.md).

Pine v4. QuantCT's "Ichimoku Cloud Strategy Idea": the standard Ichimoku lines,
compared against price with HISTORY references (not the plots' display offsets),
plus an optional percentage stop bound to each entry:

    donchian(len) => avg(lowest(len), highest(len))
    conversion_line = donchian(9)
    base_line       = donchian(26)
    lead_line1      = avg(conversion_line, base_line)
    lead_line2      = donchian(52)
    chikou          = close

    chikou_free_long  = close > high[displacement] and
                        close > max(lead_line1[2*displacement], lead_line2[2*displacement])
    enter_long        = chikou_free_long and
                        close > max(lead_line1[displacement], lead_line2[displacement])
    exit_long         = close < lead_line1[displacement] or close < lead_line2[displacement]

    chikou_free_short = close < low[displacement] and
                        close < min(lead_line1[2*displacement], lead_line2[2*displacement])
    enter_short       = chikou_free_short and
                        close < min(lead_line1[displacement], lead_line2[displacement])
    exit_short        = close > lead_line1[displacement] or close > lead_line2[displacement]

    strategy.entry("Long",  strategy.long, when=enter_long)
    strategy.close("Long",  when=exit_long)
    if (not long_only)
        strategy.entry("Short", strategy.short, when=enter_short)
        strategy.close("Short", when=exit_short)

    sl_long  = strategy.position_avg_price * (1 - (slp / 100))
    sl_short = strategy.position_avg_price * (1 + (slp / 100))
    if (use_sl)
        strategy.exit(id="SL", from_entry="Long",  stop=sl_long)
        strategy.exit(id="SL", from_entry="Short", stop=sl_short)

`donchian` is built on v4's ONE-ARGUMENT `lowest(len)` / `highest(len)`, whose
source defaults to the bar's `low` / `high` (not close) -- so it is a Donchian
channel on low/high, which is what the port computes. `avg(a, b)` is
`(a + b) / 2`.

`strategy.close` is a MARKET close of the entry it names, so the engine fills it
at the next bar's open, exactly as Pine does. The `enter_*` and `exit_*`
conditions cannot both be true on one bar: `enter_long` needs
`close > max(lead_line1[d], lead_line2[d])` while `exit_long` needs
`close < lead_line1[d] or close < lead_line2[d]`, which that implies is false;
the short side is the mirror image.

`long_only` and `use_sl` are `input`s, so they are broadcast per bar through
`pine_context` and read in `pine_script` like any other Pine series.

`strategy()` declares `pyramiding=0`, `default_qty_type=strategy.percent_of_equity`,
`default_qty_value=99`, `initial_capital=1000`, and
`commission_type=strategy.commission.percent` / `commission_value=0.1`; the
`overlay` / `shorttitle` / title arguments have no trade effect.

The `/*backtest` header declares `period: 1d` on `Futures_Binance` BTC_USDT, so
`timeframe` is "1d". `basePeriod: 1h` is the FMZ backtester's own fill
granularity, not the strategy's period.

FIDELITY -- what is preserved, and what is a recorded uncertainty:

* `lowest(len)` / `highest(len)` are v4's one-argument forms; the port computes
  `ta.pine_lowest(dataframe["low"], len)` and
  `ta.pine_highest(dataframe["high"], len)`. The one-argument forms' default
  source is documented as low / high respectively; that reading was checked
  against the v4 documentation, not measured on the platform.
* All four cloud comparisons use HISTORY references, reproduced with `.shift()`.
  The three `plot` offsets (`+displacement` on the two lead lines,
  `-displacement` on `chikou`) are display-only and are NOT shifts of the data;
  `fill()` likewise places no order.
* `chikou = close` is computed and is read only by `plot(chikou, offset=...)`,
  which is display-only. It is carried as a column so the source's computation
  is not dropped.
* `colors = enter_long ? ... : enter_short ? ... : color.orange` is computed and
  read only by the two plots; it has no trade effect and is not reproduced.
* `sl_long` / `sl_short` are computed EVERY bar, before the `if (use_sl)` guard,
  exactly as the source computes them, and are na while flat. Only the values
  inside the guard are used, so computing them unconditionally changes nothing
  observable -- but the source's shape is kept.
* `strategy.exit(id="SL", ...)` is called TWICE per bar with the SAME id and a
  different `from_entry`. In the declared default configuration (`use_sl =
  false`) neither call is reached at all, so no exit order exists and the
  question does not arise. MEASURED with `use_sl = true` on BTC/USDT:USDT 1d,
  2024-01-01..2025-01-01 (367 bars), against the `use_sl = false` run on the same
  window: 13 round trips instead of 11, and three of the closes land exactly
  on a SHORT's `position_avg_price * 1.05` (54009.6 -> 56710.08 on 2024-08-07,
  58685.2 -> 61619.46 on 2024-08-21, 61158.8 -> 64216.74 on 2024-08-23) while
  nothing lands on a long's `* 0.95`, and all three arrive as `exit` orders
  rather than `close` fills.
  That is positive evidence only for the Short-bound leg resting under the shared
  id, which is what `PineBroker._place` does (one order per id, second call
  replaces the first). It is NOT proof the Long-bound leg is absent -- a long
  stop simply need not have been reached in this window -- so it is recorded as
  the engine's modelled behaviour rather than as an established Pine fact.
  Whether Pine's real engine keys the two calls apart is UNPUBLISHED;
  PINE_SEMANTICS.md 3.6 records the same class of risk for same-id re-placement.
* MEASURED on BTC/USDT:USDT 1d, the default verification window
  2024-01-01..2025-01-01: with the declared defaults (`use_sl = false`,
  `long_only = false`) the port books 11 closed round trips and 1 position still
  open at the end (long 0.0083995 at 64278.2, opened on bar 268). 0 of the 11 end
  on an exit order -- none can, because `strategy.exit` is only reached when
  `use_sl` is true -- so every close is a `strategy.close` market fill or an
  opposite entry reversing the position. The framework side of the same run
  agrees: 11 closed trades, all with `exit_reason = exit_signal`, plus one
  force-exit at the window boundary.
* `source_reproduce_stops` is True: `strategy.exit(stop=...)` is a real,
  entry-bound stop leg and it does arm when `use_sl` is set.
* The md's code block is line-for-line identical to
  sources/SM_3dca6615c95e29c0.pine. The md's argument table has seven rows and
  each matches the corresponding `input()` default (9, 26, 52, 26, false, 5,
  false); no md-vs-code disagreement was found.
* The md PROSE describes the Ichimoku cloud in general terms and never mentions
  `chikou`, `high[displacement]` or the `2 * displacement` filter. That is
  incompleteness, not contradiction: nothing in the prose contradicts the code.
* No `security()` call, no `barstate.isrealtime` branch, no repainting and no
  future-data reference. In particular the `[displacement]` / `[2 * displacement]`
  references look BACKWARD (they are `shift(+n)`), so they do not repaint.
* CHAIN VERIFICATION (`verify_chain.py --port SM_3dca6615c95e29c0`, BTC/USDT:USDT
  1d 2024-01-01..2025-01-01): every trade agrees on open date, close date,
  direction, open price and close price -- 11 vs 11 trades, all mismatch counts
  0, `max_price_gap` 0.0 -- but the verdict is `mismatch` on
  `pnl_beyond_step_mismatches: 11`, `max_pnl_gap` 0.65675
  (`max_pnl_gap_relative` 7.6e-4). ATTRIBUTED, NOT FIXED: the cause is the
  venue's contract-step rounding of the ORDER SIZE, which this port does not
  control and must not paper over. The engine holds a float quantity
  (0.014950, 0.012696, ...) while Freqtrade rounds the amount DOWN to the
  0.0001 contract step (0.0149, 0.0126, ...); measured qty gaps are 1e-5..9.6e-5,
  inside the comparison's own `step_allowance` of 1e-3, but that size error
  reaches the P&L through the trade's price move (9.6e-5 x 6679.4 = 0.64 on the
  worst trade) while the comparison's P&L allowance is only
  `1e-5 * notional` = 0.009. So `pnl_allowance` is roughly 70x tighter than the
  `step_allowance` it is meant to be consistent with, and the gap it flags is
  exactly the rounding it declares admissible. This is a property of
  verify_chain's tolerances, not of the port; `verify_chain.py` is a shared-layer
  file and was not modified.
* Leverage, margin, liquidation, funding and the venue's contract-step rounding
  of order quantities are not modelled.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


def _donchian(dataframe: pd.DataFrame, length: int) -> pd.Series:
    """`donchian(len) => avg(lowest(len), highest(len))` on low/high.

    The one-argument v4 `lowest` / `highest` default to the bar's low / high.
    """
    return ta.pine_avg(
        ta.pine_lowest(dataframe["low"], length),
        ta.pine_highest(dataframe["high"], length),
    )


class SMIchimokuEarlyCloud_3dca66(PinePortBase, IStrategy):
    source_id = "SM_3dca6615c95e29c0"
    source_file = (
        "Ichimoku-Early-Cloud-Trend-Following-Strategy-一云双提前知机会均线趋势跟踪策略.md"
    )
    timeframe = "1d"
    can_short = True
    source_defaults: dict = {
        "conversion_period": 9,
        "base_period": 26,
        "lagging_span2_period": 52,
        "displacement": 26,
        "long_only": False,
        "slp": 5.0,
        "use_sl": False,
    }
    source_qty_type = "percent_of_equity"
    source_qty_value = 99.0
    source_commission_percent = 0.1
    source_pyramiding = 0
    source_initial_capital = 1000.0
    source_reproduce_stops = True
    source_fidelity_notes = [
        "donchian(len) uses v4's one-argument lowest(len) / highest(len), whose "
        "source defaults to the bar's low / high; the port computes "
        "lowest(low, len) and highest(high, len), i.e. a Donchian channel.",
        "The four cloud comparisons use HISTORY references "
        "(lead_line1[displacement], lead_line1[2 * displacement], ...), "
        "reproduced with .shift(); the plots' `offset = displacement` is "
        "display-only and is not a shift of the data.",
        "chikou = close is computed and read only by the display-only plot; it is "
        "carried as a column so the computation is not dropped.",
        "colors (the plot colour ternary) is computed and read only by the plots; "
        "no trade effect, not reproduced.",
        "sl_long / sl_short are computed every bar before the `if (use_sl)` guard, "
        "as the source computes them, and are na while flat.",
        "strategy.exit(id='SL', ...) is called twice per bar with the same id and "
        "a different from_entry. With use_sl=false (the default) neither call is "
        "reached, so no exit order exists. Measured with use_sl=true on "
        "BTC/USDT:USDT 1d 2024-01-01..2025-01-01: 13 round trips vs 11 with "
        "use_sl=false, and three of the closes land exactly on a short's "
        "position_avg_price*1.05 (56710.08 on 2024-08-07, 61619.46 on 2024-08-21, "
        "64216.74 on 2024-08-23) while none lands on a long's *0.95 -- positive "
        "evidence for the Short-bound leg resting under the shared id, as "
        "PineBroker._place's one-order-per-id model predicts, but NOT proof the "
        "Long-bound leg is absent. Whether Pine keys them apart is unpublished -- "
        "recorded, not guessed. The double call is the SOURCE's own and not an "
        "extraction artifact: the platform that hosts it (fmz.com/strategy/435139, "
        "fetched 2026-09-24) renders both strategy.exit(id=\"SL\", ...) lines, "
        "bound to from_entry=\"Long\" and \"Short\" respectively, exactly as the "
        "extracted .pine does.",
        "Measured on BTC/USDT:USDT 1d 2024-01-01..2025-01-01 with the declared "
        "defaults: 11 closed round trips, 1 position still open, and 0 closes "
        "from an exit order (none is reachable while use_sl is false) -- every "
        "close is a strategy.close market fill or an opposite entry reversing "
        "the position.",
        "source_reproduce_stops is True: strategy.exit(stop=...) is a real "
        "entry-bound stop leg and does arm when use_sl is set.",
        "The md's code block is identical to the .pine and its seven-row argument "
        "table matches every input() default (9, 26, 52, 26, false, 5, false); no "
        "md-vs-code disagreement found.",
        "The md prose never mentions chikou, high[displacement] or the "
        "2 * displacement filter -- incompleteness, not contradiction.",
        "No security() call, no barstate.isrealtime branch, no repainting and no "
        "future-data reference; the [displacement] references look backward.",
        "CHAIN: verify_chain --port SM_3dca6615c95e29c0 returns 'mismatch' with "
        "open_date/close_date/direction mismatches 0 and max_price_gap 0.0, but "
        "pnl_beyond_step_mismatches 11 (max_pnl_gap 0.65675, relative 7.6e-4). "
        "Attributed: Freqtrade rounds the order amount down to the 0.0001 "
        "contract step while the engine keeps the float quantity; the measured "
        "qty gaps (1e-5..9.6e-5) sit inside the comparison's own step_allowance "
        "of 1e-3, but the comparison's pnl_allowance is only 1e-5*notional "
        "(0.009), ~70x tighter than the step it admits. The flagged gap is the "
        "admissible rounding itself. verify_chain.py is shared-layer and was "
        "not modified.",
    ]

    def pine_indicators(self, dataframe, params):
        conversion_period = int(params["conversion_period"])
        base_period = int(params["base_period"])
        lagging2_period = int(params["lagging_span2_period"])
        displacement = int(params["displacement"])

        conversion_line = _donchian(dataframe, conversion_period)
        base_line = _donchian(dataframe, base_period)
        lead_line1 = ta.pine_avg(conversion_line, base_line)
        lead_line2 = _donchian(dataframe, lagging2_period)
        chikou = dataframe["close"]

        close = dataframe["close"]
        high = dataframe["high"]
        low = dataframe["low"]

        # lead_line1[displacement] / lead_line2[displacement] and the 2x pair.
        lead1_d = lead_line1.shift(displacement)
        lead2_d = lead_line2.shift(displacement)
        lead1_2d = lead_line1.shift(2 * displacement)
        lead2_2d = lead_line2.shift(2 * displacement)
        max_d = ta.pine_max(lead1_d, lead2_d)
        min_d = ta.pine_min(lead1_d, lead2_d)
        max_2d = ta.pine_max(lead1_2d, lead2_2d)
        min_2d = ta.pine_min(lead1_2d, lead2_2d)

        # chikou_free_long = close > high[displacement] and
        #                    close > max(lead_line1[2d], lead_line2[2d])
        chikou_free_long = (close > high.shift(displacement)) & (close > max_2d)
        enter_long = chikou_free_long & (close > max_d)
        exit_long = (close < lead1_d) | (close < lead2_d)

        chikou_free_short = (close < low.shift(displacement)) & (close < min_2d)
        enter_short = chikou_free_short & (close < min_d)
        exit_short = (close > lead1_d) | (close > lead2_d)

        dataframe["pine_conversion_line"] = conversion_line
        dataframe["pine_base_line"] = base_line
        dataframe["pine_lead_line1"] = lead_line1
        dataframe["pine_lead_line2"] = lead_line2
        dataframe["pine_chikou"] = chikou
        dataframe["pine_enter_long"] = enter_long.to_numpy()
        dataframe["pine_exit_long"] = exit_long.to_numpy()
        dataframe["pine_enter_short"] = enter_short.to_numpy()
        dataframe["pine_exit_short"] = exit_short.to_numpy()
        return dataframe

    def pine_context(self, dataframe, params):
        size = len(dataframe)
        # Inputs are read through source_parameters(), so they are broadcast per
        # bar and read in pine_script like any other Pine series.
        return {
            "enter_long": dataframe["pine_enter_long"].to_numpy(),
            "exit_long": dataframe["pine_exit_long"].to_numpy(),
            "enter_short": dataframe["pine_enter_short"].to_numpy(),
            "exit_short": dataframe["pine_exit_short"].to_numpy(),
            "long_only": np.full(size, bool(params["long_only"]), dtype=bool),
            "use_sl": np.full(size, bool(params["use_sl"]), dtype=bool),
            "slp": np.full(size, float(params["slp"]), dtype=float),
        }

    def pine_script(self, broker, i, ctx):
        # strategy.entry("Long", strategy.long, when=enter_long)
        broker.entry("Long", "long", when=bool(ctx["enter_long"][i]))
        # strategy.close("Long", when=exit_long)
        broker.close("Long", when=bool(ctx["exit_long"][i]))

        # if (not long_only)
        #     strategy.entry("Short", strategy.short, when=enter_short)
        #     strategy.close("Short", when=exit_short)
        if not ctx["long_only"][i]:
            broker.entry("Short", "short", when=bool(ctx["enter_short"][i]))
            broker.close("Short", when=bool(ctx["exit_short"][i]))

        # sl_long  = strategy.position_avg_price * (1 - (slp / 100))
        # sl_short = strategy.position_avg_price * (1 + (slp / 100))
        # Computed every bar, before the guard, exactly as the source computes
        # them; strategy.position_avg_price is na while flat.
        average = broker.position_avg_price
        slp = ctx["slp"][i]
        sl_long = average * (1 - (slp / 100))
        sl_short = average * (1 + (slp / 100))

        # if (use_sl)
        #     strategy.exit(id="SL", from_entry="Long", stop=sl_long)
        #     strategy.exit(id="SL", from_entry="Short", stop=sl_short)
        if ctx["use_sl"][i]:
            broker.exit("SL", "Long", stop=sl_long)
            broker.exit("SL", "Short", stop=sl_short)
