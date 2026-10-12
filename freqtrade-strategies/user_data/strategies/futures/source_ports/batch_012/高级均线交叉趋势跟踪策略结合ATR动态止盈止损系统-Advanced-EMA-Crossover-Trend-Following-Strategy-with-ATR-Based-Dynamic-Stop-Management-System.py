"""batch_012 port of 高级均线交叉趋势跟踪策略结合ATR动态止盈止损系统-Advanced-EMA-Crossover-Trend-Following-Strategy-with-ATR-Based-Dynamic-Stop-Management-System.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2024-12-29 00:00:00\nend: 2025-01-05 00:00:00\nperiod: 2m\nbasePeriod: 2m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This Pine Script™ code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © jesusperezguitarra89\n\n//@version=6\nstrategy("High Profit Buy/Sell Signals", overlay=true)\n\n// Parámetros ajustables\nfastLength = input.int(5, title="Fast EMA Length")\nslowLength = input.int(20, title="Slow EMA Length")\natrLength = input.int(10, title="ATR Length")\natrMultiplier = input.float(2.5, title="ATR Multiplier")\nstopLossPercent = input.float(1.0, title="Stop Loss %")\ntakeProfitPercent = input.float(5.0, title="Take Profit %")\ntrailingStop = input.float(2.0, title="Trailing Stop %")\n\n// Cálculo de EMAs\nfastEMA = ta.ema(close, fastLength)\nslowEMA = ta.ema(close, slowLength)\n\n// Cálculo del ATR\natr = ta.atr(atrLength)\n\n// Señales de compra y venta\nlongCondition = ta.crossover(fastEMA, slowEMA) and close > slowEMA + atrMultiplier * atr\nshortCondition = ta.crossunder(fastEMA, slowEMA) and close < slowEMA - atrMultiplier * atr\n\n// Dibujar señales en el gráfico\nplotshape(series=longCondition, location=location.belowbar, color=color.green, style=shape.labelup, text="BUY")\nplotshape(series=shortCondition, location=location.abovebar, color=color.red, style=shape.labeldown, text="SELL")\n\n// Estrategia de backtesting para marcos de tiempo en minutos\nif longCondition\n    strategy.entry("Buy", strategy.long)\n    strategy.exit("Take Profit", from_entry="Buy", limit=close * (1 + takeProfitPercent / 100), stop=close * (1 - stopLossPercent / 100), trail_points=atr * trailingStop)\nif shortCondition\n    strategy.entry("Sell", strategy.short)\n    strategy.exit("Take Profit", from_entry="Sell", limit=close * (1 - takeProfitPercent / 100), stop=close * (1 + stopLossPercent / 100), trail_points=atr * trailingStop)\n\n// Mostrar EMAs\nplot(fastEMA, color=color.blue, title="Fast EMA")\nplot(slowEMA, color=color.orange, title="Slow EMA")\n\n'

class SMATRAdvancedEMACrossoverTrendFollowingStrategywithATRBas9b49d3(PinePortBase, IStrategy):
    source_id = "SM_9b49d38d85149003"
    source_file = '高级均线交叉趋势跟踪策略结合ATR动态止盈止损系统-Advanced-EMA-Crossover-Trend-Following-Strategy-with-ATR-Based-Dynamic-Stop-Management-System.md'
    timeframe = '2m'
    can_short = True
    source_defaults = {'fastLength': 5, 'slowLength': 20, 'atrLength': 10, 'atrMultiplier': 2.5, 'stopLossPercent': 1.0, 'takeProfitPercent': 5.0, 'trailingStop': 2.0}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_reproduce_stops = True
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_012 md and exposed through the same PinePortBase interface used by batch_001.']

    def pine_indicators(self, dataframe, params):
        # Runtime evaluates the source against the complete OHLCV frame.
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch012Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
