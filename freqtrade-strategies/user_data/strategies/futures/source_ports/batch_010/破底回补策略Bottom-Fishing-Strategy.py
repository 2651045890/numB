"""Source-faithful deep-assisted port of 破底回补策略Bottom-Fishing-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_dc7e5b51(PinePortBase, IStrategy):
    source_file = '破底回补策略Bottom-Fishing-Strategy.md'
    timeframe = '1m'
    can_short = False
    source_defaults = {'fromMonth': 1, 'fromDay': 1, 'fromYear': 2020, 'thruMonth': 1, 'thruDay': 1, 'thruYear': 2112, 'showDate': True, 'RSI_entry': 35, 'RSI_exit': 65}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 30.0
    source_pyramiding = 0
    source_initial_capital = 1000.0
    source_commission_percent = 0.1
    source_features = ['strategy.entry', 'strategy.close', '=>']
    source_fidelity_notes = []
    pine_assignments = [{'mode': '', 'name': 'fromMonth', 'op': '=', 'expr': 'input(defval = 1, title = "From Month", type = input.integer, minval = 1, maxval = 12)', 'conditions': []}, {'mode': '', 'name': 'fromDay', 'op': '=', 'expr': 'input(defval = 1, title = "From Day", type = input.integer, minval = 1, maxval = 31)', 'conditions': []}, {'mode': '', 'name': 'fromYear', 'op': '=', 'expr': 'input(defval = 2020, title = "From Year", type = input.integer, minval = 1970)', 'conditions': []}, {'mode': '', 'name': 'thruMonth', 'op': '=', 'expr': 'input(defval = 1, title = "Thru Month", type = input.integer, minval = 1, maxval = 12)', 'conditions': []}, {'mode': '', 'name': 'thruDay', 'op': '=', 'expr': 'input(defval = 1, title = "Thru Day", type = input.integer, minval = 1, maxval = 31)', 'conditions': []}, {'mode': '', 'name': 'thruYear', 'op': '=', 'expr': 'input(defval = 2112, title = "Thru Year", type = input.integer, minval = 1970)', 'conditions': []}, {'mode': '', 'name': 'showDate', 'op': '=', 'expr': 'input(defval = true, title = "Show Date Range", type = input.bool)', 'conditions': []}, {'mode': '', 'name': 'start', 'op': '=', 'expr': 'timestamp(fromYear, fromMonth, fromDay, 00, 00) // backtest start window', 'conditions': []}, {'mode': '', 'name': 'finish', 'op': '=', 'expr': 'timestamp(thruYear, thruMonth, thruDay, 23, 59) // backtest finish window', 'conditions': []}, {'mode': '', 'name': 'lengthRSI', 'op': '=', 'expr': '(14)', 'conditions': []}, {'mode': '', 'name': 'RSI', 'op': '=', 'expr': 'rsi(close, lengthRSI)', 'conditions': []}, {'mode': '', 'name': 'RSI_entry', 'op': '=', 'expr': "input(35, title = 'RSI Entry', minval=1)", 'conditions': []}, {'mode': '', 'name': 'RSI_exit', 'op': '=', 'expr': "input(65, title = 'RSI Close', minval=1)", 'conditions': []}, {'mode': '', 'name': 'movingaverage_signal', 'op': '=', 'expr': 'sma(close, input(100))', 'conditions': []}]
    pine_user_functions = [{'name': 'window', 'args': '', 'body': 'true // create function "within window of time"'}]
    pine_controls = []
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry(id="long", long = true, when = RSI< RSI_entry and close < movingaverage_signal and window())', 'conditions': [], 'statement': 'strategy.entry(id="long", long = true, when = RSI< RSI_entry and close < movingaverage_signal and window())'}, {'kind': 'close', 'call': 'strategy.close("long", when = RSI > RSI_exit and window())', 'conditions': [], 'statement': 'strategy.close("long", when = RSI > RSI_exit and window())'}]
    original_pine = '/*backtest\nstart: 2024-01-10 00:00:00\nend: 2024-01-17 00:00:00\nperiod: 1m\nbasePeriod: 1m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This source code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © Coinrule\n\n//@version=4\nstrategy(shorttitle=\'Optimized RSI Strategy\',title=\'Optimized RSI Strategy - Buy The Dips (by Coinrule)\', overlay=true, initial_capital = 1000, default_qty_type = strategy.percent_of_equity, default_qty_type = strategy.percent_of_equity, default_qty_value = 30, commission_type=strategy.commission.percent, commission_value=0.1)\n\n//Backtest dates\nfromMonth = input(defval = 1,    title = "From Month",      type = input.integer, minval = 1, maxval = 12)\nfromDay   = input(defval = 1,    title = "From Day",        type = input.integer, minval = 1, maxval = 31)\nfromYear  = input(defval = 2020, title = "From Year",       type = input.integer, minval = 1970)\nthruMonth = input(defval = 1,    title = "Thru Month",      type = input.integer, minval = 1, maxval = 12)\nthruDay   = input(defval = 1,    title = "Thru Day",        type = input.integer, minval = 1, maxval = 31)\nthruYear  = input(defval = 2112, title = "Thru Year",       type = input.integer, minval = 1970)\n\nshowDate  = input(defval = true, title = "Show Date Range", type = input.bool)\n\nstart     = timestamp(fromYear, fromMonth, fromDay, 00, 00)        // backtest start window\nfinish    = timestamp(thruYear, thruMonth, thruDay, 23, 59)        // backtest finish window\nwindow()  => true       // create function "within window of time"\n\n\n\n// RSI inputs and calculations\nlengthRSI = (14)\nRSI = rsi(close, lengthRSI)\n\nRSI_entry = input(35, title = \'RSI Entry\', minval=1)\nRSI_exit = input(65, title = \'RSI Close\', minval=1)\n\n//Calculate Moving Averages\nmovingaverage_signal = sma(close, input(100))\n\n//Entry \nstrategy.entry(id="long", long = true, when = RSI< RSI_entry and close < movingaverage_signal and window())\n\n//Exit\n//RSI\nstrategy.close("long", when = RSI > RSI_exit and window())\n\nplot (movingaverage_signal)'

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
