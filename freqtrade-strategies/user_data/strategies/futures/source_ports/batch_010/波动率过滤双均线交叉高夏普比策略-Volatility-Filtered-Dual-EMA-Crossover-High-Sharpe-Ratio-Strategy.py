"""Source-faithful deep-assisted port of 波动率过滤双均线交叉高夏普比策略-Volatility-Filtered-Dual-EMA-Crossover-High-Sharpe-Ratio-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_b43cbbfb(PinePortBase, IStrategy):
    source_file = '波动率过滤双均线交叉高夏普比策略-Volatility-Filtered-Dual-EMA-Crossover-High-Sharpe-Ratio-Strategy.md'
    timeframe = '1m'
    can_short = True
    source_defaults = {'ema_fast_length': 10, 'ema_slow_length': 30, 'atr_length': 14, 'atr_mean_length': 20, 'atr_std_length': 20, 'risk_factor': 0.01, 'slippage': 0.001}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.exit', 'strategy.entry', 'strategy.equity', 'for ']
    source_fidelity_notes = ['Reads broker/strategy state; signals depend on fill timing and cannot be reduced to indicator-only booleans without changing behavior.', 'Uses strategy.exit; stop/limit/profit/loss/trailing arguments have Pine order semantics and may fill intrabar.']
    pine_assignments = [{'mode': '', 'name': 'ema_fast_length', 'op': '=', 'expr': 'input.int(10, title="Fast EMA Length")', 'conditions': []}, {'mode': '', 'name': 'ema_slow_length', 'op': '=', 'expr': 'input.int(30, title="Slow EMA Length")', 'conditions': []}, {'mode': '', 'name': 'atr_length', 'op': '=', 'expr': 'input.int(14, title="ATR Length")', 'conditions': []}, {'mode': '', 'name': 'atr_mean_length', 'op': '=', 'expr': 'input.int(20, title="ATR Mean Length")', 'conditions': []}, {'mode': '', 'name': 'atr_std_length', 'op': '=', 'expr': 'input.int(20, title="ATR Std Dev Length")', 'conditions': []}, {'mode': '', 'name': 'risk_factor', 'op': '=', 'expr': 'input.float(0.01, title="Risk Factor") // 单笔交易风险占账户资金的百分比', 'conditions': []}, {'mode': '', 'name': 'slippage', 'op': '=', 'expr': 'input.float(0.001, title="Slippage") // 假设滑点', 'conditions': []}, {'mode': '', 'name': 'ema_fast', 'op': '=', 'expr': 'ta.ema(close, ema_fast_length)', 'conditions': []}, {'mode': '', 'name': 'ema_slow', 'op': '=', 'expr': 'ta.ema(close, ema_slow_length)', 'conditions': []}, {'mode': '', 'name': 'atr_value', 'op': '=', 'expr': 'ta.atr(atr_length)', 'conditions': []}, {'mode': '', 'name': 'atr_mean', 'op': '=', 'expr': 'ta.sma(atr_value, atr_mean_length)', 'conditions': []}, {'mode': '', 'name': 'atr_std', 'op': '=', 'expr': 'ta.stdev(atr_value, atr_std_length)', 'conditions': []}, {'mode': '', 'name': 'long_condition', 'op': '=', 'expr': 'ta.crossover(ema_fast, ema_slow) and atr_value > (atr_mean + atr_std)', 'conditions': []}, {'mode': '', 'name': 'short_condition', 'op': '=', 'expr': 'ta.crossunder(ema_fast, ema_slow) and atr_value > (atr_mean + atr_std)', 'conditions': []}, {'mode': '', 'name': 'long_stop_loss', 'op': '=', 'expr': 'close - 2 * atr_value // 基于ATR的止损', 'conditions': []}, {'mode': '', 'name': 'long_take_profit', 'op': '=', 'expr': 'close + 4 * atr_value // 基于ATR的止盈', 'conditions': []}, {'mode': '', 'name': 'short_stop_loss', 'op': '=', 'expr': 'close + 2 * atr_value // 基于ATR的止损', 'conditions': []}, {'mode': '', 'name': 'short_take_profit', 'op': '=', 'expr': 'close - 4 * atr_value // 基于ATR的止盈', 'conditions': []}, {'mode': '', 'name': 'position_size_calc', 'op': '=', 'expr': '(strategy.equity * risk_factor) / (2 * atr_value)', 'conditions': []}, {'mode': '', 'name': 'position_size', 'op': '=', 'expr': 'math.min(position_size_calc, strategy.equity) // 限制仓位不能大于账户总值', 'conditions': []}]
    pine_user_functions = []
    pine_controls = [{'indent': 0, 'statement': 'if (long_condition)'}, {'indent': 0, 'statement': 'if (short_condition)'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("Long", strategy.long, qty=position_size)', 'conditions': ['(long_condition)'], 'statement': 'strategy.entry("Long", strategy.long, qty=position_size)'}, {'kind': 'entry', 'call': 'strategy.entry("Short", strategy.short, qty=position_size)', 'conditions': ['(short_condition)'], 'statement': 'strategy.entry("Short", strategy.short, qty=position_size)'}, {'kind': 'exit', 'call': 'strategy.exit("Take Profit/Stop Loss Long", "Long", stop=long_stop_loss, limit=long_take_profit)', 'conditions': [], 'statement': 'strategy.exit("Take Profit/Stop Loss Long", "Long", stop=long_stop_loss, limit=long_take_profit)'}, {'kind': 'exit', 'call': 'strategy.exit("Take Profit/Stop Loss Short", "Short", stop=short_stop_loss, limit=short_take_profit)', 'conditions': [], 'statement': 'strategy.exit("Take Profit/Stop Loss Short", "Short", stop=short_stop_loss, limit=short_take_profit)'}]
    original_pine = '/*backtest\nstart: 2025-02-17 00:00:00\nend: 2025-02-24 00:00:00\nperiod: 1m\nbasePeriod: 1m\nexchanges: [{"eid":"Binance","currency":"SOL_USDT"}]\n*/\n\n//@version=6\nstrategy("Aggressive Strategy for High IV Market", overlay=true)\n\n// 用户输入\nema_fast_length = input.int(10, title="Fast EMA Length")\nema_slow_length = input.int(30, title="Slow EMA Length")\natr_length = input.int(14, title="ATR Length")\natr_mean_length = input.int(20, title="ATR Mean Length")\natr_std_length = input.int(20, title="ATR Std Dev Length")\nrisk_factor = input.float(0.01, title="Risk Factor")  // 单笔交易风险占账户资金的百分比\nslippage = input.float(0.001, title="Slippage") // 假设滑点\n\n// 计算EMA、ATR、均值、标准差\nema_fast = ta.ema(close, ema_fast_length)\nema_slow = ta.ema(close, ema_slow_length)\natr_value = ta.atr(atr_length)\natr_mean = ta.sma(atr_value, atr_mean_length)\natr_std = ta.stdev(atr_value, atr_std_length)\n\n// 进场条件\nlong_condition = ta.crossover(ema_fast, ema_slow) and atr_value > (atr_mean + atr_std)\nshort_condition = ta.crossunder(ema_fast, ema_slow) and atr_value > (atr_mean + atr_std)\n\n// 止损与止盈设置\nlong_stop_loss = close - 2 * atr_value  // 基于ATR的止损\nlong_take_profit = close + 4 * atr_value  // 基于ATR的止盈\nshort_stop_loss = close + 2 * atr_value  // 基于ATR的止损\nshort_take_profit = close - 4 * atr_value  // 基于ATR的止盈\n\n// 动态仓位控制\nposition_size_calc = (strategy.equity * risk_factor) / (2 * atr_value)\nposition_size = math.min(position_size_calc, strategy.equity)  // 限制仓位不能大于账户总值\n\n// 进场与出场信号\nif (long_condition)\n    strategy.entry("Long", strategy.long, qty=position_size)\n\nif (short_condition)\n    strategy.entry("Short", strategy.short, qty=position_size)\n\n// 止损与止盈\nstrategy.exit("Take Profit/Stop Loss Long", "Long", stop=long_stop_loss, limit=long_take_profit)\nstrategy.exit("Take Profit/Stop Loss Short", "Short", stop=short_stop_loss, limit=short_take_profit)\n\n// 绘制图表\nplot(ema_fast, title="Fast EMA", color=color.blue, linewidth=2)\nplot(ema_slow, title="Slow EMA", color=color.orange, linewidth=2)\nplot(long_stop_loss, title="Long Stop Loss", color=color.red, linewidth=1, style=plot.style_line)\nplot(long_take_profit, title="Long Take Profit", color=color.green, linewidth=1, style=plot.style_line)\nplot(short_stop_loss, title="Short Stop Loss", color=color.red, linewidth=1, style=plot.style_line)\nplot(short_take_profit, title="Short Take Profit", color=color.green, linewidth=1, style=plot.style_line)\n\n// 显示信号\nbgcolor(long_condition ? color.new(color.green, 90) : na, title="Long Signal Background")\nbgcolor(short_condition ? color.new(color.red, 90) : na, title="Short Signal Background")'

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
