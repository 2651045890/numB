"""batch_012 port of 零延迟趋势动量指标交易策略-Zero-Lag-Trend-Momentum-Indicator-Trading-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2024-11-14 00:00:00\nend: 2025-02-19 08:00:00\nperiod: 1d\nbasePeriod: 1d\nexchanges: [{"eid":"Binance","currency":"DOGE_USDT"}]\n*/\n\n// This Pine Script™ code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © josephdelvecchio\n\n//@version=6\nstrategy("Zero Lag Trend Strategy", overlay=true)\n\n// -- Input Parameters --\ntimeframe = input.timeframe("10", "Timeframe")\nzeroLagMovAvg = input.string("ema", "Zero Lag Moving Average", options=["ema", "sma"])\nlength = input.int(50, "Lookback Period")\nvolatility_mult = input.float(1.5, "Volatility Multiplier")\nloop_start = input.int(1, "Loop Start")\nloop_end = input.int(50, "Loop End")\nthreshold_up = input.int(5, "Threshold Up")\nthreshold_down = input.int(-5, "Threshold Down")\nsignalpct = input.float(8, "Signal Percentage")\nstoppct = input.float(0, "Stop Percentage")\n\n// -- Helper Variables --\nnATR = ta.atr(length)\nlag = math.floor((length - 1) / 2)\nzl_basis = zeroLagMovAvg == "ema" ? ta.ema(2 * close - close[lag], length) : ta.sma(2 * close - close[lag], length)\nvolatility = ta.highest(nATR, length * 3) * volatility_mult\n\n// -- Trend Strength Scoring Function --\nforloop_analysis(basis_price, loop_start, loop_end) =>\n    int sum = 0 // Use \'sum\' as you did originally, for the +/- logic\n    for i = loop_start to loop_end\n        if basis_price > basis_price[i]\n            sum += 1\n        else if basis_price < basis_price[i] // Explicitly check for less than\n            sum -= 1\n        // If they are equal, do nothing (sum remains unchanged)\n    sum\n\nscore = forloop_analysis(zl_basis, loop_start, loop_end)\n\n// -- Signal Generation --\nlong_signal = score > threshold_up and close > zl_basis + volatility\nshort_signal = score < threshold_down and close < zl_basis - volatility\n\n// -- Trend Detection (Ensure One Trade Until Reversal) --\nvar int trend = na\ntrend := long_signal ? 1 : short_signal ? -1 : trend[1]\ntrend_changed = trend != trend[1]\n\n// -- Stop-Loss & Take-Profit --\nstop_loss = close * (1 - stoppct / 100)\ntake_profit = close * (1 + signalpct / 100)\n\n// -- Strategy Orders (Enter Only When Trend Changes) --\n\nif long_signal\n    strategy.entry("Long", strategy.long)\nelse if short_signal\n    strategy.entry("Short", strategy.short)\n\n// -- Strategy Exits --\nstrategy.exit("Exit Long", from_entry="Long", stop=stop_loss, limit=take_profit)\nstrategy.exit("Exit Short", from_entry="Short", stop=take_profit, limit=stop_loss)\n\n// -- Visualization --\np_basis = zl_basis\nplot(p_basis, title="Zero Lag Line", color=color.blue, linewidth=2)\n\n// -- Buy/Sell Arrows --\nplotshape(series=trend_changed and trend == 1, location=location.belowbar, color=color.green, style=shape.triangleup, size=size.large, title="Buy Signal")\nplotshape(series=trend_changed and trend == -1, location=location.abovebar, color=color.red, style=shape.triangledown, size=size.large, title="Sell Signal")\n\n'

class SMZeroLagTrendMomentumIndicatorTradingStrategyfbb85a(PinePortBase, IStrategy):
    source_id = "SM_fbb85ae0d288cc2c"
    source_file = '零延迟趋势动量指标交易策略-Zero-Lag-Trend-Momentum-Indicator-Trading-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'timeframe': '10', 'zeroLagMovAvg': 'ema', 'length': 50, 'volatility_mult': 1.5, 'loop_start': 1, 'loop_end': 50, 'threshold_up': 5, 'threshold_down': -5, 'signalpct': 8, 'stoppct': 0}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_reproduce_stops = True
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_012 md and exposed through the same PinePortBase interface used by batch_001.', 'Custom Pine function(s) are present; the original source is embedded verbatim and this generic pass flags them for per-strategy semantic verification.', 'Loop/switch logic is present and requires per-strategy semantic verification against TradingView/FMZ before treating results as parity-certified.']

    def pine_indicators(self, dataframe, params):
        # Runtime evaluates the source against the complete OHLCV frame.
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch012Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
