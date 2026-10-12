"""batch_012 port of 逆转双均线交叉策略Reversal-Dual-Moving-Average-Crossover-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-11-27 00:00:00\nend: 2023-12-27 00:00:00\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=3\n//study(title="MA Crossover Strategy", overlay = true)\nstrategy("MA Crossover Strategy with MA Turning Point Exits", overlay=true)\nsrc = input(close, title="Source")\n\nprice = request.security(syminfo.tickerid, timeframe.period, src)\nma1 = input(5, title="1st MA Length")\ntype1 = input("HMA", "1st MA Type", options=["SMA", "EMA", "HMA", "VWMA"])\n\nma2 = input(7, title="2nd MA Length")\ntype2 = input("HMA", "2nd MA Type", options=["SMA", "EMA", "HMA", "VWMA"])\n\nf_hma(_src, _length)=>\n    _return = wma((2*wma(_src, _length/2))-wma(_src, _length), round(sqrt(_length)))\nprice1 = if (type1 == "SMA")\n    sma(price, ma1)\nelse\n    if (type1 == "EMA")\n        ema(price, ma1)\n    else\n        if (type1 == "VWMA")\n            vwma(price, ma1)\n        else\n            f_hma(price, ma1)\n    \nprice2 = if (type2 == "SMA")\n    sma(price, ma2)\nelse\n    if (type2 == "EMA")\n        ema(price, ma2)\n    else\n        if (type2 == "VWMA")\n            vwma(price, ma2)\n        else\n            f_hma(price, ma2)\n\n//plot(series=price, style=line,  title="Price", color=black, linewidth=1, transp=0)\nplot(series=price1, style=line,  title="1st MA", color=blue, linewidth=2, transp=0)\nplot(series=price2, style=line, title="2nd MA", color=green, linewidth=2, transp=0)\n\n\nlongCondition = crossover(price1, price2)\nif (longCondition) // and time>timestamp(2018,6,1,9,30)\n    strategy.entry("Long", strategy.long)\n\nshortCondition = crossunder(price1, price2)\nif (shortCondition) // and time>timestamp(2018,6,1,9,30)\n    strategy.entry("Short", strategy.short)\n\nlookback1 = input(1, "Lookback 1")\nroc1 = roc(price1, lookback1)\n\nma1up = false\nma1down = false\nma2up = false\nma2down = false\n\nma1up := nz(ma1up[1])\nma1down := nz(ma1down[1])\nma2up := nz(ma2up[1])\nma2down := nz(ma2down[1])\n\ntrendStrength1 = input(2, title="Minimum slope magnitude * 100", type=float) * 0.01\n\nif crossover(roc1, trendStrength1)\n    ma1up := true\n    ma1down := false\n    \nif crossunder(roc1, -trendStrength1) \n    ma1up := false\n    ma1down := true\n\nshortexitCondition = ma1up and ma1down[1]\nif (shortexitCondition)\n    strategy.close("Short")\n\nlongexitCondition = ma1down and ma1up[1]\nif (longexitCondition)\n    strategy.close("Long")\n\n\n'

class SMReversalDualMovingAverageCrossoverStrategy8a7317(PinePortBase, IStrategy):
    source_id = "SM_8a7317a79cad3814"
    source_file = '逆转双均线交叉策略Reversal-Dual-Moving-Average-Crossover-Strategy.md'
    timeframe = '1h'
    can_short = True
    source_defaults = {'src': 'close', 'ma1': 5, 'type1': 'HMA', 'ma2': 7, 'type2': 'HMA', 'lookback1': 1}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_reproduce_stops = False
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_012 md and exposed through the same PinePortBase interface used by batch_001.', 'request.security/security is present: generic adapter keeps the expression but same-frame evaluation is only an approximation; manual multi-timeframe parity verification is required.', 'Custom Pine function(s) are present; the original source is embedded verbatim and this generic pass flags them for per-strategy semantic verification.']

    def pine_indicators(self, dataframe, params):
        # Runtime evaluates the source against the complete OHLCV frame.
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch012Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
