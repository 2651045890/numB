"""batch_011 port of 自动交易趋势追踪动态风险管理策略-Automated-Trading-Trend-Tracking-Dynamic-Risk-Management-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2024-04-02 00:00:00\nend: 2025-04-02 00:00:00\nperiod: 1d\nbasePeriod: 1d\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("Strategia Semmoncino", shorttitle="semmoncino", overlay=true, default_qty_type=strategy.percent_of_equity, default_qty_value=10, commission_type=strategy.commission.percent, commission_value=0.05)\n\n// Inputs\nuseVolumeFilter = input.bool(true, title="Usa Filtro di Volume")\nvolumeThreshold = input.float(1.5, title="Soglia Volume (x Media)", minval=1)\natrPeriod = input.int(14, title="ATR Period", minval=1)\natrMultiplier = input.float(2.0, title="ATR Multiplier", minval=0.1)\ntakeProfitMultiplier = input.float(6.0, title="Take Profit Multiplier", minval=1.0)  // Aumentato per ottimizzare\nriskPerTrade = input.float(2.0, title="Rischio per Trade (%)", minval=0.1) / 100\nmaxDailyLoss = input.float(2.0, title="Perdita Massima Giornaliera (%)", minval=0.1) / 100\nmaxDrawdown = input.float(10.0, title="Drawdown Massimo (%)", minval=0.1) / 100\nshortMAPeriod = input.int(20, title="MA Breve Termine", minval=1)\nlongMAPeriod = input.int(100, title="MA Lungo Termine", minval=1)\n\n// MACD Inputs\nmacdFastLength = input.int(12, title="MACD Fast Length")\nmacdSlowLength = input.int(26, title="MACD Slow Length")\nmacdSignalLength = input.int(9, title="MACD Signal Length")\n\nshowSignals = input.bool(true, title="Mostra Segnali di Entrata")\n\n// Prezzi di Apertura e Chiusura delle Candele Precedenti (senza repainting)\nprevOpen = ta.valuewhen(1, open, 0)\nprevClose = ta.valuewhen(1, close, 0)\n\n// Calculate ATR\natr = ta.atr(atrPeriod)\n\n// Calculate Volume Filter\nvolumeAvg = ta.sma(volume, 20)\nvolumeFilter = useVolumeFilter ? volume > (volumeAvg * volumeThreshold) : true\n\n// Calculate Moving Averages\nshortMA = ta.sma(close, shortMAPeriod)\nlongMA = ta.sma(close, longMAPeriod)\n\n// Calculate MACD\n[macdLine, signalLine, _] = ta.macd(close, macdFastLength, macdSlowLength, macdSignalLength)\nmacdConditionLong = macdLine > signalLine\nmacdConditionShort = macdLine < signalLine\n\n// Determine Trend Direction\nuptrend = shortMA > longMA\ndowntrend = shortMA < longMA\n\n// Determine Order Conditions\nlongCondition = prevClose > prevOpen and volumeFilter and uptrend and macdConditionLong\nshortCondition = prevClose < prevOpen and volumeFilter and downtrend and macdConditionShort\n\n// Calcola la dimensione della posizione basata sul capitale iniziale\ninitialCapital = strategy.initial_capital\npositionSize = (initialCapital * riskPerTrade) / (atr * atrMultiplier)\n\n// Calculate Take Profit and Stop Loss Levels dynamically using ATR\ntakeProfitLong = close + (atr * takeProfitMultiplier)\nstopLossLong = close - (atr * 1.5)  // Ridotto per ottimizzare\ntakeProfitShort = close - (atr * takeProfitMultiplier)\nstopLossShort = close + (atr * 1.5)  // Ridotto per ottimizzare\n\n// Limite di Perdita Giornaliera\nvar float dailyLossLimit = na\nif na(dailyLossLimit) or (time - time) > 86400000 // Se è un nuovo giorno\n    dailyLossLimit := strategy.equity * (1 - maxDailyLoss)\n\n// Drawdown Massimo\nvar float drawdownLimit = na\nif na(drawdownLimit)\n    drawdownLimit := strategy.equity * (1 - maxDrawdown)\n\n// Controllo delle Perdite\nif strategy.equity < dailyLossLimit\n    strategy.cancel_all()\n    strategy.close_all()\n    label.new(bar_index, high, text="Perdita Giornaliera Massima Raggiunta", color=color.red)\n\nif strategy.equity < drawdownLimit\n    strategy.cancel_all()\n    strategy.close_all()\n    label.new(bar_index, high, text="Drawdown Massimo Raggiunto", color=color.red)\n\n// Strategy Entries\nif (longCondition)\n    strategy.entry("Long", strategy.long, qty=positionSize)\n    strategy.exit("Take Profit/Stop Loss Long", from_entry="Long", limit=takeProfitLong, stop=stopLossLong)\n\nif (shortCondition)\n    strategy.entry("Short", strategy.short, qty=positionSize)\n    strategy.exit("Take Profit/Stop Loss Short", from_entry="Short", limit=takeProfitShort, stop=stopLossShort)\n\n// Plot Entry Signals\nplotshape(series=longCondition and showSignals ? close : na, location=location.belowbar, color=color.green, style=shape.labelup, text="LONG")\nplotshape(series=shortCondition and showSignals ? close : na, location=location.abovebar, color=color.red, style=shape.labeldown, text="SHORT")\n\n// Plot Moving Averages\nplot(shortMA, color=color.blue, title="MA Breve Termine", linewidth=2)\nplot(longMA, color=color.orange, title="MA Lungo Termine", linewidth=2)\n\n// Plot MACD\nhline(0, "Zero Line", color=color.gray)\nplot(macdLine - signalLine, title="MACD Histogram", color=color.red, style=plot.style_histogram)'

class SMFBC015AC04A9828D(PinePortBase, IStrategy):
    source_id = "SM_fbc015ac04a9828d"
    source_file = '自动交易趋势追踪动态风险管理策略-Automated-Trading-Trend-Tracking-Dynamic-Risk-Management-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'useVolumeFilter': True, 'volumeThreshold': 1.5, 'atrPeriod': 14, 'atrMultiplier': 2.0, 'takeProfitMultiplier': 6.0, 'riskPerTrade': 2.0, 'maxDailyLoss': 2.0, 'maxDrawdown': 10.0, 'shortMAPeriod': 20, 'longMAPeriod': 100, 'macdFastLength': 12, 'macdSlowLength': 26, 'macdSignalLength': 9, 'showSignals': True}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 10
    source_commission_percent = 0.05
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = True
    source_risk_flags = ['broker_state', 'tuple', 'exit_order', 'var_state', 'alert_or_drawing']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
