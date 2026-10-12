"""batch_011 port of 自适应趋势跟踪与动态风控策略-Adaptive-Trend-Following-with-Dynamic-Risk-Control-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2024-02-20 00:00:00\nend: 2025-02-17 08:00:00\nperiod: 1h\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=6\nstrategy("妮可百分百", overlay=true)\n\n// ? 設定 Parabolic SAR 參數\nstart = input.float(0.02, "起始 AF")\nincrement = input.float(0.02, "加速因子")\nmaximum = input.float(0.2, "最大 AF")\n\n// ? 計算 Parabolic SAR\nSAR = ta.sar(start, increment, maximum)\n\n// ? ATR 計算（用於動態止損）\natrLength = input.int(14, "ATR 計算週期")\natrMultiplier = input.float(1.3, "ATR 係數")  // 2倍 ATR 作為止損範圍\nATR = ta.atr(atrLength)\n\n// ? 固定 0.5% 止盈計算\ntakeProfitPercent = 0.007  // 0.7% 固定止盈\ntakeProfitLong = close * (1 + takeProfitPercent)  // 多單止盈\ntakeProfitShort = close * (1 - takeProfitPercent) // 空單止盈\n\n// ? **50 EMA 過濾**\nema50 = ta.ema(close, 50)\n\n// ? **RSI 過濾（防止震盪進場）**\nrsiLength = input.int(14, "RSI 週期")\nrsi = ta.rsi(close, rsiLength)\nlongFilter = rsi > 40  // 只在 RSI > 31 時做多\nshortFilter = rsi < 60 // 只在 RSI < 69 時做空\n\n// ? **檢查是否已經有持倉**\nisFlat = strategy.position_size == 0  // **無持倉時，才能開新單**\n\n// ? **多頭進場條件**\nlongCondition = ta.crossover(close, SAR) and close > ema50 and longFilter and isFlat  \n\n// ? **空頭進場條件**\nshortCondition = ta.crossunder(close, SAR) and close < ema50 and shortFilter and isFlat  \n\n// ? **進場策略**\nif (longCondition)\n    strategy.entry("B", strategy.long, comment="B")\n\nif (shortCondition)\n    strategy.entry("S", strategy.short, comment="S")\n\n// ? **止盈 & 止損**\nstopLossLong = close - (ATR * atrMultiplier)  // 多單 ATR 止損\nstopLossShort = close + (ATR * atrMultiplier) // 空單 ATR 止損\n\nstrategy.exit("Exit Long", from_entry="B", stop=stopLossLong, limit=takeProfitLong, comment="TP Long")\nstrategy.exit("Exit Short", from_entry="S", stop=stopLossShort, limit=takeProfitShort, comment="TP Short")\n\n// ? **標記進出場點**\nplotshape(series=longCondition, location=location.belowbar, style=shape.triangleup, size=size.small, title="B")\nplotshape(series=shortCondition, location=location.abovebar, style=shape.triangledown, size=size.small, title="S")\n\n// ? **繪製 50 EMA**\nplot(ema50, color=color.blue, title="50 EMA")\n'

class SM86977C52F646DBB0(PinePortBase, IStrategy):
    source_id = "SM_86977c52f646dbb0"
    source_file = '自适应趋势跟踪与动态风控策略-Adaptive-Trend-Following-with-Dynamic-Risk-Control-Strategy.md'
    timeframe = '1h'
    can_short = True
    source_defaults = {'start': 0.02, 'increment': 0.02, 'maximum': 0.2, 'atrLength': 14, 'atrMultiplier': 1.3, 'rsiLength': 14}
    source_qty_type = 'fixed'
    source_qty_value = 1
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
