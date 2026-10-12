"""Source-faithful deep-assisted port of 捕捉底部策略Bottom-Catching-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_e2cedba8(PinePortBase, IStrategy):
    source_file = '捕捉底部策略Bottom-Catching-Strategy.md'
    timeframe = '1m'
    can_short = False
    source_defaults = {'showDate': True, 'length': 14}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['request.security', 'strategy.entry', 'strategy.close', 'strategy.position_size']
    source_fidelity_notes = ['Uses request.security / multi-timeframe context; exact parity depends on HTF resampling, gaps and lookahead semantics.', 'Reads broker/strategy state; signals depend on fill timing and cannot be reduced to indicator-only booleans without changing behavior.']
    pine_assignments = [{'mode': '', 'name': 'showDate', 'op': '=', 'expr': "input(defval=true, title='Show Date Range')", 'conditions': []}, {'mode': '', 'name': 'timePeriod', 'op': '=', 'expr': 'time >= timestamp(syminfo.timezone, 2022, 4, 1, 0, 0)', 'conditions': []}, {'mode': '', 'name': 'notInTrade', 'op': '=', 'expr': 'strategy.position_size <= 0', 'conditions': []}, {'mode': '', 'name': 'length', 'op': '=', 'expr': 'input(14)', 'conditions': []}, {'mode': '', 'name': 'vrsi', 'op': '=', 'expr': 'ta.rsi(close, length)', 'conditions': []}, {'mode': '', 'name': 'buyCondition1', 'op': '=', 'expr': 'vrsi < 40', 'conditions': []}, {'mode': '', 'name': 'decrease', 'op': '=', 'expr': '3', 'conditions': []}, {'mode': '', 'name': 'buyCondition2', 'op': '=', 'expr': '(vrsi < vrsi[1] - decrease)', 'conditions': []}, {'mode': '', 'name': 'fastEMA', 'op': '=', 'expr': 'ta.sma(close, 50)', 'conditions': []}, {'mode': '', 'name': 'slowEMA', 'op': '=', 'expr': 'ta.sma(close, 100)', 'conditions': []}, {'mode': '', 'name': 'buyCondition3', 'op': '=', 'expr': 'ta.crossunder(fastEMA, slowEMA)', 'conditions': []}, {'mode': '', 'name': 'sellCondition1', 'op': '=', 'expr': 'vrsi > 65', 'conditions': []}, {'mode': '', 'name': 'EMA9', 'op': '=', 'expr': 'ta.sma(close, 9)', 'conditions': []}, {'mode': '', 'name': 'EMA50', 'op': '=', 'expr': 'ta.sma(close, 50)', 'conditions': []}, {'mode': '', 'name': 'sellCondition2', 'op': '=', 'expr': 'ta.crossover(EMA9, EMA50)', 'conditions': []}]
    pine_user_functions = []
    pine_controls = [{'indent': 0, 'statement': 'if(buyCondition1 and buyCondition2 and buyCondition3 and timePeriod)'}, {'indent': 0, 'statement': 'if(sellCondition1 and sellCondition2 and timePeriod)'}]
    pine_orders = [{'kind': 'entry', 'call': "strategy.entry(id='Long', direction = strategy.long)", 'conditions': [], 'statement': "strategy.entry(id='Long', direction = strategy.long)"}, {'kind': 'close', 'call': "strategy.close(id='Long')", 'conditions': [], 'statement': "strategy.close(id='Long')"}]
    original_pine = '/*backtest\nstart: 2023-11-14 00:00:00\nend: 2023-11-21 00:00:00\nperiod: 1m\nbasePeriod: 1m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This source code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © Coinrule\n\n//@version=5\nstrategy("V3 - Catching the Bottom",\n         overlay=true)\n\nshowDate = input(defval=true, title=\'Show Date Range\')\ntimePeriod = time >= timestamp(syminfo.timezone, 2022, 4, 1, 0, 0)\nnotInTrade = strategy.position_size <= 0\n\n//==================================Buy Conditions============================================\n\n//RSI\nlength = input(14)\nvrsi = ta.rsi(close, length)\n\nbuyCondition1 = vrsi < 40\n\n//RSI decrease\ndecrease = 3\nbuyCondition2 = (vrsi < vrsi[1] - decrease)\n//sellCondition1 = request.security(syminfo.tickerid, "15", buyCondition2)\n\n//EMAs \nfastEMA = ta.sma(close, 50)\nslowEMA = ta.sma(close, 100)\nbuyCondition3 = ta.crossunder(fastEMA, slowEMA)\n//buyCondition2 = request.security(syminfo.tickerid, "15", buyCondition3)\n\nif(buyCondition1 and buyCondition2 and buyCondition3 and timePeriod)\n    strategy.entry(id=\'Long\', direction = strategy.long)\n\n//==================================Sell Conditions============================================\n\nsellCondition1 = vrsi > 65\n\nEMA9 = ta.sma(close, 9)\nEMA50 = ta.sma(close, 50)\nsellCondition2 = ta.crossover(EMA9, EMA50)\n\nif(sellCondition1 and sellCondition2 and timePeriod)\n    strategy.close(id=\'Long\')\n\n//Best on: ETH 5mins (7.59%), BNB 5mins (5.42%), MATIC 30mins (15.61%), XRP 45mins (10.14%) ---> EMA\n//Best on: MATIC 2h (16.09%), XRP 15m (5.25%), SOL 15m (4.28%), AVAX 5m (3.19%)'

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
