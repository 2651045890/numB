"""Source-faithful deep-assisted port of 方向趋势指数交易策略Directional-Trend-Index-Trading-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_4ee2eff4(PinePortBase, IStrategy):
    source_file = '方向趋势指数交易策略Directional-Trend-Index-Trading-Strategy.md'
    timeframe = '4h'
    can_short = True
    source_defaults = {'r': 14, 's': 10, 'u': 5, 'OS': 45, 'OB': -45, 'reverse': False}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.entry', 'for ']
    source_fidelity_notes = []
    pine_assignments = [{'mode': '', 'name': 'r', 'op': '=', 'expr': 'input(14, minval=1)', 'conditions': []}, {'mode': '', 'name': 's', 'op': '=', 'expr': 'input(10, minval=1)', 'conditions': []}, {'mode': '', 'name': 'u', 'op': '=', 'expr': 'input(5, minval=1)', 'conditions': []}, {'mode': '', 'name': 'OS', 'op': '=', 'expr': 'input(45, minval=1)', 'conditions': []}, {'mode': '', 'name': 'OB', 'op': '=', 'expr': 'input(-45, maxval=-1)', 'conditions': []}, {'mode': '', 'name': 'reverse', 'op': '=', 'expr': 'input(false, title="Trade reverse")', 'conditions': []}, {'mode': '', 'name': 'xHMU', 'op': '=', 'expr': 'iff(high - high[1] > 0, high - high[1], 0)', 'conditions': []}, {'mode': '', 'name': 'xLMD', 'op': '=', 'expr': 'iff(low - low[1] < 0, -(low - low[1]), 0)', 'conditions': []}, {'mode': '', 'name': 'xPrice', 'op': '=', 'expr': 'xHMU - xLMD', 'conditions': []}, {'mode': '', 'name': 'xPriceAbs', 'op': '=', 'expr': 'abs(xPrice)', 'conditions': []}, {'mode': '', 'name': 'xuXA', 'op': '=', 'expr': 'ema(ema(ema(xPrice, r),s),u)', 'conditions': []}, {'mode': '', 'name': 'xuXAAbs', 'op': '=', 'expr': 'ema(ema(ema(xPriceAbs, r),s),u)', 'conditions': []}, {'mode': '', 'name': 'Val1', 'op': '=', 'expr': '100 * xuXA', 'conditions': []}, {'mode': '', 'name': 'Val2', 'op': '=', 'expr': 'xuXAAbs', 'conditions': []}, {'mode': '', 'name': 'DTI', 'op': '=', 'expr': 'iff(Val2 != 0, Val1 / Val2, 0)', 'conditions': []}, {'mode': '', 'name': 'pos', 'op': '=', 'expr': 'iff(DTI > OS, -1, iff(DTI < OB, 1, nz(pos[1], 0)))', 'conditions': []}, {'mode': '', 'name': 'possig', 'op': '=', 'expr': 'iff(reverse and pos == 1, -1, iff(reverse and pos == -1, 1, pos))', 'conditions': []}]
    pine_user_functions = []
    pine_controls = [{'indent': 0, 'statement': 'if (possig == 1)'}, {'indent': 0, 'statement': 'if (possig == -1)'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("Long", strategy.long)', 'conditions': ['(possig == 1)'], 'statement': 'strategy.entry("Long", strategy.long)'}, {'kind': 'entry', 'call': 'strategy.entry("Short", strategy.short)', 'conditions': ['(possig == -1)'], 'statement': 'strategy.entry("Short", strategy.short)'}]
    original_pine = '/*backtest\nstart: 2023-08-18 00:00:00\nend: 2023-09-17 00:00:00\nperiod: 4h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=2\n////////////////////////////////////////////////////////////\n//  Copyright by HPotter v1.0 29/03/2017\n// This technique was described by William Blau in his book "Momentum,\n// Direction and Divergence" (1995). His book focuses on three key aspects \n// of trading: momentum, direction and divergence. Blau, who was an electrical \n// engineer before becoming a trader, thoroughly examines the relationship between \n// price and momentum in step-by-step examples. From this grounding, he then looks \n// at the deficiencies in other oscillators and introduces some innovative techniques, \n// including a fresh twist on Stochastics. On directional issues, he analyzes the \n// intricacies of ADX and offers a unique approach to help define trending and \n// non-trending periods.\n// Directional Trend Index is an indicator similar to DM+ developed by Welles Wilder. \n// The DM+ (a part of Directional Movement System which includes both DM+ and \n// DM- indicators) indicator helps determine if a security is "trending." William \n// Blau added to it a zeroline, relative to which the indicator is deemed positive or \n// negative. A stable uptrend is a period when the DTI value is positive and rising, a \n// downtrend when it is negative and falling. \n//\n// You can change long to short in the Input Settings\n// Please, use it only for learning or paper trading. Do not for real trading.\n////////////////////////////////////////////////////////////\nstrategy(title="Directional Trend Index (DTI)", shorttitle="DTI")\nr = input(14, minval=1)\ns = input(10, minval=1)\nu = input(5, minval=1)\nOS = input(45, minval=1)\nOB = input(-45, maxval=-1)\nreverse = input(false, title="Trade reverse")\nhline(0, color=green, linestyle=line)\nxHMU = iff(high - high[1] > 0, high - high[1], 0)\nxLMD = iff(low - low[1] < 0, -(low - low[1]), 0)\nxPrice = xHMU - xLMD\nxPriceAbs = abs(xPrice)\nxuXA = ema(ema(ema(xPrice, r),s),u)\nxuXAAbs = ema(ema(ema(xPriceAbs, r),s),u)\nVal1 = 100 * xuXA\nVal2 = xuXAAbs\nDTI = iff(Val2 != 0, Val1 / Val2, 0)\npos = iff(DTI > OS, -1,\n\t     iff(DTI < OB, 1, nz(pos[1], 0))) \npossig = iff(reverse and pos == 1, -1,\n          iff(reverse and pos == -1, 1, pos))\t   \nif (possig == 1) \n    strategy.entry("Long", strategy.long)\nif (possig == -1)\n    strategy.entry("Short", strategy.short)\t   \t    \nbarcolor(possig == -1 ? red: possig == 1 ? green : blue )\nplot(DTI, color=maroon, title="DTI")\nplot(OB, color=blue, title="OB")\nplot(OS, color=red, title="OS")'

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
