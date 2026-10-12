"""Source-faithful deep-assisted port of 快速EMA和慢速EMA动量突破策略fast-EMA-and-slow-EMA-Momentum-Breakthrough-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_ce70de45(PinePortBase, IStrategy):
    source_file = '快速EMA和慢速EMA动量突破策略fast-EMA-and-slow-EMA-Momentum-Breakthrough-Strategy.md'
    timeframe = '1d'
    can_short = False
    source_defaults = {'fastEmaLength': 37, 'slowEmaLength': 370}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.entry', 'strategy.close', 'for ']
    source_fidelity_notes = []
    pine_assignments = [{'mode': '', 'name': 'fastEmaLength', 'op': '=', 'expr': 'input(37, title="Fast EMA Length")', 'conditions': []}, {'mode': '', 'name': 'slowEmaLength', 'op': '=', 'expr': 'input(370, title="Slow EMA Length")', 'conditions': []}, {'mode': '', 'name': 'fastEma', 'op': '=', 'expr': 'ta.ema(close, fastEmaLength)', 'conditions': []}, {'mode': '', 'name': 'slowEma', 'op': '=', 'expr': 'ta.ema(close, slowEmaLength)', 'conditions': []}, {'mode': '', 'name': 'buyCondition', 'op': '=', 'expr': 'ta.crossover(fastEma, slowEma)', 'conditions': []}, {'mode': '', 'name': 'sellCondition', 'op': '=', 'expr': 'ta.crossunder(fastEma, slowEma)', 'conditions': []}]
    pine_user_functions = []
    pine_controls = []
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("Buy", strategy.long, when=buyCondition)', 'conditions': [], 'statement': 'strategy.entry("Buy", strategy.long, when=buyCondition)'}, {'kind': 'close', 'call': 'strategy.close("Buy", when=sellCondition)', 'conditions': [], 'statement': 'strategy.close("Buy", when=sellCondition)'}]
    original_pine = '/*backtest\nstart: 2022-12-20 00:00:00\nend: 2023-12-26 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This Pine Script™ code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © umerhafeez37733\n\n//@version=5\nstrategy("EMA Crossover Strategy", overlay=true)\n\n// Input for EMA lengths\nfastEmaLength = input(37, title="Fast EMA Length")\nslowEmaLength = input(370, title="Slow EMA Length")\n\n// Calculate EMAs\nfastEma = ta.ema(close, fastEmaLength)\nslowEma = ta.ema(close, slowEmaLength)\n\n// Plot EMAs on the chart\nplot(fastEma, title="Fast EMA", color=color.blue)\nplot(slowEma, title="Slow EMA", color=color.red)\n\n// Buy condition: Fast EMA crosses above Slow EMA\nbuyCondition = ta.crossover(fastEma, slowEma)\n\n// Sell condition: Fast EMA crosses below Slow EMA\nsellCondition = ta.crossunder(fastEma, slowEma)\n\n// Plot Buy and Sell signals on the chart\nplotshape(series=buyCondition, title="Buy Signal", color=color.green, style=shape.triangleup, location=location.belowbar)\nplotshape(series=sellCondition, title="Sell Signal", color=color.red, style=shape.triangledown, location=location.abovebar)\n\n// Execute strategy\nstrategy.entry("Buy", strategy.long, when=buyCondition)\nstrategy.close("Buy", when=sellCondition)'

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
