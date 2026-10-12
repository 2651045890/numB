"""Source-faithful deep-assisted port of 牛市回调短线策略Scalping-Dips-in-Bull-Market-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_ae9ac21d(PinePortBase, IStrategy):
    source_file = '牛市回调短线策略Scalping-Dips-in-Bull-Market-Strategy.md'
    timeframe = '1h'
    can_short = False
    source_defaults = {'fromMonth': 1, 'fromDay': 10, 'fromYear': 2020, 'thruMonth': 1, 'thruDay': 1, 'thruYear': 2112, 'showDate': True, 'inp_lkb': 1, 'MA': 50}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 30.0
    source_pyramiding = 0
    source_initial_capital = 1000.0
    source_commission_percent = 0.1
    source_features = ['strategy.entry', 'strategy.close', '=>']
    source_fidelity_notes = []
    pine_assignments = [{'mode': '', 'name': 'fromMonth', 'op': '=', 'expr': 'input(defval = 1, title = "From Month")', 'conditions': []}, {'mode': '', 'name': 'fromDay', 'op': '=', 'expr': 'input(defval = 10, title = "From Day")', 'conditions': []}, {'mode': '', 'name': 'fromYear', 'op': '=', 'expr': 'input(defval = 2020, title = "From Year")', 'conditions': []}, {'mode': '', 'name': 'thruMonth', 'op': '=', 'expr': 'input(defval = 1, title = "Thru Month")', 'conditions': []}, {'mode': '', 'name': 'thruDay', 'op': '=', 'expr': 'input(defval = 1, title = "Thru Day")', 'conditions': []}, {'mode': '', 'name': 'thruYear', 'op': '=', 'expr': 'input(defval = 2112, title = "Thru Year")', 'conditions': []}, {'mode': '', 'name': 'showDate', 'op': '=', 'expr': 'input(defval = true, title = "Show Date Range")', 'conditions': []}, {'mode': '', 'name': 'start', 'op': '=', 'expr': 'timestamp(fromYear, fromMonth, fromDay, 00, 00) // backtest start window', 'conditions': []}, {'mode': '', 'name': 'finish', 'op': '=', 'expr': 'timestamp(thruYear, thruMonth, thruDay, 23, 59) // backtest finish window', 'conditions': []}, {'mode': '', 'name': 'inp_lkb', 'op': '=', 'expr': "input(1, title='Lookback Period')", 'conditions': []}, {'mode': '', 'name': 'overall_change', 'op': '=', 'expr': '((close[0] - close[lkb]) / close[lkb]) * 100', 'conditions': []}, {'mode': '', 'name': 'overall', 'op': '=', 'expr': 'perc_change(inp_lkb)', 'conditions': []}, {'mode': '', 'name': 'MA', 'op': '=', 'expr': "input(50, title='Moving Average')", 'conditions': []}, {'mode': '', 'name': 'MAsignal', 'op': '=', 'expr': 'sma(close, MA)', 'conditions': []}, {'mode': '', 'name': 'dip', 'op': '=', 'expr': '-(input(2))', 'conditions': []}, {'mode': '', 'name': 'Stop_loss', 'op': '=', 'expr': '((input (10))/100)', 'conditions': []}, {'mode': '', 'name': 'Take_profit', 'op': '=', 'expr': '((input (3))/100)', 'conditions': []}, {'mode': '', 'name': 'longStopPrice', 'op': '=', 'expr': 'strategy.position_avg_price * (1 - Stop_loss)', 'conditions': []}, {'mode': '', 'name': 'longTakeProfit', 'op': '=', 'expr': 'strategy.position_avg_price * (1 + Take_profit)', 'conditions': []}]
    pine_user_functions = [{'name': 'window', 'args': '', 'body': 'true'}, {'name': 'perc_change', 'args': 'lkb', 'body': ''}]
    pine_controls = []
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry(id="long", long = true, when = overall< dip and MAsignal > close and window())', 'conditions': [], 'statement': 'strategy.entry(id="long", long = true, when = overall< dip and MAsignal > close and window())'}, {'kind': 'close', 'call': 'strategy.close("long", when = close < longStopPrice or close > longTakeProfit and window())', 'conditions': [], 'statement': 'strategy.close("long", when = close < longStopPrice or close > longTakeProfit and window())'}]
    original_pine = '/*backtest\nstart: 2023-12-30 00:00:00\nend: 2024-01-29 00:00:00\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This source code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © Coinrule\n\n//@version=3\nstrategy(shorttitle=\'Scalping Dips On Trend\',title=\'Scalping Dips On Trend (by Coinrule)\', overlay=true, initial_capital = 1000, default_qty_type = strategy.percent_of_equity, default_qty_value = 30, commission_type=strategy.commission.percent, commission_value=0.1)\n\n//Backtest dates\nfromMonth = input(defval = 1,  title = "From Month")     \nfromDay   = input(defval = 10,    title = "From Day")       \nfromYear  = input(defval = 2020, title = "From Year")       \nthruMonth = input(defval = 1,    title = "Thru Month")     \nthruDay   = input(defval = 1,    title = "Thru Day")     \nthruYear  = input(defval = 2112, title = "Thru Year")       \n\nshowDate  = input(defval = true, title = "Show Date Range")\n\nstart     = timestamp(fromYear, fromMonth, fromDay, 00, 00)        // backtest start window\nfinish    = timestamp(thruYear, thruMonth, thruDay, 23, 59)        // backtest finish window\nwindow()  => true\n\ninp_lkb = input(1, title=\'Lookback Period\')\n \nperc_change(lkb) =>\n    overall_change = ((close[0] - close[lkb]) / close[lkb]) * 100\n\n// Call the function    \noverall = perc_change(inp_lkb)\n\n//MA inputs and calculations\nMA=input(50, title=\'Moving Average\')\n\nMAsignal = sma(close, MA)\n\n//Entry\n\ndip= -(input(2))\n\nstrategy.entry(id="long", long = true, when = overall< dip and MAsignal > close and window()) \n\n//Exit\nStop_loss= ((input (10))/100)\nTake_profit= ((input (3))/100)\n\nlongStopPrice  = strategy.position_avg_price * (1 - Stop_loss)\nlongTakeProfit = strategy.position_avg_price * (1 + Take_profit)\n\nstrategy.close("long", when = close < longStopPrice or close > longTakeProfit and window())'

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
