"""Source-faithful deep-assisted port of 朗格安德逆转策略Langande-Reversal-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_097ad49b(PinePortBase, IStrategy):
    source_file = '朗格安德逆转策略Langande-Reversal-Strategy.md'
    timeframe = '2h'
    can_short = True
    source_defaults = {'leftBars': 4, 'rightBars': 2}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.entry', 'strategy.equity']
    source_fidelity_notes = ['Reads broker/strategy state; signals depend on fill timing and cannot be reduced to indicator-only booleans without changing behavior.']
    pine_assignments = [{'mode': '', 'name': 'leftBars', 'op': '=', 'expr': 'input(4)', 'conditions': []}, {'mode': '', 'name': 'rightBars', 'op': '=', 'expr': 'input(2)', 'conditions': []}, {'mode': '', 'name': 'swh', 'op': '=', 'expr': 'pivothigh(leftBars, rightBars)', 'conditions': []}, {'mode': '', 'name': 'swl', 'op': '=', 'expr': 'pivotlow(leftBars, rightBars)', 'conditions': []}, {'mode': '', 'name': 'swh_cond', 'op': '=', 'expr': 'not na(swh)', 'conditions': []}, {'mode': '', 'name': 'hprice', 'op': '=', 'expr': '0.0', 'conditions': []}, {'mode': '', 'name': 'hprice', 'op': ':=', 'expr': 'swh_cond ? swh : hprice[1]', 'conditions': []}, {'mode': '', 'name': 'le', 'op': '=', 'expr': 'false', 'conditions': []}, {'mode': '', 'name': 'le', 'op': ':=', 'expr': 'swh_cond ? true : (le[1] and high > hprice ? false : le[1])', 'conditions': []}, {'mode': '', 'name': 'swl_cond', 'op': '=', 'expr': 'not na(swl)', 'conditions': []}, {'mode': '', 'name': 'lprice', 'op': '=', 'expr': '0.0', 'conditions': []}, {'mode': '', 'name': 'lprice', 'op': ':=', 'expr': 'swl_cond ? swl : lprice[1]', 'conditions': []}, {'mode': '', 'name': 'se', 'op': '=', 'expr': 'false', 'conditions': []}, {'mode': '', 'name': 'se', 'op': ':=', 'expr': 'swl_cond ? true : (se[1] and low < lprice ? false : se[1])', 'conditions': []}]
    pine_user_functions = []
    pine_controls = [{'indent': 0, 'statement': 'if (le)'}, {'indent': 0, 'statement': 'if (se)'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("PivRevLE", strategy.long, comment="BUY**", stop=hprice + syminfo.mintick)', 'conditions': ['(le)'], 'statement': 'strategy.entry("PivRevLE", strategy.long, comment="BUY**", stop=hprice + syminfo.mintick)'}, {'kind': 'entry', 'call': 'strategy.entry("PivRevSE", strategy.short, comment="SELL**", stop=lprice - syminfo.mintick)', 'conditions': ['(se)'], 'statement': 'strategy.entry("PivRevSE", strategy.short, comment="SELL**", stop=lprice - syminfo.mintick)'}]
    original_pine = '/*backtest\nstart: 2023-08-17 00:00:00\nend: 2023-09-16 00:00:00\nperiod: 2h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=3\nstrategy("lokendra Reversal Strategy", overlay=true)\n\nleftBars = input(4)\nrightBars = input(2)\n\nswh = pivothigh(leftBars, rightBars)\nswl = pivotlow(leftBars, rightBars)\n\nswh_cond = not na(swh)\n\nhprice = 0.0\nhprice := swh_cond ? swh : hprice[1]\n\nle = false\nle := swh_cond ? true : (le[1] and high > hprice ? false : le[1])\n\nif (le)\n    strategy.entry("PivRevLE", strategy.long, comment="BUY**", stop=hprice + syminfo.mintick)\n\nswl_cond = not na(swl)\n\nlprice = 0.0\nlprice := swl_cond ? swl : lprice[1]\n\n\nse = false\nse := swl_cond ? true : (se[1] and low < lprice ? false : se[1])\n\nif (se)\n    strategy.entry("PivRevSE", strategy.short, comment="SELL**", stop=lprice - syminfo.mintick)\n\n//plot(strategy.equity, title="equity", color=red, linewidth=2, style=areabr)'

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
