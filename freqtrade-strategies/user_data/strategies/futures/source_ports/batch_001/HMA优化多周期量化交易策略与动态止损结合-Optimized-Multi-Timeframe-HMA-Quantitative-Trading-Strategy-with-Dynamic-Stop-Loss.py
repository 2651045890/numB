"""Port of sources/SM_64f8cf6afcafc509.pine
(batch_001/HMA优化多周期量化交易策略与动态止损结合-Optimized-Multi-Timeframe-HMA-Quantitative-Trading-Strategy-with-Dynamic-Stop-Loss.md).

Pine v5 ("DAP Hull Sweet Scalp v1 Strategy", after InSilico's Hull Suite). A
Hull moving average is crossed against a copy of itself two bars back, entries
are allowed only inside a session, and each entry arms a trailing scalp exit:

    HMA(_src, _length)  = ta.wma(2*ta.wma(_src, _length/2) - ta.wma(_src, _length),
                                 math.round(math.sqrt(_length)))
    EHMA(_src, _length) = ta.ema(2*ta.ema(_src, _length/2) - ta.ema(_src, _length),
                                 math.round(math.sqrt(_length)))
    THMA(_src, _length) = ta.wma(ta.wma(_src, _length/3)*3 - ta.wma(_src, _length/2)
                                 - ta.wma(_src, _length), _length)
    Mode(modeSwitch, src, len) = modeSwitch=='Hma'  ? HMA(src, len)
                               : modeSwitch=='Ehma' ? EHMA(src, len)
                               : modeSwitch=='Thma' ? THMA(src, len/2) : na

    HULL  = Mode(modeSwitch, close, length)
    MHULL = HULL[0];  SHULL = HULL[2]

    Session = not na(time(timeframe.period, session))       # session='1800-1700'
    start   = Session and not Session[1]
    end     = not Session and Session[1]

    strategy.risk.allow_entry_in(strat_dir_value)           # default 'long'

    if Session and ta.crossover(HULL[0], HULL[2])
        strategy.entry('long',  strategy.long)
        strategy.exit('trailing stop', from_entry='long',  trail_points=slPoints, trail_offset=slOffset)
    if Session and ta.crossunder(HULL[0], HULL[2])
        strategy.entry('short', strategy.short)
        strategy.exit('trailing stop', from_entry='short', trail_points=slPoints, trail_offset=slOffset)
    if end
        strategy.close_all("End of Session - Go FLat")

`strategy()` declares only its title and `overlay`, so every property is Pine's
documented default: `strategy.fixed` / 1 contract, initial capital 1000000,
commission 0%, pyramiding 0, `process_orders_on_close=false`.

The `/*backtest` header declares `period: 1d` on Futures_Binance BTC_USDT, so
`timeframe` is "1d"; `basePeriod: 1h` is the FMZ backtester's fill granularity
for those daily bars.

FIDELITY (what is kept, what is a modelling choice, what cannot be done):

* `strategy.risk.allow_entry_in(...)` is NOT modelled by the shared engine
  (PINE_SEMANTICS.md 二.3). It DOES change the source's trading behaviour: with
  the declared default `Strategy Direction = 'long'` the short entry is
  suppressed. Rather than emit shorts the source would never take, the port
  reproduces this one risk rule exactly, from the same input, and notes it here
  as port-level logic standing in for an unmodelled shared-layer feature.
* The trailing exit is the unverified-trail class of PINE_SEMANTICS.md 3.6 /
  二.9(b): the source re-places `strategy.exit('trailing stop', ...)` on every
  signal bar with the SAME id, and the engine replaces a same-id exit with a
  fresh order (ratchet reset), so the trail can only arm and trigger inside one
  bar. Whether the original platform carries the ratchet across a same-id
  replacement is unverified, so this port cannot be called equivalent for the
  trailing behaviour.
* `trail_points` / `trail_offset` are in TICKS in Pine and the engine consumes
  them as PRICE distances, so the port multiplies both by mintick, the same
  conversion PINE_SEMANTICS.md 3.5 requires for `profit=` / `loss=`. With
  slPoints = slOffset = 1 on a 0.1-tick symbol the trail is 0.1 price units
  wide. No other port in this repository uses a trailing exit, so this
  conversion has no established precedent to follow.
* `_length / 2`, `_length / 3` and `len / 2` pass a FLOAT where Pine's `ta.wma`
  / `ta.ema` want an `int`. Pine casts implicitly by rounding to the nearest
  integer (`math.round` semantics, halfway away from zero), which is what
  `_pine_int` below does: 55/2 -> 28, 55/3 -> 18. This is a MODELLING CHOICE
  with real parity risk (truncation would give 27 and 18 instead) and needs
  original-platform comparison to settle; it is not something pine_ta decides.
* `math.round(math.sqrt(_length))` is explicit in the source and is reproduced
  as such: 55 -> 7.
* The session guard is evaluated against UTC bar open times (PINE_SEMANTICS.md
  3.4). `time(timeframe.period, '1800-1700')` asks whether the bar's time falls
  in a window that runs from 18:00 to 17:00 the next day, so on 1d bars --
  whose open is 00:00 -- every bar is inside it. `Session` is therefore true
  throughout, `start`/`end` are never true, and the closing
  `strategy.close_all()` never fires. This is derived, not hardcoded.
* `bgcolor` / `plot` / `fill` / `barcolor`, `hullColor`, `switchColor`,
  `candleCol`, `visualSwitch`, `thicknesSwitch`, `transpSwitch` and `MHULL`
  feed only the plot objects and are not reproduced.
* Leverage, margin, liquidation, funding and the venue's contract-step rounding
  are not modelled.
"""
import math

