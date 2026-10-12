"""batch_011 port of 简易跟踪趋势策略Simple-Trend-Following-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-08-14 00:00:00\nend: 2023-09-13 00:00:00\nperiod: 4h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// © Milleman\n//@version=4\nstrategy("Millebot", overlay=true, default_qty_type = strategy.percent_of_equity, default_qty_value = 100, initial_capital=100000, commission_type=strategy.commission.percent, commission_value=0.04)\n\n// Risk management settings\nSpacer2 = input(false, title="=== Risk management settings ===")\nRisk = input(1.0, title="% Risk")/100\nRRR = input(2,title="Risk Reward Ratio",step=0.1,minval=0,maxval=20)\nSL = input(5,title="StopLoss %",step=0.25)/100\n\n// Baseline : McGinley Dynamic\nSpacer3 = input(false, title="=== Baseline - Switch L/S ===")\nMcG_Source = input(close, title="McGinley source")\nMcG_length = input(50, title=" McG length", minval=1)\nMcG_LS_Switch = 0.0\nMcG_LS_Switch := na(McG_LS_Switch[1]) ? ema(McG_Source, McG_length) : McG_LS_Switch[1] + (McG_Source - McG_LS_Switch[1]) / (McG_length * pow(McG_Source/McG_LS_Switch[1], 4))\n\n// Confirmation indicator\nSpacer4 = input(false, title="=== Confirmation indicator ===")\nC1_Act = input(false, title=" Confirmation indicator Activation")\nC1_src = input(ohlc4, title="Source")\nC1_len = input(5,title="Length")\nC1 = sma(C1_src,C1_len)\n\n// Entry indicator : Hull Moving Average\nSpacer5 = input(false, title="=== Entry indicator configuration ===")\nsrc = input(ohlc4, title="Source")\nlength = input(50,title="Length HMA")\nHMA = ema(wma(2*wma(src, length/2)-wma(src, length), round(sqrt(length))),1)\n\n//VARIABLES MANAGEMENT\nTriggerPrice = 0.0, TriggerPrice := TriggerPrice[1]\nTriggerxATR = 0.0, TriggerxATR := TriggerxATR[1]\nSLPrice = 0.0, SLPrice := SLPrice[1], TPPrice = 0.0, TPPrice := TPPrice[1]\nisLong = false, isLong := isLong[1], isShort = false, isShort := isShort[1]\n\n//LOGIC\nGoLong = crossover(HMA[0],HMA[1]) and strategy.position_size == 0.0 and (McG_LS_Switch/McG_LS_Switch[1] > 1) and (not C1_Act or C1>C1[1])\nGoShort = crossunder(HMA[0],HMA[1]) and strategy.position_size == 0.0 and (McG_LS_Switch/McG_LS_Switch[1] < 1) and (not C1_Act or C1<C1[1])\n\n//FRAMEWORK\n\n//Long\nif GoLong and not GoLong[1]\n    isLong := true, TriggerPrice := close\n    TPPrice := TriggerPrice * (1 + (SL * RRR))\n    SLPrice := TriggerPrice * (1-SL)\n    Entry_Contracts = strategy.equity * Risk / ((TriggerPrice-SLPrice)/TriggerPrice) / TriggerPrice //Het aantal contracts moet meegegeven worden. => budget * risk / %afstand tot SL / prijs = aantal contracts\n    strategy.entry("Long", strategy.long, comment=tostring(round(TriggerxATR/TriggerPrice*1000)), qty=Entry_Contracts)\n    strategy.exit("TPSL","Long", limit=TPPrice, stop=SLPrice, qty_percent = 100)\nif isLong and crossunder(HMA[0],HMA[1])\n    strategy.close_all(comment="TrendChange")\n    isLong := false\n\n//Short\nif GoShort and not GoShort[1]\n    isShort := true, TriggerPrice := close\n    TPPrice := TriggerPrice * (1 - (SL * RRR))\n    SLPrice := TriggerPrice * (1 + SL)\n    Entry_Contracts = strategy.equity * Risk / ((SLPrice-TriggerPrice)/TriggerPrice) / TriggerPrice //Het aantal contracts moet meegegeven worden. => budget * risk / %afstand tot SL / prijs = aantal contracts\n    strategy.entry("Short", strategy.short, comment=tostring(round(TriggerxATR/TriggerPrice*1000)), qty=Entry_Contracts)\n    strategy.exit("TPSL","Short", limit=TPPrice, stop=SLPrice)//, qty_percent = 100)\nif isShort and crossover(HMA[0],HMA[1])\n    strategy.close_all(comment="TrendChange")\n    isShort := false\n\n//VISUALISATION\nplot(McG_LS_Switch,color=color.blue,title="Baseline")\nplot(C1_Act?C1:na,color=color.white,title="confirmation Indicator")\nplot(HMA, color=(HMA[0]>HMA[1]? color.green : color.red), linewidth=4, transp=40, title="Entry Indicator")\nplot(isLong or isShort ? TPPrice : na, title="TakeProfit", color=color.green, style=plot.style_linebr)\nplot(isLong or isShort ? SLPrice : na, title="StopLoss", color=color.red, style=plot.style_linebr)\nbgcolor(isLong[1] and cross(low,SLPrice) and low[1] > SLPrice ? color.yellow : na, transp=75, title="SL Long")\nbgcolor(isShort[1] and cross(high,SLPrice) and high[1] < SLPrice ? color.yellow : na, transp=75, title="SL Short")'

class SMD3F2CC4E7DD4405C(PinePortBase, IStrategy):
    source_id = "SM_d3f2cc4e7dd4405c"
    source_file = '简易跟踪趋势策略Simple-Trend-Following-Strategy.md'
    timeframe = '4h'
    can_short = True
    source_defaults = {'Spacer2': False, 'Risk': 1.0, 'RRR': 2, 'SL': 5, 'Spacer3': False, 'McG_length': 50, 'Spacer4': False, 'C1_Act': False, 'C1_len': 5, 'Spacer5': False, 'length': 50}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 100
    source_commission_percent = 0.04
    source_pyramiding = 0
    source_initial_capital = 100000
    source_reproduce_stops = True
    source_risk_flags = ['func', 'broker_state', 'exit_order', 'var_state']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
