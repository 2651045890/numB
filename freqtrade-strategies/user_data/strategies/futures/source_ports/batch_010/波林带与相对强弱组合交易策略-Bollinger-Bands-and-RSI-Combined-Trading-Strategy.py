"""Source-faithful deep-assisted port of 波林带与相对强弱组合交易策略-Bollinger-Bands-and-RSI-Combined-Trading-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_e7a36949(PinePortBase, IStrategy):
    source_file = '波林带与相对强弱组合交易策略-Bollinger-Bands-and-RSI-Combined-Trading-Strategy.md'
    timeframe = '1d'
    can_short = False
    source_defaults = {'length': 20, 'mult': 2.5, 'rsiLength': 14, 'rsiOverbought': 70, 'rsiOversold': 30}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.entry', 'strategy.close', 'for ']
    source_fidelity_notes = []
    pine_assignments = [{'mode': '', 'name': 'length', 'op': '=', 'expr': 'input(20, title="Length")', 'conditions': []}, {'mode': '', 'name': 'mult', 'op': '=', 'expr': 'input(2.5, title="Multiplier")', 'conditions': []}, {'mode': '', 'name': 'basis', 'op': '=', 'expr': 'ta.sma(close, length)', 'conditions': []}, {'mode': '', 'name': 'dev', 'op': '=', 'expr': 'mult * ta.stdev(close, length)', 'conditions': []}, {'mode': '', 'name': 'upper', 'op': '=', 'expr': 'basis + dev', 'conditions': []}, {'mode': '', 'name': 'lower', 'op': '=', 'expr': 'basis - dev', 'conditions': []}, {'mode': '', 'name': 'rsiLength', 'op': '=', 'expr': 'input(14, title="RSI Length")', 'conditions': []}, {'mode': '', 'name': 'rsiOverbought', 'op': '=', 'expr': 'input(70, title="RSI Overbought Level")', 'conditions': []}, {'mode': '', 'name': 'rsiOversold', 'op': '=', 'expr': 'input(30, title="RSI Oversold Level")', 'conditions': []}, {'mode': '', 'name': 'rsi', 'op': '=', 'expr': 'ta.rsi(close, rsiLength)', 'conditions': []}, {'mode': '', 'name': 'p1', 'op': '=', 'expr': 'plot(upper, "Upper", color=color.red)', 'conditions': []}, {'mode': '', 'name': 'p2', 'op': '=', 'expr': 'plot(lower, "Lower", color=color.green)', 'conditions': []}, {'mode': '', 'name': 'buyCondition', 'op': '=', 'expr': 'close < lower and rsi < rsiOversold', 'conditions': []}, {'mode': '', 'name': 'sellCondition', 'op': '=', 'expr': 'close > upper and rsi > rsiOverbought', 'conditions': []}, {'mode': '', 'name': 'exitCondition', 'op': '=', 'expr': 'rsi > 50', 'conditions': []}]
    pine_user_functions = []
    pine_controls = [{'indent': 0, 'statement': 'if (buyCondition)'}, {'indent': 0, 'statement': 'if (sellCondition)'}, {'indent': 0, 'statement': 'if (exitCondition)'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("Buy", strategy.long)', 'conditions': ['(buyCondition)'], 'statement': 'strategy.entry("Buy", strategy.long)'}, {'kind': 'close', 'call': 'strategy.close("Buy")', 'conditions': ['(sellCondition)'], 'statement': 'strategy.close("Buy")'}, {'kind': 'close', 'call': 'strategy.close("Buy")', 'conditions': ['(exitCondition)'], 'statement': 'strategy.close("Buy")'}]
    original_pine = '/*backtest\nstart: 2019-12-23 08:00:00\nend: 2024-11-27 00:00:00\nperiod: 1d\nbasePeriod: 1d\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("Bollinger Bands + RSI Strategy", shorttitle="BB_RSI", overlay=true)\n\n// Define the Bollinger Bands parameters\nlength = input(20, title="Length")\nmult = input(2.5, title="Multiplier")\nbasis = ta.sma(close, length)\ndev = mult * ta.stdev(close, length)\nupper = basis + dev\nlower = basis - dev\n\n// Define the RSI parameters\nrsiLength = input(14, title="RSI Length")\nrsiOverbought = input(70, title="RSI Overbought Level")\nrsiOversold = input(30, title="RSI Oversold Level")\nrsi = ta.rsi(close, rsiLength)\n\n// Plot the Bollinger Bands and RSI\nplot(basis, "Basis", color=color.yellow)\np1 = plot(upper, "Upper", color=color.red)\np2 = plot(lower, "Lower", color=color.green)\nfill(p1, p2, color=color.rgb(255, 255, 255, 90))\nhline(rsiOverbought, "Overbought", color=color.red)\nhline(rsiOversold, "Oversold", color=color.green)\n\n// Generate Buy and Sell signals\nbuyCondition = close < lower and rsi < rsiOversold\nsellCondition = close > upper and rsi > rsiOverbought\n\nif (buyCondition)\n    strategy.entry("Buy", strategy.long)\n\nif (sellCondition)\n    strategy.close("Buy")\n\n// Optional: Add exit strategy for buys\nexitCondition = rsi > 50\nif (exitCondition)\n    strategy.close("Buy")\n\n// Plot RSI on a separate panel\nplot(rsi, "RSI", color=color.purple)'

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
