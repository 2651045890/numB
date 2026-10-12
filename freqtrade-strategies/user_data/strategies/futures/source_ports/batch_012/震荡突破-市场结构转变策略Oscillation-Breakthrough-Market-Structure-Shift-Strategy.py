"""batch_012 port of 震荡突破-市场结构转变策略Oscillation-Breakthrough-Market-Structure-Shift-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2022-11-28 00:00:00\nend: 2023-12-04 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This source code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © jl01794\n\n//@version=5\nstrategy(title="ICT_MSS[PROTOTYPE]", overlay=true, initial_capital=10000, currency="USD", margin_long=15, margin_short=15, max_lines_count=500)\n\n\n// INPUTS\nTime_Frame  = input.timeframe("60", title="Focused Time Frame")\nFTF_LTF = input.timeframe("15", title="Focused Time Frame(LTF)")\n//\n\n// SECURITY DATA [FOR ONE TIMEFRAME REFERENCE]\n\nFTF_Close = request.security(syminfo.tickerid, Time_Frame, close)\nFTF_Open = request.security(syminfo.tickerid, Time_Frame, open)\nFTFLTF_High = request.security(syminfo.tickerid, FTF_LTF, ta.highest(2)) \nFTFLTF_Low = request.security(syminfo.tickerid, FTF_LTF, ta.lowest(2)) \nFTFLTF_Close = request.security(syminfo.tickerid, FTF_LTF, close)\nFTFLTF_Open = request.security(syminfo.tickerid, FTF_LTF, open)\n\n// TIME BASED CLOSE AND OPEN\n_close = FTF_Close\n_open = FTF_Open\n_LTFclose = FTFLTF_Close\n_LTFopen = FTFLTF_Open\n\n// CANDLE STATE\ngreenCandle = close > open\nredCandle = close < open\nLTFgreenCandle = FTFLTF_Close > FTFLTF_Open\nLTFredCandle = FTFLTF_Close < FTFLTF_Open\n\n// ENGULFING TIMEFRAME REFERENCE\nFTF_greenCandle = request.security(syminfo.tickerid, Time_Frame, greenCandle)\nFTF_redCandle = request.security(syminfo.tickerid, Time_Frame, redCandle)\nFTFLTF_greenCandle = request.security(syminfo.tickerid, FTF_LTF, LTFgreenCandle)\nFTFLTF_redCandle = request.security(syminfo.tickerid, FTF_LTF, LTFredCandle)\n\n//--------------------------------------------------------------------------------------------------------------\n\n//ENGULFING_FTF_LTF\nB_EnP_mss = FTFLTF_redCandle[1] and        // 1E PIVOT BUY\n     FTFLTF_greenCandle\n//\n\n\nB_EnPs_mss = FTFLTF_greenCandle[1] and        // 1E PIVOT SELL\n     FTFLTF_redCandle\n//  \n\n//--------------------------------------------------------------------------------------------------------------\n\ndisplay_LTF = timeframe.isintraday and timeframe.multiplier <= 15\n\n//--------------------------------------------------------------------------------------------------------------\n\n// STORED DATAS\nvar float EH_MSS1 = na\nvar float EL_MSS1 = na\nvar bool can_draw = false\nvar line l1_mss = na\nvar line l1s_mss = na\n\n//--------------------------------------------------------------------------------------------------------------\n\n// MSS BUY\nif (B_EnPs_mss) and (display_LTF)                                                 \n    EH_MSS1 := FTFLTF_High \n    can_draw := true                                                            \n    l1_mss := line.new(bar_index, EH_MSS1, bar_index -3, EH_MSS1, color=color.purple)     \nelse\n    if (can_draw)\n        if (FTFLTF_High > EH_MSS1)                                                    \n            can_draw := false                                                  \n        else\n            line.set_x2(l1_mss, bar_index) \n//\n\n// MSS SELL\nif (B_EnP_mss) and (display_LTF)                                                 \n    EL_MSS1 := FTFLTF_Low \n    can_draw := true                                                            \n    l1s_mss := line.new(bar_index, EL_MSS1, bar_index -3, EL_MSS1, color=color.purple)     \nelse\n    if (can_draw)\n        if (FTFLTF_Low < EL_MSS1)                                                    \n            can_draw := false                                                  \n        else\n            line.set_x2(l1s_mss, bar_index) \n          \n\n//--------------------------------------------------------------------------------------------------------------\n\n// ORDER\n\n// BUY\nlongCondition_mssB = B_EnPs_mss and FTFLTF_High and close and high[1]\nopenOr = FTFLTF_High \n\n//SELL\nshortCondition_mssS = B_EnP_mss and FTFLTF_Low and close and low[1]\nopenOrs = FTFLTF_Low \n\n\nif (longCondition_mssB) \n    strategy.entry("Buy", strategy.long, 1, stop = openOr, when = longCondition_mssB)\n//\n\nif (shortCondition_mssS) \n    strategy.entry("Sell", strategy.short, 1, stop = openOrs, when = shortCondition_mssS)\n//\n\n// EXIT \nlong_tp = open < FTFLTF_Close[1]\nshort_tp = open > FTFLTF_Close[1]\n\n//if (long_tp)\n    //strategy.close("Buy", qty_percent = 100, when = long_tp)\n//\n\n//if (short_tp)\n    //strategy.close("Sell", qty_percent = 100, when = short_tp)\n//\n'

class SMOscillationBreakthroughMarketStructureShiftStrategy6cb09c(PinePortBase, IStrategy):
    source_id = "SM_6cb09cfda2666498"
    source_file = '震荡突破-市场结构转变策略Oscillation-Breakthrough-Market-Structure-Shift-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'Time_Frame': '60', 'FTF_LTF': '15'}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 10000
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
