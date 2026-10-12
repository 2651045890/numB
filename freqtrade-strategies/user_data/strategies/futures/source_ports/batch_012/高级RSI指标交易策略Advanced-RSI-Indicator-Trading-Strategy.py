"""batch_012 port of 高级RSI指标交易策略Advanced-RSI-Indicator-Trading-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2024-01-06 00:00:00\nend: 2024-02-05 00:00:00\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\n// Lets connect on LinkedIn (https://www.linkedin.com/in/lets-grow-with-quality/)\n// Optimized for S&P500 Daily. Use it as a buy confirmation on certain levels (Springs, Pullbacks, ...) or let it run \n// without "Weekly RSI Filter" and pyramiding for 4 x more trades.\n// This strategy is optimized for minimum drawdowns and has several filters on board for use on different securities\n\nstrategy("S&P500 RSI2 Studio", overlay=true)\n\nbaseLength = input(2, title="Base RSI Length")\noverSold = input(10, title="Overbought Level")\noverBought = input(90, title="Oversold Level")\noverBoughtExit = input(70, title="Overbought Level Exit")\nenableWeeklyRsiFilter = input(true, title="Enable Weekly RSI Filter")\nweeklyOverSold = input(30, title="Weekly Oversold Level")\nweeklyOverBought = input(70, title="Weekly OverOverbought Level")\nweeklyRsiLength = input(2, title="weeklyRsiLength")\n\nenableWmaFilter = input(false, title="Enable MA Filter")\nwmaLength = input(100, title="WMA Length")\n\nexitRsiLength = input(4, title="Exit RSI Length")\ndailyRsiLength = input(4, title="Daily RSI Length")\n\nenable2ndRSIFilter = input(false, title="Enable 2nd RSI Filter")\nSecRSIFilterLengh = input(14, title="2nd RSI Filter Length")\nSecRSIFilterOverSold = input(20, title="2nd RSI Filter Oversold Level")\n\nenableAtrFilter = input(true, title="Enable ATR Filter")\nnumAtrDays = input(14, title="Number of Days ATR Average")\natrFilterFactor = input(2, title="ATR Filter Factor")\n\nweeklyRsi = request.security(syminfo.tickerid, "W", ta.wma(ta.rsi(close, weeklyRsiLength), 1))\nexitRsi = request.security(syminfo.tickerid, "D", ta.wma(ta.rsi(close, exitRsiLength), 2))\ndailyRsi = request.security(syminfo.tickerid, "D", ta.wma(ta.rsi(close, dailyRsiLength), 2))\nprice = close\n\npriceDropCondition = ta.atr(1) >= ta.atr(numAtrDays) * atrFilterFactor\npreventEarlyEntry = not priceDropCondition\n\nvrsi = ta.wma(ta.rsi(price, baseLength), 2)\nwma = ta.wma(price, wmaLength)\n\n\nbuyCond1 = ta.crossunder(vrsi, overSold)\nbuyCond2 = enableWeeklyRsiFilter ? weeklyRsi < weeklyOverSold : true\nbuyCond3 = enable2ndRSIFilter ? ta.wma(ta.rsi(close, SecRSIFilterLengh),2) < SecRSIFilterOverSold : true\nbuyCond4 = enableWmaFilter ? price > ta.wma(close, wmaLength) : true\nbuyCond5 = enableAtrFilter ? preventEarlyEntry : true\n \nbuy = buyCond1 and buyCond2 and buyCond3 and buyCond4 and buyCond5\n\nif (not na(vrsi))\n    if buy \n        strategy.entry("RSI2 Studio", strategy.long, comment="Long")\n\nif (exitRsi > overBoughtExit)\n    strategy.close("RSI2 Studio", comment="Close Long")\n'

class SMRSIAdvancedRSIIndicatorTradingStrategya252c2(PinePortBase, IStrategy):
    source_id = "SM_a252c2f1c8d0df5f"
    source_file = '高级RSI指标交易策略Advanced-RSI-Indicator-Trading-Strategy.md'
    timeframe = '1h'
    can_short = False
    source_defaults = {'baseLength': 2, 'overSold': 10, 'overBought': 90, 'overBoughtExit': 70, 'enableWeeklyRsiFilter': True, 'weeklyOverSold': 30, 'weeklyOverBought': 70, 'weeklyRsiLength': 2, 'enableWmaFilter': False, 'wmaLength': 100, 'exitRsiLength': 4, 'dailyRsiLength': 4, 'enable2ndRSIFilter': False, 'SecRSIFilterLengh': 14, 'SecRSIFilterOverSold': 20, 'enableAtrFilter': True, 'numAtrDays': 14, 'atrFilterFactor': 2}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_reproduce_stops = False
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_012 md and exposed through the same PinePortBase interface used by batch_001.', 'request.security/security is present: generic adapter keeps the expression but same-frame evaluation is only an approximation; manual multi-timeframe parity verification is required.']

    def pine_indicators(self, dataframe, params):
        # Runtime evaluates the source against the complete OHLCV frame.
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch012Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
