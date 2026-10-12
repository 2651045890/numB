"""Source-faithful deep-assisted port of 机械化交易策略Mechanical-Trading-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_b2f2d71a(PinePortBase, IStrategy):
    source_file = '机械化交易策略Mechanical-Trading-Strategy.md'
    timeframe = '4h'
    can_short = False
    source_defaults = {'profitTarget': 0.4, 'stopLoss': 0.2}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.exit', 'strategy.entry', 'strategy.equity']
    source_fidelity_notes = ['Reads broker/strategy state; signals depend on fill timing and cannot be reduced to indicator-only booleans without changing behavior.', 'Uses strategy.exit; stop/limit/profit/loss/trailing arguments have Pine order semantics and may fill intrabar.']
    pine_assignments = [{'mode': '', 'name': 'profitTarget', 'op': '=', 'expr': 'input(0.4, "Profit Target (%)") / 100', 'conditions': []}, {'mode': '', 'name': 'stopLoss', 'op': '=', 'expr': 'input(0.2, "Stop Loss (%)") / 100', 'conditions': []}, {'mode': '', 'name': 'entryPrice', 'op': '=', 'expr': 'close', 'conditions': []}, {'mode': '', 'name': 'takeProfitLevel', 'op': '=', 'expr': 'entryPrice + (entryPrice * profitTarget)', 'conditions': []}, {'mode': '', 'name': 'stopLossLevel', 'op': '=', 'expr': 'entryPrice - (entryPrice * stopLoss)', 'conditions': []}, {'mode': '', 'name': 'positionSize', 'op': '=', 'expr': 'strategy.equity * 0.02 // Example: 2% of equity', 'conditions': ['(hour(time) == 16)']}]
    pine_user_functions = []
    pine_controls = [{'indent': 0, 'statement': 'if (hour(time) == 16)'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("Buy", strategy.long)', 'conditions': ['(hour(time) == 16)'], 'statement': 'strategy.entry("Buy", strategy.long)'}, {'kind': 'exit', 'call': 'strategy.exit("Take Profit", "Buy", limit=takeProfitLevel,stop =stopLossLevel )', 'conditions': ['(hour(time) == 16)'], 'statement': 'strategy.exit("Take Profit", "Buy", limit=takeProfitLevel,stop =stopLossLevel )'}]
    original_pine = '/*backtest\nstart: 2023-08-14 00:00:00\nend: 2023-09-13 00:00:00\nperiod: 4h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("Mechanical Trading Strategy", overlay=true)\n\n// Define strategy parameters\nprofitTarget = input(0.4, "Profit Target (%)") / 100\nstopLoss = input(0.2, "Stop Loss (%)") / 100\n\n// Define strategy variables\nentryPrice = close\ntakeProfitLevel = entryPrice + (entryPrice * profitTarget)\nstopLossLevel =  entryPrice - (entryPrice * stopLoss)\n// Entry condition\nif (hour(time) == 16)\n    // Calculate position size based on available capital and risk tolerance\n    positionSize = strategy.equity * 0.02 // Example: 2% of equity\n\n    strategy.entry("Buy", strategy.long)\n    strategy.exit("Take Profit", "Buy", limit=takeProfitLevel,stop =stopLossLevel )'

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
