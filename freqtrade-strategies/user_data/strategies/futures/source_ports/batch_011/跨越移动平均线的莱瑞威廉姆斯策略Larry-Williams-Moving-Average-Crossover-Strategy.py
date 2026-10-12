"""batch_011 port of 跨越移动平均线的莱瑞威廉姆斯策略Larry-Williams-Moving-Average-Crossover-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '// @_benac\n//@version=5\nstrategy(\'Larry\', overlay=true , initial_capital=1000 )\n\n\n////////////////////////////////////////////////////////\n//                                                    //\n//                                                    //\n//                 Codigo Operacional                 //\n//                                                    //\n//                                                    //\n////////////////////////////////////////////////////////\n\n// Usage for Stocks , or Criptos with value bigger then 1, cuz of 0.01 ´pip.\n// Daily timeframe\n//Observation Point\nstart     = timestamp(2020, 00, 00, 00, 00)         // backtest start window\nfinish    = timestamp(2022, 01, 07, 23, 59)        // backtest finish window\nwindow()  => true // create function "within window of time"  \n\nif time < start \n    strategy.close_all("Closing All")\n\n// Take infos from inputs. \ninp_mmshort = input.int(defval = 9, title = "Media Curta"  )\ninp_mminter = input.int(defval = 21, title = "Media Curta"  )\n\n// Risk Manager, here define max and min \ninp_max = input.int(defval = 15, title = "Percentual Ganho"  )\ninp_min = input.int(defval = 5, title = "Percental  Perda"  )\n\n// Converting the input to % \npmax = (inp_max / 100 )\npmin =  (inp_min / 100)\n\n// Infos From Moving Average\nmm_short = ta.sma(close , inp_mmshort)\nmm_inter = ta.ema(close , inp_mminter)\n\n\n// Trend Logic\n//Long Condition \n\n//Setup do Larry Willians Bem Simples , media virou para cima e rompeu a maxima de referencia, compra. \ntendencia_alta = mm_short[2] > mm_short[1] and mm_short > mm_short[1] and close > high[1] and close > mm_short and mm_short > mm_inter\ntendencia_baixa = mm_short[2] < mm_short[1] and mm_short < mm_short[1] and close > low[1] and close < mm_short and mm_short < mm_inter\n\n// Creating the entry\nif tendencia_alta \n    strategy.entry("Compra" , strategy.long , stop = low - 0.01  )\n    stop_inst = low - 0.01 \nif tendencia_baixa \n    strategy.entry("Venda" , strategy.short , stop= high + 0.01  )\n    stop_inst = high + 0.01\n\n\n// TrailingStop Creation\n\n// Sell Position\nif strategy.position_size < 0 \n    gain_p = strategy.opentrades.entry_price(0) - (strategy.opentrades.entry_price(0) * pmax) \n    stop_p = strategy.opentrades.entry_price(0) + (strategy.opentrades.entry_price(0) * pmin) \n    // Managing the position\n    if close < gain_p \n        strategy.close_all(comment = " 1 - Ganho : " + str.tostring( gain_p) + " Perda : " + str.tostring( stop_p)  )\n    if close > stop_p \n        strategy.close_all(comment = " 2 - Ganho : " + str.tostring( gain_p) + " Perda : " + str.tostring( stop_p)  )\n    \n    if  high > mm_short[1]\n        strategy.close_all(comment = " 3 - Ganho : " + str.tostring( gain_p) + " Perda : " + str.tostring( stop_p)  )\n      \n\n// Buy Position    \nif strategy.position_size > 0\n    gain_p = strategy.opentrades.entry_price(0) + (strategy.opentrades.entry_price(0) * pmax) \n    stop_p = strategy.opentrades.entry_price(0) - (strategy.opentrades.entry_price(0) * pmin) \n    // Managing the position\n    if close > gain_p \n        strategy.close_all(comment = " 1- Ganho : " + str.tostring( gain_p) + " Perda : " + str.tostring( stop_p)  )\n    if close < stop_p \n        strategy.close_all(comment = " 2 -Ganho : " + str.tostring( gain_p) + " Perda : " + str.tostring( stop_p)  )\n    if low < mm_short[1]\n        strategy.close_all(comment = " 3 -Ganho : " + str.tostring( gain_p) + " Perda : " + str.tostring( stop_p)  )\n        \n\n'

class SMD2F55F8C0CD47DA4(PinePortBase, IStrategy):
    source_id = "SM_d2f55f8c0cd47da4"
    source_file = '跨越移动平均线的莱瑞威廉姆斯策略Larry-Williams-Moving-Average-Crossover-Strategy.md'
    timeframe = '5m'
    can_short = True
    source_defaults = {'inp_mmshort': 9, 'inp_mminter': 21, 'inp_max': 15, 'inp_min': 5}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000
    source_reproduce_stops = False
    source_risk_flags = ['func', 'broker_state', 'entry_price_order']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
