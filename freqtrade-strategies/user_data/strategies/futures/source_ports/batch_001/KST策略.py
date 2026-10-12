"""Port of sources/SM_7630bde3f42d5907.pine (batch_001/KST策略.md).

Pine v4 (`//@version=4`, but see FIDELITY on the `ta.` namespace). The
Know Sure Thing oscillator against its own SMA, long on a cross above, short on
a cross below:

    ROCma1 = sma(roc(close, ROC1), 10)
    ROCma2 = sma(roc(close, ROC2), 10)
    ROCma3 = sma(roc(close, ROC3), 10)
    ROCma4 = sma(roc(close, ROC4), 15)
    KST    = ROCma1 + ROCma2 * 2 + ROCma3 * 3 + ROCma4 * 4
    signal = sma(KST, SMA1)
    ta.crossover(KST, signal)  -> strategy.entry("L", strategy.long)
    ta.crossunder(KST, signal) -> strategy.entry("S", strategy.short)

Only `ROC1..ROC4` and `SMA1` are inputs; the four smoothing lengths (10, 10, 10,
15) are literals in the source and stay literals here.

`strategy()` declares `pyramiding=1`, which is NOT Pine's default 0: a second
entry in a direction that is already open is allowed once, so a repeated
crossover while long stacks a second long rather than being ignored. It also
declares `percent_of_equity` / 100 and `commission_value=0.07`, so the port
carries pyramiding=1, qty_type=percent_of_equity, qty_value=100.0 and
commission 0.07%. Initial capital is unset in the source, hence Pine's
documented default 1000000.

The `/*backtest` header declares `period: 1h` on Futures_Binance BTC_USDT, so
`timeframe` is "1h"; its `basePeriod: 15m` is the FMZ backtester's own
granularity for filling those 1h bars, not the strategy's period.

There is no exit call in the source: a position is closed only by the opposite
entry reversing it, so `source_reproduce_stops` is False and a position open at
the end of the window stays open.

FIDELITY:

* The source is annotated `//@version=4` yet calls `ta.crossover` /
  `ta.crossunder`, which are v5/v6 namespace forms -- v4 spells them bare
  (`crossover(KST, signal)`). The two are the same function; the port reproduces
  what the calls mean, and which annotation the platform resolves changes
  nothing here because no v4-vs-v5 semantic difference applies to the calls
  used (`roc`, `sma`, `crossover`, `crossunder`, `strategy.entry`).
* `roc` is Pine's PERCENT rate of change -- `100 * (source - source[length]) /
  source[length]` -- so KST's units are percent, not price. pine_ta.pine_roc
  implements exactly that.
* The two commented-out guards in the source (`//and KST >= 0`,
  `//and signal >=0`) are commented out and place no condition; they are NOT
  restored, so the port fires on every cross regardless of sign.
* `hline(0)`, `plot(KST, ...)`, `plot(signal, ...)`, the title and `overlay`
  are display-only and are not reproduced.
* `sma` returns na until its window is full and na anywhere in the window
  propagates, which is Pine's behaviour and is what pine_ta.pine_sma does; the
  first KST value therefore needs ROC4 (30) + 15 bars.
* Leverage, margin, liquidation and funding are not modelled; the venue's
  contract-step rounding is not modelled either, so the framework and the
  engine can differ by a rounded quantity (the chain verifier measures that
  separately rather than treating it as a signal difference).
"""
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


class SMKst_7630bd(PinePortBase, IStrategy):
    source_id = "SM_7630bde3f42d5907"
    source_file = "KST策略.md"
    timeframe = "1h"
    can_short = True
    source_defaults: dict = {"ROC1": 10, "ROC2": 15, "ROC3": 20, "ROC4": 30, "SMA1": 9}
    source_qty_type = "percent_of_equity"
    source_qty_value = 100.0
    source_commission_percent = 0.07
    source_pyramiding = 1
    source_initial_capital = 1_000_000.0
    source_reproduce_stops = False
    source_fidelity_notes = [
        "Source is annotated `//@version=4` but calls the v5/v6 `ta.crossover` / "
        "`ta.crossunder` namespace forms; they are the same functions as v4's "
        "bare `crossover` / `crossunder`, and no v4-vs-v5 difference applies to "
        "any call this source uses.",
        "The source's `//and KST >= 0` / `//and signal >=0` guards are commented "
        "out; they are not restored, so every cross fires.",
        "`roc` is Pine's PERCENT rate of change (x100); KST's units are percent.",
        "The four smoothing lengths 10/10/10/15 are literals in the source, not "
        "inputs, and stay literals.",
        "pyramiding=1 is declared by the source (Pine's default is 0), so a "
        "repeated same-direction entry stacks once instead of being ignored.",
        "No exit call exists: a position is closed only by an opposite entry "
        "reversing it, so source_reproduce_stops is False and a position open "
        "at the end of the window stays open.",
        "hline/plot/title/overlay are display-only and are not reproduced.",
        "percent_of_equity sizing is reproduced from the engine's own recorded "
        "fill notional, not re-derived from the live wallet.",
    ]

    def pine_indicators(self, dataframe, params):
        close = dataframe["close"]
        rocma1 = ta.pine_sma(ta.pine_roc(close, int(params["ROC1"])), 10)
        rocma2 = ta.pine_sma(ta.pine_roc(close, int(params["ROC2"])), 10)
        rocma3 = ta.pine_sma(ta.pine_roc(close, int(params["ROC3"])), 10)
        rocma4 = ta.pine_sma(ta.pine_roc(close, int(params["ROC4"])), 15)
        kst = rocma1 + rocma2 * 2 + rocma3 * 3 + rocma4 * 4
        signal = ta.pine_sma(kst, int(params["SMA1"]))
        dataframe["pine_kst"] = kst
        dataframe["pine_kst_signal"] = signal
        dataframe["pine_long_condition"] = ta.pine_crossover(kst, signal)
        dataframe["pine_short_condition"] = ta.pine_crossunder(kst, signal)
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "kst": dataframe["pine_kst"].to_numpy(),
            "kst_signal": dataframe["pine_kst_signal"].to_numpy(),
            "long_condition": dataframe["pine_long_condition"].to_numpy(),
            "short_condition": dataframe["pine_short_condition"].to_numpy(),
        }

    def pine_script(self, broker, i, ctx):
        # if ta.crossover(KST, signal)
        #     strategy.entry("L", strategy.long)
        if ctx["long_condition"][i]:
            broker.entry("L", "long")
        # if ta.crossunder(KST, signal)
        #     strategy.entry("S", strategy.short)
        if ctx["short_condition"][i]:
            broker.entry("S", "short")
