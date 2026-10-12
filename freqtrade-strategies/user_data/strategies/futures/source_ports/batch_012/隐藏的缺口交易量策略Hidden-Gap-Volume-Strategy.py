"""batch_012 port of 隐藏的缺口交易量策略Hidden-Gap-Volume-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-09-10 00:00:00\nend: 2023-10-10 00:00:00\nperiod: 3h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=2\n////////////////////////////////////////////////////////////\n//  Copyright by HPotter v1.0 20/06/2017\n// If Volume is less then the previous 20 intervals, Volume is gray.\n// If Volume is greater then the previous 40 intervals, Volume is black.\n// If Volume is less then the previous 2 intervals, Volume is purple.\n// If Volume is less then the previous, Volume is red.\n// If Volume is greater then the previous, Volume is blue.\n// Other - white.\n// You can add on the indicator a 2.5 Standart Deviation of a 20 period \n// Bollinger Band Shifted 3 periods forward.\n//\n// You can change long to short in the Input Settings\n// Please, use it only for learning or paper trading. Do not for real trading.\n////////////////////////////////////////////////////////////\nstrategy(title="Hidden Gap`s VSA Volume")\nLength_HH = input(40, minval=1)\nLength_LLSmall = input(2, minval=2)\nLength_LLBig = input(20, minval=2)\nLengthMA    = input(20, minval=1)\nreverse = input(false, title="Trade reverse")\nhline(0, color=gray, linestyle=hline.style_dashed)\nxSMA_vol = sma(volume, LengthMA)\nxHH_vol = highest(volume, Length_HH)\nxLL_volSmall = lowest(volume, Length_LLSmall)\nxLL_volBig = lowest(volume, Length_LLBig)\nBarColor = iff(volume > xHH_vol[1], black,\n             iff(volume < xLL_volBig[1], gray,\n              iff(volume < xLL_volSmall[1], purple,\n               iff(volume > volume[1], blue, \n                 iff(volume < volume[1], red, white)))))\npos = iff(volume > xSMA_vol, -1,\n\t     iff(volume < xSMA_vol, 1, nz(pos[1], 0))) \npossig = iff(reverse and pos == 1, -1,\n          iff(reverse and pos == -1, 1, pos))\t   \nif (possig == 1) \n    strategy.entry("Long", strategy.long)\nif (possig == -1)\n    strategy.entry("Short", strategy.short)\t   \t    \nbarcolor(possig == -1 ? red: possig == 1 ? green : blue )                 \nplot(volume, color=BarColor, title="Vol", style=histogram, linewidth=2)\nplot(xSMA_vol, color=black, title="SMA")\n'

class SMHiddenGapVolumeStrategyf21f3d(PinePortBase, IStrategy):
    source_id = "SM_f21f3d1d1c83adbc"
    source_file = '隐藏的缺口交易量策略Hidden-Gap-Volume-Strategy.md'
    timeframe = '3h'
    can_short = True
    source_defaults = {'Length_HH': 40, 'Length_LLSmall': 2, 'Length_LLBig': 20, 'LengthMA': 20, 'reverse': False}
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
