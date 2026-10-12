"""batch_012 port of 追踪趋势获利策略Take-Profit-on-Trend-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-08-26 00:00:00\nend: 2023-09-25 00:00:00\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This source code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © BHD_Trade_Bot\n\n// @version=5\nstrategy(\n shorttitle            = \'Take Profit On Trend\',\n title                 = \'Take Profit On Trend (by BHD_Trade_Bot)\',\n overlay               = true,\n calc_on_every_tick    = true,\n calc_on_order_fills   = true,\n use_bar_magnifier     = true,\n initial_capital       = 1000,\n default_qty_type      = strategy.percent_of_equity,\n default_qty_value     = 100,\n commission_type       = strategy.commission.percent,\n commission_value      = 0.1)\n\n\n\n// Backtest Time Period\nstart_year   = input(title=\'Start year\'   ,defval=2021)\nstart_month  = input(title=\'Start month\'  ,defval=1)\nstart_day    = input(title=\'Start day\'    ,defval=1)\nstart_time = timestamp(start_year, start_month, start_day, 00, 00)\n\nend_year     = input(title=\'end year\'     ,defval=2050)\nend_month    = input(title=\'end month\'    ,defval=1)\nend_day      = input(title=\'end day\'      ,defval=1)\nend_time = timestamp(end_year, end_month, end_day, 23, 59)\n\nis_back_test_time() => true\n\n\n\n// EMA\nema50 = ta.ema(close, 50)\nema200 = ta.ema(close, 200)\n\n// RSI\nrsi200 = ta.rsi(close, 200)\n\n// EMA_CD\nemacd = ema50 - ema200\nemacd_signal = ta.ema(emacd, 50)\nhist = emacd - emacd_signal\n\n// BHD Unit\nbhd_unit = ta.rma(high - low, 200) * 2\nbhd_upper = ema200 + bhd_unit\nbhd_lower = ema200 - bhd_unit\n\n\n\n// All n candles is going down\nall_body_decrease(n) =>\n    isValid = true\n    for i = 0 to (n - 1)\n        if (close[i] > close[i + 1])\n            isValid := false\n            break\n    isValid\n\n\n\n// ENTRY CONDITIONS\n\n// Long-term uptrend\nentry_condition1 = rsi200 > 51 and hist > 0\n\n// Short-term downtrend\nentry_condition2 = all_body_decrease(2)\n\nENTRY_CONDITIONS = entry_condition1 and entry_condition2\n\nif ENTRY_CONDITIONS and is_back_test_time()\n    strategy.entry(\'entry\', strategy.long)\n\n\n// CLOSE CONDITIONS\n\n// Price increase 2 BHD unit\ntake_profit = close > strategy.position_avg_price + bhd_unit * 2\n\n// Price decrease 3 BHD unit\nstop_loss = close < strategy.position_avg_price - bhd_unit * 3\n\nCLOSE_CONDITIONS = take_profit or stop_loss\n\nif CLOSE_CONDITIONS\n    strategy.close(\'entry\')\n\n\n\n// Draw\nplot(ema50, color=color.orange, linewidth=2)\nplot(ema200, color=color.purple, linewidth=2)\nbhd_upper_line = plot(bhd_upper, color=color.teal)\nbhd_lower_line = plot(bhd_lower, color=color.teal)\nfill(bhd_upper_line, bhd_lower_line, color=color.new(color.teal, 90))\n\n'

class SMTakeProfitonTrendStrategyf6b52a(PinePortBase, IStrategy):
    source_id = "SM_f6b52a6a02748cb4"
    source_file = '追踪趋势获利策略Take-Profit-on-Trend-Strategy.md'
    timeframe = '1h'
    can_short = False
    source_defaults = {'start_year': 2021, 'start_month': 1, 'start_day': 1, 'end_year': 2050, 'end_month': 1, 'end_day': 1}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_reproduce_stops = False
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_012 md and exposed through the same PinePortBase interface used by batch_001.', 'Custom Pine function(s) are present; the original source is embedded verbatim and this generic pass flags them for per-strategy semantic verification.', 'Loop/switch logic is present and requires per-strategy semantic verification against TradingView/FMZ before treating results as parity-certified.', 'The source reads live strategy position state; batch_001-style broker-state parity must be checked manually for this file.']

    def pine_indicators(self, dataframe, params):
        # Runtime evaluates the source against the complete OHLCV frame.
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch012Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
