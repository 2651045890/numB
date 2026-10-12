"""Source-faithful deep-assisted port of 指数移动平均线交叉杠杆策略-Exponential-Moving-Average-Crossover-Leverage-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_5fa49589(PinePortBase, IStrategy):
    source_file = '指数移动平均线交叉杠杆策略-Exponential-Moving-Average-Crossover-Leverage-Strategy.md'
    timeframe = '1h'
    can_short = False
    source_defaults = {'startDate': 'timestamp("2023-01-01"', 'endDate': 'timestamp("2024-04-028"', 'leverage': 3.0, 'useEMA': True, 'ema1_length': 20, 'ema2_length': 55}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 100.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.entry', 'strategy.close', 'strategy.equity', 'var ', 'for ']
    source_fidelity_notes = ['Uses persistent Pine state (var/varip); state is order-dependent and must be evaluated bar-by-bar, not replaced by a vectorized fill-forward approximation.', 'Reads broker/strategy state; signals depend on fill timing and cannot be reduced to indicator-only booleans without changing behavior.']
    pine_assignments = [{'mode': '', 'name': 'startDate', 'op': '=', 'expr': 'input(defval=timestamp("2023-01-01"), title="Start Date")', 'conditions': []}, {'mode': '', 'name': 'endDate', 'op': '=', 'expr': 'input(defval=timestamp("2024-04-028"), title="End Date")', 'conditions': []}, {'mode': '', 'name': 'leverage', 'op': '=', 'expr': 'input.float(3.0, title="Leverage Multiplier", minval=1.0, maxval=10.0, step=0.1)', 'conditions': []}, {'mode': '', 'name': 'useEMA', 'op': '=', 'expr': 'input.bool(true, title="Use EMA (true) or MA (false)?")', 'conditions': []}, {'mode': '', 'name': 'src', 'op': '=', 'expr': 'close', 'conditions': []}, {'mode': '', 'name': 'ema1_length', 'op': '=', 'expr': "input.int(20, title='EMA/MA-1 Length')", 'conditions': []}, {'mode': '', 'name': 'ema2_length', 'op': '=', 'expr': "input.int(55, title='EMA/MA-2 Length')", 'conditions': []}, {'mode': '', 'name': 'pema1', 'op': '=', 'expr': 'useEMA ? ta.ema(src, ema1_length) : ta.sma(src, ema1_length)', 'conditions': []}, {'mode': '', 'name': 'pema2', 'op': '=', 'expr': 'useEMA ? ta.ema(src, ema2_length) : ta.sma(src, ema2_length)', 'conditions': []}, {'mode': '', 'name': 'crossedAbove', 'op': '=', 'expr': 'ta.crossover(pema1, pema2)', 'conditions': []}, {'mode': 'var', 'name': 'readyToEnter', 'op': '=', 'expr': 'false', 'conditions': []}, {'mode': '', 'name': 'readyToEnter', 'op': ':=', 'expr': 'true', 'conditions': ['(crossedAbove)']}, {'mode': '', 'name': 'entryCondition', 'op': '=', 'expr': 'readyToEnter', 'conditions': []}, {'mode': '', 'name': 'readyToEnter', 'op': ':=', 'expr': 'false', 'conditions': ['(entryCondition)']}, {'mode': '', 'name': 'exitCondition', 'op': '=', 'expr': 'ta.crossunder(pema1, pema2)', 'conditions': []}, {'mode': '', 'name': 'inBacktestPeriod', 'op': '=', 'expr': 'true', 'conditions': []}, {'mode': '', 'name': 'ema1_color', 'op': '=', 'expr': 'pema1 > pema2 ? color.red : color.green', 'conditions': []}, {'mode': '', 'name': 'ema2_color', 'op': '=', 'expr': 'pema1 > pema2 ? color.red : color.green', 'conditions': []}]
    pine_user_functions = []
    pine_controls = [{'indent': 0, 'statement': 'if (crossedAbove)'}, {'indent': 0, 'statement': 'if (entryCondition)'}, {'indent': 0, 'statement': 'if (inBacktestPeriod)'}, {'indent': 4, 'statement': 'if (entryCondition)'}, {'indent': 4, 'statement': 'if (exitCondition)'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("Long", strategy.long, qty=strategy.equity * leverage / close)', 'conditions': ['(inBacktestPeriod)', '(entryCondition)'], 'statement': 'strategy.entry("Long", strategy.long, qty=strategy.equity * leverage / close)'}, {'kind': 'close', 'call': 'strategy.close("Long")', 'conditions': ['(inBacktestPeriod)', '(exitCondition)'], 'statement': 'strategy.close("Long")'}]
    original_pine = '/*backtest\nstart: 2024-03-01 00:00:00\nend: 2024-03-31 23:59:59\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("EMA Crossover Strategy with Leverage, Conditional Entry, and MA Option", overlay=true, default_qty_type=strategy.percent_of_equity, default_qty_value=100)\n\n// Inputs for backtesting period\nstartDate = input(defval=timestamp("2023-01-01"), title="Start Date")\nendDate = input(defval=timestamp("2024-04-028"), title="End Date")\n\n// Input for leverage multiplier\nleverage = input.float(3.0, title="Leverage Multiplier", minval=1.0, maxval=10.0, step=0.1)\n\n// Input for choosing between EMA and MA\nuseEMA = input.bool(true, title="Use EMA (true) or MA (false)?")\n\n// Input source and lengths for MAs\nsrc = close\nema1_length = input.int(20, title=\'EMA/MA-1 Length\')\nema2_length = input.int(55, title=\'EMA/MA-2 Length\')\n\n// Calculate the MAs based on user selection\npema1 = useEMA ? ta.ema(src, ema1_length) : ta.sma(src, ema1_length)\npema2 = useEMA ? ta.ema(src, ema2_length) : ta.sma(src, ema2_length)\n\n// Tracking the crossover condition for strategy entry\ncrossedAbove = ta.crossover(pema1, pema2)\n\n// Define a variable to track if a valid entry condition has been met\nvar bool readyToEnter = false\n\n// Check for MA crossover and update readyToEnter\nif (crossedAbove)\n    readyToEnter := true\n\n// Entry condition: Enter when price touches MA-1 after the crossover // and (low <= pema1 and high >= pema1)\nentryCondition = readyToEnter\n\n// Reset readyToEnter after entry\nif (entryCondition)\n    readyToEnter := false\n\n// Exit condition: Price crosses under MA-1\nexitCondition = ta.crossunder(pema1, pema2)\n\n// Check if the current bar\'s time is within the specified period\ninBacktestPeriod = true\n\n// Execute trade logic only within the specified date range and apply leverage to position sizing\nif (inBacktestPeriod)\n    if (entryCondition)\n        strategy.entry("Long", strategy.long, qty=strategy.equity * leverage / close)\n    if (exitCondition)\n        strategy.close("Long")\n\n\n// Plotting the MAs for visual reference\nema1_color = pema1 > pema2 ? color.red : color.green\nema2_color = pema1 > pema2 ? color.red : color.green\nplot(pema1, color=ema1_color, style=plot.style_line, linewidth=1, title=\'EMA/MA-1\')\nplot(pema2, color=ema2_color, style=plot.style_line, linewidth=1, title=\'EMA/MA-2\')'

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
