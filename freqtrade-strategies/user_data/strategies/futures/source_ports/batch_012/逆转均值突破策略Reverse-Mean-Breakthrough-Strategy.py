"""batch_012 port of 逆转均值突破策略Reverse-Mean-Breakthrough-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-12-12 00:00:00\nend: 2023-12-19 00:00:00\nperiod: 3m\nbasePeriod: 1m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy(title=\'BroTheJo Strategy\', shorttitle=\'BTJ INV\', overlay=true)\n\n// Input settings\nstopLossInPips = input.int(10, minval=0, title=\'Stop Loss (in Pips)\')\nccimomCross = input.string(\'CCI\', \'Entry Signal Source\', options=[\'CCI\', \'Momentum\'])\nccimomLength = input.int(10, minval=1, title=\'CCI/Momentum Length\')\nuseDivergence = input.bool(false, title=\'Find Regular Bullish/Bearish Divergence\')\nrsiOverbought = input.int(65, minval=1, title=\'RSI Overbought Level\')\nrsiOversold = input.int(35, minval=1, title=\'RSI Oversold Level\')\nrsiLength = input.int(14, minval=1, title=\'RSI Length\')\nplotMeanReversion = input.bool(true, \'Plot Mean Reversion Bands on the chart\')\nemaPeriod = input(200, title=\'Lookback Period (EMA)\')\nbandMultiplier = input.float(1.6, title=\'Outer Bands Multiplier\')\n\n// CCI and Momentum calculation\nmomLength = ccimomCross == \'Momentum\' ? ccimomLength : 10\nmom = close - close[momLength]\ncci = ta.cci(close, ccimomLength)\nccimomCrossUp = ccimomCross == \'Momentum\' ? ta.cross(mom, 0) : ta.cross(cci, 0)\nccimomCrossDown = ccimomCross == \'Momentum\' ? ta.cross(0, mom) : ta.cross(0, cci)\n\n// RSI calculation\nsrc = close\nup = ta.rma(math.max(ta.change(src), 0), rsiLength)\ndown = ta.rma(-math.min(ta.change(src), 0), rsiLength)\nrsi = down == 0 ? 100 : up == 0 ? 0 : 100 - 100 / (1 + up / down)\noversoldAgo = rsi[0] <= rsiOversold or rsi[1] <= rsiOversold or rsi[2] <= rsiOversold or rsi[3] <= rsiOversold\noverboughtAgo = rsi[0] >= rsiOverbought or rsi[1] >= rsiOverbought or rsi[2] >= rsiOverbought or rsi[3] >= rsiOverbought\n\n// Regular Divergence Conditions\nbullishDivergenceCondition = rsi[0] > rsi[1] and rsi[1] < rsi[2]\nbearishDivergenceCondition = rsi[0] < rsi[1] and rsi[1] > rsi[2]\n\n// Mean Reversion Indicator\nmeanReversion = plotMeanReversion ? ta.ema(close, emaPeriod) : na\nstdDev = plotMeanReversion ? ta.stdev(close, emaPeriod) : na\nupperBand = plotMeanReversion ? meanReversion + stdDev * bandMultiplier : na\nlowerBand = plotMeanReversion ? meanReversion - stdDev * bandMultiplier : na\n\n// Entry Conditions\nprevHigh = ta.highest(high, 1)\nprevLow = ta.lowest(low, 1)\nshortEntryCondition = ccimomCrossUp and oversoldAgo and (not useDivergence or bullishDivergenceCondition) and (prevHigh >= meanReversion) and (prevLow >= meanReversion)\nlongEntryCondition = ccimomCrossDown and overboughtAgo and (not useDivergence or bearishDivergenceCondition) and (prevHigh <= meanReversion) and (prevLow <= meanReversion)\n\n// Plotting\noldShortEntryCondition = ccimomCrossUp and oversoldAgo and (not useDivergence or bullishDivergenceCondition)\noldLongEntryCondition = ccimomCrossDown and overboughtAgo and (not useDivergence or bearishDivergenceCondition)\nplotshape(oldLongEntryCondition, title=\'BUY\', style=shape.triangleup, text=\'B\', location=location.belowbar, color=color.new(color.lime, 0), textcolor=color.new(color.white, 0), size=size.tiny)\nplotshape(oldShortEntryCondition, title=\'SELL\', style=shape.triangledown, text=\'S\', location=location.abovebar, color=color.new(color.red, 0), textcolor=color.new(color.white, 0), size=size.tiny)\n\n// Strategy logic\nif (longEntryCondition)\n    stopLoss = close - stopLossInPips\n    strategy.entry("Buy", strategy.long)\n    strategy.exit("exit", "Buy", stop=stopLoss)\nif (shortEntryCondition)\n    stopLoss = close + stopLossInPips\n    strategy.entry("Sell", strategy.short)\n    strategy.exit("exit", "Sell", stop=stopLoss)\n\n// Close all open positions when outside of bands\ncloseAll = (high >= upperBand) or (low <= lowerBand)\n\nif (closeAll)\n    strategy.close_all("Take Profit/Cut Loss")\n\n// Plotting\nplot(upperBand, title=\'Upper Band\', color=color.fuchsia, linewidth=1)\nplot(meanReversion, title=\'Mean\', color=color.gray, linewidth=1)\nplot(lowerBand, title=\'Lower Band\', color=color.blue, linewidth=1)\n\n'

class SMReverseMeanBreakthroughStrategy725f58(PinePortBase, IStrategy):
    source_id = "SM_725f58057e787daa"
    source_file = '逆转均值突破策略Reverse-Mean-Breakthrough-Strategy.md'
    timeframe = '3m'
    can_short = True
    source_defaults = {'stopLossInPips': 10, 'ccimomCross': 'CCI', 'ccimomLength': 10, 'useDivergence': False, 'rsiOverbought': 65, 'rsiOversold': 35, 'rsiLength': 14, 'plotMeanReversion': True, 'emaPeriod': 200, 'bandMultiplier': 1.6}
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
