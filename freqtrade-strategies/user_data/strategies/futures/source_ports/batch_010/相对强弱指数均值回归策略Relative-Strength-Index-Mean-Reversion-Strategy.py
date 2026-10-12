"""Source-faithful deep-assisted port of 相对强弱指数均值回归策略Relative-Strength-Index-Mean-Reversion-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_11fd4c08(PinePortBase, IStrategy):
    source_file = '相对强弱指数均值回归策略Relative-Strength-Index-Mean-Reversion-Strategy.md'
    timeframe = '3h'
    can_short = True
    source_defaults = {}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.entry', 'strategy.close', 'strategy.position_size']
    source_fidelity_notes = ['Reads broker/strategy state; signals depend on fill timing and cannot be reduced to indicator-only booleans without changing behavior.']
    pine_assignments = [{'mode': '', 'name': 'rsiLength', 'op': '=', 'expr': '14', 'conditions': []}, {'mode': '', 'name': 'rsiThresholdBuy', 'op': '=', 'expr': '30', 'conditions': []}, {'mode': '', 'name': 'rsiThresholdSell', 'op': '=', 'expr': '70', 'conditions': []}, {'mode': '', 'name': 'smaPeriod', 'op': '=', 'expr': '20', 'conditions': []}, {'mode': '', 'name': 'stopLossPercentage', 'op': '=', 'expr': '0.5 // 0.5% stop loss', 'conditions': []}, {'mode': '', 'name': 'profitTargetPercentage', 'op': '=', 'expr': '1 // 1% profit target', 'conditions': []}, {'mode': '', 'name': 'rsi', 'op': '=', 'expr': 'ta.rsi(close, rsiLength)', 'conditions': []}, {'mode': '', 'name': 'sma', 'op': '=', 'expr': 'ta.sma(close, smaPeriod)', 'conditions': []}, {'mode': '', 'name': 'buySignal', 'op': '=', 'expr': 'rsi < rsiThresholdBuy and close < sma', 'conditions': []}, {'mode': '', 'name': 'sellSignal', 'op': '=', 'expr': 'rsi > rsiThresholdSell and close > sma', 'conditions': []}, {'mode': '', 'name': 'stopLoss', 'op': '=', 'expr': 'strategy.position_avg_price * (1 - stopLossPercentage / 100)', 'conditions': ['strategy.position_size > 0']}, {'mode': '', 'name': 'takeProfit', 'op': '=', 'expr': 'strategy.position_avg_price * (1 + profitTargetPercentage / 100)', 'conditions': ['strategy.position_size > 0']}]
    pine_user_functions = []
    pine_controls = [{'indent': 0, 'statement': 'if strategy.position_size > 0'}, {'indent': 4, 'statement': 'if close <= stopLoss or close >= takeProfit'}, {'indent': 0, 'statement': 'if buySignal'}, {'indent': 0, 'statement': 'if sellSignal'}]
    pine_orders = [{'kind': 'close', 'call': "strategy.close('Exit', comment='Stop Loss / Take Profit')", 'conditions': ['strategy.position_size > 0', 'close <= stopLoss or close >= takeProfit'], 'statement': "strategy.close('Exit', comment='Stop Loss / Take Profit')"}, {'kind': 'entry', 'call': "strategy.entry('Buy', strategy.long)", 'conditions': ['buySignal'], 'statement': "strategy.entry('Buy', strategy.long)"}, {'kind': 'entry', 'call': "strategy.entry('Sell', strategy.short)", 'conditions': ['sellSignal'], 'statement': "strategy.entry('Sell', strategy.short)"}]
    original_pine = '/*backtest\nstart: 2024-04-01 00:00:00\nend: 2024-04-30 23:59:59\nperiod: 3h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy(\'Mean Reversion with Tight Stop Loss\', overlay=true)\n\n// Define parameters\nrsiLength = 14\nrsiThresholdBuy = 30\nrsiThresholdSell = 70\nsmaPeriod = 20\nstopLossPercentage = 0.5  // 0.5% stop loss\nprofitTargetPercentage = 1  // 1% profit target\n\n// Calculate indicators\nrsi = ta.rsi(close, rsiLength)\nsma = ta.sma(close, smaPeriod)\n\n// Entry conditions\nbuySignal = rsi < rsiThresholdBuy and close < sma\nsellSignal = rsi > rsiThresholdSell and close > sma\n\n// Exit conditions\nif strategy.position_size > 0\n    stopLoss = strategy.position_avg_price * (1 - stopLossPercentage / 100)\n    takeProfit = strategy.position_avg_price * (1 + profitTargetPercentage / 100)\n\n    if close <= stopLoss or close >= takeProfit\n        strategy.close(\'Exit\', comment=\'Stop Loss / Take Profit\')\n\n// Execute trades\nif buySignal\n    strategy.entry(\'Buy\', strategy.long)\n\nif sellSignal\n    strategy.entry(\'Sell\', strategy.short)'

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
