"""Source-faithful deep-assisted port of 指数移动平均线交叉动态跟踪止损策略-EMA-Crossover-Dynamic-Trailing-Stop-Loss-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_4944227b(PinePortBase, IStrategy):
    source_file = '指数移动平均线交叉动态跟踪止损策略-EMA-Crossover-Dynamic-Trailing-Stop-Loss-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'emaLength1': 9, 'emaLength2': 21, 'trailStopPercent': 1.0}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.entry', 'strategy.close', 'strategy.position_size', 'var ', 'for ', 'alert']
    source_fidelity_notes = ['Uses persistent Pine state (var/varip); state is order-dependent and must be evaluated bar-by-bar, not replaced by a vectorized fill-forward approximation.', 'Reads broker/strategy state; signals depend on fill timing and cannot be reduced to indicator-only booleans without changing behavior.']
    pine_assignments = [{'mode': '', 'name': 'emaLength1', 'op': '=', 'expr': 'input.int(9, title="Short EMA Length")', 'conditions': []}, {'mode': '', 'name': 'emaLength2', 'op': '=', 'expr': 'input.int(21, title="Long EMA Length")', 'conditions': []}, {'mode': '', 'name': 'trailStopPercent', 'op': '=', 'expr': 'input.float(1.0, title="Trailing Stop Percentage", minval=0.1, step=0.1) / 100', 'conditions': []}, {'mode': '', 'name': 'ema1', 'op': '=', 'expr': 'ta.ema(close, emaLength1)', 'conditions': []}, {'mode': '', 'name': 'ema2', 'op': '=', 'expr': 'ta.ema(close, emaLength2)', 'conditions': []}, {'mode': '', 'name': 'crossoverCondition', 'op': '=', 'expr': 'ta.crossover(ema1, ema2)', 'conditions': []}, {'mode': '', 'name': 'crossunderCondition', 'op': '=', 'expr': 'ta.crossunder(ema1, ema2)', 'conditions': []}, {'mode': '', 'name': 'buyCondition', 'op': '=', 'expr': 'crossoverCondition', 'conditions': []}, {'mode': '', 'name': 'sellCondition', 'op': '=', 'expr': 'crossunderCondition', 'conditions': []}, {'mode': 'var', 'name': 'highestPrice', 'op': '=', 'expr': 'na', 'conditions': []}, {'mode': 'var', 'name': 'lowestPrice', 'op': '=', 'expr': 'na', 'conditions': []}, {'mode': '', 'name': 'highestPrice', 'op': ':=', 'expr': 'close', 'conditions': ['(buyCondition)']}, {'mode': '', 'name': 'lowestPrice', 'op': ':=', 'expr': 'close', 'conditions': ['(sellCondition)']}, {'mode': '', 'name': 'highestPrice', 'op': ':=', 'expr': 'math.max(highestPrice, close)', 'conditions': ['(strategy.position_size > 0)']}, {'mode': '', 'name': 'trailStopPrice', 'op': '=', 'expr': 'highestPrice * (1 - trailStopPercent)', 'conditions': ['(strategy.position_size > 0)']}, {'mode': '', 'name': 'lowestPrice', 'op': ':=', 'expr': 'math.min(lowestPrice, close)', 'conditions': ['(strategy.position_size < 0)']}, {'mode': '', 'name': 'trailStopPrice', 'op': '=', 'expr': 'lowestPrice * (1 + trailStopPercent)', 'conditions': ['(strategy.position_size < 0)']}]
    pine_user_functions = []
    pine_controls = [{'indent': 0, 'statement': 'if (buyCondition)'}, {'indent': 0, 'statement': 'if (sellCondition)'}, {'indent': 0, 'statement': 'if (strategy.position_size > 0)'}, {'indent': 4, 'statement': 'if (close < trailStopPrice)'}, {'indent': 0, 'statement': 'if (strategy.position_size < 0)'}, {'indent': 4, 'statement': 'if (close > trailStopPrice)'}, {'indent': 0, 'statement': 'if (buyCondition)'}, {'indent': 0, 'statement': 'if (sellCondition)'}]
    pine_orders = [{'kind': 'close', 'call': 'strategy.close("Buy")', 'conditions': ['(strategy.position_size > 0)', '(close < trailStopPrice)'], 'statement': 'strategy.close("Buy")'}, {'kind': 'close', 'call': 'strategy.close("Sell")', 'conditions': ['(strategy.position_size < 0)', '(close > trailStopPrice)'], 'statement': 'strategy.close("Sell")'}, {'kind': 'entry', 'call': 'strategy.entry("Buy", strategy.long)', 'conditions': ['(buyCondition)'], 'statement': 'strategy.entry("Buy", strategy.long)'}, {'kind': 'entry', 'call': 'strategy.entry("Sell", strategy.short)', 'conditions': ['(sellCondition)'], 'statement': 'strategy.entry("Sell", strategy.short)'}]
    original_pine = '/*backtest\nstart: 2024-04-21 00:00:00\nend: 2025-04-20 00:00:00\nperiod: 1d\nbasePeriod: 1d\nexchanges: [{"eid":"Futures_Binance","currency":"TRX_USD"}]\n*/\n\n//@version=6\nstrategy("EMA Crossover Strategy with Trailing Stop and Alerts", overlay=true)\n\n// Input for EMA lengths\nemaLength1 = input.int(9, title="Short EMA Length")\nemaLength2 = input.int(21, title="Long EMA Length")\n\n// Input for trailing stop percentage\ntrailStopPercent = input.float(1.0, title="Trailing Stop Percentage", minval=0.1, step=0.1) / 100\n\n// Calculate EMAs\nema1 = ta.ema(close, emaLength1)\nema2 = ta.ema(close, emaLength2)\n\n// Plot EMAs\nplot(ema1, color=color.blue, title="Short EMA")\nplot(ema2, color=color.red, title="Long EMA")\n\n// Crossover and Crossunder conditions\ncrossoverCondition = ta.crossover(ema1, ema2)\ncrossunderCondition = ta.crossunder(ema1, ema2)\n\n// Buy and Sell conditions\nbuyCondition = crossoverCondition\nsellCondition = crossunderCondition\n\n// Trailing stop logic\nvar float highestPrice = na\nvar float lowestPrice = na\n\nif (buyCondition)\n    highestPrice := close\nif (sellCondition)\n    lowestPrice := close\n\nif (strategy.position_size > 0)\n    highestPrice := math.max(highestPrice, close)\n    trailStopPrice = highestPrice * (1 - trailStopPercent)\n    if (close < trailStopPrice)\n        strategy.close("Buy")\n\nif (strategy.position_size < 0)\n    lowestPrice := math.min(lowestPrice, close)\n    trailStopPrice = lowestPrice * (1 + trailStopPercent)\n    if (close > trailStopPrice)\n        strategy.close("Sell")\n\n// Plot buy and sell signals\nplotshape(series=buyCondition, location=location.belowbar, color=color.green, style=shape.labelup, title="Buy Signal")\nplotshape(series=sellCondition, location=location.abovebar, color=color.red, style=shape.labeldown, title="Sell Signal")\n\n// Alerts\nalertcondition(buyCondition, title="Buy Alert", message="Buy Signal: EMA crossover")\nalertcondition(sellCondition, title="Sell Alert", message="Sell Signal: EMA crossunder")\n\n// Strategy execution\nif (buyCondition)\n    strategy.entry("Buy", strategy.long)\nif (sellCondition)\n    strategy.entry("Sell", strategy.short)'

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
