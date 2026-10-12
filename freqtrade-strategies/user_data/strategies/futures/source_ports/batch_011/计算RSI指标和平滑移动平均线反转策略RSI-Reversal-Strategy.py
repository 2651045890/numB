"""batch_011 port of 计算RSI指标和平滑移动平均线反转策略RSI-Reversal-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-01-12 00:00:00\nend: 2024-01-18 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=3\nstrategy(title="RSI Reverse", shorttitle="RSI Reverse")\n\n\nRSI_main = input(14, title="RSI Main Period")\nRSI_smooth = input(5, title="RSI Smooth Period")\n\n//Functions\nRVS(input) => (exp(2*input)-1) / (exp(2*input)+1)\n\n//RSI Calculation\nraw_RSI=0.1*(rsi(close,RSI_main)-50)\nwma_RSI=wma(raw_RSI,RSI_smooth)\nRVS_RSI = RVS(wma_RSI)\n\n\nthreshold1 = RVS_RSI < 0.8? 1 : 0\nthreshold2 = -0.8\n\n\nplot(RVS_RSI,color=red)\nplot(threshold1,color=blue)\nplot(threshold2,color=blue)\n\nbuycon = crossover(RVS_RSI,threshold2)\nsellcon = crossunder(RVS_RSI , threshold1)\n\nmonthfrom =input(6)\nmonthuntil =input(12)\ndayfrom=input(1)\ndayuntil=input(31)\n\n\nif (  buycon  ) \n    strategy.entry("BUY", strategy.long, stop=close, oca_name="TREND", comment="BUY")\n    \nelse\n    strategy.cancel(id="BUY")\n\n\nif ( sellcon) \n\n    strategy.close("BUY")\n    \n\n\n\n'

class SM318F658BF14E2786(PinePortBase, IStrategy):
    source_id = "SM_318f658bf14e2786"
    source_file = '计算RSI指标和平滑移动平均线反转策略RSI-Reversal-Strategy.md'
    timeframe = '1d'
    can_short = False
    source_defaults = {'RSI_main': 14, 'RSI_smooth': 5, 'monthfrom': 6, 'monthuntil': 12, 'dayfrom': 1, 'dayuntil': 31}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = False
    source_risk_flags = ['func', 'entry_price_order']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
