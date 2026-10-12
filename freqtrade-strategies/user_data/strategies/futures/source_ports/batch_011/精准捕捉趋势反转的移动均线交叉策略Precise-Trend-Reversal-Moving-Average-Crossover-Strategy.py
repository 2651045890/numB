"""batch_011 port of 精准捕捉趋势反转的移动均线交叉策略Precise-Trend-Reversal-Moving-Average-Crossover-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2024-01-14 00:00:00\nend: 2024-01-21 00:00:00\nperiod: 15m\nbasePeriod: 5m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("[S_R__9] - Death and Golden Cross", overlay=true)\n\n// Specific Time Date Range For Backtest\nstartDate = input.int(title=\'Start Date\', defval=1, minval=1, maxval=31, group=\'DATE CONFIG\')\nstartMonth = input.int(title=\'Start Month\', defval=1, minval=1, maxval=12, group=\'DATE CONFIG\')\nstartYear = input.int(title=\'Start Year\', defval=2023, minval=1800, maxval=2100, group=\'DATE CONFIG\')\n\nendDate = input.int(title=\'End Date\', defval=31, minval=1, maxval=31, group=\'DATE CONFIG\')\nendMonth = input.int(title=\'End Month\', defval=12, minval=1, maxval=12, group=\'DATE CONFIG\')\nendYear = input.int(title=\'End Year\', defval=2023, minval=1800, maxval=2100, group=\'DATE CONFIG\')\n\nSPECIFIC_DATE = input.bool(title=\'USE SPECIFIC DATE ?\', defval=false, group=\'DATE CONFIG\')\n\ninDateRange = SPECIFIC_DATE ? time >= timestamp(syminfo.timezone, startYear, startMonth, startDate, 0, 0) and time < timestamp(syminfo.timezone, endYear, endMonth, endDate, 0, 0) : true\n\n// Calculate 50 SMA and 200 SMA\nsma50 = ta.sma(close, 50)\nsma200 = ta.sma(close, 200)\n\n// Detect a Death Cross (50 SMA crossing below 200 SMA)\ndeathCross = ta.crossunder(sma50, sma200)\n// Detect a Golden Cross (50 SMA crossing above 200 SMA)\ngoldenCross = ta.crossover(sma50, sma200)\n\n// Strategy Execution\nif (inDateRange)\n    if (deathCross)\n        strategy.entry("Death Cross long", strategy.short)\n\n    if (goldenCross)\n        strategy.entry("Golden Cross short", strategy.long)\n\n// Plot SMAs\nplot(sma50, color=color.red, title="50 SMA")\nplot(sma200, color=color.blue, title="200 SMA")\n\n// Plotting Death Cross signal\nplotshape(series=deathCross and inDateRange, title="Death Cross Signal", location=location.belowbar, color=color.red, style=shape.labeldown, text="DEATH CROSS")\n\n// Plotting Golden Cross signal\nplotshape(series=goldenCross and inDateRange, title="Golden Cross Signal", location=location.abovebar, color=color.green, style=shape.labelup, text="GOLDEN CROSS")\n'

class SMC772DF571ECF1BD5(PinePortBase, IStrategy):
    source_id = "SM_c772df571ecf1bd5"
    source_file = '精准捕捉趋势反转的移动均线交叉策略Precise-Trend-Reversal-Moving-Average-Crossover-Strategy.md'
    timeframe = '15m'
    can_short = True
    source_defaults = {'startDate': 1, 'startMonth': 1, 'startYear': 2023, 'endDate': 31, 'endMonth': 12, 'endYear': 2023, 'SPECIFIC_DATE': False}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = False
    source_risk_flags = ['common_subset']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
