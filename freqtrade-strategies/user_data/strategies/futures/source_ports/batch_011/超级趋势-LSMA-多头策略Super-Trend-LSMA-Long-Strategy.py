"""batch_011 port of 超级趋势-LSMA-多头策略Super-Trend-LSMA-Long-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2022-12-11 00:00:00\nend: 2023-12-17 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=4\nstrategy(title = "Supertrend LSMA long Strategy", overlay = true,  pyramiding=1,initial_capital = 100, default_qty_type= strategy.percent_of_equity, default_qty_value = 100, calc_on_order_fills=false, slippage=0,commission_type=strategy.commission.percent,commission_value=0.1)\n\n\natrPeriod = input(14, "ATR Length")\nfactor = input(3, "Factor")\n\n//Time\nfromDay = input(defval = 1, title = "From Day", minval = 1, maxval = 31)\nfromMonth = input(defval = 1, title = "From Month", minval = 1, maxval = 12)\nfromYear = input(defval = 2010, title = "From Year", minval = 1970)\n //monday and session \n// To Date Inputs\ntoDay = input(defval = 31, title = "To Day", minval = 1, maxval = 31)\ntoMonth = input(defval = 12, title = "To Month", minval = 1, maxval = 12)\ntoYear = input(defval = 2031, title = "To Year", minval = 1970)\n\nstartDate = timestamp(fromYear, fromMonth, fromDay, 00, 00)\nfinishDate = timestamp(toYear, toMonth, toDay, 00, 00)\ntime_cond = time >= startDate and time <= finishDate\n\n//LSMA\nlengthx = input(title="Length LSMA", type=input.integer, defval=101)\noffset = 0//input(title="Offset", type=input.integer, defval=0)\nsrc = input(close, title="Source")\nlsma = linreg(src, lengthx, offset)\n\n\n\n[_, direction] = supertrend(factor, atrPeriod)\n\nif(time_cond)\n    if change(direction) < 0 and close > lsma\n        strategy.entry("long", strategy.long)\n    \n    if change(direction) > 0 //and close < lsma\n        strategy.close("long")\n        //strategy.entry("short", strategy.short)\n\n//strategy.close("long",when=close<lsma)\n//strategy.close("short",when=change(direction) < 0 )\n\n    \n//plot(strategy.equity, title="equity", color=color.red, linewidth=2, style=plot.style_areabr)'

class SME7E37A26953CD19D(PinePortBase, IStrategy):
    source_id = "SM_e7e37a26953cd19d"
    source_file = '超级趋势-LSMA-多头策略Super-Trend-LSMA-Long-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'atrPeriod': 14, 'factor': 3, 'fromDay': 1, 'fromMonth': 1, 'fromYear': 2010, 'toDay': 31, 'toMonth': 12, 'toYear': 2031, 'lengthx': 101}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 100
    source_commission_percent = 0.1
    source_pyramiding = 1
    source_initial_capital = 100
    source_reproduce_stops = False
    source_risk_flags = ['broker_state', 'tuple']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
