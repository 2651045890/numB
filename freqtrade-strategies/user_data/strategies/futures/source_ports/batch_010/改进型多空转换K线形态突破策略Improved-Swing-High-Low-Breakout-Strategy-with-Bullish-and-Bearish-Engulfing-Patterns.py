"""Source-faithful deep-assisted port of 改进型多空转换K线形态突破策略Improved-Swing-High-Low-Breakout-Strategy-with-Bullish-and-Bearish-Engulfing-Patterns.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_e9de4a62(PinePortBase, IStrategy):
    source_file = '改进型多空转换K线形态突破策略Improved-Swing-High-Low-Breakout-Strategy-with-Bullish-and-Bearish-Engulfing-Patterns.md'
    timeframe = '4h'
    can_short = True
    source_defaults = {'length': 14, 'multiplier': 3, 'risk_reward_ratio': 1.6, 'target_multiplier': 2}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.exit', 'strategy.entry', 'var ']
    source_fidelity_notes = ['Uses persistent Pine state (var/varip); state is order-dependent and must be evaluated bar-by-bar, not replaced by a vectorized fill-forward approximation.', 'Uses strategy.exit; stop/limit/profit/loss/trailing arguments have Pine order semantics and may fill intrabar.']
    pine_assignments = [{'mode': '', 'name': 'length', 'op': '=', 'expr': 'input(14, title="Swing Length")', 'conditions': []}, {'mode': '', 'name': 'multiplier', 'op': '=', 'expr': 'input(3, title="Multiplier")', 'conditions': []}, {'mode': '', 'name': 'risk_reward_ratio', 'op': '=', 'expr': 'input(1.6, title="Risk-Reward Ratio")', 'conditions': []}, {'mode': '', 'name': 'target_multiplier', 'op': '=', 'expr': 'input(2, title="Target Multiplier")', 'conditions': []}, {'mode': 'var', 'name': 'lastHigh', 'op': '=', 'expr': 'na', 'conditions': []}, {'mode': 'var', 'name': 'lastLow', 'op': '=', 'expr': 'na', 'conditions': []}, {'mode': 'var', 'name': 'isHigh', 'op': '=', 'expr': 'na', 'conditions': []}, {'mode': 'var', 'name': 'isLow', 'op': '=', 'expr': 'na', 'conditions': []}, {'mode': '', 'name': 'lastHigh', 'op': ':=', 'expr': 'high[1]', 'conditions': ['high[1] < high and high[2] < high[1]']}, {'mode': '', 'name': 'isHigh', 'op': ':=', 'expr': 'true', 'conditions': ['high[1] < high and high[2] < high[1]']}, {'mode': '', 'name': 'isLow', 'op': ':=', 'expr': 'false', 'conditions': ['high[1] < high and high[2] < high[1]']}, {'mode': '', 'name': 'lastLow', 'op': ':=', 'expr': 'low[1]', 'conditions': ['low[1] > low and low[2] > low[1]']}, {'mode': '', 'name': 'isLow', 'op': ':=', 'expr': 'true', 'conditions': ['low[1] > low and low[2] > low[1]']}, {'mode': '', 'name': 'isHigh', 'op': ':=', 'expr': 'false', 'conditions': ['low[1] > low and low[2] > low[1]']}, {'mode': '', 'name': 'isHigh', 'op': ':=', 'expr': 'false', 'conditions': ['ELSE']}, {'mode': '', 'name': 'isLow', 'op': ':=', 'expr': 'false', 'conditions': ['ELSE']}, {'mode': '', 'name': 'buySignal', 'op': '=', 'expr': 'close > lastHigh and close > open and close[1] < open[1] // Bullish engulfing', 'conditions': []}, {'mode': '', 'name': 'sellSignal', 'op': '=', 'expr': 'close < lastLow and close < open and close[1] > open[1] // Bearish engulfing', 'conditions': []}, {'mode': '', 'name': 'stopLevel', 'op': '=', 'expr': 'close', 'conditions': []}, {'mode': '', 'name': 'targetLevel', 'op': '=', 'expr': 'close + (close - stopLevel) * risk_reward_ratio', 'conditions': []}]
    pine_user_functions = []
    pine_controls = [{'indent': 0, 'statement': 'if high[1] < high and high[2] < high[1]'}, {'indent': 0, 'statement': 'else if low[1] > low and low[2] > low[1]'}, {'indent': 0, 'statement': 'else'}, {'indent': 0, 'statement': 'if buySignal'}, {'indent': 0, 'statement': 'if sellSignal'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("Buy", strategy.long)', 'conditions': ['buySignal'], 'statement': 'strategy.entry("Buy", strategy.long)'}, {'kind': 'exit', 'call': 'strategy.exit("TP/SL", "Buy", profit=targetLevel, loss=stopLevel)', 'conditions': ['buySignal'], 'statement': 'strategy.exit("TP/SL", "Buy", profit=targetLevel, loss=stopLevel)'}, {'kind': 'entry', 'call': 'strategy.entry("Sell", strategy.short)', 'conditions': ['sellSignal'], 'statement': 'strategy.entry("Sell", strategy.short)'}, {'kind': 'exit', 'call': 'strategy.exit("TP/SL", "Sell", profit=targetLevel, loss=stopLevel)', 'conditions': ['sellSignal'], 'statement': 'strategy.exit("TP/SL", "Sell", profit=targetLevel, loss=stopLevel)'}]
    original_pine = '/*backtest\nstart: 2024-04-01 00:00:00\nend: 2024-04-30 23:59:59\nperiod: 4h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This Pine Script™ code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © Markoline007\n\n//@version=5\nstrategy("Improved Swing High/Low Breakout Strategy", overlay=true)\n\n// Define input variables\nlength = input(14, title="Swing Length")\nmultiplier = input(3, title="Multiplier")\nrisk_reward_ratio = input(1.6, title="Risk-Reward Ratio")\ntarget_multiplier = input(2, title="Target Multiplier")\n\n// Calculate swing highs and swing lows\nvar float lastHigh = na\nvar float lastLow = na\nvar bool isHigh = na\nvar bool isLow = na\n\nif high[1] < high and high[2] < high[1]\n    lastHigh := high[1]\n    isHigh := true\n    isLow := false\nelse if low[1] > low and low[2] > low[1]\n    lastLow := low[1]\n    isLow := true\n    isHigh := false\nelse\n    isHigh := false\n    isLow := false\n\n// Define buy and sell conditions\nbuySignal = close > lastHigh and close > open and close[1] < open[1] // Bullish engulfing\nsellSignal = close < lastLow and close < open and close[1] > open[1] // Bearish engulfing\n\n// Calculate stop and target levels\nstopLevel = close\ntargetLevel = close + (close - stopLevel) * risk_reward_ratio\n\n// Execute buy and sell trades\nif buySignal\n    strategy.entry("Buy", strategy.long)\n    strategy.exit("TP/SL", "Buy", profit=targetLevel, loss=stopLevel)\nif sellSignal\n    strategy.entry("Sell", strategy.short)\n    strategy.exit("TP/SL", "Sell", profit=targetLevel, loss=stopLevel)'

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
