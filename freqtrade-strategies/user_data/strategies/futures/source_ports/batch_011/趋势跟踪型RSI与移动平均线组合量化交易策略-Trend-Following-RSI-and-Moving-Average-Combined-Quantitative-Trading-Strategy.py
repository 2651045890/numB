"""batch_011 port of 趋势跟踪型RSI与移动平均线组合量化交易策略-Trend-Following-RSI-and-Moving-Average-Combined-Quantitative-Trading-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2019-12-23 08:00:00\nend: 2025-01-04 08:00:00\nperiod: 1d\nbasePeriod: 1d\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This Pine Script™ code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © raiford87\n\n//@version=6\nstrategy("RSI + MA Trend Strategy (v6)",\n     shorttitle="RSI_MA_Trend_v6",\n     overlay=true,\n     initial_capital=50000,\n     default_qty_type=strategy.fixed,\n     default_qty_value=1)\n\n// ─────────────────────────────────────────────────────────────────────────────────────\n// 1. USER INPUTS\n// ─────────────────────────────────────────────────────────────────────────────────────\nmaLength       = input.int(50,   "Moving Average Length")\nrsiLength      = input.int(14,   "RSI Length")\nrsiBuyLevel    = input.int(55,   "RSI > X for Buy",  minval=1, maxval=99)\nrsiSellLevel   = input.int(45,   "RSI < X for Sell", minval=1, maxval=99)\n\nstopLossPerc   = input.float(1.0,  "Stop Loss %",    minval=0.1)\ntakeProfitPerc = input.float(2.0,  "Take Profit %",  minval=0.1)\n\n// ─────────────────────────────────────────────────────────────────────────────────────\n// 2. INDICATOR CALCULATIONS\n// ─────────────────────────────────────────────────────────────────────────────────────\nmaValue = ta.sma(close, maLength)\nrsiVal  = ta.rsi(close, rsiLength)\n\n// Trend conditions\nbullTrend = close > maValue\nbearTrend = close < maValue\n\n// RSI conditions\nrsiBull   = rsiVal > rsiBuyLevel\nrsiBear   = rsiVal < rsiSellLevel\n\n// ─────────────────────────────────────────────────────────────────────────────────────\n// 3. ENTRY CONDITIONS\n// ─────────────────────────────────────────────────────────────────────────────────────\nlongCondition  = bullTrend and rsiBull\nshortCondition = bearTrend and rsiBear\n\nif longCondition\n    strategy.entry("RSI MA Long", strategy.long)\nif shortCondition\n    strategy.entry("RSI MA Short", strategy.short)\n\n// ─────────────────────────────────────────────────────────────────────────────────────\n// 4. STOP LOSS & TAKE PROFIT\n// ─────────────────────────────────────────────────────────────────────────────────────\nstopLossLevel   = stopLossPerc   * 0.01\ntakeProfitLevel = takeProfitPerc * 0.01\n\nif strategy.position_size > 0\n    stopPriceLong = strategy.position_avg_price * (1 - stopLossLevel)\n    tpPriceLong   = strategy.position_avg_price * (1 + takeProfitLevel)\n    strategy.exit("Exit Long", from_entry="RSI MA Long", stop=stopPriceLong, limit=tpPriceLong)\n\nif strategy.position_size < 0\n    stopPriceShort = strategy.position_avg_price * (1 + stopLossLevel)\n    tpPriceShort   = strategy.position_avg_price * (1 - takeProfitLevel)\n    strategy.exit("Exit Short", from_entry="RSI MA Short", stop=stopPriceShort, limit=tpPriceShort)\n\n// ─────────────────────────────────────────────────────────────────────────────────────\n// 5. PLOT SIGNALS & LEVELS\n// ─────────────────────────────────────────────────────────────────────────────────────\nplot(maValue, color=color.yellow, linewidth=2, title="Moving Average")\n\nplotchar(longCondition,  title="Long Signal",  char=\'▲\', location=location.belowbar, color=color.green, size=size.tiny)\nplotchar(shortCondition, title="Short Signal", char=\'▼\', location=location.abovebar, color=color.red,   size=size.tiny)\n\n// Plot Stop & TP lines\nposIsLong  = strategy.position_size > 0\nposIsShort = strategy.position_size < 0\n\nplotStopLong = posIsLong ? strategy.position_avg_price * (1 - stopLossLevel) : na\nplotTpLong   = posIsLong ? strategy.position_avg_price * (1 + takeProfitLevel): na\nplotStopShort= posIsShort? strategy.position_avg_price * (1 + stopLossLevel) : na\nplotTpShort  = posIsShort? strategy.position_avg_price * (1 - takeProfitLevel): na\n\nplot(plotStopLong,  color=color.red,   linewidth=2, style=plot.style_line, title="Stop Loss Long")\nplot(plotTpLong,    color=color.green, linewidth=2, style=plot.style_line, title="Take Profit Long")\nplot(plotStopShort, color=color.red,   linewidth=2, style=plot.style_line, title="Stop Loss Short")\nplot(plotTpShort,   color=color.green, linewidth=2, style=plot.style_line, title="Take Profit Short")\n'

class SMEAB3D2A509B26536(PinePortBase, IStrategy):
    source_id = "SM_eab3d2a509b26536"
    source_file = '趋势跟踪型RSI与移动平均线组合量化交易策略-Trend-Following-RSI-and-Moving-Average-Combined-Quantitative-Trading-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'maLength': 50, 'rsiLength': 14, 'rsiBuyLevel': 55, 'rsiSellLevel': 45, 'stopLossPerc': 1.0, 'takeProfitPerc': 2.0}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 50000
    source_reproduce_stops = True
    source_risk_flags = ['broker_state', 'exit_order']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
