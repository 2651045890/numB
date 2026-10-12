"""Port of sources/SM_82519f7676ef9ec0.pine
(batch_001/Dual-Moving-Average-Breakout-Strategy.md).

Pine v2 -- Noro's "Multima v1.0". Two moving averages of `close`, an SMA
(`lenma1`, default 40) and an EMA (`lenma2`, default 40), are each turned into
a -1/0/+1 vote against the close:

    ma1 = sma(close, lenma1)
    ma2 = ema(close, lenma2)
    signal1 = usema1 == false ? 0 : close > ma1 ? 1 : -1
    signal2 = usema2 == false ? 0 : close > ma2 ? 1 : -1
    lots = signal1 + signal2

`lots` is the sum of the two votes: +2 / +1 / 0 / -1 / -2. The whole order
logic is three statements:

    if lots > 0 and (close < open or usecf == false)
        strategy.entry("Long", strategy.long, needlong == false ? 0 : na)
    if lots < 0 and (close > open or usecf == false)
        strategy.entry("Short", strategy.short, needshort == false ? 0 : na)
    if lots == 0
        strategy.close_all()

so the entry needs BOTH a majority vote and a candle whose colour agrees with
it (`usecf`, "Use color-filter", default true; `close < open` is a down candle
for the long, `close > open` an up candle for the short). `lots == 0` means the
two votes cancel -- one average above the close and one below -- and closes
everything. With `usecf` true that `lots == 0` branch is the only exit in the
source: there is no `strategy.exit`, no stop and no take-profit, so
`source_reproduce_stops` is False and a position is closed either by that flat
vote or by the opposite entry reversing it.

`needlong` / `needshort` gate the entry through the QUANTITY argument, exactly
as written: `needlong == false ? 0 : na`. A quantity of 0 is an order for zero
contracts, so Pine's engine rejects it at fill time and never opens a position;
`na` means "use `default_qty_*`". The port passes `qty=0.0` / `qty=None`
respectively and lets pine_engine's `entry_will_fill` drop the zero order, so
disabling a side produces no signal at all rather than a signal of size zero.

`strategy(title=..., default_qty_type = strategy.percent_of_equity,
default_qty_value=100.0, pyramiding=0)` sets the sizing and nothing else:
initial capital and commission are NOT declared, so Pine's own defaults apply
(initial_capital 1000000, commission 0%). `default_qty_value=100.0` with
`percent_of_equity` is 100% of equity per entry.

The `/*backtest` header declares `period: 10m` on Futures_Binance BTC_USDT, so
`timeframe` is "10m"; its `basePeriod: 1m` is the backtester's own fill
granularity for those 10m bars.

FIDELITY: see `source_fidelity_notes` -- chiefly the `close > ma1` comparison
during the SMA warmup (na compares false, so `signal1` is -1 there) and the
seeded-EMA front-end risk inherited from the shared layer.
"""
import numpy as np
import pandas as pd
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


