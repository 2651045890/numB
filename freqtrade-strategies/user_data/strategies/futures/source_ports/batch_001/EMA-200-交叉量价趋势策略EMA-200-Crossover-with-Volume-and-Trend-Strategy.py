"""Port of sources/SM_2015ec1c780f7145.pine (batch_001/EMA-200-交叉量价趋势策略EMA-200-Crossover-with-Volume-and-Trend-Strategy.md).

Pine v5. A "Jurik" line against a 200-period EMA, double-gated by a volume
threshold and a price-vs-EMA test:

    calcola_media_mobile_jurik(source, length) =>
        alpha = 0.5
        sum1 = 0.0
        sum2 = 0.0
        for i = 0 to length - 1
            sum1 := sum1 + (1 - alpha) * math.pow(alpha, i) * source[i]
            sum2 := sum2 + (1 - alpha) * math.pow(alpha, i)
        sum1 / sum2

    ema    = ta.ema(close, ema_periodo)
    jurik  = calcola_media_mobile_jurik(close, jurik_periodo)
    volume_cond = volume > vol_threshold
    uptrend   = ta.crossover(close, ema)   and volume_cond
    downtrend = ta.crossunder(close, ema)  and volume_cond
    long_condition  = uptrend   and ta.crossover(jurik, ema)  and close > ema and jurik < close
    short_condition = downtrend and ta.crossunder(jurik, ema) and close < ema and jurik > close

    strategy.entry("Buy",  strategy.long,  when=long_condition,  qty=risk_position_size)
    strategy.entry("Sell", strategy.short, when=short_condition, qty=risk_position_size)

`strategy()` declares only `title`, `shorttitle` and `overlay`, so every property
is Pine's documented default: `strategy.fixed` / 1 contract, initial capital
1000000, commission 0%, pyramiding 0. `risk_position_size` is the literal 1, so
the entries' `qty=1` is the default quantity too.

There is no exit call: a position is closed only by the opposite entry
reversing it, so `source_reproduce_stops` is False.

THE "JURIK" IS NOT A JURIK MOVING AVERAGE AND IS NOT REPLACED BY ONE. The
function is a FINITE, FIXED-WEIGHT linear filter: with `alpha` hard-coded to 0.5
(the source's own comment calls it "Valore fittizio per alpha", a dummy value)
it is a normalised geometric-weighted mean of the last `length` closes,
weights `(1 - alpha) * alpha ** i` on `close[i]`, divided by their sum. It has
no phase parameter and no adaptive term -- the two things that make a real Jurik
MA a Jurik MA. The port therefore computes the source's own weighted sum
(`_jurik_weights`), not `pine_ta`'s or any library's JMA, and a substitution
would change every value the entries are filtered on.

na handling: the source's loop indexes `source[i]` for i up to `length - 1`,
which is na for the first `length - 1` bars, so `sum1` is na there and `jurik` is
na until bar `length - 1`; `math.exp` of na is na and both crossovers are false
until then.

FIDELITY:

* `risk_position_size = 1` is a LITERAL in the source; the `risk_factor` input
  (default 3, `input.float(minval=0)`) is declared and then NEVER READ by any
  expression in the source. It is kept in `source_defaults` because the source
  declares it, and it is deliberately not wired into the sizing: doing so would
  be inventing behaviour the source does not have.
* `math.pow(alpha, i)` with `alpha = 0.5` gives `0.5 ** i` for i in 0..length-1,
  i.e. 50 weights for the default `jurik_periodo = 50`; the loop's upper bound is
  `length - 1` INCLUSIVE, so exactly `length` terms.
* THE MD CONTRADICTS THE SOURCE in two places, both recorded and not
  reconciled: the md titles the strategy "Jurik 50-100" (and the source's own
  comment says "con fase 100"), but the source has a single `jurik_periodo`
  input and no phase/`fase` parameter at all, so nothing in the code implements
  a 100-period or phase-adjusted variant; and the md describes the entry as
  "price crosses above both averages", while the crossover tests in the code
  are `ta.crossover(close, ema)` (price vs EMA) and `ta.crossover(jurik, ema)`
  (Jurik vs EMA) -- the price/Jurik relation is a LEVEL test (`jurik < close`),
  not a cross.
* `volume` is the frame's own volume column, compared with a strict `>`
  against `vol_threshold` (10000 by default). `volume_cond` gates BOTH sides.
* `plotshape(...)` calls are display-only and are not reproduced.
* `ta.ema` seeding is the modelled choice recorded in PINE_SEMANTICS.md 3.1
  (first non-na value as the seed); Pine does not publish its exact rule, so the
  EMA differs from the original platform in the early bars and converges after.
* Leverage, margin, liquidation and funding are not modelled; the venue's
  contract-step rounding is not modelled either.
"""
import numpy as np
import pandas as pd
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


