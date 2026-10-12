"""batch_011 port of 自适应动量马丁格尔交易系统-Adaptive-Momentum-Martingale-Trading-System.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2024-12-06 00:00:00\nend: 2025-01-04 08:00:00\nperiod: 1h\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("Adaptive Crypto Trading Strategy with Martingale", shorttitle = "ACTS_w_MG_V1",overlay=true)\n\n// Inputs\nsmoothing_length = input.int(14, title="Smoothing Length (Autoencoder)")\nmomentum_window = input.int(21, title="Momentum Window (CNN)")\nvolatility_threshold = input.float(0.02, title="Volatility Threshold (GAN Simulation)")\ntake_profit = input.float(0.05, title="Take Profit (%)")\nstop_loss = input.float(0.02, title="Stop Loss (%)")\n\n// Martingale Inputs\nbase_lot_size = input.float(1, title="Base Lot Size")  // Initial trade size\nmultiplier = input.float(2, title="Martingale Multiplier")  // Lot size multiplier after a loss\nmax_lot_size = input.float(2, title="Maximum Lot Size")  // Cap on lot size\nvar float lot_size = base_lot_size  // Initialize the lot size\n\n// Step 1: Data Smoothing (Autoencoder)\nsmoothed_price = ta.sma(close, smoothing_length)\n\n// Step 2: Feature Extraction (Momentum - CNN Simulation)\nmomentum = ta.sma(close, momentum_window) - close\nvolatility = ta.stdev(close, momentum_window)\n\n// Step 3: Entry Conditions (GAN-Inspired Pattern Detection)\nlong_condition = (momentum > 0 and volatility > volatility_threshold)\nshort_condition = (momentum < 0 and volatility > volatility_threshold)\n\n// Martingale Logic\nif (strategy.closedtrades > 0)\n    if (strategy.closedtrades.profit(strategy.closedtrades - 1) < 0)\n        lot_size := math.min(lot_size * multiplier, max_lot_size)  // Increase lot size after a loss, but cap it\n    else\n        lot_size := base_lot_size  // Reset lot size after a win or on the first trade\n\n// Step 4: Take Profit and Stop Loss Management\nlong_take_profit = close * (1 + take_profit)\nlong_stop_loss = close * (1 - stop_loss)\nshort_take_profit = close * (1 - take_profit)\nshort_stop_loss = close * (1 + stop_loss)\n\n// Execute Trades\nif (long_condition)\n    strategy.entry("Long", strategy.long, qty=lot_size, stop=long_stop_loss, limit=long_take_profit)\n\nif (short_condition)\n    strategy.entry("Short", strategy.short, qty=lot_size, stop=short_stop_loss, limit=short_take_profit)\n\n'

class SM2D2DB4FC3C688158(PinePortBase, IStrategy):
    source_id = "SM_2d2db4fc3c688158"
    source_file = '自适应动量马丁格尔交易系统-Adaptive-Momentum-Martingale-Trading-System.md'
    timeframe = '1h'
    can_short = True
    source_defaults = {'smoothing_length': 14, 'momentum_window': 21, 'volatility_threshold': 0.02, 'take_profit': 0.05, 'stop_loss': 0.02, 'base_lot_size': 1, 'multiplier': 2, 'max_lot_size': 2}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = False
    source_risk_flags = ['broker_state', 'entry_price_order', 'var_state']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
