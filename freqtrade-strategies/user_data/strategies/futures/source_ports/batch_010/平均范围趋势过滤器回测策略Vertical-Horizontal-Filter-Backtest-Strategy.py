"""Source-faithful deep-assisted port of 平均范围趋势过滤器回测策略Vertical-Horizontal-Filter-Backtest-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_9d0a6bcc(PinePortBase, IStrategy):
    source_file = '平均范围趋势过滤器回测策略Vertical-Horizontal-Filter-Backtest-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'Length': 28, 'Signal': 0.4, 'reverse': False}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.entry']
    source_fidelity_notes = []
    pine_assignments = [{'mode': '', 'name': 'Length', 'op': '=', 'expr': 'input(28, minval=1)', 'conditions': []}, {'mode': '', 'name': 'Signal', 'op': '=', 'expr': 'input(0.4, step=0.01)', 'conditions': []}, {'mode': '', 'name': 'reverse', 'op': '=', 'expr': 'input(false, title="Trade reverse")', 'conditions': []}, {'mode': '', 'name': 'xHH', 'op': '=', 'expr': 'highest(high, Length)', 'conditions': []}, {'mode': '', 'name': 'xLL', 'op': '=', 'expr': 'lowest(low, Length)', 'conditions': []}, {'mode': '', 'name': 'xNumerator', 'op': '=', 'expr': 'abs(xHH - xLL)', 'conditions': []}, {'mode': '', 'name': 'xDenominator', 'op': '=', 'expr': 'sum(abs(close - close[1]), Length)', 'conditions': []}, {'mode': '', 'name': 'xVHF', 'op': '=', 'expr': 'xNumerator / xDenominator', 'conditions': []}, {'mode': '', 'name': 'pos', 'op': '=', 'expr': 'iff(xVHF > Signal, 1, iff(xVHF < Signal, -1, nz(pos[1], 0)))', 'conditions': []}, {'mode': '', 'name': 'possig', 'op': '=', 'expr': 'iff(reverse and pos == 1, -1, iff(reverse and pos == -1, 1, pos))', 'conditions': []}]
    pine_user_functions = []
    pine_controls = [{'indent': 0, 'statement': 'if (possig == 1)'}, {'indent': 0, 'statement': 'if (possig == -1)'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("Long", strategy.long)', 'conditions': ['(possig == 1)'], 'statement': 'strategy.entry("Long", strategy.long)'}, {'kind': 'entry', 'call': 'strategy.entry("Short", strategy.short)', 'conditions': ['(possig == -1)'], 'statement': 'strategy.entry("Short", strategy.short)'}]
    original_pine = '/*backtest\nstart: 2023-01-01 00:00:00\nend: 2024-01-07 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=2\n////////////////////////////////////////////////////////////\n//  Copyright by HPotter v1.0 27/04/2018\n// Vertical Horizontal Filter was initiated by Adam White. It was first published \n// in a magazine called “Issues of Futures” in August, 1991. The Vertical Horizontal \n// Filter (VHF) is a very common Indicator used by traders to find out the Phase of \n// a Price Trend. Normally, a price trend can be in a Trending Phase or a Congestion \n// Phase/Choppy Movement Phase. Adam White created this particular Technical Indicator \n// to determine whether prices are trending in a particular direction or are they going \n// through a transitional period. He used it to measure the range of Futures available\n// in the market.\n//\n// You can change long to short in the Input Settings\n// WARNING:\n//  - For purpose educate only\n//  - This script to change bars colors.\n////////////////////////////////////////////////////////////\nstrategy(title="Vertical Horizontal Filter Backtest")\nLength = input(28, minval=1)\nSignal = input(0.4, step=0.01)\nreverse = input(false, title="Trade reverse")\nhline(Signal, color=blue, linestyle=line)\nxHH = highest(high, Length)\nxLL = lowest(low, Length)\nxNumerator = abs(xHH - xLL)\nxDenominator = sum(abs(close - close[1]), Length)\nxVHF = xNumerator / xDenominator \npos = iff(xVHF > Signal, 1,\n       iff(xVHF < Signal, -1, nz(pos[1], 0))) \npossig = iff(reverse and pos == 1, -1,\n          iff(reverse and pos == -1, 1, pos))\t   \nif (possig == 1) \n    strategy.entry("Long", strategy.long)\nif (possig == -1)\n    strategy.entry("Short", strategy.short)\t   \t    \nbarcolor(possig == -1 ? red: possig == 1 ? green : blue ) \nplot(xVHF, color=blue, title="VHF")'

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
