"""Source-faithful deep-assisted port of 相对强度指数止损策略Relative-Strength-Index-Stop-Loss-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_8d82ddb1(PinePortBase, IStrategy):
    source_file = '相对强度指数止损策略Relative-Strength-Index-Stop-Loss-Strategy.md'
    timeframe = '5m'
    can_short = True
    source_defaults = {'rsiLength': 15, 'stopLossPercent': 1}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.exit', 'strategy.entry', 'strategy.close', 'strategy.equity', 'for ']
    source_fidelity_notes = ['Reads broker/strategy state; signals depend on fill timing and cannot be reduced to indicator-only booleans without changing behavior.', 'Uses strategy.exit; stop/limit/profit/loss/trailing arguments have Pine order semantics and may fill intrabar.']
    pine_assignments = [{'mode': '', 'name': 'rsiValue', 'op': '=', 'expr': 'ta.rsi(close, 7)', 'conditions': []}, {'mode': '', 'name': 'rsiLength', 'op': '=', 'expr': 'input(15, title="RSI Length")', 'conditions': []}, {'mode': '', 'name': 'rsiOverbought', 'op': '=', 'expr': '75', 'conditions': []}, {'mode': '', 'name': 'rsiOversold', 'op': '=', 'expr': '37', 'conditions': []}, {'mode': '', 'name': 'stopLossPercent', 'op': '=', 'expr': 'input(1, title="Stop Loss Percentage") / 100', 'conditions': []}, {'mode': '', 'name': 'equityLimit', 'op': '=', 'expr': 'strategy.equity * 0.97 // Set the daily loss limit to 3%', 'conditions': []}]
    pine_user_functions = []
    pine_controls = [{'indent': 0, 'statement': 'if (rsiValue < rsiOversold)'}, {'indent': 0, 'statement': 'if (rsiValue > rsiOverbought)'}, {'indent': 0, 'statement': 'if (rsiValue > rsiOverbought)'}, {'indent': 0, 'statement': 'if (rsiValue < rsiOversold)'}, {'indent': 0, 'statement': 'if (rsiValue < rsiOversold)'}, {'indent': 0, 'statement': 'if (rsiValue > rsiOverbought)'}, {'indent': 0, 'statement': 'if (rsiValue > rsiOverbought)'}, {'indent': 0, 'statement': 'if (rsiValue < rsiOversold)'}, {'indent': 0, 'statement': 'if (strategy.equity < equityLimit)'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("Buy", strategy.long)', 'conditions': ['(rsiValue < rsiOversold)'], 'statement': 'strategy.entry("Buy", strategy.long)'}, {'kind': 'exit', 'call': 'strategy.exit("Buy", from_entry="Buy", loss=close * stopLossPercent)', 'conditions': ['(rsiValue > rsiOverbought)'], 'statement': 'strategy.exit("Buy", from_entry="Buy", loss=close * stopLossPercent)'}, {'kind': 'entry', 'call': 'strategy.entry("Sell", strategy.short)', 'conditions': ['(rsiValue > rsiOverbought)'], 'statement': 'strategy.entry("Sell", strategy.short)'}, {'kind': 'exit', 'call': 'strategy.exit("Sell", from_entry="Sell", loss=close * stopLossPercent)', 'conditions': ['(rsiValue < rsiOversold)'], 'statement': 'strategy.exit("Sell", from_entry="Sell", loss=close * stopLossPercent)'}, {'kind': 'entry', 'call': 'strategy.entry("Buy", strategy.long)', 'conditions': ['(rsiValue < rsiOversold)'], 'statement': 'strategy.entry("Buy", strategy.long)'}, {'kind': 'exit', 'call': 'strategy.exit("Buy", from_entry="Buy", loss=close * stopLossPercent)', 'conditions': ['(rsiValue > rsiOverbought)'], 'statement': 'strategy.exit("Buy", from_entry="Buy", loss=close * stopLossPercent)'}, {'kind': 'entry', 'call': 'strategy.entry("Sell", strategy.short)', 'conditions': ['(rsiValue > rsiOverbought)'], 'statement': 'strategy.entry("Sell", strategy.short)'}, {'kind': 'exit', 'call': 'strategy.exit("Sell", from_entry="Sell", loss=close * stopLossPercent)', 'conditions': ['(rsiValue < rsiOversold)'], 'statement': 'strategy.exit("Sell", from_entry="Sell", loss=close * stopLossPercent)'}, {'kind': 'close_all', 'call': 'strategy.close_all()', 'conditions': ['(strategy.equity < equityLimit)'], 'statement': 'strategy.close_all()'}]
    original_pine = '//@version=5\nstrategy("RSI Strategy with Daily Loss Limit", overlay=true)\n\n// Define RSI conditions\nrsiValue = ta.rsi(close, 7)\nrsiLength = input(15, title="RSI Length")\nrsiOverbought = 75\nrsiOversold = 37\n\n// Define stop-loss percentage\nstopLossPercent = input(1, title="Stop Loss Percentage") / 100\n\n// Enter long (buy) when RSI is below 40 with stop-loss\nif (rsiValue < rsiOversold)\n    strategy.entry("Buy", strategy.long)\n\n// Exit long when RSI is above 80 or when stop-loss is hit\nif (rsiValue > rsiOverbought)\n    strategy.exit("Buy", from_entry="Buy", loss=close * stopLossPercent)\n\n// Enter short (sell) when RSI is above 80 with stop-loss\nif (rsiValue > rsiOverbought)\n    strategy.entry("Sell", strategy.short)\n\n// Exit short when RSI is below 40 or when stop-loss is hit\nif (rsiValue < rsiOversold)\n    strategy.exit("Sell", from_entry="Sell", loss=close * stopLossPercent)\n\n// Track account equity\nequityLimit = strategy.equity * 0.97  // Set the daily loss limit to 3%\n\n// Enter long (buy) when RSI is below 40\nif (rsiValue < rsiOversold)\n    strategy.entry("Buy", strategy.long)\n\n// Exit long when RSI is above 80 or when stop-loss is hit\nif (rsiValue > rsiOverbought)\n    strategy.exit("Buy", from_entry="Buy", loss=close * stopLossPercent)\n\n// Enter short (sell) when RSI is above 80\nif (rsiValue > rsiOverbought)\n    strategy.entry("Sell", strategy.short)\n\n// Exit short when RSI is below 40 or when stop-loss is hit\nif (rsiValue < rsiOversold)\n    strategy.exit("Sell", from_entry="Sell", loss=close * stopLossPercent)\n\n// Plot RSI on the chart\nplot(rsiValue, title="RSI", color=color.blue)\n\n// Stop trading for the day if the daily loss limit is reached\nif (strategy.equity < equityLimit)\n    strategy.close_all()'

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
