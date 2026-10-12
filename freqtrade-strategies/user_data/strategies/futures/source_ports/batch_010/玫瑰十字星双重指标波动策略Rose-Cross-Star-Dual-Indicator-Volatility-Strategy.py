"""Source-faithful deep-assisted port of 玫瑰十字星双重指标波动策略Rose-Cross-Star-Dual-Indicator-Volatility-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_4c5020c0(PinePortBase, IStrategy):
    source_file = '玫瑰十字星双重指标波动策略Rose-Cross-Star-Dual-Indicator-Volatility-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'length': 20, 'mult': 2.0}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.entry', 'strategy.close']
    source_fidelity_notes = []
    pine_assignments = [{'mode': '', 'name': 'src', 'op': '=', 'expr': 'close', 'conditions': []}, {'mode': '', 'name': 'length', 'op': '=', 'expr': 'input(20, title="Longitud", minval=1)', 'conditions': []}, {'mode': '', 'name': 'mult', 'op': '=', 'expr': 'input(2.0)', 'conditions': []}, {'mode': '', 'name': 'basis', 'op': '=', 'expr': 'sma(src, length)', 'conditions': []}, {'mode': '', 'name': 'upper', 'op': '=', 'expr': 'basis + mult * stdev(src, length)', 'conditions': []}, {'mode': '', 'name': 'lower', 'op': '=', 'expr': 'basis - mult * stdev(src, length)', 'conditions': []}, {'mode': '', 'name': 'rsiSource', 'op': '=', 'expr': 'rsi(close, 14)', 'conditions': []}, {'mode': '', 'name': 'overbought', 'op': '=', 'expr': '70', 'conditions': []}, {'mode': '', 'name': 'oversold', 'op': '=', 'expr': '30', 'conditions': []}, {'mode': '', 'name': 'longCondition', 'op': '=', 'expr': 'crossover(src, lower) and rsiSource < oversold', 'conditions': []}, {'mode': '', 'name': 'shortCondition', 'op': '=', 'expr': 'crossunder(src, upper) and rsiSource > overbought', 'conditions': []}, {'mode': '', 'name': 'longExit', 'op': '=', 'expr': 'crossunder(src, upper)', 'conditions': []}, {'mode': '', 'name': 'shortExit', 'op': '=', 'expr': 'crossover(src, lower)', 'conditions': []}]
    pine_user_functions = []
    pine_controls = [{'indent': 0, 'statement': 'if (longCondition)'}, {'indent': 0, 'statement': 'if (shortCondition)'}, {'indent': 0, 'statement': 'if (longExit)'}, {'indent': 0, 'statement': 'if (shortExit)'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("Compra", strategy.long, stop=low)', 'conditions': ['(longCondition)'], 'statement': 'strategy.entry("Compra", strategy.long, stop=low)'}, {'kind': 'entry', 'call': 'strategy.entry("Venta", strategy.short, stop=high)', 'conditions': ['(shortCondition)'], 'statement': 'strategy.entry("Venta", strategy.short, stop=high)'}, {'kind': 'close', 'call': 'strategy.close("Compra")', 'conditions': ['(longExit)'], 'statement': 'strategy.close("Compra")'}, {'kind': 'close', 'call': 'strategy.close("Venta")', 'conditions': ['(shortExit)'], 'statement': 'strategy.close("Venta")'}]
    original_pine = '/*backtest\nstart: 2022-10-24 00:00:00\nend: 2023-10-30 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=4\nstrategy("Estrategia de Ruptura con Bollinger y RSI Modificada", shorttitle="BB RSI Mod", overlay=true)\n\n// Parámetros de Bollinger Bands\nsrc = close\nlength = input(20, title="Longitud", minval=1)\nmult = input(2.0)\nbasis = sma(src, length)\nupper = basis + mult * stdev(src, length)\nlower = basis - mult * stdev(src, length)\n\n// Parámetros del RSI\nrsiSource = rsi(close, 14)\noverbought = 70\noversold = 30\n\nlongCondition = crossover(src, lower) and rsiSource < oversold\nshortCondition = crossunder(src, upper) and rsiSource > overbought\n\nlongExit = crossunder(src, upper)\nshortExit = crossover(src, lower)\n\nif (longCondition)\n    strategy.entry("Compra", strategy.long, stop=low)\n    \nif (shortCondition)\n    strategy.entry("Venta", strategy.short, stop=high)\n\nif (longExit)\n    strategy.close("Compra")\n\nif (shortExit)\n    strategy.close("Venta")\n\n// Visualización\nplotshape(series=longCondition, title="Compra", location=location.belowbar, color=color.green, style=shape.labelup, text="Compra")\nplotshape(series=shortCondition, title="Venta", location=location.abovebar, color=color.red, style=shape.labeldown, text="Venta")\nplot(upper, "Banda Superior", color=color.red)\nplot(lower, "Banda Inferior", color=color.green)'

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
