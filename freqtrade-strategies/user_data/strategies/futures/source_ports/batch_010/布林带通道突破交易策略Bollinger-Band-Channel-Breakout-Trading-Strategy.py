"""Source-faithful deep-assisted port of 布林带通道突破交易策略Bollinger-Band-Channel-Breakout-Trading-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_e8e65519(PinePortBase, IStrategy):
    source_file = '布林带通道突破交易策略Bollinger-Band-Channel-Breakout-Trading-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'length': 45, 'mult': 2.5}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 100.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.entry', 'strategy.cancel']
    source_fidelity_notes = []
    pine_assignments = [{'mode': '', 'name': 'source', 'op': '=', 'expr': 'close', 'conditions': []}, {'mode': '', 'name': 'length', 'op': '=', 'expr': 'input(45, minval=1)', 'conditions': []}, {'mode': '', 'name': 'mult', 'op': '=', 'expr': 'input(2.5, minval=0.001, maxval=50)', 'conditions': []}, {'mode': '', 'name': 'basis', 'op': '=', 'expr': 'sma(source, length)', 'conditions': []}, {'mode': '', 'name': 'dev', 'op': '=', 'expr': 'mult * stdev(source, length)', 'conditions': []}, {'mode': '', 'name': 'upper', 'op': '=', 'expr': 'basis + dev', 'conditions': []}, {'mode': '', 'name': 'lower', 'op': '=', 'expr': 'basis - dev', 'conditions': []}, {'mode': '', 'name': 'buyEntry', 'op': '=', 'expr': 'crossover(source, lower)', 'conditions': []}, {'mode': '', 'name': 'sellEntry', 'op': '=', 'expr': 'crossunder(source, upper)', 'conditions': []}]
    pine_user_functions = []
    pine_controls = [{'indent': 0, 'statement': 'if (crossover(source, lower))'}, {'indent': 0, 'statement': 'else'}, {'indent': 0, 'statement': 'if (crossunder(source, upper))'}, {'indent': 0, 'statement': 'else'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("BBandLE", strategy.long, stop=lower, oca_name="BollingerBands", comment="BBandLE")', 'conditions': ['(crossover(source, lower))'], 'statement': 'strategy.entry("BBandLE", strategy.long, stop=lower, oca_name="BollingerBands", comment="BBandLE")'}, {'kind': 'cancel', 'call': 'strategy.cancel(id="BBandLE")', 'conditions': ['ELSE'], 'statement': 'strategy.cancel(id="BBandLE")'}, {'kind': 'entry', 'call': 'strategy.entry("BBandSE", strategy.short, stop=upper, oca_name="BollingerBands", comment="BBandSE")', 'conditions': ['(crossunder(source, upper))'], 'statement': 'strategy.entry("BBandSE", strategy.short, stop=upper, oca_name="BollingerBands", comment="BBandSE")'}, {'kind': 'cancel', 'call': 'strategy.cancel(id="BBandSE")', 'conditions': ['ELSE'], 'statement': 'strategy.cancel(id="BBandSE")'}]
    original_pine = '/*backtest\nstart: 2022-09-05 00:00:00\nend: 2023-09-11 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=3\nstrategy("Kozlod - BB Strategy - 1 minute", overlay=true, default_qty_type = strategy.percent_of_equity, default_qty_value = 100)\n\n// \n// author: Kozlod\n// date: 2019-05-27\n// RSI - BTCUSDT - 1m\n// https://www.tradingview.com/u/Kozlod/\n// https://t.me/quantnomad\n//\n\nsource = close\nlength = input(45, minval=1)\nmult = input(2.5, minval=0.001, maxval=50)\n\nbasis = sma(source, length)\ndev = mult * stdev(source, length)\n\nupper = basis + dev\nlower = basis - dev\n\nplot(upper)\nplot(lower)\n\nbuyEntry  = crossover(source, lower)\nsellEntry = crossunder(source, upper)\n\nif (crossover(source, lower))\n    strategy.entry("BBandLE", strategy.long, stop=lower, oca_name="BollingerBands",  comment="BBandLE")\nelse\n    strategy.cancel(id="BBandLE")\n\nif (crossunder(source, upper))\n    strategy.entry("BBandSE", strategy.short, stop=upper, oca_name="BollingerBands",  comment="BBandSE")\nelse\n    strategy.cancel(id="BBandSE")'

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
