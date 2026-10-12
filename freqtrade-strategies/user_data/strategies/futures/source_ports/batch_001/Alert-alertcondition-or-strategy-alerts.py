"""Port of sources/SM_a4c003093730deb0.pine
(batch_001/Alert-alertcondition-or-strategy-alerts.md).

Pine v4. A stochastic %K/%D cross with a level filter, entered with a RESTING
STOP order one `entry_distance` tick beyond the signal bar's own close, and
managed by a pivot-derived stop plus a fixed tick take-profit:

    periodK = 13; periodD = 3; smoothK = 4        (literals, not inputs)
    k = sma(stoch(close, high, low, periodK), smoothK)
    d = sma(k, periodD)
    GoLong  = crossover(k, d)  and k < 80
    GoShort = crossunder(k, d) and k > 20

    piv_high = pivothigh(high, 1, 1);  piv_low = pivotlow(low, 1, 1)
    var float stoploss_long = low          # initialised on bar 0 only
    var float stoploss_short = high
    pl = valuewhen(piv_low,  piv_low,  0)
    ph = valuewhen(piv_high, piv_high, 0)
    if GoLong  -> stoploss_long  := low  < pl ? low  : pl
    if GoShort -> stoploss_short := high > ph ? high : ph

    CancelLong  = crossunder(low,  stoploss_long)  and position_size[1] <= 0 and position_size <= 0
    CancelShort = crossover(high, stoploss_short) and position_size[1] >= 0 and position_size >= 0

    strategy.entry("Long",  strategy.long,  when=GoLong,  stop=close + entry_distance*mintick)
    strategy.exit("XLong",  from_entry="Long",  stop=stoploss_long,  profit=TakeProfitLevel)
    strategy.cancel("Long", when=CancelLong)
    strategy.entry("Short", strategy.short, when=GoShort, stop=close - entry_distance*mintick)
    strategy.exit("XShort", from_entry="Short", stop=stoploss_short, profit=TakeProfitLevel)
    strategy.cancel("Short", when=CancelShort)

`strategy()` declares its own properties, and NOT Pine's defaults:

    commission_type = strategy.commission.cash_per_order, commission_value = 0.00003
    default_qty_value = 100000, initial_capital = 1000
    default_qty_type = not declared -> Pine's default strategy.fixed
    pyramiding      = not declared -> Pine's default 0
    overlay = true

The `/*backtest` header declares `period: 4h` on Futures_Binance BTC_USDT, so
`timeframe` is "4h"; `basePeriod: 15m` is the FMZ backtester's fill granularity.

FIDELITY (what is kept, what is a modelling choice, what cannot be done):

* `stoch(source, high, low, length)` is Pine v4's raw %K and is written out
  here -- `100*(source - lowest(low,length)) / (highest(high,length) -
  lowest(low,length))` -- rather than swapped for a library oscillator whose
  smoothing/source differ.
* The stop order placed at `close +/- entry_distance * syminfo.mintick` is a
  RESTING ENTRY. It fills on a LATER bar at that level, which Freqtrade's
  strategy interface cannot express (PINE_SEMANTICS.md 二.11): the projected
  `enter_long` / `enter_short` is a market order at the next bar's open. Where
  the next bar trades through the level the prices agree, otherwise they do not,
  and when the level is never touched the engine stays flat while the framework
  is already in. This is a framework boundary, not a port defect; it is the
  reason this port is expected to compare as a mismatch.
* `profit=TakeProfitLevel` is in TICKS; the port passes it through as ticks and
  lets the engine resolve `avg_price +/- 400*mintick`, which is the same
  conversion PINE_SEMANTICS.md 3.5 requires of a port.
* commission is declared by the source as `strategy.commission.cash_per_order`
  with value 0.00003 -- a cash amount PER ORDER, which the engine does not
  model (it models a percent of notional). Carrying 0.00003 as a percent would
  be a far larger cost, because the source's `fixed`/100000 sizing makes the
  notional enormous; the port therefore carries source_commission_percent = 0.0
  and records the real declaration here. The absolute commission the source
  charges is 0.00003 currency units per order (nil), so the cost basis is
  unaffected either way.
* `var float stoploss_long = low` is a Pine `var`: it initialises ONCE, on bar
  0, from that bar's low/high, then persists and is reassigned only when
  GoLong/GoShort fires. It is reproduced as a carried value, including Pine's
  `low < na -> false -> pl (na)` branch, which can make the stop na (and hence
  `CancelLong` false) until the first pivot is available.
* `strategy.position_size[1]` is the previous bar's position, carried in
  context. At bar 0 it is na, and `na <= 0` is false in Pine, so both cancel
  conditions are false there.
* `pivothigh`/`pivotlow` with left=right=1 report the pivot `right` bars after
  it, and `valuewhen(..., 0)` carries the most recent reported value forward --
  both are pine_ta.pine_pivothigh / pine_pivotlow / pine_valuewhen, which
  define exactly that.
* `strategy.exit` is called every bar (the source does not gate it on the
  position); the engine keeps one order per id and replaces it, and an exit
  whose `from_entry` is not open is neither filled nor published
  (PINE_SEMANTICS.md 1.12).
* `default_qty_value=100000` with `strategy.fixed` means 100000 contracts per
  entry against an initial capital of 1000. The engine has no margin check and
  opens them; the framework's max-stake gate will refuse the notional, which is
  PINE_SEMANTICS.md 1.5's framework veto and is reported, not hidden.
* `alert()` / `plot` / `plotshape` calls are display/alert only and are not
  reproduced; `syminfo.mintick` on BTC/USDT:USDT is 0.1.
"""
import numpy as np
import pandas as pd
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


