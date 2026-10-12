"""Source-faithful deep-assisted port of 极值反转追踪策略Extremum-Reversion-Tracking-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_7f045a2d(PinePortBase, IStrategy):
    source_file = '极值反转追踪策略Extremum-Reversion-Tracking-Strategy.md'
    timeframe = '6h'
    can_short = True
    source_defaults = {'needlong': True, 'needshort': False, 'capital': 100, 'tf': 'W', 'fromyear': 1900, 'toyear': 2100, 'frommonth': 1, 'tomonth': 12, 'fromday': 1, 'today': 31}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 100.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['request.security', 'strategy.entry', 'strategy.close', 'strategy.position_size', 'strategy.equity', 'for ']
    source_fidelity_notes = ['Uses request.security / multi-timeframe context; exact parity depends on HTF resampling, gaps and lookahead semantics.', 'Reads broker/strategy state; signals depend on fill timing and cannot be reduced to indicator-only booleans without changing behavior.']
    pine_assignments = [{'mode': '', 'name': 'needlong', 'op': '=', 'expr': 'input(true, defval = true, title = "Long")', 'conditions': []}, {'mode': '', 'name': 'needshort', 'op': '=', 'expr': 'input(false, defval = false, title = "Short")', 'conditions': []}, {'mode': '', 'name': 'capital', 'op': '=', 'expr': 'input(100, defval = 100, minval = 1, maxval = 10000, title = "Capital, %")', 'conditions': []}, {'mode': '', 'name': 'tf', 'op': '=', 'expr': "input('W', title = 'Timeframe for extremums')", 'conditions': []}, {'mode': '', 'name': 'fromyear', 'op': '=', 'expr': 'input(1900, defval = 1900, minval = 1900, maxval = 2100, title = "From Year")', 'conditions': []}, {'mode': '', 'name': 'toyear', 'op': '=', 'expr': 'input(2100, defval = 2100, minval = 1900, maxval = 2100, title = "To Year")', 'conditions': []}, {'mode': '', 'name': 'frommonth', 'op': '=', 'expr': 'input(01, defval = 01, minval = 01, maxval = 12, title = "From Month")', 'conditions': []}, {'mode': '', 'name': 'tomonth', 'op': '=', 'expr': 'input(12, defval = 12, minval = 01, maxval = 12, title = "To Month")', 'conditions': []}, {'mode': '', 'name': 'fromday', 'op': '=', 'expr': 'input(01, defval = 01, minval = 01, maxval = 31, title = "From day")', 'conditions': []}, {'mode': '', 'name': 'today', 'op': '=', 'expr': 'input(31, defval = 31, minval = 01, maxval = 31, title = "To day")', 'conditions': []}, {'mode': '', 'name': 'highm', 'op': '=', 'expr': 'request.security(syminfo.tickerid, tf, high[1])', 'conditions': []}, {'mode': '', 'name': 'lowm', 'op': '=', 'expr': 'request.security(syminfo.tickerid, tf, low[1])', 'conditions': []}, {'mode': '', 'name': 'upcolorm', 'op': '=', 'expr': 'highm == highm[1] ? lime : na', 'conditions': []}, {'mode': '', 'name': 'dncolorm', 'op': '=', 'expr': 'lowm == lowm[1] ? red : na', 'conditions': []}, {'mode': '', 'name': 'size', 'op': '=', 'expr': 'strategy.position_size', 'conditions': []}, {'mode': '', 'name': 'up', 'op': '=', 'expr': 'size > 0 ? highm * 1000000 : highm != highm[1] ? highm : up[1]', 'conditions': []}, {'mode': '', 'name': 'dn', 'op': '=', 'expr': 'size < 0 ? 0 : lowm != lowm[1] ? lowm : dn[1]', 'conditions': []}, {'mode': '', 'name': 'exit', 'op': '=', 'expr': 'true', 'conditions': []}, {'mode': '', 'name': 'lot', 'op': '=', 'expr': 'strategy.position_size != strategy.position_size[1] ? strategy.equity / close * capital / 100 : lot[1]', 'conditions': []}]
    pine_user_functions = []
    pine_controls = [{'indent': 0, 'statement': 'if highm > 0 and high[1] < highm and highm == highm[1]'}, {'indent': 0, 'statement': 'if lowm > 0 and low[1] > lowm and lowm == lowm[1]'}, {'indent': 0, 'statement': 'if exit'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("Long", strategy.long, needlong == false ? 0 : lot, stop = up)', 'conditions': ['highm > 0 and high[1] < highm and highm == highm[1]'], 'statement': 'strategy.entry("Long", strategy.long, needlong == false ? 0 : lot, stop = up)'}, {'kind': 'entry', 'call': 'strategy.entry("Short", strategy.short, needshort == false ? 0 : lot, stop = dn)', 'conditions': ['lowm > 0 and low[1] > lowm and lowm == lowm[1]'], 'statement': 'strategy.entry("Short", strategy.short, needshort == false ? 0 : lot, stop = dn)'}, {'kind': 'close_all', 'call': 'strategy.close_all()', 'conditions': ['exit'], 'statement': 'strategy.close_all()'}]
    original_pine = '/*backtest\nstart: 2024-01-01 00:00:00\nend: 2024-01-31 23:59:59\nperiod: 6h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//Noro\n//2018\n\n//@version=2\nstrategy(title = "Noro\'s Extremum Strategy v1.0", shorttitle = "Extremum str 1.0", overlay = true, default_qty_type = strategy.percent_of_equity, default_qty_value = 100, pyramiding = 0)\n\n//Settings\nneedlong = input(true, defval = true, title = "Long")\nneedshort = input(false, defval = false, title = "Short")\ncapital = input(100, defval = 100, minval = 1, maxval = 10000, title = "Capital, %")\ntf = input(\'W\', title = \'Timeframe for extremums\')\nfromyear = input(1900, defval = 1900, minval = 1900, maxval = 2100, title = "From Year")\ntoyear = input(2100, defval = 2100, minval = 1900, maxval = 2100, title = "To Year")\nfrommonth = input(01, defval = 01, minval = 01, maxval = 12, title = "From Month")\ntomonth = input(12, defval = 12, minval = 01, maxval = 12, title = "To Month")\nfromday = input(01, defval = 01, minval = 01, maxval = 31, title = "From day")\ntoday = input(31, defval = 31, minval = 01, maxval = 31, title = "To day")\n\n//Levels\nhighm = request.security(syminfo.tickerid, tf, high[1])\nlowm = request.security(syminfo.tickerid, tf, low[1])\nupcolorm = highm == highm[1] ? lime : na\ndncolorm = lowm == lowm[1] ? red : na\nplot(highm, color = upcolorm, linewidth = 3)\nplot(lowm, color = dncolorm, linewidth = 3)\n\n//Signals\nsize = strategy.position_size\nup = size > 0 ? highm * 1000000 : highm != highm[1] ? highm : up[1]\ndn = size < 0 ? 0 : lowm != lowm[1] ? lowm : dn[1]\nexit = true\n\n//Trading\nlot = strategy.position_size != strategy.position_size[1] ? strategy.equity / close * capital / 100 : lot[1]\n\nif highm > 0 and high[1] < highm and highm == highm[1]\n    strategy.entry("Long", strategy.long, needlong == false ? 0 : lot, stop = up)\n    \nif lowm > 0 and low[1] > lowm and lowm == lowm[1]\n    strategy.entry("Short", strategy.short, needshort == false ? 0 : lot, stop = dn)\n\nif exit\n    strategy.close_all()'

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
