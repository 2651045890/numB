"""batch_012 port of 黄金交叉短期突破策略Short-term-Breakthrough-Strategy-Based-on-Golden-Crossover.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2024-01-27 00:00:00\nend: 2024-02-26 00:00:00\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("simple pull back", overlay=true, default_qty_type=strategy.percent_of_equity, default_qty_value=100)\n\n// Input values\nmalongperiod = input.int(200, "Long Term SMA Period", group="Parameters")\nmashortperiod = input.int(21, "Short Term SMA Period", group="Parameters")\nstoprate = 1  // Set the stop loss percentage to 1%\nprofit = input.int(1, "Take Profit Percentage", group="Parameters") // Change the take profit percentage to 1%\nstartday = input(title="Start Trade Day", defval=timestamp("01 Jan 2000 13:30 +0000"), group="Period")\nendday = input(title="End Trade Day", defval=timestamp("1 Jan 2099 19:30 +0000"), group="Period")\n\n// Plotting indicators\nmalong = ta.sma(close, malongperiod)\nmashort = ta.ema(close, mashortperiod)\n\nplot(malong, color=color.aqua, linewidth=2)\nplot(mashort, color=color.yellow, linewidth=2)\n\n// Date range\ndatefilter = true\n\n// Long entry condition\nif close > malong and close < mashort and strategy.position_size == 0 and datefilter and ta.rsi(close, 3) < 20\n    strategy.entry("Long", strategy.long)\n\n// Short entry condition\nif close < malong and close > mashort and strategy.position_size == 0 and datefilter and ta.rsi(close, 3) > 80\n    strategy.entry("Short", strategy.short)\n\n// Exit conditions with 1% stop loss and 1% take profit\nstrategy.exit("Cut", "Long", stop=(1 - 0.01 * stoprate) * strategy.position_avg_price, limit=(1 + 0.01 * profit) * strategy.position_avg_price)\n\nif close > mashort and close < low[1] and strategy.position_size > 0\n    strategy.close("Long")\nif close < mashort and close > high[1] and strategy.position_size < 0\n    strategy.close("Short")\n'

class SMShorttermBreakthroughStrategyBasedonGoldenCrossovere1282a(PinePortBase, IStrategy):
    source_id = "SM_e1282a710c455dbc"
    source_file = '黄金交叉短期突破策略Short-term-Breakthrough-Strategy-Based-on-Golden-Crossover.md'
    timeframe = '1h'
    can_short = True
    source_defaults = {'malongperiod': 200, 'mashortperiod': 21, 'startday': 'timestamp("01 Jan 2000 13:30 +0000")', 'endday': 'timestamp("1 Jan 2099 19:30 +0000")'}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 100
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
