"""Source-faithful deep-assisted port of 改进型双重-EMA-回撤突破交易策略-Enhanced-Dual-EMA-Pullback-Breakout-Trading-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_7ed486b0(PinePortBase, IStrategy):
    source_file = '改进型双重-EMA-回撤突破交易策略-Enhanced-Dual-EMA-Pullback-Breakout-Trading-Strategy.md'
    timeframe = '1d'
    can_short = False
    source_defaults = {'emaLength': 8}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.entry', 'strategy.position_size', 'var ', 'for ', '=>']
    source_fidelity_notes = ['Uses persistent Pine state (var/varip); state is order-dependent and must be evaluated bar-by-bar, not replaced by a vectorized fill-forward approximation.', 'Reads broker/strategy state; signals depend on fill timing and cannot be reduced to indicator-only booleans without changing behavior.']
    pine_assignments = [{'mode': '', 'name': 'emaLength', 'op': '=', 'expr': 'input(8, title="EMA Length")', 'conditions': []}, {'mode': '', 'name': 'ema', 'op': '=', 'expr': 'ta.ema(close, emaLength)', 'conditions': []}, {'mode': 'var', 'name': 'prevSwingHigh', 'op': '=', 'expr': 'na', 'conditions': []}, {'mode': 'var', 'name': 'waitingForPullback', 'op': '=', 'expr': 'false', 'conditions': []}, {'mode': 'var', 'name': 'waitingForBreakout', 'op': '=', 'expr': 'false', 'conditions': []}, {'mode': 'var', 'name': 'readyToTrigger', 'op': '=', 'expr': 'false', 'conditions': []}, {'mode': '', 'name': 'prevSwingHigh', 'op': ':=', 'expr': 'high[1]', 'conditions': ['swingHigh()']}, {'mode': '', 'name': 'waitingForPullback', 'op': ':=', 'expr': 'true', 'conditions': ['swingHigh()']}, {'mode': '', 'name': 'waitingForBreakout', 'op': ':=', 'expr': 'false', 'conditions': ['swingHigh()']}, {'mode': '', 'name': 'readyToTrigger', 'op': ':=', 'expr': 'false', 'conditions': ['swingHigh()']}, {'mode': '', 'name': 'waitingForPullback', 'op': ':=', 'expr': 'false', 'conditions': ['waitingForPullback and low <= ema']}, {'mode': '', 'name': 'waitingForBreakout', 'op': ':=', 'expr': 'true', 'conditions': ['waitingForPullback and low <= ema']}, {'mode': '', 'name': 'waitingForBreakout', 'op': ':=', 'expr': 'false', 'conditions': ['waitingForBreakout and high > prevSwingHigh']}, {'mode': '', 'name': 'readyToTrigger', 'op': ':=', 'expr': 'true', 'conditions': ['waitingForBreakout and high > prevSwingHigh']}, {'mode': '', 'name': 'readyToTrigger', 'op': ':=', 'expr': 'false', 'conditions': ['readyToTrigger and low <= ema']}]
    pine_user_functions = [{'name': 'swingHigh', 'args': '', 'body': ''}]
    pine_controls = [{'indent': 0, 'statement': 'if swingHigh()'}, {'indent': 0, 'statement': 'if waitingForPullback and low <= ema'}, {'indent': 0, 'statement': 'if waitingForBreakout and high > prevSwingHigh'}, {'indent': 0, 'statement': 'if readyToTrigger and low <= ema'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("Long", strategy.long)', 'conditions': ['readyToTrigger and low <= ema'], 'statement': 'strategy.entry("Long", strategy.long)'}]
    original_pine = '/*backtest\nstart: 2023-07-24 00:00:00\nend: 2024-07-29 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("8 EMA Pullback Strategy - Refined", overlay=true)\n\n// Input parameters\nemaLength = input(8, title="EMA Length")\n\n// Calculate EMA\nema = ta.ema(close, emaLength)\n\n// Function to detect a swing high\nswingHigh() =>\n    high[2] < high[1] and high[1] > high[0]\n\n// Variables to track state\nvar float prevSwingHigh = na\nvar bool waitingForPullback = false\nvar bool waitingForBreakout = false\nvar bool readyToTrigger = false\n\n// Detect new swing high\nif swingHigh()\n    prevSwingHigh := high[1]\n    waitingForPullback := true\n    waitingForBreakout := false\n    readyToTrigger := false\n\n// Check for pullback to EMA\nif waitingForPullback and low <= ema\n    waitingForPullback := false\n    waitingForBreakout := true\n\n// Check for breakout above previous swing high\nif waitingForBreakout and high > prevSwingHigh\n    waitingForBreakout := false\n    readyToTrigger := true\n\n// Check for pullback to EMA after breakout (entry condition)\nif readyToTrigger and low <= ema\n    strategy.entry("Long", strategy.long)\n    readyToTrigger := false\n\n// Plot EMA\nplot(ema, color=color.blue, title="8 EMA")\n\n// Plot entry points\nplotshape(strategy.position_size > 0, title="Entry", location=location.belowbar, color=color.green, style=shape.triangleup, size=size.small)'

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
