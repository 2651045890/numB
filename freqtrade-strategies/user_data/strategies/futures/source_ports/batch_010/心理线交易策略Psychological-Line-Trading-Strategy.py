"""Source-faithful deep-assisted port of 心理线交易策略Psychological-Line-Trading-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_a265ab66(PinePortBase, IStrategy):
    source_file = '心理线交易策略Psychological-Line-Trading-Strategy.md'
    timeframe = '15m'
    can_short = True
    source_defaults = {'Length': 20, 'reverse': False}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.entry', 'for ']
    source_fidelity_notes = []
    pine_assignments = [{'mode': '', 'name': 'Length', 'op': '=', 'expr': 'input(20, minval=1)', 'conditions': []}, {'mode': '', 'name': 'reverse', 'op': '=', 'expr': 'input(false, title="Trade reverse")', 'conditions': []}, {'mode': '', 'name': 'xPSY', 'op': '=', 'expr': 'sum(close > close[1],Length) / Length * 100', 'conditions': []}, {'mode': '', 'name': 'clr', 'op': '=', 'expr': 'iff(xPSY >= 50, green, red)', 'conditions': []}, {'mode': '', 'name': 'pos', 'op': '=', 'expr': 'iff(xPSY > 50, 1, iff(xPSY < 50, -1, nz(pos[1], 0)))', 'conditions': []}, {'mode': '', 'name': 'possig', 'op': '=', 'expr': 'iff(reverse and pos == 1, -1, iff(reverse and pos == -1, 1, pos))', 'conditions': []}, {'mode': '', 'name': 'p1', 'op': '=', 'expr': 'plot(50, color=black, title="0")', 'conditions': []}, {'mode': '', 'name': 'p2', 'op': '=', 'expr': 'plot(xPSY, color=blue, title="PSY")', 'conditions': []}]
    pine_user_functions = []
    pine_controls = [{'indent': 0, 'statement': 'if (possig == 1)'}, {'indent': 0, 'statement': 'if (possig == -1)'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("Long", strategy.long)', 'conditions': ['(possig == 1)'], 'statement': 'strategy.entry("Long", strategy.long)'}, {'kind': 'entry', 'call': 'strategy.entry("Short", strategy.short)', 'conditions': ['(possig == -1)'], 'statement': 'strategy.entry("Short", strategy.short)'}]
    original_pine = '/*backtest\nstart: 2023-09-12 00:00:00\nend: 2023-09-19 00:00:00\nperiod: 15m\nbasePeriod: 5m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=2\n////////////////////////////////////////////////////////////\n//  Copyright by HPotter v1.0 10/04/2018\n// Psychological line (PSY), as an indicator, is the ratio of the number of \n// rising periods over the total number of periods. It reflects the buying \n// power in relation to the selling power.\n//\n// If PSY is above 50%, it indicates that buyers are in control. Likewise, \n// if it is below 50%, it indicates the sellers are in control. If the PSY \n// moves along the 50% area, it indicates balance between the buyers and \n// sellers and therefore there is no direction movement for the market.\n//\n// You can change long to short in the Input Settings\n// WARNING:\n//  - For purpose educate only\n//  - This script to change bars colors.\n////////////////////////////////////////////////////////////\nstrategy(title="Psychological line Backtest")\nLength = input(20, minval=1)\nreverse = input(false, title="Trade reverse")\nxPSY = sum(close > close[1],Length) / Length * 100\nclr = iff(xPSY >= 50, green, red)\npos = iff(xPSY > 50, 1,\n       iff(xPSY < 50, -1, nz(pos[1], 0))) \npossig = iff(reverse and pos == 1, -1,\n          iff(reverse and pos == -1, 1, pos))\t   \nif (possig == 1) \n    strategy.entry("Long", strategy.long)\nif (possig == -1)\n    strategy.entry("Short", strategy.short)\t   \t    \nbarcolor(possig == -1 ? red: possig == 1 ? green : blue ) \np1 = plot(50, color=black, title="0")\np2 = plot(xPSY, color=blue, title="PSY")\nfill(p1, p2, color=clr)'

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
