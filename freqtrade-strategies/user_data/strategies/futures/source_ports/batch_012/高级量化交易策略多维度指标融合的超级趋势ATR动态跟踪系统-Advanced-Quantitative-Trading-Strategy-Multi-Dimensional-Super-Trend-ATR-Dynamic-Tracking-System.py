"""batch_012 port of 高级量化交易策略多维度指标融合的超级趋势ATR动态跟踪系统-Advanced-Quantitative-Trading-Strategy-Multi-Dimensional-Super-Trend-ATR-Dynamic-Tracking-System.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2024-02-22 00:00:00\nend: 2025-02-19 08:00:00\nperiod: 1h\nbasePeriod: 1h\nexchanges: [{"eid":"Binance","currency":"ETH_USDT"}]\n*/\n\n//@version=6\nstrategy("ETH 超级趋势增强策略-精简版", overlay=true, initial_capital=10000, default_qty_type=strategy.percent_of_equity, default_qty_value=100)\n\n// —————————— 参数配置区 ——————————\n// 超级趋势参数\natrPeriod = input.int(8, "ATR周期（8-10）", minval=8, maxval=10)\nfactor = input.float(3.5, "乘数（3.5-4）", minval=3.5, maxval=4, step=0.1)\n\n// MACD参数\nfastLength = input.int(10, "MACD快线周期")\nslowLength = input.int(21, "MACD慢线周期")\nsignalLength = input.int(7, "信号线周期")\n\n// ADX参数\nadxLength = input.int(18, "ADX周期")\nadxThreshold = input.int(28, "ADX趋势阈值")\n\n// 成交量验证\nvolFilterRatio = input.float(1.8, "成交量放大倍数", step=0.1)\n\n// ATR止损\natrStopMulti = input.float(2.2, "ATR止损乘数", step=0.1)\n\n// —————————— 核心指标计算 ——————————\n// 1. 超级趋势（修复索引使用）\n[supertrend, direction] = ta.supertrend(factor, atrPeriod)\nplot(supertrend, color=direction < 0 ? color.new(color.green, 0) : color.new(color.red, 0), linewidth=2)\n\n// 2. MACD指标\n[macdLine, signalLine, histLine] = ta.macd(close, fastLength, slowLength, signalLength)\nmacdCol = histLine > histLine[1] ? color.green : color.red\n\n// 3. ADX趋势强度\n[DIMinus, DIPlus, ADX] = ta.dmi(adxLength, adxLength)\n\n// 4. 成交量验证\nvolMA = ta.sma(volume, 20)\nvolValid = volume > volMA * volFilterRatio\n\n// 5. ATR动态止损\natrVal = ta.atr(14)\nvar float stopPrice = na\n\n// —————————— 三重背离检测 ——————————\n// RSI背离检测\nrsiVal = ta.rsi(close, 14)\npriceHigh = ta.highest(high, 5)\nrsiHigh = ta.highest(rsiVal, 5)\ndivergenceRSI = high >= priceHigh[1] and rsiVal < rsiHigh[1]\n\n// MACD柱状图背离\nmacdHigh = ta.highest(histLine, 5)\ndivergenceMACD = high >= priceHigh[1] and histLine < macdHigh[1]\n\n// 成交量背离\nvolHigh = ta.highest(volume, 5)\ndivergenceVol = high >= priceHigh[1] and volume < volHigh[1]\n\ntripleDivergence = divergenceRSI and divergenceMACD and divergenceVol\n\n// —————————— 信号生成逻辑 ——————————\n// 多头条件（6层过滤）\nlongCondition = \n  direction < 0 and            // 超级趋势看涨\n  histLine > 0 and             // MACD柱在零轴上方\n  ADX > adxThreshold and       // 趋势强度达标\n  close > open and             // 阳线确认\n  volValid and                 // 成交量验证\n  not tripleDivergence         // 无三重顶背离\n\n// 空头条件（精简条件）\nshortCondition = \n  direction > 0 and            // 超级趋势看跌\n  histLine < 0 and             // MACD柱在零轴下方\n  ADX > adxThreshold and       // 趋势强度达标\n  close < open and             // 阴线确认\n  volValid and                 // 成交量验证\n  tripleDivergence             // 出现三重顶背离\n\n// —————————— 交易执行模块 ——————————\nif (longCondition)\n    strategy.entry("Long", strategy.long)\n    stopPrice := close - atrVal * atrStopMulti\n\nif (shortCondition)\n    strategy.entry("Short", strategy.short)\n    stopPrice := close + atrVal * atrStopMulti\n\n// 动态止损触发\nstrategy.exit("Exit Long", "Long", stop=stopPrice)\nstrategy.exit("Exit Short", "Short", stop=stopPrice)\n\n// 趋势反转离场\nif (direction > 0 and strategy.position_size > 0)\n    strategy.close("Long")\n    \nif (direction < 0 and strategy.position_size < 0)\n    strategy.close("Short")\n\n// —————————— 可视化提示 ——————————\nplotshape(longCondition, style=shape.triangleup, location=location.belowbar, color=color.green, size=size.small, title="买入信号")\nplotshape(shortCondition, style=shape.triangledown, location=location.abovebar, color=color.red, size=size.small, title="卖出信号")\nplot(strategy.position_size != 0 ? stopPrice : na, color=color.orange, style=plot.style_linebr, linewidth=2, title="动态止损线")\n\n// —————————— 预警系统 ——————————\nalertcondition(tripleDivergence, title="三重顶背离预警", message="ETH出现三重顶背离！")\n\nlongCondition := longCondition \n'

class SMATRAdvancedQuantitativeTradingStrategyMultiDimensionalS4cc63f(PinePortBase, IStrategy):
    source_id = "SM_4cc63f0685823425"
    source_file = '高级量化交易策略多维度指标融合的超级趋势ATR动态跟踪系统-Advanced-Quantitative-Trading-Strategy-Multi-Dimensional-Super-Trend-ATR-Dynamic-Tracking-System.md'
    timeframe = '1h'
    can_short = True
    source_defaults = {'atrPeriod': 8, 'factor': 3.5, 'fastLength': 10, 'slowLength': 21, 'signalLength': 7, 'adxLength': 18, 'adxThreshold': 28, 'volFilterRatio': 1.8, 'atrStopMulti': 2.2}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 100
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 10000
    source_reproduce_stops = True
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_012 md and exposed through the same PinePortBase interface used by batch_001.', 'The source reads live strategy position state; batch_001-style broker-state parity must be checked manually for this file.']

    def pine_indicators(self, dataframe, params):
        # Runtime evaluates the source against the complete OHLCV frame.
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch012Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
