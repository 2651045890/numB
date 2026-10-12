"""batch_011 port of 移动平均与动量蜡烛趋势跟踪系统-Moving-Average-and-Momentum-Candle-Trend-Following-System.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2024-04-16 00:00:00\nend: 2025-04-15 00:00:00\nperiod: 1d\nbasePeriod: 1d\nexchanges: [{"eid":"Futures_Binance","currency":"TRX_USD"}]\n*/\n\n//@version=5\nstrategy("MA200 + Momentum Candle Strategy (No Duplicate Entry)", overlay=true, default_qty_type=strategy.percent_of_equity, default_qty_value=10)\n\n// === Input\nmaLength = input.int(200, title="MA Period")\nshowSignals = input.bool(true, title="Tampilkan Sinyal")\nuseSLTP = input.bool(true, title="Gunakan SL/TP?")\nslPips = input.int(50, title="Stop Loss (pips)")\ntpPips = input.int(100, title="Take Profit (pips)")\n\n// === Perhitungan MA dan candle body\nma200 = ta.sma(close, maLength)\nprevBody = math.abs(close[1] - open[1])\ncurrBody = math.abs(close - open)\n\n// === Momentum candle logic\nisBullishMomentum = close > open and currBody > prevBody\nisBearishMomentum = close < open and currBody > prevBody\n\n// === Syarat entry\nisBuySignal = close > ma200 and isBullishMomentum\nisSellSignal = close < ma200 and isBearishMomentum\n\n// === SL/TP\npipSize = syminfo.mintick * 10\nsl = slPips * pipSize\ntp = tpPips * pipSize\n\n// === Cek apakah ada posisi terbuka\nnoOpenTrade = strategy.opentrades == 0\n\n// === Eksekusi entry jika belum ada posisi terbuka\nif isBuySignal and noOpenTrade\n    strategy.entry("Buy", strategy.long)\n    if useSLTP\n        strategy.exit("Exit Buy", from_entry="Buy", stop=close - sl, limit=close + tp)\n\nif isSellSignal and noOpenTrade\n    strategy.entry("Sell", strategy.short)\n    if useSLTP\n        strategy.exit("Exit Sell", from_entry="Sell", stop=close + sl, limit=close - tp)\n\n// === Plot MA dan sinyal visual\nplot(ma200, color=color.orange, title="MA 200")\n\nplotshape(showSignals and isBuySignal and noOpenTrade, title="Buy Signal", location=location.belowbar, color=color.green, style=shape.labelup, text="Buy")\nplotshape(showSignals and isSellSignal and noOpenTrade, title="Sell Signal", location=location.abovebar, color=color.red, style=shape.labeldown, text="Sell")\n'

class SM991A7B3D1A3F565C(PinePortBase, IStrategy):
    source_id = "SM_991a7b3d1a3f565c"
    source_file = '移动平均与动量蜡烛趋势跟踪系统-Moving-Average-and-Momentum-Candle-Trend-Following-System.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'maLength': 200, 'showSignals': True, 'useSLTP': True, 'slPips': 50, 'tpPips': 100}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 10
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = True
    source_risk_flags = ['broker_state', 'exit_order']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
