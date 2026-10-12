"""batch_011 port of 趋势偏离指标K线结合移动平均线波浪策略Trend-Deviation-Index-with-Moving-Average-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-10-29 00:00:00\nend: 2023-11-05 00:00:00\nperiod: 30m\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=4\nstrategy(title="TSIHULLBOT", shorttitle="TSICCIHULL", default_qty_type=strategy.percent_of_equity, default_qty_value=100)\nlong = input(title="Long Length", type=input.integer, defval=50)\nshort = input(title="Short Length", type=input.integer, defval=50)\nsignal = input(title="Signal Length", type=input.integer, defval=7)\nprice = input(title="Source",type=input.source,defval=open)\nlineupper = input(title="Upper Line", type=input.integer, defval=250)\nlinelower = input(title="Lower Line", type=input.integer, defval=-250)\ndouble_smooth(price, long, short) =>\n    fist_smooth = hma(price, long)\n    hma(fist_smooth, short)\npc = change(price)\ndouble_smoothed_pc = double_smooth(pc, long, short)\ndouble_smoothed_abs_pc = double_smooth(abs(pc), long, short)\ntsi_value = (100 * (double_smoothed_pc / double_smoothed_abs_pc))*5\ntsihmaline=(hma(tsi_value,signal))*5\nclr = tsihmaline < tsi_value ? color.red : color.lime\nclr2 = tsi_value < tsi_value[1] ? color.red : color.lime\ni1=plot(lineupper+3, color=color.black, linewidth=3)\ni2=plot(linelower+3, color=color.black, linewidth=3)\ni3=plot(lineupper, color=clr)\ni4=plot(linelower, color=clr)\ntrendv=tsihmaline/5.6\nplot(trendv, linewidth=7,  color=color.black)\nplot(trendv, linewidth=4,  color=color.yellow)\nj1=plot(tsi_value, linewidth=5, color=color.black)\nj2=plot(tsi_value[1], linewidth=5, color=color.black)\nj3=plot(tsi_value, color=clr2)\nj4=plot(tsi_value[1], color=clr2)\nfill(i3,i4,color=clr,transp=90)\nfill(j3,j4,color=clr2,transp=15)\nlongCondition = tsihmaline>tsihmaline[1] and price>price[1]\nif (longCondition)\n    strategy.entry("Buy ⤴️", strategy.long)\nshortCondition = tsihmaline<tsihmaline[1] and price<price[1]\nif (shortCondition)\n    strategy.entry("Sell ⤵️", strategy.short)'

class SM23FF1121709B774A(PinePortBase, IStrategy):
    source_id = "SM_23ff1121709b774a"
    source_file = '趋势偏离指标K线结合移动平均线波浪策略Trend-Deviation-Index-with-Moving-Average-Strategy.md'
    timeframe = '30m'
    can_short = True
    source_defaults = {'long': 50, 'short': 50, 'signal': 7, 'lineupper': 250, 'linelower': -250}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 100
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = False
    source_risk_flags = ['func']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
