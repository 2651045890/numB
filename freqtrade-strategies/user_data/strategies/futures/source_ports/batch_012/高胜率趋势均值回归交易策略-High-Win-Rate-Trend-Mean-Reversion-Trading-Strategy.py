"""batch_012 port of 高胜率趋势均值回归交易策略-High-Win-Rate-Trend-Mean-Reversion-Trading-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2024-01-01 00:00:00\nend: 2024-11-11 00:00:00\nperiod: 2d\nbasePeriod: 2d\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("High Win Rate Mean Reversion Strategy for Gold", overlay=true)\n\n// Input Parameters\nbbLength = input.int(20, title="Bollinger Bands Length")\nbbMult = input.float(2, title="Bollinger Bands Multiplier")\nrsiLength = input.int(14, title="RSI Length")\nrsiOverbought = input.int(70, title="RSI Overbought Level")\nrsiOversold = input.int(30, title="RSI Oversold Level")\natrLength = input.int(14, title="ATR Length")\nrrRatio = input.float(0.75, title="Risk/Reward Ratio", step=0.05)  // Lower RRR to achieve a high win rate\nriskPerTrade = input.float(2.0, title="Risk per Trade (%)", step=0.1) / 100  // 2% risk per trade\n\n// Bollinger Bands Calculation\nbasis = ta.sma(close, bbLength)\ndev = bbMult * ta.stdev(close, bbLength)\nupperBand = basis + dev\nlowerBand = basis - dev\n\n// RSI Calculation\nrsi = ta.rsi(close, rsiLength)\n\n// ATR Calculation for Stop Loss\natr = ta.atr(atrLength)\n\n// Entry Conditions: Mean Reversion\nlongCondition = close < lowerBand and rsi < rsiOversold\nshortCondition = close > upperBand and rsi > rsiOverbought\n\n// Stop Loss and Take Profit based on ATR\nlongStopLoss = close - atr * 1.0  // 1x ATR stop loss for long trades\nshortStopLoss = close + atr * 1.0  // 1x ATR stop loss for short trades\n\nlongTakeProfit = close + (close - longStopLoss) * rrRatio  // 0.75x ATR take profit\nshortTakeProfit = close - (shortStopLoss - close) * rrRatio  // 0.75x ATR take profit\n\n// Calculate position size based on risk\nequity = strategy.equity\nriskAmount = equity * riskPerTrade\nqtyLong = riskAmount / (close - longStopLoss)\nqtyShort = riskAmount / (shortStopLoss - close)\n\n// Long Trade\nif (longCondition)\n    strategy.entry("Long", strategy.long, qty=qtyLong)\n    strategy.exit("Take Profit/Stop Loss", from_entry="Long", limit=longTakeProfit, stop=longStopLoss)\n\n// Short Trade\nif (shortCondition)\n    strategy.entry("Short", strategy.short, qty=qtyShort)\n    strategy.exit("Take Profit/Stop Loss", from_entry="Short", limit=shortTakeProfit, stop=shortStopLoss)\n\n// Plot Bollinger Bands\nplot(upperBand, color=color.red, linewidth=2, title="Upper Bollinger Band")\nplot(lowerBand, color=color.green, linewidth=2, title="Lower Bollinger Band")\nplot(basis, color=color.gray, linewidth=2, title="Bollinger Basis")\n\n// Plot RSI for visual confirmation\nhline(rsiOverbought, "Overbought", color=color.red)\nhline(rsiOversold, "Oversold", color=color.green)\nplot(rsi, color=color.purple, title="RSI")\n\n'

class SMHighWinRateTrendMeanReversionTradingStrategy169ad2(PinePortBase, IStrategy):
    source_id = "SM_169ad2bf57566768"
    source_file = '高胜率趋势均值回归交易策略-High-Win-Rate-Trend-Mean-Reversion-Trading-Strategy.md'
    timeframe = '2d'
    can_short = True
    source_defaults = {'bbLength': 20, 'bbMult': 2, 'rsiLength': 14, 'rsiOverbought': 70, 'rsiOversold': 30, 'atrLength': 14}
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
