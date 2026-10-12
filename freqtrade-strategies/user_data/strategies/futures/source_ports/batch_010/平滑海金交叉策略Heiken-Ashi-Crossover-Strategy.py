"""Source-faithful deep-assisted port of 平滑海金交叉策略Heiken-Ashi-Crossover-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_f5c62e10(PinePortBase, IStrategy):
    source_file = '平滑海金交叉策略Heiken-Ashi-Crossover-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'FromMonth': 1, 'FromDay': 1, 'FromYear': 2017, 'ToMonth': 1, 'ToDay': 1, 'ToYear': 9999}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.entry', 'while ', '=>']
    source_fidelity_notes = []
    pine_assignments = [{'mode': '', 'name': 'FromMonth', 'op': '=', 'expr': 'input(defval = 1, title = "From Month", minval = 1)', 'conditions': []}, {'mode': '', 'name': 'FromDay', 'op': '=', 'expr': 'input(defval = 1, title = "From Day", minval = 1)', 'conditions': []}, {'mode': '', 'name': 'FromYear', 'op': '=', 'expr': 'input(defval = 2017, title = "From Year", minval = 1998)', 'conditions': []}, {'mode': '', 'name': 'ToMonth', 'op': '=', 'expr': 'input(defval = 1, title = "To Month", minval = 1)', 'conditions': []}, {'mode': '', 'name': 'ToDay', 'op': '=', 'expr': 'input(defval = 1, title = "To Day", minval = 1)', 'conditions': []}, {'mode': '', 'name': 'ToYear', 'op': '=', 'expr': 'input(defval = 9999, title = "To Year", minval = 1998)', 'conditions': []}, {'mode': '', 'name': 'haclose', 'op': '=', 'expr': '((open + high + low + close)/4)//[smoothing]', 'conditions': []}, {'mode': '', 'name': 'haopen', 'op': '=', 'expr': 'na(haopen[1]) ? (open + close)/2 : (haopen[1] + haclose[1]) / 2', 'conditions': []}]
    pine_user_functions = [{'name': 'heikUpColor', 'args': '', 'body': 'haclose > haopen'}, {'name': 'heikDownColor', 'args': '', 'body': 'haclose <= haopen'}]
    pine_controls = [{'indent': 0, 'statement': 'if (heikUpColor() )'}, {'indent': 0, 'statement': 'if (heikDownColor())'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("LONG", strategy.long, comment="LONG")', 'conditions': ['(heikUpColor() )'], 'statement': 'strategy.entry("LONG", strategy.long, comment="LONG")'}, {'kind': 'entry', 'call': 'strategy.entry("SHORT", strategy.short, comment="SHORT")', 'conditions': ['(heikDownColor())'], 'statement': 'strategy.entry("SHORT", strategy.short, comment="SHORT")'}]
    original_pine = '/*backtest\nstart: 2022-12-06 00:00:00\nend: 2023-12-12 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=2\nstrategy("Heikin-Ashi Strategy", overlay=true)\n\n// Plots Color Of Heikin-Ashi Bars while Viewing Candlestics or Bars\n//Works on Candlesticks and OHLC Bars - Does now work on Heikin-Ashi bars - But I have verified its accuracy\n// Created By User ChrisMoody 1-30-2014 with help from Alex in Tech Support\n\n// === BACKTEST RANGE ===\nFromMonth = input(defval = 1, title = "From Month", minval = 1)\nFromDay   = input(defval = 1, title = "From Day", minval = 1)\nFromYear  = input(defval = 2017, title = "From Year", minval = 1998)\nToMonth   = input(defval = 1, title = "To Month", minval = 1)\nToDay     = input(defval = 1, title = "To Day", minval = 1)\nToYear    = input(defval = 9999, title = "To Year", minval = 1998)\n\n\nhaclose = ((open + high + low + close)/4)//[smoothing]\nhaopen = na(haopen[1]) ? (open + close)/2 : (haopen[1] + haclose[1]) / 2\n\nheikUpColor() => haclose > haopen\nheikDownColor() => haclose <= haopen\n\nbarcolor(heikUpColor() ? aqua: heikDownColor() ? red : na)\n\n\nif (heikUpColor() )\n    strategy.entry("LONG", strategy.long, comment="LONG")\n    \nif (heikDownColor())\n    strategy.entry("SHORT", strategy.short, comment="SHORT")\n\n\n//plot(pos, title="pos", style=line, linewidth=1, color=red )'

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
