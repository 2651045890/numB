"""Source-faithful deep-assisted port of 移动均线交叉趋势追踪策略Moving-Average-Crossover-Trend-Following-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_6a0e4ccd(PinePortBase, IStrategy):
    source_file = '移动均线交叉趋势追踪策略Moving-Average-Crossover-Trend-Following-Strategy.md'
    timeframe = '5m'
    can_short = True
    source_defaults = {'emaFast': 10, 'emaSlow': 20, 'tradeDirection': 'Both', 'startDate': "timestamp('01 Jan 2023 00:00'", 'endDate': "timestamp('31 Dec 2030 23:59'", 'take_profit_percent': 1.0, 'stop_loss_percent': 1.0}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.exit', 'strategy.entry', 'strategy.position_size']
    source_fidelity_notes = ['Reads broker/strategy state; signals depend on fill timing and cannot be reduced to indicator-only booleans without changing behavior.', 'Uses strategy.exit; stop/limit/profit/loss/trailing arguments have Pine order semantics and may fill intrabar.']
    pine_assignments = [{'mode': '', 'name': 'emaFast', 'op': '=', 'expr': "input.int(title='Fast EMA', defval=10, minval=1, maxval=9999)", 'conditions': []}, {'mode': '', 'name': 'emaSlow', 'op': '=', 'expr': "input.int(title='Slow EMA', defval=20, minval=1, maxval=9999)", 'conditions': []}, {'mode': '', 'name': 'tradeDirection', 'op': '=', 'expr': "input.string(title='Trade Direction', options=['Long', 'Short', 'Both'], defval='Both')", 'conditions': []}, {'mode': '', 'name': 'startDate', 'op': '=', 'expr': "input(title='Start Date', defval=timestamp('01 Jan 2023 00:00'))", 'conditions': []}, {'mode': '', 'name': 'endDate', 'op': '=', 'expr': "input(title='End Date', defval=timestamp('31 Dec 2030 23:59'))", 'conditions': []}, {'mode': '', 'name': 'take_profit_percent', 'op': '=', 'expr': 'input(1.0, title ="Take Profit Percent") / 100.0', 'conditions': []}, {'mode': '', 'name': 'stop_loss_percent', 'op': '=', 'expr': 'input(1.0, title ="Stop Loss Percent") / 100.0', 'conditions': []}, {'mode': '', 'name': 'fastEMA', 'op': '=', 'expr': 'ta.ema(close, emaFast)', 'conditions': []}, {'mode': '', 'name': 'slowEMA', 'op': '=', 'expr': 'ta.ema(close, emaSlow)', 'conditions': []}, {'mode': '', 'name': 'emapos', 'op': '=', 'expr': 'ta.ema(close, 200)', 'conditions': []}, {'mode': '', 'name': 'inDateRange', 'op': '=', 'expr': 'true', 'conditions': []}, {'mode': '', 'name': 'longOK', 'op': '=', 'expr': "tradeDirection == 'Long' or tradeDirection == 'Both'", 'conditions': []}, {'mode': '', 'name': 'shortOK', 'op': '=', 'expr': "tradeDirection == 'Short' or tradeDirection == 'Both'", 'conditions': []}, {'mode': '', 'name': 'longCondition', 'op': '=', 'expr': 'ta.crossover(fastEMA, slowEMA) and inDateRange', 'conditions': []}, {'mode': '', 'name': 'shortCondition', 'op': '=', 'expr': 'ta.crossunder(fastEMA, slowEMA) and inDateRange', 'conditions': []}]
    pine_user_functions = []
    pine_controls = [{'indent': 0, 'statement': 'if longCondition and longOK'}, {'indent': 0, 'statement': 'if shortCondition and shortOK'}, {'indent': 0, 'statement': 'if strategy.position_size > 0 and longOK'}, {'indent': 0, 'statement': 'if strategy.position_size < 0 and shortOK'}]
    pine_orders = [{'kind': 'entry', 'call': "strategy.entry(id='long', direction=strategy.long)", 'conditions': ['longCondition and longOK'], 'statement': "strategy.entry(id='long', direction=strategy.long)"}, {'kind': 'entry', 'call': "strategy.entry(id='short', direction=strategy.short)", 'conditions': ['shortCondition and shortOK'], 'statement': "strategy.entry(id='short', direction=strategy.short)"}, {'kind': 'exit', 'call': "strategy.exit(id='exit long', from_entry='long', limit=strategy.position_avg_price * (1 + take_profit_percent), stop=strategy.position_avg_price * (1 - stop_loss_percent))", 'conditions': ['strategy.position_size > 0 and longOK'], 'statement': "strategy.exit(id='exit long', from_entry='long', limit=strategy.position_avg_price * (1 + take_profit_percent), stop=strategy.position_avg_price * (1 - stop_loss_percent))"}, {'kind': 'exit', 'call': "strategy.exit(id='exit short', from_entry='short', limit=strategy.position_avg_price * (1 - take_profit_percent), stop=strategy.position_avg_price * (1 + stop_loss_percent))", 'conditions': ['strategy.position_size < 0 and shortOK'], 'statement': "strategy.exit(id='exit short', from_entry='short', limit=strategy.position_avg_price * (1 - take_profit_percent), stop=strategy.position_avg_price * (1 + stop_loss_percent))"}]
    original_pine = '/*backtest\nstart: 2024-01-28 00:00:00\nend: 2024-02-04 00:00:00\nperiod: 5m\nbasePeriod: 1m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy(\'Zhukov trade\', overlay=true, calc_on_every_tick=true, currency=currency.USD)\n\n// INPUT:\n\n// Options to enter fast and slow Exponential Moving Average (EMA) values\nemaFast = input.int(title=\'Fast EMA\', defval=10, minval=1, maxval=9999)\nemaSlow = input.int(title=\'Slow EMA\', defval=20, minval=1, maxval=9999)\n\n// Option to select trade directions\ntradeDirection = input.string(title=\'Trade Direction\', options=[\'Long\', \'Short\', \'Both\'], defval=\'Both\')\n\n// Options that configure the backtest date range\nstartDate = input(title=\'Start Date\', defval=timestamp(\'01 Jan 2023 00:00\'))\nendDate = input(title=\'End Date\', defval=timestamp(\'31 Dec 2030 23:59\'))\n\n// Set take profit and stop loss percentages\ntake_profit_percent = input(1.0, title ="Take Profit Percent") / 100.0\nstop_loss_percent = input(1.0, title ="Stop Loss Percent") / 100.0\n\n// CALCULATIONS:\n\n// Use the built-in function to calculate two EMA lines\nfastEMA = ta.ema(close, emaFast)\nslowEMA = ta.ema(close, emaSlow)\nemapos = ta.ema(close, 200)\n\n// PLOT:\n\n// Draw the EMA lines on the chart\nplot(series=fastEMA, color=color.new(color.orange, 0), linewidth=2)\nplot(series=slowEMA, color=color.new(color.blue, 0), linewidth=2)\nplot(series=emapos, color=color.new(color.red, 0), linewidth=2)\n\n// CONDITIONS:\n\n// Check if the close time of the current bar falls inside the date range\ninDateRange = true\n\n// Translate input into trading conditions\nlongOK = tradeDirection == \'Long\' or tradeDirection == \'Both\'\nshortOK = tradeDirection == \'Short\' or tradeDirection == \'Both\'\n\n// Decide if we should go long or short using the built-in functions\nlongCondition = ta.crossover(fastEMA, slowEMA) and inDateRange\nshortCondition = ta.crossunder(fastEMA, slowEMA) and inDateRange\n\n// ORDERS:\n\n// Submit entry (or reverse) orders\nif longCondition and longOK\n    strategy.entry(id=\'long\', direction=strategy.long)\n\nif shortCondition and shortOK\n    strategy.entry(id=\'short\', direction=strategy.short)\n\n// Exit orders\nif strategy.position_size > 0 and longOK\n    strategy.exit(id=\'exit long\', from_entry=\'long\', limit=strategy.position_avg_price * (1 + take_profit_percent), stop=strategy.position_avg_price * (1 - stop_loss_percent))\n\nif strategy.position_size < 0 and shortOK\n    strategy.exit(id=\'exit short\', from_entry=\'short\', limit=strategy.position_avg_price * (1 - take_profit_percent), stop=strategy.position_avg_price * (1 + stop_loss_percent))'

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
