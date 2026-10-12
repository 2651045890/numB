"""Source-faithful deep-assisted port of 渔夫转身EMA多重止损多重止盈策略Fisher-Turnaround-EMA-Multi-Take-Profit-and-Multi-Stop-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_5d6be310(PinePortBase, IStrategy):
    source_file = '渔夫转身EMA多重止损多重止盈策略Fisher-Turnaround-EMA-Multi-Take-Profit-and-Multi-Stop-Strategy.md'
    timeframe = '1d'
    can_short = False
    source_defaults = {'fts_length': 14, 'atr_length': 14}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.exit', 'strategy.entry', 'strategy.position_size', 'for ']
    source_fidelity_notes = ['Reads broker/strategy state; signals depend on fill timing and cannot be reduced to indicator-only booleans without changing behavior.', 'Uses strategy.exit; stop/limit/profit/loss/trailing arguments have Pine order semantics and may fill intrabar.']
    pine_assignments = [{'mode': '', 'name': 'fts_length', 'op': '=', 'expr': 'input(14, title="Blackflag FTS Length")', 'conditions': []}, {'mode': '', 'name': 'atr_length', 'op': '=', 'expr': 'input(14, title="ATR Length")', 'conditions': []}, {'mode': '', 'name': 'short', 'op': '=', 'expr': 'ema(close, 12)', 'conditions': []}, {'mode': '', 'name': 'long', 'op': '=', 'expr': 'ema(close, 26)', 'conditions': []}, {'mode': '', 'name': 'up', 'op': '=', 'expr': '0.0', 'conditions': []}, {'mode': '', 'name': 'down', 'op': '=', 'expr': '0.0', 'conditions': []}, {'mode': '', 'name': 'up', 'op': ':=', 'expr': 'up + (high[i] - low[i])', 'conditions': []}, {'mode': '', 'name': 'down', 'op': ':=', 'expr': 'down + (high[i] - low[i])', 'conditions': []}, {'mode': '', 'name': 'fts_value', 'op': '=', 'expr': 'down == 0 ? 100 : 100 - (100 / (1 + (up / down)))', 'conditions': []}, {'mode': '', 'name': 'buy_condition', 'op': '=', 'expr': 'crossover(short, long) and fts_value > 0', 'conditions': []}, {'mode': '', 'name': 'atr_value', 'op': '=', 'expr': 'atr(atr_length)', 'conditions': []}, {'mode': '', 'name': 'stop_loss_level', 'op': '=', 'expr': 'close - atr_value', 'conditions': []}, {'mode': '', 'name': 'take_profit_level1', 'op': '=', 'expr': 'close + 2 * atr_value', 'conditions': []}, {'mode': '', 'name': 'take_profit_level2', 'op': '=', 'expr': 'close + 3 * atr_value', 'conditions': []}, {'mode': '', 'name': 'sell_condition', 'op': '=', 'expr': 'crossunder(short, long) or fts_value < 0', 'conditions': []}, {'mode': '', 'name': 'position_size', 'op': '=', 'expr': 'strategy.position_size', 'conditions': []}, {'mode': '', 'name': 'target_position_size1', 'op': '=', 'expr': 'position_size * 0.5', 'conditions': []}, {'mode': '', 'name': 'target_position_size2', 'op': '=', 'expr': 'position_size * 1', 'conditions': []}]
    pine_user_functions = []
    pine_controls = [{'indent': 0, 'statement': 'for i = 0 to fts_length - 1'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("Buy", strategy.long, when = buy_condition)', 'conditions': [], 'statement': 'strategy.entry("Buy", strategy.long, when = buy_condition)'}, {'kind': 'exit', 'call': 'strategy.exit("Take Profit 1", from_entry="Buy", loss=close, profit=take_profit_level1, qty=target_position_size1)', 'conditions': [], 'statement': 'strategy.exit("Take Profit 1", from_entry="Buy", loss=close, profit=take_profit_level1, qty=target_position_size1)'}, {'kind': 'exit', 'call': 'strategy.exit("Take Profit 2/Move Stop Loss", from_entry="Buy", loss=close, profit=take_profit_level2, qty=target_position_size2)', 'conditions': [], 'statement': 'strategy.exit("Take Profit 2/Move Stop Loss", from_entry="Buy", loss=close, profit=take_profit_level2, qty=target_position_size2)'}]
    original_pine = '/*backtest\nstart: 2022-12-29 00:00:00\nend: 2024-01-04 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This source code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © Eliebf13\n//@version=4\nstrategy("GDAX EMA & Blackflag FTS Strategy with Multiple Take Profits and Dynamic Stop Loss", overlay=true)\n\n// Input parameters for Blackflag FTS\nfts_length = input(14, title="Blackflag FTS Length")\natr_length = input(14, title="ATR Length")\n\n// GDAX EMA calculation\nshort = ema(close, 12)\nlong = ema(close, 26)\n\n// Calculate Blackflag FTS signal line manually\nup = 0.0\ndown = 0.0\nfor i = 0 to fts_length - 1\n    up := up + (high[i] - low[i])\n    down := down + (high[i] - low[i])\n\nfts_value = down == 0 ? 100 : 100 - (100 / (1 + (up / down)))\n\n// Buy condition: GDAX EMA crossover and Blackflag FTS signal above zero\nbuy_condition = crossover(short, long) and fts_value > 0\n\n// ATR calculation\natr_value = atr(atr_length)\n\n// Calculate Stop Loss and Take Profit levels\nstop_loss_level = close - atr_value\ntake_profit_level1 = close + 2 * atr_value\ntake_profit_level2 = close + 3 * atr_value\n\n// Sell condition: GDAX EMA crossunder or Blackflag FTS signal below zero\nsell_condition = crossunder(short, long) or fts_value < 0\n\n// Strategy orders with Multiple Take Profits and Dynamic Stop Loss\nstrategy.entry("Buy", strategy.long, when = buy_condition)\n\n// Calculate position size for 50% closure at each take profit level\nposition_size = strategy.position_size\ntarget_position_size1 = position_size * 0.5\ntarget_position_size2 = position_size * 1\n\nstrategy.exit("Take Profit 1", from_entry="Buy", loss=close, profit=take_profit_level1, qty=target_position_size1)\nstrategy.exit("Take Profit 2/Move Stop Loss", from_entry="Buy", loss=close, profit=take_profit_level2, qty=target_position_size2)\n\n// Plot GDAX EMA lines\nplot(short, color=#6f92ce, linewidth=2, title="Ema 12")\nplot(long, color=#e08937, linewidth=2, title="Ema 26")\n\n// Plot Blackflag FTS signal\nplot(fts_value, color=color.blue, title="Blackflag FTS Signal")\n\n// Plot buy and sell signals on the chart\nplotshape(series=buy_condition, location=location.belowbar, color=color.green, style=shape.triangleup, title="Buy Signal")\nplotshape(series=sell_condition, location=location.abovebar, color=color.red, style=shape.triangledown, title="Sell Signal")'

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
