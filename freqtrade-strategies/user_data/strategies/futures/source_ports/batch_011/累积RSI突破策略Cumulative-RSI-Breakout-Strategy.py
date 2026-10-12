"""batch_011 port of 累积RSI突破策略Cumulative-RSI-Breakout-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-09-26 00:00:00\nend: 2023-10-26 00:00:00\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This source code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// @version=5\n// Author = TradeAutomation\n\n\nstrategy(title="Cumulative RSI Strategy", shorttitle="CRSI Strategy", process_orders_on_close=true, overlay=true, commission_type=strategy.commission.cash_per_contract, commission_value=.0035, slippage = 1, margin_long = 75, initial_capital = 25000, default_qty_type=strategy.percent_of_equity, default_qty_value=110)\n\n\n// Cumulative RSI Indicator Calculations //\nrlen  = input.int(title="RSI Length", defval=3, minval=1)\ncumlen = input(3, "RSI Cumulation Length")\nrsi = ta.rsi(close, rlen)\ncumRSI = math.sum(rsi, cumlen)\nob = (100*cumlen*input(94, "Oversold Level")*.01)\nos = (100*cumlen*input(20, "Overbought Level")*.01)\n\n\n// Operational Function //\nTrendFilterInput = input(false, "Only Trade When Price is Above EMA?")\nema = ta.ema(close, input(100, "EMA Length"))\nTrendisLong = (close>ema)\nplot(ema)\n\n\n// Backtest Timeframe Inputs // \nstartDate = input.int(title="Start Date", defval=1, minval=1, maxval=31)\nstartMonth = input.int(title="Start Month", defval=1, minval=1, maxval=12)\nstartYear = input.int(title="Start Year", defval=2010, minval=1950, maxval=2100)\nendDate = input.int(title="End Date", defval=1, minval=1, maxval=31)\nendMonth = input.int(title="End Month", defval=1, minval=1, maxval=12)\nendYear = input.int(title="End Year", defval=2099, minval=1950, maxval=2100)\nInDateRange = (time >= timestamp(syminfo.timezone, startYear, startMonth, startDate, 0, 0)) and (time < timestamp(syminfo.timezone, endYear, endMonth, endDate, 0, 0))\n\n\n// Buy and Sell Functions //\nif (InDateRange and TrendFilterInput==true)\n    strategy.entry("Long", strategy.long, when = ta.crossover(cumRSI, os) and TrendisLong, comment="Buy", alert_message="buy")\n    strategy.close("Long", when = ta.crossover(cumRSI, ob) , comment="Sell", alert_message="Sell")\nif (InDateRange and TrendFilterInput==false)\n    strategy.entry("Long", strategy.long, when = ta.crossover(cumRSI, os), comment="Buy", alert_message="buy")\n    strategy.close("Long", when = ta.crossover(cumRSI, ob), comment="Sell", alert_message="sell")\nif (not InDateRange)\n    strategy.close_all()'

class SME0DE8746FE092542(PinePortBase, IStrategy):
    source_id = "SM_e0de8746fe092542"
    source_file = '累积RSI突破策略Cumulative-RSI-Breakout-Strategy.md'
    timeframe = '1h'
    can_short = False
    source_defaults = {'rlen': 3, 'cumlen': 3, 'TrendFilterInput': False, 'startDate': 1, 'startMonth': 1, 'startYear': 2010, 'endDate': 1, 'endMonth': 1, 'endYear': 2099}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 110
    source_commission_percent = 0.0035
    source_pyramiding = 0
    source_initial_capital = 25000
    source_reproduce_stops = False
    source_risk_flags = ['common_subset']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
