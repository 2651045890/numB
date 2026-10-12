"""Source-faithful deep-assisted port of 相对强弱指数发散策略RSI-Divergence-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_1e71f2c1(PinePortBase, IStrategy):
    source_file = '相对强弱指数发散策略RSI-Divergence-Strategy.md'
    timeframe = '1m'
    can_short = True
    source_defaults = {'rsiLength': 14, 'overboughtLevel': 70, 'oversoldLevel': 30}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.entry', 'strategy.close']
    source_fidelity_notes = []
    pine_assignments = [{'mode': '', 'name': 'rsiLength', 'op': '=', 'expr': 'input(14, "RSI Length")', 'conditions': []}, {'mode': '', 'name': 'overboughtLevel', 'op': '=', 'expr': 'input(70, "Overbought Level")', 'conditions': []}, {'mode': '', 'name': 'oversoldLevel', 'op': '=', 'expr': 'input(30, "Oversold Level")', 'conditions': []}, {'mode': '', 'name': 'rsiValue', 'op': '=', 'expr': 'ta.rsi(close, rsiLength)', 'conditions': []}, {'mode': '', 'name': 'priceLow', 'op': '=', 'expr': 'ta.lowest(low, rsiLength)', 'conditions': []}, {'mode': '', 'name': 'priceHigh', 'op': '=', 'expr': 'ta.highest(high, rsiLength)', 'conditions': []}, {'mode': '', 'name': 'rsiLow', 'op': '=', 'expr': 'ta.lowest(rsiValue, rsiLength)', 'conditions': []}, {'mode': '', 'name': 'rsiHigh', 'op': '=', 'expr': 'ta.highest(rsiValue, rsiLength)', 'conditions': []}, {'mode': '', 'name': 'bullishDivergence', 'op': '=', 'expr': 'low < priceLow[1] and rsiValue > rsiLow[1]', 'conditions': []}, {'mode': '', 'name': 'bearishDivergence', 'op': '=', 'expr': 'high > priceHigh[1] and rsiValue < rsiHigh[1]', 'conditions': []}, {'mode': '', 'name': 'longEntry', 'op': '=', 'expr': 'bullishDivergence and rsiValue < oversoldLevel', 'conditions': []}, {'mode': '', 'name': 'longExit', 'op': '=', 'expr': 'rsiValue > overboughtLevel', 'conditions': []}, {'mode': '', 'name': 'shortEntry', 'op': '=', 'expr': 'bearishDivergence and rsiValue > overboughtLevel', 'conditions': []}, {'mode': '', 'name': 'shortExit', 'op': '=', 'expr': 'rsiValue < oversoldLevel', 'conditions': []}]
    pine_user_functions = []
    pine_controls = [{'indent': 0, 'statement': 'if (longEntry)'}, {'indent': 0, 'statement': 'if (longExit)'}, {'indent': 0, 'statement': 'if (shortEntry)'}, {'indent': 0, 'statement': 'if (shortExit)'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("Long Entry", strategy.long)', 'conditions': ['(longEntry)'], 'statement': 'strategy.entry("Long Entry", strategy.long)'}, {'kind': 'close', 'call': 'strategy.close("Long Entry")', 'conditions': ['(longExit)'], 'statement': 'strategy.close("Long Entry")'}, {'kind': 'entry', 'call': 'strategy.entry("Short Entry", strategy.short)', 'conditions': ['(shortEntry)'], 'statement': 'strategy.entry("Short Entry", strategy.short)'}, {'kind': 'close', 'call': 'strategy.close("Short Entry")', 'conditions': ['(shortExit)'], 'statement': 'strategy.close("Short Entry")'}]
    original_pine = '/*backtest\nstart: 2024-02-13 00:00:00\nend: 2024-02-20 00:00:00\nperiod: 1m\nbasePeriod: 1m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("RSI Divergence Strategy", overlay=true)\n\n// RSI Parameters\nrsiLength = input(14, "RSI Length")\noverboughtLevel = input(70, "Overbought Level")\noversoldLevel = input(30, "Oversold Level")\nrsiValue = ta.rsi(close, rsiLength)\n\n// Divergence detection\npriceLow = ta.lowest(low, rsiLength)\npriceHigh = ta.highest(high, rsiLength)\nrsiLow = ta.lowest(rsiValue, rsiLength)\nrsiHigh = ta.highest(rsiValue, rsiLength)\n\nbullishDivergence = low < priceLow[1] and rsiValue > rsiLow[1]\nbearishDivergence = high > priceHigh[1] and rsiValue < rsiHigh[1]\n\n// Strategy Conditions\nlongEntry = bullishDivergence and rsiValue < oversoldLevel\nlongExit = rsiValue > overboughtLevel\nshortEntry = bearishDivergence and rsiValue > overboughtLevel\nshortExit = rsiValue < oversoldLevel\n\n// ENTER_LONG Condition\nif (longEntry)\n    strategy.entry("Long Entry", strategy.long)\n\n// EXIT_LONG Condition\nif (longExit)\n    strategy.close("Long Entry")\n\n// ENTER_SHORT Condition\nif (shortEntry)\n    strategy.entry("Short Entry", strategy.short)\n\n// EXIT_SHORT Condition\nif (shortExit)\n    strategy.close("Short Entry")'

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
