"""batch_012 port of 随机漩涡策略Stochastic-Vortex-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2022-12-14 00:00:00\nend: 2023-12-20 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=4\nstrategy("Stochastic and Vortex Strategy", overlay=true)\n\n// Stochastic Oscillator settings\nkPeriod = input(14, title="K Period")\ndPeriod = input(3, title="D Period")\nslowing = input(3, title="Slowing")\nk = sma(stoch(close, high, low, kPeriod), slowing)\nd = sma(k, dPeriod)\n\n// Vortex Indicator settings\nlengthVI = input(14, title="Vortex Length")\ntr = max(max(high - low, abs(high - close[1])), abs(low - close[1]))\nvmPlus = abs(high - low[1])\nvmMinus = abs(low - high[1])\nviPlus = sum(vmPlus, lengthVI) / sum(tr, lengthVI)\nviMinus = sum(vmMinus, lengthVI) / sum(tr, lengthVI)\n\n// Buy condition\nbuyCondition = crossover(k, d) and viPlus > viMinus\n\nif (buyCondition)\n    strategy.entry("Buy", strategy.long)\n\nplotshape(series=buyCondition, title="Buy Signal", location=location.belowbar, color=color.green, style=shape.labelup, text="BUY")\nplot(k, title="%K", color=color.blue)\nplot(d, title="%D", color=color.orange)\nhline(80, "Overbought", color=color.red)\nhline(20, "Oversold", color=color.green)\nplot(viPlus, title="VI+", color=color.purple)\nplot(viMinus, title="VI-", color=color.red)\n\n'

class SMStochasticVortexStrategy351c04(PinePortBase, IStrategy):
    source_id = "SM_351c04d58a245450"
    source_file = '随机漩涡策略Stochastic-Vortex-Strategy.md'
    timeframe = '1d'
    can_short = False
    source_defaults = {'kPeriod': 14, 'dPeriod': 3, 'slowing': 3, 'lengthVI': 14}
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
