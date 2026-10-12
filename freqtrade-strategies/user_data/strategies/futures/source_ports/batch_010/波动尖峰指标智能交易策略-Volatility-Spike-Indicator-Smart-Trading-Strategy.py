"""Source-faithful deep-assisted port of 波动尖峰指标智能交易策略-Volatility-Spike-Indicator-Smart-Trading-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_4826d027(PinePortBase, IStrategy):
    source_file = '波动尖峰指标智能交易策略-Volatility-Spike-Indicator-Smart-Trading-Strategy.md'
    timeframe = '3h'
    can_short = True
    source_defaults = {}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 100.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['request.security', 'strategy.exit', 'strategy.entry', 'strategy.position_size', '=>']
    source_fidelity_notes = ['Uses request.security / multi-timeframe context; exact parity depends on HTF resampling, gaps and lookahead semantics.', 'Reads broker/strategy state; signals depend on fill timing and cannot be reduced to indicator-only booleans without changing behavior.', 'Uses strategy.exit; stop/limit/profit/loss/trailing arguments have Pine order semantics and may fill intrabar.']
    pine_assignments = [{'mode': '', 'name': 'fixed_investment', 'op': '=', 'expr': '30000', 'conditions': []}, {'mode': '', 'name': 'spike_threshold', 'op': '=', 'expr': '0.62 // Spike threshold (0.80%)', 'conditions': []}, {'mode': '', 'name': 'profit_target', 'op': '=', 'expr': '0.42 // Take profit (0.48%)', 'conditions': []}, {'mode': '', 'name': 'stop_loss', 'op': '=', 'expr': '1 // Stop loss (10%)', 'conditions': []}, {'mode': '', 'name': 'spike_up', 'op': '=', 'expr': '(high_price - close_price) / close_price >= threshold / 100 // Bullish spike (high - close)', 'conditions': []}, {'mode': '', 'name': 'spike_down', 'op': '=', 'expr': '(close_price - low_price) / close_price >= threshold / 100 // Bearish spike (close - low)', 'conditions': []}, {'mode': '', 'name': 'long_condition', 'op': '=', 'expr': 'spike_up and not spike_down // Only bullish spikes', 'conditions': []}, {'mode': '', 'name': 'short_condition', 'op': '=', 'expr': 'spike_down and not spike_up // Only bearish spikes', 'conditions': []}, {'mode': '', 'name': 'qty_long', 'op': '=', 'expr': 'fixed_investment / close', 'conditions': []}, {'mode': '', 'name': 'qty_short', 'op': '=', 'expr': 'fixed_investment / close', 'conditions': []}]
    pine_user_functions = [{'name': 'detect_spike', 'args': 'threshold, close_price, high_price, low_price', 'body': ''}]
    pine_controls = [{'indent': 0, 'statement': 'if (long_condition)'}, {'indent': 0, 'statement': 'if (short_condition)'}, {'indent': 0, 'statement': 'if (strategy.position_size > 0)'}, {'indent': 0, 'statement': 'if (strategy.position_size < 0)'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("Long", strategy.long, qty=qty_long)', 'conditions': ['(long_condition)'], 'statement': 'strategy.entry("Long", strategy.long, qty=qty_long)'}, {'kind': 'entry', 'call': 'strategy.entry("Short", strategy.short, qty=qty_short)', 'conditions': ['(short_condition)'], 'statement': 'strategy.entry("Short", strategy.short, qty=qty_short)'}, {'kind': 'exit', 'call': 'strategy.exit("Take Profit Long", "Long", limit=strategy.position_avg_price * (1 + profit_target / 100), stop=strategy.position_avg_price * (1 - stop_loss / 100))', 'conditions': ['(strategy.position_size > 0)'], 'statement': 'strategy.exit("Take Profit Long", "Long", limit=strategy.position_avg_price * (1 + profit_target / 100), stop=strategy.position_avg_price * (1 - stop_loss / 100))'}, {'kind': 'exit', 'call': 'strategy.exit("Take Profit Short", "Short", limit=strategy.position_avg_price * (1 - profit_target / 100), stop=strategy.position_avg_price * (1 + stop_loss / 100))', 'conditions': ['(strategy.position_size < 0)'], 'statement': 'strategy.exit("Take Profit Short", "Short", limit=strategy.position_avg_price * (1 - profit_target / 100), stop=strategy.position_avg_price * (1 + stop_loss / 100))'}]
    original_pine = '/*backtest\nstart: 2024-11-08 00:00:00\nend: 2025-02-18 08:00:00\nperiod: 3h\nbasePeriod: 3h\nexchanges: [{"eid":"Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=6\nstrategy("Spike Strategy 1h Optimized", overlay=true, margin_long=100, margin_short=100, default_qty_type=strategy.percent_of_equity, default_qty_value=100)\n\n// Fixed investment amount per trade (30,000 USDT)\nfixed_investment = 30000\n\n// Optimized parameters\nspike_threshold = 0.62 // Spike threshold (0.80%)\nprofit_target = 0.42 // Take profit (0.48%)\nstop_loss = 1  // Stop loss (10%)\n\n// Function to detect spikes\ndetect_spike(threshold, close_price, high_price, low_price) =>\n    spike_up = (high_price - close_price) / close_price >= threshold / 100   // Bullish spike (high - close)\n    spike_down = (close_price - low_price) / close_price >= threshold / 100  // Bearish spike (close - low)\n    [spike_up, spike_down]\n\n// Detecting spikes\n[spike_up, spike_down] = request.security(syminfo.tickerid, "60", detect_spike(spike_threshold, close, high, low))\n\n// Entry conditions\nlong_condition = spike_up and not spike_down  // Only bullish spikes\nshort_condition = spike_down and not spike_up // Only bearish spikes\n\n// Calculate the quantity to invest based on the current price\nqty_long = fixed_investment / close\nqty_short = fixed_investment / close\n\n// Executing the orders\nif (long_condition)\n    strategy.entry("Long", strategy.long, qty=qty_long)\n\nif (short_condition)\n    strategy.entry("Short", strategy.short, qty=qty_short)\n\n// Exiting orders with take profit and stop loss\nif (strategy.position_size > 0)\n    strategy.exit("Take Profit Long", "Long", limit=strategy.position_avg_price * (1 + profit_target / 100), stop=strategy.position_avg_price * (1 - stop_loss / 100))\n\nif (strategy.position_size < 0)\n    strategy.exit("Take Profit Short", "Short", limit=strategy.position_avg_price * (1 - profit_target / 100), stop=strategy.position_avg_price * (1 + stop_loss / 100))\n\n// Plot spikes (optional)\nplotshape(series=long_condition, title="Long Spike", location=location.belowbar, color=color.green, style=shape.labelup, text="BUY")\nplotshape(series=short_condition, title="Short Spike", location=location.abovebar, color=color.red, style=shape.labeldown, text="SELL")'

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
