"""Source-faithful deep-assisted port of 抛物线SAR趋势跟踪策略-60Parabolic-SAR-Trend-Tracking-Strategy-60.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_0fc8639b(PinePortBase, IStrategy):
    source_file = '抛物线SAR趋势跟踪策略-60Parabolic-SAR-Trend-Tracking-Strategy-60.md'
    timeframe = '1m'
    can_short = True
    source_defaults = {'start': 0.02, 'increment': 0.02, 'maximum': 0.2, 'long_win': 0.1, 'short_win': 2, 'lose_pct': 0.5, 'win_pct_long': 0.2, 'win_pct_short': 0.1, 'start1': 0.02, 'increment1': 0.02, 'maximum1': 0.2}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 20.0
    source_pyramiding = 5
    source_initial_capital = 500.0
    source_commission_percent = 0.08
    source_features = ['request.security', 'strategy.entry', 'strategy.close', 'strategy.position_size', 'for ']
    source_fidelity_notes = ['Uses request.security / multi-timeframe context; exact parity depends on HTF resampling, gaps and lookahead semantics.', 'Reads broker/strategy state; signals depend on fill timing and cannot be reduced to indicator-only booleans without changing behavior.']
    pine_assignments = [{'mode': '', 'name': 'start', 'op': '=', 'expr': 'input(0.02, title="Start Value")', 'conditions': []}, {'mode': '', 'name': 'increment', 'op': '=', 'expr': 'input(0.02, title="Increment Value")', 'conditions': []}, {'mode': '', 'name': 'maximum', 'op': '=', 'expr': 'input(0.2, title="Maximum Value")', 'conditions': []}, {'mode': '', 'name': 'long_win', 'op': '=', 'expr': 'input(0.1,title = "Preceding Increase for Long (%)")/100', 'conditions': []}, {'mode': '', 'name': 'short_win', 'op': '=', 'expr': 'input(2,title = "Preceding Decrease for Short (%)")/100', 'conditions': []}, {'mode': '', 'name': 'lose_pct', 'op': '=', 'expr': 'input (0.5, title="Stop Loss Percentage")', 'conditions': []}, {'mode': '', 'name': 'win_pct_long', 'op': '=', 'expr': 'input(0.2,title = "Take Profit for Long Positions")', 'conditions': []}, {'mode': '', 'name': 'win_pct_short', 'op': '=', 'expr': 'input(0.1,title = "Take Profit for Short Positions")', 'conditions': []}, {'mode': '', 'name': 'start1', 'op': '=', 'expr': 'input(0.02, title="Start Value (1H)")', 'conditions': []}, {'mode': '', 'name': 'increment1', 'op': '=', 'expr': 'input(0.02, title="Increment Value (1H)")', 'conditions': []}, {'mode': '', 'name': 'maximum1', 'op': '=', 'expr': 'input(0.2, title="Maximum Value (1H)")', 'conditions': []}, {'mode': '', 'name': 'sarValue', 'op': '=', 'expr': 'ta.sar(start, increment, maximum)', 'conditions': []}, {'mode': '', 'name': 'longSignal', 'op': '=', 'expr': 'ta.crossover(close, sarValue)', 'conditions': []}, {'mode': '', 'name': 'shortSignal', 'op': '=', 'expr': 'ta.crossunder(close, sarValue)', 'conditions': []}, {'mode': '', 'name': 'sarValue_1h', 'op': '=', 'expr': 'request.security(syminfo.tickerid, "5", ta.sar(start1, increment1, maximum1)[1])', 'conditions': []}, {'mode': '', 'name': 'longSignal1', 'op': '=', 'expr': 'close > sarValue_1h', 'conditions': []}, {'mode': '', 'name': 'shortSignal1', 'op': '=', 'expr': 'close < sarValue_1h', 'conditions': []}]
    pine_user_functions = []
    pine_controls = [{'indent': 0, 'statement': 'if longSignal and (close - open)/open > long_win and longSignal1'}, {'indent': 0, 'statement': 'if shortSignal and (open - close)/open > short_win and shortSignal1'}, {'indent': 0, 'statement': 'if strategy.position_size > 0 and shortSignal and (close - strategy.position_avg_price)/strategy.position_avg_price > win_pct_long'}, {'indent': 0, 'statement': 'if strategy.position_size < 0 and longSignal and (strategy.position_avg_price - close)/strategy.position_avg_price > win_pct_short'}, {'indent': 0, 'statement': 'if strategy.position_size > 0 and (strategy.position_avg_price - close)/strategy.position_avg_price > lose_pct'}, {'indent': 0, 'statement': 'if strategy.position_size < 0 and (close - strategy.position_avg_price)/strategy.position_avg_price > lose_pct'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("Long", strategy.long)', 'conditions': ['longSignal and (close - open)/open > long_win and longSignal1'], 'statement': 'strategy.entry("Long", strategy.long)'}, {'kind': 'entry', 'call': 'strategy.entry("Short", strategy.short)', 'conditions': ['shortSignal and (open - close)/open > short_win and shortSignal1'], 'statement': 'strategy.entry("Short", strategy.short)'}, {'kind': 'close_all', 'call': 'strategy.close_all("Take Profit")', 'conditions': ['strategy.position_size > 0 and shortSignal and (close - strategy.position_avg_price)/strategy.position_avg_price > win_pct_long'], 'statement': 'strategy.close_all("Take Profit")'}, {'kind': 'close_all', 'call': 'strategy.close_all("Take Profit")', 'conditions': ['strategy.position_size < 0 and longSignal and (strategy.position_avg_price - close)/strategy.position_avg_price > win_pct_short'], 'statement': 'strategy.close_all("Take Profit")'}, {'kind': 'close_all', 'call': 'strategy.close_all("Stop Loss")', 'conditions': ['strategy.position_size > 0 and (strategy.position_avg_price - close)/strategy.position_avg_price > lose_pct'], 'statement': 'strategy.close_all("Stop Loss")'}, {'kind': 'close_all', 'call': 'strategy.close_all("Stop Loss")', 'conditions': ['strategy.position_size < 0 and (close - strategy.position_avg_price)/strategy.position_avg_price > lose_pct'], 'statement': 'strategy.close_all("Stop Loss")'}]
    original_pine = '/*backtest\nstart: 2024-02-29 00:00:00\nend: 2024-03-07 00:00:00\nperiod: 1m\nbasePeriod: 1m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("SAR Trend 6.0", default_qty_type = strategy.percent_of_equity, default_qty_value =20, initial_capital=500, commission_type=strategy.commission.percent, commission_value=0.08, pyramiding=5 )\n\n// Parabolic SAR Parameters\nstart = input(0.02, title="Start Value")\nincrement = input(0.02, title="Increment Value")\nmaximum = input(0.2, title="Maximum Value")\nlong_win=input(0.1,title = "Preceding Increase for Long (%)")/100\nshort_win=input(2,title = "Preceding Decrease for Short (%)")/100\nlose_pct=input (0.5, title="Stop Loss Percentage")\nwin_pct_long=input(0.2,title = "Take Profit for Long Positions")\nwin_pct_short=input(0.1,title = "Take Profit for Short Positions")\nstart1 = input(0.02, title="Start Value (1H)")\nincrement1 = input(0.02, title="Increment Value (1H)")\nmaximum1 = input(0.2, title="Maximum Value (1H)")\n\n// Calculating Parabolic SAR\nsarValue = ta.sar(start, increment, maximum)\n\n// Generating Trading Signals\nlongSignal = ta.crossover(close, sarValue)\nshortSignal = ta.crossunder(close, sarValue)\n\n// Get Parabolic SAR value for 1-hour time frame\nsarValue_1h = request.security(syminfo.tickerid, "5", ta.sar(start1, increment1, maximum1)[1])\n\n// Generating Trading Signals\nlongSignal1 = close > sarValue_1h\nshortSignal1 = close < sarValue_1h\n\nif longSignal and (close - open)/open > long_win and longSignal1 \n    strategy.entry("Long", strategy.long)\nif shortSignal and (open - close)/open > short_win and shortSignal1 \n    strategy.entry("Short", strategy.short)\n\nif strategy.position_size > 0 and shortSignal and (close - strategy.position_avg_price)/strategy.position_avg_price > win_pct_long\n    strategy.close_all("Take Profit")\n\nif strategy.position_size < 0 and longSignal and (strategy.position_avg_price - close)/strategy.position_avg_price > win_pct_short\n    strategy.close_all("Take Profit")\n\nif strategy.position_size > 0 and (strategy.position_avg_price - close)/strategy.position_avg_price > lose_pct\n    strategy.close_all("Stop Loss")\n\nif strategy.position_size < 0 and (close - strategy.position_avg_price)/strategy.position_avg_price > lose_pct\n    strategy.close_all("Stop Loss")'

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
