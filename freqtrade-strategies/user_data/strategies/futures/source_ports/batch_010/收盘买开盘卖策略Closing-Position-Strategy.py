"""Source-faithful deep-assisted port of 收盘买开盘卖策略Closing-Position-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_ab58fd99(PinePortBase, IStrategy):
    source_file = '收盘买开盘卖策略Closing-Position-Strategy.md'
    timeframe = '1h'
    can_short = True
    source_defaults = {}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['request.security', 'strategy.entry', 'strategy.close', 'strategy.position_size']
    source_fidelity_notes = ['Uses request.security / multi-timeframe context; exact parity depends on HTF resampling, gaps and lookahead semantics.', 'Reads broker/strategy state; signals depend on fill timing and cannot be reduced to indicator-only booleans without changing behavior.']
    pine_assignments = [{'mode': '', 'name': 'daily_open', 'op': '=', 'expr': 'request.security(syminfo.tickerid, "D", open)', 'conditions': []}, {'mode': '', 'name': 'daily_close', 'op': '=', 'expr': 'request.security(syminfo.tickerid, "D", close)', 'conditions': []}, {'mode': '', 'name': 'sma200', 'op': '=', 'expr': 'ta.sma(daily_close, 200)', 'conditions': []}, {'mode': '', 'name': 'end_of_day', 'op': '=', 'expr': '(hour == 20) and (minute == 0) // Assuming the end of the regular trading hours is 20:00', 'conditions': []}, {'mode': '', 'name': 'start_of_day', 'op': '=', 'expr': '(hour == 9) and (minute == 30) // Assuming the start of the trading session is 09:30', 'conditions': []}, {'mode': '', 'name': 'long_condition', 'op': '=', 'expr': 'end_of_day and (daily_close > sma200)', 'conditions': []}, {'mode': '', 'name': 'short_condition', 'op': '=', 'expr': 'end_of_day and (daily_close < sma200)', 'conditions': []}]
    pine_user_functions = []
    pine_controls = [{'indent': 0, 'statement': 'if (long_condition)'}, {'indent': 0, 'statement': 'if (short_condition)'}, {'indent': 0, 'statement': 'if (strategy.position_size > 0 and start_of_day) // If we are long, sell at the open of the session'}, {'indent': 0, 'statement': 'if (strategy.position_size < 0 and start_of_day) // If we are short, buy at the open of the session'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("Long", strategy.long)', 'conditions': ['(long_condition)'], 'statement': 'strategy.entry("Long", strategy.long)'}, {'kind': 'entry', 'call': 'strategy.entry("Short", strategy.short)', 'conditions': ['(short_condition)'], 'statement': 'strategy.entry("Short", strategy.short)'}, {'kind': 'close', 'call': 'strategy.close("Long")', 'conditions': ['(strategy.position_size > 0 and start_of_day) // If we are long, sell at the open of the session'], 'statement': 'strategy.close("Long")'}, {'kind': 'close', 'call': 'strategy.close("Short")', 'conditions': ['(strategy.position_size < 0 and start_of_day) // If we are short, buy at the open of the session'], 'statement': 'strategy.close("Short")'}]
    original_pine = '/*backtest\nstart: 2023-10-10 00:00:00\nend: 2023-11-09 00:00:00\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This source code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © Youngmoneyinvestments\n\n//@version=5\nstrategy("End of Day Trading Strategy", overlay=true)\n\n// Get the daily open, high, low, and close prices\ndaily_open = request.security(syminfo.tickerid, "D", open)\ndaily_close = request.security(syminfo.tickerid, "D", close)\n\n// Calculate the 200 period SMA on daily close\nsma200 = ta.sma(daily_close, 200)\n\n// Define the entry and exit conditions\nend_of_day = (hour == 20) and (minute == 0) // Assuming the end of the regular trading hours is 20:00\nstart_of_day = (hour == 9) and (minute == 30) // Assuming the start of the trading session is 09:30\n\nlong_condition = end_of_day and (daily_close > sma200)\nshort_condition = end_of_day and (daily_close < sma200)\n\n// Execute the strategy logic\nif (long_condition)\n    strategy.entry("Long", strategy.long)\nif (short_condition)\n    strategy.entry("Short", strategy.short)\n\n// Exit conditions\nif (strategy.position_size > 0 and start_of_day) // If we are long, sell at the open of the session\n    strategy.close("Long")\nif (strategy.position_size < 0 and start_of_day) // If we are short, buy at the open of the session\n    strategy.close("Short")\n\n// Plot the SMA on the chart\nplot(sma200, "200 SMA", color=color.blue)'

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
