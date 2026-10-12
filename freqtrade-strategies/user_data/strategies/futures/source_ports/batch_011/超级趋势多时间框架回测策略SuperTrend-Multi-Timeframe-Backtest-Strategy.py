"""batch_011 port of 超级趋势多时间框架回测策略SuperTrend-Multi-Timeframe-Backtest-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-11-27 00:00:00\nend: 2023-12-04 00:00:00\nperiod: 45m\nbasePeriod: 5m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=4\n\n//@Gurjant_Singh IISMA-Indian Institute of stock Market Analysis \n\nstrategy("SupterTrend ", overlay=true, initial_capital=100000, default_qty_type=strategy.percent_of_equity, default_qty_value=300, calc_on_order_fills=false, calc_on_every_tick=false)\n\n\n\n\nmult = input(type=input.float, defval=3)\nlen = input(type=input.integer, defval=5)\n[superTrend, dir] = supertrend(mult, len)\n\n\n\nplot(superTrend)\n\nintrady = input(false, "Do you want to exit intrday position", type = input.bool)\n\nIntraDay_SquareOff = minute >= 45 and hour >= 14\n\n\n\nbuy = close > superTrend\n\nsell = close < superTrend\n\nif buy\n    strategy.entry("Buy", true)\n    \nif sell\n    strategy.entry("sell", false)\n\nif intrady and IntraDay_SquareOff\n    strategy.close("buy")\n    strategy.close("sell")\n\n\n\n\n'

class SM39AAD8765637370D(PinePortBase, IStrategy):
    source_id = "SM_39aad8765637370d"
    source_file = '超级趋势多时间框架回测策略SuperTrend-Multi-Timeframe-Backtest-Strategy.md'
    timeframe = '45m'
    can_short = False
    source_defaults = {'mult': 3, 'len': 5, 'intrady': False}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 300
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 100000
    source_reproduce_stops = False
    source_risk_flags = ['tuple']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
