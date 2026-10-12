"""Port of sources/SM_c7350b594647226d.pine
(batch_001/Combo-Backtest-123-Reversal-Relative-Volatility-Index.md).

Pine v4, HPotter's "Combo Backtest 123 Reversal & Relative Volatility Index".
Two stateful sub-strategies ANDed, one order per bar:

    Reversal123(Length, KSmoothing, DLength, Level):
        vFast = sma(stoch(close, high, low, Length), KSmoothing)
        vSlow = sma(vFast, DLength)
        pos := close[2] < close[1] and close > close[1]
               and vFast < vSlow and vFast > Level      ?  1
             : close[2] > close[1] and close < close[1]
               and vFast > vSlow and vFast < Level      ? -1
             : nz(pos[1], 0)

    RVI(Period, BuyZone, SellZone):
        StdDev = stdev(close, Period)
        d = iff(close > close[1], 0, StdDev)        // down move
        u = iff(close > close[1], StdDev, 0)        // up move
        nU := (13 * nz(nU[1], 0) + u) / 14          // Wilder-style recursion
        nD := (13 * nz(nD[1], 0) + d) / 14
        nRes = 100 * nU / (nU + nD)
        pos := nRes < BuyZone ? -1 : nRes > SellZone ? 1 : nz(pos[1], 0)

    pos    = posReversal123 == 1 and posRVI == 1  ?  1
           : posReversal123 == -1 and posRVI == -1 ? -1 : 0
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
The `/*backtest` header declares `period: 30m` on Futures_Binance BTC_USDT, so
`timeframe` is "30m"; `basePeriod: 15m` is the FMZ backtester's own granularity
for filling 30m bars, not the strategy's period.

BOTH LEGS ARE STICKY: the reversal leg latches on its entry condition and then
carries `nz(pos[1], 0)`, and the RVI leg latches on a zone break and carries
`nz(pos[1], 0)`. Neither can return to 0 once it has triggered, so the ANDed
result is 0 -- and therefore `close_all` -- exactly when the two legs disagree.

ORDER TIMING is the engine's usual one: orders are placed at the signal bar's
close and fill at the next bar's open. The three calls are mutually exclusive
because `possig` is a single value, so exactly one order per bar and no
entry-and-exit-on-one-bar shape (PINE_SEMANTICS.md 1.13 does not apply).

FIDELITY:

* Pine v4's `stoch(source, high, low, length)` =
  `100 * (source - lowest(low, length)) / (highest(high, length) - lowest(low, length))`
  is written out in `pine_indicators` because `pine_ta` has no `pine_stoch`.
  The source's own argument order (`close, high, low`) is kept.
* `sma(x, 1)` is the identity, so the default `KSmoothing=1` leaves `vFast` as
  the raw stoch; it still goes through `pine_sma` so an override behaves.
* A zero-width stoch window (`highest == lowest`, so the numerator is 0 too) is
  left to 0/0, which yields na -- the same value Pine's division by zero
  produces. It is not special-cased.
* `nU` / `nD` are recursive filters, not rolling sums: the source writes
  `nU := (13 * nz(nU[1], 0) + u) / 14`, so each bar folds in 13/14 of the
  previous bar's value. Reproduced with an explicit bar loop that carries the
  previous value and applies `nz` (a NaN previous value contributes 0).
* `nRes = 100 * nU / (nU + nD)` is na while either accumulator is na, which is
  the whole warm-up: `stdev(close, Period)` is na until its window fills, so
  `u` and `d` are na on alternating bars and the accumulators keep resetting
  through `nz`. This is Pine's own behaviour and is not special-cased.
* A comparison against na is false, so `nRes < BuyZone` / `nRes > SellZone` are
  both false while `nRes` is na and the RVI leg carries `nz(pos[1], 0)`.
* `reverse` is `input(false)` and used in a boolean context (`reverse and
  pos == 1`), not the numeric-comparison trap of PINE_SEMANTICS.md 1.16, so no
  `int()` coercion is needed.
* md vs code (recorded, code followed): the md's argument table lists
  `v_input_3 = true` for `KSmoothing`, but the source declares
  `KSmoothing = input(1, minval=1)`, i.e. 1. The source wins.
* md vs code (recorded, code followed): the md describes the reversal leg as
  going long when the close is higher than the prior two days and the
  stochastic is oversold, and going short on the mirror. The code's long branch
  needs `close[2] < close[1]` (a DOWN bar first) and then `close > close[1]`
  (an UP bar now), with `vFast > Level` (i.e. the stochastic ABOVE 50, not
  oversold). The code is followed.
* md vs code (recorded, code followed): the md says the strategy "goes long
  below 30 RVI and short above 70 RVI". The code's RVI leg is the opposite way
  round -- `nRes < BuyZone` latches -1 (SHORT) and `nRes > SellZone` latches
  +1 (LONG). The code is followed.
* md vs code (recorded): the md never mentions that a leg disagreement flattens
  the position through `close_all`, nor that the RVI is a recursive
  Wilder-smoothed measure of up/down volatility.
* No strategy.exit / stop / limit / trail exists, so `source_reproduce_stops`
  is False; `can_short` is True because the short entry is present.
* Leverage, margin, liquidation, funding, `request.security` and the venue's
  contract-step rounding are not modelled.
"""
import numpy as np
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


