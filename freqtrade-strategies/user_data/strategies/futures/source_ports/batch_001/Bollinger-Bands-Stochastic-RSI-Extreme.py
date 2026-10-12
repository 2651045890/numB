"""Port of sources/SM_a16666a9e5ad11e1.pine
(batch_001/Bollinger-Bands-Stochastic-RSI-Extreme.md).

Pine v4 (`//@version=4`, `study(...)`), 15m. The file declares an INDICATOR, not
a strategy:

    study(shorttitle="BBSR Extreme",
          title="Bollinger Bands Stochastic RSI Extreme Signal",
          overlay=true, resolution="")

and a conversion tool has appended an order block after it
(PINE_SEMANTICS.md 1.17):

    if Bear
        strategy.entry("Enter Long", strategy.long)
    else if Bull
        strategy.entry("Enter Short", strategy.short)

`strategy.entry` cannot compile inside a v4 `study()`, so the "original strategy"
IS the indicator plus that appended block, and its trading behaviour is exactly
what the block does: open a position when one of the two conditions holds, and
NEVER exit. The file contains no `strategy.close`, no `strategy.exit` and not
even a commented-out exit line, so `source_reproduce_stops` is False and a
position is only ever ended by the opposite entry reversing it.

The indicator, transcribed:

    basis = sma(close, 20)
    dev   = 2.0 * stdev(close, 20)
    upper = basis + dev ;  lower = basis - dev
    rsi1  = rsi(close, 14)
    k     = sma(stoch(rsi1, rsi1, rsi1, 14), 3)
    d     = sma(k, 3)
    stoch(source, high, low, len) = 100 * (source - lowest(low, len))
                                        / (highest(high, len) - lowest(low, len))
    Bear = close[1] > upper[1] and close < upper
           and k[1] > 90 and d[1] > 90
    Bull = close[1] < lower[1] and close > lower
           and k[1] < 10 and d[1] < 10

THE POLARITY IS THE SOURCE'S, NOT THE NAME'S: `Bear` -- price closing back INSIDE
the upper band after closing above it, with the smoothed stochastic above 90 --
is the LONG arm, and `Bull` (the mirror at the lower band, stochastic below 10)
is the SHORT arm. The md's prose attaches those band patterns to the opposite
labels; the source is the authority (iron rule 2) and the port follows it.

`strategy()` is never declared, so every strategy property is Pine's documented
default: `fixed` sizing of 1 contract, initial capital 1000000, commission 0%,
`pyramiding = 0`, `process_orders_on_close = false`. With `pyramiding = 0` a
same-direction entry placed while that direction is already open is ignored
outright by the engine, so a run holds at most one position.

FIDELITY -- translation choices and source/md mismatches:

1. MD/SOURCE MISMATCH (labels): the md's "Strategy Description" lists the
   upper-band pattern under "( Bullish )" and the lower-band pattern under
   "( Bearish )". The source is the inverse -- `Bear` (upper band) drives
   `strategy.entry("Enter Long", ...)` and `Bull` (lower band) drives
   `strategy.entry("Enter Short", ...)`. The port follows the source.
2. MD/SOURCE MISMATCH (thresholds): the md's "( Bullish )" bullet says the RSI
   stochastic must be "below the set threshold (10 by default)" while the same
   bullet describes the upper-band pattern. In the source the upper-band (`Bear`)
   arm requires `k[1] > 90` AND `d[1] > 90`, and the lower-band (`Bull`) arm
   requires `k[1] < 10` AND `d[1] < 10`.
3. MD/SOURCE MISMATCH (which bar): the md says "A candle closes above the upper
   Bollinger Band / The following candle closes within the upper Bollinger
   Band". The source compares `close[1] > upper[1]` against the CURRENT bar's
   `close < upper`, i.e. a single-bar filter on the two most recent closes, and
   the stochastic thresholds are also read at `[1]`.
4. MD/SOURCE MISMATCH (indicator granularity): the md calls it "the RSI
   Stochastic"; the source gates on the smoothed stochastic of the RSI -- BOTH
   `k` (sma of stoch, 3) and `d` (sma of k, 3) -- at `[1]`.
5. MD/SOURCE MISMATCH (argument table): the md renders `v_input_2` ("Offset") as
   `false` and `v_input_4` ("StdDev") as `2`; the source declares `input(0, ...)`
   and `input(2.0, ...)`. The source's values are used.
6. `stdev` is the POPULATION standard deviation (ddof = 0) in both v4 and v5;
   `pine_ta.pine_stdev` implements exactly that. Using a sample (ddof = 1)
   stdev here would widen both bands slightly.
7. `stoch(rsi1, rsi1, rsi1, 14)` uses the same RSI series for source, high and
   low, so `highest` / `lowest` run over `rsi1`. Both return na until 14 bars
   have elapsed, and the window's division is a float division by zero --
   na in Pine -- whenever `highest == lowest`, which pandas gives as 0/0 = NaN.
8. `sma` / `highest` / `lowest` propagate na inside their window and return na
   until the window is full (pine_ta's model of them, PINE_SEMANTICS.md 3.2);
   the first `k` therefore needs 14 (stoch) + 3 (k) bars and the first `d` 14 +
   3 + 3 bars.
9. `rsi(src, 14)` -> `pine_ta.pine_rsi`, whose boundary conventions (100 with no
   losses, na until the averages form) are PINE_SEMANTICS.md 3.3, unverified
   against the original platform bar by bar.
10. `offset` and the `input.source` (`src`) are declared inputs; `offset` only
    shifts the three `plot(...)` calls and `src` feeds `basis`/`dev`/`rsi1` (the
    band comparison itself is on `close`, as in the source). The `offset` value
    therefore has no effect on any order and is carried in `source_defaults` for
    provenance only.
11. `plot`, `plotshape`, `fill`, `alertcondition`, the `study` title/shorttitle
    and `resolution=""` are display-only and are not reproduced; the series the
    entry test reads are kept as columns.
12. No `request.security()`, no `barstate.isrealtime` branch, no repainting:
    every value the signals read is either the current bar's or an earlier one's.
13. The `/*backtest` header declares `period: 15m` on Futures_Binance BTC_USDT,
    hence `timeframe = "15m"`; its `basePeriod: 5m` is the FMZ backtester's own
    intrabar fill granularity, not the strategy's period.
14. Leverage, margin, liquidation, funding and the venue's contract-step
    rounding of order quantities are not modelled (PINE_SEMANTICS.md section 2);
    the chain verifier measures the step rounding separately.
"""
import numpy as np

