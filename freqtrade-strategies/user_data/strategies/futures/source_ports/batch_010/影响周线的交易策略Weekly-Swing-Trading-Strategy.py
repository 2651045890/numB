"""Source-faithful deep-assisted port of 影响周线的交易策略Weekly-Swing-Trading-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_399064a8(PinePortBase, IStrategy):
    source_file = '影响周线的交易策略Weekly-Swing-Trading-Strategy.md'
    timeframe = '3h'
    can_short = False
    source_defaults = {}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.exit', 'strategy.entry', 'strategy.close']
    source_fidelity_notes = ['Uses strategy.exit; stop/limit/profit/loss/trailing arguments have Pine order semantics and may fill intrabar.']
    pine_assignments = [{'mode': '', 'name': 'shortEma', 'op': '=', 'expr': 'ema(close, 9)', 'conditions': []}, {'mode': '', 'name': 'longEma', 'op': '=', 'expr': 'ema(close, 21)', 'conditions': []}, {'mode': '', 'name': 'rsiValue', 'op': '=', 'expr': 'rsi(close, 14)', 'conditions': []}, {'mode': '', 'name': 'longCondition', 'op': '=', 'expr': 'crossover(shortEma, longEma) and rsiValue > 50', 'conditions': []}, {'mode': '', 'name': 'riskPerTrade', 'op': '=', 'expr': '0.02', 'conditions': []}, {'mode': '', 'name': 'stopLossPercent', 'op': '=', 'expr': '0.05 // 5% stop loss', 'conditions': []}, {'mode': '', 'name': 'stopLossPrice', 'op': '=', 'expr': 'close * (1 - stopLossPercent)', 'conditions': []}, {'mode': '', 'name': 'profitTargetPercent', 'op': '=', 'expr': '0.10 // 10% profit target', 'conditions': []}, {'mode': '', 'name': 'profitTargetPrice', 'op': '=', 'expr': 'close * (1 + profitTargetPercent)', 'conditions': []}, {'mode': '', 'name': 'trailStopPercent', 'op': '=', 'expr': '0.03 // 3% trailing stop', 'conditions': []}, {'mode': '', 'name': 'exitCondition', 'op': '=', 'expr': 'crossunder(shortEma, longEma) or rsiValue < 50 // Exit when EMAs cross or RSI drops below 50', 'conditions': []}]
    pine_user_functions = []
    pine_controls = [{'indent': 0, 'statement': 'if (longCondition)'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("Long", strategy.long)', 'conditions': ['(longCondition)'], 'statement': 'strategy.entry("Long", strategy.long)'}, {'kind': 'exit', 'call': 'strategy.exit("Stop Loss", "Long", stop=stopLossPrice)', 'conditions': [], 'statement': 'strategy.exit("Stop Loss", "Long", stop=stopLossPrice)'}, {'kind': 'exit', 'call': 'strategy.exit("Take Profit", "Long", limit=profitTargetPrice, trail_price=trailStopPercent, trail_offset=trailStopPercent)', 'conditions': [], 'statement': 'strategy.exit("Take Profit", "Long", limit=profitTargetPrice, trail_price=trailStopPercent, trail_offset=trailStopPercent)'}, {'kind': 'close', 'call': 'strategy.close("Long", when=exitCondition)', 'conditions': [], 'statement': 'strategy.close("Long", when=exitCondition)'}]
    original_pine = '/*backtest\nstart: 2023-12-22 00:00:00\nend: 2024-01-21 00:00:00\nperiod: 3h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=4\nstrategy("Weekly Swing Trading Strategy", overlay=true)\n\n// Entry Indicators\nshortEma = ema(close, 9)\nlongEma = ema(close, 21)\nrsiValue = rsi(close, 14)\n\n// Entry Condition\nlongCondition = crossover(shortEma, longEma) and rsiValue > 50\nif (longCondition)\n    strategy.entry("Long", strategy.long)\n\n// Position Sizing (2% risk per trade)\nriskPerTrade = 0.02\nstopLossPercent = 0.05 // 5% stop loss\nstopLossPrice = close * (1 - stopLossPercent)\nstrategy.exit("Stop Loss", "Long", stop=stopLossPrice)\n\n// Profit Target and Trailing Stop\nprofitTargetPercent = 0.10 // 10% profit target\nprofitTargetPrice = close * (1 + profitTargetPercent)\ntrailStopPercent = 0.03 // 3% trailing stop\nstrategy.exit("Take Profit", "Long", limit=profitTargetPrice, trail_price=trailStopPercent, trail_offset=trailStopPercent)\n\n// Exit Strategy\nexitCondition = crossunder(shortEma, longEma) or rsiValue < 50 // Exit when EMAs cross or RSI drops below 50\nstrategy.close("Long", when=exitCondition)\n\nplot(shortEma, color=color.red)\nplot(longEma, color=color.blue)\nhline(50, "RSI 50", color=color.purple)'

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
