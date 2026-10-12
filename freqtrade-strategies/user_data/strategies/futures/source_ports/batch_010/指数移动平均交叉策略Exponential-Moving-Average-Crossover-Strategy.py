"""Source-faithful deep-assisted port of 指数移动平均交叉策略Exponential-Moving-Average-Crossover-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_0f9e8fab(PinePortBase, IStrategy):
    source_file = '指数移动平均交叉策略Exponential-Moving-Average-Crossover-Strategy.md'
    timeframe = '1h'
    can_short = True
    source_defaults = {'needlong': True, 'needshort': True, 'capital': 100, 'tf': 'D', 'len': 3, 'src': 'close', 'fromyear': 1900, 'toyear': 2100, 'frommonth': 1, 'tomonth': 12, 'fromday': 1, 'today': 31}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 100.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['request.security', 'strategy.entry', 'strategy.close', 'strategy.position_size', 'strategy.equity']
    source_fidelity_notes = ['Uses request.security / multi-timeframe context; exact parity depends on HTF resampling, gaps and lookahead semantics.', 'Reads broker/strategy state; signals depend on fill timing and cannot be reduced to indicator-only booleans without changing behavior.']
    pine_assignments = [{'mode': '', 'name': 'needlong', 'op': '=', 'expr': 'input(true, defval = true, title = "Long")', 'conditions': []}, {'mode': '', 'name': 'needshort', 'op': '=', 'expr': 'input(true, defval = true, title = "Short")', 'conditions': []}, {'mode': '', 'name': 'capital', 'op': '=', 'expr': 'input(100, defval = 100, minval = 1, maxval = 10000, title = "Lot")', 'conditions': []}, {'mode': '', 'name': 'tf', 'op': '=', 'expr': 'input("D", title = "Big Timeframe")', 'conditions': []}, {'mode': '', 'name': 'len', 'op': '=', 'expr': 'input(3, minval = 1, title = "MA length")', 'conditions': []}, {'mode': '', 'name': 'src', 'op': '=', 'expr': 'input(close, title = "MA Source")', 'conditions': []}, {'mode': '', 'name': 'fromyear', 'op': '=', 'expr': 'input(1900, defval = 1900, minval = 1900, maxval = 2100, title = "From Year")', 'conditions': []}, {'mode': '', 'name': 'toyear', 'op': '=', 'expr': 'input(2100, defval = 2100, minval = 1900, maxval = 2100, title = "To Year")', 'conditions': []}, {'mode': '', 'name': 'frommonth', 'op': '=', 'expr': 'input(01, defval = 01, minval = 01, maxval = 12, title = "From Month")', 'conditions': []}, {'mode': '', 'name': 'tomonth', 'op': '=', 'expr': 'input(12, defval = 12, minval = 01, maxval = 12, title = "To Month")', 'conditions': []}, {'mode': '', 'name': 'fromday', 'op': '=', 'expr': 'input(01, defval = 01, minval = 01, maxval = 31, title = "From day")', 'conditions': []}, {'mode': '', 'name': 'today', 'op': '=', 'expr': 'input(31, defval = 31, minval = 01, maxval = 31, title = "To day")', 'conditions': []}, {'mode': '', 'name': 'ma1', 'op': '=', 'expr': 'request.security(syminfo.tickerid, tf, sma(src, len))', 'conditions': []}, {'mode': '', 'name': 'ma2', 'op': '=', 'expr': 'sma(src, len)', 'conditions': []}, {'mode': '', 'name': 'size', 'op': '=', 'expr': 'strategy.position_size', 'conditions': []}, {'mode': '', 'name': 'lot', 'op': '=', 'expr': '0.0', 'conditions': []}, {'mode': '', 'name': 'lot', 'op': ':=', 'expr': 'size != size[1] ? strategy.equity / close * capital / 100 : lot[1]', 'conditions': []}]
    pine_user_functions = []
    pine_controls = [{'indent': 0, 'statement': 'if ma2 > ma1'}, {'indent': 0, 'statement': 'if ma2 < ma1'}, {'indent': 0, 'statement': 'if time > timestamp(toyear, tomonth, today, 23, 59)'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("L", strategy.long, needlong ? lot : 0, when = (time > timestamp(fromyear, frommonth, fromday, 00, 00) and time < timestamp(toyear, tomonth, today, 23, 59)))', 'conditions': ['ma2 > ma1'], 'statement': 'strategy.entry("L", strategy.long, needlong ? lot : 0, when = (time > timestamp(fromyear, frommonth, fromday, 00, 00) and time < timestamp(toyear, tomonth, today, 23, 59)))'}, {'kind': 'entry', 'call': 'strategy.entry("S", strategy.short, needshort ? lot : 0, when = (time > timestamp(fromyear, frommonth, fromday, 00, 00) and time < timestamp(toyear, tomonth, today, 23, 59)))', 'conditions': ['ma2 < ma1'], 'statement': 'strategy.entry("S", strategy.short, needshort ? lot : 0, when = (time > timestamp(fromyear, frommonth, fromday, 00, 00) and time < timestamp(toyear, tomonth, today, 23, 59)))'}, {'kind': 'close_all', 'call': 'strategy.close_all()', 'conditions': ['time > timestamp(toyear, tomonth, today, 23, 59)'], 'statement': 'strategy.close_all()'}]
    original_pine = '/*backtest\nstart: 2023-09-16 00:00:00\nend: 2023-10-16 00:00:00\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=3\nstrategy("Noro\'s Singapore Strategy", shorttitle = "Singapore str", overlay = true, default_qty_type = strategy.percent_of_equity, default_qty_value = 100, pyramiding = 0)\n\n//Settings\nneedlong = input(true, defval = true, title = "Long")\nneedshort = input(true, defval = true, title = "Short")\ncapital = input(100, defval = 100, minval = 1, maxval = 10000, title = "Lot")\ntf = input("D", title = "Big Timeframe")\nlen = input(3, minval = 1, title = "MA length")\nsrc = input(close, title = "MA Source")\nfromyear = input(1900, defval = 1900, minval = 1900, maxval = 2100, title = "From Year")\ntoyear = input(2100, defval = 2100, minval = 1900, maxval = 2100, title = "To Year")\nfrommonth = input(01, defval = 01, minval = 01, maxval = 12, title = "From Month")\ntomonth = input(12, defval = 12, minval = 01, maxval = 12, title = "To Month")\nfromday = input(01, defval = 01, minval = 01, maxval = 31, title = "From day")\ntoday = input(31, defval = 31, minval = 01, maxval = 31, title = "To day")\n\n//MAs\nma1 = request.security(syminfo.tickerid, tf, sma(src, len))\nma2 = sma(src, len)\nplot(ma1, linewidth = 2, color = blue, title = "Big TF MA")\nplot(ma2, linewidth = 2, color = red, title = "MA")\n\n//Trading\nsize = strategy.position_size\nlot = 0.0\nlot := size != size[1] ? strategy.equity / close * capital / 100 : lot[1]\n\nif ma2 > ma1\n    strategy.entry("L", strategy.long, needlong ? lot : 0, when = (time > timestamp(fromyear, frommonth, fromday, 00, 00) and time < timestamp(toyear, tomonth, today, 23, 59)))\nif ma2 < ma1\n    strategy.entry("S", strategy.short, needshort ? lot : 0, when = (time > timestamp(fromyear, frommonth, fromday, 00, 00) and time < timestamp(toyear, tomonth, today, 23, 59)))\nif time > timestamp(toyear, tomonth, today, 23, 59)\n    strategy.close_all()'

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
