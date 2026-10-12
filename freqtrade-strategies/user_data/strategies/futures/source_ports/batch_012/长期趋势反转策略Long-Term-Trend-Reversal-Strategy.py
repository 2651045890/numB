"""batch_012 port of 长期趋势反转策略Long-Term-Trend-Reversal-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-11-05 00:00:00\nend: 2023-11-12 00:00:00\nperiod: 45m\nbasePeriod: 5m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This source code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © racer8\n//@version=4\n// This Algo Strategy Has Only 3 rules and 62% Win Rate (Youtube) \n\nstrategy("Trend Bounce", overlay=true)\n\nnn = input(7,"Channel Length")\nhi = highest(high,nn)\nlo = lowest(low,nn)\nn2 = input(200,"Ma Length")\nma = sma(close,n2)\n\nif close>ma and close<lo[1]\n    strategy.entry("Buy",strategy.long)\nif close>hi[1]\n    strategy.close("Buy") \n    \nif close<ma and close>hi[1]\n    strategy.entry("Sell",strategy.short)\nif close<lo[1]\n    strategy.close("Sell")\n\n\nplot(hi,"high",color=color.aqua)\nplot(lo,"low",color=color.aqua)\nplot(ma,"sma",color=color.yellow)       \n\n//-----------------------------------------Stop Loss-------------------------------------------------------\n\natr = sma(tr,10)[1]\nbought = strategy.position_size[0] > strategy.position_size[1]\nsold = strategy.position_size[0] < strategy.position_size[1]\nslm = input(2.0,"ATR Stop Loss",minval=0)\nStopPrice_Long  = strategy.position_avg_price - slm*atr              // determines stop loss\'s price \nStopPrice_Short  = strategy.position_avg_price + slm*atr              // determines stop loss\'s price \nFixedStopPrice_Long = valuewhen(bought,StopPrice_Long,0)                  // stores original StopPrice  \nFixedStopPrice_Short = valuewhen(sold,StopPrice_Short,0)                  // stores original StopPrice  \nplot(FixedStopPrice_Long,"ATR Stop Loss Long",color=color.blue,linewidth=1,style=plot.style_cross)\nplot(FixedStopPrice_Short,"ATR Stop Loss Short",color=color.red,linewidth=1,style=plot.style_cross)\nif strategy.position_size > 0\n    strategy.exit(id="Stop", stop=FixedStopPrice_Long)    // commands stop loss order to exit!\nif strategy.position_size < 0\n    strategy.exit(id="Stop", stop=FixedStopPrice_Short)    // commands stop loss order to exit!\n\n\n'

class SMLongTermTrendReversalStrategye55670(PinePortBase, IStrategy):
    source_id = "SM_e556706cb96de16c"
    source_file = '长期趋势反转策略Long-Term-Trend-Reversal-Strategy.md'
    timeframe = '45m'
    can_short = True
    source_defaults = {'nn': 7, 'n2': 200, 'slm': 2.0}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_reproduce_stops = True
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_012 md and exposed through the same PinePortBase interface used by batch_001.', 'The source reads live strategy position state; batch_001-style broker-state parity must be checked manually for this file.']

    def pine_indicators(self, dataframe, params):
        # Runtime evaluates the source against the complete OHLCV frame.
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch012Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
