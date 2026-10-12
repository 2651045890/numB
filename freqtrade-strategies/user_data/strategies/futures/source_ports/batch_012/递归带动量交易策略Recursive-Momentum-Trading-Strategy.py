"""batch_012 port of 递归带动量交易策略Recursive-Momentum-Trading-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-12-01 00:00:00\nend: 2023-12-31 23:59:59\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// @version=5\n// Original indicator by alexgrover\nstrategy(\'Extended Recursive Bands Strategy\', overlay=true, commission_type=strategy.commission.percent,commission_value=0.06,default_qty_type =strategy.percent_of_equity,default_qty_value = 100,initial_capital =1000)\nlength = input.int(260, step=10, title=\'Length\')\nsrc = input(close, title=\'Source\')\nmethod = input.string(\'Classic\', options=[\'Classic\', \'Atr\', \'Stdev\', \'Ahlr\', \'Rfv\'], title=\'Method\')\nbandDirectionCheck = input.bool(true, title=\'Bands Hold Direction\')\nlookback = input(3)\n//----\natr = ta.atr(length)\nstdev = ta.stdev(src, length)\nahlr = ta.sma(high - low, length)\nrfv = 0.\nrfv := ta.rising(src, length) or ta.falling(src, length) ? math.abs(ta.change(src)) : rfv[1]\n//-----\nf(a, b, c) =>\n    method == a ? b : c\nv(x) =>\n    f(\'Atr\', atr, f(\'Stdev\', stdev, f(\'Ahlr\', ahlr, f(\'Rfv\', rfv, x))))\n//----\nsc = 2 / (length + 1)\na = 0.\na := math.max(nz(a[1], src), src) - sc * v(math.abs(src - nz(a[1], src)))\nb = 0.\nb := math.min(nz(b[1], src), src) + sc * v(math.abs(src - nz(b[1], src)))\nc = (a+b)/2\n\n// Colors\nbeColor = #675F76\nbuColor = #a472ff\n\n// Plots\npA = plot(a, color=color.new(beColor, 0), linewidth=2, title=\'Upper Band\')\npB = plot(b, color=color.new(buColor, 0), linewidth=2, title=\'Lower Band\')\npC = plot(c, color=color.rgb(120,123,134,0), linewidth=2, title=\'Middle Band\')\nfill(pC, pA, color=color.new(beColor,90))\nfill(pC, pB, color=color.new(buColor,90))\n\n// Band keeping direction\n// By Adulari\nlongc = 0\nshortc = 0\nfor i = 0 to lookback-1\n    if b[i] > b[i+1]\n        longc:=longc+1\n    if a[i] < a[i+1]\n        shortc:=shortc+1\nbhdLong = if bandDirectionCheck\n    longc==lookback\nelse\n    true\nbhdShort = if bandDirectionCheck\n    shortc==lookback\nelse\n    true\n\n// Strategy\nif b>=low and bhdLong\n    strategy.entry(id=\'Long\',direction=strategy.long)\nif high>=a and bhdShort\n    strategy.entry(id=\'Short\',direction=strategy.short)\n\n// TP at middle line\n//if low<=c and strategy.position_size<0 and strategy.position_avg_price>close\n    //strategy.exit(id="Short",limit=close)\n//if high>=c and strategy.position_size>0 and strategy.position_avg_price<close\n    //strategy.exit(id="Long",limit=close)\n'

class SMRecursiveMomentumTradingStrategyea6bb6(PinePortBase, IStrategy):
    source_id = "SM_ea6bb6c4aa63a575"
    source_file = '递归带动量交易策略Recursive-Momentum-Trading-Strategy.md'
    timeframe = '1h'
    can_short = True
    source_defaults = {'length': 260, 'src': 'close', 'method': 'Classic', 'bandDirectionCheck': True, 'lookback': 3}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 100
    source_commission_percent = 0.06
    source_pyramiding = 0
    source_initial_capital = 1000
    source_reproduce_stops = True
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_012 md and exposed through the same PinePortBase interface used by batch_001.', 'Custom Pine function(s) are present; the original source is embedded verbatim and this generic pass flags them for per-strategy semantic verification.', 'Loop/switch logic is present and requires per-strategy semantic verification against TradingView/FMZ before treating results as parity-certified.', 'The source reads live strategy position state; batch_001-style broker-state parity must be checked manually for this file.']

    def pine_indicators(self, dataframe, params):
        # Runtime evaluates the source against the complete OHLCV frame.
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch012Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
