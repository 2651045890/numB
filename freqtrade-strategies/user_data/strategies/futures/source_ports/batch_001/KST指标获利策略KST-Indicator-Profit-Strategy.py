"""Port of sources/SM_1cce75bc265fa9b0.pine (batch_001/KST指标获利策略KST-Indicator-Profit-Strategy.md).

Pine v5. The Know Sure Thing oscillator against its own SMA, long on a cross
above, short on a cross below:

    smaroc(roclen, smalen) => sma(roc(close, roclen), smalen)
    kst = smaroc(11, 9) + 2 * smaroc(15, 14) + 3 * smaroc(20, 8) + 4 * smaroc(33, 15)
    sig = sma(kst, 9)

    strategy.entry("Long", strategy.long, when = crossover(kst, sig))
    strategy.entry("Short", strategy.short, when = crossunder(kst, sig))

`strategy()` declares only `title`, `shorttitle` and `overlay`, so every
property is Pine's documented default: `strategy.fixed` / 1 contract, initial
capital 1000000, commission 0%, pyramiding 0, `process_orders_on_close=false`.
The two entries carry no `qty`, so the default 1 contract is what fills.

There is no exit call in the source: a position is closed only by the opposite
entry reversing it, so `source_reproduce_stops` is False and a position still
open at the end of the window stays open.

All nine inputs are `input.int(minval=1)`; their defaults are copied verbatim
into `source_defaults` under the source's own variable names. The four
smoothing lengths are NOT literals here -- unlike the other KST source in
batch_001 (`SM_7630bde3f42d5907`, whose smoothing lengths are hard-coded
10/10/10/15) every length in this source is an input, so the two ports must not
share defaults. Verified against the source line by line; the md's argument
table agrees with it.

FIDELITY:

* `ta.roc` is Pine's PERCENT rate of change -- `100 * (source - source[len]) /
  source[len]` -- so the KST's units are percent, not price. `pine_ta.pine_roc`
  implements exactly that.
* The indicator chain is reproduced by the source's own formula, not by a
  library KST: four `sma(roc(close, n), m)` terms with weights 1/2/3/4 and a
  final `sma(kst, 9)`. `pine_ta.pine_sma` returns na until its window is full
  and propagates na inside it, which is Pine's behaviour; the first usable KST
  value therefore needs roclen4(33) + smalen4(15) bars, and `sig` needs a
  further 9. No signal can fire before that, on either side of the comparison.
* The source writes `when=longCondition` on the long entry and
  `when=shortCondition` on the short one; both are kept, in source order.
  `crossover` / `crossunder` are mutually exclusive, so the two can never both
  fire on one bar.
* `plot(kst)`, `plot(sig)`, `hline(0)` and the title/overlay are display-only
  and are not reproduced. The source has no guard such as `and kst >= 0`.
* THE MD'S PROSE CONTRADICTS THE SOURCE and the source is followed. The md
  describes "a stock picking strategy applied to the 30-minute cycle of SPY";
  the source's own `/*backtest` header declares
  `period: 1d` on `Futures_Binance` / `BTC_USDT`, which is what `timeframe`
  below is set from, and the source contains no universe or symbol logic at
  all -- it is a single-instrument signal script. The prose is recorded rather
  than reconciled, and the trading logic is unaffected by the disagreement.
* Leverage, margin, liquidation and funding are not modelled; the venue's
  contract-step rounding is not modelled either, so the framework and the
  engine can differ by a rounded quantity (the chain verifier measures that
  separately rather than treating it as a signal difference).
"""
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


class SMKstIndicatorProfit_1cce75(PinePortBase, IStrategy):
    source_id = "SM_1cce75bc265fa9b0"
    source_file = "KST指标获利策略KST-Indicator-Profit-Strategy.md"
    timeframe = "1d"
    can_short = True
    source_defaults: dict = {
        "roclen1": 11,
        "roclen2": 15,
        "roclen3": 20,
        "roclen4": 33,
        "smalen1": 9,
        "smalen2": 14,
        "smalen3": 8,
        "smalen4": 15,
        "siglen": 9,
    }
    # strategy(title, overlay=true): Pine defaults, nothing declared.
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    source_reproduce_stops = False
    source_fidelity_notes = [
        "No exit call exists in the source: a position is closed only by the "
        "opposite entry reversing it, so source_reproduce_stops is False and a "
        "position open at the end of the window stays open.",
        "roc is Pine's PERCENT rate of change (x100), so kst is in percent.",
        "The four smoothing lengths are `input.int` values in this source (not "
        "literals), so this port's defaults differ from the other batch_001 KST "
        "port SM_7630bde3f42d5907 and must not be shared with it.",
        "sma returns na until its window is full and na propagates through it, "
        "so the first kst value needs roclen4+smalen4 bars and sig a further "
        "siglen; no signal can fire before that.",
        "plot/hline/title/overlay are display-only and are not reproduced.",
        "The md's prose calls this a 30-minute SPY stock-picking strategy; the "
        "source's /*backtest header declares period: 1d on Futures_Binance "
        "BTC_USDT, which is what `timeframe` is taken from. Recorded, not "
        "reconciled; the code has no symbol logic.",
    ]

    def pine_indicators(self, dataframe, params):
        close = dataframe["close"]
        # smaroc(roclen, smalen) => ta.sma(ta.roc(close, roclen), smalen)
        rocma1 = ta.pine_sma(ta.pine_roc(close, int(params["roclen1"])), int(params["smalen1"]))
        rocma2 = ta.pine_sma(ta.pine_roc(close, int(params["roclen2"])), int(params["smalen2"]))
        rocma3 = ta.pine_sma(ta.pine_roc(close, int(params["roclen3"])), int(params["smalen3"]))
        rocma4 = ta.pine_sma(ta.pine_roc(close, int(params["roclen4"])), int(params["smalen4"]))
        # kst = 1*smaroc(1) + 2*smaroc(2) + 3*smaroc(3) + 4*smaroc(4)
        kst = rocma1 + 2 * rocma2 + 3 * rocma3 + 4 * rocma4
        # sig = ta.sma(kst, siglen)
        sig = ta.pine_sma(kst, int(params["siglen"]))

        dataframe["pine_kst"] = kst
        dataframe["pine_kst_signal"] = sig
        dataframe["pine_long_condition"] = ta.pine_crossover(kst, sig)
        dataframe["pine_short_condition"] = ta.pine_crossunder(kst, sig)
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "long_condition": dataframe["pine_long_condition"].to_numpy(),
            "short_condition": dataframe["pine_short_condition"].to_numpy(),
        }

    def pine_script(self, broker, i, ctx):
        # strategy.entry("Long", strategy.long, when=longCondition)
        if ctx["long_condition"][i]:
            broker.entry("Long", "long")
        # strategy.entry("Short", strategy.short, when=shortCondition)
        if ctx["short_condition"][i]:
            broker.entry("Short", "short")
