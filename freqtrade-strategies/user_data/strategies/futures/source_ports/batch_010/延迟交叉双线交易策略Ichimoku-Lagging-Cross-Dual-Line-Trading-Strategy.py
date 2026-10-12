"""Source-faithful deep-assisted port of 延迟交叉双线交易策略Ichimoku-Lagging-Cross-Dual-Line-Trading-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_2b4a63ee(PinePortBase, IStrategy):
    source_file = '延迟交叉双线交易策略Ichimoku-Lagging-Cross-Dual-Line-Trading-Strategy.md'
    timeframe = '4h'
    can_short = True
    source_defaults = {'conversionPeriods': 9, 'basePeriods': 26, 'laggingSpan2Periods': 52, 'displacement': 26}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.entry', '=>']
    source_fidelity_notes = []
    pine_assignments = [{'mode': '', 'name': 'conversionPeriods', 'op': '=', 'expr': 'input(9, minval=1, title="Conversion Line Periods"),', 'conditions': []}, {'mode': '', 'name': 'basePeriods', 'op': '=', 'expr': 'input(26, minval=1, title="Base Line Periods")', 'conditions': []}, {'mode': '', 'name': 'laggingSpan2Periods', 'op': '=', 'expr': 'input(52, minval=1, title="Lagging Span 2 Periods"),', 'conditions': []}, {'mode': '', 'name': 'displacement', 'op': '=', 'expr': 'input(26, minval=1, title="Displacement")', 'conditions': []}, {'mode': '', 'name': 'conversionLine', 'op': '=', 'expr': 'donchian(conversionPeriods)', 'conditions': []}, {'mode': '', 'name': 'baseLine', 'op': '=', 'expr': 'donchian(basePeriods)', 'conditions': []}, {'mode': '', 'name': 'leadLine1', 'op': '=', 'expr': 'avg(conversionLine, baseLine)', 'conditions': []}, {'mode': '', 'name': 'leadLine2', 'op': '=', 'expr': 'donchian(laggingSpan2Periods)', 'conditions': []}, {'mode': '', 'name': 'p1', 'op': '=', 'expr': 'plot(leadLine1, offset = displacement - 1, color=color.green, title="Lead 1")', 'conditions': []}, {'mode': '', 'name': 'p2', 'op': '=', 'expr': 'plot(leadLine2, offset = displacement - 1, color=color.red, title="Lead 2")', 'conditions': []}, {'mode': '', 'name': 'longCondition', 'op': '=', 'expr': 'crossover(conversionLine,baseLine)', 'conditions': []}, {'mode': '', 'name': 'shortCondition', 'op': '=', 'expr': 'crossover(baseLine, conversionLine)', 'conditions': []}]
    pine_user_functions = [{'name': 'donchian', 'args': 'len', 'body': 'avg(lowest(len), highest(len))'}]
    pine_controls = [{'indent': 0, 'statement': 'if (longCondition)'}, {'indent': 0, 'statement': 'if (shortCondition)'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("Buy", strategy.long)', 'conditions': ['(longCondition)'], 'statement': 'strategy.entry("Buy", strategy.long)'}, {'kind': 'entry', 'call': 'strategy.entry("Short", strategy.short)', 'conditions': ['(shortCondition)'], 'statement': 'strategy.entry("Short", strategy.short)'}]
    original_pine = '/*backtest\nstart: 2023-09-19 00:00:00\nend: 2023-10-19 00:00:00\nperiod: 4h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This source code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © iamskrv\n\n//@version=4\nstrategy("Ichimoku Cloud Strategy v2.0", overlay=true)\n\n//@version=4\n// study(title="Ichimoku Cloud", shorttitle="Ichimoku", overlay=true)\n\nconversionPeriods = input(9, minval=1, title="Conversion Line Periods"),\nbasePeriods = input(26, minval=1, title="Base Line Periods")\nlaggingSpan2Periods = input(52, minval=1, title="Lagging Span 2 Periods"),\ndisplacement = input(26, minval=1, title="Displacement")\n\ndonchian(len) => avg(lowest(len), highest(len))\n\nconversionLine = donchian(conversionPeriods)\nbaseLine = donchian(basePeriods)\nleadLine1 = avg(conversionLine, baseLine)\nleadLine2 = donchian(laggingSpan2Periods)\n\nplot(conversionLine, color=#0496ff, title="Conversion Line")\nplot(baseLine, color=#991515, title="Base Line")\nplot(close, offset = -displacement + 1, color=#459915, title="Lagging Span")\n\np1 = plot(leadLine1, offset = displacement - 1, color=color.green,\n title="Lead 1")\np2 = plot(leadLine2, offset = displacement - 1, color=color.red, \n title="Lead 2")\nfill(p1, p2, color = leadLine1 > leadLine2 ? color.green : color.red)\n\n// Strategy\n\n\nlongCondition = crossover(conversionLine,baseLine)\nif (longCondition)\n    strategy.entry("Buy", strategy.long)\n\nshortCondition = crossover(baseLine, conversionLine)\nif (shortCondition)\n    strategy.entry("Short", strategy.short)'

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
