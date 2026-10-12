"""Source-faithful deep-assisted port of 影子交易策略Shadow-Trading-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_6a7fce93(PinePortBase, IStrategy):
    source_file = '影子交易策略Shadow-Trading-Strategy.md'
    timeframe = '10m'
    can_short = True
    source_defaults = {'size': 1, 'scarto': 0.0018, 'min': 0.001, 'offset': 0.0, 'monthBegin': 1, 'yearBegin': 2013, 'Target': 20, 'Stop': 70, 'Trailing': 0}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.exit', 'strategy.entry', 'strategy.close', 'strategy.opentrades']
    source_fidelity_notes = ['Reads broker/strategy state; signals depend on fill timing and cannot be reduced to indicator-only booleans without changing behavior.', 'Uses strategy.exit; stop/limit/profit/loss/trailing arguments have Pine order semantics and may fill intrabar.']
    pine_assignments = [{'mode': '', 'name': 'size', 'op': '=', 'expr': 'input(1,type=float)', 'conditions': []}, {'mode': '', 'name': 'pinnaL', 'op': '=', 'expr': 'abs(high - close)', 'conditions': []}, {'mode': '', 'name': 'pinnaS', 'op': '=', 'expr': 'abs(low-close)', 'conditions': []}, {'mode': '', 'name': 'scarto', 'op': '=', 'expr': 'input(title="Tail Tollerance", type=float, defval=0.0018)', 'conditions': []}, {'mode': '', 'name': 'corpo', 'op': '=', 'expr': 'abs(close - open)', 'conditions': []}, {'mode': '', 'name': 'dim', 'op': '=', 'expr': 'abs(high-low)', 'conditions': []}, {'mode': '', 'name': 'min', 'op': '=', 'expr': 'input(0.001)', 'conditions': []}, {'mode': '', 'name': 'shortE', 'op': '=', 'expr': '(open + dim)', 'conditions': []}, {'mode': '', 'name': 'longE', 'op': '=', 'expr': '(open - dim)', 'conditions': []}, {'mode': '', 'name': 'longcond', 'op': '=', 'expr': '(dim > min) and (close > open) and (pinnaL > (corpo*size)) and (open-low<scarto)', 'conditions': []}, {'mode': '', 'name': 'minimo', 'op': '=', 'expr': 'low+scarto', 'conditions': []}, {'mode': '', 'name': 'massimo', 'op': '=', 'expr': 'high+scarto', 'conditions': []}, {'mode': '', 'name': 'shortcond', 'op': '=', 'expr': '(dim > min) and(close < open) and (pinnaS > (corpo*size)) and (high-open<scarto)', 'conditions': []}, {'mode': '', 'name': 'ss', 'op': '=', 'expr': 'shortcond ? close : na', 'conditions': []}, {'mode': '', 'name': 'll', 'op': '=', 'expr': 'longcond ? close : na', 'conditions': []}, {'mode': '', 'name': 'offset', 'op': '=', 'expr': 'input(0.00000)', 'conditions': []}, {'mode': '', 'name': 'DayClose', 'op': '=', 'expr': '2', 'conditions': []}, {'mode': '', 'name': 'closup', 'op': '=', 'expr': 'barssince(change(strategy.opentrades)>0) >= DayClose', 'conditions': []}, {'mode': '', 'name': 'longCondition', 'op': '=', 'expr': '(close > open) and (pinnaL > (corpo*size)) and (open-low<scarto)', 'conditions': []}, {'mode': '', 'name': 'crossFlag', 'op': '=', 'expr': 'longcond ? 1 : 0', 'conditions': []}, {'mode': '', 'name': 'monthBegin', 'op': '=', 'expr': 'input(1,maxval = 12)', 'conditions': []}, {'mode': '', 'name': 'yearBegin', 'op': '=', 'expr': 'input(2013, maxval= 2015, minval=2000)', 'conditions': []}, {'mode': '', 'name': 'shortCondition', 'op': '=', 'expr': '(close < open) and (pinnaS > (corpo*size)) and (high-open<scarto)', 'conditions': []}, {'mode': '', 'name': 'Target', 'op': '=', 'expr': 'input(20)', 'conditions': []}, {'mode': '', 'name': 'Stop', 'op': '=', 'expr': 'input(70) //- 2', 'conditions': []}, {'mode': '', 'name': 'Trailing', 'op': '=', 'expr': 'input(0)', 'conditions': []}, {'mode': '', 'name': 'CQ', 'op': '=', 'expr': '100', 'conditions': []}, {'mode': '', 'name': 'TPP', 'op': '=', 'expr': '(Target > 0) ? Target*10: na', 'conditions': []}, {'mode': '', 'name': 'SLP', 'op': '=', 'expr': '(Stop > 0) ? Stop*10 : na', 'conditions': []}, {'mode': '', 'name': 'TSP', 'op': '=', 'expr': '(Trailing > 0) ? Trailing : na', 'conditions': []}]
    pine_user_functions = []
    pine_controls = [{'indent': 0, 'statement': 'if(month(time)>monthBegin and year(time) >yearBegin)'}, {'indent': 4, 'statement': 'if (longcond)'}, {'indent': 0, 'statement': 'if(month(time)>monthBegin and year(time) >yearBegin)'}, {'indent': 4, 'statement': 'if (shortcond)'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("short", strategy.short, stop = low - offset)', 'conditions': ['(longcond)'], 'statement': 'strategy.entry("short", strategy.short, stop = low - offset)'}, {'kind': 'entry', 'call': 'strategy.entry("long", strategy.long, stop = high + offset)', 'conditions': ['(shortcond)'], 'statement': 'strategy.entry("long", strategy.long, stop = high + offset)'}, {'kind': 'exit', 'call': 'strategy.exit("Close Long", "long", qty_percent=CQ, profit=TPP, loss=SLP, trail_points=TSP)', 'conditions': [], 'statement': 'strategy.exit("Close Long", "long", qty_percent=CQ, profit=TPP, loss=SLP, trail_points=TSP)'}, {'kind': 'exit', 'call': 'strategy.exit("Close Short", "short", qty_percent=CQ, profit=TPP, loss=SLP, trail_points=TSP)', 'conditions': [], 'statement': 'strategy.exit("Close Short", "short", qty_percent=CQ, profit=TPP, loss=SLP, trail_points=TSP)'}]
    original_pine = '/*backtest\nstart: 2023-10-01 00:00:00\nend: 2023-10-11 23:59:59\nperiod: 10m\nbasePeriod: 1m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=2\nstrategy("Shadow Trading", overlay=true)\n\nsize = input(1,type=float)\npinnaL = abs(high - close) \npinnaS = abs(low-close)\nscarto = input(title="Tail Tollerance", type=float, defval=0.0018)\ncorpo = abs(close - open)\ndim = abs(high-low)\nmin = input(0.001)\nshortE = (open + dim)\n\nlongE = (open - dim)\nbarcolor(dim > min and (close > open) and (pinnaL > (corpo*size)) and (open-low<scarto) ? navy : na)\n\nlongcond = (dim > min) and (close > open) and (pinnaL > (corpo*size)) and (open-low<scarto)\nminimo=low+scarto\nmassimo=high+scarto\nbarcolor( dim > min and(close < open) and (pinnaS > (corpo*size)) and (high-open<scarto) ? orange: na)\nshortcond = (dim > min) and(close < open) and (pinnaS > (corpo*size)) and (high-open<scarto)\n//plot(shortE)\n//plot(longE)\n//plot(open)\nss= shortcond ? close : na\nll=longcond ? close : na\noffset= input(0.00000)\n\nDayClose = 2\nclosup = barssince(change(strategy.opentrades)>0)  >= DayClose \n\nlongCondition = (close > open) and (pinnaL > (corpo*size)) and (open-low<scarto) \n\ncrossFlag = longcond ? 1 : 0\nmonthBegin = input(1,maxval = 12)\nyearBegin = input(2013, maxval= 2015, minval=2000)\n\nif(month(time)>monthBegin and year(time) >yearBegin)\n    if (longcond)\n        strategy.entry("short", strategy.short, stop = low - offset)   \n//strategy.close("short", when = closup)\nshortCondition = (close < open) and (pinnaS > (corpo*size)) and (high-open<scarto)\nif(month(time)>monthBegin and year(time) >yearBegin)\n    if (shortcond)\n        strategy.entry("long", strategy.long, stop = high + offset)\n//strategy.close("long", when = closup)\n\nTarget =  input(20) \nStop = input(70) //- 2\nTrailing = input(0) \nCQ = 100\n\nTPP = (Target > 0) ? Target*10: na\nSLP = (Stop > 0) ? Stop*10 : na\nTSP = (Trailing > 0) ? Trailing : na\n\nstrategy.exit("Close Long", "long", qty_percent=CQ, profit=TPP, loss=SLP, trail_points=TSP)\nstrategy.exit("Close Short", "short", qty_percent=CQ, profit=TPP, loss=SLP, trail_points=TSP)'

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
