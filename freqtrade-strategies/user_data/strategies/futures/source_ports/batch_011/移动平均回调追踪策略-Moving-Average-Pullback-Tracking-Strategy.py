"""batch_011 port of 移动平均回调追踪策略-Moving-Average-Pullback-Tracking-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-03-22 00:00:00\nend: 2024-03-27 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This Pine Script™ code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © contapessoal_ivan\n// @version=5\nstrategy("Pullback Strategy", \n     overlay=true, \n     initial_capital=1000,\n     default_qty_type=strategy.percent_of_equity, \n     default_qty_value=100, // 100% of balance invested on each trade\n     commission_type=strategy.commission.cash_per_contract, \n     commission_value=0.005) // Interactive Brokers rate\n\n// Get user input\ni_ma1           = input.int(title="MA 1 Length", defval=200, step=10, group="Strategy Parameters", tooltip="Long-term MA")\ni_ma2           = input.int(title="MA 2 Length", defval=10, step=10, group="Strategy Parameters", tooltip="Short-term MA")\ni_stopPercent   = input.float(title="Stop Loss Percent", defval=0.10, step=0.1, group="Strategy Parameters", tooltip="Failsafe Stop Loss Percent Decline")\ni_lowerClose    = input.bool(title="Exit On Lower Close", defval=false, group="Strategy Parameters", tooltip="Wait for a lower-close before exiting above MA2")\ni_startTime     = input(title="Start Filter", defval=timestamp("26 Jan 2023 00:00 +0000"), group="Time Filter", tooltip="Start date & time to begin searching for setups")\ni_endTime       = input(title="End Filter", defval=timestamp("26 Mar 2024 23:59 +0000"), group="Time Filter", tooltip="End date & time to stop searching for setups")\n\n// Get indicator values\nma1 = ta.sma(close, i_ma1)\nma2 = ta.sma(close, i_ma2)\n\n// Check filter(s)\nf_dateFilter = true\n\n// Check buy/sell conditions\nvar float buyPrice = 0\nbuyCondition    = close > ma1 and close < ma2 and strategy.position_size == 0 and f_dateFilter\nsellCondition   = close > ma2 and strategy.position_size > 0 and (not i_lowerClose or close < low[1])\nstopDistance    = strategy.position_size > 0 ? ((buyPrice - close) / close) : na\nstopPrice       = strategy.position_size > 0 ? buyPrice - (buyPrice * i_stopPercent) : na\nstopCondition   = strategy.position_size > 0 and stopDistance > i_stopPercent\n\n// Enter positions\nif buyCondition\n    strategy.entry(id="Long", direction=strategy.long)\n\nif buyCondition[1]\n    buyPrice := open\n\n// Exit positions\nif sellCondition or stopCondition\n    strategy.close(id="Long", comment="Exit" + (stopCondition ? "SL=true" : ""))\n    buyPrice := na\n\n// Draw pretty colors\nplot(buyPrice, color=color.lime, style=plot.style_linebr)\nplot(stopPrice, color=color.red, style=plot.style_linebr, offset=-1)\nplot(ma1, color=color.blue)\nplot(ma2, color=color.orange)\n'

class SM8374C7CDDEF59AFE(PinePortBase, IStrategy):
    source_id = "SM_8374c7cddef59afe"
    source_file = '移动平均回调追踪策略-Moving-Average-Pullback-Tracking-Strategy.md'
    timeframe = '1d'
    can_short = False
    source_defaults = {'i_ma1': 200, 'i_ma2': 10, 'i_stopPercent': 0.1, 'i_lowerClose': False}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 100
    source_commission_percent = 0.005
    source_pyramiding = 0
    source_initial_capital = 1000
    source_reproduce_stops = False
    source_risk_flags = ['broker_state', 'var_state']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
