"""Source-faithful deep-assisted port of 相对强度指数平盘反转策略Relative-Strength-Index-Flat-Reversal-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_0a61f3fc(PinePortBase, IStrategy):
    source_file = '相对强度指数平盘反转策略Relative-Strength-Index-Flat-Reversal-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'RSIlength': 14}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.entry', 'strategy.cancel', 'strategy.equity']
    source_fidelity_notes = ['Reads broker/strategy state; signals depend on fill timing and cannot be reduced to indicator-only booleans without changing behavior.']
    pine_assignments = [{'mode': '', 'name': 'RSIlength', 'op': '=', 'expr': 'input(14, minval=1, title="RSI Period Length")', 'conditions': []}, {'mode': '', 'name': 'RSIoverSold', 'op': '=', 'expr': '30', 'conditions': []}, {'mode': '', 'name': 'RSIoverBought', 'op': '=', 'expr': '70', 'conditions': []}, {'mode': '', 'name': 'RSITriggerLine', 'op': '=', 'expr': '30', 'conditions': []}, {'mode': '', 'name': 'RSI', 'op': '=', 'expr': 'rsi(close, RSIlength)', 'conditions': []}, {'mode': '', 'name': 'price', 'op': '=', 'expr': 'close', 'conditions': []}, {'mode': '', 'name': 'vrsi', 'op': '=', 'expr': 'rsi(price, RSIlength)', 'conditions': []}, {'mode': '', 'name': 'source', 'op': '=', 'expr': 'close', 'conditions': []}, {'mode': '', 'name': 'buyEntry', 'op': '=', 'expr': 'crossover(source, RSITriggerLine)', 'conditions': []}, {'mode': '', 'name': 'sellEntry', 'op': '=', 'expr': 'crossunder(source, RSITriggerLine)', 'conditions': []}, {'mode': '', 'name': 'p1', 'op': '=', 'expr': 'plot(RSIoverSold, color=green,title="30")', 'conditions': []}, {'mode': '', 'name': 'p2', 'op': '=', 'expr': 'plot(RSIoverBought, color=green,title="70")', 'conditions': []}, {'mode': '', 'name': 'p3', 'op': '=', 'expr': 'plot(RSITriggerLine, color=green,title="30")', 'conditions': []}]
    pine_user_functions = []
    pine_controls = [{'indent': 0, 'statement': 'if (not na(vrsi))'}, {'indent': 4, 'statement': 'if (crossover(RSI, RSITriggerLine))'}, {'indent': 4, 'statement': 'else'}, {'indent': 4, 'statement': 'if (crossunder(RSI, RSIoverBought))'}, {'indent': 4, 'statement': 'else'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("RSI_L", strategy.long, comment="RSI_L")', 'conditions': ['(not na(vrsi))', '(crossover(RSI, RSITriggerLine))'], 'statement': 'strategy.entry("RSI_L", strategy.long, comment="RSI_L")'}, {'kind': 'cancel', 'call': 'strategy.cancel(id="RSI_L")', 'conditions': ['(not na(vrsi))', 'ELSE'], 'statement': 'strategy.cancel(id="RSI_L")'}, {'kind': 'entry', 'call': 'strategy.entry("RSI_S", strategy.short, comment="RSI_S")', 'conditions': ['(not na(vrsi))', '(crossunder(RSI, RSIoverBought))'], 'statement': 'strategy.entry("RSI_S", strategy.short, comment="RSI_S")'}, {'kind': 'cancel', 'call': 'strategy.cancel(id="RSI_S")', 'conditions': ['(not na(vrsi))', 'ELSE'], 'statement': 'strategy.cancel(id="RSI_S")'}]
    original_pine = '/*backtest\nstart: 2022-11-20 00:00:00\nend: 2023-11-26 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=2\nstrategy("RSI OverTrend Strategy (by Marcoweb) v1.0", shorttitle="RSI_L_30_Strat_v1.0", overlay=true)\n\n///////////// RSI\nRSIlength = input(14, minval=1, title="RSI Period Length") \nRSIoverSold = 30\nRSIoverBought = 70\nRSITriggerLine = 30\n\nRSI = rsi(close, RSIlength)\nprice = close\nvrsi = rsi(price, RSIlength)\n\nsource = close\nbuyEntry = crossover(source, RSITriggerLine)\nsellEntry = crossunder(source, RSITriggerLine)\nplot(RSI, color=red,title="RSI")\np1 = plot(RSIoverSold, color=green,title="30")\np2 = plot(RSIoverBought, color=green,title="70")\np3 = plot(RSITriggerLine, color=green,title="30")\n\n\n///////////// RSI Level 30 v1.0 Strategy \nif (not na(vrsi))\n\n    if (crossover(RSI, RSITriggerLine))\n        strategy.entry("RSI_L", strategy.long,  comment="RSI_L")\n    else\n        strategy.cancel(id="RSI_L")\n        \n    if (crossunder(RSI, RSIoverBought))\n        strategy.entry("RSI_S", strategy.short,  comment="RSI_S")\n    else\n        strategy.cancel(id="RSI_S")\n        \n//plot(strategy.equity, title="equity", color=red, linewidth=2, style=areabr)'

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
