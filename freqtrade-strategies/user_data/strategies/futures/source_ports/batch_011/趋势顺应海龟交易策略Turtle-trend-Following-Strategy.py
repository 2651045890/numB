"""batch_011 port of 趋势顺应海龟交易策略Turtle-trend-Following-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-12-14 00:00:00\nend: 2023-12-21 00:00:00\nperiod: 1m\nbasePeriod: 1m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// © Aayonga \n//@version=5\nstrategy(\'帆船探险寻找传说\', overlay=true)\n\nuseDateFilter=input.bool(true,title = "启用回测时间范围限定", group = "回测范围")\nbacktesStarDate=input(timestamp("1 Jan 2015"),title = "开始时间", group = "回测范围")\nbacktestEndDate=input(timestamp("1 Jan 2040"),title = "结束时间",group = "回测范围")\ninTradeWindow= true\n\n\nA = input(50, \'计算的周期\')\n\n\nshallowsea = ta.highest(A)\ndeepsea= ta.lowest(A)\n\n//趋势形成条件\nLength1 = input.int(15, title=\'短期市场平均成本\', minval=1, group=\'市场平均成本\')\nLength2 = input.int(120, title=\'中期市场平均成本\', minval=1, group=\'市场平均成本\')\nLength3 = input.int(220, title=\'长期市场平均成本\', minval=1, group=\'市场平均成本\')\nSMA1 = ta.ema(close, Length1)\nSMA2 = ta.sma(close, Length2)\nSMA3 = ta.sma(close, Length3)\n\n\n//趋势看多\nlongTrend=SMA1>SMA3 and open >SMA3 \n\nshortTrend=SMA1<SMA3 \n\nbullPinBar = ((close > open) and ((open - low) > 0.66* (high - low))) or ((close < open) and ((close - low) > 0.9 * (high - low)))\nbearPinBar = ((close > open) and ((high - close) > 0.75 * (high - low))) or ((close < open) and ((high - open) >0.9 * (high - low)))\n\n\n\nif close > shallowsea[5] and shortTrend and inTradeWindow\n    strategy.entry(\'⛵?\', strategy.short)\n\nif close < deepsea[5] and longTrend and inTradeWindow\n    strategy.entry(\'?\', strategy.long)\n\nif  bullPinBar and inTradeWindow\n    strategy.close(\'⛵?\',comment = \'?\')\n\nif bearPinBar and inTradeWindow\n    strategy.close(\'?\',comment = \'?\')\n\nplot(shallowsea,style=plot.style_area, color=color.new(#71bfef, 0))\nplot(deepsea, style=plot.style_area,color=color.new(#298bd1, 0))\n\n\n'

class SMC7384C570A042D94(PinePortBase, IStrategy):
    source_id = "SM_c7384c570a042d94"
    source_file = '趋势顺应海龟交易策略Turtle-trend-Following-Strategy.md'
    timeframe = '1m'
    can_short = True
    source_defaults = {'useDateFilter': True, 'A': 50, 'Length1': 15, 'Length2': 120, 'Length3': 220}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = False
    source_risk_flags = ['common_subset']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
