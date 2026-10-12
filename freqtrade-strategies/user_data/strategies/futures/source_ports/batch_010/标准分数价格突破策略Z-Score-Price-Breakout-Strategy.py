"""Source-faithful deep-assisted port of 标准分数价格突破策略Z-Score-Price-Breakout-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_c419268c(PinePortBase, IStrategy):
    source_file = '标准分数价格突破策略Z-Score-Price-Breakout-Strategy.md'
    timeframe = '15m'
    can_short = True
    source_defaults = {'Period': 20, 'Trigger': 0, 'reverse': False}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.entry', 'for ', 'while ']
    source_fidelity_notes = []
    pine_assignments = [{'mode': '', 'name': 'Period', 'op': '=', 'expr': 'input(20, minval=1)', 'conditions': []}, {'mode': '', 'name': 'Trigger', 'op': '=', 'expr': 'input(0)', 'conditions': []}, {'mode': '', 'name': 'reverse', 'op': '=', 'expr': 'input(false, title="Trade reverse")', 'conditions': []}, {'mode': '', 'name': 'xStdDev', 'op': '=', 'expr': 'stdev(close, Period)', 'conditions': []}, {'mode': '', 'name': 'xMA', 'op': '=', 'expr': 'sma(close, Period)', 'conditions': []}, {'mode': '', 'name': 'nRes', 'op': '=', 'expr': '(close - xMA) / xStdDev', 'conditions': []}, {'mode': '', 'name': 'pos', 'op': '=', 'expr': 'iff(nRes > Trigger, 1, iff(nRes < Trigger, -1, nz(pos[1], 0)))', 'conditions': []}, {'mode': '', 'name': 'possig', 'op': '=', 'expr': 'iff(reverse and pos == 1, -1, iff(reverse and pos == -1, 1, pos))', 'conditions': []}]
    pine_user_functions = []
    pine_controls = [{'indent': 0, 'statement': 'if (possig == 1)'}, {'indent': 0, 'statement': 'if (possig == -1)'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("Long", strategy.long)', 'conditions': ['(possig == 1)'], 'statement': 'strategy.entry("Long", strategy.long)'}, {'kind': 'entry', 'call': 'strategy.entry("Short", strategy.short)', 'conditions': ['(possig == -1)'], 'statement': 'strategy.entry("Short", strategy.short)'}]
    original_pine = '/*backtest\nstart: 2023-11-29 00:00:00\nend: 2023-12-04 19:00:00\nperiod: 15m\nbasePeriod: 5m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=2\n////////////////////////////////////////////////////////////\n//  Copyright by HPotter v1.0 18/01/2017\n// The author of this indicator is Veronique Valcu. The z-score (z) for a data \n// item x measures the distance (in standard deviations StdDev) and direction \n// of the item from its mean (U):\n//     z = (x-StdDev) / U\n// A value of zero indicates that the data item x is equal to the mean U, while \n// positive or negative values show that the data item is above (x>U) or below \n// (x Values of +2 and -2 show that the data item is two standard deviations \n// above or below the chosen mean, respectively, and over 95.5% of all data \n// items are contained within these two horizontal references (see Figure 1).\n// We substitute x with the closing price C, the mean U with simple moving \n// average (SMA) of n periods (n), and StdDev with the standard deviation of \n// closing prices for n periods, the above formula becomes:\n//     Z_score = (C - SMA(n)) / StdDev(C,n)\n// The z-score indicator is not new, but its use can be seen as a supplement to \n// Bollinger bands. It offers a simple way to assess the position of the price \n// vis-a-vis its resistance and support levels expressed by the Bollinger Bands. \n// In addition, crossings of z-score averages may signal the start or the end of \n// a tradable trend. Traders may take a step further and look for stronger signals \n// by identifying common crossing points of z-score, its average, and average of average. \n//\n// You can change long to short in the Input Settings\n// Please, use it only for learning or paper trading. Do not for real trading.\n////////////////////////////////////////////////////////////\nstrategy(title="Z-Score Strategy", shorttitle="Z-Score Strategy")\nPeriod = input(20, minval=1)\nTrigger = input(0)\nreverse = input(false, title="Trade reverse")\nhline(Trigger, color=purple, linestyle=line)\nxStdDev = stdev(close, Period)\nxMA = sma(close, Period)\nnRes = (close - xMA) / xStdDev\npos = iff(nRes > Trigger, 1,\n\t   iff(nRes < Trigger, -1, nz(pos[1], 0))) \npossig = iff(reverse and pos == 1, -1,\n          iff(reverse and pos == -1, 1, pos))\t   \nif (possig == 1) \n    strategy.entry("Long", strategy.long)\nif (possig == -1)\n    strategy.entry("Short", strategy.short)\t   \t    \nbarcolor(possig == -1 ? red: possig == 1 ? green : blue )\nplot(nRes, color=blue, title="Z-Score")'

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
