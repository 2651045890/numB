"""batch_012 port of 高低TEMA平均值震荡策略Oscillation-Strategy-of-High-and-Low-TEMA-Average.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2022-11-08 00:00:00\nend: 2023-11-14 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=4\nstrategy(title="TEMA_HMA_VWMACD short strategy", shorttitle="Short strategy", overlay=false, default_qty_type=strategy.percent_of_equity, default_qty_value=100, commission_type=strategy.commission.percent, commission_value=0.018, currency=\'USD\')\nstartP = timestamp(input(2017, "Start Year"), input(12, "Month"), input(17, "Day"), 0, 0)\nend   = timestamp(9999,1,1,0,0)\n_testPeriod() =>\n    iff(time >= startP and time <= end, true, false)\n    \n\nslow = input(13, "Short period")\nfast = input(21, "Long period")\nsignal = input(5, "Smoothing period")\n\nFast = ema( volume * close, fast ) / ema( volume, fast ) \nSlow = ema( volume * close, slow ) / ema( volume, slow ) \nMacd = Slow - Fast \nSignal = ema(Macd, signal) \nHist=Macd-Signal\nplot(Hist, color=color.silver, linewidth=1, style=plot.style_histogram)\nplot(0, color=color.red)\n\nlength = input(400, minval=1, title = "HMA")\nhullma = wma(2*wma(close, length/2)-wma(close, length), floor(sqrt(length)))\n\ntema_length_1 = input(5, "Fast moving TEMA")\ntema_length_2 = input(8, "Slow moving TEMA")\n\n\ntema(sec, length)=>\n    tema1= ema(sec, length)\n    tema2= ema(tema1, length)\n    tema3= ema(tema2, length)\n    tema = 3*tema1-3*tema2+tema3\n\ntema1 = tema(hlc3, tema_length_1)\ntema2 = tema(hlc3, tema_length_2)\n\nthreshold  = 0\ntm = tema1 - tema2\nplot_fast = plot(tm, color = tm > 0 ? color.green : color.red)\nplot(threshold, color=color.purple)\n\nup =  crossover(tm, 0) \ndown = crossunder(tm, 0)\n\nlongCondition =  (Hist < 0) and hullma > close and (tema1 < tema2)  and _testPeriod() \nstrategy.entry(\'BUY\', strategy.short, when=longCondition)  \n \nshortCondition =  (Hist > 0) or hullma < close or up\nstrategy.close(\'BUY\', when=shortCondition)\n\n\n// Take profit  \ntp = input(1, type=input.float, title=\'Take Profit (%)\')  \nsl = input(4, type=input.float, title=\'Stop Loss (%)\')  \nstrategy.exit(\'XLong\', from_entry=\'BUY\', profit=(close * (tp/100) * (1/syminfo.mintick)), loss=(close * (sl/100) * (1/syminfo.mintick)))\n'

class SMTEMAOscillationStrategyofHighandLowTEMAAveragedcdb72(PinePortBase, IStrategy):
    source_id = "SM_dcdb72ce1aba1be9"
    source_file = '高低TEMA平均值震荡策略Oscillation-Strategy-of-High-and-Low-TEMA-Average.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'slow': 13, 'fast': 21, 'signal': 5, 'length': 400, 'tema_length_1': 5, 'tema_length_2': 8, 'tp': 1, 'sl': 4}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 100
    source_commission_percent = 0.018
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_reproduce_stops = True
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_012 md and exposed through the same PinePortBase interface used by batch_001.', 'Custom Pine function(s) are present; the original source is embedded verbatim and this generic pass flags them for per-strategy semantic verification.']

    def pine_indicators(self, dataframe, params):
        # Runtime evaluates the source against the complete OHLCV frame.
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch012Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