class SMCombo123ReversalRvi_c7350b(PinePortBase, IStrategy):
    source_id = "SM_c7350b594647226d"
    source_file = "Combo-Backtest-123-Reversal-Relative-Volatility-Index.md"
    timeframe = "30m"
    can_short = True
    # input() defaults. The two `----` separator inputs are display-only labels
    # and are not parameters; `reverse` is used as written.
    source_defaults: dict = {
        "Length": 14,
        "KSmoothing": 1,
        "DLength": 3,
        "Level": 50,
        "Period": 10,
        "BuyZone": 30,
        "SellZone": 70,
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
        "entry condition and otherwise carries nz(pos[1], 0); the RVI leg "
        "latches on a BuyZone/SellZone break and carries nz(pos[1], 0). The "
        "ANDed result is 0 exactly when the legs disagree, and that 0 issues "
        "close_all.",
        "nU / nD are recursive Wilder-style filters -- (13 * nz(nU[1], 0) + u) / "
        "14 -- not rolling sums, and are carried with an explicit bar loop.",
        "nRes is na while either accumulator is na (the whole warm-up, because "
        "stdev(close, Period) is na until its window fills); na comparisons are "
        "false, so the RVI leg carries its previous state then. Not "
        "special-cased.",
        "The RVI leg's d/u split uses a STRICT `close > close[1]`: an unchanged "
        "close counts as a down move (d = StdDev, u = 0), as the source has it.",
        "md vs code (recorded, code followed): the md's argument table shows "
        "v_input_3 = true for KSmoothing; the source declares "
        "KSmoothing = input(1, minval=1) = 1.",
        "md vs code (recorded, code followed): the md's reversal description "
        "has the long condition backwards -- the code's long branch needs "
        "close[2] < close[1] AND close > close[1] AND vFast > Level.",
        "md vs code (recorded): the md never mentions that a leg disagreement "
        "flattens through close_all, nor the RVI's recursive construction.",
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
        period = int(params["Period"])
        buy_zone = float(params["BuyZone"])
        sell_zone = float(params["SellZone"])

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

        # ---- RVI ---------------------------------------------------------
        stddev = ta.pine_stdev(close, period)
        # iff(close > close[1], 0, StdDev) / iff(close > close[1], StdDev, 0).
        # An na comparison is false in Pine, so bar 0 takes the same branch a
        # false comparison would; both readings land on the same accumulator
        # value because nz(na) is 0 on the next bar.
        up_move = (close > close.shift(1)).fillna(False).to_numpy(dtype=bool)
        stddev_values = stddev.to_numpy(dtype=float)
        d_values = np.where(up_move, 0.0, stddev_values)
        u_values = np.where(up_move, stddev_values, 0.0)

        n_u = 0.0
        n_d = 0.0
        nres_values = np.full(len(dataframe), np.nan, dtype=float)
        pos_rvi = np.zeros(len(dataframe), dtype=float)
        carried = 0.0
        for i in range(len(dataframe)):
            # nU := (13 * nz(nU[1], 0) + u) / 14
            n_u = (13.0 * (0.0 if np.isnan(n_u) else n_u) + u_values[i]) / 14.0
            n_d = (13.0 * (0.0 if np.isnan(n_d) else n_d) + d_values[i]) / 14.0
            # nRes = 100 * nU / (nU + nD)
            denominator = n_u + n_d
            n_res = 100.0 * n_u / denominator if denominator != 0.0 else np.nan
            nres_values[i] = n_res
            # pos := nRes < BuyZone ? -1 : nRes > SellZone ? 1 : nz(pos[1], 0)
            if not np.isnan(n_res) and n_res < buy_zone:
                carried = -1.0
            elif not np.isnan(n_res) and n_res > sell_zone:
                carried = 1.0
            pos_rvi[i] = carried

        # ---- combination -------------------------------------------------
        combined = np.where(
            (reversal == 1) & (pos_rvi == 1), 1.0,
            np.where((reversal == -1) & (pos_rvi == -1), -1.0, 0.0),
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
        dataframe["pine_nres"] = nres_values
        dataframe["pine_pos_rvi"] = pos_rvi
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
