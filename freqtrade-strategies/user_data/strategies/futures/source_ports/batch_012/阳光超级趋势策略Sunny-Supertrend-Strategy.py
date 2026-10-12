"""batch_012 port of 阳光超级趋势策略Sunny-Supertrend-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-11-12 00:00:00\nend: 2023-12-12 00:00:00\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("Sunny Supertrend Strategy", overlay=true, default_qty_type=strategy.percent_of_equity)\n\natrPeriod = input(10, "ATR Length")\nfactor = input.float(3.0, "Factor", step = 0.01)\n\n[_, direction] = ta.supertrend(factor, atrPeriod)\n\nshor= close > open and close[1] > open[1] and close[2] > open[2] \nlon = open > close and open[1] > close[1] and  open[2] > close[2]\ntt= ta.change(direction) < 0\nss= ta.change(direction) > 0\nlong= tt\nlongexit = lon or ss\nshort= ss\nshortexit = shor or tt\n\nlongPosMem = false\nlongexitPosMem = false\nshortPosMem = false\nshortexitPosMem = false\n\nlongPosMem := long ? true : short ? false : longPosMem[1]\nlongexitPosMem := longexit ? true : shortexit ? false : longexitPosMem[1]\nshortPosMem := short ? true : long ? false : shortPosMem[1]\nshortexitPosMem := shortexit ? true : longexit ? false : shortexitPosMem[1]\n\nlongy = long and not(longPosMem[1])\nlongexity = longexit and not(longexitPosMem[1])\nshorty = short and not(shortPosMem[1])\nshortexity = shortexit and not(shortexitPosMem[1])\n\n//Use this to customize the look of the arrows to suit your needs.\nplotshape(longy, location=location.abovebar, color=color.green, style=shape.arrowup, text="Buy")\nplotshape(longexity, location=location.top, color=color.green, style=shape.xcross, text="Buy exit")\nplotshape(shorty, location=location.belowbar, color=color.red, style=shape.arrowdown, text="Sell")\nplotshape(shortexity, location=location.bottom, color=color.red, style=shape.xcross, text="Sell exit")\n\n\n//plot(strategy.equity, title="equity", color=color.red, linewidth=2, style=plot.style_areabr)\n// STEP 1:\n// Make input options that configure backtest date range\nstartDate = input.int(title="Start Date", defval=1, minval=1, maxval=31)\nstartMonth = input.int(title="Start Month", \n     defval=1, minval=1, maxval=12)\nstartYear = input.int(title="Start Year",\n     defval=2021, minval=1800, maxval=2100)\n\nendDate = input.int(title="End Date",\n     defval=1, minval=1, maxval=31)\nendMonth = input.int(title="End Month",\n     defval=2, minval=1, maxval=12)\nendYear = input.int(title="End Year",\n     defval=2021, minval=1800, maxval=2100)\n\n// STEP 2:\n// Look if the close time of the current bar\n// falls inside the date range\ninDateRange =  true\n\n\n\n// STEP 3:\n// Submit entry orders, but only when bar is inside date range\nif (inDateRange and longy)\n    strategy.entry("enter long",strategy.long,when= longy)\n    strategy.close("long",when=longexity)\n\n\nif (inDateRange and shorty)\n    strategy.entry("enter short",strategy.short,when = shorty)\n    strategy.close("short", when=shortexity)\n\n'

class SMSunnySupertrendStrategyf7717d(PinePortBase, IStrategy):
    source_id = "SM_f7717dc26e667897"
    source_file = '阳光超级趋势策略Sunny-Supertrend-Strategy.md'
    timeframe = '1h'
    can_short = True
    source_defaults = {'atrPeriod': 10, 'factor': 3.0, 'startDate': 1}
    source_qty_type = 'percent_of_equity'
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
