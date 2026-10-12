"""Source-faithful deep-assisted port of 玻尔带附近突破策略Bollinger-Breakout-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_43873fd5(PinePortBase, IStrategy):
    source_file = '玻尔带附近突破策略Bollinger-Breakout-Strategy.md'
    timeframe = '1h'
    can_short = True
    source_defaults = {'needlong': True, 'needshort': True, 'length': 20, 'mult': 1.0, 'fromyear': 1900, 'toyear': 2100, 'frommonth': 1, 'tomonth': 12}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 100.0
    source_pyramiding = 5
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.entry', 'strategy.close', 'strategy.position_size']
    source_fidelity_notes = ['Reads broker/strategy state; signals depend on fill timing and cannot be reduced to indicator-only booleans without changing behavior.']
    pine_assignments = [{'mode': '', 'name': 'needlong', 'op': '=', 'expr': 'input(true, defval = true, title = "Long")', 'conditions': []}, {'mode': '', 'name': 'needshort', 'op': '=', 'expr': 'input(true, defval = true, title = "Short")', 'conditions': []}, {'mode': '', 'name': 'length', 'op': '=', 'expr': 'input(20, minval=1)', 'conditions': []}, {'mode': '', 'name': 'mult', 'op': '=', 'expr': 'input(1.0, minval=0.001, maxval=50)', 'conditions': []}, {'mode': '', 'name': 'fromyear', 'op': '=', 'expr': 'input(1900, defval = 1900, minval = 1900, maxval = 2100, title = "From Year")', 'conditions': []}, {'mode': '', 'name': 'toyear', 'op': '=', 'expr': 'input(2100, defval = 2100, minval = 1900, maxval = 2100, title = "To Year")', 'conditions': []}, {'mode': '', 'name': 'frommonth', 'op': '=', 'expr': 'input(01, defval = 01, minval = 01, maxval = 12, title = "From Month")', 'conditions': []}, {'mode': '', 'name': 'tomonth', 'op': '=', 'expr': 'input(12, defval = 12, minval = 01, maxval = 12, title = "To Month")', 'conditions': []}, {'mode': '', 'name': 'source', 'op': '=', 'expr': 'close', 'conditions': []}, {'mode': '', 'name': 'basis', 'op': '=', 'expr': 'sma(source, length)', 'conditions': []}, {'mode': '', 'name': 'dev', 'op': '=', 'expr': 'mult * stdev(source, length)', 'conditions': []}, {'mode': '', 'name': 'upper', 'op': '=', 'expr': 'basis + dev', 'conditions': []}, {'mode': '', 'name': 'lower', 'op': '=', 'expr': 'basis - dev', 'conditions': []}, {'mode': '', 'name': 'up', 'op': '=', 'expr': 'close < lower', 'conditions': []}, {'mode': '', 'name': 'dn', 'op': '=', 'expr': 'close > upper', 'conditions': []}, {'mode': '', 'name': 'exit', 'op': '=', 'expr': '(strategy.position_size > 0 and close > open) or (strategy.position_size < 0 and close < open)', 'conditions': []}]
    pine_user_functions = []
    pine_controls = [{'indent': 0, 'statement': 'if up'}, {'indent': 0, 'statement': 'if dn'}, {'indent': 0, 'statement': 'if time > timestamp(toyear, tomonth, 31, 00, 00) or exit'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("Long", strategy.long, needlong == false ? 0 : na, when=(time > timestamp(fromyear, frommonth, 01, 00, 00) and time < timestamp(toyear, tomonth, 31, 00, 00)))', 'conditions': ['up'], 'statement': 'strategy.entry("Long", strategy.long, needlong == false ? 0 : na, when=(time > timestamp(fromyear, frommonth, 01, 00, 00) and time < timestamp(toyear, tomonth, 31, 00, 00)))'}, {'kind': 'entry', 'call': 'strategy.entry("Short", strategy.short, needshort == false ? 0 : na, when=(time > timestamp(fromyear, frommonth, 01, 00, 00) and time < timestamp(toyear, tomonth, 31, 00, 00)))', 'conditions': ['dn'], 'statement': 'strategy.entry("Short", strategy.short, needshort == false ? 0 : na, when=(time > timestamp(fromyear, frommonth, 01, 00, 00) and time < timestamp(toyear, tomonth, 31, 00, 00)))'}, {'kind': 'close_all', 'call': 'strategy.close_all()', 'conditions': ['time > timestamp(toyear, tomonth, 31, 00, 00) or exit'], 'statement': 'strategy.close_all()'}]
    original_pine = '/*backtest\nstart: 2023-08-21 00:00:00\nend: 2023-09-20 00:00:00\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//Noro\n//2018\n\n//@version=2\nstrategy("Noro\'s Bollinger Strategy v1.0", shorttitle = "Bollinger str 1.0", overlay = true, default_qty_type = strategy.percent_of_equity, default_qty_value = 100.0, pyramiding = 5)\n\n//Settings\nneedlong = input(true, defval = true, title = "Long")\nneedshort = input(true, defval = true, title = "Short")\n\nlength = input(20, minval=1)\nmult = input(1.0, minval=0.001, maxval=50)\n\nfromyear = input(1900, defval = 1900, minval = 1900, maxval = 2100, title = "From Year")\ntoyear = input(2100, defval = 2100, minval = 1900, maxval = 2100, title = "To Year")\nfrommonth = input(01, defval = 01, minval = 01, maxval = 12, title = "From Month")\ntomonth = input(12, defval = 12, minval = 01, maxval = 12, title = "To Month")\n\nsource = close\nbasis = sma(source, length)\ndev = mult * stdev(source, length)\n\nupper = basis + dev\nlower = basis - dev\n\nup = close < lower\ndn = close > upper\nexit = (strategy.position_size > 0 and close > open) or (strategy.position_size < 0 and close < open)\n\nif up\n    strategy.entry("Long", strategy.long, needlong == false ? 0 : na, when=(time > timestamp(fromyear, frommonth, 01, 00, 00) and time < timestamp(toyear, tomonth, 31, 00, 00)))\n\nif dn\n    strategy.entry("Short", strategy.short, needshort == false ? 0 : na, when=(time > timestamp(fromyear, frommonth, 01, 00, 00) and time < timestamp(toyear, tomonth, 31, 00, 00)))\n    \nif time > timestamp(toyear, tomonth, 31, 00, 00) or exit\n    strategy.close_all()'

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
