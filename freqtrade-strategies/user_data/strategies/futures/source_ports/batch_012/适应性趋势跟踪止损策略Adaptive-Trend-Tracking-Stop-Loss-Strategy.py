"""batch_012 port of 适应性趋势跟踪止损策略Adaptive-Trend-Tracking-Stop-Loss-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-10-09 00:00:00\nend: 2023-10-16 00:00:00\nperiod: 1m\nbasePeriod: 1m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=4\n// This source code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n\n// Wilder\'s Volatility Trailing Stop Strategy with various MA\'s\n// by SparkyFlary\n\n//For Educational Purposes\n//Results can differ on different markets and can fail at any time. Profit is not guaranteed.\nstrategy(title="Wilder\'s Volatility Trailing Stop Strategy with various MA\'s", shorttitle="Trailing Stop Strategy", overlay=true)\n\nAtrMult = input(3.0, title="ATR multiplier")\nATRlength = input(7, title="ATR length")\nATRavgType = input("RMA", title="ATR moving average type", options=["RMA", "EMA", "SMA", "HULL"])\nsicType = input("close", title="significant close type for trail calculation", options=["close", "high-low"])\n\n//function for choosing moving averages\nf_ma(type, src, len) =>\n    float result = 0\n    if type == "RMA" // Wilder\'s moving averaege or Running moving average\n        result := rma(src, len)\n    if type == "EMA" // Exponential moving average\n        result := ema(src, len)\n    if type == "SMA" // Simple moving average\n        result := sma(src, len)\n    if type == "HULL" // Hull moving average\n        result := wma(2 * wma(src, len / 2) - wma(src, len), round(sqrt(len)))\n    result\n\nATR = f_ma(ATRavgType, tr, ATRlength)\nupperTrail = lowest(sicType=="close"?close:low, ATRlength) + AtrMult * ATR\nlowerTrail = highest(sicType=="close"?close:high, ATRlength) - AtrMult * ATR\n\nfloat TS = 0\nTS := close < TS[1] ? upperTrail[1] : close > TS[1] ? lowerTrail[1] : TS\n\n//plot\nplot(TS, title="trailing stop", color=close<TS?color.red:color.green)\n\n//Strategy\nbuy = crossover(close, TS)\n//sell = close < TS\nshort = crossunder(close, TS)\n//cover = close > TS\n\nstrategy.entry(id="enter long", long=true, when=buy)\n//strategy.close(id="enter long", comment="exit long", when=sell)\nstrategy.entry(id="enter short", long=false, when=short)\n//strategy.close(id="enter short", comment="exit short", when=cover)\n'

class SMAdaptiveTrendTrackingStopLossStrategy9554e5(PinePortBase, IStrategy):
    source_id = "SM_9554e5abb8617c4c"
    source_file = '适应性趋势跟踪止损策略Adaptive-Trend-Tracking-Stop-Loss-Strategy.md'
    timeframe = '1m'
    can_short = False
    source_defaults = {'AtrMult': 3.0, 'ATRlength': 7, 'ATRavgType': 'RMA', 'sicType': 'close'}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_reproduce_stops = False
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_012 md and exposed through the same PinePortBase interface used by batch_001.', 'Custom Pine function(s) are present; the original source is embedded verbatim and this generic pass flags them for per-strategy semantic verification.']

    def pine_indicators(self, dataframe, params):
        # Runtime evaluates the source against the complete OHLCV frame.
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch012Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
