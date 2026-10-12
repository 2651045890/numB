"""batch_012 port of 高级区间突破多时间周期交易策略-Advanced-Multi-Timeframe-Range-Breakout-Trading-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2025-01-18 00:00:00\nend: 2025-02-17 00:00:00\nperiod: 6h\nbasePeriod: 6h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=6\nstrategy("Candle Range Theory Strategy", overlay=true)\n\n// Input parameters\nvar string HTF = input.timeframe("240", "Higher Timeframe (Minutes)")  // 4H default\nvar float stopLossMultiplier = input.float(1.5, "Stop Loss Multiplier", minval=0.5)\nvar bool useVolFilter = input.bool(false, "Use Volume Filter")\nvar float volThreshold = input.float(1.5, "Volume Threshold Multiplier", minval=1.0)\n\n// Function to get higher timeframe data\ngetHtfData(src) =>\n    request.security(syminfo.tickerid, HTF, src)\n\n// Calculate volume condition once per bar\nvar bool volCondition = true\nif useVolFilter\n    float vol = getHtfData(volume)\n    float avgVol = ta.sma(vol, 20)\n    volCondition := vol > avgVol * volThreshold\n\n// Get HTF candle data\nhtf_open = getHtfData(open)\nhtf_high = getHtfData(high)\nhtf_low = getHtfData(low)\nhtf_close = getHtfData(close)\n\n// Store previous candle data\nvar float h1 = na  // High of Candle 1\nvar float l1 = na  // Low of Candle 1\nvar float h2 = na  // High of Candle 2\nvar float l2 = na  // Low of Candle 2\nvar float prevClose = na\n\n// Track setup conditions\nvar string setupType = na\nvar float triggerLevel = na\nvar float targetLevel = na\nvar float stopLevel = na\n\n// Update candle data - fixed time function usage\nvar bool isNewBar = false\nisNewBar := ta.change(request.security(syminfo.tickerid, HTF, time)) != 0\n\nif isNewBar\n    h1 := h2\n    l1 := l2\n    h2 := htf_high[1]\n    l2 := htf_low[1]\n    prevClose := htf_close[1]\n\n    // Identify setup conditions\n    if not na(h1) and not na(h2) and not na(prevClose)\n        if (h2 > h1 and prevClose < h1)  // Short setup\n            setupType := "short"\n            triggerLevel := l2\n            targetLevel := l1\n            stopLevel := h2 + (h2 - l1) * stopLossMultiplier\n        else if (l2 < l1 and prevClose > l1)  // Long setup\n            setupType := "long"\n            triggerLevel := h2\n            targetLevel := h1\n            stopLevel := l2 - (h1 - l2) * stopLossMultiplier\n        else\n            setupType := na\n            triggerLevel := na\n            targetLevel := na\n            stopLevel := na\n\n// Entry conditions using pre-calculated volume condition - fixed line breaks\nbool longCondition = setupType == "long" and high > triggerLevel and not na(triggerLevel) and volCondition\nbool shortCondition = setupType == "short" and low < triggerLevel and not na(triggerLevel) and volCondition\n\n// Execute trades\nif longCondition\n    strategy.entry("Long", strategy.long, comment="Long Entry")\n    strategy.exit("Long Exit", "Long", limit=targetLevel, stop=stopLevel)\n\nif shortCondition\n    strategy.entry("Short", strategy.short, comment="Short Entry")\n    strategy.exit("Short Exit", "Short", limit=targetLevel, stop=stopLevel)\n\n// Plot signals - fixed plotshape parameters\nplotshape(series=longCondition, title="Long Signal", location=location.belowbar, color=color.green, style=shape.triangleup)\nplotshape(series=shortCondition, title="Short Signal", location=location.abovebar, color=color.red, style=shape.triangledown)\n\nplot(triggerLevel, "Trigger Level", color=color.yellow, style=plot.style_circles)\nplot(targetLevel, "Target Level", color=color.blue, style=plot.style_circles)\nplot(stopLevel, "Stop Level", color=color.red, style=plot.style_circles)\n\n'

class SMAdvancedMultiTimeframeRangeBreakoutTradingStrategyee13ce(PinePortBase, IStrategy):
    source_id = "SM_ee13ce5cca7b84a1"
    source_file = '高级区间突破多时间周期交易策略-Advanced-Multi-Timeframe-Range-Breakout-Trading-Strategy.md'
    timeframe = '6h'
    can_short = True
    source_defaults = {'stopLossMultiplier': 1.5, 'useVolFilter': False, 'volThreshold': 1.5}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_reproduce_stops = True
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_012 md and exposed through the same PinePortBase interface used by batch_001.', 'request.security/security is present: generic adapter keeps the expression but same-frame evaluation is only an approximation; manual multi-timeframe parity verification is required.', 'Custom Pine function(s) are present; the original source is embedded verbatim and this generic pass flags them for per-strategy semantic verification.']

    def pine_indicators(self, dataframe, params):
        # Runtime evaluates the source against the complete OHLCV frame.
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch012Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
