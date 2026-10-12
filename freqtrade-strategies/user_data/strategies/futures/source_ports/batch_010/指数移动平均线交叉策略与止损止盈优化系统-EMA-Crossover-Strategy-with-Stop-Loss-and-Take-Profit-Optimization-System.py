"""Source-faithful deep-assisted port of 指数移动平均线交叉策略与止损止盈优化系统-EMA-Crossover-Strategy-with-Stop-Loss-and-Take-Profit-Optimization-System.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_888d270e(PinePortBase, IStrategy):
    source_file = '指数移动平均线交叉策略与止损止盈优化系统-EMA-Crossover-Strategy-with-Stop-Loss-and-Take-Profit-Optimization-System.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.exit', 'strategy.entry', 'for ']
    source_fidelity_notes = ['Uses strategy.exit; stop/limit/profit/loss/trailing arguments have Pine order semantics and may fill intrabar.']
    pine_assignments = [{'mode': '', 'name': 'ema5', 'op': '=', 'expr': 'ta.ema(close, 5)', 'conditions': []}, {'mode': '', 'name': 'ema15', 'op': '=', 'expr': 'ta.ema(close, 15)', 'conditions': []}, {'mode': '', 'name': 'longCondition', 'op': '=', 'expr': 'ta.crossover(ema5, ema15)', 'conditions': []}, {'mode': '', 'name': 'shortCondition', 'op': '=', 'expr': 'ta.crossunder(ema5, ema15)', 'conditions': []}, {'mode': '', 'name': 'stopLossPercent', 'op': '=', 'expr': '1.5 // Stop-loss at 1.5%', 'conditions': []}, {'mode': '', 'name': 'takeProfitPercent', 'op': '=', 'expr': '3.0 // Take-profit at 3%', 'conditions': []}, {'mode': '', 'name': 'longStopLoss', 'op': '=', 'expr': 'strategy.position_avg_price * (1 - stopLossPercent / 100)', 'conditions': []}, {'mode': '', 'name': 'longTakeProfit', 'op': '=', 'expr': 'strategy.position_avg_price * (1 + takeProfitPercent / 100)', 'conditions': []}, {'mode': '', 'name': 'shortStopLoss', 'op': '=', 'expr': 'strategy.position_avg_price * (1 + stopLossPercent / 100)', 'conditions': []}, {'mode': '', 'name': 'shortTakeProfit', 'op': '=', 'expr': 'strategy.position_avg_price * (1 - takeProfitPercent / 100)', 'conditions': []}]
    pine_user_functions = []
    pine_controls = [{'indent': 0, 'statement': 'if (longCondition)'}, {'indent': 0, 'statement': 'if (shortCondition)'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("Long", strategy.long)', 'conditions': ['(longCondition)'], 'statement': 'strategy.entry("Long", strategy.long)'}, {'kind': 'exit', 'call': 'strategy.exit("Take Profit/Stop Loss", "Long", stop=longStopLoss, limit=longTakeProfit)', 'conditions': ['(longCondition)'], 'statement': 'strategy.exit("Take Profit/Stop Loss", "Long", stop=longStopLoss, limit=longTakeProfit)'}, {'kind': 'entry', 'call': 'strategy.entry("Short", strategy.short)', 'conditions': ['(shortCondition)'], 'statement': 'strategy.entry("Short", strategy.short)'}, {'kind': 'exit', 'call': 'strategy.exit("Take Profit/Stop Loss", "Short", stop=shortStopLoss, limit=shortTakeProfit)', 'conditions': ['(shortCondition)'], 'statement': 'strategy.exit("Take Profit/Stop Loss", "Short", stop=shortStopLoss, limit=shortTakeProfit)'}]
    original_pine = '/*backtest\nstart: 2019-12-23 08:00:00\nend: 2024-11-26 00:00:00\nperiod: 1d\nbasePeriod: 1d\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("5 EMA and 15 EMA Crossover with Stop Loss and Target", overlay=true)\n\n// Define EMAs\nema5 = ta.ema(close, 5)\nema15 = ta.ema(close, 15)\n\n// Plot EMAs on the chart\nplot(ema5, title="5 EMA", color=color.blue)\nplot(ema15, title="15 EMA", color=color.red)\n\n// Crossover conditions\nlongCondition = ta.crossover(ema5, ema15)\nshortCondition = ta.crossunder(ema5, ema15)\n\n// Stop-loss and take-profit percentage\nstopLossPercent = 1.5  // Stop-loss at 1.5%\ntakeProfitPercent = 3.0  // Take-profit at 3%\n\n// Calculate stop-loss and take-profit levels for long and short positions\nlongStopLoss = strategy.position_avg_price * (1 - stopLossPercent / 100)\nlongTakeProfit = strategy.position_avg_price * (1 + takeProfitPercent / 100)\n\nshortStopLoss = strategy.position_avg_price * (1 + stopLossPercent / 100)\nshortTakeProfit = strategy.position_avg_price * (1 - takeProfitPercent / 100)\n\n// Enter long position with stop-loss and take-profit\nif (longCondition)\n    strategy.entry("Long", strategy.long)\n    strategy.exit("Take Profit/Stop Loss", "Long", stop=longStopLoss, limit=longTakeProfit)\n\n// Enter short position with stop-loss and take-profit\nif (shortCondition)\n    strategy.entry("Short", strategy.short)\n    strategy.exit("Take Profit/Stop Loss", "Short", stop=shortStopLoss, limit=shortTakeProfit)\n\n// Plot stop-loss and take-profit levels\nplot(longStopLoss, title="Long Stop Loss", color=color.red, linewidth=1, style=plot.style_linebr)\nplot(longTakeProfit, title="Long Take Profit", color=color.green, linewidth=1, style=plot.style_linebr)\nplot(shortStopLoss, title="Short Stop Loss", color=color.red, linewidth=1, style=plot.style_linebr)\nplot(shortTakeProfit, title="Short Take Profit", color=color.green, linewidth=1, style=plot.style_linebr)'

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
