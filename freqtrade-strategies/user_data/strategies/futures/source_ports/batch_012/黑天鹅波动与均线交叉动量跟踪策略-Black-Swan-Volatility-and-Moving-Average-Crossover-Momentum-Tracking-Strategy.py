"""batch_012 port of 黑天鹅波动与均线交叉动量跟踪策略-Black-Swan-Volatility-and-Moving-Average-Crossover-Momentum-Tracking-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2024-12-05 00:00:00\nend: 2024-12-12 00:00:00\nperiod: 45m\nbasePeriod: 45m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\n\n//黑天鹅警报器，作者（）：道格拉斯机器人\n//适合1分钟-3分钟的k线，发生波动超过百分之二时，自动报警\nstrategy(\'黑天鹅警报\', overlay=true, initial_capital=10000, currency=\'USD\', default_qty_type=strategy.percent_of_equity, default_qty_value=100, commission_type=strategy.commission.percent, commission_value=0.075, pyramiding=3)\n//-------------------------------------------\n//-------------------------------------------\ntimecondition = timeframe.period == \'480\' or timeframe.period == \'240\' or timeframe.period == \'D\' or timeframe.period == \'720\'\n// Make input options that configure backtest date range\nstartDate = input.int(title=\'Start Date\', defval=1, minval=1, maxval=31)\nstartMonth = input.int(title=\'Start Month\', defval=11, minval=1, maxval=12)\nstartYear = input.int(title=\'Start Year\', defval=2018, minval=1800, maxval=2100)\nendDate = input.int(title=\'End Date\', defval=1, minval=1, maxval=31)\nendMonth = input.int(title=\'End Month\', defval=11, minval=1, maxval=12)\nendYear = input.int(title=\'End Year\', defval=2031, minval=1800, maxval=2100)\n// Look if the close time of the current bar\n// falls inside the date range\ninDateRange = time >= timestamp(syminfo.timezone, startYear, startMonth, startDate, 0, 0) and time < timestamp(syminfo.timezone, endYear, endMonth, endDate, 0, 0)\n\n\n\n// Inputs\na = input(1, title=\'Key Vaule. \\\'This changes the sensitivity\\\'\')\nc = input(10, title=\'ATR Period\')\nh = input(false, title=\'Signals from Heikin Ashi Candles\')\n\n\nma60 = ta.sma(close, 60)\nema144 = ta.ema(close, 144)\n\nema169 = ta.ema(close, 169)\nma20 = ta.sma(close, 20)\n\n\nplot(ema144, color=color.new(color.yellow, 0), title=\'144\')\nplot(ema169, color=color.new(color.orange, 0), title=\'169\')\n\n\nheitiane = close - open\nheitiane := math.abs(heitiane)\nheitiane /= close\n\nif inDateRange and heitiane > 0.0191 and close < open  //  and close>f3\n    strategy.entry(\'botsell20\', strategy.short, comment=\'黑天鹅追空\' + str.tostring(heitiane))\n\nif ta.crossover(ema144, ema169)\n    strategy.close(\'botsell20\', comment=\'平空\')\nif inDateRange and heitiane > 0.0191 and close > open  //  and close>f3\n    strategy.entry(\'botbuy20\', strategy.long, comment=\'白天鹅追多\' + str.tostring(heitiane))\n\nif ta.crossunder(ema144, ema169)\n    strategy.close(\'botbuy20\', comment=\'平多\')\n\n\n\n'

class SMBlackSwanVolatilityandMovingAverageCrossoverMomentumTra013730(PinePortBase, IStrategy):
    source_id = "SM_0137300d6c8f2ec8"
    source_file = '黑天鹅波动与均线交叉动量跟踪策略-Black-Swan-Volatility-and-Moving-Average-Crossover-Momentum-Tracking-Strategy.md'
    timeframe = '45m'
    can_short = True
    source_defaults = {'startDate': 1, 'startMonth': 11, 'startYear': 2018, 'endDate': 1, 'endMonth': 11, 'endYear': 2031, 'a': 1, 'c': 10, 'h': False}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 100
    source_commission_percent = 0.075
    source_pyramiding = 3
    source_initial_capital = 10000
    source_reproduce_stops = False
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_012 md and exposed through the same PinePortBase interface used by batch_001.']

    def pine_indicators(self, dataframe, params):
        # Runtime evaluates the source against the complete OHLCV frame.
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch012Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
