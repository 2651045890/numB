"""Source-faithful deep-assisted port of 智能资金指数策略回测Smart-Money-Index-SMI-Strategy-Backtest.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_5861e33d(PinePortBase, IStrategy):
    source_file = '智能资金指数策略回测Smart-Money-Index-SMI-Strategy-Backtest.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'Length': 18, 'reverse': False}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.entry', 'for ']
    source_fidelity_notes = []
    pine_assignments = [{'mode': '', 'name': 'Length', 'op': '=', 'expr': 'input(18, minval=1)', 'conditions': []}, {'mode': '', 'name': 'reverse', 'op': '=', 'expr': 'input(false, title="Trade reverse")', 'conditions': []}, {'mode': '', 'name': 'xcloseH1', 'op': '=', 'expr': 'security(syminfo.tickerid, "60", close[1])', 'conditions': []}, {'mode': '', 'name': 'xopenH1', 'op': '=', 'expr': 'security(syminfo.tickerid, "60", open[1])', 'conditions': []}, {'mode': '', 'name': 'nRes', 'op': '=', 'expr': 'nz(nRes[1], 1) - (open - close) + (xopenH1 - xcloseH1)', 'conditions': []}, {'mode': '', 'name': 'xSmaRes', 'op': '=', 'expr': 'sma(nRes, Length)', 'conditions': []}, {'mode': '', 'name': 'pos', 'op': '=', 'expr': 'iff(xSmaRes > nRes, 1, iff(xSmaRes < nRes, -1, nz(pos[1], 0)))', 'conditions': []}, {'mode': '', 'name': 'possig', 'op': '=', 'expr': 'iff(reverse and pos == 1, -1, iff(reverse and pos == -1, 1, pos))', 'conditions': []}]
    pine_user_functions = []
    pine_controls = [{'indent': 0, 'statement': 'if (possig == 1)'}, {'indent': 0, 'statement': 'if (possig == -1)'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("Long", strategy.long)', 'conditions': ['(possig == 1)'], 'statement': 'strategy.entry("Long", strategy.long)'}, {'kind': 'entry', 'call': 'strategy.entry("Short", strategy.short)', 'conditions': ['(possig == -1)'], 'statement': 'strategy.entry("Short", strategy.short)'}]
    original_pine = '/*backtest\nstart: 2022-09-14 00:00:00\nend: 2023-09-20 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=2\n////////////////////////////////////////////////////////////\n//  Copyright by HPotter v1.0 01/08/2018\n// Attention:\n// If you would to use this indicator on the ES, you should have intraday data 60min in your account.\n//\n// Smart money index (SMI) or smart money flow index is a technical analysis indicator demonstrating investors sentiment. \n// The index was invented and popularized by money manager Don Hays.[1] The indicator is based on intra-day price patterns.\n// The main idea is that the majority of traders (emotional, news-driven) overreact at the beginning of the trading day \n// because of the overnight news and economic data. There is also a lot of buying on market orders and short covering at the opening. \n// Smart, experienced investors start trading closer to the end of the day having the opportunity to evaluate market performance.\n// Therefore, the basic strategy is to bet against the morning price trend and bet with the evening price trend. The SMI may be calculated \n// for many markets and market indices (S&P 500, DJIA, etc.)\n//\n// The SMI sends no clear signal whether the market is bullish or bearish. There are also no fixed absolute or relative readings signaling \n// about the trend. Traders need to look at the SMI dynamics relative to that of the market. If, for example, SMI rises sharply when the \n// market falls, this fact would mean that smart money is buying, and the market is to revert to an uptrend soon. The opposite situation \n// is also true. A rapidly falling SMI during a bullish market means that smart money is selling and that market is to revert to a downtrend \n// soon. The SMI is, therefore, a trend-based indicator.\n// Some analysts use the smart money index to claim that precious metals such as gold will continually maintain value in the future.\n//\n// You can change long to short in the Input Settings\n// WARNING:\n// - For purpose educate only\n// - This script to change bars colors.\n////////////////////////////////////////////////////////////\nstrategy(title="Smart Money Index (SMI) Backtest", shorttitle="Smart Money Index")\nLength = input(18, minval=1)\nreverse = input(false, title="Trade reverse")\nxcloseH1 = security(syminfo.tickerid, "60", close[1])\nxopenH1 =  security(syminfo.tickerid, "60", open[1])\nnRes = nz(nRes[1], 1) - (open - close) + (xopenH1 - xcloseH1)\nxSmaRes = sma(nRes, Length)\npos = iff(xSmaRes > nRes, 1,\n       iff(xSmaRes < nRes, -1, nz(pos[1], 0))) \npossig = iff(reverse and pos == 1, -1,\n          iff(reverse and pos == -1, 1, pos))\t   \nif (possig == 1) \n    strategy.entry("Long", strategy.long)\nif (possig == -1)\n    strategy.entry("Short", strategy.short)\t   \t    \nbarcolor(possig == -1 ? red: possig == 1 ? green : blue ) \nplot(xSmaRes, color=red, title="SMASMI")\nplot(nRes, color=green, title="SMI")'

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
