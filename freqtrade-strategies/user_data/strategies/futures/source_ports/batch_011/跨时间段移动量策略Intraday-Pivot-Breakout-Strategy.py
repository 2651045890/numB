"""batch_011 port of 跨时间段移动量策略Intraday-Pivot-Breakout-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2022-10-27 00:00:00\nend: 2023-11-02 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//   ____________        _________           _____________\n//  |____________|      ||________|          ||__________|\n//       ||             ||        ||         ||\n//       ||             ||________||         ||\n//       ||     H E     ||________   U L L   ||       H A R T I S T\n//       ||             ||        ||         ||\n//       ||             ||________||         ||__________\n//       ||             ||________|          ||__________|\n  \n//@version=5\n// strategy("PIVOT STRATEGY [5MIN TF]",overlay=true ,commission_type = strategy.cash, commission_value = 30 , slippage = 2, default_qty_value = 60, currency = currency.NONE, pyramiding = 0)\nleftbars = input(defval = 10)\nrightbars = input(defval = 15)\n\n// ═══════════════════════════ //\n// ——————————> INPUTS <——————— //\n// ═══════════════════════════ //\n\nEMA1 = input.int(title=\'PRICE CROSS EMA\', defval = 150, minval = 10 ,maxval = 400)\nfactor1 = input.float(title=\'_ATR LONG\',defval = 3.2 , minval = 1 , maxval = 5 , step = 0.1, tooltip = "ATR TRAIL LONG")\nfactor2 = input.float(title=\'_ATR SHORT\',defval = 3.2 , minval = 1 , maxval = 5 , step = 0.1, tooltip = "ATR TRAIL SHORT")\nrisk = input.float(title=\'RISK\',defval = 200 , minval = 1 , maxval = 5000 , step = 50, tooltip = "RISK PER TRADE")\n\nvar initialCapital = strategy.equity\nt = time(timeframe.period, \'0935-1400:1234567\')\ntime_cond = true\n\n// ══════════════════════════════════ //\n// ———————————> EMA DATA <——————————— //\n// ══════════════════════════════════ //\nema1 = ta.ema(close, EMA1)\n\nplot(ema1, color=color.new(color.yellow, 0), style=plot.style_linebr, title=\'ema1\')\n\n// ══════════════════════════════════ //\n// ————————> TRAIL DATA <———————————— //\n// ══════════════════════════════════ //\n// *******Calculate LONG TRAIL data*****\nATR_LO = ta.atr(14)*factor1\n\n// *******Calculate SHORT TRAIL data*****\nATR_SH = ta.atr(14)*factor2\n\nlongStop = close - ATR_LO\nshortStop = close + ATR_SH\n\n// Plot atr data\n//plot(longStop, color=color.new(color.green, 0), style=plot.style_linebr, title=\'Long Trailing Stop\')\n//plot(shortStop , color=color.new(color.red, 0), style=plot.style_linebr, title=\'Short Trailing Stop\')\n\n// ══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════ //\n// ————————————————————————————————————————————————————————> PIVOT DATA <———————————————————————————————————————————————————————————————————————————————————————————————————— //\n// ══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════ //\n\nph = ta.pivothigh(close,leftbars, rightbars)\npl = ta.pivotlow(close,leftbars, rightbars)\n\npvt_condition1 = not na(ph)\n\nupper_price = 0.0\nupper_price := pvt_condition1 ? ph : upper_price[1]\n\npvt_condition2 = not na(pl)\n\nlower_price = 0.0\nlower_price := pvt_condition2 ? pl : lower_price[1]\n\n// Signals\nlong  = ta.crossover(high, upper_price + syminfo.mintick)\nshort = ta.crossunder(low, lower_price - syminfo.mintick)\n\nplot(upper_price, color= close > ema1  ? color.green : na, style=plot.style_line, title=\'PH\')\n\nplot(lower_price,  color= close <  ema1  ? color.red : na, style=plot.style_line, title=\'PL\')\n\n\n// ══════════════════════════════════//\n// ————————> LONG POSITIONS <————————//\n// ══════════════════════════════════//\n//******barinstate.isconfirmed used to avoid repaint in real time*******\n\nif ( long and strategy.opentrades==0 and barstate.isconfirmed and time_cond and close >= ema1 )\n    strategy.entry(id= "Long" ,direction = strategy.long, comment = "B")\n    \n//plot(longStop , color=color.new(color.blue, 0), style=plot.style_linebr, title=\'long Stop\')\n\nif strategy.position_size > 0 \n    strategy.exit("long tsl", "Long" , stop = longStop ,comment=\'S\')\n \n\n// ═════════════════════════════════════//\n// ————————> SHORT POSITIONS <————————— //\n// ═════════════════════════════════════//\nif ( short and strategy.opentrades==0 and barstate.isconfirmed and time_cond and close <= ema1 )\n    strategy.entry(id = "Short" ,direction = strategy.short,  comment = "S") \n\nif strategy.position_size < 0\n    strategy.exit("short tsl", "Short" ,  stop = shortStop ,comment=\'B\')\n\n// ════════════════════════════════════════════════//\n// ————————> CLOSE ALL POSITIONS BY 3PM <————————— //\n// ════════════════════════════════════════════════//\nstrategy.close_all(when = hour == 14 and minute == 55)\n\n// ════════════════════════════════════════//\n// ————————> MAX INTRADAY LOSS  <————————— //\n// ════════════════════════════════════════//\n// strategy.risk.max_intraday_loss(type = strategy.cash, value = risk)\n\n'

class SM4892E3933B155358(PinePortBase, IStrategy):
    source_id = "SM_4892e3933b155358"
    source_file = '跨时间段移动量策略Intraday-Pivot-Breakout-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'leftbars': 10, 'rightbars': 15, 'EMA1': 150, 'factor1': 3.2, 'factor2': 3.2, 'risk': 200}
    source_qty_type = 'fixed'
    source_qty_value = 60
    source_commission_percent = 30
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = True
    source_risk_flags = ['broker_state', 'exit_order', 'var_state', 'timeframe']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
