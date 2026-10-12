"""batch_012 port of 零时滞后-Hull-EMA-组合-趋势跟踪策略Zero-Lag-Hull-EMA-Combo-Trend-Following-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-08-19 00:00:00\nend: 2023-09-18 00:00:00\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=3\n// Zero Lag EMA combined with Hull moving average for smoothing purposes.\n// author: email: sbginter@gmail.com\n\nstrategy("Ujanja", overlay=true)\n\n\n\nPeriod = input(title="Period",defval=30, minval=1)\nS_period=input(title="Smoother Period",defval=176)\nEMA1= ema(close,Period)\nEMA2= ema(EMA1,Period)\nDifference= EMA1 - EMA2\nZeroLagEMA= EMA1 + Difference\n\nn2ma=2*wma(ZeroLagEMA,round(S_period/2))\nnma=wma(ZeroLagEMA,S_period)\ndiff=n2ma-nma\nsqn=round(sqrt(S_period))\n\n\nn2ma1=2*wma(ZeroLagEMA[1],round(S_period/2))\nnma1=wma(ZeroLagEMA[1],S_period)\ndiff1=n2ma1-nma1\nsqn1=round(sqrt(S_period))\n\n\nn1=wma(diff,sqn)\nn2=wma(diff1,sqn)\n\nc=n1>n2?green:red\nma=plot(n1,color=c)\n\n\nlongCondition = n1>n2\nif (longCondition)\n    strategy.entry("Long", strategy.long)\n\nshortCondition = longCondition != true\nif (shortCondition)\n    strategy.entry("Short", strategy.short)\n'

class SMHullEMAZeroLagHullEMAComboTrendFollowingStrategy62f85b(PinePortBase, IStrategy):
    source_id = "SM_62f85b0f181acd02"
    source_file = '零时滞后-Hull-EMA-组合-趋势跟踪策略Zero-Lag-Hull-EMA-Combo-Trend-Following-Strategy.md'
    timeframe = '1h'
    can_short = True
    source_defaults = {'Period': 30, 'S_period': 176}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
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
