"""batch_011 port of 趋势突破-长阴影策略Trend-Breakout-Long-Shadow-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2022-11-08 00:00:00\nend: 2023-11-14 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This source code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © ondrej17\n\n//@version=4\nstrategy("longWickstrategy", overlay=true )\n \n// Inputs\nst_yr_inp = input(defval=2020, title=\'Backtest Start Year\')\nst_mn_inp = input(defval=01, title=\'Backtest Start Month\')\nst_dy_inp = input(defval=01, title=\'Backtest Start Day\')\nen_yr_inp = input(defval=2025, title=\'Backtest End Year\')\nen_mn_inp = input(defval=01, title=\'Backtest End Month\')\nen_dy_inp = input(defval=01, title=\'Backtest End Day\')\nsltp_inp = input(defval=0.8, title=\'N - % offset for N*SL and (2N)*TP\')/100\n \n// Dates\nstart = timestamp(st_yr_inp, st_mn_inp, st_dy_inp,00,00)\nend = timestamp(en_yr_inp, en_mn_inp, en_dy_inp,00,00)\ncanTrade = time >= start and time <= end\n// Indicators Setup\n\n\n \n// Strategy Calcuations\nlowerWick = (open > close) ? close-low : open - low\nupperWick = (open > close) ? high-open : high-close\nwickLength = max(lowerWick,upperWick)\ncandleLength = high-low\nwickToCandleRatio = wickLength / candleLength\nentryFilterCandleLength = candleLength > 0.75*atr(48)\n\n\n// Entries and Exits\n \nlongCondition = entryFilterCandleLength and wickToCandleRatio > 0.5 and lowerWick > upperWick and canTrade and strategy.position_size == 0\nshortCondition = entryFilterCandleLength and wickToCandleRatio > 0.5 and lowerWick < upperWick and canTrade and strategy.position_size == 0\n\nstrategy.entry("pendingLong", strategy.long, limit=low+wickLength/2, when = longCondition)\nstrategy.entry("pendingShort", strategy.short, limit=high-wickLength/2, when = shortCondition)\n\nlongStop = strategy.position_size > 0 ? strategy.position_avg_price*(1-sltp_inp) : na\nlongTP = strategy.position_size > 0 ? strategy.position_avg_price*(1+2*sltp_inp) : na\nshortStop = strategy.position_size < 0 ? strategy.position_avg_price*(1+sltp_inp) : na\nshortTP = strategy.position_size < 0 ? strategy.position_avg_price*(1-2*sltp_inp) : na\n\nstrategy.exit("longSLTP","pendingLong", stop=longStop, limit = longTP)\nstrategy.exit("shortSLTP","pendingShort", stop=shortStop, limit = shortTP)  \n \n\nplot(longStop, color=color.red, style=plot.style_linebr, linewidth=2)\nplot(shortStop, color=color.red, style=plot.style_linebr, linewidth=2)\nplot(longTP, color=color.green, style=plot.style_linebr, linewidth=2)\nplot(shortTP, color=color.green, style=plot.style_linebr, linewidth=2)\n\nplotLongCondition = longCondition ? high+abs(open-close) : na\nplot(plotLongCondition, style=plot.style_circles, linewidth=4, color=color.green)\nplotShortCondition = shortCondition ? high+abs(open-close) : na\nplot(plotShortCondition, style=plot.style_circles, linewidth=4, color=color.red)\n\n'

class SMF62E2200E3269E57(PinePortBase, IStrategy):
    source_id = "SM_f62e2200e3269e57"
    source_file = '趋势突破-长阴影策略Trend-Breakout-Long-Shadow-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'st_yr_inp': 2020, 'en_yr_inp': 2025, 'sltp_inp': 0.8}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = True
    source_risk_flags = ['broker_state', 'entry_price_order', 'exit_order']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
