"""batch_012 port of 长期趋势与波动率识别相结合的指数移动均线超级趋势量化交易策略-Long-term-Trend-and-Volatility-Recognition-Combined-Exponential-Moving-Average-SuperTrend-Quantitative-Trading-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2025-01-01 00:00:00\nend: 2025-03-23 00:00:00\nperiod: 3h\nbasePeriod: 3h\nexchanges: [{"eid":"Futures_Binance","currency":"BNB_USDT"}]\n*/\n\n//@version=6\nstrategy("Moving Average + SuperTrend Strategy", overlay=true)\n\n// === Indicator Settings ===\nma_length = input.int(200, title="Moving Average Length")\nfactor = input.float(3.0, title="SuperTrend Factor")\nperiod = input.int(14, title="SuperTrend Period")\n\n// === Calculate Moving Average (MA 400) ===\nma_400 = ta.sma(close, ma_length)\n\n// === Calculate SuperTrend ===\nsrc = close\nhl = math.avg(high, low)\natr = ta.atr(period)\n\nup = hl - factor * atr\ndn = hl + factor * atr\n\ntrendUp = 0.0\ntrendDown = 0.0\ntrend = 0\n\ntrendUp := close[1] > trendUp[1] ? math.max(up, trendUp[1]) : up\ntrendDown := close[1] < trendDown[1] ? math.min(dn, trendDown[1]) : dn\ntrend := close > trendDown[1] ? 1 : close < trendUp[1] ? -1 : nz(trend[1], 1)\n\nsuperTrend = trend == 1 ? trendUp : trendDown\n\n// === Entry and Exit Conditions ===\nlongCondition = close > ma_400 and trend == 1\nshortCondition = close < ma_400 and trend == -1\n\n// === Execute Trades ===\nif (longCondition)\n    strategy.entry("Buy", strategy.long)\n\nif (shortCondition)\n    strategy.entry("Sell", strategy.short)\n\n// === Exit Trades ===\nif (strategy.position_size > 0 and trend == -1)\n    strategy.close("Buy")\n\nif (strategy.position_size < 0 and trend == 1)\n    strategy.close("Sell")\n\n// === Plot Indicators on the Chart ===\nplot(ma_400, color=color.blue, linewidth=2, title="MA 400")\nplot(superTrend, color=trend == 1 ? color.green : color.red, linewidth=2, title="SuperTrend")\n\n'

class SMLongtermTrendandVolatilityRecognitionCombinedExponentia4a3867(PinePortBase, IStrategy):
    source_id = "SM_4a386783184af604"
    source_file = '长期趋势与波动率识别相结合的指数移动均线超级趋势量化交易策略-Long-term-Trend-and-Volatility-Recognition-Combined-Exponential-Moving-Average-SuperTrend-Quantitative-Trading-Strategy.md'
    timeframe = '3h'
    can_short = True
    source_defaults = {'ma_length': 200, 'factor': 3.0, 'period': 14}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
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
