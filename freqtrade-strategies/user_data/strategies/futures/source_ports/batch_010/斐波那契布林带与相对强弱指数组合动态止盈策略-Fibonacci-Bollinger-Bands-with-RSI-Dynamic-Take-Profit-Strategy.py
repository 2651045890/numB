"""Source-faithful deep-assisted port of 斐波那契布林带与相对强弱指数组合动态止盈策略-Fibonacci-Bollinger-Bands-with-RSI-Dynamic-Take-Profit-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_f6fc864b(PinePortBase, IStrategy):
    source_file = '斐波那契布林带与相对强弱指数组合动态止盈策略-Fibonacci-Bollinger-Bands-with-RSI-Dynamic-Take-Profit-Strategy.md'
    timeframe = '1h'
    can_short = True
    source_defaults = {'length': 200, 'src': 'hlc3', 'mult': 3.0, 'rsiLength': 14, 'profitTargetPercent': 2.0}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 100.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.entry', 'strategy.close', 'strategy.position_size']
    source_fidelity_notes = ['Reads broker/strategy state; signals depend on fill timing and cannot be reduced to indicator-only booleans without changing behavior.']
    pine_assignments = [{'mode': '', 'name': 'length', 'op': '=', 'expr': 'input(200, title="VWMA Length")', 'conditions': []}, {'mode': '', 'name': 'src', 'op': '=', 'expr': 'input(hlc3, title="Source")', 'conditions': []}, {'mode': '', 'name': 'mult', 'op': '=', 'expr': 'input(3.0, title="Deviation Multiplier")', 'conditions': []}, {'mode': '', 'name': 'rsiLength', 'op': '=', 'expr': 'input.int(14, title="RSI Length")', 'conditions': []}, {'mode': '', 'name': 'profitTargetPercent', 'op': '=', 'expr': 'input.float(2.0, title="Profit Target (%)")', 'conditions': []}, {'mode': '', 'name': 'basis', 'op': '=', 'expr': 'ta.vwma(src, length)', 'conditions': []}, {'mode': '', 'name': 'dev', 'op': '=', 'expr': 'mult * ta.stdev(src, length)', 'conditions': []}, {'mode': '', 'name': 'upper_6', 'op': '=', 'expr': 'basis + (1 * dev) // RED line', 'conditions': []}, {'mode': '', 'name': 'lower_6', 'op': '=', 'expr': 'basis - (1 * dev) // GREEN line', 'conditions': []}, {'mode': '', 'name': 'rsi', 'op': '=', 'expr': 'ta.rsi(close, rsiLength)', 'conditions': []}, {'mode': '', 'name': 'buySignal', 'op': '=', 'expr': 'ta.crossover(close, upper_6)', 'conditions': []}, {'mode': '', 'name': 'sellSignal', 'op': '=', 'expr': 'ta.crossunder(close, lower_6)', 'conditions': []}, {'mode': '', 'name': 'longTakeProfit', 'op': '=', 'expr': 'strategy.position_avg_price * (1 + profitTargetPercent / 100)', 'conditions': []}, {'mode': '', 'name': 'shortTakeProfit', 'op': '=', 'expr': 'strategy.position_avg_price * (1 - profitTargetPercent / 100)', 'conditions': []}]
    pine_user_functions = []
    pine_controls = [{'indent': 0, 'statement': 'if buySignal'}, {'indent': 0, 'statement': 'if sellSignal'}, {'indent': 0, 'statement': 'if strategy.position_size > 0'}, {'indent': 4, 'statement': 'if close >= longTakeProfit or rsi < 30'}, {'indent': 0, 'statement': 'if strategy.position_size < 0'}, {'indent': 4, 'statement': 'if close <= shortTakeProfit or rsi > 70'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("Long", strategy.long)', 'conditions': ['buySignal'], 'statement': 'strategy.entry("Long", strategy.long)'}, {'kind': 'entry', 'call': 'strategy.entry("Short", strategy.short)', 'conditions': ['sellSignal'], 'statement': 'strategy.entry("Short", strategy.short)'}, {'kind': 'close', 'call': 'strategy.close("Long")', 'conditions': ['strategy.position_size > 0', 'close >= longTakeProfit or rsi < 30'], 'statement': 'strategy.close("Long")'}, {'kind': 'close', 'call': 'strategy.close("Short")', 'conditions': ['strategy.position_size < 0', 'close <= shortTakeProfit or rsi > 70'], 'statement': 'strategy.close("Short")'}]
    original_pine = '/*backtest\nstart: 2024-04-02 00:00:00\nend: 2025-04-01 00:00:00\nperiod: 1h\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"ETH_USDT"}]\n*/\n\n//@version=5\nstrategy("Fibonacci BB Strategy with RSI + 2% Exit", overlay=true, default_qty_type=strategy.percent_of_equity, default_qty_value=100)\n\n// === INPUTS ===\nlength = input(200, title="VWMA Length")\nsrc = input(hlc3, title="Source")\nmult = input(3.0, title="Deviation Multiplier")\nrsiLength = input.int(14, title="RSI Length")\nprofitTargetPercent = input.float(2.0, title="Profit Target (%)")\n\n// === FBB CALCULATIONS ===\nbasis = ta.vwma(src, length)\ndev = mult * ta.stdev(src, length)\nupper_6 = basis + (1 * dev)  // RED line\nlower_6 = basis - (1 * dev)  // GREEN line\n\n// === RSI ===\nrsi = ta.rsi(close, rsiLength)\n\n// === SIGNAL CONDITIONS ===\nbuySignal = ta.crossover(close, upper_6)\nsellSignal = ta.crossunder(close, lower_6)\n\n// === STRATEGY ENTRIES ===\nif buySignal\n    strategy.entry("Long", strategy.long)\n\nif sellSignal\n    strategy.entry("Short", strategy.short)\n\n// === STRATEGY EXITS ===\n// 2% profit in points\nlongTakeProfit = strategy.position_avg_price * (1 + profitTargetPercent / 100)\nshortTakeProfit = strategy.position_avg_price * (1 - profitTargetPercent / 100)\n\n// Long Exit: RSI < 30 or price >= TP\nif strategy.position_size > 0\n    if close >= longTakeProfit or rsi < 30\n        strategy.close("Long")\n\n// Short Exit: RSI > 70 or price <= TP\nif strategy.position_size < 0\n    if close <= shortTakeProfit or rsi > 70\n        strategy.close("Short")\n\n// === PLOTS ===\nplot(basis, color=color.fuchsia, linewidth=2, title="VWMA Basis")\nplot(upper_6, color=color.red, linewidth=2, title="Upper Band (1x Dev)")\nplot(lower_6, color=color.green, linewidth=2, title="Lower Band (1x Dev)")'

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
