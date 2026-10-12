"""Source-faithful deep-assisted port of 指数均线交叉策略Exponential-Moving-Average-Crossover-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_4cd2fa11(PinePortBase, IStrategy):
    source_file = '指数均线交叉策略Exponential-Moving-Average-Crossover-Strategy.md'
    timeframe = '1h'
    can_short = True
    source_defaults = {'fib_level': 0.5}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.exit', 'strategy.entry', 'var ']
    source_fidelity_notes = ['Uses persistent Pine state (var/varip); state is order-dependent and must be evaluated bar-by-bar, not replaced by a vectorized fill-forward approximation.', 'Uses strategy.exit; stop/limit/profit/loss/trailing arguments have Pine order semantics and may fill intrabar.']
    pine_assignments = [{'mode': '', 'name': 'fib_level', 'op': '=', 'expr': 'input(0.5, title="Fibonacci Level")', 'conditions': []}, {'mode': '', 'name': 'fib_price', 'op': '=', 'expr': 'ta.lowest(low, 100) + (ta.highest(high, 100) - ta.lowest(low, 100)) * fib_level', 'conditions': []}, {'mode': '', 'name': 'long_condition', 'op': '=', 'expr': 'ta.crossover(close, fib_price)', 'conditions': []}, {'mode': '', 'name': 'short_condition', 'op': '=', 'expr': 'ta.crossunder(close, fib_price)', 'conditions': []}, {'mode': '', 'name': 'long_exit', 'op': '=', 'expr': 'ta.highest(high, 10)', 'conditions': []}, {'mode': '', 'name': 'short_exit', 'op': '=', 'expr': 'ta.lowest(low, 10)', 'conditions': []}, {'mode': 'var', 'name': 'inLong', 'op': '=', 'expr': 'false', 'conditions': []}, {'mode': 'var', 'name': 'inShort', 'op': '=', 'expr': 'false', 'conditions': []}, {'mode': '', 'name': 'inLong', 'op': ':=', 'expr': 'true', 'conditions': ['(long_condition)', 'not inLong']}, {'mode': '', 'name': 'inShort', 'op': ':=', 'expr': 'true', 'conditions': ['(short_condition)', 'not inShort']}, {'mode': '', 'name': 'inLong', 'op': ':=', 'expr': 'false', 'conditions': ['(ta.crossover(close, long_exit) or ta.crossunder(close, short_exit))']}, {'mode': '', 'name': 'inShort', 'op': ':=', 'expr': 'false', 'conditions': ['(ta.crossover(close, long_exit) or ta.crossunder(close, short_exit))']}]
    pine_user_functions = []
    pine_controls = [{'indent': 0, 'statement': 'if (long_condition)'}, {'indent': 4, 'statement': 'if not inLong'}, {'indent': 0, 'statement': 'if (short_condition)'}, {'indent': 4, 'statement': 'if not inShort'}, {'indent': 0, 'statement': 'if (ta.crossover(close, long_exit) or ta.crossunder(close, short_exit))'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("Buy", strategy.long)', 'conditions': ['(long_condition)', 'not inLong'], 'statement': 'strategy.entry("Buy", strategy.long)'}, {'kind': 'exit', 'call': 'strategy.exit("Exit", "Buy", limit=long_exit)', 'conditions': ['(long_condition)'], 'statement': 'strategy.exit("Exit", "Buy", limit=long_exit)'}, {'kind': 'entry', 'call': 'strategy.entry("Sell", strategy.short)', 'conditions': ['(short_condition)', 'not inShort'], 'statement': 'strategy.entry("Sell", strategy.short)'}, {'kind': 'exit', 'call': 'strategy.exit("Exit", "Sell", limit=short_exit)', 'conditions': ['(short_condition)'], 'statement': 'strategy.exit("Exit", "Sell", limit=short_exit)'}]
    original_pine = '/*backtest\nstart: 2023-12-08 00:00:00\nend: 2024-01-07 00:00:00\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("Fibonacci Strategy", overlay=true)\n\n// Define Fibonacci 0.5 level\nfib_level = input(0.5, title="Fibonacci Level")\n\n// Calculate Fibonacci 0.5 level price\nfib_price = ta.lowest(low, 100) + (ta.highest(high, 100) - ta.lowest(low, 100)) * fib_level\n\n// Define entry and exit conditions\nlong_condition = ta.crossover(close, fib_price)\nshort_condition = ta.crossunder(close, fib_price)\n\n// Set exit points (using previous high or low)\nlong_exit = ta.highest(high, 10)\nshort_exit = ta.lowest(low, 10)\n\n// Plot Fibonacci 0.5 level\nplot(fib_price, "Fib 0.5", color=color.blue, linewidth=1, style=plot.style_circles)\n\n// Initialize variables\nvar inLong = false\nvar inShort = false\n\n// Set trading signals\nif (long_condition)\n    if not inLong\n        strategy.entry("Buy", strategy.long)\n        inLong := true\n    strategy.exit("Exit", "Buy", limit=long_exit)\n\nif (short_condition)\n    if not inShort\n        strategy.entry("Sell", strategy.short)\n        inShort := true\n    strategy.exit("Exit", "Sell", limit=short_exit)\n\nif (ta.crossover(close, long_exit) or ta.crossunder(close, short_exit))\n    inLong := false\n    inShort := false'

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
