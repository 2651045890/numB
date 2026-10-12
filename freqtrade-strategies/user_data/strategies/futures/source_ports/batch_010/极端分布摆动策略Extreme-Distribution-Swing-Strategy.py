"""Source-faithful deep-assisted port of 极端分布摆动策略Extreme-Distribution-Swing-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_a5c290bd(PinePortBase, IStrategy):
    source_file = '极端分布摆动策略Extreme-Distribution-Swing-Strategy.md'
    timeframe = '1h'
    can_short = True
    source_defaults = {'length': 9}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.entry', 'strategy.close', 'for ', '=>']
    source_fidelity_notes = []
    pine_assignments = [{'mode': '', 'name': 'length', 'op': '=', 'expr': 'input(9, minval=1)', 'conditions': []}, {'mode': '', 'name': 'src', 'op': '=', 'expr': 'close', 'conditions': []}, {'mode': '', 'name': 'momm', 'op': '=', 'expr': 'change(src)', 'conditions': []}, {'mode': '', 'name': 'm1', 'op': '=', 'expr': 'f1(momm)', 'conditions': []}, {'mode': '', 'name': 'm2', 'op': '=', 'expr': 'f2(momm)', 'conditions': []}, {'mode': '', 'name': 'sm1', 'op': '=', 'expr': 'sum(m1, length)', 'conditions': []}, {'mode': '', 'name': 'sm2', 'op': '=', 'expr': 'sum(m2, length)', 'conditions': []}, {'mode': '', 'name': 'chandeMO', 'op': '=', 'expr': 'percent(sm1-sm2, sm1+sm2)', 'conditions': []}, {'mode': '', 'name': 'lengthLookback', 'op': '=', 'expr': '425 //425 golden number', 'conditions': []}, {'mode': '', 'name': 'buyPercentile', 'op': '=', 'expr': '1', 'conditions': []}, {'mode': '', 'name': 'sellPercentile', 'op': '=', 'expr': '99', 'conditions': []}, {'mode': '', 'name': 'linePercentileLow', 'op': '=', 'expr': '2.5', 'conditions': []}, {'mode': '', 'name': 'linePercentileHigh', 'op': '=', 'expr': '97.5', 'conditions': []}, {'mode': '', 'name': 'buy', 'op': '=', 'expr': 'percentile_nearest_rank(chandeMO, lengthLookback, buyPercentile)', 'conditions': []}, {'mode': '', 'name': 'exitBuy', 'op': '=', 'expr': 'percentile_nearest_rank(chandeMO, lengthLookback, linePercentileHigh)', 'conditions': []}, {'mode': '', 'name': 'sell', 'op': '=', 'expr': 'percentile_nearest_rank(chandeMO, lengthLookback, sellPercentile)', 'conditions': []}, {'mode': '', 'name': 'exitSell', 'op': '=', 'expr': 'percentile_nearest_rank(chandeMO, lengthLookback, linePercentileLow)', 'conditions': []}, {'mode': '', 'name': 'chandeMA', 'op': '=', 'expr': 'sma(chandeMO, 9) //sma for potential other strategies implementing cross / trend', 'conditions': []}, {'mode': '', 'name': 'closeLongCondition', 'op': '=', 'expr': 'chandeMO > exitBuy ? true : false', 'conditions': []}, {'mode': '', 'name': 'closeShortCondition', 'op': '=', 'expr': 'chandeMO < exitSell ? true : false', 'conditions': []}, {'mode': '', 'name': 'longCondition', 'op': '=', 'expr': 'chandeMO < buy', 'conditions': []}, {'mode': '', 'name': 'shortCondition', 'op': '=', 'expr': 'chandeMO > sell', 'conditions': []}]
    pine_user_functions = [{'name': 'f1', 'args': 'm', 'body': 'm >= 0.0 ? m : 0.0'}, {'name': 'f2', 'args': 'm', 'body': 'm >= 0.0 ? 0.0 : -m'}, {'name': 'percent', 'args': 'nom, div', 'body': '100 * nom / div'}]
    pine_controls = [{'indent': 0, 'statement': 'if (longCondition)'}, {'indent': 0, 'statement': 'if (shortCondition)'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("long", strategy.long)', 'conditions': ['(longCondition)'], 'statement': 'strategy.entry("long", strategy.long)'}, {'kind': 'entry', 'call': 'strategy.entry("short", strategy.short)', 'conditions': ['(shortCondition)'], 'statement': 'strategy.entry("short", strategy.short)'}]
    original_pine = '/*backtest\nstart: 2023-10-13 00:00:00\nend: 2023-11-12 00:00:00\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=4\nstrategy("Chande Minute Swinger", overlay=true)\n\n//Chande\n\nlength = input(9, minval=1)\nsrc = close\nmomm = change(src)\nf1(m) => m >= 0.0 ? m : 0.0\nf2(m) => m >= 0.0 ? 0.0 : -m\nm1 = f1(momm)\nm2 = f2(momm)\nsm1 = sum(m1, length)\nsm2 = sum(m2, length)\npercent(nom, div) => 100 * nom / div\nchandeMO = percent(sm1-sm2, sm1+sm2)\n\n//Parameters to change\n\nlengthLookback = 425 //425 golden number\nbuyPercentile = 1\nsellPercentile = 99\nlinePercentileLow = 2.5\nlinePercentileHigh = 97.5\n\nbuy = percentile_nearest_rank(chandeMO, lengthLookback, buyPercentile)\nexitBuy= percentile_nearest_rank(chandeMO, lengthLookback, linePercentileHigh)\nsell = percentile_nearest_rank(chandeMO, lengthLookback, sellPercentile)\nexitSell = percentile_nearest_rank(chandeMO, lengthLookback, linePercentileLow)\n\nchandeMA = sma(chandeMO, 9) //sma for potential other strategies implementing cross / trend\n\n//Entry conditions\n\ncloseLongCondition = chandeMO > exitBuy ? true : false\ncloseShortCondition = chandeMO < exitSell ? true : false\nlongCondition = chandeMO < buy\nshortCondition = chandeMO > sell\n\nif (longCondition)\n    strategy.entry("long", strategy.long)\n    \n\nif (shortCondition)\n    strategy.entry("short", strategy.short)\n    \n//Introducing the closes and a stoploss will minimise loss and bring up the sharpe ratio\n//Current settings are enabled for maximum potential but big risk\n    \n//strategy.close("long", when=(closeLongCondition == true))\n//strategy.close("short", when=(closeShortCondition == true))'

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
