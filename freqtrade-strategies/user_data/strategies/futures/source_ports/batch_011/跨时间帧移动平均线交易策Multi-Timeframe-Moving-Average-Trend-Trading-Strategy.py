"""batch_011 port of 跨时间帧移动平均线交易策Multi-Timeframe-Moving-Average-Trend-Trading-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-09-15 00:00:00\nend: 2023-09-22 00:00:00\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=3\n//Cryptocurrency Trading Tools by XMAXPRO\n//ATA\n//Test 1.0v Date  : 10.11.2018\n//\n\nstrategy("MTF+MA", overlay=false, shorttitle="MTF-MA", overlay = true,default_qty_type = strategy.percent_of_equity, default_qty_value = 100, commission_type=strategy.commission.percent,commission_value=0.1,initial_capital=100000)\nsrc = input(title= "Source", defval=close)\nfast = input(title="Input For Fast MA",  defval=21)\nslow = input(title="Input For Slow MA",defval=34)\n//MTF source\nlong = input(title="LONGTERM",  defval="D")\nmid = input(title="MIDTERM",  defval="180")\nshort = input(title="SHORTTERM",  defval="15")\n//MTF Grafikleri\nln = security(syminfo.ticker, long, src)\nmd = security(syminfo.ticker, mid, src)\nsh = security(syminfo.ticker, short, src)\n//0\nlnma = ema(ln,fast) - ema(ln,slow)\nmdma = ema(sh,fast) - ema(md,slow)\nshma = ema(sh,fast) - ema(sh,slow)\n\nplot(lnma,color=green,linewidth=3)\nplot(mdma,color=blue,linewidth=3)\nplot(shma,color=red,linewidth=3)\nplot(0,color=white,linewidth=3)\n\nlongCond = lnma>0 and mdma>0  and shma>0\nshortCond= lnma<0  and mdma<0  and shma <0 \n\n\n\nmonthfrom =input(8)\nmonthuntil =input(12)\ndayfrom=input(1)\ndayuntil=input(31)\nyearfrom=input(2018)\nyearuntil=input(2020)\n\nif (  longCond  ) \n    strategy.entry("LONG", strategy.long, stop=close, oca_name="TREND",  comment="LONG")\n    \nelse\n    strategy.cancel(id="LONG")\n    \n\n\n\nif ( shortCond   ) \n\n    strategy.entry("SHORT", strategy.short,stop=close, oca_name="TREND",  comment="SHORT")\nelse\n    strategy.cancel(id="SHORT")\n'

class SM7CA77A04B79490B8(PinePortBase, IStrategy):
    source_id = "SM_7ca77a04b79490b8"
    source_file = '跨时间帧移动平均线交易策Multi-Timeframe-Moving-Average-Trend-Trading-Strategy.md'
    timeframe = '1h'
    can_short = True
    source_defaults = {'fast': 21, 'slow': 34, 'long': 'D', 'mid': '180', 'short': '15', 'monthfrom': 8, 'monthuntil': 12, 'dayfrom': 1, 'dayuntil': 31, 'yearfrom': 2018, 'yearuntil': 2020}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 100
    source_commission_percent = 0.1
    source_pyramiding = 0
    source_initial_capital = 100000
    source_reproduce_stops = False
    source_risk_flags = ['mtf', 'entry_price_order']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
