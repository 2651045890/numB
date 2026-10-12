"""batch_011 port of 趋势跟踪型EMA双线限价买入策略-Dual-EMA-Trend-Following-Strategy-with-Limit-Buy-Entry.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2019-12-23 08:00:00\nend: 2024-12-09 08:00:00\nperiod: 1d\nbasePeriod: 1d\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("Limit Buy at EMA20 (Last 30 Days)", overlay=true)\n\n// Inputs for EMAs\nema20Length = input.int(30, title="EMA 20 Length")\nema300Length = input.int(300, title="EMA 300 Length")\ntpPercentage = input.float(10.0, title="Take Profit (%)", step=0.1) / 100\nslPercentage = input.float(5.0, title="Stop Loss (%)", step=0.1) / 100  // Stop loss at 15%\n\n// Calculate EMAs\nema20 = ta.ema(close, ema20Length)\nema300 = ta.ema(close, ema300Length)\n\n// Plot EMAs\nplot(ema20, color=color.blue, title="EMA 20")\nplot(ema300, color=color.red, title="EMA 300")\n\n// Limit backtesting to the last 30 days\nstartTime = timestamp(year(timenow), month(timenow), dayofmonth(timenow) - 30, 0, 0)\nif (time < startTime)\n    strategy.close_all()\n    strategy.cancel_all()\n\n// Entry Condition: Price above EMA300\nlongCondition = close > ema300 and time >= startTime\n\n// Calculate position size (10% of equity)\npositionSize = strategy.equity * 0.10 / ema20  // Use EMA20 as the limit price\n\n// Place a limit buy order at EMA20\nif (longCondition)\n    strategy.order("Limit Buy", strategy.long, qty=positionSize, limit=ema20)\n\n// Calculate TP and SL levels\ntpPrice = ema20 * (1 + tpPercentage)\nslPrice = ema20 * (1 - slPercentage)\n\n// Set take profit and stop loss\nif (strategy.position_size > 0)\n    strategy.exit("Take Profit/Stop Loss", "Limit Buy", stop=slPrice, limit=tpPrice)\n'

class SM6069F221BA0C682D(PinePortBase, IStrategy):
    source_id = "SM_6069f221ba0c682d"
    source_file = '趋势跟踪型EMA双线限价买入策略-Dual-EMA-Trend-Following-Strategy-with-Limit-Buy-Entry.md'
    timeframe = '1d'
    can_short = False
    source_defaults = {'ema20Length': 30, 'ema300Length': 300, 'tpPercentage': 10.0, 'slPercentage': 5.0}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = True
    source_risk_flags = ['broker_state', 'entry_price_order', 'exit_order']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