def _level(value) -> float | None:
    """A price, or None when Pine would have na there (no resting leg)."""
    value = float(value)
    return value if np.isfinite(value) else None


class SMAlertAlertconditionStrategyAlerts_a4c003(PinePortBase, IStrategy):
    source_id = "SM_a4c003093730deb0"
    source_file = "Alert-alertcondition-or-strategy-alerts.md"
    timeframe = "4h"
    can_short = True
    # Input defaults, exactly as written in the source.
    source_defaults: dict = {
        "TakeProfitLevel": 400,
        "entry_distance": 10,
    }
    # periodK / periodD / smoothK are literals in the source, not inputs; they
    # are kept as literals in pine_indicators.
    #
    # strategy(title=..., commission_type=strategy.commission.cash_per_order,
    #          commission_value=0.00003, overlay=true, default_qty_value=100000,
    #          initial_capital=1000)
    source_qty_type = "fixed"
    source_qty_value = 100000.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1000.0
    # strategy.exit(stop=..., profit=...): both legs rest inside the bar.
    source_reproduce_stops = True
    source_mintick = 0.1
    source_fidelity_notes = [
        "Both entries are RESTING STOP orders at close +/- 10*mintick, which "
        "Freqtrade has no expression for; the projected signal is a next-open "
        "market order (PINE_SEMANTICS.md 二.11). Expected cause of mismatch.",
        "The source's commission is `strategy.commission.cash_per_order` with "
        "value 0.00003 -- cash per order, which the engine does not model. It "
        "is recorded here and the port carries 0.0 percent rather than "
        "misreading 0.00003 as a percent of notional.",
        "`default_qty_type` is not declared, so Pine's documented default "
        "strategy.fixed applies; with default_qty_value=100000 against "
        "initial_capital=1000 the framework's max-stake gate should veto the "
        "entries (PINE_SEMANTICS.md 1.5) -- reported, not compensated.",
        "`stoch(close, high, low, 13)` is written out from Pine v4's own "
        "definition rather than substituted with a library oscillator.",
        "`var float stoploss_long = low` / `stoploss_short = high` initialise "
        "once on bar 0 and persist; reproduced as carried values, including "
        "the branch that makes the stop na before the first pivot exists.",
        "`strategy.position_size[1]` is carried across bars; it is na on bar 0 "
        "and `na <= 0` is false in Pine, so both cancels are false there.",
        "`profit=TakeProfitLevel` is in ticks and is passed as ticks, resolved "
        "by the engine against the position's average price.",
        "The source places both exits unconditionally every bar; the engine "
        "keeps one order per id and ignores an exit whose from_entry is not "
        "open (PINE_SEMANTICS.md 1.12).",
        "`alert()`, `plot`, `plotshape` are display/alert only; not reproduced.",
    ]

    # ---- indicators --------------------------------------------------------
    def pine_indicators(self, dataframe, params):
        close = dataframe["close"]
        high = dataframe["high"]
        low = dataframe["low"]

        period_k, period_d, smooth_k = 13, 3, 4

        # k = sma(stoch(close, high, low, periodK), smoothK)
        # stoch(source, high, low, length) in v4 is the raw %K:
        #   100 * (source - lowest(low, length)) / (highest(high, length) - lowest(low, length))
        lowest_low = ta.pine_lowest(low, period_k)
        highest_high = ta.pine_highest(high, period_k)
        span = highest_high - lowest_low
        with np.errstate(divide="ignore", invalid="ignore"):
            raw_k = 100.0 * (close - lowest_low) / span
        raw_k = raw_k.where(span != 0.0)
        k = ta.pine_sma(raw_k, smooth_k)
        d = ta.pine_sma(k, period_d)

        go_long = ta.pine_crossover(k, d) & (k < 80)
        go_short = ta.pine_crossunder(k, d) & (k > 20)

        # piv_high = pivothigh(high, 1, 1) / piv_low = pivotlow(low, 1, 1),
        # reported one bar after the pivot; valuewhen(..., 0) carries the most
        # recent reported value forward.
        pivot_high = ta.pine_pivothigh(high, 1, 1)
        pivot_low = ta.pine_pivotlow(low, 1, 1)
        pl = ta.pine_valuewhen(pivot_low.notna(), pivot_low, 0)
        ph = ta.pine_valuewhen(pivot_high.notna(), pivot_high, 0)

        # var float stoploss_long = low  /  var float stoploss_short = high
        count = len(dataframe)
        low_values = low.to_numpy(dtype=float)
        high_values = high.to_numpy(dtype=float)
        pl_values = pl.to_numpy(dtype=float)
        ph_values = ph.to_numpy(dtype=float)
        long_flags = go_long.fillna(False).to_numpy(dtype=bool)
        short_flags = go_short.fillna(False).to_numpy(dtype=bool)
        stoploss_long = np.full(count, np.nan)
        stoploss_short = np.full(count, np.nan)
        carried_long = low_values[0]
        carried_short = high_values[0]
        for i in range(count):
            if long_flags[i]:
                # low < pl ? low : pl  -- with pl na this yields na
                carried_long = low_values[i] if low_values[i] < pl_values[i] else pl_values[i]
            if short_flags[i]:
                # high > ph ? high : ph
                carried_short = high_values[i] if high_values[i] > ph_values[i] else ph_values[i]
            stoploss_long[i] = carried_long
            stoploss_short[i] = carried_short

        stoploss_long = pd.Series(stoploss_long, index=dataframe.index, dtype=float)
        stoploss_short = pd.Series(stoploss_short, index=dataframe.index, dtype=float)

        dataframe["pine_k"] = k
        dataframe["pine_d"] = d
        dataframe["pine_go_long"] = go_long.fillna(False).astype(bool)
        dataframe["pine_go_short"] = go_short.fillna(False).astype(bool)
        dataframe["pine_stoploss_long"] = stoploss_long
        dataframe["pine_stoploss_short"] = stoploss_short
        # CancelLong / CancelShort with the two position_size terms factored out
        # into pine_script, where the broker's position is known.
        dataframe["pine_cross_down_long"] = ta.pine_crossunder(
            low, stoploss_long
        ).to_numpy(dtype=bool)
        dataframe["pine_cross_up_short"] = ta.pine_crossover(
            high, stoploss_short
        ).to_numpy(dtype=bool)
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "go_long": dataframe["pine_go_long"].to_numpy(dtype=bool),
            "go_short": dataframe["pine_go_short"].to_numpy(dtype=bool),
            "stoploss_long": dataframe["pine_stoploss_long"].to_numpy(dtype=float),
            "stoploss_short": dataframe["pine_stoploss_short"].to_numpy(dtype=float),
            "cross_down_long": dataframe["pine_cross_down_long"].to_numpy(dtype=bool),
            "cross_up_short": dataframe["pine_cross_up_short"].to_numpy(dtype=bool),
            "close": dataframe["close"].to_numpy(dtype=float),
            "take_profit_ticks": float(params["TakeProfitLevel"]),
            "entry_distance": float(params["entry_distance"]),
            # strategy.position_size[1]; na on bar 0, which makes both cancel
            # conditions false there (`na <= 0` is false in Pine).
            "state": {"prev_position": float("nan")},
        }

    # ---- orders ------------------------------------------------------------
    def pine_script(self, broker, i, ctx):
        close = float(ctx["close"][i])
        offset = ctx["entry_distance"] * float(self.source_mintick)
        state = ctx["state"]
        prev_position = state["prev_position"]
        position = broker.position_size

        stoploss_long = ctx["stoploss_long"][i]
        stoploss_short = ctx["stoploss_short"][i]

        # CancelLong = crossunder(low, stoploss_long) and position_size[1] <= 0
        #              and position_size <= 0
        cancel_long = (
            bool(ctx["cross_down_long"][i]) and prev_position <= 0 and position <= 0
        )
        # CancelShort = crossover(high, stoploss_short) and position_size[1] >= 0
        #               and position_size >= 0
        cancel_short = (
            bool(ctx["cross_up_short"][i]) and prev_position >= 0 and position >= 0
        )

        # strategy.entry("Long", strategy.long, when=GoLong, stop=close+entry_distance*mintick)
        if ctx["go_long"][i]:
            broker.entry("Long", "long", stop=close + offset)
        # strategy.exit("XLong", from_entry="Long", stop=stoploss_long, profit=TakeProfitLevel)
        broker.exit(
            "XLong", from_entry="Long",
            stop=_level(stoploss_long),
            profit=ctx["take_profit_ticks"],
        )
        # strategy.cancel("Long", when = CancelLong)
        if cancel_long:
            broker.cancel("Long")

        # strategy.entry("Short", strategy.short, when=GoShort, stop=close-entry_distance*mintick)
        if ctx["go_short"][i]:
            broker.entry("Short", "short", stop=close - offset)
        # strategy.exit("XShort", from_entry="Short", stop=stoploss_short, profit=TakeProfitLevel)
        broker.exit(
            "XShort", from_entry="Short",
            stop=_level(stoploss_short),
            profit=ctx["take_profit_ticks"],
        )
        # strategy.cancel("Short", when = CancelShort)
        if cancel_short:
            broker.cancel("Short")

        state["prev_position"] = position
