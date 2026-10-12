"""batch_011 port of 自适应趋势跟踪交易策略200均线突破与动态风险管理系统-Adaptive-Trend-Following-Trading-Strategy-200-EMA-Breakout-with-Dynamic-Risk-Management-System.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-07-23 00:00:00\nend: 2024-07-28 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("200 EMA Strategy", overlay=true)\n\n// Input parameters\nemaLength = input.int(200, title="EMA Length")\nstopLossPercent = input.float(1.0, title="Stop Loss (%)", step=0.1)\ntakeProfitPercent = input.float(2.0, title="Take Profit (%)", step=0.1)\n\n// Enable buy and sell strategies\nenableBuy = input.bool(true, title="Enable Buy Strategy")\nenableSell = input.bool(true, title="Enable Sell Strategy")\n\n// Calculate 200 EMA\nema200 = ta.ema(close, emaLength)\n\n// Plot the EMA on the chart\nplot(ema200, color=color.blue, title="200 EMA")\n\n// Buy condition: close is above the 200 EMA\nif (enableBuy and ta.crossover(close, ema200))\n    // Define stop loss and take profit levels\n    stopLossPrice = close * (1 - stopLossPercent / 100)\n    takeProfitPrice = close * (1 + takeProfitPercent / 100)\n    \n    // Enter long position\n    strategy.entry("Buy", strategy.long)\n    \n    // Set stop loss and take profit\n    strategy.exit("Take Profit/Stop Loss", "Buy", stop=stopLossPrice, limit=takeProfitPrice)\n\n// Sell condition: close is below the 200 EMA\nif (enableSell and ta.crossunder(close, ema200))\n    // Define stop loss and take profit levels\n    stopLossPrice = close * (1 + stopLossPercent / 100)\n    takeProfitPrice = close * (1 - takeProfitPercent / 100)\n    \n    // Enter short position\n    strategy.entry("Sell", strategy.short)\n    \n    // Set stop loss and take profit\n    strategy.exit("Take Profit/Stop Loss", "Sell", stop=stopLossPrice, limit=takeProfitPrice)\n'

class SMA2FA10F3F7E63CC2(PinePortBase, IStrategy):
    source_id = "SM_a2fa10f3f7e63cc2"
    source_file = '自适应趋势跟踪交易策略200均线突破与动态风险管理系统-Adaptive-Trend-Following-Trading-Strategy-200-EMA-Breakout-with-Dynamic-Risk-Management-System.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'emaLength': 200, 'stopLossPercent': 1.0, 'takeProfitPercent': 2.0, 'enableBuy': True, 'enableSell': True}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = True
    source_risk_flags = ['exit_order']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
