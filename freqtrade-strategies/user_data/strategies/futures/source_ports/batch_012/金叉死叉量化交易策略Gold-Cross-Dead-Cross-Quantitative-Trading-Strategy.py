"""batch_012 port of 金叉死叉量化交易策略Gold-Cross-Dead-Cross-Quantitative-Trading-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2024-01-01 00:00:00\nend: 2024-01-31 23:59:59\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("Estrategia de Cruce de Medias Móviles", overlay=true)\n\n// Medias móviles\nma30 = ta.sma(close, 30)\nma60 = ta.sma(close, 60)\nma200 = ta.sma(close, 200)\n\n// Cruce de medias móviles\ncrossoverUp = ta.crossover(ma30, ma200)\ncrossoverDown = ta.crossunder(ma30, ma200)\n\n// Señales de compra y venta\nlongCondition = crossoverUp\nshortCondition = crossoverDown\n\n// Ejecución de órdenes\nif (longCondition)\n    strategy.entry("Buy", strategy.long)\n    strategy.exit("Cover", "Buy", stop=close - 40.000, limit=close + 40.000)\nif (shortCondition)\n    strategy.entry("Sell", strategy.short)\n    strategy.exit("Cover", "Sell", stop=close + 40.000, limit=close - 40.000)\n\n// Plot de las medias móviles\nplot(ma30, color=color.blue, title="MA 30")\nplot(ma60, color=color.orange, title="MA 60")\nplot(ma200, color=color.green, title="MA 200")\n\n// Condiciones para cerrar la posición contraria\nif (strategy.position_size > 0)\n    if (crossoverDown)\n        strategy.close("Buy")\nif (strategy.position_size < 0)\n    if (crossoverUp)\n        strategy.close("Sell")\n'

class SMGoldCrossDeadCrossQuantitativeTradingStrategyfdc808(PinePortBase, IStrategy):
    source_id = "SM_fdc808dbedba3352"
    source_file = '金叉死叉量化交易策略Gold-Cross-Dead-Cross-Quantitative-Trading-Strategy.md'
    timeframe = '1h'
    can_short = True
    source_defaults = {}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_reproduce_stops = True
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_012 md and exposed through the same PinePortBase interface used by batch_001.', 'The source reads live strategy position state; batch_001-style broker-state parity must be checked manually for this file.']

    def pine_indicators(self, dataframe, params):
        # Runtime evaluates the source against the complete OHLCV frame.
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch012Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
