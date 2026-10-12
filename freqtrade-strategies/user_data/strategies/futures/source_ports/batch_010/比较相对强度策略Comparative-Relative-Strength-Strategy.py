"""Source-faithful deep-assisted port of 比较相对强度策略Comparative-Relative-Strength-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_8e5cc215(PinePortBase, IStrategy):
    source_file = '比较相对强度策略Comparative-Relative-Strength-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'b': 'BTC_USDT:swap', 'len': 10, 'BuyBand': 0.9988, 'SellBand': 0.996, 'CloseBand': 0.9975, 'reverse': False}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.entry', 'strategy.close', 'for ', 'timeframe.', 'line.']
    source_fidelity_notes = ['Drawing/table calls are display-only unless their IDs/state are later read; preserved in source map but excluded from trade signal calculation where non-causal.']
    pine_assignments = [{'mode': '', 'name': 'a', 'op': '=', 'expr': 'syminfo.tickerid', 'conditions': []}, {'mode': '', 'name': 'b', 'op': '=', 'expr': 'input("BTC_USDT:swap")', 'conditions': []}, {'mode': '', 'name': 'len', 'op': '=', 'expr': 'input(10)', 'conditions': []}, {'mode': '', 'name': 'BuyBand', 'op': '=', 'expr': 'input(0.9988, step = 0.0001)', 'conditions': []}, {'mode': '', 'name': 'SellBand', 'op': '=', 'expr': 'input(0.9960, step = 0.0001)', 'conditions': []}, {'mode': '', 'name': 'CloseBand', 'op': '=', 'expr': 'input(0.9975, step = 0.0001)', 'conditions': []}, {'mode': '', 'name': 'reverse', 'op': '=', 'expr': 'input(false, title="Trade reverse")', 'conditions': []}, {'mode': '', 'name': 'as', 'op': '=', 'expr': 'security(a, timeframe.period, close)', 'conditions': []}, {'mode': '', 'name': 'bs', 'op': '=', 'expr': 'security(b, timeframe.period, close)', 'conditions': []}, {'mode': '', 'name': 'nRes', 'op': '=', 'expr': 'sma(as/bs, len)', 'conditions': []}, {'mode': '', 'name': 'pos', 'op': '=', 'expr': 'iff(nRes > BuyBand, 1, iff(nRes < SellBand, -1, iff(pos[1] == 1 and nRes < CloseBand, 0, iff(pos[1] == -1 and nRes > CloseBand, 0, nz(pos[1], 0)))))', 'conditions': []}, {'mode': '', 'name': 'possig', 'op': '=', 'expr': 'iff(reverse and pos == 1, -1, iff(reverse and pos == -1, 1, pos))', 'conditions': []}]
    pine_user_functions = []
    pine_controls = [{'indent': 0, 'statement': 'if (possig == 1)'}, {'indent': 0, 'statement': 'if (possig == -1)'}, {'indent': 0, 'statement': 'if (possig == 0)'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("Long", strategy.long)', 'conditions': ['(possig == 1)'], 'statement': 'strategy.entry("Long", strategy.long)'}, {'kind': 'entry', 'call': 'strategy.entry("Short", strategy.short)', 'conditions': ['(possig == -1)'], 'statement': 'strategy.entry("Short", strategy.short)'}, {'kind': 'close', 'call': 'strategy.close("Long", when = possig == 0)', 'conditions': ['(possig == 0)'], 'statement': 'strategy.close("Long", when = possig == 0)'}, {'kind': 'close', 'call': 'strategy.close("Short", when = possig == 0)', 'conditions': ['(possig == 0)'], 'statement': 'strategy.close("Short", when = possig == 0)'}]
    original_pine = '/*backtest\nstart: 2022-09-07 00:00:00\nend: 2023-09-13 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=2\n////////////////////////////////////////////////////////////\n//  Copyright by HPotter v1.0 10/03/2017\n// Comparative Relative Strength Strategy for ES\n//\n// You can change long to short in the Input Settings\n// Please, use it only for learning or paper trading. Do not for real trading.\n////////////////////////////////////////////////////////////\nstrategy("Comparative Relative Strength Strategy", shorttitle="CRS")\na = syminfo.tickerid \nb = input("BTC_USDT:swap") \nlen = input(10) \nBuyBand = input(0.9988, step = 0.0001)\nSellBand = input(0.9960, step = 0.0001)\nCloseBand = input(0.9975, step = 0.0001)\nreverse = input(false, title="Trade reverse")\nhline(CloseBand, color=blue, linestyle=hline.style_dashed)\nhline(SellBand, color=red, linestyle=hline.style_solid)\nhline(BuyBand, color=green, linestyle=hline.style_solid)\nas = security(a, timeframe.period, close) \nbs = security(b, timeframe.period, close) \nnRes = sma(as/bs, len)\npos = iff(nRes > BuyBand, 1,\n\t     iff(nRes < SellBand, -1,\n\t      iff(pos[1] == 1 and nRes < CloseBand, 0,\n\t       iff(pos[1] == -1 and nRes > CloseBand, 0, nz(pos[1], 0)))))\npossig = iff(reverse and pos == 1, -1,\n          iff(reverse and pos == -1, 1, pos))\t   \nif (possig == 1) \n    strategy.entry("Long", strategy.long)\nif (possig == -1)\n    strategy.entry("Short", strategy.short)\t   \t \nif (possig == 0)\n    strategy.close("Long", when = possig == 0)\t \n    strategy.close("Short", when = possig == 0)\t \nbarcolor(possig == -1 ? red: possig == 1 ? green : blue )\nplot(as/bs, title="CRS", color=gray) \nplot(nRes, color=navy)'

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
