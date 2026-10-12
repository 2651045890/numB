"""Port of sources/SM_cd224f81d15b913b.pine (batch_001/Dual-Moving-Average-Crossover-Tracking-Strategy.md).

Pine v3. BiznesFilosof's dual moving-average tracker, with a time window and a
"barred close" lag:

    startY/startM/startD/finishY/finishM/finishD -> timestart / timefinish
    window = time >= timestart and time <= timefinish

    lma1 = input(21, "Length MA1");  exponential1 = input(false, "exponential")
    lma2 = input(1,  "Length MA2");  exponential2 = input(false, "exponential")
    lbars = input(0, "Length bars close")

    ma1 = exponential1 ? ema(close, lma1) : sma(close, lma1)
    ma2 = exponential2 ? ema(close, lma2) : sma(close, lma2)
    source = ma2

    strategy.entry("LongEntryID",  strategy.long,  comment="LONG",  when = crossover(ma2, ma1)  and window)
    strategy.entry("ShortEntryID", strategy.short, comment="SHORT", when = crossunder(ma2, ma1) and window)

    if crossunder(source, ma1) and strategy.position_size > 0
        strategy.close_all()
    if crossunder(ma2[lbars], ma1[lbars]) and strategy.position_size > 0 and lbars != 0
        strategy.close_all()
    if crossover(source, ma1) and strategy.position_size < 0
        strategy.close_all()
    if crossover(ma2[lbars], ma1[lbars]) and strategy.position_size < 0 and lbars != 0
        strategy.close_all()

With the declared defaults `ma2 = sma(close, 1) = close`, so `source` is the
close itself and the two close conditions are "price crosses the slow MA".
`lbars = 0` makes both lagged close blocks inert (`lbars != 0` is false) and, for
the same `lbars`, `ma2[lbars]` would be `ma2` anyway; the lagged crossovers are
computed and carried so that raising `lbars` behaves as written.

There is no `? -1 : 0` shape anywhere in this source, so PINE_SEMANTICS.md
1.17's minus-truthiness trap does not arise and nothing was rewritten into
`== 1` / `> 0`.

FIDELITY:

* The `strategy(...)` declaration is COMMENTED OUT in the source
  (`// strategy("Moving Average Strategy of BiznesFilosof", ..., initial_capital
  =10000, default_qty_type=strategy.percent_of_equity, default_qty_value=20,
  commission_type=strategy.commission.percent, commission_value=0.15,
  pyramiding=0)`), so it declares nothing and Pine's documented defaults apply:
  `default_qty_type` fixed, 1 unit, 1000000 initial capital, 0% commission,
  pyramiding 0. The commented values are recorded in the notes rather than
  used; reading a comment as a declaration is the same error as restoring a
  commented-out `strategy.exit` (PINE_SEMANTICS.md 1.17).
* `window` is evaluated against the bar's own time. `timestamp(y, m, d, h, min)`
  in Pine uses the EXCHANGE's timezone; the corpus pairs are UTC-quoted
  (PINE_SEMANTICS.md 3.4), and the data frame's index is converted to UTC before
  the comparison. With the declared 2011-01-01 / 2050-12-31 bounds the window is
  true for every bar of any modern backtest, but it is reproduced rather than
  dropped (PINE_SEMANTICS.md section 2, item 8: `input.time` limits are not
  applied by the common layer).
* `strategy.position_size` is read at bar close, i.e. the position as it stands
  BEFORE this bar's own entry order fills -- Pine fills on the next bar's open.
  The port reads `broker.position_size` inside `pine_script`, which is the same
  value for the same bar.
* `comment="LONG"` / `comment="SHORT"` are labels; the engine's order ledger
  carries no comment field and none is invented.
* The md's argument table renders the integer defaults `1` and `0` as
  `true` / `false` (`v_input_2|true|Start Month`, `v_input_9|true|Length MA2`,
  `v_input_11|false|Length bars close`). The source's own defaults are 1 / 1 / 0;
  the rendering is an artifact of the md exporter, not a difference.
* `/*backtest` declares `period: 1d` on Futures_Binance BTC_USDT, so timeframe
  is "1d"; `basePeriod: 1h` is the FMZ backtester's fill granularity.
* Leverage, margin, liquidation, funding and the venue's contract-step rounding
  are not modelled.
"""
import pandas as pd

from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


def _window_mask(index, start, finish) -> pd.Series:
    """`time >= timestart and time <= timefinish` for the bars in `index`.

    Pine's `timestamp()` resolves in the exchange's timezone; the corpus data is
    UTC (PINE_SEMANTICS.md 3.4), so a tz-aware index is converted to UTC and
    compared tz-naive, and a naive index is taken as UTC already.
    """
    stamps = pd.DatetimeIndex(index)
    if stamps.tz is not None:
        stamps = stamps.tz_convert("UTC").tz_localize(None)
    return pd.Series(
        (stamps >= start) & (stamps <= finish), index=index, dtype=bool
    )