class SMDualMovingAverageBreakout_82519f(PinePortBase, IStrategy):
    source_id = "SM_82519f7676ef9ec0"
    source_file = "Dual-Moving-Average-Breakout-Strategy.md"
    timeframe = "10m"
    can_short = True
    source_defaults: dict = {
        # input(true, "long")
        "needlong": True,
        # input(true, "short")
        "needshort": True,
        # input(true, "Use MA1 (SMA, blue)")
        "usema1": True,
        # input(true, "Use MA2 (EMA, red)")
        "usema2": True,
        # input(40, defval = 40, minval = 2, maxval = 1000, title = "MA1 length")
        "lenma1": 40,
        # input(40, defval = 40, minval = 2, maxval = 1000, title = "MA2 length")
        "lenma2": 40,
        # input(true, defval = true, title = "Use color-filter")
        "usecf": True,
    }
    # strategy(default_qty_type = strategy.percent_of_equity,
    #           default_qty_value=100.0, pyramiding=0) -- nothing else declared.
    source_qty_type = "percent_of_equity"
    source_qty_value = 100.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    source_reproduce_stops = False
    source_fidelity_notes = [
        "No `strategy.exit` exists in the source: the only exits are the "
        "`lots == 0` -> strategy.close_all() branch and the opposite entry "
        "reversing the position. source_reproduce_stops is therefore False.",
        "The gating of a side is done through the ORDER QUANTITY, not an `if` "
        "guard: `needlong == false ? 0 : na`. A zero quantity is an order the "
        "engine cannot fill, so the port passes qty=0.0 and lets "
        "pine_engine.entry_will_fill drop it; `na` becomes qty=None, i.e. "
        "Pine's default_qty_* sizing.",
        "`close > ma1` (and `close > ma2`) is FALSE while the average is na, "
        "which is Pine's rule for comparing against na (`if`/`?:` on an na "
        "condition takes the else branch). pine_ta.pine_sma returns na until "
        "the SMA window has filled, so for the first lenma1-1 bars signal1 is "
        "-1 rather than +1/-1, and `lots` there is 0 or -2 -- the SHORT side of "
        "the strategy can therefore fire during the SMA warmup. Reproduced as "
        "written rather than special-cased.",
        "pine_ta.pine_ema is seeded with the first observation (PINE_SEMANTICS "
        "3.1); if the original platform seeds ta.ema with an SMA of the first "
        "`lenma2` values, this port's EMA exists from bar 1 where the source's "
        "does not exist until bar ~lenma2. The recursion converges, so this is "
        "a front-end difference only -- but the source's conditions are simple "
        "`close > ma` comparisons, so a differing early EMA changes early "
        "entries. Unresolved and shared-layer, not corrected here.",
        "initial_capital and commission are not declared by the source, so "
        "Pine's defaults are carried: 1000000 and 0%. `default_qty_value=100.0` "
        "with percent_of_equity is 100% of equity per entry, reproduced by the "
        "engine's own sizing (the port base hands Freqtrade the engine's "
        "recorded notional, not a re-derivation).",
        "`strategy.close_all()` is modelled by the engine as a next-open market "
        "close of every open entry; Pine's close_all has the same next-open "
        "timing. With pyramiding=0 the second and later same-direction entries "
        "while a position is open are rejected.",
        "Leverage, margin, liquidation, funding and venue contract-step "
        "rounding are not modelled.",
    ]

    def pine_indicators(self, dataframe, params):
        close = dataframe["close"]
        ma1 = ta.pine_sma(close, params["lenma1"])
        ma2 = ta.pine_ema(close, params["lenma2"])

        # signal1 = usema1 == false ? 0 : close > ma1 ? 1 : -1
        # A comparison against na is false, so the -1 arm is taken on those bars.
        signal1 = pd.Series(np.where(close > ma1, 1.0, -1.0), index=dataframe.index)
        if not params["usema1"]:
            signal1 = pd.Series(0.0, index=dataframe.index)
        # signal2 = usema2 == false ? 0 : close > ma2 ? 1 : -1
        signal2 = pd.Series(np.where(close > ma2, 1.0, -1.0), index=dataframe.index)
        if not params["usema2"]:
            signal2 = pd.Series(0.0, index=dataframe.index)
        lots = (signal1 + signal2).astype(int)

        # (close < open or usecf == false) and (close > open or usecf == false)
        down_candle = (dataframe["close"] < dataframe["open"]).to_numpy(bool)
        up_candle = (dataframe["close"] > dataframe["open"]).to_numpy(bool)
        if params["usecf"] is False:
            down_candle = np.ones(len(dataframe), dtype=bool)
            up_candle = np.ones(len(dataframe), dtype=bool)

        dataframe["pine_ma1"] = ma1
        dataframe["pine_ma2"] = ma2
        dataframe["pine_signal1"] = signal1
        dataframe["pine_signal2"] = signal2
        dataframe["pine_lots"] = lots
        dataframe["pine_long_condition"] = (lots > 0).to_numpy() & down_candle
        dataframe["pine_short_condition"] = (lots < 0).to_numpy() & up_candle
        dataframe["pine_flat_condition"] = (lots == 0).to_numpy()
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "close": dataframe["close"].to_numpy(dtype=float),
            "open": dataframe["open"].to_numpy(dtype=float),
            "long_condition": dataframe["pine_long_condition"].to_numpy(bool),
            "short_condition": dataframe["pine_short_condition"].to_numpy(bool),
            "flat_condition": dataframe["pine_flat_condition"].to_numpy(bool),
            # needlong == false ? 0 : na ; needshort == false ? 0 : na
            "long_qty": None if params["needlong"] else 0.0,
            "short_qty": None if params["needshort"] else 0.0,
        }

    def pine_script(self, broker, i, ctx):
        # if lots > 0 and (close < open or usecf == false)
        #     strategy.entry("Long", strategy.long, needlong == false ? 0 : na)
        if ctx["long_condition"][i]:
            broker.entry("Long", "long", ctx["long_qty"])
        # if lots < 0 and (close > open or usecf == false)
        #     strategy.entry("Short", strategy.short, needshort == false ? 0 : na)
        if ctx["short_condition"][i]:
            broker.entry("Short", "short", ctx["short_qty"])
        # if lots == 0
        #     strategy.close_all()
        if ctx["flat_condition"][i]:
            broker.close_all()
