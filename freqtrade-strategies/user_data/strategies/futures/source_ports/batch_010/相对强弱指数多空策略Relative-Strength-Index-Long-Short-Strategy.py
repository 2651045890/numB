"""Source-faithful deep-assisted port of 相对强弱指数多空策略Relative-Strength-Index-Long-Short-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_8173c75f(PinePortBase, IStrategy):
    source_file = '相对强弱指数多空策略Relative-Strength-Index-Long-Short-Strategy.md'
    timeframe = '1h'
    can_short = True
    source_defaults = {'testStartYear': 2016, 'testStartMonth': 1, 'testStartDay': 1, 'testStopYear': 2030, 'testStopMonth': 12, 'testStopDay': 30, 'len': 4, 'correlationcrossover': 1, 'IndexSwitch': 'CRYPTOCAP:TOTAL2', 'IndexHTF': '120', 'switchColor': True}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['request.security', 'strategy.entry', 'switch', '=>', 'alert']
    source_fidelity_notes = ['Uses request.security / multi-timeframe context; exact parity depends on HTF resampling, gaps and lookahead semantics.', 'Uses barmerge.lookahead_on; source can intentionally expose/repaint future HTF values. Preserve when parity-testing, disable for live-safe testing only as a separate variant.']
    pine_assignments = [{'mode': '', 'name': 'testStartYear', 'op': '=', 'expr': "input(2016, 'Backtest Start Year')", 'conditions': []}, {'mode': '', 'name': 'testStartMonth', 'op': '=', 'expr': "input(1, 'Backtest Start Month')", 'conditions': []}, {'mode': '', 'name': 'testStartDay', 'op': '=', 'expr': "input(1, 'Backtest Start Day')", 'conditions': []}, {'mode': '', 'name': 'testPeriodStart', 'op': '=', 'expr': 'timestamp(testStartYear, testStartMonth, testStartDay, 0, 0)', 'conditions': []}, {'mode': '', 'name': 'testStopYear', 'op': '=', 'expr': "input(2030, 'Backtest Stop Year')", 'conditions': []}, {'mode': '', 'name': 'testStopMonth', 'op': '=', 'expr': "input(12, 'Backtest Stop Month')", 'conditions': []}, {'mode': '', 'name': 'testStopDay', 'op': '=', 'expr': "input(30, 'Backtest Stop Day')", 'conditions': []}, {'mode': '', 'name': 'testPeriodStop', 'op': '=', 'expr': 'timestamp(testStopYear, testStopMonth, testStopDay, 0, 0)', 'conditions': []}, {'mode': '', 'name': 'len', 'op': '=', 'expr': "input(4, title='length of rsi comparison')", 'conditions': []}, {'mode': '', 'name': 'correlationcrossover', 'op': '=', 'expr': "input(1, title='correlation crossover')", 'conditions': []}, {'mode': '', 'name': 'IndexSwitch', 'op': '=', 'expr': "input.string('CRYPTOCAP:TOTAL2', title='Index selection', options=['CRYPTOCAP:TOTAL2', 'CRYPTOCAP:TOTAL', 'CRYPTOCAP:OTHERS', 'CRYPTOCAP:USDT', 'CRYPTOINDEX:CIX100', 'CRYPTOCAP:BTC.D', 'CRYPTOCAP:BTC'])", 'conditions': []}, {'mode': '', 'name': 'IndexHTF', 'op': '=', 'expr': "input.string('120', title='higher time frame reference index', options=['1', '2', '5', '10', '15', '30', '45', '60', '90', '120', '150', '240', '360', '720', 'D', '3D', 'W', 'M'])", 'conditions': []}, {'mode': '', 'name': 'switchColor', 'op': '=', 'expr': "input(true, 'Color Hull according to trend?')", 'conditions': []}, {'mode': '', 'name': 'ref', 'op': '=', 'expr': 'request.security(IndexSwitch, IndexHTF, close[1], lookahead=barmerge.lookahead_on)', 'conditions': []}, {'mode': '', 'name': 'RSI_ref', 'op': '=', 'expr': 'ta.rsi(ref, len)', 'conditions': []}, {'mode': '', 'name': 'RSI_close', 'op': '=', 'expr': 'ta.rsi(close, len)', 'conditions': []}, {'mode': '', 'name': 'relative', 'op': '=', 'expr': 'RSI_ref / RSI_close', 'conditions': []}, {'mode': '', 'name': 'long', 'op': '=', 'expr': 'ta.crossover(relative, correlationcrossover)', 'conditions': []}, {'mode': '', 'name': 'short', 'op': '=', 'expr': 'ta.crossunder(relative, correlationcrossover)', 'conditions': []}, {'mode': '', 'name': 'corr', 'op': '=', 'expr': 'plot(correlationcrossover, color=color.new(color.green, 0), linewidth=1)', 'conditions': []}, {'mode': '', 'name': 'hullColor', 'op': '=', 'expr': 'switchColor ? relative > correlationcrossover ? #00ff00 : #ff0000 : #ff9800', 'conditions': []}, {'mode': '', 'name': 'Fi1', 'op': '=', 'expr': "plot(relative, title='relative', color=hullColor, linewidth=1, transp=50)", 'conditions': []}]
    pine_user_functions = [{'name': 'testPeriod', 'args': '', 'body': ''}]
    pine_controls = [{'indent': 0, 'statement': 'if long and testPeriod()'}, {'indent': 0, 'statement': 'if short and testPeriod()'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("long", strategy.long)', 'conditions': ['long and testPeriod()'], 'statement': 'strategy.entry("long", strategy.long)'}, {'kind': 'entry', 'call': 'strategy.entry("long", strategy.short)', 'conditions': ['short and testPeriod()'], 'statement': 'strategy.entry("long", strategy.short)'}]
    original_pine = '/*backtest\nstart: 2023-10-16 00:00:00\nend: 2023-11-15 00:00:00\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy(\'RSI correlation with cryptoindices [strategy version]\', overlay=false)\n\n// Testing Start dates\ntestStartYear = input(2016, \'Backtest Start Year\')\ntestStartMonth = input(1, \'Backtest Start Month\')\ntestStartDay = input(1, \'Backtest Start Day\')\ntestPeriodStart = timestamp(testStartYear, testStartMonth, testStartDay, 0, 0)\n//Stop date if you want to use a specific range of dates\ntestStopYear = input(2030, \'Backtest Stop Year\')\ntestStopMonth = input(12, \'Backtest Stop Month\')\ntestStopDay = input(30, \'Backtest Stop Day\')\ntestPeriodStop = timestamp(testStopYear, testStopMonth, testStopDay, 0, 0)\ntestPeriod() =>\n    time >= testPeriodStart and time <= testPeriodStop ? true : false\n\nlen = input(4, title=\'length of rsi comparison\')\ncorrelationcrossover = input(1, title=\'correlation crossover\')\nIndexSwitch = input.string(\'CRYPTOCAP:TOTAL2\', title=\'Index selection\', options=[\'CRYPTOCAP:TOTAL2\', \'CRYPTOCAP:TOTAL\', \'CRYPTOCAP:OTHERS\', \'CRYPTOCAP:USDT\', \'CRYPTOINDEX:CIX100\', \'CRYPTOCAP:BTC.D\', \'CRYPTOCAP:BTC\'])\nIndexHTF = input.string(\'120\', title=\'higher time frame reference index\', options=[\'1\', \'2\', \'5\', \'10\', \'15\', \'30\', \'45\', \'60\', \'90\', \'120\', \'150\', \'240\', \'360\', \'720\', \'D\', \'3D\', \'W\', \'M\'])\nswitchColor = input(true, \'Color Hull according to trend?\')\nref = request.security(IndexSwitch, IndexHTF, close[1], lookahead=barmerge.lookahead_on)\nRSI_ref = ta.rsi(ref, len)\nRSI_close = ta.rsi(close, len)\nrelative = RSI_ref / RSI_close\nplot(relative, color=color.new(color.blue, 0))\nlong = ta.crossover(relative, correlationcrossover)\nshort = ta.crossunder(relative, correlationcrossover)\ncorr = plot(correlationcrossover, color=color.new(color.green, 0), linewidth=1)\nhullColor = switchColor ? relative > correlationcrossover ? #00ff00 : #ff0000 : #ff9800\n\n//PLOT\n///< Frame\nFi1 = plot(relative, title=\'relative\', color=hullColor, linewidth=1, transp=50)\nfill(Fi1, corr, title=\'Band Filler\', color=hullColor, transp=50)\n\nif long and testPeriod()\n    strategy.entry("long", strategy.long)\n    \nif short and testPeriod()\n    strategy.entry("long", strategy.short)\n\n// alertcondition(long, title=\'long\', message=\'long\')\n// alertcondition(short, title=\'short\', message=\'short\')'

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
