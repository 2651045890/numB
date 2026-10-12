"""Source-faithful deep-assisted port of 布林带超买超卖策略-Bollinger-Band-Overbought-Oversold-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_5135272b(PinePortBase, IStrategy):
    source_file = '布林带超买超卖策略-Bollinger-Band-Overbought-Oversold-Strategy.md'
    timeframe = '1d'
    can_short = False
    source_defaults = {}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.entry', 'strategy.close', 'strategy.opentrades', 'for ', 'line.']
    source_fidelity_notes = ['Reads broker/strategy state; signals depend on fill timing and cannot be reduced to indicator-only booleans without changing behavior.', 'Drawing/table calls are display-only unless their IDs/state are later read; preserved in source map but excluded from trade signal calculation where non-causal.']
    pine_assignments = [{'mode': '', 'name': 'sma200', 'op': '=', 'expr': 'ta.sma(close, 200)', 'conditions': []}, {'mode': '', 'name': 'length', 'op': '=', 'expr': '20 // Bollinger Band period', 'conditions': []}, {'mode': '', 'name': 'src', 'op': '=', 'expr': 'close // Source for Bollinger Bands', 'conditions': []}, {'mode': '', 'name': 'mult', 'op': '=', 'expr': '2.0 // Bollinger Band standard deviation multiplier', 'conditions': []}, {'mode': '', 'name': 'basis', 'op': '=', 'expr': 'ta.sma(src, length)', 'conditions': []}, {'mode': '', 'name': 'dev', 'op': '=', 'expr': 'ta.stdev(src, length)', 'conditions': []}, {'mode': '', 'name': 'upperBand', 'op': '=', 'expr': 'basis + mult * dev', 'conditions': []}, {'mode': '', 'name': 'lowerBand', 'op': '=', 'expr': 'basis - mult * dev', 'conditions': []}, {'mode': '', 'name': 'percentB', 'op': '=', 'expr': '(close - lowerBand) / (upperBand - lowerBand)', 'conditions': []}, {'mode': '', 'name': 'condition1', 'op': '=', 'expr': 'close > sma200 // Condition 1: Close is above the 200-day moving average', 'conditions': []}, {'mode': '', 'name': 'condition2', 'op': '=', 'expr': 'percentB[2] < 0.2 and percentB[1] < 0.2 and percentB < 0.2', 'conditions': []}, {'mode': '', 'name': 'buyCondition', 'op': '=', 'expr': 'condition1 and condition2', 'conditions': []}, {'mode': '', 'name': 'sellCondition', 'op': '=', 'expr': 'percentB > 0.8', 'conditions': []}]
    pine_user_functions = []
    pine_controls = [{'indent': 0, 'statement': 'if buyCondition'}, {'indent': 0, 'statement': 'if sellCondition'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("Buy", strategy.long)', 'conditions': ['buyCondition'], 'statement': 'strategy.entry("Buy", strategy.long)'}, {'kind': 'close', 'call': 'strategy.close("Buy")', 'conditions': ['sellCondition'], 'statement': 'strategy.close("Buy")'}]
    original_pine = '/*backtest\nstart: 2019-12-23 08:00:00\nend: 2024-09-24 08:00:00\nperiod: 1d\nbasePeriod: 1d\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This Pine Script™ code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © EdgeTools\n\n//@version=5\nstrategy("Larry Connors %b Strategy (Bollinger Band)", overlay=false)\n\n// Parameters for moving averages and Bollinger Bands\nsma200 = ta.sma(close, 200)\nlength = 20  // Bollinger Band period\nsrc = close  // Source for Bollinger Bands\nmult = 2.0   // Bollinger Band standard deviation multiplier\n\n// Calculate Bollinger Bands and %b\nbasis = ta.sma(src, length)\ndev = ta.stdev(src, length)\nupperBand = basis + mult * dev\nlowerBand = basis - mult * dev\npercentB = (close - lowerBand) / (upperBand - lowerBand)\n\n// Conditions for the strategy\ncondition1 = close > sma200  // Condition 1: Close is above the 200-day moving average\n\n// %b must be below 0.2 for the last three consecutive days\ncondition2 = percentB[2] < 0.2 and percentB[1] < 0.2 and percentB < 0.2\n\n// Combined buy condition\nbuyCondition = condition1 and condition2\n\n// Sell condition: %b closes above 0.8\nsellCondition = percentB > 0.8\n\n// Execute buy signal when buy condition is met\nif buyCondition\n    strategy.entry("Buy", strategy.long)\n\n// Execute sell signal when the sell condition is met\nif sellCondition\n    strategy.close("Buy")\n\n// Plotting Bollinger Bands\nplot(upperBand, color=color.new(color.rgb(255, 0, 0), 50), title="Upper Bollinger Band")  // Red color with 50% transparency\nplot(lowerBand, color=color.new(color.rgb(0, 255, 0), 50), title="Lower Bollinger Band")  // Green color with 50% transparency\nplot(basis, color=color.rgb(0, 0, 255), title="Middle Bollinger Band")  // Blue color\n\n// Plot %b value for visual confirmation\nplot(percentB, color=color.rgb(128, 0, 128), linewidth=2, title="%b Value")  // Purple color\n\n// Additional lines to improve visualization\nhline(0.2, "Oversold (0.2)", color=color.rgb(255, 165, 0), linestyle=hline.style_dashed)  // Orange dashed line at 0.2\nhline(0.8, "Overbought (0.8)", color=color.rgb(255, 105, 180), linestyle=hline.style_dashed)  // Pink dashed line at 0.8\n\n// Set background color when a position is open\nbgcolor(strategy.opentrades > 0 ? color.new(color.green, 50) : na)'

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
