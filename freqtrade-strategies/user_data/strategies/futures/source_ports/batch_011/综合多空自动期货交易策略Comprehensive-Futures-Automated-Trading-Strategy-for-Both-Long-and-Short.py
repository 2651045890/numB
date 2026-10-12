"""batch_011 port of 综合多空自动期货交易策略Comprehensive-Futures-Automated-Trading-Strategy-for-Both-Long-and-Short.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2024-01-01 00:00:00\nend: 2024-01-31 23:59:59\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=4\n//author：盧振興 芙蓉中華中學畢業 育達科技大學畢業碩士\n//參考資料 : QQE MOD By:Mihkel00 ,SuperTrend By:KivancOzbilgic , TrendIndicator A-V2 By:Dziwne\n\nstrategy("綜合交易策略", shorttitle="Comprehensive Strategy", overlay=true)\n\n// 添加單邊或多空參數\nOnlyLong = input(true, title="單邊")\n\n// SuperTrend 参数\nPeriodsST = input(9, title="ST ATR Period")\nMultiplierST = input(3.9, title="ST ATR Multiplier")\nsrcST = input(hl2, title="ST Source")\n\natrST = atr(PeriodsST)\nupST = srcST - (MultiplierST * atrST)\nupST := close[2] > upST[1] ? max(upST, upST[1]) : upST\ndnST = srcST + (MultiplierST * atrST)\ndnST := close[2] < dnST[1] ? min(dnST, dnST[1]) : dnST\ntrendST = 1\ntrendST := nz(trendST[1], trendST)\ntrendST := trendST == -1 and close[2] > dnST[1] ? 1 : trendST == 1 and close[2] < upST[1] ? -1 : trendST\n\n// QQE 参数\nRSI_PeriodQQE = input(6, title=\'QQE RSI Length\')\nSFQQE = input(5, title=\'QQE RSI Smoothing\')\nQQE = input(3, title=\'QQE Fast Factor\')\nThreshHoldQQE = input(3, title="QQE Thresh-hold")\nsrcQQE = input(close, title="QQE RSI Source")\n\nWilders_PeriodQQE = RSI_PeriodQQE * 2 - 1\n\nRsiQQE = rsi(srcQQE, RSI_PeriodQQE)\nRsiMaQQE = ema(RsiQQE, SFQQE)\nAtrRsiQQE = abs(RsiMaQQE[1] - RsiMaQQE)\nMaAtrRsiQQE = ema(AtrRsiQQE, Wilders_PeriodQQE)\ndarQQE = ema(MaAtrRsiQQE, Wilders_PeriodQQE) * QQE\n\nbasisQQE = sma(RsiMaQQE - 50, 50)\ndevQQE = 0.35 * stdev(RsiMaQQE - 50, 50)\nupperQQE = basisQQE + devQQE\nlowerQQE = basisQQE - devQQE\n\nqqeCondition = RsiMaQQE[1] - 50 > upperQQE[1] ? true : RsiMaQQE[1] - 50 < lowerQQE[1] ? false : na\n\n// Trend Indicator A-V2 参数\nma_periodA_V2 = input(52, title="TIA-V2 EMA Period")\noA_V2 = ema(open, ma_periodA_V2)\ncA_V2 = ema(close, ma_periodA_V2)\ntrendIndicatorAV2Condition = cA_V2[1] >= oA_V2[1] ? true : false\n\n// 综合交易逻辑\nlongCondition = trendST == 1 and qqeCondition and trendIndicatorAV2Condition\nshortCondition = trendST == -1 and not qqeCondition and not trendIndicatorAV2Condition\n\n// 针对多单的开平仓逻辑\nif (OnlyLong)\n    if (longCondition)\n        strategy.entry("Buy", strategy.long)        \n    else\n        strategy.close("Buy")\n\n// 多空都做时的逻辑\nif (not OnlyLong)\n    if (longCondition)\n        strategy.entry("Buy", strategy.long)\n    else if (shortCondition)\n        strategy.entry("Sell",strategy.short)\n\n    // 添加多空平仓逻辑\n    if (not longCondition)\n        strategy.close("Buy")\n    if (not shortCondition)\n        strategy.close("Sell")\n\n// 可视化信号\nplotshape(series=longCondition, title="Buy Signal", location=location.belowbar, color=color.green, style=shape.labelup, text="BUY")\nplotshape(series=shortCondition and not OnlyLong, title="Sell Signal", location=location.abovebar, color=color.red, style=shape.labeldown, text="SELL")\n'

class SMA43EB57598435868(PinePortBase, IStrategy):
    source_id = "SM_a43eb57598435868"
    source_file = '综合多空自动期货交易策略Comprehensive-Futures-Automated-Trading-Strategy-for-Both-Long-and-Short.md'
    timeframe = '1h'
    can_short = True
    source_defaults = {'OnlyLong': True, 'PeriodsST': 9, 'MultiplierST': 3.9, 'RSI_PeriodQQE': 6, 'SFQQE': 5, 'QQE': 3, 'ThreshHoldQQE': 3, 'ma_periodA_V2': 52}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
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
