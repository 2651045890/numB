"""batch_011 port of 趋势跟踪止损反转策略-Parabolic-SAR-Trend-Tracking-Stop-Loss-Reversal-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2024-01-24 00:00:00\nend: 2024-01-31 00:00:00\nperiod: 30m\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=4\nstrategy("Parabolic SAR Strategy", overlay=true)\nstart = input(0.02)\nincrement = input(0.02)\nmaximum = input(0.2)\nvar bool uptrend = na\nvar float EP = na\nvar float SAR = na\nvar float AF = start\nvar float nextBarSAR = na\nif bar_index > 0\n\tfirstTrendBar = false\n\tSAR := nextBarSAR\n\tif bar_index == 1\n\t\tfloat prevSAR = na\n\t\tfloat prevEP = na\n\t\tlowPrev = low[1]\n\t\thighPrev = high[1]\n\t\tcloseCur = close\n\t\tclosePrev = close[1]\n\t\tif closeCur > closePrev\n\t\t\tuptrend := true\n\t\t\tEP := high\n\t\t\tprevSAR := lowPrev\n\t\t\tprevEP := high\n\t\telse\n\t\t\tuptrend := false\n\t\t\tEP := low\n\t\t\tprevSAR := highPrev\n\t\t\tprevEP := low\n\t\tfirstTrendBar := true\n\t\tSAR := prevSAR + start * (prevEP - prevSAR)\n\tif uptrend\n\t\tif SAR > low\n\t\t\tfirstTrendBar := true\n\t\t\tuptrend := false\n\t\t\tSAR := max(EP, high)\n\t\t\tEP := low\n\t\t\tAF := start\n\telse\n\t\tif SAR < high\n\t\t\tfirstTrendBar := true\n\t\t\tuptrend := true\n\t\t\tSAR := min(EP, low)\n\t\t\tEP := high\n\t\t\tAF := start\n\tif not firstTrendBar\n\t\tif uptrend\n\t\t\tif high > EP\n\t\t\t\tEP := high\n\t\t\t\tAF := min(AF + increment, maximum)\n\t\telse\n\t\t\tif low < EP\n\t\t\t\tEP := low\n\t\t\t\tAF := min(AF + increment, maximum)\n\tif uptrend\n\t\tSAR := min(SAR, low[1])\n\t\tif bar_index > 1\n\t\t\tSAR := min(SAR, low[2])\n\telse\n\t\tSAR := max(SAR, high[1])\n\t\tif bar_index > 1\n\t\t\tSAR := max(SAR, high[2])\n\tnextBarSAR := SAR + AF * (EP - SAR)\n\tif barstate.isconfirmed\n\t\tif uptrend\n\t\t\tstrategy.entry("ParSE", strategy.short, stop=nextBarSAR, comment="ParSE")\n\t\t\tstrategy.cancel("ParLE")\n\t\telse\n\t\t\tstrategy.entry("ParLE", strategy.long, stop=nextBarSAR, comment="ParLE")\n\t\t\tstrategy.cancel("ParSE")\nplot(SAR, style=plot.style_cross, linewidth=3, color=color.orange)\nplot(nextBarSAR, style=plot.style_cross, linewidth=3, color=color.aqua)\n//Stop Loss Inputs\nuse_short_stop_loss = input(false, title="Short Stop Loss", group="Stop Loss and Take Profit", inline="Short_SL")\nshort_stop_loss = input(title="(%)", type=input.float, minval=0.0, step=0.1, \n     defval=5, group="Stop Loss and Take Profit", inline="Short_SL") * 0.01\nuse_long_stop_loss = input(false, title="Long Stop Loss", group="Stop Loss and Take Profit", inline="Long_SL")\nlong_stop_loss = input(title="(%)", type=input.float, minval=0.0, step=0.1, \n     defval=5, group="Stop Loss and Take Profit", inline="Long_SL") * 0.01\n\n//Take Profit Inputs     \nuse_short_take_profit = input(false, title="Short Take Profit", group="Stop Loss and Take Profit", inline="Short_TP")\nshort_take_profit = input(title="(%)", type=input.float, minval=0.0, step=0.1,\n     defval = 20, group="Stop Loss and Take Profit", inline="Short_TP") * .01\nuse_long_take_profit = input(false, title="Long Take Profit", group="Stop Loss and Take Profit", inline="Long_TP")\nlong_take_profit = input(title="(%)", type=input.float, minval=0.0, step=0.1,\n     defval = 20, group="Stop Loss and Take Profit", inline="Long_TP") * .01\n\n\nlongStopPrice  = strategy.position_avg_price * (1 - long_stop_loss)\nshortStopPrice = strategy.position_avg_price * (1 + short_stop_loss)\nlongLimitPrice = strategy.position_avg_price * (1 + long_take_profit)\nshortLimitPrice = strategy.position_avg_price * (1 - short_take_profit)\n\n\nif (strategy.position_size > 0.0)\n    if (use_long_stop_loss and not use_long_take_profit)\n        strategy.exit("Long", stop = longStopPrice)\n    if (use_long_take_profit and not use_long_stop_loss)\n        strategy.exit("Long", limit = longLimitPrice)\n    if (use_long_take_profit and use_long_stop_loss)\n        strategy.exit("Long", stop = longStopPrice, limit=longLimitPrice)\nif (strategy.position_size < 0.0)\n    if (use_short_stop_loss and not use_short_take_profit)\n        strategy.exit("Short", stop = shortStopPrice)\n    if (use_short_take_profit and not use_short_stop_loss)\n        strategy.exit("Short", limit = shortLimitPrice)\n    if (use_short_take_profit and use_short_stop_loss)\n        strategy.exit("Short", stop = shortStopPrice, limit = shortLimitPrice)\n\n//plot(strategy.equity, title="equity", color=color.red, linewidth=2, style=plot.style_areabr)'

class SM84833E90737A5484(PinePortBase, IStrategy):
    source_id = "SM_84833e90737a5484"
    source_file = '趋势跟踪止损反转策略-Parabolic-SAR-Trend-Tracking-Stop-Loss-Reversal-Strategy.md'
    timeframe = '30m'
    can_short = True
    source_defaults = {'start': 0.02, 'increment': 0.02, 'maximum': 0.2, 'use_short_stop_loss': False, 'short_stop_loss': 5, 'use_long_stop_loss': False, 'long_stop_loss': 5, 'use_short_take_profit': False, 'short_take_profit': 20, 'use_long_take_profit': False, 'long_take_profit': 20}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = True
    source_risk_flags = ['broker_state', 'entry_price_order', 'exit_order', 'var_state']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
