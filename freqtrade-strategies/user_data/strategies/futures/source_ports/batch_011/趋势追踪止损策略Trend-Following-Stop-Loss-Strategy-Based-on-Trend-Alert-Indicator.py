"""batch_011 port of 趋势追踪止损策略Trend-Following-Stop-Loss-Strategy-Based-on-Trend-Alert-Indicator.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-01-29 00:00:00\nend: 2024-02-04 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This Pine Script™ code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © jaque_verdatre\n\n//@version=5\nstrategy("TrendAlert Based", overlay = true)\n\n// Get inputs\nTrendAlert = input.source(close, "TrendAlert")\natrLength = input.int(title="ATR Length", defval=15, minval=1)\nuseStructure = input.bool(title="Use Structure?", defval=true)\nlookback = input.int(title="How Far To Look Back For High/Lows", defval=8, minval=1)\natrStopMultiplier = input.float(title="ATR Multiplier", defval=0.2, minval=0.1)\nLimitMultiplier = input.float(title = "Limit Multiplier", defval = 0.5, minval = 0.1)\nPineConnectorID = input.int(title = "Pine Connector ID",defval = 0)\nCurrencyToSend = input.string(title = "personilized currency", defval = "ETHUSD")\nRisk = input.int(title = "risk in % to send", defval = 10, minval = 1)\n\n// Calculate data\natr = ta.atr(atrLength)\nlowestLow = ta.lowest(low, lookback)\nhighestHigh = ta.highest(high, lookback)\nlongStop = (useStructure ? lowestLow : close) - atr * atrStopMultiplier\nshortStop = (useStructure ? highestHigh : close) + atr * atrStopMultiplier\n\n// Draw data to chart\nplot(atr, color=color.rgb(33, 149, 243), title="ATR", display = display.none)\nplot(longStop, color=color.green, title="Long Trailing Stop")\nplot(shortStop, color=color.red, title="Short Trailing Stop")\n\nvar float LimitL = na\nvar float LimitS = na\nvar float LPosPrice = na\nvar float SPosPrice = na\nvar float LPosLongStop = na\nvar float SPosShortStop = na\n\nKnowLimit (PosPrice, PosStop) =>\n    (PosPrice-PosStop)*LimitMultiplier+PosPrice\n\n\nNotInTrade = strategy.position_size == 0\nInLongTrade = strategy.position_size > 0\nInShortTrade = strategy.position_size < 0\n\nlongCondition = TrendAlert > 0 and NotInTrade\nif (longCondition)\n    LPosPrice := close\n    LPosLongStop := longStop\n    LimitL := KnowLimit(LPosPrice, LPosLongStop)\n    strategy.entry("long", strategy.long)\n    LTPPip = LimitL-LPosPrice\n    LSLPip = LPosPrice-longStop\n    alert(str.tostring(PineConnectorID)+\',buy,\'+str.tostring(CurrencyToSend)+\',risk=\'+str.tostring(Risk)+\',sl=\'+str.tostring(LSLPip)+\'tp=\'+str.tostring(LTPPip), alert.freq_once_per_bar_close)\n    strategy.exit("exit", "long", stop = longStop, limit = LimitL)\n\nshortCondition = TrendAlert < 0 and NotInTrade\nif (shortCondition)\n    SPosPrice := close\n    SPosShortStop := shortStop\n    LimitS := KnowLimit(SPosPrice, SPosShortStop)\n    strategy.entry("short", strategy.short)\n    STPPip = SPosPrice-LimitS\n    SSLPip = shortStop - SPosPrice\n    alert(str.tostring(PineConnectorID)+\',sell,ETHUSD,risk=10,sl=\'+str.tostring(SSLPip)+\'tp=\'+str.tostring(STPPip), alert.freq_once_per_bar_close)\n    strategy.exit("exit", "short", stop = shortStop, limit = LimitS)\n\nplotshape(longCondition, color = color.green, style = shape.labelup, location = location.belowbar, size = size.normal, title = "Long Condition")\nplotshape(shortCondition, color = color.red, style = shape.labeldown, location = location.abovebar, size = size.normal, title = "Short Condition")\n\nif (InShortTrade)\n    LimitL := close\n    LPosLongStop := close\n    LPosPrice := close\n\nPlotLongTakeProfit = plot(LimitL, color = InLongTrade ? color.rgb(0, 255, 64) : color.rgb(120, 123, 134, 100), title = "Long Take Profit")\nPlotLongStopLoss = plot(LPosLongStop, color = InLongTrade ? color.rgb(255, 0, 0) : color.rgb(120, 123, 134, 100), title = "Long Stop Loss")\nPlotLongPosPrice = plot(LPosPrice, color = InLongTrade ? color.gray : color.rgb(120, 123, 134, 100), title = "Long Position Price")\n\nif (InLongTrade)\n    LimitS := close\n    SPosShortStop := close\n    SPosPrice := close\n\nPlotShortTakeProfit = plot(LimitS, color = InShortTrade ? color.rgb(0, 255, 64) : color.rgb(120, 123, 134, 100), title = "Short Take Profit")\nPlotShortStopLoss = plot(SPosShortStop, color = InShortTrade ? color.rgb(255, 0, 0) : color.rgb(120, 123, 134, 100), title = "Short Stop Loss")\nPlotShortPosPrice = plot(SPosPrice, color = InShortTrade ? color.gray : color.rgb(120, 123, 134, 100), title = "Short Position Price")\n\nfill(PlotLongPosPrice, PlotLongTakeProfit, color = InLongTrade ? color.rgb(0, 255, 0, 95) : color.rgb(0, 255, 0, 100))\nfill(PlotShortPosPrice, PlotShortTakeProfit, color = InShortTrade ? color.rgb(0, 255, 0, 95) : color.rgb(0, 255, 0, 100))\n\nfill(PlotLongPosPrice, PlotLongStopLoss, color = InLongTrade ? color.rgb(255, 0, 0, 95) : color.rgb(255, 0, 0, 100))\nfill(PlotShortPosPrice, PlotShortStopLoss, color = InShortTrade ? color.rgb(255, 0, 0, 95) : color.rgb(255, 0, 0, 100))'

class SM1D3E122D5B19B72A(PinePortBase, IStrategy):
    source_id = "SM_1d3e122d5b19b72a"
    source_file = '趋势追踪止损策略Trend-Following-Stop-Loss-Strategy-Based-on-Trend-Alert-Indicator.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'atrLength': 15, 'useStructure': True, 'lookback': 8, 'atrStopMultiplier': 0.2, 'LimitMultiplier': 0.5, 'PineConnectorID': 0, 'CurrencyToSend': 'ETHUSD', 'Risk': 10}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
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
