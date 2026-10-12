"""batch_012 port of 量化交易策略-开仓量化趋势跟踪Quantitative-Trading-Strategy-Quantity-Trend-Tracking-Opening.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-12-12 00:00:00\nend: 2024-01-11 00:00:00\nperiod: 30m\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This source code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © avsr90\n\n//@version=5\nstrategy(title="Lp-Op vol",shorttitle="LPV", max_bars_back = 5000,overlay=false,format=format.volume )\n\n//Resolutions\n\nResn=input.timeframe(defval="",title="resolution")\nResn1=input.timeframe(defval="D",title="resolution")\n\n//Intraday Open and Last Price and Last price- Open Price calculations.\n\nLast_Price=math.round_to_mintick(close)\nOpen_Price = request.security(syminfo.tickerid ,Resn1,close[1],barmerge.gaps_off, barmerge.lookahead_on) \nOp_Cl=math.round_to_mintick(Last_Price-Open_Price)\n\n\n//length from Intra Day Open Price \n \nNifnum= ta.change(Open_Price)\nLength_Intraday=int(math.max(1, nz(ta.barssince(Nifnum)) + 1))\n\n//Input for Length for Volume \n\nLength_Vol=input(defval=20, title="L for Vol")\n\n// Last Price- Open price Volume, Average Intraday Last price-Open Price Volume \n//and  Volume Bars  calculations.\n\nOp_Cl_Vol=(Op_Cl*volume)\nAvg_Vol_Opcl=ta.sma(Op_Cl_Vol,Length_Intraday)\nVol_Bars=ta.sma(volume,Length_Vol)\n\n//Plots \nplot(Op_Cl_Vol,color=Op_Cl_Vol>0 ? color.green:color.red,title="OPCLV")\nplot(Avg_Vol_Opcl, title="Avg Vol", color=color.fuchsia)\nplot(Vol_Bars, title="Vol Bars", color=color.yellow)\n\n//Strategy parameters \n\nstartst=timestamp(2015,10,1)\n\nstrategy.entry("lo",strategy.long,when= ta.crossover(Op_Cl_Vol,Avg_Vol_Opcl) and ta.crossover(volume,Vol_Bars))\nstrategy.entry("sh",strategy.short,when=ta.crossunder(Op_Cl_Vol,Avg_Vol_Opcl)and ta.crossunder(volume,Vol_Bars )) \n\n\n'

class SMQuantitativeTradingStrategyQuantityTrendTrackingOpeningbbb879(PinePortBase, IStrategy):
    source_id = "SM_bbb87975a99d0b43"
    source_file = '量化交易策略-开仓量化趋势跟踪Quantitative-Trading-Strategy-Quantity-Trend-Tracking-Opening.md'
    timeframe = '30m'
    can_short = True
    source_defaults = {'Resn': '', 'Resn1': 'D', 'Length_Vol': 20}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_reproduce_stops = False
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_012 md and exposed through the same PinePortBase interface used by batch_001.', 'request.security/security is present: generic adapter keeps the expression but same-frame evaluation is only an approximation; manual multi-timeframe parity verification is required.']

    def pine_indicators(self, dataframe, params):
        # Runtime evaluates the source against the complete OHLCV frame.
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch012Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
