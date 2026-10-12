"""Port of sources/SM_7259860f816499c5.pine (batch_001/AlphaTrend-use-mfi.md).

Pine v5 (the file carries no `//@version` annotation but uses the v5 `ta.`
namespace and `input.float`). KivancOzbilgic's AlphaTrend, the MFI-gated
variant, with a conversion tool's order block appended -- the pattern
PINE_SEMANTICS.md 1.17 records:

    coeff         = input.float(5, 'Multiplier')
    AP            = input(14, 'Common Period')
    ATR           = ta.sma(ta.tr, AP)
    src           = input.source(close, "source")
    upT           = low  - ATR * coeff
    downT         = high + ATR * coeff
    AlphaTrend = 0.0
    AlphaTrend := ta.mfi(hlc3, 14) >= 50
                  ? (upT   < nz(AlphaTrend[1]) ? nz(AlphaTrend[1]) : upT)
                  : (downT > nz(AlphaTrend[1]) ? nz(AlphaTrend[1]) : downT)

    if ta.crossover(low, AlphaTrend)
        strategy.entry("BUY", strategy.long)
    else if ta.crossunder(high, AlphaTrend)
        strategy.entry("SELL", strategy.short, when=ta.crossunder(high, AlphaTrend))

`strategy.entry` does not compile inside `indicator()`, so the trading
behaviour of this source is what the appended block does: enter on the cross,
and NEVER exit. No exit call of any kind exists in the file -- there is not even
a commented-out `strategy.exit` line -- so a position is only ever ended by the
opposite entry reversing it.

`AlphaTrend` is a ratchet: each bar either holds the previous value or steps to
that bar's band, so it is walked bar by bar. `ta.crossover(low, AlphaTrend)` is
the low crossing ABOVE the line and `ta.crossunder(high, AlphaTrend)` the high
crossing BELOW it; they cannot both fire on one bar (`low <= high`), and the
source's if / else-if order is preserved anyway.

`ta.mfi` is not in the shared layer and is written out in `_pine_mfi` from its
documented definition:

    upper = math.sum(volume * (ta.change(series) <= 0 ? 0 : series), length)
    lower = math.sum(volume * (ta.change(series) >= 0 ? 0 : series), length)
    mfi   = 100.0 - (100.0 / (1.0 + upper / lower))

There is no `strategy(...)` call, so the Pine defaults apply: `fixed` /
1 contract, initial capital 1000000, commission 0%, `pyramiding 0`,
`process_orders_on_close=false`.

FIDELITY:

* `ta.tr` (bare) is v5's `ta.tr` with `handle_na = false`, i.e. na on the first
  bar. `pine_ta.pine_tr(..., handle_na=False)` is the shared layer's model of
  it, but its pandas pipeline yields `high - low` on the first bar instead of
  na; because `ta.sma` propagates na, the source's ATR-SMA is na on bars
  0..13 and first valid on bar 14, while the modelled one is first valid on
  bar 13. That advances the whole `upT` / `downT` / `AlphaTrend` chain by one
  bar in the warmup region. This is a documented public-layer boundary --
  PINE_SEMANTICS.md 3.7 -- recorded rather than patched locally.
* The MFI length is the hardcoded literal 14 in the source, NOT the `AP`
  input; the port keeps 14 hardcoded. `AP` only drives the ATR.
* `src = input.source(close, "source")` is declared and then never used by the
  source (the bands use `low` / `high`, the gate uses `hlc3`). It is carried in
  `source_defaults` for provenance only and does not enter any calculation.
* `ta.mfi`'s `upper / lower` when `lower == 0` (a window in which every
  `ta.change(hlc3)` is <= 0) is left to IEEE division, giving `mfi = 100`.
  Pine's own convention for a float division by zero is not established here;
  if the platform returns na instead, that bar would take the `downT` branch
  rather than the `upT` branch. Recorded, not guessed.
* Pine treats an na ternary condition as false, so every warmup bar (where
  `ATR`, the MFI gate or `AlphaTrend[1]` is na) evaluates the `downT` leg and
  `AlphaTrend` itself becomes na rather than 0. Plain numpy comparisons against
  NaN are also false, which reproduces this.
* `nz(AlphaTrend[1])` collapses the first bar's na to 0, as in the source.
* The `when=ta.crossunder(high, AlphaTrend)` argument on the short entry is the
  same expression as the enclosing `else if`; it can never be false there, so
  dropping it from the port changes nothing.
* No exit call exists: `source_reproduce_stops` is False.
* `plot(AlphaTrend)` is display-only and is not reproduced.
* The `/*backtest` header declares `period: 1d` on Bitfinex BTC_USD, so
  `timeframe` is "1d"; `basePeriod: 1h` is the FMZ backtester's own fill
  granularity, not the strategy's period.
* No `security()` call, no `barstate.isrealtime` branch, no repainting.
* Leverage, margin, liquidation, funding and the venue's contract-step
  rounding of order quantities are not modelled.
"""
import numpy as np
import pandas as pd
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


