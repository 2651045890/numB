"""Source-faithful deep-assisted port of 慢速随机指标趋势追踪策略Slow-Stochastic-Trend-Following-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_d664ac0d(PinePortBase, IStrategy):
    source_file = '慢速随机指标趋势追踪策略Slow-Stochastic-Trend-Following-Strategy.md'
    timeframe = '1m'
    can_short = True
    source_defaults = {'smoothK': 400, 'price': 'ohlc4', 'SMAsmoothK': 275, 'smoothD': 10, 'OB': 78.5, 'OS': 23}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.entry', 'strategy.close']
    source_fidelity_notes = []
    pine_assignments = [{'mode': '', 'name': 'smoothK', 'op': '=', 'expr': 'input(400, step=5)', 'conditions': []}, {'mode': '', 'name': 'price', 'op': '=', 'expr': 'input(ohlc4)', 'conditions': []}, {'mode': '', 'name': 'SMAsmoothK', 'op': '=', 'expr': 'input(275, step=5)', 'conditions': []}, {'mode': '', 'name': 'k', 'op': '=', 'expr': 'sma(stoch(price, high, low, smoothK), SMAsmoothK)', 'conditions': []}, {'mode': '', 'name': 'smoothD', 'op': '=', 'expr': 'input(10, step=2)', 'conditions': []}, {'mode': '', 'name': 'd', 'op': '=', 'expr': 'sma(k, smoothD)', 'conditions': []}, {'mode': '', 'name': 'OB', 'op': '=', 'expr': 'input(78.5, step=0.5)', 'conditions': []}, {'mode': '', 'name': 'OS', 'op': '=', 'expr': 'input(23, step=0.5)', 'conditions': []}, {'mode': '', 'name': 'long', 'op': '=', 'expr': 'crossover(d, OS)', 'conditions': []}, {'mode': '', 'name': 'short', 'op': '=', 'expr': 'crossunder(d, OB)', 'conditions': []}, {'mode': '', 'name': 'closelong', 'op': '=', 'expr': 'crossover(d, OB)', 'conditions': []}, {'mode': '', 'name': 'closeshort', 'op': '=', 'expr': 'crossunder(d, OS)', 'conditions': []}]
    pine_user_functions = []
    pine_controls = []
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("Long", strategy.long, when=long) //_signal or long) //or closeshort_signal)', 'conditions': [], 'statement': 'strategy.entry("Long", strategy.long, when=long) //_signal or long) //or closeshort_signal)'}, {'kind': 'entry', 'call': 'strategy.entry("Short", strategy.short, when=short) //_signal or short) // or closelong_signal)', 'conditions': [], 'statement': 'strategy.entry("Short", strategy.short, when=short) //_signal or short) // or closelong_signal)'}, {'kind': 'close', 'call': 'strategy.close("Long", when=closelong)', 'conditions': [], 'statement': 'strategy.close("Long", when=closelong)'}, {'kind': 'close', 'call': 'strategy.close("Short", when=closeshort)', 'conditions': [], 'statement': 'strategy.close("Short", when=closeshort)'}]
    original_pine = '/*backtest\nstart: 2023-12-20 00:00:00\nend: 2023-12-27 00:00:00\nperiod: 1m\nbasePeriod: 1m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=4\nstrategy(title="Slow Stochastic OB/OS Strategy", overlay=false )\n\nsmoothK = input(400, step=5) \nprice = input(ohlc4)\nSMAsmoothK = input(275, step=5)\nk = sma(stoch(price, high, low, smoothK), SMAsmoothK)\nplot(k, color=white)\n\n\nsmoothD = input(10, step=2)\nd = sma(k, smoothD)\nplot(d, color=red)\n\n\nOB = input(78.5, step=0.5)\nOS = input(23, step=0.5)\nhline(OB, linewidth=1, color=red)\nhline(OS,linewidth=1, color=green)\nhline(50,linewidth=1, color=gray)\n\n\nlong = crossover(d, OS)\nshort = crossunder(d, OB)\n\nstrategy.entry("Long", strategy.long, when=long) //_signal or long) //or closeshort_signal)\nstrategy.entry("Short", strategy.short, when=short) //_signal or short) // or closelong_signal)\n\n//If you want to try to play with exits you can activate these!\n\ncloselong = crossover(d, OB)\ncloseshort = crossunder(d, OS)\n\nstrategy.close("Long", when=closelong)\nstrategy.close("Short", when=closeshort)'

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
