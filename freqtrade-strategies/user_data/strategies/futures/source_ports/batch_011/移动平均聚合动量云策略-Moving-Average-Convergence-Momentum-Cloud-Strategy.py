"""batch_011 port of 移动平均聚合动量云策略-Moving-Average-Convergence-Momentum-Cloud-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-05-28 00:00:00\nend: 2024-06-02 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("Enhanced Starlight Analysis Strategy", overlay=true)\n\n// Inputs for moving averages\nshortLength = input.int(5, title="Short Moving Average Length")\nlongLength = input.int(20, title="Long Moving Average Length")\n\n// Calculate moving averages\nma1 = ta.sma(close, shortLength)\nma2 = ta.sma(close, longLength)\n\n// Determine the fill color based on the relationship between ma1 and ma2\nfillColor = ma1 > ma2 ? color.new(color.green, 90) : color.new(color.red, 90)\n\n// Plot the moving averages and fill the space between them\nplot(ma1, "5-bar SMA", color=color.blue)\nplot(ma2, "20-bar SMA", color=color.orange)\nfill(plot(ma1), plot(ma2), fillColor, "SMA plot fill")\n\n// Additional Analysis: Bollinger Bands\nbbLength = input.int(20, title="BB Length")\nbbMult = input.float(2.0, title="BB Multiplier")\n[bbUpper, bbMiddle, bbLower] = ta.bb(close, bbLength, bbMult)\nplot(bbUpper, color=color.red, title="BB Upper")\nplot(bbMiddle, color=color.green, title="BB Middle")\nplot(bbLower, color=color.red, title="BB Lower")\n\n// Additional Analysis: RSI\nrsiLength = input.int(14, title="RSI Length")\nrsi = ta.rsi(close, rsiLength)\nplot(rsi, color=color.purple, title="RSI")\nhline(70, "Overbought", color=color.red)\nhline(30, "Oversold", color=color.green)\n\n// Ichimoku Cloud\ntenkan = ta.sma((high + low) / 2, 9)\nkijun = ta.sma((high + low) / 2, 26)\nsenkouA = ta.sma((tenkan + kijun) / 2, 26)\nsenkouB = ta.sma((high + low) / 2, 52)\nplot(tenkan, color=color.red, title="Tenkan")\nplot(kijun, color=color.blue, title="Kijun")\nplot(senkouA, color=color.green, title="Senkou A")\nplot(senkouB, color=color.red, title="Senkou B")\nfill(plot(senkouA, "Senkou A", color=color.green), plot(senkouB, "Senkou B", color=color.red), color.new(color.purple, 80), title="Kumo (Cloud)")\n\n// Signals and Alerts\ncrossAbove = ta.crossover(ma1, ma2)\ncrossBelow = ta.crossunder(ma1, ma2)\nplotshape(series=crossAbove, location=location.abovebar, color=color.green, style=shape.triangleup, title="Buy Signal")\nplotshape(series=crossBelow, location=location.belowbar, color=color.red, style=shape.triangledown, title="Sell Signal")\n\nalertcondition(crossAbove, title="Buy Alert", message="MA1 has crossed above MA2 - Buy Signal")\nalertcondition(crossBelow, title="Sell Alert", message="MA1 has crossed below MA2 - Sell Signal")\n\n// Strategy Logic: Execute Buy and Sell Orders\nif (crossAbove)\n    strategy.entry("Buy", strategy.long)\nif (crossBelow)\n    strategy.close("Buy")\n\n// Equations for Further Analysis\n// Example: Calculating Momentum\nmomentum = close - close[1]\nplot(momentum, color=color.yellow, title="Momentum")\n\n// Example: Calculating Rate of Change (ROC)\nrocLength = input.int(12, title="ROC Length")\nroc = (close - close[rocLength]) / close[rocLength] * 100\nplot(roc, color=color.black, title="Rate of Change (ROC)")\n\n// Display Summary Label\nvar label summaryLabel = label.new(x=bar_index, y=na, text="", xloc=xloc.bar_index, yloc=yloc.price, color=color.green, textcolor=color.white, size=size.small)\nif (bar_index % 10 == 0)  // Update label every 10 bars\n    label.set_xy(summaryLabel, bar_index, high)\n    label.set_text(summaryLabel, "Short MA: " + str.tostring(ma1) + "\\nLong MA: " + str.tostring(ma2) + "\\nRSI: " + str.tostring(rsi) + "\\nMomentum: " + str.tostring(momentum) + "\\nROC: " + str.tostring(roc))\n\n// Plot title for the indicator\nplot(close, title="Enhanced Starlight Analysis Strategy", color=color.white)\n'

class SM9D1546E866D157CD(PinePortBase, IStrategy):
    source_id = "SM_9d1546e866d157cd"
    source_file = '移动平均聚合动量云策略-Moving-Average-Convergence-Momentum-Cloud-Strategy.md'
    timeframe = '1d'
    can_short = False
    source_defaults = {'shortLength': 5, 'longLength': 20, 'bbLength': 20, 'bbMult': 2.0, 'rsiLength': 14, 'rocLength': 12}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = False
    source_risk_flags = ['tuple', 'var_state', 'alert_or_drawing']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
