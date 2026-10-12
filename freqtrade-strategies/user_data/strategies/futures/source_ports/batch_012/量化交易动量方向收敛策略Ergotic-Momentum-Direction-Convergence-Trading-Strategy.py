"""batch_012 port of 量化交易动量方向收敛策略Ergotic-Momentum-Direction-Convergence-Trading-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-01-26 00:00:00\nend: 2024-02-01 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version = 2\n////////////////////////////////////////////////////////////\n//  Copyright by HPotter v1.0 13/12/2016\n// r - Length of first EMA smoothing of 1 day momentum        4\n// s - Length of second EMA smoothing of 1 day smoothing      8    \n// u- Length of third EMA smoothing of 1 day momentum         6  \n// Length of EMA signal line                                  3\n// Source of Ergotic TSI                                      Close\n//\n// This is one of the techniques described by William Blau in his book "Momentum,\n// Direction and Divergence" (1995). If you like to learn more, we advise you to \n// read this book. His book focuses on three key aspects of trading: momentum, \n// direction and divergence. Blau, who was an electrical engineer before becoming \n// a trader, thoroughly examines the relationship between price and momentum in \n// step-by-step examples. From this grounding, he then looks at the deficiencies \n// in other oscillators and introduces some innovative techniques, including a \n// fresh twist on Stochastics. On directional issues, he analyzes the intricacies \n// of ADX and offers a unique approach to help define trending and non-trending periods. \n//\n// You can use in the xPrice any series: Open, High, Low, Close, HL2, HLC3, OHLC4 and ect...\n// You can change long to short in the Input Settings\n// Please, use it only for learning or paper trading. Do not for real trading.\n////////////////////////////////////////////////////////////\nstrategy(title="Ergotic TSI Strategy Backtest")\nr = input(4, minval=1)\ns = input(8, minval=1)\nu = input(6, minval=1)\nSmthLen = input(3, minval=1)\nreverse = input(false, title="Trade reverse")\nhline(0, color=blue, linestyle=line)\nxPrice = close\nxPrice1 = xPrice - xPrice[1]\nxPrice2 = abs(xPrice - xPrice[1])\nxSMA_R = ema(ema(ema(xPrice1,r), s),u)\nxSMA_aR = ema(ema(ema(xPrice2, r), s),u)\nVal1 = 100 * xSMA_R\nVal2 = xSMA_aR\nxTSI = iff (Val2 != 0, Val1 / Val2, 0)\nxEMA_TSI = ema(xTSI, SmthLen)\npos = iff(xTSI > xEMA_TSI, 1,\n\t   iff(xTSI < xEMA_TSI, -1, nz(pos[1], 0))) \npossig = iff(reverse and pos == 1, -1,\n          iff(reverse and pos == -1, 1, pos))\t   \nif (possig == 1) \n    strategy.entry("Long", strategy.long)\nif (possig == -1)\n    strategy.entry("Short", strategy.short)\t   \t    \nbarcolor(possig == -1 ? red: possig == 1 ? green : blue )\nplot(xTSI, color=green, title="Ergotic TSI")\nplot(xEMA_TSI, color=red, title="SigLin")\n'

class SMErgoticMomentumDirectionConvergenceTradingStrategyddc938(PinePortBase, IStrategy):
    source_id = "SM_ddc9382aa4892ac4"
    source_file = '量化交易动量方向收敛策略Ergotic-Momentum-Direction-Convergence-Trading-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'r': 4, 's': 8, 'u': 6, 'SmthLen': 3, 'reverse': False}
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
