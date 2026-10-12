"""Source-faithful deep-assisted port of 每日均成本策略结合EMA触碰信号Daily-DCA-Strategy-with-Touching-EMAs.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_f0529a20(PinePortBase, IStrategy):
    source_file = '每日均成本策略结合EMA触碰信号Daily-DCA-Strategy-with-Touching-EMAs.md'
    timeframe = '3m'
    can_short = False
    source_defaults = {'daily_investment': 50000, 'start_year': 2022, 'start_month': 1, 'start_day': 1, 'end_year': 2023, 'end_month': 12, 'end_day': 1, 'trade_count_limit': 10000, 'enable_sell': True}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_pyramiding = 10000
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.entry', 'strategy.close', 'var ', 'for ']
    source_fidelity_notes = ['Uses persistent Pine state (var/varip); state is order-dependent and must be evaluated bar-by-bar, not replaced by a vectorized fill-forward approximation.']
    pine_assignments = [{'mode': '', 'name': 'daily_investment', 'op': '=', 'expr': 'input(50000, title="Daily Investment")', 'conditions': []}, {'mode': '', 'name': 'start_year', 'op': '=', 'expr': 'input(2022, title="Start Year")', 'conditions': []}, {'mode': '', 'name': 'start_month', 'op': '=', 'expr': 'input(1, title="Start Month")', 'conditions': []}, {'mode': '', 'name': 'start_day', 'op': '=', 'expr': 'input(1, title="Start Day")', 'conditions': []}, {'mode': '', 'name': 'end_year', 'op': '=', 'expr': 'input(2023, title="End Year")', 'conditions': []}, {'mode': '', 'name': 'end_month', 'op': '=', 'expr': 'input(12, title="End Month")', 'conditions': []}, {'mode': '', 'name': 'end_day', 'op': '=', 'expr': 'input(1, title="End Day")', 'conditions': []}, {'mode': '', 'name': 'trade_count_limit', 'op': '=', 'expr': 'input(10000, title="Pyramiding Limit")', 'conditions': []}, {'mode': '', 'name': 'enable_sell', 'op': '=', 'expr': 'input(true, title="Enable Sell")', 'conditions': []}, {'mode': '', 'name': 'start_date', 'op': '=', 'expr': 'timestamp(start_year, start_month, start_day)', 'conditions': []}, {'mode': 'var', 'name': 'trade_count', 'op': '=', 'expr': '0', 'conditions': []}, {'mode': '', 'name': 'shares_to_buy', 'op': '=', 'expr': 'daily_investment / close', 'conditions': []}, {'mode': '', 'name': 'isNewDay', 'op': '=', 'expr': 'dayofmonth != dayofmonth[1] and time >= start_date', 'conditions': []}, {'mode': '', 'name': 'ema5_cross_above', 'op': '=', 'expr': 'crossover(close, ema(close, 5))', 'conditions': []}, {'mode': '', 'name': 'ema10_cross_above', 'op': '=', 'expr': 'crossover(close, ema(close, 10))', 'conditions': []}, {'mode': '', 'name': 'ema20_cross_above', 'op': '=', 'expr': 'crossover(close, ema(close, 20))', 'conditions': []}, {'mode': '', 'name': 'ema50_cross_above', 'op': '=', 'expr': 'crossover(close, ema(close, 50))', 'conditions': []}, {'mode': '', 'name': 'ema100_cross_above', 'op': '=', 'expr': 'crossover(close, ema(close, 100))', 'conditions': []}, {'mode': '', 'name': 'ema200_cross_above', 'op': '=', 'expr': 'crossover(close, ema(close, 200))', 'conditions': []}, {'mode': '', 'name': 'trade_count', 'op': ':=', 'expr': 'trade_count + 1', 'conditions': ['isNewDay and (ema5_cross_above or ema10_cross_above or ema20_cross_above or ema50_cross_above or ema100_cross_above or ema200_cross_above) and trade_count < trade_count_limit']}, {'mode': '', 'name': 'sell_condition', 'op': '=', 'expr': 'true', 'conditions': []}]
    pine_user_functions = []
    pine_controls = [{'indent': 0, 'statement': 'if isNewDay and (ema5_cross_above or ema10_cross_above or ema20_cross_above or ema50_cross_above or ema100_cross_above or ema200_cross_above) and trade_count < trade_count_limit'}, {'indent': 0, 'statement': 'if enable_sell and sell_condition'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("Buy", strategy.long, qty=shares_to_buy)', 'conditions': ['isNewDay and (ema5_cross_above or ema10_cross_above or ema20_cross_above or ema50_cross_above or ema100_cross_above or ema200_cross_above) and trade_count < trade_count_limit'], 'statement': 'strategy.entry("Buy", strategy.long, qty=shares_to_buy)'}, {'kind': 'close_all', 'call': 'strategy.close_all()', 'conditions': ['enable_sell and sell_condition'], 'statement': 'strategy.close_all()'}]
    original_pine = '/*backtest\nstart: 2024-01-08 00:00:00\nend: 2024-01-15 00:00:00\nperiod: 3m\nbasePeriod: 1m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=4\nstrategy("Daily DCA Strategy with Touching EMAs", overlay=true, pyramiding=10000)\n\n// Customizable Parameters\ndaily_investment = input(50000, title="Daily Investment")\nstart_year = input(2022, title="Start Year")\nstart_month = input(1, title="Start Month")\nstart_day = input(1, title="Start Day")\nend_year = input(2023, title="End Year")\nend_month = input(12, title="End Month")\nend_day = input(1, title="End Day")\ntrade_count_limit = input(10000, title="Pyramiding Limit")\nenable_sell = input(true, title="Enable Sell")\n\nstart_date = timestamp(start_year, start_month, start_day)\nvar int trade_count = 0\n\n// Calculate the number of shares to buy based on the current closing price\nshares_to_buy = daily_investment / close\n\n// Check if a new day has started and after the start date\nisNewDay = dayofmonth != dayofmonth[1] and time >= start_date\n\n// Buy conditions based on EMA crossovers\nema5_cross_above = crossover(close, ema(close, 5))\nema10_cross_above = crossover(close, ema(close, 10))\nema20_cross_above = crossover(close, ema(close, 20))\nema50_cross_above = crossover(close, ema(close, 50))\nema100_cross_above = crossover(close, ema(close, 100))\nema200_cross_above = crossover(close, ema(close, 200))\n\nif isNewDay and (ema5_cross_above or ema10_cross_above or ema20_cross_above or ema50_cross_above or ema100_cross_above or ema200_cross_above) and trade_count < trade_count_limit\n    strategy.entry("Buy", strategy.long, qty=shares_to_buy)\n    trade_count := trade_count + 1\n\n// Dynamic sell conditions (optional)\nsell_condition =  true\n\nif enable_sell and sell_condition\n    strategy.close_all()\n\n// EMA Ribbon for visualization\nplot(ema(close, 5), color=color.red, title="EMA 5")\nplot(ema(close, 10), color=color.orange, title="EMA 10")\nplot(ema(close, 20), color=color.yellow, title="EMA 20")\nplot(ema(close, 50), color=color.green, title="EMA 50")\nplot(ema(close, 100), color=color.blue, title="EMA 100")\nplot(ema(close, 200), color=color.purple, title="EMA 200")'

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
