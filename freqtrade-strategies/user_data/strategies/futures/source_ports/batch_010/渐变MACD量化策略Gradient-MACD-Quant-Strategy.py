"""Source-faithful deep-assisted port of 渐变MACD量化策略Gradient-MACD-Quant-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_a5eb761a(PinePortBase, IStrategy):
    source_file = '渐变MACD量化策略Gradient-MACD-Quant-Strategy.md'
    timeframe = '1h'
    can_short = True
    source_defaults = {'fastmacd': 12, 'slowmacd': 26, 'signalmacd': 9, 'yearfrom': 2020, 'yearuntil': 2042, 'monthfrom': 1, 'monthuntil': 12, 'dayfrom': 1, 'dayuntil': 31}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 100.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.1
    source_features = ['strategy.entry', 'strategy.cancel']
    source_fidelity_notes = []
    pine_assignments = [{'mode': '', 'name': 'haopen', 'op': '=', 'expr': '0.0', 'conditions': []}, {'mode': '', 'name': 'haclose', 'op': '=', 'expr': '(open + high + low + close) / 4', 'conditions': []}, {'mode': '', 'name': 'haopen', 'op': ':=', 'expr': 'na(haopen[1]) ? (open + close) / 2 : (haopen[1] + haclose[1]) / 2', 'conditions': []}, {'mode': '', 'name': 'hahigh', 'op': '=', 'expr': 'max(high, max(haopen, haclose))', 'conditions': []}, {'mode': '', 'name': 'halow', 'op': '=', 'expr': 'min(low, min(haopen, haclose))', 'conditions': []}, {'mode': '', 'name': 'hacolor', 'op': '=', 'expr': 'haclose > haopen ? color.green : color.red', 'conditions': []}, {'mode': '', 'name': 'src', 'op': '=', 'expr': 'haclose', 'conditions': []}, {'mode': '', 'name': 'fastmacd', 'op': '=', 'expr': "input(12,title='MACD Fast Line Length')", 'conditions': []}, {'mode': '', 'name': 'slowmacd', 'op': '=', 'expr': "input(26,title='MACD Slow Line Length')", 'conditions': []}, {'mode': '', 'name': 'signalmacd', 'op': '=', 'expr': "input(9,title='Signal Line Length')", 'conditions': []}, {'mode': '', 'name': 'macdslowline1', 'op': '=', 'expr': 'sma(src,slowmacd)', 'conditions': []}, {'mode': '', 'name': 'macdslowline2', 'op': '=', 'expr': 'sma(macdslowline1,slowmacd)', 'conditions': []}, {'mode': '', 'name': 'DEMAslow', 'op': '=', 'expr': '((2 * macdslowline1) - macdslowline2 )', 'conditions': []}, {'mode': '', 'name': 'macdfastline1', 'op': '=', 'expr': 'sma(src,fastmacd)', 'conditions': []}, {'mode': '', 'name': 'macdfastline2', 'op': '=', 'expr': 'sma(macdfastline1,fastmacd)', 'conditions': []}, {'mode': '', 'name': 'DEMAfast', 'op': '=', 'expr': '((2 * macdfastline1) - macdfastline2)', 'conditions': []}, {'mode': '', 'name': 'MACDLine', 'op': '=', 'expr': '(DEMAfast - DEMAslow)', 'conditions': []}, {'mode': '', 'name': 'SignalLine', 'op': '=', 'expr': 'sma(MACDLine, signalmacd)', 'conditions': []}, {'mode': '', 'name': 'delta', 'op': '=', 'expr': 'MACDLine-SignalLine', 'conditions': []}, {'mode': '', 'name': 'swap1', 'op': '=', 'expr': 'delta>0?color.green:color.red', 'conditions': []}, {'mode': '', 'name': 'p1', 'op': '=', 'expr': "plot(MACDLine,color=color.blue,title='MACD Line')", 'conditions': []}, {'mode': '', 'name': 'p2', 'op': '=', 'expr': "plot(SignalLine,color=color.red,title='Signal')", 'conditions': []}, {'mode': '', 'name': 'yearfrom', 'op': '=', 'expr': 'input(2020)', 'conditions': []}, {'mode': '', 'name': 'yearuntil', 'op': '=', 'expr': 'input(2042)', 'conditions': []}, {'mode': '', 'name': 'monthfrom', 'op': '=', 'expr': 'input(1)', 'conditions': []}, {'mode': '', 'name': 'monthuntil', 'op': '=', 'expr': 'input(12)', 'conditions': []}, {'mode': '', 'name': 'dayfrom', 'op': '=', 'expr': 'input(1)', 'conditions': []}, {'mode': '', 'name': 'dayuntil', 'op': '=', 'expr': 'input(31)', 'conditions': []}]
    pine_user_functions = []
    pine_controls = [{'indent': 0, 'statement': 'if ( crossover(delta,0) and year >= yearfrom and year <= yearuntil and month>=monthfrom and month <=monthuntil and dayofmonth>=dayfrom and dayofmonth < dayuntil)'}, {'indent': 0, 'statement': 'else'}, {'indent': 0, 'statement': 'if ( crossunder(delta,0) and year >= yearfrom and year <= yearuntil and month>=monthfrom and month <=monthuntil and dayofmonth>=dayfrom and dayofmonth < dayuntil )'}, {'indent': 0, 'statement': 'else'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("MMAL", strategy.long, stop=close, oca_name="TREND", comment="AL")', 'conditions': ['( crossover(delta,0) and year >= yearfrom and year <= yearuntil and month>=monthfrom and month <=monthuntil and dayofmonth>=dayfrom and dayofmonth < dayuntil)'], 'statement': 'strategy.entry("MMAL", strategy.long, stop=close, oca_name="TREND", comment="AL")'}, {'kind': 'cancel', 'call': 'strategy.cancel(id="MMAL")', 'conditions': ['ELSE'], 'statement': 'strategy.cancel(id="MMAL")'}, {'kind': 'entry', 'call': 'strategy.entry("MMSAT", strategy.short,stop=close, oca_name="TREND", comment="SAT")', 'conditions': ['( crossunder(delta,0) and year >= yearfrom and year <= yearuntil and month>=monthfrom and month <=monthuntil and dayofmonth>=dayfrom and dayofmonth < dayuntil )'], 'statement': 'strategy.entry("MMSAT", strategy.short,stop=close, oca_name="TREND", comment="SAT")'}, {'kind': 'cancel', 'call': 'strategy.cancel(id="MMSAT")', 'conditions': ['ELSE'], 'statement': 'strategy.cancel(id="MMSAT")'}]
    original_pine = '/*backtest\nstart: 2023-11-18 00:00:00\nend: 2023-12-18 00:00:00\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=4\nstrategy("MACD ASHI BARS .v1 ", overlay=false,default_qty_type = strategy.percent_of_equity, default_qty_value = 100,commission_type=strategy.commission.percent,commission_value=0.1,slippage=1)\n\n// Calculation HA Values \nhaopen  = 0.0\nhaclose = (open + high + low + close) / 4\nhaopen := na(haopen[1]) ? (open + close) / 2 : (haopen[1] + haclose[1]) / 2\nhahigh  = max(high, max(haopen, haclose))\nhalow   = min(low,  min(haopen, haclose))\n\n// HA colors\nhacolor = haclose > haopen ? color.green : color.red\nsrc=haclose\n\n\n\nfastmacd = input(12,title=\'MACD Fast  Line Length\')\nslowmacd = input(26,title=\'MACD Slow Line Length\')\nsignalmacd = input(9,title=\'Signal Line Length\')\n\nmacdslowline1 = sma(src,slowmacd)\nmacdslowline2 = sma(macdslowline1,slowmacd)\nDEMAslow = ((2 * macdslowline1) - macdslowline2 )\n\nmacdfastline1 = sma(src,fastmacd)\nmacdfastline2 = sma(macdfastline1,fastmacd)\nDEMAfast = ((2 * macdfastline1) - macdfastline2)\n\nMACDLine = (DEMAfast - DEMAslow)\n\nSignalLine = sma(MACDLine, signalmacd)\n\ndelta = MACDLine-SignalLine\n\n\n\n\nswap1 = delta>0?color.green:color.red\n\n\n\nplot(delta,color=swap1,style=plot.style_columns,title=\'Histo\',histbase=0,transp=20)\np1 = plot(MACDLine,color=color.blue,title=\'MACD Line\')\np2 = plot(SignalLine,color=color.red,title=\'Signal\')\nfill(p1, p2, color=color.blue)\nhline(0)\n\n\n\nyearfrom = input(2020)\nyearuntil =input(2042)\nmonthfrom =input(1)\nmonthuntil =input(12)\ndayfrom=input(1)\ndayuntil=input(31)\n\n\n\n\n\n\n\nif ( crossover(delta,0)  and   year >= yearfrom and year <= yearuntil and month>=monthfrom and month <=monthuntil and dayofmonth>=dayfrom and dayofmonth < dayuntil) \n    strategy.entry("MMAL", strategy.long, stop=close, oca_name="TREND",  comment="AL")\n    \nelse\n    strategy.cancel(id="MMAL")\n\n\nif (  crossunder(delta,0) and  year >= yearfrom and year <= yearuntil and month>=monthfrom and month <=monthuntil and dayofmonth>=dayfrom and dayofmonth < dayuntil ) \n\n    strategy.entry("MMSAT", strategy.short,stop=close, oca_name="TREND",  comment="SAT")\nelse\n    strategy.cancel(id="MMSAT")'

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
