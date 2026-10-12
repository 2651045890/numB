"""Source-faithful deep-assisted port of 布林带趋势突破交易策略Bollinger-Bands-Breakout-Trend-Trading-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_b72a5747(PinePortBase, IStrategy):
    source_file = '布林带趋势突破交易策略Bollinger-Bands-Breakout-Trend-Trading-Strategy.md'
    timeframe = '4h'
    can_short = True
    source_defaults = {'riskRewardRatio': 3.0}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.exit', 'strategy.entry', 'var ']
    source_fidelity_notes = ['Uses persistent Pine state (var/varip); state is order-dependent and must be evaluated bar-by-bar, not replaced by a vectorized fill-forward approximation.', 'Uses strategy.exit; stop/limit/profit/loss/trailing arguments have Pine order semantics and may fill intrabar.']
    pine_assignments = [{'mode': '', 'name': 'length', 'op': '=', 'expr': '20', 'conditions': []}, {'mode': '', 'name': 'mult', 'op': '=', 'expr': '1.5', 'conditions': []}, {'mode': '', 'name': 'src', 'op': '=', 'expr': 'close', 'conditions': []}, {'mode': '', 'name': 'riskRewardRatio', 'op': '=', 'expr': 'input(3.0, title="Risk-Reward Ratio")', 'conditions': []}, {'mode': '', 'name': 'basis', 'op': '=', 'expr': 'ta.ema(src, length)', 'conditions': []}, {'mode': '', 'name': 'dev', 'op': '=', 'expr': 'mult * ta.stdev(src, length)', 'conditions': []}, {'mode': '', 'name': 'upper', 'op': '=', 'expr': 'basis + dev', 'conditions': []}, {'mode': '', 'name': 'lower', 'op': '=', 'expr': 'basis - dev', 'conditions': []}, {'mode': 'var', 'name': 'twoCandlesAgoUpperCrossLow', 'op': '=', 'expr': 'na', 'conditions': []}, {'mode': 'var', 'name': 'twoCandlesAgoLowerCrossHigh', 'op': '=', 'expr': 'na', 'conditions': []}, {'mode': '', 'name': 'twoCandlesAgoUpperCrossLow', 'op': ':=', 'expr': 'low[2]', 'conditions': ['(close[2] > upper[2])']}, {'mode': '', 'name': 'twoCandlesAgoLowerCrossHigh', 'op': ':=', 'expr': 'high[2]', 'conditions': ['(close[2] < lower[2])']}, {'mode': '', 'name': 'longCondition', 'op': '=', 'expr': '(not na(twoCandlesAgoLowerCrossHigh)) and (high > twoCandlesAgoLowerCrossHigh)', 'conditions': []}, {'mode': '', 'name': 'shortCondition', 'op': '=', 'expr': '(not na(twoCandlesAgoUpperCrossLow)) and (low < twoCandlesAgoUpperCrossLow)', 'conditions': []}, {'mode': '', 'name': 'stopLoss', 'op': '=', 'expr': 'low - (high - low) * 0.05', 'conditions': ['(longCondition)']}, {'mode': '', 'name': 'takeProfit', 'op': '=', 'expr': 'close + (close - stopLoss) * riskRewardRatio', 'conditions': ['(longCondition)']}, {'mode': '', 'name': 'stopLoss', 'op': '=', 'expr': 'high + (high - low) * 0.05', 'conditions': ['(shortCondition)']}, {'mode': '', 'name': 'takeProfit', 'op': '=', 'expr': 'close - (stopLoss - close) * riskRewardRatio', 'conditions': ['(shortCondition)']}]
    pine_user_functions = []
    pine_controls = [{'indent': 0, 'statement': 'if (close[2] > upper[2])'}, {'indent': 0, 'statement': 'if (close[2] < lower[2])'}, {'indent': 0, 'statement': 'if (longCondition)'}, {'indent': 0, 'statement': 'if (shortCondition)'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("Buy", strategy.long)', 'conditions': ['(longCondition)'], 'statement': 'strategy.entry("Buy", strategy.long)'}, {'kind': 'exit', 'call': 'strategy.exit("Exit Buy", "Buy", stop=stopLoss, limit=takeProfit)', 'conditions': ['(longCondition)'], 'statement': 'strategy.exit("Exit Buy", "Buy", stop=stopLoss, limit=takeProfit)'}, {'kind': 'entry', 'call': 'strategy.entry("Sell", strategy.short)', 'conditions': ['(shortCondition)'], 'statement': 'strategy.entry("Sell", strategy.short)'}, {'kind': 'exit', 'call': 'strategy.exit("Exit Sell", "Sell", stop=stopLoss, limit=takeProfit)', 'conditions': ['(shortCondition)'], 'statement': 'strategy.exit("Exit Sell", "Sell", stop=stopLoss, limit=takeProfit)'}]
    original_pine = '/*backtest\nstart: 2024-02-25 00:00:00\nend: 2024-02-26 00:00:00\nperiod: 4h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This Pine Script™ code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n\n\n//@version=5\nstrategy("Bollinger Band Strategy with Early Signal (v5)", overlay=true)\n\n// Inputs\nlength = 20\nmult = 1.5\nsrc = close\nriskRewardRatio = input(3.0, title="Risk-Reward Ratio")\n\n// Calculating Bollinger Bands\nbasis = ta.ema(src, length)\ndev = mult * ta.stdev(src, length)\nupper = basis + dev\nlower = basis - dev\n\n// Plotting Bollinger Bands\nplot(upper, "Upper Band", color=color.red)\nplot(lower, "Lower Band", color=color.green)\n\n// Tracking Two Candles Ago Crossing Bollinger Bands\nvar float twoCandlesAgoUpperCrossLow = na\nvar float twoCandlesAgoLowerCrossHigh = na\n\nif (close[2] > upper[2])\n    twoCandlesAgoUpperCrossLow := low[2]\nif (close[2] < lower[2])\n    twoCandlesAgoLowerCrossHigh := high[2]\n\n// Entry Conditions\nlongCondition = (not na(twoCandlesAgoLowerCrossHigh)) and (high > twoCandlesAgoLowerCrossHigh)\nshortCondition = (not na(twoCandlesAgoUpperCrossLow)) and (low < twoCandlesAgoUpperCrossLow)\n\n// Plotting Entry Points\nplotshape(longCondition, title="Buy Signal", location=location.belowbar, color=color.green, style=shape.labelup, text="BUY")\nplotshape(shortCondition, title="Sell Signal", location=location.abovebar, color=color.red, style=shape.labeldown, text="SELL")\n\n// Strategy Execution\nif (longCondition)\n    stopLoss = low - (high - low) * 0.05\n    takeProfit = close + (close - stopLoss) * riskRewardRatio\n    strategy.entry("Buy", strategy.long)\n    strategy.exit("Exit Buy", "Buy", stop=stopLoss, limit=takeProfit)\n\nif (shortCondition)\n    stopLoss = high + (high - low) * 0.05\n    takeProfit = close - (stopLoss - close) * riskRewardRatio\n    strategy.entry("Sell", strategy.short)\n    strategy.exit("Exit Sell", "Sell", stop=stopLoss, limit=takeProfit)'

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
