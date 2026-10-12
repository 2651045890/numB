"""Source-faithful deep-assisted port of 斐波那契黄金和谐突破策略-Fibonacci-Golden-Harmony-Breakout-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_e5d25da0(PinePortBase, IStrategy):
    source_file = '斐波那契黄金和谐突破策略-Fibonacci-Golden-Harmony-Breakout-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.entry', 'var ']
    source_fidelity_notes = ['Uses persistent Pine state (var/varip); state is order-dependent and must be evaluated bar-by-bar, not replaced by a vectorized fill-forward approximation.']
    pine_assignments = [{'mode': '', 'name': 'Period', 'op': '=', 'expr': "input.int(10, title='Period')", 'conditions': []}, {'mode': '', 'name': 'Trendtype', 'op': '=', 'expr': 'input.string(title="Type", defval=\'Wicks\', options=[\'Wicks\', \'Body\']) == \'Wicks\'', 'conditions': []}, {'mode': '', 'name': 'Extensions', 'op': '=', 'expr': "input.string(title='Extend', defval='25', options=['25', '50', '75'])", 'conditions': []}, {'mode': '', 'name': 'LineCol1', 'op': '=', 'expr': 'input.color(color.rgb(109, 111, 111, 19), title="Line Color")', 'conditions': []}, {'mode': '', 'name': 'ShowTargets', 'op': '=', 'expr': 'input.bool(true, title="Show Targets")', 'conditions': []}, {'mode': '', 'name': 'ShowFib', 'op': '=', 'expr': 'input.bool(true, title="Show Golden Pocket")', 'conditions': []}, {'mode': '', 'name': 'gp_color_618', 'op': '=', 'expr': 'input.color(color.new(color.yellow, 0), title="0.618 Level Color")', 'conditions': []}, {'mode': '', 'name': 'gp_color_65', 'op': '=', 'expr': 'input.color(color.new(color.orange, 0), title="0.65 Level Color")', 'conditions': []}, {'mode': '', 'name': 'fast_ema', 'op': '=', 'expr': 'ta.ema(close, 9)', 'conditions': []}, {'mode': '', 'name': 'slow_ema', 'op': '=', 'expr': 'ta.ema(close, 21)', 'conditions': []}, {'mode': '', 'name': 'ema_200', 'op': '=', 'expr': 'ta.ema(close, 200)', 'conditions': []}, {'mode': '', 'name': 'hma_300', 'op': '=', 'expr': 'ta.hma(close, 300)', 'conditions': []}, {'mode': '', 'name': 'ma_18', 'op': '=', 'expr': 'ta.sma(close, 18)', 'conditions': []}, {'mode': 'var', 'name': 'low', 'op': '=', 'expr': 'na', 'conditions': []}, {'mode': 'var', 'name': 'high', 'op': '=', 'expr': 'na', 'conditions': []}, {'mode': 'var', 'name': 'fib_618', 'op': '=', 'expr': 'na', 'conditions': []}, {'mode': 'var', 'name': 'fib_65', 'op': '=', 'expr': 'na', 'conditions': []}, {'mode': '', 'name': 'low', 'op': ':=', 'expr': 'na(low) ? close : math.min(low, close)', 'conditions': ['(ta.crossover(fast_ema, slow_ema)) // Example condition to reset high and low']}, {'mode': '', 'name': 'high', 'op': ':=', 'expr': 'na(high) ? close : math.max(high, close)', 'conditions': ['(ta.crossover(fast_ema, slow_ema)) // Example condition to reset high and low']}, {'mode': '', 'name': 'low', 'op': ':=', 'expr': 'na', 'conditions': ['(ta.crossunder(fast_ema, slow_ema)) // Example condition to plot the golden pocket']}, {'mode': '', 'name': 'high', 'op': ':=', 'expr': 'na', 'conditions': ['(ta.crossunder(fast_ema, slow_ema)) // Example condition to plot the golden pocket']}, {'mode': '', 'name': 'fib_618', 'op': ':=', 'expr': 'high - (high - low) * 0.618', 'conditions': ['(ShowFib and not na(low) and not na(high))']}, {'mode': '', 'name': 'fib_65', 'op': ':=', 'expr': 'high - (high - low) * 0.65', 'conditions': ['(ShowFib and not na(low) and not na(high))']}]
    pine_user_functions = []
    pine_controls = [{'indent': 0, 'statement': 'if (ta.crossover(fast_ema, slow_ema)) // Example condition to reset high and low'}, {'indent': 0, 'statement': 'else if (ta.crossunder(fast_ema, slow_ema)) // Example condition to plot the golden pocket'}, {'indent': 0, 'statement': 'if (ShowFib and not na(low) and not na(high))'}, {'indent': 0, 'statement': 'if (ShowFib and not na(fib_618) and close > fib_618 and ta.crossover(close, fib_618))'}, {'indent': 0, 'statement': 'if (ShowFib and not na(fib_618) and close < fib_618 and ta.crossunder(close, fib_618))'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("Buy", strategy.long)', 'conditions': ['(ShowFib and not na(fib_618) and close > fib_618 and ta.crossover(close, fib_618))'], 'statement': 'strategy.entry("Buy", strategy.long)'}, {'kind': 'entry', 'call': 'strategy.entry("Sell", strategy.short)', 'conditions': ['(ShowFib and not na(fib_618) and close < fib_618 and ta.crossunder(close, fib_618))'], 'statement': 'strategy.entry("Sell", strategy.short)'}]
    original_pine = '/*backtest\nstart: 2023-05-22 00:00:00\nend: 2024-05-27 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Binance","currency":"BTC_USDT"}]\n*/\n\n// This Pine Script™ code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © spikeroy123\n\n//@version=5\nstrategy("Golden Pocket Trendline Breakout Strategy", overlay=true, max_bars_back=500, max_lines_count=500)\n\n// Core settings\nint Period = input.int(10, title=\'Period\')\nbool Trendtype = input.string(title="Type", defval=\'Wicks\', options=[\'Wicks\', \'Body\']) == \'Wicks\'\nstring Extensions = input.string(title=\'Extend\', defval=\'25\', options=[\'25\', \'50\', \'75\'])\ncolor LineCol1 = input.color(color.rgb(109, 111, 111, 19), title="Line Color")\nbool ShowTargets = input.bool(true, title="Show Targets")\n\n// Fibonacci settings\nbool ShowFib = input.bool(true, title="Show Golden Pocket")\ncolor gp_color_618 = input.color(color.new(color.yellow, 0), title="0.618 Level Color")\ncolor gp_color_65 = input.color(color.new(color.orange, 0), title="0.65 Level Color")\n\n// Calculate EMAs and HMA\nfast_ema = ta.ema(close, 9)\nslow_ema = ta.ema(close, 21)\nema_200 = ta.ema(close, 200)\nhma_300 = ta.hma(close, 300)\nma_18 = ta.sma(close, 18)\n\n// Plot EMAs and HMA\nplot(fast_ema, color=color.blue, title="Fast EMA (9)")\nplot(slow_ema, color=color.red, title="Slow EMA (21)")\nplot(ema_200, color=color.orange, title="EMA 200")\nplot(hma_300, color=color.green, title="HMA 300")\nplot(ma_18, color=color.purple, title="MA 18") // Plot 18-day moving average\n\n// Calculate and plot Golden Pocket\nvar float low = na\nvar float high = na\nvar float fib_618 = na\nvar float fib_65 = na\n\nif (ta.crossover(fast_ema, slow_ema))  // Example condition to reset high and low\n    low := na(low) ? close : math.min(low, close)\n    high := na(high) ? close : math.max(high, close)\nelse if (ta.crossunder(fast_ema, slow_ema))  // Example condition to plot the golden pocket\n    low := na\n    high := na\n\nif (ShowFib and not na(low) and not na(high))\n    fib_618 := high - (high - low) * 0.618\n    fib_65 := high - (high - low) * 0.65\n\n\nif (ShowFib and not na(fib_618) and close > fib_618 and ta.crossover(close, fib_618))\n    strategy.entry("Buy", strategy.long)\n\nif (ShowFib and not na(fib_618) and close < fib_618 and ta.crossunder(close, fib_618))\n    strategy.entry("Sell", strategy.short)'

    def pine_indicators(self, dataframe, params):
        self._semantic_rt = SemanticRuntime(dataframe, params, self.pine_assignments, self.pine_user_functions)
        return self._semantic_rt.materialize()

    def pine_context(self, dataframe, params):
        # Keep the complete, strategy-specific semantic program available to the
        # broker replay layer.  Hand-audited files replace this with compact numpy
        # arrays; assisted files intentionally retain the original expressions.
        return {'dataframe': dataframe, 'params': dict(params), 'orders': self.pine_orders,
                'assignments': self.pine_assignments, 'functions': self.pine_user_functions,
                'source': self.original_pine}

    def pine_script(self, broker, i, ctx):
        # The order program is preserved explicitly above.  Stateful Pine programs
        # (var/arrays/security/broker-state reads) require the chain verifier/runtime
        # replay to execute their exact bar-by-bar semantics.  This method does not
        # fabricate orders when an expression cannot be proven equivalent.
        replay = getattr(broker, 'replay_source_program', None)
        if replay is not None:
            return replay(self.original_pine, i, ctx)
        return None
