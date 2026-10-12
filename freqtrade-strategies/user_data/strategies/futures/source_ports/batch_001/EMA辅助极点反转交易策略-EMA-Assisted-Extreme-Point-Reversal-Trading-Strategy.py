"""Port of sources/SM_1bf04bd37adf18c8.pine (batch_001/EMA辅助极点反转交易策略-EMA-Assisted-Extreme-Point-Reversal-Trading-Strategy.md).

Pine v5. A CCI (or Momentum) zero cross, gated by a four-bar RSI extreme, an
optional RSI divergence and a 100-EMA side filter:

    ccimomCross  = input.string('CCI', 'Entry Signal Source', options=['CCI','Momentum'])
    ccimomLength = input.int(10, minval=1)
    useDivergence = input.bool(true, ...)
    rsiOverbought = input.int(65, minval=1)
    rsiOversold   = input.int(35, minval=1)
    rsiLength     = input.int(14, minval=1)

    emaLength = 100                       // literal, not an input
    emaValue  = ta.ema(close, emaLength)

    momLength      = ccimomCross == 'Momentum' ? ccimomLength : 10
    mom            = close - close[momLength]
    cci            = ta.cci(close, ccimomLength)
    ccimomCrossUp  = ccimomCross == 'Momentum' ? ta.cross(mom, 0) : ta.cross(cci, 0)
    ccimomCrossDown = ccimomCross == 'Momentum' ? ta.cross(0, mom) : ta.cross(0, cci)

    up   = ta.rma(math.max(ta.change(src), 0), rsiLength)
    down = ta.rma(-math.min(ta.change(src), 0), rsiLength)
    rsi  = down == 0 ? 100 : up == 0 ? 0 : 100 - 100 / (1 + up / down)

    oversoldAgo   = rsi[0] <= rsiOversold   or rsi[1] <= ... or rsi[3] <= ...
    overboughtAgo = rsi[0] >= rsiOverbought or rsi[1] >= ... or rsi[3] >= ...

    bullishDivergenceCondition = rsi[0] > rsi[1] and rsi[1] < rsi[2]
    bearishDivergenceCondition = rsi[0] < rsi[1] and rsi[1] > rsi[2]

    longEntryCondition  = ccimomCrossUp   and oversoldAgo
                          and (not useDivergence or bullishDivergenceCondition)
                          and close < emaValue
    shortEntryCondition = ccimomCrossDown and overboughtAgo
                          and (not useDivergence or bearishDivergenceCondition)
                          and close > emaValue

    if (longEntryCondition)  -> strategy.entry("Buy",  strategy.long)
    if (shortEntryCondition) -> strategy.entry("Sell", strategy.short)

Both branches of the `ccimomCross` switch are implemented, not just the default
'CCI' one, so overriding `ccimomCross` to 'Momentum' reproduces the source's
other branch rather than silently keeping the CCI legs.

`ta.cci` is not in `pine_ta`, so it is implemented here from Pine's own
definition (see `_pine_cci`), and `ta.dev` inside it from Pine's definition of
the mean absolute deviation about the window's own SMA.

The orders are two market `strategy.entry` calls with no qty, no `when` and no
stop/limit/trail, and there is no exit call anywhere: a position is only ever
closed or reversed by the opposite entry, so `source_reproduce_stops` is False
and a position open at the end of the window stays open.

`strategy("Extreme Points + 100 EMA Strategy", overlay=true)` declares only
`title` and `overlay`, so qty type `strategy.fixed` / 1 contract, initial
capital 1000000, commission 0%, `pyramiding` 0 and
`process_orders_on_close=false` are Pine's documented defaults.

The `/*backtest` header declares `period: 3d` on Futures_Binance BTC_USDT;
`basePeriod: 3d` matches it, so 3d is the strategy's own period here.

FIDELITY:

* `ta.cci(source, length) = (source - ta.sma(source, length)) / (0.015 * dev)`
  where `ta.dev` is the MEAN ABSOLUTE deviation of the window about that same
  window's SMA -- not `ta.stdev` and not a sample deviation. `pine_ta` has no
  `ta.cci` / `ta.dev`, so both are written out in `_pine_cci`. The window
  propagates na and is na until it is full, matching Pine.
* MODELLED CHOICE: `ta.dev == 0` is a zero-width window (the price did not move
  for `length` bars) and CCI is then undefined; Pine's float arithmetic yields
  na and the port returns na there rather than +/-inf.
* MODELLED CHOICE: the port implements Pine's own `ta.rsi` arithmetic inline
  (`down == 0 ? 100 : up == 0 ? 0 : 100 - 100/(1 + up/down)`) rather than
  calling `pine_ta.pine_rsi`. The two agree on the normal range but differ at
  the edges -- `pine_rsi` short-circuits to 100 whenever the average loss is
  zero and returns na while either average is still forming, whereas this
  source's expression checks `down == 0` FIRST and then `up == 0`, and picks
  its own na path through the nested ternary. The source's own expression is
  what is reproduced.
* `math.max(ta.change(src), 0)` / `-math.min(ta.change(src), 0)` become
  `max(change, 0)` and `max(-change, 0)`; the first bar is na for both because
  `ta.change` is na there, and na propagates through `ta.rma`'s window.
* `oversoldAgo` / `overboughtAgo` read `rsi[0]` through `rsi[3]`, i.e. the
  current bar and the three before it -- not a lagged window. Reproduced with
  three shifts, each na treated as false (Pine's na comparisons are false).
* `useDivergence` is `input.bool(true)` and is read only in `not useDivergence`,
  a plain boolean context with no `!= 0` / `== 0` / arithmetic around it, so
  PINE_SEMANTICS.md 1.16 (Pine v2/v3 bool-as-number) does not apply. It is
  reproduced as a bool and negated, not coerced to an integer.
* `momLength` is `ccimomLength` under 'Momentum' but the literal 10 under 'CCI'
  (the default). The port reproduces both; under the default it is 10, so `mom`
  ignores `ccimomLength` entirely and `ccimomLength` only reaches `ta.cci`.
* `ta.cross(a, b)` is direction-agnostic -- true on a cross either way -- which
  is why the source uses `ta.cross(cci, 0)` for the up leg and `ta.cross(0, cci)`
  for the down leg with the arguments swapped. Both spell the same symmetric
  test; `pine_cross` is used for each.
* md-vs-source: the md title/prose calls this an "EMA-assisted extreme point
  reversal" strategy; the shipped code has no exit and no stop, so an entry is
  only ever undone by the opposite entry. Recorded, not reconciled.
* `plot` / `plotshape` / `alertcondition` are display-only or order-free
  (PINE_SEMANTICS.md 2.7) and place no condition.
* Leverage, margin, liquidation, funding and the venue's contract-step
  rounding are not modelled; the chain verifier measures the rounding
  separately.
"""
import numpy as np
import pandas as pd
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


