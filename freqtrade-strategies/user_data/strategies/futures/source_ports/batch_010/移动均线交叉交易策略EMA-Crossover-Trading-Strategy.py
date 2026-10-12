"""Source-faithful deep-assisted port of 移动均线交叉交易策略EMA-Crossover-Trading-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_fef4bbfe(PinePortBase, IStrategy):
    source_file = '移动均线交叉交易策略EMA-Crossover-Trading-Strategy.md'
    timeframe = '1h'
    can_short = True
    source_defaults = {'position_size_pct': 1, 'len1': 25, 'src1': 'close', 'len2': 100, 'src2': 'close', 'lenrsi': 14}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.entry', 'var ', 'for ']
    source_fidelity_notes = ['Uses persistent Pine state (var/varip); state is order-dependent and must be evaluated bar-by-bar, not replaced by a vectorized fill-forward approximation.']
    pine_assignments = [{'mode': '', 'name': 'position_size_pct', 'op': '=', 'expr': "input(1, title='Position Size (%)') / 100", 'conditions': []}, {'mode': '', 'name': 'len1', 'op': '=', 'expr': "input.int(25, minval=1, title='EMA 1')", 'conditions': []}, {'mode': '', 'name': 'src1', 'op': '=', 'expr': "input(close, title='Source')", 'conditions': []}, {'mode': '', 'name': 'ema1', 'op': '=', 'expr': 'ta.ema(src1, len1)', 'conditions': []}, {'mode': '', 'name': 'len2', 'op': '=', 'expr': "input.int(100, minval=1, title='EMA 2')", 'conditions': []}, {'mode': '', 'name': 'src2', 'op': '=', 'expr': "input(close, title='Source')", 'conditions': []}, {'mode': '', 'name': 'ema2', 'op': '=', 'expr': 'ta.ema(src2, len2)', 'conditions': []}, {'mode': '', 'name': 'lenrsi', 'op': '=', 'expr': "input(14, title='RSI length')", 'conditions': []}, {'mode': '', 'name': 'outrsi', 'op': '=', 'expr': 'ta.rsi(close,lenrsi)', 'conditions': []}, {'mode': '', 'name': 'bodybar1', 'op': '=', 'expr': 'math.abs(close - open)', 'conditions': []}, {'mode': '', 'name': 'bodybar2', 'op': '=', 'expr': 'math.abs(close[1] - open[1])', 'conditions': []}, {'mode': '', 'name': 'emaCrossoverUp', 'op': '=', 'expr': 'ta.crossover(ema1, ema2)', 'conditions': []}, {'mode': '', 'name': 'emaCrossoverDown', 'op': '=', 'expr': 'ta.crossunder(ema1, ema2)', 'conditions': []}, {'mode': 'var', 'name': 'entrybar', 'op': '=', 'expr': 'close // Initialize entrybar with the current close', 'conditions': []}, {'mode': '', 'name': 'emaCrossoverUpOccured', 'op': '=', 'expr': 'ta.crossover(close, ema1) and ema1 > ema2 and bodybar1 > bodybar2 and close > entrybar', 'conditions': []}, {'mode': '', 'name': 'emaCrossoverDownOccured', 'op': '=', 'expr': 'ta.crossunder(close, ema1) and ema1 < ema2 and bodybar1 > bodybar2 and close < entrybar', 'conditions': []}]
    pine_user_functions = []
    pine_controls = [{'indent': 0, 'statement': 'if emaCrossoverUpOccured'}, {'indent': 0, 'statement': 'else if emaCrossoverDownOccured'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("Enter Long", strategy.long)', 'conditions': ['emaCrossoverUpOccured'], 'statement': 'strategy.entry("Enter Long", strategy.long)'}, {'kind': 'entry', 'call': 'strategy.entry("Enter Short", strategy.short)', 'conditions': ['emaCrossoverDownOccured'], 'statement': 'strategy.entry("Enter Short", strategy.short)'}]
    original_pine = '/*backtest\nstart: 2023-11-11 00:00:00\nend: 2023-12-11 00:00:00\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy(\'EMA Crossover Signal\', shorttitle=\'EMA Crossover Signal\', overlay=true)\n// Define input for position size as a percentage of equity\nposition_size_pct = input(1, title=\'Position Size (%)\') / 100\n\n//Input EMA\nlen1 = input.int(25, minval=1, title=\'EMA 1\')\nsrc1 = input(close, title=\'Source\')\nema1 = ta.ema(src1, len1)\nlen2 = input.int(100, minval=1, title=\'EMA 2\')\nsrc2 = input(close, title=\'Source\')\nema2 = ta.ema(src2, len2)\n//End of format\n\n//Format RSI\nlenrsi = input(14, title=\'RSI length\')\noutrsi = ta.rsi(close,lenrsi)\n\nbodybar1 = math.abs(close - open)\nbodybar2 = math.abs(close[1] - open[1])\n// Plot the EMAs\nplot(ema1, color=color.new(color.blue, 0), title=\'EMA 1\')\nplot(ema2, color=color.new(color.red, 0), title=\'EMA 2\')\n\n// EMA Crossover conditions\nemaCrossoverUp = ta.crossover(ema1, ema2)\nemaCrossoverDown = ta.crossunder(ema1, ema2)\nvar entrybar = close  // Initialize entrybar with the current close\n\n// Calculate crossovers outside of the if statements\nemaCrossoverUpOccured = ta.crossover(close, ema1) and ema1 > ema2 and bodybar1 > bodybar2 and close > entrybar\nemaCrossoverDownOccured = ta.crossunder(close, ema1) and ema1 < ema2 and bodybar1 > bodybar2 and close < entrybar\n\nplotshape(series=emaCrossoverUpOccured, location=location.abovebar, color=color.new(color.green, 0), style=shape.triangleup, title=\'New Buy Order\', size=size.tiny)\nplotshape(series=emaCrossoverDownOccured, location=location.belowbar, color=color.new(color.red, 0), style=shape.triangledown, title=\'New Sell Order\', size=size.tiny)\n\nif emaCrossoverUpOccured\n    strategy.entry("Enter Long", strategy.long)\nelse if emaCrossoverDownOccured\n    strategy.entry("Enter Short", strategy.short)'

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
