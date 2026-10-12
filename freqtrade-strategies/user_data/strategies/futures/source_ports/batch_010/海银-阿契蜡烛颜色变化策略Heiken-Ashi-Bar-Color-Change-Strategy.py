"""Source-faithful deep-assisted port of 海银-阿契蜡烛颜色变化策略Heiken-Ashi-Bar-Color-Change-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_275c88f7(PinePortBase, IStrategy):
    source_file = '海银-阿契蜡烛颜色变化策略Heiken-Ashi-Bar-Color-Change-Strategy.md'
    timeframe = '1d'
    can_short = False
    source_defaults = {}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.entry']
    source_fidelity_notes = []
    pine_assignments = [{'mode': '', 'name': 'haopen', 'op': '=', 'expr': '0.0', 'conditions': []}, {'mode': '', 'name': 'haclose', 'op': '=', 'expr': '((open + high + low + close)/4)', 'conditions': []}, {'mode': '', 'name': 'haopen', 'op': ':=', 'expr': 'na(haopen[1]) ? (open + close)/2 : (haopen[1] + haclose[1]) / 2', 'conditions': []}, {'mode': '', 'name': 'hahigh', 'op': '=', 'expr': 'max(high, max(haopen, haclose))', 'conditions': []}, {'mode': '', 'name': 'halow', 'op': '=', 'expr': 'min(low, min(haopen, haclose))', 'conditions': []}, {'mode': '', 'name': 'hacolor', 'op': '=', 'expr': 'haclose > haopen ? green : red', 'conditions': []}, {'mode': '', 'name': 'turnGreen', 'op': '=', 'expr': 'haclose > haopen and haclose[1] <= haopen[1]', 'conditions': []}, {'mode': '', 'name': 'turnRed', 'op': '=', 'expr': 'haclose <= haopen and haclose[1] > haopen[1]', 'conditions': []}]
    pine_user_functions = []
    pine_controls = []
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("long", true, when = turnGreen)', 'conditions': [], 'statement': 'strategy.entry("long", true, when = turnGreen)'}, {'kind': 'entry', 'call': 'strategy.entry("short", false, when = turnRed)', 'conditions': [], 'statement': 'strategy.entry("short", false, when = turnRed)'}]
    original_pine = '/*backtest\nstart: 2022-10-08 00:00:00\nend: 2023-10-08 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=3\nstrategy("Kozlod - Heikin-Ashi Bar Color Change Strategy", overlay = true)\n\n// \n// author: Kozlod\n// date: 2018-09-03\n// https://www.tradingview.com/u/Kozlod/\n// \n\n// Calculation HA Values \nhaopen   = 0.0\nhaclose  = ((open + high + low + close)/4)\nhaopen  := na(haopen[1]) ? (open + close)/2 : (haopen[1] + haclose[1]) / 2\nhahigh   = max(high, max(haopen, haclose))\nhalow    = min(low,  min(haopen, haclose))\n\n// HA colors\nhacolor =  haclose  > haopen ? green : red\n\n// Signals\nturnGreen = haclose  >  haopen and haclose[1] <= haopen[1]\nturnRed   = haclose  <= haopen and haclose[1]  > haopen[1]\n\n// Plotting\nbgcolor(hacolor)\n\nplotshape(turnGreen, style = shape.arrowup,   location = location.belowbar, color = green)\nplotshape(turnRed,   style = shape.arrowdown, location = location.abovebar, color = red) \n\n// Alerts\nstrategy.entry("long",  true,  when = turnGreen)\nstrategy.entry("short", false, when = turnRed)'

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
