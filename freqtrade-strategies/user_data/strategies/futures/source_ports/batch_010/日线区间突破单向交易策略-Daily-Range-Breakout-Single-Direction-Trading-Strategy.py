"""Source-faithful deep-assisted port of 日线区间突破单向交易策略-Daily-Range-Breakout-Single-Direction-Trading-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_2d020e77(PinePortBase, IStrategy):
    source_file = '日线区间突破单向交易策略-Daily-Range-Breakout-Single-Direction-Trading-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 100.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['request.security', 'strategy.exit', 'strategy.entry', 'strategy.opentrades', 'var ', 'for ']
    source_fidelity_notes = ['Uses request.security / multi-timeframe context; exact parity depends on HTF resampling, gaps and lookahead semantics.', 'Uses persistent Pine state (var/varip); state is order-dependent and must be evaluated bar-by-bar, not replaced by a vectorized fill-forward approximation.', 'Reads broker/strategy state; signals depend on fill timing and cannot be reduced to indicator-only booleans without changing behavior.', 'Uses strategy.exit; stop/limit/profit/loss/trailing arguments have Pine order semantics and may fill intrabar.']
    pine_assignments = [{'mode': 'var', 'name': 'pip', 'op': '=', 'expr': '1.0', 'conditions': []}, {'mode': '', 'name': 'take_profit_pips', 'op': '=', 'expr': '50', 'conditions': []}, {'mode': '', 'name': 'stop_loss_pips', 'op': '=', 'expr': '50', 'conditions': []}, {'mode': '', 'name': 'prevDayHigh', 'op': '=', 'expr': 'request.security(syminfo.tickerid, "D", high[1])', 'conditions': []}, {'mode': '', 'name': 'prevDayLow', 'op': '=', 'expr': 'request.security(syminfo.tickerid, "D", low[1])', 'conditions': []}, {'mode': 'var', 'name': 'breakout_traded', 'op': '=', 'expr': 'false', 'conditions': []}, {'mode': 'var', 'name': 'breakdown_traded', 'op': '=', 'expr': 'false', 'conditions': []}, {'mode': '', 'name': 'breakout_traded', 'op': ':=', 'expr': 'false', 'conditions': ['(ta.change(time("D")))']}, {'mode': '', 'name': 'breakdown_traded', 'op': ':=', 'expr': 'false', 'conditions': ['(ta.change(time("D")))']}, {'mode': '', 'name': 'longCondition', 'op': '=', 'expr': 'close > prevDayHigh and strategy.opentrades == 0 and not breakout_traded', 'conditions': []}, {'mode': '', 'name': 'shortCondition', 'op': '=', 'expr': 'close < prevDayLow and strategy.opentrades == 0 and not breakdown_traded', 'conditions': []}, {'mode': '', 'name': 'breakout_traded', 'op': ':=', 'expr': 'true // Set breakout flag', 'conditions': ['(longCondition)']}, {'mode': '', 'name': 'breakdown_traded', 'op': ':=', 'expr': 'true // Set breakdown flag', 'conditions': ['(shortCondition)']}]
    pine_user_functions = []
    pine_controls = [{'indent': 0, 'statement': 'if (ta.change(time("D")))'}, {'indent': 0, 'statement': 'if (longCondition)'}, {'indent': 0, 'statement': 'if (shortCondition)'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("Long", strategy.long)', 'conditions': ['(longCondition)'], 'statement': 'strategy.entry("Long", strategy.long)'}, {'kind': 'exit', 'call': 'strategy.exit("Take Profit/Stop Loss", "Long", limit=close + take_profit_pips * pip, stop=close - stop_loss_pips * pip)', 'conditions': ['(longCondition)'], 'statement': 'strategy.exit("Take Profit/Stop Loss", "Long", limit=close + take_profit_pips * pip, stop=close - stop_loss_pips * pip)'}, {'kind': 'entry', 'call': 'strategy.entry("Short", strategy.short)', 'conditions': ['(shortCondition)'], 'statement': 'strategy.entry("Short", strategy.short)'}, {'kind': 'exit', 'call': 'strategy.exit("Take Profit/Stop Loss", "Short", limit=close - take_profit_pips * pip, stop=close + stop_loss_pips * pip)', 'conditions': ['(shortCondition)'], 'statement': 'strategy.exit("Take Profit/Stop Loss", "Short", limit=close - take_profit_pips * pip, stop=close + stop_loss_pips * pip)'}]
    original_pine = '/*backtest\nstart: 2019-12-23 08:00:00\nend: 2024-12-09 08:00:00\nperiod: 1d\nbasePeriod: 1d\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("US 30 Daily Breakout Strategy (Single Trade Per Breakout/Breakdown, New York Time)", overlay=true, default_qty_type=strategy.percent_of_equity, default_qty_value=100, trim_orders = true)\n\n// Set pip size for US 30 (1 pip = 1 point)\nvar float pip = 1.0\n\n// Set take profit and stop loss in points (1 pip = 1 point)\ntake_profit_pips = 50\nstop_loss_pips = 50\n\n// Calculate the previous day\'s high and low (assumes chart timezone is set to New York)\nprevDayHigh = request.security(syminfo.tickerid, "D", high[1])\nprevDayLow = request.security(syminfo.tickerid, "D", low[1])\n\n// Initialize flags to track if a breakout/breakdown trade has been taken\nvar bool breakout_traded = false\nvar bool breakdown_traded = false\n\n// Reset flags at the start of a new day in New York timezone (as per chart setting)\nif (ta.change(time("D")))\n    breakout_traded := false\n    breakdown_traded := false\n\n// Condition for a long entry: candle closes above the previous day\'s high and no breakout trade has been taken\nlongCondition = close > prevDayHigh and strategy.opentrades == 0 and not breakout_traded\n\n// Condition for a short entry: candle closes below the previous day\'s low and no breakdown trade has been taken\nshortCondition = close < prevDayLow and strategy.opentrades == 0 and not breakdown_traded\n\n// Execute long trade if the condition is met, and set the breakout flag\nif (longCondition)\n    strategy.entry("Long", strategy.long)\n    strategy.exit("Take Profit/Stop Loss", "Long", limit=close + take_profit_pips * pip, stop=close - stop_loss_pips * pip)\n    breakout_traded := true  // Set breakout flag\n\n// Execute short trade if the condition is met, and set the breakdown flag\nif (shortCondition)\n    strategy.entry("Short", strategy.short)\n    strategy.exit("Take Profit/Stop Loss", "Short", limit=close - take_profit_pips * pip, stop=close + stop_loss_pips * pip)\n    breakdown_traded := true  // Set breakdown flag\n\n// Plotting the previous day\'s high and low for visualization\nplot(prevDayHigh, color=color.green, linewidth=1, title="Previous Day High")\nplot(prevDayLow, color=color.red, linewidth=1, title="Previous Day Low")'

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
