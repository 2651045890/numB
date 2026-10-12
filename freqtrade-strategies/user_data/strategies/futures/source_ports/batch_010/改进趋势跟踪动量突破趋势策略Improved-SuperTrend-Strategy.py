"""Source-faithful deep-assisted port of 改进趋势跟踪动量突破趋势策略Improved-SuperTrend-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_ff5b0d2a(PinePortBase, IStrategy):
    source_file = '改进趋势跟踪动量突破趋势策略Improved-SuperTrend-Strategy.md'
    timeframe = '10m'
    can_short = True
    source_defaults = {'atr_length': 14, 'atr_multiplier': 1.5, 'filter_length': 5, 'stoch_length': 14, 'smooth_k': 3}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.entry', 'strategy.close', 'for ']
    source_fidelity_notes = []
    pine_assignments = [{'mode': '', 'name': 'atr_length', 'op': '=', 'expr': 'input(14, title="ATR Length")', 'conditions': []}, {'mode': '', 'name': 'atr_multiplier', 'op': '=', 'expr': 'input(1.5, title="ATR Multiplier")', 'conditions': []}, {'mode': '', 'name': 'filter_length', 'op': '=', 'expr': 'input(5, title="Filter Length")', 'conditions': []}, {'mode': '', 'name': 'stoch_length', 'op': '=', 'expr': 'input(14, title="Stochastic RSI Length")', 'conditions': []}, {'mode': '', 'name': 'smooth_k', 'op': '=', 'expr': 'input(3, title="Stochastic RSI %K Smoothing")', 'conditions': []}, {'mode': '', 'name': 'tr', 'op': '=', 'expr': 'ta.rma(ta.tr, atr_length)', 'conditions': []}, {'mode': '', 'name': 'atr', 'op': '=', 'expr': 'ta.rma(tr, atr_length)', 'conditions': []}, {'mode': '', 'name': 'upper_band', 'op': '=', 'expr': 'ta.sma(close, atr_length) + atr_multiplier * atr', 'conditions': []}, {'mode': '', 'name': 'lower_band', 'op': '=', 'expr': 'ta.sma(close, atr_length) - atr_multiplier * atr', 'conditions': []}, {'mode': '', 'name': 'is_uptrend', 'op': '=', 'expr': 'close > lower_band', 'conditions': []}, {'mode': '', 'name': 'is_downtrend', 'op': '=', 'expr': 'close < upper_band', 'conditions': []}, {'mode': '', 'name': 'super_trend', 'op': '=', 'expr': 'is_uptrend ? lower_band : na', 'conditions': []}, {'mode': '', 'name': 'super_trend', 'op': ':=', 'expr': 'is_downtrend ? upper_band : super_trend', 'conditions': []}, {'mode': '', 'name': 'filtered_super_trend', 'op': '=', 'expr': 'ta.sma(super_trend, filter_length)', 'conditions': []}, {'mode': '', 'name': 'rsi_value', 'op': '=', 'expr': 'ta.rsi(close, stoch_length)', 'conditions': []}, {'mode': '', 'name': 'stoch_rsi', 'op': '=', 'expr': 'ta.sma(ta.stoch(rsi_value, rsi_value, rsi_value, stoch_length), smooth_k)', 'conditions': []}, {'mode': '', 'name': 'long_condition', 'op': '=', 'expr': 'ta.crossover(close, filtered_super_trend) and is_uptrend and stoch_rsi < 80', 'conditions': []}, {'mode': '', 'name': 'short_condition', 'op': '=', 'expr': 'ta.crossunder(close, filtered_super_trend) and is_downtrend and stoch_rsi > 20', 'conditions': []}, {'mode': '', 'name': 'exit_long_condition', 'op': '=', 'expr': 'ta.crossunder(close, filtered_super_trend) and is_uptrend', 'conditions': []}, {'mode': '', 'name': 'exit_short_condition', 'op': '=', 'expr': 'ta.crossover(close, filtered_super_trend) and is_downtrend', 'conditions': []}]
    pine_user_functions = []
    pine_controls = []
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("Long", strategy.long, when=long_condition)', 'conditions': [], 'statement': 'strategy.entry("Long", strategy.long, when=long_condition)'}, {'kind': 'entry', 'call': 'strategy.entry("Short", strategy.short, when=short_condition)', 'conditions': [], 'statement': 'strategy.entry("Short", strategy.short, when=short_condition)'}, {'kind': 'close', 'call': 'strategy.close("Long", when=exit_long_condition)', 'conditions': [], 'statement': 'strategy.close("Long", when=exit_long_condition)'}, {'kind': 'close', 'call': 'strategy.close("Short", when=exit_short_condition)', 'conditions': [], 'statement': 'strategy.close("Short", when=exit_short_condition)'}]
    original_pine = '/*backtest\nstart: 2024-01-09 00:00:00\nend: 2024-01-16 00:00:00\nperiod: 10m\nbasePeriod: 1m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("Improved SuperTrend Strategy with Stochastic RSI", shorttitle="IST+StochRSI", overlay=true)\n\n// Input parameters\natr_length = input(14, title="ATR Length")\natr_multiplier = input(1.5, title="ATR Multiplier")\nfilter_length = input(5, title="Filter Length")\nstoch_length = input(14, title="Stochastic RSI Length")\nsmooth_k = input(3, title="Stochastic RSI %K Smoothing")\n\n// Calculate True Range (TR) and Average True Range (ATR)\ntr = ta.rma(ta.tr, atr_length)\natr = ta.rma(tr, atr_length)\n\n// Calculate SuperTrend\nupper_band = ta.sma(close, atr_length) + atr_multiplier * atr\nlower_band = ta.sma(close, atr_length) - atr_multiplier * atr\n\nis_uptrend = close > lower_band\nis_downtrend = close < upper_band\n\nsuper_trend = is_uptrend ? lower_band : na\nsuper_trend := is_downtrend ? upper_band : super_trend\n\n// Filter for reducing false signals\nfiltered_super_trend = ta.sma(super_trend, filter_length)\n\n// Calculate Stochastic RSI\nrsi_value = ta.rsi(close, stoch_length)\nstoch_rsi = ta.sma(ta.stoch(rsi_value, rsi_value, rsi_value, stoch_length), smooth_k)\n\n// Entry conditions\nlong_condition = ta.crossover(close, filtered_super_trend) and is_uptrend and stoch_rsi < 80\nshort_condition = ta.crossunder(close, filtered_super_trend) and is_downtrend and stoch_rsi > 20\n\n// Exit conditions\nexit_long_condition = ta.crossunder(close, filtered_super_trend) and is_uptrend\nexit_short_condition = ta.crossover(close, filtered_super_trend) and is_downtrend\n\n// Plot SuperTrend and filtered SuperTrend\nplot(super_trend, color=color.orange, title="SuperTrend", linewidth=2)\nplot(filtered_super_trend, color=color.blue, title="Filtered SuperTrend", linewidth=2)\n\n// Plot Buy and Sell signals\nplotshape(series=long_condition, title="Buy Signal", color=color.green, style=shape.triangleup, location=location.belowbar)\nplotshape(series=short_condition, title="Sell Signal", color=color.red, style=shape.triangledown, location=location.abovebar)\n\n// Output signals to the console for analysis\nplotchar(long_condition, "Long Signal", "▲", location.belowbar, color=color.green, size=size.small)\nplotchar(short_condition, "Short Signal", "▼", location.abovebar, color=color.red, size=size.small)\n\n// Strategy entry and exit\nstrategy.entry("Long", strategy.long, when=long_condition)\nstrategy.entry("Short", strategy.short, when=short_condition)\nstrategy.close("Long", when=exit_long_condition)\nstrategy.close("Short", when=exit_short_condition)'

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
