"""batch_012 port of 黄金分割式均值回归趋势交易策略Golden-Ratio-Mean-Reversion-Trend-Trading-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2022-11-30 00:00:00\nend: 2023-12-06 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=3\n//\n// A port of the TradeStation EasyLanguage code for a mean-revision strategy described at\n//     http://traders.com/Documentation/FEEDbk_docs/2017/01/TradersTips.html\n//\n// "In “Mean-Reversion Swing Trading,” which appeared in the December 2016 issue of STOCKS & COMMODITIES, author Ken Calhoun\n//  describes a trading methodology where the trader attempts to enter an existing trend after there has been a pullback. \n//  He suggests looking for 50% pullbacks in strong trends and waiting for price to move back in the direction of the trend\n//  before entering the trade."\n//\n//  See Also:\n//    - 9 Mistakes Quants Make that Cause Backtests to Lie (https://blog.quantopian.com/9-mistakes-quants-make-that-cause-backtests-to-lie-by-tucker-balch-ph-d/)\n//    - When Backtests Meet Reality (http://financial-hacker.com/Backtest.pdf)\n//    - Why MT4 backtesting does not work (http://www.stevehopwoodforex.com/phpBB3/viewtopic.php?f=28&t=4020)\n//\n// \n// -----------------------------------------------------------------------------\n// Copyright 2018 sherwind\n//\n// This program is free software: you can redistribute it and/or modify\n// it under the terms of the GNU General Public License as published by\n// the Free Software Foundation, either version 3 of the License, or\n// any later version.\n//\n// This program is distributed in the hope that it will be useful,\n// but WITHOUT ANY WARRANTY; without even the implied warranty of\n// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the\n// GNU General Public License for more details.\n// \n// The GNU General Public License can be found here\n// <http://www.gnu.org/licenses/>.\n//\n// -----------------------------------------------------------------------------\n//\n\nstrategy("Mean-Reversion Swing Trading Strategy v1", shorttitle="MRST Strategy v1", overlay=true)\nchannel_len  = input(defval=20, title="Channel Period", minval=1)\npullback_pct = input(defval=0.5, title="Percent Pull Back Trigger", minval=0.01, maxval=1, step=0.01)\ntrend_filter_len = input(defval=50, title="Trend MA Period", minval=1)\n\n\nupper_band = highest(high, channel_len)\nlower_band = lowest(low, channel_len)\ntrend      = sma(close, trend_filter_len)\n\nlow_ref  = 0.0\nlow_ref  :=  nz(low_ref[1])\nhigh_ref = 0.0\nhigh_ref := nz(high_ref[1])\nlong_ok  = false\nlong_ok  := nz(long_ok[1])\nshort_ok = false\nshort_ok := nz(short_ok[1])\nlong_ok2 = false\nlong_ok2  := nz(long_ok2[1])\n\nif (low == lower_band)\n    low_ref  := low\n    long_ok  := false\n    short_ok := true\n    long_ok2 := false\n\nif (high == upper_band)\n    high_ref := high\n    long_ok  := true\n    short_ok := false\n    long_ok2  := true\n\n// Pull Back Level\ntrigger = long_ok2 ? high_ref - pullback_pct * (high_ref - low_ref) : low_ref + pullback_pct * (high_ref - low_ref)\n\nplot(upper_band, title="Upper Band", color=long_ok2?green:red)\nplot(lower_band, title="Lower Band", color=long_ok2?green:red)\nplot(trigger, title="Trigger", color=purple)\nplot(trend, title="Trend", color=orange)\n\nenter_long = long_ok[1] and long_ok and crossover(close, trigger) and close > trend and strategy.position_size <= 0\nenter_short = short_ok[1] and short_ok and crossunder(close, trigger) and close < trend and strategy.position_size >= 0\n\nif (enter_long)\n    long_ok := false\n    strategy.entry("pullback-long", strategy.long, stop=close, comment="pullback-long")\nelse\n    strategy.cancel("pullback-long")\n\nif (enter_short)\n\tshort_ok := false\n    strategy.entry("pullback-short", strategy.short, stop=close, comment="pullback-short")\nelse\n    strategy.cancel("pullback-short")\n\nstrategy.exit("exit-long", "pullback-long", limit=upper_band, stop=lower_band)\nstrategy.exit("exit-short", "pullback-short", limit=lower_band, stop=upper_band)\n\n'

class SMGoldenRatioMeanReversionTrendTradingStrategy1bdc0d(PinePortBase, IStrategy):
    source_id = "SM_1bdc0d941b46e2dd"
    source_file = '黄金分割式均值回归趋势交易策略Golden-Ratio-Mean-Reversion-Trend-Trading-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'channel_len': 20, 'pullback_pct': 0.5, 'trend_filter_len': 50}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_reproduce_stops = True
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_012 md and exposed through the same PinePortBase interface used by batch_001.', 'The source reads live strategy position state; batch_001-style broker-state parity must be checked manually for this file.']

    def pine_indicators(self, dataframe, params):
        # Runtime evaluates the source against the complete OHLCV frame.
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch012Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
