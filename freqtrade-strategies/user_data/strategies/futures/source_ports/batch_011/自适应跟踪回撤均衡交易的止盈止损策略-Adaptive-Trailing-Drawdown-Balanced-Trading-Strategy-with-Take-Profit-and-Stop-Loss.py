"""batch_011 port of 自适应跟踪回撤均衡交易的止盈止损策略-Adaptive-Trailing-Drawdown-Balanced-Trading-Strategy-with-Take-Profit-and-Stop-Loss.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2024-12-04 00:00:00\nend: 2024-12-11 00:00:00\nperiod: 10m\nbasePeriod: 10m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("Greedy Strategy - maclaurin", pyramiding = 100, calc_on_order_fills=false, overlay=true, default_qty_type = strategy.percent_of_equity, default_qty_value = 100)\nbacktestStartDate = input(timestamp("1 Jan 1990"),\n     title="Start Date", group="Backtest Time Period",\n     tooltip="This start date is in the time zone of the exchange " +\n     "where the chart\'s instrument trades. It doesn\'t use the time " +\n     "zone of the chart or of your computer.")\nbacktestEndDate = input(timestamp("1 Jan 2023"),\n     title="End Date", group="Backtest Time Period",\n     tooltip="This end date is in the time zone of the exchange " +\n     "where the chart\'s instrument trades. It doesn\'t use the time " +\n     "zone of the chart or of your computer.")\ninTradeWindow = true\ntp = input(10)\nsl = input(10)\nmaxidf = input(title="Max Intraday Filled Orders", defval=5)\n// strategy.risk.max_intraday_filled_orders(maxidf)\nupGap = open > high[1]\ndnGap = open < low[1]\ndn = strategy.position_size < 0 and open > close\nup = strategy.position_size > 0 and open < close\nif inTradeWindow and upGap\n    strategy.entry("GapUp", strategy.long, stop = high[1])\nelse\n    strategy.cancel("GapUp")\nif inTradeWindow and dn\n    strategy.entry("Dn", strategy.short, stop = close)\nelse\n    strategy.cancel("Dn")\nif inTradeWindow and dnGap\n    strategy.entry("GapDn", strategy.short, stop = low[1])\nelse\n    strategy.cancel("GapDn")\nif inTradeWindow and up\n    strategy.entry("Up", strategy.long, stop = close)\nelse\n    strategy.cancel("Up")\nXQty = strategy.position_size < 0 ? -strategy.position_size : strategy.position_size\ndir = strategy.position_size < 0 ? -1 : 1\nlmP = strategy.position_avg_price + dir*tp*syminfo.mintick\nslP = strategy.position_avg_price - dir*sl*syminfo.mintick\nfloat nav = na\nrevCond = strategy.position_size > 0 ? dnGap : (strategy.position_size < 0 ? upGap : false)\nif inTradeWindow and not revCond and XQty > 0\n    strategy.order("TP", strategy.position_size < 0 ? strategy.long : strategy.short, XQty, lmP, nav, "TPSL",  "TPSL")\n    strategy.order("SL", strategy.position_size < 0 ? strategy.long : strategy.short, XQty, nav, slP, "TPSL", "TPSL")\nif XQty == 0 or revCond\n    strategy.cancel("TP")\n    strategy.cancel("SL")\n//plot(strategy.equity, title="equity", color=color.red, linewidth=2, style=plot.style_areabr)\n'

class SMF2B9A0963723930E(PinePortBase, IStrategy):
    source_id = "SM_f2b9a0963723930e"
    source_file = '自适应跟踪回撤均衡交易的止盈止损策略-Adaptive-Trailing-Drawdown-Balanced-Trading-Strategy-with-Take-Profit-and-Stop-Loss.md'
    timeframe = '10m'
    can_short = True
    source_defaults = {'tp': 10, 'sl': 10, 'maxidf': 5}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 100
    source_commission_percent = 0
    source_pyramiding = 100
    source_initial_capital = 1000000
    source_reproduce_stops = False
    source_risk_flags = ['broker_state', 'entry_price_order']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
