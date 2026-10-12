"""Port of sources/SM_d7f0afb3cb7db496.pine (batch_001/Delta-RSI-Oscillator-Strategy.md).

Pine v4 (`//@version=4`, `study(...)`), and the file declares a STUDY, not a
`strategy(...)`: the two `strategy.entry` calls at the bottom are an order
block APPENDED to the indicator by the converter site that published it
(fmz.com/strategy/366641, named in the md's Detail link). Pine v4 does not
compile `strategy.entry` inside `study()`, so the "original strategy" is the
study PLUS that appended block, and the trading behaviour it defines is
entry-only.

The indicator is the Delta-RSI oscillator: the time derivative of an RSI,
obtained by fitting a local polynomial of order `degree` to the last `window`
RSI values on a fixed integer grid and evaluating its derivative at the newest
point, plus the normalized RMSE of that fit:

    src       = rsi(close, rsi_l)                      # Wilder RSI
    [drsi, nrmse] = diff(src, window, degree)
    signalline = ema(drsi, signalLength)

    crossup        = crossover(drsi, 0.0)              # drsi crosses zero up
    crossdw        = crossunder(drsi, 0.0)
    crosssignalup  = crossover(drsi, signalline)
    crosssignaldw  = crossunder(drsi, signalline)
    dirchangeup    = drsi > drsi[1] and drsi[1] < drsi[2] and drsi[1] < 0
    dirchangedw    = drsi < drsi[1] and drsi[1] > drsi[2] and drsi[1] > 0
    filter_rmse    = usenrmse ? nrmse < rmse_thrs : true

    golong  = (buycond  == "Direction Change" ? dirchangeup :
               buycond  == "Zero-Crossing"    ? crossup       : crosssignalup)  and filter_rmse
    goshort = (sellcond == "Direction Change" ? dirchangedw :
               sellcond == "Zero-Crossing"    ? crossdw       : crosssignaldw) and filter_rmse

    if golong
        strategy.entry("Enter Long", strategy.long)
    else if goshort
        strategy.entry("Enter Short", strategy.short)

The appended block reads ONLY `golong` / `goshort`. The source's own exit
series `endlong` / `endshort` (driven by the `endcond` input and by
`showendlabels`) are computed and then used by four `plotshape` calls and four
`alertcondition` calls -- there is no `strategy.close`, no `strategy.exit`, and
no commented-out one anywhere in the file. So the strategy has NO exits: a
position is only ever left by the opposite entry, which the engine models as a
reverse fill. `source_reproduce_stops` is False accordingly.

`study(...)` carries no strategy() properties, so Pine's documented defaults
apply: `default_qty_type` fixed, `default_qty_value` 1, commission 0%,
`pyramiding` 0, `initial_capital` 1000000 USD, `process_orders_on_close` false.

FIDELITY:

* This file is one of the converter-appended sources described in
  PINE_SEMANTICS.md 1.17. The appended block's conditions are ordinary booleans
  (`golong` / `goshort` are ternaries over comparisons), NOT the `? -1 : 0`
  shape, so the `-1`-is-truthy trap of 1.17 does not arise here and no integer
  truthiness had to be preserved. `if golong ... else if goshort` is kept as
  `if` / `elif` so that a bar on which the two conditions coincide -- possible
  only when `buycond` and `sellcond` are set to different options -- places the
  LONG order, which is what the source's `else if` says.
* `diff()` is transcribed rather than replaced by a library implementation: the
  source builds its own Vandermonde matrix `J[i][j] = i**j` (RAW integer grid
  0..window-1, not the centred grid the source's own comment describes), takes a
  pseudoinverse built from a modified Gram-Schmidt QR factorisation, and reads
  the derivative off `sum(i * a_i * (window-1)**(i-1))`. numpy's `pinv`/`lstsq`
  are NOT used: they would answer a slightly different question than this
  algorithm does and would hide any transcription error. `J` depends only on
  (window, degree), so the pseudoinverse is computed once and reused for every
  bar instead of being recomputed per bar as Pine does -- the inputs are
  identical each bar, so the value is identical too; this is an exact
  optimisation, not a modelling choice.
* Pine's na propagation is preserved: while the RSI window is not full `src` is
  na, so `Y_raw` is na, so `a_i`, the derivative and the NRMSE are all na; the
  port computes them and lets NaN propagate exactly as Pine does, rather than
  skipping the bar.
* `rsi` is Pine's Wilder RSI (pine_ta.pine_rsi), and `ema` is
  pine_ta.pine_ema, whose first-value seeding rule is an unpublished
  TradingView detail recorded as a parity risk in PINE_SEMANTICS.md 3.1. The
  signal line's seeding therefore carries that risk (the zero-crossing
  conditions, which are the defaults, do not read the signal line at all).
* `filter_rmse` is `true` for every bar unless `usenrmse` is set; exactly as in
  the source, and `nrmse` is computed either way. Pine treats an na comparison
  as false, so an unfitted bar is filtered out when `usenrmse` is on -- the
  port's NaN comparison does the same.
* `rmse_thrs` is the source's `input(...)/100`, so its default is 0.1, not 10.
  The port stores the divided value, which is what the comparison uses.
* `islong` / `isshort` / `showendlabels` are inputs that gate only the four
  `plotshape` calls (and `endcond` only feeds `endlong`/`endshort`, which no
  order reads). They are NOT carried in `source_defaults` because nothing in
  the trading path reads them; the whole label/plot layer (`plotshape`,
  `plot`-free here) and the four `alertcondition` calls place no order and are
  dropped.
* The `/*backtest` header declares period 1h on Futures_Binance BTC_USDT; its
  `basePeriod: 15m` is the host's intrabar granularity for filling 1h bars, not
  the strategy's period. The header's window (2022-04-29 to 2022-05-28) is
  extraction metadata, not an `input.time` filter, so no data is trimmed.
* The source's larger inputs need `window > degree` ("Length ( > Order)"); with
  the defaults (21, 2) `J` is full column rank. A parameter pair that violates
  it makes `J` rank-deficient and the whole indicator na -- the port reports
  that as na without inventing a value.
* Leverage, margin, liquidation, funding and the venue's contract-step
  rounding are not modelled; the chain verifier measures the rounding
  separately (PINE_SEMANTICS.md 1.6).
"""
import numpy as np
import pandas as pd
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


