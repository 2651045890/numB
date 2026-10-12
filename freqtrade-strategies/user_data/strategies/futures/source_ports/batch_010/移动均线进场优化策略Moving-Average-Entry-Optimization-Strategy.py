"""Source-faithful deep-assisted port of 移动均线进场优化策略Moving-Average-Entry-Optimization-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_73229724(PinePortBase, IStrategy):
    source_file = '移动均线进场优化策略Moving-Average-Entry-Optimization-Strategy.md'
    timeframe = '1h'
    can_short = True
    source_defaults = {'period': 20, 'maxwait': 3, 'threshold': 0.01}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.entry', 'strategy.close', 'strategy.position_size', 'for ']
    source_fidelity_notes = ['Reads broker/strategy state; signals depend on fill timing and cannot be reduced to indicator-only booleans without changing behavior.']
    pine_assignments = [{'mode': '', 'name': 'period', 'op': '=', 'expr': "input(20,'')", 'conditions': []}, {'mode': '', 'name': 'maxwait', 'op': '=', 'expr': "input(3,'')", 'conditions': []}, {'mode': '', 'name': 'threshold', 'op': '=', 'expr': "input(0.01,'')", 'conditions': []}, {'mode': '', 'name': 'signal', 'op': '=', 'expr': '0', 'conditions': []}, {'mode': '', 'name': 'trend', 'op': '=', 'expr': '0.0', 'conditions': []}, {'mode': '', 'name': 'newtrend', 'op': '=', 'expr': '0.0', 'conditions': []}, {'mode': '', 'name': 'wait', 'op': '=', 'expr': '0.0', 'conditions': []}, {'mode': '', 'name': 'initialentry', 'op': '=', 'expr': '0.0', 'conditions': []}, {'mode': '', 'name': 'trend', 'op': ':=', 'expr': 'sma(close,period)', 'conditions': []}, {'mode': '', 'name': 'signal', 'op': ':=', 'expr': 'nz(signal[1])', 'conditions': []}, {'mode': '', 'name': 'signal', 'op': ':=', 'expr': '1', 'conditions': ['trend > nz(trend[1])']}, {'mode': '', 'name': 'signal', 'op': ':=', 'expr': '-1', 'conditions': ['ELSE', 'trend < nz(trend[1])']}, {'mode': '', 'name': 'wait', 'op': ':=', 'expr': 'nz(wait[1])', 'conditions': []}, {'mode': '', 'name': 'initialentry', 'op': ':=', 'expr': 'nz(initialentry[1])', 'conditions': []}, {'mode': '', 'name': 'signal', 'op': ':=', 'expr': '-1', 'conditions': ['signal != signal[1]', 'strategy.position_size > 0']}, {'mode': '', 'name': 'signal', 'op': ':=', 'expr': '1', 'conditions': ['signal != signal[1]', 'ELSE', 'strategy.position_size < 0']}, {'mode': '', 'name': 'wait', 'op': ':=', 'expr': '0', 'conditions': ['signal != signal[1]']}, {'mode': '', 'name': 'initialentry', 'op': ':=', 'expr': 'close', 'conditions': ['signal != signal[1]']}, {'mode': '', 'name': 'wait', 'op': ':=', 'expr': 'wait + 1', 'conditions': ['ELSE', 'signal != 0 and strategy.position_size == 0']}]
    pine_user_functions = []
    pine_controls = [{'indent': 0, 'statement': 'if trend > nz(trend[1])'}, {'indent': 0, 'statement': 'else'}, {'indent': 1, 'statement': 'if trend < nz(trend[1])'}, {'indent': 0, 'statement': 'if signal != signal[1]'}, {'indent': 1, 'statement': 'if strategy.position_size > 0'}, {'indent': 1, 'statement': 'else'}, {'indent': 2, 'statement': 'if strategy.position_size < 0'}, {'indent': 0, 'statement': 'else'}, {'indent': 1, 'statement': 'if signal != 0 and strategy.position_size == 0'}, {'indent': 0, 'statement': 'if strategy.position_size == 0'}, {'indent': 1, 'statement': 'if wait >= maxwait'}, {'indent': 2, 'statement': 'if signal > 0'}, {'indent': 2, 'statement': 'else'}, {'indent': 3, 'statement': 'if signal < 0'}, {'indent': 1, 'statement': 'else'}, {'indent': 2, 'statement': 'if signal > 0 and close < initialentry - threshold'}, {'indent': 2, 'statement': 'else'}, {'indent': 3, 'statement': 'if signal < 0 and close > initialentry + threshold'}]
    pine_orders = [{'kind': 'close', 'call': "strategy.close('long',comment='trend sell')", 'conditions': ['signal != signal[1]', 'strategy.position_size > 0'], 'statement': "strategy.close('long',comment='trend sell')"}, {'kind': 'close', 'call': "strategy.close('short',comment='trend buy')", 'conditions': ['signal != signal[1]', 'ELSE', 'strategy.position_size < 0'], 'statement': "strategy.close('short',comment='trend buy')"}, {'kind': 'entry', 'call': "strategy.entry('long',strategy.long, comment='maxtime Long')", 'conditions': ['strategy.position_size == 0', 'wait >= maxwait', 'signal > 0'], 'statement': "strategy.entry('long',strategy.long, comment='maxtime Long')"}, {'kind': 'entry', 'call': "strategy.entry('short',strategy.short, comment='maxtime Short')", 'conditions': ['strategy.position_size == 0', 'wait >= maxwait', 'ELSE', 'signal < 0'], 'statement': "strategy.entry('short',strategy.short, comment='maxtime Short')"}, {'kind': 'entry', 'call': "strategy.entry('long',strategy.long, comment='delayed Long')", 'conditions': ['strategy.position_size == 0', 'ELSE', 'signal > 0 and close < initialentry - threshold'], 'statement': "strategy.entry('long',strategy.long, comment='delayed Long')"}, {'kind': 'entry', 'call': "strategy.entry('short',strategy.short, comment='delayed short')", 'conditions': ['strategy.position_size == 0', 'ELSE', 'ELSE', 'signal < 0 and close > initialentry + threshold'], 'statement': "strategy.entry('short',strategy.short, comment='delayed short')"}]
    original_pine = '/*backtest\nstart: 2023-08-14 00:00:00\nend: 2023-09-13 00:00:00\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This source code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © dongyun\n\n//@version=4\nstrategy("等待一个更好的入场机会", overlay=true)\n\nperiod = input(20,\'\')\nmaxwait = input(3,\'\')\nthreshold = input(0.01,\'\')\n\nsignal = 0\ntrend = 0.0\nnewtrend = 0.0\nwait = 0.0\ninitialentry = 0.0\n\ntrend := sma(close,period)\nsignal := nz(signal[1])\nif trend > nz(trend[1])\n\tsignal := 1\nelse\n\tif trend < nz(trend[1])\n\t\tsignal := -1\n\nwait := nz(wait[1])\ninitialentry := nz(initialentry[1])\n\nif signal != signal[1]\n\tif strategy.position_size > 0\n\t\tstrategy.close(\'long\',comment=\'trend sell\')\n\t\tsignal := -1\n\telse\n\t\tif strategy.position_size < 0\n    \t\tstrategy.close(\'short\',comment=\'trend buy\')\n    \t\tsignal := 1\n\twait := 0\n\tinitialentry := close\nelse\n\tif signal != 0 and strategy.position_size == 0\n\t\twait := wait + 1\n\n// test for better entry\nif strategy.position_size == 0\n\tif wait >= maxwait\n\t\tif signal > 0\n\t\t\tstrategy.entry(\'long\',strategy.long, comment=\'maxtime Long\')\n\t\telse\n\t\t\tif signal < 0\n\t\t\t\tstrategy.entry(\'short\',strategy.short, comment=\'maxtime Short\')\n\telse\n\t\tif signal > 0 and close < initialentry - threshold\n\t\t\tstrategy.entry(\'long\',strategy.long, comment=\'delayed Long\')\n\t\telse\n\t\t\tif signal < 0 and close > initialentry + threshold\n\t\t\t\tstrategy.entry(\'short\',strategy.short, comment=\'delayed short\')'

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
