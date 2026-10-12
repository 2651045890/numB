"""batch_012 port of 重心回测交易策略Center-of-Gravity-Backtesting-Trading-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-11-11 00:00:00\nend: 2023-12-11 00:00:00\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=2\n////////////////////////////////////////////////////////////\n//  Copyright by HPotter v1.0 15/03/2018\n// The indicator is based on moving averages. On the basis of these, the \n// "center" of the price is calculated, and price channels are also constructed, \n// which act as corridors for the asset quotations.\n//\n// You can change long to short in the Input Settings\n// WARNING:\n//  - For purpose educate only\n//  - This script to change bars colors.\n////////////////////////////////////////////////////////////\nstrategy(title="Center Of Gravity Backtest", shorttitle="CFO", overlay = true)\nLength = input(20, minval=1)\nm = input(5, minval=0)\nPercent = input(1, minval=0)\nSignalLine = input(1, minval=1, maxval = 2, title = "Trade from line (1 or 2)")\nreverse = input(false, title="Trade reverse")\nxLG = linreg(close, Length, m)\nxLG1r = xLG + ((close * Percent) / 100)\nxLG1s = xLG - ((close * Percent) / 100)\nxLG2r = xLG + ((close * Percent) / 100) * 2\nxLG2s = xLG - ((close * Percent) / 100) * 2\nxSignalR = iff(SignalLine == 1, xLG1r, xLG2r)\nxSignalS = iff(SignalLine == 1, xLG1s, xLG2s)\npos = iff(close > xSignalR, 1,\n       iff(close < xSignalS, -1, nz(pos[1], 0))) \npossig = iff(reverse and pos == 1, -1,\n          iff(reverse and pos == -1, 1, pos))\t   \nif (possig == 1) \n    strategy.entry("Long", strategy.long)\nif (possig == -1)\n    strategy.entry("Short", strategy.short)\t   \t    \nbarcolor(possig == -1 ? red: possig == 1 ? green : blue ) \nplot(xLG, color=blue, title="CFO")\nplot(xLG1r, color=green, title="LG1r")\nplot(xLG2r, color=green, title="LG2r")\nplot(xLG1s, color=red, title="LG1s")\nplot(xLG2s, color=red, title="LG2s")\n'

class SMCenterofGravityBacktestingTradingStrategyb15cf2(PinePortBase, IStrategy):
    source_id = "SM_b15cf2e3aaa9c332"
    source_file = '重心回测交易策略Center-of-Gravity-Backtesting-Trading-Strategy.md'
    timeframe = '1h'
    can_short = True
    source_defaults = {'Length': 20, 'm': 5, 'Percent': 1, 'SignalLine': 1, 'reverse': False}
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
