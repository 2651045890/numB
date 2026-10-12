"""Port of sources/SM_5dfe21afbb9c15ca.pine (batch_001/EMA-ADX-VOL-加密货币杀手EMA-ADX-VOL-CRYPTO-KILLER.md).

Pine v4 ("EMA/ADX/VOL-CRYPTO KILLER [15M]" by BabehDyo). Both sides. A LONG
needs, on the same bar, a strong DI+ ADX, price above ALL FIVE EMAs (8/13/21/34/
55), the Range Filter's up-leg and a volume burst; a SHORT is the mirror. Two
volume thresholds exist and either one qualifies. The block below is the source
verbatim, in evaluation order:

    up = change(high); down = -change(low)
    plusDM  = na(up)   ? na : (up   > down and up   > 0 ? up   : 0)
    minusDM = na(down) ? na : (down > up   and down > 0 ? down : 0)
    truerange = rma(tr, ADX_len)
    _plus  = fixnan(100 * rma(plusDM,  ADX_len) / truerange)
    _minus = fixnan(100 * rma(minusDM, ADX_len) / truerange)
    sum = _plus + _minus
    _adx = 100 * rma(abs(_plus - _minus) / (sum == 0 ? 1 : sum), ADX_len)
        -> [DIPlusC, DIMinusC, ADXC]
    ... calcADX_Masanakamura(ADX_len) -> [DIPlusM, DIMinusM, ADXM]
    DIPlus = ADX_options == "CLASSIC" ? DIPlusC : DIPlusM      (and the same
    for DIMinus / ADX, off the same ADX_options input)

    EMA1..EMA5 = ema(close, 8/13/21/34/55)
    L_ema = EMA1 < close and ... and EMA5 < close
    S_ema = EMA1 > close and ... and EMA5 > close

    Range_filter(src, 15, 2.6) -> [smoothrng, filt, upward, downward]
    hband = filt + smoothrng ; lband = filt - smoothrng
    L_RF = high > hband and upward   > 0
    S_RF = low  < lband and downward > 0

    Volume_condt  = volume > sma(volume, 20) * 3.2
    Volume_condt1 = volume > sma(volume, 22) * 1.9

    L_1 = L_adx and Volume_condt  and L_RF and L_ema
    L_2 = L_adx and  L_RF and L_ema and Volume_condt1
    L_basic_condt = L_1 or L_2                  (S_* mirrored)

    if L_basic_condt
        strategy.entry("LONG", strategy.long)
    if S_basic_condt
        strategy.entry("SHORT", strategy.short)
    strategy.exit("TP_L", "LONG",  profit=..., limit=..., loss=...)
    strategy.exit("TP_S", "SHORT", profit=..., limit=..., loss=...)

Both ADX implementations are COMPUTED every bar -- the CLASSIC one is not dead
code behind the default `ADX_options = "MASANAKAMURA"`, it is one arm of the
ternary that selects DIPlus / DIMinus / ADX.

The source's own bookkeeping (`CondIni_long` / `CondIni_short`, `nLongs` /
`nShorts`, `last_open_longCondition` / `last_open_shortCondition`, `sum_long` /
`sum_short`, `Position_Price` and the TP/SL hit latches `Final_*`) drives ONLY
the `profit` / `loss` / `limit` arguments of the two `strategy.exit` calls. It
places no order of its own; it is reproduced bar by bar in `pine_script` in the
source's own order.

`time` is the only clock the source reads (to order "which happened last"). It
appears ONLY as the value assigned by the eight `? time : nz(...)` statements
(lines 176-181, 212-213, 242-243 -- measured by grep) and those values are later
only ever COMPARED with `>`. A strictly increasing integer surrogate therefore
preserves every comparison exactly; the port uses bar position + 1, the +1
keeping every value clear of the `nz(na) -> 0` sentinel.

FIDELITY, the parts that are modelled rather than certified:

* `fixnan` is not in pine_ta and is written out as a forward fill.
* `tr` is called BARE inside calcADX (`rma(tr, _len)`), i.e. Pine's
  handle_na=false default, so `pine_ta.pine_tr(frame, handle_na=False)` is the
  counterpart. PINE_SEMANTICS.md 3.7 records that the modelled pine_tr returns
  high-low on the first bar where Pine returns na, which can move the ta.rma
  seed by one bar. Not corrected (shared layer).
* `strategy.exit`'s `profit` / `loss` are tick distances (PINE_SEMANTICS.md 3.5)
  and are passed through as ticks; the engine converts them with `mintick`.
* `pyramiding = 1` is declared. The engine honours it, but the Freqtrade side
  cannot hold a second same-direction position
  (`position_adjustment_enable = False`, PINE_SEMANTICS.md section 2 item 10),
  so that part of the source is NOT reproduced end to end. Stated, not hidden.
"""
import math

import numpy as np
import pandas as pd
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


def _fixnan(series: pd.Series) -> pd.Series:
    """Pine `fixnan`: replace na with the last non-na value."""
    return series.ffill()


def _nz(value) -> float:
    """Pine `nz` on a scalar: na (NaN) becomes 0."""
    if value is None:
        return 0.0
    value = float(value)
    return value if math.isfinite(value) else 0.0


