"""batch_012 port of 随机交叉指标动量交易策略-Stochastic-Crossover-Indicator-Momentum-Trading-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2024-03-28 00:00:00\nend: 2024-04-27 00:00:00\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=4\nstrategy("Stochastic Crossover Buy/Sell", shorttitle="Stochastic Crossover", overlay=true)\n\n// Stochastic Oscillator Parameters\nlength = input(14, title="Stochastic Length")\nsmoothK = input(3, title="Stochastic %K Smoothing")\nsmoothD = input(3, title="Stochastic %D Smoothing")\n\n// Calculate %K and %D\nstoch = stoch(close, high, low, length)\nk = sma(stoch, smoothK)\nd = sma(k, smoothD)\n\n// Plot Stochastic Lines\nplot(k, color=color.blue, linewidth=2, title="%K")\nplot(d, color=color.red, linewidth=2, title="%D")\n\n// Stochastic Crossover Buy/Sell Signals\nbuySignal = crossover(k, d) and k < 20 // Buy when %K crosses above %D and %K is below 20\nsellSignal = crossunder(k, d) and k > 80 // Sell when %K crosses below %D and %K is above 80\n\n// Plot Buy/Sell Arrows\nplotshape(series=buySignal, style=shape.triangleup, location=location.belowbar, color=color.green, size=size.small, title="Buy Signal")\nplotshape(series=sellSignal, style=shape.triangledown, location=location.abovebar, color=color.red, size=size.small, title="Sell Signal")\n\n// Entry and Exit Points\nstrategy.entry("Buy", strategy.long, when=buySignal)\nstrategy.close("Buy", when=sellSignal)\n\nstrategy.entry("Sell", strategy.short, when=sellSignal)\nstrategy.close("Sell", when=buySignal)\n\n'

class SMStochasticCrossoverIndicatorMomentumTradingStrategy8750ea(PinePortBase, IStrategy):
    source_id = "SM_8750ead9c91f9acb"
    source_file = '随机交叉指标动量交易策略-Stochastic-Crossover-Indicator-Momentum-Trading-Strategy.md'
    timeframe = '1h'
    can_short = True
    source_defaults = {'length': 14, 'smoothK': 3, 'smoothD': 3}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
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
