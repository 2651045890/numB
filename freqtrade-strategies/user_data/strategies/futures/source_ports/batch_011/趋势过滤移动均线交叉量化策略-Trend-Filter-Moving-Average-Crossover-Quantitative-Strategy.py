"""batch_011 port of 趋势过滤移动均线交叉量化策略-Trend-Filter-Moving-Average-Crossover-Quantitative-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-11-23 00:00:00\nend: 2023-11-30 00:00:00\nperiod: 1m\nbasePeriod: 1m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n////////////////////////////////////////////////////////////////////////////////\n// Booz Strategy\n// Developed for Godstime\n// Version 1.1\n// 11/28/2021\n////////////////////////////////////////////////////////////////////////////////\n\n//@version=4\nstrategy("Booz Strategy", "", true)\n\n// ----------------------------- Inputs ------------------------------------- //\nsource_ma_type = input("EMA", "Source MA Type", options=["SMA", "EMA"])\nsource_ma_length = input(50, "Source MA Length")\nfast_ma_length = input(20, "Fast MA Length")\nslow_ma_length = input(50, "Slow MA Length")        \nuse_trend_filter = input(true, "Trend Filter")\ntrend_filter_ma_type = input("EMA", "Trend Filter MA Type", options=["SMA", "EMA"])\ntrend_filter_ma_length = input(200, "Trend Filter MA Period")\nshow_mas = input(true, "Show MAs")\nswing_trading_mode = input(false, "Swing Trading")\n\n// -------------------------- Calculations ---------------------------------- //\nfast_ma = ema(close, fast_ma_length)\nslow_ma = ema(close, slow_ma_length)\nsource_ma = source_ma_type == "EMA"? ema(close, source_ma_length): \n                                     sma(close, source_ma_length)\ntrend_filter_ma = trend_filter_ma_type == "EMA"? ema(close, trend_filter_ma_length): \n                                                 sma(close, trend_filter_ma_length)\n\n// --------------------------- Conditions ----------------------------------- //\nuptrend = not use_trend_filter or close > trend_filter_ma\nbuy_cond = crossover(fast_ma, slow_ma) and uptrend\n\ndowntrend = not use_trend_filter or close < trend_filter_ma\nsell_cond = crossunder(fast_ma, slow_ma) and downtrend\n\n// ---------------------------- Plotting ------------------------------------ //\nbgcolor(use_trend_filter and downtrend? color.red: use_trend_filter? color.green: na)\nplot(show_mas? fast_ma: na, "Fast MA", color.green)\nplot(show_mas? slow_ma: na, "Slow MA", color.red)\nplot(show_mas? source_ma: na, "Source MA", color.purple)\nplot(show_mas? trend_filter_ma: na, "Trend Filter MA", color.blue)\n\n\n// ---------------------------- Trading  ------------------------------------ //\n// Inputs\nsl_perc = input(1.0, "Stop Loss (in %)", group="Backtest Control")/100\ntp_perc = input(1.0, "Take Profit (in %)", group="Backtest Control")/100\nleverage = input(10, "Leverage", maxval=100, group="Backtest Control")\nbt_start_time = input(timestamp("2021 01 01"), "Backtest Start Time", input.time, group="Backtest Control")\nbt_end_time = input(timestamp("2021 12 31"), "Backtest End Time", input.time, group="Backtest Control")\n\n// Trading Window\nin_trading_window = true\ntrade_qty = 1\n\n// Long Side\nstrategy.entry("Long Entry", strategy.long, trade_qty, when=buy_cond and in_trading_window)\nlong_tp = strategy.position_avg_price * (1 + tp_perc)\nlong_sl = strategy.position_avg_price * (1 - sl_perc)\nif not swing_trading_mode\n    strategy.exit("Long Exit", "Long Entry", limit=long_tp, stop=long_sl)\n\n// Short Side\nstrategy.entry("Short Entry", strategy.short, trade_qty, when=sell_cond and in_trading_window)\nshort_tp = strategy.position_avg_price * (1 - tp_perc)\nshort_sl = strategy.position_avg_price * (1 + sl_perc)\nif not swing_trading_mode\n    strategy.exit("Short Exit", "Short Entry", limit=short_tp, stop=short_sl)\n\n// End of trading window close\nstrategy.close_all(when=not in_trading_window)'

class SM8767B91826387AA9(PinePortBase, IStrategy):
    source_id = "SM_8767b91826387aa9"
    source_file = '趋势过滤移动均线交叉量化策略-Trend-Filter-Moving-Average-Crossover-Quantitative-Strategy.md'
    timeframe = '1m'
    can_short = True
    source_defaults = {'source_ma_type': 'EMA', 'source_ma_length': 50, 'fast_ma_length': 20, 'slow_ma_length': 50, 'use_trend_filter': True, 'trend_filter_ma_type': 'EMA', 'trend_filter_ma_length': 200, 'show_mas': True, 'swing_trading_mode': False, 'sl_perc': 1.0, 'tp_perc': 1.0, 'leverage': 10}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
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
