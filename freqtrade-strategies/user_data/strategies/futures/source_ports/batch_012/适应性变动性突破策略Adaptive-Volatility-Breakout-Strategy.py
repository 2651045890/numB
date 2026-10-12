"""batch_012 port of 适应性变动性突破策略Adaptive-Volatility-Breakout-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-01-01 00:00:00\nend: 2024-01-07 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This source code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © Dicargo_Beam\n\n//@version=5\nstrategy("Volatility Breakout Strategy", overlay=true, default_qty_type= strategy.percent_of_equity, default_qty_value=100,process_orders_on_close=false)\n\nk = input.float(0.6)\n\n\n[o,h,l,c] = request.security(syminfo.tickerid,"D",[open,high,low,close])\n\nlp = math.log(c[1])+(math.log(h[1])-math.log(l[1]))*k\n_lp = math.pow(2.718,lp)\n\nlongcond = _lp < high\nexit = hour==0 or  math.log(close) < (math.log(l[1])+lp)/2\n\n\n\nplot(_lp,"Entry",color=color.yellow)\n//plot(l,"Yesterday\'s Low")\nplot((_lp+l[1])/2,"StopLoss",color=color.red)\n\n\nstrategy.entry("Long", strategy.long,comment = "Long", when = longcond and strategy.opentrades == 0)\n\nstrategy.close("Long", comment="Exit", when = exit)\n\n\nvar bg = 0\nbg := if hour == 0\n    bg + 1\nelse\n    bg[1]\n\nbgcolor(bg/2== math.floor(bg/2) ? color.new(color.blue,95):na)\n\n\n\n'

class SMAdaptiveVolatilityBreakoutStrategyd70b58(PinePortBase, IStrategy):
    source_id = "SM_d70b584e55132746"
    source_file = '适应性变动性突破策略Adaptive-Volatility-Breakout-Strategy.md'
    timeframe = '1d'
    can_short = False
    source_defaults = {'k': 0.6}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 100
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_reproduce_stops = False
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_012 md and exposed through the same PinePortBase interface used by batch_001.', 'request.security/security is present: generic adapter keeps the expression but same-frame evaluation is only an approximation; manual multi-timeframe parity verification is required.', 'The source reads live strategy position state; batch_001-style broker-state parity must be checked manually for this file.']

    def pine_indicators(self, dataframe, params):
        # Runtime evaluates the source against the complete OHLCV frame.
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch012Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
