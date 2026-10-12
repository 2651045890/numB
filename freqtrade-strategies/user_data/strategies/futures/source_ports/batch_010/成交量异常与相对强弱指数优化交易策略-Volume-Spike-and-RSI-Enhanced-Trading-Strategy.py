"""Source-faithful deep-assisted port of 成交量异常与相对强弱指数优化交易策略-Volume-Spike-and-RSI-Enhanced-Trading-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_65078e0c(PinePortBase, IStrategy):
    source_file = '成交量异常与相对强弱指数优化交易策略-Volume-Spike-and-RSI-Enhanced-Trading-Strategy.md'
    timeframe = '1h'
    can_short = True
    source_defaults = {'rsi_length': 14, 'overSold': 30, 'overBought': 70, 'volume_threshold': 1.5, 'risk_reward_ratio': 2.0, 'atr_length': 14}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.exit', 'strategy.entry', 'for ']
    source_fidelity_notes = ['Uses strategy.exit; stop/limit/profit/loss/trailing arguments have Pine order semantics and may fill intrabar.']
    pine_assignments = [{'mode': '', 'name': 'rsi_length', 'op': '=', 'expr': 'input(14, title="RSI Length")', 'conditions': []}, {'mode': '', 'name': 'overSold', 'op': '=', 'expr': 'input(30, title="RSI Oversold Level")', 'conditions': []}, {'mode': '', 'name': 'overBought', 'op': '=', 'expr': 'input(70, title="RSI Overbought Level")', 'conditions': []}, {'mode': '', 'name': 'volume_threshold', 'op': '=', 'expr': 'input(1.5, title="Volume Spike Multiplier (e.g., 1.5x avg volume)")', 'conditions': []}, {'mode': '', 'name': 'risk_reward_ratio', 'op': '=', 'expr': 'input(2.0, title="Risk-Reward Ratio (1:X)")', 'conditions': []}, {'mode': '', 'name': 'atr_length', 'op': '=', 'expr': 'input(14, title="ATR Length")', 'conditions': []}, {'mode': '', 'name': 'vrsi', 'op': '=', 'expr': 'ta.rsi(close, rsi_length)', 'conditions': []}, {'mode': '', 'name': 'avg_volume', 'op': '=', 'expr': 'ta.sma(volume, 20)', 'conditions': []}, {'mode': '', 'name': 'volume_spike', 'op': '=', 'expr': 'volume > avg_volume * volume_threshold', 'conditions': []}, {'mode': '', 'name': 'long_condition', 'op': '=', 'expr': 'volume_spike and vrsi < overSold and close > open // Bullish price action', 'conditions': []}, {'mode': '', 'name': 'short_condition', 'op': '=', 'expr': 'volume_spike and vrsi > overBought and close < open // Bearish price action', 'conditions': []}, {'mode': '', 'name': 'stop_loss', 'op': '=', 'expr': 'low - ta.atr(atr_length)', 'conditions': ['(long_condition)']}, {'mode': '', 'name': 'take_profit', 'op': '=', 'expr': 'close + (close - stop_loss) * risk_reward_ratio', 'conditions': ['(long_condition)']}, {'mode': '', 'name': 'stop_loss', 'op': '=', 'expr': 'high + ta.atr(atr_length)', 'conditions': ['(short_condition)']}, {'mode': '', 'name': 'take_profit', 'op': '=', 'expr': 'close - (stop_loss - close) * risk_reward_ratio', 'conditions': ['(short_condition)']}]
    pine_user_functions = []
    pine_controls = [{'indent': 0, 'statement': 'if (long_condition)'}, {'indent': 0, 'statement': 'if (short_condition)'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("Buy", strategy.long, comment="Buy Signal")', 'conditions': ['(long_condition)'], 'statement': 'strategy.entry("Buy", strategy.long, comment="Buy Signal")'}, {'kind': 'exit', 'call': 'strategy.exit("Take Profit/Stop Loss", "Buy", stop=stop_loss, limit=take_profit)', 'conditions': ['(long_condition)'], 'statement': 'strategy.exit("Take Profit/Stop Loss", "Buy", stop=stop_loss, limit=take_profit)'}, {'kind': 'entry', 'call': 'strategy.entry("Sell", strategy.short, comment="Sell Signal")', 'conditions': ['(short_condition)'], 'statement': 'strategy.entry("Sell", strategy.short, comment="Sell Signal")'}, {'kind': 'exit', 'call': 'strategy.exit("Take Profit/Stop Loss", "Sell", stop=stop_loss, limit=take_profit)', 'conditions': ['(short_condition)'], 'statement': 'strategy.exit("Take Profit/Stop Loss", "Sell", stop=stop_loss, limit=take_profit)'}]
    original_pine = '/*backtest\nstart: 2024-02-21 00:00:00\nend: 2025-02-18 08:00:00\nperiod: 1h\nbasePeriod: 1h\nexchanges: [{"eid":"Binance","currency":"ETH_USDT"}]\n*/\n\n//@version=6\nstrategy("Volume Spike & RSI Scalping (Session Restricted)", overlay=true)\n\n// Inputs\nrsi_length = input(14, title="RSI Length")\noverSold = input(30, title="RSI Oversold Level")\noverBought = input(70, title="RSI Overbought Level")\nvolume_threshold = input(1.5, title="Volume Spike Multiplier (e.g., 1.5x avg volume)")\nrisk_reward_ratio = input(2.0, title="Risk-Reward Ratio (1:X)")\natr_length = input(14, title="ATR Length")\n\n\n\n// RSI Calculation\nvrsi = ta.rsi(close, rsi_length)\n\n// Volume Spike Detection\navg_volume = ta.sma(volume, 20)\nvolume_spike = volume > avg_volume * volume_threshold\n\n// Entry Signals Based on RSI and Volume\nlong_condition = volume_spike and vrsi < overSold and close > open // Bullish price action\nshort_condition = volume_spike and vrsi > overBought and close < open // Bearish price action\n\n// Execute Trades\nif (long_condition)\n    stop_loss = low - ta.atr(atr_length)\n    take_profit = close + (close - stop_loss) * risk_reward_ratio\n    strategy.entry("Buy", strategy.long, comment="Buy Signal")\n    strategy.exit("Take Profit/Stop Loss", "Buy", stop=stop_loss, limit=take_profit)\n\nif (short_condition)\n    stop_loss = high + ta.atr(atr_length)\n    take_profit = close - (stop_loss - close) * risk_reward_ratio\n    strategy.entry("Sell", strategy.short, comment="Sell Signal")\n    strategy.exit("Take Profit/Stop Loss", "Sell", stop=stop_loss, limit=take_profit)\n\n// Background Highlighting for Signals\nbgcolor(long_condition ? color.new(color.green, 85) : na, title="Long Signal Background")\nbgcolor(short_condition ? color.new(color.red, 85) : na, title="Short Signal Background")'

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
