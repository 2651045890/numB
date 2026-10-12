"""batch_012 port of 黄金趋势通道反转突破动量策略-Gold-Trend-Channel-Reversal-Momentum-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2019-12-23 08:00:00\nend: 2024-12-09 08:00:00\nperiod: 1d\nbasePeriod: 1d\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("Gold Scalping Strategy with Precise Entries", overlay=true)\n\n// Inputs for EMAs and ATR\nema50 = ta.ema(close, 50)\nema200 = ta.ema(close, 200)\natr = ta.atr(14)\nrsi = ta.rsi(close, 14)\n\n// Set 50 pips for gold (assuming 1 pip = 0.10 movement in XAU/USD)\npip_target = 20 * 0.10\n\n// Bullish/Bearish Engulfing Pattern\nbullish_engulfing = close > open and close[1] < open[1] and close > close[1] and open < close[1]\nbearish_engulfing = close < open and close[1] > open[1] and close < close[1] and open > close[1]\n\n// Define trend and exact entry conditions\nlongCondition = (ema50 > ema200) and (rsi >= 45 and rsi <= 55) and (bullish_engulfing) and (close > ema50)\nshortCondition = (ema50 < ema200) and (rsi >= 45 and rsi <= 55) and (bearish_engulfing) and (close < ema50)\n\n// ATR-based stop loss\nlongStopLoss = close - atr\nshortStopLoss = close + atr\n\n// Entry Conditions with precise points\nif (longCondition)\n    strategy.entry("Long", strategy.long)\n    strategy.exit("Take Profit/Stop Loss", "Long", limit=close + pip_target, stop=longStopLoss)\n\nif (shortCondition)\n    strategy.entry("Short", strategy.short)\n    strategy.exit("Take Profit/Stop Loss", "Short", limit=close - pip_target, stop=shortStopLoss)\n\n// Plot EMAs\nplot(ema50, color=color.green, title="50 EMA")\nplot(ema200, color=color.red, title="200 EMA")\n\n// Plot Buy/Sell Signals\nplotshape(series=longCondition, location=location.belowbar, color=color.green, style=shape.labelup, title="Buy Signal", text="BUY")\nplotshape(series=shortCondition, location=location.abovebar, color=color.red, style=shape.labeldown, title="Sell Signal", text="SELL")\n\n'

class SMGoldTrendChannelReversalMomentumStrategy26f125(PinePortBase, IStrategy):
    source_id = "SM_26f125ce61a4c033"
    source_file = '黄金趋势通道反转突破动量策略-Gold-Trend-Channel-Reversal-Momentum-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {}
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
