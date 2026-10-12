"""Port of sources/SM_f227547f30ba6b13.pine
(batch_001/123反转与费希尔变换指标组合策略123-Reversal-and-Fisher-Transform-Indicator-Combo-Strategy.md).

Pine v4, HPotter's "Combo Backtest 123 Reversal & Fisher Transform Indicator".
Same order shape as its sibling SM_c7350b594647226d -- two stateful
sub-strategies ANDed, one order per bar -- but the second leg is Ehlers' Fisher
transform of `hl2` instead of the relative volatility index:

    Reversal123(Length, KSmoothing, DLength, Level):
        vFast = sma(stoch(close, high, low, Length), KSmoothing)
        vSlow = sma(vFast, DLength)
        pos := close[2] < close[1] and close > close[1]
               and vFast < vSlow and vFast > Level      ?  1
             : close[2] > close[1] and close < close[1]
               and vFast > vSlow and vFast < Level      ? -1
             : nz(pos[1], 0)

    FTI(Length):
        xHL2    = hl2
        xMaxH   = highest(xHL2, Length)
        xMinL   = lowest(xHL2, Length)
        nValue1 := 0.33 * 2 * ((xHL2 - xMinL) / (xMaxH - xMinL) - 0.5)
                   + 0.67 * nz(nValue1[1])
        nValue2 = nValue1 > .99 ?  .999
                : nValue1 < -.99 ? -.999 : nValue1
        nFish   := 0.5 * log((1 + nValue2) / (1 - nValue2))
                   + 0.5 * nz(nFish[1])
        pos := nFish > nz(nFish[1]) ? 1
             : nFish < nz(nFish[1]) ? -1 : nz(pos[1], 0)

    pos    = posReversal123 == 1 and posFTI == 1  ?  1
           : posReversal123 == -1 and posFTI == -1 ? -1 : 0
    possig = reverse ? -pos : pos

    if possig == 1
        strategy.entry("Long", strategy.long)
    if possig == -1
        strategy.entry("Short", strategy.short)
    if possig == 0
        strategy.close_all()

`strategy()` declares only `title` / `shorttitle` / `overlay`, so every
property is Pine's documented default: `strategy.fixed` / 1 contract, initial
capital 1000000, commission 0%, pyramiding 0, `process_orders_on_close=false`.
The `/*backtest` header declares `period: 4h` on Futures_Binance BTC_USDT, so
`timeframe` is "4h"; `basePeriod: 15m` is the FMZ backtester's own granularity
for filling 4h bars, not the strategy's period.

BOTH LEGS ARE STICKY: the reversal leg latches and carries `nz(pos[1], 0)`; the
Fisher leg latches on the direction of `nFish` and carries `nz(pos[1], 0)` when
`nFish` is exactly unchanged. The ANDed result is 0 -- therefore `close_all` --
exactly when the two legs disagree.

ORDER TIMING is the engine's usual one: orders are placed at the signal bar's
close and fill at the next bar's open. `possig` is a single value, so exactly
one of the three calls fires per bar and no entry-and-exit-on-one-bar shape
arises (PINE_SEMANTICS.md 1.13 does not apply).

FIDELITY:

* Pine v4's `stoch(source, high, low, length)` =
  `100 * (source - lowest(low, length)) / (highest(high, length) - lowest(low, length))`
  is written out in `pine_indicators` because `pine_ta` has no `pine_stoch`.
  The source's own argument order (`close, high, low`) is kept.
* `sma(x, 1)` is the identity, so the default `KSmoothing=1` leaves `vFast` as
  the raw stoch; it still goes through `pine_sma` so an override behaves.
* A zero-width stoch window (`highest == lowest`, so the numerator is 0 too) is
  left to 0/0, which yields na -- the same value Pine's division by zero
  produces. The FTI's `(xHL2 - xMinL) / (xMaxH - xMinL)` is guarded the same
  way (an all-equal `hl2` window yields na). Neither is special-cased beyond
  that.
* The Fisher leg is TWO recursive filters, not rolling statistics:
  `nValue1 := 0.33 * 2 * (...) + 0.67 * nz(nValue1[1])` and
  `nFish := 0.5 * log(...) + 0.5 * nz(nFish[1])`. Both are carried with explicit
  bar loops and `nz` (a NaN previous value contributes 0).
* The clamp is strict and asymmetric on purpose: `> .99` and `< -.99` are the
  source's bounds, so a value of exactly +/-0.99 is NOT clamped.
* `0.33 * 2 * (...)` keeps the source's evaluation order rather than folding the
  constant, because float multiplication is not associative.
* `nFish`'s divisions cannot blow up: `nValue2` is clamped to +/-0.999, so
  `1 - nValue2` stays in [0.001, 1.999].
* A comparison against na is false. `log` of an na argument is na, which makes
  `nFish` na and the Fisher leg carry `nz(pos[1], 0)`; `highest`/`lowest` are na
  until their window fills, so the Fisher leg cannot trigger before `LengthFTI`
  bars have elapsed.
* `reverse` is `input(false)` and used in a boolean context (`reverse and
  pos == 1`), not the numeric-comparison trap of PINE_SEMANTICS.md 1.16, so no
  `int()` coercion is needed.
* md vs code (recorded, code followed): the md's argument table lists
  `v_input_2 = true` for `KSmoothing`, but the source declares
  `KSmoothing = input(1, minval=1)`, i.e. 1. The source wins.
* md vs code (recorded, code followed): the md describes the 123 reversal as
  "prices gaping significantly over three consecutive days with the third day
  closing in the opposite direction of the previous two days", and the source's
  own header comment adds that the long side wants an oversold stochastic. The
  code's long branch needs `close[2] < close[1]` (a DOWN bar first) and then
  `close > close[1]` (an UP bar now), with `vFast > Level` (the stochastic
  ABOVE 50). The code is followed.
* source comment vs code (recorded, code followed): the source's own header
  says the Fisher transform is applied "such as the relative strength index",
  but `FTI` actually normalizes `hl2` over `highest`/`lowest(hl2, Length)` and
  applies `0.5 * ln((1 + x) / (1 - x))` to that -- no RSI is computed anywhere
  in the script. The code is followed.
* md vs code (recorded): the md never mentions that a leg disagreement flattens
  the position through `close_all`.
* No strategy.exit / stop / limit / trail exists, so `source_reproduce_stops`
  is False; `can_short` is True because the short entry is present.
* Leverage, margin, liquidation, funding, `request.security` and the venue's
  contract-step rounding are not modelled.
"""
import numpy as np
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


