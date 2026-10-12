"""Source-faithful deep-assisted port of 技术图形确认型多周期动量策略-Technical-Chart-Pattern-Confirmation-Momentum-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_b059734d(PinePortBase, IStrategy):
    source_file = '技术图形确认型多周期动量策略-Technical-Chart-Pattern-Confirmation-Momentum-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'atrLength': 14}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.exit', 'strategy.entry', 'for ', '=>']
    source_fidelity_notes = ['Uses strategy.exit; stop/limit/profit/loss/trailing arguments have Pine order semantics and may fill intrabar.']
    pine_assignments = [{'mode': '', 'name': 'atrLength', 'op': '=', 'expr': 'input.int(14, title="ATR Length")', 'conditions': []}, {'mode': '', 'name': 'atrValue', 'op': '=', 'expr': 'ta.atr(atrLength)', 'conditions': []}, {'mode': '', 'name': 'stopLoss', 'op': '=', 'expr': 'atrValue * 1.5 // Stop loss 1.5 ATR', 'conditions': []}, {'mode': '', 'name': 'takeProfit', 'op': '=', 'expr': 'atrValue * 3 // Take profit 3 ATR', 'conditions': []}, {'mode': '', 'name': 'longSignal', 'op': '=', 'expr': '(isHeadAndShoulders() or isDoubleBottom() or isAscendingTriangle()) and close > high[1]', 'conditions': []}, {'mode': '', 'name': 'shortSignal', 'op': '=', 'expr': '(isDoubleTop() or isDescendingTriangle() or isFlagPattern()) and close < low[1]', 'conditions': []}]
    pine_user_functions = [{'name': 'isHeadAndShoulders', 'args': '', 'body': ''}, {'name': 'isDoubleTop', 'args': '', 'body': ''}, {'name': 'isDoubleBottom', 'args': '', 'body': ''}, {'name': 'isSymmetricalTriangle', 'args': '', 'body': ''}, {'name': 'isAscendingTriangle', 'args': '', 'body': ''}, {'name': 'isDescendingTriangle', 'args': '', 'body': ''}, {'name': 'isFlagPattern', 'args': '', 'body': ''}]
    pine_controls = [{'indent': 0, 'statement': 'if (longSignal)'}, {'indent': 0, 'statement': 'if (shortSignal)'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("Buy", strategy.long)', 'conditions': ['(longSignal)'], 'statement': 'strategy.entry("Buy", strategy.long)'}, {'kind': 'exit', 'call': 'strategy.exit("Take Profit/Stop Loss", from_entry="Buy", stop=close - stopLoss, limit=close + takeProfit)', 'conditions': ['(longSignal)'], 'statement': 'strategy.exit("Take Profit/Stop Loss", from_entry="Buy", stop=close - stopLoss, limit=close + takeProfit)'}, {'kind': 'entry', 'call': 'strategy.entry("Sell", strategy.short)', 'conditions': ['(shortSignal)'], 'statement': 'strategy.entry("Sell", strategy.short)'}, {'kind': 'exit', 'call': 'strategy.exit("Take Profit/Stop Loss", from_entry="Sell", stop=close + stopLoss, limit=close - takeProfit)', 'conditions': ['(shortSignal)'], 'statement': 'strategy.exit("Take Profit/Stop Loss", from_entry="Sell", stop=close + stopLoss, limit=close - takeProfit)'}]
    original_pine = '/*backtest\nstart: 2024-02-29 00:00:00\nend: 2025-02-26 08:00:00\nperiod: 1d\nbasePeriod: 1d\nexchanges: [{"eid":"Futures_Binance","currency":"ETH_USDT"}]\n*/\n\n//@version=5\nstrategy("Chart Pattern Strategy - Full Set", overlay=true)\n\n// ATR settings for stop loss and take profit\natrLength = input.int(14, title="ATR Length")\natrValue = ta.atr(atrLength)\nstopLoss = atrValue * 1.5  // Stop loss 1.5 ATR\ntakeProfit = atrValue * 3  // Take profit 3 ATR\n\n// Head and Shoulders Detection\nisHeadAndShoulders() =>\n    high[1] > high[2] and high[1] > high[0] and high[1] > high[3] and high[1] > high[4] and high[0] < high[2] and high[0] < high[3]\n\n// Double Top Detection\nisDoubleTop() =>\n    high[1] > high[2] and high[1] > high[0] and high[1] > high[3] and high[1] > high[4] and high[0] < high[2] and high[0] < high[3]\n\n// Double Bottom Detection\nisDoubleBottom() =>\n    low[1] < low[2] and low[1] < low[0] and low[1] < low[3] and low[1] < low[4] and low[0] > low[2] and low[0] > low[3]\n\n// Symmetrical Triangle Detection\nisSymmetricalTriangle() =>\n    high[2] > high[1] and low[2] < low[1] and high[3] < high[2] and low[3] > low[2]\n\n// Ascending Triangle Detection (Bullish)\nisAscendingTriangle() =>\n    high[2] < high[1] and low[2] > low[1] and high[3] < high[2] and low[3] > low[2]\n\n// Descending Triangle Detection (Bearish)\nisDescendingTriangle() =>\n    high[2] > high[1] and low[2] < low[1] and high[3] < high[2] and low[3] < low[2]\n\n// Flags/Pennants Detection\nisFlagPattern() =>\n    high[1] < high[0] and low[1] > low[0] and high[2] < high[1] and low[2] < low[1]\n\n// Entry Logic (Confirmation based on Breakouts)\nlongSignal = (isHeadAndShoulders() or isDoubleBottom() or isAscendingTriangle()) and close > high[1]\nshortSignal = (isDoubleTop() or isDescendingTriangle() or isFlagPattern()) and close < low[1]\n\n// Plotting Chart Patterns on the Chart\nplotshape(isHeadAndShoulders(), title="Head and Shoulders", location=location.abovebar, color=color.red, style=shape.labelup, text="HS")\nplotshape(isDoubleTop(), title="Double Top", location=location.abovebar, color=color.red, style=shape.labelup, text="DT")\nplotshape(isDoubleBottom(), title="Double Bottom", location=location.belowbar, color=color.green, style=shape.labeldown, text="DB")\nplotshape(isSymmetricalTriangle(), title="Symmetrical Triangle", location=location.top, color=color.blue, style=shape.triangledown, text="ST")\nplotshape(isAscendingTriangle(), title="Ascending Triangle", location=location.belowbar, color=color.green, style=shape.labelup, text="AT")\nplotshape(isDescendingTriangle(), title="Descending Triangle", location=location.abovebar, color=color.red, style=shape.labeldown, text="DT")\nplotshape(isFlagPattern(), title="Flag Pattern", location=location.abovebar, color=color.orange, style=shape.triangledown, text="Flag")\n\n// Executing Trades based on Patterns\nif (longSignal)\n    strategy.entry("Buy", strategy.long)\n    strategy.exit("Take Profit/Stop Loss", from_entry="Buy", stop=close - stopLoss, limit=close + takeProfit)\n\nif (shortSignal)\n    strategy.entry("Sell", strategy.short)\n    strategy.exit("Take Profit/Stop Loss", from_entry="Sell", stop=close + stopLoss, limit=close - takeProfit)'

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
