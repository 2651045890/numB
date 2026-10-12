"""Source-faithful deep-assisted port of 极化分形效率PFE交易策略Polarized-Fractal-Efficiency-PFE-Trading-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_7c3e38c4(PinePortBase, IStrategy):
    source_file = '极化分形效率PFE交易策略Polarized-Fractal-Efficiency-PFE-Trading-Strategy.md'
    timeframe = '3m'
    can_short = True
    source_defaults = {'Length': 9, 'LengthEMA': 5, 'BuyBand': 50, 'SellBand': -50, 'reverse': False}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.entry']
    source_fidelity_notes = []
    pine_assignments = [{'mode': '', 'name': 'Length', 'op': '=', 'expr': 'input(9, minval=1)', 'conditions': []}, {'mode': '', 'name': 'LengthEMA', 'op': '=', 'expr': 'input(5, minval=1)', 'conditions': []}, {'mode': '', 'name': 'BuyBand', 'op': '=', 'expr': 'input(50, step = 0.1)', 'conditions': []}, {'mode': '', 'name': 'SellBand', 'op': '=', 'expr': 'input(-50, step = 0.1)', 'conditions': []}, {'mode': '', 'name': 'reverse', 'op': '=', 'expr': 'input(false, title="Trade reverse")', 'conditions': []}, {'mode': '', 'name': 'PFE', 'op': '=', 'expr': 'sqrt(pow(close - close[Length], 2) + 100)', 'conditions': []}, {'mode': '', 'name': 'C2C', 'op': '=', 'expr': 'sum(sqrt(pow((close - close[1]), 2) + 1), Length)', 'conditions': []}, {'mode': '', 'name': 'xFracEff', 'op': '=', 'expr': 'iff(close - close[Length] > 0, round((PFE / C2C) * 100) , round(-(PFE / C2C) * 100))', 'conditions': []}, {'mode': '', 'name': 'xEMA', 'op': '=', 'expr': 'ema(xFracEff, LengthEMA)', 'conditions': []}, {'mode': '', 'name': 'pos', 'op': '=', 'expr': 'iff(xEMA < SellBand, -1, iff(xEMA > BuyBand, 1, nz(pos[1], 0)))', 'conditions': []}, {'mode': '', 'name': 'possig', 'op': '=', 'expr': 'iff(reverse and pos == 1, -1, iff(reverse and pos == -1, 1, pos))', 'conditions': []}]
    pine_user_functions = []
    pine_controls = [{'indent': 0, 'statement': 'if (possig == 1)'}, {'indent': 0, 'statement': 'if (possig == -1)'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("Long", strategy.long)', 'conditions': ['(possig == 1)'], 'statement': 'strategy.entry("Long", strategy.long)'}, {'kind': 'entry', 'call': 'strategy.entry("Short", strategy.short)', 'conditions': ['(possig == -1)'], 'statement': 'strategy.entry("Short", strategy.short)'}]
    original_pine = '/*backtest\nstart: 2024-01-07 00:00:00\nend: 2024-01-14 00:00:00\nperiod: 3m\nbasePeriod: 1m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=2\n////////////////////////////////////////////////////////////\n//  Copyright by HPotter v1.0 29/09/2017\n// The Polarized Fractal Efficiency (PFE) indicator measures the efficiency \n// of price movements by drawing on concepts from fractal geometry and chaos \n// theory. The more linear and efficient the price movement, the shorter the \n// distance the prices must travel between two points and thus the more efficient \n// the price movement.\n//\n// You can change long to short in the Input Settings\n// WARNING:\n// - For purpose educate only\n// - This script to change bars colors.\n////////////////////////////////////////////////////////////\nstrategy(title="PFE (Polarized Fractal Efficiency)", shorttitle="PFE (Polarized Fractal Efficiency)")\nLength = input(9, minval=1)\nLengthEMA = input(5, minval=1)\nBuyBand = input(50, step = 0.1)\nSellBand = input(-50, step = 0.1)\nreverse = input(false, title="Trade reverse")\nhline(BuyBand, color=green, linestyle=line, title = "TopBand")\nhline(SellBand, color=red, linestyle=line, title = "LowBand")\nPFE = sqrt(pow(close - close[Length], 2) + 100)\nC2C = sum(sqrt(pow((close - close[1]), 2) + 1), Length)\nxFracEff = iff(close - close[Length] > 0,  round((PFE / C2C) * 100) , round(-(PFE / C2C) * 100))\nxEMA = ema(xFracEff, LengthEMA)\npos = iff(xEMA < SellBand, -1,\n\t   iff(xEMA > BuyBand, 1, nz(pos[1], 0))) \npossig = iff(reverse and pos == 1, -1,\n          iff(reverse and pos == -1, 1, pos))\t   \nif (possig == 1) \n    strategy.entry("Long", strategy.long)\nif (possig == -1)\n    strategy.entry("Short", strategy.short)\t   \t    \nbarcolor(possig == -1 ? red: possig == 1 ? green : blue ) \nplot(xEMA, color=blue, title="PFE")'

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
