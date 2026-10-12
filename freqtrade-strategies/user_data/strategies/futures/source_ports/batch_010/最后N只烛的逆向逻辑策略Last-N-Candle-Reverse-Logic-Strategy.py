"""Source-faithful deep-assisted port of 最后N只烛的逆向逻辑策略Last-N-Candle-Reverse-Logic-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_b1bab38d(PinePortBase, IStrategy):
    source_file = '最后N只烛的逆向逻辑策略Last-N-Candle-Reverse-Logic-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'numCandlesToCheck': 5, 'numCandlesToExit': 2, 'investmentValue': 10000, 'inverseLogic': False}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.entry', 'strategy.close', 'var ', 'for ', '=>']
    source_fidelity_notes = ['Uses persistent Pine state (var/varip); state is order-dependent and must be evaluated bar-by-bar, not replaced by a vectorized fill-forward approximation.']
    pine_assignments = [{'mode': '', 'name': 'numCandlesToCheck', 'op': '=', 'expr': 'input(5, title="Number of Candles to Check")', 'conditions': []}, {'mode': '', 'name': 'numCandlesToExit', 'op': '=', 'expr': 'input(2, title="Number of Candles To Exit") // Corrected the input title', 'conditions': []}, {'mode': 'var', 'name': 'consecutiveGreenCandles', 'op': '=', 'expr': '0', 'conditions': []}, {'mode': 'var', 'name': 'consecutiveRedCandles', 'op': '=', 'expr': '0', 'conditions': []}, {'mode': 'var', 'name': 'barsSinceEntry', 'op': '=', 'expr': '0', 'conditions': []}, {'mode': '', 'name': 'consecutiveGreenCandles', 'op': ':=', 'expr': 'consecutiveGreenCandles + 1', 'conditions': ['isGreenCandle(i)']}, {'mode': '', 'name': 'consecutiveRedCandles', 'op': ':=', 'expr': '0 // Reset the count for consecutive red candles', 'conditions': ['isGreenCandle(i)']}, {'mode': '', 'name': 'consecutiveRedCandles', 'op': ':=', 'expr': 'consecutiveRedCandles + 1', 'conditions': ['isRedCandle(i)']}, {'mode': '', 'name': 'consecutiveGreenCandles', 'op': ':=', 'expr': '0 // Reset the count for consecutive green candles', 'conditions': ['isRedCandle(i)']}, {'mode': '', 'name': 'lastNCandlesGreen', 'op': '=', 'expr': 'consecutiveGreenCandles >= numCandlesToCheck', 'conditions': []}, {'mode': '', 'name': 'lastNCandlesRed', 'op': '=', 'expr': 'consecutiveRedCandles >= numCandlesToCheck', 'conditions': []}, {'mode': '', 'name': 'investmentValue', 'op': '=', 'expr': 'input(10000, title="Investment Value")', 'conditions': []}, {'mode': 'var', 'name': 'assetPrice', 'op': '=', 'expr': 'close', 'conditions': []}, {'mode': 'var', 'name': 'quantity', 'op': '=', 'expr': 'investmentValue / assetPrice', 'conditions': []}, {'mode': '', 'name': 'inverseLogic', 'op': '=', 'expr': 'input(false, title="inverseLogic")', 'conditions': []}, {'mode': '', 'name': 'barsSinceEntry', 'op': ':=', 'expr': '0', 'conditions': ['lastNCandlesGreen']}, {'mode': '', 'name': 'barsSinceEntry', 'op': ':=', 'expr': '0', 'conditions': ['lastNCandlesRed']}, {'mode': '', 'name': 'barsSinceEntry', 'op': ':=', 'expr': 'barsSinceEntry + 1', 'conditions': []}]
    pine_user_functions = [{'name': 'isGreenCandle', 'args': 'candle', 'body': ''}, {'name': 'isRedCandle', 'args': 'candle', 'body': ''}]
    pine_controls = [{'indent': 0, 'statement': 'for i = 0 to numCandlesToCheck - 1'}, {'indent': 4, 'statement': 'if isGreenCandle(i)'}, {'indent': 4, 'statement': 'else if isRedCandle(i)'}, {'indent': 0, 'statement': 'if lastNCandlesGreen'}, {'indent': 4, 'statement': 'if inverseLogic'}, {'indent': 4, 'statement': 'else'}, {'indent': 0, 'statement': 'if lastNCandlesRed'}, {'indent': 4, 'statement': 'if inverseLogic'}, {'indent': 4, 'statement': 'else'}, {'indent': 0, 'statement': 'if barsSinceEntry >= numCandlesToExit'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("Short", strategy.long, qty = quantity)', 'conditions': ['lastNCandlesGreen', 'inverseLogic'], 'statement': 'strategy.entry("Short", strategy.long, qty = quantity)'}, {'kind': 'entry', 'call': 'strategy.entry("Buy", strategy.long, qty = quantity)// Reset barsSinceEntry when entering a trade', 'conditions': ['lastNCandlesGreen', 'ELSE'], 'statement': 'strategy.entry("Buy", strategy.long, qty = quantity)// Reset barsSinceEntry when entering a trade'}, {'kind': 'entry', 'call': 'strategy.entry("Buy", strategy.long, qty = quantity)', 'conditions': ['lastNCandlesRed', 'inverseLogic'], 'statement': 'strategy.entry("Buy", strategy.long, qty = quantity)'}, {'kind': 'entry', 'call': 'strategy.entry("Short", strategy.short, qty = quantity)', 'conditions': ['lastNCandlesRed', 'ELSE'], 'statement': 'strategy.entry("Short", strategy.short, qty = quantity)'}, {'kind': 'close', 'call': 'strategy.close("Buy")', 'conditions': ['barsSinceEntry >= numCandlesToExit'], 'statement': 'strategy.close("Buy")'}, {'kind': 'close', 'call': 'strategy.close("Short")', 'conditions': ['barsSinceEntry >= numCandlesToExit'], 'statement': 'strategy.close("Short")'}]
    original_pine = '/*backtest\nstart: 2022-12-25 00:00:00\nend: 2023-12-25 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=4\nstrategy("Last Number of  Candles", overlay=true)\n\n// Define the condition for a green candle\nisGreenCandle(candle) =>\n    close[candle] > open[candle]\n\n// Define the condition for a red candle\nisRedCandle(candle) =>\n    close[candle] < open[candle]\n\n// Input to specify the number of candles to check\nnumCandlesToCheck = input(5, title="Number of Candles to Check")\nnumCandlesToExit = input(2, title="Number of Candles To Exit")  // Corrected the input title\n\n// Initialize variables to count consecutive green and red candles\nvar int consecutiveGreenCandles = 0\nvar int consecutiveRedCandles = 0\n\n// Initialize barsSinceEntry outside the loop\nvar int barsSinceEntry = 0\n\n// Loop through the last "numCandlesToCheck" candles\nfor i = 0 to numCandlesToCheck - 1\n    if isGreenCandle(i)\n        consecutiveGreenCandles := consecutiveGreenCandles + 1\n        consecutiveRedCandles := 0 // Reset the count for consecutive red candles\n    else if isRedCandle(i)\n        consecutiveRedCandles := consecutiveRedCandles + 1\n        consecutiveGreenCandles := 0 // Reset the count for consecutive green candles\n\n// Check if the last "numCandlesToCheck" candles are green or red\nlastNCandlesGreen = consecutiveGreenCandles >= numCandlesToCheck\nlastNCandlesRed = consecutiveRedCandles >= numCandlesToCheck\n\n// Calculate the quantity based on the investment value and current asset price\ninvestmentValue = input(10000, title="Investment Value")\nvar assetPrice = close\nvar quantity = investmentValue / assetPrice\n\n\ninverseLogic = input(false, title="inverseLogic")\n\n// Entry condition: Open a buy order if the last "numCandlesToCheck" candles are green\nif lastNCandlesGreen\n    if inverseLogic\n        strategy.entry("Short", strategy.long, qty = quantity)\n    else \n        strategy.entry("Buy", strategy.long, qty = quantity)// Reset barsSinceEntry when entering a trade\n    barsSinceEntry := 0\n\n// Entry condition: Open a short order if the last "numCandlesToCheck" candles are red\nif lastNCandlesRed\n    if inverseLogic\n        strategy.entry("Buy", strategy.long, qty = quantity)\n\n    else \n        strategy.entry("Short", strategy.short, qty = quantity)\n    // Reset barsSinceEntry when entering a trade\n    barsSinceEntry := 0\n\n// Increment barsSinceEntry\nbarsSinceEntry := barsSinceEntry + 1\n\n// Exit condition: Close the position after 2 bars\nif barsSinceEntry >= numCandlesToExit\n    strategy.close("Buy")\n    strategy.close("Short")'

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
