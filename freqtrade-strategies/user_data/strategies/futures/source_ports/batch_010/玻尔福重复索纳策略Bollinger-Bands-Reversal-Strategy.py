"""Source-faithful deep-assisted port of 玻尔福重复索纳策略Bollinger-Bands-Reversal-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_a6d57830(PinePortBase, IStrategy):
    source_file = '玻尔福重复索纳策略Bollinger-Bands-Reversal-Strategy.md'
    timeframe = '1d'
    can_short = False
    source_defaults = {'length': 55, 'maType': 'SMA', 'src': 'close', 'mult': 1.0, 'offset': 0}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.entry', 'strategy.close', 'switch', '=>']
    source_fidelity_notes = []
    pine_assignments = [{'mode': '', 'name': 'length', 'op': '=', 'expr': 'input.int(55, minval=1)', 'conditions': []}, {'mode': '', 'name': 'maType', 'op': '=', 'expr': 'input.string("SMA", "Basis MA Type", options = ["SMA", "EMA", "SMMA (RMA)", "WMA", "VWMA"])', 'conditions': []}, {'mode': '', 'name': 'src', 'op': '=', 'expr': 'input(close, title="Source")', 'conditions': []}, {'mode': '', 'name': 'mult', 'op': '=', 'expr': 'input.float(1., minval=0.001, maxval=50, title="StdDev")', 'conditions': []}, {'mode': '', 'name': 'basis', 'op': '=', 'expr': 'ma(src, length, maType)', 'conditions': []}, {'mode': '', 'name': 'dev', 'op': '=', 'expr': 'mult * ta.stdev(src, length)', 'conditions': []}, {'mode': '', 'name': 'upper', 'op': '=', 'expr': 'basis + dev', 'conditions': []}, {'mode': '', 'name': 'lower', 'op': '=', 'expr': 'basis - dev', 'conditions': []}, {'mode': '', 'name': 'enterCondition', 'op': '=', 'expr': '(close > lower and open < lower and close > open) or (close > upper and open < upper and close > open)', 'conditions': []}, {'mode': '', 'name': 'exitCondition', 'op': '=', 'expr': '(close < upper and open > upper) or (close > open and (upper - lower) > 2 * basis) or (close < lower)', 'conditions': []}, {'mode': '', 'name': 'offset', 'op': '=', 'expr': 'input.int(0, "Offset", minval = -500, maxval = 500)', 'conditions': []}, {'mode': '', 'name': 'p1', 'op': '=', 'expr': 'plot(upper, "Upper", color=#2962FF, offset = offset)', 'conditions': []}, {'mode': '', 'name': 'p2', 'op': '=', 'expr': 'plot(lower, "Lower", color=#2962FF, offset = offset)', 'conditions': []}]
    pine_user_functions = [{'name': 'ma', 'args': 'source, length, _type', 'body': ''}]
    pine_controls = [{'indent': 4, 'statement': 'switch _type'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("Long", strategy.long, when=enterCondition)', 'conditions': [], 'statement': 'strategy.entry("Long", strategy.long, when=enterCondition)'}, {'kind': 'close', 'call': 'strategy.close("Long", when=exitCondition)', 'conditions': [], 'statement': 'strategy.close("Long", when=exitCondition)'}]
    original_pine = '/*backtest\nstart: 2023-02-13 00:00:00\nend: 2024-02-19 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("BB Strategy", shorttitle="BB", overlay=true)\n\nlength = input.int(55, minval=1)\nmaType = input.string("SMA", "Basis MA Type", options = ["SMA", "EMA", "SMMA (RMA)", "WMA", "VWMA"])\nsrc = input(close, title="Source")\nmult = input.float(1., minval=0.001, maxval=50, title="StdDev")\n\nma(source, length, _type) =>\n    switch _type\n        "SMA" => ta.sma(source, length)\n        "EMA" => ta.ema(source, length)\n        "SMMA (RMA)" => ta.rma(source, length)\n        "WMA" => ta.wma(source, length)\n        "VWMA" => ta.vwma(source, length)\n\nbasis = ma(src, length, maType)\ndev = mult * ta.stdev(src, length)\nupper = basis + dev\nlower = basis - dev\n\n// Entry conditions\nenterCondition = (close > lower and open < lower and close > open) or (close > upper and open < upper and close > open)\n\n// Exit conditions\nexitCondition = (close < upper and open > upper) or (close > open and (upper - lower) > 2 * basis) or (close < lower)\n\nstrategy.entry("Long", strategy.long, when=enterCondition)\nstrategy.close("Long", when=exitCondition)\n\n// Plotting\noffset = input.int(0, "Offset", minval = -500, maxval = 500)\nplot(basis, "Basis", color=#FF6D00, offset = offset)\np1 = plot(upper, "Upper", color=#2962FF, offset = offset)\np2 = plot(lower, "Lower", color=#2962FF, offset = offset)\nfill(p1, p2, title = "Background", color=color.rgb(33, 150, 243, 95))'

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
