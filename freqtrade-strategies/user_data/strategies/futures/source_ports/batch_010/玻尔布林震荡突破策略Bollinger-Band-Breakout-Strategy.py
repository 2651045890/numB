"""Source-faithful deep-assisted port of 玻尔布林震荡突破策略Bollinger-Band-Breakout-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_3adf07e0(PinePortBase, IStrategy):
    source_file = '玻尔布林震荡突破策略Bollinger-Band-Breakout-Strategy.md'
    timeframe = '3m'
    can_short = False
    source_defaults = {'length': 16, 'mult': 3, 'upper_bbw_input': 50, 'lower_bbw_input': 20, 'testStartYear': 2019, 'testStartMonth': 1, 'testStartDay': 1, 'testStopYear': 2020, 'testStopMonth': 12, 'testStopDay': 31, 'tp_inp': 8}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.exit', 'strategy.entry', 'strategy.close', '=>']
    source_fidelity_notes = ['Uses strategy.exit; stop/limit/profit/loss/trailing arguments have Pine order semantics and may fill intrabar.']
    pine_assignments = [{'mode': '', 'name': 'source', 'op': '=', 'expr': 'close', 'conditions': []}, {'mode': '', 'name': 'length', 'op': '=', 'expr': 'input(16, minval=1)', 'conditions': []}, {'mode': '', 'name': 'mult', 'op': '=', 'expr': 'input(3, step=0.1, minval=0.001, maxval=50)', 'conditions': []}, {'mode': '', 'name': 'basis', 'op': '=', 'expr': 'sma(source, length)', 'conditions': []}, {'mode': '', 'name': 'dev', 'op': '=', 'expr': 'mult * stdev(source, length)', 'conditions': []}, {'mode': '', 'name': 'upper', 'op': '=', 'expr': 'basis + dev', 'conditions': []}, {'mode': '', 'name': 'lower', 'op': '=', 'expr': 'basis - dev', 'conditions': []}, {'mode': '', 'name': 'p1', 'op': '=', 'expr': 'plot(upper, color=color.blue)', 'conditions': []}, {'mode': '', 'name': 'p2', 'op': '=', 'expr': 'plot(lower, color=color.blue)', 'conditions': []}, {'mode': '', 'name': 'bbw', 'op': '=', 'expr': '(upper-lower)/basis*1000', 'conditions': []}, {'mode': '', 'name': 'upper_bbw_input', 'op': '=', 'expr': 'input(title="BBW Upper Threshold", step=1, minval=0, defval=50)', 'conditions': []}, {'mode': '', 'name': 'lower_bbw_input', 'op': '=', 'expr': 'input(title="BBW Lower Threshold", step=1, minval=0, defval=20)', 'conditions': []}, {'mode': '', 'name': 'testStartYear', 'op': '=', 'expr': 'input(2019, "Backtest Start Year")', 'conditions': []}, {'mode': '', 'name': 'testStartMonth', 'op': '=', 'expr': 'input(1, "Backtest Start Month")', 'conditions': []}, {'mode': '', 'name': 'testStartDay', 'op': '=', 'expr': 'input(1, "Backtest Start Day")', 'conditions': []}, {'mode': '', 'name': 'testPeriodStart', 'op': '=', 'expr': 'timestamp(testStartYear,testStartMonth,testStartDay,0,0)', 'conditions': []}, {'mode': '', 'name': 'testStopYear', 'op': '=', 'expr': 'input(2020, "Backtest Stop Year")', 'conditions': []}, {'mode': '', 'name': 'testStopMonth', 'op': '=', 'expr': 'input(12, "Backtest Stop Month")', 'conditions': []}, {'mode': '', 'name': 'testStopDay', 'op': '=', 'expr': 'input(31, "Backtest Stop Day")', 'conditions': []}, {'mode': '', 'name': 'testPeriodStop', 'op': '=', 'expr': 'timestamp(testStopYear,testStopMonth,testStopDay,0,0)', 'conditions': []}, {'mode': '', 'name': 'tp_inp', 'op': '=', 'expr': "input(8, title='Take Profit %', step=0.1)/100", 'conditions': []}, {'mode': '', 'name': 'take_level', 'op': '=', 'expr': 'strategy.position_avg_price * (1 + tp_inp)', 'conditions': []}, {'mode': '', 'name': 'entry_long', 'op': '=', 'expr': 'crossover(source, lower) and (bbw < upper_bbw_input) and (bbw > lower_bbw_input)', 'conditions': []}, {'mode': '', 'name': 'exit_long', 'op': '=', 'expr': 'cross(high,upper) or close < lower', 'conditions': []}]
    pine_user_functions = [{'name': 'testPeriod', 'args': '', 'body': 'true'}]
    pine_controls = [{'indent': 0, 'statement': 'if testPeriod()'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry(id="LongBB", long=true, comment="LongBB", when=entry_long)', 'conditions': ['testPeriod()'], 'statement': 'strategy.entry(id="LongBB", long=true, comment="LongBB", when=entry_long)'}, {'kind': 'exit', 'call': 'strategy.exit("Take Profit Long","LongBB",limit=take_level)', 'conditions': ['testPeriod()'], 'statement': 'strategy.exit("Take Profit Long","LongBB",limit=take_level)'}, {'kind': 'close', 'call': 'strategy.close(id="LongBB", when=exit_long )', 'conditions': ['testPeriod()'], 'statement': 'strategy.close(id="LongBB", when=exit_long )'}]
    original_pine = '/*backtest\nstart: 2023-10-30 00:00:00\nend: 2023-11-06 00:00:00\nperiod: 3m\nbasePeriod: 1m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=4\nstrategy("Bollinger Bands BAT/USDT 30min", overlay=true )\n\n/// Indicators\n///Bollinger Bands\nsource = close\nlength = input(16, minval=1)\nmult = input(3, step=0.1, minval=0.001, maxval=50)\nbasis = sma(source, length)\ndev = mult * stdev(source, length)\n\nupper = basis + dev\nlower = basis - dev\n\nplot(basis, color=color.red)\np1 = plot(upper, color=color.blue)\np2 = plot(lower, color=color.blue)\nfill(p1, p2)\n\n//Bollinger bands width\nbbw = (upper-lower)/basis*1000\n//plot(bbw, color=color.blue)\n\nupper_bbw_input = input(title="BBW Upper Threshold", step=1, minval=0, defval=50)\nlower_bbw_input = input(title="BBW Lower Threshold", step=1, minval=0, defval=20)\n\n\n// Backtesting Period\ntestStartYear = input(2019, "Backtest Start Year")\ntestStartMonth = input(1, "Backtest Start Month")\ntestStartDay = input(1, "Backtest Start Day")\ntestPeriodStart = timestamp(testStartYear,testStartMonth,testStartDay,0,0)\n\ntestStopYear = input(2020, "Backtest Stop Year")\ntestStopMonth = input(12, "Backtest Stop Month")\ntestStopDay = input(31, "Backtest Stop Day")\ntestPeriodStop = timestamp(testStopYear,testStopMonth,testStopDay,0,0)\n\ntestPeriod() => true\n\n// Take Profit\ntp_inp = input(8, title=\'Take Profit %\', step=0.1)/100\ntake_level = strategy.position_avg_price * (1 + tp_inp)\n\n//Entry Strategy\nentry_long = crossover(source, lower) and (bbw < upper_bbw_input) and (bbw > lower_bbw_input)\nexit_long = cross(high,upper) or close < lower\n\nif testPeriod()\n\n    strategy.entry(id="LongBB", long=true, comment="LongBB", when=entry_long)\n    strategy.exit("Take Profit Long","LongBB",limit=take_level)\n    strategy.close(id="LongBB", when=exit_long )'

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
