"""Source-faithful deep-assisted port of 底部跟随交易策略Bottom-Following-Trading-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_be6308c7(PinePortBase, IStrategy):
    source_file = '底部跟随交易策略Bottom-Following-Trading-Strategy.md'
    timeframe = '1h'
    can_short = True
    source_defaults = {}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 100.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.entry']
    source_fidelity_notes = []
    pine_assignments = [{'mode': '', 'name': 'src', 'op': '=', 'expr': 'close', 'conditions': []}, {'mode': '', 'name': 'fastup', 'op': '=', 'expr': 'rma(max(change(src), 0), 2)', 'conditions': []}, {'mode': '', 'name': 'fastdown', 'op': '=', 'expr': 'rma(-min(change(src), 0), 2)', 'conditions': []}, {'mode': '', 'name': 'fastrsi', 'op': '=', 'expr': 'fastdown == 0 ? 100 : fastup == 0 ? 0 : 100 - (100 / (1 + fastup / fastdown))', 'conditions': []}, {'mode': '', 'name': 'mac', 'op': '=', 'expr': 'sma(close, 10)', 'conditions': []}, {'mode': '', 'name': 'len', 'op': '=', 'expr': 'abs(close - mac)', 'conditions': []}, {'mode': '', 'name': 'sma', 'op': '=', 'expr': 'sma(len, 100)', 'conditions': []}, {'mode': '', 'name': 'max', 'op': '=', 'expr': 'max(open, close)', 'conditions': []}, {'mode': '', 'name': 'min', 'op': '=', 'expr': 'min(open, close)', 'conditions': []}, {'mode': '', 'name': 'up', 'op': '=', 'expr': 'close < open and len > sma * 3 and min < min[1] and fastrsi < 10 ? 1 : 0', 'conditions': []}, {'mode': '', 'name': 'sell', 'op': '=', 'expr': 'sma(close, 5)', 'conditions': []}, {'mode': '', 'name': 'dn', 'op': '=', 'expr': 'high > sell ? 1 : 0', 'conditions': []}, {'mode': '', 'name': 'longCondition', 'op': '=', 'expr': 'up == 1', 'conditions': []}, {'mode': '', 'name': 'shortCondition', 'op': '=', 'expr': 'dn == 1', 'conditions': []}]
    pine_user_functions = []
    pine_controls = [{'indent': 0, 'statement': 'if (longCondition)'}, {'indent': 0, 'statement': 'if (shortCondition)'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("Long", strategy.long)', 'conditions': ['(longCondition)'], 'statement': 'strategy.entry("Long", strategy.long)'}, {'kind': 'entry', 'call': 'strategy.entry("Exit", strategy.short, 0)', 'conditions': ['(shortCondition)'], 'statement': 'strategy.entry("Exit", strategy.short, 0)'}]
    original_pine = '/*backtest\nstart: 2023-08-16 00:00:00\nend: 2023-09-15 00:00:00\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=3\nstrategy("Noro\'s CryptoBottom Strategy", shorttitle = "CryptoBottom str", overlay = true, default_qty_type = strategy.percent_of_equity, default_qty_value=100.0, pyramiding=0)\n\n//Fast RSI\nsrc = close\nfastup = rma(max(change(src), 0), 2)\nfastdown = rma(-min(change(src), 0), 2)\nfastrsi = fastdown == 0 ? 100 : fastup == 0 ? 0 : 100 - (100 / (1 + fastup / fastdown))\n\nmac = sma(close, 10)\nlen = abs(close - mac)\nsma = sma(len, 100)\nmax = max(open, close)\nmin = min(open, close)\nup = close < open and len > sma * 3 and min < min[1] and fastrsi < 10 ? 1 : 0\n//dn = close > open and len > sma * 3 and max > max[1] and fastrsi > 90 ? 1 : 0\nplotarrow(up == 1 ? 1 : na, colorup = blue, colordown = blue)\n//plotarrow(dn == 1 ? -1 : na, colorup = blue, colordown = blue)\n\nsell = sma(close, 5)\ndn = high > sell ? 1 : 0\nplot(sell)\n\nlongCondition = up == 1\nif (longCondition)\n    strategy.entry("Long", strategy.long)\n\nshortCondition = dn == 1\nif (shortCondition)\n    strategy.entry("Exit", strategy.short, 0)'

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
