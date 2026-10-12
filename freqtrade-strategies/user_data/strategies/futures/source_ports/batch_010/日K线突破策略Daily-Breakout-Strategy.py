"""Source-faithful deep-assisted port of 日K线突破策略Daily-Breakout-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_2a69ec99(PinePortBase, IStrategy):
    source_file = '日K线突破策略Daily-Breakout-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 1.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['request.security', 'strategy.exit', 'strategy.entry', 'strategy.equity', 'for ']
    source_fidelity_notes = ['Uses request.security / multi-timeframe context; exact parity depends on HTF resampling, gaps and lookahead semantics.', 'Uses barmerge.lookahead_on; source can intentionally expose/repaint future HTF values. Preserve when parity-testing, disable for live-safe testing only as a separate variant.', 'Reads broker/strategy state; signals depend on fill timing and cannot be reduced to indicator-only booleans without changing behavior.', 'Uses strategy.exit; stop/limit/profit/loss/trailing arguments have Pine order semantics and may fill intrabar.']
    pine_assignments = [{'mode': '', 'name': 'initialCapital', 'op': '=', 'expr': '10000', 'conditions': []}, {'mode': '', 'name': 'riskFactor', 'op': '=', 'expr': '3500', 'conditions': []}, {'mode': '', 'name': 'lastDayOpen', 'op': '=', 'expr': 'request.security(syminfo.tickerid, "D", open[1], lookahead=barmerge.lookahead_on)', 'conditions': []}, {'mode': '', 'name': 'lastDayClose', 'op': '=', 'expr': 'request.security(syminfo.tickerid, "D", close[1], lookahead=barmerge.lookahead_on)', 'conditions': []}, {'mode': '', 'name': 'lastDayColor', 'op': '=', 'expr': 'lastDayOpen < lastDayClose ? color.green : color.red', 'conditions': []}, {'mode': '', 'name': 'availableCapital', 'op': '=', 'expr': 'strategy.equity', 'conditions': []}, {'mode': '', 'name': 'tradeSize', 'op': '=', 'expr': 'availableCapital / riskFactor', 'conditions': []}, {'mode': '', 'name': 'buyCondition', 'op': '=', 'expr': 'lastDayColor == color.green', 'conditions': []}, {'mode': '', 'name': 'sellCondition', 'op': '=', 'expr': 'lastDayColor == color.red', 'conditions': []}, {'mode': '', 'name': 'stopLoss', 'op': '=', 'expr': '0.001 * lastDayOpen * tradeSize', 'conditions': []}]
    pine_user_functions = []
    pine_controls = []
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("Buy", strategy.long, qty=tradeSize, when=buyCondition)', 'conditions': [], 'statement': 'strategy.entry("Buy", strategy.long, qty=tradeSize, when=buyCondition)'}, {'kind': 'entry', 'call': 'strategy.entry("Sell", strategy.short, qty=tradeSize, when=sellCondition)', 'conditions': [], 'statement': 'strategy.entry("Sell", strategy.short, qty=tradeSize, when=sellCondition)'}, {'kind': 'exit', 'call': 'strategy.exit("StopLoss/Profit", from_entry="Buy", loss=stopLoss)', 'conditions': [], 'statement': 'strategy.exit("StopLoss/Profit", from_entry="Buy", loss=stopLoss)'}, {'kind': 'exit', 'call': 'strategy.exit("StopLoss/Profit", from_entry="Sell", loss=stopLoss)', 'conditions': [], 'statement': 'strategy.exit("StopLoss/Profit", from_entry="Sell", loss=stopLoss)'}]
    original_pine = '/*backtest\nstart: 2022-12-26 00:00:00\nend: 2023-08-30 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("Daily Candle Strategy", overlay=true, default_qty_type=strategy.percent_of_equity, default_qty_value=0.0)\n\n// Input parameters\ninitialCapital = 10000\nriskFactor = 3500\n\n// Calculate the opening and closing values for the last day\'s candle\nlastDayOpen = request.security(syminfo.tickerid, "D", open[1], lookahead=barmerge.lookahead_on)\nlastDayClose = request.security(syminfo.tickerid, "D", close[1], lookahead=barmerge.lookahead_on)\n\n// Determine the color of the last day\'s candle\nlastDayColor = lastDayOpen < lastDayClose ? color.green : color.red\n\n// Plot the last day\'s candle on the chart\nplotshape(series=na, color=lastDayColor, style=shape.triangledown, location=location.abovebar)\n\n// Calculate trade size based on available capital at last day\'s closing\navailableCapital = strategy.equity\ntradeSize = availableCapital / riskFactor\n\n// Trading conditions\nbuyCondition = lastDayColor == color.green\nsellCondition = lastDayColor == color.red\n\n// Execute strategy orders with calculated trade size\nstrategy.entry("Buy", strategy.long, qty=tradeSize, when=buyCondition)\nstrategy.entry("Sell", strategy.short, qty=tradeSize, when=sellCondition)\n\n// Exit strategy\nstopLoss = 0.001 * lastDayOpen * tradeSize\nstrategy.exit("StopLoss/Profit", from_entry="Buy", loss=stopLoss)\nstrategy.exit("StopLoss/Profit", from_entry="Sell", loss=stopLoss)\n\n// Plot stop loss level on the chart\nplot(stopLoss, color=color.red, linewidth=2, title="Stop Loss")'

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
