"""Source-faithful deep-assisted port of 现代拉盖尔变换相对强弱指标优化策略-Modern-Laguerre-Transform-Relative-Strength-Index-Optimization-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_ebe9612d(PinePortBase, IStrategy):
    source_file = '现代拉盖尔变换相对强弱指标优化策略-Modern-Laguerre-Transform-Relative-Strength-Index-Optimization-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'gamma': 0.5, 'BuyBand': 0.8, 'SellBand': 0.2, 'reverse': False}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.entry']
    source_fidelity_notes = []
    pine_assignments = [{'mode': '', 'name': 'gamma', 'op': '=', 'expr': 'input(0.5, minval=-0.1, maxval = 0.9)', 'conditions': []}, {'mode': '', 'name': 'BuyBand', 'op': '=', 'expr': 'input(0.8, step = 0.01)', 'conditions': []}, {'mode': '', 'name': 'SellBand', 'op': '=', 'expr': 'input(0.2, step = 0.01)', 'conditions': []}, {'mode': '', 'name': 'reverse', 'op': '=', 'expr': 'input(false, title="Trade reverse")', 'conditions': []}, {'mode': '', 'name': 'xL0', 'op': '=', 'expr': '(1-gamma) * close + gamma * nz(xL0[1], 1)', 'conditions': []}, {'mode': '', 'name': 'xL1', 'op': '=', 'expr': '- gamma * xL0 + nz(xL0[1], 1) + gamma * nz(xL1[1], 1)', 'conditions': []}, {'mode': '', 'name': 'xL2', 'op': '=', 'expr': '- gamma * xL1 + nz(xL1[1], 1) + gamma * nz(xL2[1], 1)', 'conditions': []}, {'mode': '', 'name': 'xL3', 'op': '=', 'expr': '- gamma * xL2 + nz(xL2[1], 1) + gamma * nz(xL3[1], 1)', 'conditions': []}, {'mode': '', 'name': 'CU', 'op': '=', 'expr': '(xL0 >= xL1 ? xL0 - xL1 : 0) + (xL1 >= xL2 ? xL1 - xL2 : 0) + (xL2 >= xL3 ? xL2 - xL3 : 0)', 'conditions': []}, {'mode': '', 'name': 'CD', 'op': '=', 'expr': '(xL0 >= xL1 ? 0 : xL1 - xL0) + (xL1 >= xL2 ? 0 : xL2 - xL1) + (xL2 >= xL3 ? 0 : xL3 - xL2)', 'conditions': []}, {'mode': '', 'name': 'nRes', 'op': '=', 'expr': 'iff(CU + CD != 0, CU / (CU + CD), 0)', 'conditions': []}, {'mode': '', 'name': 'pos', 'op': '=', 'expr': 'iff(nRes > BuyBand, 1, iff(nRes < SellBand, -1, nz(pos[1], 0)))', 'conditions': []}, {'mode': '', 'name': 'possig', 'op': '=', 'expr': 'iff(reverse and pos == 1, -1, iff(reverse and pos == -1, 1, pos))', 'conditions': []}]
    pine_user_functions = []
    pine_controls = [{'indent': 0, 'statement': 'if (possig == 1)'}, {'indent': 0, 'statement': 'if (possig == -1)'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("Long", strategy.long)', 'conditions': ['(possig == 1)'], 'statement': 'strategy.entry("Long", strategy.long)'}, {'kind': 'entry', 'call': 'strategy.entry("Short", strategy.short)', 'conditions': ['(possig == -1)'], 'statement': 'strategy.entry("Short", strategy.short)'}]
    original_pine = '/*backtest\nstart: 2022-11-15 00:00:00\nend: 2023-11-21 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=2\n////////////////////////////////////////////////////////////\n//  Copyright by HPotter v1.0 01/09/2017\n// This is RSI indicator which is more sesitive to price changes. \n// It is based upon a modern math tool - Laguerre transform filter.\n// With help of Laguerre filter one becomes able to create superior \n// indicators using very short data lengths as well. The use of shorter \n// data lengths means you can make the indicators more responsive to \n// changes in the price.\n//\n// You can change long to short in the Input Settings \n// WARNING:\n//  - For purpose educate only\n//  - This script to change bars colors.\n////////////////////////////////////////////////////////////\nstrategy(title="Laguerre-based RSI", shorttitle="Laguerre-RSI")\ngamma = input(0.5, minval=-0.1, maxval = 0.9)\nBuyBand = input(0.8, step = 0.01)\nSellBand = input(0.2, step = 0.01)\nreverse = input(false, title="Trade reverse")\nhline(BuyBand, color=green, linestyle=line)\nhline(SellBand, color=red, linestyle=line)\nxL0 = (1-gamma) * close + gamma * nz(xL0[1], 1)\nxL1 = - gamma * xL0 + nz(xL0[1], 1) + gamma * nz(xL1[1], 1)\nxL2 = - gamma * xL1 + nz(xL1[1], 1) + gamma * nz(xL2[1], 1)\nxL3 = - gamma * xL2 + nz(xL2[1], 1) + gamma * nz(xL3[1], 1)\nCU = (xL0 >= xL1 ? xL0 - xL1 : 0) + (xL1 >= xL2 ? xL1 - xL2 : 0)  + (xL2 >= xL3 ? xL2 - xL3 : 0)\nCD = (xL0 >= xL1 ? 0 : xL1 - xL0) + (xL1 >= xL2 ? 0 : xL2 - xL1)  + (xL2 >= xL3 ? 0 : xL3 - xL2)\nnRes = iff(CU + CD != 0, CU / (CU + CD), 0)\npos = iff(nRes > BuyBand, 1,\n\t   iff(nRes < SellBand, -1, nz(pos[1], 0))) \npossig = iff(reverse and pos == 1, -1,\n          iff(reverse and pos == -1, 1, pos))\t   \nif (possig == 1) \n    strategy.entry("Long", strategy.long)\nif (possig == -1)\n    strategy.entry("Short", strategy.short)\t   \t    \nbarcolor(possig == -1 ? red: possig == 1 ? green : blue )  \nplot(nRes, color=red, title="Laguerre-based RSI")'

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
