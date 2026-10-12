"""Port of sources/SM_e1c6216a94daeb51.pine (batch_001/Laguerre-RSI与ADX滤波交易信号策略-Laguerre-RSI-with-ADX-Filtered-Trading-Signals-Strategy.md).

Pine v5 (`//@version=5`). A four-stage Laguerre filter feeding a Laguerre RSI,
gated by Wilder's ADX:

    [diPlus, diMinus, adx] = ta.dmi(adxLength, adxSmoothing)

    gamma = 1 - alpha
    L0 = 0.0
    L0 := (1 - gamma) * src + gamma * nz(L0[1])
    L1 = 0.0
    L1 := -gamma * L0 + nz(L0[1]) + gamma * nz(L1[1])
    L2 = 0.0
    L2 := -gamma * L1 + nz(L1[1]) + gamma * nz(L2[1])
    L3 = 0.0
    L3 := -gamma * L2 + nz(L2[1]) + gamma * nz(L3[1])
    cu = (L0 > L1 ? L0 - L1 : 0) + (L1 > L2 ? L1 - L2 : 0) + (L2 > L3 ? L2 - L3 : 0)
    cd = (L0 < L1 ? L1 - L0 : 0) + (L1 < L2 ? L2 - L1 : 0) + (L2 < L3 ? L3 - L2 : 0)
    temp = cu + cd == 0 ? -1 : cu + cd
    LaRSI = temp == -1 ? 0 : cu / temp

    longCondition  = ta.crossover(100 * LaRSI, buyLevel) and adx > adxLevel
    shortCondition = ta.crossunder(100 * LaRSI, sellLevel) and adx > adxLevel

    strategy.entry('Long', strategy.long, when=longCondition)
    strategy.entry('Short', strategy.short, when=shortCondition)

Only `L0`'s assignment uses this bar's value on the right-hand side (`L0`); the
other three use the PREVIOUS bar's value (`L0[1]` etc.), so the filter is a
fourth-order cascade and the port iterates it bar by bar. `nz` makes the
previous-bar reads 0 at bar 0, which is what seeds the recursion.

THE ADX IS IMPLEMENTED FROM PINE'S OWN `ta.dmi` DOCUMENTED FORMULA, not taken
from a library function -- `pine_ta` has no `dmi`, so the definition is written
out in `_pine_dmi` below and the formula quoted there (iron rule 3). It reads
`ta.tr` and `ta.rma`, both of which pine_ta does supply.

Both entries are MARKET orders, so they fill at the next bar's open in the
engine -- the same bar and the same price Freqtrade uses. There is no stop,
limit, exit, close or cancel anywhere in the source: a position is closed only
by the opposite entry reversing it.

`strategy('Laguerre RSI ...', shorttitle='LaRSI_ADX Signals', overlay=false)`
declares only display properties, so Pine's documented defaults apply and are
what this port carries: `default_qty_type=fixed`, one unit per order,
`commission_value=0`, `pyramiding=0`, `process_orders_on_close=false`, initial
capital 1000000. `overlay=false` puts the plots in a pane and has no effect on
orders.

The `/*backtest` header declares `period: 1d` on Futures_Binance BTC_USDT, so
`timeframe` is "1d"; its `basePeriod: 1h` is the FMZ backtester's own filling
granularity for those daily bars, not the strategy's period.

FIDELITY:

* `ta.dmi` is not in `pine_ta`; it is implemented here from Pine's documented
  expansion (quoted in `_pine_dmi`). Two details of that expansion are
  reproduced rather than simplified: `fixnan` (a forward fill of the DI series)
  and the `sum == 0 ? 1 : sum` guard before the ADX smoother. A hand-rolled
  ADX that skipped either would diverge on the same data.
* `fixnan` is not in `pine_ta` either; `_fixnan` is a forward fill, which is
  what Pine's `fixnan` does. On this source it only ever touches the na prefix
  (the DI series is never na after warm-up), so it changes nothing here -- it
  is implemented so that the formula is the source's, not an approximation.
* `ta.tr`'s first bar: Pine's `ta.tr` defaults to `handle_na = false` and is na
  on bar 1, while `pine_ta.pine_tr` gives `high - low` there. This shifts the
  ATR/DI seeding by one bar (PINE_SEMANTICS.md section 3.7, recorded there and
  not corrected). `pine_tr` is used as-is.
* `alpha` is `input.float(minval=0, maxval=1, step=0.1, defval=0.2)`; the port
  carries 0.2 and does not clamp an override, since Pine enforces minval/maxval
  at the input widget rather than in the script.
* `src` is `input(title='Source', defval=close)`; it is carried as a source
  name and resolved with `pine_ta.pine_source`.
* `temp = cu + cd == 0 ? -1 : cu + cd` relies on `?:` binding looser than `==`,
  i.e. it reads `((cu + cd) == 0) ? -1 : (cu + cd)`. The port reproduces that
  reading; it is not reorganised into a branch on `cu + cd`.
* `100 * LaRSI` is crossed against the raw `buyLevel` / `sellLevel` inputs
  (20 / 80), and `adx` is compared to `adxLevel` with a strict `>`.
* `crossover` / `crossunder` return false when either operand is na, so no
  signal can arrive before the ADX and the Laguerre filter exist; pine_ta
  reproduces that.
* `plot` / `hline` calls and the shorttitle are display-only and are not
  reproduced.
* There is no exit call in the source, so `source_reproduce_stops` is False and
  a position open at the end of the window stays open.
* Leverage, margin, liquidation, funding and the venue's contract-step
  rounding are not modelled; the framework and the engine can differ by a
  rounded quantity (measured separately by the chain verifier).
"""
import numpy as np
import pandas as pd

