"""Source-faithful deep-assisted port of 快速震荡RSI交易策略Fast-Oscillating-RSI-Trading-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_1be7738d(PinePortBase, IStrategy):
    source_file = '快速震荡RSI交易策略Fast-Oscillating-RSI-Trading-Strategy.md'
    timeframe = '1d'
    can_short = False
    source_defaults = {'uprsiperiod': 2, 'dnrsiperiod': 9, 'limit': 30, 'rsisrc': 'close', 'rb': 1, 'fromyear': 2018, 'toyear': 2018, 'frommonth': 1, 'tomonth': 12, 'fromday': 1, 'today': 31}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.entry', 'strategy.close']
    source_fidelity_notes = []
    pine_assignments = [{'mode': '', 'name': 'uprsiperiod', 'op': '=', 'expr': 'input(2, defval = 2, minval = 2, maxval = 50, title = "RSI UP Period")', 'conditions': []}, {'mode': '', 'name': 'dnrsiperiod', 'op': '=', 'expr': 'input(9, defval = 9, minval = 2, maxval = 50, title = "RSI DN Period")', 'conditions': []}, {'mode': '', 'name': 'limit', 'op': '=', 'expr': 'input(30, defval = 30, minval = 1, maxval = 100, title = "RSI limit")', 'conditions': []}, {'mode': '', 'name': 'rsisrc', 'op': '=', 'expr': 'input(close, defval = close, title = "RSI Price")', 'conditions': []}, {'mode': '', 'name': 'rb', 'op': '=', 'expr': 'input(1, defval = 1, minval = 1, maxval = 5, title = "RSI Bars")', 'conditions': []}, {'mode': '', 'name': 'sps', 'op': '=', 'expr': '0', 'conditions': []}, {'mode': '', 'name': 'fromyear', 'op': '=', 'expr': 'input(2018, defval = 2018, minval = 1900, maxval = 2100, title = "From Year")', 'conditions': []}, {'mode': '', 'name': 'toyear', 'op': '=', 'expr': 'input(2018, defval = 2018, minval = 1900, maxval = 2100, title = "To Year")', 'conditions': []}, {'mode': '', 'name': 'frommonth', 'op': '=', 'expr': 'input(01, defval = 01, minval = 01, maxval = 12, title = "From Month")', 'conditions': []}, {'mode': '', 'name': 'tomonth', 'op': '=', 'expr': 'input(12, defval = 12, minval = 01, maxval = 12, title = "To Month")', 'conditions': []}, {'mode': '', 'name': 'fromday', 'op': '=', 'expr': 'input(01, defval = 01, minval = 01, maxval = 31, title = "From day")', 'conditions': []}, {'mode': '', 'name': 'today', 'op': '=', 'expr': 'input(31, defval = 31, minval = 01, maxval = 31, title = "To day")', 'conditions': []}, {'mode': '', 'name': 'fastup', 'op': '=', 'expr': 'rma(max(change(rsisrc), 0), uprsiperiod)', 'conditions': []}, {'mode': '', 'name': 'fastdown', 'op': '=', 'expr': 'rma(-min(change(rsisrc), 0), dnrsiperiod)', 'conditions': []}, {'mode': '', 'name': 'fastrsi', 'op': '=', 'expr': 'fastdown == 0 ? 100 : fastup == 0 ? 0 : 100 - (100 / (1 + fastup / fastdown))', 'conditions': []}, {'mode': '', 'name': 'bar', 'op': '=', 'expr': 'close > open ? 1 : close < open ? -1 : 0', 'conditions': []}, {'mode': '', 'name': 'uplimit', 'op': '=', 'expr': '100 - limit', 'conditions': []}, {'mode': '', 'name': 'dnlimit', 'op': '=', 'expr': 'limit', 'conditions': []}, {'mode': '', 'name': 'ur', 'op': '=', 'expr': 'fastrsi > uplimit', 'conditions': []}, {'mode': '', 'name': 'dr', 'op': '=', 'expr': 'fastrsi < dnlimit', 'conditions': []}, {'mode': '', 'name': 'uprsi', 'op': '=', 'expr': 'rb == 1 and ur ? 1 : rb == 2 and ur and ur[1] ? 1 : rb == 3 and ur and ur[1] and ur[2] ? 1 : rb == 4 and ur and ur[1] and ur[2] and ur[3] ? 1 : rb == 5 and ur and ur[1] and ur[2] and ur[3] and ur[4] ? 1 : 0', 'conditions': []}, {'mode': '', 'name': 'dnrsi', 'op': '=', 'expr': 'rb == 1 and dr ? 1 : rb == 2 and dr and dr[1] ? 1 : rb == 3 and dr and dr[1] and dr[2] ? 1 : rb == 4 and dr and dr[1] and dr[2] and dr[3] ? 1 : rb == 5 and dr and dr[1] and dr[2] and dr[3] and dr[4] ? 1 : 0', 'conditions': []}, {'mode': '', 'name': 'body', 'op': '=', 'expr': 'abs(close - open)', 'conditions': []}, {'mode': '', 'name': 'emabody', 'op': '=', 'expr': 'ema(body, 30)', 'conditions': []}, {'mode': '', 'name': 'up', 'op': '=', 'expr': 'bar == -1 and sps == 0 and dnrsi and body > emabody / 4', 'conditions': []}, {'mode': '', 'name': 'dn', 'op': '=', 'expr': 'bar == 1 and sps == 0 and uprsi and body > emabody / 4', 'conditions': []}, {'mode': '', 'name': 'exit', 'op': '=', 'expr': 'bar == 1 and fastrsi > dnlimit and body > emabody / 2', 'conditions': []}, {'mode': '', 'name': 'sps', 'op': ':=', 'expr': '1', 'conditions': ['up']}, {'mode': '', 'name': 'sps', 'op': ':=', 'expr': '0', 'conditions': ['exit']}]
    pine_user_functions = []
    pine_controls = [{'indent': 0, 'statement': 'if up'}, {'indent': 0, 'statement': 'if exit'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("Long", strategy.long)', 'conditions': ['up'], 'statement': 'strategy.entry("Long", strategy.long)'}, {'kind': 'close_all', 'call': 'strategy.close_all()', 'conditions': ['exit'], 'statement': 'strategy.close_all()'}]
    original_pine = '/*backtest\nstart: 2023-01-07 00:00:00\nend: 2024-01-07 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=3\nstrategy(title = "Noro\'s FRSI Strategy v1.22", shorttitle = "FRSI str 1.22", overlay = true )\n\n//Settings\nuprsiperiod = input(2, defval = 2, minval = 2, maxval = 50, title = "RSI UP Period")\ndnrsiperiod = input(9, defval = 9, minval = 2, maxval = 50, title = "RSI DN Period")\nlimit = input(30, defval = 30, minval = 1, maxval = 100, title = "RSI limit")\nrsisrc = input(close, defval = close, title = "RSI Price")\nrb = input(1, defval = 1, minval = 1, maxval = 5, title = "RSI Bars")\nsps = 0\nfromyear = input(2018, defval = 2018, minval = 1900, maxval = 2100, title = "From Year")\ntoyear = input(2018, defval = 2018, minval = 1900, maxval = 2100, title = "To Year")\nfrommonth = input(01, defval = 01, minval = 01, maxval = 12, title = "From Month")\ntomonth = input(12, defval = 12, minval = 01, maxval = 12, title = "To Month")\nfromday = input(01, defval = 01, minval = 01, maxval = 31, title = "From day")\ntoday = input(31, defval = 31, minval = 01, maxval = 31, title = "To day")\n\n//Fast RSI\nfastup = rma(max(change(rsisrc), 0), uprsiperiod)\nfastdown = rma(-min(change(rsisrc), 0), dnrsiperiod)\nfastrsi = fastdown == 0 ? 100 : fastup == 0 ? 0 : 100 - (100 / (1 + fastup / fastdown))\n\n//Limits\nbar = close > open ? 1 : close < open ? -1 : 0\nuplimit = 100 - limit\ndnlimit = limit\n\n//RSI Bars\nur = fastrsi > uplimit\ndr = fastrsi < dnlimit\nuprsi = rb == 1 and ur ? 1 : rb == 2 and ur and ur[1] ? 1 : rb == 3 and ur and ur[1] and ur[2] ? 1 : rb == 4 and ur and ur[1] and ur[2] and ur[3] ? 1 : rb == 5 and ur and ur[1] and ur[2] and ur[3] and ur[4] ? 1 : 0\ndnrsi = rb == 1 and dr ? 1 : rb == 2 and dr and dr[1] ? 1 : rb == 3 and dr and dr[1] and dr[2] ? 1 : rb == 4 and dr and dr[1] and dr[2] and dr[3] ? 1 : rb == 5 and dr and dr[1] and dr[2] and dr[3] and dr[4] ? 1 : 0\n\n//Body\nbody = abs(close - open)\nemabody = ema(body, 30)\n\n//Signals\nup = bar == -1 and sps == 0 and dnrsi and body > emabody / 4\ndn = bar == 1 and sps == 0 and uprsi and body > emabody / 4\nexit = bar == 1 and fastrsi > dnlimit and body > emabody / 2\n\n//Trading\nif up\n    strategy.entry("Long", strategy.long)\n    sps := 1\n\nif exit\n    strategy.close_all()\n    sps := 0'

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
