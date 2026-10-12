"""Source-faithful deep-assisted port of 正成交量指数策略Positive-Volume-Index-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_9508e948(PinePortBase, IStrategy):
    source_file = '正成交量指数策略Positive-Volume-Index-Strategy.md'
    timeframe = '3h'
    can_short = True
    source_defaults = {'EMA_Len': 255, 'reverse': False}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.entry']
    source_fidelity_notes = []
    pine_assignments = [{'mode': '', 'name': 'EMA_Len', 'op': '=', 'expr': 'input(255, minval=1)', 'conditions': []}, {'mode': '', 'name': 'reverse', 'op': '=', 'expr': 'input(false, title="Trade reverse")', 'conditions': []}, {'mode': '', 'name': 'xROC', 'op': '=', 'expr': 'roc(close, 1)', 'conditions': []}, {'mode': '', 'name': 'nRes', 'op': '=', 'expr': 'iff(volume > volume[1], nz(nRes[1], 0) + xROC, nz(nRes[1], 0))', 'conditions': []}, {'mode': '', 'name': 'nResEMA', 'op': '=', 'expr': 'ema(nRes, EMA_Len)', 'conditions': []}, {'mode': '', 'name': 'pos', 'op': '=', 'expr': 'iff(nRes > nResEMA, 1, iff(nRes < nResEMA, -1, nz(pos[1], 0)))', 'conditions': []}, {'mode': '', 'name': 'possig', 'op': '=', 'expr': 'iff(reverse and pos == 1, -1, iff(reverse and pos == -1, 1, pos))', 'conditions': []}]
    pine_user_functions = []
    pine_controls = [{'indent': 0, 'statement': 'if (possig == 1)'}, {'indent': 0, 'statement': 'if (possig == -1)'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("Long", strategy.long)', 'conditions': ['(possig == 1)'], 'statement': 'strategy.entry("Long", strategy.long)'}, {'kind': 'entry', 'call': 'strategy.entry("Short", strategy.short)', 'conditions': ['(possig == -1)'], 'statement': 'strategy.entry("Short", strategy.short)'}]
    original_pine = '/*backtest\nstart: 2023-08-18 00:00:00\nend: 2023-09-17 00:00:00\nperiod: 3h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=2\n////////////////////////////////////////////////////////////\n//  Copyright by HPotter v1.0 11/10/2017\n// The theory behind the indexes is as follows: On days of increasing volume, \n// you can expect prices to increase, and on days of decreasing volume, you can \n// expect prices to decrease. This goes with the idea of the market being in-gear \n// and out-of-gear. Both PVI and NVI work in similar fashions: Both are a running \n// cumulative of values, which means you either keep adding or subtracting price \n// rate of change each day to the previous day`s sum. In the case of PVI, if today`s \n// volume is less than yesterday`s, don`t add anything; if today`s volume is greater, \n// then add today`s price rate of change. For NVI, add today`s price rate of change \n// only if today`s volume is less than yesterday`s.\n//\n// You can change long to short in the Input Settings\n// WARNING:\n// - For purpose educate only\n// - This script to change bars colors.\n////////////////////////////////////////////////////////////\nstrategy(title="Positive Volume Index", shorttitle="Positive Volume Index")\nEMA_Len = input(255, minval=1)\nreverse = input(false, title="Trade reverse")\nxROC = roc(close, 1)\nnRes = iff(volume > volume[1], nz(nRes[1], 0) + xROC, nz(nRes[1], 0))\nnResEMA = ema(nRes, EMA_Len)\npos = iff(nRes > nResEMA, 1,\n\t   iff(nRes < nResEMA, -1, nz(pos[1], 0))) \npossig = iff(reverse and pos == 1, -1,\n          iff(reverse and pos == -1, 1, pos))\t   \nif (possig == 1) \n    strategy.entry("Long", strategy.long)\nif (possig == -1)\n    strategy.entry("Short", strategy.short)\t   \t    \nbarcolor(possig == -1 ? red: possig == 1 ? green : blue )  \nplot(nRes, color=red, title="PVI")\nplot(nResEMA, color=blue, title="EMA")'

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
