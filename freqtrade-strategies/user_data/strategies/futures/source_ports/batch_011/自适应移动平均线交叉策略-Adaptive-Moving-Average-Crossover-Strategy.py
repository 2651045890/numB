"""batch_011 port of 自适应移动平均线交叉策略-Adaptive-Moving-Average-Crossover-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-07-23 00:00:00\nend: 2024-07-28 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("MA Cross Over Strategy", overlay=true, initial_capital=10000, process_orders_on_close=true, default_qty_type=strategy.percent_of_equity, default_qty_value=100)\n\n// 参数：EMA的周期\nema_length = input.int(120, title="MA Length")\ntypeMA = input(title = "Method", defval = "SMA", options=["SMA", "EMA", "SMMA (RMA)", "WMA", "VWMA"], group="Smoothing")\n\nma(source, length, type) =>\n    switch type\n        "SMA" => ta.sma(source, length)\n        "EMA" => ta.ema(source, length)\n        "SMMA (RMA)" => ta.rma(source, length)\n        "WMA" => ta.wma(source, length)\n        "VWMA" => ta.vwma(source, length)\n// 计算EMA\nma_value = ma(close, ema_length, typeMA)\n\n// === INPUT BACKTEST RANGE ===\n// i_from = input.time(defval = timestamp("01 Jan 2020 00:00 +0000"), title = "From")\n// i_thru = input.time(defval = timestamp("01 Aug 2024 00:00 +0000"), title = "Thru")\n\n// === INPUT SHOW PLOT ===\ni_show = input     (defval = true, title = "Show Date Range")\n\n// === FUNCTION EXAMPLE ===\ndate() => true\n\n// 生成交易信号\nvar int position = na\ncv = ta.crossover(close, ma_value)\ncu = ta.crossunder(close, ma_value)\nif date() and cv\n    position := 1\nelse if date() and cu\n    position := -1\n\n// 显示MA\nplot(ma_value, title=\'MA\', color=color.blue, linewidth=2)\n\n\n// 策略实现\nif (position == 1)\n    strategy.entry("Buy", strategy.long)\nif (position == -1)\n    strategy.close("Buy")'

class SM55325DC274D15674(PinePortBase, IStrategy):
    source_id = "SM_55325dc274d15674"
    source_file = '自适应移动平均线交叉策略-Adaptive-Moving-Average-Crossover-Strategy.md'
    timeframe = '1d'
    can_short = False
    source_defaults = {'ema_length': 120, 'typeMA': 'SMA', 'i_show': True}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 100
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 10000
    source_reproduce_stops = False
    source_risk_flags = ['func', 'switch', 'var_state']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
