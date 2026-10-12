"""Source-faithful deep-assisted port of 百分比追踪止损策略Percent-Trailing-Stop-Loss-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_fcff9fc0(PinePortBase, IStrategy):
    source_file = '百分比追踪止损策略Percent-Trailing-Stop-Loss-Strategy.md'
    timeframe = '2h'
    can_short = True
    source_defaults = {'trailStop': 10}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.exit', 'strategy.entry', 'strategy.position_size']
    source_fidelity_notes = ['Reads broker/strategy state; signals depend on fill timing and cannot be reduced to indicator-only booleans without changing behavior.', 'Uses strategy.exit; stop/limit/profit/loss/trailing arguments have Pine order semantics and may fill intrabar.']
    pine_assignments = [{'mode': '', 'name': 'longCondition', 'op': '=', 'expr': 'crossover(sma(close, 10), sma(close, 20))', 'conditions': []}, {'mode': '', 'name': 'shortCondition', 'op': '=', 'expr': 'crossunder(sma(close, 10), sma(close, 20))', 'conditions': []}, {'mode': '', 'name': 'trailStop', 'op': '=', 'expr': 'input(title="Long Trailing Stop (%)", type=input.float, minval=0.0, step=0.1, defval=10) * 0.01', 'conditions': []}, {'mode': '', 'name': 'longStopPrice', 'op': '=', 'expr': '0.0', 'conditions': []}, {'mode': '', 'name': 'shortStopPrice', 'op': '=', 'expr': '0.0', 'conditions': []}, {'mode': '', 'name': 'longStopPrice', 'op': ':=', 'expr': 'if strategy.position_size > 0', 'conditions': []}, {'mode': '', 'name': 'stopValue', 'op': '=', 'expr': 'close * (1 - trailStop)', 'conditions': []}, {'mode': '', 'name': 'shortStopPrice', 'op': ':=', 'expr': 'if strategy.position_size < 0', 'conditions': []}, {'mode': '', 'name': 'stopValue', 'op': '=', 'expr': 'close * (1 + trailStop)', 'conditions': []}]
    pine_user_functions = []
    pine_controls = [{'indent': 0, 'statement': 'if (longCondition)'}, {'indent': 0, 'statement': 'if (shortCondition)'}, {'indent': 0, 'statement': 'else'}, {'indent': 0, 'statement': 'else'}, {'indent': 0, 'statement': 'if strategy.position_size > 0'}, {'indent': 0, 'statement': 'if strategy.position_size < 0'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("My Long Entry Id", strategy.long)', 'conditions': ['(longCondition)'], 'statement': 'strategy.entry("My Long Entry Id", strategy.long)'}, {'kind': 'entry', 'call': 'strategy.entry("My Short Entry Id", strategy.short)', 'conditions': ['(shortCondition)'], 'statement': 'strategy.entry("My Short Entry Id", strategy.short)'}, {'kind': 'exit', 'call': 'strategy.exit(id="Close Long", stop=longStopPrice)', 'conditions': ['strategy.position_size > 0'], 'statement': 'strategy.exit(id="Close Long", stop=longStopPrice)'}, {'kind': 'exit', 'call': 'strategy.exit(id="Close Short", stop=shortStopPrice)', 'conditions': ['strategy.position_size < 0'], 'statement': 'strategy.exit(id="Close Short", stop=shortStopPrice)'}]
    original_pine = '/*backtest\nstart: 2023-08-19 00:00:00\nend: 2023-09-18 00:00:00\nperiod: 2h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// © theCrypster\n\n//@version=4\nstrategy("Percent Trailing Stop %", overlay=true)\n\n//ENTER SOME SETUP TRADES FOR TSL EXAMPLE\nlongCondition = crossover(sma(close, 10), sma(close, 20))\nif (longCondition)\n    strategy.entry("My Long Entry Id", strategy.long)\n\nshortCondition = crossunder(sma(close, 10), sma(close, 20))\nif (shortCondition)\n    strategy.entry("My Short Entry Id", strategy.short)\n    \n\n//TRAILING STOP CODE\ntrailStop = input(title="Long Trailing Stop (%)", type=input.float, minval=0.0, step=0.1, defval=10) * 0.01\n\nlongStopPrice = 0.0\nshortStopPrice = 0.0\nlongStopPrice := if strategy.position_size > 0\n    stopValue = close * (1 - trailStop)\n    max(stopValue, longStopPrice[1])\nelse\n    0\nshortStopPrice := if strategy.position_size < 0\n    stopValue = close * (1 + trailStop)\n    min(stopValue, shortStopPrice[1])\nelse\n    999999\n\n//PLOT TSL LINES\nplot(series=strategy.position_size > 0 ? longStopPrice : na, color=color.red, style=plot.style_linebr, linewidth=1, title="Long Trail Stop", offset=1, title="Long Trail Stop")\nplot(series=strategy.position_size < 0 ? shortStopPrice : na, color=color.red, style=plot.style_linebr, linewidth=1, title="Short Trail Stop", offset=1, title="Short Trail Stop")\n\n\n//EXIT TRADE @ TSL\nif strategy.position_size > 0\n    strategy.exit(id="Close Long", stop=longStopPrice)\nif strategy.position_size < 0\n    strategy.exit(id="Close Short", stop=shortStopPrice)'

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
