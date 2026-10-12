"""Port of sources/SM_c5708b1444e81f60.pine (batch_001/EHMA-Range-Strategy.md).

Pine v4 (`//@version=4`). An Exponential Hull Moving Average with a percentage
band around it; a bar closing outside the band is the entry, a bar closing back
inside it is the exit:

    borserman_ema(x, y) =>
        alpha = 2 / (y + 1)
        sum = 0.0
        sum := alpha * x + (1 - alpha) * nz(sum[1])
    EHMA  = borserman_ema(2 * borserman_ema(close, Period / 2)
                              - borserman_ema(close, Period), sqrtPeriod)
    upper = EHMA + EHMA * RangeWidth
    lower = EHMA - EHMA * RangeWidth
    long  = close > upper ;  exit_long  = close < lower
    short = close < lower ;  exit_short = close > upper

`pos_type` selects which of the three blocks runs -- "Both" (the default) places
all four calls, "Long" only the long pair, "Short" only the short pair. Only one
`if` branch executes, exactly as in Pine.

The Borserman EMA is NOT `ta.ema`. Its running value starts from ZERO state
(`sum = 0.0`, then `nz(sum[1])` on the first bar gives 0), so bar 0 holds
`alpha * x[0]` rather than `x[0]`. A `ta.ema` seeded with the first observation
(what `pine_ta.pine_ema` does) differs from it by `(1 - alpha)^t * x[0]`, which
with alpha = 2/181 decays with a half-life of ~63 bars -- hundreds of bars before
the two agree. The recursion is therefore transcribed literally, with the
source's own initial state, rather than delegated to `pine_ta`.

`strategy()` in the source is COMMENTED OUT, and it is the only declaration of
execution properties in the file:

    //strategy(
    //  title="EHMA Range Strategy",
    //  process_orders_on_close=true,
    //  explicit_plot_zorder=true,
    //  overlay=true,
    //  initial_capital=1500,
    //  default_qty_type=strategy.percent_of_equity,
    //  commission_type=strategy.commission.percent,
    //  commission_value=0.085,
    //  default_qty_value=100
    //  )

Commented code places no declaration, so it is read the same way the commented
exit line in a sibling source is read: as absent. Pine's documented defaults
therefore apply -- fixed sizing, qty 1, initial capital 1000000, commission 0%,
`pyramiding=0`, `process_orders_on_close=false`. Note the consequence that is
NOT adopted here: had the commented block been taken as authoritative it would
also have brought `process_orders_on_close=true`, i.e. same-bar fills, which the
shared engine does not model (it fills market orders at the next bar's open).
The commented values are recorded verbatim in `source_fidelity_notes` so the
choice is visible rather than silent.

FIDELITY:

* `time_cond = true` is a literal; the two `startDate` / `finishDate` inputs
  above it are commented out and place no date filter. The port applies none.
* `strategy.entry(...)` / `strategy.close(...)` pass no `qty`, so both are
  sized by `default_qty_type` / `default_qty_value`.
* The four calls are made in the source's written order -- entry Long, close
  Long, entry Short, close Short -- because that order is the fill priority in
  the engine.
* `long == exit_short` and `short == exit_long` are the SAME expressions in the
  source (`close > upper` and `close < lower`), so on a long bar the closing
  `strategy.close("Short")` is placed right after the reversing long entry. The
  engine nets the reversal first and finds no "Short" entry left to close,
  matching Pine's `strategy.close(id)` being a no-op for an entry that is gone.
* `plot(...)`, `EHMAcolor` and `overlay` are display-only.
* Pine's `nz(sum[1])` on the first bar is modelled as initial state 0.
* Leverage, margin, liquidation and funding are not modelled, and the venue's
  contract-step rounding is not modelled either (the chain verifier measures
  that separately rather than treating it as a signal difference).
"""
import numpy as np
import pandas as pd

from freqtrade.strategy import IStrategy

from pine_port_base import PinePortBase


def _borserman_ema(values: np.ndarray, y: float) -> np.ndarray:
    """Pine `borserman_ema`: alpha = 2/(y+1), running from ZERO state.

    `sum = 0.0` then `sum := alpha * x + (1 - alpha) * nz(sum[1])` means the
    first bar evaluates as `alpha * x[0]` -- `nz` turns the missing `sum[1]`
    into 0 -- so the recursion starts from 0, not from the first observation.
    """
    alpha = 2.0 / (y + 1.0)
    out = np.empty(len(values), dtype=float)
    state = 0.0
    for i, value in enumerate(values):
        # nz(sum[1]): an na observation leaves the run at zero contribution.
        state = alpha * float(value) + (1.0 - alpha) * state
        out[i] = state
    return out


