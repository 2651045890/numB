"""batch_012 port of 麦克德红蓝杠杆策略Macd-Blue-Red-Leverage-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2022-12-13 00:00:00\nend: 2023-12-19 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//Author: SudeepBisht\n//@version=3\nstrategy("SB_Elder Impulse System", overlay=true)\nuseCustomResolution=input(false, type=bool)\ncustomResolution=input("D")\nsource = request.security(syminfo.tickerid, useCustomResolution ? customResolution : timeframe.period, close)\nshowColorBars=input(false, type=bool)\nlengthEMA = input(13)\nfastLength = input(12, minval=1), slowLength=input(26,minval=1)\nsignalLength=input(9,minval=1)\n\ncalc_hist(source, fastLength, slowLength) =>\n    fastMA = ema(source, fastLength)\n    slowMA = ema(source, slowLength)\n    macd = fastMA - slowMA\n    signal = sma(macd, signalLength)\n    macd - signal\n\nget_color(emaSeries, macdHist) =>\n    g_f = (emaSeries > emaSeries[1]) and (macdHist > macdHist[1])\n    r_f = (emaSeries < emaSeries[1]) and (macdHist < macdHist[1])\n    g_f ? green : r_f ? red : blue\n    \nb_color = get_color(ema(source, lengthEMA), calc_hist(source, fastLength, slowLength))    \n//bgcolor(b_color, transp=0)\n//barcolor(showColorBars ? b_color : na)\n\nchk=b_color==green?1:b_color==red?-1:0\n\n\nif (not na(chk))\n    if(chk==1)\n        strategy.entry("RsiLE", strategy.long, comment="RsiLE")\n    if(chk==-1)\n        strategy.entry("RsiSE", strategy.short, comment="RsiSE")\n    if(chk==0)\n        strategy.close_all()\n'

class SMMacdBlueRedLeverageStrategy6d7630(PinePortBase, IStrategy):
    source_id = "SM_6d76309f80705a03"
    source_file = '麦克德红蓝杠杆策略Macd-Blue-Red-Leverage-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'useCustomResolution': False, 'customResolution': 'D', 'showColorBars': False, 'lengthEMA': 13, 'fastLength': 12, 'signalLength': 9}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_reproduce_stops = False
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_012 md and exposed through the same PinePortBase interface used by batch_001.', 'request.security/security is present: generic adapter keeps the expression but same-frame evaluation is only an approximation; manual multi-timeframe parity verification is required.', 'Custom Pine function(s) are present; the original source is embedded verbatim and this generic pass flags them for per-strategy semantic verification.']

    def pine_indicators(self, dataframe, params):
        # Runtime evaluates the source against the complete OHLCV frame.
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch012Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