def _adx_classic(dataframe: pd.DataFrame, length: int):
    """Pine `calcADX(_len)` unchanged, returning (DIPlus, DIMinus, ADX)."""
    high, low = dataframe["high"], dataframe["low"]
    # up = change(high) ; down = -change(low)
    up = ta.pine_change(high, 1)
    down = -ta.pine_change(low, 1)
    # plusDM  = na(up)   ? na : (up   > down and up   > 0 ? up   : 0)
    # minusDM = na(down) ? na : (down > up   and down > 0 ? down : 0)
    # `up.where(cond, 0)` would turn the warmup na into 0, so the na is put
    # back afterwards -- Pine returns na there, and pine_rma skips na.
    plus_dm = up.where((up > down) & (up > 0.0), 0.0).where(up.notna(), np.nan)
    minus_dm = down.where((down > up) & (down > 0.0), 0.0).where(down.notna(), np.nan)
    # truerange = rma(tr, _len) -- bare `tr`, i.e. handle_na = false.
    truerange = ta.pine_rma(ta.pine_tr(dataframe, handle_na=False), length)
    # _plus = fixnan(100 * rma(plusDM, _len) / truerange) (and the mirror).
    # Division by zero is na on Pine; +/-inf is mapped onto na before fixnan,
    # which then feeds it exactly like a warmup na.
    plus = _fixnan(
        (100.0 * ta.pine_rma(plus_dm, length) / truerange).replace(
            [np.inf, -np.inf], np.nan
        )
    )
    minus = _fixnan(
        (100.0 * ta.pine_rma(minus_dm, length) / truerange).replace(
            [np.inf, -np.inf], np.nan
        )
    )
    # sum = _plus + _minus ; _adx = 100 * rma(abs(_plus - _minus) /
    #                                          (sum == 0 ? 1 : sum), _len)
    total = plus + minus
    divisor = total.where(total != 0.0, 1.0)
    adx = 100.0 * ta.pine_rma((plus - minus).abs() / divisor, length)
    return plus, minus, adx


def _adx_masanakamura(dataframe: pd.DataFrame, length: int):
    """Pine `calcADX_Masanakamura(_len)`, returning (DIP, DIM, adx).

    The three `Smoothed*` locals are declared WITHOUT `var` and re-initialised
    to 0.0 on every bar, but the `:=` lines read their own `[1]` history, so the
    recursion carries across bars from a zero seed:

        Smoothed := nz(Smoothed[1]) - nz(Smoothed[1]) / _len + increment

    which is Wilder smoothing seeded at 0, NOT pine_ta.pine_rma's SMA seed --
    so it is written out here rather than mapped onto pine_rma. `nz` on the
    `[1]` references of high / low / close is 0 on the first bar.
    """
    high = dataframe["high"].to_numpy(dtype=float)
    low = dataframe["low"].to_numpy(dtype=float)
    close = dataframe["close"].to_numpy(dtype=float)
    n = len(high)
    dip = np.full(n, np.nan)
    dim = np.full(n, np.nan)
    dx = np.full(n, np.nan)
    smoothed_tr = 0.0
    smoothed_plus = 0.0
    smoothed_minus = 0.0
    for i in range(n):
        previous_high = high[i - 1] if i >= 1 else 0.0  # nz(high[1])
        previous_low = low[i - 1] if i >= 1 else 0.0  # nz(low[1])
        previous_close = close[i - 1] if i >= 1 else 0.0  # nz(close[1])
        # TrueRange = max(max(high - low, abs(high - nz(close[1]))),
        #                 abs(low - nz(close[1])))
        true_range = max(
            max(high[i] - low[i], abs(high[i] - previous_close)),
            abs(low[i] - previous_close),
        )
        up_move = high[i] - previous_high
        down_move = previous_low - low[i]
        # DirectionalMovementPlus  = high-nz(high[1]) > nz(low[1])-low
        #                             ? max(high-nz(high[1]), 0) : 0
        # DirectionalMovementMinus = nz(low[1])-low > high-nz(high[1])
        #                             ? max(nz(low[1])-low, 0) : 0
        movement_plus = max(up_move, 0.0) if up_move > down_move else 0.0
        movement_minus = max(down_move, 0.0) if down_move > up_move else 0.0
        smoothed_tr = smoothed_tr - smoothed_tr / length + true_range
        smoothed_plus = smoothed_plus - smoothed_plus / length + movement_plus
        smoothed_minus = smoothed_minus - smoothed_minus / length + movement_minus
        # DIP = SDMP / STR * 100 ; DIM = SDMM / STR * 100 ; a zero STR is na.
        dip[i] = (smoothed_plus / smoothed_tr * 100.0) if smoothed_tr != 0.0 else np.nan
        dim[i] = (smoothed_minus / smoothed_tr * 100.0) if smoothed_tr != 0.0 else np.nan
        # DX = abs(DIP-DIM) / (DIP+DIM) * 100
        denominator = dip[i] + dim[i]
        dx[i] = (
            abs(dip[i] - dim[i]) / denominator * 100.0
            if denominator != 0.0 and math.isfinite(denominator)
            else np.nan
        )
    # adx = sma(DX, _len) -- SMA, not rma, in this variant.
    adx = ta.pine_sma(pd.Series(dx, index=dataframe.index), length)
    return (
        pd.Series(dip, index=dataframe.index),
        pd.Series(dim, index=dataframe.index),
        adx,
    )


