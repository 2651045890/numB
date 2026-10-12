"""batch_012 port of 量化交易策略之双均线突破策略Quantitative-Trading-Strategy-Based-on-Double-Moving-Average-Crossover.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2024-01-21 00:00:00\nend: 2024-02-20 00:00:00\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy(\'Pine Script Tutorial Example Strategy 1\', overlay=true, initial_capital=100000, default_qty_value=100, default_qty_type=strategy.percent_of_equity)\n\n//OBV\nsrc = close\nobv = ta.cum(math.sign(ta.change(src)) * volume)\nma(source, length, type) =>\n    switch type\n        "SMA" => ta.sma(source, length)\n        "EMA" => ta.ema(source, length)\n        "SMMA (RMA)" => ta.rma(source, length)\n        "WMA" => ta.wma(source, length)\n        "VWMA" => ta.vwma(source, length)\ntypeMA = input.string(title = "Method", defval = "SMA", options=["SMA", "EMA", "SMMA (RMA)", "WMA", "VWMA"], group="Smoothing")\nsmoothingLength = input.int(title = "Length", defval = 20, minval = 1, maxval = 100, group="Smoothing")\nLimit = input.float(title = "Limit", defval = 1, minval = 0.1, maxval = 10, group="Smoothing")\nsmoothingLine_ma = ma(obv,smoothingLength, typeMA)\nobv_diff = (obv-smoothingLine_ma)*100/obv\n\n//PVT\nvar cumVolp = 0.\ncumVolp += nz(volume)\nif barstate.islast and cumVolp == 0\n    runtime.error("No volume is provided by the data vendor.")\nsrcp = close\nvt = ta.cum(ta.change(srcp)/srcp[1]*volume)\nsmoothingLine_map = ma(vt,smoothingLength, typeMA)\npvt_diff = (vt-smoothingLine_map)*100/vt\n\n// plot(obv_diff+close+100 ,title="OBV_DIFF", color = color.rgb(255, 118, 54))\n// plot(pvt_diff+close+80 ,title="PVT_DIFF", color = color.rgb(223, 61, 255))\n\nindicator = (pvt_diff+obv_diff)/2\ngoLongCondition1 = ta.crossover(indicator,Limit)\ntimePeriod = time >= timestamp(syminfo.timezone, 2023,1, 1, 0, 0)  // Backtesting Time\nnotInTrade = strategy.position_size <= 0\nif goLongCondition1 and timePeriod and notInTrade\n    stopLoss = low * 0.99 // -2%\n    takeProfit = high * 1.05 // +5%\n    strategy.entry(\'long\', strategy.long )\n    strategy.exit(\'exit\', \'long\', stop=stopLoss, limit=takeProfit)\n\n\n\n\n\n\n// fastEMA = ta.ema(close, 24)\n// slowEMA = ta.ema(close, 100)\n// goLongCondition1 = ta.crossover(fastEMA, slowEMA)\n// timePeriod = time >= timestamp(syminfo.timezone, 2018, 12, 15, 0, 0)\n// notInTrade = strategy.position_size <= 0\n// if goLongCondition1 and timePeriod and notInTrade\n//     stopLoss = low * 0.97\n//     takeProfit = high * 1.12\n//     strategy.entry(\'long\', strategy.long)\n//     strategy.exit(\'exit\', \'long\', stop=stopLoss, limit=takeProfit)\n// plot(fastEMA, color=color.new(color.blue, 0))\n// plot(slowEMA, color=color.new(color.yellow, 0))\n'

class SMQuantitativeTradingStrategyBasedonDoubleMovingAverageCr765e4f(PinePortBase, IStrategy):
    source_id = "SM_765e4fd31e498083"
    source_file = '量化交易策略之双均线突破策略Quantitative-Trading-Strategy-Based-on-Double-Moving-Average-Crossover.md'
    timeframe = '1h'
    can_short = False
    source_defaults = {'typeMA': 'SMA', 'smoothingLength': 20, 'Limit': 1}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 100
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 100000
    source_reproduce_stops = True
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_012 md and exposed through the same PinePortBase interface used by batch_001.', 'Custom Pine function(s) are present; the original source is embedded verbatim and this generic pass flags them for per-strategy semantic verification.', 'Loop/switch logic is present and requires per-strategy semantic verification against TradingView/FMZ before treating results as parity-certified.', 'The source reads live strategy position state; batch_001-style broker-state parity must be checked manually for this file.']

    def pine_indicators(self, dataframe, params):
        # Runtime evaluates the source against the complete OHLCV frame.
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch012Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
