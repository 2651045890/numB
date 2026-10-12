"""Source-faithful deep-assisted port of 布林线与StochRSI动量策略Bollinger-Bands-and-StochRSI-Momentum-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_a2def256(PinePortBase, IStrategy):
    source_file = '布林线与StochRSI动量策略Bollinger-Bands-and-StochRSI-Momentum-Strategy.md'
    timeframe = '1m'
    can_short = True
    source_defaults = {'bollinger_length': 20, 'bollinger_dev': 2, 'stoch_length': 14, 'k_period': 3, 'd_period': 3}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.entry']
    source_fidelity_notes = []
    pine_assignments = [{'mode': '', 'name': 'bollinger_length', 'op': '=', 'expr': 'input.int(20, title="Bollinger Bands Length")', 'conditions': []}, {'mode': '', 'name': 'bollinger_dev', 'op': '=', 'expr': 'input.float(2, title="Bollinger Bands Deviation")', 'conditions': []}, {'mode': '', 'name': 'sma', 'op': '=', 'expr': 'ta.sma(close, bollinger_length)', 'conditions': []}, {'mode': '', 'name': 'dev', 'op': '=', 'expr': 'bollinger_dev * ta.stdev(close, bollinger_length)', 'conditions': []}, {'mode': '', 'name': 'upper_band', 'op': '=', 'expr': 'sma + dev', 'conditions': []}, {'mode': '', 'name': 'lower_band', 'op': '=', 'expr': 'sma - dev', 'conditions': []}, {'mode': '', 'name': 'stoch_length', 'op': '=', 'expr': 'input.int(14, title="StochRSI Length")', 'conditions': []}, {'mode': '', 'name': 'k_period', 'op': '=', 'expr': 'input.int(3, title="K Period")', 'conditions': []}, {'mode': '', 'name': 'd_period', 'op': '=', 'expr': 'input.int(3, title="D Period")', 'conditions': []}, {'mode': '', 'name': 'rsi', 'op': '=', 'expr': 'ta.rsi(close, stoch_length)', 'conditions': []}, {'mode': '', 'name': 'k', 'op': '=', 'expr': 'ta.sma(ta.stoch(rsi, rsi, rsi, k_period), k_period)', 'conditions': []}, {'mode': '', 'name': 'd', 'op': '=', 'expr': 'ta.sma(k, d_period)', 'conditions': []}, {'mode': '', 'name': 'buy_condition', 'op': '=', 'expr': 'ta.crossover(k, d) and close < lower_band', 'conditions': []}, {'mode': '', 'name': 'sell_condition', 'op': '=', 'expr': 'ta.crossunder(k, d) and close > upper_band', 'conditions': []}]
    pine_user_functions = []
    pine_controls = [{'indent': 0, 'statement': 'if (buy_condition)'}, {'indent': 0, 'statement': 'if (sell_condition)'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("Buy", strategy.long)', 'conditions': ['(buy_condition)'], 'statement': 'strategy.entry("Buy", strategy.long)'}, {'kind': 'entry', 'call': 'strategy.entry("Sell", strategy.short)', 'conditions': ['(sell_condition)'], 'statement': 'strategy.entry("Sell", strategy.short)'}]
    original_pine = '/*backtest\nstart: 2023-10-22 00:00:00\nend: 2023-10-29 00:00:00\nperiod: 1m\nbasePeriod: 1m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("My Strategy with Bollinger Bands and StochRSI", overlay=true)\n\n// Define your Bollinger Bands parameters\nbollinger_length = input.int(20, title="Bollinger Bands Length")\nbollinger_dev = input.float(2, title="Bollinger Bands Deviation")\n\n// Calculate Bollinger Bands\nsma = ta.sma(close, bollinger_length)\ndev = bollinger_dev * ta.stdev(close, bollinger_length)\n\nupper_band = sma + dev\nlower_band = sma - dev\n\n// Define your StochRSI parameters\nstoch_length = input.int(14, title="StochRSI Length")\nk_period = input.int(3, title="K Period")\nd_period = input.int(3, title="D Period")\n\n// Calculate StochRSI\nrsi = ta.rsi(close, stoch_length)\nk = ta.sma(ta.stoch(rsi, rsi, rsi, k_period), k_period)\nd = ta.sma(k, d_period)\n\n// Define your buy and sell conditions\nbuy_condition = ta.crossover(k, d) and close < lower_band\nsell_condition = ta.crossunder(k, d) and close > upper_band\n\n// Place orders based on the conditions\nif (buy_condition)\n    strategy.entry("Buy", strategy.long)\n\nif (sell_condition)\n    strategy.entry("Sell", strategy.short)\n\n// Optional: Plot buy and sell signals on the chart\nplotshape(buy_condition, color=color.green, style=shape.triangleup, location=location.belowbar, size=size.small)\nplotshape(sell_condition, color=color.red, style=shape.triangledown, location=location.abovebar, size=size.small)\n\n// Plot Bollinger Bands and StochRSI on the chart\nplot(upper_band, title="Upper Bollinger Band", color=color.blue)\nplot(lower_band, title="Lower Bollinger Band", color=color.orange)\nplot(k, title="StochRSI K", color=color.green)\nplot(d, title="StochRSI D", color=color.red)'

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
