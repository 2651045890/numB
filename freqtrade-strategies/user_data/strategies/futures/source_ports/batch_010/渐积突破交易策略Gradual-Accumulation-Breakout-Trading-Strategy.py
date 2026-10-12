"""Source-faithful deep-assisted port of 渐积突破交易策略Gradual-Accumulation-Breakout-Trading-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_10d49624(PinePortBase, IStrategy):
    source_file = '渐积突破交易策略Gradual-Accumulation-Breakout-Trading-Strategy.md'
    timeframe = '2h'
    can_short = True
    source_defaults = {'AccumulationLength': 32, 'DistributionLength': 35, 'SpringLength': 10, 'UpthrustLength': 20, 'stopPercentage': 10}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 10.0
    source_pyramiding = 0
    source_initial_capital = 1000.0
    source_commission_percent = 0.0
    source_features = ['strategy.exit', 'strategy.entry', 'strategy.close']
    source_fidelity_notes = ['Uses strategy.exit; stop/limit/profit/loss/trailing arguments have Pine order semantics and may fill intrabar.']
    pine_assignments = [{'mode': '', 'name': 'AccumulationLength', 'op': '=', 'expr': 'input(32, "Accumulation")', 'conditions': []}, {'mode': '', 'name': 'DistributionLength', 'op': '=', 'expr': 'input(35, "Distribution")', 'conditions': []}, {'mode': '', 'name': 'SpringLength', 'op': '=', 'expr': 'input(10, "Spring")', 'conditions': []}, {'mode': '', 'name': 'UpthrustLength', 'op': '=', 'expr': 'input(20, "Upthrust")', 'conditions': []}, {'mode': '', 'name': 'stopPercentage', 'op': '=', 'expr': 'input(10, "Stop Percentage")', 'conditions': []}, {'mode': '', 'name': 'isAccumulation', 'op': '=', 'expr': 'ta.crossover(close, ta.sma(close, AccumulationLength))', 'conditions': []}, {'mode': '', 'name': 'isDistribution', 'op': '=', 'expr': 'ta.crossunder(close, ta.sma(close, DistributionLength))', 'conditions': []}, {'mode': '', 'name': 'isSpring', 'op': '=', 'expr': 'ta.crossover(low, ta.sma(low, SpringLength))', 'conditions': []}, {'mode': '', 'name': 'isUpthrust', 'op': '=', 'expr': 'ta.crossunder(high, ta.sma(high, UpthrustLength))', 'conditions': []}, {'mode': '', 'name': 'enterLong', 'op': '=', 'expr': 'isAccumulation and isSpring', 'conditions': []}, {'mode': '', 'name': 'exitLong', 'op': '=', 'expr': 'isDistribution and isUpthrust', 'conditions': []}, {'mode': '', 'name': 'enterShort', 'op': '=', 'expr': 'isDistribution and isUpthrust', 'conditions': []}, {'mode': '', 'name': 'exitShort', 'op': '=', 'expr': 'isAccumulation and isSpring', 'conditions': []}, {'mode': '', 'name': 'stopLossLevelLong', 'op': '=', 'expr': 'close * (1 - stopPercentage / 100)', 'conditions': []}, {'mode': '', 'name': 'stopLossLevelShort', 'op': '=', 'expr': 'close * (1 + stopPercentage / 100)', 'conditions': []}]
    pine_user_functions = []
    pine_controls = [{'indent': 0, 'statement': 'if (enterLong)'}, {'indent': 0, 'statement': 'if (exitLong)'}, {'indent': 0, 'statement': 'if (enterShort)'}, {'indent': 0, 'statement': 'if (exitShort)'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("Long", strategy.long)', 'conditions': ['(enterLong)'], 'statement': 'strategy.entry("Long", strategy.long)'}, {'kind': 'close', 'call': 'strategy.close("Long")', 'conditions': ['(exitLong)'], 'statement': 'strategy.close("Long")'}, {'kind': 'entry', 'call': 'strategy.entry("Short", strategy.short)', 'conditions': ['(enterShort)'], 'statement': 'strategy.entry("Short", strategy.short)'}, {'kind': 'close', 'call': 'strategy.close("Short")', 'conditions': ['(exitShort)'], 'statement': 'strategy.close("Short")'}, {'kind': 'exit', 'call': 'strategy.exit("Stop Loss Long", "Long", stop=stopLossLevelLong)', 'conditions': [], 'statement': 'strategy.exit("Stop Loss Long", "Long", stop=stopLossLevelLong)'}, {'kind': 'exit', 'call': 'strategy.exit("Stop Loss Short", "Short", stop=stopLossLevelShort)', 'conditions': [], 'statement': 'strategy.exit("Stop Loss Short", "Short", stop=stopLossLevelShort)'}]
    original_pine = '/*backtest\nstart: 2023-09-24 00:00:00\nend: 2023-10-24 00:00:00\nperiod: 2h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This source code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © deperp\n\n//@version=5\nstrategy("Wyckoff Range Strategy",  overlay=true, initial_capital=1000, default_qty_type=strategy.percent_of_equity, default_qty_value=10, commission_type=strategy.commission.percent)\n\n// Input Variables\nAccumulationLength = input(32, "Accumulation")\nDistributionLength = input(35, "Distribution")\nSpringLength = input(10, "Spring")\nUpthrustLength = input(20, "Upthrust")\nstopPercentage = input(10, "Stop Percentage")\n\n// Accumulation Phase\nisAccumulation = ta.crossover(close, ta.sma(close, AccumulationLength))\n\n// Distribution Phase\nisDistribution = ta.crossunder(close, ta.sma(close, DistributionLength))\n\n// Spring and Upthrust\nisSpring = ta.crossover(low, ta.sma(low, SpringLength))\nisUpthrust = ta.crossunder(high, ta.sma(high, UpthrustLength))\n\n// Strategy Conditions\nenterLong = isAccumulation and isSpring\nexitLong = isDistribution and isUpthrust\n\nenterShort = isDistribution and isUpthrust\nexitShort = isAccumulation and isSpring\n\n// Entry and Exit Conditions\nif (enterLong)\n    strategy.entry("Long", strategy.long)\n    \nif (exitLong)\n    strategy.close("Long")\n\nif (enterShort)\n    strategy.entry("Short", strategy.short)\n\nif (exitShort)\n    strategy.close("Short")\n\n// Stop Loss\nstopLossLevelLong = close * (1 - stopPercentage / 100)\nstopLossLevelShort = close * (1 + stopPercentage / 100)\nstrategy.exit("Stop Loss Long", "Long", stop=stopLossLevelLong)\nstrategy.exit("Stop Loss Short", "Short", stop=stopLossLevelShort)\n\n// Plotting Wyckoff Schematics\nplotshape(isAccumulation, title="Accumulation Phase", location=location.belowbar, color=color.green, style=shape.labelup, text="Accumulation")\nplotshape(isDistribution, title="Distribution Phase", location=location.abovebar, color=color.red, style=shape.labeldown, text="Distribution")\nplotshape(isSpring, title="Spring", location=location.belowbar, color=color.blue, style=shape.triangleup)\nplotshape(isUpthrust, title="Upthrust", location=location.abovebar, color=color.orange, style=shape.triangledown)'

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
