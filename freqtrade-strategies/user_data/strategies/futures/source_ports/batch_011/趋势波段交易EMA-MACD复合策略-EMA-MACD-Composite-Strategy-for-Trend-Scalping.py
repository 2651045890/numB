"""batch_011 port of 趋势波段交易EMA-MACD复合策略-EMA-MACD-Composite-Strategy-for-Trend-Scalping.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2019-12-23 08:00:00\nend: 2024-12-10 08:00:00\nperiod: 1d\nbasePeriod: 1d\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This Pine Script™ code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © YDMykael\n\n//@version=6\n//@version=5\nstrategy("TrendScalp Bot", overlay=true, default_qty_type=strategy.percent_of_equity, default_qty_value=100)\n\n// Inputs for indicators\nfastEMA = input.int(50, title="Fast EMA")\nslowEMA = input.int(200, title="Slow EMA")\nrsiPeriod = input.int(14, title="RSI Period")\nmacdFast = input.int(12, title="MACD Fast Length")\nmacdSlow = input.int(26, title="MACD Slow Length")\nmacdSignal = input.int(9, title="MACD Signal Length")\n\n// Indicators\nfastEMAValue = ta.ema(close, fastEMA)\nslowEMAValue = ta.ema(close, slowEMA)\nrsiValue = ta.rsi(close, rsiPeriod)\n[macdLine, signalLine, _] = ta.macd(close, macdFast, macdSlow, macdSignal)\n\n// Trend detection\nisUptrend = fastEMAValue > slowEMAValue\nisDowntrend = fastEMAValue < slowEMAValue\n\n// Entry conditions\nlongCondition = isUptrend and rsiValue > 55 and macdLine > signalLine\nshortCondition = isDowntrend and rsiValue < 45 and macdLine < signalLine\n\n// Plot EMA\nplot(fastEMAValue, color=color.blue, title="Fast EMA")\nplot(slowEMAValue, color=color.red, title="Slow EMA")\n\n// Buy/Sell signals\nif (longCondition)\n    strategy.entry("Buy", strategy.long)\nif (shortCondition)\n    strategy.entry("Sell", strategy.short)\n\n// Exit on opposite signal\nif (not isUptrend or not (macdLine > signalLine))\n    strategy.close("Buy")\nif (not isDowntrend or not (macdLine < signalLine))\n    strategy.close("Sell")\n\n// Alerts\nalertcondition(longCondition, title="Buy Alert", message="TrendScalp Bot: Buy Signal")\nalertcondition(shortCondition, title="Sell Alert", message="TrendScalp Bot: Sell Signal")\n'

class SM87F1EA68F0D2A84C(PinePortBase, IStrategy):
    source_id = "SM_87f1ea68f0d2a84c"
    source_file = '趋势波段交易EMA-MACD复合策略-EMA-MACD-Composite-Strategy-for-Trend-Scalping.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'fastEMA': 50, 'slowEMA': 200, 'rsiPeriod': 14, 'macdFast': 12, 'macdSlow': 26, 'macdSignal': 9}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 100
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = False
    source_risk_flags = ['tuple']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
