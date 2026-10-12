"""batch_012 port of 黄金交叉均线交易策略Golden-Cross-Moving-Average-Trading-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2022-11-28 00:00:00\nend: 2023-12-04 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=2\nstrategy("Golden Cross, SMA 200 Long Only, Moving Average Strategy (by ChartArt)", shorttitle="CA_-_Golden_Cross_Strat", overlay=true)\n\n// ChartArt\'s Golden Cross Strategy\n//\n// Version 1.0\n// Idea by ChartArt on June 19, 2016.\n//\n// This moving average strategy is very easy to follow:\n//\n// The strategy goes long when the faster SMA 50 (the\n// simple moving average of the last 50 bars) crosses\n// above the SMA 200. Orders are closed when the SMA 50\n// crosses below SMA 200. The strategy does not short.\n//\n// This simple strategy does not have any other\n// stop loss or take profit money management logic.\n//\n// List of my work: \n// https://www.tradingview.com/u/ChartArt/\n// \n//  __             __  ___       __  ___ \n// /  ` |__|  /\\  |__)  |   /\\  |__)  |  \n// \\__, |  | /~~\\ |  \\  |  /~~\\ |  \\  |  \n// \n// \n\n\n// Input\nswitch1=input(true, title="Enable Bar Color?")\nswitch2=input(false, title="Show Fast Moving Average")\nswitch3=input(true, title="Show Slow Moving Average")\nmovingaverage_fast = sma(close, input(50))\nmovingaverage_slow = sma(close, input(200))\n\n// Calculation\nbullish_cross = crossover(movingaverage_fast, movingaverage_slow)\nbearish_cross = crossunder(movingaverage_fast, movingaverage_slow)\n\n// Strategy\nif bullish_cross\n    strategy.entry("long", strategy.long)\n\nstrategy.close("long", when = bearish_cross )\n\n// Colors\nbartrendcolor = close > movingaverage_fast and close > movingaverage_slow and change(movingaverage_slow) > 0 ? green : close < movingaverage_fast and close < movingaverage_slow and change(movingaverage_slow) < 0 ? red : blue\nbarcolor(switch1?bartrendcolor:na)\n\n// Output\nplot(switch2?movingaverage_fast:na,color = change(movingaverage_fast) > 0 ? green : red,linewidth=3)\nplot(switch3?movingaverage_slow:na,color = change(movingaverage_slow) > 0 ? green : red,linewidth=3)\n\n//\nalertcondition(bullish_cross, title=\'Golden Cross (bullish)\', message=\'Bullish\')\nalertcondition(bearish_cross, title=\'Death Cross (bearish)\', message=\'Bearish\')\n'

class SMGoldenCrossMovingAverageTradingStrategy4c4e69(PinePortBase, IStrategy):
    source_id = "SM_4c4e696ba7a39e9c"
    source_file = '黄金交叉均线交易策略Golden-Cross-Moving-Average-Trading-Strategy.md'
    timeframe = '1d'
    can_short = False
    source_defaults = {'switch1': True, 'switch2': False, 'switch3': True}
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
