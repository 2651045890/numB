"""Source-faithful deep-assisted port of 熊转魔法蜡烛反转策略Bearish-Engulfing-Reversal-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_bfe56e37(PinePortBase, IStrategy):
    source_file = '熊转魔法蜡烛反转策略Bearish-Engulfing-Reversal-Strategy.md'
    timeframe = '1h'
    can_short = True
    source_defaults = {'input_takeprofit': 40, 'input_stoploss': 20, 'input_minsizebody': 2}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.entry', 'strategy.close']
    source_fidelity_notes = []
    pine_assignments = [{'mode': '', 'name': 'input_takeprofit', 'op': '=', 'expr': 'input(40, title="Take Profit pip")', 'conditions': []}, {'mode': '', 'name': 'input_stoploss', 'op': '=', 'expr': 'input(20, title="Stop Loss pip")', 'conditions': []}, {'mode': '', 'name': 'input_minsizebody', 'op': '=', 'expr': 'input(2, title="Min. Size Body pip")', 'conditions': []}, {'mode': '', 'name': 'pos', 'op': '=', 'expr': '0.0', 'conditions': []}, {'mode': '', 'name': 'posprice', 'op': '=', 'expr': '0.0', 'conditions': []}, {'mode': '', 'name': 'posprice', 'op': ':=', 'expr': 'abs( close[1] - open[1]) >= input_minsizebody? close[1] > open[1] ? open > close ? open >= close[1] ? open[1] >= close ? open - close > close[1] - open[1] ? close :nz(posprice[1], 0) :nz(posprice[1], 0) : nz(posprice[1], 0) : nz(posprice[1], 0) : nz(posprice[1], 0): nz(posprice[1], 0)', 'conditions': []}, {'mode': '', 'name': 'pos', 'op': ':=', 'expr': 'iff(posprice > 0, -1, 0)', 'conditions': []}, {'mode': '', 'name': 'posprice', 'op': ':=', 'expr': 'iff(low <= posprice - input_takeprofit and posprice > 0, 0 , nz(posprice, 0))', 'conditions': []}, {'mode': '', 'name': 'posprice', 'op': ':=', 'expr': 'iff(high >= posprice + input_stoploss and posprice > 0, 0 , nz(posprice, 0))', 'conditions': []}]
    pine_user_functions = []
    pine_controls = [{'indent': 0, 'statement': 'if (pos == 0)'}, {'indent': 0, 'statement': 'if (pos == -1)'}]
    pine_orders = [{'kind': 'close_all', 'call': 'strategy.close_all()', 'conditions': ['(pos == 0)'], 'statement': 'strategy.close_all()'}, {'kind': 'entry', 'call': 'strategy.entry("Short", strategy.short)', 'conditions': ['(pos == -1)'], 'statement': 'strategy.entry("Short", strategy.short)'}]
    original_pine = '/*backtest\nstart: 2023-12-04 00:00:00\nend: 2024-01-03 00:00:00\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=3\n////////////////////////////////////////////////////////////\n//  Copyright by HPotter v1.0 30/10/2018\n//\n//    This is a bearish candlestick reversal pattern formed by two candlesticks. \n//    Following an uptrend, the first candlestick is a up candlestick which is \n//    followed by a down candlestick which has a long real body that engulfs or \n//    contains  the real body of the prior bar. The Engulfing pattern is the reverse \n//    of the Harami pattern. \n//\n// WARNING:\n// - For purpose educate only\n// - This script to change bars colors.\n////////////////////////////////////////////////////////////\n\nstrategy(title = "Bearish Engulfing Backtest", overlay = true)\ninput_takeprofit = input(40, title="Take Profit pip")\ninput_stoploss = input(20, title="Stop Loss pip")\ninput_minsizebody = input(2, title="Min. Size Body pip")\nbarcolor(abs(close[1] - open[1]) >= input_minsizebody? close[1] > open[1] ? open > close ? open >= close[1] ? open[1] >= close ? open - close > close[1] - open[1] ? yellow :na :na : na : na : na: na)\npos = 0.0\nbarcolor(nz(pos[1], 0) == -1 ? red: nz(pos[1], 0) == 1 ? green : blue ) \nposprice = 0.0\nposprice := abs( close[1] - open[1]) >= input_minsizebody? close[1] > open[1] ? open > close ? open >= close[1] ? open[1] >= close ? open - close > close[1] - open[1] ? close :nz(posprice[1], 0) :nz(posprice[1], 0) : nz(posprice[1], 0) : nz(posprice[1], 0) : nz(posprice[1], 0): nz(posprice[1], 0)\npos := iff(posprice > 0, -1, 0)\nif (pos == 0) \n    strategy.close_all()\nif (pos == -1)\n    strategy.entry("Short", strategy.short)\t   \t    \nposprice := iff(low <= posprice - input_takeprofit and posprice > 0, 0 ,  nz(posprice, 0))\nposprice := iff(high >= posprice + input_stoploss and posprice > 0, 0 ,  nz(posprice, 0))'

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
