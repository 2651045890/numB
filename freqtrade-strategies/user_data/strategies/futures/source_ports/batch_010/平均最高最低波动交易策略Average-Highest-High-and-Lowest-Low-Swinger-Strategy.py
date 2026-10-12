"""Source-faithful deep-assisted port of 平均最高最低波动交易策略Average-Highest-High-and-Lowest-Low-Swinger-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_07dbe07c(PinePortBase, IStrategy):
    source_file = '平均最高最低波动交易策略Average-Highest-High-and-Lowest-Low-Swinger-Strategy.md'
    timeframe = '1m'
    can_short = False
    source_defaults = {'varLo': 9, 'varHi': 26}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.entry']
    source_fidelity_notes = []
    pine_assignments = [{'mode': '', 'name': 'varLo', 'op': '=', 'expr': 'input(title="Fast Line", type=input.integer, defval=9, minval=1)', 'conditions': []}, {'mode': '', 'name': 'varHi', 'op': '=', 'expr': 'input(title="Slow Line", type=input.integer, defval=26, minval=1)', 'conditions': []}, {'mode': '', 'name': 'a', 'op': '=', 'expr': 'lowest(varLo)', 'conditions': []}, {'mode': '', 'name': 'b', 'op': '=', 'expr': 'highest(varLo)', 'conditions': []}, {'mode': '', 'name': 'c', 'op': '=', 'expr': '(a + b ) / 2', 'conditions': []}, {'mode': '', 'name': 'd', 'op': '=', 'expr': 'lowest(varHi)', 'conditions': []}, {'mode': '', 'name': 'e', 'op': '=', 'expr': 'highest(varHi)', 'conditions': []}, {'mode': '', 'name': 'f', 'op': '=', 'expr': '(d + e) / 2', 'conditions': []}, {'mode': '', 'name': 'g', 'op': '=', 'expr': '((c + f) / 2)[varHi]', 'conditions': []}, {'mode': '', 'name': 'h', 'op': '=', 'expr': '((highest(varHi * 2) + lowest(varHi * 2)) / 2)[varHi]', 'conditions': []}, {'mode': '', 'name': 'long', 'op': '=', 'expr': 'close > c and close > f and close >g and close > h', 'conditions': []}, {'mode': '', 'name': 'short', 'op': '=', 'expr': 'close < c and close < f and close<g and close < h', 'conditions': []}]
    pine_user_functions = []
    pine_controls = []
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("long",1,when=long)', 'conditions': [], 'statement': 'strategy.entry("long",1,when=long)'}, {'kind': 'entry', 'call': "strategy.entry('short',0,when=short)", 'conditions': [], 'statement': "strategy.entry('short',0,when=short)"}]
    original_pine = '/*backtest\nstart: 2023-11-27 00:00:00\nend: 2023-12-04 00:00:00\nperiod: 1m\nbasePeriod: 1m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This source code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © exlux99\n\n//@version=4\nstrategy(title = "Avg HH/LL Crypto Swinger", overlay = true )\n\nvarLo = input(title="Fast Line", type=input.integer, defval=9, minval=1)\nvarHi = input(title="Slow  Line", type=input.integer, defval=26, minval=1)\n\na = lowest(varLo)\nb = highest(varLo)\nc = (a + b ) / 2\n\nd = lowest(varHi)\ne = highest(varHi)\nf = (d + e) / 2\n\ng = ((c + f) / 2)[varHi]\nh = ((highest(varHi * 2) + lowest(varHi * 2)) / 2)[varHi]\n\n\n\nlong=close > c and close > f and close >g and close > h\nshort=close < c and close < f and close<g and close < h\n\nstrategy.entry("long",1,when=long)\nstrategy.entry(\'short\',0,when=short)'

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
