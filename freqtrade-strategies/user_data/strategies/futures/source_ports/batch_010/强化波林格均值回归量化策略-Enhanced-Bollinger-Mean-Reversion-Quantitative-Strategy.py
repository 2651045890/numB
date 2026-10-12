"""Source-faithful deep-assisted port of 强化波林格均值回归量化策略-Enhanced-Bollinger-Mean-Reversion-Quantitative-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_7ac9e436(PinePortBase, IStrategy):
    source_file = '强化波林格均值回归量化策略-Enhanced-Bollinger-Mean-Reversion-Quantitative-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'length': 20, 'src': 'close', 'mult': 2.0}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.exit', 'strategy.entry', 'for ']
    source_fidelity_notes = ['Uses strategy.exit; stop/limit/profit/loss/trailing arguments have Pine order semantics and may fill intrabar.']
    pine_assignments = [{'mode': '', 'name': 'length', 'op': '=', 'expr': 'input.int(20, title="BB Length")', 'conditions': []}, {'mode': '', 'name': 'src', 'op': '=', 'expr': 'input(close, title="Source")', 'conditions': []}, {'mode': '', 'name': 'mult', 'op': '=', 'expr': 'input.float(2.0, title="BB Multiplier")', 'conditions': []}, {'mode': '', 'name': 'basis', 'op': '=', 'expr': 'ta.sma(src, length)', 'conditions': []}, {'mode': '', 'name': 'dev', 'op': '=', 'expr': 'mult * ta.stdev(src, length)', 'conditions': []}, {'mode': '', 'name': 'upper', 'op': '=', 'expr': 'basis + dev', 'conditions': []}, {'mode': '', 'name': 'lower', 'op': '=', 'expr': 'basis - dev', 'conditions': []}, {'mode': '', 'name': 'p1', 'op': '=', 'expr': 'plot(upper, color=color.red)', 'conditions': []}, {'mode': '', 'name': 'p2', 'op': '=', 'expr': 'plot(lower, color=color.red)', 'conditions': []}, {'mode': '', 'name': 'ema_filter', 'op': '=', 'expr': 'ta.ema(close, 50)', 'conditions': []}, {'mode': '', 'name': 'atr_value', 'op': '=', 'expr': 'ta.atr(14)', 'conditions': []}, {'mode': '', 'name': 'buy_condition', 'op': '=', 'expr': 'ta.crossover(close, lower) and close > ema_filter', 'conditions': []}, {'mode': '', 'name': 'sell_condition', 'op': '=', 'expr': 'ta.crossunder(close, upper) and close < ema_filter', 'conditions': []}]
    pine_user_functions = []
    pine_controls = [{'indent': 0, 'statement': 'if (buy_condition)'}, {'indent': 0, 'statement': 'if (sell_condition)'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("Buy", strategy.long)', 'conditions': ['(buy_condition)'], 'statement': 'strategy.entry("Buy", strategy.long)'}, {'kind': 'entry', 'call': 'strategy.entry("Sell", strategy.short)', 'conditions': ['(sell_condition)'], 'statement': 'strategy.entry("Sell", strategy.short)'}, {'kind': 'exit', 'call': 'strategy.exit("Take Profit/Stop Loss", from_entry="Buy", limit=2*atr_value, stop=1*atr_value)', 'conditions': [], 'statement': 'strategy.exit("Take Profit/Stop Loss", from_entry="Buy", limit=2*atr_value, stop=1*atr_value)'}, {'kind': 'exit', 'call': 'strategy.exit("Take Profit/Stop Loss", from_entry="Sell", limit=2*atr_value, stop=1*atr_value)', 'conditions': [], 'statement': 'strategy.exit("Take Profit/Stop Loss", from_entry="Sell", limit=2*atr_value, stop=1*atr_value)'}]
    original_pine = '/*backtest\nstart: 2019-12-23 08:00:00\nend: 2024-11-17 00:00:00\nperiod: 1d\nbasePeriod: 1d\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("Optimized Bollinger Mean Reversion", overlay=true)\n\n// Bollinger Band Settings\nlength = input.int(20, title="BB Length")\nsrc = input(close, title="Source")\nmult = input.float(2.0, title="BB Multiplier")\n\n// Bollinger Bands Calculation\nbasis = ta.sma(src, length)\ndev = mult * ta.stdev(src, length)\nupper = basis + dev\nlower = basis - dev\n\n// Plot the Bollinger Bands\nplot(basis, color=color.blue)\np1 = plot(upper, color=color.red)\np2 = plot(lower, color=color.red)\nfill(p1, p2, color=color.rgb(41, 98, 255, 90))\n\n// Trend Filter - 50 EMA\nema_filter = ta.ema(close, 50)\n\n// ATR for Dynamic Stop Loss/Take Profit\natr_value = ta.atr(14)\n\n// Buy condition - price touches lower band and above 50 EMA\nbuy_condition = ta.crossover(close, lower) and close > ema_filter\n\n// Sell condition - price touches upper band and below 50 EMA\nsell_condition = ta.crossunder(close, upper) and close < ema_filter\n\n// Strategy Execution\nif (buy_condition)\n    strategy.entry("Buy", strategy.long)\n\nif (sell_condition)\n    strategy.entry("Sell", strategy.short)\n\n// Exit with dynamic ATR-based stop loss and take profit\nstrategy.exit("Take Profit/Stop Loss", from_entry="Buy", limit=2*atr_value, stop=1*atr_value)\nstrategy.exit("Take Profit/Stop Loss", from_entry="Sell", limit=2*atr_value, stop=1*atr_value)'

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
