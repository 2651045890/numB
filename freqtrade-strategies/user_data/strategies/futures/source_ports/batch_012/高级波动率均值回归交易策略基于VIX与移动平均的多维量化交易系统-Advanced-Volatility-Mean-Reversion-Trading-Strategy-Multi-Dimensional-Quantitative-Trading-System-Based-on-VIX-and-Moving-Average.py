"""batch_012 port of 高级波动率均值回归交易策略基于VIX与移动平均的多维量化交易系统-Advanced-Volatility-Mean-Reversion-Trading-Strategy-Multi-Dimensional-Quantitative-Trading-System-Based-on-VIX-and-Moving-Average.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2019-12-23 08:00:00\nend: 2024-12-09 08:00:00\nperiod: 1d\nbasePeriod: 1d\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This Pine Script™ code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © EdgeTools\n\n//@version=5\nstrategy("Connors VIX Reversal III invented by Dave Landry", overlay=true)\n\n// Inputs\nvixSymbol = input("swap", "VIX Symbol")\nlengthMA = input(10, title="Length of Moving Average")\npercentThreshold = input(10, title="Percentage Threshold")\nbuyColor = input(color.rgb(0, 255, 0,90), title="Buy Signal Color")\nsellColor = input(color.rgb(255, 0, 0,90), title="Sell Signal Color")\nexitColor = input(color.rgb(0, 0, 255,90), title="Exit Signal Color")\n\n// Fetch VIX data\nvixClose = request.security(vixSymbol, "D", close)\nvixHigh = request.security(vixSymbol, "D", high)\nvixLow = request.security(vixSymbol, "D", low)\n\n// Calculate 10-day Moving Average of VIX\nvixMA = ta.sma(vixClose, lengthMA)\n\n// Calculate yesterday\'s 10-day Moving Average\nvixMA_yesterday = ta.sma(vixClose[1], lengthMA)\n\n// Buy Rules\nbuyCondition1 = vixLow > vixMA\nbuyCondition2 = vixClose > vixMA * (1 + percentThreshold / 100)\nbuySignal = buyCondition1 and buyCondition2\n\n// Sell Rules\nsellCondition1 = vixHigh < vixMA\nsellCondition2 = vixClose < vixMA * (1 - percentThreshold / 100)\nsellSignal = sellCondition1 and sellCondition2\n\n// Exit Rules\nbuyExit = vixLow < vixMA_yesterday\nsellExit = vixHigh > vixMA_yesterday\n\n// Plot Buy/Sell Signals\nbgcolor(buySignal ? buyColor : na)\nbgcolor(sellSignal ? sellColor : na)\n\n// Exit Signals\nbgcolor(buyExit ? exitColor : na)\nbgcolor(sellExit ? exitColor : na)\n\n// Strategy\nif (buySignal)\n    strategy.entry("Buy", strategy.long)\nif (sellSignal)\n    strategy.entry("Sell", strategy.short)\n\nif (buyExit)\n    strategy.close("Buy")\nif (sellExit)\n    strategy.close("Sell")\n\n'

class SMVIXAdvancedVolatilityMeanReversionTradingStrategyMultiDd8278b(PinePortBase, IStrategy):
    source_id = "SM_d8278bb2dbd07310"
    source_file = '高级波动率均值回归交易策略基于VIX与移动平均的多维量化交易系统-Advanced-Volatility-Mean-Reversion-Trading-Strategy-Multi-Dimensional-Quantitative-Trading-System-Based-on-VIX-and-Moving-Average.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'vixSymbol': 'swap', 'lengthMA': 10, 'percentThreshold': 10, 'buyColor': 'color.rgb(0, 255, 0,90)', 'sellColor': 'color.rgb(255, 0, 0,90)', 'exitColor': 'color.rgb(0, 0, 255,90)'}
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
