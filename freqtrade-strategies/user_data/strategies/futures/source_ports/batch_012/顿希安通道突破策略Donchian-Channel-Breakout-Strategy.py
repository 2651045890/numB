"""batch_012 port of 顿希安通道突破策略Donchian-Channel-Breakout-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-09-11 00:00:00\nend: 2023-09-15 00:00:00\nperiod: 3m\nbasePeriod: 1m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=3\n//future strategy\n//strategy(title = "stub", default_qty_type = strategy.fixed, default_qty_value = 1,  overlay = true, commission_type=strategy.commission.cash_per_contract,commission_value=2)\n//stock strategy\nstrategy(title = "dc", default_qty_type = strategy.percent_of_equity, default_qty_value = 100,  overlay = true, commission_type=strategy.commission.cash_per_contract,commission_value=.005)\n//forex strategy\n//strategy(title = "stub", default_qty_type = strategy.percent_of_equity, default_qty_value = 100,  overlay = true)\n//crypto strategy\n//strategy(title = "stub", default_qty_type = strategy.percent_of_equity, default_qty_value = 100,  overlay = true, commission_type=strategy.commission.percent,commission_value=.25,default_qty_value=10000)\n\n\ntestStartYear = input(2000, "Backtest Start Year")\ntestStartMonth = input(1, "Backtest Start Month")\ntestStartDay = input(1, "Backtest Start Day")\ntestPeriodStart = timestamp(testStartYear,testStartMonth,testStartDay,0,0)\n\ntestEndYear = input(2018, "Backtest Start Year")\ntestEndMonth = input(12, "Backtest Start Month")\ntestEndDay = input(1, "Backtest Start Day")\ntestPeriodEnd = timestamp(testStartYear,testStartMonth,testStartDay,0,0)\n\n\ntestPeriod() =>\n    true\n    //time >= testPeriodStart  ? true : false\n\ndcPeriod = 20\n\ndcUpper = highest(close, dcPeriod)[1]\ndcLower = lowest(close, dcPeriod)[1]\ndcAverage = (dcUpper + dcLower) / 2\n\nplot(dcLower, style=line, linewidth=3, color=red, offset=1)\nplot(dcUpper, style=line, linewidth=3, color=aqua, offset=1)\n\nplot(dcAverage, color=yellow, style=line, linewidth=1, title="Mid-Line Average")\n\nstrategy.entry("simpleBuy", strategy.long, when=close >= dcUpper)\nstrategy.close("simpleBuy",when=close < dcAverage)\n    \n//strategy.entry("simpleSell", strategy.short,when=close <= dcLower)\n//strategy.close("simpleSell",when=close > dcAverage)\n    \n\n\n'

class SMDonchianChannelBreakoutStrategyfe202f(PinePortBase, IStrategy):
    source_id = "SM_fe202f2e9b0e3072"
    source_file = '顿希安通道突破策略Donchian-Channel-Breakout-Strategy.md'
    timeframe = '3m'
    can_short = True
    source_defaults = {'testStartYear': 2000, 'testStartMonth': 1, 'testStartDay': 1, 'testEndYear': 2018, 'testEndMonth': 12, 'testEndDay': 1}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 2
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_reproduce_stops = False
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_012 md and exposed through the same PinePortBase interface used by batch_001.', 'Custom Pine function(s) are present; the original source is embedded verbatim and this generic pass flags them for per-strategy semantic verification.']

    def pine_indicators(self, dataframe, params):
        # Runtime evaluates the source against the complete OHLCV frame.
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch012Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
