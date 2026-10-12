"""Port of sources/SM_9e729c512438b09b.pine (batch_001/Adaptive-Trend-Detection-Strategy-with-Dual-Envelope-EMA-System-基于双包络EMA系统的自适应趋势检测策略.md).

Pine v5. Despite the md's title, the source's own `strategy(title=...)` is
"Andean Oscillator [Strategy]" by alexgrover -- the four `nz(max(...))` /
`nz(min(...))` envelope recursions are the Andean Oscillator, and the trade rule
is the two lines the author marks as "ibA demonštrácia" (demonstration only):

    var float alpha = 2.0 / (length + 1)
    up1 := nz(math.max(C, O, up1[1] - (up1[1] - C) * alpha), C)
    up2 := nz(math.max(C*C, O*O, up2[1] - (up2[1] - C*C) * alpha), C*C)
    dn1 := nz(math.min(C, O, dn1[1] + (C - dn1[1]) * alpha), C)
    dn2 := nz(math.min(C*C, O*O, dn2[1] + (C*C - dn2[1]) * alpha), C*C)
    bull = math.sqrt(dn2 - dn1 * dn1)
    bear = math.sqrt(up2 - up1 * up1)
    signal = ta.ema(math.max(bull, bear), sig_length)

    if bull > bear
        strategy.entry("Long", strategy.long)
    if bear > bull
        strategy.entry("Short", strategy.short)

`signal` is only ever `plot()`ed; no order reads it. There is no exit call of any
kind in the source, so `source_reproduce_stops` is False and a position is closed
only when the opposite `strategy.entry` reverses it (`pyramiding=0`). A position
still open on the last bar stays open.

`/*backtest` header: period 1h on Futures_Binance BTC_USDT; `basePeriod: 1h` is
the FMZ backtester's own fill granularity, not the strategy period.

FIDELITY:

* `math.max` / `math.min` here are the three-argument forms, and they are wrapped
  in `nz(..., C)` because on the first bar `up1[1]` etc. are na. MODELLED CHOICE:
  an na argument makes the max/min na (which is what makes the source's `nz`
  load-bearing), so bar 0 seeds each envelope at the close (up1 = C, up2 = C*C,
  dn1 = C, dn2 = C*C) and bar 0's bull and bear are both 0, hence no order.
  TradingView does not document `math.max`'s na behaviour; the alternative
  reading (na arguments ignored) seeds bar 0 at max(C, O) instead. The two
  seeds differ by at most |C - O| and decay by (1 - alpha) per bar, so they
  converge, but the early bars are a known equivalence risk.
* The `var` declarations matter: `alpha`, `up1`, `up2`, `dn1`, `dn2` are
  initialised once, not per bar. Reproduced as a single forward pass whose
  pre-bar state is na, which is what `var x = 0.` plus the `nz` wrapper means.
* Pine's `math.sqrt` returns na for a negative argument. `dn2 - dn1*dn1` (and
  its up-side twin) is a variance-like quantity and is not guaranteed
  non-negative by construction, so sqrt is applied with Pine's na behaviour
  rather than `np.clip`-ed to 0 -- clipping would invent a bull/bear value the
  source never had.
* `bull > bear` / `bear > bull` are strict, so a bar where the two are equal
  (bar 0, and any bar where both envelopes collapse) fires nothing. The two `if`
  blocks are kept in source order; they are mutually exclusive here anyway.
* `signal` is computed (it is part of the source) but is plot-only: no condition
  reads it, so it cannot change behaviour. Its `ta.ema` seeding is the shared
  layer's modelled choice (PINE_SEMANTICS 3.1) and is therefore inert.
* No exit call exists: `source_reproduce_stops` is False. With `pyramiding=0` a
  repeated same-direction entry is refused, and an opposite entry reverses by
  closing the old position and opening the new one (PINE_SEMANTICS 1.1).
* `strategy(...)` declares `default_qty_type=strategy.percent_of_equity`,
  `default_qty_value=100` and `initial_capital=10000` -- 100% of equity per
  trade, and NOT Pine's 1000000 default capital. It declares no commission, so
  the commission basis is 0%. `pyramiding=0` and `process_orders_on_close=false`
  are Pine's defaults and the source states pyramiding explicitly.
* md vs source: the md is a generic Chinese/English marketing description
  ("Overview / Strategy Principles / Advantages / Risks / Optimization
  Directions") that never names the Andean Oscillator, never states the
  `bull > bear` rule and never lists the two inputs. Two of its claims do not
  describe this source: "内置资金管理系统,限制每次交易的资金使用比例" / "Built-in
  money management system limits position sizes" -- the source's
  `default_qty_value=100` is 100% of equity, i.e. it limits nothing; and
  "Math calculation ... adaptively adjusts sensitivity" -- there is no
  adaptive mechanism beyond the fixed-alpha envelope recursion. The md also
  credits ChaoZhang while the source header is `(c) alexgrover` with a link to
  the alpaca.markets Andean Oscillator article. Recorded, not "fixed": the
  source is the authority (PINE_SEMANTICS, 铁律 2).
* Leverage, margin, liquidation and funding are not modelled by the engine, and
  the venue's contract-step rounding is applied by the framework but not by the
  engine (PINE_SEMANTICS 1.6); the chain verifier measures that separately.
* `plot()` calls and the `overlay=false` / `title` / `shorttitle` arguments are
  display-only and are not reproduced.
"""
import numpy as np
import pandas as pd
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


