"""Source-faithful deep-assisted port of 理查德布克斯塔伯动量突破策略Richard-Bookstaber-Momentum-Breakout-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_1629dec3(PinePortBase, IStrategy):
    source_file = '理查德布克斯塔伯动量突破策略Richard-Bookstaber-Momentum-Breakout-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'averageLength': 14, 'multiplier': 2.0}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 100.0
    source_pyramiding = 0
    source_initial_capital = 20000.0
    source_commission_percent = 0.0
    source_features = ['strategy.entry', 'var ', '=>']
    source_fidelity_notes = ['Uses persistent Pine state (var/varip); state is order-dependent and must be evaluated bar-by-bar, not replaced by a vectorized fill-forward approximation.']
    pine_assignments = [{'mode': 'var', 'name': 'averageLength', 'op': '=', 'expr': 'input.int(14, "Average length", 2)', 'conditions': []}, {'mode': 'var', 'name': 'multiplier', 'op': '=', 'expr': 'input.float(2.0, "Multiplier", 0.0, step=0.1)', 'conditions': []}, {'mode': '', 'name': 'atr', 'op': '=', 'expr': 'ta.atr(averageLength) * multiplier', 'conditions': []}, {'mode': '', 'name': 'closingChange', 'op': '=', 'expr': 'ta.change(close, 1)', 'conditions': []}, {'mode': '', 'name': 'res', 'op': '=', 'expr': 'closingChange * signal > atr[1]', 'conditions': []}, {'mode': '', 'name': 'longCondition', 'op': '=', 'expr': 'atrPenetration(1)', 'conditions': []}, {'mode': '', 'name': 'shortCondition', 'op': '=', 'expr': 'atrPenetration(-1)', 'conditions': []}]
    pine_user_functions = [{'name': 'atrPenetration', 'args': 'int signal', 'body': ''}]
    pine_controls = [{'indent': 0, 'statement': 'if (longCondition)'}, {'indent': 0, 'statement': 'if (shortCondition)'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry(strategy.direction.long, strategy.long)', 'conditions': ['(longCondition)'], 'statement': 'strategy.entry(strategy.direction.long, strategy.long)'}, {'kind': 'entry', 'call': 'strategy.entry(strategy.direction.short, strategy.short)', 'conditions': ['(shortCondition)'], 'statement': 'strategy.entry(strategy.direction.short, strategy.short)'}]
    original_pine = '/*backtest\nstart: 2022-10-26 00:00:00\nend: 2023-11-01 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This source code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © EduardoMattje\n\n//@version=5\nstrategy("Volatility System", overlay=false, margin_long=0, margin_short=0, default_qty_type=strategy.percent_of_equity, \n default_qty_value=100, process_orders_on_close=true, initial_capital=20000)\n\n// Inputs\n\nvar averageLength = input.int(14, "Average length", 2)\nvar multiplier = input.float(2.0, "Multiplier", 0.0, step=0.1)\n\n// Calculations\n\natr = ta.atr(averageLength) * multiplier\nclosingChange = ta.change(close, 1)\n\natrPenetration(int signal) =>\n    res = closingChange * signal > atr[1]\n\nlongCondition = atrPenetration(1)\nshortCondition = atrPenetration(-1)\n\n// Order calls\n\nif (longCondition)\n    strategy.entry(strategy.direction.long, strategy.long)\n\nif (shortCondition)\n    strategy.entry(strategy.direction.short, strategy.short)\n\n// Visuals\n\nplot(atr, "ATR", color.white, 2)\nplot(math.abs(closingChange), "Absolute close change", color.red)'

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
