"""batch_011 port of 自适应价格通道策略Adaptive-Price-Channel-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-11-03 00:00:00\nend: 2023-12-03 00:00:00\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("Adaptive Price Channel Strategy", overlay=true)\n\nlength = input(20, title="Length")\nexit_length = input(10, title="Exit After X Periods")\natr_multiplier = input(3.2, title="ATR Multiplier")\n\nstartDate = input(defval = timestamp("2019-01-15T08:15:15+00:00"), title = "Start Date")\nendDate = input(defval = timestamp("2033-04-01T08:15:00+00:00"), title = "End Date")\n\nhh = ta.highest(high, length)\nll = ta.lowest(low, length)\natr = ta.atr(length)\n\n// calculate +DI and -DI\nupMove = high - high[1]\ndownMove = low[1] - low\nplusDM = na(upMove[1]) ? na : (upMove > downMove and upMove > 0 ? upMove : 0)\nminusDM = na(downMove[1]) ? na : (downMove > upMove and downMove > 0 ? downMove : 0)\nplusDI = ta.rma(plusDM, length) / atr * 100\nminusDI = ta.rma(minusDM, length) / atr * 100\n\n// calculate ADX\ndx = math.abs(plusDI - minusDI) / (plusDI + minusDI) * 100\nadx = ta.rma(dx, length)\n\nvar int barSinceEntry = na\n\nif (not na(close[length]) )\n    if (adx < 25) // Sideways market\n        if (close > hh - atr_multiplier * atr)\n            strategy.entry("PChLE", strategy.long, comment="PChLE")\n            barSinceEntry := 0\n        else if (close < ll + atr_multiplier * atr)\n            strategy.entry("PChSE", strategy.short, comment="PChSE")\n            barSinceEntry := 0\n    else if (adx >= 25 and plusDI > minusDI) // Bullish market\n        if (close > hh - atr_multiplier * atr)\n            strategy.entry("PChLE", strategy.long, comment="PChLE")\n            barSinceEntry := 0\n    else if (adx >= 25 and plusDI < minusDI) // Bearish market\n        if (close < ll + atr_multiplier * atr)\n            strategy.entry("PChSE", strategy.short, comment="PChSE")\n            barSinceEntry := 0\n\nif (na(barSinceEntry))\n    barSinceEntry := barSinceEntry[1] + 1\nelse if (barSinceEntry >= exit_length)\n    strategy.close("PChLE")\n    strategy.close("PChSE")\n    barSinceEntry := na\n\nplot(hh, title="Highest High", color=color.green, linewidth=2)\nplot(ll, title="Lowest Low", color=color.red, linewidth=2)\n\n'

class SMD14B07E9760A52B0(PinePortBase, IStrategy):
    source_id = "SM_d14b07e9760a52b0"
    source_file = '自适应价格通道策略Adaptive-Price-Channel-Strategy.md'
    timeframe = '1h'
    can_short = True
    source_defaults = {'length': 20, 'exit_length': 10, 'atr_multiplier': 3.2}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = False
    source_risk_flags = ['var_state']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
