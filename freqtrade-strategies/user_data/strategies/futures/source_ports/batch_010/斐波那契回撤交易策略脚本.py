"""Source-faithful deep-assisted port of 斐波那契回撤交易策略脚本.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_f0e1422f(PinePortBase, IStrategy):
    source_file = '斐波那契回撤交易策略脚本.md'
    timeframe = '1d'
    can_short = False
    source_defaults = {'length': 50, 'fib1': 0.236, 'fib2': 0.382, 'fib3': 0.618}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_pyramiding = 0
    source_initial_capital = 10000.0
    source_commission_percent = 0.0
    source_features = ['strategy.entry', 'strategy.close']
    source_fidelity_notes = []
    pine_assignments = [{'mode': '', 'name': 'length', 'op': '=', 'expr': 'input(50, title="斐波那契周期长度")', 'conditions': []}, {'mode': '', 'name': 'fib1', 'op': '=', 'expr': 'input(0.236, title="斐波那契水平1")', 'conditions': []}, {'mode': '', 'name': 'fib2', 'op': '=', 'expr': 'input(0.382, title="斐波那契水平2")', 'conditions': []}, {'mode': '', 'name': 'fib3', 'op': '=', 'expr': 'input(0.618, title="斐波那契水平3")', 'conditions': []}, {'mode': '', 'name': 'highLevel', 'op': '=', 'expr': 'ta.highest(high, length)', 'conditions': []}, {'mode': '', 'name': 'lowLevel', 'op': '=', 'expr': 'ta.lowest(low, length)', 'conditions': []}, {'mode': '', 'name': 'range1', 'op': '=', 'expr': 'highLevel - lowLevel', 'conditions': []}, {'mode': '', 'name': 'fibLevel1', 'op': '=', 'expr': 'highLevel - range1 * fib1', 'conditions': []}, {'mode': '', 'name': 'fibLevel2', 'op': '=', 'expr': 'highLevel - range1 * fib2', 'conditions': []}, {'mode': '', 'name': 'fibLevel3', 'op': '=', 'expr': 'highLevel - range1 * fib3', 'conditions': []}, {'mode': '', 'name': 'longCondition', 'op': '=', 'expr': 'ta.crossover(close, fibLevel3)', 'conditions': []}, {'mode': '', 'name': 'shortCondition', 'op': '=', 'expr': 'ta.crossunder(close, fibLevel1)', 'conditions': []}]
    pine_user_functions = []
    pine_controls = []
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("Buy", strategy.long, when=longCondition)', 'conditions': [], 'statement': 'strategy.entry("Buy", strategy.long, when=longCondition)'}, {'kind': 'close', 'call': 'strategy.close("Buy", when=shortCondition)', 'conditions': [], 'statement': 'strategy.close("Buy", when=shortCondition)'}]
    original_pine = '/*backtest\nstart: 2022-10-27 00:00:00\nend: 2023-11-02 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("斐波那契回撤交易策略", overlay=true, initial_capital=10000)\n\n// 参数\nlength = input(50, title="斐波那契周期长度")\nfib1 = input(0.236, title="斐波那契水平1")\nfib2 = input(0.382, title="斐波那契水平2")\nfib3 = input(0.618, title="斐波那契水平3")\n\n// 计算斐波那契水平\nhighLevel = ta.highest(high, length)\nlowLevel = ta.lowest(low, length)\nrange1 = highLevel - lowLevel\nfibLevel1 = highLevel - range1 * fib1\nfibLevel2 = highLevel - range1 * fib2\nfibLevel3 = highLevel - range1 * fib3\n\n// 条件\nlongCondition = ta.crossover(close, fibLevel3)\nshortCondition = ta.crossunder(close, fibLevel1)\n\n// 下单\nstrategy.entry("Buy", strategy.long, when=longCondition)\nstrategy.close("Buy", when=shortCondition)\n\n// 图表标记\nplot(fibLevel1, title="Fib 0.236", color=color.red)\nplot(fibLevel2, title="Fib 0.382", color=color.orange)\nplot(fibLevel3, title="Fib 0.618", color=color.green)'

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
