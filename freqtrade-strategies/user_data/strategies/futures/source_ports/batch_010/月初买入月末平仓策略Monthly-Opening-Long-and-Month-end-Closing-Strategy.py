"""Source-faithful deep-assisted port of 月初买入月末平仓策略Monthly-Opening-Long-and-Month-end-Closing-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_f7273458(PinePortBase, IStrategy):
    source_file = '月初买入月末平仓策略Monthly-Opening-Long-and-Month-end-Closing-Strategy.md'
    timeframe = '1h'
    can_short = True
    source_defaults = {'Year': 2020, 'Month': 1, 'LongOnly': True, 'Use_stoploss': False, 'stoploss_input': 150}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 100.0
    source_pyramiding = 0
    source_initial_capital = 1000.0
    source_commission_percent = 0.2
    source_features = ['strategy.entry', 'strategy.close', 'strategy.position_size']
    source_fidelity_notes = ['Reads broker/strategy state; signals depend on fill timing and cannot be reduced to indicator-only booleans without changing behavior.']
    pine_assignments = [{'mode': '', 'name': 'Year', 'op': '=', 'expr': 'input(defval = 2020, title = "From Year", minval = 2010) //', 'conditions': []}, {'mode': '', 'name': 'Month', 'op': '=', 'expr': 'input(defval = 1, title = "From Month", minval = 1, maxval=12)', 'conditions': []}, {'mode': '', 'name': 'LongOnly', 'op': '=', 'expr': 'input(true, title="Only go Long?")', 'conditions': []}, {'mode': '', 'name': 'longCondition', 'op': '=', 'expr': 'dayofweek==dayofweek.monday and (time > timestamp(Year, Month, 01, 00, 00, 00))', 'conditions': []}, {'mode': '', 'name': 'shortCondition', 'op': '=', 'expr': 'dayofweek==dayofweek.friday and (time > timestamp(Year, Month, 01, 23, 59, 59))', 'conditions': []}, {'mode': '', 'name': 'Use_stoploss', 'op': '=', 'expr': 'input(false, title="Use stoploss ?")', 'conditions': []}, {'mode': '', 'name': 'stoploss_input', 'op': '=', 'expr': 'input(150, title="Stoploss in $")', 'conditions': []}, {'mode': '', 'name': 'Stoploss', 'op': '=', 'expr': 'Use_stoploss ? strategy.position_size>0 ? iff(strategy.position_size>0,strategy.position_avg_price - stoploss_input, na) : strategy.position_size<0 ? iff(strategy.position_size<0,strategy.position_avg_price + stoploss_input, na) : na : na', 'conditions': []}]
    pine_user_functions = []
    pine_controls = [{'indent': 0, 'statement': 'if (longCondition)'}, {'indent': 0, 'statement': 'if (shortCondition and LongOnly==false)'}, {'indent': 0, 'statement': 'if (shortCondition and LongOnly)'}, {'indent': 0, 'statement': 'if (low < Stoploss)'}, {'indent': 0, 'statement': 'if (high > Stoploss)'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("Buy on Monday", strategy.long)', 'conditions': ['(longCondition)'], 'statement': 'strategy.entry("Buy on Monday", strategy.long)'}, {'kind': 'entry', 'call': 'strategy.entry("Short on Friday", strategy.short)', 'conditions': ['(shortCondition and LongOnly==false)'], 'statement': 'strategy.entry("Short on Friday", strategy.short)'}, {'kind': 'close', 'call': 'strategy.close("Buy on Monday", comment="Sell on Friday")', 'conditions': ['(shortCondition and LongOnly)'], 'statement': 'strategy.close("Buy on Monday", comment="Sell on Friday")'}, {'kind': 'close', 'call': 'strategy.close("Buy on Monday", comment="Long Stopped on Someday")', 'conditions': ['(low < Stoploss)'], 'statement': 'strategy.close("Buy on Monday", comment="Long Stopped on Someday")'}, {'kind': 'close', 'call': 'strategy.close("Short on Friday", comment="Short Stopped on Someday")', 'conditions': ['(high > Stoploss)'], 'statement': 'strategy.close("Short on Friday", comment="Short Stopped on Someday")'}]
    original_pine = '/*backtest\nstart: 2023-10-02 00:00:00\nend: 2023-11-01 00:00:00\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// © Je_Buurman September 1st 2020\n\n//@version=4\nstrategy("Buurmans Tutorial", overlay=true, initial_capital=1000, pyramiding=0, default_qty_type=strategy.percent_of_equity, default_qty_value=100, commission_value=0.2)\n\n// Some initial inputs, these are needed in case the strategy returns an error of "too many trades, > 3000" \n\nYear    = input(defval = 2020, title = "From Year", minval = 2010)              // \nMonth   = input(defval = 1, title = "From Month", minval = 1, maxval=12)\nLongOnly=input(true, title="Only go Long?")\n\n\n// Phase I - the initial "Strategy" - buy Monday, sell Friday\n\nlongCondition = dayofweek==dayofweek.monday and (time > timestamp(Year, Month, 01, 00, 00, 00))\nshortCondition = dayofweek==dayofweek.friday and (time > timestamp(Year, Month, 01, 23, 59, 59))\n\n\n// Phase II - some rudimentary "risk-management" e.g. stoploss\n\nUse_stoploss=input(false, title="Use stoploss ?")\nstoploss_input=input(150, title="Stoploss in $")\nStoploss = Use_stoploss ? strategy.position_size>0 ? iff(strategy.position_size>0,strategy.position_avg_price - stoploss_input, na) : strategy.position_size<0 ? iff(strategy.position_size<0,strategy.position_avg_price + stoploss_input, na) : na : na\nplot(Use_stoploss and strategy.position_size!=0 ? Stoploss : na, color=iff(Stoploss!=na,color.silver, color.red),style=plot.style_linebr)\n\n\n// Phase III - make it more profitable by trying to filter conditions\n// only buy on odd Mondays ? only buy on full moon Mondays ? something else entirely ?\n\n\n// The actual trades, going Long, close Long, going Short and Stoploss\n\nif (longCondition)\n    strategy.entry("Buy on Monday", strategy.long)\n    \nif (shortCondition and LongOnly==false)\n    strategy.entry("Short on Friday", strategy.short)\n\nif (shortCondition and LongOnly)\n    strategy.close("Buy on Monday", comment="Sell on Friday")\n\nif (low < Stoploss)\n    strategy.close("Buy on Monday", comment="Long Stopped on Someday")\nif (high > Stoploss)\n    strategy.close("Short on Friday", comment="Short Stopped on Someday")'

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
