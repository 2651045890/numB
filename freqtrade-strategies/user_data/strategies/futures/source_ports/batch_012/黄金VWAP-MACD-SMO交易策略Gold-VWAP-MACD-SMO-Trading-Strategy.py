"""batch_012 port of 黄金VWAP-MACD-SMO交易策略Gold-VWAP-MACD-SMO-Trading-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-09-19 00:00:00\nend: 2023-10-19 00:00:00\nperiod: 4h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This source code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © exlux99\n\n//@version=4\n// strategy("VWAP Gold strategy", overlay = true, default_qty_type = strategy.percent_of_equity, default_qty_value = 10000, calc_on_every_tick = true, commission_type = strategy.commission.percent, commission_value = 0.005)\n\n\nsource = input(low)\n\n\n//vwap monthly\ntimeframeM = time("M")\nbeginningM = na(timeframeM[1]) or timeframeM > timeframeM[1]\n\nsumsourceM = source * volume\nsumVolM = volume\nsumsourceM := beginningM ? sumsourceM : sumsourceM + sumsourceM[1]\nsumVolM := beginningM ? sumVolM : sumVolM + sumVolM[1]\nvwapMonthly= sumsourceM / sumVolM\n\n//macd\nfast_length = input(title="Fast Length", type=input.integer, defval=12)\nslow_length = input(title="Slow Length", type=input.integer, defval=26)\nsrc = input(title="Source", type=input.source, defval=close)\nsignal_length = input(title="Signal Smoothing", type=input.integer, minval = 1, maxval = 50, defval = 9)\n\n\nfast_ma = ema(src, fast_length)\nslow_ma = ema(src, slow_length)\nmacd = fast_ma - slow_ma\nsignal =  ema(macd, signal_length)\nhist = macd - signal\n\n\n//SMO\nlonglen = input(22, minval=1, title="Long Length SMO")\nshortlen = input(6, minval=1, title="Short Length SMO")\nsiglen = input(5, minval=1, title="Signal Line Length SMO")\nerg = tsi(close, shortlen, longlen)\nsig = ema(erg, siglen)\nosc = erg - sig\n\n\nshortCondition =  close < vwapMonthly and hist < hist[1] and osc < 0\nlongCondition =  close > vwapMonthly and hist> hist[1] and osc > 0\n\ntplong=input(0.085, step=0.005, title="Take profit % for long")\nsllong=input(0.03, step=0.005, title="Stop loss % for long")\ntpshort=input(0.05, step=0.005, title="Take profit % for short")\nslshort=input(0.025, step=0.005, title="Stop loss % for short")\n\nstrategy.entry("long",1,when=longCondition)\nstrategy.entry("short",0,when=shortCondition)\n\nstrategy.exit("short_tp/sl", "long", profit=close * tplong / syminfo.mintick, loss=close * sllong / syminfo.mintick, comment=\'LONG EXIT\',  alert_message = \'closeshort\')\nstrategy.exit("short_tp/sl", "short", profit=close * tpshort / syminfo.mintick, loss=close * slshort / syminfo.mintick, comment=\'SHORT EXIT\',  alert_message = \'closeshort\')\n\n\n\n'

class SMVWAPMACDSMOGoldVWAPMACDSMOTradingStrategy7a2791(PinePortBase, IStrategy):
    source_id = "SM_7a2791a292ef615a"
    source_file = '黄金VWAP-MACD-SMO交易策略Gold-VWAP-MACD-SMO-Trading-Strategy.md'
    timeframe = '4h'
    can_short = False
    source_defaults = {'source': 'low', 'fast_length': 12, 'slow_length': 26, 'src': 'close', 'signal_length': 9, 'longlen': 22, 'shortlen': 6, 'siglen': 5, 'tplong': 0.085, 'sllong': 0.03, 'tpshort': 0.05, 'slshort': 0.025}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 10000
    source_commission_percent = 0.005
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
