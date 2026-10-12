"""batch_011 port of 自适应指数平均线范围策略Adaptive-Exponential-Moving-Average-Range-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-02-25 00:00:00\nend: 2024-02-25 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\nargs: [["v_input_1",1]]\n*/\n\n// Credit is due where credit is due:\n// Hull Moving Average: developed by Alan Hull\n// EHMA: coded by Twitter @borserman\n// I\'ve built on their work in an attempt to create a strategy more robust to fake moves\n// @0xLetoII\n\n//@version=4\nstrategy(\n  title="EHMA Range Strategy",\n  process_orders_on_close=true,\n  explicit_plot_zorder=true,\n  overlay=true, \n  initial_capital=1500, \n  default_qty_type=strategy.percent_of_equity, \n  commission_type=strategy.commission.percent, \n  commission_value=0.085,\n  default_qty_value=100\n  )\n  \n\n// Position Type\npos_type = input(defval = "Long", title="Position Type", options=["Both", "Long", "Short"])\n\n// Inputs\nPeriod = input(defval=180, title="Length")\nRangeWidth = input(defval=0.02, step=0.01, title="Range Width")\nsqrtPeriod = sqrt(Period)\n\n// Function for the Borserman EMA\nborserman_ema(x, y) =>\n    alpha = 2 / (y + 1)\n    sum = 0.0\n    sum := alpha * x + (1 - alpha) * nz(sum[1])\n\n// Calculate the Exponential Hull Moving Average\nEHMA = borserman_ema(2 * borserman_ema(close, Period / 2) - borserman_ema(close, Period), sqrtPeriod)\n\n// Create upper & lower bounds around the EHMA for broader entries & exits\nupper = EHMA + (EHMA * RangeWidth)\nlower = EHMA - (EHMA * RangeWidth)\n\n// Plots\nEHMAcolor = (close > EHMA ? color.green : color.red)\nplot(EHMA, color=EHMAcolor, linewidth=2)\nplot(lower, color=color.orange, linewidth=2)\nplot(upper, color=color.blue, linewidth=2)\n\n\n// Strategy\nlong = close > upper\nexit_long = close < lower\nshort = close < lower\nexit_short = close > upper\n\n\n// Calculate start/end date and time condition\nstartDate  = input(timestamp("2017-01-01T00:00:00"))\nfinishDate = input(timestamp("2029-01-01T00:00:00"))\n \ntime_cond  = true\n\n\n// Entries & Exits\nif pos_type == "Both"\n    strategy.entry("Long", strategy.long, comment="Long", when=long and time_cond)\n    strategy.close("Long", comment="Exit Long", when=exit_long and time_cond)\n    strategy.entry("Short", strategy.short, comment="Short", when=short and time_cond)\n    strategy.close("Short", comment="Exit Short", when=exit_short and time_cond)\nif pos_type == "Long"\n    strategy.entry("Long", strategy.long, comment="Long", when=long and time_cond)\n    strategy.close("Long", comment="Exit Long", when=exit_long and time_cond)\nif pos_type == "Short"\n    strategy.entry("Short", strategy.short, comment="Short", when=short and time_cond)\n    strategy.close("Short", comment="Exit Short", when=exit_short and time_cond)\n    '

class SM10283BD16852F1A7(PinePortBase, IStrategy):
    source_id = "SM_10283bd16852f1a7"
    source_file = '自适应指数平均线范围策略Adaptive-Exponential-Moving-Average-Range-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'pos_type': 'Long', 'Period': 180, 'RangeWidth': 0.02}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 100
    source_commission_percent = 0.085
    source_pyramiding = 0
    source_initial_capital = 1500
    source_reproduce_stops = False
    source_risk_flags = ['func', 'var_state']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
