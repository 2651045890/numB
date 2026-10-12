"""batch_011 port of 自适应价格区域反转交易策略Adaptive-Price-Zone-Reversal-Trading-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-12-05 00:00:00\nend: 2023-12-11 08:00:00\nperiod: 1m\nbasePeriod: 1m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=4\n////////////////////////////////////////////////////////////\n//  Copyright by HPotter v1.0 15/01/2020\n//\n// The adaptive price zone (APZ) is a volatility-based technical indicator that helps investors \n// identify possible market turning points, which can be especially useful in a sideways-moving \n// market. It was created by technical analyst Lee Leibfarth in the article “Identify the \n// Turning Point: Trading With An Adaptive Price Zone,” which appeared in the September 2006 issue \n// of the journal Technical Analysis of Stocks and Commodities.\n// This indicator attempts to signal significant price movements by using a set of bands based on \n// short-term, double-smoothed exponential moving averages that lag only slightly behind price changes. \n// It can help short-term investors and day traders profit in volatile markets by signaling price \n// reversal points, which can indicate potentially lucrative times to buy or sell. The APZ can be \n// implemented as part of an automated trading system and can be applied to the charts of all tradeable assets.\n//\n// WARNING:\n// - For purpose educate only\n// - This script to change bars colors.\n////////////////////////////////////////////////////////////\n\nstrategy(title="Adaptive Price Zone Backtest", shorttitle="APZ", overlay = true)\nnPeriods = input(20, minval=1)\nnBandPct = input(2, minval=0)\nreverse = input(false, title="Trade reverse")\nxHL = high - low\nnP = ceil(sqrt(nPeriods))\nxVal1 = ema(ema(close,nP), nP)\nxVal2 = ema(ema(xHL,nP), nP)\nUpBand = nBandPct * xVal2 + xVal1\nDnBand = xVal1 - nBandPct * xVal2\npos = 0\npos := iff(low < DnBand , 1,\n\t   iff(high > UpBand, -1, pos[1])) \npossig = iff(reverse and pos == 1, -1,\n          iff(reverse and pos == -1 , 1, pos))\t   \nif (possig == 1) \n    strategy.entry("Long", strategy.long)\nif (possig == -1)\n    strategy.entry("Short", strategy.short)\t \nif (possig == 0) \n    strategy.close_all()\nbarcolor(possig == -1 ? #b50404: possig == 1 ? #079605 : #0536b3 )'

class SM1D614BCDB423A102(PinePortBase, IStrategy):
    source_id = "SM_1d614bcdb423a102"
    source_file = '自适应价格区域反转交易策略Adaptive-Price-Zone-Reversal-Trading-Strategy.md'
    timeframe = '1m'
    can_short = True
    source_defaults = {'nPeriods': 20, 'nBandPct': 2, 'reverse': False}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = False
    source_risk_flags = ['var_state']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
