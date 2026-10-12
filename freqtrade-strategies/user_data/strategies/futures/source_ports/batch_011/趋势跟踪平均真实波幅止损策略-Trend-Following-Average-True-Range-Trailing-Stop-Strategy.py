"""batch_011 port of 趋势跟踪平均真实波幅止损策略-Trend-Following-Average-True-Range-Trailing-Stop-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2024-04-01 00:00:00\nend: 2024-04-30 23:59:59\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("Long TAP", overlay=true)\n\n// Constants\nkeyValueDefault = 3.0\nkeyValueStep = 0.5\natrPeriodDefault = 10\n\n// Inputs\nkeyValue = input.float(keyValueDefault, title="Key Value")\natrPeriod = input.int(atrPeriodDefault, title="ATR Period")\n\n// Calculations\nxATR = ta.atr(atrPeriod)\nnLoss = keyValue * xATR\n\n// Trailing Stop Calculation\nvar float xATRTrailingStop = 0.0\nxATRTrailingStop := ta.highest(math.max(nz(xATRTrailingStop[1], 0), close - nLoss), 1)\nxATRTrailingStop := ta.lowest(math.min(nz(xATRTrailingStop, 0), close + nLoss), 1)\n\n// Position Calculation\nvar int pos = 0\npos := nz(pos[1], 0)\nif (close[1] < nz(xATRTrailingStop, 0) and close > nz(xATRTrailingStop, 0))\n    pos := 1\nelse if (close[1] > nz(xATRTrailingStop, 0) and close < nz(xATRTrailingStop, 0))\n    pos := -1\n\n// Plotting Trailing Stop\nvar color xcolor = na\nif (pos == -1)\n    xcolor := color.red\nelse if (pos == 1)\n    xcolor := color.green\nplot(xATRTrailingStop, color=xcolor, title="Trailing Stop")\n\n// Buy/Sell Signals\nbuySignal = ta.crossover(close, xATRTrailingStop)\nsellSignal = ta.crossunder(close, xATRTrailingStop)\n\n// Strategy\nif (buySignal)\n    strategy.entry("Long", strategy.long)\n    label.new(bar_index, xATRTrailingStop, text="Buy Signal", color=color.green, style=label.style_label_up, yloc=yloc.belowbar)\nif (sellSignal)\n    strategy.entry("Short", strategy.short)\n    label.new(bar_index, xATRTrailingStop, text="Sell Signal", color=color.red, style=label.style_label_down, yloc=yloc.abovebar)\n\n// Alerts\nalertcondition(buySignal, title=\'UT BOT Buy\', message=\'UT BOT Buy\')\nalertcondition(sellSignal, title=\'UT BOT Sell\', message=\'UT BOT Sell\')\n'

class SME4A68BABF3545839(PinePortBase, IStrategy):
    source_id = "SM_e4a68babf3545839"
    source_file = '趋势跟踪平均真实波幅止损策略-Trend-Following-Average-True-Range-Trailing-Stop-Strategy.md'
    timeframe = '1h'
    can_short = True
    source_defaults = {}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = False
    source_risk_flags = ['var_state', 'alert_or_drawing']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
