"""Source-faithful deep-assisted port of 积极底部截获量化策略Aggressive-Bottom-Sniping-Quantitative-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_8ec48952(PinePortBase, IStrategy):
    source_file = '积极底部截获量化策略Aggressive-Bottom-Sniping-Quantitative-Strategy.md'
    timeframe = '1m'
    can_short = False
    source_defaults = {'v_len': 20, 'mult': 2, 'rsi_len': 20, 'oversold': 30, 'close_time': 10}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.entry', 'strategy.close', 'strategy.position_size']
    source_fidelity_notes = ['Reads broker/strategy state; signals depend on fill timing and cannot be reduced to indicator-only booleans without changing behavior.']
    pine_assignments = [{'mode': '', 'name': 'v_len', 'op': '=', 'expr': 'input(20, title="Volume SMA Length")', 'conditions': []}, {'mode': '', 'name': 'mult', 'op': '=', 'expr': 'input(2)', 'conditions': []}, {'mode': '', 'name': 'rsi_len', 'op': '=', 'expr': 'input(20, title="RSI Length")', 'conditions': []}, {'mode': '', 'name': 'oversold', 'op': '=', 'expr': 'input(30, title="Oversold")', 'conditions': []}, {'mode': '', 'name': 'close_time', 'op': '=', 'expr': 'input(10, title="Close After")', 'conditions': []}, {'mode': '', 'name': 'v', 'op': '=', 'expr': 'volume', 'conditions': []}, {'mode': '', 'name': 'basis', 'op': '=', 'expr': 'sma(v, v_len)', 'conditions': []}, {'mode': '', 'name': 'dev', 'op': '=', 'expr': 'mult * stdev(v, v_len)', 'conditions': []}, {'mode': '', 'name': 'upper_volume', 'op': '=', 'expr': 'basis + dev', 'conditions': []}, {'mode': '', 'name': 'rsi', 'op': '=', 'expr': 'rsi(close, rsi_len)', 'conditions': []}, {'mode': '', 'name': 'long', 'op': '=', 'expr': 'v > upper_volume and rsi < oversold', 'conditions': []}, {'mode': '', 'name': 'passed_time', 'op': '=', 'expr': '0.0', 'conditions': []}, {'mode': '', 'name': 'passed_time', 'op': ':=', 'expr': '1', 'conditions': ['strategy.position_size != 0']}, {'mode': '', 'name': 'passed_time', 'op': ':=', 'expr': '0', 'conditions': ['ELSE']}, {'mode': '', 'name': 'passed_time', 'op': ':=', 'expr': 'passed_time[1] + 1', 'conditions': ['strategy.position_size != 0 and strategy.position_size[1] != 0']}, {'mode': '', 'name': 'v_color', 'op': '=', 'expr': 'close >= close[1] ? color.new(#3eb370, 0) : color.new(#e9546b, 0)', 'conditions': []}]
    pine_user_functions = []
    pine_controls = [{'indent': 0, 'statement': 'if strategy.position_size != 0'}, {'indent': 0, 'statement': 'else'}, {'indent': 0, 'statement': 'if strategy.position_size != 0 and strategy.position_size[1] != 0'}, {'indent': 0, 'statement': 'if passed_time >= close_time'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("Long", true, when=long)', 'conditions': [], 'statement': 'strategy.entry("Long", true, when=long)'}, {'kind': 'close_all', 'call': 'strategy.close_all()', 'conditions': ['passed_time >= close_time'], 'statement': 'strategy.close_all()'}]
    original_pine = '/*backtest\nstart: 2024-01-10 00:00:00\nend: 2024-01-17 00:00:00\nperiod: 1m\nbasePeriod: 1m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This source code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © footlz\n\n//@version=4\nstrategy("Bottom catch strategy", overlay=true)\n\nv_len = input(20, title="Volume SMA Length")\nmult = input(2)\nrsi_len = input(20, title="RSI Length")\noversold = input(30, title="Oversold")\nclose_time = input(10, title="Close After")\n\nv = volume\nbasis = sma(v, v_len)\ndev = mult * stdev(v, v_len)\nupper_volume = basis + dev\n\nrsi = rsi(close, rsi_len)\n\nlong = v > upper_volume and rsi < oversold\n\nstrategy.entry("Long", true, when=long)\n\npassed_time = 0.0\nif strategy.position_size != 0\n    passed_time := 1\nelse\n    passed_time := 0\n\nif strategy.position_size != 0 and strategy.position_size[1] != 0\n    passed_time := passed_time[1] + 1\n\nif passed_time >= close_time\n    strategy.close_all()\n\n// If want to enable plot, change overlay=false.\nv_color = close >= close[1] ? color.new(#3eb370, 0) : color.new(#e9546b, 0)\n\n// plot(v, title="volume", color=v_color, style=plot.style_columns)\n// plot(upper_volume, title="Threshold", color=color.aqua)'

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
