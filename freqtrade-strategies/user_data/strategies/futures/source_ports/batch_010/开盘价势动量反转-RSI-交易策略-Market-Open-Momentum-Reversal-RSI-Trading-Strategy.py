"""Source-faithful deep-assisted port of 开盘价势动量反转-RSI-交易策略-Market-Open-Momentum-Reversal-RSI-Trading-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_deb0d02a(PinePortBase, IStrategy):
    source_file = '开盘价势动量反转-RSI-交易策略-Market-Open-Momentum-Reversal-RSI-Trading-Strategy.md'
    timeframe = '7m'
    can_short = True
    source_defaults = {}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.entry', 'strategy.close', 'strategy.position_size', 'var ', 'for ']
    source_fidelity_notes = ['Uses persistent Pine state (var/varip); state is order-dependent and must be evaluated bar-by-bar, not replaced by a vectorized fill-forward approximation.', 'Reads broker/strategy state; signals depend on fill timing and cannot be reduced to indicator-only booleans without changing behavior.']
    pine_assignments = [{'mode': '', 'name': 'session_start', 'op': '=', 'expr': 'timestamp("GMT-4", year, month, dayofmonth, 09, 30, 00)', 'conditions': []}, {'mode': '', 'name': 'initial_window', 'op': '=', 'expr': '90 * 1000 // in milliseconds', 'conditions': []}, {'mode': '', 'name': 'is_in_initial_window', 'op': '=', 'expr': '(time - session_start) <= initial_window and (time - session_start) >= 0', 'conditions': []}, {'mode': 'var', 'name': 'open_price', 'op': '=', 'expr': '0.0', 'conditions': []}, {'mode': 'var', 'name': 'direction', 'op': '=', 'expr': '0.0', 'conditions': []}, {'mode': 'var', 'name': 'direction_set', 'op': '=', 'expr': 'false', 'conditions': []}, {'mode': '', 'name': 'open_price', 'op': ':=', 'expr': 'close', 'conditions': ['(time == session_start)']}, {'mode': '', 'name': 'direction_set', 'op': ':=', 'expr': 'false', 'conditions': ['(time == session_start)']}, {'mode': '', 'name': 'direction', 'op': ':=', 'expr': 'close > open_price ? 1.0 : close < open_price ? -1.0 : 0.0', 'conditions': ['(is_in_initial_window[1] and not is_in_initial_window and not direction_set)']}, {'mode': '', 'name': 'direction_set', 'op': ':=', 'expr': 'true', 'conditions': ['(is_in_initial_window[1] and not is_in_initial_window and not direction_set)']}, {'mode': '', 'name': 'direction_set', 'op': ':=', 'expr': 'false', 'conditions': ['(time == session_start)']}, {'mode': '', 'name': 'rsi_length', 'op': '=', 'expr': '14', 'conditions': []}, {'mode': '', 'name': 'rsi_overbought', 'op': '=', 'expr': '70', 'conditions': []}, {'mode': '', 'name': 'rsi_oversold', 'op': '=', 'expr': '30', 'conditions': []}, {'mode': '', 'name': 'rsi', 'op': '=', 'expr': 'ta.rsi(close, rsi_length)', 'conditions': []}, {'mode': '', 'name': 'reversal_signal', 'op': '=', 'expr': '(direction == 1.0 and rsi >= rsi_overbought) or (direction == -1.0 and rsi <= rsi_oversold)', 'conditions': []}, {'mode': '', 'name': 'max_hold_time', 'op': '=', 'expr': '600 * 1000 // in milliseconds', 'conditions': []}, {'mode': '', 'name': 'is_within_hold_time', 'op': '=', 'expr': '(time - (session_start + initial_window)) <= max_hold_time and (time - (session_start + initial_window)) >= 0', 'conditions': []}]
    pine_user_functions = []
    pine_controls = [{'indent': 0, 'statement': 'if (time == session_start)'}, {'indent': 0, 'statement': 'if (is_in_initial_window[1] and not is_in_initial_window and not direction_set)'}, {'indent': 0, 'statement': 'if (time == session_start)'}, {'indent': 0, 'statement': 'if (direction_set and direction != 0.0 and is_within_hold_time and not reversal_signal)'}, {'indent': 4, 'statement': 'if (direction == 1.0)'}, {'indent': 4, 'statement': 'else if (direction == -1.0)'}, {'indent': 0, 'statement': 'if (reversal_signal or not is_within_hold_time)'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("BuyCall", strategy.long)', 'conditions': ['(direction_set and direction != 0.0 and is_within_hold_time and not reversal_signal)', '(direction == 1.0)'], 'statement': 'strategy.entry("BuyCall", strategy.long)'}, {'kind': 'entry', 'call': 'strategy.entry("BuyPut", strategy.short)', 'conditions': ['(direction_set and direction != 0.0 and is_within_hold_time and not reversal_signal)', '(direction == -1.0)'], 'statement': 'strategy.entry("BuyPut", strategy.short)'}, {'kind': 'close_all', 'call': 'strategy.close_all("Exit")', 'conditions': ['(reversal_signal or not is_within_hold_time)'], 'statement': 'strategy.close_all("Exit")'}]
    original_pine = '/*backtest\nstart: 2025-04-13 00:00:00\nend: 2025-04-20 00:00:00\nperiod: 7m\nbasePeriod: 7m\nexchanges: [{"eid":"Futures_Binance","currency":"TRX_USD"}]\n*/\n\n// @version=5\nstrategy("Market Open Options Strategy", overlay=true)\n\n// Define trading session start (e.g., 9:30 AM for US markets)\nsession_start = timestamp("GMT-4", year, month, dayofmonth, 09, 30, 00)\n\n// Time window for initial direction (90 seconds = 1.5 minutes)\ninitial_window = 90 * 1000 // in milliseconds\nis_in_initial_window = (time - session_start) <= initial_window and (time - session_start) >= 0\n\n// Variables to track open price and direction\nvar float open_price = 0.0\nvar float direction = 0.0\nvar bool direction_set = false\n\n// Capture open price at session start\nif (time == session_start)\n    open_price := close\n    direction_set := false\n\n// Determine direction after 90 seconds\nif (is_in_initial_window[1] and not is_in_initial_window and not direction_set)\n    direction := close > open_price ? 1.0 : close < open_price ? -1.0 : 0.0\n    direction_set := true\n\n// Reset direction_set at the start of a new day\nif (time == session_start)\n    direction_set := false\n\n// Reversal indicator (RSI-based)\nrsi_length = 14\nrsi_overbought = 70\nrsi_oversold = 30\nrsi = ta.rsi(close, rsi_length)\nreversal_signal = (direction == 1.0 and rsi >= rsi_overbought) or (direction == -1.0 and rsi <= rsi_oversold)\n\n// Time-based exit (10 minutes = 600 seconds)\nmax_hold_time = 600 * 1000 // in milliseconds\nis_within_hold_time = (time - (session_start + initial_window)) <= max_hold_time and (time - (session_start + initial_window)) >= 0\n\n// Strategy logic\nif (direction_set and direction != 0.0 and is_within_hold_time and not reversal_signal)\n    if (direction == 1.0)\n        strategy.entry("BuyCall", strategy.long)\n    else if (direction == -1.0)\n        strategy.entry("BuyPut", strategy.short)\n\n// Exit conditions: Reversal or time-based\nif (reversal_signal or not is_within_hold_time)\n    strategy.close_all("Exit")\n\n// Plot signals\nplotshape(direction == 1.0 and strategy.position_size == 0 and direction_set ? close : na, "Buy Call", shape.triangleup, location.belowbar, color.green, size=size.small)\nplotshape(direction == -1.0 and strategy.position_size == 0 and direction_set ? close : na, "Buy Put", shape.triangledown, location.abovebar, color.red, size=size.small)'

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
