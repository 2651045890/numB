"""batch_011 port of 超趋势增强枢轴反转策略SuperTrend-Enhanced-Pivot-Reversal-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2022-10-18 00:00:00\nend: 2023-10-24 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This source code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © PresentTrading\n\n//@version=5\nstrategy("SuperTrend Enhanced Pivot Reversal - Strategy [PresentTrading]", overlay=true, precision=3, default_qty_type=strategy.cash, \n commission_value= 0.1, commission_type=strategy.commission.percent, slippage= 1, \n  currency=currency.USD, default_qty_type = strategy.percent_of_equity, default_qty_value = 10, initial_capital= 10000)\n\n// Pivot Reversal parameters\nleftBars = input(6)\nrightBars = input(3)\nswh = ta.pivothigh(leftBars, rightBars)\nswl = ta.pivotlow(leftBars, rightBars)\n\n// SuperTrend parameters\natrPeriod = input(5, "ATR Length")\nfactor = input.float(2.618, "Factor", step = 0.01)\n\n[superTrend, direction] = ta.supertrend(factor, atrPeriod)\n\n// Plot the SuperTrend\nplot(superTrend, title="SuperTrend", color=color.blue)\n\n\n// Trade Direction parameter\ntradeDirection = input.string(title="Trade Direction", defval="Both", options=["Long", "Short", "Both"])\n\n// Stop Loss Level (in %)\nstopLossLevel = input(20, title="Stop Loss Level (%)")\n\n// Convert the stop loss level to a price difference\nstopLossPrice = stopLossLevel / 100\n\n\n// Long entry\nswh_cond = not na(swh)\nhprice = 0.0\nhprice := swh_cond ? swh : hprice[1]\nle = false\nle := swh_cond ? true : (le[1] and high > hprice ? false : le[1])\nif (le and direction > 0 and (tradeDirection == "Long" or tradeDirection == "Both"))\n    strategy.entry("PivRevLE", strategy.long, comment="PivRevLE", stop=hprice + syminfo.mintick)\n    strategy.exit("Exit Long", "PivRevLE", stop = hprice * (1 - stopLossPrice))\n\n// Short entry\nswl_cond = not na(swl)\nlprice = 0.0\nlprice := swl_cond ? swl : lprice[1]\nse = false\nse := swl_cond ? true : (se[1] and low < lprice ? false : se[1])\nif (se and direction < 0 and (tradeDirection == "Short" or tradeDirection == "Both"))\n    strategy.entry("PivRevSE", strategy.short, comment="PivRevSE", stop=lprice - syminfo.mintick)\n    strategy.exit("Exit Short", "PivRevSE", stop = lprice * (1 + stopLossPrice))\n\n\n// Closing positions when the tradeDirection is one-sided or when SuperTrend direction changes\nif ((tradeDirection == "Long" and se and direction < 0) or (tradeDirection == "Long" and direction < 0))\n    strategy.close("PivRevLE")\nif ((tradeDirection == "Short" and le and direction > 0) or (tradeDirection == "Short" and direction > 0))\n    strategy.close("PivRevSE")\n\n// Plot pivot highs and lows\nplotshape(swh_cond, title="Pivot Highs", location=location.belowbar, color=color.green, style=shape.triangleup)\nplotshape(swl_cond, title="Pivot Lows", location=location.abovebar, color=color.red, style=shape.triangledown)\n\n// Closing positions when the tradeDirection is one-sided\nif (tradeDirection == "Long" and se and direction < 0)\n    strategy.close("PivRevLE")\nif (tradeDirection == "Short" and le and direction > 0)\n    strategy.close("PivRevSE")\n\n'

class SMB4EE12994B04E851(PinePortBase, IStrategy):
    source_id = "SM_b4ee12994b04e851"
    source_file = '超趋势增强枢轴反转策略SuperTrend-Enhanced-Pivot-Reversal-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'leftBars': 6, 'rightBars': 3, 'atrPeriod': 5, 'factor': 2.618, 'tradeDirection': 'Both', 'stopLossLevel': 20}
    source_qty_type = 'cash'
    source_qty_value = 10
    source_commission_percent = 0.1
    source_pyramiding = 0
    source_initial_capital = 10000
    source_reproduce_stops = True
    source_risk_flags = ['tuple', 'entry_price_order', 'exit_order', 'var_state']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
