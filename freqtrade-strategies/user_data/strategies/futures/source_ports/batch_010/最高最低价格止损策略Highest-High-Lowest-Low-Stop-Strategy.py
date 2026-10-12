"""Source-faithful deep-assisted port of 最高最低价格止损策略Highest-High-Lowest-Low-Stop-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_0b13927d(PinePortBase, IStrategy):
    source_file = '最高最低价格止损策略Highest-High-Lowest-Low-Stop-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'hiLen': 20, 'loLen': 20}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.exit', 'strategy.entry', 'strategy.position_size', 'for ']
    source_fidelity_notes = ['Reads broker/strategy state; signals depend on fill timing and cannot be reduced to indicator-only booleans without changing behavior.', 'Uses strategy.exit; stop/limit/profit/loss/trailing arguments have Pine order semantics and may fill intrabar.']
    pine_assignments = [{'mode': '', 'name': 'hiLen', 'op': '=', 'expr': 'input.int(20, title="Highest High Lookback", minval=2)', 'conditions': []}, {'mode': '', 'name': 'loLen', 'op': '=', 'expr': 'input.int(20, title="Lowest Low Lookback", minval=2)', 'conditions': []}, {'mode': '', 'name': 'hiHighs', 'op': '=', 'expr': 'ta.highest(high, hiLen)[1]', 'conditions': []}, {'mode': '', 'name': 'loLows', 'op': '=', 'expr': 'ta.lowest(low, loLen)[1]', 'conditions': []}, {'mode': '', 'name': 'higherCloses', 'op': '=', 'expr': 'close > close[1] and', 'conditions': []}, {'mode': '', 'name': 'lowerCloses', 'op': '=', 'expr': 'close < close[1] and', 'conditions': []}, {'mode': '', 'name': 'isFlat', 'op': '=', 'expr': 'strategy.position_size == 0', 'conditions': []}]
    pine_user_functions = []
    pine_controls = [{'indent': 0, 'statement': 'if isFlat and higherCloses'}, {'indent': 0, 'statement': 'if isFlat and lowerCloses'}, {'indent': 0, 'statement': 'if strategy.position_size > 0'}, {'indent': 0, 'statement': 'if strategy.position_size < 0'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("EL", strategy.long)', 'conditions': ['isFlat and higherCloses'], 'statement': 'strategy.entry("EL", strategy.long)'}, {'kind': 'entry', 'call': 'strategy.entry("ES", strategy.short)', 'conditions': ['isFlat and lowerCloses'], 'statement': 'strategy.entry("ES", strategy.short)'}, {'kind': 'exit', 'call': 'strategy.exit("XL HH", stop=loLows)', 'conditions': ['strategy.position_size > 0'], 'statement': 'strategy.exit("XL HH", stop=loLows)'}, {'kind': 'exit', 'call': 'strategy.exit("XS LL", stop=hiHighs)', 'conditions': ['strategy.position_size < 0'], 'statement': 'strategy.exit("XS LL", stop=hiHighs)'}]
    original_pine = '/*backtest\nstart: 2023-03-02 00:00:00\nend: 2024-03-07 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy(title="Highest high/lowest low stop", overlay=true)\n\n// STEP 1:\n// Make inputs for length of highest high and lowest low\nhiLen = input.int(20, title="Highest High Lookback", minval=2)\nloLen = input.int(20, title="Lowest Low Lookback", minval=2)\n\n// STEP 2:\n// Calculate recent extreme high and low\nhiHighs = ta.highest(high, hiLen)[1]\nloLows  = ta.lowest(low, loLen)[1]\n\n// Plot stop values for visual confirmation\nplot(strategy.position_size > 0 ? loLows : na,\n     style=plot.style_circles, color=color.green, linewidth=3,\n     title="Lowest Low Stop")\n\nplot(strategy.position_size < 0 ? hiHighs : na,\n     style=plot.style_circles, color=color.red, linewidth=3,\n     title="Highest High Stop")\n\n// Trading conditions for this example strategy\nhigherCloses = close > close[1] and\n     close[1] > close[2] and \n     close[2] > close[3]\n\nlowerCloses = close < close[1] and\n     close[1] < close[2] and \n     close[2] < close[3]\n\nisFlat = strategy.position_size == 0\n\n// Submit entry orders\nif isFlat and higherCloses\n    strategy.entry("EL", strategy.long)\n\nif isFlat and lowerCloses\n    strategy.entry("ES", strategy.short)\n\n// STEP 3:\n// Submit stops based on highest high and lowest low\nif strategy.position_size > 0\n    strategy.exit("XL HH", stop=loLows)\n\nif strategy.position_size < 0\n    strategy.exit("XS LL", stop=hiHighs)'

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
