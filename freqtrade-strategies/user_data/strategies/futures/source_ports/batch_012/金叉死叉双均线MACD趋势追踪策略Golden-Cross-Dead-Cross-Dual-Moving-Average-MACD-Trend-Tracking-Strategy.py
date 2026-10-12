"""batch_012 port of 金叉死叉双均线MACD趋势追踪策略Golden-Cross-Dead-Cross-Dual-Moving-Average-MACD-Trend-Tracking-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-12-14 00:00:00\nend: 2023-12-21 00:00:00\nperiod: 15m\nbasePeriod: 5m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=2\nstrategy(\'The Puria Method\', shorttitle = \'Puria\',overlay = true)\n\n//=== GENERAL INPUTS ===\n\n// short ma\nmaFastSource   = input(defval = close, title = "Fast MA Source")\nmaFastLength   = input(defval = 5, title = "Fast MA Period", minval = 1)\n\n// long ma 1\nmaSlow1Source   = input(defval = low, title = "Slow MA1 Source")\nmaSlow1Length   = input(defval = 85, title = "Slow MA Period", minval = 1)\n\n// long ma 2\nmaSlow2Source   = input(defval = low, title = "Slow MA2 Source")\nmaSlow2Length   = input(defval = 75, title = "Slow MA Period", minval = 1)\n\n//macd\nmacdFastLength   = input(defval = 12, title = "Fast MACD Period", minval = 1)\nmacdSlowLength   = input(defval = 26, title = "Slow MACD Period", minval = 1)\nmacdSmaLength   = input(defval = 9, title = "SMA MACD Period", minval = 1)\n\n// the risk management inputs\ninpTakeProfit   = input(defval = 30, title = "Take Profit", minval = 0)\ninpStopLoss     = input(defval = 10, title = "Stop Loss", minval = 0)\ninpTrailStop    = input(defval = 5, title = "Trailing Stop Loss", minval = 0)\ninpTrailOffset  = input(defval = 0, title = "Trailing Stop Loss Offset", minval = 0)\n\n// if an input is less than 1, assuming not wanted so we assign \'na\' value to disable it.\nuseTakeProfit   = inpTakeProfit  >= 1 ? inpTakeProfit  : na\nuseStopLoss     = inpStopLoss    >= 1 ? inpStopLoss    : na\nuseTrailStop    = inpTrailStop   >= 1 ? inpTrailStop   : na\nuseTrailOffset  = inpTrailOffset >= 1 ? inpTrailOffset : na\n\n// === SERIES SETUP ===\nmaFast = ema(maFastSource, maFastLength)\nmaSlow1 = wma(maSlow1Source, maSlow1Length)\nmaSlow2 = wma(maSlow2Source, maSlow2Length)\n[_, signal, histLine] = macd(close, macdFastLength, macdSlowLength, macdSmaLength)\n\n// === PLOTTING ===\nfast = plot(maFast, title = "Fast MA", color = green, linewidth = 2, style = line, transp = 50)\nslow1 = plot(maSlow1, title = "Slow MA1", color = red, linewidth = 2, style = line, transp = 50)\nslow2 = plot(maSlow2, title = "Slow MA2", color = red, linewidth = 2, style = line, transp = 50)\n\n// === LOGIC ===\nsignalUp = crossover(maFast, maSlow1) and crossover(maFast, maSlow2) and histLine > 0\nsignalDown = crossunder(maFast, maSlow1) and crossunder(maFast, maSlow2) and histLine < 0\n\n// ===STRATEGY===\nstrategy.entry(id = "Long", long = true, when = signalUp) \nstrategy.entry(id = "Short", long = false, when = signalDown)\nstrategy.exit("Exit Long", from_entry = "Long", profit = useTakeProfit, loss = useStopLoss, trail_points = useTrailStop, trail_offset = useTrailOffset)\nstrategy.exit("Exit Short", from_entry = "Short", profit = useTakeProfit, loss = useStopLoss, trail_points = useTrailStop, trail_offset = useTrailOffset)\n'

class SMMACDGoldenCrossDeadCrossDualMovingAverageMACDTrendTrackd6bce2(PinePortBase, IStrategy):
    source_id = "SM_d6bce2272834d46f"
    source_file = '金叉死叉双均线MACD趋势追踪策略Golden-Cross-Dead-Cross-Dual-Moving-Average-MACD-Trend-Tracking-Strategy.md'
    timeframe = '15m'
    can_short = False
    source_defaults = {'maFastSource': 'close', 'maFastLength': 5, 'maSlow1Source': 'low', 'maSlow1Length': 85, 'maSlow2Source': 'low', 'maSlow2Length': 75, 'macdFastLength': 12, 'macdSlowLength': 26, 'macdSmaLength': 9, 'inpTakeProfit': 30, 'inpStopLoss': 10, 'inpTrailStop': 5, 'inpTrailOffset': 0}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_reproduce_stops = True
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_012 md and exposed through the same PinePortBase interface used by batch_001.']

    def pine_indicators(self, dataframe, params):
        # Runtime evaluates the source against the complete OHLCV frame.
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch012Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
