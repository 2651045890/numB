"""batch_012 port of 逆向线性回归策略Reverse-Linear-Regression-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-12-21 00:00:00\nend: 2023-12-28 00:00:00\nperiod: 30m\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=4\nstrategy("Reverse Up/Down Strategy", currency=currency.USD, initial_capital=1000, pyramiding=2, default_qty_type=strategy.percent_of_equity, default_qty_value=100,overlay=true)\n\n//User Options\nconsecutiveBarsUp   = input(title="Sell after how many bars up?",   type=input.integer, minval=1, defval=1)\nconsecutiveBarsDown = input(title="Buy after how many bars down?",  type=input.integer, minval=1, defval=1)\natrLength           = input(title="ATR Length",                     type=input.integer, minval=1, defval=14)\natrMult             = input(title="ATR Multiplier",                 type=input.float,   minval=0.1, defval=2.33)\n\n//ATR Channel\nadjustedATR     = sma(atr(atrLength),atrLength) * atrMult\nlongATR         = low - adjustedATR\nshortATR        = high + adjustedATR\nplot(shortATR,  title="Short ATR",  color=color.red)\nplot(longATR,   title="Long ATR",   color=color.lime)\n\n\n// This is the true linear regression slope rather than an approximation given by numerical differentiation\nsrc = hlc3\nlen = input(defval=14, minval=1, title="Slope Length")\nlrc = linreg(src, len, 0)\nlrc1 = linreg(src, len,1)\nlrs = (lrc-lrc1)\n\n//Check if last candle was up or down\npriceOpen = open\npriceClose = close\nlongCondition = priceOpen > priceClose\nshortCondition = priceOpen < priceClose\nups = 0.0\ndns = 0.0\n\nups := shortCondition ? nz(ups[1]) + 1 : 0\ndns := longCondition ? nz(dns[1]) + 1 : 0\n\nif (shortCondition)\n    strategy.close("buy", qty_percent=100, comment="Close")\n    if (ups >= consecutiveBarsUp and lrs <= 0)\n    \tstrategy.entry("sell", strategy.short, comment="Sell")\n    \t\n\nif (longCondition)\n    strategy.close("sell", qty_percent=100, comment="Close")\n    if (dns >= consecutiveBarsDown and lrs >= 0)\n\t    strategy.entry("buy", strategy.long, comment = "Buy")\n\n'

class SMReverseLinearRegressionStrategye50836(PinePortBase, IStrategy):
    source_id = "SM_e50836836a5633b3"
    source_file = '逆向线性回归策略Reverse-Linear-Regression-Strategy.md'
    timeframe = '30m'
    can_short = True
    source_defaults = {'consecutiveBarsUp': 1, 'consecutiveBarsDown': 1, 'atrLength': 14, 'atrMult': 2.33, 'len': 14}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 100
    source_commission_percent = 0.0
    source_pyramiding = 2
    source_initial_capital = 1000
    source_reproduce_stops = False
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_012 md and exposed through the same PinePortBase interface used by batch_001.']

    def pine_indicators(self, dataframe, params):
        # Runtime evaluates the source against the complete OHLCV frame.
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch012Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
