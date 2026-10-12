"""Source-faithful deep-assisted port of 神经均线交叉趋势跟踪策略结合EMA过滤系统-Neural-Moving-Average-Crossover-Trend-Following-Strategy-with-EMA-Filtering-System.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_1a9d8cb7(PinePortBase, IStrategy):
    source_file = '神经均线交叉趋势跟踪策略结合EMA过滤系统-Neural-Moving-Average-Crossover-Trend-Following-Strategy-with-EMA-Filtering-System.md'
    timeframe = '1h'
    can_short = True
    source_defaults = {}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.entry', 'strategy.close']
    source_fidelity_notes = []
    pine_assignments = [{'mode': '', 'name': 'sma9', 'op': '=', 'expr': 'ta.sma(close, 9)', 'conditions': []}, {'mode': '', 'name': 'sma15', 'op': '=', 'expr': 'ta.sma(close, 15)', 'conditions': []}, {'mode': '', 'name': 'ema200', 'op': '=', 'expr': 'ta.ema(close, 200)', 'conditions': []}, {'mode': '', 'name': 'bullish_crossover', 'op': '=', 'expr': 'ta.crossover(sma9, sma15) // Buy signal', 'conditions': []}, {'mode': '', 'name': 'bearish_crossover', 'op': '=', 'expr': 'ta.crossunder(sma9, sma15) // Sell signal', 'conditions': []}, {'mode': '', 'name': 'above_ema200', 'op': '=', 'expr': 'close > ema200', 'conditions': []}, {'mode': '', 'name': 'below_ema200', 'op': '=', 'expr': 'close < ema200', 'conditions': []}, {'mode': '', 'name': 'buy_signal', 'op': '=', 'expr': 'bullish_crossover and above_ema200', 'conditions': []}, {'mode': '', 'name': 'sell_signal', 'op': '=', 'expr': 'bearish_crossover and below_ema200', 'conditions': []}, {'mode': '', 'name': 'exit_long', 'op': '=', 'expr': 'bearish_crossover', 'conditions': []}, {'mode': '', 'name': 'exit_short', 'op': '=', 'expr': 'bullish_crossover', 'conditions': []}, {'mode': '', 'name': 'buy_reentry', 'op': '=', 'expr': 'ta.barssince(bullish_crossover) > 0 and above_ema200', 'conditions': []}, {'mode': '', 'name': 'sell_reentry', 'op': '=', 'expr': 'ta.barssince(bearish_crossover) > 0 and below_ema200', 'conditions': []}]
    pine_user_functions = []
    pine_controls = [{'indent': 0, 'statement': 'if buy_signal'}, {'indent': 0, 'statement': 'if sell_signal'}, {'indent': 0, 'statement': 'if exit_long'}, {'indent': 0, 'statement': 'if exit_short'}, {'indent': 0, 'statement': 'if buy_reentry'}, {'indent': 0, 'statement': 'if sell_reentry'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("Buy", strategy.long)', 'conditions': ['buy_signal'], 'statement': 'strategy.entry("Buy", strategy.long)'}, {'kind': 'entry', 'call': 'strategy.entry("Sell", strategy.short)', 'conditions': ['sell_signal'], 'statement': 'strategy.entry("Sell", strategy.short)'}, {'kind': 'close', 'call': 'strategy.close("Buy")', 'conditions': ['exit_long'], 'statement': 'strategy.close("Buy")'}, {'kind': 'close', 'call': 'strategy.close("Sell")', 'conditions': ['exit_short'], 'statement': 'strategy.close("Sell")'}, {'kind': 'entry', 'call': 'strategy.entry("Buy", strategy.long)', 'conditions': ['buy_reentry'], 'statement': 'strategy.entry("Buy", strategy.long)'}, {'kind': 'entry', 'call': 'strategy.entry("Sell", strategy.short)', 'conditions': ['sell_reentry'], 'statement': 'strategy.entry("Sell", strategy.short)'}]
    original_pine = '/*backtest\nstart: 2024-02-19 00:00:00\nend: 2025-02-17 00:00:00\nperiod: 1h\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n\n//@version=5\nstrategy("SMA Crossover with EMA Filter", overlay=true)\n\n// Define indicators\nsma9 = ta.sma(close, 9)\nsma15 = ta.sma(close, 15)\nema200 = ta.ema(close, 200)\n\n// Crossover conditions\nbullish_crossover = ta.crossover(sma9, sma15) // Buy signal\nbearish_crossover = ta.crossunder(sma9, sma15) // Sell signal\n\n// Filters\nabove_ema200 = close > ema200\nbelow_ema200 = close < ema200\n\n// Buy condition (only above 200 EMA)\nbuy_signal = bullish_crossover and above_ema200\nif buy_signal\n    strategy.entry("Buy", strategy.long)\n\n// Sell condition (only below 200 EMA)\nsell_signal = bearish_crossover and below_ema200\nif sell_signal\n    strategy.entry("Sell", strategy.short)\n\n// Exit condition if the signal reverses\nexit_long = bearish_crossover\nexit_short = bullish_crossover\nif exit_long\n    strategy.close("Buy")\nif exit_short\n    strategy.close("Sell")\n\n// Re-entry condition when price crosses EMA 200 after a prior crossover\nbuy_reentry = ta.barssince(bullish_crossover) > 0 and above_ema200\nsell_reentry = ta.barssince(bearish_crossover) > 0 and below_ema200\nif buy_reentry\n    strategy.entry("Buy", strategy.long)\nif sell_reentry\n    strategy.entry("Sell", strategy.short)\n\n// Plot indicators\nplot(sma9, color=color.blue, title="SMA 9")\nplot(sma15, color=color.red, title="SMA 15")\nplot(ema200, color=color.orange, title="EMA 200")'

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
