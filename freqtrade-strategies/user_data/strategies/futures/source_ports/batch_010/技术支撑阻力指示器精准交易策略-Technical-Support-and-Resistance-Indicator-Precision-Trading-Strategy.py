"""Source-faithful deep-assisted port of 技术支撑阻力指示器精准交易策略-Technical-Support-and-Resistance-Indicator-Precision-Trading-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_b69212ff(PinePortBase, IStrategy):
    source_file = '技术支撑阻力指示器精准交易策略-Technical-Support-and-Resistance-Indicator-Precision-Trading-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.entry', 'for ']
    source_fidelity_notes = []
    pine_assignments = [{'mode': '', 'name': 'highMax', 'op': '=', 'expr': 'ta.highest(high, 20)', 'conditions': []}, {'mode': '', 'name': 'lowMin', 'op': '=', 'expr': 'ta.lowest(low, 20)', 'conditions': []}, {'mode': '', 'name': 'buySignal', 'op': '=', 'expr': 'close > open and close > highMax[1]', 'conditions': []}, {'mode': '', 'name': 'sellSignal', 'op': '=', 'expr': 'close < open and close < lowMin[1]', 'conditions': []}, {'mode': '', 'name': 'basis', 'op': '=', 'expr': 'ta.sma(close, 20)', 'conditions': []}, {'mode': '', 'name': 'dev', 'op': '=', 'expr': 'ta.stdev(close, 20)', 'conditions': []}, {'mode': '', 'name': 'upperBB', 'op': '=', 'expr': 'basis + 2 * dev', 'conditions': []}, {'mode': '', 'name': 'lowerBB', 'op': '=', 'expr': 'basis - 2 * dev', 'conditions': []}]
    pine_user_functions = []
    pine_controls = [{'indent': 0, 'statement': 'if (buySignal)'}, {'indent': 0, 'statement': 'if (sellSignal)'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("Buy", strategy.long)', 'conditions': ['(buySignal)'], 'statement': 'strategy.entry("Buy", strategy.long)'}, {'kind': 'entry', 'call': 'strategy.entry("Sell", strategy.short)', 'conditions': ['(sellSignal)'], 'statement': 'strategy.entry("Sell", strategy.short)'}]
    original_pine = '/*backtest\nstart: 2023-07-23 00:00:00\nend: 2024-07-28 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("Mars Signals: Precision Trading", overlay=true)\n\n// Calculate the highest highs and lowest lows for support and resistance points\nfloat highMax = ta.highest(high, 20)\nfloat lowMin = ta.lowest(low, 20)\n\n// Draw support and resistance lines\nplot(highMax, "Resistance", color=color.red)\nplot(lowMin, "Support", color=color.green)\n\n// Identify price action patterns for deciding on buying or selling\nbool buySignal = close > open and close > highMax[1]\nbool sellSignal = close < open and close < lowMin[1]\n\n// Plot buy and sell signals\nplotshape(series=buySignal, location=location.belowbar, color=color.green, style=shape.labelup, text="Buy")\nplotshape(series=sellSignal, location=location.abovebar, color=color.red, style=shape.labeldown, text="Sell")\n\n// Display Bollinger Bands for further analysis\nfloat basis = ta.sma(close, 20)\nfloat dev = ta.stdev(close, 20)\nfloat upperBB = basis + 2 * dev\nfloat lowerBB = basis - 2 * dev\nplot(upperBB, "Upper Bollinger Band", color=color.purple)\nplot(lowerBB, "Lower Bollinger Band", color=color.orange)\n\n// Use strategy function for entering and exiting trades\nif (buySignal)\n    strategy.entry("Buy", strategy.long)\nif (sellSignal)\n    strategy.entry("Sell", strategy.short)'

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
