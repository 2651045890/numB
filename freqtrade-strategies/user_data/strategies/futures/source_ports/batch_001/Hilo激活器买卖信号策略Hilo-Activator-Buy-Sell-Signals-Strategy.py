"""Port of sources/SM_9bf94fee6b0a94fd.pine (batch_001/Hilo激活器买卖信号策略Hilo-Activator-Buy-Sell-Signals-Strategy.md).

Pine v4, `//@version=4`, `strategy("Hilo Activator com Sinais de Compra e Venda",
overlay=true)`. A shifted moving average of the highs/lows that alternates
between "upper line" and "lower line" according to a latched trend state:

    period = input(8)                        // Período
    shift  = input(1)                        // Deslocamento
    exp    = input(false)                    // Média Móvel Exponencial
    max = exp ? ema(high[shift], period) : sma(high[shift], period)
    min = exp ? ema(low[shift],  period) : sma(low[shift],  period)

    pos = close > max ? -1 : close < min ? 1 : 0
    pos := pos == 0 ? na(pos[1]) ? 0 : pos[1] : pos
    hilo = pos == 1 ? max : min

    buySignal  = crossover(close, hilo)
    sellSignal = crossunder(close, hilo)

    strategy.entry("Buy",  strategy.long,  when = buySignal)
    strategy.entry("Sell", strategy.short, when = sellSignal)

The third line is a LATCH: when neither band is broken (`pos == 0`) the previous
bar's `pos` is carried forward, and on the very first bar -- where `pos[1]` does
not exist and is na -- it settles at 0. So the state only ever changes on a bar
that actually breaks a band. It is reproduced as a forward pass over the
bars, which is causal by construction.

`shift` is a positive displacement: `high[1]` / `low[1]` are the PREVIOUS bar's
extremes, so the two lines are computed one bar back and no look-ahead exists.

`strategy()` declares only `title` / `overlay`, so Pine's documented defaults
apply and are what this port carries: `default_qty_type=fixed`, one unit per
order, `commission_value=0`, `pyramiding=0`, `process_orders_on_close=false`,
initial capital 1000000.

The `/*backtest` header declares `period: 10m` on Futures_Binance BTC_USDT, so
`timeframe` is "10m"; its `basePeriod: 1m` is the FMZ backtester's own filling
granularity for those 10m bars, not the strategy's period. There is no local 10m
futures history, so the chain verifier reports `skipped_no_local_data`.

FIDELITY:

* The source names its two series `max` and `min`, shadowing Pine's builtins of
  the same name. They are ordinary series here and are named `upper_line` /
  `lower_line`; nothing in the source reads a `math.max` / `math.min`.
* `exp` is a `bool` input used only as a bare condition (`exp ? a : b`), never
  in a numeric context, so no section-1.16 bool-as-number hazard applies; the
  port uses its truthiness directly rather than comparing it to 0 or 1.
* Only the `sma` branch of `exp` is reachable at the declared default. The port
  implements the `ema` branch too, so a `source_parameters` override of `exp`
  selects the same series the source would.
* `sma` returns na until its window is full and `crossover` / `crossunder`
  against an na operand are false, so no signal can arrive before `period +
  shift` bars have elapsed.
* `plotshape(...)` markers and the commented-out `plotbar(...)` are display-only
  and are not reproduced.
* The md's Strategy Arguments table lists `v_input_2` ("Deslocamento") with a
  default of `true`; the source's `shift` input is `input(1)` -- the integer 1.
  The source is reproduced. The table's `true` reads as a mis-rendered `1`
  (the following row, `exp`, is the one that really is a bool).
* Leverage, margin, liquidation and funding are not modelled; the venue's
  contract-step rounding is not modelled either, so the framework and the
  engine can differ by a rounded quantity (measured separately by the chain
  verifier rather than treated as a signal difference).
"""
import numpy as np
import pandas as pd

from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


