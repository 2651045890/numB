"""Source-faithful deep-assisted port of 智能型指数均线交易策略优化系统-Intelligent-Exponential-Moving-Average-Trading-Strategy-Optimization-System.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_15a95b4e(PinePortBase, IStrategy):
    source_file = '智能型指数均线交易策略优化系统-Intelligent-Exponential-Moving-Average-Trading-Strategy-Optimization-System.md'
    timeframe = '45m'
    can_short = True
    source_defaults = {'emaShortLength': 9, 'emaLongLength': 21, 'src': 'close'}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.entry', 'strategy.close']
    source_fidelity_notes = []
    pine_assignments = [{'mode': '', 'name': 'emaShortLength', 'op': '=', 'expr': 'input.int(9, title="Short EMA Length", minval=1)', 'conditions': []}, {'mode': '', 'name': 'emaLongLength', 'op': '=', 'expr': 'input.int(21, title="Long EMA Length", minval=1)', 'conditions': []}, {'mode': '', 'name': 'src', 'op': '=', 'expr': 'input(close, title="Source")', 'conditions': []}, {'mode': '', 'name': 'emaShort', 'op': '=', 'expr': 'ta.ema(src, emaShortLength)', 'conditions': []}, {'mode': '', 'name': 'emaLong', 'op': '=', 'expr': 'ta.ema(src, emaLongLength)', 'conditions': []}, {'mode': '', 'name': 'isUptrend', 'op': '=', 'expr': 'emaShort > emaLong', 'conditions': []}, {'mode': '', 'name': 'isDowntrend', 'op': '=', 'expr': 'emaShort < emaLong', 'conditions': []}, {'mode': '', 'name': 'longCondition', 'op': '=', 'expr': 'isUptrend and ta.crossover(close, emaShort)', 'conditions': []}, {'mode': '', 'name': 'shortCondition', 'op': '=', 'expr': 'isDowntrend and ta.crossunder(close, emaShort)', 'conditions': []}, {'mode': '', 'name': 'exitLong', 'op': '=', 'expr': 'ta.crossunder(close, emaShort)', 'conditions': []}, {'mode': '', 'name': 'exitShort', 'op': '=', 'expr': 'ta.crossover(close, emaShort)', 'conditions': []}]
    pine_user_functions = []
    pine_controls = [{'indent': 0, 'statement': 'if (longCondition)'}, {'indent': 0, 'statement': 'if (shortCondition)'}, {'indent': 0, 'statement': 'if (exitLong)'}, {'indent': 0, 'statement': 'if (exitShort)'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("Buy", strategy.long)', 'conditions': ['(longCondition)'], 'statement': 'strategy.entry("Buy", strategy.long)'}, {'kind': 'entry', 'call': 'strategy.entry("Sell", strategy.short)', 'conditions': ['(shortCondition)'], 'statement': 'strategy.entry("Sell", strategy.short)'}, {'kind': 'close', 'call': 'strategy.close("Buy")', 'conditions': ['(exitLong)'], 'statement': 'strategy.close("Buy")'}, {'kind': 'close', 'call': 'strategy.close("Sell")', 'conditions': ['(exitShort)'], 'statement': 'strategy.close("Sell")'}]
    original_pine = '/*backtest\nstart: 2024-12-19 00:00:00\nend: 2024-12-25 08:00:00\nperiod: 45m\nbasePeriod: 45m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This Pine Script™ code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © Jerryorange\n\n//@version=6\nstrategy("Smart EMA Algo", overlay=true)\n\n// Inputs\nemaShortLength = input.int(9, title="Short EMA Length", minval=1)\nemaLongLength = input.int(21, title="Long EMA Length", minval=1)\nsrc = input(close, title="Source")\n\n// EMA Calculations\nemaShort = ta.ema(src, emaShortLength)\nemaLong = ta.ema(src, emaLongLength)\n\n// Market Direction\nisUptrend = emaShort > emaLong\nisDowntrend = emaShort < emaLong\n\n// Entry Conditions\nlongCondition = isUptrend and ta.crossover(close, emaShort)\nshortCondition = isDowntrend and ta.crossunder(close, emaShort)\n\n// Exit Conditions\nexitLong = ta.crossunder(close, emaShort)\nexitShort = ta.crossover(close, emaShort)\n\n// Strategy Logic\nif (longCondition)\n    strategy.entry("Buy", strategy.long)\n\nif (shortCondition)\n    strategy.entry("Sell", strategy.short)\n\nif (exitLong)\n    strategy.close("Buy")\n\nif (exitShort)\n    strategy.close("Sell")\n\n// Plot EMAs\nplot(emaShort, color=color.blue, title="Short EMA")\nplot(emaLong, color=color.red, title="Long EMA")'

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
