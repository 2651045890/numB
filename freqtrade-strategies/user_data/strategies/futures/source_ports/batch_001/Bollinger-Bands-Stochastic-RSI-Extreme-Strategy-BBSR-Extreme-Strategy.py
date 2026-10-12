"""Port of sources/SM_44cd883bd2ef5e10.pine
(batch_001/Bollinger-Bands-Stochastic-RSI-Extreme-Strategy-BBSR-Extreme-Strategy.md).

Pine v5, "BBSR Extreme Strategy [nachodog]". Bollinger bands decide that price
has poked outside a band and come back in; a Stochastic RSI built on top of the
RSI decides that momentum was at an extreme on the PREVIOUS bar:

    basis = ta.sma(src, length)
    dev   = mult * ta.stdev(src, length)
    upper = basis + dev ; lower = basis - dev

    rsi1 = ta.rsi(src, lengthRSI)
    k    = ta.sma(ta.stoch(rsi1, rsi1, rsi1, lengthStoch), smoothK)
    d    = ta.sma(k, smoothD)

    Bear = close[1] > upper[1] and close < upper and k[1] > upperlimit and d[1] > upperlimit
    Bull = close[1] < lower[1] and close > lower and k[1] < lowerlimit and d[1] < lowerlimit

    if (Bull) strategy.entry("Bull Entry", strategy.long)
    if (Bear) strategy.entry("Bear Entry", strategy.short)

    strategy.exit("Exit Long",  from_entry="Bull Entry", stop=close*(1-sl_pct/100), when=Bear or close<lower)
    strategy.exit("Exit Short", from_entry="Bear Entry", stop=close*(1+sl_pct/100), when=Bull or close>upper)

`strategy()` declares only title/shorttitle/overlay, so Pine's documented
defaults are in force and carried here: fixed / 1 contract / initial_capital
1000000 / commission 0% / pyramiding 0 / process_orders_on_close false.

The `/*backtest` header declares `period: 1h` on Futures_Binance BTC_USDT;
its `basePeriod: 15m` is the FMZ backtester's own fill granularity, not the
strategy's period, so `timeframe` is "1h".

FIDELITY:

* `ta.stoch(rsi1, rsi1, rsi1, lengthStoch)` passes the SAME series as high, low
  and close, so under Pine's definition
  `stoch = 100 * (source - lowest(low, n)) / (highest(high, n) - lowest(low, n))`
  it collapses to `100 * (rsi1 - lowest(rsi1, n)) / (highest(rsi1, n) - lowest(rsi1, n))`.
  That identity is written out explicitly in `pine_indicators`; it is NOT a
  substitute library call.
* Pine returns na for the 0/0 division when the RSI window is flat
  (highest == lowest); the port masks that case to NaN so the comparisons stay
  false instead of becoming true on an inf. A modelling choice, not a
  documented rule.
* `ta.sma` propagates na through its window and returns na until the window is
  full, which is what pine_ta.pine_sma does; k and d therefore need
  lengthStoch + smoothK (and + smoothD) RSI bars.
* The `stop=` level is evaluated every bar as `close * (1 -/+ sl_pct/100)` --
  a percentage of the CURRENT bar's close, not a fixed entry-relative level.
  Because the two exit calls sit at the top level (not inside `if`), the stop
  is re-placed on EVERY bar, so while a position lives it trails the close. The
  port reproduces that by calling broker.exit unconditionally with the `when=`
  flag the source uses, which is also what makes the exit legs get replaced by
  id in the engine.
* `when=Bear or close < lower` (long) / `when=Bull or close > upper` (short) is
  kept verbatim, including the fact that the long exit's `stop=` is still the
  long stop on bars where the exit is gated off.
* `offset` is an input used only for the `plot(..., offset=offset)` calls; it
  never enters the arithmetic or a condition. It is still exposed as a
  parameter so an override does not silently vanish. Recorded, not applied.
* MD/SOURCE MISMATCH (rendered default): the md argument table renders
  `v_input_int_1` (Offset) as `false`; the source declares `input.int(0, ...)`.
  The source's 0 is carried.
* MD/SOURCE NOTE: the md prose describes the exits as "reverse or exit"; the
  source only ever exits (no reversal is placed by the exit block). The source
  is followed -- a reversal happens only if the opposite entry condition fires.
* Leverage, margin, liquidation and funding are not modelled, and neither is
  the venue's contract-step rounding (measured separately by the chain
  verifier).
"""
import numpy as np
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


