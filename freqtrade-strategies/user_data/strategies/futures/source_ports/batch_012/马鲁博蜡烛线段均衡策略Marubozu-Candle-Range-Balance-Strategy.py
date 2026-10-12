"""batch_012 port of 马鲁博蜡烛线段均衡策略Marubozu-Candle-Range-Balance-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2024-01-01 00:00:00\nend: 2024-01-31 23:59:59\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=4\n\nstrategy(title="Marubozu", shorttitle="Marubozu", overlay=true, initial_capital = 1000, default_qty_type=strategy.percent_of_equity, default_qty_value=100, commission_type=strategy.commission.percent , commission_value=0 )\n\nC_Len = 14 // ema depth for bodyAvg\nC_ShadowPercent = 5.0 // size of shadows\nC_ShadowEqualsPercent = 100.0\nC_DojiBodyPercent = 5.0\nC_Factor = 2.0 // shows the number of times the shadow dominates the candlestick body\n\nC_BodyHi = max(close, open)\nC_BodyLo = min(close, open)\nC_Body = C_BodyHi - C_BodyLo\nC_BodyAvg = ema(C_Body, C_Len)\nC_SmallBody = C_Body < C_BodyAvg\nC_LongBody = C_Body > C_BodyAvg\nC_UpShadow = high - C_BodyHi\nC_DnShadow = C_BodyLo - low\nC_HasUpShadow = C_UpShadow > C_ShadowPercent / 100 * C_Body\nC_HasDnShadow = C_DnShadow > C_ShadowPercent / 100 * C_Body\nC_WhiteBody = open < close\nC_BlackBody = open > close\nC_Range = high-low\nC_IsInsideBar = C_BodyHi[1] > C_BodyHi and C_BodyLo[1] < C_BodyLo\nC_BodyMiddle = C_Body / 2 + C_BodyLo\nC_ShadowEquals = C_UpShadow == C_DnShadow or (abs(C_UpShadow - C_DnShadow) / C_DnShadow * 100) < C_ShadowEqualsPercent and (abs(C_DnShadow - C_UpShadow) / C_UpShadow * 100) < C_ShadowEqualsPercent\nC_IsDojiBody = C_Range > 0 and C_Body <= C_Range * C_DojiBodyPercent / 100\nC_Doji = C_IsDojiBody and C_ShadowEquals\n\npatternLabelPosLow = low - (atr(30) * 0.6)\npatternLabelPosHigh = high + (atr(30) * 0.6)\n\nC_MarubozuWhiteBullishNumberOfCandles = 1\nC_MarubozuShadowPercentWhite = 5.0\nC_MarubozuWhiteBullish = C_WhiteBody and C_LongBody and C_UpShadow <= C_MarubozuShadowPercentWhite/100*C_Body and C_DnShadow <= C_MarubozuShadowPercentWhite/100*C_Body and C_WhiteBody\nalertcondition(C_MarubozuWhiteBullish, title = "Marubozu White", message = "New Marubozu White - Bullish pattern detected.")\nif C_MarubozuWhiteBullish\n    var ttBullishMarubozuWhite = "Marubozu White\\nA Marubozu White Candle is a candlestick that does not have a shadow that extends from its candle body at either the open or the close. Marubozu is Japanese for “close-cropped” or “close-cut.” Other sources may call it a Bald or Shaven Head Candle."\n    label.new(bar_index, patternLabelPosLow, text="MW", style=label.style_label_up, color = color.blue, textcolor=color.white, tooltip = ttBullishMarubozuWhite)\nbgcolor(highest(C_MarubozuWhiteBullish?1:0, C_MarubozuWhiteBullishNumberOfCandles)!=0 ? color.blue : na, offset=-(C_MarubozuWhiteBullishNumberOfCandles-1))\n\nC_MarubozuBlackBearishNumberOfCandles = 1\nC_MarubozuShadowPercentBearish = 5.0\nC_MarubozuBlackBearish = C_BlackBody and C_LongBody and C_UpShadow <= C_MarubozuShadowPercentBearish/100*C_Body and C_DnShadow <= C_MarubozuShadowPercentBearish/100*C_Body and C_BlackBody\nalertcondition(C_MarubozuBlackBearish, title = "Marubozu Black", message = "New Marubozu Black - Bearish pattern detected.")\nif C_MarubozuBlackBearish\n    var ttBearishMarubozuBlack = "Marubozu Black\\nThis is a candlestick that has no shadow, which extends from the red-bodied candle at the open, the close, or even at both. In Japanese, the name means “close-cropped” or “close-cut.” The candlestick can also be referred to as Bald or Shaven Head."\n    label.new(bar_index, patternLabelPosHigh, text="MB", style=label.style_label_down, color = color.red, textcolor=color.white, tooltip = ttBearishMarubozuBlack)\nbgcolor(highest(C_MarubozuBlackBearish?1:0, C_MarubozuBlackBearishNumberOfCandles)!=0 ? color.red : na, offset=-(C_MarubozuBlackBearishNumberOfCandles-1))\n\nstrategy.entry("short",1,when= C_MarubozuBlackBearish)\n\nstrategy.entry("long",0,when=C_MarubozuWhiteBullish)\n\nstrategy.close("long",when= close[1] < open[1]and close[2] < open[2] and close > open)\nstrategy.close("short",when= close[1] > open[1]and close[2] > open[2] and close < open)\n'

class SMMarubozuCandleRangeBalanceStrategy9ec93d(PinePortBase, IStrategy):
    source_id = "SM_9ec93d344f29a8fe"
    source_file = '马鲁博蜡烛线段均衡策略Marubozu-Candle-Range-Balance-Strategy.md'
    timeframe = '1h'
    can_short = False
    source_defaults = {}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 100
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000
    source_reproduce_stops = False
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_012 md and exposed through the same PinePortBase interface used by batch_001.']

    def pine_indicators(self, dataframe, params):
        # Runtime evaluates the source against the complete OHLCV frame.
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch012Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
