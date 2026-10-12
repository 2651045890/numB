"""batch_011 port of 移动平均趋势跟踪策略Moving-Average-Trend-Tracking-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-02-13 00:00:00\nend: 2024-02-19 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This source code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n//@version=5\n//1.0 - 240202 @caddjax\n\nstrategy(title = "+DI Crossover", overlay=false)\n\n//DMI + ADX Chart w/ overlay\n// © jrregencia\n\nlensig = input.int(14, title="ADX Smoothing", minval=1, maxval=50)\nlen = input.int(6, minval=1, title="DI Length")\nup = ta.change(high)\ndown = -ta.change(low)\nplusDM = na(up) ? na : (up > down and up > 0 ? up : 0)\nminusDM = na(down) ? na : (down > up and down > 0 ? down : 0)\ntrur = ta.rma(ta.tr, len)\nplus = fixnan(100 * ta.rma(plusDM, len) / trur)\nminus = fixnan(100 * ta.rma(minusDM, len) / trur)\nsum = plus + minus\nadx = 100 * ta.rma(math.abs(plus - minus) / (sum == 0 ? 1 : sum), lensig)\nadxmax = input.int(50, title="ADX Max Buying Area", minval=1, maxval=100)\nadxmin = input.int(0, title="ADX Min Buying Area", minval=0, maxval=99)\n\n\n\n//DI cross alert\nDIPcross = ta.crossover(plus, minus) ? plus : na\nplotshape(DIPcross, style = shape.cross , color=color.white, location=location.absolute)\n\nplot(adx, color=color.rgb(255, 238, 0, 23), title="ADX", linewidth=2)\np1 = plot(plus, color=color.rgb(16, 137, 0, 31), title="+DI", linewidth=1)\np2 = plot(minus, color=color.rgb(143, 82, 255, 25), title="-DI", linewidth=1)\nadxmaxl = hline(adxmax, title="ADX MaxLine", color=color.silver, linestyle=hline.style_solid)\nadxminl = hline(adxmin, title="ADX MinLine", color=color.silver, linestyle=hline.style_solid)\nfill(p1, p2, title="Cloud Fill", color = plus > minus ? color.teal : color.red, transp=50)\nfill(adxmaxl, adxminl, title="ADX Fill", color=color.silver, transp=90)\n\n// Configure trail stop level with input options (optional)\nlongTrailPerc = input.float(3, title="Trail Long Loss (%)",\n     minval=0.0, step=0.1) * 0.01\n// Determine trail stop loss prices\nlongStopPrice = 0.0\n\n// Determine entry condition\nenterLong = ta.crossover(plus, minus) ? plus : na\n\nlongStopPrice := if strategy.position_size > 0\n    stopValue = high[1] * (1 - longTrailPerc)\n    math.max(stopValue, longStopPrice[1])\nelse\n    0\n// Submit entry orders\nif enterLong\n    strategy.entry("EL", strategy.long)    \n// Submit exit orders for trail stop loss price\nif strategy.position_size > 0\n    strategy.exit("XL TRL STP", stop=longStopPrice)    '

class SMA046B0CC45BBD0F9(PinePortBase, IStrategy):
    source_id = "SM_a046b0cc45bbd0f9"
    source_file = '移动平均趋势跟踪策略Moving-Average-Trend-Tracking-Strategy.md'
    timeframe = '1d'
    can_short = False
    source_defaults = {'lensig': 14, 'len': 6, 'adxmax': 50, 'adxmin': 0, 'longTrailPerc': 3}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
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
