"""batch_012 port of 高频价格失衡区域动量交易策略基于指数均线和ATR动态止盈止损-High-Frequency-Fair-Value-Gap-Momentum-Trading-Strategy-with-EMA-and-ATR-Based-Dynamic-Exit.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2024-02-21 00:00:00\nend: 2025-02-01 08:00:00\nperiod: 1d\nbasePeriod: 1d\nexchanges: [{"eid":"Binance","currency":"ETH_USDT"}]\n*/\n\n//@version=5\nstrategy("Effective FVG Strategy - Forex", overlay=true, default_qty_type=strategy.percent_of_equity, default_qty_value=10)\n\n// === Exponential Moving Averages for Faster Trend Detection ===\nema50 = ta.ema(close, 50)\nema200 = ta.ema(close, 200)\nbullishTrend = ema50 > ema200\nbearishTrend = ema50 < ema200\n\n// === Volume & Imbalance Filters ===\nhighVolume = volume > ta.sma(volume, 20) * 1.5  // 1.5x higher than average volume\nstrongImbalance = math.abs(close - open) > ta.sma(math.abs(close - open), 20)  // Large price movement\n\n// === Fair Value Gap (FVG) Detection ===\nfvgUp = low[2] > high[0]  // Bullish FVG\nfvgDown = high[2] < low[0]  // Bearish FVG\n\n// Effective FVGs with trend confirmation\nvalidBullFVG = fvgUp and highVolume and strongImbalance and bullishTrend\nvalidBearFVG = fvgDown and highVolume and strongImbalance and bearishTrend\n\n// === ATR-based Take Profit & Stop Loss (Optimized for Forex) ===\natr = ta.atr(14)\nlongTP = close + (2 * atr)  // TP = 2x ATR\nlongSL = close - (1.2 * atr)  // SL = 1.2x ATR\nshortTP = close - (2 * atr)\nshortSL = close + (1.2 * atr)\n\n// === Execute Trades ===\nif validBullFVG\n    strategy.entry("Long", strategy.long)\n    strategy.exit("Long Exit", from_entry="Long", limit=longTP, stop=longSL)\n\nif validBearFVG\n    strategy.entry("Short", strategy.short)\n    strategy.exit("Short Exit", from_entry="Short", limit=shortTP, stop=shortSL)\n\n// === Plot Buy/Sell Signals ===\nplotshape(series=validBullFVG, location=location.belowbar, color=color.green, style=shape.labelup, text="BUY", title="BUY Signal")\nplotshape(series=validBearFVG, location=location.abovebar, color=color.red, style=shape.labeldown, text="SELL", title="SELL Signal")\n\n// Highlight Significant FVGs\nbgcolor(validBullFVG ? color.new(color.green, 85) : na)\nbgcolor(validBearFVG ? color.new(color.red, 85) : na)\n\n'

class SMATRHighFrequencyFairValueGapMomentumTradingStrategywitha74a07(PinePortBase, IStrategy):
    source_id = "SM_a74a0734d5cb990c"
    source_file = '高频价格失衡区域动量交易策略基于指数均线和ATR动态止盈止损-High-Frequency-Fair-Value-Gap-Momentum-Trading-Strategy-with-EMA-and-ATR-Based-Dynamic-Exit.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 10
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
