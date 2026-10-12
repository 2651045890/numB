"""batch_011 port of 移动平均线转折点交叉交易策略Moving-Average-Turning-Point-Crossover-Trading-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-12-01 00:00:00\nend: 2023-12-31 23:59:59\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=4\n//study(title="MA Crossover Strategy", overlay = true)\nstrategy("MA Crossover Strategy with MA Turning Point Exits", overlay=true)\nsrc = input(close, title="Source")\n\nprice = request.security(syminfo.tickerid, timeframe.period, src)\nma1 = input(25, title="1st MA Length")\ntype1 = input("SMA", "1st MA Type", options=["SMA", "EMA"])\n\nma2 = input(50, title="2nd MA Length")\ntype2 = input("SMA", "2nd MA Type", options=["SMA", "EMA"])\n\nprice1 = if (type1 == "SMA")\n    sma(price, ma1)\nelse\n    ema(price, ma1)\n    \nprice2 = if (type2 == "SMA")\n    sma(price, ma2)\nelse\n    ema(price, ma2)\n\n\n//plot(series=price, style=line,  title="Price", color=black, linewidth=1, transp=0)\nplot(series=price1, style=line,  title="1st MA", color=blue, linewidth=2, transp=0)\nplot(series=price2, style=line, title="2nd MA", color=green, linewidth=2, transp=0)\n\n\nlongCondition = crossover(price1, price2)\nif (longCondition)\n    strategy.entry("Long", strategy.long)\n\nshortCondition = crossunder(price1, price2)\nif (shortCondition)\n    strategy.entry("Short", strategy.short)\n\nlookback1 = input(1, "Lookback 1")\nroc1 = roc(price1, lookback1)\n\nma1up = false\nma1down = false\nma2up = false\nma2down = false\n\nma1up := nz(ma1up[1])\nma1down := nz(ma1down[1])\nma2up := nz(ma2up[1])\nma2down := nz(ma2down[1])\n\ntrendStrength1 = input(2, title="Minimum slope magnitude * 100", type=float) * 0.01\n\nif crossover(roc1, trendStrength1)\n    ma1up := true\n    ma1down := false\n    \nif crossunder(roc1, -trendStrength1) \n    ma1up := false\n    ma1down := true\n\nshortexitCondition = ma1up and ma1down[1]\nif (shortexitCondition)\n    strategy.close("Short")\n\nlongexitCondition = ma1down and ma1up[1]\nif (longexitCondition)\n    strategy.close("Long")\n\n'

class SMD15CAB860907A959(PinePortBase, IStrategy):
    source_id = "SM_d15cab860907a959"
    source_file = '移动平均线转折点交叉交易策略Moving-Average-Turning-Point-Crossover-Trading-Strategy.md'
    timeframe = '1h'
    can_short = True
    source_defaults = {'ma1': 25, 'type1': 'SMA', 'ma2': 50, 'type2': 'SMA', 'lookback1': 1, 'trendStrength1': 2}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = False
    source_risk_flags = ['mtf', 'var_state', 'timeframe']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