class SMBbsrExtreme_44cd88(PinePortBase, IStrategy):
    source_id = "SM_44cd883bd2ef5e10"
    source_file = "Bollinger-Bands-Stochastic-RSI-Extreme-Strategy-BBSR-Extreme-Strategy.md"
    timeframe = "1h"
    can_short = True
    source_defaults: dict = {
        "src": "close",
        "offset": 0,
        "sl_pct": 1.5,
        "length": 20,
        "mult": 2.0,
        "smoothK": 3,
        "smoothD": 3,
        "lengthRSI": 14,
        "lengthStoch": 14,
        "upperlimit": 90.0,
        "lowerlimit": 10.0,
    }
    # strategy(title/shorttitle/overlay) only: Pine defaults.
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    source_reproduce_stops = True
    source_fidelity_notes = [
        "ta.stoch(rsi1, rsi1, rsi1, lengthStoch) collapses to "
        "100*(rsi1 - lowest(rsi1,n)) / (highest(rsi1,n) - lowest(rsi1,n)); the "
        "formula is written out rather than calling a substitute.",
        "The 0/0 case (flat RSI window) is na in Pine and masked to NaN here so "
        "the comparisons stay false; a modelling choice, not a documented rule.",
        "The stop is recomputed every bar from the CURRENT close and re-placed "
        "every bar (the exit calls are at top level), so it trails the close "
        "while a position lives.",
        "when=Bear or close<lower / Bull or close>upper kept verbatim, "
        "including the stop= still being passed on gated-off bars.",
        "`offset` is a plot-only input and is recorded, not applied.",
        "MD/SOURCE MISMATCH: the md argument table renders the Offset default "
        "as `false`; the source says input.int(0). Source followed.",
        "MD/SOURCE NOTE: the md prose says the exits 'reverse'; the source's "
        "exit block only exits. A reversal only happens via the opposite entry.",
        "Pine's strategy() declares no sizing/cost properties here, so fixed / "
        "1 contract / 1000000 / 0% / pyramiding 0 are in force and "
        "process_orders_on_close is false.",
        "The /*backtest header's period: 1h sets the timeframe; its "
        "basePeriod: 15m is the FMZ fill granularity, not the strategy period.",
        "Leverage, margin, liquidation, funding and contract-step rounding are "
        "not modelled.",
    ]

    def pine_indicators(self, dataframe, params):
        src = ta.pine_source(dataframe, str(params["src"]))
        length = int(params["length"])
        mult = float(params["mult"])
        smooth_k = int(params["smoothK"])
        smooth_d = int(params["smoothD"])
        length_rsi = int(params["lengthRSI"])
        length_stoch = int(params["lengthStoch"])
        upper_limit = float(params["upperlimit"])
        lower_limit = float(params["lowerlimit"])
        sl_pct = float(params["sl_pct"])

        # basis = ta.sma(src, length) ; dev = mult * ta.stdev(src, length)
        basis = ta.pine_sma(src, length)
        dev = mult * ta.pine_stdev(src, length)
        upper = basis + dev
        lower = basis - dev

        # rsi1 = ta.rsi(src, lengthRSI)
        rsi1 = ta.pine_rsi(src, length_rsi)
        # k = ta.sma(ta.stoch(rsi1, rsi1, rsi1, lengthStoch), smoothK)
        # ta.stoch(high=rsi1, low=rsi1, close=rsi1, n) with Pine's definition
        #   100 * (source - lowest(low, n)) / (highest(high, n) - lowest(low, n))
        lowest_rsi = ta.pine_lowest(rsi1, length_stoch)
        highest_rsi = ta.pine_highest(rsi1, length_stoch)
        span = highest_rsi - lowest_rsi
        with np.errstate(divide="ignore", invalid="ignore"):
            stoch = 100.0 * (rsi1 - lowest_rsi) / span
        # Pine: a 0/0 division is na.
        stoch = stoch.where(span != 0.0)
        k = ta.pine_sma(stoch, smooth_k)
        d = ta.pine_sma(k, smooth_d)

        close = dataframe["close"]
        # Bear = close[1] > upper[1] and close < upper and k[1] > upperlimit and d[1] > upperlimit
        bear = (
            (close.shift(1) > upper.shift(1))
            & (close < upper)
            & (k.shift(1) > upper_limit)
            & (d.shift(1) > upper_limit)
        )
        # Bull = close[1] < lower[1] and close > lower and k[1] < lowerlimit and d[1] < lowerlimit
        bull = (
            (close.shift(1) < lower.shift(1))
            & (close > lower)
            & (k.shift(1) < lower_limit)
            & (d.shift(1) < lower_limit)
        )

        dataframe["pine_bb_upper"] = upper
        dataframe["pine_bb_lower"] = lower
        dataframe["pine_stoch_k"] = k
        dataframe["pine_stoch_d"] = d
        dataframe["pine_bull"] = bull.fillna(False)
        dataframe["pine_bear"] = bear.fillna(False)
        # strategy.exit("Exit Long",  ..., stop=close * (1 - sl_pct / 100), when=Bear or close < lower)
        dataframe["pine_exit_long_stop"] = close * (1.0 - sl_pct / 100.0)
        # strategy.exit("Exit Short", ..., stop=close * (1 + sl_pct / 100), when=Bull or close > upper)
        dataframe["pine_exit_short_stop"] = close * (1.0 + sl_pct / 100.0)
        dataframe["pine_exit_long_when"] = (bear | (close < lower)).fillna(False)
        dataframe["pine_exit_short_when"] = (bull | (close > upper)).fillna(False)
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "bull": dataframe["pine_bull"].to_numpy(),
            "bear": dataframe["pine_bear"].to_numpy(),
            "exit_long_stop": dataframe["pine_exit_long_stop"].to_numpy(),
            "exit_short_stop": dataframe["pine_exit_short_stop"].to_numpy(),
            "exit_long_when": dataframe["pine_exit_long_when"].to_numpy(),
            "exit_short_when": dataframe["pine_exit_short_when"].to_numpy(),
        }

    def pine_script(self, broker, i, ctx):
        # if (Bull) strategy.entry("Bull Entry", strategy.long)
        if ctx["bull"][i]:
            broker.entry("Bull Entry", "long")

        # if (Bear) strategy.entry("Bear Entry", strategy.short)
        if ctx["bear"][i]:
            broker.entry("Bear Entry", "short")

        # strategy.exit("Exit Long", from_entry="Bull Entry",
        #               stop=close * (1 - sl_pct / 100), when=Bear or close < lower)
        broker.exit(
            "Exit Long",
            "Bull Entry",
            when=bool(ctx["exit_long_when"][i]),
            stop=float(ctx["exit_long_stop"][i]),
        )

        # strategy.exit("Exit Short", from_entry="Bear Entry",
        #               stop=close * (1 + sl_pct / 100), when=Bull or close > upper)
        broker.exit(
            "Exit Short",
            "Bear Entry",
            when=bool(ctx["exit_short_when"][i]),
            stop=float(ctx["exit_short_stop"][i]),
        )