def _pine_dev(source: pd.Series, length: int) -> pd.Series:
    """Pine `ta.dev`: mean ABSOLUTE deviation about the window's own SMA.

        ta.dev(source, length) = sma(math.abs(source - sma(source, length)), length)

    evaluated with both `source` and the mean taken over the SAME window, which
    is why it is a windowed apply rather than a rolling mean of a rolling
    residual. na inside the window propagates, and the result is na until the
    window is full.
    """
    length = int(length)

    def _deviation(window: np.ndarray) -> float:
        if np.isnan(window).any():
            return np.nan
        return float(np.abs(window - window.mean()).mean())

    return source.rolling(length, min_periods=length).apply(_deviation, raw=True)


def _pine_cci(source: pd.Series, length: int) -> pd.Series:
    """Pine `ta.cci`:

        (source - ta.sma(source, length)) / (0.015 * ta.dev(source, length))

    Not in `pine_ta`, so written out from Pine's definition. A zero mean
    absolute deviation makes the quotient undefined and is returned as na.
    """
    length = int(length)
    mean = ta.pine_sma(source, length)
    deviation = _pine_dev(source, length)
    with np.errstate(divide="ignore", invalid="ignore"):
        cci = (source - mean) / (0.015 * deviation)
    cci = cci.replace([np.inf, -np.inf], np.nan)
    # A window in which the price never moved has no CCI; na, not infinity.
    return cci.where(deviation != 0.0)


