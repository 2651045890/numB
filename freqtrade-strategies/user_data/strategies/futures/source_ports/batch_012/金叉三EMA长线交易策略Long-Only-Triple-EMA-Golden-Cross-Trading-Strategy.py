"""batch_012 port of 金叉三EMA长线交易策略Long-Only-Triple-EMA-Golden-Cross-Trading-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-09-18 00:00:00\nend: 2023-09-20 00:00:00\nperiod: 5m\nbasePeriod: 1m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=2\nstrategy("Long only EMA CROSS 8/50/200 Backtest", shorttitle="Golden Cross Tri EMA", overlay=true)\n\n// EMA 8/50/200 Cross TEST\n\n\n\n// Input\nswitch1=input(true, title="Enable Bar Color?")\nswitch2=input(true, title="Show 8 EMA")\nswitch3=input(true, title="Show 50 EMA")\nswitch4=input(true, title="Show 200 EMA")\nswitch5=input(false, title="Show profit level EMA")\nbool_Long_EMA200=input(false, title="Long only above EMA200")\nmovingaverage_8 = ema(close, input(8))\nmovingaverage_50 = ema(close, input(50))\nmovingaverage_market_signal = ema(close, input(200))\nmovingaverage_profitlvl = ema(close, input(50))\n\n\n// Calculation\nbullish_cross = if bool_Long_EMA200 == true\n    crossover(movingaverage_8, movingaverage_50) and movingaverage_8 > movingaverage_market_signal\nelse \n    bullish_cross = crossover(movingaverage_8, movingaverage_50)\nbearish_cross = crossunder(close, movingaverage_profitlvl)\n\n// Strategy\nif bullish_cross\n    strategy.entry("long", strategy.long)\n\nstrategy.close("long", when = bearish_cross )\n\n// Colors\nbartrendcolor = close > movingaverage_8 and close > movingaverage_50 and change(movingaverage_50) > 0 ? green : close < movingaverage_8 and close < movingaverage_50 and change(movingaverage_50) < 0 ? red : blue\nbarcolor(switch1?bartrendcolor:na)\n\n// Output\nplot(switch2?movingaverage_8:na,color = change(movingaverage_8) > 0 ? green : red,linewidth=2, title="EMA8")\nplot(switch3?movingaverage_50:na,color = change(movingaverage_50) > 0 ? green : red,linewidth=2,title="EMA50")\nplot(switch4?movingaverage_market_signal:na,color = change(movingaverage_market_signal) > 0 ? green : red,linewidth=3,title="EMA200")\nplot(switch5?movingaverage_profitlvl:na,color = change(movingaverage_profitlvl) > 0 ? green : red,linewidth=3, title="EMA Profit LVL")\n\n//\nalertcondition(bullish_cross, title=\'Golden Cross (bullish)\', message=\'Bullish\')\nalertcondition(bearish_cross, title=\'Death Cross (bearish)\', message=\'Bearish\')\n'

class SMEMALongOnlyTripleEMAGoldenCrossTradingStrategy3f5b91(PinePortBase, IStrategy):
    source_id = "SM_3f5b91781f61ed84"
    source_file = '金叉三EMA长线交易策略Long-Only-Triple-EMA-Golden-Cross-Trading-Strategy.md'
    timeframe = '5m'
    can_short = False
    source_defaults = {'switch1': True, 'switch2': True, 'switch3': True, 'switch4': True, 'switch5': False, '_Long_EMA200': False}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_reproduce_stops = False
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_012 md and exposed through the same PinePortBase interface used by batch_001.']

    def pine_indicators(self, dataframe, params):
        # Runtime evaluates the source against the complete OHLCV frame.
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch012Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
