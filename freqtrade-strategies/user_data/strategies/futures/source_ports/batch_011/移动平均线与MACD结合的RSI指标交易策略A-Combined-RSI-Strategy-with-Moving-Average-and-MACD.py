"""batch_011 port of 移动平均线与MACD结合的RSI指标交易策略A-Combined-RSI-Strategy-with-Moving-Average-and-MACD.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-02-13 00:00:00\nend: 2024-02-19 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy(\'sachin 3.30 \', overlay=true)\n\n// Input parameters\nlength = input.int(14, title=\'RSI Length\', minval=1)\noverbought = input.int(70, title=\'RSI Overbought Level\', minval=0, maxval=100)\noversold = input.int(30, title=\'RSI Oversold Level\', minval=0, maxval=100)\nema3_length = input(3, title=\'EMA 3 Length\')\nema30_length = input(30, title=\'EMA 30 Length\')\nema50_length = input(50, title=\'EMA 50 Length\')\n\n// Calculate EMAs\nema3 = ta.ema(close, ema3_length)\nema30 = ta.ema(close, ema30_length)\nema50 = ta.ema(close, ema50_length)\n\n// Calculate RSI\nrsiValue = ta.rsi(close, length)\n\n// Calculate MACD\n[macdLine, signalLine, hist] = ta.macd(close, 12, 26, 9)\n\nvar float buyPrice = na\n\n// Buy condition: EMA 3 crosses above EMA 30 and price is above EMA 50\nbuyCondition = ta.crossover(ema3, ema30) and close > ema50\nif (buyCondition)\n    buyPrice := close\n    strategy.entry(\'Buy\', strategy.long)\n\n// Exit long position when close is below EMA30 and below the low of the previous 3 candles after the buy entry\nexitLongCondition = close < ema30 and close < ta.lowest(low, 3) and close < buyPrice\nif (exitLongCondition)\n    strategy.close(\'BuyExit\')\n\n// Sell condition: EMA 3 crosses below EMA 30 and price is below EMA 50\nsellCondition = ta.crossunder(ema3, ema30) and close < ema50\nif (sellCondition)\n    strategy.entry(\'Sell\', strategy.short)\n\n// Exit short position when close is above EMA30 and above the high of the previous 3 candles after the sell entry\nexitShortCondition = close > ema30 and close > ta.highest(high, 3)\nif (exitShortCondition)\n    strategy.close(\'SellExit\')\n\n// Plot EMAs on the chart\nplot(ema3, color=color.new(color.blue, 0), title=\'EMA 3\')\nplot(ema30, color=color.new(color.red, 0), title=\'EMA 30\')\n\n// Change color of EMA 50 based on MACD histogram\nema50Color = hist > 0 ? color.new(color.blue, 0) : hist < 0 ? color.new(color.black, 0) : color.new(color.blue, 0)\nplot(ema50, color=ema50Color, title=\'EMA 50 Colored\')\n\n// Change color of EMA 30 based on RSI trend\nema30Color = rsiValue > oversold ? color.new(color.green, 0) : rsiValue < overbought ? color.new(color.red, 0) : color.new(color.blue, 0)\nplot(ema30, color=ema30Color, title=\'EMA 30 Colored\')\n\n// Highlight Buy and Sell signals on the chart\nbgcolor(buyCondition ? color.new(color.green, 90) : na)\nbgcolor(sellCondition ? color.new(color.red, 90) : na)\n\n// Plotting Buy and Sell Signals on the Chart until strategy exit\nbarcolor(strategy.position_size > 0 and rsiValue > overbought ? color.new(color.yellow, 0) : strategy.position_size < 0 and rsiValue < oversold ? color.new(color.black, 0) : na)\n'

class SM530242EB2422294A(PinePortBase, IStrategy):
    source_id = "SM_530242eb2422294a"
    source_file = '移动平均线与MACD结合的RSI指标交易策略A-Combined-RSI-Strategy-with-Moving-Average-and-MACD.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'length': 14, 'overbought': 70, 'oversold': 30, 'ema3_length': 3, 'ema30_length': 30, 'ema50_length': 50}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = False
    source_risk_flags = ['broker_state', 'tuple', 'var_state']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
