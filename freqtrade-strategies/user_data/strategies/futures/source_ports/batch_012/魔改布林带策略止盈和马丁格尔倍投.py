"""batch_012 port of 魔改布林带策略止盈和马丁格尔倍投.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '\n//@version=4\nstrategy("Bollinger Bands %B Crossover", overlay=true,pyramiding = 5)\n\n// Load Bollinger Bands %B indicator\nsource = input(close, title="Source")\nlength = input(20, minval=1, title="Length")\nmult = input(2.0, minval=0.001, maxval=50, title="Multiplier")\nbasis = sma(source, length)\ndev = mult * stdev(source, length)\nupper = basis + dev\nlower = basis - dev\nbb = (source - lower) / (upper - lower)\n\n// Define long and short conditions\nlongCondition = crossover(bb, 0)\nshortCondition = crossunder(bb, 1)\n\n// 马丁格尔策略参数\nuseMartin = input(true, title="使用马丁格尔倍投")\ninitialQty = input(0.001, title="初始仓位大小")\nmartinFactor = input(2, title="马丁格尔倍数")\n// 止盈止损\nprofitTarget = input(1.5, title="止盈倍数")\nstopLoss = input(0.95, title="止损倍数")\n//定义触发加仓的百分比\ndropPercentage=10\n//计算当前持仓总成本\ntotalCost=strategy.position_avg_price*strategy.position_size\n//计算当前持仓盈亏\nprofitLoss=(close-totalCost)/totalCost*100\n\n\n\n// 买入条件满足时，产生买入信号，并设置止盈\nif (longCondition)\n\xa0\xa0\xa0 strategy.entry("Buy", strategy.long)\n\xa0\xa0\xa0  if useMartin\n//判断是否需要加仓\nif profitLoss<=-dropPercentage and strategy.position_size >0\n\xa0\xa0\xa0\xa0\xa0\xa0\xa0 strategy.order("Buy1", "Buy",qty=strategy.position_size * martinFactor,when=strategy.long )\nif strategy.position_size >0\n        strategy.exit("Take Profit/Stop Loss", "Buy", profit=strategy.position_avg_price  *profitTarget )\n\n// 卖出条件满足时，产生卖出信号，并设置止盈\nif (shortCondition)\n\xa0\xa0\xa0 strategy.entry("Sell",strategy.short)\n\xa0\xa0\xa0  if useMartin\n//判断是否需要加仓\nif profitLoss<= -dropPercentage and strategy.position_size <0\n\xa0\xa0\xa0\xa0\xa0\xa0\xa0strategy.order( "Sell2","Sell", qty=strategy.position_size * martinFactor,when=strategy.short)\nif strategy.position_size <0\n       strategy.exit("Take Profit/Stop Loss", "Sell", profit=strategy.position_avg_price  *stopLoss )\n\n\n\n'

class SMStrategybe9ecf(PinePortBase, IStrategy):
    source_id = "SM_be9ecf0184414be4"
    source_file = '魔改布林带策略止盈和马丁格尔倍投.md'
    timeframe = '1h'
    can_short = True
    source_defaults = {'source': 'close', 'length': 20, 'mult': 2.0, 'useMartin': True, 'initialQty': 0.001, 'martinFactor': 2, 'profitTarget': 1.5, 'stopLoss': 0.95}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 5
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
