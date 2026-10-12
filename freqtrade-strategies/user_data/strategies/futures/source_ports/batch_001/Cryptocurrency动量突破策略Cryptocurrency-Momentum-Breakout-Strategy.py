"""Port of sources/SM_51dbd0ce1b72bced.pine
(batch_001/Cryptocurrency动量突破策略Cryptocurrency-Momentum-Breakout-Strategy.md).

Pine v3, long only, on the `/*backtest` header's `period: 1d`. One custom
indicator -- the "[BoTo] Pump&Dump" candle-body oscillator -- drives both the
entry and the exit:

    multiplier = input(3.0)
    length     = input(100)
    stop       = input(100.0, title = "Stop loss, %")

    body = abs(close - open)
    sma  = sma(body, length) * multiplier

    pump = body > sma and close > open
    dump = body > sma and close < open

    size = strategy.position_size
    autostop = 0.0
    autostop := pump and size == 0 ? low : autostop[1]
    userstop = 0.0
    userstop := pump and size == 0 ? close - (close / 100 * stop) : userstop[1]

    if pump
        strategy.entry("Pump", strategy.long)
    if dump or low < autostop or low < userstop
        strategy.close_all()

Both stops are LATCHED, both are armed on the same bar and only while flat
(`pump and size == 0`), and both are plain conditions on the COMPLETED bar --
neither is a resting order. `autostop` latches the signal bar's own `low`;
`userstop` latches `close - close/100*stop`, a percentage below the signal
bar's close. The close they trigger is a market `strategy.close_all()`, which
the engine fills at the NEXT bar's open -- exactly the timing Freqtrade gives a
next-candle market exit, so no stop level has to be mirrored through
`pine_stop_level` and `source_reproduce_stops` is False.

MEASURED, and surprising enough to record: at the source's own default
`stop = 100.0` the percentage stop is INERT. `close - close/100*100` is 0 up to
floating-point rounding (measured on the BTC/USDT 1d `verify_chain` frame,
367 bars: |userstop| <= 1.46e-11, exactly 0.0 on 299 of them), and `low` is
positive, so `low < userstop` is never true. Only the `autostop` (breakout)
leg and the `dump` signal can ever close a position at the default settings.
The md's prose presents the two stop methods as freely combinable
alternatives; the code agrees that both exist, but at the published defaults
one of them cannot fire.

The `0.0` initialisers on `autostop` / `userstop` are a red herring and are NOT
reproduced as 0.0. Neither is `var`, so the declaration runs every bar and is
immediately overwritten by the `:=` on the same bar; the `:=`'s else-branch is
`autostop[1]` / `userstop[1]`, which is na on the first bar. The literal
therefore never reaches the comparison -- the series is na until it is first
armed. Modelled as na-initialised state, which is what the recursion actually
carries. (Downstream the two are indistinguishable here, because `low < 0` and
`low < na` are both false for a positive low; the na model is used because it
is the one the source's recursion describes.)

`strategy()` declares default_qty_type = strategy.percent_of_equity with
default_qty_value = 100 -- a full-equity long per entry -- and pyramiding = 0.
`initial_capital` is not declared, so Pine's documented default 1000000 USD is
used; `commission_type`/`commission_value` are not declared either, so Pine's
0% default stands. The md's argument table agrees with all three input
defaults (3 / 100 / 100).

Warmup: `sma(body, 100)` is na until 100 bars have elapsed, so `body > sma` --
and therefore `pump` and `dump` -- is false on the first 99 bars (indices
0..98); the first bar that can signal is index 99. Verified by counting on the
`verify_chain` frame.

FIDELITY:

* `pump` / `dump` compare against a na `sma` during the warmup; Pine treats an
  na comparison as false and pandas gives False here, so the columns are False
  rather than na. That is what the two `if`s read.
* md-vs-source: the md's prose says the long is opened "at the close of that
  candlestick". The code places a plain market `strategy.entry` with no
  `process_orders_on_close`, so it fills at the NEXT bar's open. The code is
  followed; the prose overstates the entry price by one bar's move.
* `plot(body, ...)`, `plot(sma, ...)`, `col = pump ? green : dump ? red : na`
  and `bgcolor(...)` are display-only, read by nothing and place no order, so
  they are not reproduced. `col` is also a dead local (the plotting framework,
  not the script, consumes it).
* The source declares no `strategy.exit`, no `stop=`/`limit=` argument and no
  other exit order, so `source_reproduce_stops` is False.
* `can_short` is False: the source has no short entry at all.
* Pine's `time`/session functions, `request.security`, `varip` and
  `strategy.risk.*` are not used by this source.
* No future-data reference and no repainting: every input is the current bar's
  own OHLC plus `sma` of past bodies; orders fill on the next bar's open.
* The backtest window in the `/*backtest` header (2022-10-19 to 2023-04-13) is
  the host's extraction metadata, not an `input.time` filter, so the port runs
  on whatever range the caller supplies. The header's `basePeriod: 1h` is the
  host's intrabar granularity for filling 1d bars, not the strategy's period.
* Leverage, margin, liquidation, funding and the venue's contract-step rounding
  are not modelled.
"""
from __future__ import annotations

import numpy as np
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


