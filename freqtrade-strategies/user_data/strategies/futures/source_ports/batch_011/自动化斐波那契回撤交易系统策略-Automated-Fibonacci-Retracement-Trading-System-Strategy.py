"""batch_011 port of 自动化斐波那契回撤交易系统策略-Automated-Fibonacci-Retracement-Trading-System-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2025-01-01 00:00:00\nend: 2025-03-31 00:00:00\nperiod: 1d\nbasePeriod: 1d\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("Estrategia Fibonacci con Señales", overlay=true, initial_capital=100, currency=currency.USD, margin_long=100, margin_short=100)\n\n// 1. Configuración de Fibonacci\nlookback = input.int(20, "Período Swing", minval=10)\nfibLevels = input.string("38.2|61.8", "Niveles Fib") \nriskPercentage = input.float(1.0, "Riesgo por Operación %", step=0.5)\n\n// 2. Detectar swings y niveles Fib\nswingHigh = ta.highest(high, lookback)\nswingLow = ta.lowest(low, lookback)\nfib382 = swingLow + (swingHigh - swingLow) * 0.382\nfib618 = swingLow + (swingHigh - swingLow) * 0.618\n\n// 3. Condiciones de trading\nlongCondition = ta.crossover(close, fib618)\nshortCondition = ta.crossunder(close, fib382)\n\n// 4. Indicadores Visuales\nplotshape(series=longCondition, title="Señal Compra", color=color.new(color.green, 0), \n  style=shape.triangleup, location=location.belowbar, size=size.small, text="COMPRA")\n\nplotshape(series=shortCondition, title="Señal Venta", color=color.new(color.red, 0), \n  style=shape.triangledown, location=location.abovebar, size=size.small, text="VENTA")\n\n// 5. Gestión de Capital\npositionSize = (strategy.equity * riskPercentage/100) / (close * 0.01)\n\n// 6. Lógica de Ejecución\nif (longCondition)\n    strategy.entry("Long", strategy.long, qty=positionSize)\n    strategy.exit("SL/TP Long", "Long", stop=close*0.99, limit=close*1.02)\n\nif (shortCondition)\n    strategy.entry("Short", strategy.short, qty=positionSize)\n    strategy.exit("SL/TP Short", "Short", stop=close*1.01, limit=close*0.98)\n\n// 7. Líneas Fibonacci\nplot(fib382, "38.2% Fib", color=color.purple, linewidth=2)\nplot(fib618, "61.8% Fib", color=color.blue, linewidth=2)\n\n// 8. Alertas\nalertcondition(longCondition, "Alerta COMPRA Oro", "Entrada Long en Fib 61.8%")\nalertcondition(shortCondition, "Alerta VENTA Oro", "Entrada Short en Fib 38.2%")'

class SM489B7F5AB2972B33(PinePortBase, IStrategy):
    source_id = "SM_489b7f5ab2972b33"
    source_file = '自动化斐波那契回撤交易系统策略-Automated-Fibonacci-Retracement-Trading-System-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'lookback': 20, 'fibLevels': '38.2|61.8', 'riskPercentage': 1.0}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 100
    source_reproduce_stops = True
    source_risk_flags = ['broker_state', 'exit_order']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
