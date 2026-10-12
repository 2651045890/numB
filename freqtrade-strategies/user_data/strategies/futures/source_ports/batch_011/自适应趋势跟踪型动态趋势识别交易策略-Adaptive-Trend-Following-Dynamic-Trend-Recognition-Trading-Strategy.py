"""batch_011 port of 自适应趋势跟踪型动态趋势识别交易策略-Adaptive-Trend-Following-Dynamic-Trend-Recognition-Trading-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2019-12-23 08:00:00\nend: 2024-12-25 08:00:00\nperiod: 1d\nbasePeriod: 1d\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=6\nstrategy("Supertrend + KAMA Long Strategy", overlay=true, commission_type=strategy.commission.percent, commission_value=0.1, slippage=3)\n\n// User-defined inputs for date range\nstartDate   = input(timestamp("2018-01-01 00:00:00"), title="Start Date")\nendDate     = input(timestamp("2069-12-31 23:59:59"), title="End Date")\ninDateRange = true\n\n// Inputs for KAMA and Supertrend\nkamaLength  = input.int(21, title="KAMA Length", minval=1)\natrPeriod   = input.int(10, title="Supertrend ATR Length", minval=1)\nfactor      = input.float(3.0, title="Supertrend Factor", minval=0.01, step=0.01)\n\n//------------------------- Kaufman Moving Average Adaptive (KAMA) -------------------------\nxPrice   = close\nxvnoise  = math.abs(xPrice - xPrice[1])\nLength   = kamaLength\nnfastend = 0.666\nnslowend = 0.0645\nnsignal  = math.abs(xPrice - xPrice[Length])\nfloat nnoise = 0.0\nfor i = 0 to Length - 1\n    nnoise := nnoise + xvnoise[i]\nnefratio = nnoise != 0.0 ? nsignal / nnoise : 0.0\nnsmooth  = math.pow(nefratio * (nfastend - nslowend) + nslowend, 2)\nvar float nAMA = na\nnAMA := nz(nAMA[1]) + nsmooth * (xPrice - nz(nAMA[1]))\nplot(nAMA, color=color.blue, linewidth=2, title="Kaufman KAMA")\n\n//------------------------- Supertrend Calculation -------------------------\n[stValue, dirValue] = ta.supertrend(factor, atrPeriod)\nupTrend   = dirValue < 0\ndownTrend = dirValue >= 0\nplot(dirValue < 0 ? stValue : na, "Up Trend", color=color.green, style=plot.style_linebr)\nplot(dirValue >= 0 ? stValue : na, "Down Trend", color=color.red, style=plot.style_linebr)\n\n//------------------------- Strategy Logic -------------------------\n// Entry condition: Supertrend is in uptrend AND price is above KAMA\ncanLong = inDateRange and upTrend and close > nAMA\n\n// Exit condition (Take Profit): Supertrend switches to downtrend AND price is below KAMA\nstopLoss = inDateRange and downTrend and close < nAMA\n\nif canLong\n    strategy.entry("Long", strategy.long)\n    label.new(bar_index, low, "BUY", color=color.green, textcolor=color.white, style=label.style_label_down, size=size.normal)\n\nif stopLoss\n    strategy.close("Long", comment="Stop Loss")\n    label.new(bar_index, high, "STOP LOSS", color=color.red, textcolor=color.white, style=label.style_label_up, size=size.normal)\n\n//------------------------- Alerts -------------------------\nalertcondition(canLong, title="Long Entry", message="Supertrend + KAMA Long Signal")\nalertcondition(stopLoss, title="Stop Loss", message="Supertrend switched to Downtrend and Price below KAMA")\n'

class SM7FE04A2A8B2B1D38(PinePortBase, IStrategy):
    source_id = "SM_7fe04a2a8b2b1d38"
    source_file = '自适应趋势跟踪型动态趋势识别交易策略-Adaptive-Trend-Following-Dynamic-Trend-Recognition-Trading-Strategy.md'
    timeframe = '1d'
    can_short = False
    source_defaults = {'kamaLength': 21, 'atrPeriod': 10, 'factor': 3.0}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0.1
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = False
    source_risk_flags = ['loop', 'tuple', 'var_state', 'alert_or_drawing']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
