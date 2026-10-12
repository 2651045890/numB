"""batch_011 port of 自适应波动率与动量量化交易系统AVMQTS-Adaptive-Volatility-and-Momentum-Quantitative-Trading-System-AVMQTS.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2019-12-23 08:00:00\nend: 2024-11-25 08:00:00\nperiod: 1d\nbasePeriod: 1d\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("[ETH] Volatility & Momentum Adaptive Strategy", shorttitle="Definitive 1 day Ethereum Signal", overlay=true, initial_capital=10000, currency=currency.USD)\n\n// === Input Parameters === //\ntrade_size = input.float(5, title="Trade Size (ETH)")\natr_length = input.int(8, minval=1, title="ATR Length")\nmacd_fast = input.int(8, minval=1, title="MACD Fast Length")\nmacd_slow = input.int(7, minval=1, title="MACD Slow Length")\nmacd_signal = input.int(9, minval=1, title="MACD Signal Length")\nmomentum_length = input.int(37, title="Momentum Length")\nstop_loss_percent = input.float(9.9, title="Stop Loss Percentage (%)")\ntake_profit_percent = input.float(9.0, title="Take Profit Percentage (%)")\nalternate_signal = input.bool(true, title="Alternate Buy/Sell Signals")\n\n// === Indicators === //\n// ATR to measure volatility\natr = ta.atr(atr_length)\n\n// MACD for trend momentum\n[macd_line, signal_line, _] = ta.macd(close, macd_fast, macd_slow, macd_signal)\nmacd_cross_up = ta.crossover(macd_line, signal_line)\nmacd_cross_down = ta.crossunder(macd_line, signal_line)\n\n// Momentum\nmomentum = ta.mom(close, momentum_length)\n\n// === Signal Control Variables === //\nvar bool last_signal_long = na\nvar int last_trade_bar = na\nmin_bars_between_trades = 5 // Adjust for minimal trade frequency control\ntime_elapsed = na(last_trade_bar) or (bar_index - last_trade_bar) >= min_bars_between_trades\n\n// === Buy and Sell Conditions === //\n// Buy when:\nbuy_signal = (macd_cross_up and momentum > 0 and close > ta.sma(close, 50) and time_elapsed)\n\n// Sell when:\nsell_signal = (macd_cross_down and momentum < 0 and close < ta.sma(close, 50) and time_elapsed)\n\n// Enforce alternate signals if selected\nif alternate_signal\n    buy_signal := buy_signal and (na(last_signal_long) or not last_signal_long)\n    sell_signal := sell_signal and (not na(last_signal_long) and last_signal_long)\n\n// === Trade Execution === //\n// Buy Position\nif (buy_signal)\n    if strategy.position_size < 0\n        strategy.close("Short")\n    strategy.entry("Long", strategy.long, qty=trade_size)\n    last_signal_long := true\n    last_trade_bar := bar_index\n\n// Sell Position\nif (sell_signal)\n    if strategy.position_size > 0\n        strategy.close("Long")\n    strategy.entry("Short", strategy.short, qty=trade_size)\n    last_signal_long := false\n    last_trade_bar := bar_index\n\n// === Stop Loss and Take Profit === //\nif strategy.position_size > 0\n    long_take_profit = strategy.position_avg_price * (1 + take_profit_percent / 100)\n    long_stop_loss = strategy.position_avg_price * (1 - stop_loss_percent / 100)\n    strategy.exit("TP/SL Long", from_entry="Long", limit=long_take_profit, stop=long_stop_loss)\n\nif strategy.position_size < 0\n    short_take_profit = strategy.position_avg_price * (1 - take_profit_percent / 100)\n    short_stop_loss = strategy.position_avg_price * (1 + stop_loss_percent / 100)\n    strategy.exit("TP/SL Short", from_entry="Short", limit=short_take_profit, stop=short_stop_loss)\n\n// === Visual Signals === //\nplotshape(series=buy_signal and time_elapsed, title="Buy Signal", location=location.belowbar, color=color.green, style=shape.labelup, text="BUY")\nplotshape(series=sell_signal and time_elapsed, title="Sell Signal", location=location.abovebar, color=color.red, style=shape.labeldown, text="SELL")\n'

class SME63FD9EF0A4D9AB1(PinePortBase, IStrategy):
    source_id = "SM_e63fd9ef0a4d9ab1"
    source_file = '自适应波动率与动量量化交易系统AVMQTS-Adaptive-Volatility-and-Momentum-Quantitative-Trading-System-AVMQTS.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'trade_size': 5, 'atr_length': 8, 'macd_fast': 8, 'macd_slow': 7, 'macd_signal': 9, 'momentum_length': 37, 'stop_loss_percent': 9.9, 'take_profit_percent': 9.0, 'alternate_signal': True}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 10000
    source_reproduce_stops = True
    source_risk_flags = ['broker_state', 'tuple', 'exit_order', 'var_state']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
