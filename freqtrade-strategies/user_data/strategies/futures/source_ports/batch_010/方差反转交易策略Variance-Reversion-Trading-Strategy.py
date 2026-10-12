"""Source-faithful deep-assisted port of 方差反转交易策略Variance-Reversion-Trading-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_2e1af6b9(PinePortBase, IStrategy):
    source_file = '方差反转交易策略Variance-Reversion-Trading-Strategy.md'
    timeframe = '1h'
    can_short = False
    source_defaults = {'SL': 0.01, 'CRV': 3, 'len': 30, 'ratio_sma_lookback_len': 20, 'mult': 1.5}
    source_qty_type = 'cash'
    source_qty_value = 10000.0
    source_pyramiding = 1
    source_initial_capital = 10000.0
    source_commission_percent = 0.0
    source_features = ['request.security', 'strategy.exit', 'strategy.entry', 'strategy.position_size']
    source_fidelity_notes = ['Uses request.security / multi-timeframe context; exact parity depends on HTF resampling, gaps and lookahead semantics.', 'Reads broker/strategy state; signals depend on fill timing and cannot be reduced to indicator-only booleans without changing behavior.', 'Uses strategy.exit; stop/limit/profit/loss/trailing arguments have Pine order semantics and may fill intrabar.']
    pine_assignments = [{'mode': '', 'name': 'SL', 'op': '=', 'expr': 'input.float(0.01,step=0.01)', 'conditions': []}, {'mode': '', 'name': 'CRV', 'op': '=', 'expr': 'input.float(3)', 'conditions': []}, {'mode': '', 'name': 'TP', 'op': '=', 'expr': 'SL * CRV', 'conditions': []}, {'mode': '', 'name': 'len', 'op': '=', 'expr': 'input.int(30,"Lookback period in Days",step=10)', 'conditions': []}, {'mode': '', 'name': 'ratio_sma_lookback_len', 'op': '=', 'expr': 'input.int(20,step=10)', 'conditions': []}, {'mode': '', 'name': 'mult', 'op': '=', 'expr': 'input.float(1.5,"Standard Deviation Multiple")', 'conditions': []}, {'mode': '', 'name': 'ratio_sma', 'op': '=', 'expr': 'ta.sma(request.security("USI:PCC","D",close),ratio_sma_lookback_len)', 'conditions': []}, {'mode': '', 'name': 'median', 'op': '=', 'expr': 'ta.sma(ratio_sma,len)', 'conditions': []}, {'mode': '', 'name': 'standartDeviation', 'op': '=', 'expr': 'ta.stdev(ratio_sma,len)', 'conditions': []}, {'mode': '', 'name': 'upperDeviation', 'op': '=', 'expr': 'median + mult*standartDeviation', 'conditions': []}, {'mode': '', 'name': 'lowerDeviation', 'op': '=', 'expr': 'median - mult*standartDeviation', 'conditions': []}, {'mode': '', 'name': 'isBuy', 'op': '=', 'expr': 'ta.crossunder(ratio_sma, upperDeviation)// and close < buyZone', 'conditions': []}, {'mode': '', 'name': 'isCloseShort', 'op': '=', 'expr': '(ratio_sma > median and strategy.position_size < 0)', 'conditions': []}, {'mode': '', 'name': 'isSL', 'op': '=', 'expr': '(strategy.position_avg_price * (1.0 - SL) > low and strategy.position_size > 0) or (strategy.position_avg_price * (1.0 + SL) < high and strategy.position_size < 0)', 'conditions': []}, {'mode': '', 'name': 'isSell', 'op': '=', 'expr': 'ta.crossover(ratio_sma,lowerDeviation)', 'conditions': []}, {'mode': '', 'name': 'isTP', 'op': '=', 'expr': 'strategy.position_avg_price * (1 + TP) < high', 'conditions': []}]
    pine_user_functions = []
    pine_controls = [{'indent': 0, 'statement': 'if(isBuy)'}, {'indent': 0, 'statement': 'if(isCloseShort)'}, {'indent': 0, 'statement': 'if(isSL)'}, {'indent': 0, 'statement': 'if(isTP)'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("Long", strategy.long)', 'conditions': [], 'statement': 'strategy.entry("Long", strategy.long)'}, {'kind': 'exit', 'call': 'strategy.exit("Close Short",limit=close)', 'conditions': [], 'statement': 'strategy.exit("Close Short",limit=close)'}, {'kind': 'exit', 'call': 'strategy.exit("SL",limit=close)', 'conditions': [], 'statement': 'strategy.exit("SL",limit=close)'}, {'kind': 'exit', 'call': 'strategy.exit("TP",limit=close)', 'conditions': [], 'statement': 'strategy.exit("TP",limit=close)'}]
    original_pine = '/*backtest\nstart: 2023-09-30 00:00:00\nend: 2023-10-30 00:00:00\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This source code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © I11L\n\n//@version=5\nstrategy("I11L Long Put/Call Ratio Inversion", overlay=false, pyramiding=1, default_qty_value=10000, initial_capital=10000, default_qty_type=strategy.cash)\n\nSL = input.float(0.01,step=0.01)\nCRV = input.float(3)\nTP = SL * CRV\n\nlen = input.int(30,"Lookback period in Days",step=10)\nratio_sma_lookback_len = input.int(20,step=10)\nmult = input.float(1.5,"Standard Deviation Multiple")\n\nratio_sma = ta.sma(request.security("USI:PCC","D",close),ratio_sma_lookback_len)\n\nmedian = ta.sma(ratio_sma,len)\nstandartDeviation = ta.stdev(ratio_sma,len)\nupperDeviation = median + mult*standartDeviation\nlowerDeviation = median - mult*standartDeviation\n\n\nisBuy = ta.crossunder(ratio_sma, upperDeviation)// and close < buyZone\nisCloseShort = (ratio_sma > median and strategy.position_size < 0)\nisSL = (strategy.position_avg_price * (1.0 - SL) > low and strategy.position_size > 0) or (strategy.position_avg_price * (1.0 + SL) < high and strategy.position_size < 0)\nisSell = ta.crossover(ratio_sma,lowerDeviation) \nisTP = strategy.position_avg_price * (1 + TP) < high\n\nif(isBuy)\n    strategy.entry("Long", strategy.long)\n\nif(isCloseShort)\n    strategy.exit("Close Short",limit=close)\n\nif(isSL)\n    strategy.exit("SL",limit=close)\n\nif(isTP)\n    strategy.exit("TP",limit=close)\n    \nplot(ratio_sma,color=color.white)\nplot(median,color=color.gray)\nplot(upperDeviation,color=color.rgb(0,255,0,0))\nplot(lowerDeviation,color=color.rgb(255,0,0,0))\n\nbgcolor(isBuy?color.rgb(0,255,0,90):na)\nbgcolor(isSell?color.rgb(255,0,0,90):na)'

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
