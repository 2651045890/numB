"""batch_012 port of 高级RSI背离与均线组合的量化交易策略-Advanced-Quantitative-Trading-Strategy-Combining-RSI-Divergence-and-Moving-Averages.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2024-05-28 00:00:00\nend: 2024-06-27 00:00:00\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("Advanced Gold Scalping Strategy with RSI Divergence", overlay=false)\n\n// Input parameters\nrsiLengthInput = input.int(60, minval=1, title="RSI Length", group="RSI Settings")\nrsiSourceInput = input.source(ohlc4, "Source", group="RSI Settings")\nmaTypeInput = input.string("SMMA (RMA)", title="MA Type", options=["SMA", "Bollinger Bands", "EMA", "SMMA (RMA)", "WMA", "VWMA"], group="MA Settings")\nmaLengthInput = input.int(3, title="MA Length", group="MA Settings")\nbbMultInput = input.float(2.0, minval=0.001, maxval=50, title="BB StdDev", group="MA Settings")\nshowDivergence = input(true, title="Show Divergence", group="RSI Settings")\nstopLoss = input.float(11, title="Stop Loss (pips)", group="Trade Settings")\ntakeProfit = input.float(33, title="Take Profit (pips)", group="Trade Settings")\n\n// RSI and MA calculation\nma(source, length, type) =>\n    switch type\n        "SMA" => ta.sma(source, length)\n        "Bollinger Bands" => ta.sma(source, length)\n        "EMA" => ta.ema(source, length)\n        "SMMA (RMA)" => ta.rma(source, length)\n        "WMA" => ta.wma(source, length)\n        "VWMA" => ta.vwma(source, length)\n\nup = ta.rma(math.max(ta.change(rsiSourceInput), 0), rsiLengthInput)\ndown = ta.rma(-math.min(ta.change(rsiSourceInput), 0), rsiLengthInput)\nrsi = down == 0 ? 100 : up == 0 ? 0 : 100 - (100 / (1 + up / down))\nrsiMA = ma(rsi, maLengthInput, maTypeInput)\nisBB = maTypeInput == "Bollinger Bands"\n\n// Divergence detection\nlookbackRight = 5\nlookbackLeft = 5\nrangeUpper = 60\nrangeLower = 5\n\nplFound = na(ta.pivotlow(rsi, lookbackLeft, lookbackRight)) ? false : true\nphFound = na(ta.pivothigh(rsi, lookbackLeft, lookbackRight)) ? false : true\n\n_inRange(cond) =>\n    bars = ta.barssince(cond == true)\n    rangeLower <= bars and bars <= rangeUpper\n\n// Bullish divergence\nrsiHL = rsi[lookbackRight] > ta.valuewhen(plFound, rsi[lookbackRight], 1) and _inRange(plFound[1])\npriceLL = low[lookbackRight] < ta.valuewhen(plFound, low[lookbackRight], 1)\nbullishDivergence = priceLL and rsiHL and plFound\n\n// Bearish divergence\nrsiLH = rsi[lookbackRight] < ta.valuewhen(phFound, rsi[lookbackRight], 1) and _inRange(phFound[1])\npriceHH = high[lookbackRight] > ta.valuewhen(phFound, high[lookbackRight], 1)\nbearishDivergence = priceHH and rsiLH and phFound\n\n// Entry conditions\nlongCondition = bullishDivergence and rsi < 40\nshortCondition = bearishDivergence and rsi > 60\n\n// Convert pips to price for Gold (assuming 1 pip = 0.1 for XAUUSD)\nstopLossPrice = stopLoss * 0.1\ntakeProfitPrice = takeProfit * 0.1\n\n// Execute trades\nif (longCondition)\n    strategy.entry("Long", strategy.long)\n    strategy.exit("TP/SL", "Long", stop=strategy.position_avg_price - stopLossPrice, limit=strategy.position_avg_price + takeProfitPrice)\n\nif (shortCondition)\n    strategy.entry("Short", strategy.short)\n    strategy.exit("TP/SL", "Short", stop=strategy.position_avg_price + stopLossPrice, limit=strategy.position_avg_price - takeProfitPrice)\n\n// Plotting\nplot(rsi, "RSI", color=#7E57C2)\n// plot(rsiMA, "RSI-based MA", color=color.yellow)\nhline(60, "RSI Upper Band", color=#787B86)\n// hline(50, "RSI Middle Band", color=color.new(#787B86, 50))\nhline(40, "RSI Lower Band", color=#787B86)\nfill(hline(60), hline(40), color=color.rgb(126, 87, 194, 90), title="RSI Background Fill")\n\n// Divergence visualization\nplotshape(showDivergence and bullishDivergence ? rsi[lookbackRight] : na, offset=-lookbackRight, title="Bullish Divergence", text="Bull", style=shape.labelup, location=location.absolute, color=color.green, textcolor=color.white)\nplotshape(showDivergence and bearishDivergence ? rsi[lookbackRight] : na, offset=-lookbackRight, title="Bearish Divergence", text="Bear", style=shape.labeldown, location=location.absolute, color=color.red, textcolor=color.white)\n\n'

class SMRSIAdvancedQuantitativeTradingStrategyCombiningRSIDiverfd0016(PinePortBase, IStrategy):
    source_id = "SM_fd0016e470f99ba5"
    source_file = '高级RSI背离与均线组合的量化交易策略-Advanced-Quantitative-Trading-Strategy-Combining-RSI-Divergence-and-Moving-Averages.md'
    timeframe = '1h'
    can_short = True
    source_defaults = {'rsiLengthInput': 60, 'rsiSourceInput': 'ohlc4', 'maTypeInput': 'SMMA (RMA)', 'maLengthInput': 3, 'bbMultInput': 2.0, 'showDivergence': True, 'stopLoss': 11, 'takeProfit': 33}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
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
