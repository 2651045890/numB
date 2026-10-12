"""batch_011 port of 趋势跟踪均线交叉策略Trend-Following-Moving-Average-Crossover-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-10-24 00:00:00\nend: 2023-10-31 00:00:00\nperiod: 15m\nbasePeriod: 5m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This source code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © pernath\n\n//@version=5\nstrategy("TREND_CATCHER", overlay=true, commission_value=0.05, commission_type=strategy.commission.percent, initial_capital=1000)\n\n//#####variables##############\nprofit_short=input(title=\'profit_short\', defval=27)\nstop_short=input(title=\'stop_short\', defval=2)\n\nstop_long=input(title=\'stop_long\', defval=3)\nprofit_long=input(title=\'profit_long\', defval=35)\n\n\nmedia_1=input(title=\'media_1\', defval=55)\nmedia_2=input(title=\'media_2\', defval=100)\nresta_medias=input(title=\'resta_medias\', defval=0)\nresta_medias2=input(title=\'resta_medias2\', defval=0)\n\nRSI_periodos=input(title=\'RSI_periodos\', defval=42)\n//###############VARIABLES###################\n\n\n\n\n//#####Alert#####\nid_bot = ""\nemail_token = ""\nlong_open =""\nlong_close =""\nshort_open =""\nshort_close =""\n//#  {{strategy.order.alert_message}}\n\n\n//#############################\n//#############################\n\n//###############EMA##############/\n//plot(ta.ema(close, 1), title=\'ema 5\', color=color.white)\nplot(ta.ema(close, 12), title=\'ema 12\', color=color.white)\nplot(ta.ema(close, 25), title=\'ema 25\', color=color.white)\nplot(ta.ema(close, 30), title=\'ema 30\', color=color.white, linewidth=1)\nplot(ta.ema(close, 40), title=\'ema 40\', color=color.white, linewidth=1)\nplot(ta.ema(close, 55), title=\'ema 55\', color=color.orange, linewidth=1)\nplot(ta.ema(close, 100), title=\'ema 100\', color=color.red, linewidth=1)\nplot(ta.ema(close, 200), title=\'ema 200\', color=color.white, linewidth=3)\n\n//#############################/\n\n\n\n\n\n//######VISUAL#############\nEMA50 = ta.ema(close, 55)\nEMA100 = ta.ema(close, 100)\n\n\nestado_medias=EMA50-EMA100\n\n\n\n\na = plot(EMA50, title="EMA(50)", color=color.orange, linewidth=1 ) \nb = plot(EMA100, title="EMA(100)", color=color.red, linewidth=1 )\n\n\nvar color col = na\ncol := estado_medias>resta_medias ? color.green : color.red\nfill(a,b,color=col,transp=40)\n\n\n//######VISUAL#############\n\n\n\n\n\nGo_Short=(ta.crossunder(ta.ema(close,100),ta.ema(close,200)))\nGo_Long=((ta.crossover(ta.ema(close,55),ta.ema(close,100))and(ta.ema(close,12)>ta.ema(close,200))))\n\n\nstrategy.close("enter long", (Go_Short),alert_message=long_open)\n\ncancelar_short=((ta.crossunder(ta.ema(close,25),ta.ema(close,6))))\n\n\n\nif Go_Short\n    strategy.entry("enter short", strategy.short,1, alert_message=short_open) \n  \nstrategy.exit("cerrar short", "enter short", 1, profit=close*profit_short/100/syminfo.mintick, loss=close*stop_short/100/syminfo.mintick, alert_message=short_close)\n\n\n\n\nstrategy.close("enter short", (Go_Long),alert_message=short_close)\ncancelar=((ta.crossunder(ta.ema(close,12),ta.ema(close,30))))\n\n\n\nif Go_Long\n    strategy.entry("enter long", strategy.long,1,alert_message=long_open)\n\nstrategy.exit("cerrar long", "enter long", 1, profit=close*profit_long/100/syminfo.mintick, loss=close*stop_long/100/syminfo.mintick, alert_message=long_close)\n\n\n\n\nstrategy.close("enter short", (cancelar_short),alert_message=short_close)\n\nstrategy.close("enter long", (cancelar),alert_message=long_close)\n\n\n//posiciones abiertas\nbgcolor((strategy.position_size > 0 or strategy.position_size < 0) ? color.blue : na, transp=70)\n\n\n\n\n\n\n\n'

class SM63CC5D4A9A73E6CA(PinePortBase, IStrategy):
    source_id = "SM_63cc5d4a9a73e6ca"
    source_file = '趋势跟踪均线交叉策略Trend-Following-Moving-Average-Crossover-Strategy.md'
    timeframe = '15m'
    can_short = True
    source_defaults = {'profit_short': 27, 'stop_short': 2, 'stop_long': 3, 'profit_long': 35, 'media_1': 55, 'media_2': 100, 'resta_medias': 0, 'resta_medias2': 0, 'RSI_periodos': 42}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0.05
    source_pyramiding = 0
    source_initial_capital = 1000
    source_reproduce_stops = True
    source_risk_flags = ['broker_state', 'exit_order', 'var_state']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
