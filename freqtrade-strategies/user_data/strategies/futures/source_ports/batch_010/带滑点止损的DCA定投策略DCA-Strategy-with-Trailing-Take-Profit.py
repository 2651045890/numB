"""Source-faithful deep-assisted port of 带滑点止损的DCA定投策略DCA-Strategy-with-Trailing-Take-Profit.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_d656641e(PinePortBase, IStrategy):
    source_file = '带滑点止损的DCA定投策略DCA-Strategy-with-Trailing-Take-Profit.md'
    timeframe = '1d'
    can_short = False
    source_defaults = {'takeProfitPercent': 0.6, 'trailingPercent': 0.1, 'maxDCAOrders': 10, 'priceDeviationPercent': 1.0}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 10.0
    source_pyramiding = 0
    source_initial_capital = 1000.0
    source_commission_percent = 0.0
    source_features = ['strategy.entry', 'strategy.close', 'var ', 'for ']
    source_fidelity_notes = ['Uses persistent Pine state (var/varip); state is order-dependent and must be evaluated bar-by-bar, not replaced by a vectorized fill-forward approximation.']
    pine_assignments = [{'mode': '', 'name': 'takeProfitPercent', 'op': '=', 'expr': 'input.float(0.6, title="Take Profit (%)", minval=0.1, maxval=5)', 'conditions': []}, {'mode': '', 'name': 'trailingPercent', 'op': '=', 'expr': 'input.float(0.1, title="Trailing Stop (%)", minval=0.05, maxval=1)', 'conditions': []}, {'mode': '', 'name': 'maxDCAOrders', 'op': '=', 'expr': 'input.int(10, title="Max DCA Orders", minval=1, maxval=20)', 'conditions': []}, {'mode': '', 'name': 'priceDeviationPercent', 'op': '=', 'expr': 'input.float(1.0, title="Price Deviation (%)", minval=0.5, maxval=5)', 'conditions': []}, {'mode': 'var', 'name': 'lastBuyPrice', 'op': '=', 'expr': 'na', 'conditions': []}, {'mode': 'var', 'name': 'buyCount', 'op': '=', 'expr': '0', 'conditions': []}, {'mode': 'var', 'name': 'initialBuyPrice', 'op': '=', 'expr': 'na', 'conditions': []}, {'mode': 'var', 'name': 'trailingStopPrice', 'op': '=', 'expr': 'na', 'conditions': []}, {'mode': '', 'name': 'lastBuyPrice', 'op': ':=', 'expr': 'close', 'conditions': ['(buyCount < maxDCAOrders)', '(na(lastBuyPrice) or close < lastBuyPrice * (1 - priceDeviationPercent / 100))']}, {'mode': '', 'name': 'initialBuyPrice', 'op': ':=', 'expr': 'close', 'conditions': ['(buyCount < maxDCAOrders)', '(na(lastBuyPrice) or close < lastBuyPrice * (1 - priceDeviationPercent / 100))', '(na(initialBuyPrice))']}, {'mode': '', 'name': 'trailingStopPrice', 'op': ':=', 'expr': 'close * (1 - trailingPercent / 100)', 'conditions': ['(not na(lastBuyPrice) and close > lastBuyPrice * (1 + takeProfitPercent / 100))', '(na(trailingStopPrice) or close > trailingStopPrice)']}, {'mode': '', 'name': 'lastBuyPrice', 'op': ':=', 'expr': 'na', 'conditions': ['(not na(lastBuyPrice) and close > lastBuyPrice * (1 + takeProfitPercent / 100))', '(close < trailingStopPrice)']}, {'mode': '', 'name': 'trailingStopPrice', 'op': ':=', 'expr': 'na', 'conditions': ['(not na(lastBuyPrice) and close > lastBuyPrice * (1 + takeProfitPercent / 100))', '(close < trailingStopPrice)']}, {'mode': '', 'name': 'buyCount', 'op': ':=', 'expr': '0', 'conditions': ['(not na(lastBuyPrice) and close > lastBuyPrice * (1 + takeProfitPercent / 100))', '(close < trailingStopPrice)']}, {'mode': '', 'name': 'initialBuyPrice', 'op': ':=', 'expr': 'na', 'conditions': ['(not na(lastBuyPrice) and close > lastBuyPrice * (1 + takeProfitPercent / 100))', '(close < trailingStopPrice)']}]
    pine_user_functions = []
    pine_controls = [{'indent': 0, 'statement': 'if (buyCount < maxDCAOrders)'}, {'indent': 4, 'statement': 'if (na(lastBuyPrice) or close < lastBuyPrice * (1 - priceDeviationPercent / 100))'}, {'indent': 8, 'statement': 'if (na(initialBuyPrice))'}, {'indent': 0, 'statement': 'if (not na(lastBuyPrice) and close > lastBuyPrice * (1 + takeProfitPercent / 100))'}, {'indent': 4, 'statement': 'if (na(trailingStopPrice) or close > trailingStopPrice)'}, {'indent': 4, 'statement': 'if (close < trailingStopPrice)'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("Buy", strategy.long)', 'conditions': ['(buyCount < maxDCAOrders)', '(na(lastBuyPrice) or close < lastBuyPrice * (1 - priceDeviationPercent / 100))'], 'statement': 'strategy.entry("Buy", strategy.long)'}, {'kind': 'close', 'call': 'strategy.close("Buy")', 'conditions': ['(not na(lastBuyPrice) and close > lastBuyPrice * (1 + takeProfitPercent / 100))', '(close < trailingStopPrice)'], 'statement': 'strategy.close("Buy")'}]
    original_pine = '/*backtest\nstart: 2023-02-16 00:00:00\nend: 2024-02-22 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This Pine Script™ code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © Stavolt\n\n//@version=5\nstrategy("DCA Strategy with Trailing Take Profit", overlay=true, initial_capital=1000, default_qty_type=strategy.percent_of_equity, default_qty_value=10)\n\n// Correctly using input to define user-configurable parameters\ntakeProfitPercent = input.float(0.6, title="Take Profit (%)", minval=0.1, maxval=5)\ntrailingPercent = input.float(0.1, title="Trailing Stop (%)", minval=0.05, maxval=1)\nmaxDCAOrders = input.int(10, title="Max DCA Orders", minval=1, maxval=20)\npriceDeviationPercent = input.float(1.0, title="Price Deviation (%)", minval=0.5, maxval=5)\n\nvar float lastBuyPrice = na\nvar int buyCount = 0\nvar float initialBuyPrice = na\nvar float trailingStopPrice = na\n\n// Strategy logic here...\n// Note: The detailed logic for buying and selling based on the DCA strategy\n// needs to be tailored to your specific requirements and tested for correctness.\n\nif (buyCount < maxDCAOrders)\n    if (na(lastBuyPrice) or close < lastBuyPrice * (1 - priceDeviationPercent / 100))\n        strategy.entry("Buy", strategy.long)\n        lastBuyPrice := close\n        buyCount += 1\n        if (na(initialBuyPrice))\n            initialBuyPrice := close\n\nif (not na(lastBuyPrice) and close > lastBuyPrice * (1 + takeProfitPercent / 100))\n    if (na(trailingStopPrice) or close > trailingStopPrice)\n        trailingStopPrice := close * (1 - trailingPercent / 100)\n    if (close < trailingStopPrice)\n        strategy.close("Buy")\n        lastBuyPrice := na\n        trailingStopPrice := na\n        buyCount := 0\n        initialBuyPrice := na'

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
