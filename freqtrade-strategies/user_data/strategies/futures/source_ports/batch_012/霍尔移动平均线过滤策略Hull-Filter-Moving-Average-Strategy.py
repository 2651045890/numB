"""batch_012 port of 霍尔移动平均线过滤策略Hull-Filter-Moving-Average-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-12-04 00:00:00\nend: 2024-01-03 00:00:00\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=4\nstrategy("Hull Filtered Strategy", overlay=true, pyramiding=0, default_qty_type= strategy.percent_of_equity, default_qty_value = 10, calc_on_order_fills=false, slippage=0,commission_type=strategy.commission.percent,commission_value=0)\n\n// Parameters for Hull Moving Averages\nsrc = input(close, title="Source")\nsignal_period = input(50, title="Period of signal HMA")\nfilter_period = input(200, title="Period of filter HMA")\n\nstrat_dir_input = input(title="Strategy Direction", defval="all", options=["long", "short", "all"])\n\n// Set allowed trading directions\nstrat_dir_value = strat_dir_input == "long" ? strategy.direction.long : strat_dir_input == "short" ? strategy.direction.short : strategy.direction.all\nstrategy.risk.allow_entry_in(strat_dir_value)\n\n// stop loss and take profit\nsl_factor = input(2,title="Stop Loss Factor")\ntp_factor = input(3,title="Take Profit Factor")\natr_period = input(14, title="ATR Period (SL/TP)")\n\n// Testing Start dates\ntestStartYear = input(2010, "Backtest Start Year")\ntestStartMonth = input(1, "Backtest Start Month")\ntestStartDay = input(1, "Backtest Start Day")\ntestPeriodStart = timestamp(testStartYear,testStartMonth,testStartDay,0,0)\n\n//Stop date if you want to use a specific range of dates\ntestStopYear = input(2030, "Backtest Stop Year")\ntestStopMonth = input(12, "Backtest Stop Month")\ntestStopDay = input(31, "Backtest Stop Day")\ntestPeriodStop = timestamp(testStopYear,testStopMonth,testStopDay,0,0)\n\n\n// -----------------------------------------------------------------------------\n// Global variables\n// -----------------------------------------------------------------------------\nvar float tp = na\nvar float sl = na\nvar float position = na\n\n\n// -----------------------------------------------------------------------------\n// Functions\n// -----------------------------------------------------------------------------\ntestWindow() =>\n    time >= testPeriodStart and time <= testPeriodStop ? true : false\n\n\n// -----------------------------------------------------------------------------\n// The engine\n// -----------------------------------------------------------------------------\nhma_signal = hma(src, signal_period)\nhma_filter = hma(src, filter_period)\n\n// Used to determine exits and stop losses\natr_e = atr(atr_period)\n\n// if hma_filter increases hma_trend is set to 1, if it decreases hma_trend is set to -1. If no trend is available, hma_trend is set to ß0\ntrend = hma_filter > hma_filter[1]  ?  1 : hma_filter < hma_filter[1] ? -1 : 0\nsignal = hma_signal > hma_signal[1] ? 1 : hma_signal  < hma_signal[1] ? -1 : 0\n\n\n// -----------------------------------------------------------------------------\n// signals\n// -----------------------------------------------------------------------------\nif signal[0] == 1 and signal[1] != 1 and trend == 1 and testWindow()\n    sl := close - sl_factor*atr_e\n    tp := close + tp_factor*atr_e\n    strategy.entry("HMA_LNG", strategy.long)\n    strategy.exit("LE", "HMA_LNG", profit=100*tp_factor*atr_e, loss=100*sl_factor*atr_e)\n    \nif signal[0] == -1 and signal[1] != -1 and trend == -1 and testWindow()\n    sl := close + sl_factor*atr_e\n    tp := close - tp_factor*atr_e\n    strategy.entry("HMA_SHRT", strategy.short)\n    strategy.exit("SE", "HMA_SHRT", profit=100*tp_factor*atr_e, loss=100*sl_factor*atr_e)\n\n\nif strategy.position_size != 0\n    sl := sl[1]\n    tp := tp[1]\n\n// -----------------------------------------------------------------------------\n// PLOT\n// -----------------------------------------------------------------------------\nhma_s = plot(hma_signal, title="SIGNAL", color = signal == 1 ? color.green : color.red)\nhma_l = plot(hma_filter, title="TREND", color = trend == 1 ? color.green : color.red)\n\nplot(tp, title="TAKE PROFIT", color= strategy.position_size != 0 ? color.blue: na, linewidth=1)  \nplot(sl, title="STOP LOSS", color= strategy.position_size != 0 ? color.red: na, linewidth = 1)\n\n'

class SMHullFilterMovingAverageStrategy9f4abc(PinePortBase, IStrategy):
    source_id = "SM_9f4abc6056f77615"
    source_file = '霍尔移动平均线过滤策略Hull-Filter-Moving-Average-Strategy.md'
    timeframe = '1h'
    can_short = True
    source_defaults = {'src': 'close', 'signal_period': 50, 'filter_period': 200, 'strat_dir_input': 'all', 'sl_factor': 2, 'tp_factor': 3, 'atr_period': 14, 'testStartYear': 2010, 'testStartMonth': 1, 'testStartDay': 1, 'testStopYear': 2030, 'testStopMonth': 12, 'testStopDay': 31}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 10
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_reproduce_stops = True
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_012 md and exposed through the same PinePortBase interface used by batch_001.', 'Custom Pine function(s) are present; the original source is embedded verbatim and this generic pass flags them for per-strategy semantic verification.', 'The source reads live strategy position state; batch_001-style broker-state parity must be checked manually for this file.']

    def pine_indicators(self, dataframe, params):
        # Runtime evaluates the source against the complete OHLCV frame.
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch012Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
