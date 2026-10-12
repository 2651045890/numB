"""Port of sources/SM_51e4f51c3383fce4.pine
(batch_001/EMA-bands-leledc-bollinger-bands-trend-catching-strategy.md).

Pine v5 (`//@version=5`), 703 lines, three credited indicator blocks assembled
into one strategy: VishvaP's 34-EMA reversion bands, Joy_Bangla's Leledc
exhaustion bars, and a Bollinger-bands/RSI exhaustion bar. The active trading
logic at the defaults is small, but the port keeps every branch the source can
reach rather than only the ones the defaults select.

    EMA            = ta.ema(close, 34)
    highShortEMA   = ta.ema(high, 34)      lowShortEMA = ta.ema(low, 34)
    shortbandsHigh = ((highShortEMA - EMA) * phi) * pi + EMA
    shortbandsLow  = (-(EMA - lowShortEMA) * phi) * pi + EMA
    shortbandsHighEMA = ta.wma(shortbandsHigh, 8)   (same for Low)
    phiExtensionHigh  = ((highShortEMA - EMA) * phi) * (phi + 4) + EMA
    phiExtensionLow   = (-(EMA - lowShortEMA) * phi) * (phi + 4) + EMA
    phiExtensionHighEMA = ta.wma(phiExtensionHigh, 8)  (same for Low)
    BBbasis = ta.sma(close, 20) ; BBdev = 1.8 * ta.stdev(close, 20)
    vrsi = ta.rsi(close, 8) ; RSIoverSold = vrsi < 30 ; RSIoverBought = vrsi > 70
    OSOBcolor = RSIoverBought and close[1] > BBupper and close < BBupper ? yellow
              : RSIoverSold  and close[1] < BBlower and close > BBlower ? blue : na
    leleVol = volume > ta.sma(volume, 100) * 1.5
    major = lele(maj_qual = 6, maj_len = 30)     -- stateful exhaustion counter

    longMidBreak  = crossUpTopMB or wiggleUpTopMB
    shortMidBreak = crossDownBotMB or wiggleDownBotMB

At the input DEFAULTS four calls fire, in this source order:

    if needLong  and longMidBreak      -> strategy.entry('Long',  strategy.long)
    if needShort and shortMidBreak     -> strategy.entry('Short', strategy.short)
    ... and, inside `if strategy.position_size > 0`,
    if midClose == 'Opposite band' and (crossDownBotMB or wiggleDownBotMB)
                                       -> strategy.close('Long')
    ... and, inside `if strategy.position_size < 0`,
    if midClose == 'Opposite band' and (crossUpTopMB or wiggleUpTopMB)
                                       -> strategy.close('Short')

`CTbandTop` / `CTbandBottom`, the counter-trend (`needCTlong` / `needCTshort`),
bounce (`s_longBounce` / `s_shortBounce`) and default-positioning
(`alwaysLong` / `alwaysShort`) paths all default to false and place nothing, but
are implemented so that overriding a parameter through the config exercises the
same branches the source would.

The `strategy(...)` call is COMMENTED OUT and is the file's only declaration of
execution properties:

    //strategy(title='EMA bands + leledc + bollinger bands trend catching
    //  strategy w/ countertrend scalp', ..., initial_capital = 1000,
    //  commission_value= 0.036, pyramiding= 0, default_qty_type=
    //  strategy.percent_of_equity, default_qty_value= 100, ...)

Commented code places no declaration, so it is read as absent and Pine's
documented defaults apply: fixed sizing, qty 1, initial capital 1000000,
commission 0%, `pyramiding=0`, `process_orders_on_close=false`. The commented
values are recorded verbatim in `source_fidelity_notes` and are not adopted.

FIDELITY:

* The two exits are `strategy.exit(id='Counter Trend Long' / 'Counter Trend
  Short', ...)` with NO `from_entry`. Both blocks are already gated on
  `strategy.opentrades.entry_id(strategy.opentrades - 1) == '<that id>'`, so the
  open entry IS that id and the port passes it explicitly as `from_entry`; the
  engine's `from_entry=None` would instead close every open entry. With
  `pyramiding=0` the two readings coincide, and the explicit binding is the one
  that stays correct if the source platform ever holds a second entry.
* `trail_*` never appears in this source, so `source_reproduce_stops` is True
  only for the `stop=CTlongSL` / `stop=CTshortSL` legs of the counter-trend
  exits (unreachable at the defaults). The long/short closes are market closes
  and reach the framework as next-open signals.
* The source repeats `crossUpBotOuterRB or crossUpBotOuterRB` (and
  `crossDownTopOuterRB or crossDownTopOuterRB`) where the mirrored branch has
  `... or wiggle...`. That is a copy/paste slip in the source, not a modelling
  choice: it is reproduced LITERALLY (the `wiggle` term is never consulted in
  those two branches) and recorded, not quietly corrected.
* `lele()` is a stateful counter (`bindex` / `sindex` re-enter through
  `bindex[bindexSindex]` on every bar, then reset to 0 when an exhaustion bar
  fires). It is transcribed bar by bar with the source's own initial state
  (`nz(..., 0)` on the first bar) rather than approximated.
* The `strategy.position_size[i]` history the Leledc / BB counting loops read is
  recorded per bar by the port as it runs: the engine fills bar `t`'s open
  before calling the script for bar `t`, which is exactly the value Pine reads
  as `strategy.position_size` while evaluating bar `t`.
* Dead code, not reproduced: `buyEntry` / `sellEntry`, `leledcSrc`,
  `mezzalinea`-style leftovers, `showSlowEMA` / `maj` / `switch1` / `switch2` /
  `showReverBars` / `trendColor` (display), the whole `colorBar` block (its only
  consumer, `barcolor(colorBar)`, is commented out), `plot()` / `plotchar()` /
  `bgcolor()` / `fill()` calls, and the commented-out RSI+BB entry block and
  commented-out minor-Leledc block.
* `input.bool` never appears in a numeric context here, so PINE_SEMANTICS
  section 1.16 does not apply.
* Leverage, margin, liquidation and funding are not modelled, and the venue's
  contract-step rounding is not modelled either (the chain verifier measures
  that separately rather than treating it as a signal difference).
"""
import numpy as np
import pandas as pd

