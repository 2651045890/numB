"""batch_011 port of 超越指标动量系统交易策略SMI-Ergodic-Oscillator-Momentum-Trading-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-10-01 00:00:00\nend: 2023-10-31 00:00:00\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=2\n////////////////////////////////////////////////////////////\n//  Copyright by HPotter v1.0 03/11/2017\n// The SMI Ergodic Indicator is the same as the True Strength Index (TSI) developed by \n// William Blau, except the SMI includes a signal line. The SMI uses double moving averages \n// of price minus previous price over 2 time frames. The signal line, which is an EMA of the \n// SMI, is plotted to help trigger trading signals. Adjustable guides are also given to fine \n// tune these signals. The user may change the input (close), method (EMA), period lengths \n// and guide values.\n// You can use in the xPrice any series: Open, High, Low, Close, HL2, HLC3, OHLC4 and ect...\n//\n// You can change long to short in the Input Settings\n// WARNING:\n// - For purpose educate only\n// - This script to change bars colors.\n////////////////////////////////////////////////////////////\nstrategy(title="SMI Ergodic Oscillator")\nfastPeriod = input(4, minval=1)\nslowPeriod = input(8, minval=1)\nSmthLen = input(3, minval=1)\nTopBand = input(0.5, step=0.1)\nLowBand = input(-0.5, step=0.1)\nreverse = input(false, title="Trade reverse")\n// hline(0, color=gray, linestyle=dashed)\n// hline(TopBand, color=red, linestyle=line)\n// hline(LowBand, color=green, linestyle=line)\nxPrice = close\nxPrice1 = xPrice - xPrice[1]\nxPrice2 = abs(xPrice - xPrice[1])\nxSMA_R = ema(ema(xPrice1,fastPeriod),slowPeriod)\nxSMA_aR = ema(ema(xPrice2, fastPeriod),slowPeriod)\nxSMI = xSMA_R / xSMA_aR\nxEMA_SMI = ema(xSMI, SmthLen)\npos = iff(xEMA_SMI < LowBand, -1,\n\t   iff(xEMA_SMI > TopBand, 1, nz(pos[1], 0))) \npossig = iff(reverse and pos == 1, -1,\n          iff(reverse and pos == -1, 1, pos))\t   \nif (possig == 1) \n    strategy.entry("Long", strategy.long)\nif (possig == -1)\n    strategy.entry("Short", strategy.short)\t   \t    \nbarcolor(possig == -1 ? red: possig == 1 ? green : blue )  \nplot(xSMI, color=green, title="Ergotic SMI")\nplot(xEMA_SMI, color=red, title="SigLin")'

class SMC3D984202F7BD6A7(PinePortBase, IStrategy):
    source_id = "SM_c3d984202f7bd6a7"
    source_file = '超越指标动量系统交易策略SMI-Ergodic-Oscillator-Momentum-Trading-Strategy.md'
    timeframe = '1h'
    can_short = True
    source_defaults = {'fastPeriod': 4, 'slowPeriod': 8, 'SmthLen': 3, 'TopBand': 0.5, 'LowBand': -0.5, 'reverse': False}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = False
    source_risk_flags = ['alert_or_drawing']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
