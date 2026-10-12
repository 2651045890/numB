"""Source-faithful deep-assisted port of 指数移动平均线交叉结合动态止损策略-EMA-Crossover-Strategy-with-Dynamic-Trailing-Stop-Loss.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_c25d6565(PinePortBase, IStrategy):
    source_file = '指数移动平均线交叉结合动态止损策略-EMA-Crossover-Strategy-with-Dynamic-Trailing-Stop-Loss.md'
    timeframe = '2d'
    can_short = True
    source_defaults = {'length_ema': 68, 'initial_stop_loss_points': 20, 'trail_distance': 10}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.exit', 'strategy.entry', 'var ', 'for ']
    source_fidelity_notes = ['Uses persistent Pine state (var/varip); state is order-dependent and must be evaluated bar-by-bar, not replaced by a vectorized fill-forward approximation.', 'Uses strategy.exit; stop/limit/profit/loss/trailing arguments have Pine order semantics and may fill intrabar.']
    pine_assignments = [{'mode': '', 'name': 'length_ema', 'op': '=', 'expr': 'input(68, title="EMA Length")', 'conditions': []}, {'mode': '', 'name': 'initial_stop_loss_points', 'op': '=', 'expr': 'input(20, title="Initial Stop Loss in Points")', 'conditions': []}, {'mode': '', 'name': 'trail_distance', 'op': '=', 'expr': 'input(10, title="Trailing Stop Adjustment in Points")', 'conditions': []}, {'mode': '', 'name': 'ema68', 'op': '=', 'expr': 'ta.ema(close, length_ema)', 'conditions': []}, {'mode': 'var', 'name': 'entry_price', 'op': '=', 'expr': 'na // Store entry price', 'conditions': []}, {'mode': 'var', 'name': 'is_long', 'op': '=', 'expr': 'false // Track if we are in a long trade', 'conditions': []}, {'mode': 'var', 'name': 'is_short', 'op': '=', 'expr': 'false // Track if we are in a short trade', 'conditions': []}, {'mode': '', 'name': 'entry_price', 'op': ':=', 'expr': 'close', 'conditions': ['ta.crossover(close, ema68)']}, {'mode': '', 'name': 'is_long', 'op': ':=', 'expr': 'true', 'conditions': ['ta.crossover(close, ema68)']}, {'mode': '', 'name': 'is_short', 'op': ':=', 'expr': 'false', 'conditions': ['ta.crossover(close, ema68)']}, {'mode': '', 'name': 'entry_price', 'op': ':=', 'expr': 'close', 'conditions': ['ta.crossunder(close, ema68)']}, {'mode': '', 'name': 'is_long', 'op': ':=', 'expr': 'false', 'conditions': ['ta.crossunder(close, ema68)']}, {'mode': '', 'name': 'is_short', 'op': ':=', 'expr': 'true', 'conditions': ['ta.crossunder(close, ema68)']}, {'mode': '', 'name': 'stop_loss', 'op': '=', 'expr': 'entry_price - initial_stop_loss_points', 'conditions': ['is_long']}, {'mode': '', 'name': 'trail_price', 'op': '=', 'expr': 'entry_price + initial_stop_loss_points', 'conditions': ['is_long']}, {'mode': '', 'name': 'stop_loss', 'op': ':=', 'expr': 'entry_price + trail_distance', 'conditions': ['is_long', 'close >= trail_price']}, {'mode': '', 'name': 'stop_loss', 'op': '=', 'expr': 'entry_price + initial_stop_loss_points', 'conditions': ['is_short']}, {'mode': '', 'name': 'trail_price', 'op': '=', 'expr': 'entry_price - initial_stop_loss_points', 'conditions': ['is_short']}, {'mode': '', 'name': 'stop_loss', 'op': ':=', 'expr': 'entry_price - trail_distance', 'conditions': ['is_short', 'close <= trail_price']}]
    pine_user_functions = []
    pine_controls = [{'indent': 0, 'statement': 'if ta.crossover(close, ema68)'}, {'indent': 0, 'statement': 'if ta.crossunder(close, ema68)'}, {'indent': 0, 'statement': 'if is_long'}, {'indent': 4, 'statement': 'if close >= trail_price'}, {'indent': 0, 'statement': 'if is_short'}, {'indent': 4, 'statement': 'if close <= trail_price'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("Long", strategy.long)', 'conditions': ['ta.crossover(close, ema68)'], 'statement': 'strategy.entry("Long", strategy.long)'}, {'kind': 'entry', 'call': 'strategy.entry("Short", strategy.short)', 'conditions': ['ta.crossunder(close, ema68)'], 'statement': 'strategy.entry("Short", strategy.short)'}, {'kind': 'exit', 'call': 'strategy.exit("LongExit", "Long", stop=stop_loss, when=close < ema68)', 'conditions': ['is_long'], 'statement': 'strategy.exit("LongExit", "Long", stop=stop_loss, when=close < ema68)'}, {'kind': 'exit', 'call': 'strategy.exit("ShortExit", "Short", stop=stop_loss, when=close > ema68)', 'conditions': ['is_short'], 'statement': 'strategy.exit("ShortExit", "Short", stop=stop_loss, when=close > ema68)'}]
    original_pine = '/*backtest\nstart: 2024-10-01 00:00:00\nend: 2025-02-18 08:00:00\nperiod: 2d\nbasePeriod: 2d\nexchanges: [{"eid":"Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("EMA 68 with Trailing Stop-Loss", overlay=true)\n\n// Inputs for customization\nlength_ema = input(68, title="EMA Length")\ninitial_stop_loss_points = input(20, title="Initial Stop Loss in Points")\ntrail_distance = input(10, title="Trailing Stop Adjustment in Points")\n\nema68 = ta.ema(close, length_ema)\n\n// Plot EMA\nplot(ema68, color=color.blue, title="68-Day EMA")\n\nvar float entry_price = na // Store entry price\nvar bool is_long = false // Track if we are in a long trade\nvar bool is_short = false // Track if we are in a short trade\n\n// Buy Condition: Close above 68-day EMA\nif ta.crossover(close, ema68)\n    strategy.entry("Long", strategy.long)\n    entry_price := close\n    is_long := true\n    is_short := false\n\n// Sell Condition: Close below 68-day EMA\nif ta.crossunder(close, ema68)\n    strategy.entry("Short", strategy.short)\n    entry_price := close\n    is_long := false\n    is_short := true\n\n// Long Exit Conditions\nif is_long\n    stop_loss = entry_price - initial_stop_loss_points\n    trail_price = entry_price + initial_stop_loss_points\n    if close >= trail_price\n        stop_loss := entry_price + trail_distance\n    strategy.exit("LongExit", "Long", stop=stop_loss, when=close < ema68)\n\n// Short Exit Conditions\nif is_short\n    stop_loss = entry_price + initial_stop_loss_points\n    trail_price = entry_price - initial_stop_loss_points\n    if close <= trail_price\n        stop_loss := entry_price - trail_distance\n    strategy.exit("ShortExit", "Short", stop=stop_loss, when=close > ema68)'

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