class SMEma200CrossoverVolumeTrend_2015ec(PinePortBase, IStrategy):
    source_id = "SM_2015ec1c780f7145"
    source_file = "EMA-200-交叉量价趋势策略EMA-200-Crossover-with-Volume-and-Trend-Strategy.md"
    timeframe = "1d"
    can_short = True
    source_defaults: dict = {
        "jurik_periodo": 50,
        "ema_periodo": 200,
        "vol_threshold": 10000,
        "risk_factor": 3,
    }
    # strategy(title, shorttitle, overlay=true): Pine defaults, nothing declared.
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    source_reproduce_stops = False
    source_fidelity_notes = [
        "The `calcola_media_mobile_jurik` function is NOT a Jurik moving average: "
        "it is a finite fixed-weight filter with alpha hard-coded to 0.5 (the "
        "source's own comment calls it a dummy value), no phase and no adaptive "
        "term. The source's own weighted sum is computed; no JMA library is "
        "substituted.",
        "risk_position_size is the literal 1; the risk_factor input (default 3) "
        "is declared by the source but never read by any expression. It is kept "
        "in source_defaults and deliberately not wired into sizing.",
        "The md calls this 'Jurik 50-100' and the source comment mentions phase "
        "100, but the code has one jurik_periodo input and no phase parameter. "
        "Recorded, not reconciled.",
        "The md describes the entry as price crossing above both averages; in "
        "the code the Jurik/price relation is a level test (jurik < close / "
        "jurik > close) and only close-vs-EMA and jurik-vs-EMA are crossovers. "
        "Recorded, not reconciled.",
        "The Jurik filter is na for its first length-1 bars (source[i] is na "
        "there, so the weighted sum is na); both crossovers are false until it "
        "is defined.",
        "volume_cond uses a strict `>` against vol_threshold on the frame's own "
        "volume column, and gates both the long and the short side.",
        "ta.ema seeding is the modelled choice in PINE_SEMANTICS.md 3.1 (first "
        "non-na value seeds the recursion); Pine does not publish its rule, so "
        "early EMA values may differ from the original platform.",
        "No exit call exists: a position is closed only by the opposite entry "
        "reversing it, so source_reproduce_stops is False and a position open "
        "at the end of the window stays open.",
        "plotshape(...) is display-only and is not reproduced.",
    ]

    @staticmethod
    def _jurik(source: pd.Series, length: int) -> pd.Series:
        """`calcola_media_mobile_jurik`: sum((1-a) a^i x[i]) / sum((1-a) a^i), a = 0.5."""
        alpha = 0.5
        index = np.arange(length, dtype=float)
        weights = (1.0 - alpha) * np.power(alpha, index)
        denominator = weights.sum()
        values = source.to_numpy(dtype=float)
        out = np.full(len(values), np.nan)
        for i in range(length - 1, len(values)):
            # window[0] is source[0] = the current bar, window[k] is source[k].
            window = values[i - length + 1 : i + 1][::-1]
            if np.isnan(window).any():
                # an na term makes sum1 na, and na propagates out of the ratio
                continue
            out[i] = float(np.dot(window, weights) / denominator)
        return pd.Series(out, index=source.index, dtype=float)

    def pine_indicators(self, dataframe, params):
        close = dataframe["close"]
        volume = dataframe["volume"]

        ema = ta.pine_ema(close, int(params["ema_periodo"]))
        jurik = self._jurik(close, int(params["jurik_periodo"]))

        volume_cond = (volume > float(params["vol_threshold"])).fillna(False)
        uptrend = ta.pine_crossover(close, ema) & volume_cond
        downtrend = ta.pine_crossunder(close, ema) & volume_cond

        # long  = uptrend   and crossover(jurik, ema) and close > ema and jurik < close
        # short = downtrend and crossunder(jurik, ema) and close < ema and jurik > close
        long_condition = (
            uptrend
            & ta.pine_crossover(jurik, ema)
            & (close > ema).fillna(False)
            & (jurik < close).fillna(False)
        )
        short_condition = (
            downtrend
            & ta.pine_crossunder(jurik, ema)
            & (close < ema).fillna(False)
            & (jurik > close).fillna(False)
        )

        dataframe["pine_ema"] = ema
        dataframe["pine_jurik"] = jurik
        dataframe["pine_volume_cond"] = volume_cond
        dataframe["pine_long_condition"] = long_condition.fillna(False)
        dataframe["pine_short_condition"] = short_condition.fillna(False)
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "long_condition": dataframe["pine_long_condition"].to_numpy(),
            "short_condition": dataframe["pine_short_condition"].to_numpy(),
        }

    def pine_script(self, broker, i, ctx):
        # strategy.entry("Buy", strategy.long, when=long_condition, qty=risk_position_size)
        if ctx["long_condition"][i]:
            broker.entry("Buy", "long", 1)
        # strategy.entry("Sell", strategy.short, when=short_condition, qty=risk_position_size)
        if ctx["short_condition"][i]:
            broker.entry("Sell", "short", 1)
