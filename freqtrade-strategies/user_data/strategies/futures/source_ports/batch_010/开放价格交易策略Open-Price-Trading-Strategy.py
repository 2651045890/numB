"""Source-faithful deep-assisted port of 开放价格交易策略Open-Price-Trading-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_2bf27958(PinePortBase, IStrategy):
    source_file = '开放价格交易策略Open-Price-Trading-Strategy.md'
    timeframe = '4h'
    can_short = True
    source_defaults = {}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 10.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.entry', 'strategy.equity']
    source_fidelity_notes = ['Reads broker/strategy state; signals depend on fill timing and cannot be reduced to indicator-only booleans without changing behavior.']
    pine_assignments = [{'mode': '', 'name': 'x', 'op': '=', 'expr': '((open[1])/(close[1]))', 'conditions': []}, {'mode': '', 'name': 'x1', 'op': '=', 'expr': '((open[2])/(close[2]))', 'conditions': []}, {'mode': '', 'name': 'x2', 'op': '=', 'expr': '((open[3])/(close[3]))', 'conditions': []}, {'mode': '', 'name': 'x3', 'op': '=', 'expr': '((open[4])/(close[4]))', 'conditions': []}, {'mode': '', 'name': 'x4', 'op': '=', 'expr': '((open[5])/(close[5]))', 'conditions': []}, {'mode': '', 'name': 'x5', 'op': '=', 'expr': '((open[6])/(close[6]))', 'conditions': []}, {'mode': '', 'name': 'x6', 'op': '=', 'expr': '((open[7])/(close[7]))', 'conditions': []}, {'mode': '', 'name': 'x7', 'op': '=', 'expr': '((open[8])/(close[8]))', 'conditions': []}, {'mode': '', 'name': 'x8', 'op': '=', 'expr': '((open[9])/(close[9]))', 'conditions': []}, {'mode': '', 'name': 'y', 'op': '=', 'expr': '(x+x1+x2+x3+x4+x5+x6+x7+x8)/9', 'conditions': []}]
    pine_user_functions = []
    pine_controls = [{'indent': 0, 'statement': 'if (y < 1 )'}, {'indent': 0, 'statement': 'if (y > 1)'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("Up", strategy.long)', 'conditions': ['(y < 1 )'], 'statement': 'strategy.entry("Up", strategy.long)'}, {'kind': 'entry', 'call': 'strategy.entry("Down", strategy.short)', 'conditions': ['(y > 1)'], 'statement': 'strategy.entry("Down", strategy.short)'}]
    original_pine = '/*backtest\nstart: 2023-09-14 00:00:00\nend: 2023-09-21 00:00:00\nperiod: 4h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=2\nstrategy("PerfectStrategy", overlay=true, default_qty_type = strategy.percent_of_equity, default_qty_value = 10)\n \n\nx = ((open[1])/(close[1]))\nx1 = ((open[2])/(close[2]))\nx2= ((open[3])/(close[3]))\nx3 = ((open[4])/(close[4]))\nx4 = ((open[5])/(close[5]))\nx5 = ((open[6])/(close[6]))\nx6 = ((open[7])/(close[7]))\nx7 = ((open[8])/(close[8]))\nx8 = ((open[9])/(close[9]))\n\ny = (x+x1+x2+x3+x4+x5+x6+x7+x8)/9\nif (y < 1 )\n    strategy.entry("Up", strategy.long)\n\nif (y > 1)\n    strategy.entry("Down", strategy.short)\n\n//plot(strategy.equity, title="equity", color=red, linewidth=2, style=areabr)'

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
