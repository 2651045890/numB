"""Port of sources/SM_200d9bbcebcdc2e0.pine (batch_001/AMACD-All-Moving-Average-Convergence-Divergence.md).

Pine v5. EltAlt's AMACD is an INDICATOR -- `indicator(title='AMACD - All Moving
Average Convergence Divergence', overlay=false, ...)` -- that rebuilds MACD out
of any chosen moving-average family for each of its three legs:

    MA_fast = calcMA(FastType, FastSource, FastLength)      // EMA, 12, close
    MA_slow = calcMA(SlowType, SlowSource, SlowLength)      // SMA, 26, close
    macd    = MA_fast - MA_slow
    signal  = SignalLength > 1 ? calcMA(SignalType, macd, SignalLength) : 0   // SMA, 9
    hist    = macd - signal
    histMA  = calcMA(MAHistType, hist, MAHistLength)        // EMA, 5

    longSignal  = ta.crossover(hist, 0)
    shortSignal = ta.crossunder(hist, 0)
    MACrossUpZero   = ta.crossover(macd, 0)
    MACrossDownZero = ta.crossover(macd, 0)     // source: crossover, not crossunder
    longHistMA  = histMA > histMA[1]
    shortHistMA = histMA < histMA[1]
    risingHist  = ta.rising (hist, risingHistLength)  and (hist < 0 or not backtestBuyRisingHistBelow)
    fallingHist = ta.falling(hist, fallingHistLength) and (hist > 0 or not backtestSellRisingHistAbove)

    bool openLong / closeLong / openShort / closeShort
    var int dealstate = 0
    if (... buy conditions ...)
        if (dealstate[1] == -1) and generateClose
            closeShort := true
            dealstate := 0
        else
            openLong := true
            dealstate := 1
    if (... sell conditions ...)
        if (dealstate[1] == 1) and generateClose
            closeLong := true
            dealstate := 0
        else
            openShort := true
            dealstate := -1

A converter then appended the order block at the end of the file -- and, unlike
most sources in this family, the block carries LIVE exits:

    if openLong and longOpenSignal
        strategy.entry("Enter Long", strategy.long)
    else if openShort and shortOpenSignal
        strategy.entry("Enter Short", strategy.short)

    strategy.close("Enter Long",when=(closeLong and longCloseSignal),comment="Long_OK")
    strategy.close("Enter Short",when=(closeShort and shortCloseSignal),comment="Short_OK")

Both `strategy.close` calls are executable (they are NOT commented out), so this
port has real exits and the tier note that says "NO exits" does not hold for
this item. They are market closes, which the engine's signal projection can
represent, so `source_reproduce_stops` stays False (there is no stop / limit /
trail leg anywhere in the file).

The trading state machine is reproduced literally:

* `dealstate[1]` is the value at the END of the PREVIOUS bar. Both blocks read
  it, so the sell block still sees the old value even when the buy block has
  already rewritten `dealstate` on the same bar. The port snapshots it at the
  top of each bar, exactly as Pine's history reference does. On bar 0
  `dealstate[1]` is na, and `na == -1` / `na == 1` are false in Pine; the port's
  seed of 0 gives the same branch, since 0 equals neither.
* Both blocks can fire on the same bar (with `dealstate[1] == 0` they both take
  their `else` arms, and with `dealstate[1] == 1` the buy block opens a long
  while the sell block closes one). The emitted orders therefore need the
  source's own order: both entries first, then both closes -- and the
  `else if` precedence between the two entries.
* `longOpenSignal = 1`, `shortOpenSignal = -1`, `longCloseSignal = 2`,
  `shortCloseSignal = -2` are integers used as bare conditions
  (`openLong and longOpenSignal`). This is the PINE_SEMANTICS.md 1.17 family:
  a non-zero number is TRUE, in Pine AND in Python, so the port tests them for
  non-zero and does NOT normalise them into `== 1` / `> 0`. `-1` stays `-1`
  (see `minus_truthiness` in the notes).
* `MACrossDownZero = ta.crossover(macd, 0)` is a source bug: the "down" test is
  a second crossover. It is preserved as written; both of those inputs default
  to `false`, so it changes nothing under the declared defaults.

FIDELITY:

* `indicator()` declares no strategy properties, so Pine's documented defaults
  apply: `default_qty_type` fixed, 1 unit, 1000000 initial capital, 0%
  commission, pyramiding 0, `process_orders_on_close` false.
* `calcMA` is the source's own `switch`, transcribed type for type. Under the
  declared defaults only two branches are ever evaluated -- `'EMA'` (FastType,
  MAHistType) and `'SMA'` (SlowType, SignalType). The port supports
  EMA / SMA / WMA / VWMA / HMA / RMA / LSMA / Double-* / Triple-* / SWMA and
  RAISES for ALMA / VIDYA / FRAMA, whose definitions the source does not pin
  down well enough to reproduce (see the notes and the blockers).
* `ta.rising` / `ta.falling` are not in pine_ta. They are implemented from
  Pine's documented reading ("rising for `length` bars long", i.e. a chain of
  `length` strict increases); the alternative reading ("greater than any of the
  previous `length` values") would differ. They only matter when
  `backtestBuyRisingHist` / `backtestSellFallingHist` are enabled, which the
  declared defaults do not do.
* `/*backtest` declares `period: 30m` on Futures_Binance BTC_USDT, so timeframe
  is "30m"; `basePeriod: 15m` is the FMZ backtester's fill granularity.
* Leverage, margin, liquidation, funding and the venue's contract-step rounding
  are not modelled.
"""
import math

