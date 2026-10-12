"""batch_011 port of 经典动态MACD优化交易策略Dynamic-MACD-Optimization-Trading-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-12-01 00:00:00\nend: 2023-12-31 23:59:59\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("优化版MACD交易策略 ", overlay=true)\n\n// 输入参数\nfastLength = input(16, "快速线周期")\nslowLength = input(34, "慢速线周期")\nsignalSmoothing = input(10, "信号线平滑")\nrsiPeriod = input(19, "RSI周期")\noverboughtRsi = 70\noversoldRsi = 30\nvolumeAvgPeriod = input(13, "成交量平均周期")\nstopLossPerc = input.float(10.5, "止损百分比", step=0.1)\ntakeProfitPerc = input.float(0.3, "止盈百分比", step=0.1)\n\n// 计算指标\n[macdLine, signalLine, _] = ta.macd(close, fastLength, slowLength, signalSmoothing)\nrsi = ta.rsi(close, rsiPeriod)\nvolumeAvg = ta.sma(volume, volumeAvgPeriod)\n\n// 交易信号\nlongCondition = ta.crossover(macdLine, signalLine) and macdLine > 0 and rsi < overboughtRsi and volume > volumeAvg\nshortCondition = ta.crossunder(macdLine, signalLine) and macdLine < 0 and rsi > oversoldRsi and volume > volumeAvg\n\n// 止损和止盈\nlongStopLossPrice = close * (1 - stopLossPerc / 100)\nlongTakeProfitPrice = close * (1 + takeProfitPerc / 100)\nshortStopLossPrice = close * (1 + stopLossPerc / 100)\nshortTakeProfitPrice = close * (1 - takeProfitPerc / 100)\n\n// 执行交易\nif longCondition\n    strategy.entry("买入", strategy.long)\n    strategy.exit("买入止损止盈", "买入", stop=longStopLossPrice, limit=longTakeProfitPrice)\n\nif shortCondition\n    strategy.entry("卖出", strategy.short)\n    strategy.exit("卖出止损止盈", "卖出", stop=shortStopLossPrice, limit=shortTakeProfitPrice)'

class SME087E34DF369AB9E(PinePortBase, IStrategy):
    source_id = "SM_e087e34df369ab9e"
    source_file = '经典动态MACD优化交易策略Dynamic-MACD-Optimization-Trading-Strategy.md'
    timeframe = '1h'
    can_short = True
    source_defaults = {'fastLength': 16, 'slowLength': 34, 'signalSmoothing': 10, 'rsiPeriod': 19, 'volumeAvgPeriod': 13, 'stopLossPerc': 10.5, 'takeProfitPerc': 0.3}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = True
    source_risk_flags = ['tuple', 'exit_order']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
