"""Source-faithful deep-assisted port of 移动均线布林带融合交易策略Moving-Average-Bollinger-Band-Fusion-Trading-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_3e6dd8c5(PinePortBase, IStrategy):
    source_file = '移动均线布林带融合交易策略Moving-Average-Bollinger-Band-Fusion-Trading-Strategy.md'
    timeframe = '3h'
    can_short = False
    source_defaults = {'BBlength': 24}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.entry', 'strategy.close', 'for ']
    source_fidelity_notes = []
    pine_assignments = [{'mode': '', 'name': 'ma_short', 'op': '=', 'expr': 'sma(close,8)', 'conditions': []}, {'mode': '', 'name': 'ma_long', 'op': '=', 'expr': 'sma(close,89)', 'conditions': []}, {'mode': '', 'name': 'entry_ma', 'op': '=', 'expr': 'crossover (ma_short,ma_long)', 'conditions': []}, {'mode': '', 'name': 'exit_ma', 'op': '=', 'expr': 'crossunder (ma_short,ma_long)', 'conditions': []}, {'mode': '', 'name': 'BBlength', 'op': '=', 'expr': 'input(24, minval=1,title="Bollinger Period Length")', 'conditions': []}, {'mode': '', 'name': 'BBmult', 'op': '=', 'expr': '2 // input(2.0, minval=0.001, maxval=50,title="Bollinger Bands Standard Deviation")', 'conditions': []}, {'mode': '', 'name': 'BBbasis', 'op': '=', 'expr': 'sma(close, BBlength)', 'conditions': []}, {'mode': '', 'name': 'BBdev', 'op': '=', 'expr': 'BBmult * stdev(close, BBlength)', 'conditions': []}, {'mode': '', 'name': 'BBupper', 'op': '=', 'expr': 'BBbasis + BBdev', 'conditions': []}, {'mode': '', 'name': 'BBlower', 'op': '=', 'expr': 'BBbasis - BBdev', 'conditions': []}, {'mode': '', 'name': 'source', 'op': '=', 'expr': 'close', 'conditions': []}, {'mode': '', 'name': 'entry_bb', 'op': '=', 'expr': 'crossover(source, BBlower)', 'conditions': []}, {'mode': '', 'name': 'exit_bb', 'op': '=', 'expr': 'crossunder(source, BBupper)', 'conditions': []}, {'mode': '', 'name': 'vs_entry', 'op': '=', 'expr': 'false', 'conditions': []}, {'mode': '', 'name': 'vs_exit', 'op': '=', 'expr': 'false', 'conditions': []}, {'mode': '', 'name': 'vs_entry', 'op': ':=', 'expr': 'true', 'conditions': ['(entry_bb[i])']}, {'mode': '', 'name': 'vs_exit', 'op': ':=', 'expr': 'true', 'conditions': ['(exit_bb[i])']}, {'mode': '', 'name': 'entry', 'op': '=', 'expr': 'entry_ma and vs_entry', 'conditions': []}, {'mode': '', 'name': 'exit', 'op': '=', 'expr': 'exit_ma and vs_exit', 'conditions': []}]
    pine_user_functions = []
    pine_controls = [{'indent': 0, 'statement': 'for i = 0 to 63'}, {'indent': 4, 'statement': 'if (entry_bb[i])'}, {'indent': 4, 'statement': 'if (exit_bb[i])'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry(id="long_ma",long=true,when=entry)', 'conditions': [], 'statement': 'strategy.entry(id="long_ma",long=true,when=entry)'}, {'kind': 'close', 'call': 'strategy.close(id="long_ma", when=exit)', 'conditions': [], 'statement': 'strategy.close(id="long_ma", when=exit)'}, {'kind': 'entry', 'call': 'strategy.entry(id="short_ma",long=false,when=exit)', 'conditions': [], 'statement': 'strategy.entry(id="short_ma",long=false,when=exit)'}, {'kind': 'close', 'call': 'strategy.close(id="short_ma",when=entry)', 'conditions': [], 'statement': 'strategy.close(id="short_ma",when=entry)'}]
    original_pine = '/*backtest\nstart: 2023-08-18 00:00:00\nend: 2023-09-17 00:00:00\nperiod: 3h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=2\nstrategy("MA-Zorrillo",overlay=true)\n\nma_short= sma(close,8)\nma_long= sma(close,89)\n\nentry_ma = crossover (ma_short,ma_long)\nexit_ma = crossunder (ma_short,ma_long) \n\n\nBBlength = input(24, minval=1,title="Bollinger Period Length")\nBBmult = 2 // input(2.0, minval=0.001, maxval=50,title="Bollinger Bands Standard Deviation")\nBBbasis = sma(close, BBlength)\nBBdev = BBmult * stdev(close, BBlength)\nBBupper = BBbasis + BBdev\nBBlower = BBbasis - BBdev\n\nsource = close\nentry_bb = crossover(source, BBlower)\nexit_bb = crossunder(source, BBupper)\n\n\nvs_entry = false\nvs_exit = false\nfor i = 0 to 63\n    if (entry_bb[i])\n        vs_entry :=  true\n    if (exit_bb[i])\n        vs_exit :=  true\n        \n\nentry = entry_ma and vs_entry\nexit =  exit_ma and vs_exit\n\nstrategy.entry(id="long_ma",long=true,when=entry)\nstrategy.close(id="long_ma", when=exit)\n\nstrategy.entry(id="short_ma",long=false,when=exit)\nstrategy.close(id="short_ma",when=entry)'

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
