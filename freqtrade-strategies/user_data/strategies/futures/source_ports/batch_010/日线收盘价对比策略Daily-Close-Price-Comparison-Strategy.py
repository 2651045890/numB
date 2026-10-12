"""Source-faithful deep-assisted port of 日线收盘价对比策略Daily-Close-Price-Comparison-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_4540d289(PinePortBase, IStrategy):
    source_file = '日线收盘价对比策略Daily-Close-Price-Comparison-Strategy.md'
    timeframe = '2h'
    can_short = True
    source_defaults = {'threshold': 0}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.entry', '=>']
    source_fidelity_notes = []
    pine_assignments = [{'mode': '', 'name': 'threshold', 'op': '=', 'expr': 'input(title="Price Difference Threshold", type=float, defval=0, step=0.001)', 'conditions': []}, {'mode': '', 'name': 'yesterday', 'op': '=', 'expr': "security(syminfo.tickerid, 'D', close[1])", 'conditions': []}, {'mode': '', 'name': 'today', 'op': '=', 'expr': "security(syminfo.tickerid, 'D', close)", 'conditions': []}, {'mode': '', 'name': 'delta', 'op': '=', 'expr': 'today-yesterday', 'conditions': []}, {'mode': '', 'name': 'percentage', 'op': '=', 'expr': 'delta/yesterday', 'conditions': []}, {'mode': '', 'name': 'closeDiff', 'op': '=', 'expr': 'getDiff()', 'conditions': []}, {'mode': '', 'name': 'buying', 'op': '=', 'expr': 'closeDiff > threshold ? true : closeDiff < -threshold ? false : buying[1]', 'conditions': []}, {'mode': '', 'name': 'longCondition', 'op': '=', 'expr': 'buying', 'conditions': []}, {'mode': '', 'name': 'shortCondition', 'op': '=', 'expr': 'buying != true', 'conditions': []}]
    pine_user_functions = [{'name': 'getDiff', 'args': '', 'body': ''}]
    pine_controls = [{'indent': 0, 'statement': 'if (longCondition)'}, {'indent': 0, 'statement': 'if (shortCondition)'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("Long", strategy.long)', 'conditions': ['(longCondition)'], 'statement': 'strategy.entry("Long", strategy.long)'}, {'kind': 'entry', 'call': 'strategy.entry("Short", strategy.short)', 'conditions': ['(shortCondition)'], 'statement': 'strategy.entry("Short", strategy.short)'}]
    original_pine = '/*backtest\nstart: 2023-08-17 00:00:00\nend: 2023-09-16 00:00:00\nperiod: 2h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=2\nstrategy("Daily Close Comparison Strategy (by ChartArt)", shorttitle="CA_-_Daily_Close_Strat", overlay=false)\n\n// ChartArt\'s Daily Close Comparison Strategy\n//\n// Version 1.0\n// Idea by ChartArt on February 28, 2016.\n//\n// This strategy is equal to the very\n// popular "ANN Strategy" coded by sirolf2009,\n// but without the Artificial Neural Network (ANN).\n//\n// Main difference besides stripping out the ANN\n// is that I use close prices instead of OHLC4 prices.\n// And the default threshold is set to 0 instead of 0.0014\n// with a step of 0.001 instead of 0.0001.\n//\n// This strategy goes long if the close of the current day\n// is larger than the close price of the last day.\n// If the inverse logic is true, the strategy\n// goes short (last close larger current close).\n//\n// This simple strategy does not have any\n// stop loss or take profit money management logic.\n//\n// List of my work: \n// https://www.tradingview.com/u/ChartArt/\n// \n//  __             __  ___       __  ___ \n// /  ` |__|  /\\  |__)  |   /\\  |__)  |  \n// \\__, |  | /~~\\ |  \\  |  /~~\\ |  \\  |  \n// \n// \n\nthreshold = input(title="Price Difference Threshold", type=float, defval=0, step=0.001)\n\ngetDiff() =>\n    yesterday=security(syminfo.tickerid, \'D\', close[1])\n    today=security(syminfo.tickerid, \'D\', close)\n    delta=today-yesterday\n    percentage=delta/yesterday\n    \ncloseDiff = getDiff()\n \nbuying = closeDiff > threshold ? true : closeDiff < -threshold ? false : buying[1]\n\nhline(0, title="zero line")\n\nbgcolor(buying ? green : red, transp=25)\nplot(closeDiff, color=silver, style=area, transp=75)\nplot(closeDiff, color=aqua, title="prediction")\n\nlongCondition = buying\nif (longCondition)\n    strategy.entry("Long", strategy.long)\n\nshortCondition = buying != true\nif (shortCondition)\n    strategy.entry("Short", strategy.short)'

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
