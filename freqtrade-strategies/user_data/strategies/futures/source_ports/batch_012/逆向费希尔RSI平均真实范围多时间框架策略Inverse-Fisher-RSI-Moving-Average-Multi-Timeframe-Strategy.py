"""batch_012 port of 逆向费希尔RSI平均真实范围多时间框架策略Inverse-Fisher-RSI-Moving-Average-Multi-Timeframe-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2022-11-14 00:00:00\nend: 2023-11-20 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=4\nstrategy(title = "Inverse Fisher RSI-MTF2", shorttitle="INRSIM2",overlay=true)\n//Inputs\nRSI_pm = input(5, title="RSI Main Period",minval=2)\nRSI_ps = input(1, title="RSI Smooth Period",minval=0)\n\n//Functions\nIF(input)=>(exp(2*input)-1)/(exp(2*input)+1)\n\n//RSI Calculation\nraw_RSI=0.1*(rsi(close,RSI_pm)-50)\nwma_RSI=wma(raw_RSI,RSI_ps)*100\nIF_RSI = IF(wma_RSI)\n\nresCustom = input(title="Timeframe", defval="1440" )\nv=request.security(syminfo.tickerid, resCustom,IF_RSI)\na=v>0.8\nb=v<-0.8\n\nz=0.8\nbuy = crossover(v,z)\nsell=crossunder(v,b)\n \nplotshape(sell, title="sell", style=shape.triangledown,location=location.abovebar, color=red, transp=0, size=size.small)\nplotshape(buy,  title="buy", style=shape.triangleup,location=location.belowbar, color=green, transp=0, size=size.small)\n\n\n//Strategy\ngolong =  crossover(v,z)\ngoshort =  crossunder(v,b)\n\nstrategy.entry("Buy",strategy.long,when = golong)\nstrategy.entry("Sell",strategy.short,when = goshort)\n\n\n\n\n'

class SMRSIInverseFisherRSIMovingAverageMultiTimeframeStrategy527e3c(PinePortBase, IStrategy):
    source_id = "SM_527e3cb5abf3a25d"
    source_file = '逆向费希尔RSI平均真实范围多时间框架策略Inverse-Fisher-RSI-Moving-Average-Multi-Timeframe-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'RSI_pm': 5, 'RSI_ps': 1, 'resCustom': '1440'}
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
