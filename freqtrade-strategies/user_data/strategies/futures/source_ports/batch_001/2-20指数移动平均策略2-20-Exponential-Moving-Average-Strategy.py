"""Port of sources/SM_63b8264cc9856a3a.pine (2-20 Exponential Moving Average).

Pine v2, HPotter's "Strategy 2/20 Exponential Moving Average". Bare v2
builtins only -- `ema`, `max`, `min`, `iff`, `nz` -- over a single input:

    Length = input(20, minval=1)
    xXA = ema(close, Length)
    nHH = max(high, high[1])
    nLL = min(low, low[1])
    nXS = iff((nLL > xXA) or (nHH < xXA), nLL, nHH)
    pos = iff(nXS > close[1], -1, iff(nXS < close[1], 1, nz(pos[1], 0)))

`nXS` is a two-bar Donchian band (the *inside* band: nLL when the bar's range
sits wholly above the EMA, nHH when it sits wholly below, nHH otherwise) and
`pos` latches the direction of nXS relative to the previous close, holding the
previous value whenever the two are equal or either side is na (Pine compares
na as false, which falls through to `nz(pos[1], 0)`).

pos == 1 places "Long", pos == -1 places "Short". Both are market entries, so
the opposite entry nets against the open position -- a reversal is one order.
Because pos holds its value for many consecutive bars, the same entry is
re-issued every bar; with pyramiding 0 the engine refuses the repeats while a
position in that direction is already open, exactly as Pine does.

The strategy() declaration carries no sizing or capital properties, so Pine's
documented defaults apply: initial_capital 1000000 USD, default_qty_type
strategy.fixed, default_qty_value 1, commission 0%, pyramiding 0.

FIDELITY: v2 `ema` is ta.ema, translated by pine_ta.pine_ema (first-value
seed, documented in PINE_SEMANTICS.md as a parity risk). `max`/`min` propagate
na the way Pine's do, and `iff`/`or` treat an na comparison as false.
`barcolor(...)` is plot-only and carries no trade meaning, so it is dropped.
"""
import numpy as np

from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


class SMStrategy220Ema_63b826(PinePortBase, IStrategy):
    source_id = "SM_63b8264cc9856a3a"
    source_file = "2-20指数移动平均策略2-20-Exponential-Moving-Average-Strategy.md"
    timeframe = "1d"
    can_short = True
    source_defaults = {"Length": 20}
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    source_fidelity_notes = [
        "The strategy() declaration sets no sizing or capital property, so "
        "Pine's documented defaults are used: initial_capital 1000000, "
        "default_qty_type strategy.fixed, default_qty_value 1, commission 0%, "
        "pyramiding 0.",
        "v2 `ema` is ta.ema; pine_ta seeds the recursion with the first "
        "non-na value (PINE_SEMANTICS.md records this as a parity risk, since "
        "TradingView does not publish its exact seeding rule).",
        "`pos` is self-referential (`nz(pos[1], 0)`); it is reproduced with an "
        "explicit forward recursion, so bar i only ever reads bar i-1.",
        "`barcolor(...)` is a plot-only statement with no trade meaning and is "
        "dropped.",
    ]

    @staticmethod
    def _position_series(nXS: np.ndarray, close: np.ndarray) -> np.ndarray:
        """Pine `pos`, evaluated once per bar with the previous value in hand.

        `iff(nXS > close[1], -1, iff(nXS < close[1], 1, nz(pos[1], 0)))`: an na
        operand makes the comparison false, so the bar keeps the previous pos
        (0 on the first bar, where close[1] is na).
        """
        out = np.zeros(len(nXS), dtype=float)
        previous = 0.0
        for i in range(len(nXS)):
            if i > 0:
                reference, value = close[i - 1], nXS[i]
                if not (np.isnan(reference) or np.isnan(value)):
                    if value > reference:
                        previous = -1.0
                    elif value < reference:
                        previous = 1.0
            out[i] = previous
        return out

    def pine_indicators(self, dataframe, params):
        length = int(params["Length"])
        close = dataframe["close"].astype(float)
        high = dataframe["high"].astype(float)
        low = dataframe["low"].astype(float)

        xXA = ta.pine_ema(close, length)
        # Bare v2 max/min over a two-bar window; na propagates, so the first
        # bar's band is na and nXS falls through to na.
        nHH = ta.pine_max(high, high.shift(1))
        nLL = ta.pine_min(low, low.shift(1))
        # (nLL > xXA) or (nHH < xXA): na comparisons are false in Pine, which
        # pandas' comparison operators already give.
        use_nLL = (nLL > xXA).to_numpy() | (nHH < xXA).to_numpy()
        nXS = np.where(
            use_nLL, nLL.to_numpy(dtype=float), nHH.to_numpy(dtype=float)
        )

        dataframe["pine_xema"] = xXA.to_numpy()
        dataframe["pine_nxs"] = nXS
        dataframe["pine_pos"] = self._position_series(nXS, close.to_numpy(dtype=float))
        return dataframe

    def pine_context(self, dataframe, params):
        return {"pos": dataframe["pine_pos"].to_numpy()}

    def pine_script(self, broker, i, ctx):
        pos = ctx["pos"][i]
        if pos == 1.0:
            broker.entry("Long", "long")
        elif pos == -1.0:
            broker.entry("Short", "short")
