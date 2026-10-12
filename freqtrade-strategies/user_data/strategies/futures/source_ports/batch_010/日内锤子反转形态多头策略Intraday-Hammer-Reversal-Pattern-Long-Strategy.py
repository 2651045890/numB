"""Source-faithful deep-assisted port of 日内锤子反转形态多头策略Intraday-Hammer-Reversal-Pattern-Long-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_5725a52c(PinePortBase, IStrategy):
    source_file = '日内锤子反转形态多头策略Intraday-Hammer-Reversal-Pattern-Long-Strategy.md'
    timeframe = '1d'
    can_short = False
    source_defaults = {}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.exit', 'strategy.entry', '=>']
    source_fidelity_notes = ['Uses strategy.exit; stop/limit/profit/loss/trailing arguments have Pine order semantics and may fill intrabar.']
    pine_assignments = [{'mode': '', 'name': 'bodySize', 'op': '=', 'expr': 'math.abs(close[1] - open[1])', 'conditions': []}, {'mode': '', 'name': 'lowerWickSize', 'op': '=', 'expr': 'open[1] - low[1]', 'conditions': []}, {'mode': '', 'name': 'upperWickSize', 'op': '=', 'expr': 'high[1] - open[1] // For a red candle, the upper wick is from the open to the high', 'conditions': []}, {'mode': '', 'name': 'bodyIsSmall', 'op': '=', 'expr': 'bodySize <= (high[1] - low[1]) * 0.3 // Body is less than 30% of the entire candle range', 'conditions': []}, {'mode': '', 'name': 'lowerWickIsLong', 'op': '=', 'expr': 'lowerWickSize >= bodySize * 2 // Lower wick is at least twice the body length', 'conditions': []}, {'mode': '', 'name': 'noUpperWick', 'op': '=', 'expr': 'upperWickSize == 0 or high[1] <= open[1] * 1.01 // No upper wick or very small', 'conditions': []}, {'mode': '', 'name': 'entryCondition', 'op': '=', 'expr': 'isHammer() and isGreenWithNoSmallTail() and low >low[1]', 'conditions': []}, {'mode': '', 'name': 'stopLossLevel', 'op': '=', 'expr': 'low[1]', 'conditions': []}, {'mode': '', 'name': 'profitTargetLevel', 'op': '=', 'expr': 'close * 1.5', 'conditions': []}, {'mode': '', 'name': 'positionSize', 'op': '=', 'expr': '50000 / close', 'conditions': []}]
    pine_user_functions = [{'name': 'isHammer', 'args': '', 'body': ''}, {'name': 'isGreenWithNoSmallTail', 'args': '', 'body': ''}]
    pine_controls = [{'indent': 0, 'statement': 'if (entryCondition)'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("Hammer Buy", strategy.long,qty=positionSize)', 'conditions': ['(entryCondition)'], 'statement': 'strategy.entry("Hammer Buy", strategy.long,qty=positionSize)'}, {'kind': 'exit', 'call': 'strategy.exit("Take Profit / Stop Loss", "Hammer Buy", stop=stopLossLevel, limit=profitTargetLevel)', 'conditions': ['(entryCondition)'], 'statement': 'strategy.exit("Take Profit / Stop Loss", "Hammer Buy", stop=stopLossLevel, limit=profitTargetLevel)'}]
    original_pine = '/*backtest\nstart: 2023-03-09 00:00:00\nend: 2024-03-14 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("Hammer Pattern and Follow-Up Green Candle Strategy", overlay=true)\n\n// Detecting a Hammer candle\nisHammer() =>\n    bodySize = math.abs(close[1] - open[1])\n    lowerWickSize = open[1] - low[1]\n    upperWickSize = high[1] - open[1] // For a red candle, the upper wick is from the open to the high\n    bodyIsSmall = bodySize <= (high[1] - low[1]) * 0.3 // Body is less than 30% of the entire candle range\n    lowerWickIsLong = lowerWickSize >= bodySize * 2 // Lower wick is at least twice the body length\n    noUpperWick = upperWickSize == 0 or high[1] <= open[1] * 1.01 // No upper wick or very small\n    close[1] < open[1] and bodyIsSmall and lowerWickIsLong and noUpperWick\n\n// Check if the current candle is green with no or small tail\nisGreenWithNoSmallTail() =>\n    close > open\n\n// Entry condition\nentryCondition = isHammer() and isGreenWithNoSmallTail() and low >low[1]\n\n// Calculate stop loss and take profit levels\nstopLossLevel = low[1]\nprofitTargetLevel = close * 1.5\n//Calculate position bodySize\npositionSize = 50000 / close\n\n// Execute strategy\nif (entryCondition)\n    strategy.entry("Hammer Buy", strategy.long,qty=positionSize)\n    strategy.exit("Take Profit / Stop Loss", "Hammer Buy", stop=stopLossLevel, limit=profitTargetLevel)'

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
