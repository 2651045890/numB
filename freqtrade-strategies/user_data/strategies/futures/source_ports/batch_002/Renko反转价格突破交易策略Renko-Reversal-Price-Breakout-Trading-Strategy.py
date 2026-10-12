"""Port of sources/SM_923a0c530b718f20.pine ([STRATEGY][RS]Renko V0).

Pine v2. The script keeps two series, `ro = open` and `rc = close`, and fires a
five-bar pattern on them:

    buy_entry  = rc[4] <  ro[4] and rc[3] >  ro[3] and rc[2] >  ro[2]
                 and rc[1] > ro[1] and rc > ro
    sel_entry  = rc[4] >  ro[4] and rc[3] <  ro[3] and rc[2] <  ro[2]
                 and rc[1] < ro[1] and rc < ro

i.e. a red bar five bars back, followed by four rising bars (or the mirror for
shorts). Both branches call strategy.entry with qty=trade_size (1) and no
stop/limit, so they are plain market orders that fill on the next bar's open;
a long entry while short reverses the position, which the shared engine models.

The source declares `pyramiding=0` and `initial_capital=100000` but no
default_qty_type / default_qty_value / commission, so Pine's documented
defaults apply to those: strategy.fixed / 1 / 0%. `trade_size = 1` is a
literal, not an input, so there are no tunable parameters to carry over.
"""
import numpy as np
from freqtrade.strategy import IStrategy

from pine_port_base import PinePortBase


def _lt(a, b) -> bool:
    """Pine `<` where an na operand makes the comparison false."""
    if not (np.isfinite(a) and np.isfinite(b)):
        return False
    return bool(a < b)


def _gt(a, b) -> bool:
    """Pine `>` where an na operand makes the comparison false."""
    if not (np.isfinite(a) and np.isfinite(b)):
        return False
    return bool(a > b)


class SMRenkoReversalBreakout_923a0c(PinePortBase, IStrategy):
    source_id = "SM_923a0c530b718f20"
    source_file = "Renko反转价格突破交易策略Renko-Reversal-Price-Breakout-Trading-Strategy.md"
    timeframe = "1h"
    can_short = True
    source_defaults = {}
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 100_000.0
    source_fidelity_notes = [
        "The script is titled Renko but reads the bare `open`/`close` series; the "
        "port evaluates it on the backtest header's regular 1h bars. On a Renko "
        "chart those series would be brick open/close, which OHLCV cannot supply.",
        "`currency=currency.USD` on the strategy() declaration is not modelled: the "
        "engine keeps a plain USD-denominated ledger with no FX conversion. At the "
        "source's fixed qty of 1 the two coincide.",
    ]

    def pine_indicators(self, dataframe, params):
        # `ro = open` / `rc = close` -- the script reads raw OHLC directly, so
        # there is no indicator to compute.
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "open": dataframe["open"].to_numpy(dtype=float),
            "close": dataframe["close"].to_numpy(dtype=float),
        }

    def pine_script(self, broker, i, ctx):
        # `rc[4]` is the close four bars back, so the pattern needs five bars;
        # before that every comparison has an na operand and is false.
        if i < 4:
            return
        open_, close = ctx["open"], ctx["close"]
        buy_entry = (
            _lt(close[i - 4], open_[i - 4])
            and _gt(close[i - 3], open_[i - 3])
            and _gt(close[i - 2], open_[i - 2])
            and _gt(close[i - 1], open_[i - 1])
            and _gt(close[i], open_[i])
        )
        sel_entry = (
            _gt(close[i - 4], open_[i - 4])
            and _lt(close[i - 3], open_[i - 3])
            and _lt(close[i - 2], open_[i - 2])
            and _lt(close[i - 1], open_[i - 1])
            and _lt(close[i], open_[i])
        )
        if buy_entry:
            broker.entry("buy", "long", qty=1.0, when=True)
        if sel_entry:
            broker.entry("sell", "short", qty=1.0, when=True)
