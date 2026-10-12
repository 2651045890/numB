"""Source-faithful deep-assisted port of 指数移动平均线交叉量化交易策略-Exponential-Moving-Average-Crossover-Quantitative-Trading-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_f01273a3(PinePortBase, IStrategy):
    source_file = '指数移动平均线交叉量化交易策略-Exponential-Moving-Average-Crossover-Quantitative-Trading-Strategy.md'
    timeframe = '1h'
    can_short = True
    source_defaults = {'emaLength1': 5, 'emaLength2': 10}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 100.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.entry', 'strategy.close', 'strategy.position_size', 'for ', 'label.']
    source_fidelity_notes = ['Reads broker/strategy state; signals depend on fill timing and cannot be reduced to indicator-only booleans without changing behavior.', 'Drawing/table calls are display-only unless their IDs/state are later read; preserved in source map but excluded from trade signal calculation where non-causal.']
    pine_assignments = [{'mode': '', 'name': 'emaLength1', 'op': '=', 'expr': 'input.int(title="EMA #1 Length", defval=5)', 'conditions': []}, {'mode': '', 'name': 'emaLength2', 'op': '=', 'expr': 'input.int(title="EMA #2 Length", defval=10)', 'conditions': []}, {'mode': '', 'name': 'ema1', 'op': '=', 'expr': 'ta.ema(close, emaLength1)', 'conditions': []}, {'mode': '', 'name': 'ema2', 'op': '=', 'expr': 'ta.ema(close, emaLength2)', 'conditions': []}, {'mode': '', 'name': 'crossOver', 'op': '=', 'expr': 'ta.crossover(ema1, ema2)', 'conditions': []}, {'mode': '', 'name': 'crossUnder', 'op': '=', 'expr': 'ta.crossunder(ema1, ema2)', 'conditions': []}, {'mode': '', 'name': 'cross', 'op': '=', 'expr': 'crossOver or crossUnder', 'conditions': []}, {'mode': '', 'name': 'crossPrice', 'op': '=', 'expr': 'cross ? close : na', 'conditions': []}, {'mode': '', 'name': 'highestPrice', 'op': '=', 'expr': 'crossOver', 'conditions': []}, {'mode': '', 'name': 'highestPrice', 'op': ':=', 'expr': 'false', 'conditions': ['crossPrice <= close[i]']}, {'mode': '', 'name': 'lowestPrice', 'op': '=', 'expr': 'crossUnder', 'conditions': []}, {'mode': '', 'name': 'lowestPrice', 'op': ':=', 'expr': 'false', 'conditions': ['crossPrice >= close[i]']}, {'mode': '', 'name': 'highestEmaPrice', 'op': '=', 'expr': 'ema1 > ema2 ? ema1 : ema2', 'conditions': ['cross']}]
    pine_user_functions = []
    pine_controls = [{'indent': 0, 'statement': 'for i = 1 to 10'}, {'indent': 4, 'statement': 'if crossPrice <= close[i]'}, {'indent': 0, 'statement': 'for i = 1 to 10'}, {'indent': 4, 'statement': 'if crossPrice >= close[i]'}, {'indent': 0, 'statement': 'if cross'}, {'indent': 4, 'statement': 'if highestPrice and strategy.position_size == 0'}, {'indent': 4, 'statement': 'if lowestPrice and strategy.position_size == 0'}, {'indent': 0, 'statement': 'if strategy.position_size > 0 and crossUnder'}, {'indent': 0, 'statement': 'if strategy.position_size < 0 and crossOver'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry(id="Buy", direction=strategy.long)', 'conditions': ['cross', 'highestPrice and strategy.position_size == 0'], 'statement': 'strategy.entry(id="Buy", direction=strategy.long)'}, {'kind': 'entry', 'call': 'strategy.entry(id="Sell", direction=strategy.short)', 'conditions': ['cross', 'lowestPrice and strategy.position_size == 0'], 'statement': 'strategy.entry(id="Sell", direction=strategy.short)'}, {'kind': 'close', 'call': 'strategy.close("Buy")', 'conditions': ['strategy.position_size > 0 and crossUnder'], 'statement': 'strategy.close("Buy")'}, {'kind': 'close', 'call': 'strategy.close("Sell")', 'conditions': ['strategy.position_size < 0 and crossOver'], 'statement': 'strategy.close("Sell")'}]
    original_pine = '/*backtest\nstart: 2024-02-01 00:00:00\nend: 2024-02-29 23:59:59\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This source code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © ZenAndTheArtOfTrading\n// @version=5\nstrategy("ema giao nhau", overlay=true, default_qty_type=strategy.percent_of_equity, default_qty_value=100)\n\n// Get user input\nemaLength1 = input.int(title="EMA #1 Length", defval=5)\nemaLength2 = input.int(title="EMA #2 Length", defval=10)\n\n// Get MAs\nema1 = ta.ema(close, emaLength1)\nema2 = ta.ema(close, emaLength2)\n\n// Draw MAs\nplot(ema1, color=color.blue, title="EMA 1")\nplot(ema2, color=color.red, title="EMA 2")\n\n// Detect crossovers\nbool crossOver = ta.crossover(ema1, ema2)\nbool crossUnder = ta.crossunder(ema1, ema2)\nbool cross = crossOver or crossUnder\n//float crossPrice = ta.valuewhen(cross, close, 0)\nfloat crossPrice = cross ? close : na\n\n// Check if the crossover price is the highest price over the past 10 bars\nbool highestPrice = crossOver\nfor i = 1 to 10\n    if crossPrice <= close[i]\n        highestPrice := false\n        break\n\n// Check if the crossover price is the lowest price over the past 10 bars\nbool lowestPrice = crossUnder\nfor i = 1 to 10\n    if crossPrice >= close[i]\n        lowestPrice := false\n        break\n\n// Flag the bar if it is a high/low close\nbgcolor(highestPrice ? color.new(color.green, 50) : na)\nbgcolor(lowestPrice ? color.new(color.red, 50) : na)\n\n// Display crossover price\nif cross\n    highestEmaPrice = ema1 > ema2 ? ema1 : ema2\n    label myLabel = label.new(bar_index, highestEmaPrice, "CrossPrice=" + str.tostring(crossPrice), color=color.white)\n    if highestPrice and strategy.position_size == 0\n        strategy.entry(id="Buy", direction=strategy.long)\n    if lowestPrice and strategy.position_size == 0\n        strategy.entry(id="Sell", direction=strategy.short)\n\n// Exit trades when short-term EMA is breached\nif strategy.position_size > 0 and crossUnder\n    strategy.close("Buy")\nif strategy.position_size < 0 and crossOver\n    strategy.close("Sell")'

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
