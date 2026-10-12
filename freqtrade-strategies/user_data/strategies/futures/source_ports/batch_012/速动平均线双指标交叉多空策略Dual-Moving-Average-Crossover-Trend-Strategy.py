"""batch_012 port of 速动平均线双指标交叉多空策略Dual-Moving-Average-Crossover-Trend-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-10-22 00:00:00\nend: 2023-11-21 00:00:00\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy(\'SteffVans\', shorttitle=\'SteffVans strategy\', overlay=true, process_orders_on_close = true)\n\n// Input settings\nmacd_fast_length = input(12)\nmacd_slow_length = input(26)\nmacd_signal_length = input(9)\n\n// Calculate MACD values\n[macd_line, signal_line, _] = ta.macd(close, macd_fast_length, macd_slow_length, macd_signal_length)\nmg = ta.lowest(signal_line, 30) >= -0\n\n// RSI\nma(source, length, type) =>\n    switch type\n        "SMA" => ta.sma(source, length)\n        "Bollinger Bands" => ta.sma(source, length)\n        "EMA" => ta.ema(source, length)\n        "SMMA (RMA)" => ta.rma(source, length)\n        "WMA" => ta.wma(source, length)\n        "VWMA" => ta.vwma(source, length)\n\nrsiLengthInput = input.int(14, minval=1)\nrsiSourceInput = input.source(close, "Source", group="RSI Settings")\nmaTypeInput = input.string("SMA", title="MA Type", options=["SMA", "Bollinger Bands", "EMA", "SMMA (RMA)", "WMA", "VWMA"], group="MA Settings")\nmaLengthInput = input.int(14, title="MA Length", group="MA Settings")\nbbMultInput = input.float(2.0, minval=0.001, maxval=50, title="BB StdDev", group="MA Settings")\n\nup = ta.rma(math.max(ta.change(rsiSourceInput), 0), rsiLengthInput)\ndown = ta.rma(-math.min(ta.change(rsiSourceInput), 0), rsiLengthInput)\nRSI = down == 0 ? 100 : up == 0 ? 0 : 100 - (100 / (1 + up / down))\n\n\n//  AO\nAO = ta.sma((high + low) / 2, 5) - ta.sma((high + low) / 2, 34)\ncrossaosell = AO < AO[1] and AO[1] < AO[2] and AO[2] > AO[3]  and ta.lowest(low,3)\n\n// Uptrend sma\nlen1 = input.int(5, minval=1)\nlen2 = input.int(10, minval=1)\nlen3 = input.int(20, minval=1)\nsrc = input(close)\n\nout1 = ta.sma(src, len1)\nout2 = ta.sma(src, len2)\nout3 = ta.sma(src, len3)\n\n\n\n// Timeframe \nmacdl60 = request.security(syminfo.tickerid, "60", signal_line,lookahead = barmerge.lookahead_on)\nao = request.security(syminfo.tickerid, "60", AO,lookahead = barmerge.lookahead_on)\nrsi = request.security(syminfo.tickerid, "60", RSI,lookahead = barmerge.lookahead_on)\ngood = request.security(syminfo.tickerid, "60", mg,lookahead = barmerge.lookahead_on)\nbad = request.security(syminfo.tickerid, "60", crossaosell,lookahead = barmerge.lookahead_on)\n\nma1 = request.security(syminfo.tickerid, "D", out1,lookahead = barmerge.lookahead_on)\nma2 = request.security(syminfo.tickerid, "D", out2, lookahead = barmerge.lookahead_on)\nma3 = request.security(syminfo.tickerid, "D", out3, lookahead = barmerge.lookahead_on)\n\n\n\n\n\n\n// Kriteria BUY and SELL\nuptrend1 =  request.security(syminfo.tickerid, "D", close,lookahead = barmerge.lookahead_on) > ma1 and ma1 > ma3 and ma2 > ma3\nuptrend2 = ta.lowest(ma1,12) > ta.lowest(ma3,12) and ta.lowest(ma2,12) > ta.lowest(ma3,12) \n\n\n \n\n// Triger BUY and SELL \ncross1 = ao > ao[1] and ao[1] < ao[2] and ao > 0 and good and rsi >= 60 and uptrend1\ncross2 = ao > 0 and ao[1] < 0 and good and rsi >=50 and uptrend1\ncross3 =  ao > 0 and ao[1] < 0 and not good and uptrend2 and uptrend1\ncross4 =  ao > ao[1] and ao[1] > ao[2] and ao[2] < ao[3] and ao[3] < ao[4]  and not good and uptrend2 and uptrend1\n\ns1 = ao < ao[1] and ao[1] < ao[2] and ao[2] < ao[3] and ao > 0 and rsi < 50 and request.security(syminfo.tickerid, "D", close,lookahead = barmerge.lookahead_on) < ma1\ns2 =  ao < 0 and ao < ao[2] and rsi < 50 and request.security(syminfo.tickerid, "D", close,lookahead = barmerge.lookahead_on) < ma1 \n\n// Variabel Buy dan Sell\nbuySignal = false\nsellSignal = false\n\n// Syarat masuk Buy\nbuyCondition =  cross1 or cross2 or cross3 or cross4\nif buyCondition\n    buySignal := true\n\n// Syarat masuk Sell\nsellCondition = s1 or s2\nif sellCondition\n    sellSignal := true\n\n// Reset sinyal jika ada sinyal berulang\nif buySignal and sellSignal\n    sellSignal := false\nif sellSignal and buySignal\n    buySignal := false\n\n// Logika perdagangan\nif buySignal\n    strategy.entry("Buy", strategy.long, comment = "BUY")\nif sellSignal\n    strategy.close("Buy")\n\n\nplotshape(cross1,title = "Stefkuy1", style = shape.labelup, location = location.belowbar, color = color.green,text = "1", textcolor = color.white,size = size.small)\nplotshape(cross2,title = "Stefkuy2", style = shape.labelup, location = location.belowbar, color = color.green, text = "2", textcolor= color.white, size = size.small)\nplotshape(cross3,title = "StefVan1", style = shape.labelup, location = location.belowbar, color = color.rgb(0, 153, 255), text = "3", textcolor= color.white,size = size.small)\nplotshape(cross4,title = "StefVan2", style = shape.labelup, location = location.belowbar, color = color.rgb(0, 153, 255), text = "4", textcolor= color.white,size = size.small)\n\n'

class SMDualMovingAverageCrossoverTrendStrategycdcc0c(PinePortBase, IStrategy):
    source_id = "SM_cdcc0c08085a2774"
    source_file = '速动平均线双指标交叉多空策略Dual-Moving-Average-Crossover-Trend-Strategy.md'
    timeframe = '1h'
    can_short = False
    source_defaults = {'macd_fast_length': 12, 'macd_slow_length': 26, 'macd_signal_length': 9, 'rsiLengthInput': 14, 'rsiSourceInput': 'close', 'maTypeInput': 'SMA', 'maLengthInput': 14, 'bbMultInput': 2.0, 'len1': 5, 'len2': 10, 'len3': 20, 'src': 'close'}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_reproduce_stops = False
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_012 md and exposed through the same PinePortBase interface used by batch_001.', 'request.security/security is present: generic adapter keeps the expression but same-frame evaluation is only an approximation; manual multi-timeframe parity verification is required.', 'Custom Pine function(s) are present; the original source is embedded verbatim and this generic pass flags them for per-strategy semantic verification.', 'Loop/switch logic is present and requires per-strategy semantic verification against TradingView/FMZ before treating results as parity-certified.']

    def pine_indicators(self, dataframe, params):
        # Runtime evaluates the source against the complete OHLCV frame.
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch012Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
