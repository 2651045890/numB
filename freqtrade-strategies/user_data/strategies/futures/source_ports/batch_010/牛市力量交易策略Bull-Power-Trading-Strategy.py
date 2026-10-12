"""Source-faithful deep-assisted port of 牛市力量交易策略Bull-Power-Trading-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_12525c9a(PinePortBase, IStrategy):
    source_file = '牛市力量交易策略Bull-Power-Trading-Strategy.md'
    timeframe = '1h'
    can_short = True
    source_defaults = {'SellLevel': 40, 'BuyLevel': 3, 'reverse': False}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.entry']
    source_fidelity_notes = []
    pine_assignments = [{'mode': '', 'name': 'SellLevel', 'op': '=', 'expr': 'input(40, step=0.01)', 'conditions': []}, {'mode': '', 'name': 'BuyLevel', 'op': '=', 'expr': 'input(3, step=0.01)', 'conditions': []}, {'mode': '', 'name': 'reverse', 'op': '=', 'expr': 'input(false, title="Trade reverse")', 'conditions': []}, {'mode': '', 'name': 'value', 'op': '=', 'expr': 'iff (close < open , iff (close[1] < open , max(high - close[1], close - low), max(high - open, close - low)), iff (close > open, iff(close[1] > open, high - low, max(open - close[1], high - low)), iff(high - close > close - low, iff (close[1] < open, max(high - close[1], close - low), high - open), iff (high - close < close - low, iff(close[1] > open, high - low, max(open - close, high - low)), iff (close[1] > open, max(high - open, close - low), iff(close[1] < open, max(open - close, high - low), high - low))))))', 'conditions': []}, {'mode': '', 'name': 'pos', 'op': '=', 'expr': 'iff(value > SellLevel, -1, iff(value <= BuyLevel, 1, nz(pos[1], 0)))', 'conditions': []}, {'mode': '', 'name': 'possig', 'op': '=', 'expr': 'iff(reverse and pos == 1, -1, iff(reverse and pos == -1, 1, pos))', 'conditions': []}]
    pine_user_functions = []
    pine_controls = [{'indent': 0, 'statement': 'if (possig == -1)'}, {'indent': 0, 'statement': 'if (possig == 1)'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("Short", strategy.short)', 'conditions': ['(possig == -1)'], 'statement': 'strategy.entry("Short", strategy.short)'}, {'kind': 'entry', 'call': 'strategy.entry("Long", strategy.long)', 'conditions': ['(possig == 1)'], 'statement': 'strategy.entry("Long", strategy.long)'}]
    original_pine = '/*backtest\nstart: 2023-12-12 00:00:00\nend: 2024-01-11 00:00:00\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=2\n////////////////////////////////////////////////////////////\n//  Copyright by HPotter v1.0 30/01/2017\n//  Bull Power Indicator\n//  To get more information please see "Bull And Bear Balance Indicator" \n//  by Vadim Gimelfarb. \n////////////////////////////////////////////////////////////\nstrategy(title = "Bull Power Strategy")\nSellLevel = input(40, step=0.01)\nBuyLevel = input(3, step=0.01)\nreverse = input(false, title="Trade reverse")\nhline(SellLevel, color=red, linestyle=line)\nhline(BuyLevel, color=green, linestyle=line)\nvalue = iff (close < open ,  \n         iff (close[1] < open ,  max(high - close[1], close - low), max(high - open, close - low)),\n          iff (close > open, \n           iff(close[1] > open,  high - low, max(open - close[1], high - low)), \n             iff(high - close > close - low, \n              iff (close[1] < open, max(high - close[1], close - low), high - open), \n               iff (high - close < close - low, \n                 iff(close[1] > open,  high - low, max(open - close, high - low)), \n                  iff (close[1] > open, max(high - open, close - low),\n                   iff(close[1] < open, max(open - close, high - low), high - low))))))\npos = iff(value > SellLevel, -1,\n\t     iff(value <= BuyLevel, 1, nz(pos[1], 0))) \npossig = iff(reverse and pos == 1, -1,\n          iff(reverse and pos == -1, 1, pos))\nif (possig == -1) \n    strategy.entry("Short", strategy.short)\nif (possig == 1)\n    strategy.entry("Long", strategy.long)\nbarcolor(possig == -1 ? red: possig == 1 ? green : blue )\nplot(value, style=line, linewidth=2, color=blue)'

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
