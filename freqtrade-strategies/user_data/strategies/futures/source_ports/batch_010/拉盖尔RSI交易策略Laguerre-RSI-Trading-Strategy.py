"""Source-faithful deep-assisted port of 拉盖尔RSI交易策略Laguerre-RSI-Trading-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_1a9f2960(PinePortBase, IStrategy):
    source_file = '拉盖尔RSI交易策略Laguerre-RSI-Trading-Strategy.md'
    timeframe = '1d'
    can_short = False
    source_defaults = {'src': 'close', 'alpha': 0.2, 'colorchange': False, 'Date1': True, 'FromDay1': 1, 'FromMonth1': 1, 'FromYear1': 2020, 'ToDay1': 1, 'ToMonth1': 1, 'ToYear1': 9999}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.entry', '=>']
    source_fidelity_notes = []
    pine_assignments = [{'mode': '', 'name': 'src', 'op': '=', 'expr': 'input(title="Source", defval=close)', 'conditions': []}, {'mode': '', 'name': 'alpha', 'op': '=', 'expr': 'input(title="Alpha", type=float, minval=0, maxval=1, step=0.1, defval=0.2)', 'conditions': []}, {'mode': '', 'name': 'colorchange', 'op': '=', 'expr': 'input(title="Change Color ?", type=bool, defval=false)', 'conditions': []}, {'mode': '', 'name': 'Date1', 'op': '=', 'expr': 'input(true, title = "=== Date Backtesting ===")', 'conditions': []}, {'mode': '', 'name': 'FromDay1', 'op': '=', 'expr': 'input(defval = 1, title = "From Day", minval = 1, maxval = 31)', 'conditions': []}, {'mode': '', 'name': 'FromMonth1', 'op': '=', 'expr': 'input(defval = 1, title = "From Month", minval = 1, maxval = 12)', 'conditions': []}, {'mode': '', 'name': 'FromYear1', 'op': '=', 'expr': 'input(defval = 2020, title = "From Year", minval = 2017)', 'conditions': []}, {'mode': '', 'name': 'ToDay1', 'op': '=', 'expr': 'input(defval = 1, title = "To Day", minval = 1, maxval = 31)', 'conditions': []}, {'mode': '', 'name': 'ToMonth1', 'op': '=', 'expr': 'input(defval = 1, title = "To Month", minval = 1, maxval = 12)', 'conditions': []}, {'mode': '', 'name': 'ToYear1', 'op': '=', 'expr': 'input(defval = 9999, title = "To Year", minval = 2017)', 'conditions': []}, {'mode': '', 'name': 'start1', 'op': '=', 'expr': 'timestamp(FromYear1, FromMonth1, FromDay1, 00, 00)', 'conditions': []}, {'mode': '', 'name': 'finish1', 'op': '=', 'expr': 'timestamp(ToYear1, ToMonth1, ToDay1, 23, 59)', 'conditions': []}, {'mode': '', 'name': 'gamma', 'op': '=', 'expr': '1-alpha', 'conditions': []}, {'mode': '', 'name': 'L0', 'op': '=', 'expr': '0.0', 'conditions': []}, {'mode': '', 'name': 'L0', 'op': ':=', 'expr': '(1-gamma) * src + gamma * nz(L0[1])', 'conditions': []}, {'mode': '', 'name': 'L1', 'op': '=', 'expr': '0.0', 'conditions': []}, {'mode': '', 'name': 'L1', 'op': ':=', 'expr': '-gamma * L0 + nz(L0[1]) + gamma * nz(L1[1])', 'conditions': []}, {'mode': '', 'name': 'L2', 'op': '=', 'expr': '0.0', 'conditions': []}, {'mode': '', 'name': 'L2', 'op': ':=', 'expr': '-gamma * L1 + nz(L1[1]) + gamma * nz(L2[1])', 'conditions': []}, {'mode': '', 'name': 'L3', 'op': '=', 'expr': '0.0', 'conditions': []}, {'mode': '', 'name': 'L3', 'op': ':=', 'expr': '-gamma * L2 + nz(L2[1]) + gamma * nz(L3[1])', 'conditions': []}, {'mode': '', 'name': 'cu', 'op': '=', 'expr': '(L0>L1 ? L0-L1 : 0) + (L1>L2 ? L1-L2 : 0) + (L2>L3 ? L2-L3 : 0)', 'conditions': []}, {'mode': '', 'name': 'cd', 'op': '=', 'expr': '(L0<L1 ? L1-L0 : 0) + (L1<L2 ? L2-L1 : 0) + (L2<L3 ? L3-L2 : 0)', 'conditions': []}, {'mode': '', 'name': 'temp', 'op': '=', 'expr': 'cu+cd==0 ? -1 : cu+cd', 'conditions': []}, {'mode': '', 'name': 'LaRSI', 'op': '=', 'expr': 'temp==-1 ? 0 : cu/temp', 'conditions': []}, {'mode': '', 'name': 'Color', 'op': '=', 'expr': 'colorchange ? (LaRSI > LaRSI[1] ? green : red) : blue', 'conditions': []}]
    pine_user_functions = [{'name': 'window1', 'args': '', 'body': 'time >= start1 and time <= finish1 ? true : false'}]
    pine_controls = []
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("Long", true, when = window1() and crossover(cu, cd))', 'conditions': [], 'statement': 'strategy.entry("Long", true, when = window1() and crossover(cu, cd))'}, {'kind': 'entry', 'call': 'strategy.entry("Short", false, when = window1() and crossunder(cu, cd))', 'conditions': [], 'statement': 'strategy.entry("Short", false, when = window1() and crossunder(cu, cd))'}]
    original_pine = '/*backtest\nstart: 2022-12-12 00:00:00\nend: 2023-12-18 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This source code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © mertriver1\n// Developer: John EHLERS\n//@version=3\n// Author:Kıvanç Özbilgiç\nstrategy("Laguerre RSI", shorttitle="LaRSI", overlay=false)\nsrc = input(title="Source", defval=close)\nalpha = input(title="Alpha", type=float, minval=0, maxval=1, step=0.1, defval=0.2)\ncolorchange = input(title="Change Color ?", type=bool, defval=false)\n\nDate1      = input(true, title = "=== Date Backtesting ===")\nFromDay1   = input(defval = 1, title = "From Day", minval = 1, maxval = 31)\nFromMonth1 = input(defval = 1, title = "From Month", minval = 1, maxval = 12)\nFromYear1  = input(defval = 2020, title = "From Year", minval = 2017)\n\nToDay1     = input(defval = 1, title = "To Day", minval = 1, maxval = 31)\nToMonth1   = input(defval = 1, title = "To Month", minval = 1, maxval = 12)\nToYear1    = input(defval = 9999, title = "To Year", minval = 2017)\n\nstart1     = timestamp(FromYear1, FromMonth1, FromDay1, 00, 00) \nfinish1    = timestamp(ToYear1, ToMonth1, ToDay1, 23, 59)        \nwindow1()  => time >= start1 and time <= finish1 ? true : false\n\ngamma=1-alpha\nL0 = 0.0\nL0 := (1-gamma) * src + gamma * nz(L0[1])\nL1 = 0.0\nL1 := -gamma * L0 + nz(L0[1]) + gamma * nz(L1[1])\n\nL2 = 0.0\nL2 := -gamma * L1 + nz(L1[1]) + gamma * nz(L2[1])\n\nL3 = 0.0\nL3 := -gamma * L2 + nz(L2[1]) + gamma * nz(L3[1])\n\ncu= (L0>L1 ? L0-L1 : 0) + (L1>L2 ? L1-L2 : 0) + (L2>L3 ? L2-L3 : 0)\n\ncd= (L0<L1 ? L1-L0 : 0) + (L1<L2 ? L2-L1 : 0) + (L2<L3 ? L3-L2 : 0)\n\ntemp= cu+cd==0 ? -1 : cu+cd\nLaRSI=temp==-1 ? 0 : cu/temp\n\nColor = colorchange ? (LaRSI > LaRSI[1] ? green : red) : blue\nplot(100*LaRSI, title="LaRSI", linewidth=2, color=Color, transp=0)\nplot(20,linewidth=1, color=maroon, transp=0)\nplot(80,linewidth=1, color=maroon, transp=0)\n\nstrategy.entry("Long",   true, when = window1() and crossover(cu, cd))\nstrategy.entry("Short", false, when = window1() and crossunder(cu, cd))'

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
