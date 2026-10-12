"""Source-faithful deep-assisted port of 熊市MACD做空策略Bear-Market-MACD-Short-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_23bc7099(PinePortBase, IStrategy):
    source_file = '熊市MACD做空策略Bear-Market-MACD-Short-Strategy.md'
    timeframe = '2h'
    can_short = True
    source_defaults = {}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 30.0
    source_pyramiding = 0
    source_initial_capital = 10000.0
    source_commission_percent = 0.1
    source_features = ['strategy.exit', 'strategy.entry', 'strategy.position_size']
    source_fidelity_notes = ['Reads broker/strategy state; signals depend on fill timing and cannot be reduced to indicator-only booleans without changing behavior.', 'Uses strategy.exit; stop/limit/profit/loss/trailing arguments have Pine order semantics and may fill intrabar.']
    pine_assignments = [{'mode': '', 'name': 'slowEMA', 'op': '=', 'expr': 'ta.ema(close, 450)', 'conditions': []}, {'mode': '', 'name': 'goShortCondition1', 'op': '=', 'expr': 'ta.crossunder(macdLine, signalLine)', 'conditions': []}, {'mode': '', 'name': 'goShortCondition2', 'op': '=', 'expr': 'slowEMA > close', 'conditions': []}, {'mode': '', 'name': 'timePeriod', 'op': '=', 'expr': 'time >= timestamp(syminfo.timezone, 2021, 12, 1, 0, 0)', 'conditions': []}, {'mode': '', 'name': 'notInTrade', 'op': '=', 'expr': 'strategy.position_size <= 0', 'conditions': []}, {'mode': '', 'name': 'strategyDirection', 'op': '=', 'expr': 'strategy.direction.short', 'conditions': []}, {'mode': '', 'name': 'stopLoss', 'op': '=', 'expr': 'high * 1.04', 'conditions': ['(goShortCondition1 and goShortCondition2 and timePeriod and notInTrade)']}, {'mode': '', 'name': 'takeProfit', 'op': '=', 'expr': 'low * 0.92', 'conditions': ['(goShortCondition1 and goShortCondition2 and timePeriod and notInTrade)']}]
    pine_user_functions = []
    pine_controls = [{'indent': 0, 'statement': 'if (goShortCondition1 and goShortCondition2 and timePeriod and notInTrade)'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("Short", strategy.short)', 'conditions': ['(goShortCondition1 and goShortCondition2 and timePeriod and notInTrade)'], 'statement': 'strategy.entry("Short", strategy.short)'}, {'kind': 'exit', 'call': 'strategy.exit("exit","Short", stop=stopLoss, limit=takeProfit)', 'conditions': ['(goShortCondition1 and goShortCondition2 and timePeriod and notInTrade)'], 'statement': 'strategy.exit("exit","Short", stop=stopLoss, limit=takeProfit)'}]
    original_pine = '/*backtest\nstart: 2023-08-14 00:00:00\nend: 2023-09-13 00:00:00\nperiod: 2h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This source code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © Coinrule\n\n//@version=5\nstrategy("Shorting Bearish MACD Cross with Price Below EMA 450 (By Coinrule)", overlay=true, initial_capital = 10000, default_qty_value = 30, default_qty_type = strategy.percent_of_equity, commission_type=strategy.commission.percent, commission_value=0.1)\n\n// EMAs \nslowEMA = ta.ema(close, 450)\n\n// MACD\n[macdLine, signalLine, histogramLine] = ta.macd(close, 11, 26, 9)\n\n// Conditions\ngoShortCondition1 = ta.crossunder(macdLine, signalLine)\ngoShortCondition2 = slowEMA > close\n\ntimePeriod = time >= timestamp(syminfo.timezone, 2021, 12, 1, 0, 0)\nnotInTrade = strategy.position_size <= 0\nstrategyDirection = strategy.direction.short\n\nif (goShortCondition1 and goShortCondition2 and timePeriod and notInTrade)\n    stopLoss = high * 1.04\n    takeProfit = low * 0.92\n    strategy.entry("Short", strategy.short)\n    strategy.exit("exit","Short", stop=stopLoss, limit=takeProfit)\n    \nplot(slowEMA, color=color.green)'

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
