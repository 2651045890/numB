"""Port of sources/SM_ee1e998be59f8142.pine (batch_001/AlphaTrend.md).

Pine v5 (`//@version=5`). KivancOzbilgic's AlphaTrend, with a conversion tool's
order block appended -- the pattern PINE_SEMANTICS.md 1.17 records:

    coeff  = input.float(1, 'Multiplier', step=0.1)
    AP     = input(8, 'Common Period')
    ATR    = ta.sma(ta.tr, AP)
    upT    = low  - ATR * coeff
    downT  = high + ATR * coeff
    AlphaTrend = 0.0
    AlphaTrend := (novolumedata ? ta.rsi(src, AP) >= 50 : ta.mfi(hlc3, AP) >= 50)
                  ? (upT   < nz(AlphaTrend[1]) ? nz(AlphaTrend[1]) : upT)
                  : (downT > nz(AlphaTrend[1]) ? nz(AlphaTrend[1]) : downT)

    buySignalk  = ta.crossover(AlphaTrend, AlphaTrend[2])
    sellSignalk = ta.crossunder(AlphaTrend, AlphaTrend[2])
    K1 = ta.barssince(buySignalk)      K2 = ta.barssince(sellSignalk)
    O1 = ta.barssince(buySignalk[1])   O2 = ta.barssince(sellSignalk[1])

    if buySignalk and showsignalsk and O1 > K2
        strategy.entry("entry long", strategy.long)
    else if sellSignalk and showsignalsk and O2 > K1
        strategy.entry("entry short", strategy.short)

`strategy.entry` does not compile inside `indicator()`, so the trading
behaviour of this source is what the appended block does: enter on the filtered
cross of AlphaTrend and its own 2-bar-offset copy, and NEVER exit. No exit call
of any kind exists in the file -- the two `plotshape` signal markers are
commented out, but neither is an exit -- so a position is only ever ended by
the opposite entry reversing it.

`showsignalsk` is a bool INPUT defaulting to true and is carried in
`source_defaults` and read in `pine_script`, not folded away: with its default
the conditions reduce to the two filtered crosses, but an override to false
turns entries off entirely, which is what the source does.

`O1 > K2` / `O2 > K1` are the source's "the last signal is the fresher one"
filters. `ta.barssince` returns na until its condition has fired once, and na
comparisons are false, so no entry can fire until both crosses have occurred at
least once -- `O1`/`O2` additionally need the PREVIOUS bar's cross, so nothing
fires on the bars of the first signals either. That warmup shape is reproduced
rather than optimised away.

There is no `strategy(...)` call, so the Pine defaults apply: `fixed` /
1 contract, initial capital 1000000, commission 0%, `pyramiding 0`,
`process_orders_on_close=false`.

FIDELITY:

* Converter-appended order block (PINE_SEMANTICS 1.17): the file declares
  `indicator()` and the trailing if / else-if entry pair is what the tool
  added. The port reproduces that block's actual behaviour.
* NO exit call exists in the source, not even a commented-out one, so
  `source_reproduce_stops` is False and a position is only ever ended by the
  opposite entry reversing it.
* No `? -1 : 0` construct is present, so the 1.17 integer-truthiness trap does
  not apply; the if / else-if order (entry long first) is preserved.
* MD / SOURCE DISCREPANCY: the md prose states the AlphaTrend defaults as
  "coefficient: 1 ... common period: 14". The source says
  `AP = input(8, 'Common Period')`, and the md's own argument table also lists
  `v_input_1 | 8 | Common Period`. The source is authoritative (rule 2), so the
  port uses 8; the prose's 14 is recorded, not adopted.
* The md's argument table renders `input.float(1, ...)` as `true`; the
  source's `step=0.1` float default is 1.0.
* `novolumedata` chooses between `ta.rsi(src, AP) >= 50` and
  `ta.mfi(hlc3, AP) >= 50`. Both branches are implemented, since the input is
  exposed by the source; with its default (false) the MFI branch runs.
* `ta.mfi` is not in the shared layer and is written out in `_pine_mfi` from
  its documented definition:
      upper = math.sum(volume * (ta.change(series) <= 0 ? 0 : series), length)
      lower = math.sum(volume * (ta.change(series) >= 0 ? 0 : series), length)
      mfi   = 100.0 - (100.0 / (1.0 + upper / lower))
  The MFI length here is `AP` (8), NOT a hardcoded literal, unlike the sibling
  source AlphaTrend-use-mfi.
* `ta.mfi`'s `upper / lower` when `lower == 0` (a window in which every
  `ta.change(hlc3)` is <= 0) is left to IEEE division, giving `mfi = 100`.
  Pine's own convention for a float division by zero is not established here;
  if the platform returns na instead, that bar would take the `downT` branch
  rather than the `upT` branch. Recorded, not guessed.
* `ta.tr` (bare) is v5's `ta.tr` with `handle_na = false`, i.e. na on the first
  bar. `pine_ta.pine_tr(..., handle_na=False)` is the shared layer's model of
  it, but its pandas pipeline yields `high - low` on the first bar instead of
  na; because `ta.sma` propagates na, the source's ATR-SMA is first valid one
  bar later than the modelled one, advancing the whole upT / downT /
  AlphaTrend chain in the warmup region. This is a documented public-layer
  boundary -- PINE_SEMANTICS 3.7 -- recorded rather than patched locally.
* AlphaTrend is a ratchet (`nz(AlphaTrend[1])` holds the line until a band
  steps past it), so it is walked bar by bar; `nz` collapses the first bar's na
  to 0, and every warmup bar where the ATR or the gate is na evaluates the
  `downT` leg and yields na, exactly as the ternary does in Pine.
* `ta.barssince` returns na until its condition is first true
  (pine_ta.pine_barssince); comparisons against na are false, which is what
  holds the entries off until both crosses have history.
* The two `plotshape` lines are commented out in the source and place no
  order; `color1`, `k1 = plot(...)`, `k2 = plot(...)` and the
  `indicator(..., timeframe='')` argument are display-only.
* `pine_ema` is not used here; `pine_rsi` uses Wilder smoothing (PINE_SEMANTICS
  3.3 for its boundaries).
* `/*backtest` declares `period: 1d` on Bitfinex BTC_USD, so `timeframe` is
  "1d"; `basePeriod: 1d` is the FMZ backtester's own fill granularity.
* No `security()` call, no `barstate.isrealtime` branch, no repainting, no
  `strategy.risk.*` rule.
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


class SMAlphaTrend_ee1e99(PinePortBase, IStrategy):
    source_id = "SM_ee1e998be59f8142"
    source_file = "AlphaTrend.md"
    timeframe = "1d"
    can_short = True
    source_defaults: dict = {
        "coeff": 1.0,
        "AP": 8,
        "src": "close",
        "showsignalsk": True,
        "novolumedata": False,
    }
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    source_reproduce_stops = False
    source_fidelity_notes = [
        "Converter-appended order block (PINE_SEMANTICS 1.17): the file declares "
        "indicator() and the trailing if / else-if entry pair is what the tool "
        "added. The port reproduces that block's actual behaviour -- enter on "
        "the filtered AlphaTrend / AlphaTrend[2] cross, never exit.",
        "NO exit call exists in the source, so source_reproduce_stops is False "
        "and a position is only ever ended by the opposite entry reversing it. "
        "The two plotshape signal markers are commented out and are not exits.",
        "MD / SOURCE DISCREPANCY: the md prose says the AlphaTrend default "
        "'common period' is 14, but the source's AP = input(8, 'Common Period') "
        "and the md's own argument table both say 8. The source is "
        "authoritative (rule 2): the port uses 8. Recorded, not adopted.",
        "No `? -1 : 0` construct is present, so the 1.17 integer-truthiness "
        "trap does not apply; the if / else-if order (entry long first) is "
        "preserved in pine_script.",
        "showsignalsk is a bool input defaulting to true; it is carried in "
        "source_defaults and read in pine_script, so an override to false "
        "turns entries off as the source would.",
        "The gate is (novolumedata ? ta.rsi(src, AP) >= 50 : ta.mfi(hlc3, AP) "
        ">= 50); both branches are implemented because the input is exposed. "
        "The default (false) selects the MFI branch, whose length is AP = 8, "
        "not a literal.",
        "ta.mfi is not in the shared layer; _pine_mfi implements its "
        "documented definition (math.sum weighted by the sign of ta.change, "
        "then 100 - 100/(1 + upper/lower)).",
        "ta.mfi's upper/lower with lower == 0 is left to IEEE division "
        "(mfi = 100). Pine's float-division-by-zero convention is not "
        "established here; if it returns na the branch taken differs. "
        "Recorded, not guessed.",
        "Bare ta.tr in v5 is handle_na=false (na on bar 0); pine_ta.pine_tr "
        "returns high - low there instead, moving ta.sma(ta.tr, AP)'s seeding "
        "point one bar earlier and with it the whole upT/downT/AlphaTrend "
        "chain. PINE_SEMANTICS 3.7 boundary: recorded, not patched locally.",
        "Pine treats an na ternary condition as false, so warmup bars fall "
        "through to the downT leg and AlphaTrend becomes na, not 0; "
        "nz(AlphaTrend[1]) then collapses that na to 0 on the next bar.",
        "ta.barssince is na until its condition first fires; O1/O2 use the "
        "PREVIOUS bar's cross, so the first signals cannot produce entries and "
        "an na comparison is false -- reproduced, not optimised.",
        "The commented-out plotshape lines, color1, the two plot() calls and "
        "indicator(..., timeframe='') are display-only and are not reproduced.",
        "/*backtest declares period: 1d on Bitfinex BTC_USD; basePeriod: 1d is "
        "the FMZ backtester's fill granularity, not the strategy's period.",
        "No security() call, no barstate.isrealtime branch, no repainting, no "
        "strategy.risk.* rule.",
        "Leverage, margin, liquidation, funding and the venue's contract-step "
        "rounding of order quantities are not modelled.",
    ]

    def pine_indicators(self, dataframe, params):
        coefficient = float(params["coeff"])
        atr_period = int(params["AP"])
        no_volume = bool(params["novolumedata"])

        # ATR = ta.sma(ta.tr, AP)  -- ta.tr with handle_na = false.
        true_range = ta.pine_tr(dataframe, handle_na=False)
        atr = ta.pine_sma(true_range, atr_period)

        # Gate: (novolumedata ? ta.rsi(src, AP) >= 50 : ta.mfi(hlc3, AP) >= 50)
        if no_volume:
            gate = ta.pine_rsi(ta.pine_source(dataframe, str(params["src"])), atr_period) >= 50
            gate_values = gate.fillna(False).to_numpy(dtype=bool)
        else:
            hl3 = ta.pine_source(dataframe, "hlc3")
            gate = _pine_mfi(hl3, dataframe["volume"], atr_period) >= 50
            gate_values = gate.fillna(False).to_numpy(dtype=bool)

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
                alpha_trend[i] = reference if up_t[i] < reference else up_t[i]
            else:
                # downT > nz(AlphaTrend[1]) ? nz(AlphaTrend[1]) : downT
                alpha_trend[i] = reference if down_t[i] > reference else down_t[i]

        line = pd.Series(alpha_trend, index=dataframe.index)
        offset_line = line.shift(2)
        long_condition = ta.pine_crossover(line, offset_line)
        short_condition = ta.pine_crossunder(line, offset_line)

        signals_long = long_condition.astype(float)
        signals_short = short_condition.astype(float)
        k1 = ta.pine_barssince(long_condition)
        k2 = ta.pine_barssince(short_condition)
        o1 = ta.pine_barssince(signals_long.shift(1))
        o2 = ta.pine_barssince(signals_short.shift(1))

        # `and` in Pine requires every operand true; NaN comparisons are false.
        long_entry = (
            long_condition.to_numpy(dtype=bool)
            & (o1.to_numpy(dtype=float) > k2.to_numpy(dtype=float))
        )
        short_entry = (
            short_condition.to_numpy(dtype=bool)
            & (o2.to_numpy(dtype=float) > k1.to_numpy(dtype=float))
        )

        dataframe["pine_alphatrend"] = line
        dataframe["pine_long_condition"] = long_condition.to_numpy()
        dataframe["pine_short_condition"] = short_condition.to_numpy()
        dataframe["pine_long_entry"] = long_entry
        dataframe["pine_short_entry"] = short_entry
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "alphatrend": dataframe["pine_alphatrend"].to_numpy(),
            "long_entry": dataframe["pine_long_entry"].to_numpy(),
            "short_entry": dataframe["pine_short_entry"].to_numpy(),
            "showsignalsk": bool(params["showsignalsk"]),
        }

    def pine_script(self, broker, i, ctx):
        # if buySignalk and showsignalsk and O1 > K2
        #     strategy.entry("entry long", strategy.long)
        # else if sellSignalk and showsignalsk and O2 > K1
        #     strategy.entry("entry short", strategy.short)
        if ctx["long_entry"][i] and ctx["showsignalsk"]:
            broker.entry("entry long", "long")
        elif ctx["short_entry"][i] and ctx["showsignalsk"]:
            broker.entry("entry short", "short")
