"""Source-faithful deep-assisted port of 波浪买卖反转5分钟时间框架策略Wave-Buying-and-Selling-Reversal-5-Minutes-Timeframe-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_1d45ceb3(PinePortBase, IStrategy):
    source_file = '波浪买卖反转5分钟时间框架策略Wave-Buying-and-Selling-Reversal-5-Minutes-Timeframe-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.entry', 'strategy.close', 'strategy.position_size']
    source_fidelity_notes = ['Reads broker/strategy state; signals depend on fill timing and cannot be reduced to indicator-only booleans without changing behavior.']
    pine_assignments = []
    pine_user_functions = []
    pine_controls = [{'indent': 0, 'statement': 'if (close - open) < -5'}, {'indent': 0, 'statement': 'if strategy.position_size > 0'}, {'indent': 0, 'statement': 'if close * 1.01 <= strategy.position_avg_price'}, {'indent': 0, 'statement': 'if close * 0.98 >= strategy.position_avg_price'}, {'indent': 0, 'statement': 'if strategy.position_size < 0'}, {'indent': 0, 'statement': 'if close * 0.99 >= strategy.position_avg_price'}, {'indent': 0, 'statement': 'if close * 1.02 <= strategy.position_avg_price'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("Long", strategy.long)', 'conditions': ['(close - open) < -5'], 'statement': 'strategy.entry("Long", strategy.long)'}, {'kind': 'entry', 'call': 'strategy.entry("Short1", strategy.short, qty=2, limit=close * 1.01)', 'conditions': ['strategy.position_size > 0'], 'statement': 'strategy.entry("Short1", strategy.short, qty=2, limit=close * 1.01)'}, {'kind': 'entry', 'call': 'strategy.entry("Short2", strategy.short, qty=2, limit=close * 1.01)', 'conditions': ['strategy.position_size > 0'], 'statement': 'strategy.entry("Short2", strategy.short, qty=2, limit=close * 1.01)'}, {'kind': 'entry', 'call': 'strategy.entry("LongLimit", strategy.long, qty=1, limit=close * 0.98)', 'conditions': ['strategy.position_size > 0'], 'statement': 'strategy.entry("LongLimit", strategy.long, qty=1, limit=close * 0.98)'}, {'kind': 'close', 'call': 'strategy.close("Long")', 'conditions': ['close * 1.01 <= strategy.position_avg_price'], 'statement': 'strategy.close("Long")'}, {'kind': 'close', 'call': 'strategy.close("Short1")', 'conditions': ['close * 0.98 >= strategy.position_avg_price'], 'statement': 'strategy.close("Short1")'}, {'kind': 'close', 'call': 'strategy.close("Short2")', 'conditions': ['close * 0.98 >= strategy.position_avg_price'], 'statement': 'strategy.close("Short2")'}, {'kind': 'entry', 'call': 'strategy.entry("Long1", strategy.long, qty=2, limit=close * 0.99)', 'conditions': ['strategy.position_size < 0'], 'statement': 'strategy.entry("Long1", strategy.long, qty=2, limit=close * 0.99)'}, {'kind': 'entry', 'call': 'strategy.entry("Long2", strategy.long, qty=2, limit=close * 0.99)', 'conditions': ['strategy.position_size < 0'], 'statement': 'strategy.entry("Long2", strategy.long, qty=2, limit=close * 0.99)'}, {'kind': 'entry', 'call': 'strategy.entry("ShortLimit", strategy.short, qty=1, limit=close * 1.02)', 'conditions': ['strategy.position_size < 0'], 'statement': 'strategy.entry("ShortLimit", strategy.short, qty=1, limit=close * 1.02)'}, {'kind': 'close', 'call': 'strategy.close("Short")', 'conditions': ['close * 0.99 >= strategy.position_avg_price'], 'statement': 'strategy.close("Short")'}, {'kind': 'close', 'call': 'strategy.close("Long1")', 'conditions': ['close * 1.02 <= strategy.position_avg_price'], 'statement': 'strategy.close("Long1")'}, {'kind': 'close', 'call': 'strategy.close("Long2")', 'conditions': ['close * 1.02 <= strategy.position_avg_price'], 'statement': 'strategy.close("Long2")'}]
    original_pine = '/*backtest\nstart: 2023-02-22 00:00:00\nend: 2024-02-28 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("pokupka perevorot 5min tf", overlay=true)\n\n// Activation block (executed only once)\nif (close - open) < -5\n    strategy.entry("Long", strategy.long)\n\n// Checking chart state block (executed continuously)\nif strategy.position_size > 0\n    // If long position is open\n    strategy.entry("Short1", strategy.short, qty=2, limit=close * 1.01)\n    strategy.entry("Short2", strategy.short, qty=2, limit=close * 1.01)\n    strategy.entry("LongLimit", strategy.long, qty=1, limit=close * 0.98)\n\n// Execution block (executed continuously)\nif close * 1.01 <= strategy.position_avg_price\n    // If price has increased by 1%, indicating a short position\n    strategy.close("Long")\n\nif close * 0.98 >= strategy.position_avg_price\n    // If price has decreased by 2%, indicating two long positions\n    strategy.close("Short1")\n    strategy.close("Short2")\n\n// Checking chart state block (executed continuously)\nif strategy.position_size < 0\n    // If short position is open\n    strategy.entry("Long1", strategy.long, qty=2, limit=close * 0.99)\n    strategy.entry("Long2", strategy.long, qty=2, limit=close * 0.99)\n    strategy.entry("ShortLimit", strategy.short, qty=1, limit=close * 1.02)\n\n// Execution block (executed continuously)\nif close * 0.99 >= strategy.position_avg_price\n    // If price has decreased by 1%, indicating a long position\n    strategy.close("Short")\n\nif close * 1.02 <= strategy.position_avg_price\n    // If price has increased by 2%, indicating two short positions\n    strategy.close("Long1")\n    strategy.close("Long2")'

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
