"""Source-faithful deep-assisted port of 干浪激活器策略Gann-HiLo-Activator-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_dd942e7c(PinePortBase, IStrategy):
    source_file = '干浪激活器策略Gann-HiLo-Activator-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'len': 3, 'displace': 1, 'from_start': False, 'backtest_year': 2017, 'backtest_month': 1, 'backtest_day': 1}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 20.0
    source_pyramiding = 0
    source_initial_capital = 1000.0
    source_commission_percent = 0.0
    source_features = ['strategy.entry']
    source_fidelity_notes = []
    pine_assignments = [{'mode': '', 'name': 'len', 'op': '=', 'expr': "input.int(3, 'Length', step=1, minval=1)", 'conditions': []}, {'mode': '', 'name': 'displace', 'op': '=', 'expr': "input.int(1, 'Offset', step=1, minval=0)", 'conditions': []}, {'mode': '', 'name': 'from_start', 'op': '=', 'expr': "input(false, 'Begin from start?')", 'conditions': []}, {'mode': '', 'name': 'backtest_year', 'op': '=', 'expr': "input(2017, 'From Year')", 'conditions': []}, {'mode': '', 'name': 'backtest_month', 'op': '=', 'expr': "input.int(01, 'From Month', minval=1, maxval=12, step=1)", 'conditions': []}, {'mode': '', 'name': 'backtest_day', 'op': '=', 'expr': "input.int(01, 'From Day', minval=1, maxval=31, step=1)", 'conditions': []}, {'mode': '', 'name': 'start_time', 'op': '=', 'expr': 'from_start ? 0 : timestamp(backtest_year, backtest_month, backtest_day, 00, 00)', 'conditions': []}, {'mode': '', 'name': 'hilo', 'op': '=', 'expr': 'na', 'conditions': []}, {'mode': '', 'name': 'hi', 'op': '=', 'expr': 'ta.sma(high, len)', 'conditions': []}, {'mode': '', 'name': 'lo', 'op': '=', 'expr': 'ta.sma(low, len)', 'conditions': []}, {'mode': '', 'name': 'hilo', 'op': ':=', 'expr': 'close > hi[displace] ? 1 : close < lo[displace] ? -1 : hilo[1]', 'conditions': []}, {'mode': '', 'name': 'ghla', 'op': '=', 'expr': 'hilo == -1 ? hi[displace] : lo[displace]', 'conditions': []}, {'mode': '', 'name': 'color', 'op': '=', 'expr': 'hilo == -1 ? color.red : color.green', 'conditions': []}, {'mode': '', 'name': 'buyCondition', 'op': '=', 'expr': 'hilo == 1 and hilo[1] == -1', 'conditions': []}, {'mode': '', 'name': 'sellCondition', 'op': '=', 'expr': 'hilo == -1 and hilo[1] == 1', 'conditions': []}]
    pine_user_functions = []
    pine_controls = [{'indent': 0, 'statement': 'if buyCondition and time >= start_time'}, {'indent': 0, 'statement': 'if sellCondition and time >= start_time'}]
    pine_orders = [{'kind': 'entry', 'call': "strategy.entry('Long', strategy.long)", 'conditions': ['buyCondition and time >= start_time'], 'statement': "strategy.entry('Long', strategy.long)"}, {'kind': 'entry', 'call': "strategy.entry('Short', strategy.short)", 'conditions': ['sellCondition and time >= start_time'], 'statement': "strategy.entry('Short', strategy.short)"}]
    original_pine = '/*backtest\nstart: 2022-09-10 00:00:00\nend: 2023-09-16 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This source code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © starbolt\n\n//@version=5\nstrategy(\'Gann HiLo Activator Strategy\', overlay=true, pyramiding=0, default_qty_type=strategy.percent_of_equity, default_qty_value=20, initial_capital=1000, process_orders_on_close=true)\n\nlen = input.int(3, \'Length\', step=1, minval=1)\ndisplace = input.int(1, \'Offset\', step=1, minval=0)\nfrom_start = input(false, \'Begin from start?\')\nbacktest_year = input(2017, \'From Year\')\nbacktest_month = input.int(01, \'From Month\', minval=1, maxval=12, step=1)\nbacktest_day = input.int(01, \'From Day\', minval=1, maxval=31, step=1)\n\nstart_time = from_start ? 0 : timestamp(backtest_year, backtest_month, backtest_day, 00, 00)\n\nfloat hilo = na\nhi = ta.sma(high, len)\nlo = ta.sma(low, len)\n\nhilo := close > hi[displace] ? 1 : close < lo[displace] ? -1 : hilo[1]\nghla = hilo == -1 ? hi[displace] : lo[displace]\ncolor = hilo == -1 ? color.red : color.green\n\nbuyCondition = hilo == 1 and hilo[1] == -1\nsellCondition = hilo == -1 and hilo[1] == 1\n\nif buyCondition and time >= start_time\n    strategy.entry(\'Long\', strategy.long)\n\nif sellCondition and time >= start_time\n    strategy.entry(\'Short\', strategy.short)\n\nplot(ghla, color=color, style=plot.style_cross)'

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
