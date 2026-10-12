"""Port of sources/SM_96514cf998084bd1.pine (batch_001/Ichimoku混合Macd和Tsi综合策略Ichimoku-Mixed-Equilibrium-Table-Macd-and-Tsi-Combined-Strategy.md).

Pine v4 (`strategy("Ichimoku with MACD/ CMF/ TSI", overlay=true,
margin_long=0, margin_short=0)`). Ichimoku + SMA-MACD + Chaikin Money Flow +
True Strength Index, all six conditions ANDed:

    middle(len) => avg(lowest(len), highest(len))
    tenkan  = middle(10)            kijun   = middle(30)
    senkouA = avg(tenkan, kijun)    senkouB = middle(52)
    ss_high = max(senkouA[25], senkouB[25])      # ss_offset-1 = 26-1
    ss_low  = min(senkouA[25], senkouB[25])

    fast_ma = sma_source ? sma(src, 17) : ema(src, 17)
    slow_ma = sma_source ? sma(src, 28) : ema(src, 28)
    macd    = fast_ma - slow_ma
    signal  = sma_signal ? sma(macd, 5) : ema(macd, 5)
    hist    = macd - signal

    tk_cross_bull   = tenkan > kijun
    tk_cross_bear   = tenkan < kijun
    cs_cross_bull   = mom(close, 25) > 0
    cs_cross_bear   = mom(close, 25) < 0
    price_above_kumo = close > ss_high
    price_below_kumo = close < ss_low

    ad = close==high and close==low or high==low ? 0
         : ((2*close-low-high)/(high-low)) * volume
    mf = sum(ad, 8) / sum(volume, 8)

    double_smooth(src, long, short) => ema(ema(src, long), short)
    tsi_value = 100 * (double_smooth(pc,8,8) / double_smooth(abs(pc),8,8))
                with pc = change(close) = close - close[1]

    bullish = tk_cross_bull and cs_cross_bull and price_above_kumo
              and hist > 0 and mf > 0.1 and tsi_value > 0
    bearish = tk_cross_bear and cs_cross_bear and price_below_kumo
              and hist < 0 and mf < -0.1 and tsi_value < 0

    strategy.entry("Long",  strategy.long,  when=bullish and long_entry)
    strategy.entry("Short", strategy.short, when=bearish and short_entry)
    strategy.close("Long",  when=bearish and not short_entry)
    strategy.close("Short", when=bullish and not long_entry)

`strategy()` declares only the title, `overlay` and the two zero margins, so
Pine's documented defaults apply and the port carries them explicitly:
`strategy.fixed` / 1 contract, initial capital 1000000, commission 0%,
pyramiding 0, process_orders_on_close=false. `margin_long`/`margin_short` are
the margin CALL thresholds, not leverage; the engine models unlevered sizing.

The `/*backtest` header declares `period: 1h` on Futures_Binance BTC_USDT, so
`timeframe` is "1h"; its `basePeriod: 15m` is the FMZ backtester's own
granularity for filling those hourly bars, not the strategy's period.

Two "cross" names are level tests, not crosses: `tk_cross_bull` is
`tenkan > kijun` (Pine has no cross there) and `cs_cross_bull` is
`mom(close, 25) > 0`, i.e. the close against the close 25 bars ago. Both are
reproduced as written.

FIDELITY (the full list is in `source_fidelity_notes` below):

* With the default inputs `long_entry = short_entry = true`, BOTH
  `strategy.close` calls are dead: `bearish and not short_entry` and
  `bullish and not long_entry` are false on every bar. The port keeps the
  calls (so the behaviour follows the inputs, as the source does) and the
  positions are only ever changed by an opposite entry, which the engine nets.
* `mom` is not in pine_ta; it is Pine's `source - source[length]` and is
  written out here, with the formula in a comment.
* The md prose disagrees with the code in five places, all recorded and none
  "fixed" in the port: the prose's "天平线上穿基准线" is a CROSS where the code
  tests the LEVEL `tenkan > kijun`; the prose's "先行线在0轴之上" is a zero-line
  test the code never applies to a span (its third term is `mom(close, 25) > 0`);
  the prose's "收盘价在云端之上" refers to the cloud as it stands, while the code
  reads `max(senkouA, senkouB)` 25 bars BACK; the prose calls it 短线 /
  high-frequency short-term trading; and the prose's "reverse trade flattens the
  previous position" happens through the opposite entry, not through the two
  `strategy.close` calls, which are dead under the default inputs.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


def _middle(low: pd.Series, high: pd.Series, length: int) -> pd.Series:
    """Ichimoku `middle(len) => avg(lowest(len), highest(len))`.

    `lowest(len)`/`highest(len)` default to the bar's low / high, and na
    propagates through the window (pine_ta's rolling functions).
    """
    return (ta.pine_lowest(low, length) + ta.pine_highest(high, length)) / 2.0


def _mom(source: pd.Series, length: int) -> pd.Series:
    """Pine `mom(source, length)` = source - source[length].

    Not provided by pine_ta, so the documented formula is written out. na
    propagates from the shifted term.
    """
    return source - source.shift(length)


def _pine_max(a: pd.Series, b: pd.Series) -> pd.Series:
    """Pine `max(a, b)`: na propagates, so numpy's maximum, not Series.max."""
    return pd.Series(
        np.maximum(a.to_numpy(dtype=float), b.to_numpy(dtype=float)),
        index=a.index, dtype=float,
    )


def _pine_min(a: pd.Series, b: pd.Series) -> pd.Series:
    """Pine `min(a, b)`: na propagates (see _pine_max)."""
    return pd.Series(
        np.minimum(a.to_numpy(dtype=float), b.to_numpy(dtype=float)),
        index=a.index, dtype=float,
    )


class SMIchimokuMixedEquilibriumTableMacdAndTsiCombined_96514c(PinePortBase, IStrategy):
    source_id = "SM_96514cf998084bd1"
    source_file = (
        "Ichimoku混合Macd和Tsi综合策略"
        "Ichimoku-Mixed-Equilibrium-Table-Macd-and-Tsi-Combined-Strategy.md"
    )
    timeframe = "1h"
    can_short = True
    source_defaults: dict = {
        "ts_bars": 10,
        "ks_bars": 30,
        "ssb_bars": 52,
        "cs_offset": 26,
        "ss_offset": 26,
        "long_entry": True,
        "short_entry": True,
        "fast_length": 17,
        "slow_length": 28,
        "src": "close",
        "signal_length": 5,
        "sma_source": True,
        "sma_signal": True,
        "lengthA": 8,
        "long": 8,
        "short": 8,
    }
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    # No strategy.exit and no stop/limit/trail leg on any order: both exits are
    # `strategy.close`, i.e. market closes projected as next-open signals.
    source_reproduce_stops = False
    source_fidelity_notes = [
        "With the DEFAULT inputs long_entry = short_entry = true, both "
        "strategy.close calls are dead: `bearish and not short_entry` and "
        "`bullish and not long_entry` are false on every bar. The calls are kept "
        "(they are read from the parameters, so setting an input false revives "
        "them, exactly as in the source) and positions otherwise change only "
        "through an opposite entry, which the engine nets against the open one.",
        "`tk_cross_bull`/`tk_cross_bear` are LEVEL tests (`tenkan > kijun`, "
        "`tenkan < kijun`), not crosses, despite the variable names.",
        "`cs_cross_bull`/`cs_cross_bear` are `mom(close, cs_offset-1) > 0` / "
        "`< 0` with cs_offset-1 = 25, i.e. the close against the close 25 bars "
        "ago. `mom` is not in pine_ta and is written out here as its documented "
        "`source - source[length]`.",
        "The kumo reference is `max(senkouA[ss_offset-1], senkouB[ss_offset-1])` "
        "with ss_offset-1 = 25: the spans are read 25 bars BACK, i.e. the cloud "
        "as it stood then, not displaced into the future. Reproduced as written; "
        "Pine's `max`/`min` propagate na, so numpy's maximum/minimum are used "
        "rather than a pandas reduction that would skip it.",
        "md prose disagreement 1: the prose says the signal is '天平线上穿基准线' "
        "('the Tenkan-sen line crosses above the Kijun-sen line'). The code has no "
        "cross: it tests the LEVEL `tenkan > kijun`, which stays true for the whole "
        "of an extended advance instead of only on the crossing bar.",
        "md prose disagreement 2: the prose says '先行线在0轴之上' ('the Chikou Span "
        "is above the 0 axis'). The code applies no 0-line test to any Senkou or "
        "Chikou span; its third term is `mom(close, cs_offset-1) > 0`, a 25-bar "
        "momentum of the CLOSE, reproduced as written.",
        "md prose disagreement 3: the prose says '收盘价在一目均衡表的云端之上' "
        "('the closing price is above the Ichimoku cloud'). The code's cloud "
        "reference `ss_high` is `max(senkouA, senkouB)` read 25 bars BACK, i.e. the "
        "cloud as it stood then, not the cloud on the current bar. Code followed.",
        "md prose disagreement 4: the prose calls the strategy '短线交易' / "
        "'日内价格趋势' / high-frequency short-term trading. The header's declared "
        "period and the six-condition conjunction decide the frequency; the port "
        "runs on the header's period and adds no timeframe of its own.",
        "md prose disagreement 5: the prose says '当指标发出与之前相反信号时,进行反向"
        "交易平掉之前头寸' ('a reverse trade flattens the previous position'). That "
        "happens only through the OPPOSITE ENTRY, since both strategy.close calls "
        "are dead under the default inputs (see the first note); the engine nets a "
        "reverse entry the same way. The prose does not mention the close calls at "
        "any point, and neither statement contradicts the code's behaviour.",
        "The CMF's `ad` is 0 when `(close==high and close==low) or high==low`, "
        "which is exactly the case where `high-low` is zero, so the guarded "
        "division never produces a 0/0; the port computes the quotient on the "
        "non-zero denominator and substitutes 0 elsewhere.",
        "`sum(ad, lengthA)` / `sum(volume, lengthA)` are na until 8 bars have "
        "elapsed and propagate na, so `mf` is na during warmup and every "
        "condition built on it is false then.",
        "TA.EMA / the TSI smoothing use pine_ta's documented first-value seeding "
        "(PINE_SEMANTICS.md 3.1 lists ta.ema seeding as a parity risk); `pc = "
        "change(close)` is na on the first bar and so the TSI is na until its "
        "recursion seeds.",
        "No strategy.exit anywhere, so source_reproduce_stops is False; both "
        "exits are market closes projected as next-open signals.",
        "Leverage, margin, liquidation, funding and the venue's contract-step "
        "rounding are not modelled. margin_long/margin_short are margin-call "
        "thresholds, not leverage, and place no order condition.",
    ]

    def pine_indicators(self, dataframe, params):
        close = dataframe["close"].astype(float)
        high = dataframe["high"].astype(float)
        low = dataframe["low"].astype(float)
        volume = dataframe["volume"].astype(float)

        ts_bars = int(params["ts_bars"])
        ks_bars = int(params["ks_bars"])
        ssb_bars = int(params["ssb_bars"])
        cs_offset = int(params["cs_offset"])
        ss_offset = int(params["ss_offset"])

        # ---- Ichimoku components ------------------------------------------
        tenkan = _middle(low, high, ts_bars)
        kijun = _middle(low, high, ks_bars)
        senkou_a = (tenkan + kijun) / 2.0
        senkou_b = _middle(low, high, ssb_bars)
        ss_high = _pine_max(senkou_a.shift(ss_offset - 1), senkou_b.shift(ss_offset - 1))
        ss_low = _pine_min(senkou_a.shift(ss_offset - 1), senkou_b.shift(ss_offset - 1))

        # ---- MACD on the configurable MA family ---------------------------
        src = ta.pine_source(dataframe, params["src"]).astype(float)
        fast_length = int(params["fast_length"])
        slow_length = int(params["slow_length"])
        signal_length = int(params["signal_length"])
        sma_source = bool(params["sma_source"])
        sma_signal = bool(params["sma_signal"])
        if sma_source:
            fast_ma = ta.pine_sma(src, fast_length)
            slow_ma = ta.pine_sma(src, slow_length)
        else:
            fast_ma = ta.pine_ema(src, fast_length)
            slow_ma = ta.pine_ema(src, slow_length)
        macd = fast_ma - slow_ma
        signal = (ta.pine_sma(macd, signal_length) if sma_signal
                  else ta.pine_ema(macd, signal_length))
        hist = macd - signal

        # ---- Ichimoku / kumo conditions -----------------------------------
        tk_cross_bull = tenkan > kijun
        tk_cross_bear = tenkan < kijun
        cs_cross_bull = _mom(close, cs_offset - 1) > 0
        cs_cross_bear = _mom(close, cs_offset - 1) < 0
        price_above_kumo = close > ss_high
        price_below_kumo = close < ss_low

        # ---- CMF ----------------------------------------------------------
        length_a = int(params["lengthA"])
        high_low = high - low
        money_flow_multiplier = (2.0 * close - low - high) / high_low.where(high_low != 0.0)
        ad = (money_flow_multiplier * volume).where(high_low != 0.0, 0.0)
        mf = ta.pine_sum(ad, length_a) / ta.pine_sum(volume, length_a)

        # ---- TSI ----------------------------------------------------------
        long_length = int(params["long"])
        short_length = int(params["short"])
        pc = ta.pine_change(close, 1)
        double_smoothed_pc = ta.pine_ema(ta.pine_ema(pc, long_length), short_length)
        double_smoothed_abs_pc = ta.pine_ema(
            ta.pine_ema(pc.abs(), long_length), short_length
        )
        tsi_value = 100.0 * (double_smoothed_pc / double_smoothed_abs_pc)

        def _and(*series):
            out = pd.Series(True, index=dataframe.index, dtype=bool)
            for item in series:
                out &= item.fillna(False).astype(bool)
            return out

        bullish = _and(
            tk_cross_bull, cs_cross_bull, price_above_kumo,
            hist > 0.0, mf > 0.1, tsi_value > 0.0,
        )
        bearish = _and(
            tk_cross_bear, cs_cross_bear, price_below_kumo,
            hist < 0.0, mf < -0.1, tsi_value < 0.0,
        )

        dataframe["pine_tenkan"] = tenkan
        dataframe["pine_kijun"] = kijun
        dataframe["pine_senkou_a"] = senkou_a
        dataframe["pine_senkou_b"] = senkou_b
        dataframe["pine_ss_high"] = ss_high
        dataframe["pine_ss_low"] = ss_low
        dataframe["pine_macd"] = macd
        dataframe["pine_macd_signal"] = signal
        dataframe["pine_macd_hist"] = hist
        dataframe["pine_mf"] = mf
        dataframe["pine_tsi"] = tsi_value
        dataframe["pine_bullish"] = bullish
        dataframe["pine_bearish"] = bearish
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "bullish": dataframe["pine_bullish"].to_numpy(),
            "bearish": dataframe["pine_bearish"].to_numpy(),
        }

    def pine_script(self, broker, i, ctx):
        long_entry = bool(self.source_parameters()["long_entry"])
        short_entry = bool(self.source_parameters()["short_entry"])
        bullish = bool(ctx["bullish"][i])
        bearish = bool(ctx["bearish"][i])
        # strategy.entry("Long", strategy.long, when=bullish and long_entry)
        broker.entry("Long", "long", when=bullish and long_entry)
        # strategy.entry("Short", strategy.short, when=bearish and short_entry)
        broker.entry("Short", "short", when=bearish and short_entry)
        # strategy.close("Long", when=bearish and not short_entry)
        broker.close("Long", when=bearish and not short_entry)
        # strategy.close("Short", when=bullish and not long_entry)
        broker.close("Short", when=bullish and not long_entry)
