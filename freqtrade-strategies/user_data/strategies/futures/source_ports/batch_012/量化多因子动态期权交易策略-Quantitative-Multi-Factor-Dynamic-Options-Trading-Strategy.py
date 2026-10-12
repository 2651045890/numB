"""batch_012 port of 量化多因子动态期权交易策略-Quantitative-Multi-Factor-Dynamic-Options-Trading-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2024-03-31 00:00:00\nend: 2025-03-29 08:00:00\nperiod: 1h\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"ETH_USDT"}]\n*/\n\n//@version=6\nstrategy("Vinayz Options Stratergy", overlay=true, default_qty_type=strategy.percent_of_equity, default_qty_value=2)\n\n// ---- Input Parameters ----\natrPeriod = input(14, title="ATR Period")\nbbLength = input(20, title="BB Period")\nbbStdDev = input(2, title="BB Std Dev")\nrsiPeriod = input(14, title="RSI Period")\natrMultiplier = input(1.5, title="ATR Trailing Stop Multiplier")\nvwapLength = input(20, title="VWAP Length")\ntargetMultiplier = input(2, title="Target Multiplier") // Target set at 2x ATR\nmaxHoldingBars = input(3, title="Max Holding Period (Bars)")\n\n// ---- Indicator Calculations ----\natrValue = ta.atr(atrPeriod)\nsmaValue = ta.sma(close, bbLength)\nupperBB = smaValue + bbStdDev * ta.stdev(close, bbLength)\nlowerBB = smaValue - bbStdDev * ta.stdev(close, bbLength)\nrsiValue = ta.rsi(close, rsiPeriod)\nvwap = ta.vwma(close, vwapLength)\n\n// ---- Volume Spike/Breakout Detection ----\nvolSMA = ta.sma(volume, 10)\nvolSpike = volume > volSMA * 1.5\n\n// ---- ATR Volatility Filter to Avoid Low Volatility Zones ----\natrFilter = atrValue > ta.sma(atrValue, 20) * 0.5\n\n// ---- Long Call Entry Conditions ----\nlongCE = ta.crossover(close, upperBB) and rsiValue > 60 and volSpike and close > vwap and atrFilter\n// ---- Long Put Entry Conditions ----\nlongPE = ta.crossunder(close, lowerBB) and rsiValue < 40 and volSpike and close < vwap and atrFilter\n\n// ---- Stop Loss and Target Calculation ----\nlongStopLoss = strategy.position_size > 0 ? strategy.position_avg_price - atrMultiplier * atrValue : na\nshortStopLoss = strategy.position_size < 0 ? strategy.position_avg_price + atrMultiplier * atrValue : na\nlongTarget = strategy.position_size > 0 ? strategy.position_avg_price + targetMultiplier * atrValue : na\nshortTarget = strategy.position_size < 0 ? strategy.position_avg_price - targetMultiplier * atrValue : na\n\n// ---- Buy/Sell Logic ----\nif (longCE)\n    strategy.entry("CE Entry", strategy.long)\n    label.new(bar_index, high, "BUY CE", color=color.green, textcolor=color.white, yloc=yloc.abovebar, size=size.small, tooltip="Buy CE Triggered")\n\nif (longPE)\n    strategy.entry("PE Entry", strategy.short)\n    label.new(bar_index, low, "BUY PE", color=color.red, textcolor=color.white, yloc=yloc.belowbar, size=size.small, tooltip="Buy PE Triggered")\n\n// ---- Exit Conditions ----\nif (strategy.position_size > 0)\n    // Exit Long CE on Target Hit\n    if (close >= longTarget)\n        strategy.close("CE Entry", comment="CE Target Hit")\n    // Exit Long CE on Stop Loss\n    if (close <= longStopLoss)\n        strategy.close("CE Entry", comment="CE Stop Loss Hit")\n    // Time-Based Exit after 3 candles\n    if (bar_index - strategy.opentrades.entry_bar_index(strategy.opentrades - 1) >= maxHoldingBars)\n        strategy.close("CE Entry", comment="CE Timed Exit")\n\nif (strategy.position_size < 0)\n    // Exit Short PE on Target Hit\n    if (close <= shortTarget)\n        strategy.close("PE Entry", comment="PE Target Hit")\n    // Exit Short PE on Stop Loss\n    if (close >= shortStopLoss)\n        strategy.close("PE Entry", comment="PE Stop Loss Hit")\n    // Time-Based Exit after 3 candles\n    if (bar_index - strategy.opentrades.entry_bar_index(strategy.opentrades - 1) >= maxHoldingBars)\n        strategy.close("PE Entry", comment="PE Timed Exit")\n\n// ---- Plotting ----\nplot(upperBB, color=color.green, title="Upper BB")\nplot(lowerBB, color=color.red, title="Lower BB")\nplot(rsiValue, title="RSI", color=color.blue, linewidth=1)\nhline(60, "Overbought", color=color.blue)\nhline(40, "Oversold", color=color.blue)\nplot(vwap, color=color.orange, linewidth=1, title="VWAP")\n\n// ---- Plot Volume Breakout/Spike ----\nbarcolor(volSpike ? color.yellow : na, title="Volume Spike Indicator")\n\n//plotshape(volSpike, title="Volume Breakout", location=location.bottom, style=shape.triangleup, color=color.purple, size=size.small, text="Spike")\n\n// ---- Alerts ----\nalertcondition(longCE, "CE Buy Alert", "Bank Nifty CE Buy Triggered!")\nalertcondition(longPE, "PE Buy Alert", "Bank Nifty PE Buy Triggered!")\n\n'

class SMQuantitativeMultiFactorDynamicOptionsTradingStrategy42de2c(PinePortBase, IStrategy):
    source_id = "SM_42de2c489415ad72"
    source_file = '量化多因子动态期权交易策略-Quantitative-Multi-Factor-Dynamic-Options-Trading-Strategy.md'
    timeframe = '1h'
    can_short = True
    source_defaults = {'atrPeriod': 14, 'bbLength': 20, 'bbStdDev': 2, 'rsiPeriod': 14, 'atrMultiplier': 1.5, 'vwapLength': 20, 'maxHoldingBars': 3}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 2
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
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
