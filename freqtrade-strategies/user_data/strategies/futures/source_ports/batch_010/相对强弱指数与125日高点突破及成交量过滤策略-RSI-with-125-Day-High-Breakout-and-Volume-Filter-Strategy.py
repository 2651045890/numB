"""Source-faithful deep-assisted port of 相对强弱指数与125日高点突破及成交量过滤策略-RSI-with-125-Day-High-Breakout-and-Volume-Filter-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_e0240a8c(PinePortBase, IStrategy):
    source_file = '相对强弱指数与125日高点突破及成交量过滤策略-RSI-with-125-Day-High-Breakout-and-Volume-Filter-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'length': 14, 'overSold': 30, 'overBought': 70}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.entry', 'for ']
    source_fidelity_notes = []
    pine_assignments = [{'mode': '', 'name': 'length', 'op': '=', 'expr': 'input(14, title="RSI Length")', 'conditions': []}, {'mode': '', 'name': 'overSold', 'op': '=', 'expr': 'input(30, title="Oversold Level")', 'conditions': []}, {'mode': '', 'name': 'overBought', 'op': '=', 'expr': 'input(70, title="Overbought Level")', 'conditions': []}, {'mode': '', 'name': 'price', 'op': '=', 'expr': 'close', 'conditions': []}, {'mode': '', 'name': 'vrsi', 'op': '=', 'expr': 'ta.rsi(price, length)', 'conditions': []}, {'mode': '', 'name': 'co', 'op': '=', 'expr': 'ta.crossover(vrsi, overSold)', 'conditions': []}, {'mode': '', 'name': 'cu', 'op': '=', 'expr': 'ta.crossunder(vrsi, overBought)', 'conditions': []}, {'mode': '', 'name': 'high_125', 'op': '=', 'expr': 'ta.highest(high, 125)', 'conditions': []}, {'mode': '', 'name': 'cross_above_high_125', 'op': '=', 'expr': 'ta.crossover(price, high_125)', 'conditions': []}, {'mode': '', 'name': 'cross_below_high_125', 'op': '=', 'expr': 'ta.crossunder(price, high_125)', 'conditions': []}, {'mode': '', 'name': 'volume_increased', 'op': '=', 'expr': 'volume > 2 * volume[1]', 'conditions': []}]
    pine_user_functions = []
    pine_controls = [{'indent': 0, 'statement': 'if (not na(vrsi))'}, {'indent': 4, 'statement': 'if (co and volume_increased)'}, {'indent': 4, 'statement': 'if (cu and volume_increased)'}, {'indent': 0, 'statement': 'if (cross_above_high_125 and volume_increased)'}, {'indent': 0, 'statement': 'if (cross_below_high_125 and volume_increased)'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("RsiLE", strategy.long, comment="RsiLE")', 'conditions': ['(not na(vrsi))', '(co and volume_increased)'], 'statement': 'strategy.entry("RsiLE", strategy.long, comment="RsiLE")'}, {'kind': 'entry', 'call': 'strategy.entry("RsiSE", strategy.short, comment="RsiSE")', 'conditions': ['(not na(vrsi))', '(cu and volume_increased)'], 'statement': 'strategy.entry("RsiSE", strategy.short, comment="RsiSE")'}, {'kind': 'entry', 'call': 'strategy.entry("BuyHigh125", strategy.long, comment="BuyHigh125")', 'conditions': ['(cross_above_high_125 and volume_increased)'], 'statement': 'strategy.entry("BuyHigh125", strategy.long, comment="BuyHigh125")'}, {'kind': 'entry', 'call': 'strategy.entry("SellHigh125", strategy.short, comment="SellHigh125")', 'conditions': ['(cross_below_high_125 and volume_increased)'], 'statement': 'strategy.entry("SellHigh125", strategy.short, comment="SellHigh125")'}]
    original_pine = '/*backtest\nstart: 2024-02-22 00:00:00\nend: 2025-02-19 08:00:00\nperiod: 1d\nbasePeriod: 1d\nexchanges: [{"eid":"Binance","currency":"ETH_USDT"}]\n*/\n\n//@version=6\nstrategy("RSI Strategy with 125-Day High and Volume Filter", overlay=true)\n\n// Input variables\nlength = input(14, title="RSI Length")\noverSold = input(30, title="Oversold Level")\noverBought = input(70, title="Overbought Level")\nprice = close\n\n// RSI Calculation\nvrsi = ta.rsi(price, length)\n\n// Conditions for RSI crossover\nco = ta.crossover(vrsi, overSold)\ncu = ta.crossunder(vrsi, overBought)\n\n// 125-day high calculation\nhigh_125 = ta.highest(high, 125)\n\n// Crossing conditions for 125-day high\ncross_above_high_125 = ta.crossover(price, high_125)\ncross_below_high_125 = ta.crossunder(price, high_125)\n\n// Volume condition: Check if current volume is at least 2 times the previous volume\nvolume_increased = volume > 2 * volume[1]\n\n// Entry logic for RSI and 125-day high with volume filter\nif (not na(vrsi))\n    if (co and volume_increased)\n        strategy.entry("RsiLE", strategy.long, comment="RsiLE")\n    if (cu and volume_increased)\n        strategy.entry("RsiSE", strategy.short, comment="RsiSE")\n\n// Entry logic for 125-day high crossing with volume filter\nif (cross_above_high_125 and volume_increased)\n    strategy.entry("BuyHigh125", strategy.long, comment="BuyHigh125")\n\nif (cross_below_high_125 and volume_increased)\n    strategy.entry("SellHigh125", strategy.short, comment="SellHigh125")\n\n// Plot the 125-day high for visualization\nplot(high_125, title="125-Day High", color=color.orange, linewidth=2, style=plot.style_line)'

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
