"""Source-faithful deep-assisted port of 流量主导型震荡量化策略Volume-driven-Oscillation-Quant-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_dbcf1734(PinePortBase, IStrategy):
    source_file = '流量主导型震荡量化策略Volume-driven-Oscillation-Quant-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'TrigLen': 13, 'FastX': 34, 'SlowX': 55, 'reverse': False}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.entry', 'for ']
    source_fidelity_notes = []
    pine_assignments = [{'mode': '', 'name': 'TrigLen', 'op': '=', 'expr': 'input(13, minval=1)', 'conditions': []}, {'mode': '', 'name': 'FastX', 'op': '=', 'expr': 'input(34, minval=1)', 'conditions': []}, {'mode': '', 'name': 'SlowX', 'op': '=', 'expr': 'input(55, minval=1)', 'conditions': []}, {'mode': '', 'name': 'reverse', 'op': '=', 'expr': 'input(false, title="Trade reverse")', 'conditions': []}, {'mode': '', 'name': 'xTrend', 'op': '=', 'expr': 'iff(hlc3 > hlc3[1], volume * 100, -volume * 100)', 'conditions': []}, {'mode': '', 'name': 'xFast', 'op': '=', 'expr': 'ema(xTrend, FastX)', 'conditions': []}, {'mode': '', 'name': 'xSlow', 'op': '=', 'expr': 'ema(xTrend, SlowX)', 'conditions': []}, {'mode': '', 'name': 'xKVO', 'op': '=', 'expr': 'xFast - xSlow', 'conditions': []}, {'mode': '', 'name': 'xTrigger', 'op': '=', 'expr': 'ema(xKVO, TrigLen)', 'conditions': []}, {'mode': '', 'name': 'pos', 'op': '=', 'expr': 'iff(xKVO > xTrigger, 1, iff(xKVO < xTrigger, -1, nz(pos[1], 0)))', 'conditions': []}, {'mode': '', 'name': 'possig', 'op': '=', 'expr': 'iff(reverse and pos == 1, -1, iff(reverse and pos == -1, 1, pos))', 'conditions': []}]
    pine_user_functions = []
    pine_controls = [{'indent': 0, 'statement': 'if (possig == 1)'}, {'indent': 0, 'statement': 'if (possig == -1)'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("Long", strategy.long)', 'conditions': ['(possig == 1)'], 'statement': 'strategy.entry("Long", strategy.long)'}, {'kind': 'entry', 'call': 'strategy.entry("Short", strategy.short)', 'conditions': ['(possig == -1)'], 'statement': 'strategy.entry("Short", strategy.short)'}]
    original_pine = '/*backtest\nstart: 2022-11-28 00:00:00\nend: 2023-12-04 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=2\n////////////////////////////////////////////////////////////\n//  Copyright by HPotter v1.0 30/08/2017\n// The Klinger Oscillator (KO) was developed by Stephen J. Klinger. Learning \n// from prior research on volume by such well-known technicians as Joseph Granville, \n// Larry Williams, and Marc Chaikin, Mr. Klinger set out to develop a volume-based \n// indicator to help in both short- and long-term analysis.\n// The KO was developed with two seemingly opposite goals in mind: to be sensitive \n// enough to signal short-term tops and bottoms, yet accurate enough to reflect the \n// long-term flow of money into and out of a security.\n// The KO is based on the following tenets:\n// Price range (i.e. High - Low) is a measure of movement and volume is the force behind \n// the movement. The sum of High + Low + Close defines a trend. Accumulation occurs when \n// today\'s sum is greater than the previous day\'s. Conversely, distribution occurs when \n// today\'s sum is less than the previous day\'s. When the sums are equal, the existing trend \n// is maintained.\n// Volume produces continuous intra-day changes in price reflecting buying and selling pressure. \n// The KO quantifies the difference between the number of shares being accumulated and distributed \n// each day as "volume force". A strong, rising volume force should accompany an uptrend and then \n// gradually contract over time during the latter stages of the uptrend and the early stages of \n// the following downtrend. This should be followed by a rising volume force reflecting some \n// accumulation before a bottom develops.\n//\n// You can change long to short in the Input Settings\n// Please, use it only for learning or paper trading. \n////////////////////////////////////////////////////////////\nstrategy(title="Klinger Volume Oscillator (KVO)", shorttitle="KVO")\nTrigLen = input(13, minval=1)\nFastX = input(34, minval=1)\nSlowX = input(55, minval=1)\nreverse = input(false, title="Trade reverse")\nhline(0, color=gray, linestyle=line)\nxTrend = iff(hlc3 > hlc3[1], volume * 100, -volume * 100)\nxFast = ema(xTrend, FastX)\nxSlow = ema(xTrend, SlowX)\nxKVO = xFast - xSlow\nxTrigger = ema(xKVO, TrigLen)\npos = iff(xKVO > xTrigger, 1,\n\t   iff(xKVO < xTrigger, -1, nz(pos[1], 0))) \npossig = iff(reverse and pos == 1, -1,\n          iff(reverse and pos == -1, 1, pos))\t   \nif (possig == 1) \n    strategy.entry("Long", strategy.long)\nif (possig == -1)\n    strategy.entry("Short", strategy.short)\t   \t    \nbarcolor(possig == -1 ? red: possig == 1 ? green : blue )  \nplot(xKVO, color=blue, title="KVO")\nplot(xTrigger, color=red, title="Trigger")'

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