import numpy as np
import pandas as pd

from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase

# The five MA families calcMA can select that this port does not reproduce.
# `ta.alma` / `ta.swma` are built-ins whose exact weight normalisation the
# source never spells out, and `vidya` / `frama` are written out in the source
# but depend on Pine's int/int division and on `math.log(0)`:
#   vidya: `alpha = 2 / (length + 1)` is an INT division -> 0 for every allowed
#          length (minval=2), so `src*0*cmo + nz(vidya[1])*(1-0*cmo)` collapses
#          the series to its nz seed;
#   frama: `w = math.log(2 / (v + 1))` is `math.log(0)` with SC=198 (int), and
#          whether Pine returns na or -inf there decides between a na frama and
#          a pass-through/EMA frama.
# Neither is resolvable without the original platform, and guessing would be an
# approximate port dressed up as a faithful one. All three are unreachable
# under the declared defaults (EMA / SMA / SMA / EMA).
UNSUPPORTED_MA_TYPES = ("ALMA", "VIDYA", "FRAMA")


def _pine_int(value: float) -> int:
    """Pine's implicit float -> int cast: round half away from zero."""
    return int(math.floor(abs(value) + 0.5)) * (1 if value >= 0 else -1)


def _pine_int_div(a: int, b: int) -> int:
    """Pine's `/` on two int operands: integer division truncated toward zero."""
    return int(math.trunc(a / b))


def _rising(source: pd.Series, length: int) -> pd.Series:
    """`ta.rising(source, length)`: rising for `length` bars long.

    Pine documents it as a chain of consecutive increases:
    `source[0] > source[1] and source[1] > source[2] and ... source[n-1] > source[n]`.
    The other reading in circulation ("greater than any of the previous
    `length` values") would be a different series; the equivalence risk is
    recorded in the fidelity notes. Unreachable under the declared defaults.
    """
    result = pd.Series(True, index=source.index, dtype=bool)
    for step in range(int(length)):
        result &= source.shift(step) > source.shift(step + 1)
    return result.fillna(False)


def _falling(source: pd.Series, length: int) -> pd.Series:
    """`ta.falling(source, length)`: the mirror of `_rising`."""
    result = pd.Series(True, index=source.index, dtype=bool)
    for step in range(int(length)):
        result &= source.shift(step) < source.shift(step + 1)
    return result.fillna(False)


def _hma(source: pd.Series, length: int) -> pd.Series:
    """`ta.hma(source, length)`, composed from pine_ta.pine_wma.

        ta.wma(2 * ta.wma(source, length / 2) - ta.wma(source, length),
               math.round(math.sqrt(length)))
    """
    length = int(length)
    inner = 2.0 * ta.pine_wma(source, _pine_int_div(length, 2)) - ta.pine_wma(
        source, length
    )
    return ta.pine_wma(inner, _pine_int(math.sqrt(length)))


