"""Port of sources/SM_0ebdc7c652d5408e.pine (batch_001/DMI乘数均线交易策略DMI-Moving-Average-Trading-Strategy.md).

Pine v5. A Wilder DMI whose entries are CONTRARIAN reversals of the two
directional lines rather than a cross of them:

    lensig = input.int(11, "ADX Smoothing", minval=1, maxval=50)
    len    = input.int(11, "DI Length",     minval=1)

    up      = ta.change(high)
    down    = -ta.change(low)
    plusDM  = na(up)   ? na : (up > down   and up   > 0 ? up   : 0)
    minusDM = na(down) ? na : (down > up   and down > 0 ? down : 0)
    trur    = ta.rma(ta.tr, len)
    plus    = fixnan(100 * ta.rma(plusDM,  len) / trur)
    minus   = fixnan(100 * ta.rma(minusDM, len) / trur)
    sum     = plus + minus
    adx     = 100 * ta.rma(math.abs(plus - minus) / (sum == 0 ? 1 : sum), lensig)

    buy  = plus < 10 and minus > 40   ->  strategy.entry('long',  strategy.long)
    sell = plus > 40 and minus < 10   ->  strategy.entry('short', strategy.short)

`adx` is computed but read by nothing: it places no condition anywhere in the
source. It is still computed here so the derived series is the source's own,
not a shortcut, but it cannot influence an order.

The order calls are the two `strategy.entry` above -- market orders, no `qty`,
no `when`, no stop/limit/trail, and no exit call anywhere in the source. A
position is therefore only ever closed or reversed by the opposite entry, so
`source_reproduce_stops` is False and a position still open at the end of the
window stays open.

`strategy(title="DMI Strategy", overlay=false)` declares only `title` and
`overlay`, so every other property is Pine's documented default: qty type
`strategy.fixed` / 1 contract, initial capital 1000000, commission 0%,
`pyramiding` 0 (one entry per direction), `process_orders_on_close=false`. The
source states none of them, and the reported `source_*` values are those
defaults rather than Freqtrade's.

The `/*backtest` header declares `period: 1m` on Futures_Binance BTC_USDT;
`basePeriod: 1m` is the FMZ backtester's own fill granularity for the same bars.

FIDELITY:

* `ta.tr` is called with no argument, and Pine's `ta.tr` defaults to
  `handle_na = false`, i.e. the FIRST bar is na. `pine_ta.pine_tr` goes through
  pandas' NaN-skipping max, which yields `high - low` on that bar instead --
  the boundary divergence recorded in PINE_SEMANTICS.md 3.7. The port restores
  Pine's documented first-bar na explicitly (see `_true_range`), because that
  one bar is what decides where `ta.rma` seeds and therefore how the whole
  +DI/-DI series is offset; 3.7 records this as unfixed in the shared layer.
* `fixnan` is Pine's forward fill: an na is replaced by the previous non-na
  value. Leading na has no previous value and STAYS na, which is what
  `Series.ffill()` does. It is implemented locally because `pine_ta` has no
  `fixnan`; `nz` is a different function (replaces with 0/replacement, not
  with the last value).
* MODELLED CHOICE: `100 * ta.rma(...) / trur` is na-divided when `trur` is 0,
  which for float arithmetic in Pine yields na. numpy would yield +/-inf
  instead, so non-finite quotients are folded back to na before `fixnan` sees
  them. The author wrapping the expression in `fixnan` is direct evidence that
  an na is the value they expected to see there.
* `plusDM` / `minusDM` use `na(up) ? na : ...`; both `up` and `down` are na
  only on bar 0 (`ta.change` of a non-na series), so the guard is reproduced as
  a per-bar mask on bar 0 alone.
* `sum == 0 ? 1 : sum` guards the ADX denominator only. On na, `na == 0` is
  false in Pine, so an na sum is divided by na (not by 1); pandas comparisons
  behave the same way, and the guard is written as `where(sum != 0, 1)`.
* `strategy.entry` with an id that is already long is refused by `pyramiding=0`.
  Reproduced by the engine's own `_can_add`; the port places the order every
  bar the condition holds, as the source does, and lets the engine refuse it.
* There is no `input(type=bool)` in this source, so PINE_SEMANTICS.md 1.16
  (bool compared as a number) does not apply.
* `plot` / `hline` are display-only and place no condition.
* `strategy.entry` in this source is a MARKET order, so PINE_SEMANTICS.md 2.11
  (resting stop/limit entries cannot be projected) does not apply here.
* Leverage, margin, liquidation and funding are not modelled; the venue's
  contract-step rounding is not modelled either (PINE_SEMANTICS.md 1.6), and
  the chain verifier measures that rounding separately.
"""
import numpy as np
import pandas as pd
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


def _true_range(dataframe) -> pd.Series:
    """Pine `ta.tr` (handle_na=false): true range with na on the first bar.

    `pine_ta.pine_tr` returns `high - low` on bar 0 (PINE_SEMANTICS.md 3.7);
    Pine documents `ta.tr` as na there. Restoring it matters because
    `ta.rma(ta.tr, len)` seeds its Wilder average on the first bar where the
    window is full, so a one-bar offset in the input shifts every later +DI
    and -DI value.
    """
    value = ta.pine_tr(dataframe)
    if len(value):
        value = value.copy()
        value.iloc[0] = np.nan
    return value


def _fixnan(series: pd.Series) -> pd.Series:
    """Pine `fixnan`: na becomes the previous non-na value; leading na stays na."""
    return series.ffill()


