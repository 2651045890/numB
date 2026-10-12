"""batch_011 port of 维加斯超级趋势增强策略Vegas-SuperTrend-Enhanced-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-04-22 00:00:00\nend: 2024-04-27 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This Pine Script™ code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © PresentTrading\n\n// The "Vegas SuperTrend Strategy" uses Vegas Channel and SuperTrend indicators on trading charts, allowing for adjustable settings like ATR length and channel size. \n// It modifies the SuperTrend\'s sensitivity to market volatility, generating buy (green) or sell (red) signals upon trend shifts. \n// Entry and exit points are visually marked, with the strategy automating trades based on these trend changes to adapt to different market conditions.\n\n//@version=5\nstrategy("Vegas SuperTrend Enhanced - strategy [presentTrading]", shorttitle="Vegas SuperTrend Enhanced - strategy [presentTrading]", overlay=true, precision=3, default_qty_type=strategy.cash, \n commission_value=0.1, commission_type=strategy.commission.percent, slippage=1, currency=currency.USD, default_qty_value=10000, initial_capital=10000)\n\n// Input settings allow the user to customize the strategy\'s parameters.\ntradeDirectionChoice = input.string(title="Trade Direction", defval="Both", options=["Long", "Short", "Both"]) // Option to select the trading direction\natrPeriod = input(10, "ATR Period for SuperTrend") // Length of the ATR for volatility measurement\nvegasWindow = input(100, "Vegas Window Length") // Length of the moving average for the Vegas Channel\nsuperTrendMultiplier = input(5, "SuperTrend Multiplier Base") // Base multiplier for the SuperTrend calculation\nvolatilityAdjustment = input.float(5, "Volatility Adjustment Factor") // Factor to adjust the SuperTrend sensitivity to the Vegas Channel width\n\n// Calculate the Vegas Channel using a simple moving average and standard deviation.\nvegasMovingAverage = ta.sma(close, vegasWindow)\nvegasChannelStdDev = ta.stdev(close, vegasWindow)\nvegasChannelUpper = vegasMovingAverage + vegasChannelStdDev\nvegasChannelLower = vegasMovingAverage - vegasChannelStdDev\n\n// Adjust the SuperTrend multiplier based on the width of the Vegas Channel.\nchannelVolatilityWidth = vegasChannelUpper - vegasChannelLower\nadjustedMultiplier = superTrendMultiplier + volatilityAdjustment * (channelVolatilityWidth / vegasMovingAverage)\n\n// Calculate the SuperTrend indicator values.\naverageTrueRange = ta.atr(atrPeriod)\nsuperTrendUpper = hlc3 - (adjustedMultiplier * averageTrueRange)\nsuperTrendLower = hlc3 + (adjustedMultiplier * averageTrueRange)\nvar float superTrendPrevUpper = na\nvar float superTrendPrevLower = na\nvar int marketTrend = 1\n\n// Update SuperTrend values and determine the current trend direction.\nsuperTrendPrevUpper := nz(superTrendPrevUpper[1], superTrendUpper)\nsuperTrendPrevLower := nz(superTrendPrevLower[1], superTrendLower)\nmarketTrend := close > superTrendPrevLower ? 1 : close < superTrendPrevUpper ? -1 : nz(marketTrend[1], 1)\nsuperTrendUpper := marketTrend == 1 ? math.max(superTrendUpper, superTrendPrevUpper) : superTrendUpper\nsuperTrendLower := marketTrend == -1 ? math.min(superTrendLower, superTrendPrevLower) : superTrendLower\nsuperTrendPrevUpper := superTrendUpper\nsuperTrendPrevLower := superTrendLower\n\n// Enhanced Visualization\n// Plot the SuperTrend and Vegas Channel for visual analysis.\nplot(marketTrend == 1 ? superTrendUpper : na, "SuperTrend Upper", color=color.green, linewidth=2)\nplot(marketTrend == -1 ? superTrendLower : na, "SuperTrend Lower", color=color.red, linewidth=2)\nplot(vegasChannelUpper, "Vegas Upper", color=color.purple, linewidth=1)\nplot(vegasChannelLower, "Vegas Lower", color=color.purple, linewidth=1)\n\n// Apply a color to the price bars based on the current market trend.\nbarcolor(marketTrend == 1 ? color.green : marketTrend == -1 ? color.red : na)\n\n// Detect trend direction changes and plot entry/exit signals.\ntrendShiftToBullish = marketTrend == 1 and marketTrend[1] == -1\ntrendShiftToBearish = marketTrend == -1 and marketTrend[1] == 1\n\nplotshape(series=trendShiftToBullish, title="Enter Long", location=location.belowbar, color=color.green, style=shape.labelup, text="Buy")\nplotshape(series=trendShiftToBearish, title="Enter Short", location=location.abovebar, color=color.red, style=shape.labeldown, text="Sell")\n\n// Define conditions for entering long or short positions, and execute trades based on these conditions.\nenterLongCondition = marketTrend == 1\nenterShortCondition = marketTrend == -1\n\n// Check trade direction choice before executing trade entries.\nif enterLongCondition and (tradeDirectionChoice == "Long" or tradeDirectionChoice == "Both")\n    strategy.entry("Long Position", strategy.long)\n\nif enterShortCondition and (tradeDirectionChoice == "Short" or tradeDirectionChoice == "Both")\n    strategy.entry("Short Position", strategy.short)\n\n// Close all positions when the market trend changes.\nif marketTrend != marketTrend[1]\n    strategy.close_all()\n'

class SMC9DDFB9DA42DC17E(PinePortBase, IStrategy):
    source_id = "SM_c9ddfb9da42dc17e"
    source_file = '维加斯超级趋势增强策略Vegas-SuperTrend-Enhanced-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'tradeDirectionChoice': 'Both', 'atrPeriod': 10, 'vegasWindow': 100, 'superTrendMultiplier': 5, 'volatilityAdjustment': 5}
    source_qty_type = 'cash'
    source_qty_value = 10000
    source_commission_percent = 0.1
    source_pyramiding = 0
    source_initial_capital = 10000
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
