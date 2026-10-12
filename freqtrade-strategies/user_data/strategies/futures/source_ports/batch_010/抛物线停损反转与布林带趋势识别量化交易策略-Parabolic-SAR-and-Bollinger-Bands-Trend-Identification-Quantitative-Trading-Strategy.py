"""Source-faithful deep-assisted port of 抛物线停损反转与布林带趋势识别量化交易策略-Parabolic-SAR-and-Bollinger-Bands-Trend-Identification-Quantitative-Trading-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_5b01767f(PinePortBase, IStrategy):
    source_file = '抛物线停损反转与布林带趋势识别量化交易策略-Parabolic-SAR-and-Bollinger-Bands-Trend-Identification-Quantitative-Trading-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'sar_step': 0.02, 'sar_max': 0.2, 'bb_length': 20, 'bb_mult': 2.0}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.entry', 'strategy.close']
    source_fidelity_notes = []
    pine_assignments = [{'mode': '', 'name': 'sar_step', 'op': '=', 'expr': 'input.float(0.02, "SAR Step", minval=0.001, maxval=0.1)', 'conditions': []}, {'mode': '', 'name': 'sar_max', 'op': '=', 'expr': 'input.float(0.2, "SAR Max", minval=0.1, maxval=0.5)', 'conditions': []}, {'mode': '', 'name': 'bb_length', 'op': '=', 'expr': 'input.int(20, "BB Length")', 'conditions': []}, {'mode': '', 'name': 'bb_mult', 'op': '=', 'expr': 'input.float(2.0, "BB Multiplier")', 'conditions': []}, {'mode': '', 'name': 'sar', 'op': '=', 'expr': 'ta.sar(sar_step, sar_max, sar_max)', 'conditions': []}, {'mode': '', 'name': 'bb_basis', 'op': '=', 'expr': 'ta.sma(close, bb_length)', 'conditions': []}, {'mode': '', 'name': 'bb_dev', 'op': '=', 'expr': 'bb_mult * ta.stdev(close, bb_length)', 'conditions': []}, {'mode': '', 'name': 'bb_upper', 'op': '=', 'expr': 'bb_basis + bb_dev', 'conditions': []}, {'mode': '', 'name': 'bb_lower', 'op': '=', 'expr': 'bb_basis - bb_dev', 'conditions': []}, {'mode': '', 'name': 'longCondition', 'op': '=', 'expr': 'close > sar and close < bb_upper', 'conditions': []}, {'mode': '', 'name': 'shortCondition', 'op': '=', 'expr': 'close < sar and close > bb_lower', 'conditions': []}, {'mode': '', 'name': 'exitLong', 'op': '=', 'expr': 'close < sar or close >= bb_upper', 'conditions': []}, {'mode': '', 'name': 'exitShort', 'op': '=', 'expr': 'close > sar or close <= bb_lower', 'conditions': []}]
    pine_user_functions = []
    pine_controls = [{'indent': 0, 'statement': 'if (longCondition)'}, {'indent': 0, 'statement': 'if (exitLong)'}, {'indent': 0, 'statement': 'if (shortCondition)'}, {'indent': 0, 'statement': 'if (exitShort)'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("Buy", strategy.long)', 'conditions': ['(longCondition)'], 'statement': 'strategy.entry("Buy", strategy.long)'}, {'kind': 'close', 'call': 'strategy.close("Buy")', 'conditions': ['(exitLong)'], 'statement': 'strategy.close("Buy")'}, {'kind': 'entry', 'call': 'strategy.entry("Sell", strategy.short)', 'conditions': ['(shortCondition)'], 'statement': 'strategy.entry("Sell", strategy.short)'}, {'kind': 'close', 'call': 'strategy.close("Sell")', 'conditions': ['(exitShort)'], 'statement': 'strategy.close("Sell")'}]
    original_pine = '/*backtest\nstart: 2024-03-27 00:00:00\nend: 2024-12-12 00:00:00\nperiod: 1d\nbasePeriod: 1d\nexchanges: [{"eid":"Futures_Binance","currency":"ETH_USDT"}]\n*/\n\n//@version=5\nstrategy("Parabolic SAR + Bollinger Bands Strategy", overlay=true)\n\n// ———— Inputs ———— //\n// Parabolic SAR Inputs\nsar_step = input.float(0.02, "SAR Step", minval=0.001, maxval=0.1)\nsar_max = input.float(0.2, "SAR Max", minval=0.1, maxval=0.5)\n\n// Bollinger Bands Inputs\nbb_length = input.int(20, "BB Length")\nbb_mult = input.float(2.0, "BB Multiplier")\n\n// ———— Calculate Indicators ———— //\n// Parabolic SAR\nsar = ta.sar(sar_step, sar_max, sar_max)\nplot(sar, "SAR", color=color.blue, style=plot.style_circles)\n\n// Bollinger Bands\nbb_basis = ta.sma(close, bb_length)\nbb_dev = bb_mult * ta.stdev(close, bb_length)\nbb_upper = bb_basis + bb_dev\nbb_lower = bb_basis - bb_dev\n\n// Plot Bollinger Bands\nplot(bb_basis, "BB Basis", color=color.orange)\nplot(bb_upper, "BB Upper", color=color.blue)\nplot(bb_lower, "BB Lower", color=color.blue)\n\n// ———— Strategy Logic ———— //\n// Long Condition: Price closes above SAR (uptrend) AND below Upper BB\nlongCondition = close > sar and close < bb_upper\n\n// Short Condition: Price closes below SAR (downtrend) AND above Lower BB\nshortCondition = close < sar and close > bb_lower\n\n// Exit Conditions\nexitLong = close < sar or close >= bb_upper\nexitShort = close > sar or close <= bb_lower\n\n// ———— Execute Orders ———— //\nif (longCondition)\n    strategy.entry("Buy", strategy.long)\nif (exitLong)\n    strategy.close("Buy")\n\nif (shortCondition)\n    strategy.entry("Sell", strategy.short)\nif (exitShort)\n    strategy.close("Sell")\n\n// ———— Visual Alerts ———— //\nplotshape(longCondition, style=shape.triangleup, location=location.belowbar, color=color.green, size=size.small)\nplotshape(shortCondition, style=shape.triangledown, location=location.abovebar, color=color.red, size=size.small)'

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
