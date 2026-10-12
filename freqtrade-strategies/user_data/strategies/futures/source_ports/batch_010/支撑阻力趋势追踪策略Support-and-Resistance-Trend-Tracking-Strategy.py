"""Source-faithful deep-assisted port of 支撑阻力趋势追踪策略Support-and-Resistance-Trend-Tracking-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_d9b2bdab(PinePortBase, IStrategy):
    source_file = '支撑阻力趋势追踪策略Support-and-Resistance-Trend-Tracking-Strategy.md'
    timeframe = '3h'
    can_short = True
    source_defaults = {'supportLevel': 100, 'resistanceLevel': 200, 'riskRewardRatio': 2, 'trailStopLoss': True}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['request.security', 'strategy.exit', 'strategy.entry']
    source_fidelity_notes = ['Uses request.security / multi-timeframe context; exact parity depends on HTF resampling, gaps and lookahead semantics.', 'Uses strategy.exit; stop/limit/profit/loss/trailing arguments have Pine order semantics and may fill intrabar.']
    pine_assignments = [{'mode': '', 'name': 'supportLevel', 'op': '=', 'expr': 'input(100, title="Support Level")', 'conditions': []}, {'mode': '', 'name': 'resistanceLevel', 'op': '=', 'expr': 'input(200, title="Resistance Level")', 'conditions': []}, {'mode': '', 'name': 'riskRewardRatio', 'op': '=', 'expr': 'input(2, title="Risk-Reward Ratio")', 'conditions': []}, {'mode': '', 'name': 'trailStopLoss', 'op': '=', 'expr': 'input(true, title="Use Trailing Stop Loss")', 'conditions': []}, {'mode': '', 'name': 'trendUp', 'op': '=', 'expr': 'close > request.security(syminfo.tickerid, "D", close[1])', 'conditions': []}, {'mode': '', 'name': 'trendDown', 'op': '=', 'expr': 'close < request.security(syminfo.tickerid, "D", close[1])', 'conditions': []}, {'mode': '', 'name': 'buySignal', 'op': '=', 'expr': 'close < supportLevel and trendUp', 'conditions': []}, {'mode': '', 'name': 'sellSignal', 'op': '=', 'expr': 'close > resistanceLevel and trendDown', 'conditions': []}, {'mode': '', 'name': 'targetPrice', 'op': '=', 'expr': 'close + (close - supportLevel) * riskRewardRatio', 'conditions': []}, {'mode': '', 'name': 'stopLossLevel', 'op': '=', 'expr': 'supportLevel', 'conditions': []}]
    pine_user_functions = []
    pine_controls = [{'indent': 0, 'statement': 'if (trailStopLoss)'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("Buy", strategy.long, when=buySignal)', 'conditions': [], 'statement': 'strategy.entry("Buy", strategy.long, when=buySignal)'}, {'kind': 'entry', 'call': 'strategy.entry("Sell", strategy.short, when=sellSignal)', 'conditions': [], 'statement': 'strategy.entry("Sell", strategy.short, when=sellSignal)'}, {'kind': 'exit', 'call': 'strategy.exit("Take Profit/Stop Loss", from_entry="Buy", loss=stopLossLevel, profit=targetPrice)', 'conditions': [], 'statement': 'strategy.exit("Take Profit/Stop Loss", from_entry="Buy", loss=stopLossLevel, profit=targetPrice)'}, {'kind': 'exit', 'call': 'strategy.exit("Take Profit/Stop Loss", from_entry="Sell", loss=targetPrice, profit=stopLossLevel)', 'conditions': [], 'statement': 'strategy.exit("Take Profit/Stop Loss", from_entry="Sell", loss=targetPrice, profit=stopLossLevel)'}, {'kind': 'exit', 'call': 'strategy.exit("Trailing Stop Loss", from_entry="Buy", loss=stopLossLevel)', 'conditions': ['(trailStopLoss)'], 'statement': 'strategy.exit("Trailing Stop Loss", from_entry="Buy", loss=stopLossLevel)'}, {'kind': 'exit', 'call': 'strategy.exit("Trailing Stop Loss", from_entry="Sell", loss=stopLossLevel)', 'conditions': ['(trailStopLoss)'], 'statement': 'strategy.exit("Trailing Stop Loss", from_entry="Sell", loss=stopLossLevel)'}]
    original_pine = '/*backtest\nstart: 2024-01-27 00:00:00\nend: 2024-02-26 00:00:00\nperiod: 3h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("Support Resistance Trend Strategy", overlay=true)\n\n// Input parameters\nsupportLevel = input(100, title="Support Level")\nresistanceLevel = input(200, title="Resistance Level")\nriskRewardRatio = input(2, title="Risk-Reward Ratio")\ntrailStopLoss = input(true, title="Use Trailing Stop Loss")\n\n// Calculate trend direction based on trend lines\ntrendUp = close > request.security(syminfo.tickerid, "D", close[1])\ntrendDown = close < request.security(syminfo.tickerid, "D", close[1])\n\n// Buy signal condition\nbuySignal = close < supportLevel and trendUp\n\n// Sell signal condition\nsellSignal = close > resistanceLevel and trendDown\n\n// Entry point and exit conditions\nstrategy.entry("Buy", strategy.long, when=buySignal)\nstrategy.entry("Sell", strategy.short, when=sellSignal)\n\n// Calculate targets and stop-loss levels\ntargetPrice = close + (close - supportLevel) * riskRewardRatio\nstopLossLevel = supportLevel\n\n// Plot support and resistance levels\nplot(supportLevel, color=color.green, linewidth=2, title="Support Level")\nplot(resistanceLevel, color=color.red, linewidth=2, title="Resistance Level")\n\n// Plot targets and stop-loss levels\nplot(targetPrice, color=color.blue, linewidth=2, title="Target Price")\nplot(stopLossLevel, color=color.orange, linewidth=2, title="Stop Loss Level")\n\n// Trailing stop-loss\nstrategy.exit("Take Profit/Stop Loss", from_entry="Buy", loss=stopLossLevel, profit=targetPrice)\nstrategy.exit("Take Profit/Stop Loss", from_entry="Sell", loss=targetPrice, profit=stopLossLevel)\n\n// Plot trail stop loss\nif (trailStopLoss)\n    strategy.exit("Trailing Stop Loss", from_entry="Buy", loss=stopLossLevel)\n    strategy.exit("Trailing Stop Loss", from_entry="Sell", loss=stopLossLevel)'

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
