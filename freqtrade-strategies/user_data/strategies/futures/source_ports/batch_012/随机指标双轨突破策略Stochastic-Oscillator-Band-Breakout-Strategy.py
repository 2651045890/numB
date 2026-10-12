"""batch_012 port of 随机指标双轨突破策略Stochastic-Oscillator-Band-Breakout-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-09-06 00:00:00\nend: 2023-09-13 00:00:00\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=2\n////////////////////////////////////////////////////////////\n//  Copyright by HPotter v1.0 05/10/2017\n// This back testing strategy generates a long trade at the Open of the following \n// bar when the %K line crosses up UpBand line.\n// It generates a short trade at the Open of the following bar when the %K line \n// crosses down DownBand line.\n//\n// You can change long to short in the Input Settings\n// WARNING:\n// - For purpose educate only\n// - This script to change bars colors.\n////////////////////////////////////////////////////////////\nstrategy(title="Strategy Stochastic", shorttitle="Strategy Stochastic")\nLength = input(7, minval=1)\nDLength = input(3, minval=1)\nUpBand = input(20, minval=1)\nDownBand = input(80, minval=1)\nreverse = input(false, title="Trade reverse")\nhline(50, color=black, linestyle=hline.style_dashed)\nhline(UpBand, color=red, linestyle=hline.style_solid)\nhline(DownBand, color=green, linestyle=hline.style_solid)\nvFast = stoch(close, high, low, Length)\nvSlow = sma(vFast, DLength)\npos = iff(vFast > UpBand, 1,\n\t   iff(vFast < DownBand, -1, nz(pos[1], 0))) \npossig = iff(reverse and pos == 1, -1,\n          iff(reverse and pos == -1, 1, pos))\t   \nif (possig == 1) \n    strategy.entry("Long", strategy.long)\nif (possig == -1)\n    strategy.entry("Short", strategy.short)\t   \t    \nbarcolor(possig == -1 ? red: possig == 1 ? green : blue )  \nplot(vSlow, color=blue, title="D")\nplot(vFast, color=red, title="K")\n'

class SMStochasticOscillatorBandBreakoutStrategydc1b81(PinePortBase, IStrategy):
    source_id = "SM_dc1b819a73d33172"
    source_file = '随机指标双轨突破策略Stochastic-Oscillator-Band-Breakout-Strategy.md'
    timeframe = '1h'
    can_short = True
    source_defaults = {'Length': 7, 'DLength': 3, 'UpBand': 20, 'DownBand': 80, 'reverse': False}
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
