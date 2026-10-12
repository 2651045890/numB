"""Source-faithful deep-assisted port of 抛物线转向SAR策略Parabolic-SAR-Reversal-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_a30d3386(PinePortBase, IStrategy):
    source_file = '抛物线转向SAR策略Parabolic-SAR-Reversal-Strategy.md'
    timeframe = '3h'
    can_short = True
    source_defaults = {'start': 0.02, 'increment': 0.02, 'maximum': 0.2, 'fromDay': 1, 'fromMonth': 1, 'fromYear': 2018, 'toDay': 1, 'toMonth': 1, 'toYear': 2019}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.entry', 'strategy.close', 'strategy.cancel']
    source_fidelity_notes = []
    pine_assignments = [{'mode': '', 'name': 'start', 'op': '=', 'expr': 'input(0.02)', 'conditions': []}, {'mode': '', 'name': 'increment', 'op': '=', 'expr': 'input(0.02)', 'conditions': []}, {'mode': '', 'name': 'maximum', 'op': '=', 'expr': 'input(0.2)', 'conditions': []}, {'mode': '', 'name': 'fromDay', 'op': '=', 'expr': 'input(defval = 1, title = "From Day", minval = 1, maxval = 31)', 'conditions': []}, {'mode': '', 'name': 'fromMonth', 'op': '=', 'expr': 'input(defval = 1, title = "From Month", minval = 1, maxval = 12)', 'conditions': []}, {'mode': '', 'name': 'fromYear', 'op': '=', 'expr': 'input(defval = 2018, title = "From Year", minval = 1970)', 'conditions': []}, {'mode': '', 'name': 'toDay', 'op': '=', 'expr': 'input(defval = 1, title = "To Day", minval = 1, maxval = 31)', 'conditions': []}, {'mode': '', 'name': 'toMonth', 'op': '=', 'expr': 'input(defval = 1, title = "To Month", minval = 1, maxval = 12)', 'conditions': []}, {'mode': '', 'name': 'toYear', 'op': '=', 'expr': 'input(defval = 2019, title = "To Year", minval = 1970)', 'conditions': []}, {'mode': '', 'name': 'startDate', 'op': '=', 'expr': 'timestamp(fromYear, fromMonth, fromDay, 00, 00)', 'conditions': []}, {'mode': '', 'name': 'finishDate', 'op': '=', 'expr': 'timestamp(toYear, toMonth, toDay, 00, 00)', 'conditions': []}, {'mode': '', 'name': 'time_cond', 'op': '=', 'expr': 'true', 'conditions': []}, {'mode': '', 'name': 'psar', 'op': '=', 'expr': 'sar(start, increment, maximum)', 'conditions': []}, {'mode': '', 'name': 'psar_long', 'op': '=', 'expr': 'high[1] < psar[2] and high > psar[1]', 'conditions': []}, {'mode': '', 'name': 'psar_short', 'op': '=', 'expr': 'low[1] > psar[2] and low < psar[1]', 'conditions': []}]
    pine_user_functions = []
    pine_controls = [{'indent': 0, 'statement': 'if (psar >= high and time_cond)'}, {'indent': 0, 'statement': 'else'}, {'indent': 0, 'statement': 'if (psar <= low and time_cond)'}, {'indent': 0, 'statement': 'else'}, {'indent': 0, 'statement': 'if (not time_cond)'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("ParLE", strategy.long, stop=psar, comment="ParLE")', 'conditions': ['(psar >= high and time_cond)'], 'statement': 'strategy.entry("ParLE", strategy.long, stop=psar, comment="ParLE")'}, {'kind': 'cancel', 'call': 'strategy.cancel("ParLE")', 'conditions': ['ELSE'], 'statement': 'strategy.cancel("ParLE")'}, {'kind': 'entry', 'call': 'strategy.entry("ParSE", strategy.short, stop=psar, comment="ParSE")', 'conditions': ['(psar <= low and time_cond)'], 'statement': 'strategy.entry("ParSE", strategy.short, stop=psar, comment="ParSE")'}, {'kind': 'cancel', 'call': 'strategy.cancel("ParSE")', 'conditions': ['ELSE'], 'statement': 'strategy.cancel("ParSE")'}, {'kind': 'close_all', 'call': 'strategy.close_all()', 'conditions': ['(not time_cond)'], 'statement': 'strategy.close_all()'}]
    original_pine = '/*backtest\nstart: 2023-08-18 00:00:00\nend: 2023-09-17 00:00:00\nperiod: 3h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=3\nstrategy("Parabolic SAR Strategy", overlay=true)\n\n// \n// author: Kozlod\n// date: 2018-09-03\n// https://www.tradingview.com/u/Kozlod/\n// \n\nstart = input(0.02)\nincrement = input(0.02)\nmaximum = input(0.2)\n\n////////////////////////////////////////////////////////////////////////////////\n// BACKTESTING RANGE\n \n// From Date Inputs\nfromDay = input(defval = 1, title = "From Day", minval = 1, maxval = 31)\nfromMonth = input(defval = 1, title = "From Month", minval = 1, maxval = 12)\nfromYear = input(defval = 2018, title = "From Year", minval = 1970)\n \n// To Date Inputs\ntoDay = input(defval = 1, title = "To Day", minval = 1, maxval = 31)\ntoMonth = input(defval = 1, title = "To Month", minval = 1, maxval = 12)\ntoYear = input(defval = 2019, title = "To Year", minval = 1970)\n \n// Calculate start/end date and time condition\nstartDate = timestamp(fromYear, fromMonth, fromDay, 00, 00)\nfinishDate = timestamp(toYear, toMonth, toDay, 00, 00)\ntime_cond = true\n \n////////////////////////////////////////////////////////////////////////////////\n\npsar = sar(start, increment, maximum)\n\n// Signals\npsar_long  = high[1] < psar[2] and high > psar[1] \npsar_short = low[1]  > psar[2] and low  < psar[1] \n\n// Plot PSAR\nplotshape(psar, location = location.absolute, style = shape.cross, size = size.tiny, color = low < psar[1] and not psar_long ? green : red)\n\n\nif (psar >= high and time_cond)\n    strategy.entry("ParLE", strategy.long, stop=psar, comment="ParLE")\nelse\n    strategy.cancel("ParLE")\n\nif (psar <= low and time_cond)\n    strategy.entry("ParSE", strategy.short, stop=psar, comment="ParSE")\nelse\n    strategy.cancel("ParSE")\n\nif (not time_cond)\n    strategy.close_all()'

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