def _range_filter(src: pd.Series, per_: int, mult: float):
    """Pine `Range_filter(_src, _per_, _mult)` -> the four returned series.

    `_filt`, `_upward` and `_downward` are reassigned through `:=` and read
    their own `[1]` history, and `_upward` / `_downward` are `var` (seeded 0),
    so the whole thing is one pass in bar order. `_filt` is NOT `var`: it is
    re-derived from `_src` each bar, but the assignment reads `nz(_filt[1])`,
    which is the previous bar's value, so the recursion still carries.

    Every comparison involving na is false on Pine (the ternary falls through
    to its else arm), which is what plain NaN comparisons do here.
    """
    wper = (per_ * 2) - 1
    # avrng = ema(abs(_src - _src[1]), _per_)
    avrng = ta.pine_ema((src - src.shift(1)).abs(), per_)
    # _smoothrng = ema(avrng, wper) * _mult
    smoothrng = ta.pine_ema(avrng, wper) * mult

    values = src.to_numpy(dtype=float)
    smooth = smoothrng.to_numpy(dtype=float)
    n = len(values)
    filt = np.full(n, np.nan)
    upward = np.zeros(n)
    downward = np.zeros(n)
    previous_filt = np.nan
    previous_upward = 0.0
    previous_downward = 0.0
    for i in range(n):
        base = _nz(previous_filt)
        # _filt := _src > nz(_filt[1])
        #     ? ((_src - _smoothrng) < nz(_filt[1]) ? nz(_filt[1]) : (_src - _smoothrng))
        #     : ((_src + _smoothrng) > nz(_filt[1]) ? nz(_filt[1]) : (_src + _smoothrng))
        if values[i] > base:
            candidate = values[i] - smooth[i]
            current = base if candidate < base else candidate
        else:
            candidate = values[i] + smooth[i]
            current = base if candidate > base else candidate
        filt[i] = current
        # _upward := _filt > _filt[1] ? nz(_upward[1]) + 1
        #                              : _filt < _filt[1] ? 0 : nz(_upward[1])
        if current > previous_filt:
            upward[i] = previous_upward + 1
        elif current < previous_filt:
            upward[i] = 0.0
        else:
            upward[i] = previous_upward
        # _downward := _filt < _filt[1] ? nz(_downward[1]) + 1
        #                                : _filt > _filt[1] ? 0 : nz(_downward[1])
        if current < previous_filt:
            downward[i] = previous_downward + 1
        elif current > previous_filt:
            downward[i] = 0.0
        else:
            downward[i] = previous_downward
        previous_filt = current
        previous_upward = upward[i]
        previous_downward = downward[i]
    index = src.index
    return (
        smoothrng,
        pd.Series(filt, index=index),
        pd.Series(upward, index=index),
        pd.Series(downward, index=index),
    )


