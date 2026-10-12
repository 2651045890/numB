"""Source-faithful deep-assisted port of 标准上涨五浪下跌五浪策略.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_e68cafc1(PinePortBase, IStrategy):
    source_file = '标准上涨五浪下跌五浪策略.md'
    timeframe = '5m'
    can_short = True
    source_defaults = {}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.entry']
    source_fidelity_notes = []
    pine_assignments = [{'mode': '', 'name': 's1', 'op': '=', 'expr': 'lowest(low, 5)', 'conditions': []}, {'mode': '', 'name': 'b1', 'op': '=', 'expr': 'highest(high, 5)', 'conditions': []}, {'mode': '', 'name': 's2', 'op': '=', 'expr': 'lowest(low[1], 5)', 'conditions': []}, {'mode': '', 'name': 'b2', 'op': '=', 'expr': 'highest(high[1], 5)', 'conditions': []}, {'mode': '', 'name': 's3', 'op': '=', 'expr': 'lowest(low[2], 5)', 'conditions': []}, {'mode': '', 'name': 'b3', 'op': '=', 'expr': 'highest(high[2], 5)', 'conditions': []}, {'mode': '', 'name': 's4', 'op': '=', 'expr': 'lowest(low[3], 5)', 'conditions': []}, {'mode': '', 'name': 'b4', 'op': '=', 'expr': 'highest(high[3], 5)', 'conditions': []}, {'mode': '', 'name': 's5', 'op': '=', 'expr': 'lowest(low[4], 5)', 'conditions': []}, {'mode': '', 'name': 'b5', 'op': '=', 'expr': 'highest(high[4], 5)', 'conditions': []}, {'mode': '', 'name': 'up_waves', 'op': '=', 'expr': '(b1 > b2) and (b2 > b3) and (b3 > b4) and (b4 > b5)', 'conditions': []}, {'mode': '', 'name': 'down_waves', 'op': '=', 'expr': '(s1 < s2) and (s2 < s3) and (s3 < s4) and (s4 < s5)', 'conditions': []}]
    pine_user_functions = []
    pine_controls = [{'indent': 0, 'statement': 'if (up_waves)'}, {'indent': 0, 'statement': 'else if (down_waves)'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("long", strategy.long, 1, stop = low[4], comment = "long")', 'conditions': ['(up_waves)'], 'statement': 'strategy.entry("long", strategy.long, 1, stop = low[4], comment = "long")'}, {'kind': 'entry', 'call': 'strategy.entry("short", strategy.short, 1, stop = high[4], comment = "short")', 'conditions': ['(down_waves)'], 'statement': 'strategy.entry("short", strategy.short, 1, stop = high[4], comment = "short")'}]
    original_pine = '//@version=4\n// 标准上涨五浪下跌五浪策略\n// 顶1\ns1 = lowest(low, 5)\n// 底1\nb1 = highest(high, 5)\n// 顶2\ns2 = lowest(low[1], 5)\n// 底2\nb2 = highest(high[1], 5)\n// 顶3\ns3 = lowest(low[2], 5)\n// 底3\nb3 = highest(high[2], 5)\n// 顶4\ns4 = lowest(low[3], 5)\n// 底4\nb4 = highest(high[3], 5)\n// 顶5\ns5 = lowest(low[4], 5)\n// 底5\nb5 = highest(high[4], 5)\n\n// 上涨五浪\nup_waves = (b1 > b2) and (b2 > b3) and (b3 > b4) and (b4 > b5)\n// 下跌五浪\ndown_waves = (s1 < s2) and (s2 < s3) and (s3 < s4) and (s4 < s5)\n\n// 交易条件\nif (up_waves)\n    strategy.entry("long", strategy.long, 1, stop = low[4], comment = "long")\n\nelse if (down_waves)\n    strategy.entry("short", strategy.short, 1, stop = high[4], comment = "short")\n\n// 绘图\nplotshape(up_waves, style = shape.triangleup, location = location.belowbar, color=green, title="上涨五浪")\nplotshape(down_waves, style = shape.triangledown, location = location.abovebar, color=red, title="下跌五浪")'

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