def _swma(source: pd.Series) -> pd.Series:
    """`ta.swma(source)`: the fixed 7-bar symmetric weights 1,2,3,4,3,2,1 / 16.

    The source comments that "SWMA doesn't take a length".
    """
    weights = np.array([1.0, 2.0, 3.0, 4.0, 3.0, 2.0, 1.0])
    weights = weights / weights.sum()
    return source.rolling(7, min_periods=7).apply(
        lambda window: float(np.dot(window, weights)), raw=True
    )


def _calc_ma(ma_type: str, source: pd.Series, length: int, volume: pd.Series):
    """The source's own `calcMA(_type, _src, _length)` switch, branch for branch."""

    def ema(value, size):
        return ta.pine_ema(value, size)

    def sma(value, size):
        return ta.pine_sma(value, size)

    def wma(value, size):
        return ta.pine_wma(value, size)

    def rma(value, size):
        return ta.pine_rma(value, size)

    ma_type = str(ma_type)
    if ma_type in UNSUPPORTED_MA_TYPES:
        raise ValueError(
            f"calcMA('{ma_type}') is not reproduced by this port: "
            + {
                "ALMA": "ta.alma's weight normalisation is not stated in the source",
                "VIDYA": "the source's own vidya() divides int by int "
                         "(2 / (length + 1) = 0) so the series collapses to its seed",
                "FRAMA": "the source's own frama() takes math.log(2 / (v + 1)) "
                         "with SC=198, i.e. math.log(0), whose Pine value is unknown",
            }[ma_type]
            + ". Unreachable under the source's declared defaults; see "
            "source_fidelity_notes."
        )
    if ma_type == "EMA":
        return ema(source, length)
    if ma_type == "SMA":
        return sma(source, length)
    if ma_type == "WMA":
        return wma(source, length)
    if ma_type == "VWMA":
        weighted = source.copy()
        weighted.attrs["volume"] = volume
        return ta.pine_vwma(weighted, length)
    if ma_type == "HMA":
        return _hma(source, length)
    if ma_type == "RMA":
        return rma(source, length)
    if ma_type == "LSMA":
        return ta.pine_linreg(source, length, 0)
    if ma_type == "Double EMA":
        return 2 * ema(source, length) - ema(ema(source, length), length)
    if ma_type == "Double SMA":
        return 2 * sma(source, length) - sma(sma(source, length), length)
    if ma_type == "Double WMA":
        return 2 * wma(source, length) - wma(wma(source, length), length)
    if ma_type == "Double RMA":
        return 2 * rma(source, length) - rma(rma(source, length), length)
    if ma_type == "Triple EMA":
        return (
            3 * (ema(source, length) - ema(ema(source, length), length))
            + ema(ema(ema(source, length), length), length)
        )
    if ma_type == "Triple SMA":
        return (
            3 * (sma(source, length) - sma(sma(source, length), length))
            + sma(sma(sma(source, length), length), length)
        )
    if ma_type == "Triple WMA":
        return (
            3 * (wma(source, length) - wma(wma(source, length), length))
            + wma(wma(wma(source, length), length), length)
        )
    if ma_type == "Triple RMA":
        return (
            3 * (rma(source, length) - rma(rma(source, length), length))
            + rma(rma(rma(source, length), length), length)
        )
    if ma_type == "SWMA":
        return _swma(source)
    raise ValueError(f"calcMA: unknown moving average type {ma_type!r}")


def _truthy(value) -> bool:
    """Pine's boolean context: a number is true when it is not zero.

    `openLong and longOpenSignal` mixes a bool with an int. Pine reads the int
    as false only at 0, which Python's `!= 0` also does -- true for 1 AND for
    -1. This is the PINE_SEMANTICS.md 1.17 family: the port must not "tidy" the
    -1 into `== 1` / `> 0`, which would silently delete every short entry.
    """
    return value is not None and value != 0


