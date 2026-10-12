"""Source-faithful deep-assisted port of 开放市场曝光度动态调仓量化交易策略-Open-Market-Exposure-Dynamic-Position-Adjustment-Quantitative-Trading-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_38d13a84(PinePortBase, IStrategy):
    source_file = '开放市场曝光度动态调仓量化交易策略-Open-Market-Exposure-Dynamic-Position-Adjustment-Quantitative-Trading-Strategy.md'
    timeframe = '1d'
    can_short = False
    source_defaults = {'length': 14, 'sharpe_length': 30, 'threshold': 0.01, 'take_profit': 0.02, 'stop_loss': 0.01}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.exit', 'strategy.entry', 'strategy.close', 'strategy.position_size', 'var ', 'for ']
    source_fidelity_notes = ['Uses persistent Pine state (var/varip); state is order-dependent and must be evaluated bar-by-bar, not replaced by a vectorized fill-forward approximation.', 'Reads broker/strategy state; signals depend on fill timing and cannot be reduced to indicator-only booleans without changing behavior.', 'Uses strategy.exit; stop/limit/profit/loss/trailing arguments have Pine order semantics and may fill intrabar.']
    pine_assignments = [{'mode': '', 'name': 'length', 'op': '=', 'expr': 'input(14, title="Length for Variance")', 'conditions': []}, {'mode': '', 'name': 'sharpe_length', 'op': '=', 'expr': 'input(30, title="Length for Sharpe Ratio")', 'conditions': []}, {'mode': '', 'name': 'threshold', 'op': '=', 'expr': 'input(0.01, title="Cumulative OME Threshold") // Define a threshold for entry', 'conditions': []}, {'mode': '', 'name': 'take_profit', 'op': '=', 'expr': 'input(0.02, title="Take Profit (%)") // Define a take profit percentage', 'conditions': []}, {'mode': '', 'name': 'stop_loss', 'op': '=', 'expr': 'input(0.01, title="Stop Loss (%)") // Define a stop loss percentage', 'conditions': []}, {'mode': '', 'name': 'daily_return', 'op': '=', 'expr': '(close - close[1]) / close[1]', 'conditions': []}, {'mode': '', 'name': 'ome', 'op': '=', 'expr': '(close - open[1]) / open[1]', 'conditions': []}, {'mode': 'var', 'name': 'cum_ome', 'op': '=', 'expr': 'na', 'conditions': []}, {'mode': '', 'name': 'cum_ome', 'op': ':=', 'expr': '0.0', 'conditions': ['na(cum_ome)']}, {'mode': '', 'name': 'cum_ome', 'op': ':=', 'expr': '0.0', 'conditions': ['(dayofweek != dayofweek[1]) // Reset cumulative OME daily']}, {'mode': '', 'name': 'cum_ome', 'op': ':=', 'expr': 'cum_ome + ome', 'conditions': []}, {'mode': '', 'name': 'mean_return', 'op': '=', 'expr': 'ta.sma(cum_ome, sharpe_length)', 'conditions': []}, {'mode': '', 'name': 'std_dev', 'op': '=', 'expr': 'ta.stdev(cum_ome, sharpe_length)', 'conditions': []}, {'mode': '', 'name': 'sharpe_ratio', 'op': '=', 'expr': 'na(cum_ome) or (std_dev == 0) ? na : mean_return / std_dev', 'conditions': []}, {'mode': '', 'name': 'target_price', 'op': '=', 'expr': 'close * (1 + take_profit)', 'conditions': ['(strategy.position_size > 0)']}, {'mode': '', 'name': 'stop_price', 'op': '=', 'expr': 'close * (1 - stop_loss)', 'conditions': ['(strategy.position_size > 0)']}]
    pine_user_functions = []
    pine_controls = [{'indent': 0, 'statement': 'if na(cum_ome)'}, {'indent': 0, 'statement': 'if (dayofweek != dayofweek[1]) // Reset cumulative OME daily'}, {'indent': 0, 'statement': 'if (cum_ome > threshold)'}, {'indent': 0, 'statement': 'if (cum_ome < -threshold)'}, {'indent': 0, 'statement': 'if (strategy.position_size > 0)'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("Long", strategy.long)', 'conditions': ['(cum_ome > threshold)'], 'statement': 'strategy.entry("Long", strategy.long)'}, {'kind': 'close', 'call': 'strategy.close("Long")', 'conditions': ['(cum_ome < -threshold)'], 'statement': 'strategy.close("Long")'}, {'kind': 'exit', 'call': 'strategy.exit("Take Profit", "Long", limit=target_price)', 'conditions': ['(strategy.position_size > 0)'], 'statement': 'strategy.exit("Take Profit", "Long", limit=target_price)'}, {'kind': 'exit', 'call': 'strategy.exit("Stop Loss", "Long", stop=stop_price)', 'conditions': ['(strategy.position_size > 0)'], 'statement': 'strategy.exit("Stop Loss", "Long", stop=stop_price)'}]
    original_pine = '/*backtest\nstart: 2019-12-23 08:00:00\nend: 2024-11-11 00:00:00\nperiod: 1d\nbasePeriod: 1d\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("Open Market Exposure (OME) Strategy", overlay=true)\n\n// Input parameters\nlength = input(14, title="Length for Variance")\nsharpe_length = input(30, title="Length for Sharpe Ratio")\nthreshold = input(0.01, title="Cumulative OME Threshold")  // Define a threshold for entry\ntake_profit = input(0.02, title="Take Profit (%)")  // Define a take profit percentage\nstop_loss = input(0.01, title="Stop Loss (%)")  // Define a stop loss percentage\n\n// Calculate Daily Returns\ndaily_return = (close - close[1]) / close[1]\n\n// Open Market Exposure (OME) calculation\nome = (close - open[1]) / open[1]\n\n// Cumulative OME\nvar float cum_ome = na\nif na(cum_ome)\n    cum_ome := 0.0\nif (dayofweek != dayofweek[1])  // Reset cumulative OME daily\n    cum_ome := 0.0\ncum_ome := cum_ome + ome\n\n// Performance Metrics Calculation (Sharpe Ratio)\nmean_return = ta.sma(cum_ome, sharpe_length)\nstd_dev = ta.stdev(cum_ome, sharpe_length)\nsharpe_ratio = na(cum_ome) or (std_dev == 0) ? na : mean_return / std_dev\n\n// Entry Condition: Buy when Cumulative OME crosses above the threshold\nif (cum_ome > threshold)\n    strategy.entry("Long", strategy.long)\n\n// Exit Condition: Sell when Cumulative OME crosses below the threshold\nif (cum_ome < -threshold)\n    strategy.close("Long")\n\n// Take Profit and Stop Loss\nif (strategy.position_size > 0)\n    // Calculate target and stop levels\n    target_price = close * (1 + take_profit)\n    stop_price = close * (1 - stop_loss)\n\n    // Place limit and stop orders\n    strategy.exit("Take Profit", "Long", limit=target_price)\n    strategy.exit("Stop Loss", "Long", stop=stop_price)'

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
