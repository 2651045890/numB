"""Source-faithful deep-assisted port of 确认发散策略Confirmed-Divergence-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_e07e1d44(PinePortBase, IStrategy):
    source_file = '确认发散策略Confirmed-Divergence-Strategy.md'
    timeframe = '1h'
    can_short = True
    source_defaults = {'length': 30, 'mult': 2.0, 'rsiprd': 14, 'ob': 70, 'os': 30, 'lengthAO1': 5, 'lengthAO2': 34, 'x': 5, 'z': 25}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.entry', 'strategy.close', 'strategy.cancel', 'strategy.equity']
    source_fidelity_notes = ['Reads broker/strategy state; signals depend on fill timing and cannot be reduced to indicator-only booleans without changing behavior.']
    pine_assignments = [{'mode': '', 'name': 'source', 'op': '=', 'expr': 'close', 'conditions': []}, {'mode': '', 'name': 'length', 'op': '=', 'expr': 'input(30, minval=1)', 'conditions': []}, {'mode': '', 'name': 'mult', 'op': '=', 'expr': 'input(2.0, minval=0.001, maxval=50)', 'conditions': []}, {'mode': '', 'name': 'src', 'op': '=', 'expr': 'close', 'conditions': []}, {'mode': '', 'name': 'rsiprd', 'op': '=', 'expr': 'input(title="RSI period",defval=14)', 'conditions': []}, {'mode': '', 'name': 'rv', 'op': '=', 'expr': 'rsi(src,rsiprd)', 'conditions': []}, {'mode': '', 'name': 'ob', 'op': '=', 'expr': 'input(title="Overbought Level", defval=70)', 'conditions': []}, {'mode': '', 'name': 'os', 'op': '=', 'expr': 'input(title="Oversold Level", defval=30)', 'conditions': []}, {'mode': '', 'name': 'lengthAO1', 'op': '=', 'expr': 'input(title="Awesome Short MA", defval=5, minval=1) //5 periods', 'conditions': []}, {'mode': '', 'name': 'lengthAO2', 'op': '=', 'expr': 'input(title="Awesome Long MA", defval=34, minval=1) //34 periods', 'conditions': []}, {'mode': '', 'name': 'AO', 'op': '=', 'expr': 'sma((high+low)/2, lengthAO1) - sma((high+low)/2, lengthAO2)', 'conditions': []}, {'mode': '', 'name': 'x', 'op': '=', 'expr': 'input(title = "short lookback period",defval=5)', 'conditions': []}, {'mode': '', 'name': 'z', 'op': '=', 'expr': 'input(title = "long lookback period",defval=25)', 'conditions': []}, {'mode': '', 'name': 'srcLL', 'op': '=', 'expr': 'src > lowest(src,x) and lowest(src,x)<lowest(src,z)[x]', 'conditions': []}, {'mode': '', 'name': 'rsiHL', 'op': '=', 'expr': 'rv>lowest(rv,x) and lowest(rv,x) > lowest(rv,z)[x] and lowest(rv,z)<os', 'conditions': []}, {'mode': '', 'name': 'aoHL', 'op': '=', 'expr': 'AO > lowest(AO,x) and lowest(AO,x) > lowest(AO,z)[x] and lowest(AO, x) < 0', 'conditions': []}, {'mode': '', 'name': 'BullishDiv', 'op': '=', 'expr': 'srcLL and rsiHL and aoHL', 'conditions': []}, {'mode': '', 'name': 'srcHH', 'op': '=', 'expr': 'src < highest(src,x) and highest(src,x)>highest(src,z)[x]', 'conditions': []}, {'mode': '', 'name': 'rsiLH', 'op': '=', 'expr': 'rv<highest(rv,x) and highest(rv,x) < highest(rv,z)[x] and highest(rv,z)>ob', 'conditions': []}, {'mode': '', 'name': 'aoLH', 'op': '=', 'expr': 'AO<highest(AO,x) and highest(AO,x) < highest(AO,z)[x] and highest(AO, x) > 0', 'conditions': []}, {'mode': '', 'name': 'BearishDiv', 'op': '=', 'expr': 'srcHH and rsiLH and aoLH', 'conditions': []}, {'mode': '', 'name': 'basis', 'op': '=', 'expr': 'sma(source, length)', 'conditions': []}, {'mode': '', 'name': 'dev', 'op': '=', 'expr': 'mult * stdev(source, length)', 'conditions': []}, {'mode': '', 'name': 'upper', 'op': '=', 'expr': 'basis + dev', 'conditions': []}, {'mode': '', 'name': 'lower', 'op': '=', 'expr': 'basis - dev', 'conditions': []}]
    pine_user_functions = []
    pine_controls = [{'indent': 0, 'statement': 'if (BullishDiv)'}, {'indent': 0, 'statement': 'else'}, {'indent': 0, 'statement': 'if (crossover(close, lower))'}, {'indent': 0, 'statement': 'if (crossunder(close, upper))'}, {'indent': 0, 'statement': 'if (BearishDiv)'}, {'indent': 0, 'statement': 'else'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("DivLE", strategy.long, stop=lower, oca_name="BullishDiv",comment="DivLE")', 'conditions': ['(BullishDiv)'], 'statement': 'strategy.entry("DivLE", strategy.long, stop=lower, oca_name="BullishDiv",comment="DivLE")'}, {'kind': 'cancel', 'call': 'strategy.cancel(id="DivLE")', 'conditions': ['ELSE'], 'statement': 'strategy.cancel(id="DivLE")'}, {'kind': 'close', 'call': 'strategy.close("DivSE")', 'conditions': ['(crossover(close, lower))'], 'statement': 'strategy.close("DivSE")'}, {'kind': 'close', 'call': 'strategy.close("DivLE")', 'conditions': ['(crossunder(close, upper))'], 'statement': 'strategy.close("DivLE")'}, {'kind': 'entry', 'call': 'strategy.entry("DivSE", strategy.short, stop=upper, oca_name="BearishDiv",comment="DivSE")', 'conditions': ['(BearishDiv)'], 'statement': 'strategy.entry("DivSE", strategy.short, stop=upper, oca_name="BearishDiv",comment="DivSE")'}, {'kind': 'cancel', 'call': 'strategy.cancel(id="DivSE")', 'conditions': ['ELSE'], 'statement': 'strategy.cancel(id="DivSE")'}]
    original_pine = '/*backtest\nstart: 2023-12-15 00:00:00\nend: 2024-01-14 00:00:00\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=3\nstrategy("Confirmed Divergence Strategy", overlay=true)\nsource = close\nlength = input(30, minval=1)\nmult = input(2.0, minval=0.001, maxval=50)\n// SETTING UP VARIABLES //\n\nsrc = close\n\n// RSI //\nrsiprd = input(title="RSI period",defval=14)\nrv = rsi(src,rsiprd)\nob = input(title="Overbought Level",  defval=70)\nos = input(title="Oversold Level",  defval=30)\nlengthAO1=input(title="Awesome Short MA", defval=5, minval=1) //5 periods\nlengthAO2=input(title="Awesome Long MA", defval=34, minval=1) //34 periods\n\n\n//Awesome//\n\nAO = sma((high+low)/2, lengthAO1) - sma((high+low)/2, lengthAO2)\n\n// look back periods //\nx = input(title = "short lookback period",defval=5)\nz = input(title = "long lookback period",defval=25)\n\n\n// END SETUP //\n\n////////////////////////\n// BULLISH DIVERGENCE //\n////////////////////////\n\n// define lower low in price //\n\nsrcLL = src > lowest(src,x) and  lowest(src,x)<lowest(src,z)[x]\n\n// define higher low in rsi //\n\nrsiHL = rv>lowest(rv,x) and lowest(rv,x) > lowest(rv,z)[x] and lowest(rv,z)<os\n\n// define higher low in AO //\n\n\naoHL = AO > lowest(AO,x) and lowest(AO,x) > lowest(AO,z)[x] and lowest(AO, x) < 0\n\n\n\nBullishDiv = srcLL and rsiHL and aoHL\n\n\n////////////////////////\n// BEARISH DIVERGENCE //\n////////////////////////\n\n// define higher high in price //\n\nsrcHH = src < highest(src,x) and  highest(src,x)>highest(src,z)[x]\n\n// define lower high in RSI //\n\nrsiLH = rv<highest(rv,x) and highest(rv,x) < highest(rv,z)[x] and highest(rv,z)>ob\n\n// define lower high in AO //\naoLH = AO<highest(AO,x) and highest(AO,x) < highest(AO,z)[x] and highest(AO, x) > 0\n\nBearishDiv = srcHH and rsiLH and aoLH\n\n\nbasis = sma(source, length)\ndev = mult * stdev(source, length)\n\nupper = basis + dev\nlower = basis - dev\n\n\n\nif (BullishDiv)\n    strategy.entry("DivLE", strategy.long, stop=lower, oca_name="BullishDiv",comment="DivLE")\nelse\n    strategy.cancel(id="DivLE")\n    \nif (crossover(close, lower))\n    strategy.close("DivSE")\n    \nif (crossunder(close, upper))\n    strategy.close("DivLE")\n\nif (BearishDiv)\n    strategy.entry("DivSE", strategy.short, stop=upper, oca_name="BearishDiv",comment="DivSE")\nelse\n    strategy.cancel(id="DivSE")\n\n//plot(strategy.equity, title="equity", color=red, linewidth=2, style=areabr)'

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
