"""Source-faithful deep-assisted port of 搏浪者策略Surf-Rider-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_ab5f87a2(PinePortBase, IStrategy):
    source_file = '搏浪者策略Surf-Rider-Strategy.md'
    timeframe = '1h'
    can_short = True
    source_defaults = {'Length': 14, 'KSmoothing': 1, 'DLength': 3, 'Level': 50, 'r': 32, 's': 12, 'reverse': False}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.entry', 'strategy.close', 'for ', '=>']
    source_fidelity_notes = []
    pine_assignments = [{'mode': '', 'name': 'vFast', 'op': '=', 'expr': 'sma(stoch(close, high, low, Length), KSmoothing)', 'conditions': []}, {'mode': '', 'name': 'vSlow', 'op': '=', 'expr': 'sma(vFast, DLength)', 'conditions': []}, {'mode': '', 'name': 'pos', 'op': '=', 'expr': '0.0', 'conditions': []}, {'mode': '', 'name': 'pos', 'op': ':=', 'expr': 'iff(close[2] < close[1] and close > close[1] and vFast < vSlow and vFast > Level, 1, iff(close[2] > close[1] and close < close[1] and vFast > vSlow and vFast < Level, -1, nz(pos[1], 0)))', 'conditions': []}, {'mode': '', 'name': 'pos', 'op': '=', 'expr': '0', 'conditions': []}, {'mode': '', 'name': 'xCO', 'op': '=', 'expr': 'close - open', 'conditions': []}, {'mode': '', 'name': 'xHL', 'op': '=', 'expr': 'high - low', 'conditions': []}, {'mode': '', 'name': 'xEMA', 'op': '=', 'expr': 'ema(ema(xCO, r), s)', 'conditions': []}, {'mode': '', 'name': 'xvEMA', 'op': '=', 'expr': 'ema(ema(xHL, r), s)', 'conditions': []}, {'mode': '', 'name': 'nRes', 'op': '=', 'expr': '100 * (xEMA / xvEMA)', 'conditions': []}, {'mode': '', 'name': 'pos', 'op': ':=', 'expr': 'iff(nRes > 0, 1, iff(nRes <= 0, -1, nz(pos[1], 0)))', 'conditions': []}, {'mode': '', 'name': 'Length', 'op': '=', 'expr': 'input(14, minval=1)', 'conditions': []}, {'mode': '', 'name': 'KSmoothing', 'op': '=', 'expr': 'input(1, minval=1)', 'conditions': []}, {'mode': '', 'name': 'DLength', 'op': '=', 'expr': 'input(3, minval=1)', 'conditions': []}, {'mode': '', 'name': 'Level', 'op': '=', 'expr': 'input(50, minval=1)', 'conditions': []}, {'mode': '', 'name': 'r', 'op': '=', 'expr': 'input(32, minval=1)', 'conditions': []}, {'mode': '', 'name': 's', 'op': '=', 'expr': 'input(12, minval=1)', 'conditions': []}, {'mode': '', 'name': 'reverse', 'op': '=', 'expr': 'input(false, title="Trade reverse")', 'conditions': []}, {'mode': '', 'name': 'posReversal123', 'op': '=', 'expr': 'Reversal123(Length, KSmoothing, DLength, Level)', 'conditions': []}, {'mode': '', 'name': 'posECO', 'op': '=', 'expr': 'ECO(r,s)', 'conditions': []}, {'mode': '', 'name': 'pos', 'op': '=', 'expr': 'iff(posReversal123 == 1 and posECO == 1 , 1, iff(posReversal123 == -1 and posECO == -1, -1, 0))', 'conditions': []}, {'mode': '', 'name': 'possig', 'op': '=', 'expr': 'iff(reverse and pos == 1, -1, iff(reverse and pos == -1 , 1, pos))', 'conditions': []}]
    pine_user_functions = [{'name': 'Reversal123', 'args': 'Length, KSmoothing, DLength, Level', 'body': ''}, {'name': 'ECO', 'args': 'r,s', 'body': ''}]
    pine_controls = [{'indent': 0, 'statement': 'if (possig == 1)'}, {'indent': 0, 'statement': 'if (possig == -1)'}, {'indent': 0, 'statement': 'if (possig == 0)'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("Long", strategy.long)', 'conditions': ['(possig == 1)'], 'statement': 'strategy.entry("Long", strategy.long)'}, {'kind': 'entry', 'call': 'strategy.entry("Short", strategy.short)', 'conditions': ['(possig == -1)'], 'statement': 'strategy.entry("Short", strategy.short)'}, {'kind': 'close_all', 'call': 'strategy.close_all()', 'conditions': ['(possig == 0)'], 'statement': 'strategy.close_all()'}]
    original_pine = '/*backtest\nstart: 2023-09-16 00:00:00\nend: 2023-10-16 00:00:00\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=4\n////////////////////////////////////////////////////////////\n//  Copyright by HPotter v1.0 16/04/2020\n// This is combo strategies for get a cumulative signal. \n//\n// First strategy\n// This System was created from the Book "How I Tripled My Money In The \n// Futures Market" by Ulf Jensen, Page 183. This is reverse type of strategies.\n// The strategy buys at market, if close price is higher than the previous close \n// during 2 days and the meaning of 9-days Stochastic Slow Oscillator is lower than 50. \n// The strategy sells at market, if close price is lower than the previous close price \n// during 2 days and the meaning of 9-days Stochastic Fast Oscillator is higher than 50.\n//\n// Second strategy\n// We call this one the ECO for short, but it will be listed on the indicator list \n// at W. Blau’s Ergodic Candlestick Oscillator. The ECO is a momentum indicator. \n// It is based on candlestick bars, and takes into account the size and direction \n// of the candlestick "body". We have found it to be a very good momentum indicator, \n// and especially smooth, because it is unaffected by gaps in price, unlike many other \n// momentum indicators.\n// We like to use this indicator as an additional trend confirmation tool, or as an \n// alternate trend definition tool, in place of a weekly indicator. The simplest way \n// of using the indicator is simply to define the trend based on which side of the "0" \n// line the indicator is located on. If the indicator is above "0", then the trend is up. \n// If the indicator is below "0" then the trend is down. You can add an additional \n// qualifier by noting the "slope" of the indicator, and the crossing points of the slow \n// and fast lines. Some like to use the slope alone to define trend direction. If the \n// lines are sloping upward, the trend is up. Alternately, if the lines are sloping \n// downward, the trend is down. In this view, the point where the lines "cross" is the \n// point where the trend changes.\n// When the ECO is below the "0" line, the trend is down, and we are qualified only to \n// sell on new short signals from the Hi-Lo Activator. In other words, when the ECO is \n// above 0, we are not allowed to take short signals, and when the ECO is below 0, we \n// are not allowed to take long signals. \n//\n// WARNING:\n// - For purpose educate only\n// - This script to change bars colors.\n////////////////////////////////////////////////////////////\nReversal123(Length, KSmoothing, DLength, Level) =>\n    vFast = sma(stoch(close, high, low, Length), KSmoothing) \n    vSlow = sma(vFast, DLength)\n    pos = 0.0\n    pos := iff(close[2] < close[1] and close > close[1] and vFast < vSlow and vFast > Level, 1,\n\t         iff(close[2] > close[1] and close < close[1] and vFast > vSlow and vFast < Level, -1, nz(pos[1], 0))) \n\tpos\n\nECO(r,s) =>\n    pos = 0\n    xCO = close - open\n    xHL = high - low\n    xEMA = ema(ema(xCO, r), s)\n    xvEMA = ema(ema(xHL, r), s)\n    nRes = 100 * (xEMA / xvEMA)\n    pos := iff(nRes > 0, 1,\n\t         iff(nRes <= 0, -1, nz(pos[1], 0))) \n    pos\n\nstrategy(title="Combo Backtest 123 Reversal & ECO Strategy", shorttitle="Combo", overlay = true)\nLength = input(14, minval=1)\nKSmoothing = input(1, minval=1)\nDLength = input(3, minval=1)\nLevel = input(50, minval=1)\n//-------------------------\nr = input(32, minval=1)\ns = input(12, minval=1)\nreverse = input(false, title="Trade reverse")\nposReversal123 = Reversal123(Length, KSmoothing, DLength, Level)\nposECO = ECO(r,s)\npos = iff(posReversal123 == 1 and posECO == 1 , 1,\n\t   iff(posReversal123 == -1 and posECO == -1, -1, 0)) \npossig = iff(reverse and pos == 1, -1,\n          iff(reverse and pos == -1 , 1, pos))\t   \nif (possig == 1) \n    strategy.entry("Long", strategy.long)\nif (possig == -1)\n    strategy.entry("Short", strategy.short)\t \nif (possig == 0) \n    strategy.close_all()\nbarcolor(possig == -1 ? #b50404: possig == 1 ? #079605 : #0536b3 )'

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
