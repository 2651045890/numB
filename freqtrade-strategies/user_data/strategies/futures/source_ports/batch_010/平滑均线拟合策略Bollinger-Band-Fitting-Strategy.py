"""Source-faithful deep-assisted port of 平滑均线拟合策略Bollinger-Band-Fitting-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_97187ea7(PinePortBase, IStrategy):
    source_file = '平滑均线拟合策略Bollinger-Band-Fitting-Strategy.md'
    timeframe = '1h'
    can_short = False
    source_defaults = {'capital': 100, 'length': 40, 'usebod': False, 'usecol': False, 'usersi': True, 'showar': False, 'fromyear': 1900, 'toyear': 2100, 'frommonth': 1, 'tomonth': 12, 'fromday': 1, 'today': 31}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 100.0
    source_pyramiding = 10
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.entry', 'strategy.close', 'strategy.position_size', 'strategy.equity']
    source_fidelity_notes = ['Reads broker/strategy state; signals depend on fill timing and cannot be reduced to indicator-only booleans without changing behavior.']
    pine_assignments = [{'mode': '', 'name': 'capital', 'op': '=', 'expr': 'input(100, defval = 100, minval = 1, maxval = 10000, title = "Capital, %")', 'conditions': []}, {'mode': '', 'name': 'length', 'op': '=', 'expr': 'input(40, defval = 40, minval = 1, maxval = 200, title = "BB Period")', 'conditions': []}, {'mode': '', 'name': 'usebod', 'op': '=', 'expr': 'input(false, defval = false, title = "Use Body-Filter")', 'conditions': []}, {'mode': '', 'name': 'usecol', 'op': '=', 'expr': 'input(false, defval = false, title = "Use Color-Filter")', 'conditions': []}, {'mode': '', 'name': 'usersi', 'op': '=', 'expr': 'input(true, defval = true, title = "Use RSI-Filter")', 'conditions': []}, {'mode': '', 'name': 'showar', 'op': '=', 'expr': 'input(false, defval = false, title = "Show Arrows")', 'conditions': []}, {'mode': '', 'name': 'fromyear', 'op': '=', 'expr': 'input(1900, defval = 1900, minval = 1900, maxval = 2100, title = "From Year")', 'conditions': []}, {'mode': '', 'name': 'toyear', 'op': '=', 'expr': 'input(2100, defval = 2100, minval = 1900, maxval = 2100, title = "To Year")', 'conditions': []}, {'mode': '', 'name': 'frommonth', 'op': '=', 'expr': 'input(01, defval = 01, minval = 01, maxval = 12, title = "From Month")', 'conditions': []}, {'mode': '', 'name': 'tomonth', 'op': '=', 'expr': 'input(12, defval = 12, minval = 01, maxval = 12, title = "To Month")', 'conditions': []}, {'mode': '', 'name': 'fromday', 'op': '=', 'expr': 'input(01, defval = 01, minval = 01, maxval = 31, title = "From day")', 'conditions': []}, {'mode': '', 'name': 'today', 'op': '=', 'expr': 'input(31, defval = 31, minval = 01, maxval = 31, title = "To day")', 'conditions': []}, {'mode': '', 'name': 'src', 'op': '=', 'expr': 'low', 'conditions': []}, {'mode': '', 'name': 'mult', 'op': '=', 'expr': '2', 'conditions': []}, {'mode': '', 'name': 'basis', 'op': '=', 'expr': 'sma(src, length)', 'conditions': []}, {'mode': '', 'name': 'dev', 'op': '=', 'expr': 'mult * stdev(src, length)', 'conditions': []}, {'mode': '', 'name': 'lower', 'op': '=', 'expr': 'basis - dev', 'conditions': []}, {'mode': '', 'name': 'fastup', 'op': '=', 'expr': 'rma(max(change(close), 0), 7)', 'conditions': []}, {'mode': '', 'name': 'fastdown', 'op': '=', 'expr': 'rma(-min(change(close), 0), 7)', 'conditions': []}, {'mode': '', 'name': 'rsi', 'op': '=', 'expr': 'fastdown == 0 ? 100 : fastup == 0 ? 0 : 100 - (100 / (1 + fastup / fastdown))', 'conditions': []}, {'mode': '', 'name': 'rsif', 'op': '=', 'expr': 'rsi < 30 or usersi == false', 'conditions': []}, {'mode': '', 'name': 'nbody', 'op': '=', 'expr': 'abs(close - open)', 'conditions': []}, {'mode': '', 'name': 'abody', 'op': '=', 'expr': 'sma(nbody, 10)', 'conditions': []}, {'mode': '', 'name': 'body', 'op': '=', 'expr': 'nbody > abody / 2 or usebod == false', 'conditions': []}, {'mode': '', 'name': 'up1', 'op': '=', 'expr': 'low < lower and (close < open or usecol == false) and body and rsif', 'conditions': []}, {'mode': '', 'name': 'exit', 'op': '=', 'expr': 'close > open and nbody > abody / 2', 'conditions': []}, {'mode': '', 'name': 'needar', 'op': '=', 'expr': 'up1 and showar', 'conditions': []}, {'mode': '', 'name': 'lot', 'op': '=', 'expr': 'strategy.position_size == 0 ? strategy.equity / close * capital / 100 : lot[1]', 'conditions': []}]
    pine_user_functions = []
    pine_controls = [{'indent': 0, 'statement': 'if up1'}, {'indent': 4, 'statement': 'if strategy.position_size < 0'}, {'indent': 0, 'statement': 'if time > timestamp(toyear, tomonth, today, 23, 59) or exit'}]
    pine_orders = [{'kind': 'close_all', 'call': 'strategy.close_all()', 'conditions': ['up1', 'strategy.position_size < 0'], 'statement': 'strategy.close_all()'}, {'kind': 'entry', 'call': 'strategy.entry("Long", strategy.long, lot, when=(time > timestamp(fromyear, frommonth, fromday, 00, 00) and time < timestamp(toyear, tomonth, today, 23, 59)))', 'conditions': ['up1'], 'statement': 'strategy.entry("Long", strategy.long, lot, when=(time > timestamp(fromyear, frommonth, fromday, 00, 00) and time < timestamp(toyear, tomonth, today, 23, 59)))'}, {'kind': 'close_all', 'call': 'strategy.close_all()', 'conditions': ['time > timestamp(toyear, tomonth, today, 23, 59) or exit'], 'statement': 'strategy.close_all()'}]
    original_pine = '/*backtest\nstart: 2023-09-23 00:00:00\nend: 2023-10-23 00:00:00\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//Noro\n//2018\n\n//Donate: 3BMEXvKkuJLobJrcpMm12bKTZoCnojZTjh\n\n//@version=2\nstrategy(title = "Noro\'s Wizard Strategy v1.1", shorttitle = "Wizard str 1.1", overlay = true, default_qty_type = strategy.percent_of_equity, default_qty_value = 100, pyramiding = 10)\n\n//Settings\ncapital = input(100, defval = 100, minval = 1, maxval = 10000, title = "Capital, %")\nlength = input(40, defval = 40, minval = 1, maxval = 200, title = "BB Period")\nusebod = input(false, defval = false, title = "Use Body-Filter")\nusecol = input(false, defval = false, title = "Use Color-Filter")\nusersi = input(true, defval = true, title = "Use RSI-Filter")\nshowar = input(false, defval = false, title = "Show Arrows")\nfromyear = input(1900, defval = 1900, minval = 1900, maxval = 2100, title = "From Year")\ntoyear = input(2100, defval = 2100, minval = 1900, maxval = 2100, title = "To Year")\nfrommonth = input(01, defval = 01, minval = 01, maxval = 12, title = "From Month")\ntomonth = input(12, defval = 12, minval = 01, maxval = 12, title = "To Month")\nfromday = input(01, defval = 01, minval = 01, maxval = 31, title = "From day")\ntoday = input(31, defval = 31, minval = 01, maxval = 31, title = "To day")\n\n//Bollinger\nsrc = low\nmult = 2\nbasis = sma(src, length)\ndev = mult * stdev(src, length)\nlower = basis - dev\nplot(lower, color = lime, linewidth = 3, title="Bottom Line")\n\n//Fast RSI Filter\nfastup = rma(max(change(close), 0), 7)\nfastdown = rma(-min(change(close), 0), 7)\nrsi = fastdown == 0 ? 100 : fastup == 0 ? 0 : 100 - (100 / (1 + fastup / fastdown))\nrsif = rsi < 30 or usersi == false\n\n//Body Filter\nnbody = abs(close - open)\nabody = sma(nbody, 10)\nbody = nbody > abody / 2 or usebod == false\n\n//Signals\nup1 = low < lower and (close < open or usecol == false) and body and rsif\nexit = close > open and nbody > abody / 2\n\n//Arrows\nneedar = up1 and showar\nplotarrow(needar ? 1 : na)\n\n//Trading\nlot = strategy.position_size == 0 ? strategy.equity / close * capital / 100 : lot[1]\n\nif up1\n    if strategy.position_size < 0\n        strategy.close_all()\n        \n    strategy.entry("Long", strategy.long, lot, when=(time > timestamp(fromyear, frommonth, fromday, 00, 00) and time < timestamp(toyear, tomonth, today, 23, 59)))\n    \nif time > timestamp(toyear, tomonth, today, 23, 59) or exit\n    strategy.close_all()'

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