from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase

PHI = 1.6180339887498949
PI = 3.141592653589793

# `OSOBcolor` and `reverBarColor` are Pine colour series; comparisons against
# them are the source's way of asking "is this bar the exhaustion / reversion
# bar". They are modelled as small integer codes, with 0 standing for na.
COLOUR_NA = 0
COLOUR_YELLOW = 1
COLOUR_BLUE = 2
COLOUR_ORANGE = 3
COLOUR_PURPLE = 4

LELE_NUM_BARS = {"First": 1, "Second": 2, "Third": 3, "Fourth": 4, "Fifth": 5}
BB_NUM_BARS = {"First": 1, "Second": 2, "Third": 3}


def _lele(close, open_, high, low, highest, lowest, lele_vol, qual, length,
          gate_volume, shift, close_val):
    """Joy_Bangla's Leledc exhaustion counter, transcribed bar by bar.

    `bindex` / `sindex` are Pine function-local series: each bar first reloads
    them from `shift` bars back with `nz(..., 0)`, then a bar that closes above
    `close[close_val]` bumps `bindex` (below bumps `sindex`). Once the counter
    exceeds `qual` and the bar is an inside/outside exhaustion candle, the
    counter resets and `ret` becomes -1 (bearish, a red bar at the high) or 1
    (bullish, a green bar at the low). With `gate_volume` set, every bar whose
    volume does not confirm forces `ret` to 0 but leaves the counters running.
    """
    n = len(close)
    bindex = np.zeros(n, dtype=float)
    sindex = np.zeros(n, dtype=float)
    ret = np.zeros(n, dtype=float)
    for t in range(n):
        # bindex := nz(bindex[bindexSindex], 0)  -- na before the series starts
        prev = t - shift
        b = bindex[prev] if prev >= 0 else 0.0
        s = sindex[prev] if prev >= 0 else 0.0
        r = 0.0
        ref = t - close_val
        if ref >= 0:
            if close[t] > close[ref]:
                b += 1.0
            if close[t] < close[ref]:
                s += 1.0
        if gate_volume and not lele_vol[t]:
            r = 0.0
        else:
            # Pine's na comparison is false, so the warmup bars simply do not fire.
            if b > qual and close[t] < open_[t] and high[t] >= highest[t]:
                b = 0.0
                r = -1.0
            if s > qual and close[t] > open_[t] and low[t] <= lowest[t]:
                s = 0.0
                r = 1.0
        bindex[t] = b
        sindex[t] = s
        ret[t] = r
    return ret


