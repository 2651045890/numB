"""batch_011 port of 突破通道趋势追踪策略Trend-Tracking-Strategy-Based-on-Channel-Breakouts.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-11-15 00:00:00\nend: 2023-11-22 00:00:00\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=3\n\n\ninitial_capital = 1000,\ndefault_qty_value = 90,\ndefault_qty_type = strategy.percent_of_equity,\npyramiding = 0,\ncommission_value = 0.002,\ncommission_type = strategy.commission.percent,\ncalc_on_every_tick = true\nlength_val = 2\nmax_bars_back = 1440\nrisk_max_drawdown = 9\n\n\nstrategy("Channel Break",max_bars_back=max_bars_back,initial_capital = initial_capital,default_qty_value = default_qty_value,default_qty_type = default_qty_type,pyramiding = pyramiding,commission_value = commission_value,commission_type = commission_type,calc_on_every_tick = calc_on_every_tick)\n// strategy.risk.max_drawdown(risk_max_drawdown, strategy.percent_of_equity) \n\nlength = input(title="Length",  minval=1, maxval=1000, defval=length_val)\n\nupBound = highest(high, length)\ndownBound = lowest(low, length)\n\n//plot (upBound)\n//plot (downBound)\n//plot (close, color=red)\n//plot (ema(close,length * 2), color=green)\n//\nif (not na(close[length]) and time>timestamp(2018, 02, 24, 0, 00) )\n    strategy.entry("Buy", strategy.long, stop=upBound + syminfo.mintick, comment="Buy")\n    strategy.entry("Short", strategy.short, stop=downBound - syminfo.mintick, comment="Short")\n    \nposition = strategy.position_size\n    \n    \n//plot(position , title="equity", color=red,style=cross,linewidth=4)\nplot(variance(position,2)>0?1:0,style=circles,linewidth=4)\n\nmessage = ""\n\nif (position > 0) \n    message = "BTCUSD L: " + tostring(strategy.position_size)\n    na(position)\n    \nif (position < 0) \n    message = "BTCUSD S: " + tostring(strategy.position_size)\n    na(position)\n\nalertcondition(variance(strategy.position_size,2) > 0, "test", message )'

class SM79832862D5D03B90(PinePortBase, IStrategy):
    source_id = "SM_79832862d5d03b90"
    source_file = '突破通道趋势追踪策略Trend-Tracking-Strategy-Based-on-Channel-Breakouts.md'
    timeframe = '1h'
    can_short = True
    source_defaults = {}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
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