from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


def _fixnan(source: pd.Series) -> pd.Series:
    """Pine `fixnan`: the last non-na value, carried forward."""
    return source.ffill()


def _pine_dmi(dataframe: pd.DataFrame, di_length: int, adx_smoothing: int):
    """Pine `ta.dmi(diLength, adxSmoothing)` -- [diPlus, diMinus, adx].

    Pine's documented expansion, reproduced literally:

        up   = ta.change(high)
        down = -ta.change(low)
        plusDM  = na(up)   ? na : (up > down and up > 0 ? up : 0)
        minusDM = na(down) ? na : (down > up and down > 0 ? down : 0)
        trur = ta.rma(ta.tr, diLength)
        plus  = fixnan(100 * ta.rma(plusDM,  diLength) / trur)
        minus = fixnan(100 * ta.rma(minusDM, diLength) / trur)
        sum   = plus + minus
        adx   = 100 * ta.rma(abs(plus - minus) / (sum == 0 ? 1 : sum), adxSmoothing)

    `pine_ta` has no `dmi`, so it is written out here rather than approximated
    by a differently-seeded ADX.
    """
    di_length = int(di_length)
    adx_smoothing = int(adx_smoothing)
    high = dataframe["high"]
    low = dataframe["low"]

    up = high.diff()
    down = -low.diff()
    plus_dm = np.where((up > down) & (up > 0), up, 0.0)
    minus_dm = np.where((down > up) & (down > 0), down, 0.0)
    # na(up) / na(down) propagate: Pine evaluates the whole ternary to na there.
    plus_dm = pd.Series(plus_dm, index=high.index).where(up.notna())
    minus_dm = pd.Series(minus_dm, index=high.index).where(down.notna())

    trur = ta.pine_rma(ta.pine_tr(dataframe), di_length)
    with np.errstate(divide="ignore", invalid="ignore"):
        plus = _fixnan(100.0 * ta.pine_rma(plus_dm, di_length) / trur)
        minus = _fixnan(100.0 * ta.pine_rma(minus_dm, di_length) / trur)
    total = plus + minus
    denominator = total.where(total != 0, 1.0)
    adx = 100.0 * ta.pine_rma((plus - minus).abs() / denominator, adx_smoothing)
    return plus, minus, adx


def _laguerre_rsi(source: pd.Series, alpha: float) -> pd.Series:
    """The source's four-stage Laguerre filter and its RSI read-out."""
    gamma = 1.0 - float(alpha)
    src = source.to_numpy(dtype=float)
    size = len(src)
    l0 = np.zeros(size)
    l1 = np.zeros(size)
    l2 = np.zeros(size)
    l3 = np.zeros(size)
    for i in range(size):
        # nz(L0[1]) and friends: bar 0's history reads as 0.
        p0 = l0[i - 1] if i > 0 else 0.0
        p1 = l1[i - 1] if i > 0 else 0.0
        p2 = l2[i - 1] if i > 0 else 0.0
        p3 = l3[i - 1] if i > 0 else 0.0
        l0[i] = (1.0 - gamma) * src[i] + gamma * p0
        l1[i] = -gamma * l0[i] + p0 + gamma * p1
        l2[i] = -gamma * l1[i] + p1 + gamma * p2
        l3[i] = -gamma * l2[i] + p2 + gamma * p3
    cu = (
        np.where(l0 > l1, l0 - l1, 0.0)
        + np.where(l1 > l2, l1 - l2, 0.0)
        + np.where(l2 > l3, l2 - l3, 0.0)
    )
    cd = (
        np.where(l0 < l1, l1 - l0, 0.0)
        + np.where(l1 < l2, l2 - l1, 0.0)
        + np.where(l2 < l3, l3 - l2, 0.0)
    )
    total = cu + cd
    # temp = cu + cd == 0 ? -1 : cu + cd ; LaRSI = temp == -1 ? 0 : cu / temp
    with np.errstate(divide="ignore", invalid="ignore"):
        value = np.where(total == 0, 0.0, cu / np.where(total == 0, 1.0, total))
    return pd.Series(value, index=source.index, dtype=float)