class SMEmaAssistedExtremePointReversal_1bf04b(PinePortBase, IStrategy):
    source_id = "SM_1bf04bd37adf18c8"
    source_file = "EMA辅助极点反转交易策略-EMA-Assisted-Extreme-Point-Reversal-Trading-Strategy.md"
    timeframe = "3d"
    can_short = True
    source_defaults: dict = {
        "ccimomCross": "CCI",
        "ccimomLength": 10,
        "useDivergence": True,
        "rsiOverbought": 65,
        "rsiOversold": 35,
        "rsiLength": 14,
    }
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    source_reproduce_stops = False
    source_fidelity_notes = [
        "ta.cci is not in pine_ta; it is written out from Pine's definition "
        "(source - sma)/(0.015 * ta.dev), with ta.dev the MEAN ABSOLUTE "
        "deviation about the window's own SMA -- not ta.stdev, not a sample "
        "deviation. Both propagate na and are na until the window is full.",
        "MODELLED CHOICE: ta.dev == 0 (price unchanged for `length` bars) leaves "
        "CCI undefined; Pine float arithmetic yields na there, so the port "
        "returns na rather than +/-inf.",
        "MODELLED CHOICE: the source's own ta.rsi arithmetic "
        "(down == 0 ? 100 : up == 0 ? 0 : ...) is implemented inline rather than "
        "calling pine_ta.pine_rsi, which short-circuits to 100 on any zero "
        "average loss and returns na while an average is still forming. The "
        "source's nested ternary and its own na path are what is reproduced.",
        "Both branches of the ccimomCross switch are implemented, not only the "
        "default 'CCI' one, so overriding the parameter reproduces the source's "
        "Momentum branch instead of silently keeping the CCI legs.",
        "momLength is the literal 10 under 'CCI' (the default) and ccimomLength "
        "only under 'Momentum'; under the default mom ignores ccimomLength "
        "entirely and only ta.cci sees it.",
        "oversoldAgo / overboughtAgo read rsi[0]..rsi[3] -- the current bar and "
        "the three before it -- with each na comparison false, as in Pine.",
        "useDivergence is input.bool(true) and is read only in `not "
        "useDivergence`, a plain boolean context with no numeric comparison "
        "around it, so PINE_SEMANTICS.md 1.16 does not apply.",
        "ta.cross(a, b) is symmetric -- true on a cross either way -- which is "
        "why the source writes ta.cross(cci, 0) for the up leg and "
        "ta.cross(0, cci) for the down leg. pine_cross is used for both.",
        "emaLength = 100 is a literal in the source, not an input, and stays a "
        "literal here.",
        "strategy() declares only title/overlay, so qty_type=fixed, qty_value=1, "
        "commission=0, pyramiding=0 and initial_capital=1000000 are Pine's "
        "documented defaults.",
        "md-vs-source: the prose calls this an EMA-assisted extreme point "
        "reversal strategy; the shipped code has no exit and no stop, so a "
        "position is undone only by the opposite entry. Recorded, not "
        "reconciled.",
        "No exit call exists, so source_reproduce_stops is False and a position "
        "open at the window end stays open.",
        "plot/plotshape/alertcondition are display-only or order-free "
        "(PINE_SEMANTICS.md 2.7) and place no condition.",
        "Leverage, margin, liquidation, funding and the venue's contract-step "
        "rounding are not modelled; the chain verifier measures the rounding "
        "separately.",
    ]

    def pine_indicators(self, dataframe, params):
        close = dataframe["close"]
        use_divergence = bool(params["useDivergence"])
        is_momentum = str(params["ccimomCross"]) == "Momentum"

        ema_value = ta.pine_ema(close, 100)

        # momLength = ccimomCross == 'Momentum' ? ccimomLength : 10
        mom_length = int(params["ccimomLength"]) if is_momentum else 10
        mom = close - close.shift(mom_length)
        cci = _pine_cci(close, int(params["ccimomLength"]))

        # `ta.cross(0, x)` passes the constant FIRST. `pine_cross` resolves a
        # scalar only as its second argument, so the constant is materialised as
        # a zero series to keep the source's argument order literal. `ta.cross`
        # is symmetric in its two arguments either way (which is exactly why the
        # source writes the zero on opposite sides for the up and down legs).
        zero_line = pd.Series(0.0, index=close.index)
        if is_momentum:
            cross_up = ta.pine_cross(mom, zero_line)
            cross_down = ta.pine_cross(zero_line, mom)
        else:
            cross_up = ta.pine_cross(cci, zero_line)
            cross_down = ta.pine_cross(zero_line, cci)

        # up = ta.rma(math.max(ta.change(src), 0), rsiLength)
        # down = ta.rma(-math.min(ta.change(src), 0), rsiLength)
        change = ta.pine_change(close)
        average_gain = ta.pine_rma(change.clip(lower=0.0), int(params["rsiLength"]))
        average_loss = ta.pine_rma((-change).clip(lower=0.0), int(params["rsiLength"]))
        # rsi = down == 0 ? 100 : up == 0 ? 0 : 100 - 100 / (1 + up / down)
        with np.errstate(divide="ignore", invalid="ignore"):
            quotient = average_gain / average_loss
            rsi = pd.Series(
                np.where(
                    (average_loss == 0.0).to_numpy(), 100.0,
                    np.where(
                        (average_gain == 0.0).to_numpy(), 0.0,
                        (100.0 - 100.0 / (1.0 + quotient)).to_numpy(),
                    ),
                ),
                index=close.index, dtype=float,
            )

        overbought = float(params["rsiOverbought"])
        oversold = float(params["rsiOversold"])
        oversold_ago = (
            (rsi <= oversold)
            | (rsi.shift(1) <= oversold)
            | (rsi.shift(2) <= oversold)
            | (rsi.shift(3) <= oversold)
        ).fillna(False)
        overbought_ago = (
            (rsi >= overbought)
            | (rsi.shift(1) >= overbought)
            | (rsi.shift(2) >= overbought)
            | (rsi.shift(3) >= overbought)
        ).fillna(False)

        # bullishDivergenceCondition = rsi[0] > rsi[1] and rsi[1] < rsi[2]
        bullish_divergence = ((rsi > rsi.shift(1)) & (rsi.shift(1) < rsi.shift(2))).fillna(False)
        # bearishDivergenceCondition = rsi[0] < rsi[1] and rsi[1] > rsi[2]
        bearish_divergence = ((rsi < rsi.shift(1)) & (rsi.shift(1) > rsi.shift(2))).fillna(False)
        divergence_ok_long = bullish_divergence if use_divergence else pd.Series(True, index=close.index)
        divergence_ok_short = bearish_divergence if use_divergence else pd.Series(True, index=close.index)

        dataframe["pine_ema_value"] = ema_value
        dataframe["pine_mom"] = mom
        dataframe["pine_cci"] = cci
        dataframe["pine_rsi"] = rsi
        dataframe["pine_oversold_ago"] = oversold_ago
        dataframe["pine_overbought_ago"] = overbought_ago
        dataframe["pine_bullish_divergence"] = bullish_divergence
        dataframe["pine_bearish_divergence"] = bearish_divergence
        dataframe["pine_long_condition"] = (
            cross_up.fillna(False)
            & oversold_ago
            & divergence_ok_long
            & (close < ema_value).fillna(False)
        ).fillna(False)
        dataframe["pine_short_condition"] = (
            cross_down.fillna(False)
            & overbought_ago
            & divergence_ok_short
            & (close > ema_value).fillna(False)
        ).fillna(False)
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "long_condition": dataframe["pine_long_condition"].to_numpy(),
            "short_condition": dataframe["pine_short_condition"].to_numpy(),
        }

    def pine_script(self, broker, i, ctx):
        # if (longEntryCondition)
        #     strategy.entry("Buy", strategy.long)
        if ctx["long_condition"][i]:
            broker.entry("Buy", "long")
        # if (shortEntryCondition)
        #     strategy.entry("Sell", strategy.short)
        if ctx["short_condition"][i]:
            broker.entry("Sell", "short")
