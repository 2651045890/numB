"""batch_012 port of 高频均值回归策略利用固定止损和获利目标的波动区间交易系统-High-Frequency-Mean-Reversion-Trading-System-with-Fixed-Stop-Loss-and-Take-Profit-for-Volatility-Zone-Trading.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2025-01-01 00:00:00\nend: 2025-03-31 00:00:00\nperiod: 1h\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"ETH_USDT"}]\n*/\n\n//@version=6\nstrategy("XAU/USD High-Frequency Mean Reversion with Fixed SL and TP", overlay=true, initial_capital=10000, default_qty_type=strategy.percent_of_equity, default_qty_value=1, commission_value=0.04)\n\n// === 1. BASIC INDICATORS ===\n[bbUpper, bbMiddle, bbLower] = ta.bb(close, 20, 2.5)  // Wider Bollinger Bands\nrsi = ta.rsi(close, 5)\nvwma = ta.vwma(close, 50)\n\n// === 2. EXTENDED PARAMETERS (INCREASED SIGNALS) ===\nrsiOverbought = input(75, "RSI Overbought")  // Increased from 72 to 75\nrsiOversold = input(25, "RSI Oversold")     // Decreased from 28 to 25\n\nbbMidUpper = bbMiddle + (bbUpper - bbMiddle) * 0.5\nbbMidLower = bbMiddle - (bbMiddle - bbLower) * 0.5\n\n// === 3. ENTRY CONDITIONS ===\nlongStrict = rsi <= rsiOversold and close <= bbLower and close > vwma\nshortStrict = rsi >= rsiOverbought and close >= bbUpper and close < vwma\n\n// Expanded signal (higher risk)\nlongAggressive = rsi <= rsiOversold + 5 and close <= bbMidLower and close > vwma\nshortAggressive = rsi >= rsiOverbought - 5 and close >= bbMidUpper and close < vwma\n\n// === 4. ADAPTIVE RISK MANAGEMENT ===\natr = ta.atr(14)  // ATR over 14 periods to measure volatility\nvolatility = ta.stdev(close, 14)  // Standard deviation of closing prices\n\nuseAdaptiveSL = input(true, "Use Adaptive SL")  // Enable Adaptive Stop Loss\nslMultiplier = useAdaptiveSL ? (volatility > ta.sma(volatility, 20) ? 2 : 1.5) : 1.8  // Adjust SL based on volatility\n\nstopLoss = atr * slMultiplier  // Stop Loss dynamically adjusts based on ATR and volatility\n\n// === 5. FIXED STOP LOSS & TAKE PROFIT SETTINGS ===\n// Fixed Stop Loss and Take Profit ratios (e.g., 1% Stop Loss and 2% Take Profit)\nstopLossPercentage = 0.01  // 1% Stop Loss\ntakeProfitPercentage = 0.02  // 2% Take Profit\n\n// Calculate Stop Loss and Take Profit levels based on percentage\nfixedStopLoss = close * stopLossPercentage\nfixedTakeProfit = close * takeProfitPercentage\n\n// === 6. LIMIT STOP LOSS TO 20 PIPS ===\n// Maximum Stop Loss of 20 pips (for XAU/USD, 1 pip = 0.01)\n// Ensure Stop Loss does not exceed 20 pips\nmaxStopLoss = 20 * syminfo.mintick  // Maximum Stop Loss = 20 pips\nfinalStopLoss = math.min(stopLoss, maxStopLoss)  // Use SL that does not exceed 20 pips\n\n// === 7. EXECUTION OF TRADES ===\nif (longStrict)\n    strategy.entry("Long Strict", strategy.long, stop=close-finalStopLoss, limit=close+fixedTakeProfit)\nif (shortStrict)\n    strategy.entry("Short Strict", strategy.short, stop=close+finalStopLoss, limit=close-fixedTakeProfit)\nif (longAggressive and strategy.position_size == 0)\n    strategy.entry("Long Aggressive", strategy.long, stop=close-finalStopLoss*1.2, limit=close+fixedTakeProfit*0.8)\nif (shortAggressive and strategy.position_size == 0)\n    strategy.entry("Short Aggressive", strategy.short, stop=close+finalStopLoss*1.2, limit=close-fixedTakeProfit*0.8)\n\n// === 8. DISPLAY ===\n// Remove TP/SL markers and labels, keeping only buy/sell signals\nplot(bbUpper, "BB Upper", color=color.blue)\nplot(bbLower, "BB Lower", color=color.blue)\nplot(bbMidUpper, "BB Mid-Upper", color=color.new(color.blue, 70), style=plot.style_circles)\nplot(bbMidLower, "BB Mid-Lower", color=color.new(color.blue, 70), style=plot.style_circles)\n\nplotshape(longStrict, "Buy Strict", shape.labelup, location.belowbar, color=color.new(#00FF00, 0), text="STRICT\\nBUY", size=size.small)\nplotshape(shortStrict, "Sell Strict", shape.labeldown, location.abovebar, color=color.new(#FF0000, 0), text="STRICT\\nSELL", size=size.small)\nplotshape(longAggressive, "Buy Aggressive", shape.triangleup, location.belowbar, color=color.new(#00AAFF, 0), size=size.small)\nplotshape(shortAggressive, "Sell Aggressive", shape.triangledown, location.abovebar, color=color.new(#FFAA00, 0), size=size.small)\n\n'

class SMHighFrequencyMeanReversionTradingSystemwithFixedStopLosca0aa1(PinePortBase, IStrategy):
    source_id = "SM_ca0aa1fd5d23a8ee"
    source_file = '高频均值回归策略利用固定止损和获利目标的波动区间交易系统-High-Frequency-Mean-Reversion-Trading-System-with-Fixed-Stop-Loss-and-Take-Profit-for-Volatility-Zone-Trading.md'
    timeframe = '1h'
    can_short = True
    source_defaults = {}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 1
    source_commission_percent = 0.04
    source_pyramiding = 0
    source_initial_capital = 10000
    source_reproduce_stops = False
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_012 md and exposed through the same PinePortBase interface used by batch_001.', 'The source reads live strategy position state; batch_001-style broker-state parity must be checked manually for this file.']

    def pine_indicators(self, dataframe, params):
        # Runtime evaluates the source against the complete OHLCV frame.
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch012Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
