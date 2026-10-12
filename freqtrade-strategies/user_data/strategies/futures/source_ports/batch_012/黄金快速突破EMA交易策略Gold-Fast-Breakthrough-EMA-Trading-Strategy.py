"""batch_012 port of 黄金快速突破EMA交易策略Gold-Fast-Breakthrough-EMA-Trading-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-12-18 00:00:00\nend: 2024-01-17 00:00:00\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=4\nstrategy("XAUUSD Trading Strategy", shorttitle="XAUUSD Strategy", overlay=true)\n\n// Inputs\nfastLength = input(9, title="Fast EMA Length")\nslowLength = input(21, title="Slow EMA Length")\natrLength = input(2, title="ATR Length")\natrMultiplier = input(2, title="ATR Multiplier")\nprofitTarget = input(0.7, title="Profit Target") * 100 // in percentage\ncommission = input(0.001, title="Commission") // 0.1% per trade\n\n// Calculations\nfastEMA = ema(close, fastLength)\nslowEMA = ema(close, slowLength)\natr = atr(atrLength)\n\n// Entry rules\nlongCondition = crossover(fastEMA, slowEMA) and close > slowEMA\nif (longCondition)\n    strategy.entry("Long", strategy.long)\n\nshortCondition = crossunder(fastEMA, slowEMA) and close < slowEMA\nif (shortCondition)\n    strategy.entry("Short", strategy.short)\n\n// Stop loss and take profit\nlongStop = lowest(atrLength) - atr * atrMultiplier\nlongTakeProfit = highest(atrLength) + atr * atrMultiplier\n\nshortStop = highest(atrLength) + atr * atrMultiplier\nshortTakeProfit = lowest(atrLength) - atr * atrMultiplier\n\nstrategy.exit("Exit Long", "Long", stop=longStop, limit=longTakeProfit)\nstrategy.exit("Exit Short", "Short", stop=shortStop, limit=shortTakeProfit)\n\n// Plot EMAs\nplot(fastEMA, title="Fast EMA", color=color.blue)\nplot(slowEMA, title="Slow EMA", color=color.red)\n'

class SMEMAGoldFastBreakthroughEMATradingStrategyc726a9(PinePortBase, IStrategy):
    source_id = "SM_c726a9185b6a11bf"
    source_file = '黄金快速突破EMA交易策略Gold-Fast-Breakthrough-EMA-Trading-Strategy.md'
    timeframe = '1h'
    can_short = True
    source_defaults = {'fastLength': 9, 'slowLength': 21, 'atrLength': 2, 'atrMultiplier': 2}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_reproduce_stops = True
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_012 md and exposed through the same PinePortBase interface used by batch_001.']

    def pine_indicators(self, dataframe, params):
        # Runtime evaluates the source against the complete OHLCV frame.
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch012Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
