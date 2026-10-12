"""Source-faithful deep-assisted port of 惯性指标交易策略Inertia-Indicator-Trading-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_c5cbfefc(PinePortBase, IStrategy):
    source_file = '惯性指标交易策略Inertia-Indicator-Trading-Strategy.md'
    timeframe = '1h'
    can_short = True
    source_defaults = {'Period': 10, 'Smooth': 14, 'reverse': False}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.entry', 'for ']
    source_fidelity_notes = []
    pine_assignments = [{'mode': '', 'name': 'Period', 'op': '=', 'expr': 'input(10, minval=1)', 'conditions': []}, {'mode': '', 'name': 'Smooth', 'op': '=', 'expr': 'input(14, minval=1)', 'conditions': []}, {'mode': '', 'name': 'reverse', 'op': '=', 'expr': 'input(false, title="Trade reverse")', 'conditions': []}, {'mode': '', 'name': 'xPrice', 'op': '=', 'expr': 'close', 'conditions': []}, {'mode': '', 'name': 'StdDev', 'op': '=', 'expr': 'stdev(xPrice, Period)', 'conditions': []}, {'mode': '', 'name': 'd', 'op': '=', 'expr': 'iff(close > close[1], 0, StdDev)', 'conditions': []}, {'mode': '', 'name': 'u', 'op': '=', 'expr': 'iff(close > close[1], StdDev, 0)', 'conditions': []}, {'mode': '', 'name': 'nU', 'op': '=', 'expr': '(13 * nz(nU[1],0) + u) / 14', 'conditions': []}, {'mode': '', 'name': 'nD', 'op': '=', 'expr': '(13 * nz(nD[1],0) + d) / 14', 'conditions': []}, {'mode': '', 'name': 'nRVI', 'op': '=', 'expr': '100 * nU / (nU + nD)', 'conditions': []}, {'mode': '', 'name': 'nRes', 'op': '=', 'expr': 'ema(nRVI, Smooth)', 'conditions': []}, {'mode': '', 'name': 'pos', 'op': '=', 'expr': 'iff(nRes > 50, 1, iff(nRes < 50, -1, nz(pos[1], 0)))', 'conditions': []}, {'mode': '', 'name': 'possig', 'op': '=', 'expr': 'iff(reverse and pos == 1, -1, iff(reverse and pos == -1, 1, pos))', 'conditions': []}]
    pine_user_functions = []
    pine_controls = [{'indent': 0, 'statement': 'if (possig == 1)'}, {'indent': 0, 'statement': 'if (possig == -1)'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("Long", strategy.long)', 'conditions': ['(possig == 1)'], 'statement': 'strategy.entry("Long", strategy.long)'}, {'kind': 'entry', 'call': 'strategy.entry("Short", strategy.short)', 'conditions': ['(possig == -1)'], 'statement': 'strategy.entry("Short", strategy.short)'}]
    original_pine = '/*backtest\nstart: 2023-11-25 00:00:00\nend: 2023-12-25 00:00:00\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=2\n////////////////////////////////////////////////////////////\n//  Copyright by HPotter v1.0 23/05/2017\n// The inertia indicator measures the market, stock or currency pair momentum and \n// trend by measuring the security smoothed RVI (Relative Volatility Index). \n// The RVI is a technical indicator that estimates the general direction of the \n// volatility of an asset.\n// The inertia indicator returns a value that is comprised between 0 and 100. \n// Positive inertia occurs when the indicator value is higher than 50. As long as \n// the inertia value is above 50, the long-term trend of the security is up. The inertia \n// is negative when its value is lower than 50, in this case the long-term trend is \n// down and should stay down if the inertia stays below 50.\n//\n// You can change long to short in the Input Settings\n// Please, use it only for learning or paper trading. Do not for real trading.\n////////////////////////////////////////////////////////////\nstrategy(title="Inertia Indicator", shorttitle="Inertia")\nPeriod = input(10, minval=1)\nSmooth = input(14, minval=1)\nreverse = input(false, title="Trade reverse")\nhline(50, color=green, linestyle=line)\nxPrice = close\nStdDev = stdev(xPrice, Period)\nd = iff(close > close[1], 0, StdDev)\nu = iff(close > close[1], StdDev, 0)\nnU = (13 * nz(nU[1],0) + u) / 14\nnD = (13 * nz(nD[1],0) + d) / 14\nnRVI = 100 * nU / (nU + nD)\nnRes = ema(nRVI, Smooth)\npos = iff(nRes > 50, 1,\n\t     iff(nRes < 50, -1, nz(pos[1], 0))) \npossig = iff(reverse and pos == 1, -1,\n          iff(reverse and pos == -1, 1, pos))\t   \nif (possig == 1) \n    strategy.entry("Long", strategy.long)\nif (possig == -1)\n    strategy.entry("Short", strategy.short)\t   \t    \nbarcolor(possig == -1 ? red: possig == 1 ? green : blue ) \nplot(nRes, color=red, title="Inertia")'

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
