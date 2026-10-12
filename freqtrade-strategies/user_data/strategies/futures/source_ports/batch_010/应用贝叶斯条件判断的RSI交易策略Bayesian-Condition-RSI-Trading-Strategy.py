"""Source-faithful deep-assisted port of 应用贝叶斯条件判断的RSI交易策略Bayesian-Condition-RSI-Trading-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_de5fe126(PinePortBase, IStrategy):
    source_file = '应用贝叶斯条件判断的RSI交易策略Bayesian-Condition-RSI-Trading-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'p': 30, 't': 1.003, 'r': 7, 'RSIT': 8, 'BAYEST': 3, 'RSIP': 14}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.entry', 'for ']
    source_fidelity_notes = []
    pine_assignments = [{'mode': '', 'name': 'p', 'op': '=', 'expr': 'input(title="Period", defval=30, minval=5, maxval=500)', 'conditions': []}, {'mode': '', 'name': 't', 'op': '=', 'expr': 'input(title="Movement Thresh", type=float, defval=1.003, minval=1.001, maxval=1.5, step=0.001)', 'conditions': []}, {'mode': '', 'name': 'r', 'op': '=', 'expr': 'input(title="Look Range", defval=7, minval=1,maxval=500, step=1)', 'conditions': []}, {'mode': '', 'name': 'RSIT', 'op': '=', 'expr': 'input(title="Jump", defval=8, minval=1,maxval=99, step=1)', 'conditions': []}, {'mode': '', 'name': 'BAYEST', 'op': '=', 'expr': 'input(title="SM", defval=3, minval=1,maxval=99, step=1)', 'conditions': []}, {'mode': '', 'name': 'RSIP', 'op': '=', 'expr': 'input(title="RSIP", defval=14, minval=2,maxval=100, step=1)', 'conditions': []}, {'mode': '', 'name': 'countup', 'op': '=', 'expr': '1', 'conditions': []}, {'mode': '', 'name': 'countdn', 'op': '=', 'expr': '1', 'conditions': []}, {'mode': '', 'name': 'countupS', 'op': '=', 'expr': '1', 'conditions': []}, {'mode': '', 'name': 'countdnS', 'op': '=', 'expr': '1', 'conditions': []}, {'mode': '', 'name': 'countup', 'op': ':=', 'expr': 'countup + 1', 'conditions': ['close[i]/close[i + r] > t']}, {'mode': '', 'name': 'countdn', 'op': ':=', 'expr': 'countdn + 1', 'conditions': ['ELSE']}, {'mode': '', 'name': 'countupS', 'op': ':=', 'expr': 'countupS + 1', 'conditions': ['close[i]/close[i + r] < 2 - t']}, {'mode': '', 'name': 'countdnS', 'op': ':=', 'expr': 'countdnS + 1', 'conditions': ['ELSE']}, {'mode': '', 'name': 'rsi', 'op': '=', 'expr': 'rsi(open,RSIP)', 'conditions': []}, {'mode': '', 'name': 'countup2', 'op': '=', 'expr': '1', 'conditions': []}, {'mode': '', 'name': 'countup3', 'op': '=', 'expr': '1', 'conditions': []}, {'mode': '', 'name': 'countup2S', 'op': '=', 'expr': '1', 'conditions': []}, {'mode': '', 'name': 'countup3S', 'op': '=', 'expr': '1', 'conditions': []}, {'mode': '', 'name': 'countup2', 'op': ':=', 'expr': 'countup2 + 1', 'conditions': ['close[i]/close[i + r] > t and rsi[i + r + 1] > rsi[i + r + 2] + RSIT']}, {'mode': '', 'name': 'countup3', 'op': ':=', 'expr': 'countup3 + 1', 'conditions': ['ELSE']}, {'mode': '', 'name': 'countup2S', 'op': ':=', 'expr': 'countup2S + 1', 'conditions': ['close[i]/close[i + r] < 2 - t and rsi[i + r + 1] < rsi[i + r + 2] - RSIT']}, {'mode': '', 'name': 'countup3S', 'op': ':=', 'expr': 'countup3S + 1', 'conditions': ['ELSE']}, {'mode': '', 'name': 'countup2b', 'op': '=', 'expr': 'countup2 / p', 'conditions': []}, {'mode': '', 'name': 'countup3b', 'op': '=', 'expr': 'countup3 / p', 'conditions': []}, {'mode': '', 'name': 'countupb', 'op': '=', 'expr': 'countup / p', 'conditions': []}, {'mode': '', 'name': 'countdnb', 'op': '=', 'expr': 'countdn / p', 'conditions': []}, {'mode': '', 'name': 'countup2bS', 'op': '=', 'expr': 'countup2S / p', 'conditions': []}, {'mode': '', 'name': 'countup3bS', 'op': '=', 'expr': 'countup3S / p', 'conditions': []}, {'mode': '', 'name': 'countupbS', 'op': '=', 'expr': 'countupS / p', 'conditions': []}, {'mode': '', 'name': 'countdnbS', 'op': '=', 'expr': 'countdnS / p', 'conditions': []}, {'mode': '', 'name': 'bayes', 'op': '=', 'expr': '0', 'conditions': []}, {'mode': '', 'name': 'bayes', 'op': ':=', 'expr': '((countupb * countup2b) / ((countupb * countup2b) + (countdnb * countup3b))) * 100', 'conditions': []}, {'mode': '', 'name': 'bayesS', 'op': '=', 'expr': '0', 'conditions': []}, {'mode': '', 'name': 'bayesS', 'op': ':=', 'expr': '((countupbS * countup2bS) / ((countupbS * countup2bS) + (countdnbS * countup3bS))) * 100', 'conditions': []}, {'mode': '', 'name': 'SN1', 'op': '=', 'expr': 'sma(bayes,BAYEST)', 'conditions': []}, {'mode': '', 'name': 'SN2', 'op': '=', 'expr': 'sma(bayesS,BAYEST)', 'conditions': []}, {'mode': '', 'name': 'shortCondition', 'op': '=', 'expr': 'crossunder(bayesS, SN2) //and rsi < 49', 'conditions': []}, {'mode': '', 'name': 'longCondition', 'op': '=', 'expr': 'crossover(bayes, SN1) //and rsi > 59', 'conditions': []}]
    pine_user_functions = []
    pine_controls = [{'indent': 0, 'statement': 'for i = p to 1'}, {'indent': 4, 'statement': 'if close[i]/close[i + r] > t'}, {'indent': 4, 'statement': 'else'}, {'indent': 4, 'statement': 'if close[i]/close[i + r] < 2 - t'}, {'indent': 4, 'statement': 'else'}, {'indent': 0, 'statement': 'for i = p to 1'}, {'indent': 4, 'statement': 'if close[i]/close[i + r] > t and rsi[i + r + 1] > rsi[i + r + 2] + RSIT'}, {'indent': 4, 'statement': 'else'}, {'indent': 4, 'statement': 'if close[i]/close[i + r] < 2 - t and rsi[i + r + 1] < rsi[i + r + 2] - RSIT'}, {'indent': 4, 'statement': 'else'}, {'indent': 0, 'statement': 'if (longCondition)'}, {'indent': 0, 'statement': 'if (shortCondition)'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("Long", strategy.long)', 'conditions': ['(longCondition)'], 'statement': 'strategy.entry("Long", strategy.long)'}, {'kind': 'entry', 'call': 'strategy.entry("Short", strategy.short)', 'conditions': ['(shortCondition)'], 'statement': 'strategy.entry("Short", strategy.short)'}]
    original_pine = '/*backtest\nstart: 2022-12-11 00:00:00\nend: 2023-03-15 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=2\n// Stealthy7 trading scripts are radikal. You have entered the mystical realm of demonic profit.\n// If you like this script, check out my bots at cryptotrader.org/?r=51\n// Let me know if you find any improvements to this script. It is beta. \n// Please subscribe.\nstrategy("Stealthy7 Bayes Conditional RSI Trader Strategy", overlay=true)\np = input(title="Period",  defval=30, minval=5, maxval=500)\nt = input(title="Movement Thresh", type=float, defval=1.003, minval=1.001, maxval=1.5, step=0.001)\nr = input(title="Look Range",  defval=7, minval=1,maxval=500, step=1)\nRSIT = input(title="Jump",  defval=8, minval=1,maxval=99, step=1)\nBAYEST = input(title="SM",  defval=3, minval=1,maxval=99, step=1)\nRSIP = input(title="RSIP",  defval=14, minval=2,maxval=100, step=1)\ncountup = 1\ncountdn = 1\ncountupS = 1\ncountdnS = 1\nfor i = p to 1\n    if close[i]/close[i + r] > t\n        countup := countup + 1\n    else\n        countdn := countdn + 1\n    if close[i]/close[i + r] < 2 - t\n        countupS := countupS + 1\n    else\n        countdnS := countdnS + 1\n\nrsi = rsi(open,RSIP)\n\ncountup2 = 1\ncountup3 = 1\ncountup2S = 1\ncountup3S = 1\nfor i = p to 1\n    if close[i]/close[i + r] > t and rsi[i + r + 1] > rsi[i + r + 2] + RSIT\n        countup2 := countup2 + 1\n    else\n        countup3 := countup3 + 1\n    if close[i]/close[i + r] < 2 - t and rsi[i + r + 1] < rsi[i + r + 2] - RSIT\n        countup2S := countup2S + 1\n    else\n        countup3S := countup3S + 1\n\ncountup2b = countup2 / p\ncountup3b = countup3 / p\ncountupb = countup / p\ncountdnb = countdn / p\n\ncountup2bS = countup2S / p\ncountup3bS = countup3S / p\ncountupbS = countupS / p\ncountdnbS = countdnS / p\nbayes = 0\nbayes := ((countupb * countup2b) / ((countupb * countup2b) + (countdnb * countup3b))) * 100\nbayesS = 0\nbayesS := ((countupbS * countup2bS) / ((countupbS * countup2bS) + (countdnbS * countup3bS))) * 100\nSN1 = sma(bayes,BAYEST)\nSN2 = sma(bayesS,BAYEST)\nshortCondition = crossunder(bayesS, SN2) //and rsi < 49\nlongCondition = crossover(bayes, SN1) //and rsi > 59\nif (longCondition)\n    strategy.entry("Long", strategy.long)\nif (shortCondition)\n    strategy.entry("Short", strategy.short)'

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
