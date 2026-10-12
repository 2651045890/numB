"""Source-faithful deep-assisted port of 斐波那契黄金分割回撤买入策略-Fibonacci-Golden-Ratio-Retracement-Buying-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_a19daf61(PinePortBase, IStrategy):
    source_file = '斐波那契黄金分割回撤买入策略-Fibonacci-Golden-Ratio-Retracement-Buying-Strategy.md'
    timeframe = '1d'
    can_short = False
    source_defaults = {'fib0': 0, 'fib1': 1, 'fib23': 0.236, 'fib38': 0.382, 'fib50': 0.5, 'fib61': 0.618, 'fib78': 0.786, 'Price': 50, 'no': 1}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.entry', 'strategy.close']
    source_fidelity_notes = []
    pine_assignments = [{'mode': '', 'name': 'fib0', 'op': '=', 'expr': 'input(0, title="Fibonacci 0% Level")', 'conditions': []}, {'mode': '', 'name': 'fib1', 'op': '=', 'expr': 'input(1, title="Fibonacci 1% Level")', 'conditions': []}, {'mode': '', 'name': 'fib23', 'op': '=', 'expr': 'input(0.236, title="Fibonacci 23.6% Level")', 'conditions': []}, {'mode': '', 'name': 'fib38', 'op': '=', 'expr': 'input(0.382, title="Fibonacci 38.2% Level")', 'conditions': []}, {'mode': '', 'name': 'fib50', 'op': '=', 'expr': 'input(0.5, title="Fibonacci 50% Level")', 'conditions': []}, {'mode': '', 'name': 'fib61', 'op': '=', 'expr': 'input(0.618, title="Fibonacci 61.8% Level")', 'conditions': []}, {'mode': '', 'name': 'fib78', 'op': '=', 'expr': 'input(0.786, title="Fibonacci 78.6% Level")', 'conditions': []}, {'mode': '', 'name': 'Price', 'op': '=', 'expr': 'input(50, title="Price")', 'conditions': []}, {'mode': '', 'name': 'priceHigh', 'op': '=', 'expr': 'ta.highest(high, Price)', 'conditions': []}, {'mode': '', 'name': 'priceLow', 'op': '=', 'expr': 'ta.lowest(low, Price)', 'conditions': []}, {'mode': '', 'name': 'priceRange', 'op': '=', 'expr': 'priceHigh - priceLow', 'conditions': []}, {'mode': '', 'name': 'fibRetracement0', 'op': '=', 'expr': 'priceHigh - fib0 * priceRange', 'conditions': []}, {'mode': '', 'name': 'fibRetracement1', 'op': '=', 'expr': 'priceHigh - fib1 * priceRange', 'conditions': []}, {'mode': '', 'name': 'fibRetracement23', 'op': '=', 'expr': 'priceHigh - fib23 * priceRange', 'conditions': []}, {'mode': '', 'name': 'fibRetracement38', 'op': '=', 'expr': 'priceHigh - fib38 * priceRange', 'conditions': []}, {'mode': '', 'name': 'fibRetracement50', 'op': '=', 'expr': 'priceHigh - fib50 * priceRange', 'conditions': []}, {'mode': '', 'name': 'fibRetracement61', 'op': '=', 'expr': 'priceHigh - fib61 * priceRange', 'conditions': []}, {'mode': '', 'name': 'fibRetracement78', 'op': '=', 'expr': 'priceHigh - fib78 * priceRange', 'conditions': []}, {'mode': '', 'name': 'no', 'op': '=', 'expr': 'input(1, title="Swing")', 'conditions': []}, {'mode': '', 'name': 'res', 'op': '=', 'expr': 'ta.highest(high, no)', 'conditions': []}, {'mode': '', 'name': 'sup', 'op': '=', 'expr': 'ta.lowest(low, no)', 'conditions': []}, {'mode': '', 'name': 'avd', 'op': '=', 'expr': 'close > res[1] ? 1 : close < sup[1] ? -1 : 0', 'conditions': []}, {'mode': '', 'name': 'avn', 'op': '=', 'expr': 'ta.valuewhen(avd != 0, avd, 0)', 'conditions': []}, {'mode': '', 'name': 'tsl', 'op': '=', 'expr': 'avn == 1 ? sup : res', 'conditions': []}, {'mode': '', 'name': 'buyCondition', 'op': '=', 'expr': '(close > tsl) and (close > fibRetracement23 or close > fibRetracement38 or close > fibRetracement50 or close > fibRetracement61 or close > fibRetracement78)', 'conditions': []}, {'mode': '', 'name': 'sellCondition', 'op': '=', 'expr': '(close < tsl) and (close < fibRetracement23 or close < fibRetracement38 or close < fibRetracement50 or close < fibRetracement61 or close < fibRetracement78)', 'conditions': []}, {'mode': '', 'name': 'barColor', 'op': '=', 'expr': 'buyCondition ? color.green : sellCondition ? color.red : na', 'conditions': []}]
    pine_user_functions = []
    pine_controls = [{'indent': 0, 'statement': 'if (buyCondition)'}, {'indent': 0, 'statement': 'if (sellCondition)'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("Buy", strategy.long)', 'conditions': ['(buyCondition)'], 'statement': 'strategy.entry("Buy", strategy.long)'}, {'kind': 'close', 'call': 'strategy.close("Buy")', 'conditions': ['(sellCondition)'], 'statement': 'strategy.close("Buy")'}]
    original_pine = '/*backtest\nstart: 2023-04-23 00:00:00\nend: 2024-04-28 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy(title=\'Fibonacci BFSP\', overlay=true)\n\n// Define Fibonacci retracement levels\nfib0 = input(0, title="Fibonacci 0% Level")\nfib1 = input(1, title="Fibonacci 1% Level")\nfib23 = input(0.236, title="Fibonacci 23.6% Level")\nfib38 = input(0.382, title="Fibonacci 38.2% Level")\nfib50 = input(0.5, title="Fibonacci 50% Level")\nfib61 = input(0.618, title="Fibonacci 61.8% Level")\nfib78 = input(0.786, title="Fibonacci 78.6% Level")\nPrice = input(50, title="Price")\n\n// Calculate Fibonacci levels\npriceHigh = ta.highest(high, Price)\npriceLow = ta.lowest(low, Price)\npriceRange = priceHigh - priceLow\nfibRetracement0 = priceHigh - fib0 * priceRange\nfibRetracement1 = priceHigh - fib1 * priceRange\nfibRetracement23 = priceHigh - fib23 * priceRange\nfibRetracement38 = priceHigh - fib38 * priceRange\nfibRetracement50 = priceHigh - fib50 * priceRange\nfibRetracement61 = priceHigh - fib61 * priceRange\nfibRetracement78 = priceHigh - fib78 * priceRange\n\n// Plot Fibonacci retracement levels\nplot(fibRetracement0, color=color.gray, linewidth=2)\nplot(fibRetracement1, color=color.gray, linewidth=2)\nplot(fibRetracement23, color=color.green, linewidth=2)\nplot(fibRetracement38, color=color.olive, linewidth=2)\nplot(fibRetracement50, color=color.white, linewidth=2)\nplot(fibRetracement61, color=color.orange, linewidth=2)\nplot(fibRetracement78, color=color.red, linewidth=2)\n\n// Inputs\nno = input(1, title="Swing")\n\n// Calculate swing highs and lows\nres = ta.highest(high, no)\nsup = ta.lowest(low, no)\n\n// Calculate trailing stop loss\navd = close > res[1] ? 1 : close < sup[1] ? -1 : 0\navn = ta.valuewhen(avd != 0, avd, 0)\ntsl = avn == 1 ? sup : res\n\n// Define buy and sell conditions\nbuyCondition = (close > tsl) and (close > fibRetracement23 or close > fibRetracement38 or close > fibRetracement50 or close > fibRetracement61 or close > fibRetracement78)\nsellCondition = (close < tsl) and (close < fibRetracement23 or close < fibRetracement38 or close < fibRetracement50 or close < fibRetracement61 or close < fibRetracement78)\n\n// Entry strategy\nif (buyCondition)\n    strategy.entry("Buy", strategy.long)\n\n// Exit strategy\nif (sellCondition)\n    strategy.close("Buy")\n\n// Color bars based on buy and sell conditions\nbarColor = buyCondition ? color.green : sellCondition ? color.red : na\nbarcolor(barColor)'

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
