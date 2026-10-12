"""batch_012 port of 随机相对强弱指数与蜡烛图确认的动态交易系统-Dynamic-Trading-System-with-Stochastic-RSI-and-Candlestick-Confirmation.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2019-12-23 08:00:00\nend: 2024-11-27 08:00:00\nperiod: 1d\nbasePeriod: 1d\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("Stochastic RSI Strategy with Candlestick Confirmation", overlay=true)\n\n// Input parameters for Stochastic RSI\nrsiPeriod = input.int(14, title="RSI Period")\nstochRsiPeriod = input.int(14, title="Stochastic RSI Period")\nkPeriod = input.int(3, title="K Period")\ndPeriod = input.int(3, title="D Period")\n\n// Overbought and Oversold levels\noverboughtLevel = input.int(80, title="Overbought Level", minval=50, maxval=100)\noversoldLevel = input.int(20, title="Oversold Level", minval=0, maxval=50)\n\n// Calculate RSI\nrsi = ta.rsi(close, rsiPeriod)\n\n// Calculate Stochastic RSI\nstochRSI = ta.stoch(rsi, rsi, rsi, stochRsiPeriod)  // Stochastic RSI calculation using the RSI values\n\n// Apply smoothing to StochRSI K and D lines\nk = ta.sma(stochRSI, kPeriod)\nd = ta.sma(k, dPeriod)\n\n// Plot Stochastic RSI on separate panel\nplot(k, title="StochRSI K", color=color.green, linewidth=2)\nplot(d, title="StochRSI D", color=color.red, linewidth=2)\nhline(overboughtLevel, "Overbought", color=color.red, linestyle=hline.style_dashed)\nhline(oversoldLevel, "Oversold", color=color.green, linestyle=hline.style_dashed)\n\n// Buy and Sell Signals based on both Stochastic RSI and Candlestick patterns\nbuySignal = ta.crossover(k, oversoldLevel) and close > open  // Buy when K crosses above oversold level and close > open (bullish candle)\nsellSignal = ta.crossunder(k, overboughtLevel) and close < open  // Sell when K crosses below overbought level and close < open (bearish candle)\n\n// Plot Buy/Sell signals as shapes on the chart\nplotshape(series=buySignal, title="Buy Signal", location=location.belowbar, color=color.green, style=shape.labelup, text="BUY", size=size.small)\nplotshape(series=sellSignal, title="Sell Signal", location=location.abovebar, color=color.red, style=shape.labeldown, text="SELL", size=size.small)\n\n// Background color shading for overbought/oversold conditions\nbgcolor(k > overboughtLevel ? color.new(color.red, 90) : na)\nbgcolor(k < oversoldLevel ? color.new(color.green, 90) : na)\n\n// Place actual orders with Stochastic RSI + candlestick pattern confirmation\nif (buySignal)\n    strategy.entry("Long", strategy.long)\n\nif (sellSignal)\n    strategy.entry("Short", strategy.short)\n\n// Optionally, you can add exit conditions for closing long/short positions\n// Close long if K crosses above the overbought level\nif (ta.crossunder(k, overboughtLevel))\n    strategy.close("Long")\n\n// Close short if K crosses below the oversold level\nif (ta.crossover(k, oversoldLevel))\n    strategy.close("Short")\n\n'

class SMDynamicTradingSystemwithStochasticRSIandCandlestickConf4c8350(PinePortBase, IStrategy):
    source_id = "SM_4c8350bf45830d43"
    source_file = '随机相对强弱指数与蜡烛图确认的动态交易系统-Dynamic-Trading-System-with-Stochastic-RSI-and-Candlestick-Confirmation.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'rsiPeriod': 14, 'stochRsiPeriod': 14, 'kPeriod': 3, 'dPeriod': 3, 'overboughtLevel': 80, 'oversoldLevel': 20}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_reproduce_stops = False
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_012 md and exposed through the same PinePortBase interface used by batch_001.']

    def pine_indicators(self, dataframe, params):
        # Runtime evaluates the source against the complete OHLCV frame.
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch012Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
