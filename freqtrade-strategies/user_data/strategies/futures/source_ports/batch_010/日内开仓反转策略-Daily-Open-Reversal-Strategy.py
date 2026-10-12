"""Source-faithful deep-assisted port of 日内开仓反转策略-Daily-Open-Reversal-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_e77b4aab(PinePortBase, IStrategy):
    source_file = '日内开仓反转策略-Daily-Open-Reversal-Strategy.md'
    timeframe = '1d'
    can_short = False
    source_defaults = {'PrevRange': 0.01, 'TP': 200, 'SL': 1000, 'startDate': 'title="Start Date"', 'startMonth': 'title="Start Month"', 'startYear': 'title="Start Year"', 'endDate': 'title="End Date"', 'endMonth': 'title="End Month"', 'endYear': 'title="End Year"'}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 100.0
    source_pyramiding = 0
    source_initial_capital = 10000.0
    source_commission_percent = 0.0
    source_features = ['strategy.exit', 'strategy.entry', 'strategy.position_size']
    source_fidelity_notes = ['Reads broker/strategy state; signals depend on fill timing and cannot be reduced to indicator-only booleans without changing behavior.', 'Uses strategy.exit; stop/limit/profit/loss/trailing arguments have Pine order semantics and may fill intrabar.']
    pine_assignments = [{'mode': '', 'name': 'PrevRange', 'op': '=', 'expr': 'input(0.0100, type=input.float, title="Previous Candle Range")', 'conditions': []}, {'mode': '', 'name': 'TP', 'op': '=', 'expr': 'input(200, title="Take Profit in pips")', 'conditions': []}, {'mode': '', 'name': 'SL', 'op': '=', 'expr': 'input(1000, title="Stop Loss in pips")', 'conditions': []}, {'mode': '', 'name': 'startDate', 'op': '=', 'expr': 'input(title="Start Date", type=input.integer, defval=1, minval=1, maxval=31)', 'conditions': []}, {'mode': '', 'name': 'startMonth', 'op': '=', 'expr': 'input(title="Start Month", type=input.integer, defval=1, minval=1, maxval=12)', 'conditions': []}, {'mode': '', 'name': 'startYear', 'op': '=', 'expr': 'input(title="Start Year", type=input.integer, defval=2015, minval=1800, maxval=2100)', 'conditions': []}, {'mode': '', 'name': 'endDate', 'op': '=', 'expr': 'input(title="End Date", type=input.integer, defval=31, minval=1, maxval=31)', 'conditions': []}, {'mode': '', 'name': 'endMonth', 'op': '=', 'expr': 'input(title="End Month", type=input.integer, defval=12, minval=1, maxval=12)', 'conditions': []}, {'mode': '', 'name': 'endYear', 'op': '=', 'expr': 'input(title="End Year", type=input.integer, defval=2020, minval=1800, maxval=2100)', 'conditions': []}, {'mode': '', 'name': 'isLong', 'op': '=', 'expr': 'strategy.position_size > 0', 'conditions': []}, {'mode': '', 'name': 'isShort', 'op': '=', 'expr': 'strategy.position_size < 0', 'conditions': []}, {'mode': '', 'name': 'longTrigger', 'op': '=', 'expr': '(open-close) > PrevRange and close<open', 'conditions': []}, {'mode': '', 'name': 'shortTrigger', 'op': '=', 'expr': '(close-open) > PrevRange and close>open', 'conditions': []}, {'mode': '', 'name': 'inDateRange', 'op': '=', 'expr': 'true', 'conditions': []}]
    pine_user_functions = []
    pine_controls = []
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry(id = "Long", long = true, when = (longTrigger and not isShort and inDateRange))', 'conditions': [], 'statement': 'strategy.entry(id = "Long", long = true, when = (longTrigger and not isShort and inDateRange))'}, {'kind': 'exit', 'call': 'strategy.exit("Exit Long", "Long", loss=SL, profit=TP)', 'conditions': [], 'statement': 'strategy.exit("Exit Long", "Long", loss=SL, profit=TP)'}, {'kind': 'entry', 'call': 'strategy.entry(id = "Short", long = false, when = (shortTrigger and not isLong and inDateRange))', 'conditions': [], 'statement': 'strategy.entry(id = "Short", long = false, when = (shortTrigger and not isLong and inDateRange))'}, {'kind': 'exit', 'call': 'strategy.exit("Exit Short", "Short", loss=SL, profit=TP)', 'conditions': [], 'statement': 'strategy.exit("Exit Short", "Short", loss=SL, profit=TP)'}]
    original_pine = '/*backtest\nstart: 2023-01-19 00:00:00\nend: 2024-01-25 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This source code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// @version=4\nstrategy("Daily Open Strategy", overlay=true, default_qty_type = strategy.percent_of_equity, default_qty_value = 100, initial_capital = 10000)\n\nPrevRange = input(0.0100, type=input.float, title="Previous Candle Range")\nTP = input(200, title="Take Profit in pips")\nSL = input(1000, title="Stop Loss in pips")\n\nstartDate = input(title="Start Date", type=input.integer,\n     defval=1, minval=1, maxval=31)\nstartMonth = input(title="Start Month", type=input.integer,\n     defval=1, minval=1, maxval=12)\nstartYear = input(title="Start Year", type=input.integer,\n     defval=2015, minval=1800, maxval=2100)\n\nendDate = input(title="End Date", type=input.integer,\n     defval=31, minval=1, maxval=31)\nendMonth = input(title="End Month", type=input.integer,\n     defval=12, minval=1, maxval=12)\nendYear = input(title="End Year", type=input.integer,\n     defval=2020, minval=1800, maxval=2100)\n\n\nisLong = strategy.position_size > 0\nisShort = strategy.position_size < 0\n\nlongTrigger = (open-close) > PrevRange and close<open \nshortTrigger = (close-open) > PrevRange and close>open\n\ninDateRange = true\n\n\nstrategy.entry(id = "Long", long = true, when = (longTrigger and not isShort and inDateRange))\nstrategy.exit("Exit Long", "Long", loss=SL, profit=TP) \n\nstrategy.entry(id = "Short", long = false, when = (shortTrigger and not isLong and inDateRange))\nstrategy.exit("Exit Short", "Short", loss=SL, profit=TP)'

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
