"""Source-faithful deep-assisted port of 牛市追踪策略Bull-Market-Chasing-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_1b640b20(PinePortBase, IStrategy):
    source_file = '牛市追踪策略Bull-Market-Chasing-Strategy.md'
    timeframe = '45m'
    can_short = True
    source_defaults = {'short_yes': True, 'ema_fast': 10, 'ema_slow': 60}
    source_qty_type = 'cash'
    source_qty_value = 1000.0
    source_pyramiding = 0
    source_initial_capital = 1000.0
    source_commission_percent = 0.075
    source_features = ['strategy.entry', 'strategy.close']
    source_fidelity_notes = []
    pine_assignments = [{'mode': '', 'name': 'short_yes', 'op': '=', 'expr': 'input.bool(true,"Attiva Short")', 'conditions': []}, {'mode': '', 'name': 'ema_fast', 'op': '=', 'expr': 'input.int(10, "Periodo Media veloce")', 'conditions': []}, {'mode': '', 'name': 'ema_slow', 'op': '=', 'expr': 'input.int(60, "Periodo Media lenta")', 'conditions': []}, {'mode': '', 'name': 'ema10', 'op': '=', 'expr': 'ta.ema(close, ema_fast)', 'conditions': []}, {'mode': '', 'name': 'ema60', 'op': '=', 'expr': 'ta.ema(close, ema_slow)', 'conditions': []}, {'mode': '', 'name': 'long_cond', 'op': '=', 'expr': 'ta.crossover(ema10, ema60)', 'conditions': []}, {'mode': '', 'name': 'short_cond', 'op': '=', 'expr': 'ta.crossunder(ema10, ema60) and short_yes', 'conditions': []}, {'mode': '', 'name': 'close_cond', 'op': '=', 'expr': 'ta.crossunder(ema10, ema60) and not short_yes', 'conditions': []}]
    pine_user_functions = []
    pine_controls = [{'indent': 0, 'statement': 'if long_cond'}, {'indent': 0, 'statement': 'if short_cond'}, {'indent': 0, 'statement': 'if close_cond'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("EL", strategy.long)', 'conditions': ['long_cond'], 'statement': 'strategy.entry("EL", strategy.long)'}, {'kind': 'entry', 'call': 'strategy.entry("ES", strategy.short)', 'conditions': ['short_cond'], 'statement': 'strategy.entry("ES", strategy.short)'}, {'kind': 'close', 'call': 'strategy.close("EL" )', 'conditions': ['close_cond'], 'statement': 'strategy.close("EL" )'}]
    original_pine = '/*backtest\nstart: 2023-09-20 00:00:00\nend: 2023-09-27 00:00:00\nperiod: 45m\nbasePeriod: 5m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This source code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © TheSocialCryptoClub\n\n//@version=5\n// strategy(title = "STB - Gianno Nano Strategy",\n//          shorttitle= "STB - Gianno Nano Strategy",\n//          overlay = true,\n//          initial_capital = 1000,\n//          default_qty_type = strategy.cash,\n//          default_qty_value = 1000,\n//          commission_type = strategy.commission.percent,\n//          commission_value = 0.075)\n\nshort_yes = input.bool(true,"Attiva Short")\nema_fast = input.int(10, "Periodo Media veloce")\nema_slow = input.int(60, "Periodo Media lenta")\n\n// Variable declarations\n\nema10 = ta.ema(close, ema_fast)\nema60 = ta.ema(close, ema_slow)\n\nplot(ema10, "EMA 10", color.yellow, 2)\nplot(ema60, "EMA 60", color.aqua, 2)\n\n// Long Condition\n\nlong_cond = ta.crossover(ema10, ema60)\nshort_cond = ta.crossunder(ema10, ema60) and short_yes\nclose_cond = ta.crossunder(ema10, ema60) and not short_yes\n// Engine strategy\n\nif long_cond\n    strategy.entry("EL", strategy.long)\nif short_cond\n    strategy.entry("ES", strategy.short)\nif close_cond\n    strategy.close("EL" )'

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