class SMLaguerreRsiAdx_e1c621(PinePortBase, IStrategy):
    source_id = "SM_e1c6216a94daeb51"
    source_file = (
        "Laguerre-RSI与ADX滤波交易信号策略-"
        "Laguerre-RSI-with-ADX-Filtered-Trading-Signals-Strategy.md"
    )
    timeframe = "1d"
    can_short = True
    source_defaults: dict = {
        "src": "close",
        "alpha": 0.2,
        "buyLevel": 20,
        "sellLevel": 80,
        "adxLength": 14,
        "adxSmoothing": 14,
        "adxLevel": 20,
    }
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    # No stop / limit / exit / close in the source.
    source_reproduce_stops = False
    source_fidelity_notes = [
        "pine_ta has no ta.dmi, so ta.dmi is implemented from Pine's documented "
        "expansion (quoted in _pine_dmi) rather than replaced by a differently "
        "seeded ADX: fixnan (forward fill) and the sum == 0 ? 1 : sum guard are "
        "both reproduced.",
        "ta.tr's first bar: Pine's ta.tr defaults to handle_na = false and is na "
        "on bar 1, while pine_ta.pine_tr returns high - low there, shifting the "
        "ATR/DI seeding by one bar. PINE_SEMANTICS.md section 3.7; recorded, not "
        "corrected (shared-layer change, not a port change).",
        "temp = cu + cd == 0 ? -1 : cu + cd is read with ?: binding loosest, "
        "i.e. ((cu + cd) == 0) ? -1 : (cu + cd); LaRSI = 0 exactly then, and "
        "cu / (cu + cd) otherwise. Reproduced as written.",
        "The Laguerre recursion is iterated bar by bar: L1..L3 read the PREVIOUS "
        "bar's L0[1]..L3[1] while L0 reads this bar's src, and nz() makes bar 0's "
        "history reads 0.",
        "alpha is input.float(minval=0, maxval=1, step=0.1, defval=0.2); 0.2 is "
        "carried and an override is not clamped here, since Pine enforces the "
        "bounds at the input widget.",
        "src is input(title='Source', defval=close) and is resolved through "
        "pine_ta.pine_source.",
        "The signal crosses 100 * LaRSI against the raw buyLevel / sellLevel "
        "inputs (20 / 80) and requires adx > adxLevel (strict >).",
        "crossover / crossunder are false when either operand is na, so no "
        "signal can arrive before the filter and the ADX exist.",
        "Both entries are market orders and fill at the next bar's open, which "
        "is what Freqtrade does too.",
        "There is no exit call in the source; source_reproduce_stops is False "
        "and a position open at the end of the window stays open.",
        "plot / hline calls, the shorttitle and overlay=false are display-only "
        "and are not reproduced.",
        "Leverage, margin, liquidation, funding and venue contract-step "
        "rounding are not modelled.",
    ]

    def pine_indicators(self, dataframe, params):
        source = ta.pine_source(dataframe, str(params["src"]))
        _plus, _minus, adx = _pine_dmi(
            dataframe, int(params["adxLength"]), int(params["adxSmoothing"])
        )
        larsi = _laguerre_rsi(source, float(params["alpha"]))
        scaled = 100.0 * larsi

        long_condition = ta.pine_crossover(scaled, float(params["buyLevel"])) & (
            adx > float(params["adxLevel"])
        )
        short_condition = ta.pine_crossunder(scaled, float(params["sellLevel"])) & (
            adx > float(params["adxLevel"])
        )

        dataframe["pine_larsi"] = scaled
        dataframe["pine_adx"] = adx
        dataframe["pine_long_condition"] = long_condition.fillna(False)
        dataframe["pine_short_condition"] = short_condition.fillna(False)
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "long_condition": dataframe["pine_long_condition"].to_numpy(dtype=bool),
            "short_condition": dataframe["pine_short_condition"].to_numpy(dtype=bool),
        }

    def pine_script(self, broker, i, ctx):
        # strategy.entry('Long', strategy.long, when=longCondition)
        if ctx["long_condition"][i]:
            broker.entry("Long", "long")
        # strategy.entry('Short', strategy.short, when=shortCondition)
        if ctx["short_condition"][i]:
            broker.entry("Short", "short")
