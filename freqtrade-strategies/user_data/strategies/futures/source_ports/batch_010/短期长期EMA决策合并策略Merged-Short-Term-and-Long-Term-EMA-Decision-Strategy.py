"""Source-faithful deep-assisted port of 短期长期EMA决策合并策略Merged-Short-Term-and-Long-Term-EMA-Decision-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_c005396b(PinePortBase, IStrategy):
    source_file = '短期长期EMA决策合并策略Merged-Short-Term-and-Long-Term-EMA-Decision-Strategy.md'
    timeframe = '1h'
    can_short = True
    source_defaults = {}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.entry', 'strategy.close', 'for ']
    source_fidelity_notes = []
    pine_assignments = [{'mode': '', 'name': 'shortEMA', 'op': '=', 'expr': 'ta.ema(close, 3)', 'conditions': []}, {'mode': '', 'name': 'longEMA', 'op': '=', 'expr': 'ta.ema(close, 30)', 'conditions': []}, {'mode': '', 'name': 'emaDifference', 'op': '=', 'expr': 'shortEMA - longEMA', 'conditions': []}, {'mode': '', 'name': 'buyThreshold', 'op': '=', 'expr': '0.0005', 'conditions': []}, {'mode': '', 'name': 'sellThreshold', 'op': '=', 'expr': '-0.0005', 'conditions': []}, {'mode': '', 'name': 'buyCondition', 'op': '=', 'expr': 'emaDifference > buyThreshold', 'conditions': []}, {'mode': '', 'name': 'sellCondition', 'op': '=', 'expr': 'emaDifference < sellThreshold', 'conditions': []}]
    pine_user_functions = []
    pine_controls = []
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("Buy", strategy.long, when = buyCondition)', 'conditions': [], 'statement': 'strategy.entry("Buy", strategy.long, when = buyCondition)'}, {'kind': 'close', 'call': 'strategy.close("Buy", when = sellCondition)', 'conditions': [], 'statement': 'strategy.close("Buy", when = sellCondition)'}, {'kind': 'entry', 'call': 'strategy.entry("Sell", strategy.short, when = sellCondition)', 'conditions': [], 'statement': 'strategy.entry("Sell", strategy.short, when = sellCondition)'}, {'kind': 'close', 'call': 'strategy.close("Sell", when = buyCondition)', 'conditions': [], 'statement': 'strategy.close("Sell", when = buyCondition)'}]
    original_pine = '/*backtest\nstart: 2023-12-05 00:00:00\nend: 2024-01-04 00:00:00\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("Merged EMA Strategy", shorttitle="MergedEMA", overlay=true)\n\n// Define EMA periods\nshortEMA = ta.ema(close, 3)\nlongEMA = ta.ema(close, 30)\n\n// Plot EMAs on the chart\nplot(shortEMA, color=color.blue, title="3 EMA")\nplot(longEMA, color=color.red, title="30 EMA")\n\n// Calculate the difference between short and long EMAs\nemaDifference = shortEMA - longEMA\n\n// Set threshold for buy and sell signals\nbuyThreshold = 0.0005\nsellThreshold = -0.0005\n\n// Define buy and sell conditions\nbuyCondition = emaDifference > buyThreshold\nsellCondition = emaDifference < sellThreshold\n\n// Plot buy and sell signals on the chart\nplotshape(series=buyCondition, title="Buy Signal", color=color.green, style=shape.triangleup, location=location.belowbar)\nplotshape(series=sellCondition, title="Sell Signal", color=color.red, style=shape.triangledown, location=location.abovebar)\n\n// Strategy logic\nstrategy.entry("Buy", strategy.long, when = buyCondition)\nstrategy.close("Buy", when = sellCondition)\n\nstrategy.entry("Sell", strategy.short, when = sellCondition)\nstrategy.close("Sell", when = buyCondition)'

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
