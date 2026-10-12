"""batch_011 port of 趋势动量跟踪策略Momentum-Tracking-Strategy-Based-on-Indicator-Integration.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-10-09 00:00:00\nend: 2023-10-16 00:00:00\nperiod: 1m\nbasePeriod: 1m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=2\nstrategy("Indicator Integrator Strat",default_qty_type = strategy.percent_of_equity, default_qty_value = 100,currency="USD",initial_capital=100, overlay=true)\n\nl = input(defval=170,title="Length for indicator")\ns = input(title="Length of summation",defval=29)\na= sma(close,l)\nr=roc(close,l)\nk=close-a\nsum = 0\nfor i = 0 to s\n    sum := sum + k[i]\nplot(a,color=yellow,linewidth=2,transp=0)\n//bc =  iff( sum > 0, white, teal)\n//plot(sum,color=bc, transp=20, linewidth=3,style=columns)\n//plot(sma(sum,3),color=white)\n//hline(0)\n\ninpTakeProfit = input(defval = 0, title = "Take Profit", minval = 0)\ninpStopLoss = input(defval = 0, title = "Stop Loss", minval = 0)\ninpTrailStop = input(defval = 0, title = "Trailing Stop Loss", minval = 0)\ninpTrailOffset = input(defval = 0, title = "Trailing Stop Loss Offset", minval = 0)\nuseTakeProfit = inpTakeProfit >= 1 ? inpTakeProfit : na\nuseStopLoss = inpStopLoss >= 1 ? inpStopLoss : na\nuseTrailStop = inpTrailStop >= 1 ? inpTrailStop : na\nuseTrailOffset = inpTrailOffset >= 1 ? inpTrailOffset : na\n\n\nlongCondition = sum>0\nexitlong = sum<0\n\nshortCondition = sum<0\nexitshort = sum>0\n\nstrategy.entry(id = "Long", long=true, when = longCondition)\nstrategy.close(id = "Long", when = exitlong)\nstrategy.exit("Exit Long", from_entry = "Long", profit = useTakeProfit, loss = useStopLoss, trail_points = useTrailStop, trail_offset = useTrailOffset, when=exitlong)\n\nstrategy.entry(id = "Short", long=false, when = shortCondition)\nstrategy.close(id = "Short", when = exitshort)\nstrategy.exit("Exit Short", from_entry = "Short", profit = useTakeProfit, loss = useStopLoss, trail_points = useTrailStop, trail_offset = useTrailOffset, when=exitshort)'

class SM4465EB2ECD09B0B3(PinePortBase, IStrategy):
    source_id = "SM_4465eb2ecd09b0b3"
    source_file = '趋势动量跟踪策略Momentum-Tracking-Strategy-Based-on-Indicator-Integration.md'
    timeframe = '1m'
    can_short = False
    source_defaults = {'l': 170, 's': 29, 'inpTakeProfit': 0, 'inpStopLoss': 0, 'inpTrailStop': 0, 'inpTrailOffset': 0}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 100
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 100
    source_reproduce_stops = True
    source_risk_flags = ['loop', 'exit_order', 'var_state']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
