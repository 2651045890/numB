"""batch_011 port of 趋势跟踪与动量结合的双指标交易策略-Dual-Indicator-Trading-Strategy-Combining-Trend-Following-and-Momentum.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2019-12-23 08:00:00\nend: 2024-09-24 08:00:00\nperiod: 1d\nbasePeriod: 1d\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("NNFX Trendilo + Zero MACD Strategy", overlay=true)\n\n// --- Inputs ---\natrPeriod = input.int(14, title="ATR Period")\nstopLossMultiplier = input.float(1.5, minval=0.0, maxval = 20.0, step = 0.1 ,title="Stop Loss Multiplier")\ntakeProfitMultiplier = input.float(2.0, minval=0.0 , maxval = 20.0, step = 0.1,title="Take Profit Multiplier")\n\n// --- Trendilo ---\ntrendiloPeriod = input.int(50, title="Trendilo Period")\ntrendilo = ta.sma(close, trendiloPeriod)\n\n// --- MACD ---\n[macdLine, signalLine, _] = ta.macd(close, 12, 26, 9)\nmacdZeroCrossUp = ta.crossover(macdLine, 0)\nmacdZeroCrossDown = ta.crossunder(macdLine, 0)\n\n// --- ATR for Stop Loss and Take Profit ---\natr = ta.atr(atrPeriod)\nstopLoss = atr * stopLossMultiplier\ntakeProfit = atr * takeProfitMultiplier\n\n// --- Trading Logic ---\nlongCondition = macdZeroCrossUp and close > trendilo\nshortCondition = macdZeroCrossDown and close < trendilo\n\n// --- Execute Long Trades ---\nif (longCondition)\n    strategy.entry("Buy", strategy.long)\n    strategy.exit("Take Profit/Stop Loss", "Buy", limit=close + takeProfit, stop=close - stopLoss)\n\n// --- Execute Short Trades ---\nif (shortCondition)\n    strategy.entry("Sell", strategy.short)\n    strategy.exit("Take Profit/Stop Loss", "Sell", limit=close - takeProfit, stop=close + stopLoss)\n\n// --- Plot Signals ---\nplotshape(series=longCondition, location=location.belowbar, color=color.green, style=shape.labelup, text="Buy")\nplotshape(series=shortCondition, location=location.abovebar, color=color.red, style=shape.labeldown, text="Sell")\n\n// --- Plot Trendilo ---\nplot(trendilo, color=color.blue, linewidth=2)\n'

class SMA0094D33B79ACCFC(PinePortBase, IStrategy):
    source_id = "SM_a0094d33b79accfc"
    source_file = '趋势跟踪与动量结合的双指标交易策略-Dual-Indicator-Trading-Strategy-Combining-Trend-Following-and-Momentum.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'atrPeriod': 14, 'stopLossMultiplier': 1.5, 'takeProfitMultiplier': 2.0, 'trendiloPeriod': 50}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = True
    source_risk_flags = ['tuple', 'exit_order']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
