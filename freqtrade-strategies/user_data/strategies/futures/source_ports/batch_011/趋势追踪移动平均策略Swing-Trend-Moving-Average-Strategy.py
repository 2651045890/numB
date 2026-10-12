"""batch_011 port of 趋势追踪移动平均策略Swing-Trend-Moving-Average-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-01-28 00:00:00\nend: 2024-02-03 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This source code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © Inkedlau\n\n//@version=5\nstrategy(\'Swing Trend Strategy\', overlay=true, pyramiding=1, default_qty_type=strategy.percent_of_equity, default_qty_value=100, initial_capital=1000, commission_value=0.1)\n\nuse_short = input.bool(false, \'Open Short Positions?\')\nexit_type = input.bool(true, \'Exit trade on Moving Average Cross?\')\nsrc = input.source(close, \'Source\')\nlen = input.int(200, \'Trend Length\')\nma_type = input.string(\'ema\', \'Moving Average Type\', options=[\'sma\', \'ema\', \'rma\', \'wma\', \'vwma\'], tooltip=\'Select the type of Moving Average to use to calculate the Trend\')\natr_multiplier = input.float(1., \'ATR Threshold\', step=0.5, tooltip=\'Filter the ranging market using the Average True Range\')\n\n// ----------------------- DESCRIPTION -----------------------\n// THIS SCRIPT IS A TREND FOLLOWING SYSTEM THAT USES A COMBINATION OF MOVING AVERAGE AND AVERAGE TRUE RANGE\n// TO SPOT THE TRENDS AND ENTER THE MARKET ACCODINGLY.\n// THE MARKET IS CONSIDERED IN AN UPTREND WHEN THE PRICE CLOSES ABOVE THE MOVING AVERAGE + THE AVERAGE TRUE RANGE OF THE LAST 10 PERIODS\n// THE MARKET IS CONSIDERED IN AN DOWNTREND WHEN THE PRICE CLOSES BLOW THE MOVING AVERAGE - THE AVERAGE TRUE RANGE OF THE LAST 10 PERIODS\n// BY DEFAULT, THE STRATEGY WILL ENTER LONG WHEN AN UPTREND IS SPOTTED, THEN CLOSES WHEN THE PRICE CLOSES BELOW THE MOVING AVERAGE\n// THE STRATEGY WILL ENTER SHORT WHEN A DOWNTREND IS SPOTTED, THEN CLOSES WHEN THE PRICE CLOSES ABOVE THE MOVING AVERAGE\n\n// ------------------ INDICATORS CALCULATION------------------\nmy_ma()=>\n    ma = close\n    if ma_type == \'sma\'\n        ma := ta.sma(src, len)\n    if ma_type == \'ema\'\n        ma := ta.ema(src, len)\n    if ma_type == \'rma\'\n        ma := ta.rma(src, len)\n    if ma_type == \'wma\'\n        ma := ta.wma(src, len)\n    if ma_type == \'vwma\'\n        ma := ta.vwma(src, len)\n    ma\n\ntrend = my_ma()\natr = ta.atr(10)\nuptrend = trend + atr * atr_multiplier\ndowntrend = trend - atr * atr_multiplier\n\n// ---------------- ENTRY AND EXIT CONDITIONS ----------------\n\nopen_long = strategy.position_size == 0 and src > uptrend\nclose_long = exit_type ? strategy.position_size > 0 and src < trend : strategy.position_size > 0 and src < downtrend\n\nopen_short = use_short and strategy.position_size == 0 and src < downtrend\nclose_short = exit_type ? strategy.position_size < 0 and src > trend : strategy.position_size < 0 and src > uptrend\n\nstrategy.entry(\'long\', strategy.long, when=open_long)\nstrategy.close(\'long\', when=close_long)\n\nstrategy.entry(\'short\', strategy.short, when=open_short)\nstrategy.close(\'short\', when=close_short)\n\n\n// ------------------ PLOTTING AND COLORING ------------------\ntcolor = src > uptrend ? color.green : src < downtrend ? color.red : na\n\nptrend = plot(trend, color=color.blue, linewidth=1)\npuptrend = plot(uptrend, color=color.green, linewidth=1)\npdowntrend = plot(downtrend, color=color.red, linewidth=1)\npclose = plot(close, color=na)\n\nfill(puptrend, pclose, color=close > uptrend ? color.green : na, transp = 90)\nfill(pdowntrend, pclose, color=close < downtrend ? color.red : na, transp = 90)\n\n'

class SM66597A52979A1E6A(PinePortBase, IStrategy):
    source_id = "SM_66597a52979a1e6a"
    source_file = '趋势追踪移动平均策略Swing-Trend-Moving-Average-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'use_short': False, 'exit_type': True, 'len': 200, 'ma_type': 'ema', 'atr_multiplier': 1.0}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 100
    source_commission_percent = 0.1
    source_pyramiding = 1
    source_initial_capital = 1000
    source_reproduce_stops = False
    source_risk_flags = ['func', 'broker_state', 'var_state']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
