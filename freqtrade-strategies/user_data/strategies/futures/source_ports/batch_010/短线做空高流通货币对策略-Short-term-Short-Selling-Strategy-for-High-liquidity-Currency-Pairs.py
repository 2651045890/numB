"""Source-faithful deep-assisted port of 短线做空高流通货币对策略-Short-term-Short-Selling-Strategy-for-High-liquidity-Currency-Pairs.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_7d11e01a(PinePortBase, IStrategy):
    source_file = '短线做空高流通货币对策略-Short-term-Short-Selling-Strategy-for-High-liquidity-Currency-Pairs.md'
    timeframe = '1h'
    can_short = True
    source_defaults = {'shortDuration': 7, 'priceDropPercentage': 30, 'riskPerTrade': 1, 'stopLossPercent': 5, 'takeProfitPercent': 30}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.entry', 'strategy.close', 'strategy.opentrades', 'strategy.equity', 'var ', 'for ', 'alert']
    source_fidelity_notes = ['Uses persistent Pine state (var/varip); state is order-dependent and must be evaluated bar-by-bar, not replaced by a vectorized fill-forward approximation.', 'Reads broker/strategy state; signals depend on fill timing and cannot be reduced to indicator-only booleans without changing behavior.']
    pine_assignments = [{'mode': '', 'name': 'shortDuration', 'op': '=', 'expr': 'input.int(7, title="Short Duration (days)")', 'conditions': []}, {'mode': '', 'name': 'priceDropPercentage', 'op': '=', 'expr': 'input.float(30, title="Price Drop Percentage", minval=0, maxval=100)', 'conditions': []}, {'mode': '', 'name': 'riskPerTrade', 'op': '=', 'expr': 'input.float(1, title="Risk per Trade (%)", minval=0.1, maxval=100) / 100 // Risk per trade as a percentage of equity', 'conditions': []}, {'mode': '', 'name': 'stopLossPercent', 'op': '=', 'expr': 'input.float(5, title="Stop Loss Percentage", minval=0) // Stop Loss Percentage', 'conditions': []}, {'mode': '', 'name': 'takeProfitPercent', 'op': '=', 'expr': 'input.float(30, title="Take Profit Percentage", minval=0) // Take Profit Percentage', 'conditions': []}, {'mode': 'var', 'name': 'shortEnd', 'op': '=', 'expr': 'na', 'conditions': []}, {'mode': 'var', 'name': 'entryPrice', 'op': '=', 'expr': 'na', 'conditions': []}, {'mode': '', 'name': 'equity', 'op': '=', 'expr': 'strategy.equity', 'conditions': []}, {'mode': '', 'name': 'riskAmount', 'op': '=', 'expr': 'equity * riskPerTrade', 'conditions': []}, {'mode': '', 'name': 'pipValue', 'op': '=', 'expr': 'syminfo.pointvalue', 'conditions': []}, {'mode': '', 'name': 'stopLossPips', 'op': '=', 'expr': 'close * (stopLossPercent / 100)', 'conditions': []}, {'mode': '', 'name': 'positionSize', 'op': '=', 'expr': 'riskAmount / (stopLossPips * pipValue)', 'conditions': []}, {'mode': '', 'name': 'shortEnd', 'op': ':=', 'expr': 'bar_index + shortDuration', 'conditions': ['(strategy.opentrades == 0)']}, {'mode': '', 'name': 'entryPrice', 'op': ':=', 'expr': 'close', 'conditions': ['(strategy.opentrades == 0)']}, {'mode': '', 'name': 'exitCondition', 'op': '=', 'expr': '(bar_index >= shortEnd) or (close <= entryPrice * (1 - priceDropPercentage / 100))', 'conditions': []}, {'mode': '', 'name': 'stopLossCondition', 'op': '=', 'expr': '(close >= entryPrice * (1 + stopLossPercent / 100))', 'conditions': []}, {'mode': '', 'name': 'takeProfitCondition', 'op': '=', 'expr': '(close <= entryPrice * (1 - takeProfitPercent / 100))', 'conditions': []}]
    pine_user_functions = []
    pine_controls = [{'indent': 0, 'statement': 'if (strategy.opentrades == 0)'}, {'indent': 0, 'statement': 'if (strategy.opentrades > 0 and (exitCondition or stopLossCondition or takeProfitCondition))'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("Short", strategy.short, qty=positionSize)', 'conditions': ['(strategy.opentrades == 0)'], 'statement': 'strategy.entry("Short", strategy.short, qty=positionSize)'}, {'kind': 'close', 'call': 'strategy.close("Short")', 'conditions': ['(strategy.opentrades > 0 and (exitCondition or stopLossCondition or takeProfitCondition))'], 'statement': 'strategy.close("Short")'}]
    original_pine = '/*backtest\nstart: 2024-04-01 00:00:00\nend: 2024-04-30 23:59:59\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("Short High-Grossing Forex Pair", overlay=true)\n\n// Parameters\nshortDuration = input.int(7, title="Short Duration (days)")\npriceDropPercentage = input.float(30, title="Price Drop Percentage", minval=0, maxval=100)\nriskPerTrade = input.float(1, title="Risk per Trade (%)", minval=0.1, maxval=100) / 100  // Risk per trade as a percentage of equity\nstopLossPercent = input.float(5, title="Stop Loss Percentage", minval=0)  // Stop Loss Percentage\ntakeProfitPercent = input.float(30, title="Take Profit Percentage", minval=0)  // Take Profit Percentage\n\n// Initialize variables\nvar int shortEnd = na\nvar float entryPrice = na\n\n// Calculate dynamic position size\nequity = strategy.equity\nriskAmount = equity * riskPerTrade\npipValue = syminfo.pointvalue\nstopLossPips = close * (stopLossPercent / 100)\npositionSize = riskAmount / (stopLossPips * pipValue)\n\n// Entry condition: Enter short position at the first bar with calculated position size\nif (strategy.opentrades == 0)\n    strategy.entry("Short", strategy.short, qty=positionSize)\n    shortEnd := bar_index + shortDuration\n    entryPrice := close\n    alert("Entering short position", alert.freq_once_per_bar_close)\n\n// Exit conditions\nexitCondition = (bar_index >= shortEnd) or (close <= entryPrice * (1 - priceDropPercentage / 100))\n\n// Stop-loss and take-profit conditions\nstopLossCondition = (close >= entryPrice * (1 + stopLossPercent / 100))\ntakeProfitCondition = (close <= entryPrice * (1 - takeProfitPercent / 100))\n\n// Exit the short position based on the conditions\nif (strategy.opentrades > 0 and (exitCondition or stopLossCondition or takeProfitCondition))\n    strategy.close("Short")\n    alert("Exiting short position", alert.freq_once_per_bar_close)\n\n// Plot entry and exit points for visualization\nplotshape(series=strategy.opentrades > 0, location=location.belowbar, color=color.red, style=shape.labeldown, text="Short")\nplotshape(series=strategy.opentrades == 0, location=location.abovebar, color=color.green, style=shape.labelup, text="Exit")\n\n// Add alert conditions\nalertcondition(strategy.opentrades > 0, title="Short Entry Alert", message="Entering short position")\nalertcondition(strategy.opentrades == 0, title="Short Exit Alert", message="Exiting short position")'

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
