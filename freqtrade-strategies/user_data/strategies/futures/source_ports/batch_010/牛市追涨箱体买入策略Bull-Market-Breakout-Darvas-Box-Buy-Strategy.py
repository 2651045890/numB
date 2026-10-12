"""Source-faithful deep-assisted port of 牛市追涨箱体买入策略Bull-Market-Breakout-Darvas-Box-Buy-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_74d53927(PinePortBase, IStrategy):
    source_file = '牛市追涨箱体买入策略Bull-Market-Breakout-Darvas-Box-Buy-Strategy.md'
    timeframe = '1h'
    can_short = False
    source_defaults = {'boxp': 5}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.exit', 'strategy.entry']
    source_fidelity_notes = ['Uses strategy.exit; stop/limit/profit/loss/trailing arguments have Pine order semantics and may fill intrabar.']
    pine_assignments = [{'mode': '', 'name': 'start_date', 'op': '=', 'expr': 'timestamp(2023, 10, 15, 0, 0)', 'conditions': []}, {'mode': '', 'name': 'boxp', 'op': '=', 'expr': 'input(5, "BOX LENGTH")', 'conditions': []}, {'mode': '', 'name': 'LL', 'op': '=', 'expr': 'lowest(low, boxp)', 'conditions': []}, {'mode': '', 'name': 'k1', 'op': '=', 'expr': 'highest(high, boxp)', 'conditions': []}, {'mode': '', 'name': 'k2', 'op': '=', 'expr': 'highest(high, boxp - 1)', 'conditions': []}, {'mode': '', 'name': 'k3', 'op': '=', 'expr': 'highest(high, boxp - 2)', 'conditions': []}, {'mode': '', 'name': 'NH', 'op': '=', 'expr': 'valuewhen(high > k1[1], high, 0)', 'conditions': []}, {'mode': '', 'name': 'box1', 'op': '=', 'expr': 'k3 < k2', 'conditions': []}, {'mode': '', 'name': 'TopBox', 'op': '=', 'expr': 'valuewhen(barssince(high > k1[1]) == boxp - 2 and box1, NH, 0)', 'conditions': []}, {'mode': '', 'name': 'BottomBox', 'op': '=', 'expr': 'valuewhen(barssince(high > k1[1]) == boxp - 2 and box1, LL, 0)', 'conditions': []}, {'mode': '', 'name': 'enterLong', 'op': '=', 'expr': 'crossover(close, TopBox)', 'conditions': []}, {'mode': '', 'name': 'exitLong', 'op': '=', 'expr': 'false // No specific exit condition mentioned in the original script', 'conditions': []}, {'mode': '', 'name': 'stopLoss', 'op': '=', 'expr': 'BottomBox', 'conditions': []}, {'mode': '', 'name': 'takeProfit', 'op': '=', 'expr': 'stopLoss * 5', 'conditions': []}]
    pine_user_functions = []
    pine_controls = []
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("Buy", strategy.long, when = enterLong)', 'conditions': [], 'statement': 'strategy.entry("Buy", strategy.long, when = enterLong)'}, {'kind': 'exit', 'call': 'strategy.exit("Exit", "Buy", stop = stopLoss, limit = takeProfit)', 'conditions': [], 'statement': 'strategy.exit("Exit", "Buy", stop = stopLoss, limit = takeProfit)'}]
    original_pine = '/*backtest\nstart: 2023-12-01 00:00:00\nend: 2023-12-31 23:59:59\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=4\nstrategy("Darvas Box Strategy - Buy Only", overlay=true)\n\nstart_date = timestamp(2023, 10, 15, 0, 0)\n\nboxp = input(5, "BOX LENGTH")\n\nLL = lowest(low, boxp)\nk1 = highest(high, boxp)\nk2 = highest(high, boxp - 1)\nk3 = highest(high, boxp - 2)\n\nNH = valuewhen(high > k1[1], high, 0)\nbox1 = k3 < k2\nTopBox = valuewhen(barssince(high > k1[1]) == boxp - 2 and box1, NH, 0)\nBottomBox = valuewhen(barssince(high > k1[1]) == boxp - 2 and box1, LL, 0)\n\nplot(TopBox, linewidth=2, color=color.green, title="TopBox")\nplot(BottomBox, linewidth=2, color=color.red, title="BottomBox")\n\n// Define entry conditions\nenterLong = crossover(close, TopBox)\n\n// Define exit conditions\nexitLong = false  // No specific exit condition mentioned in the original script\n\n// Define stop loss level\nstopLoss = BottomBox\n\n// Define take profit level (2 times the stop loss)\ntakeProfit = stopLoss * 5\n\n// Execute buy trade and set stop loss and take profit\nstrategy.entry("Buy", strategy.long, when = enterLong)\nstrategy.exit("Exit", "Buy", stop = stopLoss, limit = takeProfit)\n\n// Plot buy signal arrow\nplotshape(enterLong, title = "Buy Signal", style = shape.labelup, location = location.belowbar, color = color.green)\n\n// Plot stop loss level\nplot(stopLoss, linewidth=2, color=color.red, title="Stop Loss Level")\n\n// Plot take profit level\nplot(takeProfit, linewidth=2, color=color.rgb(19, 202, 111), title="Take Profit Level")\n\n// Hide sell signal arrow\nplotshape(false, title = "Sell Signal", style = shape.labeldown, location = location.abovebar, color = color.red, transp = 100)'

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
