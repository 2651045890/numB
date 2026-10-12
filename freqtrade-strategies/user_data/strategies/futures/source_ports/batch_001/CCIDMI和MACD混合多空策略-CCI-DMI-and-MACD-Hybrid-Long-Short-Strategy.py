"""Port of sources/SM_676cc40039b6a3c5.pine
(batch_001/CCIDMI和MACD混合多空策略-CCI-DMI-and-MACD-Hybrid-Long-Short-Strategy.md).

Pine v5. Three indicators, one combined signal per side:

    cci_value = ta.cci(close, cci_length)          # cci_length default 14
    [di_plus, di_minus, _] = ta.dmi(14, 14)
    [macd_line, signal_line, _] = ta.macd(close, 24, 52, 9)

    buy_signal      = ta.crossover(cci_value, oversold_level)   and di_plus  > di_minus and macd_line > signal_line
    sell_signal     = ta.crossunder(cci_value, overbought_level) and di_minus > di_plus  and macd_line < signal_line
    buy_exit_signal = ta.crossover(cci_value, overbought_level)
    sell_exit_signal= ta.crossunder(cci_value, oversold_level)

    strategy.entry("Buy",  strategy.long,  when=buy_signal)
    strategy.close("Buy",  when=buy_exit_signal)
    strategy.entry("Sell", strategy.short, when=sell_signal)
    strategy.close("Sell", when=sell_exit_signal)

`oversold_level` defaults to -100 and `overbought_level` to 100, so "CCI crosses
its own threshold" is what gates each side, not `cci > 0`; the strict
inequalities and their direction are the source's.

The DMI periods (14, 14) and the MACD periods (24, 52, 9) are LITERALS in the
source, not inputs, and stay literals here. The DMI's third return (ADX) is
bound to `_` and nothing depends on it, so it is not computed; only the two
directional legs are.

`strategy()` declares only `title` and `overlay`, so every other property is
Pine's default: `default_qty_type=strategy.fixed`, `default_qty_value=1`,
commission 0%, `pyramiding=0`, `process_orders_on_close=false`, initial capital
1000000. Both entries pass no `qty`.

The `/*backtest` header declares `period: 1h` on Futures_Binance BTC_USDT, so
`timeframe` is "1h"; its `basePeriod: 15m` is the FMZ backtester's own filling
granularity for those hourly bars.

Only `strategy.entry` and `strategy.close` are used: there is no stop, limit,
profit, loss or trail call anywhere, so `source_reproduce_stops` is False.

FIDELITY:

* `ta.cci` is written out from its published formula, because `pine_ta` has no
  CCI: `(source - ta.sma(source, length)) / (0.015 * ta.dev(source, length))`
  with `ta.dev(source, length) = ta.sma(|source - ta.sma(source, length)|,
  length)`. Both `ta.sma` calls are Pine's `pine_sma` (na until the window is
  full, na inside the window propagates), not pandas defaults.
* `ta.dmi` is likewise written out. Its true range is the BARE `ta.tr`
  (`handle_na=false`), which is na on the FIRST bar because there is no
  `close[1]`; PINE_SEMANTICS.md section 3.7 records that `pine_ta.pine_tr`
  returns `high - low` on that bar instead, which would start the `rma` window
  one bar early and shift the whole DI series (converging later). Because that
  na is part of the source's own initialisation, true range is built explicitly
  here and `close[1]`'s na is allowed to propagate; `pine_atr` (the
  `handle_na=true` series) is deliberately NOT used. The correction is
  idempotent if the shared layer is ever fixed.
* `plusDM` / `minusDM` keep the source's na: the outer `na(up) ? na : ...`
  ternary wins over the inner one, so the first bar enters the `rma` as na and
  does not consume a smoothing step. The na is restored explicitly instead of
  being coalesced to 0.
* `ta.dmi` wraps both directional legs in `fixnan`; `fixnan` is not in
  `pine_ta`, so it is written out as a forward fill, which is its documented
  behaviour (replace na with the last non-na value).
* MEASURED CHOICE: `100 * di / truerange` divides by a possibly-zero
  `truerange`. Pine's behaviour there is not published; pandas' +/-inf is
  mapped onto na before the forward fill, which feeds it exactly like a warmup
  na. `truerange` is never 0 on BTC data.
* `pandas.Series.max(axis=1)` skips na by default; the true range is built with
  `skipna=False` so the first bar's na actually propagates, which is what the
  source's `ta.tr` does.
* `ta.macd(close, 24, 52, 9)` is `pine_ta.pine_macd`; its EMA seeding is the
  modelled 'first non-na value' choice (PINE_SEMANTICS.md section 3.1), a parity
  risk versus TradingView's unpublished seeding. The histogram leg is bound to
  `_` in the source and is not used.
* `hline` / `plot` / the title / `overlay` are display-only.
* Leverage, margin, liquidation, funding and contract-step rounding are not
  modelled; the chain verifier measures the rounding separately.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


def _fixnan(series: pd.Series) -> pd.Series:
    """Pine `fixnan`: replace na with the last non-na value."""
    return series.ffill()


def _finite(series: pd.Series) -> pd.Series:
    """Pine division by zero is na; pandas gives +/-inf. Fold inf onto na."""
    return series.where(np.isfinite(series), np.nan)


def _pine_cci(source: pd.Series, length: int) -> pd.Series:
    """Pine `ta.cci(source, length)`.

    cci = (source - ta.sma(source, length)) / (0.015 * ta.dev(source, length))
    ta.dev(source, length) = ta.sma(|source - ta.sma(source, length)|, length)
    """
    basis = ta.pine_sma(source, length)
    deviation = ta.pine_sma((source - basis).abs(), length)
    return _finite((source - basis) / (0.015 * deviation))


def _pine_dmi_legs(dataframe: pd.DataFrame, di_length: int):
    """The two directional legs of Pine `ta.dmi(diLength, adxSmoothing)`.

        up        = ta.change(high)
        down      = -ta.change(low)
        plusDM    = na(up)   ? na : (up   > down and up   > 0 ? up   : 0)
        minusDM   = na(down) ? na : (down > up   and down > 0 ? down : 0)
        truerange = ta.rma(ta.tr, diLength)
        plus      = fixnan(100 * ta.rma(plusDM,  diLength) / truerange)
        minus     = fixnan(100 * ta.rma(minusDM, diLength) / truerange)

    The third `ta.dmi` return (ADX) is bound to `_` in the source and is not
    needed here, so `sum = plus + minus` is not computed either.
    """
    high, low, close = dataframe["high"], dataframe["low"], dataframe["close"]
    up = ta.pine_change(high, 1)
    down = -ta.pine_change(low, 1)

    # The outer `na(...) ? na :` test wins over the inner ternary, so the na is
    # restored after it (writing only the inner ternary would coalesce the first
    # bar to 0 and start the rma window one step early).
    plus_dm = up.where((up > down) & (up > 0), 0.0).where(up.notna(), np.nan)
    minus_dm = down.where((down > up) & (down > 0), 0.0).where(down.notna(), np.nan)

    # `ta.tr` handle_na=false: na on the first bar, so the rma window starts at
    # bar 1. skipna=False is required or pandas drops the na and the window
    # would start one bar early (PINE_SEMANTICS.md section 3.7).
    previous_close = close.shift(1)
    true_range = pd.concat(
        [(high - low).abs(), (high - previous_close).abs(), (low - previous_close).abs()],
        axis=1,
    ).max(axis=1, skipna=False)
    true_range_rma = ta.pine_rma(true_range, di_length)

    plus = _fixnan(_finite(100.0 * ta.pine_rma(plus_dm, di_length) / true_range_rma))
    minus = _fixnan(_finite(100.0 * ta.pine_rma(minus_dm, di_length) / true_range_rma))
    return plus, minus


class SMCciDmiAndMacdHybridLongShort_676cc4(PinePortBase, IStrategy):
    source_id = "SM_676cc40039b6a3c5"
    source_file = "CCIDMI和MACD混合多空策略-CCI-DMI-and-MACD-Hybrid-Long-Short-Strategy.md"
    timeframe = "1h"
    can_short = True
    source_defaults: dict = {
        "cci_length": 14,
        "overbought_level": 100,
        "oversold_level": -100,
    }
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    source_reproduce_stops = False
    source_fidelity_notes = [
        "ta.cci is written out from its published formula because pine_ta has "
        "no CCI: (source - sma(source, n)) / (0.015 * dev(source, n)) with "
        "dev = sma(|source - sma(source, n)|, n). Both smas are Pine's na-aware "
        "pine_sma, not pandas defaults.",
        "ta.dmi is written out too. Its true range is the bare ta.tr "
        "(handle_na=false), which is na on the first bar; PINE_SEMANTICS.md "
        "section 3.7 records that pine_ta.pine_tr returns high-low there "
        "instead, starting the rma window one bar early and shifting the whole "
        "DI series. The na is part of the source's own initialisation, so true "
        "range is built explicitly here (skipna=False) and pine_atr is "
        "deliberately not used. Idempotent if the shared layer is ever fixed.",
        "plusDM / minusDM keep the source's na: the outer `na(up) ? na : ...` "
        "ternary wins over the inner one, so the first bar enters the rma as na "
        "and does not consume a smoothing step.",
        "ta.dmi wraps both directional legs in fixnan; fixnan is not in "
        "pine_ta, so it is written out as a forward fill, its documented "
        "behaviour.",
        "MEASURED CHOICE: 100*di/truerange divides by a possibly-zero "
        "truerange. Pine's behaviour there is not published; pandas' +/-inf is "
        "mapped onto na before the forward fill, which feeds it like a warmup "
        "na. truerange is never 0 on BTC data.",
        "ta.dmi's third return (ADX) is bound to `_` in the source and nothing "
        "depends on it, so it is not computed.",
        "The DMI periods (14, 14) and MACD periods (24, 52, 9) are LITERALS in "
        "the source, not inputs, and stay literals; ta.macd's histogram leg is "
        "bound to `_` and is unused.",
        "ta.macd's EMA seeding is the modelled 'first non-na value' choice "
        "(PINE_SEMANTICS.md section 3.1), a parity risk versus TradingView.",
        "The entry/close calls use `when=` in the source and the same four "
        "calls are made in the same order (entry Buy, close Buy, entry Sell, "
        "close Sell), so the priority between them is unchanged.",
        "strategy() declares only title/overlay, so qty is Pine's default "
        "fixed/1, commission 0%, pyramiding 0, process_orders_on_close=false "
        "and initial capital 1000000.",
        "hline/plot/the title/overlay are display-only.",
        "Leverage, margin, liquidation, funding and contract-step rounding are "
        "not modelled; the chain verifier measures the rounding separately.",
    ]

    def pine_indicators(self, dataframe, params):
        close = dataframe["close"]
        cci_value = _pine_cci(close, int(params["cci_length"]))
        di_plus, di_minus = _pine_dmi_legs(dataframe, 14)
        macd = ta.pine_macd(close, 24, 52, 9)
        macd_line, signal_line = macd["macd"], macd["signal"]

        dataframe["pine_cci"] = cci_value
        dataframe["pine_di_plus"] = di_plus
        dataframe["pine_di_minus"] = di_minus
        dataframe["pine_macd"] = macd_line
        dataframe["pine_macd_signal"] = signal_line

        overbought = float(params["overbought_level"])
        oversold = float(params["oversold_level"])
        # buy_signal = crossover(cci, oversold) and di_plus > di_minus and macd > signal
        dataframe["pine_buy_signal"] = (
            ta.pine_crossover(cci_value, oversold)
            & (di_plus > di_minus)
            & (macd_line > signal_line)
        )
        # sell_signal = crossunder(cci, overbought) and di_minus > di_plus and macd < signal
        dataframe["pine_sell_signal"] = (
            ta.pine_crossunder(cci_value, overbought)
            & (di_minus > di_plus)
            & (macd_line < signal_line)
        )
        dataframe["pine_buy_exit_signal"] = ta.pine_crossover(cci_value, overbought)
        dataframe["pine_sell_exit_signal"] = ta.pine_crossunder(cci_value, oversold)
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "buy_signal": dataframe["pine_buy_signal"].to_numpy(),
            "sell_signal": dataframe["pine_sell_signal"].to_numpy(),
            "buy_exit_signal": dataframe["pine_buy_exit_signal"].to_numpy(),
            "sell_exit_signal": dataframe["pine_sell_exit_signal"].to_numpy(),
        }

    def pine_script(self, broker, i, ctx):
        # strategy.entry("Buy", strategy.long, when=buy_signal)
        broker.entry("Buy", "long", when=bool(ctx["buy_signal"][i]))
        # strategy.close("Buy", when=buy_exit_signal)
        broker.close("Buy", when=bool(ctx["buy_exit_signal"][i]))
        # strategy.entry("Sell", strategy.short, when=sell_signal)
        broker.entry("Sell", "short", when=bool(ctx["sell_signal"][i]))
        # strategy.close("Sell", when=sell_exit_signal)
        broker.close("Sell", when=bool(ctx["sell_exit_signal"][i]))
