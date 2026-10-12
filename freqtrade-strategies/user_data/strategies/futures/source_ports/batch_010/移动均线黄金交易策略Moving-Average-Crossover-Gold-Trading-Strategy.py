"""Source-faithful deep-assisted port of 移动均线黄金交易策略Moving-Average-Crossover-Gold-Trading-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_eb98b43c(PinePortBase, IStrategy):
    source_file = '移动均线黄金交易策略Moving-Average-Crossover-Gold-Trading-Strategy.md'
    timeframe = '1h'
    can_short = True
    source_defaults = {}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.exit', 'strategy.entry', 'strategy.close', 'strategy.position_size']
    source_fidelity_notes = ['Reads broker/strategy state; signals depend on fill timing and cannot be reduced to indicator-only booleans without changing behavior.', 'Uses strategy.exit; stop/limit/profit/loss/trailing arguments have Pine order semantics and may fill intrabar.']
    pine_assignments = [{'mode': '', 'name': 'ma30', 'op': '=', 'expr': 'ta.sma(close, 30)', 'conditions': []}, {'mode': '', 'name': 'ma60', 'op': '=', 'expr': 'ta.sma(close, 60)', 'conditions': []}, {'mode': '', 'name': 'ma200', 'op': '=', 'expr': 'ta.sma(close, 200)', 'conditions': []}, {'mode': '', 'name': 'crossoverUp', 'op': '=', 'expr': 'ta.crossover(ma30, ma200)', 'conditions': []}, {'mode': '', 'name': 'crossoverDown', 'op': '=', 'expr': 'ta.crossunder(ma30, ma200)', 'conditions': []}, {'mode': '', 'name': 'longCondition', 'op': '=', 'expr': 'crossoverUp', 'conditions': []}, {'mode': '', 'name': 'shortCondition', 'op': '=', 'expr': 'crossoverDown', 'conditions': []}]
    pine_user_functions = []
    pine_controls = [{'indent': 0, 'statement': 'if (longCondition)'}, {'indent': 0, 'statement': 'if (shortCondition)'}, {'indent': 0, 'statement': 'if (strategy.position_size > 0)'}, {'indent': 4, 'statement': 'if (crossoverDown)'}, {'indent': 0, 'statement': 'if (strategy.position_size < 0)'}, {'indent': 4, 'statement': 'if (crossoverUp)'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("Buy", strategy.long)', 'conditions': ['(longCondition)'], 'statement': 'strategy.entry("Buy", strategy.long)'}, {'kind': 'exit', 'call': 'strategy.exit("Cover", "Buy", stop=close - 40.000, limit=close + 40.000)', 'conditions': ['(longCondition)'], 'statement': 'strategy.exit("Cover", "Buy", stop=close - 40.000, limit=close + 40.000)'}, {'kind': 'entry', 'call': 'strategy.entry("Sell", strategy.short)', 'conditions': ['(shortCondition)'], 'statement': 'strategy.entry("Sell", strategy.short)'}, {'kind': 'exit', 'call': 'strategy.exit("Cover", "Sell", stop=close + 40.000, limit=close - 40.000)', 'conditions': ['(shortCondition)'], 'statement': 'strategy.exit("Cover", "Sell", stop=close + 40.000, limit=close - 40.000)'}, {'kind': 'close', 'call': 'strategy.close("Buy")', 'conditions': ['(strategy.position_size > 0)', '(crossoverDown)'], 'statement': 'strategy.close("Buy")'}, {'kind': 'close', 'call': 'strategy.close("Sell")', 'conditions': ['(strategy.position_size < 0)', '(crossoverUp)'], 'statement': 'strategy.close("Sell")'}]
    original_pine = '/*backtest\nstart: 2024-01-01 00:00:00\nend: 2024-01-31 23:59:59\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("Moving Averages Crossover Strategy", overlay=true)\n\n// Moving Averages\nma30 = ta.sma(close, 30)\nma60 = ta.sma(close, 60)\nma200 = ta.sma(close, 200)\n\n// Moving Averages Crossover\ncrossoverUp = ta.crossover(ma30, ma200)\ncrossoverDown = ta.crossunder(ma30, ma200)\n\n// Buy and Sell Signals\nlongCondition = crossoverUp\nshortCondition = crossoverDown\n\n// Order Execution\nif (longCondition)\n    strategy.entry("Buy", strategy.long)\n    strategy.exit("Cover", "Buy", stop=close - 40.000, limit=close + 40.000)\nif (shortCondition)\n    strategy.entry("Sell", strategy.short)\n    strategy.exit("Cover", "Sell", stop=close + 40.000, limit=close - 40.000)\n\n// Plotting Moving Averages\nplot(ma30, color=color.blue, title="MA 30")\nplot(ma60, color=color.orange, title="MA 60")\nplot(ma200, color=color.green, title="MA 200")\n\n// Conditions to close opposite position\nif (strategy.position_size > 0)\n    if (crossoverDown)\n        strategy.close("Buy")\nif (strategy.position_size < 0)\n    if (crossoverUp)\n        strategy.close("Sell")'

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
