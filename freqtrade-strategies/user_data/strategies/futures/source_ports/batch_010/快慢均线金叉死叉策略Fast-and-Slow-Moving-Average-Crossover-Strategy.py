"""Source-faithful deep-assisted port of 快慢均线金叉死叉策略Fast-and-Slow-Moving-Average-Crossover-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_b906d950(PinePortBase, IStrategy):
    source_file = '快慢均线金叉死叉策略Fast-and-Slow-Moving-Average-Crossover-Strategy.md'
    timeframe = '1h'
    can_short = True
    source_defaults = {'fastLength': 9, 'slowlength': 40}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.entry', 'strategy.equity']
    source_fidelity_notes = ['Reads broker/strategy state; signals depend on fill timing and cannot be reduced to indicator-only booleans without changing behavior.']
    pine_assignments = [{'mode': '', 'name': 'fastLength', 'op': '=', 'expr': 'input(9)', 'conditions': []}, {'mode': '', 'name': 'slowlength', 'op': '=', 'expr': 'input(40)', 'conditions': []}, {'mode': '', 'name': 'delta', 'op': '=', 'expr': 'ema(close, fastLength) - sma(close, slowlength)', 'conditions': []}]
    pine_user_functions = []
    pine_controls = [{'indent': 0, 'statement': 'if (crossover(delta, 0))'}, {'indent': 0, 'statement': 'if (crossunder(delta, 0))'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("Compra", strategy.long, comment="2MM")', 'conditions': ['(crossover(delta, 0))'], 'statement': 'strategy.entry("Compra", strategy.long, comment="2MM")'}, {'kind': 'entry', 'call': 'strategy.entry("Venda", strategy.short, comment="2MM")', 'conditions': ['(crossunder(delta, 0))'], 'statement': 'strategy.entry("Venda", strategy.short, comment="2MM")'}]
    original_pine = '/*backtest\nstart: 2023-08-15 00:00:00\nend: 2023-09-14 00:00:00\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=2\nstrategy("Cruzameto 2MM", overlay=true)\n\nfastLength = input(9)\nslowlength = input(40)\n//MACDLength = input(9)\n\ndelta = ema(close, fastLength) - sma(close, slowlength)\n//aMACD = ema(MACD, MACDLength)\n//delta = MACD - aMACD\n\nif (crossover(delta, 0))\n    strategy.entry("Compra", strategy.long, comment="2MM")\n\nif (crossunder(delta, 0))\n    strategy.entry("Venda", strategy.short, comment="2MM")\n\n//plot(strategy.equity, title="equity", color=red, linewidth=2, style=areabr)'

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
