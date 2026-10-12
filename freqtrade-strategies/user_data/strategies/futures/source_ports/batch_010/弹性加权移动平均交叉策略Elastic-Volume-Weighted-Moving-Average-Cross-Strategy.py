"""Source-faithful deep-assisted port of 弹性加权移动平均交叉策略Elastic-Volume-Weighted-Moving-Average-Cross-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_02b4a7e4(PinePortBase, IStrategy):
    source_file = '弹性加权移动平均交叉策略Elastic-Volume-Weighted-Moving-Average-Cross-Strategy.md'
    timeframe = '2h'
    can_short = True
    source_defaults = {'length1': 5, 'length2': 40}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.entry', '=>']
    source_fidelity_notes = []
    pine_assignments = [{'mode': '', 'name': 'length1', 'op': '=', 'expr': 'input(5, title="EVWMA Short")', 'conditions': []}, {'mode': '', 'name': 'length2', 'op': '=', 'expr': 'input(40, title="EVWMA Long")', 'conditions': []}, {'mode': '', 'name': 'nbfs1', 'op': '=', 'expr': 'sum(volume, length1)', 'conditions': []}, {'mode': '', 'name': 'nbfs2', 'op': '=', 'expr': 'sum(volume, length2)', 'conditions': []}, {'mode': '', 'name': 'medianSrc', 'op': '=', 'expr': 'close', 'conditions': []}, {'mode': '', 'name': 'data', 'op': '=', 'expr': '(nz(data[1]) * (nb_floating_shares - volume)/nb_floating_shares) + (volume*price/nb_floating_shares)', 'conditions': []}, {'mode': '', 'name': 'm1', 'op': '=', 'expr': 'calc_evwma(medianSrc, length1, nbfs1)', 'conditions': []}, {'mode': '', 'name': 'm2', 'op': '=', 'expr': 'calc_evwma(medianSrc, length2, nbfs2)', 'conditions': []}, {'mode': '', 'name': 'p1', 'op': '=', 'expr': 'plot(m1,color=orange,linewidth=2, title="evwma")', 'conditions': []}, {'mode': '', 'name': 'p2', 'op': '=', 'expr': 'plot(m2,color=orange,linewidth=2, title="evwma")', 'conditions': []}]
    pine_user_functions = [{'name': 'calc_evwma', 'args': 'price, length, nb_floating_shares', 'body': ''}]
    pine_controls = [{'indent': 0, 'statement': 'if (crossover(m1, m2))'}, {'indent': 0, 'statement': 'if (crossunder(m1, m2))'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("MA2CrossLE", strategy.long, comment="MA2CrossLE")', 'conditions': ['(crossover(m1, m2))'], 'statement': 'strategy.entry("MA2CrossLE", strategy.long, comment="MA2CrossLE")'}, {'kind': 'entry', 'call': 'strategy.entry("MA2CrossSE", strategy.short, comment="MA2CrossSE")', 'conditions': ['(crossunder(m1, m2))'], 'statement': 'strategy.entry("MA2CrossSE", strategy.short, comment="MA2CrossSE")'}]
    original_pine = '/*backtest\nstart: 2023-08-18 00:00:00\nend: 2023-08-26 00:00:00\nperiod: 2h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=2\n\nstrategy("Elastic Volume Weighted Moving Average Cross Strategy", shorttitle="EVWMA Cross", overlay=true)\nlength1=input(5, title="EVWMA Short")\nlength2=input(40, title="EVWMA Long")\n\nnbfs1=sum(volume, length1)\nnbfs2=sum(volume, length2)\n\nmedianSrc=close\n\ncalc_evwma(price, length, nb_floating_shares) => \n    data = (nz(data[1]) * (nb_floating_shares - volume)/nb_floating_shares) + (volume*price/nb_floating_shares)\n    data\n    \n\nm1=calc_evwma(medianSrc, length1, nbfs1)\nm2=calc_evwma(medianSrc, length2, nbfs2)\n\nif (crossover(m1, m2))\n    strategy.entry("MA2CrossLE", strategy.long, comment="MA2CrossLE")\n\nif (crossunder(m1, m2))\n    strategy.entry("MA2CrossSE", strategy.short, comment="MA2CrossSE")\n\np1=plot(m1,color=orange,linewidth=2, title="evwma")\np2=plot(m2,color=orange,linewidth=2, title="evwma")'

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
