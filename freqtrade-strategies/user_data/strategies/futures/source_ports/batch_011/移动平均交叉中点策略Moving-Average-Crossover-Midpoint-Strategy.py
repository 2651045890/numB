"""batch_011 port of 移动平均交叉中点策略Moving-Average-Crossover-Midpoint-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-11-12 00:00:00\nend: 2023-12-12 00:00:00\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This source code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © MGULHANN\n//@version=5\nstrategy(\'Forex Midpoint Stratejisi For Nasdaq \', overlay=true)\nBPeriod = input(131, \'Başlangıç Period\')\nkaydirma = input(14, \'Kaydırma Seviyesi\')\nyuzdeseviyesi = input.float(0.0006, \'Yüzde Seviyesi\', step=0.0001)\nlen = input.int(44, minval=1, title="Length")\nsrc = input(close, title="Source")\nout = ta.sma(src, len)\n\nma(source, length, type) =>\n    switch type\n        "SMA" => ta.sma(source, length)\n        "EMA" => ta.ema(source, length)\n        "SMMA (RMA)" => ta.rma(source, length)\n        "WMA" => ta.wma(source, length)\n        "VWMA" => ta.vwma(source, length)\n\ntypeMA = input.string(title = "Method", defval = "EMA", options=["SMA", "EMA", "SMMA (RMA)", "WMA", "VWMA"], group="Smoothing")\nsmoothingLength = input.int(title = "Length", defval = 53, minval = 1, maxval = 100, group="Smoothing")\nsmoothingLine = ma(out, smoothingLength, typeMA)\n//plot(smoothingLine, title="Smoothing Line", color=color.red, linewidth = 2)\n\n//zararDurdurmaYuzde = input.float(0.2, title=\'Zarar Durdurma %\', step=0.01) / 100\n//karAlmaYuzde = input.float(0.5, title=\'Kar Alma %\', step=0.01) / 100\n\n\n//MIDPOINT HESAPLA\nmidpoint1 = ta.highest(high, BPeriod) + ta.lowest(low, BPeriod)\nmidpoint2 = midpoint1 / 2\nmidyuzdeseviyesi = midpoint2 * yuzdeseviyesi\nmidtopdeger = midyuzdeseviyesi + midpoint2\n\n//GİRİŞ KOŞULLARI\nbuycross = ta.crossover(smoothingLine, midtopdeger[kaydirma]) //? aort > ta.sma(close,50) : na\nsellcross = ta.crossover(midtopdeger[kaydirma], smoothingLine) // ? aort < ta.sma(close,50) : na\n\n//LONG GİRİŞ\nif (buycross)\n    strategy.entry("BUY", strategy.long)\n    //longKarAl = strategy.position_avg_price * (1 + karAlmaYuzde)\n    //longZararDurdur = strategy.position_avg_price * (1 - zararDurdurmaYuzde)\n    //strategy.exit("Long Exit","Long", stop=longZararDurdur)\n    \n   \n//SHORT GİRİŞ    \nif (sellcross)\n    strategy.entry("SELL", strategy.short)\n    //shortKarAl = strategy.position_avg_price * (1 - karAlmaYuzde)\n    //shortZararDurdur = strategy.position_avg_price * (1 + zararDurdurmaYuzde)\n    //strategy.exit("Short Exit","Short", stop=shortZararDurdur)\n   \n//plot(midtopdeger, offset=kaydirma, linewidth=2, color=color.blue)\n'

class SME00B375023FD97AA(PinePortBase, IStrategy):
    source_id = "SM_e00b375023fd97aa"
    source_file = '移动平均交叉中点策略Moving-Average-Crossover-Midpoint-Strategy.md'
    timeframe = '1h'
    can_short = True
    source_defaults = {'BPeriod': 131, 'kaydirma': 14, 'yuzdeseviyesi': 0.0006, 'len': 44, 'typeMA': 'EMA', 'smoothingLength': 53}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = True
    source_risk_flags = ['func', 'switch', 'broker_state', 'exit_order']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
