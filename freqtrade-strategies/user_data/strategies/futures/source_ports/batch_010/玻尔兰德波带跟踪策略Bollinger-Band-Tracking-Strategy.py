"""Source-faithful deep-assisted port of 玻尔兰德波带跟踪策略Bollinger-Band-Tracking-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_a4990e2b(PinePortBase, IStrategy):
    source_file = '玻尔兰德波带跟踪策略Bollinger-Band-Tracking-Strategy.md'
    timeframe = '2h'
    can_short = False
    source_defaults = {'len': 20, 'src': 'close', 'mult': 2.0, 'trail': True, 'stop': 10000, 'limit': 20000, 'revt': True, 'timec': False, 'sess': '1600-0500'}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_pyramiding = 0
    source_initial_capital = 25000.0
    source_commission_percent = 3.02
    source_features = ['strategy.exit', 'strategy.entry', 'timeframe.']
    source_fidelity_notes = ['Uses strategy.exit; stop/limit/profit/loss/trailing arguments have Pine order semantics and may fill intrabar.']
    pine_assignments = [{'mode': '', 'name': 'len', 'op': '=', 'expr': 'input(20, minval=1, title="Length")', 'conditions': []}, {'mode': '', 'name': 'src', 'op': '=', 'expr': 'input(close, title="Source")', 'conditions': []}, {'mode': '', 'name': 'mult', 'op': '=', 'expr': 'input(2.0, "Deviation", minval=0.001, maxval=50)', 'conditions': []}, {'mode': '', 'name': 'trail', 'op': '=', 'expr': 'input(true, "Trailing Stop(checked), Market stop(unchecked)")', 'conditions': []}, {'mode': '', 'name': 'stop', 'op': '=', 'expr': 'input(10000, "Stop (in ticks)", step=5)', 'conditions': []}, {'mode': '', 'name': 'limit', 'op': '=', 'expr': 'input(20000, "Limit Out", step=5)', 'conditions': []}, {'mode': '', 'name': 'revt', 'op': '=', 'expr': 'input(true, "Reversal Entry(checked, Trend Entry(unchecked)")', 'conditions': []}, {'mode': '', 'name': 'timec', 'op': '=', 'expr': 'input(false, "Limit Time of Day (Buying Side)")', 'conditions': []}, {'mode': '', 'name': 'revti', 'op': '=', 'expr': 'if revt==false', 'conditions': []}, {'mode': '', 'name': 'basis', 'op': '=', 'expr': 'wma(src, len)', 'conditions': []}, {'mode': '', 'name': 'dev', 'op': '=', 'expr': 'mult * stdev(src, len)', 'conditions': []}, {'mode': '', 'name': 'upper', 'op': '=', 'expr': 'basis + dev', 'conditions': []}, {'mode': '', 'name': 'lower', 'op': '=', 'expr': 'basis - dev', 'conditions': []}, {'mode': '', 'name': 'p1', 'op': '=', 'expr': 'plot(upper, color=teal)', 'conditions': []}, {'mode': '', 'name': 'p2', 'op': '=', 'expr': 'plot(lower, color=teal)', 'conditions': []}, {'mode': '', 'name': 'u', 'op': '=', 'expr': 'crossover(high, upper)', 'conditions': []}, {'mode': '', 'name': 'd', 'op': '=', 'expr': 'crossunder(low, lower)', 'conditions': []}, {'mode': '', 'name': 'sess', 'op': '=', 'expr': 'input("1600-0500", "Start/Stop trades (Est time)")', 'conditions': []}, {'mode': '', 'name': 't', 'op': '=', 'expr': 'time(timeframe.period, sess)', 'conditions': []}]
    pine_user_functions = []
    pine_controls = [{'indent': 0, 'statement': 'if(timec)'}, {'indent': 0, 'statement': 'else'}, {'indent': 0, 'statement': 'if(trail)'}, {'indent': 0, 'statement': 'else'}, {'indent': 0, 'statement': 'if(timec)'}, {'indent': 0, 'statement': 'else'}, {'indent': 0, 'statement': 'if(trail)'}, {'indent': 0, 'statement': 'else'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("Enterlong", long=revt, when=d and t>1)', 'conditions': [], 'statement': 'strategy.entry("Enterlong", long=revt, when=d and t>1)'}, {'kind': 'entry', 'call': 'strategy.entry("Enterlong", long=revt, when=d)', 'conditions': ['ELSE'], 'statement': 'strategy.entry("Enterlong", long=revt, when=d)'}, {'kind': 'exit', 'call': 'strategy.exit("Exit","Enterlong", profit=limit, trail_points = 0, trail_offset = stop )', 'conditions': [], 'statement': 'strategy.exit("Exit","Enterlong", profit=limit, trail_points = 0, trail_offset = stop )'}, {'kind': 'exit', 'call': 'strategy.exit("Exit","Enterlong", profit=limit, loss = stop )', 'conditions': ['ELSE'], 'statement': 'strategy.exit("Exit","Enterlong", profit=limit, loss = stop )'}, {'kind': 'entry', 'call': 'strategy.entry("Entershort", long=revti, when=u and t>1)', 'conditions': [], 'statement': 'strategy.entry("Entershort", long=revti, when=u and t>1)'}, {'kind': 'entry', 'call': 'strategy.entry("Entershort", long=revti, when=u)', 'conditions': ['ELSE'], 'statement': 'strategy.entry("Entershort", long=revti, when=u)'}, {'kind': 'exit', 'call': 'strategy.exit("Exit","Entershort", profit=limit, trail_points = 0, trail_offset = stop )', 'conditions': [], 'statement': 'strategy.exit("Exit","Entershort", profit=limit, trail_points = 0, trail_offset = stop )'}, {'kind': 'exit', 'call': 'strategy.exit("Exit","Entershort", profit=limit, loss = stop )', 'conditions': ['ELSE'], 'statement': 'strategy.exit("Exit","Entershort", profit=limit, loss = stop )'}]
    original_pine = '/*backtest\nstart: 2024-02-19 00:00:00\nend: 2024-02-26 00:00:00\nperiod: 2h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=4\nstrategy(title="BB Strategy (Basic)",overlay=true, initial_capital=25000, default_qty_value=1, commission_type=strategy.commission.cash_per_contract, commission_value=3.02)\nlen = input(20, minval=1, title="Length")\nsrc = input(close, title="Source")\nmult = input(2.0, "Deviation", minval=0.001, maxval=50)\n//price_drop = input(.003, "When price drops (In Ticks) Enter Long", step=.001)\n//price_climb = input(.003, "When price climbs (In Ticks) Enter Short", step=.001)\ntrail = input(true, "Trailing Stop(checked), Market stop(unchecked)")\nstop = input(10000, "Stop (in ticks)", step=5)\nlimit = input(20000, "Limit Out", step=5)\n//size = input(1, "Limit Position Size (pyramiding)", minval=1)\nrevt = input(true, "Reversal Entry(checked, Trend Entry(unchecked)")\ntimec = input(false, "Limit Time of Day (Buying Side)")\n\n//calculations and plots\nrevti = if revt==false\n    true\nbasis = wma(src, len)\ndev = mult * stdev(src, len)\nupper = basis + dev\nlower = basis - dev\nplot(basis, color=red)\np1 = plot(upper, color=teal)\np2 = plot(lower, color=teal)\nfill(p1, p2)\nu = crossover(high, upper) \nd = crossunder(low, lower)\n//Time Session\nsess = input("1600-0500", "Start/Stop trades (Est time)")\nt = time(timeframe.period, sess)\n\n//Orders\nif(timec)\n    strategy.entry("Enterlong", long=revt, when=d and t>1)\nelse\n    strategy.entry("Enterlong", long=revt, when=d)\nif(trail)\n    strategy.exit("Exit","Enterlong", profit=limit, trail_points = 0, trail_offset = stop )\nelse\n    strategy.exit("Exit","Enterlong", profit=limit, loss = stop )\n    \nif(timec)\n    strategy.entry("Entershort", long=revti, when=u and t>1)\nelse\n    strategy.entry("Entershort", long=revti, when=u)\nif(trail)\n    strategy.exit("Exit","Entershort", profit=limit, trail_points = 0, trail_offset = stop )\nelse\n    strategy.exit("Exit","Entershort", profit=limit, loss = stop )'

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
