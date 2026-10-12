"""Source-faithful deep-assisted port of 月末反转DCA策略Monthly-Reversal-DCA-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_b69a97e9(PinePortBase, IStrategy):
    source_file = '月末反转DCA策略Monthly-Reversal-DCA-Strategy.md'
    timeframe = '1h'
    can_short = False
    source_defaults = {'start_year': 2017, 'start_month': 1, 'start_day': 1, 'end_year': 2050, 'end_month': 1, 'end_day': 1}
    source_qty_type = 'cash'
    source_qty_value = 1000.0
    source_pyramiding = 100
    source_initial_capital = 1000000.0
    source_commission_percent = 0.1
    source_features = ['strategy.entry', 'strategy.close', 'var ', '=>', 'barstate.']
    source_fidelity_notes = ['Uses persistent Pine state (var/varip); state is order-dependent and must be evaluated bar-by-bar, not replaced by a vectorized fill-forward approximation.']
    pine_assignments = [{'mode': '', 'name': 'start_year', 'op': '=', 'expr': "input(title='Start year' ,defval=2017)", 'conditions': []}, {'mode': '', 'name': 'start_month', 'op': '=', 'expr': "input(title='Start month' ,defval=1)", 'conditions': []}, {'mode': '', 'name': 'start_day', 'op': '=', 'expr': "input(title='Start day' ,defval=1)", 'conditions': []}, {'mode': '', 'name': 'start_time', 'op': '=', 'expr': 'timestamp(start_year, start_month, start_day, 00, 00)', 'conditions': []}, {'mode': '', 'name': 'end_year', 'op': '=', 'expr': "input(title='end year' ,defval=2050)", 'conditions': []}, {'mode': '', 'name': 'end_month', 'op': '=', 'expr': "input(title='end month' ,defval=1)", 'conditions': []}, {'mode': '', 'name': 'end_day', 'op': '=', 'expr': "input(title='end day' ,defval=1)", 'conditions': []}, {'mode': '', 'name': 'end_time', 'op': '=', 'expr': 'timestamp(end_year, end_month, end_day, 23, 59)', 'conditions': []}, {'mode': '', 'name': 'ema50', 'op': '=', 'expr': 'ta.ema(close, 50)', 'conditions': []}, {'mode': '', 'name': 'ema200', 'op': '=', 'expr': 'ta.ema(close, 200)', 'conditions': []}, {'mode': '', 'name': 'emacd', 'op': '=', 'expr': 'ema50 - ema200', 'conditions': []}, {'mode': '', 'name': 'emacd_signal', 'op': '=', 'expr': 'ta.ema(emacd, 20)', 'conditions': []}, {'mode': '', 'name': 'hist', 'op': '=', 'expr': 'emacd - emacd_signal', 'conditions': []}, {'mode': 'var', 'name': 'nPastCandles', 'op': '=', 'expr': '0', 'conditions': []}, {'mode': 'var', 'name': 'entryNumber', 'op': '=', 'expr': '0', 'conditions': []}, {'mode': '', 'name': 'nPastCandles', 'op': ':=', 'expr': 'nPastCandles + 1', 'conditions': []}, {'mode': '', 'name': 'entry_condition1', 'op': '=', 'expr': 'nPastCandles > entryNumber * 240', 'conditions': []}, {'mode': '', 'name': 'entry_condition2', 'op': '=', 'expr': 'ta.crossover(emacd, emacd_signal)', 'conditions': []}, {'mode': '', 'name': 'ENTRY_CONDITIONS', 'op': '=', 'expr': 'entry_condition1 and entry_condition2', 'conditions': []}, {'mode': '', 'name': 'entryNumber', 'op': ':=', 'expr': 'entryNumber + 1', 'conditions': ['ENTRY_CONDITIONS and window()']}, {'mode': '', 'name': 'entryId', 'op': '=', 'expr': "'Long ' + str.tostring(entryNumber)", 'conditions': ['ENTRY_CONDITIONS and window()']}, {'mode': '', 'name': 'CLOSE_CONDITIONS', 'op': '=', 'expr': 'barstate.islast', 'conditions': []}]
    pine_user_functions = [{'name': 'window', 'args': '', 'body': 'true'}]
    pine_controls = [{'indent': 0, 'statement': 'if ENTRY_CONDITIONS and window()'}, {'indent': 0, 'statement': 'if CLOSE_CONDITIONS'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry(entryId, strategy.long)', 'conditions': ['ENTRY_CONDITIONS and window()'], 'statement': 'strategy.entry(entryId, strategy.long)'}, {'kind': 'close_all', 'call': 'strategy.close_all()', 'conditions': ['CLOSE_CONDITIONS'], 'statement': 'strategy.close_all()'}]
    original_pine = '/*backtest\nstart: 2023-09-07 00:00:00\nend: 2023-10-07 00:00:00\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This source code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © BHD_Trade_Bot\n\n// @version=5\n// strategy(\n//  shorttitle            = \'DCA After Downtrend\',\n//  title                 = \'DCA After Downtrend (by BHD_Trade_Bot)\',\n//  overlay               = true,\n//  calc_on_every_tick    = true,\n//  calc_on_order_fills   = true,\n//  use_bar_magnifier     = true,\n//  pyramiding            = 100,\n//  initial_capital       = 0,\n//  default_qty_type      = strategy.cash,\n//  default_qty_value     = 1000,\n//  commission_type       = strategy.commission.percent,\n//  commission_value      = 0.1)\n\n\n\n// Backtest Time Period\nstart_year   = input(title=\'Start year\'   ,defval=2017)\nstart_month  = input(title=\'Start month\'  ,defval=1)\nstart_day    = input(title=\'Start day\'    ,defval=1)\nstart_time   = timestamp(start_year, start_month, start_day, 00, 00)\n\nend_year     = input(title=\'end year\'     ,defval=2050)\nend_month    = input(title=\'end month\'    ,defval=1)\nend_day      = input(title=\'end day\'      ,defval=1)\nend_time     = timestamp(end_year, end_month, end_day, 23, 59)\n\nwindow() => true\n\n\n\n// EMA\nema50 = ta.ema(close, 50)\nema200 = ta.ema(close, 200)\n\n// EMA_CD\nemacd = ema50 - ema200\nemacd_signal = ta.ema(emacd, 20)\nhist = emacd - emacd_signal\n\n// Count n candles after x long entries\nvar int nPastCandles = 0\nvar int entryNumber = 0\nnPastCandles := nPastCandles + 1\n\n\n\n// ENTRY CONDITIONS\n\n// 8 hours per day => 240 hours per month\nentry_condition1 = nPastCandles > entryNumber * 240\n\n// End of downtrend\nentry_condition2 = ta.crossover(emacd, emacd_signal)\n\nENTRY_CONDITIONS = entry_condition1 and entry_condition2\n\n\nif ENTRY_CONDITIONS and window()\n    entryNumber := entryNumber + 1\n    entryId = \'Long \' + str.tostring(entryNumber)\n    strategy.entry(entryId, strategy.long)\n    \n    \n\n// CLOSE CONDITIONS\n\n// Last bar\nCLOSE_CONDITIONS = barstate.islast\n\nif CLOSE_CONDITIONS\n    strategy.close_all()\n\n\n    \n// Draw\nplot(ema50, color=color.orange, linewidth=3)\nplot(ema200, color=entry_condition1 ? color.green : color.red, linewidth=3)'

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
