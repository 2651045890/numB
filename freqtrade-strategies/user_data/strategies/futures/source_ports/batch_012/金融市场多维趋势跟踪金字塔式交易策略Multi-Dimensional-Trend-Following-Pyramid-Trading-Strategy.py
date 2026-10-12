"""batch_012 port of 金融市场多维趋势跟踪金字塔式交易策略Multi-Dimensional-Trend-Following-Pyramid-Trading-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2025-01-02 00:00:00\nend: 2025-01-09 00:00:00\nperiod: 30m\nbasePeriod: 30m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT","balance":49999}]\n*/\n\n//@version=6\nstrategy("Markttechnik Strategie mit Pyramiding und Drawdown-Limit", overlay=true, pyramiding=2)\n\n// Eingabewerte\nlengthSupport = input.int(3, title="Unterstützungs-/Widerstandsfenster", minval=1)\nlengthSMA = input.int(10, title="SMA Länge für Trends", minval=1)\nriskRewardRatio = input.float(2.0, title="Risk-Reward-Ratio", minval=0.1, step=0.1)\nmaxDrawdown = input.float(5.0, title="Maximaler Drawdown (%)", minval=0.1, step=0.1)\n\n// Unterstützungs- und Widerstandszonen berechnen\nsupport = ta.lowest(low, lengthSupport)\nresistance = ta.highest(high, lengthSupport)\n\n// Trendindikator (SMA-basierter Trend)\nsma = ta.sma(close, lengthSMA)\ntrendUp = close > sma\ntrendDown = close < sma\n\n// Umkehrstäbe erkennen\nisHammer = close > open and (low < open) and ((open - low) > 2 * (close - open))\nisShootingStar = open > close and (high > open) and ((high - open) > 2 * (open - close))\n\n// Kauf- und Verkaufssignale\nbuySignal = isHammer and close > support and trendUp\nsellSignal = isShootingStar and close < resistance and trendDown\n\n// Strategiefunktionen: Pyramiding und Drawdown\nequityPeak = na(strategy.equity[1]) or strategy.equity > strategy.equity[1] ? strategy.equity : strategy.equity[1]  // Höchster Kontostand\ndrawdown = equityPeak > 0 ? (strategy.equity - equityPeak) / equityPeak * 100 : 0  // Drawdown in Prozent\n\nif buySignal and drawdown > -maxDrawdown\n    strategy.entry("Buy", strategy.long)\n    strategy.exit("Sell", "Buy", stop=low - (high - low) * riskRewardRatio, limit=close + (close - low) * riskRewardRatio)\n\nif sellSignal and drawdown > -maxDrawdown\n    strategy.entry("Sell", strategy.short)\n    strategy.exit("Cover", "Sell", stop=high + (high - low) * riskRewardRatio, limit=close - (high - close) * riskRewardRatio)\n\n// Unterstützungs- und Widerstandslinien zeichnen\nplot(support, color=color.new(color.green, 80), linewidth=1, title="Unterstützungszone")\nplot(resistance, color=color.new(color.red, 80), linewidth=1, title="Widerstandszone")\n\n// Trendlinie (SMA)\nplot(sma, color=color.blue, linewidth=2, title="SMA-Trend")\n\n// Umkehrstäbe hervorheben\nbgcolor(buySignal ? color.new(color.green, 90) : na, title="Kaufsignal Hintergrund")\nbgcolor(sellSignal ? color.new(color.red, 90) : na, title="Verkaufssignal Hintergrund")\n\n// Debugging: Drawdown anzeigen\nplot(drawdown, title="Drawdown (%)", color=color.purple, linewidth=2, style=plot.style_line)\n\n'

class SMMultiDimensionalTrendFollowingPyramidTradingStrategy809e04(PinePortBase, IStrategy):
    source_id = "SM_809e04ed29ccfa4c"
    source_file = '金融市场多维趋势跟踪金字塔式交易策略Multi-Dimensional-Trend-Following-Pyramid-Trading-Strategy.md'
    timeframe = '30m'
    can_short = True
    source_defaults = {'lengthSupport': 3, 'lengthSMA': 10, 'riskRewardRatio': 2.0, 'maxDrawdown': 5.0}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 2
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
