"""Source-faithful deep-assisted port of 指标积分策略Momentum-Integral-Indicator-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_cf79d0ea(PinePortBase, IStrategy):
    source_file = '指标积分策略Momentum-Integral-Indicator-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'l': 170, 's': 18, 'inpTakeProfit': 0, 'inpStopLoss': 0, 'inpTrailStop': 0, 'inpTrailOffset': 0}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 100.0
    source_pyramiding = 0
    source_initial_capital = 662.0
    source_commission_percent = 0.0
    source_features = ['strategy.exit', 'strategy.entry', 'strategy.close', 'strategy.cancel', 'strategy.closedtrades', 'strategy.equity', 'for ']
    source_fidelity_notes = ['Reads broker/strategy state; signals depend on fill timing and cannot be reduced to indicator-only booleans without changing behavior.', 'Uses strategy.exit; stop/limit/profit/loss/trailing arguments have Pine order semantics and may fill intrabar.']
    pine_assignments = [{'mode': '', 'name': 'l', 'op': '=', 'expr': 'input(defval=170,title="Length for indicator")', 'conditions': []}, {'mode': '', 'name': 's', 'op': '=', 'expr': 'input(title="Length of summation",defval=18)', 'conditions': []}, {'mode': '', 'name': 'a', 'op': '=', 'expr': 'sma(close,l)', 'conditions': []}, {'mode': '', 'name': 'r', 'op': '=', 'expr': 'roc(close,l)', 'conditions': []}, {'mode': '', 'name': 'k', 'op': '=', 'expr': 'close-a', 'conditions': []}, {'mode': '', 'name': 'sum', 'op': '=', 'expr': '0', 'conditions': []}, {'mode': '', 'name': 'sum', 'op': ':=', 'expr': 'sum + k[i]', 'conditions': []}, {'mode': '', 'name': 'inpTakeProfit', 'op': '=', 'expr': 'input(defval = 0, title = "Take Profit", minval = 0)', 'conditions': []}, {'mode': '', 'name': 'inpStopLoss', 'op': '=', 'expr': 'input(defval = 0, title = "Stop Loss", minval = 0)', 'conditions': []}, {'mode': '', 'name': 'inpTrailStop', 'op': '=', 'expr': 'input(defval = 0, title = "Trailing Stop Loss", minval = 0)', 'conditions': []}, {'mode': '', 'name': 'inpTrailOffset', 'op': '=', 'expr': 'input(defval = 0, title = "Trailing Stop Loss Offset", minval = 0)', 'conditions': []}, {'mode': '', 'name': 'useTakeProfit', 'op': '=', 'expr': 'inpTakeProfit >= 1 ? inpTakeProfit : na', 'conditions': []}, {'mode': '', 'name': 'useStopLoss', 'op': '=', 'expr': 'inpStopLoss >= 1 ? inpStopLoss : na', 'conditions': []}, {'mode': '', 'name': 'useTrailStop', 'op': '=', 'expr': 'inpTrailStop >= 1 ? inpTrailStop : na', 'conditions': []}, {'mode': '', 'name': 'useTrailOffset', 'op': '=', 'expr': 'inpTrailOffset >= 1 ? inpTrailOffset : na', 'conditions': []}]
    pine_user_functions = []
    pine_controls = [{'indent': 0, 'statement': 'for i = 0 to s'}, {'indent': 0, 'statement': 'if sum>0'}, {'indent': 0, 'statement': 'else'}, {'indent': 0, 'statement': 'if sum<0'}, {'indent': 0, 'statement': 'else'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("Long", strategy.long, oca_name="Long", comment="Long")', 'conditions': ['sum>0'], 'statement': 'strategy.entry("Long", strategy.long, oca_name="Long", comment="Long")'}, {'kind': 'cancel', 'call': 'strategy.cancel(id="Long")', 'conditions': ['ELSE'], 'statement': 'strategy.cancel(id="Long")'}, {'kind': 'entry', 'call': 'strategy.entry("Short", strategy.short, oca_name="Short", comment="Short")', 'conditions': ['sum<0'], 'statement': 'strategy.entry("Short", strategy.short, oca_name="Short", comment="Short")'}, {'kind': 'cancel', 'call': 'strategy.cancel(id="Short")', 'conditions': ['ELSE'], 'statement': 'strategy.cancel(id="Short")'}]
    original_pine = '/*backtest\nstart: 2023-10-06 00:00:00\nend: 2023-11-05 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=2\nstrategy("Indicator Integrator Strat",default_qty_type = strategy.percent_of_equity, default_qty_value = 100,currency="USD",initial_capital=662, overlay=false)\n\nl = input(defval=170,title="Length for indicator")\ns = input(title="Length of summation",defval=18)\na= sma(close,l)\nr=roc(close,l)\nk=close-a\nsum = 0\nfor i = 0 to s\n    sum := sum + k[i]\n//plot(a,color=yellow,linewidth=2,transp=0)\n//bc =  iff( sum > 0, white, teal)\n//plot(sum,color=bc, transp=20, linewidth=3,style=columns)\n//plot(sma(sum,3),color=white)\n//hline(0)\n\ninpTakeProfit = input(defval = 0, title = "Take Profit", minval = 0)\ninpStopLoss = input(defval = 0, title = "Stop Loss", minval = 0)\ninpTrailStop = input(defval = 0, title = "Trailing Stop Loss", minval = 0)\ninpTrailOffset = input(defval = 0, title = "Trailing Stop Loss Offset", minval = 0)\nuseTakeProfit = inpTakeProfit >= 1 ? inpTakeProfit : na\nuseStopLoss = inpStopLoss >= 1 ? inpStopLoss : na\nuseTrailStop = inpTrailStop >= 1 ? inpTrailStop : na\nuseTrailOffset = inpTrailOffset >= 1 ? inpTrailOffset : na\n\n////buyEntry = crossover(source, lower)\n////sellEntry = crossunder(source, upper)\nif sum>0\n    strategy.entry("Long", strategy.long, oca_name="Long",  comment="Long")\nelse\n    strategy.cancel(id="Long")\nif sum<0\n    strategy.entry("Short", strategy.short, oca_name="Short", comment="Short")\nelse\n    strategy.cancel(id="Short")\nstrategy.initial_capital = 50000\nplot(strategy.equity-strategy.initial_capital-strategy.closedtrades*.25/2, title="equity", color=red, linewidth=2)\nhline(0)\n//longCondition = sum>0\n//exitlong = sum<0\n\n//shortCondition = sum<0\n//exitshort = sum>0\n\n//strategy.entry(id = "Long", long=true, when = longCondition)\n//strategy.close(id = "Long", when = exitlong)\n//strategy.exit("Exit Long", from_entry = "Long", profit = useTakeProfit, loss = useStopLoss, trail_points = useTrailStop, trail_offset = useTrailOffset, when=exitlong)\n\n//strategy.entry(id = "Short", long=false, when = shortCondition)\n//strategy.close(id = "Short", when = exitshort)\n//strategy.exit("Exit Short", from_entry = "Short", profit = useTakeProfit, loss = useStopLoss, trail_points = useTrailStop, trail_offset = useTrailOffset, when=exitshort)'

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