# ---- the source's implied-2d-matrix routines, transcribed ---------------
#
# Pine arrays are flat and the source addresses them column-major via
# `matrix_get/_set(A, i, j, nrows) == A[i + nrows*j]`. Keeping the same
# convention here means the transcription can be checked line by line against
# the source.


def _matrix_get(matrix, i, j, nrows):
    return matrix[i + nrows * j]


def _matrix_set(matrix, value, i, j, nrows):
    matrix[i + nrows * j] = value


def _to_matrix(flat, nrows, ncolumns):
    """Flat column-major storage -> the (nrows x ncolumns) view of it."""
    return flat.reshape(ncolumns, nrows).T


def _transpose(flat, nrows, ncolumns):
    """`transpose(_A, _nrows, _ncolumns)` -> flat storage of the (ncol x nrow) transpose."""
    out = np.zeros(nrows * ncolumns, dtype=float)
    for i in range(nrows):
        for j in range(ncolumns):
            _matrix_set(out, _matrix_get(flat, i, j, nrows), j, i, ncolumns)
    return out


def _multiply(a_flat, b_flat, nrows_a, ncolumns_a, ncolumns_b):
    """`multiply(_A, _B, _nrowsA, _ncolumnsA, _ncolumnsB)`, flat column-major."""
    nrows_b = ncolumns_a
    out = np.zeros(nrows_a * ncolumns_b, dtype=float)
    with np.errstate(invalid="ignore"):
        for i in range(nrows_a):
            for j in range(ncolumns_b):
                element = 0.0
                for k in range(ncolumns_a):
                    element = (
                        element
                        + _matrix_get(a_flat, i, k, nrows_a)
                        * _matrix_get(b_flat, k, j, nrows_b)
                    )
                _matrix_set(out, element, i, j, nrows_a)
    return out


