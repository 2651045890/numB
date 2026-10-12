"""Source-faithful deep-assisted port of 平均随机指标交易策略Average-Stochastic-Trading-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_f1f66540(PinePortBase, IStrategy):
    source_file = '平均随机指标交易策略Average-Stochastic-Trading-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'periodK': 21, 'smoothK': 3, 'periodD': 3}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_pyramiding = 3
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.entry', 'strategy.close', 'var ']
    source_fidelity_notes = ['Uses persistent Pine state (var/varip); state is order-dependent and must be evaluated bar-by-bar, not replaced by a vectorized fill-forward approximation.']
    pine_assignments = [{'mode': '', 'name': 'periodK', 'op': '=', 'expr': 'input.int(21, title="%K Length", minval=1)', 'conditions': []}, {'mode': '', 'name': 'smoothK', 'op': '=', 'expr': 'input.int(3, title="%K Smoothing", minval=1)', 'conditions': []}, {'mode': '', 'name': 'periodD', 'op': '=', 'expr': 'input.int(3, title="%D Smoothing", minval=1)', 'conditions': []}, {'mode': '', 'name': 'k', 'op': '=', 'expr': 'ta.sma(ta.stoch(close, high, low, periodK), smoothK)', 'conditions': []}, {'mode': '', 'name': 'd', 'op': '=', 'expr': 'ta.sma(k, periodD)', 'conditions': []}, {'mode': '', 'name': '_avg_k', 'op': '=', 'expr': 'ta.ema(math.avg(k,d),smoothK)', 'conditions': []}, {'mode': '', 'name': '_avg_d', 'op': '=', 'expr': 'ta.ema(_avg_k,periodD)', 'conditions': []}, {'mode': 'var', 'name': 'arr_val', 'op': '=', 'expr': '0', 'conditions': []}, {'mode': '', 'name': 'arr_val', 'op': ':=', 'expr': '1', 'conditions': ['up']}, {'mode': '', 'name': 'arr_val', 'op': ':=', 'expr': '-1', 'conditions': ['dn']}, {'mode': '', 'name': 'arr_val', 'op': ':=', 'expr': '0', 'conditions': ['up[1] or dn[1]']}]
    pine_user_functions = []
    pine_controls = [{'indent': 0, 'statement': 'if up'}, {'indent': 0, 'statement': 'if dn'}, {'indent': 0, 'statement': 'if up[1] or dn[1]'}, {'indent': 0, 'statement': 'if _avg_d>80'}, {'indent': 0, 'statement': 'if _avg_d<20'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("Long", strategy.long)', 'conditions': ['up'], 'statement': 'strategy.entry("Long", strategy.long)'}, {'kind': 'entry', 'call': 'strategy.entry("Short", strategy.short)', 'conditions': ['dn'], 'statement': 'strategy.entry("Short", strategy.short)'}, {'kind': 'close', 'call': 'strategy.close("Long")', 'conditions': ['_avg_d>80'], 'statement': 'strategy.close("Long")'}, {'kind': 'close', 'call': 'strategy.close("Short")', 'conditions': ['_avg_d<20'], 'statement': 'strategy.close("Short")'}]
    original_pine = '/*backtest\nstart: 2022-10-19 00:00:00\nend: 2023-10-25 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\n//1. AVG Stochastic Calculate\n//1.1 AVG %K is calculated by apply EMA with smooth K period on Average of Original Stochastic %k & %d\n//+ avg_k=ema((%k+%d)/2,smoothK)\n//1.2 AVG %D is calculated by apply EMA with %d period on AVG %K\n//+ avg_d=ema(avg_k,periodD)\n//2. Parameter\n//+ %K Length: 21\n//+ %K Smoothing: 3\n//+ %D Smoothing: 3\n//+ Symbol: BTC/USDT\n//+ Timeframe: M30\n//+ Pyramiding: Maximum 3 orders at the same direction.\n//3. Signal\n//3.1 Buy Signal\n//+ Entry: AVG %K crossover AVG %D and AVG %D < 20\n//+ Exit: AVG %D > 80 \n//3.2 Sell Signal\n//+ Entry: AVG %K crossunder AVG %D and AVG %D > 80\n//+ Exit: AVG %D < 20 \nstrategy(title="AVG Stochastic Strategy [M30 Backtesting]", overlay=true, pyramiding=3)\nperiodK = input.int(21, title="%K Length", minval=1)\nsmoothK = input.int(3, title="%K Smoothing", minval=1)\nperiodD = input.int(3, title="%D Smoothing", minval=1)\nk = ta.sma(ta.stoch(close, high, low, periodK), smoothK)\nd = ta.sma(k, periodD)\n_avg_k=ta.ema(math.avg(k,d),smoothK)\n_avg_d=ta.ema(_avg_k,periodD)\nup=\n   _avg_k[1]<_avg_d[1]\n   and _avg_k>_avg_d\n   and _avg_d<20\ndn=\n   _avg_k[1]>_avg_d[1]\n   and _avg_k<_avg_d\n   and _avg_d>80\nvar arr_val=0\nif up\n    arr_val:=1\n    strategy.entry("Long", strategy.long)\nif dn\n    arr_val:=-1\n    strategy.entry("Short", strategy.short)\nif up[1] or dn[1]\n    arr_val:=0\nplotarrow(arr_val,title="Signal",colorup=color.green,colordown=color.red)\nif _avg_d>80 \n    strategy.close("Long")\nif _avg_d<20 \n    strategy.close("Short")\n//EOF'

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