class SMHiloActivatorBuySellSignals_9bf94f(PinePortBase, IStrategy):
    source_id = "SM_9bf94fee6b0a94fd"
    source_file = "Hilo激活器买卖信号策略Hilo-Activator-Buy-Sell-Signals-Strategy.md"
    timeframe = "10m"
    can_short = True
    source_defaults: dict = {"period": 8, "shift": 1, "exp": False}
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    # Neither strategy.exit nor strategy.close exists: the only way out of a
    # position is the opposite entry reversing it.
    source_reproduce_stops = False
    source_fidelity_notes = [
        "The source shadows Pine's max/min builtins with two plain series; they "
        "are carried as upper_line / lower_line and no builtin is read.",
        "`pos` is a latch: a bar that breaks neither band inherits the previous "
        "bar's state, and bar 0 settles at 0 because pos[1] is na. Reproduced "
        "as a forward pass, so it stays causal.",
        "`shift` displaces the source series backwards (high[1], low[1]), so "
        "both lines are computed from the previous bar; no look-ahead.",
        "`exp` is a bool input used only as a bare condition, never in a numeric "
        "context, so the section-1.16 bool-as-number hazard does not apply; the "
        "port uses its truthiness directly. The ema branch is implemented even "
        "though the declared default takes the sma branch.",
        "There is no exit call in the source; source_reproduce_stops is False "
        "and a position open at the end of the window stays open.",
        "The md's Strategy Arguments table shows v_input_2 ('Deslocamento') as "
        "`true`; the source's shift input is input(1). The source is "
        "reproduced -- the table row looks like a mis-rendered `1`.",
        "plotshape markers and the commented-out plotbar are display-only and "
        "are not reproduced.",
        "Leverage, margin, liquidation, funding and venue contract-step "
        "rounding are not modelled.",
    ]

    def pine_indicators(self, dataframe, params):
        high = dataframe["high"]
        low = dataframe["low"]
        close = dataframe["close"]

        period = int(params["period"])
        shift = int(params["shift"])
        use_ema = bool(params["exp"])

        high_shifted = high.shift(shift)
        low_shifted = low.shift(shift)

        # max = exp ? ema(high[shift], period) : sma(high[shift], period)
        if use_ema:
            upper_line = ta.pine_ema(high_shifted, period)
            lower_line = ta.pine_ema(low_shifted, period)
        else:
            upper_line = ta.pine_sma(high_shifted, period)
            lower_line = ta.pine_sma(low_shifted, period)

        # pos = close > max ? -1 : close < min ? 1 : 0
        # An na comparison is false, so both bands being na leaves pos at 0.
        upper_broken = (close > upper_line).fillna(False).to_numpy()
        lower_broken = (close < lower_line).fillna(False).to_numpy()
        raw = np.where(upper_broken, -1.0, np.where(lower_broken, 1.0, 0.0))

        # pos := pos == 0 ? (na(pos[1]) ? 0 : pos[1]) : pos
        position = np.zeros(len(raw), dtype=float)
        for i in range(len(raw)):
            if raw[i] != 0.0 or i == 0:
                # The first bar has no pos[1], so na(pos[1]) settles it at 0.
                position[i] = raw[i]
            else:
                position[i] = position[i - 1] if position[i - 1] != 0.0 else 0.0

        upper_arr = upper_line.to_numpy(dtype=float)
        lower_arr = lower_line.to_numpy(dtype=float)
        # hilo = pos == 1 ? max : min
        hilo = pd.Series(
            np.where(position == 1.0, upper_arr, lower_arr),
            index=dataframe.index,
            dtype=float,
        )

        dataframe["pine_hilo"] = hilo
        dataframe["pine_hilo_upper"] = upper_line
        dataframe["pine_hilo_lower"] = lower_line
        dataframe["pine_hilo_position"] = position
        dataframe["pine_buy_signal"] = ta.pine_crossover(close, hilo)
        dataframe["pine_sell_signal"] = ta.pine_crossunder(close, hilo)
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "buy_signal": dataframe["pine_buy_signal"].to_numpy(),
            "sell_signal": dataframe["pine_sell_signal"].to_numpy(),
        }

    def pine_script(self, broker, i, ctx):
        # strategy.entry("Buy", strategy.long, when = buySignal)
        if ctx["buy_signal"][i]:
            broker.entry("Buy", "long")
        # strategy.entry("Sell", strategy.short, when = sellSignal)
        if ctx["sell_signal"][i]:
            broker.entry("Sell", "short")