from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


class SMBollingerBandsStochasticRsiExtreme_a16666(PinePortBase, IStrategy):
    source_id = "SM_a16666a9e5ad11e1"
    source_file = "Bollinger-Bands-Stochastic-RSI-Extreme.md"
    timeframe = "15m"
    # The appended block has both arms: entry("Enter Long") and
    # entry("Enter Short").
    can_short = True
    source_defaults: dict = {
        # src = input(close, title="Source")
        "src": "close",
        # offset = input(0, "Offset", type=input.integer, minval=-500, maxval=500)
        "offset": 0,
        # length = input(20, title="Bollinger Band Length", minval=1)
        "length": 20,
        # mult = input(2.0, minval=0.001, maxval=50, title="StdDev")
        "mult": 2.0,
        # smoothK = input(3, "K", minval=1)
        "smoothK": 3,
        # smoothD = input(3, "D", minval=1)
        "smoothD": 3,
        # lengthRSI = input(14, "RSI Length", minval=1)
        "lengthRSI": 14,
        # lengthStoch = input(14, "Stochastic Length", minval=1)
        "lengthStoch": 14,
        # upperlimit = input(90, "Upper Limit", minval=0.01)
        "upperlimit": 90,
        # lowerlimit = input(10, "Upper Limit", minval=0.01)
        "lowerlimit": 10,
    }
    # No `strategy()` call exists in the source, so Pine's documented defaults
    # apply: `fixed` / 1 contract, initial capital 1000000, commission 0%,
    # pyramiding 0, process_orders_on_close = false.
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    # No stop / limit / trail leg exists: the file has no exit call of any kind.
    source_reproduce_stops = False
    source_fidelity_notes = [
        "The source is a Pine v4 `study()` (indicator), not a strategy: the "
        "trailing `if Bear / else if Bull` order pair is the conversion tool's "
        "appended block (PINE_SEMANTICS.md 1.17). `strategy.entry` cannot "
        "compile inside study(), so the original strategy IS the indicator plus "
        "that block -- read from the source, not from the author's intent.",
        "NO EXIT CALL EXISTS: no strategy.close, no strategy.exit, no commented-"
        "out exit line. The behaviour reproduced is 'open on the condition, "
        "never exit'; a position is only ended by the opposite entry reversing "
        "it, and one still open at the end of the window stays open.",
        "source_reproduce_stops is False because no stop/limit/trail leg exists.",
        "No `? -1 : 0` construct is present: both arms are genuine booleans, so "
        "the integer-truthiness trap of PINE_SEMANTICS.md 1.17 does not apply. "
        "The source's if / else-if order (Bear first) is preserved in "
        "pine_script.",
        "MD/SOURCE MISMATCH: the md's (Bullish) bullet describes the upper-band "
        "pattern and a stochastic below 10; the source's upper-band condition "
        "`Bear` requires k[1] > 90 and d[1] > 90 and drives the LONG entry. The "
        "source is followed.",
        "MD/SOURCE MISMATCH: the md says the pattern is 'a candle closes above "
        "the band, the FOLLOWING candle closes within it'; the source compares "
        "close[1] against upper[1]/lower[1] and the current close against the "
        "current band, and reads k and d at [1] too.",
        "MD/SOURCE MISMATCH: the md's argument table renders Offset as `false` "
        "and StdDev as `2`; the source declares input(0) and input(2.0).",
        "The md names the gate 'the RSI Stochastic'; the source gates on BOTH "
        "the smoothed stochastic K and its 3-period SMA, D, at [1].",
        "stdev is the population standard deviation (ddof=0), which is what "
        "pine_ta.pine_stdev computes (PINE_SEMANTICS.md 3.2 family).",
        "stoch(rsi1, rsi1, rsi1, 14) uses the RSI series for source, high and "
        "low, so highest/lowest run over rsi1; highest == lowest makes the "
        "window a float division by zero, which is na in Pine and 0/0 = NaN in "
        "pandas.",
        "sma / highest / lowest return na until their window is full and "
        "propagate na inside it (pine_ta's model, PINE_SEMANTICS.md 3.2), so d "
        "first exists on bar 19 and the first possible signal is later.",
        "rsi boundary behaviour (100 when there were no losses, na before the "
        "averages form) is pine_ta's modelled choice, PINE_SEMANTICS.md 3.3.",
        "The `offset` input only shifts the three plot() calls and is carried "
        "in source_defaults for provenance; it enters no order.",
        "plot / plotshape / fill / alertcondition / the study title and "
        "resolution are display-only and are not reproduced.",
        "No security() call, no barstate.isrealtime branch, no repainting.",
        "/*backtest declares period: 15m on Futures_Binance BTC_USDT; "
        "basePeriod: 5m is the FMZ backtester's fill granularity, not the "
        "strategy's period.",
        "Leverage, margin, liquidation, funding and the venue's contract-step "
        "rounding are not modelled (PINE_SEMANTICS.md section 2).",
    ]

    def pine_indicators(self, dataframe, params):
        # `src` feeds the band basis, the deviation and the RSI; the band
        # COMPARISON (`close` vs `upper` / `lower`) is against `close` in the
        # source and stays against close here.
        src = ta.pine_source(dataframe, params["src"])
        close = dataframe["close"]

        # basis = sma(src, length) ; dev = mult * stdev(src, length)
        length = int(params["length"])
        mult = float(params["mult"])
        basis = ta.pine_sma(src, length)
        dev = mult * ta.pine_stdev(src, length)
        # upper = basis + dev ; lower = basis - dev
        upper = basis + dev
        lower = basis - dev

        # rsi1 = rsi(src, lengthRSI)
        rsi1 = ta.pine_rsi(src, int(params["lengthRSI"]))
        # k = sma(stoch(rsi1, rsi1, rsi1, lengthStoch), smoothK)
        stoch_length = int(params["lengthStoch"])
        lowest = ta.pine_lowest(rsi1, stoch_length)
        highest = ta.pine_highest(rsi1, stoch_length)
        with np.errstate(divide="ignore", invalid="ignore"):
            stoch = 100.0 * (rsi1 - lowest) / (highest - lowest)
        k = ta.pine_sma(stoch, int(params["smoothK"]))
        # d = sma(k, smoothD)
        d = ta.pine_sma(k, int(params["smoothD"]))

        upper_limit = float(params["upperlimit"])
        lower_limit = float(params["lowerlimit"])

        # Bear = close[1] > upper[1] and close < upper
        #        and k[1] > upperlimit and d[1] > upperlimit
        # An na operand makes a Pine `and` falsy; a pandas comparison against
        # NaN is likewise False, so the conjunction needs no special-casing.
        bear = (
            (close.shift(1) > upper.shift(1))
            & (close < upper)
            & (k.shift(1) > upper_limit)
            & (d.shift(1) > upper_limit)
        )
        # Bull = close[1] < lower[1] and close > lower
        #        and k[1] < lowerlimit and d[1] < lowerlimit
        bull = (
            (close.shift(1) < lower.shift(1))
            & (close > lower)
            & (k.shift(1) < lower_limit)
            & (d.shift(1) < lower_limit)
        )

        dataframe["pine_basis"] = basis
        dataframe["pine_upper"] = upper
        dataframe["pine_lower"] = lower
        dataframe["pine_rsi"] = rsi1
        dataframe["pine_k"] = k
        dataframe["pine_d"] = d
        dataframe["pine_bear"] = bear.fillna(False).astype(bool)
        dataframe["pine_bull"] = bull.fillna(False).astype(bool)
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "bear": dataframe["pine_bear"].to_numpy(dtype=bool),
            "bull": dataframe["pine_bull"].to_numpy(dtype=bool),
        }

    def pine_script(self, broker, i, ctx):
        # if Bear
        #     strategy.entry("Enter Long", strategy.long)
        # else if Bull
        #     strategy.entry("Enter Short", strategy.short)
        if ctx["bear"][i]:
            broker.entry("Enter Long", "long")
        elif ctx["bull"][i]:
            broker.entry("Enter Short", "short")
