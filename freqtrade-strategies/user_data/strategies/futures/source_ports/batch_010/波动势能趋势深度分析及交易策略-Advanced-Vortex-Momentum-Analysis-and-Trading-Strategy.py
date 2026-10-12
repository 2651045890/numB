"""Source-faithful deep-assisted port of 波动势能趋势深度分析及交易策略-Advanced-Vortex-Momentum-Analysis-and-Trading-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_ad4faa4d(PinePortBase, IStrategy):
    source_file = '波动势能趋势深度分析及交易策略-Advanced-Vortex-Momentum-Analysis-and-Trading-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'length': 14}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.entry']
    source_fidelity_notes = []
    pine_assignments = [{'mode': '', 'name': 'length', 'op': '=', 'expr': 'input.int(14, title="Period", minval=1)', 'conditions': []}, {'mode': '', 'name': 'vmPlus', 'op': '=', 'expr': 'math.abs(high - low[1])', 'conditions': []}, {'mode': '', 'name': 'vmMinus', 'op': '=', 'expr': 'math.abs(low - high[1])', 'conditions': []}, {'mode': '', 'name': 'trueRange', 'op': '=', 'expr': 'math.max(math.max(high - low, math.abs(high - close[1])), math.abs(low - close[1]))', 'conditions': []}, {'mode': '', 'name': 'smoothedVMPlus', 'op': '=', 'expr': 'ta.sma(vmPlus, length)', 'conditions': []}, {'mode': '', 'name': 'smoothedVMMinus', 'op': '=', 'expr': 'ta.sma(vmMinus, length)', 'conditions': []}, {'mode': '', 'name': 'smoothedTrueRange', 'op': '=', 'expr': 'ta.sma(trueRange, length)', 'conditions': []}, {'mode': '', 'name': 'viPlus', 'op': '=', 'expr': 'smoothedVMPlus / smoothedTrueRange', 'conditions': []}, {'mode': '', 'name': 'viMinus', 'op': '=', 'expr': 'smoothedVMMinus / smoothedTrueRange', 'conditions': []}, {'mode': '', 'name': 'bullSignal', 'op': '=', 'expr': 'ta.crossover(viPlus, viMinus) // VI+ pretína VI- smerom nahor', 'conditions': []}, {'mode': '', 'name': 'bearSignal', 'op': '=', 'expr': 'ta.crossunder(viPlus, viMinus) // VI+ pretína VI- smerom nadol', 'conditions': []}]
    pine_user_functions = []
    pine_controls = [{'indent': 0, 'statement': 'if bullSignal'}, {'indent': 0, 'statement': 'if bearSignal'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("Long", strategy.long)', 'conditions': ['bullSignal'], 'statement': 'strategy.entry("Long", strategy.long)'}, {'kind': 'entry', 'call': 'strategy.entry("Short", strategy.short)', 'conditions': ['bearSignal'], 'statement': 'strategy.entry("Short", strategy.short)'}]
    original_pine = '/*backtest\nstart: 2022-02-11 00:00:00\nend: 2025-02-08 08:00:00\nperiod: 1d\nbasePeriod: 1d\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("Vortex Strategy with Signals", shorttitle="VI_Strat", overlay=true)\n\n// Užívateľský vstup\nlength = input.int(14, title="Period", minval=1)\n\n//------------------------------------\n// 1) Výpočet Vortexu\n//------------------------------------\nvmPlus     = math.abs(high - low[1])\nvmMinus    = math.abs(low - high[1])\ntrueRange  = math.max(math.max(high - low, math.abs(high - close[1])), math.abs(low - close[1]))\n\n// SMA vyhladzovanie\nsmoothedVMPlus     = ta.sma(vmPlus,     length)\nsmoothedVMMinus    = ta.sma(vmMinus,    length)\nsmoothedTrueRange  = ta.sma(trueRange,  length)\n\n// Vortex Indikátory\nviPlus  = smoothedVMPlus  / smoothedTrueRange\nviMinus = smoothedVMMinus / smoothedTrueRange\n\n//------------------------------------\n// 2) Plot indikátora\n//------------------------------------\nplot(viPlus,  color=color.green, title="VI+")\nplot(viMinus, color=color.red,   title="VI-")\n\n//------------------------------------\n// 3) Definícia signálov\n//------------------------------------\nbullSignal = ta.crossover(viPlus, viMinus)    // VI+ pretína VI- smerom nahor\nbearSignal = ta.crossunder(viPlus, viMinus)   // VI+ pretína VI- smerom nadol\n\n//------------------------------------\n// 4) Vizualizácia signálov na grafe\n//------------------------------------\nplotshape(bullSignal, \n     title="Bull Signal", \n     style=shape.labelup, \n     location=location.belowbar, \n     color=color.green, \n     text="BUY", \n     textcolor=color.white, \n     size=size.small)\n\nplotshape(bearSignal, \n     title="Bear Signal", \n     style=shape.labeldown, \n     location=location.abovebar, \n     color=color.red, \n     text="SELL", \n     textcolor=color.white, \n     size=size.small)\n\n//------------------------------------\n// 5) STRATEGY LOGIC\n//------------------------------------\nif bullSignal\n    strategy.entry("Long", strategy.long)\n\nif bearSignal\n    strategy.entry("Short", strategy.short)'

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