class SMEhmaRangeStrategy_c5708b(PinePortBase, IStrategy):
    source_id = "SM_c5708b1444e81f60"
    source_file = "EHMA-Range-Strategy.md"
    timeframe = "1d"
    can_short = True
    # Pine evaluates the script from the first bar; the recursion has no warmup.
    startup_candle_count = 0
    source_defaults: dict = {"pos_type": "Both", "Period": 180, "RangeWidth": 0.02}
    # `//strategy(...)` is commented out; Pine's documented defaults apply.
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    # The source's only exits are `strategy.close(...)` calls, which reach the
    # framework as next-open signals; there is no stop/limit/trail leg to mirror.
    source_reproduce_stops = False
    source_fidelity_notes = [
        "The `strategy(...)` call is COMMENTED OUT and is the file's only "
        "declaration of execution properties. It is not adopted -- commented "
        "code places no declaration -- so Pine's documented defaults apply: "
        "fixed sizing, qty 1, initial capital 1000000, commission 0%, "
        "pyramiding 0, process_orders_on_close=false. Recorded, not silently "
        "replaced. The commented values were: title='EHMA Range Strategy', "
        "process_orders_on_close=true, initial_capital=1500, "
        "default_qty_type=strategy.percent_of_equity, commission_type="
        "strategy.commission.percent, commission_value=0.085, "
        "default_qty_value=100. Had they been adopted, "
        "process_orders_on_close=true would additionally be a Pine behaviour "
        "this engine does not model (it fills market orders at the next bar's "
        "open, never at the signal bar's close).",
        "`borserman_ema` is NOT ta.ema: it runs from zero initial state "
        "(`sum = 0.0`, then `nz(sum[1])` = 0 on the first bar), so bar 0 holds "
        "alpha*x[0] instead of x[0]. Transcribed literally rather than "
        "delegated to pine_ta.pine_ema, whose seed is the first observation; "
        "the two differ by (1-alpha)^t * x[0], which with alpha = 2/181 has a "
        "half-life of ~63 bars and so is not a one-bar edge effect.",
        "`Period / 2` is Pine integer division (Period defaults to the integer "
        "180, so this is 90 and the choice is invisible at the default); the "
        "port truncates with `Period // 2` for integer-valued Period and "
        "divides as float otherwise, matching Pine's int/int rule.",
        "`time_cond = true` is a literal and the `startDate` / `finishDate` "
        "inputs above it are commented out, so no date filter is applied.",
        "long == exit_short and short == exit_long are literally the same "
        "expressions, so the written order -- entry Long, close Long, entry "
        "Short, close Short -- decides the order of calls and is preserved.",
        "No stop, limit, target or trailing exit exists: positions end only at "
        "the opposite band crossing, via strategy.close, so "
        "source_reproduce_stops is False.",
        "`plot()`, `EHMAcolor` and `overlay` are display-only and are not "
        "reproduced.",
        "Leverage, margin, liquidation and funding are not modelled; the "
        "venue's contract-step rounding is not modelled either.",
    ]

    def pine_indicators(self, dataframe: pd.DataFrame, params: dict) -> pd.DataFrame:
        period = float(params["Period"])
        range_width = float(params["RangeWidth"])
        close = dataframe["close"].to_numpy(dtype=float)

        # alpha = 2 / (y + 1) for each of the three call sites.
        half = period // 2 if float(period).is_integer() else period / 2.0
        sqrt_period = float(np.sqrt(period))

        inner = (
            2.0 * _borserman_ema(close, half)
            - _borserman_ema(close, period)
        )
        ehma = _borserman_ema(inner, sqrt_period)
        upper = ehma + ehma * range_width
        lower = ehma - ehma * range_width

        dataframe["pine_ehma"] = ehma
        dataframe["pine_ehma_upper"] = upper
        dataframe["pine_ehma_lower"] = lower
        close_series = dataframe["close"]
        dataframe["pine_long"] = (close_series > pd.Series(upper, index=dataframe.index))
        dataframe["pine_exit_long"] = (close_series < pd.Series(lower, index=dataframe.index))
        dataframe["pine_short"] = dataframe["pine_exit_long"]
        dataframe["pine_exit_short"] = dataframe["pine_long"]
        return dataframe

    def pine_context(self, dataframe: pd.DataFrame, params: dict) -> dict:
        return {
            "pos_type": str(params["pos_type"]),
            "long": dataframe["pine_long"].to_numpy(),
            "exit_long": dataframe["pine_exit_long"].to_numpy(),
            "short": dataframe["pine_short"].to_numpy(),
            "exit_short": dataframe["pine_exit_short"].to_numpy(),
        }

    def pine_script(self, broker, i: int, ctx: dict) -> None:
        # time_cond = true
        time_cond = True
        pos_type = ctx["pos_type"]
        # if pos_type == "Both"
        #     strategy.entry("Long", strategy.long, comment="Long", when=long and time_cond)
        #     strategy.close("Long", comment="Exit Long", when=exit_long and time_cond)
        #     strategy.entry("Short", strategy.short, comment="Short", when=short and time_cond)
        #     strategy.close("Short", comment="Exit Short", when=exit_short and time_cond)
        if pos_type == "Both":
            broker.entry("Long", "long", when=bool(ctx["long"][i]) and time_cond)
            broker.close("Long", when=bool(ctx["exit_long"][i]) and time_cond)
            broker.entry("Short", "short", when=bool(ctx["short"][i]) and time_cond)
            broker.close("Short", when=bool(ctx["exit_short"][i]) and time_cond)
        # if pos_type == "Long"
        #     strategy.entry("Long", strategy.long, comment="Long", when=long and time_cond)
        #     strategy.close("Long", comment="Exit Long", when=exit_long and time_cond)
        if pos_type == "Long":
            broker.entry("Long", "long", when=bool(ctx["long"][i]) and time_cond)
            broker.close("Long", when=bool(ctx["exit_long"][i]) and time_cond)
        # if pos_type == "Short"
        #     strategy.entry("Short", strategy.short, comment="Short", when=short and time_cond)
        #     strategy.close("Short", comment="Exit Short", when=exit_short and time_cond)
        if pos_type == "Short":
            broker.entry("Short", "short", when=bool(ctx["short"][i]) and time_cond)
            broker.close("Short", when=bool(ctx["exit_short"][i]) and time_cond)
