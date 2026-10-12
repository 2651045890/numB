"""batch_011 port of 超越移动止损盈利策略Supertrend-Moving-Stop-Loss-Take-Profit-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-01-01 00:00:00\nend: 2024-01-07 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("ST Michael Moving TP", overlay=true, default_qty_type=strategy.percent_of_equity, default_qty_value=15)\n\n// Stop loss and profit amount\nstop_loss = input(1500, title="Stop Loss Amount")\nprofit = input (15000, title="Profit Amount")\nLongTrailProfit = input (0.91, title = "Long Trailing Profit Taking")\nShortTrailProfit = input (1.01, title = "Short Trailing Profit Taking")\n\natrPeriod = input(10, "ATR Length")\nfactor = input.float(3.0, "Factor", step = 0.01)\n\n[_, direction] = ta.supertrend(factor, atrPeriod)\n\nlong_condition = ta.change(direction) <0\nshort_condition = ta.change(direction) >0\n\n\nstop_price_long = ta.valuewhen(long_condition, low[0]-stop_loss,0)\nprofit_price_long = ta.valuewhen(long_condition, high[0]+profit,0)\nstop_price_short = ta.valuewhen(short_condition, high[0]+stop_loss,0)\nprofit_price_short = ta.valuewhen(short_condition, low[0]-profit,0)\n\natr=ta.atr(10)\n\nintrade_long = strategy.position_size > 0\nintrade_short = strategy.position_size < 0\nexitConditionLong = (close < (close[1]*LongTrailProfit)) \nexitConditionShort = (close > (close[1]*ShortTrailProfit))\n\nif (long_condition)\n    strategy.entry("Long3", strategy.long)\nif (intrade_long and exitConditionLong)\n    strategy.close("Long3")\n\nif (short_condition)\n    strategy.entry("Short3", strategy.short)\nif (intrade_short and exitConditionShort)\n    strategy.close ("Short3")\n\nif (strategy.position_size>0)\n    strategy.exit("exit_long",from_entry="Long3",limit=profit_price_long,stop=stop_price_long)\n\nif (strategy.position_size<0)\n    strategy.exit("exit_short",from_entry="Short3",limit=profit_price_short,stop=stop_price_short)    '

class SM56FDB884F5F400DE(PinePortBase, IStrategy):
    source_id = "SM_56fdb884f5f400de"
    source_file = '超越移动止损盈利策略Supertrend-Moving-Stop-Loss-Take-Profit-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'stop_loss': 1500, 'profit': 15000, 'LongTrailProfit': 0.91, 'ShortTrailProfit': 1.01, 'atrPeriod': 10, 'factor': 3.0}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 15
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
