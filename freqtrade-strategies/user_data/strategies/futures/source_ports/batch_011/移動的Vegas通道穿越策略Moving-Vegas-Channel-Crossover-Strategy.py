"""batch_011 port of 移動的Vegas通道穿越策略Moving-Vegas-Channel-Crossover-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2022-12-26 00:00:00\nend: 2024-01-01 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=4\n\nstrategy("Vegas Tunnel strategy", overlay=true)\n//-------------------------------------------\n//-------------------------------------------\n// Inputs\nuseCurrentRes = input(true, title="Use Current Chart Resolution?")\nresCustom = input(title="Use Different Timeframe? Uncheck Box Above", type=input.resolution, defval="D")\n//tfSet = input(title = "Time Frame", options=["Current","120", "240", "D", "W"], defval="D")\ntfSet = useCurrentRes ? timeframe.period : resCustom\nmaPeriods2 = input(12, "12 EMA")\nmaPeriods6 = input(240, "240 SMA")\nBBlength = input(20, title="BB Length", minval=1)\nBBsrc = input(close, title="BB Source")\nmult = input(2.0, minval=0.001, maxval=50, title="BB StdDev")\nsm2 = security(syminfo.tickerid, tfSet, ema(close, maPeriods2))\nsm6 = security(syminfo.tickerid, tfSet, sma(close, maPeriods6))\np2 = plot(sm2, color=color.green, transp=30,  linewidth=2, title="SMA2")\np6 = plot(sm6, color=color.white, transp=30,  linewidth=2, title="SMA6")\n//BB\nbasis = sma(BBsrc, BBlength)\ndev = mult * stdev(BBsrc, BBlength)\nupper = basis + dev\nlower = basis - dev\noffset = input(0, "BB Offset", type = input.integer, minval = -500, maxval = 500)\n//plot(basis, "Basis", color=color.blue,linewidth, offset = offset)\npBB1 = plot(upper, "Upper", color=color.blue, offset = offset)\npBB2= plot(lower, "Lower", color=color.blue, offset = offset)\n\n//MACD\nfast_ma = ema(close, 48)\nslow_ma = ema(close, 56)\nmacd = fast_ma - slow_ma\n\n//vagas隧道\nf1=ema(close, 36)\nf2=ema(close, 43)\nf3=ema(close, 144)\nf4=ema(close, 169)\nf5=ema(close, 576)\nf6=ema(close, 676)\nf7=ema(close,2304)\nz1=plot(f1,color=color.red, title="ema36",transp=100)\nz2=plot(f2,color=color.red, title="ema43",transp=100)\nz3=plot(f3,color=color.green, title="ema144",transp=100)\nz4=plot(f4,color=color.green, title="ema169",transp=100)\nz5=plot(f5,color=color.white, title="ema576",transp=100)\nz6=plot(f6,color=color.white, title="ema676",transp=100)\nfill(z1, z2, color=color.red,transp=60)\nfill(z3, z4, color=color.green,transp=60)\nfill(z5, z6, color=color.gray,transp=60)\n\n// Make input options that configure backtest date range\nstartDate = input(title="Start Date", type=input.integer,\n     defval=1, minval=1, maxval=31)\nstartMonth = input(title="Start Month", type=input.integer,\n     defval=1, minval=1, maxval=12)\nstartYear = input(title="Start Year", type=input.integer,\n     defval=2018, minval=1800, maxval=2100)\nendDate = input(title="End Date", type=input.integer,\n     defval=1, minval=1, maxval=31)\nendMonth = input(title="End Month", type=input.integer,\n     defval=11, minval=1, maxval=12)\nendYear = input(title="End Year", type=input.integer,\n     defval=2030, minval=1800, maxval=2100)\n// Look if the close time of the current bar\n// falls inside the date range\ninDateRange =  true\n\n//波段多\nif (inDateRange and crossunder(f3,f1))// \n    strategy.entry("buy", strategy.long,1, when=macd>0, comment = "買Long-term")\nbuyclose=crossunder(f3,f5) \nstrategy.close("buy", when = buyclose, comment = "關Long-term")\n//多策略1\nif (inDateRange and crossover(low , f3) and macd>0 and f3>f6)\n    strategy.entry("buy1", strategy.long,100, comment = "買Mid-term")\nbuyclose1=crossunder(close,upper*0.999) \nif (macd<0 or f3<f6)\n    strategy.close("buy1", comment = "關Mid-term")\n//strategy.close("buy1",when=cross(basis,close), comment = "關M",qty_percent=50)\nstrategy.close("buy1", when = buyclose1, comment = "關Mid-term",qty_percent=100)\n//多策略3\nif (inDateRange and  (macd>0) and crossunder(low,f1) and f1>f4) // \n    strategy.entry("buy3", strategy.long,1, comment = "買Short-term")\nbuyclose3=crossunder(close,upper*0.999)\nif (macd<0 or f1<f4)\n    strategy.close("buy3", comment = "關Short-term")\nstrategy.close("buy3", when = buyclose3, comment = "關Short-term")\n//多策略4\nif (inDateRange and  (macd>0) and crossunder(low,f5) and f4>f5) // \n    strategy.entry("buy4", strategy.long,1, comment = "買Long-term")\nbuyclose4=crossunder(close,upper*0.999)\nif (macd<0 or f4<f6)\n    strategy.close("buy4", comment = "關Long-term")\nstrategy.close("buy4", when = buyclose4, comment = "關Long-term")\n    \n//空策略1\nif (inDateRange and  (macd<0) and crossunder(high,f1) and f1<f3 and f3<f6) // \n    strategy.entry("sell1", strategy.short,1, comment = "空Short-term")\nsellclose1=crossunder(lower*0.999,close)\nif (macd>0 or f1>f4)\n    strategy.close("sell1", comment = "關空Short-term")\nstrategy.close("sell1", when = sellclose1, comment = "關空Short-term")\n//空策略2\nif (inDateRange and  (macd<0) and crossunder(high,f4) and f4<f6) // \n    strategy.entry("sell2", strategy.short,1, comment = "空Mid-term")\nsellclose2=crossunder(lower,close)\nif (macd>0 or f4>f6)\n    strategy.close("sell2", comment = "關空Mid-term")\nstrategy.close("sell2", when = sellclose2, comment = "關Mid-term")\n//空策略3\nif (inDateRange and (macd<0) and crossunder(high,f6)) // \n    strategy.entry("sell3", strategy.short,1, comment = "空Long-term")\nsellclose3=crossunder(lower,close)\nif (macd>0 or f6>f7)\n    strategy.close("sell3", comment = "關空Long-term")\nstrategy.close("sell3", when = sellclose3, comment = "關空Long-term")'

class SM7B126C9900CFBC0D(PinePortBase, IStrategy):
    source_id = "SM_7b126c9900cfbc0d"
    source_file = '移動的Vegas通道穿越策略Moving-Vegas-Channel-Crossover-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'useCurrentRes': True, 'resCustom': 'D', 'maPeriods2': 12, 'maPeriods6': 240, 'BBlength': 20, 'mult': 2.0, 'offset': 0, 'startDate': 1, 'startMonth': 1, 'startYear': 2018, 'endDate': 1, 'endMonth': 11, 'endYear': 2030}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = False
    source_risk_flags = ['mtf', 'timeframe']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
