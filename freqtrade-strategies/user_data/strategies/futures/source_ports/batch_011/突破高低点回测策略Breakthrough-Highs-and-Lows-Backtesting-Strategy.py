"""batch_011 port of 突破高低点回测策略Breakthrough-Highs-and-Lows-Backtesting-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-01-01 00:00:00\nend: 2024-01-07 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=2\n////////////////////////////////////////////////////////////\n//  Copyright by HPotter v1.0 03/07/2018\n// This script shows a high and low period value.\n//    Width - width of lines\n//    SelectPeriod - Day or Week or Month and etc.\n//    LookBack - Shift levels 0 - current period, 1 - previous and etc.\n//\n// You can change long to short in the Input Settings\n// WARNING:\n// - For purpose educate only\n// - This script to change bars colors.\n////////////////////////////////////////////////////////////\nstrategy(title="High and Low Levels Backtest", shorttitle="HL Levels", overlay = true)\nSelectPeriod = input("D", defval="D")\nLookBack = input(1,  minval=0)\nreverse = input(false, title="Trade reverse")\nxHigh  = request.security(syminfo.tickerid, SelectPeriod, high[LookBack])\nxLow   = request.security(syminfo.tickerid, SelectPeriod, low[LookBack])\nvS1 = xHigh\nvR1 = xLow\npos = iff(close > vR1, 1,\n       iff(close < vS1, -1, nz(pos[1], 0))) \npossig = iff(reverse and pos == 1, -1,\n          iff(reverse and pos == -1, 1, pos))\t   \nif (possig == 1) \n    strategy.entry("Long", strategy.long)\nif (possig == -1)\n    strategy.entry("Short", strategy.short)\t   \t    \nbarcolor(possig == -1 ? red: possig == 1 ? green : blue ) '

class SM9778AEC3B71ACF52(PinePortBase, IStrategy):
    source_id = "SM_9778aec3b71acf52"
    source_file = '突破高低点回测策略Breakthrough-Highs-and-Lows-Backtesting-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'SelectPeriod': 'D', 'LookBack': 1, 'reverse': False}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = False
    source_risk_flags = ['mtf']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
