"""Source-faithful deep-assisted port of 枢轴点预测震荡指标回测策略Pivot-Point-Forecast-Oscillator-Backtesting-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_70fb7976(PinePortBase, IStrategy):
    source_file = '枢轴点预测震荡指标回测策略Pivot-Point-Forecast-Oscillator-Backtesting-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'Length': 14, 'Offset': 0, 'reverse': False}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.entry']
    source_fidelity_notes = []
    pine_assignments = [{'mode': '', 'name': 'Length', 'op': '=', 'expr': 'input(14, minval=1)', 'conditions': []}, {'mode': '', 'name': 'Offset', 'op': '=', 'expr': 'input(0)', 'conditions': []}, {'mode': '', 'name': 'reverse', 'op': '=', 'expr': 'input(false, title="Trade reverse")', 'conditions': []}, {'mode': '', 'name': 'xLG', 'op': '=', 'expr': 'linreg(close, Length, Offset)', 'conditions': []}, {'mode': '', 'name': 'xCFO', 'op': '=', 'expr': '((close -xLG) * 100) / close', 'conditions': []}, {'mode': '', 'name': 'pos', 'op': '=', 'expr': 'iff(xCFO > 0, 1, iff(xCFO < 0, -1, nz(pos[1], 0)))', 'conditions': []}, {'mode': '', 'name': 'possig', 'op': '=', 'expr': 'iff(reverse and pos == 1, -1, iff(reverse and pos == -1, 1, pos))', 'conditions': []}]
    pine_user_functions = []
    pine_controls = [{'indent': 0, 'statement': 'if (possig == 1)'}, {'indent': 0, 'statement': 'if (possig == -1)'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("Long", strategy.long)', 'conditions': ['(possig == 1)'], 'statement': 'strategy.entry("Long", strategy.long)'}, {'kind': 'entry', 'call': 'strategy.entry("Short", strategy.short)', 'conditions': ['(possig == -1)'], 'statement': 'strategy.entry("Short", strategy.short)'}]
    original_pine = '/*backtest\nstart: 2022-12-13 00:00:00\nend: 2023-12-19 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=2\n////////////////////////////////////////////////////////////\n//  Copyright by HPotter v1.0 19/03/2018\n// The Chande Forecast Oscillator developed by Tushar Chande The Forecast \n// Oscillator plots the percentage difference between the closing price and \n// the n-period linear regression forecasted price. The oscillator is above \n// zero when the forecast price is greater than the closing price and less \n// than zero if it is below.\n//\n// You can change long to short in the Input Settings\n// WARNING:\n//  - For purpose educate only\n//  - This script to change bars colors.\n////////////////////////////////////////////////////////////\nstrategy(title="Chande Forecast Oscillator Backtest", shorttitle="CFO")\nLength = input(14, minval=1)\nOffset = input(0)\nreverse = input(false, title="Trade reverse")\nhline(0, color=black, linestyle=line)\nxLG = linreg(close, Length, Offset)\nxCFO = ((close -xLG) * 100) / close\npos = iff(xCFO > 0, 1,\n       iff(xCFO < 0, -1, nz(pos[1], 0))) \npossig = iff(reverse and pos == 1, -1,\n          iff(reverse and pos == -1, 1, pos))\t   \nif (possig == 1) \n    strategy.entry("Long", strategy.long)\nif (possig == -1)\n    strategy.entry("Short", strategy.short)\t   \t    \nbarcolor(possig == -1 ? red: possig == 1 ? green : blue ) \nplot(xCFO, color=red, title="CFO")'

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
