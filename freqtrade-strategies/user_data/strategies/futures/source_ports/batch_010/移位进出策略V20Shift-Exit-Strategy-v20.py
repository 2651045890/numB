"""Source-faithful deep-assisted port of 移位进出策略V20Shift-Exit-Strategy-v20.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_d0e921c3(PinePortBase, IStrategy):
    source_file = '移位进出策略V20Shift-Exit-Strategy-v20.md'
    timeframe = '4d'
    can_short = True
    source_defaults = {'buy': -10.0, 'sell': 0.0, 'buysrc': 'low', 'sellsrc': 'ohlc4', 'offset': True, 'fromyear': 1900, 'toyear': 2100, 'frommonth': 1, 'tomonth': 12, 'fromday': 1, 'today': 31}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 100.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.entry', 'for ']
    source_fidelity_notes = []
    pine_assignments = [{'mode': '', 'name': 'buy', 'op': '=', 'expr': 'input(-10.0, title = "Buy, src-%")', 'conditions': []}, {'mode': '', 'name': 'sell', 'op': '=', 'expr': 'input(0.0, title = "Sell, src+%")', 'conditions': []}, {'mode': '', 'name': 'buysrc', 'op': '=', 'expr': 'input(low, title = "Source for buy")', 'conditions': []}, {'mode': '', 'name': 'sellsrc', 'op': '=', 'expr': 'input(ohlc4, title = "Source for sell")', 'conditions': []}, {'mode': '', 'name': 'offset', 'op': '=', 'expr': 'input(true)', 'conditions': []}, {'mode': '', 'name': 'fromyear', 'op': '=', 'expr': 'input(1900, defval = 1900, minval = 1900, maxval = 2100, title = "From Year")', 'conditions': []}, {'mode': '', 'name': 'toyear', 'op': '=', 'expr': 'input(2100, defval = 2100, minval = 1900, maxval = 2100, title = "To Year")', 'conditions': []}, {'mode': '', 'name': 'frommonth', 'op': '=', 'expr': 'input(01, defval = 01, minval = 01, maxval = 12, title = "From Month")', 'conditions': []}, {'mode': '', 'name': 'tomonth', 'op': '=', 'expr': 'input(12, defval = 12, minval = 01, maxval = 12, title = "To Month")', 'conditions': []}, {'mode': '', 'name': 'fromday', 'op': '=', 'expr': 'input(01, defval = 01, minval = 01, maxval = 31, title = "From day")', 'conditions': []}, {'mode': '', 'name': 'today', 'op': '=', 'expr': 'input(31, defval = 31, minval = 01, maxval = 31, title = "To day")', 'conditions': []}, {'mode': '', 'name': 'bar', 'op': '=', 'expr': 'close > open ? 1 : close < open ? -1 : 0', 'conditions': []}, {'mode': '', 'name': 'mult', 'op': '=', 'expr': '1 / syminfo.mintick', 'conditions': []}, {'mode': '', 'name': 'lb', 'op': '=', 'expr': 'bar == -1 ? buysrc + ((buysrc / 100) * (buy * 1)) : buysrc + ((buysrc / 100) * (buy * 2))', 'conditions': []}, {'mode': '', 'name': 'levelbuy', 'op': '=', 'expr': 'round(lb * mult) / mult', 'conditions': []}, {'mode': '', 'name': 'ls', 'op': '=', 'expr': 'sellsrc + ((sellsrc / 100) * sell)', 'conditions': []}, {'mode': '', 'name': 'levelsell', 'op': '=', 'expr': 'round(ls * mult) / mult', 'conditions': []}, {'mode': '', 'name': 'os', 'op': '=', 'expr': 'offset ? 1 : 0', 'conditions': []}]
    pine_user_functions = []
    pine_controls = [{'indent': 0, 'statement': 'if low[1] > 0'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("long", strategy.long, limit = levelbuy, when = (time > timestamp(fromyear, frommonth, fromday, 00, 00) and time < timestamp(toyear, tomonth, today, 23, 59)))', 'conditions': ['low[1] > 0'], 'statement': 'strategy.entry("long", strategy.long, limit = levelbuy, when = (time > timestamp(fromyear, frommonth, fromday, 00, 00) and time < timestamp(toyear, tomonth, today, 23, 59)))'}, {'kind': 'entry', 'call': 'strategy.entry("close", strategy.short, 0, limit = levelsell, when = (time > timestamp(fromyear, frommonth, fromday, 00, 00) and time < timestamp(toyear, tomonth, today, 23, 59)))', 'conditions': ['low[1] > 0'], 'statement': 'strategy.entry("close", strategy.short, 0, limit = levelsell, when = (time > timestamp(fromyear, frommonth, fromday, 00, 00) and time < timestamp(toyear, tomonth, today, 23, 59)))'}]
    original_pine = '/*backtest\nstart: 2022-09-14 00:00:00\nend: 2023-09-20 00:00:00\nperiod: 4d\nbasePeriod: 1d\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//Noro\n//2019\n\n//@version=3\nstrategy(title = "Noro\'s ShiftEx Strategy v2.0", shorttitle = "ShiftEx 2.0", overlay = true, default_qty_type = strategy.percent_of_equity, default_qty_value = 100, pyramiding = 0)\n\n//Settings\nbuy = input(-10.0, title = "Buy, src-%")\nsell = input(0.0, title = "Sell, src+%")\nbuysrc = input(low, title = "Source for buy")\nsellsrc = input(ohlc4, title = "Source for sell")\noffset = input(true)\nfromyear = input(1900, defval = 1900, minval = 1900, maxval = 2100, title = "From Year")\ntoyear = input(2100, defval = 2100, minval = 1900, maxval = 2100, title = "To Year")\nfrommonth = input(01, defval = 01, minval = 01, maxval = 12, title = "From Month")\ntomonth = input(12, defval = 12, minval = 01, maxval = 12, title = "To Month")\nfromday = input(01, defval = 01, minval = 01, maxval = 31, title = "From day")\ntoday = input(31, defval = 31, minval = 01, maxval = 31, title = "To day")\n\n//Levels\nbar = close > open ? 1 : close < open ? -1 : 0\nmult = 1 / syminfo.mintick\nlb = bar == -1 ? buysrc + ((buysrc / 100) * (buy * 1)) : buysrc + ((buysrc / 100) * (buy * 2))\nlevelbuy = round(lb * mult) / mult\nls = sellsrc + ((sellsrc / 100) * sell)\nlevelsell = round(ls * mult) / mult\n\n//Lines\nos = offset ? 1 : 0\nplot(levelbuy, offset = os, linewidth = 2, color = lime, title = "Buy")\nplot(levelsell, offset = os, linewidth = 2, color = blue, title = "Sell")\n\n//Trading\nif low[1] > 0\n    strategy.entry("long", strategy.long, limit = levelbuy, when = (time > timestamp(fromyear, frommonth, fromday, 00, 00) and time < timestamp(toyear, tomonth, today, 23, 59)))\n    strategy.entry("close", strategy.short, 0, limit = levelsell, when = (time > timestamp(fromyear, frommonth, fromday, 00, 00) and time < timestamp(toyear, tomonth, today, 23, 59)))'

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
