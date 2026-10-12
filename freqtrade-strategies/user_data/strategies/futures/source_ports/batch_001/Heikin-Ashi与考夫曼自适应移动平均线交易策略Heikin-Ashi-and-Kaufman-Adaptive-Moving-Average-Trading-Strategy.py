"""Port of sources/SM_84fd998c3522ec8a.pine
(batch_001/Heikin-Ashi与考夫曼自适应移动平均线交易策略Heikin-Ashi-and-Kaufman-Adaptive-Moving-Average-Trading-Strategy.md).

Pine v2 ("HLC3/Kaufman by Marco"). A Kaufman adaptive moving average of hlc3,
compared against a fixed higher-period EMA of hlc3, both passed through one
`request.security` each:

    Length = input(5)            xPrice = input(hlc3)
    Fastend = input(2.5)         Slowend = input(20)
    nfastend = 2/(Fastend + 1)   nslowend = 2/(Slowend + 1)
    xvnoise  = abs(xPrice - xPrice[1])
    nsignal  = abs(xPrice - xPrice[Length])
    nnoise   = sum(xvnoise, Length)
    nefratio = iff(nnoise != 0, nsignal / nnoise, 0)
    nsmooth  = pow(nefratio * (nfastend - nslowend) + nslowend, 2)
    nAMA     = nz(nAMA[1]) + nsmooth * (xPrice - nz(nAMA[1]))

    bha_close  = request.security(syminfo.ticker, timeframe.period, nAMA)
    bmha_close = request.security(syminfo.ticker, res1, hlc3)   // res1 = "D"

    bfma = ema(bmha_close[test], 1)      // test = 1
    bsma = ema(bha_close, sloma)         // sloma = 20

    golong  = crossover(bfma, bsma)   -> strategy.entry("Buy",  strategy.long)
    goshort = crossunder(bfma, bsma)  -> strategy.entry("Sell", strategy.short)

Both `request.security` calls resolve to the CHART's own period: the first
passes `timeframe.period`, and the `/*backtest` header declares `period: 1d`
while `res1` defaults to "D". `pine_ta` has no resampling (PINE_SEMANTICS
section 2, item 1), but on this source's own timeframe neither call needs any:
`bha_close` is `nAMA` and `bmha_close` is `hlc3`. The port therefore computes
them directly and records that the equivalence is tied to `res1` keeping its
"D" default -- a non-default `res1` would need multi-timeframe data the shared
layer does not provide.

`ema(..., 1)` has alpha = 2/(1+1) = 1, so `bfma` is `bmha_close[1]` = `hlc3[1]`
(the one-bar shift is `test`), and `bsma` is a 20-period EMA of KAMA.

`strategy(...)` declares only a title, a shorttitle and `overlay`, so Pine's
documented defaults apply: `fixed` / 1 contract, initial capital 1000000,
commission 0%, `pyramiding 0`, `process_orders_on_close false`. No exit call
exists, so `source_reproduce_stops` is False and a position is closed only by
the opposite entry reversing it.

FIDELITY:

* Pine v2 -> v5 namespace: `abs`, `sum`, `pow`, `iff`, `nz`, `ema`,
  `crossover`, `crossunder`, `request.security`, `syminfo.ticker` and
  `timeframe.period` are v2 bare/namespace forms; every one of them is
  mean-for-mean identical to what the port calls.
* `nAMA` is recursive through `nz(nAMA[1])`, i.e. a 0.0 seed. Reproduced by an
  explicit per-bar loop.
* MODELLING CHOICE on the warm-up of the KAMA filter, made deliberately
  because Pine v2's `sum` na-handling and `iff` na-handling are both
  undocumented. The port follows the two rules the shared layer states for
  itself -- PINE_SEMANTICS section 3.2 (`na` propagates inside a window, and a
  window that is not full is na) and the `pine_ta` note that Pine treats an na
  comparison as false in a boolean context. Consequence: `nnoise` is na for
  bars 0..4, so the guard takes its `else` branch there and `nefratio` is 0.0,
  which makes `nsmooth` `nslowend**2` and starts `nAMA` from a very small
  value on bar 0; from bar 5 the real efficiency ratio takes over. The
  alternative reading -- na propagating out of `iff` as well, leaving `nAMA`
  na until bar 5 -- would instead seed `nAMA` at bar 5 with
  `nsmooth * xPrice[5]` and a zero base. Only the original platform can settle
  which seed it used; both converge long before the signal rate settles, and
  this is recorded rather than presented as certified.
* `xvnoise[0]` and `nsignal[0..4]` are na by construction; both feed only
  through the guarded division above.
* `initial_capital` is not declared, so Pine's 1000000 default is carried.
* Leverage, margin, liquidation and funding are not modelled, and the venue's
  contract-step rounding is not modelled either.
"""
import numpy as np
import pandas as pd
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


