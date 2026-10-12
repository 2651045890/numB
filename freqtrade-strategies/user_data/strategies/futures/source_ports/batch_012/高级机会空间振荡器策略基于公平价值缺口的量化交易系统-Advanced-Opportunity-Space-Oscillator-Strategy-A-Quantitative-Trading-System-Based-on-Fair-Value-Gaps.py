"""batch_012 port of 高级机会空间振荡器策略基于公平价值缺口的量化交易系统-Advanced-Opportunity-Space-Oscillator-Strategy-A-Quantitative-Trading-System-Based-on-Fair-Value-Gaps.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2024-02-22 00:00:00\nend: 2025-02-19 08:00:00\nperiod: 1h\nbasePeriod: 1h\nexchanges: [{"eid":"Binance","currency":"ETH_USDT"}]\n*/\n\n// ----------------------------------------------------------------------------\n// This Pine Script™ code is subject to the terms of the Mozilla Public License\n// 2.0 at https://mozilla.org/MPL/2.0/\n// © OmegaTools\n// ----------------------------------------------------------------------------\n\n//@version=5\nstrategy("FVG Oscillator Strategy", \n     shorttitle="FVG Osc v5 [Strategy]", \n     overlay=false, \n     initial_capital=100000, \n     default_qty_type=strategy.percent_of_equity, \n     default_qty_value=100)\n\n//------------------------------------------------------------------------------\n// 1) Input Parameters\n//------------------------------------------------------------------------------\nlnt   = input.int(50, "Bars Back")\narea  = input.bool(true, "Show Areas")\nupcol = input.color(#2962ff, "Positive Color")\ndncol = input.color(#e91e63, "Negative Color")\n\n//------------------------------------------------------------------------------\n// 2) FVG Detection\n//    bfvg = bullish FVG, sfvg = bearish FVG\n//------------------------------------------------------------------------------\nbfvg = low > high[2]\nsfvg = high < low[2]\n\n//------------------------------------------------------------------------------\n// 3) Additional Conditions - FVG Verification (Volume, Gap Size)\n//------------------------------------------------------------------------------\nvol  = volume > ta.sma(volume, 10)\nbatr = (low - high[2]) > ta.sma(low - high[2], lnt) * 1.5\nsatr = (high - low[2]) > ta.sma(high - low[2], lnt) * 1.5\n\n//------------------------------------------------------------------------------\n// 4) Sum of Bullish / Bearish FVG within the Last lnt Bars\n//------------------------------------------------------------------------------\ncountup   = math.sum(bfvg ? 1 : 0, lnt)      // +1 for each BFVG\ncountdown = math.sum(sfvg ? -1 : 0, lnt)     // -1 for each SFVG\n\n//------------------------------------------------------------------------------\n// 5) Verification (e.g., Require Higher Volume or Large Gap)\n//------------------------------------------------------------------------------\nverifyb = (bfvg and vol[1]) or (bfvg and batr)\nverifys = (sfvg and vol[1]) or (sfvg and satr)\n\n//------------------------------------------------------------------------------\n// 6) Normalized Gap Values\n//------------------------------------------------------------------------------\nnormb = ((low - high[2]) * countup * 0.75) / ta.highest(low - high[2], lnt)\nnorms = ((high - low[2]) * countdown * 0.75) / ta.lowest(high - low[2], lnt)\n\n//------------------------------------------------------------------------------\n// 7) Total Net FVG Count + Calculation of Maximum for fill()\n//------------------------------------------------------------------------------\ntotcount = countup + countdown\nmax      = math.max(\n               ta.highest(countup, 200), \n               ta.highest(math.abs(countdown), 200)\n           )\n\n//------------------------------------------------------------------------------\n// 8) Plotting Values (as in an indicator – can be kept for visualization)\n//------------------------------------------------------------------------------\nup   = plot(countup,     "Buy FVG",  color=upcol,  display=display.none)\ndown = plot(countdown,   "Sell FVG", color=dncol,  display=display.none)\nzero = plot(0, "", color.new(color.gray, 100), display=display.none, editable=false)\n\n// Net Value (sum of FVG)\nplot(totcount, "Net Value", color=color.new(color.gray, 50))\n\n// Filling areas above/below zero\n\nplot(verifyb ? normb : na, "Long Pattern Width",  color=upcol,  linewidth=1, style=plot.style_histogram)\nplot(verifys ? norms : na, "Short Pattern Width", color=dncol, linewidth=1, style=plot.style_histogram)\n\n//------------------------------------------------------------------------------\n// 9) Simple Trading Logic (STRATEGY)\n//------------------------------------------------------------------------------\n// - If "verifyb" is detected, go long.\n// - If "verifys" is detected, go short.\n//\n// You can extend this with Stop Loss, Take Profit, \n// closing old positions, etc.\n//------------------------------------------------------------------------------\nbool goLong  = verifyb\nbool goShort = verifys\n\n// Basic example: Open Long if verifyb, Open Short if verifys.\nif goLong\n    // First close any short position if it exists\n    if strategy.position_size < 0\n        strategy.close("Short FVG")\n    // Then open Long\n    strategy.entry("Long FVG", strategy.long)\n\nif goShort\n    // First close any long position if it exists\n    if strategy.position_size > 0\n        strategy.close("Long FVG")\n    // Then open Short\n    strategy.entry("Short FVG", strategy.short)\n\n'

class SMAdvancedOpportunitySpaceOscillatorStrategyAQuantitativec0b961(PinePortBase, IStrategy):
    source_id = "SM_c0b961dde7acb523"
    source_file = '高级机会空间振荡器策略基于公平价值缺口的量化交易系统-Advanced-Opportunity-Space-Oscillator-Strategy-A-Quantitative-Trading-System-Based-on-Fair-Value-Gaps.md'
    timeframe = '1h'
    can_short = True
    source_defaults = {'lnt': 50, 'area': True, 'upcol': '#2962ff', 'dncol': '#e91e63'}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 100
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 100000
    source_reproduce_stops = False
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_012 md and exposed through the same PinePortBase interface used by batch_001.', 'The source reads live strategy position state; batch_001-style broker-state parity must be checked manually for this file.']

    def pine_indicators(self, dataframe, params):
        # Runtime evaluates the source against the complete OHLCV frame.
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch012Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
