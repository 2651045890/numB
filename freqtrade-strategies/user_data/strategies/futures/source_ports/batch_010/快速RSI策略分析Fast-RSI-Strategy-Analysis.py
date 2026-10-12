"""Source-faithful deep-assisted port of 快速RSI策略分析Fast-RSI-Strategy-Analysis.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_b2a82982(PinePortBase, IStrategy):
    source_file = '快速RSI策略分析Fast-RSI-Strategy-Analysis.md'
    timeframe = '1h'
    can_short = True
    source_defaults = {'needlong': True, 'needshort': True, 'rsiperiod': 7, 'limit': 30, 'rsisrc': 'close', 'fromyear': 2018, 'toyear': 2100, 'frommonth': 1, 'tomonth': 12, 'fromday': 1, 'today': 31}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 100.0
    source_pyramiding = 5
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.entry', 'strategy.close', 'strategy.position_size']
    source_fidelity_notes = ['Reads broker/strategy state; signals depend on fill timing and cannot be reduced to indicator-only booleans without changing behavior.']
    pine_assignments = [{'mode': '', 'name': 'needlong', 'op': '=', 'expr': 'input(true, defval = true, title = "Long")', 'conditions': []}, {'mode': '', 'name': 'needshort', 'op': '=', 'expr': 'input(true, defval = true, title = "Short")', 'conditions': []}, {'mode': '', 'name': 'rsiperiod', 'op': '=', 'expr': 'input(7, defval = 7, minval = 2, maxval = 50, title = "RSI Period")', 'conditions': []}, {'mode': '', 'name': 'limit', 'op': '=', 'expr': 'input(30, defval = 30, minval = 1, maxval = 100, title = "RSI limit")', 'conditions': []}, {'mode': '', 'name': 'rsisrc', 'op': '=', 'expr': 'input(close, defval = close, title = "RSI Source")', 'conditions': []}, {'mode': '', 'name': 'fromyear', 'op': '=', 'expr': 'input(2018, defval = 2018, minval = 1900, maxval = 2100, title = "From Year")', 'conditions': []}, {'mode': '', 'name': 'toyear', 'op': '=', 'expr': 'input(2100, defval = 2100, minval = 1900, maxval = 2100, title = "To Year")', 'conditions': []}, {'mode': '', 'name': 'frommonth', 'op': '=', 'expr': 'input(01, defval = 01, minval = 01, maxval = 12, title = "From Month")', 'conditions': []}, {'mode': '', 'name': 'tomonth', 'op': '=', 'expr': 'input(12, defval = 12, minval = 01, maxval = 12, title = "To Month")', 'conditions': []}, {'mode': '', 'name': 'fromday', 'op': '=', 'expr': 'input(01, defval = 01, minval = 01, maxval = 31, title = "From day")', 'conditions': []}, {'mode': '', 'name': 'today', 'op': '=', 'expr': 'input(31, defval = 31, minval = 01, maxval = 31, title = "To day")', 'conditions': []}, {'mode': '', 'name': 'fastup', 'op': '=', 'expr': 'rma(max(change(rsisrc), 0), rsiperiod)', 'conditions': []}, {'mode': '', 'name': 'fastdown', 'op': '=', 'expr': 'rma(-min(change(rsisrc), 0), rsiperiod)', 'conditions': []}, {'mode': '', 'name': 'fastrsi', 'op': '=', 'expr': 'fastdown == 0 ? 100 : fastup == 0 ? 0 : 100 - (100 / (1 + fastup / fastdown))', 'conditions': []}, {'mode': '', 'name': 'uplimit', 'op': '=', 'expr': '100 - limit', 'conditions': []}, {'mode': '', 'name': 'dnlimit', 'op': '=', 'expr': 'limit', 'conditions': []}, {'mode': '', 'name': 'body', 'op': '=', 'expr': 'abs(close - open)', 'conditions': []}, {'mode': '', 'name': 'emabody', 'op': '=', 'expr': 'ema(body, 30) / 3', 'conditions': []}, {'mode': '', 'name': 'bar', 'op': '=', 'expr': 'close > open ? 1 : close < open ? -1 : 0', 'conditions': []}, {'mode': '', 'name': 'up', 'op': '=', 'expr': 'bar == -1 and fastrsi < dnlimit and body > emabody', 'conditions': []}, {'mode': '', 'name': 'dn', 'op': '=', 'expr': 'bar == 1 and fastrsi > uplimit and body > emabody', 'conditions': []}, {'mode': '', 'name': 'exit', 'op': '=', 'expr': '((strategy.position_size > 0 and fastrsi > dnlimit) or (strategy.position_size < 0 and fastrsi < uplimit)) and body > emabody', 'conditions': []}]
    pine_user_functions = []
    pine_controls = [{'indent': 0, 'statement': 'if up'}, {'indent': 0, 'statement': 'if dn'}, {'indent': 0, 'statement': 'if time > timestamp(toyear, tomonth, today, 00, 00) or exit'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("Long", strategy.long, needlong == false ? 0 : na, when=(time > timestamp(fromyear, frommonth, fromday, 00, 00) and time < timestamp(toyear, tomonth, today, 00, 00)))', 'conditions': ['up'], 'statement': 'strategy.entry("Long", strategy.long, needlong == false ? 0 : na, when=(time > timestamp(fromyear, frommonth, fromday, 00, 00) and time < timestamp(toyear, tomonth, today, 00, 00)))'}, {'kind': 'entry', 'call': 'strategy.entry("Short", strategy.short, needshort == false ? 0 : na, when=(time > timestamp(fromyear, frommonth, fromday, 00, 00) and time < timestamp(toyear, tomonth, today, 00, 00)))', 'conditions': ['dn'], 'statement': 'strategy.entry("Short", strategy.short, needshort == false ? 0 : na, when=(time > timestamp(fromyear, frommonth, fromday, 00, 00) and time < timestamp(toyear, tomonth, today, 00, 00)))'}, {'kind': 'close_all', 'call': 'strategy.close_all()', 'conditions': ['time > timestamp(toyear, tomonth, today, 00, 00) or exit'], 'statement': 'strategy.close_all()'}]
    original_pine = '/*backtest\nstart: 2023-11-03 00:00:00\nend: 2023-12-03 00:00:00\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=3\nstrategy(title = "Noro\'s Fast RSI Strategy v1.1", shorttitle = "Fast RSI str 1.1", overlay = true, default_qty_type = strategy.percent_of_equity, default_qty_value = 100, pyramiding = 5)\n\n//Settings\nneedlong = input(true, defval = true, title = "Long")\nneedshort = input(true, defval = true, title = "Short")\nrsiperiod = input(7, defval = 7, minval = 2, maxval = 50, title = "RSI Period")\nlimit = input(30, defval = 30, minval = 1, maxval = 100, title = "RSI limit")\nrsisrc = input(close, defval = close, title = "RSI Source")\nfromyear = input(2018, defval = 2018, minval = 1900, maxval = 2100, title = "From Year")\ntoyear = input(2100, defval = 2100, minval = 1900, maxval = 2100, title = "To Year")\nfrommonth = input(01, defval = 01, minval = 01, maxval = 12, title = "From Month")\ntomonth = input(12, defval = 12, minval = 01, maxval = 12, title = "To Month")\nfromday = input(01, defval = 01, minval = 01, maxval = 31, title = "From day")\ntoday = input(31, defval = 31, minval = 01, maxval = 31, title = "To day")\n\n//Fast RSI\nfastup = rma(max(change(rsisrc), 0), rsiperiod)\nfastdown = rma(-min(change(rsisrc), 0), rsiperiod)\nfastrsi = fastdown == 0 ? 100 : fastup == 0 ? 0 : 100 - (100 / (1 + fastup / fastdown))\nuplimit = 100 - limit\ndnlimit = limit\n\n//Body\nbody = abs(close - open)\nemabody = ema(body, 30) / 3\n\n//Signals\nbar = close > open ? 1 : close < open ? -1 : 0\nup = bar == -1 and fastrsi < dnlimit and body > emabody\ndn = bar == 1 and fastrsi > uplimit and body > emabody\nexit = ((strategy.position_size > 0 and fastrsi > dnlimit) or (strategy.position_size < 0 and fastrsi < uplimit)) and body > emabody\n\n//Trading\nif up\n    strategy.entry("Long", strategy.long, needlong == false ? 0 : na, when=(time > timestamp(fromyear, frommonth, fromday, 00, 00) and time < timestamp(toyear, tomonth, today, 00, 00)))\n\nif dn\n    strategy.entry("Short", strategy.short, needshort == false ? 0 : na, when=(time > timestamp(fromyear, frommonth, fromday, 00, 00) and time < timestamp(toyear, tomonth, today, 00, 00)))\n    \nif time > timestamp(toyear, tomonth, today, 00, 00) or exit\n    strategy.close_all()'

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
