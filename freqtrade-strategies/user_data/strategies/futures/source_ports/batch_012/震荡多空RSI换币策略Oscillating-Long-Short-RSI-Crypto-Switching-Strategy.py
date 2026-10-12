"""batch_012 port of 震荡多空RSI换币策略Oscillating-Long-Short-RSI-Crypto-Switching-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-12-17 00:00:00\nend: 2023-12-24 00:00:00\nperiod: 3m\nbasePeriod: 1m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This source code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © exlux99\n\n//@version=4\n\nstrategy(title="Ichimoku + RSI Crypto trending strategy", overlay=true, initial_capital = 1000, default_qty_type=strategy.percent_of_equity, default_qty_value=100, commission_type=strategy.commission.percent, commission_value=0.1, pyramiding=1  )\n\nUseHAcandles    = input(true, title="Use Heikin Ashi Candles in Algo Calculations")\n//\n// === /INPUTS ===\n\n// === BASE FUNCTIONS ===\n\nhaClose = UseHAcandles ? security(heikinashi(syminfo.tickerid), timeframe.period, close) : close\nhaOpen  = UseHAcandles ? security(heikinashi(syminfo.tickerid), timeframe.period, open) : open\nhaHigh  = UseHAcandles ? security(heikinashi(syminfo.tickerid), timeframe.period, high) : high\nhaLow   = UseHAcandles ? security(heikinashi(syminfo.tickerid), timeframe.period, low) : low\n\n\n//Inputs\nts_bars = input(20, minval=1, title="Tenkan-Sen Bars")\nks_bars = input(50, minval=1, title="Kijun-Sen Bars")\nssb_bars = input(120, minval=1, title="Senkou-Span B Bars")\ncs_offset = input(30, minval=1, title="Chikou-Span Offset")\nss_offset = input(30, minval=1, title="Senkou-Span Offset")\nlong_entry = input(true, title="Long Entry")\nshort_entry = input(true, title="Short Entry")\n\n//Volatility\n//vollength = input(defval=1, title="VolLength")\n//voltarget = input(defval=0., type=input.float, step=0.1, title="Volatility Target")\n//Difference = abs((haClose - haOpen)/((haClose + haOpen)/2) * 100)\n//MovingAverage = sma(Difference, vollength)\n//highvolatility = MovingAverage > voltarget\n\n////////////////////////////////////////////////////////////////////////////////\n// BACKTESTING RANGE\n \n// From Date Inputs\nfromDay = input(defval = 1, title = "From Day", minval = 1, maxval = 31)\nfromMonth = input(defval = 1, title = "From Month", minval = 1, maxval = 12)\nfromYear = input(defval = 2019, title = "From Year", minval = 1970)\n \n// To Date Inputs\ntoDay = input(defval = 31, title = "To Day", minval = 1, maxval = 31)\ntoMonth = input(defval = 12, title = "To Month", minval = 1, maxval = 12)\ntoYear = input(defval = 2021, title = "To Year", minval = 1970)\n \n// Calculate start/end date and time condition\nstartDate = timestamp(fromYear, fromMonth, fromDay, 00, 00)\nfinishDate = timestamp(toYear, toMonth, toDay, 00, 00)\ntime_cond = true\n \n////////////////////////////////////////////////////////////////////////////////\n\nmiddle(len) => avg(lowest(len), highest(len))\n\n// Ichimoku Components\ntenkan = middle(ts_bars)\nkijun = middle(ks_bars)\nsenkouA = avg(tenkan, kijun)\nsenkouB = middle(ssb_bars)\n\n//RSI\nchange = change(haClose)\ngain = change >= 0 ? change : 0.0\nloss = change < 0 ? (-1) * change : 0.0\navgGain = rma(gain, 14)\navgLoss = rma(loss, 14)\nrs = avgGain / avgLoss\nrsi = 100 - (100 / (1 + rs))\n\nss_high = max(senkouA[ss_offset-1], senkouB[ss_offset-1])\nss_low = min(senkouA[ss_offset-1], senkouB[ss_offset-1])\n\n// Entry/Exit Signals\ntk_cross_bull = tenkan > kijun\ntk_cross_bear = tenkan < kijun\ncs_cross_bull = mom(haClose, cs_offset-1) > 0\ncs_cross_bear = mom(haClose, cs_offset-1) < 0\nprice_above_kumo = haClose > ss_high\nprice_below_kumo = haClose < ss_low\nrsi_bullish = rsi > 50\nrsi_bearish = rs < 50\nbullish = tk_cross_bull and cs_cross_bull and price_above_kumo and rsi_bullish //and highvolatility\nbearish = tk_cross_bear and cs_cross_bear and price_below_kumo and rsi_bearish //and highvolatility\n\nstrategy.entry("Long", strategy.long, when=bullish and long_entry and time_cond)\nstrategy.entry("Short", strategy.short, when=bearish and short_entry and time_cond)\n\nstrategy.close("Long", when=bearish and not short_entry and time_cond)\nstrategy.close("Short", when=bullish and not long_entry and time_cond)\n\n\n\n'

class SMRSIOscillatingLongShortRSICryptoSwitchingStrategyf8ee4d(PinePortBase, IStrategy):
    source_id = "SM_f8ee4d02bafd5f08"
    source_file = '震荡多空RSI换币策略Oscillating-Long-Short-RSI-Crypto-Switching-Strategy.md'
    timeframe = '3m'
    can_short = True
    source_defaults = {'UseHAcandles': True, 'ts_bars': 20, 'ks_bars': 50, 'ssb_bars': 120, 'cs_offset': 30, 'ss_offset': 30, 'long_entry': True, 'short_entry': True, 'fromDay': 1, 'fromMonth': 1, 'fromYear': 2019, 'toDay': 31, 'toMonth': 12, 'toYear': 2021}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 100
    source_commission_percent = 0.1
    source_pyramiding = 1
    source_initial_capital = 1000
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
