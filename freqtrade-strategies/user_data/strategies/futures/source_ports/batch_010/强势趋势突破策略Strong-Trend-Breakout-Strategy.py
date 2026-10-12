"""Source-faithful deep-assisted port of 强势趋势突破策略Strong-Trend-Breakout-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_1e4a9253(PinePortBase, IStrategy):
    source_file = '强势趋势突破策略Strong-Trend-Breakout-Strategy.md'
    timeframe = '5m'
    can_short = False
    source_defaults = {'iLength': 20, 'stopLossPercent': 1.0}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.exit', 'strategy.entry']
    source_fidelity_notes = ['Uses strategy.exit; stop/limit/profit/loss/trailing arguments have Pine order semantics and may fill intrabar.']
    pine_assignments = [{'mode': '', 'name': 'iLength', 'op': '=', 'expr': 'input(20, "Length", minval = 1)', 'conditions': []}, {'mode': '', 'name': 'stopLossPercent', 'op': '=', 'expr': 'input(1.0, "Stop Loss Percentage", type=input.float) / 100', 'conditions': []}, {'mode': '', 'name': 'up', 'op': '=', 'expr': 'na', 'conditions': []}, {'mode': '', 'name': 'up', 'op': ':=', 'expr': 'close > open ? high : nz(up[1])', 'conditions': []}, {'mode': '', 'name': 'down', 'op': '=', 'expr': 'na', 'conditions': []}, {'mode': '', 'name': 'down', 'op': ':=', 'expr': 'close < open ? low : nz(down[1])', 'conditions': []}, {'mode': '', 'name': 'highest', 'op': '=', 'expr': 'highest(up, iLength)', 'conditions': []}, {'mode': '', 'name': 'lowest', 'op': '=', 'expr': 'lowest(down, iLength)', 'conditions': []}, {'mode': '', 'name': 'p1', 'op': '=', 'expr': 'plot(highest, "Highest", color.black, 2)', 'conditions': []}, {'mode': '', 'name': 'p2', 'op': '=', 'expr': 'plot(lowest, "Lowest", color.black, 2)', 'conditions': []}, {'mode': '', 'name': 'wickDown', 'op': '=', 'expr': 'low < lowest', 'conditions': []}, {'mode': '', 'name': 'stopLossLevel', 'op': '=', 'expr': 'close * (1 - stopLossPercent)', 'conditions': []}]
    pine_user_functions = []
    pine_controls = []
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("Buy", strategy.long, when = wickDown)', 'conditions': [], 'statement': 'strategy.entry("Buy", strategy.long, when = wickDown)'}, {'kind': 'exit', 'call': 'strategy.exit("Sell at Donchian High", from_entry="Buy", limit=highest)', 'conditions': [], 'statement': 'strategy.exit("Sell at Donchian High", from_entry="Buy", limit=highest)'}, {'kind': 'exit', 'call': 'strategy.exit("Stop Loss", from_entry="Buy", stop=stopLossLevel)', 'conditions': [], 'statement': 'strategy.exit("Stop Loss", from_entry="Buy", stop=stopLossLevel)'}]
    original_pine = '/*backtest\nstart: 2023-10-22 00:00:00\nend: 2023-10-24 17:00:00\nperiod: 5m\nbasePeriod: 1m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=4\nstrategy("Donchian Wicks Strategy - Long Only with Customizable Donchian Exit and Stop Loss", "DWS", overlay = true)\n\n// INPUTS\niLength = input(20, "Length", minval = 1)\nstopLossPercent = input(1.0, "Stop Loss Percentage", type=input.float) / 100\n\n// SETTING\nfloat up = na\nup := close > open ? high : nz(up[1])\nfloat down = na\ndown := close < open ? low : nz(down[1])\n\nhighest = highest(up, iLength)\nlowest = lowest(down, iLength)\n\n// PLOT\np1 = plot(highest, "Highest", color.black, 2)\np2 = plot(lowest, "Lowest", color.black, 2)\nfill(p1, p2, color.new(color.navy, 90), title="Range")\n\n// ENTRY SIGNALS\nwickDown = low < lowest\n\n// STRATEGY IMPLEMENTATION\nstrategy.entry("Buy", strategy.long, when = wickDown)\nstrategy.exit("Sell at Donchian High", from_entry="Buy", limit=highest)\n\n// Customizable Stop Loss\nstopLossLevel = close * (1 - stopLossPercent)\nstrategy.exit("Stop Loss", from_entry="Buy", stop=stopLossLevel)'

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
