"""Source-faithful deep-assisted port of 带通滤波趋势提取策略Bandpass-Filtering-Trend-Extraction-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_6abff3bd(PinePortBase, IStrategy):
    source_file = '带通滤波趋势提取策略Bandpass-Filtering-Trend-Extraction-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'Length': 20, 'Delta': 0.5, 'Trigger': 0, 'reverse': False}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.entry', 'for ']
    source_fidelity_notes = []
    pine_assignments = [{'mode': '', 'name': 'Length', 'op': '=', 'expr': 'input(20, minval=1)', 'conditions': []}, {'mode': '', 'name': 'Delta', 'op': '=', 'expr': 'input(0.5)', 'conditions': []}, {'mode': '', 'name': 'Trigger', 'op': '=', 'expr': 'input(0)', 'conditions': []}, {'mode': '', 'name': 'reverse', 'op': '=', 'expr': 'input(false, title="Trade reverse")', 'conditions': []}, {'mode': '', 'name': 'xPrice', 'op': '=', 'expr': 'hl2', 'conditions': []}, {'mode': '', 'name': 'beta', 'op': '=', 'expr': 'cos(3.1415 * (360 / Length) / 180)', 'conditions': []}, {'mode': '', 'name': 'gamma', 'op': '=', 'expr': '1 / cos(3.1415 * (720 * Delta / Length) / 180)', 'conditions': []}, {'mode': '', 'name': 'alpha', 'op': '=', 'expr': 'gamma - sqrt(gamma * gamma - 1)', 'conditions': []}, {'mode': '', 'name': 'xBandpassFilter', 'op': '=', 'expr': '0.5 * (1 - alpha) * (xPrice - xPrice[2]) + beta * (1 + alpha) * nz(xBandpassFilter[1]) - alpha * nz(xBandpassFilter[2])', 'conditions': []}, {'mode': '', 'name': 'xMean', 'op': '=', 'expr': 'sma(xBandpassFilter, 2 * Length)', 'conditions': []}, {'mode': '', 'name': 'pos', 'op': '=', 'expr': 'iff(xMean > Trigger, 1, iff(xMean < Trigger, -1, nz(pos[1], 0)))', 'conditions': []}, {'mode': '', 'name': 'possig', 'op': '=', 'expr': 'iff(reverse and pos == 1, -1, iff(reverse and pos == -1, 1, pos))', 'conditions': []}]
    pine_user_functions = []
    pine_controls = [{'indent': 0, 'statement': 'if (possig == 1)'}, {'indent': 0, 'statement': 'if (possig == -1)'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("Long", strategy.long)', 'conditions': ['(possig == 1)'], 'statement': 'strategy.entry("Long", strategy.long)'}, {'kind': 'entry', 'call': 'strategy.entry("Short", strategy.short)', 'conditions': ['(possig == -1)'], 'statement': 'strategy.entry("Short", strategy.short)'}]
    original_pine = '/*backtest\nstart: 2022-12-27 00:00:00\nend: 2024-01-02 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version = 2\n////////////////////////////////////////////////////////////\n//  Copyright by HPotter v1.0 14/12/2016\n// The related article is copyrighted material from Stocks & Commodities Mar 2010\n//\n// You can use in the xPrice any series: Open, High, Low, Close, HL2, HLC3, OHLC4 and ect...\n// You can change long to short in the Input Settings\n// Please, use it only for learning or paper trading. Do not for real trading.\n////////////////////////////////////////////////////////////\nstrategy(title="Extracting The Trend Strategy Backtest")\nLength = input(20, minval=1)\nDelta = input(0.5)\nTrigger = input(0)\nreverse = input(false, title="Trade reverse")\nhline(Trigger, color=blue, linestyle=line)\nxPrice = hl2\nbeta = cos(3.1415 * (360 / Length) / 180)\ngamma = 1 / cos(3.1415 * (720 * Delta / Length) / 180)\nalpha = gamma - sqrt(gamma * gamma - 1)\nxBandpassFilter = 0.5 * (1 - alpha) * (xPrice - xPrice[2]) + beta * (1 + alpha) * nz(xBandpassFilter[1]) - alpha * nz(xBandpassFilter[2])\nxMean = sma(xBandpassFilter, 2 * Length)\npos = iff(xMean > Trigger, 1,\n\t   iff(xMean < Trigger, -1, nz(pos[1], 0))) \npossig = iff(reverse and pos == 1, -1,\n          iff(reverse and pos == -1, 1, pos))\t   \nif (possig == 1) \n    strategy.entry("Long", strategy.long)\nif (possig == -1)\n    strategy.entry("Short", strategy.short)\t   \t    \nbarcolor(possig == -1 ? red: possig == 1 ? green : blue )\nplot(xMean, color=red, title="ExTrend")'

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
