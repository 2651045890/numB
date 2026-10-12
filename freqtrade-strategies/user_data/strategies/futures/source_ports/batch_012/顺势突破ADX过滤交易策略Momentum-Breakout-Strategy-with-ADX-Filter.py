"""batch_012 port of 顺势突破ADX过滤交易策略Momentum-Breakout-Strategy-with-ADX-Filter.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-12-27 00:00:00\nend: 2024-01-03 00:00:00\nperiod: 5m\nbasePeriod: 1m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=4\nstrategy("Hizbullah XAUUSD Sniper", overlay=true)\n\nPrice = close\n\nLength = input(33)\nMult = input(2)\nBasis = sma(Price, Length)\nStdDev = Mult * stdev(Price, Length)\nUpper = Basis + StdDev\nLower = Basis - StdDev\n\nADX_Length = input(4)\nTrueRange = max(max(high-low, abs(high-nz(close[1]))), abs(low-nz(close[1])))\nSmoothedTrueRange = sma(TrueRange, ADX_Length)\nDirectionalMovementPlus = high-nz(high[1]) > nz(low[1])-low ? max(high-nz(high[1]), 0): 0\nDirectionalMovementMinus = nz(low[1])-low > high-nz(high[1]) ? max(nz(low[1])-low, 0): 0\nSmoothedDirectionalMovementPlus = sma(DirectionalMovementPlus, ADX_Length)\nSmoothedDirectionalMovementMinus = sma(DirectionalMovementMinus, ADX_Length)\nDIPlus = SmoothedDirectionalMovementPlus / SmoothedTrueRange * 100\nDIMinus = SmoothedDirectionalMovementMinus / SmoothedTrueRange * 100\nDX = abs(DIPlus - DIMinus) / (DIPlus + DIMinus)*100\nSmoothedADX1 = ema(DX, input(8))\nSmoothedADX2 = ema(DX, input(15))\n\nCondition1 = crossunder(Price, Upper) and SmoothedADX1 < SmoothedADX2\n\nTake_Profit = input(800)\nStop_Loss = input(400)\n\nstrategy.entry("ShortEntry", true, when = Condition1)\nstrategy.exit("ShortExit", "ShortEntry", profit = Take_Profit, loss = Stop_Loss)\n\n'

class SMADXMomentumBreakoutStrategywithADXFilterb6450a(PinePortBase, IStrategy):
    source_id = "SM_b6450abb9862c488"
    source_file = '顺势突破ADX过滤交易策略Momentum-Breakout-Strategy-with-ADX-Filter.md'
    timeframe = '5m'
    can_short = False
    source_defaults = {'Length': 33, 'Mult': 2, 'ADX_Length': 4, 'Take_Profit': 800, 'Stop_Loss': 400}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_reproduce_stops = True
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_012 md and exposed through the same PinePortBase interface used by batch_001.']

    def pine_indicators(self, dataframe, params):
        # Runtime evaluates the source against the complete OHLCV frame.
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch012Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
