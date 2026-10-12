"""batch_012 port of 高级EMA交叉策略基于动态止损和获利目标的自适应交易系统Advanced-EMA-Crossover-Strategy-Adaptive-Trading-System-with-Dynamic-Stop-Loss-and-Take-Profit-Targets.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2024-07-01 00:00:00\nend: 2024-07-28 00:00:00\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("EMA Crossover Strategy with Fixed Stop Loss, Take Profit, and Alerts", overlay=true)\n\n// Define the EMAs\nema9 = ta.ema(close, 9)\nema26 = ta.ema(close, 26)\n\n// Plot the EMAs on the chart\nplot(ema9, color=color.blue, title="9 EMA")\nplot(ema26, color=color.red, title="26 EMA")\n\n// Define the crossover conditions\nlongCondition = ta.crossover(ema9, ema26)\nshortCondition = ta.crossunder(ema9, ema26)\n\n// Define stop loss and take profit (in ticks)\ntick_size = syminfo.mintick\nstop_loss_ticks = 90\ntake_profit_ticks = 270\nstop_loss = stop_loss_ticks * tick_size\ntake_profit = take_profit_ticks * tick_size\n\n// Plot buy and sell signals on the chart\nplotshape(series=longCondition, location=location.belowbar, color=color.green, style=shape.labelup, title="Buy Signal")\nplotshape(series=shortCondition, location=location.abovebar, color=color.red, style=shape.labeldown, title="Sell Signal")\n\n// Initialize variables to store the stop loss and take profit prices\nvar float long_stop_price = na\nvar float long_take_profit_price = na\nvar float short_stop_price = na\nvar float short_take_profit_price = na\n\n// Strategy orders with fixed stop loss and take profit\nif (longCondition)\n    long_stop_price := close - stop_loss\n    long_take_profit_price := close + take_profit\n    strategy.entry("Long", strategy.long)\n    strategy.exit("Exit Long", from_entry="Long", stop=long_stop_price, limit=long_take_profit_price)\n\nif (shortCondition)\n    short_stop_price := close + stop_loss\n    short_take_profit_price := close - take_profit\n    strategy.entry("Short", strategy.short)\n    strategy.exit("Exit Short", from_entry="Short", stop=short_stop_price, limit=short_take_profit_price)\n\n// Display stop loss and take profit on chart\nplot(long_stop_price, color=color.green, linewidth=2, title="Long Stop Level")\nplot(long_take_profit_price, color=color.green, linewidth=2, title="Long Take Profit Level")\nplot(short_stop_price, color=color.red, linewidth=2, title="Short Stop Level")\nplot(short_take_profit_price, color=color.red, linewidth=2, title="Short Take Profit Level")\n\n// Alert conditions\nalertcondition(longCondition, title="Long Alert", message="9 EMA crossed above 26 EMA - Buy Signal")\nalertcondition(shortCondition, title="Short Alert", message="9 EMA crossed below 26 EMA - Sell Signal")\n\n// Trigger alerts\nif (longCondition)\n    alert("9 EMA crossed above 26 EMA - Buy Signal", alert.freq_once_per_bar)\n\nif (shortCondition)\n    alert("9 EMA crossed below 26 EMA - Sell Signal", alert.freq_once_per_bar)\n'

class SMEMAAdvancedEMACrossoverStrategyAdaptiveTradingSystemwitde09f3(PinePortBase, IStrategy):
    source_id = "SM_de09f3969bc6b73f"
    source_file = '高级EMA交叉策略基于动态止损和获利目标的自适应交易系统Advanced-EMA-Crossover-Strategy-Adaptive-Trading-System-with-Dynamic-Stop-Loss-and-Take-Profit-Targets.md'
    timeframe = '1h'
    can_short = True
    source_defaults = {}
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
