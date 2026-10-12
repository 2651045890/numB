"""batch_011 port of 突破回调开仓策略Breakthrough-Callback-Long-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2024-01-22 00:00:00\nend: 2024-02-21 00:00:00\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=3\n//  Created by Leon Ross\n//study(title="OutsideDownOpenLower", shorttitle="ODOL", overlay=true)\nstrategy(title = "Outside", shorttitle = "OB", overlay = true )\n  \n\n//Window of time\n//start     = timestamp(2018, 01, 01, 00, 00)  // backtest start window\n//finish    = timestamp(2018, 12, 31, 23, 59)        // backtest finish window\n//window()  => time >= start and time <= finish ? true : false // create function "within window of time"  \n\n//Conditions\noutsideBar = low < low[1] and high > high[1] and close < open\nallConditions = outsideBar\n  \n//Stop and Take Profit as percentages\n//inpTakeProfit   = input(2, title=\'Take Profit %\', type=float)/100\n//takeProfitValue = strategy.position_avg_price * (1 + inpTakeProfit)\n//useTakeProfit   = inpTakeProfit  > 0 ?  takeProfitValue : na\n//inpStopLoss     = input(1, title=\'Stop Loss %\', type=float)/100\n//stopLossValue = strategy.position_avg_price * (1 - inpStopLoss)\n//useStopLoss     = inpStopLoss    > 0 ?  stopLossValue   : na\n//entry = strategy.position_avg_price\n\n\n\n//Stop as last bars low and profit as percentage\nentry = strategy.position_avg_price\ninpTakeProfit   = input(2.0, title=\'Take Profit %\', type=float)/100\ntakeProfitValue = strategy.position_avg_price * (1 + inpTakeProfit)\nuseTakeProfit   = inpTakeProfit  > 0 ?  takeProfitValue : na\ninpStopLoss     = valuewhen(allConditions, low, 0)\nstopLossValue = inpStopLoss\nuseStopLoss     = inpStopLoss    > 0 ?  stopLossValue   : na\n    \n\n\n\n//Plots\nbgcolor(allConditions ==1 ? aqua : na, transp=70)\nplot(entry, color=blue, style=linebr, linewidth=2)\nplot(useStopLoss, color=red, style=linebr, linewidth=2)\nplot(useTakeProfit, color=green, style=linebr, linewidth=2)\n\n\n//Entires\nstrategy.entry(id = "Long", long = true, when = allConditions) // use function or simple condition to decide when to get in\n\n//Exits\n//if (barssince(allConditions) == 2)\n    //strategy.close("Long")\n//else\nstrategy.exit("Exit Long", from_entry = "Long", stop = useStopLoss)\n\n\n\n\n\n'

class SMF875867C07C13B7B(PinePortBase, IStrategy):
    source_id = "SM_f875867c07c13b7b"
    source_file = '突破回调开仓策略Breakthrough-Callback-Long-Strategy.md'
    timeframe = '1h'
    can_short = False
    source_defaults = {'inpTakeProfit': 2.0}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = True
    source_risk_flags = ['func', 'broker_state', 'exit_order']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
