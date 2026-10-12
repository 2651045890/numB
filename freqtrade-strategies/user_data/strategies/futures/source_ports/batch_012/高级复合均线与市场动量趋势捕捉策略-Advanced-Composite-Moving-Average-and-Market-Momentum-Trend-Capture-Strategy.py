"""batch_012 port of 高级复合均线与市场动量趋势捕捉策略-Advanced-Composite-Moving-Average-and-Market-Momentum-Trend-Capture-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '//@version=4\nstrategy("Private Strategy TradingView", shorttitle="Private Strategy TradingView", overlay=true)\n\nkeh = input(title="Double HullMA", type=input.integer, defval=12, minval=1)\nn2ma = 2 * wma(close, round(keh / 2))\nnma = wma(close, keh)\ndiff = n2ma - nma\nsqn = round(sqrt(keh))\nn2ma1 = 2 * wma(close[1], round(keh / 2))\nnma1 = wma(close[1], keh)\ndiff1 = n2ma1 - nma1\nsqn1 = round(sqrt(keh))\nn1 = wma(diff, sqn)\nn2 = wma(diff1, sqn)\n\nTenkanSenPeriods = input(9, minval=1, title="Tenkan Sen Periods")\nKijunSenPeriods = input(24, minval=1, title="Kijun Sen Periods")\nSenkouSpanBPeriods = input(51, minval=1, title="Senkou Span B Periods")\ndisplacement = input(24, minval=1, title="Displacement")\ndonchian(len) => avg(lowest(low, len), highest(high, len))\nTenkanSen = donchian(TenkanSenPeriods)\nKijunSen = donchian(KijunSenPeriods)\nSenkouSpanA = avg(TenkanSen, KijunSen)\nSenkouSpanB = donchian(SenkouSpanBPeriods)\nSenkouSpanH = max(SenkouSpanA[displacement - 1], SenkouSpanB[displacement - 1])\nSenkouSpanL = min(SenkouSpanA[displacement - 1], SenkouSpanB[displacement - 1])\nChikouSpan = close[displacement - 1]\n\nlongCondition = n1 > n2 and close > n2 and close > ChikouSpan and close > SenkouSpanH and (TenkanSen >= KijunSen or close > KijunSen)\nif (longCondition)\n    strategy.entry("Long", strategy.long)\n\nshortCondition = n1 < n2 and close < n2 and close < ChikouSpan and close < SenkouSpanL and (TenkanSen <= KijunSen or close < KijunSen)\nif (shortCondition)\n    strategy.entry("Short", strategy.short)\n\ncloselong = n1 < n2 and (close < n2 or TenkanSen < KijunSen or close < TenkanSen or close < KijunSen or close < SenkouSpanH or close < ChikouSpan)\nif (closelong)\n    strategy.close("Long")\n\ncloseshort = n1 > n2 and (close > n2 or TenkanSen > KijunSen or close > TenkanSen or close > KijunSen or close > SenkouSpanL or close > ChikouSpan)\nif (closeshort)\n    strategy.close("Short")\n\n'

class SMAdvancedCompositeMovingAverageandMarketMomentumTrendCap043bbb(PinePortBase, IStrategy):
    source_id = "SM_043bbbef6776b0a5"
    source_file = '高级复合均线与市场动量趋势捕捉策略-Advanced-Composite-Moving-Average-and-Market-Momentum-Trend-Capture-Strategy.md'
    timeframe = '1h'
    can_short = True
    source_defaults = {'keh': 12, 'TenkanSenPeriods': 9, 'KijunSenPeriods': 24, 'SenkouSpanBPeriods': 51, 'displacement': 24}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_reproduce_stops = False
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_012 md and exposed through the same PinePortBase interface used by batch_001.', 'Custom Pine function(s) are present; the original source is embedded verbatim and this generic pass flags them for per-strategy semantic verification.']

    def pine_indicators(self, dataframe, params):
        # Runtime evaluates the source against the complete OHLCV frame.
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch012Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
