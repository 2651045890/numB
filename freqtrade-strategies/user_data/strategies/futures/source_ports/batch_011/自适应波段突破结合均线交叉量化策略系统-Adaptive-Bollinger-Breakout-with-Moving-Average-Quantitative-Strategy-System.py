"""batch_011 port of 自适应波段突破结合均线交叉量化策略系统-Adaptive-Bollinger-Breakout-with-Moving-Average-Quantitative-Strategy-System.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2024-10-01 00:00:00\nend: 2024-10-31 23:59:59\nperiod: 1h\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("BB Breakout with MA 100 Strategy", overlay=true)\n\n// Parameter Bollinger Bands\nlength = input(20, title="BB Length")\nstdDev = input(2.0, title="BB Standard Deviation")\n\n// Hitung Bollinger Bands\nbasis = ta.sma(close, length)\ndev = stdDev * ta.stdev(close, length)\nupperBB = basis + dev\nlowerBB = basis - dev\n\n// Hitung Moving Average 100\nma100 = ta.sma(close, 100)\n\n// Logika untuk sinyal beli dan jual\nlongCondition = close > upperBB and close[1] <= upperBB[1]\nshortCondition = close < lowerBB and close[1] >= lowerBB[1]\n\n// Menentukan ukuran posisi (jumlah lot)\nsize = strategy.equity / close // Menentukan ukuran posisi berdasarkan ekuitas saat ini\n\n// Eksekusi order\nif (longCondition)\n    strategy.entry("Long", strategy.long, qty=size)\n\nif (shortCondition)\n    strategy.entry("Short", strategy.short, qty=size)\n\n// Menutup posisi ketika kondisi terbalik\nif (longCondition and strategy.position_size < 0)\n    strategy.close("Short")\n\nif (shortCondition and strategy.position_size > 0)\n    strategy.close("Long")\n\n// Plotting\nplot(upperBB, color=color.red, title="Upper BB")\nplot(lowerBB, color=color.green, title="Lower BB")\nplot(basis, color=color.blue, title="Basis BB")\nplot(ma100, color=color.orange, title="MA 100")\n\n// Menambahkan informasi ke grafik\nbgcolor(longCondition ? color.new(color.green, 90) : na, title="Buy Signal Background")\nbgcolor(shortCondition ? color.new(color.red, 90) : na, title="Sell Signal Background")\n'

class SM3A9FA3D429E4D424(PinePortBase, IStrategy):
    source_id = "SM_3a9fa3d429e4d424"
    source_file = '自适应波段突破结合均线交叉量化策略系统-Adaptive-Bollinger-Breakout-with-Moving-Average-Quantitative-Strategy-System.md'
    timeframe = '1h'
    can_short = True
    source_defaults = {'length': 20, 'stdDev': 2.0}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = False
    source_risk_flags = ['broker_state']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
