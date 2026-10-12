"""batch_012 port of 逆转型商品通道指数交易策略Commodity-Channel-Index-Reversal-Trading-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-01-22 00:00:00\nend: 2024-01-28 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version = 2\n////////////////////////////////////////////////////////////\n//  Copyright by HPotter v1.0 30/11/2016\n// The Commodity Channel Index (CCI) is best used with markets that display cyclical or \n// seasonal characteristics, and is formulated to detect the beginning and ending of these \n// cycles by incorporating a moving average together with a divisor that reflects both possible \n// and actual trading ranges. The final index measures the deviation from normal, which indicates \n// major changes in market trend.\n// To put it simply, the Commodity Channel Index (CCI) value shows how the instrument is trading \n// relative to its mean (average) price. When the CCI value is high, it means that the prices are \n// high compared to the average price; when the CCI value is down, it means that the prices are low \n// compared to the average price. The CCI value usually does not fall outside the -300 to 300 range \n// and, in fact, is usually in the -100 to 100 range.\n// You can change long to short in the Input Settings\n// Please, use it only for learning or paper trading. Do not for real trading.\n////////////////////////////////////////////////////////////\nstrategy(title="CCI Strategy Reversed Backtest", shorttitle="CCI Strategy")\nFastMA = input(10, minval=1)\nSlowMA = input(20, minval=1)\nreverse = input(true, title="Trade reverse")\nhline(0, color=purple)\nxCCI = cci(close, 10)\nxSMA = sma(xCCI,SlowMA)\nxFMA = sma(xCCI,FastMA)\npos = iff(xSMA < xFMA , 1,\n\t   iff(xSMA > xFMA, -1, nz(pos[1], 0))) \npossig = iff(reverse and pos == 1, -1,\n         iff(reverse and pos == -1, 1, pos))\t   \nif (possig == 1) \n    strategy.entry("Long", strategy.long)\nif (possig == -1)\n    strategy.entry("Short", strategy.short)\t   \t    \nbarcolor(pos == -1 ? red: pos == 1 ? green : blue)\nplot(xSMA, color=red, title="CCI MA Slow")\nplot(xFMA, color=blue, title="CCI MA FAST")\n\n'

class SMCommodityChannelIndexReversalTradingStrategy3dd591(PinePortBase, IStrategy):
    source_id = "SM_3dd5910f8da9d0e9"
    source_file = '逆转型商品通道指数交易策略Commodity-Channel-Index-Reversal-Trading-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'FastMA': 10, 'SlowMA': 20, 'reverse': True}
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
