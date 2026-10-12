"""batch_012 port of 金叉死叉双MA策略Double-Moving-Average-Crossover-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-12-01 00:00:00\nend: 2023-12-31 23:59:59\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("Cross 2 Moving Average Strategy", shorttitle="2MA Cross", overlay=true)\n\n// User-defined input for moving averages\nlong_period = input(20, title="Long Period")\nshort_period = input(5, title="Short Period")\ntype_ma = input.string("SMA", title = "MA type", options = ["SMA", "EMA"])\n\n// Calculating moving averages\nlong_ma = ta.sma(close, long_period)\nshort_ma = ta.sma(close, short_period)\n\n// Plot moving averages\nplot(long_ma, title="Long Moving Average", color=color.red)\nplot(short_ma, title="Short Moving Average", color=color.green)\n\n// Strategy logic for crossing of moving averages\nlongCondition = ta.crossover(short_ma, long_ma)\nshortCondition = ta.crossunder(short_ma, long_ma)\n\n// Entry orders\nif (longCondition)\n    strategy.entry("Long", strategy.long)\n\nif (shortCondition)\n    strategy.entry("Short", strategy.short)\n\n// Optional: Add stop loss and take profit\nstop_loss_perc = input(1, title="Stop Loss (%)") / 100\ntake_profit_perc = input(2, title="Take Profit (%)") / 100\n\nstrategy.exit("Exit Long", from_entry="Long", stop=close*(1-stop_loss_perc), limit=close*(1+take_profit_perc))\nstrategy.exit("Exit Short", from_entry="Short", stop=close*(1+stop_loss_perc), limit=close*(1-take_profit_perc))\n\n'

class SMMADoubleMovingAverageCrossoverStrategy19adbf(PinePortBase, IStrategy):
    source_id = "SM_19adbfcd5fab89fc"
    source_file = '金叉死叉双MA策略Double-Moving-Average-Crossover-Strategy.md'
    timeframe = '1h'
    can_short = True
    source_defaults = {'long_period': 20, 'short_period': 5, 'type_ma': 'SMA'}
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