def _pine_kama(xprice: pd.Series, length: int, fastend: float, slowend: float) -> pd.Series:
    """Pine v2 Kaufman adaptive moving average of `xprice`.

    `iff(nnoise != 0, nsignal / nnoise, 0)` is modelled as: an na `nnoise`
    fails the comparison (Pine's na-in-boolean-context rule), so the else
    branch -- 0.0 -- is taken, and a zero `nnoise` takes it too.
    """
    nfastend = 2.0 / (fastend + 1.0)
    nslowend = 2.0 / (slowend + 1.0)
    xvnoise = (xprice - xprice.shift(1)).abs()
    nsignal = (xprice - xprice.shift(length)).abs()
    nnoise = xvnoise.rolling(length, min_periods=length).sum()
    with np.errstate(divide="ignore", invalid="ignore"):
        ratio = nsignal / nnoise
    efratio = ratio.where(nnoise != 0.0, 0.0)

    nsmooth = (efratio * (nfastend - nslowend) + nslowend) ** 2
    values = xprice.to_numpy(dtype=float)
    smooth = nsmooth.to_numpy(dtype=float)
    out = np.full(len(values), np.nan)
    previous = np.nan
    for i in range(len(values)):
        base = 0.0 if np.isnan(previous) else float(previous)  # nz(nAMA[1])
        out[i] = base + smooth[i] * (values[i] - base)
        previous = out[i]
    return pd.Series(out, index=xprice.index, dtype=float)


class SMHeikinAshiKaufmanAma_84fd99(PinePortBase, IStrategy):
    source_id = "SM_84fd998c3522ec8a"
    source_file = (
        "Heikin-Ashi与考夫曼自适应移动平均线交易策略"
        "Heikin-Ashi-and-Kaufman-Adaptive-Moving-Average-Trading-Strategy.md"
    )
    timeframe = "1d"
    can_short = True
    source_defaults: dict = {
        "res1": "D",
        "test": 1,
        "sloma": 20,
        "Length": 5,
        "xPrice": "hlc3",
        "Fastend": 2.5,
        "Slowend": 20,
    }
    # strategy(title, shorttitle, overlay) -- Pine defaults elsewhere.
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    source_reproduce_stops = False
    source_fidelity_notes = [
        "Both request.security calls resolve to the chart's own period: one "
        "passes timeframe.period, the other passes res1 whose default is \"D\" "
        "and the source's /*backtest period is 1d. bha_close is therefore nAMA "
        "and bmha_close is hlc3; the port computes them directly. A non-default "
        "res1 would need multi-timeframe data, which pine_ta does not model "
        "(PINE_SEMANTICS section 2 item 1).",
        "MODELLING CHOICE for the KAMA warm-up: nnoise is na for bars 0..4 "
        "(section 3.2's na-in-window rule) and an na condition takes iff's else "
        "branch (pine_ta's na-in-boolean-context rule), so nefratio is 0.0 "
        "there and nAMA is seeded from nslowend**2 * hlc3 on bar 0. The "
        "alternative reading (na also propagates out of iff, leaving nAMA na "
        "until bar 5) cannot be settled without the original platform; "
        "recorded, not presented as certified.",
        "nAMA is recursive through nz(nAMA[1]) (0.0 seed); reproduced with an "
        "explicit per-bar loop.",
        "`ema(..., 1)` has alpha 1, so bfma is exactly bmha_close[1] = hlc3[1]; "
        "the one-bar lag comes from `test`, not from the EMA.",
        "Pine v2 bare builtins (abs/sum/pow/iff/nz/ema/crossover/crossunder) "
        "are mapped to their v5 equivalents; no v2-vs-v5 semantic difference "
        "applies to any call this source uses.",
        "No exit call exists: a position is closed only by the opposite entry "
        "reversing it, so source_reproduce_stops is False.",
        "`strategy()` sets no sizing/capital/commission, so Pine's defaults "
        "apply: fixed / 1 contract, 1000000 initial capital, 0% commission, "
        "pyramiding 0, process_orders_on_close false.",
        "The commented-out Heikin-Ashi block and the commented-out fma/sma "
        "variants are inert and are not restored.",
        "Leverage, margin, liquidation, funding and venue contract-step "
        "rounding are not modelled.",
    ]

    def pine_indicators(self, dataframe, params):
        xprice = ta.pine_source(dataframe, str(params["xPrice"]))
        nama = _pine_kama(
            xprice,
            int(params["Length"]),
            float(params["Fastend"]),
            float(params["Slowend"]),
        )

        # bha_close = request.security(ticker, timeframe.period, nAMA)
        bha_close = nama
        # bmha_close = request.security(ticker, res1, hlc3), res1 == chart period
        bmha_close = ta.pine_source(dataframe, "hlc3")

        test = int(params["test"])
        bfma = ta.pine_ema(bmha_close.shift(test), 1)
        bsma = ta.pine_ema(bha_close, int(params["sloma"]))

        dataframe["pine_kama"] = nama
        dataframe["pine_bfma"] = bfma
        dataframe["pine_bsma"] = bsma
        dataframe["pine_long_condition"] = ta.pine_crossover(bfma, bsma)
        dataframe["pine_short_condition"] = ta.pine_crossunder(bfma, bsma)
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "long_condition": dataframe["pine_long_condition"].to_numpy(),
            "short_condition": dataframe["pine_short_condition"].to_numpy(),
        }

    def pine_script(self, broker, i, ctx):
        # strategy.entry("Buy", strategy.long, when=golong)
        if ctx["long_condition"][i]:
            broker.entry("Buy", "long")
        # strategy.entry("Sell", strategy.short, when=goshort)
        if ctx["short_condition"][i]:
            broker.entry("Sell", "short")
