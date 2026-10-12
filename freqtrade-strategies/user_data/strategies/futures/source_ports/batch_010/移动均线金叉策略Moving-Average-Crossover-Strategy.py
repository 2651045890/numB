"""Source-faithful deep-assisted port of 移动均线金叉策略Moving-Average-Crossover-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_d4fb27bc(PinePortBase, IStrategy):
    source_file = '移动均线金叉策略Moving-Average-Crossover-Strategy.md'
    timeframe = '10m'
    can_short = False
    source_defaults = {'fastLength': 9, 'slowLength': 21, 'stopLossPercent': 1.0, 'takeProfitPercent': 1.0}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.exit', 'strategy.entry', 'strategy.close', 'var ', 'for ']
    source_fidelity_notes = ['Uses persistent Pine state (var/varip); state is order-dependent and must be evaluated bar-by-bar, not replaced by a vectorized fill-forward approximation.', 'Uses strategy.exit; stop/limit/profit/loss/trailing arguments have Pine order semantics and may fill intrabar.']
    pine_assignments = [{'mode': '', 'name': 'fastLength', 'op': '=', 'expr': 'input.int(9, title="Fast MA Length", minval=1)', 'conditions': []}, {'mode': '', 'name': 'slowLength', 'op': '=', 'expr': 'input.int(21, title="Slow MA Length", minval=1)', 'conditions': []}, {'mode': '', 'name': 'stopLossPercent', 'op': '=', 'expr': 'input.float(1.0, title="Stop Loss %", step=0.1)', 'conditions': []}, {'mode': '', 'name': 'takeProfitPercent', 'op': '=', 'expr': 'input.float(1.0, title="Take Profit %", step=0.1)', 'conditions': []}, {'mode': '', 'name': 'fastMA', 'op': '=', 'expr': 'ta.sma(close, fastLength)', 'conditions': []}, {'mode': '', 'name': 'slowMA', 'op': '=', 'expr': 'ta.sma(close, slowLength)', 'conditions': []}, {'mode': '', 'name': 'longCondition', 'op': '=', 'expr': 'ta.crossover(fastMA, slowMA)', 'conditions': []}, {'mode': '', 'name': 'shortCondition', 'op': '=', 'expr': 'ta.crossunder(fastMA, slowMA)', 'conditions': []}, {'mode': 'var', 'name': 'stopLossPrice', 'op': '=', 'expr': '0.0', 'conditions': []}, {'mode': 'var', 'name': 'takeProfitPrice', 'op': '=', 'expr': '0.0', 'conditions': []}, {'mode': '', 'name': 'stopLossPrice', 'op': ':=', 'expr': 'close * (1.0 - stopLossPercent / 100)', 'conditions': ['(longCondition)']}, {'mode': '', 'name': 'takeProfitPrice', 'op': ':=', 'expr': 'close * (1.0 + takeProfitPercent / 100)', 'conditions': ['(longCondition)']}]
    pine_user_functions = []
    pine_controls = [{'indent': 0, 'statement': 'if (longCondition)'}, {'indent': 0, 'statement': 'if (shortCondition)'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("Long", strategy.long)', 'conditions': ['(longCondition)'], 'statement': 'strategy.entry("Long", strategy.long)'}, {'kind': 'close', 'call': 'strategy.close("Long")', 'conditions': ['(shortCondition)'], 'statement': 'strategy.close("Long")'}, {'kind': 'exit', 'call': 'strategy.exit("Stop Loss/Profit", stop=stopLossPrice, limit=takeProfitPrice)', 'conditions': [], 'statement': 'strategy.exit("Stop Loss/Profit", stop=stopLossPrice, limit=takeProfitPrice)'}]
    original_pine = '/*backtest\nstart: 2023-09-01 00:00:00\nend: 2023-09-20 23:59:59\nperiod: 10m\nbasePeriod: 1m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("Profitable Crypto Strategy", shorttitle="Profit Strategy", overlay=true)\n\n// Define strategy parameters\nfastLength = input.int(9, title="Fast MA Length", minval=1)\nslowLength = input.int(21, title="Slow MA Length", minval=1)\nstopLossPercent = input.float(1.0, title="Stop Loss %", step=0.1)\ntakeProfitPercent = input.float(1.0, title="Take Profit %", step=0.1)\n\n// Calculate moving averages\nfastMA = ta.sma(close, fastLength)\nslowMA = ta.sma(close, slowLength)\n\n// Entry condition: Buy when fast MA crosses above slow MA\nlongCondition = ta.crossover(fastMA, slowMA)\n// Exit condition: Sell when fast MA crosses below slow MA\nshortCondition = ta.crossunder(fastMA, slowMA)\n\n// Plot moving averages on the chart\nplot(fastMA, color=color.blue, title="Fast MA")\nplot(slowMA, color=color.orange, title="Slow MA")\n\n// Strategy entry and exit logic\nvar stopLossPrice = 0.0\nvar takeProfitPrice = 0.0\n\nif (longCondition)\n    stopLossPrice := close * (1.0 - stopLossPercent / 100)\n    takeProfitPrice := close * (1.0 + takeProfitPercent / 100)\n    strategy.entry("Long", strategy.long)\n\nif (shortCondition)\n    strategy.close("Long")\n\n// Set stop loss and take profit for open positions\nstrategy.exit("Stop Loss/Profit", stop=stopLossPrice, limit=takeProfitPrice)'

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
