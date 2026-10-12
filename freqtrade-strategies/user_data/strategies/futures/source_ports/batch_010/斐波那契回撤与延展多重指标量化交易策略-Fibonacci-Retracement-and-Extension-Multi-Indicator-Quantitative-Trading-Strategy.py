"""Source-faithful deep-assisted port of 斐波那契回撤与延展多重指标量化交易策略-Fibonacci-Retracement-and-Extension-Multi-Indicator-Quantitative-Trading-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_4cd6937e(PinePortBase, IStrategy):
    source_file = '斐波那契回撤与延展多重指标量化交易策略-Fibonacci-Retracement-and-Extension-Multi-Indicator-Quantitative-Trading-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.entry', 'var ', 'array.', 'for ', 'line.']
    source_fidelity_notes = ['Uses persistent Pine state (var/varip); state is order-dependent and must be evaluated bar-by-bar, not replaced by a vectorized fill-forward approximation.', 'Uses mutable Pine arrays; mutation order and per-bar persistence are load-bearing.', 'Drawing/table calls are display-only unless their IDs/state are later read; preserved in source map but excluded from trade signal calculation where non-causal.']
    pine_assignments = [{'mode': '', 'name': 'fibRetracementLevels', 'op': '=', 'expr': 'array.new_float(5)', 'conditions': []}, {'mode': '', 'name': 'fibExtensionLevels', 'op': '=', 'expr': 'array.new_float(5)', 'conditions': []}, {'mode': '', 'name': 'highPrice', 'op': '=', 'expr': 'ta.highest(high, 10)', 'conditions': []}, {'mode': '', 'name': 'lowPrice', 'op': '=', 'expr': 'ta.lowest(low, 10)', 'conditions': []}, {'mode': '', 'name': 'fibRetracement', 'op': '=', 'expr': 'array.new_float(5)', 'conditions': []}, {'mode': '', 'name': 'shortEMA', 'op': '=', 'expr': 'ta.ema(close, 20)', 'conditions': []}, {'mode': '', 'name': 'longEMA', 'op': '=', 'expr': 'ta.ema(close, 50)', 'conditions': []}, {'mode': '', 'name': 'isUptrend', 'op': '=', 'expr': 'shortEMA > longEMA', 'conditions': []}, {'mode': '', 'name': 'isDowntrend', 'op': '=', 'expr': 'shortEMA < longEMA', 'conditions': []}, {'mode': 'var', 'name': 'lastFibRetracementLevel', 'op': '=', 'expr': 'na', 'conditions': []}, {'mode': 'var', 'name': 'lastFibExtensionLevel', 'op': '=', 'expr': 'na', 'conditions': []}, {'mode': '', 'name': 'lastFibRetracementLevel', 'op': ':=', 'expr': 'array.get(fibRetracement, i)', 'conditions': ['(isUptrend)', '(close > array.get(fibRetracement, i))']}, {'mode': '', 'name': 'lastFibRetracementLevel', 'op': ':=', 'expr': 'array.get(fibRetracement, i)', 'conditions': ['(isDowntrend)', '(close < array.get(fibRetracement, i))']}]
    pine_user_functions = []
    pine_controls = [{'indent': 0, 'statement': 'for i = 0 to 4'}, {'indent': 0, 'statement': 'if (isUptrend)'}, {'indent': 4, 'statement': 'for i = 0 to 4'}, {'indent': 8, 'statement': 'if (close > array.get(fibRetracement, i))'}, {'indent': 0, 'statement': 'if (isDowntrend)'}, {'indent': 4, 'statement': 'for i = 0 to 4'}, {'indent': 8, 'statement': 'if (close < array.get(fibRetracement, i))'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("Buy", strategy.long)', 'conditions': ['(isUptrend)', '(close > array.get(fibRetracement, i))'], 'statement': 'strategy.entry("Buy", strategy.long)'}, {'kind': 'entry', 'call': 'strategy.entry("Sell", strategy.short)', 'conditions': ['(isDowntrend)', '(close < array.get(fibRetracement, i))'], 'statement': 'strategy.entry("Sell", strategy.short)'}]
    original_pine = '/*backtest\nstart: 2019-12-23 08:00:00\nend: 2024-11-11 00:00:00\nperiod: 1d\nbasePeriod: 1d\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("Fibonacci Retracement and Extension Strategy", overlay=true)\n\n// Define the Fibonacci levels for retracement and extension\nfibRetracementLevels = array.new_float(5)\narray.set(fibRetracementLevels, 0, 0.236)\narray.set(fibRetracementLevels, 1, 0.382)\narray.set(fibRetracementLevels, 2, 0.5)\narray.set(fibRetracementLevels, 3, 0.618)\narray.set(fibRetracementLevels, 4, 0.786)\n\nfibExtensionLevels = array.new_float(5)\narray.set(fibExtensionLevels, 0, 1.618)\narray.set(fibExtensionLevels, 1, 2.618)\narray.set(fibExtensionLevels, 2, 3.618)\narray.set(fibExtensionLevels, 3, 4.236)\narray.set(fibExtensionLevels, 4, 5.618)\n\n// Calculate the high and low prices for the last 10 bars\nhighPrice = ta.highest(high, 10)\nlowPrice = ta.lowest(low, 10)\n\n// Calculate the Fibonacci retracement levels\nfibRetracement = array.new_float(5)\nfor i = 0 to 4\n    array.set(fibRetracement, i, highPrice - (highPrice - lowPrice) * array.get(fibRetracementLevels, i))\n\n// Calculate the trend using the Exponential Moving Average (EMA)\nshortEMA = ta.ema(close, 20)\nlongEMA = ta.ema(close, 50)\n\n// Define the trend conditions\nisUptrend = shortEMA > longEMA\nisDowntrend = shortEMA < longEMA\n\n// Generate buy and sell signals\nvar float lastFibRetracementLevel = na\nvar float lastFibExtensionLevel = na\n\n// Buy condition: price crosses above the highest retracement level\nif (isUptrend)\n    for i = 0 to 4\n        if (close > array.get(fibRetracement, i))\n            lastFibRetracementLevel := array.get(fibRetracement, i)\n            strategy.entry("Buy", strategy.long)\n\n// Sell condition: price crosses below the lowest retracement level\nif (isDowntrend)\n    for i = 0 to 4\n        if (close < array.get(fibRetracement, i))\n            lastFibRetracementLevel := array.get(fibRetracement, i)\n            strategy.entry("Sell", strategy.short)\n\n// Plotting the Fibonacci levels on the chart\n// for i = 0 to 4\n//     line.new(bar_index[10], array.get(fibRetracement, i), bar_index, array.get(fibRetracement, i), color=color.new(color.blue, 70), width=1)\n\n// Plot the EMAs\nplot(shortEMA, color=color.red, title="Short EMA")\nplot(longEMA, color=color.blue, title="Long EMA")'

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
