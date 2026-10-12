"""batch_012 port of 随机震荡策略Random-Oscillation-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2022-10-30 00:00:00\nend: 2023-11-05 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=2\nstrategy("Ichimoku Kinko Hyo + HULL-MA_X + MacD", shorttitle="@m", overlay=true, default_qty_type=strategy.percent_of_equity, max_bars_back=1000, default_qty_value=100, calc_on_order_fills= true, calc_on_every_tick=true, pyramiding=0)\n\nkeh=input(title="Double HullMA",defval=12, minval=1)\n\nn2ma=2*wma(close,round(keh/2))\nnma=wma(close,keh)\ndiff=n2ma-nma\nsqn=round(sqrt(keh))\nn2ma1=2*wma(close[1],round(keh/2))\nnma1=wma(close[1],keh)\ndiff1=n2ma1-nma1\nsqn1=round(sqrt(keh))\nn1=wma(diff,sqn)\nn2=wma(diff1,sqn)\nb=n1>n2?lime:red\nc=n1>n2?green:red\nd=n1>n2?red:green\n\nTenkanSenPeriods = input(9, minval=1, title="Tenkan Sen Periods")\nKijunSenPeriods = input(24, minval=1, title="Kijun Sen Periods")\nSenkouSpanBPeriods = input(51, minval=1, title="Senkou Span B Periods")\ndisplacement = input(24, minval=1, title="Displacement")\ndonchian(len) => avg(lowest(len), highest(len))\nTenkanSen = donchian(TenkanSenPeriods)\nKijunSen = donchian(KijunSenPeriods)\nSenkouSpanA = avg(TenkanSen, KijunSen)\nSenkouSpanB = donchian(SenkouSpanBPeriods)\nLS=close, offset = -displacement\n\nMACD_Length = input(9)\nMACD_fastLength = input(12)\nMACD_slowLength = input(24)\nMACD = ema(close, MACD_fastLength) - ema(close, MACD_slowLength)\naMACD = ema(MACD, MACD_Length)\n\na1=plot(n1,color=c)\na2=plot(n2,color=c)\nplot(cross(n1, n2) ? n1 : na, style = circles, color=b, linewidth = 4)\nplot(cross(n1, n2) ? n1 : na, style = line, color=d, linewidth = 3)\nplot(TenkanSen, color=blue, title="Tenkan Sen", linewidth = 2)\nplot(KijunSen, color=maroon, title="Kijun Sen", linewidth = 3)\nplot(close, offset = -displacement, color=orange, title="Chikou Span", linewidth = 2)\np1=plot (SenkouSpanA, offset = displacement, color=green,  title="Senkou Span A", linewidth = 2)\np2=plot (SenkouSpanB, offset = displacement, color=red,  title="Senkou Span B", linewidth = 3)\nfill(p1, p2, color = SenkouSpanA > SenkouSpanB ? green : red)\n\ncloselong = n1<n2 and close<n2 and (MACD<aMACD or TenkanSen<KijunSen or close<KijunSen)\nif (closelong)\n    strategy.close("Long")\n\ncloseshort = n1>n2 and close>n2 and (MACD>aMACD or TenkanSen>KijunSen or close>KijunSen)\nif (closeshort)\n    strategy.close("Short")\n\nlongCondition = n1>n2 and close>n2 and MACD>aMACD and (TenkanSen>KijunSen or close>KijunSen) \nif (longCondition)\n    strategy.entry("Long",strategy.long)\n\nshortCondition = n1<n2 and close<n2 and MACD<aMACD and (TenkanSen<KijunSen or close<KijunSen)\nif (shortCondition)\n    strategy.entry("Short",strategy.short)\n'

class SMRandomOscillationStrategyb0a21d(PinePortBase, IStrategy):
    source_id = "SM_b0a21db303a88848"
    source_file = '随机震荡策略Random-Oscillation-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'keh': 12, 'TenkanSenPeriods': 9, 'KijunSenPeriods': 24, 'SenkouSpanBPeriods': 51, 'displacement': 24, 'MACD_Length': 9, 'MACD_fastLength': 12, 'MACD_slowLength': 24}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 100
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