class SMAmacd_200d9b(PinePortBase, IStrategy):
    source_id = "SM_200d9bbcebcdc2e0"
    source_file = "AMACD-All-Moving-Average-Convergence-Divergence.md"
    timeframe = "30m"
    can_short = True
    # Pine evaluates the script from the first bar of the window; the MACD chain
    # warms up on its own (hist is na until the signal SMA has a full window).
    startup_candle_count = 0
    source_defaults: dict = {
        # Moving Averages
        "FastType": "EMA",
        "FastLength": 12,
        "SlowType": "SMA",
        "SlowLength": 26,
        "SignalType": "SMA",
        "SignalLength": 9,
        # Alma
        "offset_alma": 0.85,
        "sigma_alma": 6,
        # Frama
        "FC": 1,
        "SC": 198,
        # Buy / Sell Moving Averages
        "backtestBuyCrossover": True,
        "backtestSellCrossover": True,
        "backtestMACrossUpZero": False,
        "backtestMACrossDownZero": False,
        # Buy / Sell Histogram Moving Averages
        "backtestBuyHistMA": False,
        "backtestSellHistMA": False,
        "MAHistLength": 5,
        "MAHistType": "EMA",
        # Buy / Sell Histogram Rising / Falling
        "backtestBuyRisingHist": False,
        "backtestBuyRisingHistBelow": False,
        "risingHistLength": 1,
        "backtestSellFallingHist": False,
        "backtestSellFallingHistAbove": False,
        "fallingHistLength": 1,
        # Long / Short Signals
        "generateClose": True,
        "longOpenSignal": 1,
        "longCloseSignal": 2,
        "shortOpenSignal": -1,
        "shortCloseSignal": -2,
        # Plot Options (display only)
        "plotAlerts": True,
        "plotMA": True,
        "plotSig": True,
        "plotH": True,
        "plotHMA": True,
    }
    # `indicator()` carries no strategy() properties, so Pine's documented
    # defaults apply.
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    # Every exit in the file is a market `strategy.close(...)`; no stop, limit
    # or trailing leg exists, so there is no intrabar level to reproduce.
    source_reproduce_stops = False
    source_mintick = 0.1
    source_fidelity_notes = [
        "Converter-appended order block on an INDICATOR (`indicator(title="
        "'AMACD - All Moving Average Convergence Divergence', overlay=false)`). "
        "Pine v5 cannot call strategy.entry from an indicator, so the port "
        "reproduces what the appended block actually does.",
        "The appended block DOES carry live exits: `strategy.close(\"Enter "
        "Long\",when=(closeLong and longCloseSignal),comment=\"Long_OK\")` and "
        "`strategy.close(\"Enter Short\",when=(closeShort and "
        "shortCloseSignal),comment=\"Short_OK\")` are not commented out. So the "
        "tier note for this item ('NO exits') is wrong for this file, and "
        "source_reproduce_stops is False only because a close is a market exit, "
        "not because there is no exit.",
        "MINUS-TRUTHINESS (PINE_SEMANTICS.md 1.17 family, plus 1.16): "
        "`longOpenSignal`/`shortOpenSignal`/`longCloseSignal`/`shortCloseSignal` "
        "default to 1 / -1 / 2 / -2 and are used as BARE conditions (`openLong "
        "and longOpenSignal`). A non-zero number is true in Pine and in Python, "
        "so the port tests non-zero and keeps the -1 as -1 -- it is NOT "
        "rewritten as `== 1` / `> 0`, which would silently drop every short "
        "entry.",
        "`dealstate` is a `var int` and both blocks read `dealstate[1]`, the "
        "value at the end of the PREVIOUS bar -- the sell block sees the old "
        "value even when the buy block has already rewritten it on the same "
        "bar. The port snapshots it per bar (Pine's history reference). On bar "
        "0 `dealstate[1]` is na and both `na == -1` / `na == 1` are false; the "
        "port's 0 seed takes the same branches.",
        "Both blocks can fire on one bar (dealstate[1] == 0 -> both take their "
        "else arms; dealstate[1] == 1 -> the buy block opens a long while the "
        "sell block closes it). The order written in the source is preserved: "
        "entry Long, entry Short (with `else if` precedence), then close Long, "
        "then close Short -- that is the engine's fill priority order.",
        "DIRECTION LOCK-IN under the declared defaults: the only enabled "
        "triggers are `backtestBuyCrossover` (longSignal = crossover(hist, 0)) "
        "and `backtestSellCrossover` (shortSignal = crossunder(hist, 0)), and "
        "those two strictly alternate. With `generateClose = true`, a sell "
        "signal that arrives while `dealstate[1] == 1` CLOSES the long instead "
        "of opening a short, and the next signal is always a buy, which sets "
        "dealstate back to 1 -- so the side the FIRST signal picks is the only "
        "side ever traded (a short-only run happens when the first signal is a "
        "sell). This is the source's own documented behaviour, not a port "
        "artifact: the author's changelog says 'it's only when there are two or "
        "more consecutive signals [that] will move you from longs to shorts'. "
        "Measured on the synthetic window: 164 long entries, 0 short entries.",
        "SAME-BAR ENTRY + CLOSE (PINE_SEMANTICS.md 1.13): reachable only when "
        "the buy and the sell blocks fire on one bar, which needs one of the "
        "four optional legs (`backtestBuyHistMA`, `backtestSellHistMA`, "
        "`backtestBuyRisingHist`, `backtestSellFallingHist`) -- all false by "
        "default, so the alternating crossover pair cannot do it. Where it does "
        "happen the entry and its close land on the same next open and the "
        "projection cannot express the flattening; 1.13 records the undecided "
        "model and this port does not patch it.",
        "When both fire with dealstate[1] == 1, the entry and its close are "
        "placed on the same bar. Pine fills the entry on the next open and the "
        "close on the same next open (source order), which the engine books as "
        "a zero-length round trip. The framework is only told `enter_long` on "
        "the placement bar (the close names an entry that is not open yet, so "
        "run_pine does not project it -- PINE_SEMANTICS.md 1.12/1.13), so the "
        "framework holds a long the engine has already flattened. That is the "
        "known projection boundary, recorded rather than patched.",
        "`MACrossDownZero = ta.crossover(macd, 0)` is the source's own bug "
        "(the 'crossing down' test is a second `crossover`). Preserved as "
        "written; `backtestMACrossUpZero`/`backtestMACrossDownZero` both "
        "default to false, so it cannot fire under the declared defaults.",
        "`signal = SignalLength > 1 ? calcMA(SignalType, macd, SignalLength) : 0` "
        "is transcribed with the ternary: a SignalLength of 1 would give the "
        "constant 0 signal line, exactly as written.",
        "calcMA is transcribed branch for branch. Only 'EMA' (FastType, "
        "MAHistType) and 'SMA' (SlowType, SignalType) are reachable under the "
        "declared defaults. ALMA, VIDYA and FRAMA are NOT reproduced and raise "
        "instead: ta.alma's weight normalisation is not in the source, while "
        "the source's OWN vidya() / frama() bodies divide int by int "
        "(`2 / (length + 1)`, `math.log(2 / (v + 1))` with SC=198), which is "
        "Pine integer division -> 0 -> `math.log(0)`, whose Pine value (na vs "
        "-inf) decides between a collapsed seed line and a pass-through/EMA "
        "line. Guessing there would be an approximate port claiming fidelity.",
        "`HMA` is composed from pine_ta.pine_wma as "
        "`wma(2*wma(src, length/2) - wma(src, length), round(sqrt(length)))` "
        "with Pine's integer division for `length / 2` and its round-half-away "
        "float->int cast for `sqrt(length)`; pine_ta has no hma. `SWMA` is the "
        "documented fixed 7-bar weights 1,2,3,4,3,2,1 / 16.",
        "`ta.rising` / `ta.falling` are not in pine_ta and are implemented as "
        "the documented chain of `length` consecutive increases / decreases. "
        "The alternative reading ('greater than any of the previous `length` "
        "values') is an equivalence risk that only bites when "
        "backtestBuyRisingHist / backtestSellFallingHist are enabled -- both "
        "false by default, so it is unreachable here.",
        "EMA seeding is pine_ta's modelled choice (first non-na observation), "
        "which PINE_SEMANTICS.md 3.1 flags as a parity risk; the source's fast "
        "leg and its histogram MA are both EMAs and are seeded by the common "
        "layer, not by this port.",
        "`plot(...)`, `plotshape(...)` and `alertcondition(...)` are display / "
        "alert only and are not reproduced; `comment=\"Long_OK\"` / "
        "`\"Short_OK\"` are order labels the ledger does not carry.",
        "Venue contract-step rounding, leverage, margin, liquidation and "
        "funding are not modelled.",
    ]

    def pine_indicators(self, dataframe: pd.DataFrame, params: dict) -> pd.DataFrame:
        close = dataframe["close"]
        volume = dataframe["volume"]
        params = dict(params)

        # MA_fast = calcMA(FastType, FastSource, FastLength)
        # MA_slow = calcMA(SlowType, SlowSource, SlowLength)
        # (FastSource / SlowSource both default to `close`.)
        ma_fast = _calc_ma(
            params["FastType"], close, int(params["FastLength"]), volume
        )
        ma_slow = _calc_ma(
            params["SlowType"], close, int(params["SlowLength"]), volume
        )

        # macd = MA_fast - MA_slow
        macd = ma_fast - ma_slow
        # signal = SignalLength > 1 ? calcMA(SignalType, macd, SignalLength) : 0
        signal_length = int(params["SignalLength"])
        if signal_length > 1:
            signal = _calc_ma(
                params["SignalType"], macd, signal_length, volume
            )
        else:
            signal = pd.Series(0.0, index=dataframe.index)
        # hist = macd - signal
        hist = macd - signal
        # histMA = calcMA(MAHistType, hist, MAHistLength)
        hist_ma = _calc_ma(
            params["MAHistType"], hist, int(params["MAHistLength"]), volume
        )

        # longSignal  = ta.crossover(hist, 0)
        # shortSignal = ta.crossunder(hist, 0)
        long_signal = ta.pine_crossover(hist, 0)
        short_signal = ta.pine_crossunder(hist, 0)
        # MACrossUpZero   = ta.crossover(macd, 0)
        # MACrossDownZero = ta.crossover(macd, 0)   <- source: crossover, not crossunder
        ma_cross_up_zero = ta.pine_crossover(macd, 0)
        ma_cross_down_zero = ta.pine_crossover(macd, 0)

        # longHistMA  = histMA > histMA[1]
        # shortHistMA = histMA < histMA[1]
        long_hist_ma = hist_ma > hist_ma.shift(1)
        short_hist_ma = hist_ma < hist_ma.shift(1)

        # risingHist  = ta.rising (hist, risingHistLength)  and (hist < 0 or not backtestBuyRisingHistBelow)
        # fallingHist = ta.falling(hist, fallingHistLength) and (hist > 0 or not backtestSellFallingHistAbove)
        rising_hist = _rising(hist, int(params["risingHistLength"])) & (
            (hist < 0) | (not bool(params["backtestBuyRisingHistBelow"]))
        )
        falling_hist = _falling(hist, int(params["fallingHistLength"])) & (
            (hist > 0) | (not bool(params["backtestSellFallingHistAbove"]))
        )

        def _previous(series) -> np.ndarray:
            """`series[1]` as Pine's history reference: na on bar 0 -> false."""
            values = series.to_numpy(dtype=bool)
            out = np.zeros(len(values), dtype=bool)
            out[1:] = values[:-1]
            return out

        def _not_previous(series) -> np.ndarray:
            """`not series[1]`: bar 0 is na, and Pine reads `not na` as false."""
            values = series.to_numpy(dtype=bool)
            out = np.zeros(len(values), dtype=bool)
            out[1:] = ~values[:-1]
            return out

        # The four optional buy legs and four sell legs, each gated by its own
        # input. `and` on the two `not ...Hist[1]` terms is Pine's na-as-false.
        buy_cross = np.full(len(dataframe), bool(params["backtestBuyCrossover"])) & long_signal.to_numpy(dtype=bool)
        sell_cross = np.full(len(dataframe), bool(params["backtestSellCrossover"])) & short_signal.to_numpy(dtype=bool)
        buy_hist_ma = (
            np.full(len(dataframe), bool(params["backtestBuyHistMA"]))
            & long_hist_ma.to_numpy(dtype=bool)
            & _not_previous(long_hist_ma)
        )
        sell_hist_ma = (
            np.full(len(dataframe), bool(params["backtestSellHistMA"]))
            & short_hist_ma.to_numpy(dtype=bool)
            & _not_previous(short_hist_ma)
        )
        buy_rising = (
            np.full(len(dataframe), bool(params["backtestBuyRisingHist"]))
            & rising_hist.to_numpy(dtype=bool)
            & _not_previous(rising_hist)
        )
        sell_falling = (
            np.full(len(dataframe), bool(params["backtestSellFallingHist"]))
            & falling_hist.to_numpy(dtype=bool)
            & _not_previous(falling_hist)
        )
        buy_zero = (
            np.full(len(dataframe), bool(params["backtestMACrossUpZero"]))
            & ma_cross_up_zero.to_numpy(dtype=bool)
        )
        sell_zero = (
            np.full(len(dataframe), bool(params["backtestMACrossDownZero"]))
            & ma_cross_down_zero.to_numpy(dtype=bool)
        )

        buy_condition = buy_cross | buy_hist_ma | buy_rising | buy_zero
        sell_condition = sell_cross | sell_hist_ma | sell_falling | sell_zero

        generate_close = bool(params["generateClose"])
        long_open_signal = _truthy(params["longOpenSignal"])
        short_open_signal = _truthy(params["shortOpenSignal"])
        long_close_signal = _truthy(params["longCloseSignal"])
        short_close_signal = _truthy(params["shortCloseSignal"])

        size = len(dataframe)
        # var int dealstate = 0
        dealstate = 0
        dealstates = np.zeros(size, dtype=float)
        enter_long = np.zeros(size, dtype=bool)
        enter_short = np.zeros(size, dtype=bool)
        close_long = np.zeros(size, dtype=bool)
        close_short = np.zeros(size, dtype=bool)

        for i in range(size):
            # dealstate[1]: the value at the END of the previous bar (na on bar
            # 0, which matches neither -1 nor 1 -- the 0 seed takes the same
            # branch).
            previous = dealstate
            open_long = False
            close_long_here = False
            open_short = False
            close_short_here = False

            # if (... buy conditions ...)
            if buy_condition[i]:
                # if (dealstate[1] == -1) and generateClose
                if previous == -1 and generate_close:
                    close_short_here = True
                    dealstate = 0
                else:
                    open_long = True
                    dealstate = 1

            # if (... sell conditions ...)
            if sell_condition[i]:
                # if (dealstate[1] == 1) and generateClose
                if previous == 1 and generate_close:
                    close_long_here = True
                    dealstate = 0
                else:
                    open_short = True
                    dealstate = -1

            # if openLong and longOpenSignal / else if openShort and shortOpenSignal
            emit_long = open_long and long_open_signal
            emit_short = (not emit_long) and open_short and short_open_signal
            enter_long[i] = bool(emit_long)
            enter_short[i] = bool(emit_short)
            # strategy.close(..., when=(closeLong and longCloseSignal))
            close_long[i] = bool(close_long_here and long_close_signal)
            close_short[i] = bool(close_short_here and short_close_signal)
            dealstates[i] = float(dealstate)

        dataframe["pine_macd"] = macd
        dataframe["pine_signal"] = signal
        dataframe["pine_hist"] = hist
        dataframe["pine_hist_ma"] = hist_ma
        dataframe["pine_dealstate"] = dealstates
        dataframe["pine_enter_long"] = enter_long
        dataframe["pine_enter_short"] = enter_short
        dataframe["pine_close_long"] = close_long
        dataframe["pine_close_short"] = close_short
        return dataframe

    def pine_context(self, dataframe: pd.DataFrame, params: dict) -> dict:
        return {
            "enter_long": dataframe["pine_enter_long"].to_numpy(),
            "enter_short": dataframe["pine_enter_short"].to_numpy(),
            "close_long": dataframe["pine_close_long"].to_numpy(),
            "close_short": dataframe["pine_close_short"].to_numpy(),
        }

    def pine_script(self, broker, i: int, ctx: dict) -> None:
        # if openLong and longOpenSignal
        #     strategy.entry("Enter Long", strategy.long)
        # else if openShort and shortOpenSignal
        #     strategy.entry("Enter Short", strategy.short)
        if ctx["enter_long"][i]:
            broker.entry("Enter Long", "long")
        elif ctx["enter_short"][i]:
            broker.entry("Enter Short", "short")

        # strategy.close("Enter Long",when=(closeLong and longCloseSignal),comment="Long_OK")
        if ctx["close_long"][i]:
            broker.close("Enter Long", when=True)
        # strategy.close("Enter Short",when=(closeShort and shortCloseSignal),comment="Short_OK")
        if ctx["close_short"][i]:
            broker.close("Enter Short", when=True)
