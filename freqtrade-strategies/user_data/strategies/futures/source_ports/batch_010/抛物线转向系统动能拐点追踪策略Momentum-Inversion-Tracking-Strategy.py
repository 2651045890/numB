"""Source-faithful deep-assisted port of 抛物线转向系统动能拐点追踪策略Momentum-Inversion-Tracking-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_76ec88cc(PinePortBase, IStrategy):
    source_file = '抛物线转向系统动能拐点追踪策略Momentum-Inversion-Tracking-Strategy.md'
    timeframe = '1h'
    can_short = True
    source_defaults = {'start': 0.02, 'increment': 0.02, 'maximum': 0.2}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 10.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.entry', 'strategy.equity', 'label.']
    source_fidelity_notes = ['Reads broker/strategy state; signals depend on fill timing and cannot be reduced to indicator-only booleans without changing behavior.', 'Drawing/table calls are display-only unless their IDs/state are later read; preserved in source map but excluded from trade signal calculation where non-causal.']
    pine_assignments = [{'mode': '', 'name': 'start', 'op': '=', 'expr': 'input(0.02, title="Start")', 'conditions': []}, {'mode': '', 'name': 'increment', 'op': '=', 'expr': 'input(0.02, title="Increment")', 'conditions': []}, {'mode': '', 'name': 'maximum', 'op': '=', 'expr': 'input(0.2, title="Maximum")', 'conditions': []}, {'mode': '', 'name': 'sar', 'op': '=', 'expr': 'ta.sar(start, increment, maximum)', 'conditions': []}, {'mode': '', 'name': 'longCondition', 'op': '=', 'expr': 'ta.crossover(close, sar)', 'conditions': []}, {'mode': '', 'name': 'shortCondition', 'op': '=', 'expr': 'ta.crossunder(close, sar)', 'conditions': []}, {'mode': '', 'name': 'equity', 'op': '=', 'expr': 'strategy.equity', 'conditions': []}, {'mode': '', 'name': 'equity_str', 'op': '=', 'expr': 'str.tostring(equity)', 'conditions': []}, {'mode': '', 'name': 'equity_plot', 'op': '=', 'expr': 'plot(equity, title="Equity", color=color.blue, linewidth=2)', 'conditions': []}]
    pine_user_functions = []
    pine_controls = []
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("Long", strategy.long, when=longCondition)', 'conditions': [], 'statement': 'strategy.entry("Long", strategy.long, when=longCondition)'}, {'kind': 'entry', 'call': 'strategy.entry("Short", strategy.short, when=shortCondition)', 'conditions': [], 'statement': 'strategy.entry("Short", strategy.short, when=shortCondition)'}]
    original_pine = '/*backtest\nstart: 2023-12-17 00:00:00\nend: 2024-01-16 00:00:00\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("Parabolic SAR Strategy", shorttitle="PSAR", overlay=true, default_qty_type=strategy.percent_of_equity, default_qty_value=10)\n\n// Parabolic SAR settings\nstart = input(0.02, title="Start")\nincrement = input(0.02, title="Increment")\nmaximum = input(0.2, title="Maximum")\n\n// Calculate Parabolic SAR\nsar = ta.sar(start, increment, maximum)\n\n// Plot Parabolic SAR on the chart\nplot(sar, color=color.red, title="Parabolic SAR")\n\n// Strategy logic\nlongCondition = ta.crossover(close, sar)\nshortCondition = ta.crossunder(close, sar)\n\n// Execute strategy orders\nstrategy.entry("Long", strategy.long, when=longCondition)\nstrategy.entry("Short", strategy.short, when=shortCondition)\n\n// Plot buy and sell signals on the chart\nplotshape(series=longCondition, title="Buy Signal", color=color.green, style=shape.labelup, location=location.belowbar, text="Buy")\nplotshape(series=shortCondition, title="Sell Signal", color=color.red, style=shape.labeldown, location=location.abovebar, text="Sell")\n\n// Calculate equity manually\nequity = strategy.equity\nequity_str = str.tostring(equity)\nequity_plot = plot(equity, title="Equity", color=color.blue, linewidth=2)\n\n// Update equity plot only on bar close to avoid repainting issues\nlabel.new(bar_index, na, text=equity_str, style=label.style_none, color=color.blue, yloc=yloc.abovebar)'

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
