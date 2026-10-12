"""Source-faithful deep-assisted port of 渐进止损上移策略Gradual-Stop-Loss-Movement-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_96de87f6(PinePortBase, IStrategy):
    source_file = '渐进止损上移策略Gradual-Stop-Loss-Movement-Strategy.md'
    timeframe = '1h'
    can_short = False
    source_defaults = {}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.exit', 'strategy.entry']
    source_fidelity_notes = ['Uses strategy.exit; stop/limit/profit/loss/trailing arguments have Pine order semantics and may fill intrabar.']
    pine_assignments = [{'mode': '', 'name': 'longCondition', 'op': '=', 'expr': 'crossover(sma(close, 14), sma(close, 28))', 'conditions': []}, {'mode': '', 'name': 'first_stop', 'op': '=', 'expr': 'strategy.position_avg_price * .95', 'conditions': []}, {'mode': '', 'name': 'second_stop', 'op': '=', 'expr': 'strategy.position_avg_price', 'conditions': []}, {'mode': '', 'name': 'third_stop', 'op': '=', 'expr': 'strategy.position_avg_price * 1.05', 'conditions': []}, {'mode': '', 'name': 'fourth_stop', 'op': '=', 'expr': 'strategy.position_avg_price * 1.1', 'conditions': []}, {'mode': '', 'name': 'fifth_stop', 'op': '=', 'expr': 'strategy.position_avg_price * 1.15', 'conditions': []}, {'mode': '', 'name': 'sixth_stop', 'op': '=', 'expr': 'strategy.position_avg_price * 1.2', 'conditions': []}, {'mode': '', 'name': 'seventh_stop', 'op': '=', 'expr': 'strategy.position_avg_price * 1.25', 'conditions': []}, {'mode': '', 'name': 'eighth_stop', 'op': '=', 'expr': 'strategy.position_avg_price * 1.3', 'conditions': []}, {'mode': '', 'name': 'move_trigger', 'op': '=', 'expr': 'lowest(low,7)', 'conditions': []}, {'mode': '', 'name': 'first_check', 'op': '=', 'expr': 'na', 'conditions': []}, {'mode': '', 'name': 'first_check', 'op': ':=', 'expr': 'move_trigger > second_stop ? second_stop : first_stop', 'conditions': []}, {'mode': '', 'name': 'second_check', 'op': '=', 'expr': 'na', 'conditions': []}, {'mode': '', 'name': 'second_check', 'op': ':=', 'expr': 'move_trigger > third_stop ? third_stop : first_check', 'conditions': []}, {'mode': '', 'name': 'third_check', 'op': '=', 'expr': 'na', 'conditions': []}, {'mode': '', 'name': 'third_check', 'op': ':=', 'expr': 'move_trigger > fourth_stop ? fourth_stop : second_check', 'conditions': []}, {'mode': '', 'name': 'fourth_check', 'op': '=', 'expr': 'na', 'conditions': []}, {'mode': '', 'name': 'fourth_check', 'op': ':=', 'expr': 'move_trigger > fifth_stop ? fifth_stop : third_check', 'conditions': []}, {'mode': '', 'name': 'fifth_check', 'op': '=', 'expr': 'na', 'conditions': []}, {'mode': '', 'name': 'fifth_check', 'op': ':=', 'expr': 'move_trigger > sixth_stop ? sixth_stop : fourth_check', 'conditions': []}, {'mode': '', 'name': 'sixth_check', 'op': '=', 'expr': 'na', 'conditions': []}, {'mode': '', 'name': 'sixth_check', 'op': ':=', 'expr': 'move_trigger > seventh_stop ? seventh_stop : fifth_check', 'conditions': []}, {'mode': '', 'name': 'stop_level', 'op': '=', 'expr': 'na', 'conditions': []}, {'mode': '', 'name': 'stop_level', 'op': ':=', 'expr': 'move_trigger > eighth_stop ? eighth_stop : sixth_check', 'conditions': []}]
    pine_user_functions = []
    pine_controls = [{'indent': 0, 'statement': 'if (longCondition)'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("My Long Entry Id", strategy.long)', 'conditions': ['(longCondition)'], 'statement': 'strategy.entry("My Long Entry Id", strategy.long)'}, {'kind': 'exit', 'call': 'strategy.exit("Stop Loss","My Long Entry Id", stop=stop_level)', 'conditions': [], 'statement': 'strategy.exit("Stop Loss","My Long Entry Id", stop=stop_level)'}]
    original_pine = '/*backtest\nstart: 2023-10-13 00:00:00\nend: 2023-11-12 00:00:00\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=3\n\n///Moving Stops Script///\n///by ShanghaiCryto///\n\n///A simple, but very useful, script that reminds you to move up your stop losses as price trends upwards. ///\n///The sma entry is just stock code to demonstrate how the stop works.///\n///Doesn\'t throw off your backtesting the way a trailing stop does.///\n\n\nstrategy("Move Up Stops", overlay=true)\n\nlongCondition = crossover(sma(close, 14), sma(close, 28))\nif (longCondition)\n    strategy.entry("My Long Entry Id", strategy.long)\n\nfirst_stop = strategy.position_avg_price * .95\nsecond_stop = strategy.position_avg_price \nthird_stop = strategy.position_avg_price * 1.05\nfourth_stop = strategy.position_avg_price * 1.1\nfifth_stop = strategy.position_avg_price * 1.15\nsixth_stop = strategy.position_avg_price * 1.2\nseventh_stop = strategy.position_avg_price * 1.25\neighth_stop = strategy.position_avg_price * 1.3\n\nmove_trigger = lowest(low,7)\n\nfirst_check = na\nfirst_check := move_trigger > second_stop ? second_stop : first_stop\n\nsecond_check = na\nsecond_check := move_trigger > third_stop ? third_stop : first_check\n\nthird_check = na\nthird_check := move_trigger > fourth_stop ? fourth_stop : second_check\n\nfourth_check = na\nfourth_check := move_trigger > fifth_stop ? fifth_stop : third_check\n\nfifth_check = na\nfifth_check := move_trigger > sixth_stop ? sixth_stop : fourth_check\n\nsixth_check = na\nsixth_check := move_trigger > seventh_stop ? seventh_stop : fifth_check\n\nstop_level = na\nstop_level := move_trigger > eighth_stop ? eighth_stop : sixth_check\n\nstrategy.exit("Stop Loss","My Long Entry Id", stop=stop_level)\n\nplot(stop_level, color=red)'

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
