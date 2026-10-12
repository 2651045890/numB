"""Source-faithful deep-assisted port of 平滑移动平均线交叉策略EMA-Crossover-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_5467cf96(PinePortBase, IStrategy):
    source_file = '平滑移动平均线交叉策略EMA-Crossover-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'emaLength': 50}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.entry', 'strategy.close', 'var ', 'for ']
    source_fidelity_notes = ['Uses persistent Pine state (var/varip); state is order-dependent and must be evaluated bar-by-bar, not replaced by a vectorized fill-forward approximation.']
    pine_assignments = [{'mode': '', 'name': 'emaLength', 'op': '=', 'expr': 'input(50, title="EMA Length")', 'conditions': []}, {'mode': '', 'name': 'ema50', 'op': '=', 'expr': 'ta.ema(close, emaLength)', 'conditions': []}, {'mode': '', 'name': 'longCondition', 'op': '=', 'expr': 'ta.crossover(close, ema50)', 'conditions': []}, {'mode': '', 'name': 'shortCondition', 'op': '=', 'expr': 'ta.crossunder(close, ema50)', 'conditions': []}, {'mode': 'var', 'name': 'longSignalHigh', 'op': '=', 'expr': 'na', 'conditions': []}, {'mode': '', 'name': 'longSignalHigh', 'op': ':=', 'expr': 'high', 'conditions': ['(longCondition)']}, {'mode': 'var', 'name': 'shortSignalLow', 'op': '=', 'expr': 'na', 'conditions': []}, {'mode': '', 'name': 'shortSignalLow', 'op': ':=', 'expr': 'low', 'conditions': ['(shortCondition)']}, {'mode': '', 'name': 'longExitCondition', 'op': '=', 'expr': 'ta.crossunder(close, longSignalHigh)', 'conditions': []}, {'mode': '', 'name': 'shortExitCondition', 'op': '=', 'expr': 'ta.crossover(close, shortSignalLow)', 'conditions': []}]
    pine_user_functions = []
    pine_controls = [{'indent': 0, 'statement': 'if (longCondition)'}, {'indent': 0, 'statement': 'if (shortCondition)'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("Long", strategy.long, when=longCondition)', 'conditions': [], 'statement': 'strategy.entry("Long", strategy.long, when=longCondition)'}, {'kind': 'entry', 'call': 'strategy.entry("Short", strategy.short, when=shortCondition)', 'conditions': [], 'statement': 'strategy.entry("Short", strategy.short, when=shortCondition)'}, {'kind': 'close', 'call': 'strategy.close("Long", when=longExitCondition)', 'conditions': [], 'statement': 'strategy.close("Long", when=longExitCondition)'}, {'kind': 'close', 'call': 'strategy.close("Short", when=shortExitCondition)', 'conditions': [], 'statement': 'strategy.close("Short", when=shortExitCondition)'}]
    original_pine = '/*backtest\nstart: 2022-11-17 00:00:00\nend: 2023-11-23 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("EMA 50 Crossover Strategy", shorttitle="EMA 50 xover", overlay=true)\n\n// Input for EMA length\nemaLength = input(50, title="EMA Length")\n\n// Calculate EMA 50\nema50 = ta.ema(close, emaLength)\n\n// Define conditions for long entry\nlongCondition = ta.crossover(close, ema50)\n\n// Define conditions for short entry\nshortCondition = ta.crossunder(close, ema50)\n\n// Calculate the high of the signal candle for long entry\nvar float longSignalHigh = na\nif (longCondition)\n    longSignalHigh := high\n\n// Calculate the low of the signal candle for short entry\nvar float shortSignalLow = na\nif (shortCondition)\n    shortSignalLow := low\n\n// Long entry\nplotshape(series=longCondition, title="Long Entry Signal", location=location.belowbar, color=color.green, style=shape.triangleup, size=size.small)\n\n// Short entry\nplotshape(series=shortCondition, title="Short Entry Signal", location=location.abovebar, color=color.red, style=shape.triangledown, size=size.small)\n\n// Exit conditions\nlongExitCondition = ta.crossunder(close, longSignalHigh)\nshortExitCondition = ta.crossover(close, shortSignalLow)\n\n// Plot exit signals\nplotshape(series=longExitCondition, title="Long Exit Signal", location=location.abovebar, color=color.red, style=shape.triangledown, size=size.small)\nplotshape(series=shortExitCondition, title="Short Exit Signal", location=location.belowbar, color=color.green, style=shape.triangleup, size=size.small)\n\n// Strategy entry and exit logic\nstrategy.entry("Long", strategy.long, when=longCondition)\nstrategy.entry("Short", strategy.short, when=shortCondition)\nstrategy.close("Long", when=longExitCondition)\nstrategy.close("Short", when=shortExitCondition)\n\n// Plot EMA 50\nplot(ema50, title="EMA 50", color=color.blue)'

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
