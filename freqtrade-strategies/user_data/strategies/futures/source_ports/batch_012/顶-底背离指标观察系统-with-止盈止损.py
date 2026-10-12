"""batch_012 port of 顶-底背离指标观察系统-with-止盈止损.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2022-03-01 00:00:00\nend: 2023-02-28 23:59:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\nargs: [["v_input_1",99]]\n*/\n\n//@version=5\nstrategy("顶/底背离指标观察系统 with 止盈止损", overlay=true)\n\n// 输入止损百分比和止盈百分比，这里分别设置为1%\nstop_loss_pct = input(title="止损百分比", type=input.float, defval=1.0, step=0.1)\ntake_profit_pct = input(title="止盈百分比", type=input.float, defval=1.0, step=0.1)\n\n// 计算MACD指标\nfastline = ta.ema(close,12)  \nslowline = ta.ema(close,26)\ndiff = fastline - slowline \ndea = ta.ema(diff,9) \nmacd = 2*(diff - dea)\n\n// 判断顶背离和底背离信号\ntop_diver = ta.crossunder(macd,0) and close[1] > close\nbot_diver = ta.crossover(macd,0) and close[1] < close\nplotchar(top_diver, char=\'顶背离\', location = location.abovebar, size = size.normal, overlay=true)\nplotchar(bot_diver, char=\'底背离\', location = location.belowbar, size = size.normal, overlay=true)\n// 判断是否需要开仓\nif top_diver and strategy.position_size>= 0\n    strategy.entry("top_diver_short", strategy.short, comment="顶背离开多")\nelse if bot_diver and strategy.position_size <=0\n    strategy.entry("bot_diver_long", strategy.long, comment="底背离开空")\n// 计算止盈止损价格\n//多仓止损\nlong_stop_price = strategy.position_avg_price * (1 - stop_loss_pct / 100)\n//多仓止盈\nlong_take_profit_price = strategy.position_avg_price * (1 + take_profit_pct / 100)\n// 空仓止损\nshort_stop_price = (strategy.position_avg_price) * (1 + stop_loss_pct / 100)\n// 空仓止盈\nshort_take_profit_price =(strategy.position_avg_price) * (1 - take_profit_pct / 100)\n// 判断是否需要平仓\nif strategy.position_size > 0\n    // 多仓止损\n    strategy.exit("long_stop","bot_diver_long", stop=long_stop_price, qty_percent=100)\n    // 多仓止盈\n    strategy.exit("long_tp", "bot_diver_long", limit=long_take_profit_price, qty_percent=100)\nelse if strategy.position_size < 0\n    strategy.exit("short_stop", "top_diver_short", stop=short_stop_price, qty_percent=100)\n    strategy.exit("short_tp", "top_diver_short", limit=short_take_profit_price, qty_percent=100)\n\n\n'

class SMwithe97ea1(PinePortBase, IStrategy):
    source_id = "SM_e97ea1ea49ae5cf2"
    source_file = '顶-底背离指标观察系统-with-止盈止损.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'stop_loss_pct': 1.0, 'take_profit_pct': 1.0}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
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
