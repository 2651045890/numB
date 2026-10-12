"""batch_011 port of 趋势顺势RSI波动捕捉策略Trend-Riding-RSI-Swing-Capture-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2024-01-04 00:00:00\nend: 2024-02-03 00:00:00\nperiod: 3h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// SwingSync RSI Strategy\n// This strategy combines RSI, MACD, and volume analysis to capture swing trading opportunities.\n// It includes risk management features to protect your capital.\n// Adjust the input parameters and backtest to optimize performance.// This Pine Script™ code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © str0zzapreti\n\n//@version=5\nstrategy(\'SwingSync RSI\', overlay=true)\n// Adjustable Parameters\n// var custom_message = input.string(\'\', title=\'Symbol\')\nma_period = input.int(20, title=\'Moving Average Period\')\nstop_loss_percent = input.float(1, title=\'STOP LOSS (%)\',step=0.1)\nmacd_fast_length = input(12, title=\'MACD Fast Length\')\nmacd_slow_length = input(26, title=\'MACD Slow Length\')\nmacd_signal_smoothing = input(9, title=\'MACD Signal Smoothing\')\nrsi_period = input(14, title=\'RSI Period\')\nrsi_overbought = input(70, title=\'RSI OVERBOUGHT LEVEL\')\nrsi_oversold = input(30, title=\'RSI OVERSOLD LEVEL\')\nvolume_ma_period = input(20, title="Volume MA Period")\nvolume_threshold_percent = input(50, title="Volume Threshold (%)")\nslippage = 0.5\nrisk_per_trade = input(1, title=\'Risk per Trade (%)\')\n\n// Calculating Indicators *\nprice = close\nma = ta.sma(price, ma_period)\nrsi = ta.rsi(price, rsi_period)\nvol_ma = ta.sma(volume, volume_ma_period)\n[macdLine, signalLine, _] = ta.macd(price, macd_fast_length, macd_slow_length, macd_signal_smoothing)\nvolume_threshold = vol_ma * (1 + volume_threshold_percent / 100)\n\n// Definitions\nvolumeCheck = volume > volume_threshold\nlongRsiCheck = rsi < rsi_overbought\nlongMovAvgCross = ta.crossover(price, ma)\nlongMovAvgCheck = price > ma\nlongMacdCross = ta.crossover(macdLine, signalLine)\nlongMacdCheck = macdLine > signalLine\nshortRsiCheck = rsi > rsi_oversold\nshortMovAvgCross = ta.crossunder(price, ma)\nshortMovAvgCheck = price < ma\nshortMacdCross = ta.crossunder(macdLine, signalLine)\nshortMacdCheck = macdLine < signalLine\n\n// Entry Conditions for Long and Short Trades\nlongCondition = volumeCheck and longRsiCheck and ((longMovAvgCross and longMacdCheck) or (longMacdCross and longMovAvgCheck)) \nshortCondition = volumeCheck and shortRsiCheck and  ((shortMovAvgCross and shortMacdCheck) or (shortMacdCross and shortMovAvgCheck)) \n\n// Tracking Last Trade Day\nvar int last_trade_day = na\n\nif longCondition or shortCondition\n    last_trade_day := dayofweek\n\n// Calculate can_exit_trade based on day difference\ncan_exit_trade = dayofweek != last_trade_day\n\n// Entry Orders\nvar float max_qty_based_on_equity = na\nvar float qty = na\n\nif longCondition\n    max_qty_based_on_equity := strategy.equity / price\n    qty := (strategy.equity * risk_per_trade / 100) / price\n    if qty > max_qty_based_on_equity\n        qty := max_qty_based_on_equity\n    strategy.entry(\'Long\', strategy.long, 1)\n\nif shortCondition\n    max_qty_based_on_equity := strategy.equity / price\n    qty := (strategy.equity * risk_per_trade / 100) / price\n    if qty > max_qty_based_on_equity\n        qty := max_qty_based_on_equity\n    strategy.entry(\'Short\', strategy.short, 1)\n\n// Exit Conditions\nexitLongCondition = ta.crossunder(price, ma) or rsi > rsi_overbought\nexitShortCondition = ta.crossover(price, ma) or rsi < rsi_oversold\n\n// Calculate take profit and stop loss levels\nstopLossLevelLong = strategy.position_avg_price * (1 - stop_loss_percent / 100)\nstopLossLevelShort = strategy.position_avg_price * (1 + stop_loss_percent / 100)\n\n// Adjust for slippage\nadjusted_stop_loss_long = stopLossLevelLong * (1 + slippage / 100)\nadjusted_stop_loss_short = stopLossLevelShort * (1 - slippage / 100)\n\n// Strategy Exit Orders for Long Positions\nif strategy.position_size > 0 and can_exit_trade\n    if (close < adjusted_stop_loss_long)\n        strategy.close(\'Long\', comment=\'Stop Loss Long\')\n    if exitLongCondition\n        strategy.close(\'Long\', comment=\'Exit Long\')\n\n// Strategy Exit Orders for Short Positions\nif strategy.position_size < 0 and can_exit_trade\n    if (close > adjusted_stop_loss_short)\n        strategy.close(\'Short\', comment=\'Stop Loss Short\')\n    if exitShortCondition\n        strategy.close(\'Short\', comment=\'Exit Short\')\n\nplot(ma)\n'

class SMBB95EF5021995A7F(PinePortBase, IStrategy):
    source_id = "SM_bb95ef5021995a7f"
    source_file = '趋势顺势RSI波动捕捉策略Trend-Riding-RSI-Swing-Capture-Strategy.md'
    timeframe = '3h'
    can_short = True
    source_defaults = {'ma_period': 20, 'stop_loss_percent': 1, 'macd_fast_length': 12, 'macd_slow_length': 26, 'macd_signal_smoothing': 9, 'rsi_period': 14, 'rsi_overbought': 70, 'rsi_oversold': 30, 'volume_ma_period': 20, 'volume_threshold_percent': 50, 'risk_per_trade': 1}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = False
    source_risk_flags = ['broker_state', 'tuple', 'var_state']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
