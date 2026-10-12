"""batch_011 port of 跳空缺口反转策略Gap-Down-Reversal-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-09-11 00:00:00\nend: 2023-09-12 04:00:00\nperiod: 1m\nbasePeriod: 1m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This source code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © RolandoSantos\n\n//@version=2\n\nstrategy(title="Gap Down reversal strat", overlay=true, pyramiding=1, default_qty_type =  strategy.cash, default_qty_value = 10000, initial_capital = 10000 )\n\n/// Start date\n\nstartDate = input(title="Start Date", defval=1, minval=1, maxval=31)\nstartMonth = input(title="Start Month", defval=1, minval=1, maxval=12)\nstartYear = input(title="Start Year", defval=2009, minval=1800, maxval=2100)\n\n\n// See if this bar\'s time happened on/after start date\nafterStartDate = (time >= timestamp(syminfo.timezone, startYear, startMonth, startDate, 0, 0))\n\n// STEP 1:\n// Configure trail stop level with input options (optional)\nlongTrailPerc = input(title="Trail Long Loss (%)",\n     type=float, minval=0.0, step=0.1, defval=5.0) * 0.01\n\n\n// Calculate trading conditions\ngap_d_r = open < close[1] and close > open\n\n\n// Plot Shapes\nplotshape(gap_d_r, style=shape.triangleup, location=location.belowbar)\n///plotshape(gap_u_r, style=shape.triangledown, location=location.abovebar)\n\n///// Use Low, or close/////\n\n//hlco = input(title="Stop Modifier", defval="close", options=["open", "high", "low"])\n\n\n// STEP 2:\n// Determine trail stop loss prices\nlongStopPrice = 0.0   ///, shortStopPrice = 0.0\n\nlongStopPrice := if (strategy.position_size > 0)\n    stopValue = close * (1 - longTrailPerc)\n    max(stopValue, longStopPrice[1])\nelse\n    0\n\n\n// Plot stop loss values for confirmation\nplot(series=(strategy.position_size > 0) ? longStopPrice : na,\n     color=red, style=circles,\n     linewidth=1, title="Long Trail Stop")\n\n\n// Submit entry orders\nif (afterStartDate and gap_d_r)\n    strategy.entry(id="EL", long=true)\n\n\n// Submit exit orders for trail stop loss price\nif (strategy.position_size > 0)\n    strategy.exit(id="Stop out", stop=longStopPrice)\n\n\n\n\n\n\n\n\n\n\n\n\n\n'

class SM3BA5A923B47F1042(PinePortBase, IStrategy):
    source_id = "SM_3ba5a923b47f1042"
    source_file = '跳空缺口反转策略Gap-Down-Reversal-Strategy.md'
    timeframe = '1m'
    can_short = False
    source_defaults = {'startDate': 1, 'startMonth': 1, 'startYear': 2009, 'longTrailPerc': 5.0}
    source_qty_type = 'cash'
    source_qty_value = 10000
    source_commission_percent = 0
    source_pyramiding = 1
    source_initial_capital = 10000
    source_reproduce_stops = True
    source_risk_flags = ['broker_state', 'exit_order', 'var_state']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
