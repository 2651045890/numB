"""batch_011 port of 蜡烛包裹RSI交易策略Engulfing-Candle-RSI-Trading-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-01-29 00:00:00\nend: 2024-02-04 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=4\nstrategy("EngulfingCandle Strategy", overlay=true)\n\n// Your existing definitions\nbullishCandle=close >= open[1] and close[1] < open[1]\nbearishCandle=close <= open[1] and close[1] > open[1]\n\n// RSI Definitions\nrsiSource=input(close, title="rsiSource")\nrsiLenghth=input(14, title="rsi length", type=input.integer)\nrsiOverBought=input(70, title="rsi overbought level", type=input.integer)\nrsiOverSold=input(30, title="rsi over sold level", type=input.integer)\n\nrsiValue=rsi(rsiSource, rsiLenghth)\nisRSIOB=rsiValue >= rsiOverBought\nisRSIOS=rsiValue <= rsiOverSold\n\n// Trade Signal\ntradeSignal=((isRSIOS or isRSIOS[1] or isRSIOS[2]) and bullishCandle ) or ((isRSIOB or isRSIOB[1] or isRSIOB[2]) and bearishCandle)\n\n// Stop Loss and Take Profit Inputs\nsl_pips = input(20, title="Stop Loss (in pips)")\ntp_pips = input(40, title="Take Profit (in pips)")\n\n// Calculating Stop Loss and Take Profit Prices\nlong_sl = close - syminfo.mintick * sl_pips\nlong_tp = close + syminfo.mintick * tp_pips\nshort_sl = close + syminfo.mintick * sl_pips\nshort_tp = close - syminfo.mintick * tp_pips\n\n// Entering and Exiting Trades\nif (tradeSignal and bullishCandle)\n    strategy.entry("Long", strategy.long)\n    strategy.exit("Exit Long", "Long", stop=long_sl, limit=long_tp)\n    \nif (tradeSignal and bearishCandle)\n    strategy.entry("Short", strategy.short)\n    strategy.exit("Exit Short", "Short", stop=short_sl, limit=short_tp)\n\n// Plotting\nplotshape(tradeSignal and bullishCandle, title="Bullish", location=location.belowbar, color=color.green, style=shape.triangleup, text="Buy")\nplotshape(tradeSignal and bearishCandle, title="Bearish", location=location.abovebar, color=color.red, style=shape.triangledown, text="Sell")\n'

class SMB1B4746774935284(PinePortBase, IStrategy):
    source_id = "SM_b1b4746774935284"
    source_file = '蜡烛包裹RSI交易策略Engulfing-Candle-RSI-Trading-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'rsiLenghth': 14, 'rsiOverBought': 70, 'rsiOverSold': 30, 'sl_pips': 20, 'tp_pips': 40}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = True
    source_risk_flags = ['exit_order']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
