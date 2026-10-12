"""Source-faithful deep-assisted port of 相对波动指数回测策略Relative-Volatility-Index-Backtesting-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_75764f08(PinePortBase, IStrategy):
    source_file = '相对波动指数回测策略Relative-Volatility-Index-Backtesting-Strategy.md'
    timeframe = '4h'
    can_short = True
    source_defaults = {'Period': 10, 'BuyZone': 30, 'SellZone': 70, 'reverse': False}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.entry', 'for ', 'line.']
    source_fidelity_notes = ['Drawing/table calls are display-only unless their IDs/state are later read; preserved in source map but excluded from trade signal calculation where non-causal.']
    pine_assignments = [{'mode': '', 'name': 'Period', 'op': '=', 'expr': 'input(10, minval=1)', 'conditions': []}, {'mode': '', 'name': 'BuyZone', 'op': '=', 'expr': 'input(30, minval=1)', 'conditions': []}, {'mode': '', 'name': 'SellZone', 'op': '=', 'expr': 'input(70, minval=1)', 'conditions': []}, {'mode': '', 'name': 'reverse', 'op': '=', 'expr': 'input(false, title="Trade reverse")', 'conditions': []}, {'mode': '', 'name': 'xPrice', 'op': '=', 'expr': 'close', 'conditions': []}, {'mode': '', 'name': 'StdDev', 'op': '=', 'expr': 'stdev(xPrice, Period)', 'conditions': []}, {'mode': '', 'name': 'd', 'op': '=', 'expr': 'iff(close > close[1], 0, StdDev)', 'conditions': []}, {'mode': '', 'name': 'u', 'op': '=', 'expr': 'iff(close > close[1], StdDev, 0)', 'conditions': []}, {'mode': '', 'name': 'nU', 'op': '=', 'expr': '(13 * nz(nU[1],0) + u) / 14', 'conditions': []}, {'mode': '', 'name': 'nD', 'op': '=', 'expr': '(13 * nz(nD[1],0) + d) / 14', 'conditions': []}, {'mode': '', 'name': 'nRes', 'op': '=', 'expr': '100 * nU / (nU + nD)', 'conditions': []}, {'mode': '', 'name': 'pos', 'op': '=', 'expr': 'iff(nRes < BuyZone, -1, iff(nRes > SellZone, 1, nz(pos[1], 0)))', 'conditions': []}, {'mode': '', 'name': 'possig', 'op': '=', 'expr': 'iff(reverse and pos == 1, -1, iff(reverse and pos == -1, 1, pos))', 'conditions': []}]
    pine_user_functions = []
    pine_controls = [{'indent': 0, 'statement': 'if (possig == 1)'}, {'indent': 0, 'statement': 'if (possig == -1)'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("Long", strategy.long)', 'conditions': ['(possig == 1)'], 'statement': 'strategy.entry("Long", strategy.long)'}, {'kind': 'entry', 'call': 'strategy.entry("Short", strategy.short)', 'conditions': ['(possig == -1)'], 'statement': 'strategy.entry("Short", strategy.short)'}]
    original_pine = '/*backtest\nstart: 2023-08-26 00:00:00\nend: 2023-09-19 00:00:00\nperiod: 4h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=2\n////////////////////////////////////////////////////////////\n//  Copyright by HPotter v1.0 23/10/2017\n// The RVI is a modified form of the relative strength index (RSI). \n// The original RSI calculation separates one-day net changes into \n// positive closes and negative closes, then smoothes the data and \n// normalizes the ratio on a scale of zero to 100 as the basis for the \n// formula. The RVI uses the same basic formula but substitutes the \n// 10-day standard deviation of the closing prices for either the up \n// close or the down close. The goal is to create an indicator that \n// measures the general direction of volatility. The volatility is \n// being measured by the 10-days standard deviation of the closing prices. \n//\n// You can change long to short in the Input Settings\n// WARNING:\n// - For purpose educate only\n// - This script to change bars colors.\n////////////////////////////////////////////////////////////\nstrategy(title="Relative Volatility Index", shorttitle="RVI")\nPeriod = input(10, minval=1)\nBuyZone = input(30, minval=1)\nSellZone = input(70, minval=1)\nreverse = input(false, title="Trade reverse")\nhline(0, color=purple, linestyle=hline.style_dashed)\nhline(BuyZone, color=red, linestyle=hline.style_solid)\nhline(SellZone, color=green, linestyle=hline.style_solid)\nxPrice = close\nStdDev = stdev(xPrice, Period)\nd = iff(close > close[1], 0, StdDev)\nu = iff(close > close[1], StdDev, 0)\nnU = (13 * nz(nU[1],0) + u) / 14\nnD = (13 * nz(nD[1],0) + d) / 14\nnRes = 100 * nU / (nU + nD)\npos = iff(nRes < BuyZone, -1,\n\t   iff(nRes > SellZone, 1, nz(pos[1], 0))) \npossig = iff(reverse and pos == 1, -1,\n          iff(reverse and pos == -1, 1, pos))\t   \nif (possig == 1) \n    strategy.entry("Long", strategy.long)\nif (possig == -1)\n    strategy.entry("Short", strategy.short)\t   \t    \nbarcolor(possig == -1 ? red: possig == 1 ? green : blue )  \nplot(nRes, color=red, title="RVI")'

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
