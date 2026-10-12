"""Source-faithful deep-assisted port of 比特币快速反转突破策略Bitcoin-Rapid-Reversal-Breakout-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_1dd389d9(PinePortBase, IStrategy):
    source_file = '比特币快速反转突破策略Bitcoin-Rapid-Reversal-Breakout-Strategy.md'
    timeframe = '10m'
    can_short = True
    source_defaults = {}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.entry']
    source_fidelity_notes = []
    pine_assignments = [{'mode': '', 'name': 'longCondition', 'op': '=', 'expr': 'open > sar(0.02,0.02,0.2) and open[1] < sar(0.02,0.02,0.2)[1] and open > sma(close,50)', 'conditions': []}, {'mode': '', 'name': 'takeprofit', 'op': '=', 'expr': 'strategy.position_avg_price * (1 + 0.005)', 'conditions': []}, {'mode': '', 'name': 'stopLoss', 'op': '=', 'expr': 'strategy.position_avg_price * (1 - 0.015)', 'conditions': []}, {'mode': '', 'name': 'shortCondition', 'op': '=', 'expr': 'open < sar(0.02,0.02,0.2) and open[1] > sar(0.02,0.02,0.2)[1] and open < sma(close,50)', 'conditions': []}, {'mode': '', 'name': 'take_profit', 'op': '=', 'expr': 'strategy.position_avg_price * (1 - 0.005)', 'conditions': []}, {'mode': '', 'name': 'stop_Loss', 'op': '=', 'expr': 'strategy.position_avg_price * (1 + 0.015)', 'conditions': []}]
    pine_user_functions = []
    pine_controls = [{'indent': 0, 'statement': 'if (longCondition)'}, {'indent': 0, 'statement': 'if (shortCondition)'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("longEntry", strategy.long, limit = takeprofit, stop = stopLoss)', 'conditions': ['(longCondition)'], 'statement': 'strategy.entry("longEntry", strategy.long, limit = takeprofit, stop = stopLoss)'}, {'kind': 'entry', 'call': 'strategy.entry("shortEntry", strategy.short, limit = take_profit, stop = stop_Loss)', 'conditions': ['(shortCondition)'], 'statement': 'strategy.entry("shortEntry", strategy.short, limit = take_profit, stop = stop_Loss)'}]
    original_pine = '/*backtest\nstart: 2023-09-12 00:00:00\nend: 2023-09-19 00:00:00\nperiod: 10m\nbasePeriod: 1m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This source code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © atakhadivi\n\n//@version=4\nstrategy("rapid fire", overlay=true)\n\nlongCondition = open > sar(0.02,0.02,0.2) and open[1] < sar(0.02,0.02,0.2)[1] and open > sma(close,50)\ntakeprofit = strategy.position_avg_price * (1 + 0.005)\nstopLoss = strategy.position_avg_price * (1 - 0.015)\nif (longCondition)\n    strategy.entry("longEntry", strategy.long, limit = takeprofit, stop = stopLoss)\n\n\nshortCondition = open < sar(0.02,0.02,0.2) and open[1] > sar(0.02,0.02,0.2)[1] and open < sma(close,50)\ntake_profit = strategy.position_avg_price * (1 - 0.005)\nstop_Loss = strategy.position_avg_price * (1 + 0.015)\nif (shortCondition)\n    strategy.entry("shortEntry", strategy.short, limit = take_profit, stop = stop_Loss)'

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