import numpy as np
import pandas as pd
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


def _pine_int(value: float) -> int:
    """Pine's implicit float -> int cast: round half away from zero."""
    return int(math.floor(abs(value) + 0.5)) * (1 if value >= 0 else -1)


def _in_session(times: pd.DatetimeIndex, session: str) -> np.ndarray:
    """`not na(time(timeframe.period, session))` for an 'HHMM-HHMM' window.

    A window whose end is not after its start wraps past midnight, so a bar is
    inside it when its time-of-day is at or after the start OR before the end.
    """
    start_text, end_text = session.split("-")
    start_minutes = int(start_text[:2]) * 60 + int(start_text[2:])
    end_minutes = int(end_text[:2]) * 60 + int(end_text[2:])
    minutes = times.hour * 60 + times.minute
    if start_minutes <= end_minutes:
        inside = (minutes >= start_minutes) & (minutes < end_minutes)
    else:
        inside = (minutes >= start_minutes) | (minutes < end_minutes)
    return np.asarray(inside, dtype=bool)


class SMOptimizedMultiTimeframeHma_64f8cf(PinePortBase, IStrategy):
    source_id = "SM_64f8cf6afcafc509"
    source_file = (
        "HMA优化多周期量化交易策略与动态止损结合-Optimized-Multi-Timeframe-HMA-"
        "Quantitative-Trading-Strategy-with-Dynamic-Stop-Loss.md"
    )
    timeframe = "1d"
    # The source really does carry a short entry; it is gated at run time by
    # `Strategy Direction`, whose default 'long' suppresses it.
    can_short = True
    # Input defaults, exactly as written in the source.
    source_defaults: dict = {
        "session": "1800-1700",
        "strat_dir_input": "long",
        "modeSwitch": "Hma",
        "length": 55,
        "switchColor": True,
        "candleCol": False,
        "visualSwitch": True,
        "thicknesSwitch": 1,
        "transpSwitch": 40,
        "slPoints": 1,
        "slOffset": 1,
    }
    # strategy('DAP Hull Sweet Scalp v1 Strategy', overlay=true): title and
    # overlay only, so fixed / 1 contract, 1000000 initial capital, 0% fee,
    # pyramiding 0, process_orders_on_close=false.
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    # strategy.exit(trail_points=..., trail_offset=...) is a resting stop leg.
    source_reproduce_stops = True
    source_mintick = 0.1
    source_fidelity_notes = [
        "`strategy.risk.allow_entry_in(...)` is not modelled by the shared "
        "engine (PINE_SEMANTICS.md 二.3) but it does change behaviour: with the "
        "declared default 'long' the short entry never fires. The port "
        "reproduces that single rule from the same input rather than emitting "
        "shorts the source would not take.",
        "The trailing exit is the unverified-trail case of PINE_SEMANTICS.md "
        "3.6 / 二.9(b): the same id is re-placed every signal bar, and the "
        "engine starts a replacement's ratchet from scratch, so the trail can "
        "only arm and trigger within one bar. Not claimed equivalent.",
        "Pine's `trail_points` / `trail_offset` are in TICKS; the engine reads "
        "them as price distances, so both are multiplied by mintick here "
        "(PINE_SEMANTICS.md 3.5). No earlier port in this repository uses a "
        "trailing exit, so there is no precedent to follow.",
        "`_length/2`, `_length/3` and `len/2` are floats where Pine's ta.wma / "
        "ta.ema want an int. Pine's implicit cast rounds to the nearest integer "
        "(_pine_int): 55/2 -> 28, 55/3 -> 18. MODELLING CHOICE with parity "
        "risk -- truncation would give 27 and 18 -- needing platform"
        "comparison to settle.",
        "`math.round(math.sqrt(_length))` is explicit in the source and is "
        "reproduced as such (55 -> 7).",
        "The session window '1800-1700' wraps past midnight; evaluated against "
        "UTC 1d bar opens (00:00) every bar is inside it, so `Session` is "
        "always true, `end` is never true and the closing `close_all` never "
        "fires. Derived from the timestamps, not hardcoded.",
        "`bgcolor` / `plot` / `fill` / `barcolor` and the colour/thickness/"
        "transparency inputs are display-only and are not reproduced.",
        "`process_orders_on_close` is not declared, so Pine's default `false` "
        "applies and the engine's next-open fill model matches.",
    ]

    # ---- Hull family -------------------------------------------------------
    @staticmethod
    def _hma(source, length):
        # ta.wma(2*ta.wma(src, length/2) - ta.wma(src, length), round(sqrt(length)))
        inner = 2.0 * ta.pine_wma(source, _pine_int(length / 2)) - ta.pine_wma(
            source, int(length)
        )
        return ta.pine_wma(inner, _pine_int(math.sqrt(length)))

    @staticmethod
    def _ehma(source, length):
        inner = 2.0 * ta.pine_ema(source, _pine_int(length / 2)) - ta.pine_ema(
            source, int(length)
        )
        return ta.pine_ema(inner, _pine_int(math.sqrt(length)))

    @staticmethod
    def _thma(source, length):
        # ta.wma(ta.wma(src, length/3)*3 - ta.wma(src, length/2) - ta.wma(src, length), length)
        inner = (
            ta.pine_wma(source, _pine_int(length / 3)) * 3.0
            - ta.pine_wma(source, _pine_int(length / 2))
            - ta.pine_wma(source, int(length))
        )
        return ta.pine_wma(inner, int(length))

    def _mode(self, mode_switch: str, source, length):
        if mode_switch == "Hma":
            return self._hma(source, length)
        if mode_switch == "Ehma":
            return self._ehma(source, length)
        if mode_switch == "Thma":
            return self._thma(source, _pine_int(length / 2))
        return pd.Series(np.nan, index=source.index, dtype=float)

    # ---- indicators --------------------------------------------------------
    def pine_indicators(self, dataframe, params):
        close = dataframe["close"]
        length = int(params["length"])

        # HULL = Mode(modeSwitch, src, length)
        hull = self._mode(str(params["modeSwitch"]), close, length)
        # MHULL = HULL[0];  SHULL = HULL[2]
        shifted = hull.shift(2)

        dataframe["pine_hull"] = hull
        dataframe["pine_hull_2"] = shifted
        dataframe["pine_cross_up"] = ta.pine_crossover(hull, shifted).to_numpy(
            dtype=bool
        )
        dataframe["pine_cross_down"] = ta.pine_crossunder(hull, shifted).to_numpy(
            dtype=bool
        )

        # Session = not na(time(timeframe.period, session))
        index = dataframe.index
        if not isinstance(index, pd.DatetimeIndex) and "date" in dataframe.columns:
            index = pd.DatetimeIndex(dataframe["date"])
        times = pd.DatetimeIndex(index)
        if times.tz is None:
            times = times.tz_localize("UTC")
        session = _in_session(times, str(params["session"]))
        dataframe["pine_session"] = session
        # start = Session and not Session[1]; end = not Session and Session[1].
        # Session[1] is na on bar 0, so both are false there.
        previous = np.concatenate(([False], session[:-1]))
        dataframe["pine_session_start"] = session & ~previous
        dataframe["pine_session_end"] = ~session & previous
        return dataframe

    def pine_context(self, dataframe, params):
        direction = str(params["strat_dir_input"])
        return {
            "session": dataframe["pine_session"].to_numpy(dtype=bool),
            "cross_up": dataframe["pine_cross_up"].to_numpy(dtype=bool),
            "cross_down": dataframe["pine_cross_down"].to_numpy(dtype=bool),
            "session_end": dataframe["pine_session_end"].to_numpy(dtype=bool),
            "allow_long": direction in ("long", "all"),
            "allow_short": direction in ("short", "all"),
            # trail_points / trail_offset are ticks in Pine; the engine reads
            # them as price distances, so convert with mintick.
            "trail_points": float(params["slPoints"]) * float(self.source_mintick),
            "trail_offset": float(params["slOffset"]) * float(self.source_mintick),
        }

    # ---- orders ------------------------------------------------------------
    def pine_script(self, broker, i, ctx):
        # if Session and ta.crossover(HULL[0], HULL[2])
        if ctx["session"][i] and ctx["cross_up"][i]:
            if ctx["allow_long"]:
                broker.entry("long", "long")
            broker.exit(
                "trailing stop", from_entry="long",
                trail_points=ctx["trail_points"], trail_offset=ctx["trail_offset"],
            )

        # if Session and ta.crossunder(HULL[0], HULL[2])
        if ctx["session"][i] and ctx["cross_down"][i]:
            if ctx["allow_short"]:
                broker.entry("short", "short")
            broker.exit(
                "trailing stop", from_entry="short",
                trail_points=ctx["trail_points"], trail_offset=ctx["trail_offset"],
            )

        # if end -> strategy.close_all("End of Session - Go FLat")
        if ctx["session_end"][i]:
            broker.close_all()