def _vnorm(vector, n):
    """`vnorm(_X, _n)`: square norm of a vector of size n."""
    total = 0.0
    for i in range(n):
        total += vector[i] ** 2
    return float(np.sqrt(total))


def _qr_diag(a_flat, nrows, ncolumns):
    """`qr_diag`: modified Gram-Schmidt QR, column-oriented. Returns (Q, R) flat."""
    q = np.zeros(nrows * ncolumns, dtype=float)
    r = np.zeros(ncolumns * ncolumns, dtype=float)
    a = np.zeros(nrows, dtype=float)
    with np.errstate(divide="ignore", invalid="ignore"):
        for i in range(nrows):
            a[i] = _matrix_get(a_flat, i, 0, nrows)
        norm = _vnorm(a, nrows)
        _matrix_set(r, norm, 0, 0, ncolumns)
        for i in range(nrows):
            _matrix_set(q, a[i] / norm, i, 0, nrows)
        if ncolumns != 1:
            for k in range(1, ncolumns):
                for i in range(nrows):
                    a[i] = _matrix_get(a_flat, i, k, nrows)
                for j in range(k):
                    norm = 0.0
                    for i in range(nrows):
                        norm = norm + _matrix_get(q, i, j, nrows) * a[i]
                    _matrix_set(r, norm, j, k, ncolumns)
                    for i in range(nrows):
                        a[i] = a[i] - norm * _matrix_get(q, i, j, nrows)
                norm = _vnorm(a, nrows)
                _matrix_set(r, norm, k, k, ncolumns)
                for i in range(nrows):
                    _matrix_set(q, a[i] / norm, i, k, nrows)
    return q, r


def _pinv(a_flat, nrows, ncolumns):
    """`pinv(_A, _nrows, _ncolumns)`: R^-1 * Q^T from the source's own QR."""
    q, r = _qr_diag(a_flat, nrows, ncolumns)
    q_t = _transpose(q, nrows, ncolumns)
    r_inv = np.zeros(ncolumns * ncolumns, dtype=float)
    with np.errstate(divide="ignore", invalid="ignore"):
        _matrix_set(r_inv, 1 / _matrix_get(r, 0, 0, ncolumns), 0, 0, ncolumns)
        if ncolumns != 1:
            for j in range(1, ncolumns):
                for i in range(j):
                    total = 0.0
                    for k in range(i, j):
                        total = (
                            total
                            + _matrix_get(r_inv, i, k, ncolumns)
                            * _matrix_get(r, k, j, ncolumns)
                        )
                    _matrix_set(r_inv, total, i, j, ncolumns)
                for k in range(j):
                    _matrix_set(
                        r_inv,
                        -_matrix_get(r_inv, k, j, ncolumns)
                        / _matrix_get(r, j, j, ncolumns),
                        k,
                        j,
                        ncolumns,
                    )
                _matrix_set(
                    r_inv, 1 / _matrix_get(r, j, j, ncolumns), j, j, ncolumns
                )
    return _multiply(r_inv, q_t, ncolumns, ncolumns, nrows)


def _norm_rmse(x, x_hat):
    """`norm_rmse(_x, _xhat)`: RMSE normalized to the sample mean."""
    if len(x) != len(x_hat):
        return np.nan
    count = len(x)
    with np.errstate(divide="ignore", invalid="ignore"):
        mse = 0.0
        for i in range(count):
            mse = mse + (x[i] - x_hat[i]) ** 2 / count
        x_mean = float(np.sum(x)) / count
        return float(np.sqrt(mse) / x_mean)


