"""Source-faithful deep-assisted port of 波动突破交易策略Volatility-Breakout-Trading-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_b9055a40(PinePortBase, IStrategy):
    source_file = '波动突破交易策略Volatility-Breakout-Trading-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_pyramiding = 5
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.entry', 'strategy.position_size', 'for ', 'label.']
    source_fidelity_notes = ['Reads broker/strategy state; signals depend on fill timing and cannot be reduced to indicator-only booleans without changing behavior.', 'Drawing/table calls are display-only unless their IDs/state are later read; preserved in source map but excluded from trade signal calculation where non-causal.']
    pine_assignments = [{'mode': '', 'name': 'signal_hh', 'op': '=', 'expr': '0', 'conditions': []}, {'mode': '', 'name': 'signal_ll', 'op': '=', 'expr': '0', 'conditions': []}, {'mode': '', 'name': 'signal_hh', 'op': ':=', 'expr': '1', 'conditions': ['close[1] >= open[1] and close[2] >= open[2] and close[3] >= open[3]']}, {'mode': '', 'name': 'signal_ll', 'op': ':=', 'expr': '1', 'conditions': ['close[1] <= open[1] and close[2] <= open[2] and close[3] <= open[3]']}, {'mode': '', 'name': 'signal_vol', 'op': '=', 'expr': '0', 'conditions': []}, {'mode': '', 'name': 'max_volume', 'op': '=', 'expr': '0.0', 'conditions': []}, {'mode': '', 'name': 'vol_length', 'op': '=', 'expr': 'input(title="Volume length", type=input.integer, defval=3)', 'conditions': []}, {'mode': '', 'name': 'max_volume', 'op': ':=', 'expr': 'volume[i]', 'conditions': ['volume[i] > max_volume']}, {'mode': '', 'name': 'signal_vol', 'op': ':=', 'expr': '1', 'conditions': ['volume[0] > max_volume']}, {'mode': '', 'name': 'signal_buy', 'op': '=', 'expr': '0', 'conditions': []}, {'mode': '', 'name': 'signal_sell', 'op': '=', 'expr': '0', 'conditions': []}, {'mode': '', 'name': 'signal_buy', 'op': ':=', 'expr': '1', 'conditions': ['signal_hh and signal_vol']}, {'mode': '', 'name': 'signal_sell', 'op': ':=', 'expr': '1', 'conditions': ['signal_ll and signal_vol']}]
    pine_user_functions = []
    pine_controls = [{'indent': 0, 'statement': 'if close[1] >= open[1] and close[2] >= open[2] and close[3] >= open[3]'}, {'indent': 0, 'statement': 'if close[1] <= open[1] and close[2] <= open[2] and close[3] <= open[3]'}, {'indent': 0, 'statement': 'for i = vol_length to 1'}, {'indent': 4, 'statement': 'if volume[i] > max_volume'}, {'indent': 0, 'statement': 'if volume[0] > max_volume'}, {'indent': 0, 'statement': 'if signal_hh and signal_vol'}, {'indent': 0, 'statement': 'if signal_ll and signal_vol'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("buy", strategy.long, 5)//, when=strategy.position_size <= 0)', 'conditions': ['signal_hh and signal_vol'], 'statement': 'strategy.entry("buy", strategy.long, 5)//, when=strategy.position_size <= 0)'}, {'kind': 'entry', 'call': 'strategy.entry("sell", strategy.short, 5)//, when=strategy.position_size > 0)', 'conditions': ['signal_ll and signal_vol'], 'statement': 'strategy.entry("sell", strategy.short, 5)//, when=strategy.position_size > 0)'}]
    original_pine = '/*backtest\nstart: 2022-12-04 00:00:00\nend: 2023-03-12 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=4\nstrategy("SPAS", overlay=true, pyramiding=5, calc_on_order_fills=true)\n\nint signal_hh = 0\nint signal_ll = 0\n\nif close[1] >= open[1] and close[2] >= open[2] and close[3] >= open[3]\n    signal_hh := 1\n\nif close[1] <= open[1] and close[2] <= open[2] and close[3] <= open[3]\n    signal_ll := 1\n\nplotchar(signal_hh, char=\'H\', size=size.tiny, location=location.abovebar)\nplotchar(signal_ll, char=\'L\', size=size.tiny, location=location.abovebar)\n\nint signal_vol = 0\nfloat max_volume = 0.0\nint vol_length = input(title="Volume length", type=input.integer, defval=3)\n\nfor i = vol_length to 1\n    if volume[i] > max_volume\n        max_volume := volume[i]\n\nif volume[0] > max_volume\n    signal_vol := 1\n\nplotchar(signal_vol, char=\'V\', size=size.tiny, location=location.bottom)\n\nint signal_buy = 0\nint signal_sell = 0\n\nif signal_hh and signal_vol\n    signal_buy := 1\n    label.new(bar_index, high, "B", color=color.green)\n    strategy.entry("buy", strategy.long, 5)//, when=strategy.position_size <= 0)\n\nif signal_ll and signal_vol\n    signal_sell := 1\n    label.new(bar_index, low, "S", color=color.red)\n    strategy.entry("sell", strategy.short, 5)//, when=strategy.position_size > 0)\n\n//plotchar(signal_buy, char=\'B\', color=color.green, size=size.tiny, location=location.abovebar)\nplotarrow(signal_buy, colorup=color.green, colordown=color.orange, transp=0, maxheight=20)\n\n//plotchar(signal_sell, char=\'S\', color=color.red, size=size.tiny, location=location.abovebar)\nplotarrow(signal_sell * -1, colorup=color.green, colordown=color.orange, transp=0, maxheight=20)'

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
