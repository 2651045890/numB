"""batch_011 port of 组合式动量与均值回归高频量化策略-Combined-Momentum-and-Mean-Reversion-High-Frequency-Quantitative-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2024-12-06 00:00:00\nend: 2025-01-04 08:00:00\nperiod: 1h\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("Momentum and Mean Reversion Strategy", shorttitle = "MMV_V1", overlay=true)\n\n// --- Inputit ja parametrit ---\nuse_momentum = input.bool(true, title="Käytä Momentum-strategiaa")\nuse_mean_reversion = input.bool(true, title="Käytä Keskiarvoon Palautumista (BB)")\n\n// Momentum-parametrit\nshort_ema_period = input.int(50, title="Lyhyt EMA")\nlong_ema_period = input.int(400, title="Pitkä EMA")\n\n// Bollinger Band -parametrit\nbb_length = input.int(20, title="BB Pituus")\nbb_std = input.float(2.0, title="BB Standardipoikkeama")\n\n// --- Momentum-strategia: EMA-risteämä ---\nshort_ema = ta.ema(close, short_ema_period)\nlong_ema = ta.ema(close, long_ema_period)\n\nmomentum_long_signal = ta.crossover(short_ema, long_ema)\nmomentum_short_signal = ta.crossunder(short_ema, long_ema)\n\n// --- Keskiarvoon palautuminen: Bollinger Bands ---\n[bb_upper, bb_middle, bb_lower] = ta.bb(close, bb_length, bb_std)\n\nbb_long_signal = ta.crossover(close, bb_lower)  // Osto, kun hinta nousee alemman BB:n yli\nbb_short_signal = ta.crossunder(close, bb_upper)  // Myynti, kun hinta laskee ylemmän BB:n ali\n\n// --- Kaupankäyntilogiikka ---\nif (use_momentum and momentum_long_signal)\n    strategy.entry("Momentum Long", strategy.long)\n\nif (use_momentum and momentum_short_signal)\n    strategy.entry("Momentum Short", strategy.short)\n\nif (use_mean_reversion and bb_long_signal)\n    strategy.entry("BB Long", strategy.long)\n\nif (use_mean_reversion and bb_short_signal)\n    strategy.entry("BB Short", strategy.short)\n\n\n\n'

class SM3FE90C487890B455(PinePortBase, IStrategy):
    source_id = "SM_3fe90c487890b455"
    source_file = '组合式动量与均值回归高频量化策略-Combined-Momentum-and-Mean-Reversion-High-Frequency-Quantitative-Strategy.md'
    timeframe = '1h'
    can_short = True
    source_defaults = {'use_momentum': True, 'use_mean_reversion': True, 'short_ema_period': 50, 'long_ema_period': 400, 'bb_length': 20, 'bb_std': 2.0}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = False
    source_risk_flags = ['tuple']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