def _pine_diff(values, window, degree):
    """The source's `diff(_src, _window, _degree)`, evaluated bar by bar.

    Returns (drsi, nrmse) as float ndarrays. na in `values` propagates through
    the fit and the RMSE, which is what Pine does too.
    """
    size = len(values)
    drsi = np.full(size, np.nan)
    nrmse = np.full(size, np.nan)
    if window < 1 or degree < 1 or degree + 1 > window:
        # `J` would be rank-deficient; the source's own input tooltip requires
        # window > degree. Everything downstream is na.
        return drsi, nrmse
    # Vandermonde: _J[i][j] = pow(i, j) over the raw grid 0..window-1.
    j_flat = np.zeros(window * (degree + 1), dtype=float)
    for i in range(window):
        for j in range(degree + 1):
            _matrix_set(j_flat, float(i) ** j, i, j, window)
    j_matrix = _to_matrix(j_flat, window, degree + 1)
    pseudo = _to_matrix(_pinv(j_flat, window, degree + 1), degree + 1, window)
    with np.errstate(divide="ignore", invalid="ignore", over="ignore"):
        for t in range(window - 1, size):
            # _Y_raw[j] = _src[_window-1-j], i.e. oldest first, newest last.
            raw = np.asarray(values[t - window + 1 : t + 1], dtype=float)
            coefficients = pseudo @ raw
            derivative = 0.0
            for i in range(1, degree + 1):
                derivative = derivative + i * coefficients[i] * (window - 1) ** (i - 1)
            estimate = j_matrix @ coefficients
            drsi[t] = derivative
            nrmse[t] = _norm_rmse(raw, estimate)
    return drsi, nrmse


