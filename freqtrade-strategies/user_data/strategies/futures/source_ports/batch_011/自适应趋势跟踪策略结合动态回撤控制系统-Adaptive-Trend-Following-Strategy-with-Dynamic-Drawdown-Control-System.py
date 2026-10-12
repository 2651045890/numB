"""batch_011 port of 自适应趋势跟踪策略结合动态回撤控制系统-Adaptive-Trend-Following-Strategy-with-Dynamic-Drawdown-Control-System.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2024-11-19 00:00:00\nend: 2024-12-19 00:00:00\nperiod: 2h\nbasePeriod: 2h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy(title="Disruptor Trend-Following (Drawdown < 30%)", shorttitle="DisruptorStrategyDD", overlay=true)\n\n//-----------------------------------------------------\n// User Inputs\n//-----------------------------------------------------\nemaLen         = input.int(200,  "Long EMA Length",    minval=1)\nrsiLen         = input.int(14,   "RSI Length",         minval=1)\nrsiThreshold   = input.float(50, "RSI Buy Threshold",  minval=1, maxval=100)\nstopLossPerc   = input.float(20, "Stop-Loss %",        minval=0.1, step=0.1)\ntakeProfitPerc = input.float(40, "Take-Profit %",      minval=0.1, step=0.1)\nddLimit        = input.float(30, "Max Drawdown %",     minval=0.1, step=0.1)\n\n//-----------------------------------------------------\n// Indicators\n//-----------------------------------------------------\nemaValue       = ta.ema(close, emaLen)\nrsiValue       = ta.rsi(close, rsiLen)\n\n//-----------------------------------------------------\n// Conditions\n//-----------------------------------------------------\nlongCondition  = close > emaValue and rsiValue > rsiThreshold\nexitCondition  = close < emaValue or rsiValue < rsiThreshold\n\n//-----------------------------------------------------\n// Position Tracking\n//-----------------------------------------------------\nvar bool inTrade = false\n\nif longCondition and not inTrade\n    strategy.entry("Long", strategy.long)\n\nif inTrade and exitCondition\n    strategy.close("Long")\n\ninTrade := strategy.position_size > 0\n\n//-----------------------------------------------------\n// Stop-Loss & Take-Profit\n//-----------------------------------------------------\nif inTrade\n    stopPrice       = strategy.position_avg_price * (1 - stopLossPerc / 100)\n    takeProfitPrice = strategy.position_avg_price * (1 + takeProfitPerc / 100)\n    strategy.exit("Exit", from_entry="Long", stop=stopPrice, limit=takeProfitPrice)\n\n//-----------------------------------------------------\n// Dynamic Drawdown Handling\n//-----------------------------------------------------\nvar float peakEquity = strategy.equity\npeakEquity := math.max(peakEquity, strategy.equity)\n\ncurrentDrawdownPerc = (peakEquity - strategy.equity) / peakEquity * 100\nif currentDrawdownPerc > ddLimit\n    strategy.close_all("Max Drawdown Exceeded")\n\n//-----------------------------------------------------\n// Plotting\n//-----------------------------------------------------\nplot(emaValue, title="EMA 200", color=color.yellow, linewidth=2)\nplotchar(rsiValue, title="RSI", char=\'•\', location=location.bottom, color=color.new(color.teal, 60))\n'

class SM14D50CBBFDC5714F(PinePortBase, IStrategy):
    source_id = "SM_14d50cbbfdc5714f"
    source_file = '自适应趋势跟踪策略结合动态回撤控制系统-Adaptive-Trend-Following-Strategy-with-Dynamic-Drawdown-Control-System.md'
    timeframe = '2h'
    can_short = False
    source_defaults = {'emaLen': 200, 'rsiLen': 14, 'rsiThreshold': 50, 'stopLossPerc': 20, 'takeProfitPerc': 40, 'ddLimit': 30}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = True
    source_risk_flags = ['broker_state', 'exit_order', 'var_state']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