def _pine_mfi(source: pd.Series, volume: pd.Series, length: int) -> pd.Series:
    """Pine `ta.mfi(source, length)` from its documented definition."""
    change = ta.pine_change(source)
    # Pine's `cond ? 0 : series` takes the series when `cond` is na, so the
    # weight test is written as "is cond true?" with na counting as false --
    # which is what a numpy comparison against NaN already gives.
    upper_weight = np.where((change <= 0).to_numpy(), 0.0, source.to_numpy(dtype=float))
    lower_weight = np.where((change >= 0).to_numpy(), 0.0, source.to_numpy(dtype=float))
    upper = ta.pine_sum(pd.Series(upper_weight, index=source.index) * volume, length)
    lower = ta.pine_sum(pd.Series(lower_weight, index=source.index) * volume, length)
    with np.errstate(divide="ignore", invalid="ignore"):
        money_flow = upper / lower
        return 100.0 - (100.0 / (1.0 + money_flow))


class SMAlphaTrendUseMfi_725986(PinePortBase, IStrategy):
    source_id = "SM_7259860f816499c5"
    source_file = "AlphaTrend-use-mfi.md"
    timeframe = "1d"
    can_short = True
    source_defaults: dict = {"coeff": 5.0, "AP": 14, "src": "close"}
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    source_reproduce_stops = False
    source_fidelity_notes = [
        "Converter-appended order block (PINE_SEMANTICS 1.17): the file "
        "declares indicator() and the trailing crossover/crossunder entry pair "
        "is what the tool added. The port reproduces that block's actual "
        "behaviour -- enter on the cross, never exit.",
        "NO exit call exists in the source, not even a commented-out one, so "
        "source_reproduce_stops is False and a position is only ever ended by "
        "the opposite entry reversing it.",
        "No `? -1 : 0` construct is present, so the 1.17 integer-truthiness "
        "trap does not apply here; the if / else-if order (BUY first) is "
        "preserved in pine_script.",
        "Bare ta.tr in v5 is handle_na=false (na on bar 0); pine_ta.pine_tr "
        "returns high - low there instead, moving ta.sma(ta.tr, AP)'s seeding "
        "point one bar earlier and with it the whole upT/downT/AlphaTrend "
        "chain. PINE_SEMANTICS 3.7 boundary: recorded, not patched locally.",
        "The MFI length is the hardcoded literal 14 in the source, not the AP "
        "input; 14 stays hardcoded here. AP drives only the ATR.",
        "src = input.source(close) is declared and never used by the source; "
        "it is carried in source_defaults for provenance only.",
        "ta.mfi is not in the shared layer; _pine_mfi implements its "
        "documented definition (math.sum weighted by the sign of ta.change, "
        "then 100 - 100/(1 + upper/lower)).",
        "ta.mfi's upper/lower with lower == 0 is left to IEEE division "
        "(mfi = 100). Pine's float-division-by-zero convention is not "
        "established here; if it returns na the branch taken differs. "
        "Recorded, not guessed.",
        "Pine treats an na ternary condition as false, so warmup bars fall "
        "through to the downT leg and AlphaTrend becomes na, not 0.",
        "The short entry's `when=ta.crossunder(high, AlphaTrend)` is the same "
        "expression as the enclosing else-if and can never be false there.",
        "plot(AlphaTrend) is display-only and is not reproduced.",
        "md/source check: the md's embedded PineScript block is line-for-line "
        "identical to sources/SM_7259860f816499c5.pine, and its argument table "
        "(5 / 14 / source) matches the three input() defaults. The only "
        "difference is rendering: the table shows v_input_source_1's default as "
        "the index 0 instead of the label `close`.",
        "/*backtest declares period: 1d on Bitfinex BTC_USD; basePeriod: 1h is "
        "the FMZ backtester's fill granularity, not the strategy's period.",
        "No security() call, no barstate.isrealtime branch, no repainting.",
        "Leverage, margin, liquidation, funding and the venue's contract-step "
        "rounding of order quantities are not modelled.",
    ]

    def pine_indicators(self, dataframe, params):
        coefficient = float(params["coeff"])
        atr_period = int(params["AP"])

        # ATR = ta.sma(ta.tr, AP)  -- ta.tr with handle_na = false.
        true_range = ta.pine_tr(dataframe, handle_na=False)
        atr = ta.pine_sma(true_range, atr_period)

        # The gate is ta.mfi(hlc3, 14) with 14 LITERAL, not AP.
        hl3 = ta.pine_source(dataframe, "hlc3")
        mfi = _pine_mfi(hl3, dataframe["volume"], 14)
        gate_values = (mfi >= 50).to_numpy(dtype=bool)

        low = dataframe["low"].to_numpy(dtype=float)
        high = dataframe["high"].to_numpy(dtype=float)
        atr_values = atr.to_numpy(dtype=float)

        up_t = low - atr_values * coefficient
        down_t = high + atr_values * coefficient

        size = len(dataframe)
        alpha_trend = np.full(size, np.nan)
        for i in range(size):
            # nz(AlphaTrend[1]): na collapses to 0 on the first bar.
            previous = alpha_trend[i - 1] if i >= 1 else np.nan
            reference = previous if np.isfinite(previous) else 0.0
            if gate_values[i]:
                # upT < nz(AlphaTrend[1]) ? nz(AlphaTrend[1]) : upT
                alpha_trend[i] = (
                    reference if up_t[i] < reference else up_t[i]
                )
            else:
                # downT > nz(AlphaTrend[1]) ? nz(AlphaTrend[1]) : downT
                alpha_trend[i] = (
                    reference if down_t[i] > reference else down_t[i]
                )

        line = pd.Series(alpha_trend, index=dataframe.index)
        long_condition = ta.pine_crossover(dataframe["low"], line)
        short_condition = ta.pine_crossunder(dataframe["high"], line)

        dataframe["pine_alphatrend"] = line
        dataframe["pine_long_condition"] = long_condition.to_numpy()
        dataframe["pine_short_condition"] = short_condition.to_numpy()
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "alphatrend": dataframe["pine_alphatrend"].to_numpy(),
            "long_condition": dataframe["pine_long_condition"].to_numpy(),
            "short_condition": dataframe["pine_short_condition"].to_numpy(),
        }

    def pine_script(self, broker, i, ctx):
        # if ta.crossover(low, AlphaTrend)
        #     strategy.entry("BUY", strategy.long)
        # else if ta.crossunder(high, AlphaTrend)
        #     strategy.entry("SELL", strategy.short, when=ta.crossunder(high, AlphaTrend))
        if ctx["long_condition"][i]:
            broker.entry("BUY", "long")
        elif ctx["short_condition"][i]:
            broker.entry("SELL", "short")
