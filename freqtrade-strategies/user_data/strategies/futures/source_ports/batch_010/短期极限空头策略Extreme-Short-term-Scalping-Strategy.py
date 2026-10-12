"""Source-faithful deep-assisted port of 短期极限空头策略Extreme-Short-term-Scalping-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_fe9cb07d(PinePortBase, IStrategy):
    source_file = '短期极限空头策略Extreme-Short-term-Scalping-Strategy.md'
    timeframe = '4h'
    can_short = True
    source_defaults = {'src': 'close', 'len': 14, 'offset': 1, 'gap_tick': 100, 'fixedTP': 300, 'fixedSL': 100, 'useFixedSLTP': True, 'direction': 'ALL'}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.exit', 'strategy.entry', 'strategy.close', 'strategy.cancel', '=>']
    source_fidelity_notes = ['Uses strategy.exit; stop/limit/profit/loss/trailing arguments have Pine order semantics and may fill intrabar.']
    pine_assignments = [{'mode': '', 'name': 'src', 'op': '=', 'expr': 'input(close,title="Source")', 'conditions': []}, {'mode': '', 'name': 'len', 'op': '=', 'expr': 'input(defval=14, minval=1, title="Length")', 'conditions': []}, {'mode': '', 'name': 'offset', 'op': '=', 'expr': 'input(1)', 'conditions': []}, {'mode': '', 'name': 'out', 'op': '=', 'expr': 'linreg(src, len, offset)', 'conditions': []}, {'mode': '', 'name': 'gap_tick', 'op': '=', 'expr': 'input(100)', 'conditions': []}, {'mode': '', 'name': 'fixedTP', 'op': '=', 'expr': 'input(300)', 'conditions': []}, {'mode': '', 'name': 'fixedSL', 'op': '=', 'expr': 'input(100)', 'conditions': []}, {'mode': '', 'name': 'useFixedSLTP', 'op': '=', 'expr': 'input(true)', 'conditions': []}, {'mode': '', 'name': 'direction', 'op': '=', 'expr': 'input(defval="ALL",title="Direction of order",options=["ALL","BUY ONLY","SELL ONLY"])', 'conditions': []}, {'mode': '', 'name': 'gap', 'op': '=', 'expr': 'gap_tick*syminfo.mintick', 'conditions': []}, {'mode': '', 'name': 'tp', 'op': '=', 'expr': 'useFixedSLTP?fixedTP:gap_tick', 'conditions': []}, {'mode': '', 'name': 'sl', 'op': '=', 'expr': 'useFixedSLTP?fixedSL:gap_tick', 'conditions': []}, {'mode': '', 'name': 'longCondition', 'op': '=', 'expr': 'close<(out-gap) and (direction=="ALL" or direction=="BUY ONLY")', 'conditions': []}, {'mode': '', 'name': 'shortCondition', 'op': '=', 'expr': 'close>(out+gap) and (direction=="ALL" or direction=="SELL ONLY")', 'conditions': []}]
    pine_user_functions = []
    pine_controls = [{'indent': 0, 'statement': 'if (longCondition)'}, {'indent': 0, 'statement': 'if (shortCondition)'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("Long", strategy.long)', 'conditions': ['(longCondition)'], 'statement': 'strategy.entry("Long", strategy.long)'}, {'kind': 'exit', 'call': 'strategy.exit("exit long","Long",profit = tp,loss = sl)', 'conditions': ['(longCondition)'], 'statement': 'strategy.exit("exit long","Long",profit = tp,loss = sl)'}, {'kind': 'entry', 'call': 'strategy.entry("Short", strategy.short)', 'conditions': ['(shortCondition)'], 'statement': 'strategy.entry("Short", strategy.short)'}, {'kind': 'exit', 'call': 'strategy.exit("exit short","Short",profit =tp,loss=sl)', 'conditions': ['(shortCondition)'], 'statement': 'strategy.exit("exit short","Short",profit =tp,loss=sl)'}]
    original_pine = '/*backtest\nstart: 2024-01-09 00:00:00\nend: 2024-01-16 00:00:00\nperiod: 4h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=4\nstrategy("Extreme Scalping", overlay=true )\nsrc = input(close,title="Source")\nlen = input(defval=14, minval=1, title="Length")\noffset = input(1)\nout = linreg(src, len, offset)\nplot(out)\n\ngap_tick=input(100)\nfixedTP=input(300)\nfixedSL=input(100)\nuseFixedSLTP=input(true)\ndirection=input(defval="ALL",title="Direction of order",options=["ALL","BUY ONLY","SELL ONLY"])\ngap=gap_tick*syminfo.mintick\nplot(out+gap,color=color.red)\nplot(out-gap,color=color.green)\n\ntp=useFixedSLTP?fixedTP:gap_tick\nsl=useFixedSLTP?fixedSL:gap_tick\n\nlongCondition = close<(out-gap) and (direction=="ALL" or direction=="BUY ONLY")\nshortCondition = close>(out+gap) and (direction=="ALL" or direction=="SELL ONLY")\n\nif (longCondition)\n    strategy.entry("Long", strategy.long)\n    strategy.exit("exit long","Long",profit = tp,loss = sl)\n    \n\nif (shortCondition)\n    strategy.entry("Short", strategy.short)\n    strategy.exit("exit short","Short",profit =tp,loss=sl)\n    \n// === Backtesting Dates === thanks to Trost\n\n// testPeriodSwitch = input(true, "Custom Backtesting Dates")\n// testStartYear = input(2019, "Backtest Start Year")\n// testStartMonth = input(10, "Backtest Start Month")\n// testStartDay = input(3, "Backtest Start Day")\n// testStartHour = input(0, "Backtest Start Hour")\n// testPeriodStart = timestamp(testStartYear,testStartMonth,testStartDay,testStartHour,0)\n// testStopYear = input(2019, "Backtest Stop Year")\n// testStopMonth = input(12, "Backtest Stop Month")\n// testStopDay = input(31, "Backtest Stop Day")\n// testStopHour = input(23, "Backtest Stop Hour")\n// testPeriodStop = timestamp(testStopYear,testStopMonth,testStopDay,testStopHour,0)\n// testPeriod() =>\n//     time >= testPeriodStart and time <= testPeriodStop ? true : false\n// isPeriod = testPeriodSwitch == true ? testPeriod() : true\n// // === /END\n\n// if not isPeriod\n//     strategy.cancel_all()\n//     strategy.close_all()'

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
