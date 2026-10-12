"""batch_011 port of 移动平均线交叉多层获利策略-Moving-Average-Crossover-with-Multiple-Take-Profits-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-04-20 00:00:00\nend: 2024-04-25 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This Pine Script™ code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © ValdesTradingBots\n\n//Follow Us for More Insights and Updates!\n\n//Join our community and be the first to know about our new releases and trading tips\n\n//Facebook Group: Join our vibrant community at https://www.facebook.com/groups/707469081464839/\n//Twitter: Follow us for quick updates and insights at https://twitter.com/ValdesBots\n\n//We\'re excited to have you with us!\n\n//@version=5\nstrategy("Valdes Trading Bots MA Cross with Multiple Take Profits", overlay=true)\n\nshortPeriod = input(18, title="Short MA Period")\nlongPeriod = input(32, title="Long MA Period")\n\n// Take Profit Settings\ntp1Enabled = input(true, title="Enable Take Profit 1")\ntp1Perc = input(15, title="Take Profit 1 (%)") / 100\ntp1QtyPerc = input(25, title="Take Profit 1 Qty (%)") / 100\n\ntp2Enabled = input(true, title="Enable Take Profit 2")\ntp2Perc = input(30, title="Take Profit 2 (%)") / 100\ntp2QtyPerc = input(25, title="Take Profit 2 Qty (%)") / 100\n\ntp3Enabled = input(true, title="Enable Take Profit 3")\ntp3Perc = input(45, title="Take Profit 3 (%)") / 100\ntp3QtyPerc = input(25, title="Take Profit 3 Qty (%)") / 100\n\ntp4Enabled = input(true, title="Enable Take Profit 4")\ntp4Perc = input(60, title="Take Profit 4 (%)") / 100\ntp4QtyPerc = input(25, title="Take Profit 4 Qty (%)") / 100\n\nshortMA = ta.sma(close, shortPeriod)\nlongMA = ta.sma(close, longPeriod)\n\n// Determine the trend\nuptrend = shortMA > longMA\ndowntrend = shortMA < longMA\n\n// Assign candle colors based on the trend\ncandleColor = uptrend ? color.rgb(9, 112, 0) : downtrend ? color.rgb(255, 0, 0) : color.new(color.blue, 0)\n\nplot(shortMA, title="Short MA", color=color.rgb(9, 112, 0))\nplot(longMA, title="Long MA", color=color.rgb(255, 0, 0))\n\n// Create a cross signal\nlongCross = ta.crossover(shortMA, longMA)\nshortCross = ta.crossunder(shortMA, longMA)\n\n// Strategy entry\nif (longCross)\n    strategy.entry("Long", strategy.long)\nif (shortCross)\n    strategy.entry("Short", strategy.short)\n\n// Strategy take profit\nif (tp1Enabled and strategy.position_size > 0)\n    strategy.exit("TP1 Long", "Long", qty_percent=tp1QtyPerc, limit=strategy.position_avg_price * (1 + tp1Perc))\nif (tp1Enabled and strategy.position_size < 0)\n    strategy.exit("TP1 Short", "Short", qty_percent=tp1QtyPerc, limit=strategy.position_avg_price * (1 - tp1Perc))\n\nif (tp2Enabled and strategy.position_size > 0)\n    strategy.exit("TP2 Long", "Long", qty_percent=tp2QtyPerc, limit=strategy.position_avg_price * (1 + tp2Perc))\nif (tp2Enabled and strategy.position_size < 0)\n    strategy.exit("TP2 Short", "Short", qty_percent=tp2QtyPerc, limit=strategy.position_avg_price * (1 - tp2Perc))\n\nif (tp3Enabled and strategy.position_size > 0)\n    strategy.exit("TP3 Long", "Long", qty_percent=tp3QtyPerc, limit=strategy.position_avg_price * (1 + tp3Perc))\nif (tp3Enabled and strategy.position_size < 0)\n    strategy.exit("TP3 Short", "Short", qty_percent=tp3QtyPerc, limit=strategy.position_avg_price * (1 - tp3Perc))\n\nif (tp4Enabled and strategy.position_size > 0)\n    strategy.exit("TP4 Long", "Long", qty_percent=tp4QtyPerc, limit=strategy.position_avg_price * (1 + tp4Perc))\nif (tp4Enabled and strategy.position_size < 0)\n    strategy.exit("TP4 Short", "Short", qty_percent=tp4QtyPerc, limit=strategy.position_avg_price * (1 - tp4Perc))\n\n// Plotting the signals on the chart\nplotshape(series=longCross, title="Long Cross", location=location.belowbar, color=color.rgb(9, 112, 0), style=shape.triangleup, size=size.small)\nplotshape(series=shortCross, title="Short Cross", location=location.abovebar, color=color.rgb(255, 0, 0), style=shape.triangledown, size=size.small)\n\n// Apply candle color\nbarcolor(candleColor)\n'

class SMD8DD152AAAC24A7D(PinePortBase, IStrategy):
    source_id = "SM_d8dd152aaac24a7d"
    source_file = '移动平均线交叉多层获利策略-Moving-Average-Crossover-with-Multiple-Take-Profits-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'shortPeriod': 18, 'longPeriod': 32, 'tp1Enabled': True, 'tp1Perc': 15, 'tp1QtyPerc': 25, 'tp2Enabled': True, 'tp2Perc': 30, 'tp2QtyPerc': 25, 'tp3Enabled': True, 'tp3Perc': 45, 'tp3QtyPerc': 25, 'tp4Enabled': True, 'tp4Perc': 60, 'tp4QtyPerc': 25}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = False
    source_risk_flags = ['broker_state', 'exit_order']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
