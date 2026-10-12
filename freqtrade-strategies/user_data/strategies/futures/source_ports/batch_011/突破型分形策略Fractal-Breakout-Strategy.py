"""batch_011 port of 突破型分形策略Fractal-Breakout-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-11-18 00:00:00\nend: 2023-12-18 00:00:00\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=2\nstrategy("Fractal Breakout Strategy (by ChartArt)", shorttitle="CA_-_Fractal_Breakout_Strat", overlay=true)\n\n// ChartArt\'s Fractal Breakout Strategy\n//\n// Version 1.0\n// Idea by ChartArt on April 24, 2016.\n//\n// This long only strategy determines the last fractal top\n// and enters a trade when the price breaks above the last\n// fractal top. The strategy also calculates the average\n// price of the last 2 (or 3) fractal tops to get the trend.\n//\n// The strategy exits the long trade when the average of the\n// fractal tops is falling (when the trend is lower highs).\n// And the user can manually set a delay of this exit.\n//\n// In addition the fractals tops can be colored in blue\n// and a line can be drawn based on the fractal tops.\n// This fractal top line is colored by the fractal trend.\n//\n// List of my work: \n// https://www.tradingview.com/u/ChartArt/\n// \n//  __             __  ___       __  ___ \n// /  ` |__|  /\\  |__)  |   /\\  |__)  |  \n// \\__, |  | /~~\\ |  \\  |  /~~\\ |  \\  |  \n// \n// \n\n\n// input\n\nn_time = input(title=\'Always exit each trade after this amount of bars later (Most important strategy setting)\', defval=3)\nprice = input(hl2,title=\'Price type to determine the last fractal top and the fractal breakout, the default is (high+low)/2\')\n\n\n// fractal calculation\n\nfractal_top = high[2] > high[3] and high[2] > high[4] and high[2] > high[1] and high[2] > high[0]\nfractal_price = valuewhen(fractal_top, price, 1)\nuse_longer_average = input(true,title=\'Use Fractal price average of the last 3 fractals instead of the last 2 fractals?\')\nfractal_average = use_longer_average?(fractal_price[1] + fractal_price[2] + fractal_price[3] ) / 3 : (fractal_price[1] + fractal_price[2]) / 2\nfractal_trend = fractal_average[0] > fractal_average[1]\nno_repainting = input(true,title=\'Use the price of the last bar to prevent repainting?\')\nfractal_breakout = no_repainting?price[1] > fractal_price[0]:price[0] > fractal_price[0]\n\n\n// highlight fractal tops\n\nshow_highlight = input(true,title=\'Highlight fractal tops in blue and color all other bars in gray?\')\nhighlight = fractal_top?blue:silver\nbarcolor(show_highlight?highlight:na,offset=-2)\nshow_fractal_top_line = input(true,title=\'Draw a colored line based on the fractal tops?\')\nfractal_top_line = change(fractal_top) != 0 ? price : na\nfractal_top_line_color = change(fractal_price) > 0 and fractal_breakout == true ? green : change(fractal_price) < 0 and fractal_breakout == false ? red : blue\nplot(show_fractal_top_line?fractal_top_line:na,offset=-2,color=fractal_top_line_color,linewidth=4)\n\n\n// strategy\n\ntrade_entry = fractal_trend and fractal_breakout\ntrade_exit = fractal_trend[n_time] and fractal_trend == false \n \nif (trade_entry)\n    strategy.entry(\'Long\', strategy.long)\n \nif (trade_exit)\n    strategy.close(\'Long\')'

class SMA69E7A7FF4777653(PinePortBase, IStrategy):
    source_id = "SM_a69e7a7ff4777653"
    source_file = '突破型分形策略Fractal-Breakout-Strategy.md'
    timeframe = '1h'
    can_short = False
    source_defaults = {'n_time': 3, 'use_longer_average': True, 'no_repainting': True, 'show_highlight': True, 'show_fractal_top_line': True}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = False
    source_risk_flags = ['common_subset']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
