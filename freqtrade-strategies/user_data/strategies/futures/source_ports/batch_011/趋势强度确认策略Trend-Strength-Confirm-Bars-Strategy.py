"""batch_011 port of 趋势强度确认策略Trend-Strength-Confirm-Bars-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-12-01 00:00:00\nend: 2023-12-31 23:59:59\nperiod: 2h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("Confirm Bars Strategy [TS Trader]", overlay=true)\n\nconfirmBars = input(1)\n\n// === INPUT BACKTEST RANGE ===\nfromYear = input.int(2019, title="Backtest Start Year")\nfromMonth = input.int(1, title="Backtest Start Month", minval=1, maxval=12)\nfromDay = input.int(1, title="Backtest Start Day", minval=1, maxval=31)\ntoYear = input.int(2023, title="Backtest End Year")\ntoMonth = input.int(12, title="Backtest End Month", minval=1, maxval=12)\ntoDay = input.int(31, title="Backtest End Day", minval=1, maxval=31)\n\nstartTimestamp = timestamp(fromYear, fromMonth, fromDay, 00, 00)\nendTimestamp = timestamp(toYear, toMonth, toDay, 23, 59)\n\ninBacktestRange = true\n\n// === STRATEGY LOGIC ===\nbcount = 0\nbcount := close[1] < close ? nz(bcount[1]) + 1 : 0\nif (bcount == confirmBars and inBacktestRange)\n    strategy.entry("Buy", strategy.long, comment="Long")\n\nscount = 0\nscount := close[1] > close ? nz(scount[1]) + 1 : 0\nif (scount == confirmBars and inBacktestRange)\n    strategy.entry("Sell", strategy.short, comment="Short")'

class SMA750A1E10C01EA08(PinePortBase, IStrategy):
    source_id = "SM_a750a1e10c01ea08"
    source_file = '趋势强度确认策略Trend-Strength-Confirm-Bars-Strategy.md'
    timeframe = '2h'
    can_short = True
    source_defaults = {'confirmBars': 1, 'fromYear': 2019, 'fromMonth': 1, 'fromDay': 1, 'toYear': 2023, 'toMonth': 12, 'toDay': 31}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = False
    source_risk_flags = ['var_state']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
