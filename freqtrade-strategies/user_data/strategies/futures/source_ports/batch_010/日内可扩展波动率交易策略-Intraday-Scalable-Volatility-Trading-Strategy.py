"""Source-faithful deep-assisted port of 日内可扩展波动率交易策略-Intraday-Scalable-Volatility-Trading-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_a49a1a02(PinePortBase, IStrategy):
    source_file = '日内可扩展波动率交易策略-Intraday-Scalable-Volatility-Trading-Strategy.md'
    timeframe = '1h'
    can_short = True
    source_defaults = {}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.entry', 'strategy.close', 'for ']
    source_fidelity_notes = []
    pine_assignments = [{'mode': '', 'name': 'atrPeriod', 'op': '=', 'expr': '10', 'conditions': []}, {'mode': '', 'name': 'atrValue', 'op': '=', 'expr': 'atr(atrPeriod)', 'conditions': []}, {'mode': '', 'name': 'volatilityFactor', 'op': '=', 'expr': '1.2', 'conditions': []}, {'mode': '', 'name': 'highVolatility', 'op': '=', 'expr': 'atrValue > volatilityFactor * atrValue[1]', 'conditions': []}, {'mode': '', 'name': 'volumeCondition', 'op': '=', 'expr': 'volume > sma(volume, 50)', 'conditions': []}, {'mode': '', 'name': 'range', 'op': '=', 'expr': 'high - low', 'conditions': []}, {'mode': '', 'name': 'smaFast', 'op': '=', 'expr': 'sma(close, 5)', 'conditions': []}, {'mode': '', 'name': 'smaSlow', 'op': '=', 'expr': 'sma(close, 20)', 'conditions': []}, {'mode': '', 'name': 'isBullish', 'op': '=', 'expr': 'smaFast > smaSlow', 'conditions': []}, {'mode': '', 'name': 'newCatalyst', 'op': '=', 'expr': 'close > open', 'conditions': []}, {'mode': '', 'name': 'enterLong', 'op': '=', 'expr': 'highVolatility and volumeCondition and range > 0.005 and isBullish and newCatalyst', 'conditions': []}, {'mode': '', 'name': 'enterShort', 'op': '=', 'expr': 'highVolatility and volumeCondition and range > 0.005 and not isBullish and newCatalyst', 'conditions': []}, {'mode': '', 'name': 'exitLong', 'op': '=', 'expr': 'crossover(smaFast, smaSlow) // Example exit condition for long position', 'conditions': []}, {'mode': '', 'name': 'exitShort', 'op': '=', 'expr': 'crossunder(smaFast, smaSlow) // Example exit condition for short position', 'conditions': []}]
    pine_user_functions = []
    pine_controls = []
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("Buy", strategy.long, when=enterLong)', 'conditions': [], 'statement': 'strategy.entry("Buy", strategy.long, when=enterLong)'}, {'kind': 'entry', 'call': 'strategy.entry("Sell", strategy.short, when=enterShort)', 'conditions': [], 'statement': 'strategy.entry("Sell", strategy.short, when=enterShort)'}, {'kind': 'close', 'call': 'strategy.close("Buy", when=exitLong)', 'conditions': [], 'statement': 'strategy.close("Buy", when=exitLong)'}, {'kind': 'close', 'call': 'strategy.close("Sell", when=exitShort)', 'conditions': [], 'statement': 'strategy.close("Sell", when=exitShort)'}]
    original_pine = '/*backtest\nstart: 2024-03-01 00:00:00\nend: 2024-03-31 23:59:59\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=4\nstrategy("Intraday Scalping Strategy with Exit Conditions", shorttitle="ISS", overlay=true)\n\n// Define Volatility based on ATR for intraday\natrPeriod = 10\natrValue = atr(atrPeriod)\nvolatilityFactor = 1.2\nhighVolatility = atrValue > volatilityFactor * atrValue[1]\n\n// Define Volume conditions for intraday\nvolumeCondition = volume > sma(volume, 50)\n\n// Define Price Range for intraday\nrange = high - low\n\n// Define Technical Indicator (SMA example) for intraday\nsmaFast = sma(close, 5)\nsmaSlow = sma(close, 20)\nisBullish = smaFast > smaSlow\n\n// Define New Catalyst condition for intraday (example)\nnewCatalyst = close > open\n\n// Combine all conditions for entry in intraday\nenterLong = highVolatility and volumeCondition and range > 0.005 and isBullish and newCatalyst\nenterShort = highVolatility and volumeCondition and range > 0.005 and not isBullish and newCatalyst\n\n// Submit entry orders based on conditions\nstrategy.entry("Buy", strategy.long, when=enterLong)\nstrategy.entry("Sell", strategy.short, when=enterShort)\n\n// Define exit conditions\nexitLong = crossover(smaFast, smaSlow) // Example exit condition for long position\nexitShort = crossunder(smaFast, smaSlow) // Example exit condition for short position\n\n// Submit exit orders based on conditions\nstrategy.close("Buy", when=exitLong)\nstrategy.close("Sell", when=exitShort)'

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
