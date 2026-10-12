"""batch_011 port of 自适应RSI震荡阈值动态交易策略-Adaptive-RSI-Oscillator-Dynamic-Trading-Strategy-with-Threshold-Optimization.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2019-12-23 08:00:00\nend: 2024-11-11 00:00:00\nperiod: 1d\nbasePeriod: 1d\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This Pine Script™ code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © PineCodersTASC\n\n//  TASC Issue: October 2024\n//     Article: Overbought/Oversold\n//              Oscillators: Useless Or Just Misused\n//  Article By: Francesco P. Bufi\n//    Language: TradingView\'s Pine Script™ v5\n// Provided By: PineCoders, for tradingview.com\n\n//@version=5\ntitle  =\'TASC 2024.10 Adaptive Oscillator Threshold\'\nstitle = \'AdapThrs\'\nstrategy(title, stitle, false, default_qty_type = strategy.percent_of_equity,\n         default_qty_value = 10, slippage = 5)\n\n// --- Inputs ---\nstring sys    = input.string("BAT", "System", options=["Traditional", "BAT"])\nint rsiLen    = input.int(2, "RSI Length", 1)\nint buyLevel  = input.int(14, "Buy Level", 0)\nint adapLen   = input.int(8, "Adaptive Length", 2) \nfloat adapK   = input.float(6, "Adaptive Coefficient")\nint exitBars  = input.int(28, "Fixed-Bar Exit", 1, group = "Strategy Settings")\nfloat DSL     = input.float(1600, "Dollar Stop-Loss", 0, group = "Strategy Settings")\n\n// --- Functions --- \n//  Bufi\'s Adaptive Threshold\nBAT(float price, int length) =>\n    float sd = ta.stdev(price, length)\n    float lr = ta.linreg(price, length, 0)\n    float slope = (lr - price[length]) / (length + 1)\n    math.min(0.5, math.max(-0.5, slope / sd))\n\n// --- Calculations ---\nfloat osc = ta.rsi(close, rsiLen)\n\n// Strategy entry rules\n// - Traditional system\nif sys == "Traditional" and osc < buyLevel\n    strategy.entry("long", strategy.long)\n// - BAT system \nfloat thrs = buyLevel * adapK * BAT(close, adapLen)\nif sys == "BAT" and osc < thrs\n    strategy.entry("long", strategy.long)\n\n// Strategy exit rules\n// - Fixed-bar exit\nint nBar = bar_index - strategy.opentrades.entry_bar_index(0)\nif exitBars > 0 and nBar >= exitBars\n    strategy.close("long", "exit")\n// - Dollar stop-loss\nif DSL > 0 and strategy.opentrades.profit(0) <= - DSL\n    strategy.close("long", "Stop-loss", immediately = true)\n\n// Visuals\nrsiColor  = #1b9e77\nthrsColor = #d95f02\nrsiLine   = plot(osc, "RSI", rsiColor, 1)\nthrsLine  = plot(sys == "BAT" ? thrs : buyLevel, "Threshold", thrsColor, 1)\nzeroLine  = plot(0.0, "Zero", display = display.none)\nfill(zeroLine, thrsLine, sys == "BAT" ? thrs : buyLevel, 0.0, color.new(thrsColor, 60), na)\n'

class SM72B3081147B7C86A(PinePortBase, IStrategy):
    source_id = "SM_72b3081147b7c86a"
    source_file = '自适应RSI震荡阈值动态交易策略-Adaptive-RSI-Oscillator-Dynamic-Trading-Strategy-with-Threshold-Optimization.md'
    timeframe = '1d'
    can_short = False
    source_defaults = {'sys': 'BAT', 'rsiLen': 2, 'buyLevel': 14, 'adapLen': 8, 'adapK': 6, 'exitBars': 28, 'DSL': 1600}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 10
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = False
    source_risk_flags = ['func', 'broker_state']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
