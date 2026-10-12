"""batch_012 port of 高级双均线策略交叉交易系统-Advanced-Dual-Moving-Average-Crossover-Trading-System.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2024-04-02 00:00:00\nend: 2024-12-31 00:00:00\nperiod: 3d\nbasePeriod: 3d\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("Intraday MA Crossover Strategy ", overlay=true)\n\n// Define the short-term and long-term moving averages\nshortLength = input.int(5, title="Short MA Length")\nlongLength = input.int(21, title="Long MA Length")\n\n// Calculate the moving averages\nshortMA = ta.sma(close, shortLength)\nlongMA = ta.sma(close, longLength)\n\n// Plot the moving averages on the chart\nplot(shortMA, color=color.blue, title="Short MA (9)")\nplot(longMA, color=color.rgb(243, 179, 4), title="Long MA (21)")\n\n// Generate buy and sell signals\nlongSignal = ta.crossover(shortMA, longMA)\nshortSignal = ta.crossunder(shortMA, longMA)\n\n// Execute trades\nstrategy.entry("Buy", strategy.long, when=longSignal)\nstrategy.close("Buy", when=shortSignal)\n\n// Optional: Stop loss and take profit levels (e.g., 1% of the entry price)\nstopLossPercent = input.float(1, title="Stop Loss (%)") / 100\ntakeProfitPercent = input.float(2, title="Take Profit (%)") / 100\n\nstrategy.exit("Exit Buy", "Buy", stop=close * (1 - stopLossPercent), limit=close * (1 + takeProfitPercent))\n\n// Variables to track the unique identifier for each pair\nvar int counter = 0\nvar float buyPrice = na\nvar float sellPrice = na\nvar int buyBarIndex = na\nvar int sellBarIndex = na\n\n// Add labels and connect them with lines\nif (longSignal)\n    counter := counter + 1\n    buyPrice := low\n    buyBarIndex := bar_index\n    label.new(buyBarIndex, buyPrice, "BUY " + str.tostring(counter), color=color.rgb(54, 58, 243), style=label.style_label_up, textcolor=color.white, size=size.small)\n\nif (shortSignal and not na(buyPrice))\n    sellPrice := high\n    sellBarIndex := bar_index\n    label.new(sellBarIndex, sellPrice, "SELL " + str.tostring(counter), color=color.rgb(243, 162, 57), style=label.style_label_down, textcolor=color.white, size=size.small)\n\n\n\n// Strategy performance\nplot(strategy.equity, color=color.green, title="Equity Curve")\n\n// Alerts with dynamic messages for webhook\nalertcondition(longSignal, title="Buy Signal", message="{{ticker}}|BUY|1")\nalertcondition(shortSignal, title="Sell Signal", message="{{ticker}}|SELL|1")\n\n'

class SMAdvancedDualMovingAverageCrossoverTradingSystem7095c1(PinePortBase, IStrategy):
    source_id = "SM_7095c19f6a1065b0"
    source_file = '高级双均线策略交叉交易系统-Advanced-Dual-Moving-Average-Crossover-Trading-System.md'
    timeframe = '3d'
    can_short = False
    source_defaults = {'shortLength': 5, 'longLength': 21}
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
