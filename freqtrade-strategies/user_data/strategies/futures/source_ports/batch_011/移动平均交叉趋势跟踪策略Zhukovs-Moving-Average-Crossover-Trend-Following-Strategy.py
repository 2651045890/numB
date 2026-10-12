"""batch_011 port of 移动平均交叉趋势跟踪策略Zhukovs-Moving-Average-Crossover-Trend-Following-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2022-12-05 00:00:00\nend: 2023-12-11 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This strategy has been created for GMT trade 4h by Zhukov\n\n\n//@version=5\nstrategy(\'ZhukovTrade\', overlay=true, calc_on_every_tick=true, currency=currency.USD)\n\n// INPUT:\n\n// Options to enter fast and slow Exponential Moving Average (EMA) values\nemaFast = input.int(title=\'Fast EMA\', defval=100, minval=1, maxval=9999)\nemaSlow = input.int(title=\'Slow EMA\', defval=200, minval=1, maxval=9999)\n\n// Option to select trade directions\ntradeDirection = input.string(title=\'Trade Direction\', options=[\'Long\', \'Short\', \'Both\'], defval=\'Both\')\n\n// Options that configure the backtest date range\nstartDate = input(title=\'Start Date\', defval=timestamp(\'01 Jan 2023 00:00\'))\nendDate = input(title=\'End Date\', defval=timestamp(\'31 Dec 2023 23:59\'))\n\n\n// CALCULATIONS:\n\n// Use the built-in function to calculate two EMA lines\nfastEMA = ta.ema(close, emaFast)\nslowEMA = ta.ema(close, emaSlow)\nemapos = ta.ema(close,200)\n\n// PLOT:\n\n// Draw the EMA lines on the chart\nplot(series=fastEMA, color=color.new(color.orange, 0), linewidth=2)\nplot(series=slowEMA, color=color.new(color.blue, 0), linewidth=2)\nplot(series=emapos, color=color.new(color.red, 0), linewidth=2)\n\n\n// CONDITIONS:\n\n// Check if the close time of the current bar falls inside the date range\ninDateRange = true\n\n// Translate input into trading conditions\nlongOK = tradeDirection == \'Long\' or tradeDirection == \'Both\'\nshortOK = tradeDirection == \'Short\' or tradeDirection == \'Both\'\n\n// Decide if we should go long or short using the built-in functions\nlongCondition = ta.crossover(fastEMA, slowEMA) \nshortCondition = ta.crossunder(fastEMA, slowEMA) \n// ORDERS:\n// Set take profit and stop loss percentages\ntake_profit_percent = input(0, title="Take Profit Percent")\nstop_loss_percent = input(0, title="Stop Loss Percent")\n// Submit entry (or reverse) orders\n\n\natrPeriod = input(12, "ATR Length")\nfactor = input.float(3.0, "Factor", step = 0.01)\n\n[supertrend, direction] = ta.supertrend(factor, atrPeriod)\n\nbodyMiddle = plot((open + close) / 2, display=display.none)\nupTrend = plot(direction < 0 ? supertrend : na, "Up Trend", color = color.green, style=plot.style_linebr)\ndownTrend = plot(direction < 0? na : supertrend, "Down Trend", color = color.red, style=plot.style_linebr)\n\nfill(bodyMiddle, upTrend, color.new(color.green, 90), fillgaps=false)\nfill(bodyMiddle, downTrend, color.new(color.red, 90), fillgaps=false)\n\nif longCondition and inDateRange \n    if longOK and direction<0\n\n        strategy.entry(id=\'long\', direction=strategy.long, alert_message = "LONG")\nif shortCondition and inDateRange \n    if shortOK and direction>0\n        strategy.entry(id=\'short\', direction=strategy.short, alert_message = "SHORT")\n\n// Submit exit orders in the cases where we trade only long or only short\n\nif strategy.position_size > 0 and take_profit_percent\n    strategy.exit(id=\'tp long\',from_entry ="long",profit = take_profit_percent)\nif strategy.position_size > 0 and stop_loss_percent\n    strategy.exit(id=\'sl long\',from_entry="long",loss=stop_loss_percent)\n\nif strategy.position_size < 0 and stop_loss_percent\n    strategy.exit(id=\'sl short\',from_entry="short",loss=stop_loss_percent)\nif strategy.position_size < 0 and take_profit_percent\n    strategy.exit(id=\'tp short\',from_entry="short",profit = take_profit_percent)\n'

class SM1CB24EBF86B1ECB7(PinePortBase, IStrategy):
    source_id = "SM_1cb24ebf86b1ecb7"
    source_file = '移动平均交叉趋势跟踪策略Zhukovs-Moving-Average-Crossover-Trend-Following-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'emaFast': 100, 'emaSlow': 200, 'tradeDirection': 'Both', 'take_profit_percent': 0, 'stop_loss_percent': 0, 'atrPeriod': 12, 'factor': 3.0}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = True
    source_risk_flags = ['broker_state', 'tuple', 'exit_order']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
