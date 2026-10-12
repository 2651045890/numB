"""batch_012 port of 震荡指数变换策略Oscillator-Index-Transformation-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2022-12-15 00:00:00\nend: 2023-12-21 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=2\n////////////////////////////////////////////////////////////\n//  Copyright by HPotter v1.0 27/03/2017\n// TradeStation does not allow the user to make a Multi Data Chart with \n// a Tick Bar Chart and any other type a chart. This indicator allows the \n// user to plot a daily 3-10 Oscillator on a Tick Bar Chart or any intraday interval.\n// Walter Bressert\'s 3-10 Oscillator is a detrending oscillator derived \n// from subtracting a 10 day moving average from a 3 day moving average. \n// The second plot is an 16 day simple moving average of the 3-10 Oscillator. \n// The 16 period moving average is the slow line and the 3/10 oscillator is \n// the fast line.\n// For more information on the 3-10 Oscillator see Walter Bressert\'s book \n// "The Power of Oscillator/Cycle Combinations" \n//\n// You can change long to short in the Input Settings\n// Please, use it only for learning or paper trading. Do not for real trading.\n////////////////////////////////////////////////////////////\nstrategy(title="D_Three Ten Osc", shorttitle="D_Three Ten Osc")\nLength1 = input(3, minval=1)\nLength2 = input(10, minval=1)\nLength3 = input(16, minval=1)\nreverse = input(false, title="Trade reverse")\nhline(0, color=green, linestyle=line)\nxPrice =  request.security(syminfo.tickerid,"D", hl2)\nxfastMA = ema(xPrice, Length1)\nxslowMA = ema(xPrice, Length2)\nxMACD = xfastMA - xslowMA\nxSignal = sma(xMACD, Length3)\npos = iff(xSignal > xMACD, -1,\n\t     iff(xSignal < xMACD, 1, nz(pos[1], 0))) \npossig = iff(reverse and pos == 1, -1,\n          iff(reverse and pos == -1, 1, pos))\t   \nif (possig == 1) \n    strategy.entry("Long", strategy.long)\nif (possig == -1)\n    strategy.entry("Short", strategy.short)\t   \t    \nbarcolor(possig == -1 ? red: possig == 1 ? green : blue )\nplot(request.security(syminfo.tickerid, "D", xMACD), color=blue, title="D_Three Ten Osc")\nplot(request.security(syminfo.tickerid, "D", xSignal), color=red, title="D_Three Ave")\n'

class SMOscillatorIndexTransformationStrategy270a3e(PinePortBase, IStrategy):
    source_id = "SM_270a3e352c9f8254"
    source_file = '震荡指数变换策略Oscillator-Index-Transformation-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'Length1': 3, 'Length2': 10, 'Length3': 16, 'reverse': False}
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
