"""batch_012 port of 高级量化趋势追踪与云图反转复合交易策略-Advanced-Quantitative-Trend-Following-and-Cloud-Reversal-Composite-Trading-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2019-12-23 08:00:00\nend: 2025-01-04 08:00:00\nperiod: 1d\nbasePeriod: 1d\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("EMA Crossover Buy + Ichimoku Cloud Sell Strategy", overlay=true)\n\n// Input Parameters for the EMAs\nshortEmaPeriod = input.int(9, title="Short EMA Period", minval=1)\nlongEmaPeriod = input.int(21, title="Long EMA Period", minval=1)\n\n// Input Parameters for the Ichimoku Cloud\ntenkanPeriod = input.int(9, title="Tenkan-Sen Period", minval=1)\nkijunPeriod = input.int(26, title="Kijun-Sen Period", minval=1)\nsenkouSpanBPeriod = input.int(52, title="Senkou Span B Period", minval=1)\ndisplacement = input.int(26, title="Displacement", minval=1)\n\n// Calculate the EMAs\nshortEma = ta.ema(close, shortEmaPeriod)\nlongEma = ta.ema(close, longEmaPeriod)\n\n// Ichimoku Cloud Calculations\ntenkanSen = ta.sma(close, tenkanPeriod)\nkijunSen = ta.sma(close, kijunPeriod)\nsenkouSpanA = ta.sma(tenkanSen + kijunSen, 2)\nsenkouSpanB = ta.sma(close, senkouSpanBPeriod)\nchikouSpan = close[displacement]\n\n// Plot the EMAs on the chart\nplot(shortEma, color=color.green, title="Short EMA")\nplot(longEma, color=color.red, title="Long EMA")\n\n// Plot the Ichimoku Cloud\nplot(tenkanSen, color=color.blue, title="Tenkan-Sen")\nplot(kijunSen, color=color.red, title="Kijun-Sen")\nplot(senkouSpanA, color=color.green, title="Senkou Span A", offset=displacement)\nplot(senkouSpanB, color=color.purple, title="Senkou Span B", offset=displacement)\nplot(chikouSpan, color=color.orange, title="Chikou Span", offset=-displacement)\n\n// Buy Condition: Short EMA crosses above Long EMA\nbuyCondition = ta.crossover(shortEma, longEma)\n\n// Sell Condition: Tenkan-Sen crosses below Kijun-Sen, and price is below the cloud\nsellCondition = ta.crossunder(tenkanSen, kijunSen) and close < senkouSpanA and close < senkouSpanB\n\n// Plot Buy and Sell signals\nplotshape(series=buyCondition, title="Buy Signal", location=location.belowbar, color=color.green, style=shape.labelup, text="BUY")\nplotshape(series=sellCondition, title="Sell Signal", location=location.abovebar, color=color.red, style=shape.labeldown, text="SELL")\n\n// Execute Buy and Sell Orders\nif (buyCondition)\n    strategy.entry("Buy", strategy.long)\n\nif (sellCondition)\n    strategy.entry("Sell", strategy.short)\n\n// Optional: Add Stop Loss and Take Profit (risk management)\nstopLossPercentage = input.float(1.5, title="Stop Loss Percentage", minval=0.1) / 100\ntakeProfitPercentage = input.float(3.0, title="Take Profit Percentage", minval=0.1) / 100\n\nlongStopLoss = close * (1 - stopLossPercentage)\nlongTakeProfit = close * (1 + takeProfitPercentage)\n\nshortStopLoss = close * (1 + stopLossPercentage)\nshortTakeProfit = close * (1 - takeProfitPercentage)\n\nstrategy.exit("Take Profit/Stop Loss", "Buy", stop=longStopLoss, limit=longTakeProfit)\nstrategy.exit("Take Profit/Stop Loss", "Sell", stop=shortStopLoss, limit=shortTakeProfit)\n\n'

class SMAdvancedQuantitativeTrendFollowingandCloudReversalCompo9399d1(PinePortBase, IStrategy):
    source_id = "SM_9399d1fcaea8e1d7"
    source_file = '高级量化趋势追踪与云图反转复合交易策略-Advanced-Quantitative-Trend-Following-and-Cloud-Reversal-Composite-Trading-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'shortEmaPeriod': 9, 'longEmaPeriod': 21, 'tenkanPeriod': 9, 'kijunPeriod': 26, 'senkouSpanBPeriod': 52, 'displacement': 26}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_reproduce_stops = True
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_012 md and exposed through the same PinePortBase interface used by batch_001.']

    def pine_indicators(self, dataframe, params):
        # Runtime evaluates the source against the complete OHLCV frame.
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch012Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
