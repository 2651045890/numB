"""batch_012 port of 高级WaveTrend与EMA-Ribbon融合交易策略-Advanced-WaveTrend-and-EMA-Ribbon-Fusion-Trading-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2024-12-06 00:00:00\nend: 2025-01-04 08:00:00\nperiod: 2h\nbasePeriod: 2h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("VuManChu Cipher A Strategy", overlay=true, initial_capital=10000, default_qty_type=strategy.fixed, default_qty_value=1.0)\n\n// === 函数定义 ===\n// WaveTrend函数\nf_wavetrend(_src, _chlen, _avg, _malen) =>\n    _esa = ta.ema(_src, _chlen)\n    _de = ta.ema(math.abs(_src - _esa), _chlen)\n    _ci = (_src - _esa) / (0.015 * _de)\n    _tci = ta.ema(_ci, _avg)\n    _wt1 = _tci\n    _wt2 = ta.sma(_wt1, _malen)\n    [_wt1, _wt2]\n\n// EMA Ribbon函数\nf_emaRibbon(_src, _e1, _e2, _e3, _e4, _e5, _e6, _e7, _e8) =>\n    _ema1 = ta.ema(_src, _e1)\n    _ema2 = ta.ema(_src, _e2)\n    _ema3 = ta.ema(_src, _e3)\n    _ema4 = ta.ema(_src, _e4)\n    _ema5 = ta.ema(_src, _e5)\n    _ema6 = ta.ema(_src, _e6)\n    _ema7 = ta.ema(_src, _e7)\n    _ema8 = ta.ema(_src, _e8)\n    [_ema1, _ema2, _ema3, _ema4, _ema5, _ema6, _ema7, _ema8]\n\n// === 变量声明 ===\nvar float stopPrice = na      // 止损价格变量\nvar float targetPrice = na    // 止盈价格变量\nvar float lastLongPrice = na\nvar float lastShortPrice = na\nvar float highestSinceLastLong = na\nvar float lowestSinceLastShort = na\n\n// === WaveTrend参数 ===\nwtChannelLen = input.int(9, title = \'WT Channel Length\')\nwtAverageLen = input.int(13, title = \'WT Average Length\')\nwtMASource = hlc3\nwtMALen = input.int(3, title = \'WT MA Length\')\n\n// === EMA Ribbon参数 ===\nema1Len = input.int(5, "EMA 1 Length")\nema2Len = input.int(11, "EMA 2 Length")\nema3Len = input.int(15, "EMA 3 Length")\nema4Len = input.int(18, "EMA 4 Length")\nema5Len = input.int(21, "EMA 5 Length")\nema6Len = input.int(24, "EMA 6 Length")\nema7Len = input.int(28, "EMA 7 Length")\nema8Len = input.int(34, "EMA 8 Length")\n\n// === 计算指标 ===\n// WaveTrend计算\n[wt1, wt2] = f_wavetrend(wtMASource, wtChannelLen, wtAverageLen, wtMALen)\n\n// WaveTrend交叉条件\nwtCross = ta.cross(wt1, wt2)\nwtCrossDown = wt2 - wt1 >= 0\n\n// EMA Ribbon计算\n[ema1, ema2, ema3, ema4, ema5, ema6, ema7, ema8] = f_emaRibbon(close, ema1Len, ema2Len, ema3Len, ema4Len, ema5Len, ema6Len, ema7Len, ema8Len)\n\n// === 交易信号 ===\nlongEma = ta.crossover(ema2, ema8)\nshortEma = ta.crossover(ema8, ema2)\nredCross = ta.crossunder(ema1, ema2)\nblueTriangle = ta.crossover(ema2, ema3)\nredDiamond = wtCross and wtCrossDown\nbloodDiamond = redDiamond and redCross\n\n// 更新最高最低价\nif not na(lastLongPrice)\n    highestSinceLastLong := math.max(high, nz(highestSinceLastLong))\nif not na(lastShortPrice)\n    lowestSinceLastShort := math.min(low, nz(lowestSinceLastShort))\n\n// === 交易信号条件 ===\nlongCondition = longEma or (blueTriangle and not bloodDiamond)\nshortCondition = shortEma or bloodDiamond\n\n// === 执行交易 ===\nif (longCondition)\n    // 记录多头入场价格\n    lastLongPrice := close\n    // 重置最高价跟踪\n    highestSinceLastLong := high\n    \n    stopPrice := nz(lowestSinceLastShort, close * 0.98)  // 使用前一个空头信号后的最低价作为止损\n    float riskAmount = math.abs(close - stopPrice)\n    targetPrice := close + (riskAmount * 2)  // 止盈为止损距离的2倍\n    \n    strategy.entry("做多", strategy.long)\n    strategy.exit("多头止盈止损", "做多", limit=targetPrice, stop=stopPrice)\n\nif (shortCondition)\n    // 记录空头入场价格\n    lastShortPrice := close\n    // 重置最低价跟踪\n    lowestSinceLastShort := low\n    \n    stopPrice := nz(highestSinceLastLong, close * 1.02)  // 使用前一个多头信号后的最高价作为止损\n    float riskAmount = math.abs(stopPrice - close)\n    targetPrice := close - (riskAmount * 3)  // 止盈为止损距离的2倍\n    \n    strategy.entry("做空", strategy.short)\n    strategy.exit("空头止盈止损", "做空", limit=targetPrice, stop=stopPrice)\n\n// === 绘制信号 ===\nplotshape(longCondition, style=shape.triangleup, color=color.green, location=location.belowbar, size=size.small, title="做多信号")\nplotshape(shortCondition, style=shape.triangledown, color=color.red, location=location.abovebar, size=size.small, title="做空信号")\n\n// 绘制止损线\nplot(strategy.position_size > 0 ? stopPrice : na, color=color.red, style=plot.style_linebr, linewidth=2, title="多头止损线")\nplot(strategy.position_size < 0 ? stopPrice : na, color=color.red, style=plot.style_linebr, linewidth=2, title="空头止损线")\n\n// 绘制止盈线\nplot(strategy.position_size > 0 ? targetPrice : na, color=color.green, style=plot.style_linebr, linewidth=2, title="多头止盈线")\nplot(strategy.position_size < 0 ? targetPrice : na, color=color.green, style=plot.style_linebr, linewidth=2, title="空头止盈线")\n'

class SMWaveTrendEMARibbonAdvancedWaveTrendandEMARibbonFusionTr27036a(PinePortBase, IStrategy):
    source_id = "SM_27036acb40caf6d3"
    source_file = '高级WaveTrend与EMA-Ribbon融合交易策略-Advanced-WaveTrend-and-EMA-Ribbon-Fusion-Trading-Strategy.md'
    timeframe = '2h'
    can_short = True
    source_defaults = {'wtChannelLen': 9, 'wtAverageLen': 13, 'wtMALen': 3, 'ema1Len': 5, 'ema2Len': 11, 'ema3Len': 15, 'ema4Len': 18, 'ema5Len': 21, 'ema6Len': 24, 'ema7Len': 28, 'ema8Len': 34}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 10000
    source_reproduce_stops = True
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_012 md and exposed through the same PinePortBase interface used by batch_001.', 'Custom Pine function(s) are present; the original source is embedded verbatim and this generic pass flags them for per-strategy semantic verification.', 'The source reads live strategy position state; batch_001-style broker-state parity must be checked manually for this file.']

    def pine_indicators(self, dataframe, params):
        # Runtime evaluates the source against the complete OHLCV frame.
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch012Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
