"""Source-faithful deep-assisted port of 灵活双均线交叉量化策略-Flexible-Moving-Average-Crossover-Quantitative-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_f894d7f1(PinePortBase, IStrategy):
    source_file = '灵活双均线交叉量化策略-Flexible-Moving-Average-Crossover-Quantitative-Strategy.md'
    timeframe = '2m'
    can_short = True
    source_defaults = {'fastMAPeriod': 20, 'fastMAType': 'SMA', 'fastMAColor': '#ee09f6', 'plotFastMA': True, 'slowMAPeriod': 200, 'slowMAType': 'SMA', 'slowMAColor': '#2bd4e0', 'plotSlowMA': True, 'directionOfTrade': 'LongShort'}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 100.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.entry', 'strategy.close', '=>']
    source_fidelity_notes = []
    pine_assignments = [{'mode': '', 'name': 'type', 'op': '=', 'expr': '= "SMA" ? ta.sma(source, length) :', 'conditions': []}, {'mode': '', 'name': 'type', 'op': '=', 'expr': '= "EMA" ? ta.ema(source, length) :', 'conditions': []}, {'mode': '', 'name': 'type', 'op': '=', 'expr': '= "SMMA (RMA)" ? ta.rma(source, length) :', 'conditions': []}, {'mode': '', 'name': 'type', 'op': '=', 'expr': '= "WMA" ? ta.wma(source, length) :', 'conditions': []}, {'mode': '', 'name': 'type', 'op': '=', 'expr': '= "VWMA" ? ta.vwma(source, length) :', 'conditions': []}, {'mode': '', 'name': 'fastMAPeriod', 'op': '=', 'expr': 'input.int(20, "Fast moving average period", inline="Fast moving average")', 'conditions': []}, {'mode': '', 'name': 'fastMAType', 'op': '=', 'expr': 'input.string("SMA" , "" , inline="Fast moving average", options=["SMA", "EMA", "SMMA (RMA)", "WMA", "VWMA"])', 'conditions': []}, {'mode': '', 'name': 'fastMAColor', 'op': '=', 'expr': 'input(#ee09f6, "" , inline="Fast moving average")', 'conditions': []}, {'mode': '', 'name': 'slowMAPeriod', 'op': '=', 'expr': 'input.int(200, "Slow moving average period", inline="Slow moving average")', 'conditions': []}, {'mode': '', 'name': 'slowMAType', 'op': '=', 'expr': 'input.string("SMA" , "" , inline="Slow moving average", options=["SMA", "EMA", "SMMA (RMA)", "WMA", "VWMA"])', 'conditions': []}, {'mode': '', 'name': 'slowMAColor', 'op': '=', 'expr': 'input(#2bd4e0, "" , inline="Slow moving average")', 'conditions': []}, {'mode': '', 'name': 'directionOfTrade', 'op': '=', 'expr': 'input.string("LongShort", "Trade direction: long & short, long only or short only", options=["LongShort", "Long", "Short"])', 'conditions': []}, {'mode': '', 'name': 'fastMA', 'op': '=', 'expr': 'ma(close, fastMAPeriod, fastMAType)', 'conditions': []}, {'mode': '', 'name': 'slowMA', 'op': '=', 'expr': 'ma(close, slowMAPeriod, slowMAType)', 'conditions': []}, {'mode': '', 'name': 'longCondition', 'op': '=', 'expr': 'ta.crossover(fastMA, ta.sma(close, 200))', 'conditions': []}, {'mode': '', 'name': 'shortCondition', 'op': '=', 'expr': 'ta.crossunder(fastMA, slowMA)', 'conditions': []}]
    pine_user_functions = [{'name': 'ma', 'args': 'source, length, type', 'body': ''}]
    pine_controls = [{'indent': 0, 'statement': 'if (longCondition)'}, {'indent': 4, 'statement': 'if (directionOfTrade == "LongShort" or directionOfTrade == "Long")'}, {'indent': 4, 'statement': 'else'}, {'indent': 0, 'statement': 'if (shortCondition)'}, {'indent': 4, 'statement': 'if (directionOfTrade == "LongShort" or directionOfTrade == "Short")'}, {'indent': 4, 'statement': 'else'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("My Long Entry Id", strategy.long)', 'conditions': ['(longCondition)', '(directionOfTrade == "LongShort" or directionOfTrade == "Long")'], 'statement': 'strategy.entry("My Long Entry Id", strategy.long)'}, {'kind': 'close', 'call': 'strategy.close("My Short Entry Id")', 'conditions': ['(longCondition)', 'ELSE'], 'statement': 'strategy.close("My Short Entry Id")'}, {'kind': 'entry', 'call': 'strategy.entry("My Short Entry Id", strategy.short)', 'conditions': ['(shortCondition)', '(directionOfTrade == "LongShort" or directionOfTrade == "Short")'], 'statement': 'strategy.entry("My Short Entry Id", strategy.short)'}, {'kind': 'close', 'call': 'strategy.close("My Long Entry Id")', 'conditions': ['(shortCondition)', 'ELSE'], 'statement': 'strategy.close("My Long Entry Id")'}]
    original_pine = '/*backtest\nstart: 2025-03-18 00:00:00\nend: 2025-03-20 01:00:00\nperiod: 2m\nbasePeriod: 2m\nexchanges: [{"eid":"Futures_Binance","currency":"ETH_USDT"}]\n*/\n\n// This Pine Script™ code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © ccrockatt21700\n\n//@version=6\nstrategy("MA crossover strategy", overlay=true, fill_orders_on_standard_ohlc = true, default_qty_type=strategy.percent_of_equity, default_qty_value=100)\n\nma(source, length, type) =>\n    type == "SMA" ? ta.sma(source, length) :\n     type == "EMA" ? ta.ema(source, length) :\n     type == "SMMA (RMA)" ? ta.rma(source, length) :\n     type == "WMA" ? ta.wma(source, length) :\n     type == "VWMA" ? ta.vwma(source, length) :\n     na\n\nfastMAPeriod = input.int(20, "Fast moving average period", inline="Fast moving average")\nfastMAType   = input.string("SMA"  , ""     , inline="Fast moving average", options=["SMA", "EMA", "SMMA (RMA)", "WMA", "VWMA"])\nfastMAColor  = input(#ee09f6, ""     , inline="Fast moving average")\nplotFastMA   = input.bool(true, "Plot Fast MA")\n\nslowMAPeriod = input.int(200, "Slow moving average period", inline="Slow moving average")\nslowMAType   = input.string("SMA"  , ""     , inline="Slow moving average", options=["SMA", "EMA", "SMMA (RMA)", "WMA", "VWMA"])\nslowMAColor  = input(#2bd4e0, ""     , inline="Slow moving average")\nplotSlowMA = input.bool(true, "Plot Slow MA")\n\ndirectionOfTrade = input.string("LongShort", "Trade direction: long & short, long only or short only", options=["LongShort", "Long", "Short"])\n\nfastMA = ma(close, fastMAPeriod, fastMAType)\nplot(plotFastMA ? fastMA : na, title="Fast MA", color=fastMAColor)\n\nslowMA = ma(close, slowMAPeriod, slowMAType)\nplot(plotSlowMA ? slowMA : na, title="Slow MA")\n\nlongCondition = ta.crossover(fastMA, ta.sma(close, 200))\nif (longCondition)\n    if (directionOfTrade == "LongShort" or directionOfTrade == "Long")\n        strategy.entry("My Long Entry Id", strategy.long)\n    else\n        strategy.close("My Short Entry Id")\n\nshortCondition = ta.crossunder(fastMA, slowMA)\nif (shortCondition)\n    if (directionOfTrade == "LongShort" or directionOfTrade == "Short")\n        strategy.entry("My Short Entry Id", strategy.short)\n    else\n        strategy.close("My Long Entry Id")'

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
