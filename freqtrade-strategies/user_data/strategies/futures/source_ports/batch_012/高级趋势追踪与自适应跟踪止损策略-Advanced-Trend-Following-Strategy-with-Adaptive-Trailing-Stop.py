"""batch_012 port of 高级趋势追踪与自适应跟踪止损策略-Advanced-Trend-Following-Strategy-with-Adaptive-Trailing-Stop.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2019-12-23 08:00:00\nend: 2024-12-18 08:00:00\nperiod: 1d\nbasePeriod: 1d\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=6\nstrategy("Supertrend Strategy with Adjustable Trailing Stop [Bips]", overlay=true, default_qty_type=strategy.percent_of_equity, default_qty_value=15)\n\n// Inputs\natrPeriod = input(10, "ATR Länge", "Average True Range „wahre durchschnittliche Schwankungsbreite“ und stammt aus der technischen Analyse. Die ATR misst die Volatilität eines Instruments oder eines Marktes. Mit ihr kann die Wahrscheinlichkeit für einen Trendwechsel bestimmt werden.", group="Supertrend Settings")\nfactor = input.float(3.0, "Faktor", step=0.1, group="Supertrend Settings")\ntradeDirection = input.string("Long", "Trade Direction", options=["Both", "Long", "Short"], group="Supertrend Settings")\nsl_type    = input.string("%", "SL Type", options=["%", "ATR", "Absolute"])\n// Parameter für ST nur für einstieg -> Beim Ausstieg fragen ob der bool WWert true ist -> Für weniger und längere Trädes \n\nsl_perc    = input.float(4.0, "% SL", group="Stop Loss Einstellung")\natr_length = input.int(10, "ATR Length", group="Stop Loss Einstellung")\natr_mult   = input.float(2.0, "ATR Mult", group="Stop Loss Einstellung")\nsl_absol   = input.float(10.0, "Absolute SL", group="Stop Loss Einstellung")\n\n//-------------------------//\n// BACKTESTING RANGE\nfromDay   = input.int(defval=1, title="From Day", minval=1, maxval=31, group="Backtesting Einstellung")\nfromMonth = input.int(defval=1, title="From Month", minval=1, maxval=12, group="Backtesting Einstellung")\nfromYear  = input.int(defval=2016, title="From Year", minval=1970, group="Backtesting Einstellung")\ntoDay     = input.int(defval=1, title="To Day", minval=1, maxval=31, group="Backtesting Einstellung")\ntoMonth   = input.int(defval=1, title="To Month", minval=1, maxval=12, group="Backtesting Einstellung")\ntoYear    = input.int(defval=2100, title="To Year", minval=1970, group="Backtesting Einstellung")\n\nstartDate  = timestamp(fromYear, fromMonth, fromDay, 00, 00)\nfinishDate = timestamp(toYear, toMonth, toDay, 00, 00)\ntime_cond  = time >= startDate and time <= finishDate\n\n//-------------------------//\n// Supertrend calculation\n[_, direction] = ta.supertrend(factor, atrPeriod)\n\n// SL values\nsl_val = sl_type == "ATR"      ? atr_mult * ta.atr(atr_length) : \n         sl_type == "Absolute" ? sl_absol : \n         close * sl_perc / 100\n         \n// Init Variables\nvar pos         = 0\nvar float trailing_sl = 0.0\n\n// Signals\nlong_signal  = nz(pos[1]) !=  1 and high > nz(trailing_sl[1])\nshort_signal = nz(pos[1]) != -1 and low  < nz(trailing_sl[1]) \n\n// Calculate SL\ntrailing_sl := short_signal     ? high + sl_val : \n               long_signal      ? low  - sl_val : \n               nz(pos[1]) ==  1 ? math.max(low  - sl_val, nz(trailing_sl[1])) :  \n               nz(pos[1]) == -1 ? math.min(high + sl_val, nz(trailing_sl[1])) : \n               nz(trailing_sl[1])\n               \n// Position var               \npos := long_signal  ? 1 : short_signal ? -1 : nz(pos[1]) \n\n// Entry logic\nif ta.change(direction) < 0 and time_cond\n    if tradeDirection == "Both" or tradeDirection == "Long"\n        strategy.entry("Long", strategy.long, stop=trailing_sl)\n    else\n        strategy.close_all("Stop Short")\n\nif ta.change(direction) > 0 and time_cond\n    if tradeDirection == "Both" or tradeDirection == "Short"\n        strategy.entry("Short", strategy.short, stop=trailing_sl)\n    else\n        strategy.close_all("Stop Long")\n\n// Exit logic: Trailing Stop and Supertrend\n//if strategy.position_size > 0 and not na(trailing_sl)\n    //strategy.exit("SL-Exit Long", from_entry="Long", stop=trailing_sl)\n\n//if strategy.position_size < 0 and not na(trailing_sl)\n    //strategy.exit("SL-Exit Short", from_entry="Short", stop=trailing_sl)\n\n// Trailing Stop visualization\nplot(trailing_sl, linewidth = 2, color = pos == 1 ? color.green : color.red)\n//plot(not na(trailing_sl) ? trailing_sl : na, color=pos == 1 ? color.green : color.red, linewidth=2, title="Trailing Stop")\n\n'

class SMAdvancedTrendFollowingStrategywithAdaptiveTrailingStop5ea28d(PinePortBase, IStrategy):
    source_id = "SM_5ea28ded780e63c4"
    source_file = '高级趋势追踪与自适应跟踪止损策略-Advanced-Trend-Following-Strategy-with-Adaptive-Trailing-Stop.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'atrPeriod': 10, 'factor': 3.0, 'tradeDirection': 'Long', 'sl_type': '%', 'sl_perc': 4.0, 'atr_length': 10, 'atr_mult': 2.0, 'sl_absol': 10.0, 'fromDay': 1, 'fromMonth': 1, 'fromYear': 2016, 'toDay': 1, 'toMonth': 1, 'toYear': 2100}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 15
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_reproduce_stops = True
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_012 md and exposed through the same PinePortBase interface used by batch_001.', 'The source reads live strategy position state; batch_001-style broker-state parity must be checked manually for this file.']

    def pine_indicators(self, dataframe, params):
        # Runtime evaluates the source against the complete OHLCV frame.
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch012Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
