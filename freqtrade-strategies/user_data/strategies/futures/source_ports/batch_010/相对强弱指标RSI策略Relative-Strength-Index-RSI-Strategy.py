"""Source-faithful deep-assisted port of 相对强弱指标RSI策略Relative-Strength-Index-RSI-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_2a630829(PinePortBase, IStrategy):
    source_file = '相对强弱指标RSI策略Relative-Strength-Index-RSI-Strategy.md'
    timeframe = '1h'
    can_short = True
    source_defaults = {'Length': 12, 'Oversold': 30, 'Overbought': 70, 'reverse': False}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.entry', 'for ']
    source_fidelity_notes = []
    pine_assignments = [{'mode': '', 'name': 'Length', 'op': '=', 'expr': 'input(12, minval=1)', 'conditions': []}, {'mode': '', 'name': 'Oversold', 'op': '=', 'expr': 'input(30, minval=1)', 'conditions': []}, {'mode': '', 'name': 'Overbought', 'op': '=', 'expr': 'input(70, minval=1)', 'conditions': []}, {'mode': '', 'name': 'reverse', 'op': '=', 'expr': 'input(false, title="Trade reverse")', 'conditions': []}, {'mode': '', 'name': 'xRSI', 'op': '=', 'expr': 'rsi(close, Length)', 'conditions': []}, {'mode': '', 'name': 'pos', 'op': '=', 'expr': 'iff(xRSI > Overbought, 1, iff(xRSI < Oversold, -1, nz(pos[1], 0)))', 'conditions': []}, {'mode': '', 'name': 'possig', 'op': '=', 'expr': 'iff(reverse and pos == 1, -1, iff(reverse and pos == -1, 1, pos))', 'conditions': []}]
    pine_user_functions = []
    pine_controls = [{'indent': 0, 'statement': 'if (possig == 1)'}, {'indent': 0, 'statement': 'if (possig == -1)'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("Long", strategy.long)', 'conditions': ['(possig == 1)'], 'statement': 'strategy.entry("Long", strategy.long)'}, {'kind': 'entry', 'call': 'strategy.entry("Short", strategy.short)', 'conditions': ['(possig == -1)'], 'statement': 'strategy.entry("Short", strategy.short)'}]
    original_pine = '/*backtest\nstart: 2023-10-02 00:00:00\nend: 2023-11-01 00:00:00\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=2\n////////////////////////////////////////////////////////////\n//  Copyright by HPotter v1.0 10/01/2017\n// The RSI is a very popular indicator that follows price activity. \n// It calculates an average of the positive net changes, and an average \n// of the negative net changes in the most recent bars, and it determines \n// the ratio between these averages. The result is expressed as a number \n// between 0 and 100. Commonly it is said that if the RSI has a low value, \n// for example 30 or under, the symbol is oversold. And if the RSI has a \n// high value, 70 for example, the symbol is overbought. \n//\n// You can change long to short in the Input Settings\n// Please, use it only for learning or paper trading. Do not for real trading.\n////////////////////////////////////////////////////////////\nstrategy(title="Strategy RSI", shorttitle="Strategy RSI", overlay = true )\nLength = input(12, minval=1)\nOversold = input(30, minval=1)\nOverbought = input(70, minval=1)\nreverse = input(false, title="Trade reverse")\nxRSI = rsi(close, Length)\npos = iff(xRSI > Overbought, 1,\n\t   iff(xRSI < Oversold, -1, nz(pos[1], 0))) \npossig = iff(reverse and pos == 1, -1,\n          iff(reverse and pos == -1, 1, pos))\nif (possig == 1) \n    strategy.entry("Long", strategy.long)\nif (possig == -1)\n    strategy.entry("Short", strategy.short)\t   \t    \nbarcolor(possig == -1 ? red: possig == 1 ? green : blue )'

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
