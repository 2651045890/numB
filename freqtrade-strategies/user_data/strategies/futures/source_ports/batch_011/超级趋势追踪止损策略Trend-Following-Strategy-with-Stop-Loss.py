"""batch_011 port of 超级趋势追踪止损策略Trend-Following-Strategy-with-Stop-Loss.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2024-01-04 00:00:00\nend: 2024-01-11 00:00:00\nperiod: 5m\nbasePeriod: 1m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("Supertrend Strategy", overlay=true, default_qty_type=strategy.percent_of_equity)\n\n// Stop loss and profit amount\nstop_loss = input(300, title="Stop Loss Amount")\nprofit = input (800, title="Profit Amount")\n\natrPeriod = input(10, "ATR Length")\nfactor = input.float(3.0, "Factor", step = 0.01)\n\n[_, direction] = ta.supertrend(factor, atrPeriod)\n\nlong_condition = ta.change(direction) <0\nshort_condition = ta.change(direction) >0\nlong_condition_1= (long_condition)?1:0\nshort_condition_2 = (short_condition)?1:0\n\nstop_price_long = ta.valuewhen(long_condition, low[0]-stop_loss,0)\nprofit_price_long = ta.valuewhen(long_condition, high[0]+profit,0)\nstop_price_short = ta.valuewhen(short_condition, high[0]+stop_loss,0)\nprofit_price_short = ta.valuewhen(short_condition, low[0]-profit,0)\n\nif (long_condition)\n    strategy.entry("Michael3 Long Entry Id", strategy.long)\n\nif (short_condition)\n    strategy.entry("Michael3 Short Entry Id", strategy.short)\n\n\nif (strategy.position_size>0)\n    strategy.exit("exit_long",from_entry="Michael3 Long Entry Id",limit=profit_price_long,stop=stop_price_long)\n\nif (strategy.position_size<0)\n    strategy.exit("exit_short",from_entry="Michael3 Short Entry Id",limit=profit_price_short,stop=stop_price_short)    \n    \n\n\n//plot(strategy.equity, title="equity", color=color.red, linewidth=2, style=plot.style_areabr)'

class SM7D8C88FB8A9875D1(PinePortBase, IStrategy):
    source_id = "SM_7d8c88fb8a9875d1"
    source_file = '超级趋势追踪止损策略Trend-Following-Strategy-with-Stop-Loss.md'
    timeframe = '5m'
    can_short = True
    source_defaults = {'stop_loss': 300, 'profit': 800, 'atrPeriod': 10, 'factor': 3.0}
    source_qty_type = 'percent_of_equity'
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
