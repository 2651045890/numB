"""batch_011 port of 赫斯特未来分界线策略-Hurst-Future-Lines-of-Demarcation-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2024-04-27 00:00:00\nend: 2024-04-28 00:00:00\nperiod: 10m\nbasePeriod: 1m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This source code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © BarefootJoey\n\n//@version=5\nstrategy("Hurst Future Lines of Demarcation Strategy", overlay=true)\n\n// FLD Settings\nsource      = input(ohlc4, \'Source\')\nsmoothFLD   = input.bool(false, \'Smooth FLD\')\nFLDtransp   = input(33, \'FLD transparency\')\nFLDsmooth   = input.int(5, "FLD Smoothing", minval=1, tooltip="Number of trading days to smooth the FLD")   \nFLD_out = ta.sma(source , smoothFLD ? FLDsmooth : 1)\n\nclose_buy_in_1 = input.string(\'Price\', \'Input Close Trigger 1\', options=[\'Price\', \'Signal\', \'Trade\', \'Trend\', \'None\'])\nclose_buy_in_2 = input.string(\'Trade\', \'Input Close Trigger 2\', options=[\'Price\', \'Signal\', \'Trade\', \'Trend\', \'None\'])\n\n// Quarter Cycle (Default: 20 day) Length Pivot Cycle\ncol_q = input.color(#da00ff, "Quarter Cycle Color")\ncyc_q = input.int(5, "Signal Cycle Length")\nplot(FLD_out, color=color.new(col_q, FLDtransp), title=\'Signal FLD\', offset = math.round(cyc_q/2) )\n\n// Trade Cycle (Default: 20 day) Length Pivot Cycle\ncol = input.color(#ff9800, "Trade Cycle Color")\ncyc = input.int(20, "Trade Cycle Length")\nplot(FLD_out, color=color.new(col, FLDtransp), title=\'Trade FLD\', offset = math.round(cyc/2) )\n\n// Double Cycle (Default: 80 day) Length Pivot Cycle\ncol_d = input.color(color.aqua, "Double Cycle Color")\ncyc_d = input.int(80, "Trend Cycle Length")\nplot(FLD_out, color=color.new(col_d, FLDtransp), title=\'Trend FLD\', offset = math.round(cyc_d/2) )\n\n// Strategy Plots\nprice = source\nsignal = FLD_out[math.round(cyc_q/2)]\ntrade = FLD_out[math.round(cyc/2)]\ntrend = FLD_out[math.round(cyc_d/2)]\n\n// Trend State\nvar state = 0\nif signal > trade and trade > trend \n    state := 1 // (A)\n    state\nif state == 1 and price < signal\n    state := 2 // (B)\n    state\nif signal < trade and trade > trend \n    state := 3 // (C)\n    state\nif state == 3 and price < signal \n    state := 4 // (D)\n    state\nif signal < trade and trade < trend \n    state := 5 // (E)\n    state\nif state == 5 and price < signal\n    state := 6 // (F)\n    state\nif signal > trade and trade < trend\n    state := 7 // (G)\n    state\nif state == 7 and price < signal\n    state := 8 // (H)\n    state\nstate := state\n\n// Strategy Definitions\nclose_buy_out_1 = close_buy_in_1 == \'Price\' ? price : close_buy_in_1 == \'Signal\' ? signal : close_buy_in_1 == \'Trade\' ? trade : close_buy_in_1 == \'Trend\' ? trend : na\nclose_buy_out_2 = close_buy_in_2 == \'Price\' ? price : close_buy_in_2 == \'Signal\' ? signal : close_buy_in_2 == \'Trade\' ? trade : close_buy_in_2 == \'Trend\' ? trend : na\nbuy = ta.crossover(price, signal) and state == 1\nclose_buy = strategy.position_size>0 and ta.crossunder(close_buy_out_1, close_buy_out_2)\nsell = ta.crossunder(price, signal) and state == 6\nclose_sell = strategy.position_size<0 and ta.crossover(close_buy_out_1, close_buy_out_2)\n\n// FLD Interaction State Background\ninteraction_color = state == 1 ? color.green : // A\n  state == 2 ? color.aqua : // B\n  state == 3 ? color.blue : // C\n  state == 4 ? color.purple : // D\n  state == 5 ? color.white : // E\n  state == 6 ? color.red :// F\n  state == 7 ? color.orange : // G\n  state == 8 ? color.yellow : na // H\n\nbgcolor(color.new(interaction_color, 90), title= "A-H Background")\n\nbar_color = strategy.position_size>0 ? #00ff0a : strategy.position_size<0 ? #FF0000 : na\nbarcolor(bar_color)\n\nif buy\n    strategy.entry("Buy", strategy.long)\nif close_buy\n    strategy.close("Buy", qty_percent=100)\n\nif sell\n    strategy.entry("Sell", strategy.short)\nif close_sell\n    strategy.close("Sell", qty_percent=100)\n\n// EoS made w/ ❤ by @BarefootJoey ✌??'

class SME655A411FC1A332E(PinePortBase, IStrategy):
    source_id = "SM_e655a411fc1a332e"
    source_file = '赫斯特未来分界线策略-Hurst-Future-Lines-of-Demarcation-Strategy.md'
    timeframe = '10m'
    can_short = True
    source_defaults = {'smoothFLD': False, 'FLDtransp': 33, 'FLDsmooth': 5, 'close_buy_in_1': 'Price', 'close_buy_in_2': 'Trade', 'cyc_q': 5, 'cyc': 20, 'cyc_d': 80}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = False
    source_risk_flags = ['broker_state', 'var_state']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
