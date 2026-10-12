"""Source-faithful deep-assisted port of 毎日交易策略Day-of-the-Week-Custom-Trading-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_15f40ad0(PinePortBase, IStrategy):
    source_file = '毎日交易策略Day-of-the-Week-Custom-Trading-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'frommonth': 6, 'fromday': 14, 'fromyear': 2021, 'tomonth': 12, 'today': 31, 'toyear': 2100}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 1.0
    source_pyramiding = 0
    source_initial_capital = 30000.0
    source_commission_percent = 0.0
    source_features = ['strategy.entry', 'strategy.close', 'array.', 'for ']
    source_fidelity_notes = ['Uses mutable Pine arrays; mutation order and per-bar persistence are load-bearing.']
    pine_assignments = [{'mode': '', 'name': 'frommonth', 'op': '=', 'expr': 'input(defval = 6, minval = 01, maxval = 12, title = "From Month")', 'conditions': []}, {'mode': '', 'name': 'fromday', 'op': '=', 'expr': 'input(defval = 14, minval = 01, maxval = 31, title = "From day")', 'conditions': []}, {'mode': '', 'name': 'fromyear', 'op': '=', 'expr': 'input(defval = 2021, minval = 1900, maxval = 2100, title = "From Year")', 'conditions': []}, {'mode': '', 'name': 'tomonth', 'op': '=', 'expr': 'input(defval = 12, minval = 01, maxval = 12, title = "To Month")', 'conditions': []}, {'mode': '', 'name': 'today', 'op': '=', 'expr': 'input(defval = 31, minval = 01, maxval = 31, title = "To day")', 'conditions': []}, {'mode': '', 'name': 'toyear', 'op': '=', 'expr': 'input(defval = 2100, minval = 1900, maxval = 2100, title = "To Year")', 'conditions': []}, {'mode': '', 'name': 'timeframes', 'op': '=', 'expr': 'array.new_int(7, 1)', 'conditions': []}, {'mode': '', 'name': 'timeframes_options', 'op': '=', 'expr': "array.new_string(7, 'None')", 'conditions': []}]
    pine_user_functions = []
    pine_controls = [{'indent': 0, 'statement': 'for i = 0 to array.size(timeframes) - 1'}, {'indent': 4, 'statement': 'if dayofweek == array.get(timeframes, i) and array.get(timeframes_options, i) != array.get(timeframes_options, i==0?6:i-1)'}, {'indent': 4, 'statement': "if dayofweek == array.get(timeframes, i) and array.get(timeframes_options, i)!='None' and array.get(timeframes_options, i) != array.get(timeframes_options, i==0?6:i-1)"}, {'indent': 8, 'statement': "if array.get(timeframes_options, i) == 'Long'"}, {'indent': 8, 'statement': "else if array.get(timeframes_options, i) == 'Short'"}]
    pine_orders = [{'kind': 'close_all', 'call': 'strategy.close_all()', 'conditions': ['dayofweek == array.get(timeframes, i) and array.get(timeframes_options, i) != array.get(timeframes_options, i==0?6:i-1)'], 'statement': 'strategy.close_all()'}, {'kind': 'entry', 'call': 'strategy.entry("Long", strategy.long, when=(time > timestamp(fromyear, frommonth, fromday, 00, 00) and time < timestamp(toyear, tomonth, today, 00, 00)))', 'conditions': ["dayofweek == array.get(timeframes, i) and array.get(timeframes_options, i)!='None' and array.get(timeframes_options, i) != array.get(timeframes_options, i==0?6:i-1)", "array.get(timeframes_options, i) == 'Long'"], 'statement': 'strategy.entry("Long", strategy.long, when=(time > timestamp(fromyear, frommonth, fromday, 00, 00) and time < timestamp(toyear, tomonth, today, 00, 00)))'}, {'kind': 'entry', 'call': 'strategy.entry("Short", strategy.short, when=(time > timestamp(fromyear, frommonth, fromday, 00, 00) and time < timestamp(toyear, tomonth, today, 00, 00)))', 'conditions': ["dayofweek == array.get(timeframes, i) and array.get(timeframes_options, i)!='None' and array.get(timeframes_options, i) != array.get(timeframes_options, i==0?6:i-1)", "array.get(timeframes_options, i) == 'Short'"], 'statement': 'strategy.entry("Short", strategy.short, when=(time > timestamp(fromyear, frommonth, fromday, 00, 00) and time < timestamp(toyear, tomonth, today, 00, 00)))'}]
    original_pine = '/*backtest\nstart: 2022-09-19 00:00:00\nend: 2023-09-25 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This source code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n\n//@version=4\n// strategy("Day of Week Custom Buy/Sell Strategy", overlay=true, currency=currency.USD, default_qty_value=1.0,initial_capital=30000.00,default_qty_type=strategy.percent_of_equity)\n\nfrommonth = input(defval = 6, minval = 01, maxval = 12, title = "From Month")\nfromday = input(defval = 14, minval = 01, maxval = 31, title = "From day")\nfromyear = input(defval = 2021, minval = 1900, maxval = 2100, title = "From Year")\n\ntomonth = input(defval = 12, minval = 01, maxval = 12, title = "To Month")\ntoday = input(defval = 31, minval = 01, maxval = 31, title = "To day")\ntoyear = input(defval = 2100, minval = 1900, maxval = 2100, title = "To Year")\n\ntimeframes = array.new_int(7, 1)\ntimeframes_options = array.new_string(7, \'None\')\n\narray.set(timeframes,0,7)\narray.set(timeframes_options,0, input(defval=\'None\', options=[\'Long\',\'Short\',\'None\'], title=\'sunday\'))\narray.set(timeframes,1,1)\narray.set(timeframes_options,1, input(defval=\'Long\', options=[\'Long\',\'Short\',\'None\'], title=\'monday\'))\narray.set(timeframes,2,2)\narray.set(timeframes_options,2, input(defval=\'Long\', options=[\'Long\',\'Short\',\'None\'], title=\'tuesday\'))\narray.set(timeframes,3,3)\narray.set(timeframes_options,3, input(defval=\'Long\', options=[\'Long\',\'Short\',\'None\'], title=\'wednesday\'))\narray.set(timeframes,4,4)\narray.set(timeframes_options,4, input(defval=\'None\', options=[\'Long\',\'Short\',\'None\'], title=\'thursday\'))\narray.set(timeframes,5,5)\narray.set(timeframes_options,5, input(defval=\'None\', options=[\'Long\',\'Short\',\'None\'], title=\'friday\'))\narray.set(timeframes,6,6)\narray.set(timeframes_options,6, input(defval=\'None\', options=[\'Long\',\'Short\',\'None\'], title=\'saturday\'))\n\n\n\nfor i = 0 to array.size(timeframes) - 1\n    \n    if dayofweek == array.get(timeframes, i) and array.get(timeframes_options, i) != array.get(timeframes_options, i==0?6:i-1)\n        strategy.close_all()\n\n    if dayofweek == array.get(timeframes, i) and array.get(timeframes_options, i)!=\'None\' and array.get(timeframes_options, i) != array.get(timeframes_options, i==0?6:i-1)\n        if array.get(timeframes_options, i) == \'Long\'\n            strategy.entry("Long", strategy.long, when=(time > timestamp(fromyear, frommonth, fromday, 00, 00) and time < timestamp(toyear, tomonth, today, 00, 00)))\n        else if array.get(timeframes_options, i) == \'Short\'\n            strategy.entry("Short", strategy.short, when=(time > timestamp(fromyear, frommonth, fromday, 00, 00) and time < timestamp(toyear, tomonth, today, 00, 00)))'

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