class SMCombo123ReversalFti_f22754(PinePortBase, IStrategy):
    source_id = "SM_f227547f30ba6b13"
    source_file = (
        "123反转与费希尔变换指标组合策略"
        "123-Reversal-and-Fisher-Transform-Indicator-Combo-Strategy.md"
    )
    timeframe = "4h"
    can_short = True
    # input() defaults. `reverse` is used as written; the source has no
    # display-only separator inputs in this script.
    source_defaults: dict = {
        "Length": 15,
        "KSmoothing": 1,
        "DLength": 3,
        "Level": 50,
        "LengthFTI": 10,
        "reverse": False,
    }
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    source_reproduce_stops = False
    source_fidelity_notes = [
        "Pine v4 `stoch(source, high, low, length)` is written out explicitly "
        "(pine_ta has no pine_stoch): 100 * (close - lowest(low, L)) / "
        "(highest(high, L) - lowest(low, L)), with the source's argument order.",
        "Both legs are STICKY state machines: the reversal leg latches on its "
        "entry condition and otherwise carries nz(pos[1], 0); the Fisher leg "
        "latches on the sign of nFish minus its own previous value and carries "
        "nz(pos[1], 0) when nFish is unchanged. The ANDed result is 0 exactly "
        "when the legs disagree, and that 0 issues close_all.",
        "The Fisher leg is two recursive filters (nValue1 := 0.33 * 2 * (...) + "
        "0.67 * nz(nValue1[1]) and nFish := 0.5 * log(...) + 0.5 * nz(nFish[1])), "
        "not rolling statistics, and are carried with explicit bar loops.",
        "The nValue2 clamp uses the source's STRICT bounds (`> .99`, `< -.99`), "
        "so exactly +/-0.99 is not clamped.",
        "`0.33 * 2 * (...)` keeps the source's evaluation order rather than "
        "folding the constant, because float multiplication is not associative.",
        "A comparison against na is false; log(na) is na, so the Fisher leg "
        "carries its state through the warm-up instead of triggering.",
        "md vs code (recorded, code followed): the md's argument table shows "
        "v_input_2 = true for KSmoothing; the source declares "
        "KSmoothing = input(1, minval=1) = 1.",
        "md vs code (recorded, code followed): the md's reversal description "
        "has the long condition backwards -- the code's long branch needs "
        "close[2] < close[1] AND close > close[1] AND vFast > Level.",
        "md vs code (recorded, code followed): the md describes the Fisher leg "
        "as transforming the RSI; the code normalizes hl2 over "
        "highest/lowest(hl2, LengthFTI) and applies 0.5*ln((1+x)/(1-x)) to it.",
        "md vs code (recorded): the md never mentions that a leg disagreement "
        "flattens through close_all.",
        "No strategy.exit / stop / limit / trail exists, so "
        "source_reproduce_stops is False; can_short is True.",
        "Leverage, margin, liquidation, funding, request.security and "
        "contract-step rounding are not modelled.",
    ]

    @staticmethod
    def _sticky(up, down):
        """pos := up ? 1 : down ? -1 : nz(pos[1], 0), carried bar by bar."""
        up = np.asarray(up, dtype=bool)
        down = np.asarray(down, dtype=bool)
        out = np.zeros(len(up), dtype=float)
        carried = 0.0
        for i in range(len(up)):
            if up[i]:
                carried = 1.0
            elif down[i]:
                carried = -1.0
            out[i] = carried
        return out

    def pine_indicators(self, dataframe, params):
        close = dataframe["close"]
        high = dataframe["high"]
        low = dataframe["low"]
        length = int(params["Length"])
        ksmoothing = int(params["KSmoothing"])
        dlength = int(params["DLength"])
        level = float(params["Level"])
        length_fti = int(params["LengthFTI"])

        # ---- Reversal123 -------------------------------------------------
        # stoch(close, high, low, Length)
        lowest_low = ta.pine_lowest(low, length)
        highest_high = ta.pine_highest(high, length)
        stoch = 100.0 * (close - lowest_low) / (highest_high - lowest_low)
        # vFast = sma(stoch(...), KSmoothing); KSmoothing=1 is the identity.
        v_fast = ta.pine_sma(stoch, ksmoothing)
        v_slow = ta.pine_sma(v_fast, dlength)

        rev_long = (
            (close.shift(2) < close.shift(1))
            & (close > close.shift(1))
            & (v_fast < v_slow)
            & (v_fast > level)
        )
        rev_short = (
            (close.shift(2) > close.shift(1))
            & (close < close.shift(1))
            & (v_fast > v_slow)
            & (v_fast < level)
        )
        reversal = self._sticky(
            rev_long.fillna(False).to_numpy(dtype=bool),
            rev_short.fillna(False).to_numpy(dtype=bool),
        )

        # ---- FTI ---------------------------------------------------------
        x_hl2 = (high + low) / 2.0
        x_max_h = ta.pine_highest(x_hl2, length_fti)
        x_min_l = ta.pine_lowest(x_hl2, length_fti)
        span = (x_max_h - x_min_l).to_numpy(dtype=float)
        hl2_values = x_hl2.to_numpy(dtype=float)
        min_values = x_min_l.to_numpy(dtype=float)

        n_value1 = np.nan
        n_fish = np.nan
        pos_fti = np.zeros(len(dataframe), dtype=float)
        carried = 0.0
        for i in range(len(dataframe)):
            denominator = span[i]
            if denominator == 0.0 or np.isnan(denominator) or np.isnan(hl2_values[i]):
                normalised = np.nan
            else:
                normalised = (hl2_values[i] - min_values[i]) / denominator - 0.5
            # nValue1 := 0.33 * 2 * (...) + 0.67 * nz(nValue1[1])
            n_value1 = (
                0.33 * 2 * normalised
                + 0.67 * (0.0 if np.isnan(n_value1) else n_value1)
            )
            # nValue2 = iff(nValue1 > .99, .999, iff(nValue1 < -.99, -.999, nValue1))
            if not np.isnan(n_value1) and n_value1 > 0.99:
                n_value2 = 0.999
            elif not np.isnan(n_value1) and n_value1 < -0.99:
                n_value2 = -0.999
            else:
                n_value2 = n_value1
            # nFish := 0.5 * log((1 + nValue2) / (1 - nValue2)) + 0.5 * nz(nFish[1])
            previous_fish = 0.0 if np.isnan(n_fish) else n_fish
            n_fish = (
                0.5 * np.log((1.0 + n_value2) / (1.0 - n_value2))
                + 0.5 * previous_fish
            )
            # pos := nFish > nz(nFish[1]) ? 1 : nFish < nz(nFish[1]) ? -1 : nz(pos[1], 0)
            if not np.isnan(n_fish) and n_fish > previous_fish:
                carried = 1.0
            elif not np.isnan(n_fish) and n_fish < previous_fish:
                carried = -1.0
            pos_fti[i] = carried

        # ---- combination -------------------------------------------------
        combined = np.where(
            (reversal == 1) & (pos_fti == 1), 1.0,
            np.where((reversal == -1) & (pos_fti == -1), -1.0, 0.0),
        )
        if params["reverse"]:
            possig = np.where(
                combined == 1, -1.0, np.where(combined == -1, 1.0, combined)
            )
        else:
            possig = combined

        dataframe["pine_stoch"] = stoch
        dataframe["pine_vfast"] = v_fast
        dataframe["pine_vslow"] = v_slow
        dataframe["pine_pos_reversal123"] = reversal
        dataframe["pine_hl2"] = x_hl2
        dataframe["pine_pos_fti"] = pos_fti
        dataframe["pine_pos"] = combined
        dataframe["pine_possig"] = possig
        return dataframe

    def pine_context(self, dataframe, params):
        return {"possig": dataframe["pine_possig"].to_numpy(dtype=float)}

    def pine_script(self, broker, i, ctx):
        possig = ctx["possig"][i]
        # if (possig == 1)
        #     strategy.entry("Long", strategy.long)
        if possig == 1:
            broker.entry("Long", "long")
        # if (possig == -1)
        #     strategy.entry("Short", strategy.short)
        if possig == -1:
            broker.entry("Short", "short")
        # if (possig == 0)
        #     strategy.close_all()
        if possig == 0:
            broker.close_all()
