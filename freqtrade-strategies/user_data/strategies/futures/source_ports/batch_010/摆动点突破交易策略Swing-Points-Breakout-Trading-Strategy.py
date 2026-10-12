"""Source-faithful deep-assisted port of 摆动点突破交易策略Swing-Points-Breakout-Trading-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_e9bec531(PinePortBase, IStrategy):
    source_file = '摆动点突破交易策略Swing-Points-Breakout-Trading-Strategy.md'
    timeframe = '2h'
    can_short = True
    source_defaults = {'leftBars': 1, 'rightBars': 1}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.exit', 'strategy.entry']
    source_fidelity_notes = ['Uses strategy.exit; stop/limit/profit/loss/trailing arguments have Pine order semantics and may fill intrabar.']
    pine_assignments = [{'mode': '', 'name': 'leftBars', 'op': '=', 'expr': 'input(1)', 'conditions': []}, {'mode': '', 'name': 'rightBars', 'op': '=', 'expr': 'input(1)', 'conditions': []}, {'mode': '', 'name': 'sl', 'op': '=', 'expr': 'pivotlow(low, leftBars, rightBars)', 'conditions': []}, {'mode': '', 'name': 'sh', 'op': '=', 'expr': 'pivothigh(high, leftBars, rightBars)', 'conditions': []}, {'mode': '', 'name': 'last_sh', 'op': '=', 'expr': 'na', 'conditions': []}, {'mode': '', 'name': 'last_sh', 'op': ':=', 'expr': 'sh!=0 ? sh : nz(last_sh[1])', 'conditions': []}, {'mode': '', 'name': 'last_sl', 'op': '=', 'expr': 'na', 'conditions': []}, {'mode': '', 'name': 'last_sl', 'op': ':=', 'expr': 'sl!=0 ? sl : nz(last_sl[1])', 'conditions': []}, {'mode': '', 'name': 'EMA', 'op': '=', 'expr': 'ema(close,55)', 'conditions': []}, {'mode': '', 'name': 'longCondition', 'op': '=', 'expr': 'sh and high > EMA', 'conditions': []}, {'mode': '', 'name': 'shortCondition', 'op': '=', 'expr': 'sl and close < EMA', 'conditions': []}, {'mode': '', 'name': 'exitLongCondition', 'op': '=', 'expr': 'sl < sh[1]', 'conditions': []}, {'mode': '', 'name': 'exitShortCondition', 'op': '=', 'expr': 'sh > sl[1]', 'conditions': []}]
    pine_user_functions = []
    pine_controls = [{'indent': 0, 'statement': 'if longCondition'}, {'indent': 0, 'statement': 'if shortCondition'}, {'indent': 0, 'statement': 'if exitLongCondition'}, {'indent': 0, 'statement': 'if exitShortCondition'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("swinghigh", strategy.long, stop=last_sh)', 'conditions': ['longCondition'], 'statement': 'strategy.entry("swinghigh", strategy.long, stop=last_sh)'}, {'kind': 'entry', 'call': 'strategy.entry("swinglow", strategy.short, stop=last_sl)', 'conditions': ['shortCondition'], 'statement': 'strategy.entry("swinglow", strategy.short, stop=last_sl)'}, {'kind': 'exit', 'call': 'strategy.exit("stoplong", "swinghigh", stop = last_sl )', 'conditions': ['exitLongCondition'], 'statement': 'strategy.exit("stoplong", "swinghigh", stop = last_sl )'}, {'kind': 'exit', 'call': 'strategy.exit("stopshort", "swinglow", stop = last_sh )', 'conditions': ['exitShortCondition'], 'statement': 'strategy.exit("stopshort", "swinglow", stop = last_sh )'}]
    original_pine = '/*backtest\nstart: 2023-08-12 00:00:00\nend: 2023-09-11 00:00:00\nperiod: 2h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=3\nstrategy("Swing Points", overlay=true)\n\n\nleftBars = input(1)\nrightBars=input(1)\nsl = pivotlow(low, leftBars, rightBars)\nsh = pivothigh(high, leftBars, rightBars)\n\nlast_sh=na\nlast_sh:= sh!=0 ? sh : nz(last_sh[1])\n\nlast_sl=na\nlast_sl:= sl!=0 ? sl : nz(last_sl[1])\n\n\nEMA = ema(close,55)\n\nlongCondition = sh and high > EMA\nshortCondition = sl and close < EMA\nexitLongCondition = sl < sh[1]\nexitShortCondition = sh > sl[1]\n\nif longCondition \n    strategy.entry("swinghigh", strategy.long, stop=last_sh)\n    \nif shortCondition \n    strategy.entry("swinglow", strategy.short, stop=last_sl)\n   \nif exitLongCondition\n    strategy.exit("stoplong", "swinghigh", stop = last_sl )\n\nif exitShortCondition\n    strategy.exit("stopshort", "swinglow", stop = last_sh )\n    \nplot(EMA,linewidth = 4)'

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