class SMEmaAdxVolCryptoKiller_5dfe21(PinePortBase, IStrategy):
    source_id = "SM_5dfe21afbb9c15ca"
    source_file = "EMA-ADX-VOL-加密货币杀手EMA-ADX-VOL-CRYPTO-KILLER.md"
    # /*backtest ... period: 1d, basePeriod: 1h
    timeframe = "1d"
    can_short = True
    source_defaults = {
        # input(open, title="  Source")
        "src": "open",
        "ADX_options": "MASANAKAMURA",
        "ADX_len": 21,
        "th": 20,
        "Length_ema1": 8,
        "Length_ema2": 13,
        "Length_ema3": 21,
        "Length_ema4": 34,
        "Length_ema5": 55,
        "per_": 15,
        "mult": 2.6,
        "volume_f": 3.2,
        "sma_length": 20,
        "volume_f1": 1.9,
        "sma_length1": 22,
        "tp_long0": 0.9,
        "tp_short0": 0.9,
        "sl0": 4.2,
    }
    source_qty_type = "percent_of_equity"
    source_qty_value = 100.0
    source_commission_percent = 0.03
    source_pyramiding = 1
    source_initial_capital = 10000.0
    # strategy.exit carries `loss=` legs, so a stop leg does exist.
    source_reproduce_stops = True
    source_fidelity_notes = [
        "BOTH ADX implementations are live code. The source computes "
        "[DIPlusC,DIMinusC,ADXC] = calcADX(ADX_len) and "
        "[DIPlusM,DIMinusM,ADXM] = calcADX_Masanakamura(ADX_len) on every bar "
        "and only then selects with `ADX_options == \"CLASSIC\" ? ... : ...`. "
        "The port computes both; with the default ADX_options = MASANAKAMURA "
        "the CLASSIC arm is still computed, exactly as in the source.",
        "calcADX_Masanakamura is NOT ta.rma. Its three Smoothed* locals are "
        "declared without `var` and re-initialised to 0.0 each bar, but the "
        "`:=` lines read their own [1] history, so they are a Wilder recursion "
        "SEEDED AT 0 covering the whole series: "
        "S := nz(S[1]) - nz(S[1])/_len + increment. pine_ta.pine_rma seeds with "
        "the SMA of the first _len values instead, so it is NOT used for this "
        "branch; the recursion is written out in _adx_masanakamura. The "
        "variant's adx = sma(DX, _len) is an SMA (pine_ta.pine_sma), unlike the "
        "CLASSIC arm's rma.",
        "calcADX (CLASSIC) uses bare `tr` (rma(tr, _len)), i.e. Pine's "
        "handle_na = false; pine_ta.pine_tr(frame, handle_na=False) is the "
        "counterpart and pine_atr is deliberately not used. "
        "PINE_SEMANTICS.md 3.7 records that the modelled pine_tr returns "
        "high-low on the first bar where Pine returns na, which can shift the "
        "ta.rma seed by one bar and leave a boundary difference in the "
        "CLASSIC series. Not corrected (shared layer).",
        "plusDM / minusDM are na on the first bar (na(up) / na(down)) and "
        "pine_rma skips an na observation without advancing its window, so the "
        "CLASSIC DI seed starts one bar later than a naive read. Written out "
        "with the na preserved rather than coalesced to 0.",
        "`fixnan` is not in pine_ta; it is written out as a forward fill, which "
        "is its documented behaviour.",
        "Division by zero is na in Pine. In calcADX the DIVISION is wrapped in "
        "fixnan, so +/-inf is mapped onto na BEFORE the fixnan (an inf would "
        "otherwise be carried forward as a value), and `sum == 0 ? 1 : sum` is "
        "kept as written. In calcADX_Masanakamura, DIP / DIM with a zero "
        "SmoothedTrueRange and DX with DIP+DIM == 0 are na. The zero "
        "denominators are not expected on BTC data; the masking is explicit "
        "rather than left to IEEE.",
        "Range_filter's `_filt`, `_upward` and `_downward` are recursions in "
        "bar order: `_filt` is not `var` but still reads `nz(_filt[1])`, so it "
        "carries, and `_upward` / `_downward` are `var float = 0.0`, so their "
        "bar-0 history is na and nz() makes it 0. Reproduced as one pass in "
        "bar order in _range_filter.",
        "`time` -- used only to order 'which happened last' in the CondIni / "
        "last_open / last_*_tp / last_*_sl bookkeeping -- is replaced by bar "
        "position + 1. Measured by grep, `time` occurs only as the value "
        "assigned by the eight `? time : nz(...)` statements (lines 176-181, "
        "212-213, 242-243); nothing else reads it, and the assigned values are "
        "only ever compared with `>`. A strictly increasing surrogate "
        "therefore preserves every comparison, and the +1 keeps each value "
        "clear of the nz(na) -> 0 sentinel, which a 0-based index would not.",
        "CondIni_long and CondIni_short have IDENTICAL update rules "
        "(`longCond[1] ? 1 : shortCond[1] ? -1 : nz(...)`) over identical "
        "inputs, so the two variables hold the same value on every bar. Both "
        "are still computed and carried separately, as the source does.",
        "Dead code, computed but never read: `last_Final_longCondition` and "
        "`last_Final_shortCondition` are assigned on every bar (lines 180-181) "
        "and read nowhere; they are computed here and carried in the state "
        "dict. The two `var bool _Final_longCondition` / "
        "`_Final_shortCondition` declarations on line 146 are never read AND "
        "never assigned, so they have no value to compute and are represented "
        "by this note instead. The same holds for `Final_Long_sl0` / "
        "`Final_Short_sl0` (declared line 204, measured by grep to appear "
        "nowhere else).",
        "`profit` / `loss` are tick distances (PINE_SEMANTICS.md 3.5) and are "
        "passed to broker.exit AS TICKS; the engine multiplies by mintick "
        "(source_mintick 0.1, the BTC/USDT:USDT quote increment, which the "
        "source never states -- it reads syminfo.mintick off the symbol).",
        "The source's `profit` / `loss` are derived from "
        "`last_open_longCondition` / `last_open_shortCondition`, which are "
        "`nz(...)`-carried and therefore sit at 0.0 from bar 0, before the "
        "first long/short signal. Both tick distances are then 0, i.e. the "
        "exit's stop and take-profit legs rest AT the position's average entry "
        "price and the engine will exit a position as soon as its own entry "
        "price is touched. That is the source's own arithmetic, not a port "
        "choice; it is left as it is. Whether the original platform treats a "
        "0-tick leg as a level or as an inert leg is NOT published -- the "
        "engine's _order_stop_limit applies any finite tick distance including "
        "0, and that is the model used here.",
        "`limit = nLongs >= 1 ? strategy.position_avg_price * (1 + tp_long) : "
        "na` is an absolute PRICE, not a tick distance. It is passed as "
        "`limit=None` when it resolves to na (nLongs < 1, or flat), because the "
        "engine's _order_stop_limit tightens limit against the profit leg and a "
        "NaN there would poison the comparison.",
        "The two strategy.exit calls are placed on EVERY bar with the ids "
        "TP_L / TP_S, as in the source; the engine keeps one order per id and "
        "replaces it (PINE_SEMANTICS.md 3.6 discusses what a same-id "
        "replacement means for a trail; there is no trail here). While the "
        "entry a call names is not open the order neither fills nor publishes "
        "a level (PINE_SEMANTICS.md 1.12).",
        "pyramiding = 1 is declared. The engine honours it (a second "
        "same-direction entry stacks), but the framework side cannot hold two "
        "positions: PinePortBase sets position_adjustment_enable = False. "
        "PINE_SEMANTICS.md section 2 item 10 quantifies this on another port. "
        "So stacked entries are NOT reproduced end to end -- recorded as a "
        "known, unclosed gap rather than claimed.",
        "calc_on_order_fills = false in the source, which matches the engine's "
        "once-per-bar evaluation; slippage = 0 and commission is the source's "
        "0.03 percent. Default sizing is percent_of_equity 100 -- see "
        "PINE_SEMANTICS.md 1.4/1.5 for the framework-side sizing basis.",
        "MD/SOURCE DISAGREEMENT (prose vs code): the md says '当5条EMA均线全部"
        "上涨时判断为多头趋势形成' / 'when all 5 EMAs rise, it is judged as a "
        "bullish trend formation'. The CODE tests none of that: L_ema is "
        "`EMA1 < close and ... and EMA5 < close` (price ABOVE all five EMAs) "
        "and S_ema is `EMA1 > close and ... and EMA5 > close` (price BELOW all "
        "five). Code followed; the prose describes a different test.",
        "MEASURED: the source declares 18 input() calls (grep -c 'input(') and "
        "the md's argument table lists 18 rows whose defaults all match: open, "
        "8, 13, 21, 34, 55, MASANAKAMURA, 21, 20, 15, 2.6, 3.2, 20, 1.9, 22, "
        "0.9, 0.9, 4.2. The md's embedded PineScript block is byte-identical to "
        "sources/SM_5dfe21afbb9c15ca.pine.",
        "plot(...), plotshape(...) and barcolor(...) (Bar_color) are "
        "display-only and are reproduced as no code. L_tp, S_tp, tplLevel and "
        "tpsLevel exist only to feed plot(), per grep of their four names.",
        "The backtest window in the header (2022-11-28 to 2023-12-04) is not "
        "applied: the port runs on whatever range the caller supplies.",
        "Leverage, margin, liquidation and funding are not modelled, and the "
        "venue's contract-step rounding of order quantities is not modelled "
        "either.",
    ]

    def pine_indicators(self, dataframe, params):
        length = int(params["ADX_len"])
        threshold = float(params["th"])
        src = ta.pine_source(dataframe, str(params["src"]))
        close = dataframe["close"]
        volume = dataframe["volume"]

        # [DIPlusC, DIMinusC, ADXC] = calcADX(ADX_len)
        # [DIPlusM, DIMinusM, ADXM] = calcADX_Masanakamura(ADX_len)
        plus_c, minus_c, adx_c = _adx_classic(dataframe, length)
        plus_m, minus_m, adx_m = _adx_masanakamura(dataframe, length)
        # DIPlus / DIMinus / ADX = ADX_options == "CLASSIC" ? C : M
        if str(params["ADX_options"]) == "CLASSIC":
            di_plus, di_minus, adx = plus_c, minus_c, adx_c
        else:
            di_plus, di_minus, adx = plus_m, minus_m, adx_m
        dataframe["pine_diplus_classic"] = plus_c
        dataframe["pine_diminus_classic"] = minus_c
        dataframe["pine_adx_classic"] = adx_c
        dataframe["pine_diplus_masanakamura"] = plus_m
        dataframe["pine_diminus_masanakamura"] = minus_m
        dataframe["pine_adx_masanakamura"] = adx_m
        dataframe["pine_diplus"] = di_plus
        dataframe["pine_diminus"] = di_minus
        dataframe["pine_adx"] = adx
        # L_adx = DIPlus > DIMinus and ADX > th  (na compares false)
        dataframe["pine_l_adx"] = ((di_plus > di_minus) & (adx > threshold)).fillna(False)
        dataframe["pine_s_adx"] = ((di_plus < di_minus) & (adx > threshold)).fillna(False)

        # EMA1..5 = ema(close, Length_emaN); L_ema / S_ema against close.
        emas = [
            ta.pine_ema(close, int(params[f"Length_ema{n}"])) for n in range(1, 6)
        ]
        for n, series in enumerate(emas, start=1):
            dataframe[f"pine_ema{n}"] = series
        # L_ema = EMA1 < close and EMA2 < close and ... and EMA5 < close
        l_ema = pd.Series(True, index=dataframe.index)
        s_ema = pd.Series(True, index=dataframe.index)
        for series in emas:
            l_ema &= series < close
            s_ema &= series > close
        dataframe["pine_l_ema"] = l_ema.fillna(False)
        dataframe["pine_s_ema"] = s_ema.fillna(False)

        # Range_filter(src, per_, mult) -> [smoothrng, filt, upward, downward]
        smoothrng, filt, upward, downward = _range_filter(
            src, int(params["per_"]), float(params["mult"])
        )
        dataframe["pine_smoothrng"] = smoothrng
        dataframe["pine_filt"] = filt
        dataframe["pine_upward"] = upward
        dataframe["pine_downward"] = downward
        # hband = filt + smoothrng ; lband = filt - smoothrng
        hband = filt + smoothrng
        lband = filt - smoothrng
        high, low = dataframe["high"], dataframe["low"]
        # L_RF = high > hband and upward > 0 ; S_RF = low < lband and downward > 0
        dataframe["pine_l_rf"] = ((high > hband) & (upward > 0)).fillna(False)
        dataframe["pine_s_rf"] = ((low < lband) & (downward > 0)).fillna(False)

        # Volume_condt = volume > sma(volume, sma_length) * volume_f
        # Volume_condt1 = volume > sma(volume, sma_length1) * volume_f1
        volume_condt = volume > ta.pine_sma(volume, int(params["sma_length"])) * float(
            params["volume_f"]
        )
        volume_condt1 = volume > ta.pine_sma(
            volume, int(params["sma_length1"])
        ) * float(params["volume_f1"])
        dataframe["pine_volume_condt"] = volume_condt.fillna(False)
        dataframe["pine_volume_condt1"] = volume_condt1.fillna(False)

        # L_1 = L_adx and Volume_condt and L_RF and L_ema
        # L_2 = L_adx and L_RF and L_ema and Volume_condt1
        # L_basic_condt = L_1 or L_2      (S_* mirrored)
        l_base = dataframe["pine_l_adx"] & dataframe["pine_l_rf"] & dataframe["pine_l_ema"]
        s_base = dataframe["pine_s_adx"] & dataframe["pine_s_rf"] & dataframe["pine_s_ema"]
        dataframe["pine_l_basic_condt"] = l_base & (
            dataframe["pine_volume_condt"] | dataframe["pine_volume_condt1"]
        )
        dataframe["pine_s_basic_condt"] = s_base & (
            dataframe["pine_volume_condt"] | dataframe["pine_volume_condt1"]
        )
        return dataframe

    def pine_context(self, dataframe, params):
        # Bar position + 1 stands in for Pine's `time`: it is assigned by the
        # eight `? time :` statements and only ever compared with `>`.
        time = np.arange(len(dataframe), dtype=float) + 1.0
        return {
            "high": dataframe["high"].to_numpy(dtype=float),
            "low": dataframe["low"].to_numpy(dtype=float),
            "close": dataframe["close"].to_numpy(dtype=float),
            "time": time,
            "l_basic_condt": dataframe["pine_l_basic_condt"].to_numpy(dtype=bool),
            "s_basic_condt": dataframe["pine_s_basic_condt"].to_numpy(dtype=bool),
            "tp_long0": float(params["tp_long0"]),
            "tp_short0": float(params["tp_short0"]),
            "sl0": float(params["sl0"]),
            "state": {
                # var int CondIni_long = 0, var int CondIni_short = 0
                "cond_ini_long": 0,
                "cond_ini_short": 0,
                # var float sum_long = 0.0, var float sum_short = 0.0
                "sum_long": 0.0,
                "sum_short": 0.0,
                # var float Position_Price = 0.0 (overwritten every bar)
                "position_price": float("nan"),
                "fixnan_position_price": float("nan"),
                # var float last_open_longCondition = na (and the short)
                "last_open_long": float("nan"),
                "last_open_short": float("nan"),
                # var int last_longCondition = na (and the short)
                "last_long": float("nan"),
                "last_short": float("nan"),
                # var int last_Final_longCondition = na -- written, never read
                "last_final_long": float("nan"),
                "last_final_short": float("nan"),
                # var int nLongs = na, var int nShorts = na
                "n_longs": float("nan"),
                "n_shorts": float("nan"),
                # var bool long_tp / short_tp (assigned every bar)
                "long_tp": False,
                "short_tp": False,
                # var int last_long_tp / last_short_tp / last_long_sl / last_short_sl
                "last_long_tp": float("nan"),
                "last_short_tp": float("nan"),
                "last_long_sl": float("nan"),
                "last_short_sl": float("nan"),
                # var bool Final_Long_tp / Final_Short_tp / ..._sl
                "final_long_tp": False,
                "final_short_tp": False,
                "final_long_sl": False,
                "final_short_sl": False,
            },
        }

    def pine_script(self, broker, i, ctx):
        state = ctx["state"]
        high = float(ctx["high"][i])
        low = float(ctx["low"][i])
        close_prev = float(ctx["close"][i - 1]) if i >= 1 else float("nan")
        now = float(ctx["time"][i])
        # longCond := L_basic_condt ; shortCond := S_basic_condt
        long_cond = bool(ctx["l_basic_condt"][i])
        short_cond = bool(ctx["s_basic_condt"][i])
        # longCond[1] / shortCond[1]: na on bar 0, i.e. false.
        previous_long_cond = bool(ctx["l_basic_condt"][i - 1]) if i >= 1 else False
        previous_short_cond = bool(ctx["s_basic_condt"][i - 1]) if i >= 1 else False

        # CondIni_long := longCond[1] ? 1 : shortCond[1] ? -1 : nz(CondIni_long[1])
        # CondIni_short := longCond[1] ? 1 : shortCond[1] ? -1 : nz(CondIni_short[1])
        previous_cond_ini_long = state["cond_ini_long"]
        previous_cond_ini_short = state["cond_ini_short"]
        if previous_long_cond:
            cond_ini_long = 1
            cond_ini_short = 1
        elif previous_short_cond:
            cond_ini_long = -1
            cond_ini_short = -1
        else:
            cond_ini_long = previous_cond_ini_long
            cond_ini_short = previous_cond_ini_short

        # longCondition = (longCond[1] and nz(CondIni_long[1]) == -1)
        # shortCondition = (shortCond[1] and nz(CondIni_short[1]) == 1)
        long_condition = previous_long_cond and previous_cond_ini_long == -1
        short_condition = previous_short_cond and previous_cond_ini_short == 1

        # last_open_longCondition := longCondition ? close[1] : nz(last_open_longCondition[1])
        previous_last_open_long = _nz(state["last_open_long"])
        previous_last_open_short = _nz(state["last_open_short"])
        last_open_long = close_prev if long_condition else previous_last_open_long
        last_open_short = close_prev if short_condition else previous_last_open_short
        # last_longCondition := longCondition ? time : nz(last_longCondition[1])
        previous_last_long = _nz(state["last_long"])
        previous_last_short = _nz(state["last_short"])
        last_long = now if long_condition else previous_last_long
        last_short = now if short_condition else previous_last_short
        # in_longCondition = last_longCondition > last_shortCondition
        in_long = last_long > last_short
        in_short = last_short > last_long
        # last_Final_longCondition := longCondition ? time : nz(...)  (dead code)
        last_final_long = (
            now if long_condition else _nz(state["last_final_long"])
        )
        last_final_short = (
            now if short_condition else _nz(state["last_final_short"])
        )
        # nLongs := nz(nLongs[1]) ; nShorts := nz(nShorts[1])
        n_longs = _nz(state["n_longs"])
        n_shorts = _nz(state["n_shorts"])
        sum_long = _nz(state["sum_long"])
        sum_short = _nz(state["sum_short"])
        if long_condition:
            n_longs = n_longs + 1
            n_shorts = 0
            sum_long = previous_last_open_long + sum_long
            sum_short = 0.0
        if short_condition:
            n_longs = 0
            n_shorts = n_shorts + 1
            sum_short = previous_last_open_short + sum_short
            sum_long = 0.0
        # Position_Price := nz(Position_Price[1])   <- overwritten by the next
        # statement, kept here so the two-assignment shape is visible.
        # Position_Price := longCondition ? sum_long/nLongs
        #                                   : shortCondition ? sum_short/nShorts : na
        if long_condition:
            position_price = sum_long / n_longs
        elif short_condition:
            position_price = sum_short / n_shorts
        else:
            position_price = float("nan")
        fixnan_position_price = (
            position_price
            if math.isfinite(position_price)
            else state["fixnan_position_price"]
        )

        # tp_long = ((nLongs > 1) ? tp_long0 / nLongs : tp_long0) / 100
        # tp_short = ((nShorts > 1) ? tp_short0 / nShorts : tp_short0) / 100
        tp_long0 = ctx["tp_long0"]
        tp_short0 = ctx["tp_short0"]
        tp_long = (tp_long0 / n_longs if n_longs > 1 else tp_long0) / 100.0
        tp_short = (tp_short0 / n_shorts if n_shorts > 1 else tp_short0) / 100.0
        # long_tp := high > (fixnan(Position_Price) * (1 + tp_long)) and in_longCondition
        # short_tp := low < (fixnan(Position_Price) * (1 - tp_short)) and in_shortCondition
        long_tp = high > fixnan_position_price * (1 + tp_long) and in_long
        short_tp = low < fixnan_position_price * (1 - tp_short) and in_short
        # last_long_tp := long_tp ? time : nz(last_long_tp[1])   (and the short)
        previous_last_long_tp = _nz(state["last_long_tp"])
        previous_last_short_tp = _nz(state["last_short_tp"])
        last_long_tp = now if long_tp else previous_last_long_tp
        last_short_tp = now if short_tp else previous_last_short_tp
        # Final_Long_tp := (long_tp and last_longCondition > nz(last_long_tp[1])
        #                   and last_longCondition > nz(last_long_sl[1]))
        previous_last_long_sl = _nz(state["last_long_sl"])
        previous_last_short_sl = _nz(state["last_short_sl"])
        final_long_tp = (
            bool(long_tp)
            and last_long > previous_last_long_tp
            and last_long > previous_last_long_sl
        )
        final_short_tp = (
            bool(short_tp)
            and last_short > previous_last_short_tp
            and last_short > previous_last_short_sl
        )

        # sl = in_longCondition ? min(sl0, (Risk*100)/(Percent_Capital*max(1,nLongs)))
        #      : in_shortCondition ? min(sl0, (Risk*100)/(Percent_Capital*max(1,nShorts)))
        #      : sl0                      (Risk = sl0, Percent_Capital = 99)
        sl0 = ctx["sl0"]
        if in_long:
            sl = min(sl0, (sl0 * 100.0) / (99.0 * max(1.0, n_longs)))
        elif in_short:
            sl = min(sl0, (sl0 * 100.0) / (99.0 * max(1.0, n_shorts)))
        else:
            sl = sl0
        # Normal_long_sl = (in_longCondition and low <= ((1 - sl/100) * fixnan(Position_Price)))
        # Normal_short_sl = (in_shortCondition and high >= ((1 + sl/100) * fixnan(Position_Price)))
        normal_long_sl = in_long and low <= (1 - sl / 100.0) * fixnan_position_price
        normal_short_sl = in_short and high >= (1 + sl / 100.0) * fixnan_position_price
        # last_long_sl := Normal_long_sl ? time : nz(last_long_sl[1])   (and the short)
        last_long_sl = now if normal_long_sl else previous_last_long_sl
        last_short_sl = now if normal_short_sl else previous_last_short_sl
        # Final_Long_sl := Normal_long_sl and last_longCondition > nz(last_long_sl[1])
        #                  and last_longCondition > nz(last_long_tp[1])
        #                  and not Final_Long_tp
        final_long_sl = (
            bool(normal_long_sl)
            and last_long > previous_last_long_sl
            and last_long > previous_last_long_tp
            and not final_long_tp
        )
        final_short_sl = (
            bool(normal_short_sl)
            and last_short > previous_last_short_sl
            and last_short > previous_last_short_tp
            and not final_short_tp
        )

        # if Final_Long_tp or Final_Long_sl
        #     CondIni_long := -1 ; sum_long := 0.0 ; nLongs := na
        if final_long_tp or final_long_sl:
            cond_ini_long = -1
            sum_long = 0.0
            n_longs = float("nan")
        # if Final_Short_tp or Final_Short_sl
        #     CondIni_short := 1 ; sum_short := 0.0 ; nShorts := na
        if final_short_tp or final_short_sl:
            cond_ini_short = 1
            sum_short = 0.0
            n_shorts = float("nan")

        # Carry the whole bar's state forward before the order calls.
        state.update({
            "cond_ini_long": cond_ini_long,
            "cond_ini_short": cond_ini_short,
            "sum_long": sum_long,
            "sum_short": sum_short,
            "position_price": position_price,
            "fixnan_position_price": fixnan_position_price,
            "last_open_long": last_open_long,
            "last_open_short": last_open_short,
            "last_long": last_long,
            "last_short": last_short,
            "last_final_long": last_final_long,
            "last_final_short": last_final_short,
            "n_longs": n_longs,
            "n_shorts": n_shorts,
            "long_tp": bool(long_tp),
            "short_tp": bool(short_tp),
            "last_long_tp": last_long_tp,
            "last_short_tp": last_short_tp,
            "last_long_sl": last_long_sl,
            "last_short_sl": last_short_sl,
            "final_long_tp": final_long_tp,
            "final_short_tp": final_short_tp,
            "final_long_sl": final_long_sl,
            "final_short_sl": final_short_sl,
        })

        # if L_basic_condt
        #     strategy.entry("LONG", strategy.long)
        if long_cond:
            broker.entry("LONG", "long")
        # if S_basic_condt
        #     strategy.entry("SHORT", strategy.short)
        if short_cond:
            broker.entry("SHORT", "short")

        # strategy.exit("TP_L", "LONG", profit=<ticks>, limit=<price>, loss=<ticks>)
        # strategy.exit("TP_S", "SHORT", profit=<ticks>, limit=<price>, loss=<ticks>)
        # The two exit calls come AFTER both entries, in the source's order.
        # syminfo.mintick, read off the broker config exactly as the engine
        # applies it, so the tick distances agree with the resolved levels.
        mintick = float(broker.config.mintick)
        average = broker.position_avg_price
        profit_long = (
            abs((last_open_long * (1 + tp_long)) - last_open_long) / mintick
        )
        loss_long = (
            abs((last_open_long * (1 - (sl / 100.0))) - last_open_long) / mintick
        )
        profit_short = (
            abs((last_open_short * (1 - tp_short)) - last_open_short) / mintick
        )
        loss_short = (
            abs((last_open_short * (1 + (sl / 100.0))) - last_open_short) / mintick
        )
        # limit = nLongs >= 1 ? strategy.position_avg_price * (1 + tp_long) : na
        limit_long = (
            average * (1 + tp_long)
            if (n_longs >= 1 and math.isfinite(average))
            else None
        )
        # limit = nShorts >= 1 ? strategy.position_avg_price * (1 - tp_short) : na
        limit_short = (
            average * (1 - tp_short)
            if (n_shorts >= 1 and math.isfinite(average))
            else None
        )
        broker.exit(
            "TP_L", from_entry="LONG", profit=profit_long, limit=limit_long,
            loss=loss_long,
        )
        broker.exit(
            "TP_S", from_entry="SHORT", profit=profit_short, limit=limit_short,
            loss=loss_short,
        )
