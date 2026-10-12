"""Port of sources/SM_e5c69cc4775dab16.pine
(batch_001/EMAC指数移动平均线交叉优化策略EMAC-Exponential-Moving-Average-Cross-Optimized-Strategy.md).

Pine v4. A weekly trend filter, a five-MA stack, an R-based position size, and
an early exit on a close back through MA1:

    currentClose = security(syminfo.tickerid, "W", close)
    pastClose    = security(syminfo.tickerid, "W", close[26])
    upTrend / downTrend / sidewaysUpTrend / sidewaysDownTrend  (from pastClose)
    goTrend      = per `trendRequired` (default "Red" = the union of all four)

    ma1..ma5     = per `maNType` (default EMA/EMA/EMA/SMA/SMA at 10/20/34/100/200)
    entrySignal  = strategy.position_size <= 0
                   and close[1] < ma1[1] and close > ma1 and close > ma2
                   and close > ma3 and shortMACross and ma1 > ma3
                   and longMACross and goTrend

    atrValue   = atr(14)
    atrStop    = entrySignal and ((high - atrMult * atrValue) < low)
                 ? (high - atrMult * atrValue) : low
    initialStop = entrySignal and enableAtrStop == "Yes" ? atrStop
                  : entrySignal ? low : na
    stoploss    = valuewhen(entrySignal, initialStop, 0)
    rSize       = "Static" -> rSizeStatic
                  "Percent" -> rSizePercent * .01 * strategy.equity
    positionSize = (rSize / (close - initialStop)) > 1 ? (rSize / (close - initialStop)) : 1
    target3     = entrySignal ? (close + ((close - initialStop) * target3Mult)) : na
    t3          = valuewhen(entrySignal, target3, 0)
    ma1CrossExit = strategy.position_size > 0 and close < ma1

    strategy.order("Entry", long=true, qty=positionSize,
                   when=(strategy.position_size <= 0 and entrySignal and timeFilter))
    strategy.close_all(when = ma1CrossExit and timeFilter and earlyExit, comment="MA1 Cross Exit")
    strategy.order("Stop Loss", false, qty=strategy.position_size, stop=stoploss,
                   oca_name="Exit", when=timeFilter and yesStops, comment="Stop Loss")
    strategy.cancel("Stop Loss", when=ma1CrossExit and timeFilter and earlyExit)
    strategy.order("Target", false, qty=strategy.position_size, limit=t3,
                   oca_name="Exit", when=timeFilter and yesTargets, comment="Target")
    strategy.cancel("Target", when=ma1CrossExit and timeFilter and earlyExit)

`strategy()` declares `default_qty_value = 100`, `initial_capital = 100000`,
`default_qty_type = strategy.fixed`, `pyramiding = 0`,
`process_orders_on_close = true` and `calc_on_every_tick = false`. The
`/*backtest` header declares `period: 1d` on Futures_Binance BTC_USDT, so
`timeframe` is "1d".

WHAT THE DECLARED DEFAULTS ACTUALLY RUN (the source is read literally, so the
branches that are switched off stay switched off):

* `enableStops = "No"` -> `yesStops = 0` -> the "Stop Loss" order is never
  created, and `strategy.cancel("Stop Loss", ...)` cancels nothing.
* `enableTargets = "No"` -> `yesTargets = 0` -> the "Target" order is never
  created, and `strategy.cancel("Target", ...)` cancels nothing.
* `enableEarlyExit = "Yes"` -> `earlyExit = 1` -> the `close_all` arm is live.
* `rStaticOrPercent = "Percent"`, `rSizePercent = 3` -> R is 3% of
  `strategy.equity` AT THE BAR THE ORDER IS PLACED, which is why the size is
  computed inside `pine_script` from the broker's own equity rather than
  pre-computed as a column.
* `timeFilter = true` is a LITERAL in the source, not a comparison against
  `startYear`; `startYear` is assigned and never read. The port keeps the
  literal and declares the dead input.
* `secondSignal` (position_size > 0 variant of the entry condition) is only
  fed to `plotshape` and places no order; it is not reproduced.

FIDELITY:

* PINE_SEMANTICS 2.1: `request.security(syminfo.tickerid, "W", ...)` is not
  modelled by the engine. This port supplies the aligned series itself, using
  the documented historical-bar behaviour of `barmerge.lookahead_off` -- the
  value of the last COMPLETED weekly bar, held across the week that is still
  forming. `currentClose` is therefore the previous week's close and
  `pastClose` the close of the week `trend = 26` bars before that, both keyed
  Monday..Sunday in UTC (3.4). The alternative reading (the forming week's
  running close) is not chosen; see the notes.
* The weekly series is rebuilt from whatever frame the caller hands over, so a
  backtest window shorter than the lookback leaves the trend filter na for its
  first `trend + 1` weeks and suppresses entries there. That is a property of
  the data window, not of the source.
* PINE_SEMANTICS 1.13 is load-bearing here: the source's `Entry` and `close_all`
  are two separate calls in a fixed order, and the engine fills same-bar pending
  orders in creation order.
* `strategy.order(id, long, qty, ...)` is modelled by `PineBroker.order`, which
  the shared layer aliases to `PineBroker.entry`. For the `Entry` call that is
  exactly right (it is an opening order issued only while
  `strategy.position_size <= 0`). For the two disabled exits it would not be:
  `qty = strategy.position_size` with `long = false` is Pine's "sell exactly the
  position" order, while the entry alias computes a TARGET position and would
  reverse instead of flatten. Both exits are unreachable under the declared
  defaults (`yesStops = yesTargets = 0`), so nothing in this run depends on it;
  it is recorded because overriding those inputs would silently change shape.
* `process_orders_on_close = true` is NOT modelled by the shared engine: it
  always fills a market order at the NEXT bar's open. The framework side of the
  chain verification reads the same engine, so the two agree with each other,
  but both are one bar later than the source declares. This is a shared-layer
  gap, reported and not worked around (rule 9).
* `strategy.close_all` closes every open entry at the next open; it is projected
  as a market exit (PINE_SEMANTICS 1.12 gates the projection on the position
  actually being held).
* `stoploss` / `t3` are `valuewhen(entrySignal, ..., 0)` -- running state, so
  they are carried across bars inside `pine_script` and reset at bar 0, exactly
  as the Pine series is.
* PINE_SEMANTICS 3.1 (modelled choice): `ema()` is seeded with the first non-na
  observation and an na observation does not advance the recursion.
  TradingView's seeding rule is unpublished, so the early part of every MA here
  is an unresolved parity risk -- and this strategy's conditions are derived
  entirely from MAs, which 3.1 records as the case where the difference is
  load-bearing for the early trades. 3.2: `sma` returns na until its window is
  full and na inside the window propagates (all three of `close[1] < ma1[1]`,
  `close > ma2`, `close > ma3` go false until MA3 exists).
* PINE_SEMANTICS 2.3: `strategy.risk.*` is not used by the source.
* `calc_on_every_tick = false` matches Pine's default and the engine's
  once-per-bar evaluation.
* The `plot` / `plotshape` calls, `overlay = true`, `shorttitle` and the
  commented-out target1/target2 lines are display-only or dead.
* PINE_SEMANTICS 1.6 / 5.1: the venue's contract-step rounding and non-zero
  taker fees are not modelled; the source declares 0% commission, which is the
  cost basis the port carries.
* Leverage, margin, liquidation and funding are not modelled.
"""
from freqtrade.strategy import IStrategy

