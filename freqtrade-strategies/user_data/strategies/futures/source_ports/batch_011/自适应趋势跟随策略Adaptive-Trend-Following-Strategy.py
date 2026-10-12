"""batch_011 port of 自适应趋势跟随策略Adaptive-Trend-Following-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-12-15 00:00:00\nend: 2024-01-14 00:00:00\nperiod: 4h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=2\nstrategy("[Th] Adaptive Trend v1", shorttitle="[TH] Adaptive Trend", overlay=true)\n\nPd=input(2, minval=1,maxval = 100, title="Period")\nBw=input(50, minval=1,maxval = 100, title="Bandwidth")\nminFactor = input(0.5, minval=0.1, maxval=1.0, step=0.1, title="Minimum Factor")\nmaxFactor = input(3.00, minval=0.2, maxval=5.0, step=0.1, title="Maximum Factor")\nplot_trend=input(true, title="Plot trend")\n\nplot_losscut = input(true, title="Plot losscut")\n\n/////////////// Calculate the BB\'s ///////////////\nbasisBB = ema(close, 20)\ndevBB     = 2 * stdev(close, 20)\nupperBB = basisBB + devBB\nlowerBB = basisBB - devBB\n//plot(upperBB)\n//plot(lowerBB)\n\n///////////// Trend ////////////////////////////\n\nrawFactor = ((upperBB-lowerBB)/basisBB)*Bw\nFactor = rawFactor > minFactor ? (rawFactor > maxFactor ? maxFactor : rawFactor) : minFactor\n\nUp=hl2-(Factor*atr(Pd))\nDn=hl2+(Factor*atr(Pd))\nTrendUp=close[1]>TrendUp[1]? max(Up,TrendUp[1]) : Up\nTrendDown=close[1]<TrendDown[1]? min(Dn,TrendDown[1]) : Dn\nTrendUpPlot=plot(plot_trend?TrendUp:na, style=line, color=green, linewidth=1)\nTrendDownPlot=plot(plot_trend?TrendDown:na, style=line, color=red, linewidth=1)\nTrend = close > TrendDown[1] ? 1: close< TrendUp[1]? -1: nz(Trend[1],1)\nfill(TrendUpPlot,TrendDownPlot, color=Trend == 1 ? green : red, transp=80)\nsig_trend_long = Trend[1] == -1 and Trend == 1\nsig_trend_short = Trend[1] == 1 and Trend == -1\n\n///////////// Loss Cut ////////////////////////////\nprice_cut = sig_trend_long[1] or sig_trend_short[1] or sig_reentry_long[1] or sig_reentry_short[1] ? open : price_cut[1] \ncurrent_trend = sig_trend_long[1] ? 1 : (sig_trend_short[1] ? -1 : current_trend[1])\n\nsig_loss_cut = sig_trend_long or sig_trend_short ? false : ( current_trend == 1 ? (price_cut > low) : (current_trend == -1 ? (price_cut < high) : false) )\nhas_position = sig_loss_cut ? false : ((sig_trend_long[1] or sig_trend_short[1] or sig_reentry_long[1] or sig_reentry_short[1]) ? true : has_position[1])\nsig_reentry_long = not has_position and current_trend == 1 and low > price_cut\nsig_reentry_short = not has_position and current_trend == -1 and high < price_cut\n\nbgcolor(plot_losscut and ( not has_position or sig_loss_cut ) ? silver : white, transp=70)\nplotshape(plot_losscut and sig_loss_cut and current_trend == 1? 1 : na, color=green, style=shape.xcross, location=location.belowbar ,size=size.tiny)\nplotshape(plot_losscut and sig_loss_cut and current_trend == -1? 1 : na, color=red, style=shape.xcross, location=location.abovebar ,size=size.tiny)\n\nLossCutPlot = plot(plot_losscut ? price_cut : na, linewidth=4, color=black, transp=60)\nfill(TrendDownPlot, LossCutPlot, color=silver, transp=90)\n\nplotshape(sig_trend_long or sig_reentry_long ? Trend : na, title="Up Entry Arrow", color=green, style=shape.triangleup, location=location.belowbar, size=size.tiny)\nplotshape(sig_trend_short or sig_reentry_short ? Trend : na, title="Down Entry Arrow",color=red, style=shape.triangledown, size=size.tiny)\n    \n    \n///////////// Strategy //////////////////////////// \nif true\n\n    strategy.entry(\'long\', long=strategy.long, comment=\'Long\', when=sig_trend_long or sig_reentry_long)\n    strategy.entry(\'short\', long=strategy.short, comment=\'Short\', when=sig_trend_short or sig_reentry_short)\n    \n    if(current_trend == 1)\n        strategy.close(\'long\', when=sig_loss_cut == true) \n        //strategy.exit(\'lc\',from_entry=\'long\', stop=price_cut)\n    \n    if( current_trend == -1 )\n        strategy.close(\'short\', when=sig_loss_cut == true) \n        //strategy.exit(\'sc\',from_entry=\'short\', stop=price_cut)\n'

class SM0C04672F3F35CFE9(PinePortBase, IStrategy):
    source_id = "SM_0c04672f3f35cfe9"
    source_file = '自适应趋势跟随策略Adaptive-Trend-Following-Strategy.md'
    timeframe = '4h'
    can_short = True
    source_defaults = {'Pd': 2, 'Bw': 50, 'minFactor': 0.5, 'maxFactor': 3.0, 'plot_trend': True, 'plot_losscut': True}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = True
    source_risk_flags = ['exit_order']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
