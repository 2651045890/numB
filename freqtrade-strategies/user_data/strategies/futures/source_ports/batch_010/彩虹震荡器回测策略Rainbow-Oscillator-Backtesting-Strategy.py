"""Source-faithful deep-assisted port of 彩虹震荡器回测策略Rainbow-Oscillator-Backtesting-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_c34e7041(PinePortBase, IStrategy):
    source_file = '彩虹震荡器回测策略Rainbow-Oscillator-Backtesting-Strategy.md'
    timeframe = '1h'
    can_short = True
    source_defaults = {'Length': 2, 'LengthHHLL': 10, 'reverse': False}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.entry']
    source_fidelity_notes = []
    pine_assignments = [{'mode': '', 'name': 'Length', 'op': '=', 'expr': 'input(2, minval=1)', 'conditions': []}, {'mode': '', 'name': 'LengthHHLL', 'op': '=', 'expr': 'input(10, minval=2, title="HHV/LLV Lookback")', 'conditions': []}, {'mode': '', 'name': 'reverse', 'op': '=', 'expr': 'input(false, title="Trade reverse")', 'conditions': []}, {'mode': '', 'name': 'xMA1', 'op': '=', 'expr': 'sma(close, Length)', 'conditions': []}, {'mode': '', 'name': 'xMA2', 'op': '=', 'expr': 'sma(xMA1, Length)', 'conditions': []}, {'mode': '', 'name': 'xMA3', 'op': '=', 'expr': 'sma(xMA2, Length)', 'conditions': []}, {'mode': '', 'name': 'xMA4', 'op': '=', 'expr': 'sma(xMA3, Length)', 'conditions': []}, {'mode': '', 'name': 'xMA5', 'op': '=', 'expr': 'sma(xMA4, Length)', 'conditions': []}, {'mode': '', 'name': 'xMA6', 'op': '=', 'expr': 'sma(xMA5, Length)', 'conditions': []}, {'mode': '', 'name': 'xMA7', 'op': '=', 'expr': 'sma(xMA6, Length)', 'conditions': []}, {'mode': '', 'name': 'xMA8', 'op': '=', 'expr': 'sma(xMA7, Length)', 'conditions': []}, {'mode': '', 'name': 'xMA9', 'op': '=', 'expr': 'sma(xMA8, Length)', 'conditions': []}, {'mode': '', 'name': 'xMA10', 'op': '=', 'expr': 'sma(xMA9, Length)', 'conditions': []}, {'mode': '', 'name': 'xHH', 'op': '=', 'expr': 'highest(close, LengthHHLL)', 'conditions': []}, {'mode': '', 'name': 'xLL', 'op': '=', 'expr': 'lowest(close, LengthHHLL)', 'conditions': []}, {'mode': '', 'name': 'xHHMAs', 'op': '=', 'expr': 'max(xMA1,max(xMA2,max(xMA3,max(xMA4,max(xMA5,max(xMA6,max(xMA7,max(xMA8,max(xMA9,xMA10)))))))))', 'conditions': []}, {'mode': '', 'name': 'xLLMAs', 'op': '=', 'expr': 'min(xMA1,min(xMA2,min(xMA3,min(xMA4,min(xMA5,min(xMA6,min(xMA7,min(xMA8,min(xMA9,xMA10)))))))))', 'conditions': []}, {'mode': '', 'name': 'xRBO', 'op': '=', 'expr': '100 * ((close - ((xMA1+xMA2+xMA3+xMA4+xMA5+xMA6+xMA7+xMA8+xMA9+xMA10) / 10)) / (xHH - xLL))', 'conditions': []}, {'mode': '', 'name': 'xRB', 'op': '=', 'expr': '100 * ((xHHMAs - xLLMAs) / (xHH - xLL))', 'conditions': []}, {'mode': '', 'name': 'clr', 'op': '=', 'expr': 'iff(xRBO >= 0, green, red)', 'conditions': []}, {'mode': '', 'name': 'pos', 'op': '=', 'expr': 'iff(xRBO > 0, 1, iff(xRBO < 0, -1, nz(pos[1], 0)))', 'conditions': []}, {'mode': '', 'name': 'possig', 'op': '=', 'expr': 'iff(reverse and pos == 1, -1, iff(reverse and pos == -1, 1, pos))', 'conditions': []}, {'mode': '', 'name': 'p0', 'op': '=', 'expr': 'plot(0, color = gray, title="0")', 'conditions': []}, {'mode': '', 'name': 'p1', 'op': '=', 'expr': 'plot(xRB, color=green, title="RB")', 'conditions': []}, {'mode': '', 'name': 'p2', 'op': '=', 'expr': 'plot(-xRB, color=red, title="RB")', 'conditions': []}]
    pine_user_functions = []
    pine_controls = [{'indent': 0, 'statement': 'if (possig == 1)'}, {'indent': 0, 'statement': 'if (possig == -1)'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("Long", strategy.long)', 'conditions': ['(possig == 1)'], 'statement': 'strategy.entry("Long", strategy.long)'}, {'kind': 'entry', 'call': 'strategy.entry("Short", strategy.short)', 'conditions': ['(possig == -1)'], 'statement': 'strategy.entry("Short", strategy.short)'}]
    original_pine = '/*backtest\nstart: 2023-11-25 00:00:00\nend: 2023-12-25 00:00:00\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=2\n////////////////////////////////////////////////////////////\n//  Copyright by HPotter v1.0 18/03/2018\n// Ever since the people concluded that stock market price movements are not \n// random or chaotic, but follow specific trends that can be forecasted, they \n// tried to develop different tools or procedures that could help them identify \n// those trends. And one of those financial indicators is the Rainbow Oscillator \n// Indicator. The Rainbow Oscillator Indicator is relatively new, originally \n// introduced in 1997, and it is used to forecast the changes of trend direction.\n//\n// As market prices go up and down, the oscillator appears as a direction of the \n// trend, but also as the safety of the market and the depth of that trend. As \n// the rainbow grows in width, the current trend gives signs of continuity, and \n// if the value of the oscillator goes beyond 80, the market becomes more and more \n// unstable, being prone to a sudden reversal. When prices move towards the rainbow \n// and the oscillator becomes more and more flat, the market tends to remain more \n// stable and the bandwidth decreases. Still, if the oscillator value goes below 20, \n// the market is again, prone to sudden reversals. The safest bandwidth value where \n// the market is stable is between 20 and 80, in the Rainbow Oscillator indicator value. \n// The depth a certain price has on a chart and into the rainbow can be used to judge \n// the strength of the move.\n//\n// You can change long to short in the Input Settings\n// WARNING:\n//  - For purpose educate only\n//  - This script to change bars colors.\n////////////////////////////////////////////////////////////\nstrategy(title="Rainbow Oscillator Backtest")\nLength = input(2, minval=1)\nLengthHHLL = input(10, minval=2, title="HHV/LLV Lookback")\nreverse = input(false, title="Trade reverse")\nxMA1 = sma(close, Length)\nxMA2 = sma(xMA1, Length)\nxMA3 = sma(xMA2, Length)\nxMA4 = sma(xMA3, Length)\nxMA5 = sma(xMA4, Length)\nxMA6 = sma(xMA5, Length)\nxMA7 = sma(xMA6, Length)\nxMA8 = sma(xMA7, Length)\nxMA9 = sma(xMA8, Length)\nxMA10 = sma(xMA9, Length)\nxHH = highest(close, LengthHHLL)\nxLL = lowest(close, LengthHHLL)\nxHHMAs = max(xMA1,max(xMA2,max(xMA3,max(xMA4,max(xMA5,max(xMA6,max(xMA7,max(xMA8,max(xMA9,xMA10)))))))))\nxLLMAs = min(xMA1,min(xMA2,min(xMA3,min(xMA4,min(xMA5,min(xMA6,min(xMA7,min(xMA8,min(xMA9,xMA10)))))))))\nxRBO = 100 * ((close - ((xMA1+xMA2+xMA3+xMA4+xMA5+xMA6+xMA7+xMA8+xMA9+xMA10) / 10)) / (xHH - xLL))\nxRB = 100 * ((xHHMAs - xLLMAs) / (xHH - xLL))\nclr = iff(xRBO >= 0, green, red)\npos = iff(xRBO > 0, 1,\n       iff(xRBO < 0, -1, nz(pos[1], 0))) \npossig = iff(reverse and pos == 1, -1,\n          iff(reverse and pos == -1, 1, pos))\t   \nif (possig == 1) \n    strategy.entry("Long", strategy.long)\nif (possig == -1)\n    strategy.entry("Short", strategy.short)\t   \t    \nbarcolor(possig == -1 ? red: possig == 1 ? green : blue ) \nplot(xRBO, color=clr, title="RO", style= histogram, linewidth=2)\np0 = plot(0, color = gray, title="0")\np1 = plot(xRB, color=green, title="RB")\np2 = plot(-xRB, color=red, title="RB")\nfill(p1, p0, color=green)\nfill(p2, p0, color=red)'

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
