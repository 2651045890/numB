"""Source-faithful deep-assisted port of 机器学习启发的双均线RSI交易策略-Machine-Learning-Inspired-Dual-Moving-Average-RSI-Trading-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_84db6f4c(PinePortBase, IStrategy):
    source_file = '机器学习启发的双均线RSI交易策略-Machine-Learning-Inspired-Dual-Moving-Average-RSI-Trading-Strategy.md'
    timeframe = '1h'
    can_short = True
    source_defaults = {'length_fast': 10, 'length_slow': 50, 'rsi_length': 14, 'rsi_overbought': 70, 'rsi_oversold': 30}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.entry', 'strategy.close', 'for ']
    source_fidelity_notes = []
    pine_assignments = [{'mode': '', 'name': 'length_fast', 'op': '=', 'expr': 'input.int(10, minval=1, title="Fast MA Length")', 'conditions': []}, {'mode': '', 'name': 'length_slow', 'op': '=', 'expr': 'input.int(50, minval=1, title="Slow MA Length")', 'conditions': []}, {'mode': '', 'name': 'rsi_length', 'op': '=', 'expr': 'input.int(14, minval=1, title="RSI Length")', 'conditions': []}, {'mode': '', 'name': 'rsi_overbought', 'op': '=', 'expr': 'input.int(70, minval=1, title="RSI Overbought Level")', 'conditions': []}, {'mode': '', 'name': 'rsi_oversold', 'op': '=', 'expr': 'input.int(30, minval=1, title="RSI Oversold Level")', 'conditions': []}, {'mode': '', 'name': 'ma_fast', 'op': '=', 'expr': 'ta.sma(close, length_fast)', 'conditions': []}, {'mode': '', 'name': 'ma_slow', 'op': '=', 'expr': 'ta.sma(close, length_slow)', 'conditions': []}, {'mode': '', 'name': 'rsi', 'op': '=', 'expr': 'ta.rsi(close, rsi_length)', 'conditions': []}, {'mode': '', 'name': 'long_condition', 'op': '=', 'expr': 'ta.crossover(ma_fast, ma_slow) and rsi < rsi_overbought', 'conditions': []}, {'mode': '', 'name': 'short_condition', 'op': '=', 'expr': 'ta.crossunder(ma_fast, ma_slow) and rsi > rsi_oversold', 'conditions': []}]
    pine_user_functions = []
    pine_controls = [{'indent': 0, 'statement': 'if (long_condition)'}, {'indent': 0, 'statement': 'if (short_condition)'}, {'indent': 0, 'statement': 'if (rsi > rsi_overbought)'}, {'indent': 0, 'statement': 'if (rsi < rsi_oversold)'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("Long", strategy.long)', 'conditions': ['(long_condition)'], 'statement': 'strategy.entry("Long", strategy.long)'}, {'kind': 'entry', 'call': 'strategy.entry("Short", strategy.short)', 'conditions': ['(short_condition)'], 'statement': 'strategy.entry("Short", strategy.short)'}, {'kind': 'close', 'call': 'strategy.close("Long")', 'conditions': ['(rsi > rsi_overbought)'], 'statement': 'strategy.close("Long")'}, {'kind': 'close', 'call': 'strategy.close("Short")', 'conditions': ['(rsi < rsi_oversold)'], 'statement': 'strategy.close("Short")'}]
    original_pine = '/*backtest\nstart: 2024-05-01 00:00:00\nend: 2024-05-31 23:59:59\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("ML Inspired Strategy for Nifty50", overlay=true)\n\n// Define the input parameters for the strategy\nlength_fast = input.int(10, minval=1, title="Fast MA Length")\nlength_slow = input.int(50, minval=1, title="Slow MA Length")\nrsi_length = input.int(14, minval=1, title="RSI Length")\nrsi_overbought = input.int(70, minval=1, title="RSI Overbought Level")\nrsi_oversold = input.int(30, minval=1, title="RSI Oversold Level")\n\n// Calculate the moving averages\nma_fast = ta.sma(close, length_fast)\nma_slow = ta.sma(close, length_slow)\n\n// Calculate the RSI\nrsi = ta.rsi(close, rsi_length)\n\n// Define the conditions for long and short entries\nlong_condition = ta.crossover(ma_fast, ma_slow) and rsi < rsi_overbought\nshort_condition = ta.crossunder(ma_fast, ma_slow) and rsi > rsi_oversold\n\n// Plot the moving averages\nplot(ma_fast, title="Fast MA", color=color.blue)\nplot(ma_slow, title="Slow MA", color=color.red)\n\n// Add strategy logic for entering and exiting trades\nif (long_condition)\n    strategy.entry("Long", strategy.long)\nif (short_condition)\n    strategy.entry("Short", strategy.short)\n\n// Plot buy/sell signals on the chart\nplotshape(series=long_condition, title="Buy Signal", location=location.belowbar, color=color.green, style=shape.labelup, text="BUY")\nplotshape(series=short_condition, title="Sell Signal", location=location.abovebar, color=color.red, style=shape.labeldown, text="SELL")\n\n// Add exit conditions\nif (rsi > rsi_overbought)\n    strategy.close("Long")\nif (rsi < rsi_oversold)\n    strategy.close("Short")'

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
