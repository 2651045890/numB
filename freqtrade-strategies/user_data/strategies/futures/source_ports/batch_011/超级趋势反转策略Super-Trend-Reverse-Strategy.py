"""batch_011 port of 超级趋势反转策略Super-Trend-Reverse-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2022-12-21 00:00:00\nend: 2023-12-27 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=3\n\nstrategy(title = "Super-Trend-reverse Strategy", overlay = true)\n\n// Super Trend Strategy\nFactor=input(2,type =float, minval=1,maxval = 100)\nPd=10 //input(10,minval=1,maxval = 100)\n\n// ST1\n\nUP=hlc3-(Factor*atr(Pd))\n\nDOWN=hlc3+(Factor*atr(Pd))\n\n// ST1.2\n\nTrendUp=na\nTrendUp:=close[1]>TrendUp[1]? max(UP,TrendUp[1]) : UP\n\nTrendDown=na\nTrendDown:=close[1]<TrendDown[1]? min(DOWN,TrendDown[1]) : UP\n\n\nTrend = na\nTsl = na\n\n\nTrend := close[1] > TrendDown[1] ? 1: close[1] < TrendUp[1]? -1: nz(Trend[1],1)\nTsl := Trend==1 ? TrendUp: TrendDown\n\n\n/////////////// Functions for Reverse //////////////////////////////\n\nIF(input) => (exp(2*input)-1) / (exp(2*input)+1)\n\n//////////////////////// RSI REVERSE /////////////////////\n\nRSI_main = input(14, title="RSI Main Period")\nRSI_smooth = input(5, title="RSI Smooth Period")\n\n//Functions\nRVS(input) => (exp(2*input)-1) / (exp(2*input)+1)\n\n//RSI Calculation\nraw_RSI=0.1*(rsi(close,RSI_main)-50)\nwma_RSI=wma(raw_RSI,RSI_smooth)\nRVS_RSI = RVS(wma_RSI)\n\n\nthreshold1 = RVS_RSI < 0.8? 1 : 0\nthreshold2 = -0.8\n\n\n\n\nRSIbuy = (RVS_RSI<threshold2)\nRSIsell = (RVS_RSI > threshold1)\n\n\n\n////////////////////// RSI REVERSE ///////////////////////\n\n// Conditions\n\n\n\nlongCond = na\nshortCond = na\nlongCond :=  RSIbuy and crossover(close, Tsl)  \nshortCond :=  RSIsell and crossunder(close, Tsl) \n\n\nyearfrom = input(2018)\nyearuntil =input(2039)\nmonthfrom =input(6)\nmonthuntil =input(12)\ndayfrom=input(1)\ndayuntil=input(31)\n\n\n\nif (  longCond  and   year >= yearfrom and year <= yearuntil and month>=monthfrom and month <=monthuntil and dayofmonth>=dayfrom and dayofmonth < dayuntil) \n    strategy.entry("BUY", strategy.long, stop=close, oca_name="TREND",  comment="BUY")\n    \nelse\n    strategy.cancel(id="BUY")\n\n\nif ( shortCond and  year >= yearfrom and year <= yearuntil and month>=monthfrom and month <=monthuntil and dayofmonth>=dayfrom and dayofmonth < dayuntil ) \n\n    strategy.close("BUY")\n\n\n\n\n\n'

class SM657728DA36B1DBF3(PinePortBase, IStrategy):
    source_id = "SM_657728da36b1dbf3"
    source_file = '超级趋势反转策略Super-Trend-Reverse-Strategy.md'
    timeframe = '1d'
    can_short = False
    source_defaults = {'Factor': 2, 'RSI_main': 14, 'RSI_smooth': 5, 'yearfrom': 2018, 'yearuntil': 2039, 'monthfrom': 6, 'monthuntil': 12, 'dayfrom': 1, 'dayuntil': 31}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = False
    source_risk_flags = ['func', 'entry_price_order', 'var_state']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
