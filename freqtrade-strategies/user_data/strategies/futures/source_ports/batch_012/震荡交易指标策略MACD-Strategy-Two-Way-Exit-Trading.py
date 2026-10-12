"""batch_012 port of 震荡交易指标策略MACD-Strategy-Two-Way-Exit-Trading.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2022-12-05 00:00:00\nend: 2023-12-11 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This source code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © maxencetajet\n\n//@version=5\nstrategy("MACD Strategy", overlay=true, initial_capital=1000, slippage=25)\n\nsrc = input(title="Source", defval=close)\ntarget_stop_ratio = input.float(title=\'Risk/Reward\', defval=2, minval=0.5, maxval=100)\nrisk = input.float(2, title="Risk per Trade %")\n\nriskt = risk / 100 + 1\n\nuseDateFilter = input.bool(true, title="Filter Date Range of Backtest",\n     group="Backtest Time Period")\nbacktestStartDate = input(timestamp("5 June 2022"), \n     title="Start Date", group="Backtest Time Period",\n     tooltip="This start date is in the time zone of the exchange " + \n     "where the chart\'s instrument trades. It doesn\'t use the time " + \n     "zone of the chart or of your computer.")\nbacktestEndDate = input(timestamp("5 July 2022"),\n     title="End Date", group="Backtest Time Period",\n     tooltip="This end date is in the time zone of the exchange " + \n     "where the chart\'s instrument trades. It doesn\'t use the time " + \n     "zone of the chart or of your computer.")\n\ninTradeWindow =  true\nemaV = input.int(200, title="Length", group="EMA")\nswingHighV = input.int(7, title="Swing High", group="number of past candles")\nswingLowV = input.int(7, title="Swing Low", group="number of past candles")\n\nema = ta.ema(src, emaV)\n\nfast_length = input(title="Fast Length", defval=12, group="MACD")\nslow_length = input(title="Slow Length", defval=26, group="MACD")\nsignal_length = input.int(title="Signal Smoothing",  minval = 1, maxval = 50, defval = 9, group="MACD")\nsma_source = input.string(title="Oscillator MA Type",  defval="EMA", options=["SMA", "EMA"], group="MACD")\nsma_signal = input.string(title="Signal Line MA Type", defval="EMA", options=["SMA", "EMA"], group="MACD")\n\nfast_ma = sma_source == "SMA" ? ta.sma(src, fast_length) : ta.ema(src, fast_length)\nslow_ma = sma_source == "SMA" ? ta.sma(src, slow_length) : ta.ema(src, slow_length)\nmacd = fast_ma - slow_ma\nsignal = sma_signal == "SMA" ? ta.sma(macd, signal_length) : ta.ema(macd, signal_length)\nhist = macd - signal\n\nlongcondition = close > ema and ta.crossover(macd, signal) and macd < 0\nshortcondition = close < ema and ta.crossunder(macd, signal) and macd > 0\n\nfloat risk_long = na\nfloat risk_short = na\nfloat stopLoss = na\nfloat takeProfit = na\nfloat entry_price = na\n\nrisk_long := risk_long[1]\nrisk_short := risk_short[1]\n\nswingHigh = ta.highest(high, swingHighV)\nswingLow = ta.lowest(low, swingLowV)\n\nlotB = (strategy.equity*riskt-strategy.equity)/(close - swingLow)\nlotS = (strategy.equity*riskt-strategy.equity)/(swingHigh - close)\n\nif strategy.position_size == 0 and longcondition and inTradeWindow\n    risk_long := (close - swingLow) / close\n    strategy.entry("long", strategy.long, qty=lotB)\n    \nif strategy.position_size == 0 and shortcondition and inTradeWindow\n    risk_short := (swingHigh - close) / close  \n    strategy.entry("short", strategy.short, qty=lotS)\n\nif strategy.position_size > 0\n\n    stopLoss := strategy.position_avg_price * (1 - risk_long)\n    takeProfit := strategy.position_avg_price * (1 + target_stop_ratio * risk_long)\n    entry_price := strategy.position_avg_price\n    strategy.exit("long exit", "long", stop = stopLoss, limit = takeProfit)\n    \nif strategy.position_size < 0\n\n    stopLoss := strategy.position_avg_price * (1 + risk_short)\n    takeProfit := strategy.position_avg_price * (1 - target_stop_ratio * risk_short)\n    entry_price := strategy.position_avg_price\n    strategy.exit("short exit", "short", stop = stopLoss, limit = takeProfit)\n    \nplot(ema, color=color.white, linewidth=2, title="EMA")\np_ep = plot(entry_price, color=color.new(color.white, 0), linewidth=2, style=plot.style_linebr, title=\'entry price\')\np_sl = plot(stopLoss, color=color.new(color.red, 0), linewidth=2, style=plot.style_linebr, title=\'stopLoss\')\np_tp = plot(takeProfit, color=color.new(color.green, 0), linewidth=2, style=plot.style_linebr, title=\'takeProfit\')\nfill(p_sl, p_ep, color.new(color.red, transp=85))\nfill(p_tp, p_ep, color.new(color.green, transp=85))\n\n\n'

class SMMACDStrategyTwoWayExitTradinge193e8(PinePortBase, IStrategy):
    source_id = "SM_e193e8ae827de4c3"
    source_file = '震荡交易指标策略MACD-Strategy-Two-Way-Exit-Trading.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'src': 'close', 'target_stop_ratio': 2, 'risk': 2, 'emaV': 200, 'swingHighV': 7, 'swingLowV': 7, 'fast_length': 12, 'slow_length': 26, 'signal_length': 9, 'sma_source': 'EMA', 'sma_signal': 'EMA'}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1000
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
