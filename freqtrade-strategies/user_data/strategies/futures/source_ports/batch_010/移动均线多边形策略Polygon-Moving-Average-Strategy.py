"""Source-faithful deep-assisted port of 移动均线多边形策略Polygon-Moving-Average-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_2fb80f04(PinePortBase, IStrategy):
    source_file = '移动均线多边形策略Polygon-Moving-Average-Strategy.md'
    timeframe = '1h'
    can_short = True
    source_defaults = {'fromDay': 1, 'fromMonth': 1, 'fromYear': 2019, 'toDay': 1, 'toMonth': 1, 'toYear': 2020}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 100.0
    source_pyramiding = 1
    source_initial_capital = 5000.0
    source_commission_percent = 0.075
    source_features = ['strategy.exit', 'strategy.entry']
    source_fidelity_notes = ['Uses strategy.exit; stop/limit/profit/loss/trailing arguments have Pine order semantics and may fill intrabar.']
    pine_assignments = [{'mode': '', 'name': 'fromDay', 'op': '=', 'expr': 'input(defval = 1, title = "From Day", minval = 1, maxval = 31)', 'conditions': []}, {'mode': '', 'name': 'fromMonth', 'op': '=', 'expr': 'input(defval = 1, title = "From Month", minval = 1, maxval = 12)', 'conditions': []}, {'mode': '', 'name': 'fromYear', 'op': '=', 'expr': 'input(defval = 2019, title = "From Year", minval = 1970)', 'conditions': []}, {'mode': '', 'name': 'toDay', 'op': '=', 'expr': 'input(defval = 1, title = "To Day", minval = 1, maxval = 31)', 'conditions': []}, {'mode': '', 'name': 'toMonth', 'op': '=', 'expr': 'input(defval = 1, title = "To Month", minval = 1, maxval = 12)', 'conditions': []}, {'mode': '', 'name': 'toYear', 'op': '=', 'expr': 'input(defval = 2020, title = "To Year", minval = 1970)', 'conditions': []}, {'mode': '', 'name': 'startDate', 'op': '=', 'expr': 'timestamp(fromYear, fromMonth, fromDay, 00, 00)', 'conditions': []}, {'mode': '', 'name': 'finishDate', 'op': '=', 'expr': 'timestamp(toYear, toMonth, toDay, 00, 00)', 'conditions': []}, {'mode': '', 'name': 'time_cond', 'op': '=', 'expr': 'true', 'conditions': []}, {'mode': '', 'name': 'ema1', 'op': '=', 'expr': 'ema(close,input(3))', 'conditions': []}, {'mode': '', 'name': 'ema2', 'op': '=', 'expr': 'ema(close,input(7))', 'conditions': []}, {'mode': '', 'name': 'ema3', 'op': '=', 'expr': 'ema(close,input(13))', 'conditions': []}, {'mode': '', 'name': 'longCondition', 'op': '=', 'expr': 'close>ema1 and ema1>ema2 and ema2>ema3 and time_cond', 'conditions': []}, {'mode': '', 'name': 'shortCondition', 'op': '=', 'expr': 'close<ema1 and ema1<ema2 and ema2<ema3 and time_cond', 'conditions': []}]
    pine_user_functions = []
    pine_controls = [{'indent': 0, 'statement': 'if (longCondition)'}, {'indent': 0, 'statement': 'if (shortCondition)'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("Long", strategy.long)', 'conditions': ['(longCondition)'], 'statement': 'strategy.entry("Long", strategy.long)'}, {'kind': 'exit', 'call': 'strategy.exit("Long Exit", "Long", trail_points = close * 0.05 / syminfo.mintick, trail_offset = close * 0.02 / syminfo.mintick)', 'conditions': [], 'statement': 'strategy.exit("Long Exit", "Long", trail_points = close * 0.05 / syminfo.mintick, trail_offset = close * 0.02 / syminfo.mintick)'}, {'kind': 'entry', 'call': 'strategy.entry("Short", strategy.short)', 'conditions': ['(shortCondition)'], 'statement': 'strategy.entry("Short", strategy.short)'}, {'kind': 'exit', 'call': 'strategy.exit("Short Exit", "Short", trail_points = close * 0.05 / syminfo.mintick, trail_offset = close * 0.02 / syminfo.mintick)', 'conditions': [], 'statement': 'strategy.exit("Short Exit", "Short", trail_points = close * 0.05 / syminfo.mintick, trail_offset = close * 0.02 / syminfo.mintick)'}]
    original_pine = '/*backtest\nstart: 2023-09-30 00:00:00\nend: 2023-10-30 00:00:00\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This source code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © Crypto-Oli\n\n//@version=4\nstrategy("BLANK Strategy + TSL", initial_capital=5000, default_qty_type=strategy.percent_of_equity, default_qty_value=100, commission_type=strategy.commission.percent, pyramiding=1, commission_value=0.075, overlay=true)\n\n////////////////////////////////////////////////////////////////////////////////\n// BACKTESTING RANGE\n \n// From Date Inputs\nfromDay = input(defval = 1, title = "From Day", minval = 1, maxval = 31)\nfromMonth = input(defval = 1, title = "From Month", minval = 1, maxval = 12)\nfromYear = input(defval = 2019, title = "From Year", minval = 1970)\n \n// To Date Inputs\ntoDay = input(defval = 1, title = "To Day", minval = 1, maxval = 31)\ntoMonth = input(defval = 1, title = "To Month", minval = 1, maxval = 12)\ntoYear = input(defval = 2020, title = "To Year", minval = 1970)\n \n// Calculate start/end date and time condition\nstartDate = timestamp(fromYear, fromMonth, fromDay, 00, 00)\nfinishDate = timestamp(toYear, toMonth, toDay, 00, 00)\ntime_cond = true\n \n////////////////////////////////////////////////////////////////////////////////\n\n\n/// YOUR INPUTS BELOW - DELET EXAPLES ///\n\n\nema1=ema(close,input(3))\nema2=ema(close,input(7))\nema3=ema(close,input(13))\n\n\n/// PLOTS IF YOU NEED BELOW - DELET EXAPLES ///\n\n\nplot(ema1, "EMA1", color.yellow)\nplot(ema2, "EMA2", color.white)\nplot(ema3, "EMA3", color.blue)\n\n\n/// YOUR CONDITIONS BELOW - DELET EXAPLES ///\n\n\nlongCondition = close>ema1 and ema1>ema2 and ema2>ema3 and time_cond\nshortCondition = close<ema1 and ema1<ema2 and ema2<ema3 and time_cond\n\n/// EXECUTION ///\n\n\nif (longCondition)\n    strategy.entry("Long", strategy.long)\nstrategy.exit("Long Exit", "Long", trail_points = close * 0.05 / syminfo.mintick, trail_offset = close * 0.02 / syminfo.mintick)\n\nif (shortCondition)\n    strategy.entry("Short", strategy.short)\nstrategy.exit("Short Exit", "Short", trail_points = close * 0.05 / syminfo.mintick, trail_offset = close * 0.02 / syminfo.mintick)'

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