class SMDeltaRsiOscillatorStrategy_d7f0af(PinePortBase, IStrategy):
    source_id = "SM_d7f0afb3cb7db496"
    source_file = "Delta-RSI-Oscillator-Strategy.md"
    timeframe = "1h"
    can_short = True
    # Exactly the inputs the trading path reads, with the source's defaults.
    # `rmse_thrs` is the source's `input(..., defval=10) / 100`.
    source_defaults: dict = {
        "degree": 2,
        "rsi_l": 21,
        "window": 21,
        "signalLength": 9,
        "buycond": "Zero-Crossing",
        "sellcond": "Zero-Crossing",
        "usenrmse": False,
        "rmse_thrs": 0.1,
    }
    # study(...), not strategy(...): Pine's documented defaults apply.
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    # No strategy.close / strategy.exit / stop / limit / trail anywhere in the
    # source -- not even a commented-out one (endlong/endshort feed plotshape
    # and alertcondition only).
    source_reproduce_stops = False
    source_mintick = 0.1
    source_fidelity_notes = [
        "Converter-appended order block (PINE_SEMANTICS.md 1.17): the file declares "
        "study(), and the two strategy.entry calls at the end are an appended block "
        "added by the publishing host (fmz.com/strategy/366641). The source does not "
        "compile on TradingView; the host's Pine dialect is the behaviour reproduced "
        "here.",
        "The appended block's conditions are plain booleans, NOT the `? -1 : 0` shape, "
        "so 1.17's '-1 is truthy, do not rewrite it as == 1' trap does not arise for "
        "this source and nothing integer-valued needed preserving. `if/else if` is "
        "kept as if/elif: with buycond and sellcond set to different options a bar "
        "can satisfy both, and the source gives the LONG order priority.",
        "There is no exit of any kind: `endlong`/`endshort` (from the `endcond` and "
        "`showendlabels` inputs) are used by four plotshape calls and four "
        "alertcondition calls only -- no strategy.close, no strategy.exit, not even a "
        "commented-out one. source_reproduce_stops is False; a position is left only "
        "by the opposite entry (a reverse fill).",
        "`diff()` is transcribed, not replaced: the port reproduces the source's own "
        "Vandermonde matrix (J[i][j] = i**j on the RAW grid 0..window-1, not the "
        "centred grid the source's comment describes), its modified Gram-Schmidt QR, "
        "its R^-1*Q^T pseudoinverse and the derivative sum(i*a_i*(window-1)**(i-1)). "
        "numpy's pinv/lstsq are deliberately not used.",
        "The pseudoinverse of J depends only on (window, degree), so it is computed "
        "once here instead of once per bar as Pine does. The inputs are identical on "
        "every bar, so the value is identical: an exact optimisation, not a modelling "
        "choice.",
        "Pine's na propagation is kept rather than skipped: an unfitted bar is na in "
        "Y_raw, hence na in the coefficients, the derivative and the NRMSE, exactly "
        "as Pine propagates it.",
        "`rsi` is Wilder's (pine_ta.pine_rsi) and `ema` is pine_ta.pine_ema, whose "
        "seeding rule TradingView does not publish -- PINE_SEMANTICS.md 3.1 lists it "
        "as a parity risk. The signal line carries that risk; the default "
        "Zero-Crossing conditions never read it.",
        "`rmse_thrs` is the source's `input(defval=10)/100`, so the default actually "
        "used in the comparison is 0.1 and that is what source_defaults records.",
        "`islong` / `isshort` / `showendlabels` / `endcond` are inputs that gate only "
        "plotshape output (endcond only builds endlong/endshort, which no order "
        "reads) and are therefore not carried in source_defaults; every plotshape and "
        "alertcondition is dropped.",
        "The `/*backtest` header's period 1h is the strategy timeframe; its "
        "basePeriod: 15m is the host's intrabar granularity, and its date window is "
        "extraction metadata rather than an input.time filter, so no data is trimmed.",
        "A parameter pair with window <= degree makes J rank-deficient; the port "
        "yields na for the whole indicator rather than inventing a value.",
        "Leverage, margin, liquidation, funding and the venue's contract-step "
        "rounding are not modelled (PINE_SEMANTICS.md 1.6 measures the rounding "
        "separately).",
    ]

    def pine_indicators(self, dataframe, params):
        close = dataframe["close"]
        rsi = ta.pine_rsi(close, int(params["rsi_l"]))
        drsi, nrmse = _pine_diff(
            rsi.to_numpy(dtype=float), int(params["window"]), int(params["degree"])
        )
        drsi = pd.Series(drsi, index=dataframe.index, dtype=float)
        nrmse = pd.Series(nrmse, index=dataframe.index, dtype=float)
        signalline = ta.pine_ema(drsi, int(params["signalLength"]))

        # Pine's comparison-with-na rule: an na operand makes the comparison
        # false, which is what numpy's NaN comparisons return as well.
        crossup = ta.pine_crossover(drsi, 0.0)
        crossdw = ta.pine_crossunder(drsi, 0.0)
        crosssignalup = ta.pine_crossover(drsi, signalline)
        crosssignaldw = ta.pine_crossunder(drsi, signalline)
        dirchangeup = (drsi > drsi.shift(1)) & (drsi.shift(1) < drsi.shift(2)) & (
            drsi.shift(1) < 0.0
        )
        dirchangedw = (drsi < drsi.shift(1)) & (drsi.shift(1) > drsi.shift(2)) & (
            drsi.shift(1) > 0.0
        )

        buycond = str(params["buycond"])
        sellcond = str(params["sellcond"])
        golong = (
            dirchangeup
            if buycond == "Direction Change"
            else (crossup if buycond == "Zero-Crossing" else crosssignalup)
        )
        goshort = (
            dirchangedw
            if sellcond == "Direction Change"
            else (crossdw if sellcond == "Zero-Crossing" else crosssignaldw)
        )
        if bool(params["usenrmse"]):
            filter_rmse = nrmse < float(params["rmse_thrs"])
        else:
            filter_rmse = True
        golong = (golong & filter_rmse).fillna(False)
        goshort = (goshort & filter_rmse).fillna(False)

        dataframe["pine_drsi"] = drsi
        dataframe["pine_signalline"] = signalline
        dataframe["pine_nrmse"] = nrmse
        dataframe["pine_long_condition"] = golong
        dataframe["pine_short_condition"] = goshort
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "drsi": dataframe["pine_drsi"].to_numpy(),
            "long_condition": dataframe["pine_long_condition"].to_numpy(),
            "short_condition": dataframe["pine_short_condition"].to_numpy(),
        }

    def pine_script(self, broker, i, ctx):
        # if golong
        #     strategy.entry("Enter Long", strategy.long)
        # else if goshort
        #     strategy.entry("Enter Short", strategy.short)
        if ctx["long_condition"][i]:
            broker.entry("Enter Long", "long")
        elif ctx["short_condition"][i]:
            broker.entry("Enter Short", "short")
