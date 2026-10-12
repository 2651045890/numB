"""batch_011 port of 自适应趋势跟踪与动态止盈的多重技术指标组合策略-Adaptive-Trend-Following-Strategy-with-Dynamic-Take-Profit-Using-Multiple-Technical-Indicators.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2024-02-10 00:00:00\nend: 2025-02-08 08:00:00\nperiod: 1h\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("BTC 15分钟动态止盈策略", overlay=true)\n\n// === 参数设置 ===\n// EMA 参数\nema_short_length = input.int(50, title="短期EMA长度", minval=1)\nema_long_length = input.int(200, title="长期EMA长度", minval=1)\n\n// MACD 参数\nmacd_fast_length = input.int(12, title="MACD快速线长度", minval=1)\nmacd_slow_length = input.int(26, title="MACD慢速线长度", minval=1)\nmacd_signal_length = input.int(9, title="MACD信号线长度", minval=1)\n\n// RSI 参数\nrsi_length = input.int(14, title="RSI长度", minval=1)\nrsi_overbought = input.int(70, title="RSI超买区", minval=1, maxval=100)\nrsi_oversold = input.int(30, title="RSI超卖区", minval=1, maxval=100)\n\n// 止损参数\nstop_loss_pct = input.float(1.5, title="止损百分比", minval=0.1)\n\n// === 指标计算 ===\n// 均线\nema_short = ta.ema(close, ema_short_length)\nema_long = ta.ema(close, ema_long_length)\n\n// MACD\n[macd_line, signal_line, _] = ta.macd(close, macd_fast_length, macd_slow_length, macd_signal_length)\n\n// RSI\nrsi = ta.rsi(close, rsi_length)\n\n// === 趋势过滤 ===\nbullish_trend = ema_short > ema_long  // 多头趋势：短期均线高于长期均线\nbearish_trend = ema_short < ema_long  // 空头趋势：短期均线低于长期均线\n\n// === 买入条件 ===\n// 1. EMA 显示多头趋势\n// 2. MACD 金叉（MACD 线向上突破信号线）\n// 3. RSI 不在超买区域\nbuy_signal = bullish_trend and ta.crossover(macd_line, signal_line) and rsi < rsi_overbought\n\n// === 危险信号（动态止盈条件） ===\n// 1. 趋势反转：短期均线跌破长期均线，或者价格跌破短期均线\n// 2. MACD 死叉：MACD 线向下跌破信号线\n// 3. RSI：RSI 超买并开始回落\ndanger_signal = bearish_trend or close < ema_short or ta.crossunder(macd_line, signal_line) or (rsi > rsi_overbought and ta.falling(rsi, 2))  // 检查 RSI 最近2周期是否下降\n\n// === 策略执行 ===\nif (buy_signal)\n    strategy.entry("Buy", strategy.long)\n\n// 动态止盈和止损\nif (strategy.position_size > 0)\n    stop_price = strategy.position_avg_price * (1 - stop_loss_pct / 100)  // 固定止损\n    strategy.exit("Exit", from_entry="Buy", stop=stop_price, when=danger_signal)\n\n// === 绘制图表 ===\n// EMA 绘制\nplot(ema_short, color=color.blue, title="短期EMA")\nplot(ema_long, color=color.orange, title="长期EMA")\n\n// MACD 绘制\nplot(macd_line, color=color.green, title="MACD线")\nplot(signal_line, color=color.red, title="信号线")\n\n// RSI 超买/超卖区域\nhline(rsi_overbought, "RSI超买区", color=color.red, linestyle=hline.style_dotted)\nhline(rsi_oversold, "RSI超卖区", color=color.green, linestyle=hline.style_dotted)\n\n// 背景颜色：显示趋势\nbgcolor(bullish_trend ? color.new(color.green, 90) : color.new(color.red, 90), title="趋势背景")'

class SM31E3CD3E79855598(PinePortBase, IStrategy):
    source_id = "SM_31e3cd3e79855598"
    source_file = '自适应趋势跟踪与动态止盈的多重技术指标组合策略-Adaptive-Trend-Following-Strategy-with-Dynamic-Take-Profit-Using-Multiple-Technical-Indicators.md'
    timeframe = '1h'
    can_short = False
    source_defaults = {'ema_short_length': 50, 'ema_long_length': 200, 'macd_fast_length': 12, 'macd_slow_length': 26, 'macd_signal_length': 9, 'rsi_length': 14, 'rsi_overbought': 70, 'rsi_oversold': 30, 'stop_loss_pct': 1.5}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = True
    source_risk_flags = ['broker_state', 'tuple', 'exit_order']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
