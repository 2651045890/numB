"""Source-faithful deep-assisted port of 形态反转交易策略Doji-Candlestick-Reversal-Trading-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_490dd0a5(PinePortBase, IStrategy):
    source_file = '形态反转交易策略Doji-Candlestick-Reversal-Trading-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'smaPeriod': 10, 'tolerance': 0.1, 'lookbackEnd': 2}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.entry', 'for ']
    source_fidelity_notes = []
    pine_assignments = [{'mode': '', 'name': 'smaPeriod', 'op': '=', 'expr': 'input(title="SMA Period", defval=10, minval=0)', 'conditions': []}, {'mode': '', 'name': 'tolerance', 'op': '=', 'expr': 'input(title="Tolerance", defval=0.1, minval=0)', 'conditions': []}, {'mode': '', 'name': 'lookbackEnd', 'op': '=', 'expr': 'input(title="End", defval=2, minval=0)', 'conditions': []}, {'mode': '', 'name': 'avg', 'op': '=', 'expr': 'sma(close, smaPeriod)', 'conditions': []}, {'mode': '', 'name': 'signal_long', 'op': '=', 'expr': 'bool(false)', 'conditions': []}, {'mode': '', 'name': 'signal_short', 'op': '=', 'expr': 'bool(false)', 'conditions': []}, {'mode': '', 'name': 'is_doji', 'op': '=', 'expr': '(abs(close[i] - open[i]) / (high[i] - low[i])) < tolerance', 'conditions': []}, {'mode': '', 'name': 'signal_long', 'op': ':=', 'expr': 'signal_long or ( is_doji and (close[i-1] <= high[i] or i == 1) and close[i-1] > high[i] and high[i] < avg and close > open )', 'conditions': []}, {'mode': '', 'name': 'signal_short', 'op': ':=', 'expr': 'signal_short or ( is_doji and (close[i-1] >= low[i] or i == 1) and close[i-1] < low[i] and low[i] > avg and close < open )', 'conditions': []}]
    pine_user_functions = []
    pine_controls = [{'indent': 0, 'statement': 'for i = 1 to lookbackEnd'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("LONG", strategy.long, when=signal_long)', 'conditions': [], 'statement': 'strategy.entry("LONG", strategy.long, when=signal_long)'}, {'kind': 'entry', 'call': 'strategy.entry("SHORT", strategy.short, when=signal_short)', 'conditions': [], 'statement': 'strategy.entry("SHORT", strategy.short, when=signal_short)'}]
    original_pine = '/*backtest\nstart: 2022-09-20 00:00:00\nend: 2023-09-26 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=4\nstrategy("Doji Reversal", overlay=true)\n\nsmaPeriod = input(title="SMA Period", defval=10, minval=0)\ntolerance = input(title="Tolerance", defval=0.1, minval=0)\n\nlookbackEnd = input(title="End", defval=2, minval=0)\n\navg = sma(close, smaPeriod)\nsignal_long = bool(false)\nsignal_short = bool(false)\n\nfor i = 1 to lookbackEnd\n    is_doji = (abs(close[i] - open[i]) / (high[i] - low[i])) < tolerance\n    signal_long := signal_long or ( is_doji and (close[i-1] <= high[i] or i == 1) and close[i-1] > high[i] and high[i] < avg and close > open )\n    signal_short := signal_short or ( is_doji and (close[i-1] >= low[i] or i == 1) and close[i-1] < low[i] and low[i] > avg and close < open )\n\nplotshape(signal_long, "LONG", style=shape.triangleup, size=size.normal)\nplotshape(signal_short, "SHORT", style=shape.triangledown, size=size.normal)\n\nstrategy.entry("LONG", strategy.long, when=signal_long)\nstrategy.entry("SHORT", strategy.short, when=signal_short)'

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