class SMCryptocurrencyMomentumBreakout_51dbd0(PinePortBase, IStrategy):
    source_id = "SM_51dbd0ce1b72bced"
    source_file = (
        "Cryptocurrency动量突破策略Cryptocurrency-Momentum-Breakout-Strategy.md"
    )
    # /*backtest ... period: 1d, basePeriod: 1h
    timeframe = "1d"
    # Long only: the source has no short entry.
    can_short = False
    source_defaults: dict = {"multiplier": 3.0, "length": 100, "stop": 100.0}
    source_qty_type = "percent_of_equity"
    source_qty_value = 100.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    # Not declared by strategy(), so Pine's documented default.
    source_initial_capital = 1_000_000.0
    # The only exit is a market strategy.close_all() placed from a bar-close
    # condition; there is no resting stop or limit to mirror.
    source_reproduce_stops = False
    source_fidelity_notes = [
        "The `autostop = 0.0` / `userstop = 0.0` initialisers are NOT "
        "reproduced as 0.0. Both are plain (non-var) declarations, overwritten "
        "on the same bar by the following `:=`, whose else-branch is "
        "<name>[1] -- na on the first bar. The literal never reaches the "
        "comparison. Modelled as na-initialised per-run state. The two models "
        "are indistinguishable here (`low < 0` and `low < na` are both false "
        "for a positive low); the na model is used because it is what the "
        "recursion describes.",
        "At the default stop = 100.0 the percentage stop is INERT: "
        "close - close/100*100 is 0 up to float rounding (measured on the "
        "verify_chain BTC/USDT 1d frame, 367 bars: |userstop| <= 1.46e-11, "
        "exactly 0.0 on 299 of them) and low > 0, so `low < userstop` is never "
        "true. Only `autostop` and `dump` can close a position at the defaults.",
        "pump/dump are False (not na) during the 99-bar warmup of "
        "sma(body, 100), because a comparison with na is false; the first bar "
        "whose window is full is index 99 (measured). On the verify_chain "
        "frame the first signal is a pump at index 140: 9 pumps, 4 dumps.",
        "md-vs-source: the md prose says a long is opened 'on the close of "
        "that candlestick'. The code is a plain market strategy.entry with no "
        "process_orders_on_close, so it fills at the NEXT bar's open. Code "
        "followed, prose recorded.",
        "No strategy.exit and no stop=/limit= argument anywhere, and both "
        "stops are bar-close CONDITIONS rather than resting orders, so "
        "source_reproduce_stops is False and the engine's next-open market "
        "fill is exactly Freqtrade's.",
        "plot(body) / plot(sma) / the pump-dump `col` variable and bgcolor() "
        "are display-only and place no order; not reproduced.",
        "can_short is False -- the source never enters short, matching the "
        "md's 'long only' description.",
        "initial_capital is not declared, so Pine's documented 1000000 USD "
        "default is recorded; commission is not declared either (Pine's 0%), "
        "and the md's argument table agrees with all three input defaults.",
        "No future-data reference and no repainting: everything is the current "
        "bar's own OHLC plus sma of past bodies, and orders fill next open.",
        "The /*backtest window (2022-10-19 to 2023-04-13) is extraction "
        "metadata, not an input.time filter, so no data is trimmed. Its "
        "basePeriod: 1h is the host's intrabar granularity, not the period.",
        "Leverage, margin, liquidation, funding and the venue's contract-step "
        "rounding are not modelled.",
    ]

    def pine_indicators(self, dataframe, params):
        close = dataframe["close"]
        open_ = dataframe["open"]
        # body = abs(close - open)
        body = (close - open_).abs()
        dataframe["pine_body"] = body
        # sma = sma(body, length) * multiplier
        sma = ta.pine_sma(body, params["length"]) * float(params["multiplier"])
        dataframe["pine_sma"] = sma
        # pump = body > sma and close > open
        dataframe["pine_pump"] = ((body > sma) & (close > open_)).fillna(False)
        # dump = body > sma and close < open
        dataframe["pine_dump"] = ((body > sma) & (close < open_)).fillna(False)
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "pump": dataframe["pine_pump"].to_numpy(dtype=bool),
            "dump": dataframe["pine_dump"].to_numpy(dtype=bool),
            "low": dataframe["low"].to_numpy(dtype=float),
            "close": dataframe["close"].to_numpy(dtype=float),
            "stop": float(params["stop"]),
            # autostop / userstop: na until first armed -- see the notes.
            "state": {"autostop": float("nan"), "userstop": float("nan")},
        }

    def pine_script(self, broker, i, ctx):
        state = ctx["state"]
        low = float(ctx["low"][i])
        close = float(ctx["close"][i])

        # size = strategy.position_size
        size = broker.position_size
        # autostop := pump and size == 0 ? low : autostop[1]
        # A plain (non-var) declaration, so `[1]` is the previous bar's final
        # value -- which is what the state container holds before this update.
        autostop = state["autostop"]
        # userstop := pump and size == 0 ? close - (close / 100 * stop) : userstop[1]
        userstop = state["userstop"]
        if ctx["pump"][i] and size == 0:
            autostop = low
            userstop = close - (close / 100.0 * ctx["stop"])
        state["autostop"] = autostop
        state["userstop"] = userstop

        # if pump
        #     strategy.entry("Pump", strategy.long)
        if ctx["pump"][i]:
            broker.entry("Pump", "long")

        # if dump or low < autostop or low < userstop
        #     strategy.close_all()
        # na odds compare false, so an unarmed stop cannot fire.
        dump = bool(ctx["dump"][i])
        below_autostop = (not np.isnan(autostop)) and low < autostop
        below_userstop = (not np.isnan(userstop)) and low < userstop
        if dump or below_autostop or below_userstop:
            broker.close_all()
