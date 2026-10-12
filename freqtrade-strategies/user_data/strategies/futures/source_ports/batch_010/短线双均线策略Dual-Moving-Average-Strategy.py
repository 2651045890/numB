"""Source-faithful deep-assisted port of 短线双均线策略Dual-Moving-Average-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_3666fe5d(PinePortBase, IStrategy):
    source_file = '短线双均线策略Dual-Moving-Average-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'tim': '370', 'testStartYear': 2017, 'testStartMonth': 10, 'testStartDay': 25, 'testStartHour': 7, 'testStopYear': 2017, 'testStopMonth': 10, 'testStopDay': 30, 'testStopHour': 13}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['request.security', 'strategy.entry', '=>']
    source_fidelity_notes = ['Uses request.security / multi-timeframe context; exact parity depends on HTF resampling, gaps and lookahead semantics.']
    pine_assignments = [{'mode': '', 'name': 'tim', 'op': '=', 'expr': "input('370')", 'conditions': []}, {'mode': '', 'name': 'testStartYear', 'op': '=', 'expr': 'input(2017, "Backtest Start Year")', 'conditions': []}, {'mode': '', 'name': 'testStartMonth', 'op': '=', 'expr': 'input(10, "Backtest Start Month")', 'conditions': []}, {'mode': '', 'name': 'testStartDay', 'op': '=', 'expr': 'input(25, "Backtest Start Day")', 'conditions': []}, {'mode': '', 'name': 'testStartHour', 'op': '=', 'expr': 'input(7, "Backtest Start Hour")', 'conditions': []}, {'mode': '', 'name': 'testPeriodStart', 'op': '=', 'expr': 'timestamp(testStartYear,testStartMonth,testStartDay,testStartHour,0)', 'conditions': []}, {'mode': '', 'name': 'testStopYear', 'op': '=', 'expr': 'input(2017, "Backtest Stop Year")', 'conditions': []}, {'mode': '', 'name': 'testStopMonth', 'op': '=', 'expr': 'input(10, "Backtest Stop Month")', 'conditions': []}, {'mode': '', 'name': 'testStopDay', 'op': '=', 'expr': 'input(30, "Backtest Stop Day")', 'conditions': []}, {'mode': '', 'name': 'testStopHour', 'op': '=', 'expr': 'input(13, "Backtest stop Hour")', 'conditions': []}, {'mode': '', 'name': 'testPeriodStop', 'op': '=', 'expr': 'timestamp(testStopYear,testStopMonth,testStopDay,testStartHour,0)', 'conditions': []}, {'mode': '', 'name': 'out1', 'op': '=', 'expr': 'request.security(syminfo.tickerid, tim, open)', 'conditions': []}, {'mode': '', 'name': 'out2', 'op': '=', 'expr': 'request.security(syminfo.tickerid, tim, close)', 'conditions': []}, {'mode': '', 'name': 'longCondition', 'op': '=', 'expr': 'crossover(request.security(syminfo.tickerid, tim, close),request.security(syminfo.tickerid, tim, open))', 'conditions': []}, {'mode': '', 'name': 'shortCondition', 'op': '=', 'expr': 'crossunder(request.security(syminfo.tickerid, tim, close),request.security(syminfo.tickerid, tim, open))', 'conditions': []}]
    pine_user_functions = [{'name': 'testPeriod', 'args': '', 'body': 'true'}]
    pine_controls = [{'indent': 0, 'statement': 'if testPeriod()'}, {'indent': 4, 'statement': 'if (longCondition)'}, {'indent': 0, 'statement': 'if testPeriod()'}, {'indent': 4, 'statement': 'if (shortCondition)'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("long", strategy.long)', 'conditions': ['testPeriod()', '(longCondition)'], 'statement': 'strategy.entry("long", strategy.long)'}, {'kind': 'entry', 'call': 'strategy.entry("short", strategy.short)', 'conditions': ['testPeriod()', '(shortCondition)'], 'statement': 'strategy.entry("short", strategy.short)'}]
    original_pine = '/*backtest\nstart: 2022-10-26 00:00:00\nend: 2023-11-01 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=2\nstrategy("GetTrendStrategy timing", overlay=true)\ntim=input(\'370\')\n \n//////////////////////////////////////////////////////////////////////\n// Component Code Start\ntestStartYear = input(2017, "Backtest Start Year")\ntestStartMonth = input(10, "Backtest Start Month")\ntestStartDay = input(25, "Backtest Start Day")\ntestStartHour = input(7, "Backtest Start Hour")\ntestPeriodStart = timestamp(testStartYear,testStartMonth,testStartDay,testStartHour,0)\ntestStopYear = input(2017, "Backtest Stop Year")\ntestStopMonth = input(10, "Backtest Stop Month")\ntestStopDay = input(30, "Backtest Stop Day")\ntestStopHour = input(13, "Backtest stop Hour")\ntestPeriodStop = timestamp(testStopYear,testStopMonth,testStopDay,testStartHour,0)\n \ntestPeriod() => true\n// Component Code Stop\n//////////////////////////////////////////////////////////////////////\n \n \nout1 = request.security(syminfo.tickerid, tim, open)\nout2 = request.security(syminfo.tickerid, tim, close)\nplot(out1,color=red)\nplot(out2,color=green)\nlongCondition = crossover(request.security(syminfo.tickerid, tim, close),request.security(syminfo.tickerid, tim, open))\n \nif testPeriod()\n    if (longCondition)\n        strategy.entry("long", strategy.long)\nshortCondition = crossunder(request.security(syminfo.tickerid, tim, close),request.security(syminfo.tickerid, tim, open))\n \nif testPeriod()\n    if (shortCondition)\n        strategy.entry("short", strategy.short)'

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
