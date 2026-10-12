"""batch_012 port of 逆向工程RSI策略Reverse-Engineering-RSI-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2022-11-21 00:00:00\nend: 2023-11-27 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=2\n////////////////////////////////////////////////////////////\n//  Copyright by HPotter v1.0 25/10/2017\n// The related article is copyrighted material from\n// Stocks & Commodities.\n//\n// You can change long to short in the Input Settings\n// WARNING:\n// - For purpose educate only\n// - This script to change bars colors.\n////////////////////////////////////////////////////////////\nstrategy(title="Reverse Engineering RSI, by Giorgos Siligardos", overlay = true)\nValue = input(50, minval=1)\nWildPer = input(14,minval=1)\nreverse = input(false, title="Trade reverse")\nExpPer = 2 * WildPer - 1\nK = 2 / (ExpPer + 1)\nAUC = iff(close > close[1], K * (close - close[1]) + (1 - K) * nz(AUC[1], 1), (1-K) * nz(AUC[1], 1))\nADC = iff(close > close[1], (1-K) * nz(ADC[1], 1), K * (close[1] - close) + (1 - K) * nz(ADC[1], 1))\nnVal = (WildPer - 1) * (ADC * Value / (100 - Value) - AUC)\nnRes = iff(nVal >= 0, close + nVal, close + nVal * (100 - Value) / Value)\npos = iff(nRes > close, -1,\n\t   iff(nRes < close, 1, nz(pos[1], 0))) \npossig = iff(reverse and pos == 1, -1,\n          iff(reverse and pos == -1, 1, pos))\t   \nif (possig == 1) \n    strategy.entry("Long", strategy.long)\nif (possig == -1)\n    strategy.entry("Short", strategy.short)\t   \t    \nbarcolor(possig == -1 ? red: possig == 1 ? green : blue ) \nplot(nRes, color=blue, title="Reverse Engineering RSI")\n'

class SMRSIReverseEngineeringRSIStrategy03110f(PinePortBase, IStrategy):
    source_id = "SM_03110fe380ebf6da"
    source_file = '逆向工程RSI策略Reverse-Engineering-RSI-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'Value': 50, 'WildPer': 14, 'reverse': False}
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
