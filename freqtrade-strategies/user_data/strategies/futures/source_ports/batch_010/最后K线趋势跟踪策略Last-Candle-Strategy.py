"""Source-faithful deep-assisted port of 最后K线趋势跟踪策略Last-Candle-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_c7181039(PinePortBase, IStrategy):
    source_file = '最后K线趋势跟踪策略Last-Candle-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['request.security', 'strategy.exit', 'strategy.entry', 'strategy.close', 'for ']
    source_fidelity_notes = ['Uses request.security / multi-timeframe context; exact parity depends on HTF resampling, gaps and lookahead semantics.', 'Uses barmerge.lookahead_on; source can intentionally expose/repaint future HTF values. Preserve when parity-testing, disable for live-safe testing only as a separate variant.', 'Uses strategy.exit; stop/limit/profit/loss/trailing arguments have Pine order semantics and may fill intrabar.']
    pine_assignments = [{'mode': '', 'name': 'startDate', 'op': '=', 'expr': 'timestamp(2015, 01, 01, 00, 00)', 'conditions': []}, {'mode': '', 'name': 'endDate', 'op': '=', 'expr': 'timestamp(2023, 11, 24, 23, 59)', 'conditions': []}, {'mode': '', 'name': 'withinDateRange', 'op': '=', 'expr': 'time >= startDate and time <= endDate', 'conditions': []}, {'mode': '', 'name': 'lastCandleOpen', 'op': '=', 'expr': 'request.security(syminfo.tickerid, "D", open[1], lookahead=barmerge.lookahead_on)', 'conditions': []}, {'mode': '', 'name': 'lastCandleClose', 'op': '=', 'expr': 'request.security(syminfo.tickerid, "D", close[1], lookahead=barmerge.lookahead_on)', 'conditions': []}, {'mode': '', 'name': 'tradeDirection', 'op': '=', 'expr': 'lastCandleOpen < lastCandleClose ? 1 : -1 // 1 for buy, -1 for sell', 'conditions': []}, {'mode': '', 'name': 'stopLoss', 'op': '=', 'expr': '0.01 * lastCandleOpen', 'conditions': []}, {'mode': '', 'name': 'takeProfit', 'op': '=', 'expr': 'close', 'conditions': []}]
    pine_user_functions = []
    pine_controls = [{'indent': 0, 'statement': 'if (not withinDateRange)'}, {'indent': 0, 'statement': 'if (withinDateRange)'}, {'indent': 4, 'statement': 'if (tradeDirection == 1)'}, {'indent': 4, 'statement': 'if (tradeDirection == -1)'}]
    pine_orders = [{'kind': 'close_all', 'call': 'strategy.close_all()', 'conditions': ['(not withinDateRange)'], 'statement': 'strategy.close_all()'}, {'kind': 'entry', 'call': 'strategy.entry("Buy", strategy.long)', 'conditions': ['(withinDateRange)', '(tradeDirection == 1)'], 'statement': 'strategy.entry("Buy", strategy.long)'}, {'kind': 'entry', 'call': 'strategy.entry("Sell", strategy.short)', 'conditions': ['(withinDateRange)', '(tradeDirection == -1)'], 'statement': 'strategy.entry("Sell", strategy.short)'}, {'kind': 'exit', 'call': 'strategy.exit("StopLoss/Profit", from_entry="Buy", loss=stopLoss, profit=takeProfit)', 'conditions': [], 'statement': 'strategy.exit("StopLoss/Profit", from_entry="Buy", loss=stopLoss, profit=takeProfit)'}, {'kind': 'exit', 'call': 'strategy.exit("StopLoss/Profit", from_entry="Sell", loss=stopLoss, profit=takeProfit)', 'conditions': [], 'statement': 'strategy.exit("StopLoss/Profit", from_entry="Sell", loss=stopLoss, profit=takeProfit)'}]
    original_pine = '/*backtest\nstart: 2022-12-14 00:00:00\nend: 2023-12-20 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("Last Candle Strategy with Date Range", overlay=true)\n\n// Define the start and end dates for the backtest\nstartDate = timestamp(2015, 01, 01, 00, 00)\nendDate = timestamp(2023, 11, 24, 23, 59)\n\n// Check if the current bar is within the specified date range\nwithinDateRange = time >= startDate and time <= endDate\n\n// If outside the date range, skip the strategy logic\nif (not withinDateRange)\n    strategy.close_all()\n\n// Calculate the opening and closing values for the last candle\nlastCandleOpen = request.security(syminfo.tickerid, "D", open[1], lookahead=barmerge.lookahead_on)\nlastCandleClose = request.security(syminfo.tickerid, "D", close[1], lookahead=barmerge.lookahead_on)\n\n// Determine the trade direction based on the last candle\ntradeDirection = lastCandleOpen < lastCandleClose ? 1 : -1  // 1 for buy, -1 for sell\n\n// Plot the last candle\'s opening and closing values on the chart\nplot(lastCandleOpen, color=color.blue, title="Last Candle Open")\nplot(lastCandleClose, color=color.red, title="Last Candle Close")\n\n// Execute strategy orders\nif (withinDateRange)\n    if (tradeDirection == 1)\n        strategy.entry("Buy", strategy.long)\n\n    if (tradeDirection == -1)\n        strategy.entry("Sell", strategy.short)\n\n// Set stop loss and take profit\nstopLoss = 0.01 * lastCandleOpen\ntakeProfit = close\n\n// Exit strategy\nstrategy.exit("StopLoss/Profit", from_entry="Buy", loss=stopLoss, profit=takeProfit)\nstrategy.exit("StopLoss/Profit", from_entry="Sell", loss=stopLoss, profit=takeProfit)'

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