class SMDualMovingAverageCrossover_cd224f(PinePortBase, IStrategy):
    source_id = "SM_cd224f81d15b913b"
    source_file = "Dual-Moving-Average-Crossover-Tracking-Strategy.md"
    timeframe = "1d"
    can_short = True
    # Pine evaluates the script from the first bar of the window.
    startup_candle_count = 0
    source_defaults: dict = {
        # Period window: timestamp(startY, startM, startD, 00, 00) .. timestamp(finishY, finishM, finishD, 23, 59)
        "startY": 2011,
        "startM": 1,
        "startD": 1,
        "finishY": 2050,
        "finishM": 12,
        "finishD": 31,
        # Length MA1 / exponential / Length MA2 / exponential / Length bars close
        "lma1": 21,
        "exponential1": False,
        "lma2": 1,
        "exponential2": False,
        "lbars": 0,
    }
    # The only strategy() line in the file is commented out, so it declares
    # nothing and Pine's documented defaults apply.
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    # No stop / limit / trailing exit exists: every close is `strategy.close_all()`,
    # a market close that the engine's signal projection can express.
    source_reproduce_stops = False
    source_mintick = 0.1
    source_fidelity_notes = [
        "The `strategy(...)` declaration is commented out in the source "
        "(`// strategy(\"Moving Average Strategy of BiznesFilosof\", ... "
        "initial_capital=10000, default_qty_type=strategy.percent_of_equity, "
        "default_qty_value=20, commission_type=strategy.commission.percent, "
        "commission_value=0.15, pyramiding=0)`), so it declares nothing and "
        "Pine's documented defaults are used: fixed sizing, qty 1, initial "
        "capital 1000000, commission 0%, pyramiding 0. The commented numbers "
        "are recorded here, not applied -- and note that restoring "
        "percent_of_equity / commission would change the wallet basis, so this "
        "choice is visible rather than silent.",
        "`strategy.entry(...) when = crossover(ma2, ma1) and window` is a "
        "conditional entry call, not an `if` wrapper; the port passes the same "
        "combined condition to broker.entry.",
        "`source = ma2`, so the two 'price vs slow MA' close conditions reduce "
        "to crossunder/crossover of ma2 and ma1; with the declared `lma2 = 1` "
        "and `exponential2 = false`, ma2 = sma(close, 1) = close.",
        "`ma2[lbars]` / `ma1[lbars]` with the declared `lbars = 0` make the two "
        "lagged close blocks inert (`and lbars != 0` is false) and equal to the "
        "unlagged crossovers anyway; both are computed and carried so a raised "
        "`lbars` behaves as written.",
        "`window` is reproduced from the timestamp() inputs rather than "
        "dropped: the corpus data is UTC-quoted and Pine's timestamp() uses the "
        "exchange's timezone (PINE_SEMANTICS.md 3.4), so the portable choice is "
        "a UTC-to-UTC comparison. The declared 2011..2050 bounds make it true "
        "for every bar of any modern backtest.",
        "`strategy.position_size` is read at bar close (before this bar's own "
        "entry order fills on the next open); `broker.position_size` is that "
        "same value.",
        "SAME-BAR ENTRY + CLOSE (PINE_SEMANTICS.md 1.13): on a cross-up bar the "
        "long entry is placed and then closed by `strategy.close_all()` (the "
        "close condition is the same crossover), and the engine fills the two "
        "on the SAME next open, in source order -- a zero-length round trip. "
        "The framework only ever learns `enter_long` on that bar (the `close` "
        "names no entry and the `close_all` sees the still-short position), so "
        "it holds a long the engine has already flattened; the reverse entry "
        "that comes later is what eventually closes it. Which model the original "
        "platform uses here is exactly the undecided choice 1.13 records -- the "
        "port neither picks a side nor patches the projection.",
        "The md's argument table renders the integer defaults 1 and 0 as "
        "`true` / `false` (Start Month, Length MA2, Length bars close). The "
        "source's defaults are 1 / 1 / 0 -- an md rendering artifact, not a "
        "difference.",
        "`comment=\"LONG\"` / `comment=\"SHORT\"` are order labels and do not "
        "reach the engine's ledger; none is invented.",
        "No `? -1 : 0` shape exists in this source, so PINE_SEMANTICS.md 1.17's "
        "minus-truthiness trap does not arise and nothing was normalised into "
        "`== 1` / `> 0`.",
        "Venue contract-step rounding, leverage, margin, liquidation and "
        "funding are not modelled.",
    ]

    def pine_indicators(self, dataframe: pd.DataFrame, params: dict) -> pd.DataFrame:
        close = dataframe["close"]
        lma1 = int(params["lma1"])
        lma2 = int(params["lma2"])
        lbars = int(params["lbars"])

        # ma1 = exponential1 ? ema(close, lma1) : sma(close, lma1)
        if bool(params["exponential1"]):
            ma1 = ta.pine_ema(close, lma1)
        else:
            ma1 = ta.pine_sma(close, lma1)
        # ma2 = exponential2 ? ema(close, lma2) : sma(close, lma2)
        if bool(params["exponential2"]):
            ma2 = ta.pine_ema(close, lma2)
        else:
            ma2 = ta.pine_sma(close, lma2)

        # window = time >= timestart and time <= timefinish
        timestart = pd.Timestamp(
            int(params["startY"]), int(params["startM"]), int(params["startD"])
        )
        timefinish = pd.Timestamp(
            int(params["finishY"]), int(params["finishM"]), int(params["finishD"])
        ) + pd.Timedelta(hours=23, minutes=59)
        window = _window_mask(dataframe.index, timestart, timefinish).to_numpy()

        # strategy.entry("LongEntryID",  ..., when = crossover(ma2, ma1)  and window)
        # strategy.entry("ShortEntryID", ..., when = crossunder(ma2, ma1) and window)
        enter_long = ta.pine_crossover(ma2, ma1) & window
        enter_short = ta.pine_crossunder(ma2, ma1) & window

        # source = ma2
        source = ma2
        # ... crossunder(source, ma1) / crossover(source, ma1)
        close_after_under = ta.pine_crossunder(source, ma1)
        close_after_over = ta.pine_crossover(source, ma1)
        # ... crossunder(ma2[lbars], ma1[lbars]) / crossover(ma2[lbars], ma1[lbars])
        lagged_under = ta.pine_crossunder(ma2.shift(lbars), ma1.shift(lbars))
        lagged_over = ta.pine_crossover(ma2.shift(lbars), ma1.shift(lbars))

        dataframe["pine_ma1"] = ma1
        dataframe["pine_ma2"] = ma2
        dataframe["pine_window"] = window
        dataframe["pine_mac_tracking_long"] = enter_long
        dataframe["pine_mac_tracking_short"] = enter_short
        dataframe["pine_close_under"] = close_after_under
        dataframe["pine_close_over"] = close_after_over
        dataframe["pine_close_under_lagged"] = lagged_under
        dataframe["pine_close_over_lagged"] = lagged_over
        return dataframe

    def pine_context(self, dataframe: pd.DataFrame, params: dict) -> dict:
        return {
            "enter_long": dataframe["pine_mac_tracking_long"].to_numpy(),
            "enter_short": dataframe["pine_mac_tracking_short"].to_numpy(),
            "close_under": dataframe["pine_close_under"].to_numpy(),
            "close_over": dataframe["pine_close_over"].to_numpy(),
            "close_under_lagged": dataframe["pine_close_under_lagged"].to_numpy(),
            "close_over_lagged": dataframe["pine_close_over_lagged"].to_numpy(),
            "lbars": int(params["lbars"]),
        }

    def pine_script(self, broker, i: int, ctx: dict) -> None:
        lbars = ctx["lbars"]

        # strategy.entry("LongEntryID", strategy.long, comment="LONG", when = crossover(ma2, ma1) and window)
        if ctx["enter_long"][i]:
            broker.entry("LongEntryID", "long")
        # strategy.entry("ShortEntryID", strategy.short, comment="SHORT", when = crossunder(ma2, ma1) and window)
        if ctx["enter_short"][i]:
            broker.entry("ShortEntryID", "short")

        position = broker.position_size
        # if crossunder(source, ma1) and strategy.position_size > 0
        #     strategy.close_all()
        if ctx["close_under"][i] and position > 0:
            broker.close_all()
        # if crossunder(ma2[lbars], ma1[lbars]) and strategy.position_size > 0 and lbars != 0
        #     strategy.close_all()
        if ctx["close_under_lagged"][i] and position > 0 and lbars != 0:
            broker.close_all()
        # if crossover(source, ma1) and strategy.position_size < 0
        #     strategy.close_all()
        if ctx["close_over"][i] and position < 0:
            broker.close_all()
        # if crossover(ma2[lbars], ma1[lbars]) and strategy.position_size < 0 and lbars != 0
        #     strategy.close_all()
        if ctx["close_over_lagged"][i] and position < 0 and lbars != 0:
            broker.close_all()
