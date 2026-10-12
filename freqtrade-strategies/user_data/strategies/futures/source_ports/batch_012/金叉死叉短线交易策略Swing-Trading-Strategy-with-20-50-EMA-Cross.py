"""batch_012 port of 金叉死叉短线交易策略Swing-Trading-Strategy-with-20-50-EMA-Cross.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-01-05 00:00:00\nend: 2024-01-11 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("Swing Trading with 20/50 EMA Cross", shorttitle = "EMA Cross", overlay = true)\n\n// Define input for stop-loss and take-profit levels\nvar float stopLossPct = input.float(1, title = "Stop Loss (%)") / 100\nvar float rewardRiskRatio = input.float(2, title = "Risk-Reward Ratio")\ntakeProfitPct = stopLossPct * rewardRiskRatio\n\n// Calculate EMA values\nema20 = ta.ema(close, 20)\nema50 = ta.ema(close, 50)\n\n// Plot EMAs on the chart\nplot(ema20, title = "20 EMA", color = color.blue)\nplot(ema50, title = "50 EMA", color = color.red)\n\n// Trading conditions\nlongCondition = ta.crossover(ema20, ema50)\nshortCondition = ta.crossunder(ema20, ema50)\n\n// Execute long and short trades\nstrategy.entry("Long", strategy.long, when = longCondition)\nstrategy.entry("Short", strategy.short, when = shortCondition)\n\n// Calculate stop-loss and take-profit levels based on risk-reward ratio\nstopLossPrice = close * (1 - stopLossPct)\ntakeProfitPrice = close * (1 + takeProfitPct)\n\nstrategy.exit("Take Profit/Stop Loss", stop = stopLossPrice, limit = takeProfitPrice)\n\n'

class SMSwingTradingStrategywith2050EMACross1b1ac7(PinePortBase, IStrategy):
    source_id = "SM_1b1ac7200ee574bf"
    source_file = '金叉死叉短线交易策略Swing-Trading-Strategy-with-20-50-EMA-Cross.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'rewardRiskRatio': 2}
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
