"""Source-faithful deep-assisted port of 抛物线SAR指标背离交易策略-Parabolic-SAR-Divergence-Trading-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_4387e5c3(PinePortBase, IStrategy):
    source_file = '抛物线SAR指标背离交易策略-Parabolic-SAR-Divergence-Trading-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'length': 14, 'accelerationFactor': 0.02, 'maximumFactor': 0.2}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.entry', 'alert']
    source_fidelity_notes = []
    pine_assignments = [{'mode': '', 'name': 'length', 'op': '=', 'expr': 'input.int(14, title="SAR Length", minval=1)', 'conditions': []}, {'mode': '', 'name': 'accelerationFactor', 'op': '=', 'expr': 'input.float(0.02, title="Acceleration Factor", minval=0.01)', 'conditions': []}, {'mode': '', 'name': 'maximumFactor', 'op': '=', 'expr': 'input.float(0.2, title="Maximum Factor", minval=0.01)', 'conditions': []}, {'mode': '', 'name': 'sar', 'op': '=', 'expr': 'ta.sar(length, accelerationFactor, maximumFactor)', 'conditions': []}, {'mode': '', 'name': 'lookback', 'op': '=', 'expr': '5', 'conditions': []}, {'mode': '', 'name': 'bullCond', 'op': '=', 'expr': 'close[lookback] < close[lookback + 1] and sar[lookback] > sar[lookback + 1]', 'conditions': []}, {'mode': '', 'name': 'bearCond', 'op': '=', 'expr': 'close[lookback] > close[lookback + 1] and sar[lookback] < sar[lookback + 1]', 'conditions': []}]
    pine_user_functions = []
    pine_controls = [{'indent': 0, 'statement': 'if (bullCond)'}, {'indent': 0, 'statement': 'if (bearCond)'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("Long", strategy.long)', 'conditions': ['(bullCond)'], 'statement': 'strategy.entry("Long", strategy.long)'}, {'kind': 'entry', 'call': 'strategy.entry("Short", strategy.short)', 'conditions': ['(bearCond)'], 'statement': 'strategy.entry("Short", strategy.short)'}]
    original_pine = '/*backtest\nstart: 2019-12-23 08:00:00\nend: 2024-11-11 00:00:00\nperiod: 1d\nbasePeriod: 1d\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("SAR Divergence Strategy", overlay=true)\n\n// --- Inputs ---\nlength = input.int(14, title="SAR Length", minval=1)\naccelerationFactor = input.float(0.02, title="Acceleration Factor", minval=0.01)\nmaximumFactor = input.float(0.2, title="Maximum Factor", minval=0.01)\n\n// --- SAR Calculation ---\nsar = ta.sar(length, accelerationFactor, maximumFactor)\n\n// --- Divergence Detection ---\nlookback = 5\n\n// Bullish Divergence\nbullCond = close[lookback] < close[lookback + 1] and sar[lookback] > sar[lookback + 1]\n\n// Bearish Divergence\nbearCond = close[lookback] > close[lookback + 1] and sar[lookback] < sar[lookback + 1]\n\n// --- Strategy Logic ---\nif (bullCond)\n    strategy.entry("Long", strategy.long)\n\nif (bearCond)\n    strategy.entry("Short", strategy.short)\n\n// --- Plotting ---\nplot(sar, color=color.blue, linewidth=2, title="Parabolic SAR")\n\nplotshape(bullCond, style=shape.triangleup, color=color.green, size=size.small, title="Bullish Divergence")\nplotshape(bearCond, style=shape.triangledown, color=color.red, size=size.small, title="Bearish Divergence")\n\n// --- Alerts ---\nalertcondition(bullCond, title="Bullish SAR Divergence", message="Bullish Divergence detected")\nalertcondition(bearCond, title="Bearish SAR Divergence", message="Bearish Divergence detected")'

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
