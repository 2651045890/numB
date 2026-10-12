"""batch_012 port of 高斯波浪预测策略The-Gauss-Wave-Forecasting-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-01-15 00:00:00\nend: 2024-01-21 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=2\nstrategy("Gaussbot v1.0", overlay=true)\n\np = input(20, minval=1, title="Length")\nprice = input(open, title="Source")\n\npi=3.1415926535\n\n\nw=2*pi/p\nbeta = (1 - cos(w))/(pow(1.414,2.0/3) - 1)\nalfa = -beta + sqrt(beta*beta + 2*beta)\nret=  pow(alfa,4)*price+4*(1-alfa)*nz(ret[1])-6*pow(1-alfa,2)*nz(ret[2])+4*pow(1-alfa,3)*nz(ret[3])-pow(1-alfa,4)*nz(ret[4])\nret2 = pow(alfa,4)*ret+4*(1-alfa)*nz(ret2[1])-6*pow(1-alfa,2)*nz(ret2[2])+4*pow(1-alfa,3)*nz(ret2[3])-pow(1-alfa,4)*nz(ret2[4])\nret3 = pow(alfa,4)*ret2+4*(1-alfa)*nz(ret3[1])-6*pow(1-alfa,2)*nz(ret3[2])+4*pow(1-alfa,3)*nz(ret3[3])-pow(1-alfa,4)*nz(ret3[4])\nret4 = 3*ret-3*ret2+ret3\n\n\ndiff2 = nz(ret[1]) - nz(ret[2]) - (nz(ret[2]) - nz(ret[3]) )  \ndiff22 = nz(ret2[1]) - nz(ret2[2]) - (nz(ret2[2]) - nz(ret2[3]) ) \ndiff23 = nz(ret3[1]) - nz(ret3[2]) - (nz(ret3[2]) - nz(ret3[3]) )  \ndiff24 = nz(ret4[1]) - nz(ret4[2]) - (nz(ret4[2]) - nz(ret4[3]) )  \n\n\nlongCondition =    price[0] - ret4[1]  > 0\nshortCondition =  price[0] - ret4[1] < 0\n\nif(longCondition and shortCondition)\n    longCondition = longCondition[1]\n    shortCondition = shortCondition[1]\nif(longCondition==false and shortCondition==false)\n    longCondition = longCondition[1]\n    shortCondition = shortCondition[1]\n\n\n\nif (longCondition==true and shortCondition == false) \n    strategy.entry("Gaussbot Long", strategy.long )\nif (longCondition==false and shortCondition == true)\n    strategy.entry("Gaussbot Short", strategy.short)\n\n\n'

class SMTheGaussWaveForecastingStrategy57f99f(PinePortBase, IStrategy):
    source_id = "SM_57f99f741255c54c"
    source_file = '高斯波浪预测策略The-Gauss-Wave-Forecasting-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'p': 20, 'price': 'open'}
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