class SMDmiMovingAverageTradingStrategy_0ebdc7(PinePortBase, IStrategy):
    source_id = "SM_0ebdc7c652d5408e"
    source_file = "DMI乘数均线交易策略DMI-Moving-Average-Trading-Strategy.md"
    timeframe = "1m"
    can_short = True
    source_defaults: dict = {"lensig": 11, "len": 11}
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    source_reproduce_stops = False
    source_fidelity_notes = [
        "strategy() declares only title/overlay, so qty_type=fixed, qty_value=1, "
        "commission=0, pyramiding=0 and initial_capital=1000000 are Pine's "
        "documented defaults, not declarations in the source.",
        "adx is computed but read by nothing: it places no condition in the "
        "source. It is reproduced anyway so the derived series is the source's.",
        "ta.tr is called without an argument, i.e. handle_na=false, so its first "
        "bar is na. pine_ta.pine_tr returns high-low there instead "
        "(PINE_SEMANTICS.md 3.7); the port restores the na because that one bar "
        "decides where ta.rma seeds and offsets the whole +DI/-DI series.",
        "fixnan is Pine's forward fill (na <- previous non-na, leading na stays "
        "na). It is implemented locally: pine_ta has no fixnan, and nz is a "
        "different function (replaces with 0/replacement, not with the last "
        "value).",
        "MODELLED CHOICE: a zero trur makes the +DI/-DI quotient non-finite; "
        "Pine float arithmetic yields na there, so non-finite quotients are "
        "folded back to na before fixnan. The source wrapping the expression in "
        "fixnan is evidence that na is the expected value.",
        "plusDM/minusDM use `na(up) ? na : ...`; up and down are na only on bar "
        "0, and that mask is reproduced per bar.",
        "`sum == 0 ? 1 : sum` guards the ADX denominator only. Pine evaluates "
        "`na == 0` as false, so an na sum is divided by na, not by 1; pandas "
        "compares the same way and the guard is written `where(sum != 0, 1)`.",
        "No exit call exists, so source_reproduce_stops is False and a position "
        "still open at the end of the window stays open.",
        "No input(type=bool) exists, so PINE_SEMANTICS.md 1.16 does not apply.",
        "Entries are market orders, so PINE_SEMANTICS.md 2.11 (resting "
        "stop/limit entries cannot be projected) does not apply.",
        "plot/hline are display-only and place no condition.",
        "Leverage, margin, liquidation, funding and the venue's contract-step "
        "rounding are not modelled; the chain verifier measures the rounding "
        "separately.",
    ]

    def pine_indicators(self, dataframe, params):
        lensig = int(params["lensig"])
        length = int(params["len"])
        high, low = dataframe["high"], dataframe["low"]

        # up = ta.change(high); down = -ta.change(low)
        up = ta.pine_change(high)
        down = -ta.pine_change(low)

        # plusDM  = na(up)   ? na : (up   > down and up   > 0 ? up   : 0)
        # minusDM = na(down) ? na : (down > up   and down > 0 ? down : 0)
        plus_dm = pd.Series(
            np.where(((up > down) & (up > 0)).fillna(False).to_numpy(),
                     up.to_numpy(), 0.0),
            index=up.index, dtype=float,
        )
        minus_dm = pd.Series(
            np.where(((down > up) & (down > 0)).fillna(False).to_numpy(),
                     down.to_numpy(), 0.0),
            index=down.index, dtype=float,
        )
        plus_dm[up.isna()] = np.nan
        minus_dm[down.isna()] = np.nan

        # trur = ta.rma(ta.tr, len)
        trur = ta.pine_rma(_true_range(dataframe), length)

        with np.errstate(divide="ignore", invalid="ignore"):
            plus_raw = 100.0 * ta.pine_rma(plus_dm, length) / trur
            minus_raw = 100.0 * ta.pine_rma(minus_dm, length) / trur
        plus_raw = plus_raw.replace([np.inf, -np.inf], np.nan)
        minus_raw = minus_raw.replace([np.inf, -np.inf], np.nan)
        plus = _fixnan(plus_raw)
        minus = _fixnan(minus_raw)

        # sum = plus + minus
        total = plus + minus
        # adx = 100 * ta.rma(math.abs(plus - minus) / (sum == 0 ? 1 : sum), lensig)
        denominator = total.where(total != 0.0, 1.0)
        adx = 100.0 * ta.pine_rma((plus - minus).abs() / denominator, lensig)

        dataframe["pine_plus_di"] = plus
        dataframe["pine_minus_di"] = minus
        dataframe["pine_adx"] = adx
        # buy = plus < 10 and minus > 40
        dataframe["pine_long_condition"] = ((plus < 10.0) & (minus > 40.0)).fillna(False)
        # sell = plus > 40 and minus < 10
        dataframe["pine_short_condition"] = ((plus > 40.0) & (minus < 10.0)).fillna(False)
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "plus_di": dataframe["pine_plus_di"].to_numpy(),
            "minus_di": dataframe["pine_minus_di"].to_numpy(),
            "long_condition": dataframe["pine_long_condition"].to_numpy(),
            "short_condition": dataframe["pine_short_condition"].to_numpy(),
        }

    def pine_script(self, broker, i, ctx):
        # buy = plus < 10 and minus > 40
        # if buy
        #     strategy.entry('long', strategy.long)
        if ctx["long_condition"][i]:
            broker.entry("long", "long")
        # sell = plus > 40 and minus < 10
        # if sell
        #     strategy.entry('short', strategy.short)
        if ctx["short_condition"][i]:
            broker.entry("short", "short")