def _pine_sqrt(values: np.ndarray) -> np.ndarray:
    """`math.sqrt`: na in, na out; negative argument -> na (never complex, never 0)."""
    out = np.full(values.shape, np.nan)
    ok = ~np.isnan(values) & (values >= 0.0)
    out[ok] = np.sqrt(values[ok])
    return out


class SMAdaptiveTrendDetectionStrategyWithDualEnvelopeEmaSystem_9e729c(PinePortBase, IStrategy):
    source_id = "SM_9e729c512438b09b"
    source_file = (
        "Adaptive-Trend-Detection-Strategy-with-Dual-Envelope-EMA-System-"
        "基于双包络EMA系统的自适应趋势检测策略.md"
    )
    timeframe = "1h"
    can_short = True
    source_defaults: dict = {"length": 50, "sig_length": 9}
    source_qty_type = "percent_of_equity"
    source_qty_value = 100.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 10_000.0
    source_reproduce_stops = False
    source_fidelity_notes = [
        "The source's own title is 'Andean Oscillator [Strategy]' (alexgrover); "
        "the md's title describes it as a 'dual envelope EMA' adaptive trend "
        "system. The envelopes are reproduced from the four `nz(max/min(...))` "
        "recursions verbatim, not replaced by any library EMA/envelope.",
        "MODELLED CHOICE: na arguments make `math.max` / `math.min` na, which is "
        "what makes the source's `nz(..., C)` wrappers load-bearing; bar 0 "
        "therefore seeds up1=C, up2=C*C, dn1=C, dn2=C*C. The alternative reading "
        "(na arguments ignored) seeds bar 0 at max(C,O)/min(C,O). The seeds "
        "differ by at most |C-O| and decay by (1-alpha) per bar.",
        "`var` semantics preserved: alpha/up1/up2/dn1/dn2 are initialised once "
        "(pre-bar state na), not per bar.",
        "`math.sqrt` of a negative argument is na in Pine and is na here -- "
        "dn2 - dn1*dn1 is not guaranteed non-negative, and clipping it to 0 "
        "would invent a bull/bear value the source never had.",
        "`bull > bear` / `bear > bull` are kept strict: a bar where they are "
        "equal (bar 0) fires nothing. Both `if` blocks are in source order.",
        "`signal = ta.ema(math.max(bull, bear), sig_length)` is computed but is "
        "plot-only -- no order condition reads it, so it cannot affect trades.",
        "No exit call exists in the source (`source_reproduce_stops=False`): a "
        "position is closed only when the opposite entry reverses it "
        "(pyramiding=0), and a position open at the window end stays open.",
        "Source declares percent_of_equity / 100 and initial_capital=10000 "
        "(100% of equity per trade; NOT Pine's 1000000 default capital). It "
        "declares no commission, so the commission basis is 0%.",
        "md vs source: the md's 'built-in money management limits the position "
        "size' claim contradicts default_qty_value=100 (100% of equity); its "
        "'adaptive sensitivity' claim has no counterpart in the source; the md "
        "credits ChaoZhang while the source header is (c) alexgrover. The "
        "source is the authority; nothing was changed to match the md.",
        "Leverage/margin/liquidation/funding and venue step rounding are outside "
        "the engine (PINE_SEMANTICS 1.6, section 2).",
    ]

    def pine_indicators(self, dataframe, params):
        length = int(params["length"])
        sig_length = int(params["sig_length"])
        alpha = 2.0 / (length + 1.0)
        open_ = dataframe["open"].to_numpy(dtype=float)
        close = dataframe["close"].to_numpy(dtype=float)
        n = len(close)

        up1 = np.full(n, np.nan)
        up2 = np.full(n, np.nan)
        dn1 = np.full(n, np.nan)
        dn2 = np.full(n, np.nan)
        prev_up1 = prev_up2 = prev_dn1 = prev_dn2 = np.nan
        for i in range(n):
            c = close[i]
            o = open_[i]
            c2 = c * c
            o2 = o * o
            # up1 := nz(math.max(C, O, up1[1] - (up1[1] - C) * alpha), C)
            step = prev_up1 - (prev_up1 - c) * alpha
            u1 = c if np.isnan(step) else max(c, o, step)
            # up2 := nz(math.max(C*C, O*O, up2[1] - (up2[1] - C*C) * alpha), C*C)
            step = prev_up2 - (prev_up2 - c2) * alpha
            u2 = c2 if np.isnan(step) else max(c2, o2, step)
            # dn1 := nz(math.min(C, O, dn1[1] + (C - dn1[1]) * alpha), C)
            step = prev_dn1 + (c - prev_dn1) * alpha
            d1 = c if np.isnan(step) else min(c, o, step)
            # dn2 := nz(math.min(C*C, O*O, dn2[1] + (C*C - dn2[1]) * alpha), C*C)
            step = prev_dn2 + (c2 - prev_dn2) * alpha
            d2 = c2 if np.isnan(step) else min(c2, o2, step)
            up1[i], up2[i], dn1[i], dn2[i] = u1, u2, d1, d2
            prev_up1, prev_up2, prev_dn1, prev_dn2 = u1, u2, d1, d2

        bull = _pine_sqrt(dn2 - dn1 * dn1)
        bear = _pine_sqrt(up2 - up1 * up1)
        # math.max(bull, bear): na on either side propagates.
        largest = np.where(np.isnan(bull) | np.isnan(bear), np.nan, np.maximum(bull, bear))
        signal = ta.pine_ema(pd.Series(largest, index=dataframe.index), sig_length)

        dataframe["pine_bull"] = bull
        dataframe["pine_bear"] = bear
        dataframe["pine_signal"] = signal.to_numpy()
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "bull": dataframe["pine_bull"].to_numpy(),
            "bear": dataframe["pine_bear"].to_numpy(),
        }

    def pine_script(self, broker, i, ctx):
        # if bull > bear
        #     strategy.entry("Long", strategy.long, comment="Bull > Bear")
        if ctx["bull"][i] > ctx["bear"][i]:
            broker.entry("Long", "long")
        # if bear > bull
        #     strategy.entry("Short", strategy.short, comment="Bear > Bull")
        if ctx["bear"][i] > ctx["bull"][i]:
            broker.entry("Short", "short")
