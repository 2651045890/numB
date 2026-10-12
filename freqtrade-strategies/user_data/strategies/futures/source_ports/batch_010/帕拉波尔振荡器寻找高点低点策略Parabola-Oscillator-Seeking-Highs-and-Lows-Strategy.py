"""Source-faithful deep-assisted port of 帕拉波尔振荡器寻找高点低点策略Parabola-Oscillator-Seeking-Highs-and-Lows-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_52977e23(PinePortBase, IStrategy):
    source_file = '帕拉波尔振荡器寻找高点低点策略Parabola-Oscillator-Seeking-Highs-and-Lows-Strategy.md'
    timeframe = '12h'
    can_short = True
    source_defaults = {}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.entry']
    source_fidelity_notes = []
    pine_assignments = [{'mode': '', 'name': 'a1', 'op': '=', 'expr': '(close[2]-close[3])/1', 'conditions': []}, {'mode': '', 'name': 'a2', 'op': '=', 'expr': '(close[1]-close[3])/4', 'conditions': []}, {'mode': '', 'name': 'a3', 'op': '=', 'expr': '(close[0]-close[3])/9', 'conditions': []}, {'mode': '', 'name': 'b1', 'op': '=', 'expr': '(close[3]-close[4])/1', 'conditions': []}, {'mode': '', 'name': 'b2', 'op': '=', 'expr': '(close[2]-close[4])/4', 'conditions': []}, {'mode': '', 'name': 'b3', 'op': '=', 'expr': '(close[1]-close[4])/9', 'conditions': []}, {'mode': '', 'name': 'b4', 'op': '=', 'expr': '(close[0]-close[4])/16', 'conditions': []}, {'mode': '', 'name': 'c1', 'op': '=', 'expr': '(close[4]-close[5])/1', 'conditions': []}, {'mode': '', 'name': 'c2', 'op': '=', 'expr': '(close[3]-close[5])/4', 'conditions': []}, {'mode': '', 'name': 'c3', 'op': '=', 'expr': '(close[2]-close[5])/9', 'conditions': []}, {'mode': '', 'name': 'c4', 'op': '=', 'expr': '(close[1]-close[5])/16', 'conditions': []}, {'mode': '', 'name': 'c5', 'op': '=', 'expr': '(close[0]-close[5])/25', 'conditions': []}, {'mode': '', 'name': 'ma', 'op': '=', 'expr': '(a1+a2+a3)/3', 'conditions': []}, {'mode': '', 'name': 'da', 'op': '=', 'expr': '(a1-ma)*(a1-ma)', 'conditions': []}, {'mode': '', 'name': 'da', 'op': ':=', 'expr': 'da+(a2-ma)*(a2-ma)', 'conditions': []}, {'mode': '', 'name': 'da', 'op': ':=', 'expr': 'da+(a3-ma)*(a3-ma)', 'conditions': []}, {'mode': '', 'name': 'da', 'op': ':=', 'expr': 'sqrt(da)', 'conditions': []}, {'mode': '', 'name': 'da', 'op': ':=', 'expr': 'min(2, da)', 'conditions': []}, {'mode': '', 'name': 'da', 'op': ':=', 'expr': '1-da/2', 'conditions': []}, {'mode': '', 'name': 'da', 'op': ':=', 'expr': 'max(0.001, da)', 'conditions': []}, {'mode': '', 'name': 'mb', 'op': '=', 'expr': '(b1+b2+b3+b4)/4', 'conditions': []}, {'mode': '', 'name': 'db', 'op': '=', 'expr': '(b1-mb)*(b1-mb)', 'conditions': []}, {'mode': '', 'name': 'db', 'op': ':=', 'expr': 'db+(b2-mb)*(b2-mb)', 'conditions': []}, {'mode': '', 'name': 'db', 'op': ':=', 'expr': 'db+(b3-mb)*(b3-mb)', 'conditions': []}, {'mode': '', 'name': 'db', 'op': ':=', 'expr': 'db+(b4-mb)*(b4-mb)', 'conditions': []}, {'mode': '', 'name': 'db', 'op': ':=', 'expr': 'sqrt(db)', 'conditions': []}, {'mode': '', 'name': 'db', 'op': ':=', 'expr': 'min(2, db)', 'conditions': []}, {'mode': '', 'name': 'db', 'op': ':=', 'expr': '1-db/2', 'conditions': []}, {'mode': '', 'name': 'db', 'op': ':=', 'expr': 'max(0.001, db)', 'conditions': []}, {'mode': '', 'name': 'mc', 'op': '=', 'expr': '(c1+c2+c3+c4+c5)/5', 'conditions': []}, {'mode': '', 'name': 'dc', 'op': '=', 'expr': '(c1-mc)*(c1-mc)', 'conditions': []}, {'mode': '', 'name': 'dc', 'op': ':=', 'expr': 'dc+(c2-mc)*(c2-mc)', 'conditions': []}, {'mode': '', 'name': 'dc', 'op': ':=', 'expr': 'dc+(c3-mc)*(c3-mc)', 'conditions': []}, {'mode': '', 'name': 'dc', 'op': ':=', 'expr': 'dc+(c4-mc)*(c4-mc)', 'conditions': []}, {'mode': '', 'name': 'dc', 'op': ':=', 'expr': 'dc+(c5-mc)*(c5-mc)', 'conditions': []}, {'mode': '', 'name': 'dc', 'op': ':=', 'expr': 'sqrt(dc)', 'conditions': []}, {'mode': '', 'name': 'dc', 'op': ':=', 'expr': 'min(2, dc)', 'conditions': []}, {'mode': '', 'name': 'dc', 'op': ':=', 'expr': '1-dc/2', 'conditions': []}, {'mode': '', 'name': 'dc', 'op': ':=', 'expr': 'max(0.001, dc)', 'conditions': []}, {'mode': '', 'name': 'g', 'op': '=', 'expr': 'close', 'conditions': []}, {'mode': '', 'name': 'g', 'op': ':=', 'expr': 'da*da*ma', 'conditions': []}, {'mode': '', 'name': 'g', 'op': ':=', 'expr': 'db*db*mb', 'conditions': ['ELSE']}, {'mode': '', 'name': 'g', 'op': ':=', 'expr': 'dc*dc*mc', 'conditions': ['ELSE', 'ELSE']}, {'mode': '', 'name': 'wg', 'op': '=', 'expr': 'wma(g, 2)', 'conditions': []}, {'mode': '', 'name': 'longCondition', 'op': '=', 'expr': 'true //crossover(sma(close, 14), sma(close, 28))', 'conditions': []}, {'mode': '', 'name': 'shortCondition', 'op': '=', 'expr': 'true //crossunder(sma(close, 14), sma(close, 28))', 'conditions': []}]
    pine_user_functions = []
    pine_controls = [{'indent': 0, 'statement': 'if(da>db and da>dc)'}, {'indent': 0, 'statement': 'else'}, {'indent': 4, 'statement': 'if(db > da and db > dc)'}, {'indent': 4, 'statement': 'else'}, {'indent': 0, 'statement': 'if (longCondition)'}, {'indent': 0, 'statement': 'if (shortCondition)'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("My Long Entry Id", strategy.long)', 'conditions': ['(longCondition)'], 'statement': 'strategy.entry("My Long Entry Id", strategy.long)'}, {'kind': 'entry', 'call': 'strategy.entry("My Short Entry Id", strategy.short)', 'conditions': ['(shortCondition)'], 'statement': 'strategy.entry("My Short Entry Id", strategy.short)'}]
    original_pine = '/*backtest\nstart: 2024-02-12 00:00:00\nend: 2024-02-19 00:00:00\nperiod: 12h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=3\nstrategy("x²", overlay=false)\n\n\na1=(close[2]-close[3])/1\na2=(close[1]-close[3])/4\na3=(close[0]-close[3])/9\n\nb1=(close[3]-close[4])/1\nb2=(close[2]-close[4])/4\nb3=(close[1]-close[4])/9\nb4=(close[0]-close[4])/16\n\nc1=(close[4]-close[5])/1\nc2=(close[3]-close[5])/4\nc3=(close[2]-close[5])/9\nc4=(close[1]-close[5])/16\nc5=(close[0]-close[5])/25\n\nma=(a1+a2+a3)/3\nda=(a1-ma)*(a1-ma)\nda:=da+(a2-ma)*(a2-ma)\nda:=da+(a3-ma)*(a3-ma)\nda:=sqrt(da)\nda:=min(2, da)\nda:=1-da/2\nda:=max(0.001, da)\n\n\nmb=(b1+b2+b3+b4)/4\ndb=(b1-mb)*(b1-mb)\ndb:=db+(b2-mb)*(b2-mb)\ndb:=db+(b3-mb)*(b3-mb)\ndb:=db+(b4-mb)*(b4-mb)\ndb:=sqrt(db)\ndb:=min(2, db)\ndb:=1-db/2\ndb:=max(0.001, db)\n\nmc=(c1+c2+c3+c4+c5)/5\ndc=(c1-mc)*(c1-mc)\ndc:=dc+(c2-mc)*(c2-mc)\ndc:=dc+(c3-mc)*(c3-mc)\ndc:=dc+(c4-mc)*(c4-mc)\ndc:=dc+(c5-mc)*(c5-mc)\ndc:=sqrt(dc)\ndc:=min(2, dc)\ndc:=1-dc/2\ndc:=max(0.001, dc)\n\n\n\ng=close\nif(da>db and da>dc)\n    g:=da*da*ma\nelse\n    if(db > da and db > dc)\n        g:=db*db*mb\n    else\n        g:=dc*dc*mc\n\nwg=wma(g, 2)\nplot(wg)\nplot(0, color=black)\n\n\nlongCondition = true //crossover(sma(close, 14), sma(close, 28))\nif (longCondition)\n    strategy.entry("My Long Entry Id", strategy.long)\n\nshortCondition = true //crossunder(sma(close, 14), sma(close, 28))\nif (shortCondition)\n    strategy.entry("My Short Entry Id", strategy.short)'

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
