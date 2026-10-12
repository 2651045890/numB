"""Source-faithful deep-assisted port of 布林带随机RSI极值信号策略-Bollinger-Bands-Stochastic-RSI-Extreme-Signal-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_a7b9f76b(PinePortBase, IStrategy):
    source_file = '布林带随机RSI极值信号策略-Bollinger-Bands-Stochastic-RSI-Extreme-Signal-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'src': 'close', 'offset': 0, 'length': 20, 'mult': 2.0, 'smoothK': 3, 'smoothD': 3, 'lengthRSI': 14, 'lengthStoch': 14, 'upperlimit': 90, 'lowerlimit': 10}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.entry', 'alert']
    source_fidelity_notes = []
    pine_assignments = [{'mode': '', 'name': 'src', 'op': '=', 'expr': "input(close, title='Source')", 'conditions': []}, {'mode': '', 'name': 'offset', 'op': '=', 'expr': "input.int(0, 'Offset', minval=-500, maxval=500)", 'conditions': []}, {'mode': '', 'name': 'length', 'op': '=', 'expr': "input.int(20, title='Bollinger Band Length', minval=1)", 'conditions': []}, {'mode': '', 'name': 'mult', 'op': '=', 'expr': "input.float(2.0, minval=0.001, maxval=50, title='StdDev')", 'conditions': []}, {'mode': '', 'name': 'basis', 'op': '=', 'expr': 'ta.sma(src, length)', 'conditions': []}, {'mode': '', 'name': 'dev', 'op': '=', 'expr': 'mult * ta.stdev(src, length)', 'conditions': []}, {'mode': '', 'name': 'upper', 'op': '=', 'expr': 'basis + dev', 'conditions': []}, {'mode': '', 'name': 'lower', 'op': '=', 'expr': 'basis - dev', 'conditions': []}, {'mode': '', 'name': 'p1', 'op': '=', 'expr': "plot(upper, 'BB Upper', color=color.new(color.teal, 0), offset=offset)", 'conditions': []}, {'mode': '', 'name': 'p2', 'op': '=', 'expr': "plot(lower, 'BB Lower', color=color.new(color.teal, 0), offset=offset)", 'conditions': []}, {'mode': '', 'name': 'smoothK', 'op': '=', 'expr': "input.int(3, 'K', minval=1)", 'conditions': []}, {'mode': '', 'name': 'smoothD', 'op': '=', 'expr': "input.int(3, 'D', minval=1)", 'conditions': []}, {'mode': '', 'name': 'lengthRSI', 'op': '=', 'expr': "input.int(14, 'RSI Length', minval=1)", 'conditions': []}, {'mode': '', 'name': 'lengthStoch', 'op': '=', 'expr': "input.int(14, 'Stochastic Length', minval=1)", 'conditions': []}, {'mode': '', 'name': 'upperlimit', 'op': '=', 'expr': "input.float(90, 'Upper Limit', minval=0.01)", 'conditions': []}, {'mode': '', 'name': 'lowerlimit', 'op': '=', 'expr': "input.float(10, 'Upper Limit', minval=0.01)", 'conditions': []}, {'mode': '', 'name': 'rsi1', 'op': '=', 'expr': 'ta.rsi(src, lengthRSI)', 'conditions': []}, {'mode': '', 'name': 'k', 'op': '=', 'expr': 'ta.sma(ta.stoch(rsi1, rsi1, rsi1, lengthStoch), smoothK)', 'conditions': []}, {'mode': '', 'name': 'd', 'op': '=', 'expr': 'ta.sma(k, smoothD)', 'conditions': []}, {'mode': '', 'name': 'Bear', 'op': '=', 'expr': 'close[1] > upper[1] and close < upper and k[1] > upperlimit and d[1] > upperlimit', 'conditions': []}, {'mode': '', 'name': 'Bull', 'op': '=', 'expr': 'close[1] < lower[1] and close > lower and k[1] < lowerlimit and d[1] < lowerlimit', 'conditions': []}]
    pine_user_functions = []
    pine_controls = [{'indent': 0, 'statement': 'if Bear'}, {'indent': 0, 'statement': 'else if Bull'}]
    pine_orders = [{'kind': 'entry', 'call': "strategy.entry('Enter Long', strategy.long)", 'conditions': ['Bear'], 'statement': "strategy.entry('Enter Long', strategy.long)"}, {'kind': 'entry', 'call': "strategy.entry('Enter Short', strategy.short)", 'conditions': ['Bull'], 'statement': "strategy.entry('Enter Short', strategy.short)"}]
    original_pine = '/*backtest\nstart: 2023-04-06 00:00:00\nend: 2024-04-11 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy(shorttitle=\'BBSR Extreme\', title=\'Bollinger Bands Stochastic RSI Extreme Signal\', overlay=true)\n\n//General Inputs\nsrc = input(close, title=\'Source\')\noffset = input.int(0, \'Offset\', minval=-500, maxval=500)\n\n//Bollinger Inputs\nlength = input.int(20, title=\'Bollinger Band Length\', minval=1)\nmult = input.float(2.0, minval=0.001, maxval=50, title=\'StdDev\')\n\n//Bollinger Code\nbasis = ta.sma(src, length)\ndev = mult * ta.stdev(src, length)\nupper = basis + dev\nlower = basis - dev\nplot(basis, \'BB Basis\', color=color.new(#872323, 0), offset=offset)\np1 = plot(upper, \'BB Upper\', color=color.new(color.teal, 0), offset=offset)\np2 = plot(lower, \'BB Lower\', color=color.new(color.teal, 0), offset=offset)\nfill(p1, p2, title=\'BB Background\', color=color.new(#198787, 95))\n\n\n//Stoch Inputs\nsmoothK = input.int(3, \'K\', minval=1)\nsmoothD = input.int(3, \'D\', minval=1)\nlengthRSI = input.int(14, \'RSI Length\', minval=1)\nlengthStoch = input.int(14, \'Stochastic Length\', minval=1)\n\nupperlimit = input.float(90, \'Upper Limit\', minval=0.01)\nlowerlimit = input.float(10, \'Upper Limit\', minval=0.01)\n\n//Stochastic Code\nrsi1 = ta.rsi(src, lengthRSI)\nk = ta.sma(ta.stoch(rsi1, rsi1, rsi1, lengthStoch), smoothK)\nd = ta.sma(k, smoothD)\n\n//Evaluation\nBear = close[1] > upper[1] and close < upper and k[1] > upperlimit and d[1] > upperlimit\nBull = close[1] < lower[1] and close > lower and k[1] < lowerlimit and d[1] < lowerlimit\n\n\n//Plots\nplotshape(Bear, style=shape.triangledown, location=location.abovebar, color=color.new(color.red, 0), size=size.tiny)\nplotshape(Bull, style=shape.triangleup, location=location.belowbar, color=color.new(color.green, 0), size=size.tiny)\n\n// Alert Functionality\nalertcondition(Bear or Bull, title=\'Any Signal\', message=\'{{exchange}}:{{ticker}}\' + \' {{interval}}\' + \' BB Stochastic Extreme!\')\nalertcondition(Bear, title=\'Bearish Signal\', message=\'{{exchange}}:{{ticker}}\' + \' {{interval}}\' + \' Bearish BB Stochastic Extreme!\')\nalertcondition(Bull, title=\'Bullish Signal\', message=\'{{exchange}}:{{ticker}}\' + \' {{interval}}\' + \' Bullish BB Stochastic Extreme!\')\n\n\nif Bear\n    strategy.entry(\'Enter Long\', strategy.long)\nelse if Bull\n    strategy.entry(\'Enter Short\', strategy.short)'

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
