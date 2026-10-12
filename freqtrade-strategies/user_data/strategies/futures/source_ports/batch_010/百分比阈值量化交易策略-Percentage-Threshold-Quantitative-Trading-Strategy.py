"""Source-faithful deep-assisted port of 百分比阈值量化交易策略-Percentage-Threshold-Quantitative-Trading-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_08ca1243(PinePortBase, IStrategy):
    source_file = '百分比阈值量化交易策略-Percentage-Threshold-Quantitative-Trading-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'percentage': 1.04, 'timeframe': 'D'}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['request.security', 'strategy.entry', 'strategy.close', 'strategy.equity', 'for ']
    source_fidelity_notes = ['Uses request.security / multi-timeframe context; exact parity depends on HTF resampling, gaps and lookahead semantics.', 'Reads broker/strategy state; signals depend on fill timing and cannot be reduced to indicator-only booleans without changing behavior.']
    pine_assignments = [{'mode': '', 'name': 'percentage', 'op': '=', 'expr': 'input.float(1.04, title="Percentage Threshold", minval=0.01, step=0.01) / 100', 'conditions': []}, {'mode': '', 'name': 'timeframe', 'op': '=', 'expr': 'input.timeframe("D", title="Timeframe", options=["1", "3", "5", "15", "30", "60", "240", "D", "W", "M"])', 'conditions': []}, {'mode': '', 'name': 'high_timeframe', 'op': '=', 'expr': 'request.security(syminfo.tickerid, timeframe, high)', 'conditions': []}, {'mode': '', 'name': 'low_timeframe', 'op': '=', 'expr': 'request.security(syminfo.tickerid, timeframe, low)', 'conditions': []}, {'mode': '', 'name': 'close_timeframe', 'op': '=', 'expr': 'request.security(syminfo.tickerid, timeframe, close)', 'conditions': []}, {'mode': '', 'name': 'threshold', 'op': '=', 'expr': 'close_timeframe[1] * percentage', 'conditions': []}, {'mode': '', 'name': 'buyCondition', 'op': '=', 'expr': 'high_timeframe > (close_timeframe[1] + threshold)', 'conditions': []}, {'mode': '', 'name': 'sellCondition', 'op': '=', 'expr': 'low_timeframe < (close_timeframe[1] - threshold)', 'conditions': []}]
    pine_user_functions = []
    pine_controls = [{'indent': 0, 'statement': 'if (buyCondition)'}, {'indent': 0, 'statement': 'if (sellCondition)'}, {'indent': 0, 'statement': 'if (sellCondition)'}, {'indent': 0, 'statement': 'if (buyCondition)'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("Buy", strategy.long)', 'conditions': ['(buyCondition)'], 'statement': 'strategy.entry("Buy", strategy.long)'}, {'kind': 'entry', 'call': 'strategy.entry("Sell", strategy.short)', 'conditions': ['(sellCondition)'], 'statement': 'strategy.entry("Sell", strategy.short)'}, {'kind': 'close', 'call': 'strategy.close("Buy")', 'conditions': ['(sellCondition)'], 'statement': 'strategy.close("Buy")'}, {'kind': 'close', 'call': 'strategy.close("Sell")', 'conditions': ['(buyCondition)'], 'statement': 'strategy.close("Sell")'}]
    original_pine = '/*backtest\nstart: 2023-05-28 00:00:00\nend: 2024-06-02 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("GBS Percentage", overlay=true)\n\n// Define input options for percentage settings and timeframe\npercentage = input.float(1.04, title="Percentage Threshold", minval=0.01, step=0.01) / 100\ntimeframe = input.timeframe("D", title="Timeframe", options=["1", "3", "5", "15", "30", "60", "240", "D", "W", "M"])\n\n// Calculate high, low, and close of the selected timeframe\nhigh_timeframe = request.security(syminfo.tickerid, timeframe, high)\nlow_timeframe = request.security(syminfo.tickerid, timeframe, low)\nclose_timeframe = request.security(syminfo.tickerid, timeframe, close)\n\n// Calculate the percentage threshold based on the previous close\nthreshold = close_timeframe[1] * percentage\n\n// Define conditions for Buy and Sell\nbuyCondition = high_timeframe > (close_timeframe[1] + threshold)\nsellCondition = low_timeframe < (close_timeframe[1] - threshold)\n\n// Entry and exit rules\nif (buyCondition)\n    strategy.entry("Buy", strategy.long)\n\nif (sellCondition)\n    strategy.entry("Sell", strategy.short)\n\n// Close the positions based on the conditions\nif (sellCondition)\n    strategy.close("Buy")\n\nif (buyCondition)\n    strategy.close("Sell")\n\n// Plot Buy and Sell signals on the chart\nplotshape(series=buyCondition, title="Buy Entry", color=color.green, style=shape.triangleup, location=location.belowbar)\nplotshape(series=sellCondition, title="Sell Entry", color=color.red, style=shape.triangledown, location=location.abovebar)\n\n// Plot the equity curve of the strategy\nplot(strategy.equity, title="Equity", color=color.blue, linewidth=2)'

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
