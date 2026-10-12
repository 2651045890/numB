"""batch_011 port of 趋势追踪买卖策略Trend-Following-Buy-and-Sell-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2022-10-10 00:00:00\nend: 2023-10-16 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=4\nstrategy("Higher High / Lower Low Strategy", overlay=true)\n\n// Getting inputs\nlongOnly = input(true, title="Long or Short Only")\nuseMACD = input(true, title="Use MACD Filter")\nuseSignal = input(true, title="Use Signal Filter")\n//Filter backtest month and year\nstartMonth = input(10, minval=1, maxval=12, title="Month")\nstartYear = input(2020, minval=2000, maxval=2100, title="Year")\n//Filter funtion inputs\nperiodA = input(20, minval=1, title="Period SMA")\nperiodK = input(5, minval=1, title="Period %K")\nfast_length = input(title="Period Fast", type=input.integer, defval=5)\nslow_length = input(title="Period Slow", type=input.integer, defval=20)\nsignal_length = input(title="Signal Smoothing", type=input.integer, minval = 1, maxval = 50, defval = 30)\n\n//Calculations\nsmoothD = 3 //input(3, minval=1, title="Smooth %D")\nsmoothK = 2 //input(2, minval=1, title="Smooth %K")\nma50 = sma(close, periodA)\nk = sma(stoch(close, high, low, periodK), smoothK) - 50\nd = sma(k, smoothD)\nmacd = ema(close,fast_length) - ema(close,slow_length)\nsignal = ema(macd,signal_length)\nhist = macd - signal\n\nif (not na(k) and not na(d) and not na(macd) and not na(signal) and longOnly and month>=startMonth and year>=startYear)//\tif(k > k[1] and k[2] >= k[1] and (ma50 > ma50[1]) and (not useK or k[1] <= -threshold_k) and (not useMACD or macd > macd[1]) and (not useSignal or signal > signal[1]) and (not useHHLL or close >= high[1]) and (not useD or d <= -threshold_d))\n    if(high[2] >= high[1] and high > high[1] and (ma50 > ma50[1]) and (not useMACD or macd > macd[1]) and (not useSignal or signal > signal[1]))\n\t\tstrategy.order("HH_LE", strategy.long, when=strategy.position_size == 0, comment="HH_LE")\n    if (k < k[1])\n\t\tstrategy.order("HH_SX", strategy.short, when=strategy.position_size != 0, comment="HH_SX")\n\nif (not na(k) and not na(d) and not na(macd) and not na(signal) and not longOnly and month>=startMonth and year>=startYear)\n    if(low[2] <= low[1] and low < low[1] and (ma50 < ma50[1]) and (not useMACD or macd < macd[1]) and (not useSignal or signal < signal[1]))\n\t\tstrategy.order("HH_SE", strategy.short, when=strategy.position_size == 0, comment="HH_SE")\n    if (k > k[1])\n\t\tstrategy.order("HH_LX", strategy.long, when=strategy.position_size != 0, comment="HH_LX")\n\n//plot(strategy.equity, title="equity", color=color.red, linewidth=2, style=plot.style_areabr)\n'

class SM376B67E3311E44BF(PinePortBase, IStrategy):
    source_id = "SM_376b67e3311e44bf"
    source_file = '趋势追踪买卖策略Trend-Following-Buy-and-Sell-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'longOnly': True, 'useMACD': True, 'useSignal': True, 'startMonth': 10, 'startYear': 2020, 'periodA': 20, 'periodK': 5, 'fast_length': 5, 'slow_length': 20, 'signal_length': 30}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = False
    source_risk_flags = ['broker_state']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