import numpy as np
import pandas as pd

import pine_ta as ta
from pine_port_base import PinePortBase


def _utc_weeks(index: pd.DatetimeIndex) -> pd.PeriodIndex:
    """Calendar weeks (Monday..Sunday) of `index`, in UTC."""
    if index.tz is None:
        index = index.tz_localize("UTC")
    else:
        index = index.tz_convert("UTC")
    return index.tz_localize(None).to_period("W-SUN")


def _ma(source: pd.Series, length: int, kind: str) -> pd.Series:
    """The source's `maNType == "EMA" ? ema(...) : ... == "SMA" ? sma(...) : wma(...)`."""
    if kind == "EMA":
        return ta.pine_ema(source, length)
    if kind == "SMA":
        return ta.pine_sma(source, length)
    if kind == "WMA":
        return ta.pine_wma(source, length)
    raise ValueError(f"unrecognised MA type {kind!r}")


class SMEmacExponentialMovingAverageCross_e5c69c(PinePortBase, IStrategy):
    source_id = "SM_e5c69cc4775dab16"
    source_file = (
        "EMAC指数移动平均线交叉优化策略EMAC-Exponential-Moving-Average-Cross-"
        "Optimized-Strategy.md"
    )
    timeframe = "1d"
    # No short entry anywhere: `Entry` is long=true, and "Stop Loss" / "Target"
    # are `false` (closing orders) that the defaults never create.
    can_short = False
    source_defaults: dict = {
        "startYear": 2015,
        "rStaticOrPercent": "Percent",
        "rSizeStatic": 2000,
        "rSizePercent": 3,
        "res": "W",
        "trend": 26,
        "trendMult": 15,
        "trendRequired": "Red",
        "ma1Length": 10,
        "ma1Type": "EMA",
        "ma2Length": 20,
        "ma2Type": "EMA",
        "ma3Length": 34,
        "ma3Type": "EMA",
        "ma4Length": 100,
        "ma4Type": "SMA",
        "ma5Length": 200,
        "ma5Type": "SMA",
        "enableShortMAs": "No",
        "enableLongMAs": "No",
        "atrMult": 2.5,
        "target3Mult": 3.0,
        "enableAtrStop": "No",
        "enableStops": "No",
        "enableTargets": "No",
        "enableEarlyExit": "Yes",
    }
    # strategy(title=..., shorttitle=..., overlay=true, calc_on_every_tick=false,
    #          default_qty_value=100, initial_capital=100000,
    #          default_qty_type=strategy.fixed, pyramiding=0,
    #          process_orders_on_close=true)
    source_qty_type = "fixed"
    source_qty_value = 100.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 100_000.0
    # The only stop leg is `strategy.order("Stop Loss", ..., stop=stoploss)` and
    # its `when` is `timeFilter and yesStops`, i.e. 0 under the declared
    # `Enable Stops = "No"`: no stop order is ever created. The shared layer also
    # only publishes `pine_stop_level` for kind="exit" orders, so a
    # `strategy.order(stop=)` leg could not reach `custom_stoploss` even if the
    # input were overridden.
    source_reproduce_stops = False
    source_fidelity_notes = [
        "PARTIAL PORT -- multi-timeframe. request.security(syminfo.tickerid, "
        "\"W\", ...) is not modelled by the engine (PINE_SEMANTICS 2.1), so this "
        "port supplies the aligned series itself: the last COMPLETED calendar "
        "week's close, forward-filled across the week that is still forming, "
        "which is the documented historical-bar behaviour of "
        "barmerge.lookahead_off. currentClose is therefore the previous week's "
        "close and pastClose the close trend=26 weekly bars before that.",
        "The alternative reading of lookahead_off (the forming week's running "
        "close) would make the trend filter react to the current week instead of "
        "the completed one. The source passes no `lookahead` argument, so the "
        "platform default applies; that default is documented TradingView "
        "behaviour and no evidence about what FMZ's runtime does. This is the "
        "single largest fidelity risk in the port.",
        "Weeks are keyed Monday..Sunday in UTC, because the source's exchange is "
        "Futures_Binance BTC_USDT and the local candles are UTC "
        "(PINE_SEMANTICS 3.4: Pine calendar functions use the exchange's "
        "timezone, modelled here as UTC).",
        "The weekly series is rebuilt from the frame the caller supplies, so "
        "inside a backtest window shorter than trend+1 weeks the trend filter is "
        "na and suppresses every entry until it fills in. That is a property of "
        "the data window, not of the source.",
        "process_orders_on_close = true is declared by the source and is NOT "
        "modelled by the shared engine, which always fills a market order at the "
        "next bar's open. Both sides of the chain verification read that same "
        "engine, so they agree with each other while both sit one bar later than "
        "the source declares. Shared-layer gap: reported, not worked around.",
        "Under the declared defaults the strategy is exactly two calls: "
        "`Entry` (a long market order, only while strategy.position_size <= 0 "
        "and the entry condition holds) and `close_all` (while position_size > 0 "
        "and close < ma1). `enableStops = \"No\"` and `enableTargets = \"No\"` "
        "make yesStops and yesTargets 0, so neither the \"Stop Loss\" nor the "
        "\"Target\" order is ever created and both strategy.cancel calls cancel "
        "nothing. They are still issued here in source order.",
        "The two disabled exit orders are strategy.order(id, long=false, "
        "qty=strategy.position_size, ...), i.e. Pine's \"sell exactly the "
        "position\" order. PineBroker.order is the shared layer's alias of "
        "PineBroker.entry, which computes a TARGET position instead (and would "
        "reverse rather than flatten). Unreachable under the declared defaults; "
        "recorded because overriding Enable Stops / Enable Targets would change "
        "shape silently.",
        "strategy.order(\"Stop Loss\", ...) is a stop ENTRY order, not a "
        "strategy.exit, so even if enabled its level would not be published as "
        "pine_stop_level (used_exit_levels records kind=\"exit\" orders only). "
        "source_reproduce_stops is False and there is no stop series.",
        "timeFilter = true is a literal in the source; `startYear = "
        "input(2015, ...)` is assigned and never read by any expression. The "
        "port keeps the literal `true` and declares the dead input.",
        "secondSignal -- the same condition with strategy.position_size > 0 -- "
        "is only plotted and places no order, so it is not reproduced.",
        "MD/SOURCE DIFFERENCE: the md prose says the signal comes from the "
        "10/20/50 EMAs crossing a 50-period SMA, and the source's own comment "
        "says \"Default is 10 EMA, 20 EMA, 50 EMA, 100 SMA and 200 SMA\". The "
        "source CODE declares ma3Length = 34 and ma4Length = 100, and it "
        "compares close against all of ma1..ma3 rather than calling any of them a "
        "single trigger. The code is authoritative (rule 2); the prose and the "
        "comment are recorded as stale.",
        "MD/SOURCE DIFFERENCE: the md's Strategy Arguments table renders every "
        "options input as an index (v_input_2 default 0 for "
        "\"Percent|Static\", v_input_8 default 0 for \"Red\", v_input_19/20/23/"
        "24/25 default 0, v_input_26 default 0 for \"Yes|No\"). Those are the "
        "same defaults the source declares as strings; the table is a rendering "
        "artefact of the md exporter, not a second set of values.",
        "stoploss and t3 are valuewhen(entrySignal, ..., 0) -- running state "
        "carried across bars and reset at bar 0, as the Pine series is.",
        "rSize = rSizePercent * .01 * strategy.equity is evaluated at the bar "
        "the order is placed, so the R-based quantity is computed inside "
        "pine_script from the broker's own equity rather than pre-computed.",
        "PINE_SEMANTICS 3.1 (modelled choice): pine_ema seeds with the first "
        "non-na observation and an na observation does not advance the "
        "recursion; TradingView's seeding rule is unpublished. Every condition "
        "in this source is derived from the five MAs, which 3.1 records as the "
        "case where the seed difference is load-bearing for the earliest trades "
        "(the port can evaluate from bar ~2, an SMA-seeded platform only after "
        "~200 bars). 3.2: pine_sma returns na until its window is full and na "
        "inside the window propagates, so close > ma3 and close > ma4 both stay "
        "false until their windows exist.",
        "calc_on_every_tick = false matches Pine's default and the engine's "
        "once-per-bar evaluation. The plot / plotshape calls, overlay, "
        "shorttitle and the commented-out target1/target2 lines are display-only "
        "or dead.",
        "PINE_SEMANTICS 1.6 / 5.1: the venue's contract-step rounding and "
        "non-zero taker fees are not modelled; the source declares 0% "
        "commission, which is the cost basis the port carries.",
        "Leverage, margin, liquidation and funding are not modelled.",
    ]

    def pine_indicators(self, dataframe, params):
        index = dataframe.index
        if not isinstance(index, pd.DatetimeIndex):
            raise ValueError(
                f"{type(self).__name__} needs a DatetimeIndex to align the "
                "weekly request.security series"
            )

        close = dataframe["close"]
        high = dataframe["high"]
        low = dataframe["low"]

        trend_mult = float(params["trendMult"]) / 100.0
        trend_bars = int(params["trend"])

        # currentClose = security(syminfo.tickerid, res, close)
        # pastClose    = security(syminfo.tickerid, res, close[trend])
        weeks = _utc_weeks(index)
        weekly_close = close.groupby(weeks).last()
        # lookahead_off: the last COMPLETED weekly bar's value, held across the
        # week that is still forming. `close[trend]` is taken on the same weekly
        # series, so it sits `trend` weekly bars before it.
        current_lookup = weekly_close.shift(1).to_dict()
        past_lookup = weekly_close.shift(1 + trend_bars).to_dict()
        current_close = pd.Series(
            [current_lookup.get(week, np.nan) for week in weeks],
            index=index, dtype=float,
        )
        past_close = pd.Series(
            [past_lookup.get(week, np.nan) for week in weeks],
            index=index, dtype=float,
        )

        up_trend = current_close >= past_close * (1 + trend_mult)
        down_trend = current_close <= past_close * (1 - trend_mult)
        sideways_up = (current_close < past_close * (1 + trend_mult)) & (
            current_close > past_close
        )
        sideways_down = (current_close > past_close * (1 - trend_mult)) & (
            current_close < past_close
        )

        trend_required = str(params["trendRequired"])
        if trend_required == "Orange":
            go_trend = up_trend | sideways_up | sideways_down
        elif trend_required == "Yellow":
            go_trend = up_trend | sideways_up
        elif trend_required == "Green":
            go_trend = up_trend
        elif trend_required == "Red":
            go_trend = up_trend | sideways_up | sideways_down | down_trend
        else:
            go_trend = pd.Series(np.nan, index=index, dtype=float)
        go_trend = go_trend.fillna(False)

        # ma1 = ma1Type == "EMA" ? ema(close, ma1Length) : ma1Type == "SMA" ?
        #       sma(close, ma1Length) : wma(close, ma1Length)   (and ma2..ma5)
        ma1 = _ma(close, int(params["ma1Length"]), str(params["ma1Type"]))
        ma2 = _ma(close, int(params["ma2Length"]), str(params["ma2Type"]))
        ma3 = _ma(close, int(params["ma3Length"]), str(params["ma3Type"]))
        ma4 = _ma(close, int(params["ma4Length"]), str(params["ma4Type"]))
        ma5 = _ma(close, int(params["ma5Length"]), str(params["ma5Type"]))

        # shortMACross = enableShortMAs == "Yes" and ma1 > ma2 or enableShortMAs == "No"
        # longMACross  = enableLongMAs == "Yes" and ma4 >= ma5 or enableLongMAs == "No"
        short_ma_cross = (
            (str(params["enableShortMAs"]) == "Yes") & (ma1 > ma2)
        ) | (str(params["enableShortMAs"]) == "No")
        long_ma_cross = (
            (str(params["enableLongMAs"]) == "Yes") & (ma4 >= ma5)
        ) | (str(params["enableLongMAs"]) == "No")

        # Everything in entrySignal except `strategy.position_size <= 0`, which
        # is running state and is applied in pine_script.
        signal_core = (
            (close.shift(1) < ma1.shift(1))
            & (close > ma1)
            & (close > ma2)
            & (close > ma3)
            & short_ma_cross.fillna(False)
            & (ma1 > ma3)
            & long_ma_cross.fillna(False)
            & go_trend
        ).fillna(False)

        # atrValue = atr(14); atrMult = 2.5
        atr_value = ta.pine_atr(dataframe, 14)
        atr_mult = float(params["atrMult"])
        atr_stop_value = high - (atr_mult * atr_value)
        # atrStop = entrySignal and ((high - atrMult * atrValue) < low)
        #           ? (high - atrMult * atrValue) : low
        atr_stop = pd.Series(
            np.where(signal_core & (atr_stop_value < low) & atr_stop_value.notna(),
                     atr_stop_value, low),
            index=index, dtype=float,
        )
        # initialStop = entrySignal and enableAtrStop == "Yes" ? atrStop
        #               : entrySignal ? low : na
        initial_stop = pd.Series(
            np.where(signal_core, atr_stop if str(params["enableAtrStop"]) == "Yes" else low,
                     np.nan),
            index=index, dtype=float,
        )

        dataframe["pine_current_close"] = current_close
        dataframe["pine_past_close"] = past_close
        dataframe["pine_go_trend"] = go_trend
        dataframe["pine_ma1"] = ma1
        dataframe["pine_ma2"] = ma2
        dataframe["pine_ma3"] = ma3
        dataframe["pine_ma4"] = ma4
        dataframe["pine_ma5"] = ma5
        dataframe["pine_signal_core"] = signal_core
        dataframe["pine_atr_value"] = atr_value
        dataframe["pine_initial_stop"] = initial_stop
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "signal_core": dataframe["pine_signal_core"].to_numpy(),
            "close": dataframe["close"].to_numpy(),
            "low": dataframe["low"].to_numpy(),
            "ma1": dataframe["pine_ma1"].to_numpy(),
            "initial_stop": dataframe["pine_initial_stop"].to_numpy(),
            "r_static_or_percent": str(params["rStaticOrPercent"]),
            "r_size_static": float(params["rSizeStatic"]),
            "r_size_percent": float(params["rSizePercent"]),
            "target3_mult": float(params["target3Mult"]),
            "yes_stops": 1 if str(params["enableStops"]) == "Yes" else 0,
            "yes_targets": 1 if str(params["enableTargets"]) == "Yes" else 0,
            "early_exit": 1 if str(params["enableEarlyExit"]) == "Yes" else 0,
            "time_filter": True,
        }

    def pine_script(self, broker, i, ctx):
        if i == 0:
            # valuewhen state, carried across bars exactly as Pine carries it.
            self._emac_stoploss = np.nan
            self._emac_t3 = np.nan

        time_filter = ctx["time_filter"]

        # entrySignal = (strategy.position_size <= 0 and ...signal_core...)
        entry_signal = broker.position_size <= 0 and bool(ctx["signal_core"][i])

        # initialStop = entrySignal ? <atrStop or low> : na
        initial_stop = ctx["initial_stop"][i] if entry_signal else np.nan
        # stoploss = valuewhen(entrySignal, initialStop, 0)
        if entry_signal:
            self._emac_stoploss = initial_stop
        # target3 = entrySignal ? (close + ((close - initialStop) * target3Mult)) : na
        # t3      = valuewhen(entrySignal, target3, 0)
        if entry_signal:
            self._emac_t3 = ctx["close"][i] + (
                (ctx["close"][i] - initial_stop) * ctx["target3_mult"]
            )

        # rSize = rStaticOrPercent == "Static" ? rSizeStatic
        #       : rStaticOrPercent == "Percent" ? (rSizePercent * .01 * strategy.equity) : 1
        if ctx["r_static_or_percent"] == "Static":
            r_size = ctx["r_size_static"]
        elif ctx["r_static_or_percent"] == "Percent":
            r_size = ctx["r_size_percent"] * 0.01 * broker.equity
        else:
            r_size = 1.0
        # positionSize = (rSize/(close - initialStop)) > 1 ? (rSize/(close - initialStop)) : 1
        with np.errstate(divide="ignore", invalid="ignore"):
            raw_size = np.float64(r_size) / np.float64(
                ctx["close"][i] - initial_stop
            )
        position_size = float(raw_size) if raw_size > 1 else 1.0

        # strategy.order("Entry", long = true, qty = positionSize,
        #                when = (strategy.position_size <= 0 and entrySignal and timeFilter))
        broker.order("Entry", "long", qty=position_size,
                     when=bool(entry_signal and time_filter))

        # ma1CrossExit = strategy.position_size > 0 and close < ma1
        ma1_cross_exit = broker.position_size > 0 and ctx["close"][i] < ctx["ma1"][i]
        # strategy.close_all(when = ma1CrossExit and timeFilter and earlyExit, ...)
        broker.close_all(
            when=bool(ma1_cross_exit and time_filter and ctx["early_exit"])
        )
        # strategy.order("Stop Loss", false, qty = strategy.position_size,
        #                stop=stoploss, oca_name="Exit", when = timeFilter and yesStops)
        broker.order("Stop Loss", "short", qty=broker.position_size,
                     stop=self._emac_stoploss,
                     when=bool(time_filter and ctx["yes_stops"]))
        # strategy.cancel("Stop Loss", when = ma1CrossExit and timeFilter and earlyExit)
        broker.cancel(
            "Stop Loss",
            when=bool(ma1_cross_exit and time_filter and ctx["early_exit"]),
        )
        # strategy.order("Target", false, qty = strategy.position_size,
        #                limit=t3, oca_name="Exit", when = timeFilter and yesTargets)
        broker.order("Target", "short", qty=broker.position_size,
                     limit=self._emac_t3,
                     when=bool(time_filter and ctx["yes_targets"]))
        # strategy.cancel("Target", when = ma1CrossExit and timeFilter and earlyExit)
        broker.cancel(
            "Target",
            when=bool(ma1_cross_exit and time_filter and ctx["early_exit"]),
        )