class SMEmaBandsLeledc_51e4f5(PinePortBase, IStrategy):
    source_id = "SM_51e4f51c3383fce4"
    source_file = "EMA-bands-leledc-bollinger-bands-trend-catching-strategy.md"
    timeframe = "1h"
    can_short = True
    # Pine evaluates the script from the first bar; the rolling windows warm up
    # as na comparisons (both in Pine and in pine_ta), not as a truncation.
    startup_candle_count = 0
    source_defaults: dict = {
        "EMAlength": 34,
        "needLong": True,
        "needShort": True,
        "midClose": "Opposite band",
        "needCTlong": False,
        "CTlongType": "Leledc",
        "needCTshort": False,
        "CTshortType": "Leledc",
        "alwaysLong": False,
        "alwaysShort": False,
        "s_longBounce": False,
        "s_shortBounce": False,
        "numBars": 4,
        "useSlowEMA": False,
        "useLele": False,
        "whichLele": "First",
        "useBBExtend": False,
        "whichBBext": "First",
        "reverBandClose": False,
        "whichCTband": "Inner",
        "i_CTlongCloseCond": "Cross Top Middle Band",
        "i_CTshortCloseCond": "First Leledc",
        "i_CTlongSL": 10,
        "i_CTshortSL": 10,
        "showSlowEMA": False,
        "slowEMAlen": 200,
        "maj": True,
        "BBlength": 20,
        "BBmult": 1.8,
        "RSIlength": 8,
        "RSIos": 30,
        "RSIob": 70,
        "switch1": True,
        "switch2": False,
        "i_leleVol": False,
        "i_volMult": 1.5,
        "maj_qual": 6,
        "maj_len": 30,
        "bindexSindex": 1,
        "closeVal": 4,
        "showReverBars": False,
        "whichReverBand": "Inner",
        "trendColor": False,
    }
    # `//strategy(...)` is commented out; Pine's documented defaults apply.
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    # The only stop legs are the counter-trend `strategy.exit(..., stop=...)`
    # calls, which are unreachable at the input defaults; the long/short closes
    # are market closes.
    source_reproduce_stops = True
    source_fidelity_notes = [
        "The `strategy(...)` call is COMMENTED OUT and is the file's only "
        "declaration of execution properties, so it is read as absent and Pine's "
        "documented defaults apply: fixed sizing, qty 1, initial capital "
        "1000000, commission 0%, pyramiding 0, process_orders_on_close=false. "
        "The commented values were: title='EMA bands + leledc + bollinger bands "
        "trend catching strategy w/ countertrend scalp', overlay=true, "
        "initial_capital = 1000, commission_value= 0.036, pyramiding= 0, "
        "default_qty_type= strategy.percent_of_equity, default_qty_value= 100, "
        "margin_long=0, margin_short=0, max_bars_back=200. Recorded, not "
        "adopted.",
        "The source repeats `crossUpBotOuterRB or crossUpBotOuterRB` (in "
        "CTlongCloseCond) and `crossDownTopOuterRB or crossDownTopOuterRB` (in "
        "CTshortCloseCond) where the mirrored branch uses `... or wiggle...`. "
        "That is a copy/paste slip in the source; it is reproduced literally, "
        "so `wiggleUpBotOuterRB` / `wiggleDownTopOuterRB` are never consulted "
        "in those branches. Recorded, not corrected.",
        "`lele()` is stateful across bars (`bindex` / `sindex` reload from "
        "`bindex[bindexSindex]` each bar and reset on an exhaustion bar). "
        "Transcribed bar by bar with the source's zero initial state rather "
        "than approximated.",
        "The Leledc / BB counting loops read `strategy.position_size[n]`, i.e. "
        "the position on bars already elapsed. The port records that series as "
        "it runs: the engine fills bar t's open before calling the script for "
        "bar t, which is the value Pine reads while evaluating bar t. The loops "
        "are only reachable with useLele/useBBExtend and a 'Second'+ selection "
        "(whichLele / whichBBext default to 'First').",
        "`strategy.exit(id='Counter Trend Long', ...)` passes no `from_entry`; "
        "the enclosing guard already requires that id to be the newest open "
        "entry, so the port binds it explicitly. The engine's `from_entry=None` "
        "would close every open entry instead. With pyramiding=0 the two "
        "readings coincide.",
        "In the `i_CTlongSL == 0` branch the exit carries only `limit=CTlongTP`, "
        "and CTlongTP is na unless the close condition is a 'Touch ...' option "
        "(the default 'Cross Top Middle Band' is not). A price-legged-less "
        "strategy.exit is a Pine no-op; see PINE_SEMANTICS.md section 1.15 for "
        "the shared projection layer's known behaviour on that shape.",
        "`strategy.close(id=...)` / `strategy.entry(id=...)` calls pass no `qty`, "
        "so the engine sizes them from default_qty_type / default_qty_value.",
        "Dead code, not reproduced: `buyEntry` / `sellEntry`, `leledcSrc` (both "
        "inputs bound to series but never read), `showSlowEMA`, `maj`, "
        "`switch1`, `switch2`, `showReverBars`, `trendColor`, the entire "
        "`colorBar` block (its only consumer `barcolor(colorBar)` is commented "
        "out), and every `plot()` / `plotchar()` / `bgcolor()` / `fill()` call.",
        "The commented-out RSI+Bollinger entry block and the commented-out "
        "minor-Leledc block place no orders and are not restored.",
        "`price = input(close, title='Source')` and `leledcSrc = input(close, "
        "...)` take the close series as their default; that is reproduced as "
        "close, and no numeric default exists for them.",
        "No `input.bool` here is used in a numeric context, so PINE_SEMANTICS "
        "section 1.16 does not apply.",
        "Leverage, margin, liquidation and funding are not modelled; the "
        "venue's contract-step rounding is not modelled either.",
    ]

    def __init__(self, config):
        super().__init__(config)
        # Pine's own `strategy.position_size` series, recorded as the engine
        # advances; see the class docstring.
        self._pos_history: list[float] = []

    # ------------------------------------------------------------------ setup
    def pine_indicators(self, dataframe: pd.DataFrame, params: dict) -> pd.DataFrame:
        self._pos_history = []
        open_ = dataframe["open"]
        high = dataframe["high"]
        low = dataframe["low"]
        close = dataframe["close"]
        volume = dataframe["volume"]

        ema_len = int(params["EMAlength"])

        # ---- Bollinger bands + RSI exhaustion bar (SlumdogTrader) -----------
        bb_len = int(params["BBlength"])
        bb_mult = float(params["BBmult"])
        basis = ta.pine_sma(close, bb_len)
        deviation = bb_mult * ta.pine_stdev(close, bb_len)
        bb_upper = basis + deviation
        bb_lower = basis - deviation
        # `source = close`; buyEntry / sellEntry are computed and never read.
        rsi = ta.pine_rsi(close, int(params["RSIlength"]))
        rsi_os = rsi < float(params["RSIos"])
        rsi_ob = rsi > float(params["RSIob"])
        close_prev = close.shift(1)
        yellow = (rsi_ob & (close_prev > bb_upper) & (close < bb_upper)).fillna(False)
        blue = (rsi_os & (close_prev < bb_lower) & (close > bb_lower)).fillna(False)
        os_ob = np.where(yellow.to_numpy(), COLOUR_YELLOW,
                         np.where(blue.to_numpy(), COLOUR_BLUE, COLOUR_NA))

        # ---- Leledc exhaustion bars (Joy_Bangla) ---------------------------
        maj_len = int(params["maj_len"])
        lele_vol = (
            volume > ta.pine_sma(volume, 100) * float(params["i_volMult"])
        ).fillna(False)
        major = _lele(
            close.to_numpy(dtype=float), open_.to_numpy(dtype=float),
            high.to_numpy(dtype=float), low.to_numpy(dtype=float),
            ta.pine_highest(high, maj_len).to_numpy(dtype=float),
            ta.pine_lowest(low, maj_len).to_numpy(dtype=float),
            lele_vol.to_numpy(dtype=bool),
            qual=int(params["maj_qual"]), length=maj_len,
            gate_volume=bool(params["i_leleVol"]),
            shift=int(params["bindexSindex"]), close_val=int(params["closeVal"]),
        )

        # ---- 34 EMA reversion bands (VishvaP) ------------------------------
        high_short_ema = ta.pine_ema(high, ema_len)
        low_short_ema = ta.pine_ema(low, ema_len)
        ema = ta.pine_ema(close, ema_len)
        shortbands_high = ((high_short_ema - ema) * PHI) * PI + ema
        shortbands_low = (-(ema - low_short_ema) * PHI) * PI + ema
        shortbands_high_ema = ta.pine_wma(shortbands_high, 8)
        shortbands_low_ema = ta.pine_wma(shortbands_low, 8)
        phi_high = ((high_short_ema - ema) * PHI) * (PHI + 4) + ema
        phi_low = (-(ema - low_short_ema) * PHI) * (PHI + 4) + ema
        phi_high_ema = ta.pine_wma(phi_high, 8)
        phi_low_ema = ta.pine_wma(phi_low, 8)
        slow_ema = ta.pine_ema(close, int(params["slowEMAlen"]))

        # ---- middle-band and reversion-zone cross helpers -------------------
        def x_up(level):
            return (open_ < level) & (close > level)

        def w_up(level):
            return (open_ > level) & (close > level) & (close_prev <= level.shift(1))

        def x_dn(level):
            return (open_ > level) & (close < level)

        def w_dn(level):
            return (open_ < level) & (close < level) & (close_prev >= level.shift(1))

        cross_up_top_mb, wiggle_up_top_mb = x_up(high_short_ema), w_up(high_short_ema)
        cross_dn_top_mb, wiggle_dn_top_mb = x_dn(high_short_ema), w_dn(high_short_ema)
        cross_up_bot_mb, wiggle_up_bot_mb = x_up(low_short_ema), w_up(low_short_ema)
        cross_dn_bot_mb, wiggle_dn_bot_mb = x_dn(low_short_ema), w_dn(low_short_ema)

        long_bounce = ((open_ > high_short_ema) & (close > high_short_ema)
                       & (low < high_short_ema)).fillna(False)
        short_bounce = ((open_ < low_short_ema) & (close < low_short_ema)
                        & (high > low_short_ema)).fillna(False)

        # ---- counter-trend entry zones --------------------------------------
        inner_ct = str(params["whichCTband"]) == "Inner"
        ct_band_top = shortbands_high_ema if inner_ct else phi_high_ema
        ct_band_bottom = shortbands_low_ema if inner_ct else phi_low_ema

        # ---- counter-trend closing conditions -------------------------------
        # `CTlongCloseCond` / `CTshortCloseCond` are single nested ternaries in
        # the source; the two 'Cross Outer ...' arms repeat one term
        # (`crossUpBotOuterRB or crossUpBotOuterRB`) where the mirrored arm
        # consults the wiggle term. That repetition is the source's own, and it
        # is reproduced literally here rather than corrected.
        cross_up_top_inner_rb = x_up(shortbands_high_ema)
        wiggle_up_top_inner_rb = w_up(shortbands_high_ema)
        cross_up_top_outer_rb = x_up(phi_high_ema)
        wiggle_up_top_outer_rb = w_up(phi_high_ema)
        cross_dn_bot_inner_rb = x_dn(shortbands_low_ema)
        wiggle_dn_bot_inner_rb = w_dn(shortbands_low_ema)
        cross_dn_bot_outer_rb = x_dn(phi_low_ema)
        wiggle_dn_bot_outer_rb = w_dn(phi_low_ema)
        cross_dn_top_inner_rb = x_dn(shortbands_high_ema)
        wiggle_dn_top_inner_rb = w_dn(shortbands_high_ema)
        cross_dn_top_outer_rb = x_dn(phi_high_ema)
        # cross/wiggle pairs used by the TP arms above are re-declared here only
        # for locality; they are the same expressions as in the RB block above.
        cross_up_bot_inner_rb = x_up(shortbands_low_ema)
        wiggle_up_bot_inner_rb = w_up(shortbands_low_ema)
        cross_up_bot_outer_rb = x_up(phi_low_ema)
        wiggle_up_bot_outer_rb = w_up(phi_low_ema)
        cross_up_top_mb, wiggle_up_top_mb = x_up(high_short_ema), w_up(high_short_ema)
        cross_dn_top_mb, wiggle_dn_top_mb = x_dn(high_short_ema), w_dn(high_short_ema)
        cross_up_bot_mb, wiggle_up_bot_mb = x_up(low_short_ema), w_up(low_short_ema)
        cross_dn_bot_mb, wiggle_dn_bot_mb = x_dn(low_short_ema), w_dn(low_short_ema)

        def _and(a, b):
            return (a | b).fillna(False)

        na_bars = pd.Series(False, index=dataframe.index)
        ct_long_cond = str(params["i_CTlongCloseCond"])
        ct_long_close = na_bars.copy()
        if ct_long_cond == "Cross Inner Sell Zone":
            ct_long_close = _and(cross_up_top_inner_rb, wiggle_up_top_inner_rb)
        elif ct_long_cond == "Cross Outer Sell Zone":
            ct_long_close = _and(cross_up_top_outer_rb, wiggle_up_top_outer_rb)
        elif ct_long_cond == "Cross Top Middle Band":
            ct_long_close = _and(cross_up_top_mb, wiggle_up_top_mb)
        elif ct_long_cond == "Cross Bottom Middle Band":
            ct_long_close = _and(cross_up_bot_mb, wiggle_up_bot_mb)
        elif ct_long_cond == "Cross Inner Buy Zone":
            ct_long_close = _and(cross_up_bot_inner_rb, wiggle_up_bot_inner_rb)
        elif ct_long_cond == "Cross Outer Buy Zone":
            # Source: `crossUpBotOuterRB or crossUpBotOuterRB` (repeated term).
            ct_long_close = cross_up_bot_outer_rb.fillna(False)
        elif ct_long_cond == "First Leledc":
            ct_long_close = pd.Series(major == -1.0, index=dataframe.index)
        elif ct_long_cond == "First BB Exhaustion":
            ct_long_close = pd.Series(os_ob == COLOUR_YELLOW, index=dataframe.index)

        ct_short_cond = str(params["i_CTshortCloseCond"])
        ct_short_close = na_bars.copy()
        if ct_short_cond == "Cross Inner Buy Zone":
            ct_short_close = _and(cross_dn_bot_inner_rb, wiggle_dn_bot_inner_rb)
        elif ct_short_cond == "Cross Outer Buy Zone":
            ct_short_close = _and(cross_dn_bot_outer_rb, wiggle_dn_bot_outer_rb)
        elif ct_short_cond == "Cross Bottom Middle Band":
            ct_short_close = _and(cross_dn_bot_mb, wiggle_dn_bot_mb)
        elif ct_short_cond == "Cross Top Middle Band":
            ct_short_close = _and(cross_dn_top_mb, wiggle_dn_top_mb)
        elif ct_short_cond == "Cross Inner Sell Zone":
            ct_short_close = _and(cross_dn_top_inner_rb, wiggle_dn_top_inner_rb)
        elif ct_short_cond == "Cross Outer Sell Zone":
            # Source: `crossDownTopOuterRB or crossDownTopOuterRB` (repeated).
            ct_short_close = cross_dn_top_outer_rb.fillna(False)
        elif ct_short_cond == "First Leledc":
            ct_short_close = pd.Series(major == 1.0, index=dataframe.index)
        elif ct_short_cond == "First BB Exhaustion":
            ct_short_close = pd.Series(os_ob == COLOUR_BLUE, index=dataframe.index)

        # `CTlongTP` / `CTshortTP`: na for every non-'Touch' option, so the
        # default 'Cross Top Middle Band' leaves the exit with no limit leg.
        ct_long_tp = pd.Series(np.nan, index=dataframe.index)
        if ct_long_cond == "Touch Inner Buy Zone":
            ct_long_tp = shortbands_low_ema
        elif ct_long_cond == "Touch Top Middle Band":
            ct_long_tp = high_short_ema
        elif ct_long_cond == "Touch Bottom Middle Band":
            ct_long_tp = low_short_ema
        elif ct_long_cond == "Touch Inner Sell Zone":
            ct_long_tp = shortbands_high_ema
        elif ct_long_cond == "Touch Outer Sell Zone":
            ct_long_tp = phi_high_ema

        ct_short_tp = pd.Series(np.nan, index=dataframe.index)
        if ct_short_cond == "Touch Inner Sell Zone":
            ct_short_tp = shortbands_high_ema
        elif ct_short_cond == "Touch Bottom Middle Band":
            ct_short_tp = low_short_ema
        elif ct_short_cond == "Touch Top Middle Band":
            ct_short_tp = high_short_ema
        elif ct_short_cond == "Touch Inner Buy Zone":
            ct_short_tp = shortbands_low_ema
        elif ct_short_cond == "Touch Outer Buy Zone":
            ct_short_tp = phi_low_ema

        # ---- reversion-bar colour ------------------------------------------
        rever_inner = str(params["whichReverBand"]) == "Inner"
        rever_top = shortbands_high_ema if rever_inner else phi_high_ema
        rever_bottom = shortbands_low_ema if rever_inner else phi_low_ema
        cross_up_rb = x_up(rever_bottom)
        wiggle_up_rb = w_up(rever_bottom)
        cross_dn_rb = x_dn(rever_top)
        wiggle_dn_rb = w_dn(rever_top)
        # `reverBarColor = crossDownRB or (wiggleDownRB and not crossDownRB[1])
        #                   ? orange : crossUpRB or (wiggleUpRB and not
        #                   crossUpRB[1]) ? purple : na`
        orange = (cross_dn_rb
                  | (wiggle_dn_rb & ~cross_dn_rb.shift(1).fillna(False))).fillna(False)
        purple = (cross_up_rb
                  | (wiggle_up_rb & ~cross_up_rb.shift(1).fillna(False))).fillna(False)
        rever_color = np.where(orange.to_numpy(), COLOUR_ORANGE,
                               np.where(purple.to_numpy(), COLOUR_PURPLE, COLOUR_NA))

        in_mid = ((close > low_short_ema) & (close < high_short_ema)
                  & (open_ > low_short_ema) & (open_ < high_short_ema)).fillna(False)
        long_mid_break = (cross_up_top_mb | wiggle_up_top_mb).fillna(False)
        short_mid_break = (cross_dn_bot_mb | wiggle_dn_bot_mb).fillna(False)

        dataframe["pine_slow_ema"] = slow_ema
        dataframe["pine_high_short_ema"] = high_short_ema
        dataframe["pine_low_short_ema"] = low_short_ema
        dataframe["pine_ema"] = ema
        dataframe["pine_shortbands_high_ema"] = shortbands_high_ema
        dataframe["pine_shortbands_low_ema"] = shortbands_low_ema
        dataframe["pine_phi_high_ema"] = phi_high_ema
        dataframe["pine_phi_low_ema"] = phi_low_ema
        dataframe["pine_basis"] = basis
        dataframe["pine_bb_upper"] = bb_upper
        dataframe["pine_bb_lower"] = bb_lower
        dataframe["pine_rsi"] = rsi
        dataframe["pine_lele_vol"] = lele_vol
        dataframe["pine_major"] = major
        dataframe["pine_osob"] = os_ob
        dataframe["pine_rever_color"] = rever_color
        dataframe["pine_ct_band_top"] = ct_band_top
        dataframe["pine_ct_band_bottom"] = ct_band_bottom
        dataframe["pine_ct_long_close"] = ct_long_close.fillna(False)
        dataframe["pine_ct_short_close"] = ct_short_close.fillna(False)
        dataframe["pine_ct_long_tp"] = ct_long_tp
        dataframe["pine_ct_short_tp"] = ct_short_tp
        dataframe["pine_in_mid"] = in_mid
        dataframe["pine_long_mid_break"] = long_mid_break
        dataframe["pine_short_mid_break"] = short_mid_break
        dataframe["pine_cross_up_top_mb"] = cross_up_top_mb.fillna(False)
        dataframe["pine_wiggle_up_top_mb"] = wiggle_up_top_mb.fillna(False)
        dataframe["pine_cross_dn_bot_mb"] = cross_dn_bot_mb.fillna(False)
        dataframe["pine_wiggle_dn_bot_mb"] = wiggle_dn_bot_mb.fillna(False)
        dataframe["pine_cross_dn_top_mb"] = cross_dn_top_mb.fillna(False)
        dataframe["pine_wiggle_dn_top_mb"] = wiggle_dn_top_mb.fillna(False)
        dataframe["pine_cross_up_bot_mb"] = cross_up_bot_mb.fillna(False)
        dataframe["pine_wiggle_up_bot_mb"] = wiggle_up_bot_mb.fillna(False)
        dataframe["pine_long_bounce"] = long_bounce
        dataframe["pine_short_bounce"] = short_bounce
        return dataframe

    def pine_context(self, dataframe: pd.DataFrame, params: dict) -> dict:
        arrays = {}
        for column in dataframe.columns:
            if not column.startswith("pine_"):
                continue
            series = dataframe[column]
            arrays[column[len("pine_"):]] = (
                series.to_numpy(dtype=bool) if series.dtype == bool
                else series.to_numpy()
            )
        arrays["params"] = params
        arrays["open"] = dataframe["open"].to_numpy(dtype=float)
        arrays["high"] = dataframe["high"].to_numpy(dtype=float)
        arrays["low"] = dataframe["low"].to_numpy(dtype=float)
        arrays["close"] = dataframe["close"].to_numpy(dtype=float)
        return arrays

    # ----------------------------------------------------------------- script
    def pine_script(self, broker, i: int, ctx: dict) -> None:
        history = self._pos_history
        while len(history) <= i:
            history.append(broker.position)
        history[i] = broker.position

        p = ctx["params"]
        position = broker.position
        close_i = ctx["close"][i]
        high_i = ctx["high"][i]
        low_i = ctx["low"][i]
        slow_ema_i = ctx["slow_ema"][i]
        hs_i = ctx["high_short_ema"][i]
        ls_i = ctx["low_short_ema"][i]
        ct_top_i = ctx["ct_band_top"][i]
        ct_bottom_i = ctx["ct_band_bottom"][i]

        need_long = bool(p["needLong"])
        need_short = bool(p["needShort"])
        mid_close = str(p["midClose"])
        use_slow = bool(p["useSlowEMA"])
        s_long_bounce = bool(p["s_longBounce"])
        s_short_bounce = bool(p["s_shortBounce"])
        use_lele = bool(p["useLele"])
        use_bb = bool(p["useBBExtend"])
        rever_band_close = bool(p["reverBandClose"])
        num_lele = LELE_NUM_BARS[str(p["whichLele"])]
        num_bbs = BB_NUM_BARS[str(p["whichBBext"])]
        need_ct_long = bool(p["needCTlong"])
        need_ct_short = bool(p["needCTshort"])
        ct_long_type = str(p["CTlongType"])
        ct_short_type = str(p["CTshortType"])
        always_long = bool(p["alwaysLong"])
        always_short = bool(p["alwaysShort"])
        long_mid_break = bool(ctx["long_mid_break"][i])
        short_mid_break = bool(ctx["short_mid_break"][i])
        long_bounce = bool(ctx["long_bounce"][i])
        short_bounce = bool(ctx["short_bounce"][i])
        os_ob_i = int(ctx["osob"][i])
        rever_color_i = int(ctx["rever_color"][i])
        major_i = float(ctx["major"][i])
        ct_long_tp = float(ctx["ct_long_tp"][i])
        ct_short_tp = float(ctx["ct_short_tp"][i])
        ct_long_close = bool(ctx["ct_long_close"][i])
        ct_short_close = bool(ctx["ct_short_close"][i])

        # ---- longs open ----------------------------------------------------
        # if needLong
        #     if useSlowEMA
        #         if longMidBreak and close > slowEMA and open < highShortEMA
        #             strategy.entry('Long', strategy.long)
        #     else if longMidBreak
        #         strategy.entry('Long', strategy.long)
        if need_long:
            if use_slow:
                if long_mid_break and close_i > slow_ema_i and ctx["open"][i] < hs_i:
                    broker.entry("Long", "long")
            elif long_mid_break:
                broker.entry("Long", "long")
        if position == 0 and s_long_bounce:
            if use_slow:
                if close_i > slow_ema_i and long_bounce:
                    broker.entry("Long", "long")
            elif long_bounce:
                broker.entry("Long", "long")

        # ---- shorts open ---------------------------------------------------
        if need_short:
            if use_slow:
                if short_mid_break and close_i < slow_ema_i and ctx["open"][i] > ls_i:
                    broker.entry("Short", "short")
            elif short_mid_break:
                broker.entry("Short", "short")
        if position == 0 and s_short_bounce:
            if use_slow:
                if close_i < slow_ema_i and short_bounce:
                    broker.entry("Short", "short")
            elif short_bounce:
                broker.entry("Short", "short")

        # ---- how many Leledc / BB exhaustion bars since the entry ----------
        count_long_lele = self._count_bars(
            history, i, ctx["major"], num_lele, use_lele, want=-1.0, limit=200)
        count_short_lele = self._count_bars(
            history, i, ctx["major"], num_lele, use_lele, want=1.0, limit=200)
        count_long_bbs = self._count_bars(
            history, i, ctx["osob"], num_bbs, use_bb, want=COLOUR_YELLOW, limit=200)
        count_short_bbs = self._count_bars(
            history, i, ctx["osob"], num_bbs, use_bb, want=COLOUR_BLUE, limit=200)

        # ---- longs close ---------------------------------------------------
        if position > 0:
            if rever_band_close and rever_color_i == COLOUR_ORANGE:
                broker.close("Long", comment="Close Long")
            if use_bb and num_bbs == 1:
                if os_ob_i == COLOUR_YELLOW:
                    broker.close("Long", comment="Close Long")
                    if need_ct_short and ct_short_type == "BB Exhaustion":
                        if ctx["open"][i] > ct_top_i:
                            broker.entry("Counter Trend Short", "short")
            if use_bb and num_bbs > 1:
                if count_long_bbs == num_bbs:
                    broker.close("Long", comment="Close Long")
                    if need_ct_short and ct_short_type == "BB Exhaustion":
                        if ctx["open"][i] > ct_top_i:
                            broker.entry("Counter Trend Short", "short")
            if use_lele and num_lele == 1:
                if major_i == -1:
                    broker.close("Long", comment="Close Long")
                    if need_ct_short and ct_short_type == "Leledc":
                        if high_i > ct_top_i:
                            broker.entry("Counter Trend Short", "short")
            if use_lele and num_lele > 1:
                if count_long_lele == num_lele:
                    broker.close("Long", comment="Close Long")
                    if need_ct_short and ct_short_type == "Leledc":
                        if high_i > ct_top_i:
                            broker.entry("Counter Trend Short", "short")
            if mid_close == "Nearest band":
                if bool(ctx["cross_dn_top_mb"][i]) or bool(ctx["wiggle_dn_top_mb"][i]):
                    broker.close("Long", comment="Close Long")
            if mid_close == "Opposite band":
                if bool(ctx["cross_dn_bot_mb"][i]) or bool(ctx["wiggle_dn_bot_mb"][i]):
                    broker.close("Long", comment="Close Long")
            if mid_close == "Delayed bars inside":
                if bool(ctx["cross_dn_bot_mb"][i]) or bool(ctx["wiggle_dn_bot_mb"][i]):
                    broker.close("Long", comment="Close Long")
                if self._is_all_mid(ctx, i, int(p["numBars"])):
                    # `open[numBars] > highShortEMA and close[numBars] <
                    # highShortEMA and inMid` -- the band is the CURRENT bar's,
                    # only open/close are `numBars` back.
                    back = i - int(p["numBars"])
                    if back >= 0:
                        if (ctx["open"][back] > hs_i
                                and ctx["close"][back] < hs_i
                                and bool(ctx["in_mid"][i])):
                            broker.close("Long", comment="Close Long")

        # ---- shorts close --------------------------------------------------
        if position < 0:
            if rever_band_close and rever_color_i == COLOUR_PURPLE:
                broker.close("Short", comment="Close Short")
            if use_bb and num_bbs == 1:
                if os_ob_i == COLOUR_BLUE:
                    broker.close("Short", comment="Close Short")
                    if need_ct_long and ct_long_type == "BB Exhaustion":
                        if ctx["open"][i] < ct_bottom_i:
                            broker.entry("Counter Trend Long", "long")
            if use_bb and num_bbs > 1:
                if count_short_bbs == num_bbs:
                    broker.close("Short", comment="Close Short")
                    if need_ct_long and ct_long_type == "BB Exhaustion":
                        if ctx["open"][i] < ct_bottom_i:
                            broker.entry("Counter Trend Long", "long")
            if use_lele and num_lele == 1:
                if major_i == 1:
                    broker.close("Short", comment="Close Short")
                    if need_ct_long and ct_long_type == "Leledc":
                        if low_i < ct_bottom_i:
                            broker.entry("Counter Trend Long", "long")
            if use_lele and num_lele > 1:
                if count_short_lele == num_lele:
                    broker.close("Short", comment="Close Short")
                    if need_ct_long and ct_long_type == "Leledc":
                        if low_i < ct_bottom_i:
                            broker.entry("Counter Trend Long", "long")
            if mid_close == "Nearest band":
                if bool(ctx["cross_up_bot_mb"][i]) or bool(ctx["wiggle_up_bot_mb"][i]):
                    broker.close("Short", comment="Close Short")
            if mid_close == "Opposite band":
                if bool(ctx["cross_up_top_mb"][i]) or bool(ctx["wiggle_up_top_mb"][i]):
                    broker.close("Short", comment="Close Short")
            if mid_close == "Delayed bars inside":
                if bool(ctx["cross_up_top_mb"][i]) or bool(ctx["wiggle_up_top_mb"][i]):
                    broker.close("Short", comment="Close Short")
                if self._is_all_mid(ctx, i, int(p["numBars"])):
                    # `open[numBars] < lowShortEMA and close[numBars] >
                    # lowShortEMA and inMid`; the band is the current bar's.
                    back = i - int(p["numBars"])
                    if back >= 0:
                        if (ctx["open"][back] < ls_i
                                and ctx["close"][back] > ls_i
                                and bool(ctx["in_mid"][i])):
                            broker.close("Short", comment="Close Short")

        # ---- counter-trend longs, open then closed -------------------------
        ct_long_sl = self._flat_stop(broker, p["i_CTlongSL"], -1.0)
        if need_ct_long and position == 0:
            if ct_long_type == "Leledc":
                if major_i == 1:
                    if low_i < ct_bottom_i:
                        broker.entry("Counter Trend Long", "long")
            elif os_ob_i == COLOUR_BLUE:
                broker.entry("Counter Trend Long", "long")
        if position > 0 and self._last_open_entry_id(broker) == "Counter Trend Long":
            self._place_counter_trend_exit(
                broker, "Counter Trend Long", ct_long_sl, ct_long_tp,
                float(p["i_CTlongSL"]),
            )
            if ct_long_close:
                broker.close("Counter Trend Long", comment="Close CT Long")

        # ---- counter-trend shorts, open then closed ------------------------
        ct_short_sl = self._flat_stop(broker, p["i_CTshortSL"], 1.0)
        if need_ct_short and position == 0:
            if ct_short_type == "Leledc":
                if major_i == -1:
                    if high_i > ct_top_i:
                        broker.entry("Counter Trend Short", "short")
            elif os_ob_i == COLOUR_YELLOW:
                broker.entry("Counter Trend Short", "short")
        if position < 0 and self._last_open_entry_id(broker) == "Counter Trend Short":
            self._place_counter_trend_exit(
                broker, "Counter Trend Short", ct_short_sl, ct_short_tp,
                float(p["i_CTshortSL"]),
            )
            if ct_short_close:
                broker.close("Counter Trend Short", comment="Close CT Short")

        # ---- default positioning ------------------------------------------
        if always_long and not always_short and position == 0:
            if use_slow:
                if close_i > slow_ema_i:
                    broker.entry("Default Long", "long")
            else:
                broker.entry("Default Long", "long")
        if always_short and not always_long and position == 0:
            if use_slow:
                if close_i < slow_ema_i:
                    broker.entry("Default Short", "short")
            else:
                broker.entry("Default Short", "short")

    # ---------------------------------------------------------------- helpers
    @staticmethod
    def _count_bars(history, i, series, target, enabled, want, limit):
        """The source's Leledc / BB counting `while` loops.

        `strategy.position_size[k]` walking back from bar `i`; the loop breaks on
        a bar with no position, on the first bar of the series (`bar_index == 0`)
        or once the wanted number of marker bars has been seen.
        """
        if not enabled or target <= 1:
            return 0
        count = 0
        k = 0
        while k <= limit:
            idx = i - k
            value = history[idx] if 0 <= idx < len(history) else None
            if value is not None and value <= 0:
                break
            if idx == 0:
                break
            if 0 <= idx < len(series) and series[idx] == want:
                count += 1
            if count == target:
                break
            k += 1
        return count

    @staticmethod
    def _is_all_mid(ctx, i, num_bars):
        """`isAllMid()`: no middle-band breakout on the last `num_bars` bars."""
        for t in range(0, num_bars + 1):
            idx = i - t
            if idx < 0:
                continue
            if bool(ctx["long_mid_break"][idx]) or bool(ctx["short_mid_break"][idx]):
                return False
        return True

    @staticmethod
    def _last_open_entry_id(broker):
        """`strategy.opentrades.entry_id(strategy.opentrades - 1)`.

        The newest open entry, or None when flat (Pine's na, which makes the
        enclosing comparison false). The broker exposes the count publicly but
        not the id, so the engine's own open-entry ledger is read here.
        """
        entries = getattr(broker, "_open_entries", None)
        if not entries:
            return None
        return entries[-1].get("id")

    @staticmethod
    def _flat_stop(broker, percent, side):
        """`strategy.position_avg_price * (1 -/+ SL%)`, na when flat."""
        price = broker.position_avg_price
        if price is None or not np.isfinite(price):
            return float("nan")
        return price * (1.0 + side * float(percent) / 100.0) if side > 0 \
            else price * (1.0 - float(percent) / 100.0)

    @staticmethod
    def _place_counter_trend_exit(broker, entry_id, stop, take, percent):
        """`strategy.exit(id, stop=CTlongSL, limit=CTlongTP)` for a CT trade.

        The source guards this on `strategy.opentrades > 0`, so one of the two
        levels is always present; a call with neither would create no order in
        Pine, and none is placed here either.
        """
        percent = float(percent)
        na_take = not np.isfinite(take)
        if percent > 0:
            broker.exit(entry_id, from_entry=entry_id, stop=stop,
                        limit=None if na_take else float(take))
        elif percent == 0 and not na_take:
            broker.exit(entry_id, from_entry=entry_id, limit=float(take))
