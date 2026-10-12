"""Source-faithful deep-assisted port of 海龟交易三日反转策略Turtle-Trading-3-Day-Reversion-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_045cd6f7(PinePortBase, IStrategy):
    source_file = '海龟交易三日反转策略Turtle-Trading-3-Day-Reversion-Strategy.md'
    timeframe = '10m'
    can_short = False
    source_defaults = {'StartTime': "timestamp('01 Jan 2012 05:00 +0000'", 'EndTime': "timestamp('01 Jan 2099 00:00 +0000'"}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 100.0
    source_pyramiding = 0
    source_initial_capital = 10000000.0
    source_commission_percent = 1.0
    source_features = ['strategy.entry', 'strategy.close']
    source_fidelity_notes = []
    pine_assignments = [{'mode': '', 'name': 'StartTime', 'op': '=', 'expr': "input(defval=timestamp('01 Jan 2012 05:00 +0000'), title='Start Time')", 'conditions': []}, {'mode': '', 'name': 'EndTime', 'op': '=', 'expr': "input(defval=timestamp('01 Jan 2099 00:00 +0000'), title='End Time')", 'conditions': []}, {'mode': '', 'name': 'InDateRange', 'op': '=', 'expr': 'true', 'conditions': []}, {'mode': '', 'name': 'DayEMA5', 'op': '=', 'expr': 'ta.ema(close, 5)', 'conditions': []}, {'mode': '', 'name': 'Rule1', 'op': '=', 'expr': 'close>ta.ema(close, 200)', 'conditions': []}, {'mode': '', 'name': 'Rule2', 'op': '=', 'expr': 'close<DayEMA5', 'conditions': []}, {'mode': '', 'name': 'Rule3', 'op': '=', 'expr': 'high<high[1] and low<low[1] and high[1]<high[2] and low[1]<low[2] and high[2]<high[3] and low[2]<low[3]', 'conditions': []}, {'mode': '', 'name': 'ExitEMA', 'op': '=', 'expr': 'ta.ema(close, input.int(5, "EMA Length For Exit Strategy", tooltip = "The strategy will sell when the price crosses over this EMA"))', 'conditions': []}]
    pine_user_functions = []
    pine_controls = [{'indent': 0, 'statement': 'if (InDateRange)'}, {'indent': 0, 'statement': 'if (not InDateRange)'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("Long", strategy.long, when = Rule1 and Rule2 and Rule3)', 'conditions': ['(InDateRange)'], 'statement': 'strategy.entry("Long", strategy.long, when = Rule1 and Rule2 and Rule3)'}, {'kind': 'close', 'call': 'strategy.close("Long", when = ta.crossover(close, ExitEMA))', 'conditions': ['(InDateRange)'], 'statement': 'strategy.close("Long", when = ta.crossover(close, ExitEMA))'}, {'kind': 'close_all', 'call': 'strategy.close_all()', 'conditions': ['(not InDateRange)'], 'statement': 'strategy.close_all()'}]
    original_pine = '/*backtest\nstart: 2023-10-05 00:00:00\nend: 2023-10-12 00:00:00\nperiod: 10m\nbasePeriod: 1m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This source code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// @version = 5\n// Author = TradeAutomation\n\n\nstrategy(title="ETF 3-Day Reversion Strategy", shorttitle="ETF 3-Day Reversion Strategy", process_orders_on_close=true, overlay=true, commission_type=strategy.commission.cash_per_order, commission_value=1, initial_capital = 10000000, default_qty_type=strategy.percent_of_equity, default_qty_value=100)\n\n\n// Backtest Date Range Inputs // \nStartTime = input(defval=timestamp(\'01 Jan 2012 05:00 +0000\'), title=\'Start Time\')\nEndTime = input(defval=timestamp(\'01 Jan 2099 00:00 +0000\'), title=\'End Time\')\nInDateRange = true\n\n// Strategy Rules //\nDayEMA5 = ta.ema(close, 5)\nRule1 = close>ta.ema(close, 200)\nRule2 = close<DayEMA5\nRule3 = high<high[1] and low<low[1] and high[1]<high[2] and low[1]<low[2] and high[2]<high[3] and low[2]<low[3]\nExitEMA = ta.ema(close, input.int(5, "EMA Length For Exit Strategy", tooltip = "The strategy will sell when the price crosses over this EMA"))\nplot(DayEMA5)\nplot(ExitEMA, color=color.green)\n\n// Entry & Exit Functions //\nif (InDateRange)\n    strategy.entry("Long", strategy.long, when = Rule1 and Rule2 and Rule3)\n//    strategy.close("Long", when = ta.crossunder(close, ATRTrailingStop))\n    strategy.close("Long", when = ta.crossover(close, ExitEMA))\nif (not InDateRange)\n    strategy.close_all()'

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
