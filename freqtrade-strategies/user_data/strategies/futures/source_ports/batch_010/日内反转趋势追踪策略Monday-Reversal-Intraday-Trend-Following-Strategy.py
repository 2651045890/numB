"""Source-faithful deep-assisted port of 日内反转趋势追踪策略Monday-Reversal-Intraday-Trend-Following-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_ebcc0a2c(PinePortBase, IStrategy):
    source_file = '日内反转趋势追踪策略Monday-Reversal-Intraday-Trend-Following-Strategy.md'
    timeframe = '1h'
    can_short = False
    source_defaults = {'FirstYear': 2018, 'deltaDay': 0, 'StartHour': 0, 'HoldTime': 6, 'MM': 1, 'startHour': -7, 'endHour': 34, 'exitHour': 30}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.entry', 'strategy.close', 'strategy.position_size', 'strategy.equity', '=>']
    source_fidelity_notes = ['Reads broker/strategy state; signals depend on fill timing and cannot be reduced to indicator-only booleans without changing behavior.']
    pine_assignments = [{'mode': '', 'name': 'FirstYear', 'op': '=', 'expr': 'input(2018, minval=2000, maxval=2023, step=1)', 'conditions': []}, {'mode': '', 'name': 'FirstMonth', 'op': '=', 'expr': '1 //input(1, minval=1, maxval=12, step=1)', 'conditions': []}, {'mode': '', 'name': 'FirstDay', 'op': '=', 'expr': '1 //input(1, minval=1, maxval=31, step=1)', 'conditions': []}, {'mode': '', 'name': 'deltaDay', 'op': '=', 'expr': 'input(0)', 'conditions': []}, {'mode': '', 'name': 'StartHour', 'op': '=', 'expr': 'input(0)', 'conditions': []}, {'mode': '', 'name': 'HoldTime', 'op': '=', 'expr': 'input(6, step=1)', 'conditions': []}, {'mode': '', 'name': 'MM', 'op': '=', 'expr': 'input(1)', 'conditions': []}, {'mode': '', 'name': 'startHour', 'op': '=', 'expr': 'input(-7, step=1)', 'conditions': []}, {'mode': '', 'name': 'endHour', 'op': '=', 'expr': 'input(34, step=1)', 'conditions': []}, {'mode': '', 'name': 'exitHour', 'op': '=', 'expr': 'input(30, step=1)', 'conditions': []}, {'mode': '', 'name': 'startdateCond', 'op': '=', 'expr': '(year > FirstYear or (year == FirstYear and (month > FirstMonth or (month == FirstMonth and dayofmonth >= FirstDay))))', 'conditions': []}, {'mode': '', 'name': 'iHour', 'op': '=', 'expr': 'hour', 'conditions': []}, {'mode': '', 'name': 'iHour', 'op': ':=', 'expr': 'iHour-20', 'conditions': ['iHour > 19']}, {'mode': '', 'name': 'iHour', 'op': ':=', 'expr': 'iHour+4', 'conditions': ['ELSE']}, {'mode': '', 'name': 'timeCondition', 'op': '=', 'expr': 'true //(iHour>=startHour and iHour<=endHour and iHour<=exitHour)', 'conditions': []}, {'mode': '', 'name': 'since_flat_condition', 'op': '=', 'expr': 'strategy.position_size == 0', 'conditions': []}, {'mode': '', 'name': 'entryPrice', 'op': '=', 'expr': 'strategy.position_avg_price', 'conditions': []}, {'mode': '', 'name': 'EntryLongCondition', 'op': '=', 'expr': 'dayofweek == (dayofweek.monday+deltaDay) and close[0] < close[1] and close[1]<close[2] and startdateCond //and timeCondition and iHour > StartHour', 'conditions': []}, {'mode': '', 'name': 'ExitTimeCondition', 'op': '=', 'expr': 'false//(f_barssince(since_flat_condition, 0)>=HoldTime)', 'conditions': []}, {'mode': '', 'name': 'ExitLongCondition', 'op': '=', 'expr': 'strategy.position_size > 0 and (close[0] > high[1])// or close[0]< entryPrice-abs(close[1]-close[2])*0.2)//(ExitTimeCondition) //iHour >= exitHour or', 'conditions': []}, {'mode': '', 'name': 'lots', 'op': '=', 'expr': 'if MM < 2', 'conditions': []}, {'mode': '', 'name': 'lots', 'op': ':=', 'expr': 'lots/close', 'conditions': []}, {'mode': '', 'name': 'entryPrice', 'op': ':=', 'expr': 'strategy.position_avg_price', 'conditions': []}]
    pine_user_functions = [{'name': 'f_barssince', 'args': '_cond, _count', 'body': '_barssince=bar_index-valuewhen(_cond, bar_index, _count)'}]
    pine_controls = [{'indent': 0, 'statement': 'if iHour > 19'}, {'indent': 0, 'statement': 'else'}, {'indent': 0, 'statement': 'else'}]
    pine_orders = [{'kind': 'close', 'call': 'strategy.close("ETLong",when=(ExitLongCondition==true))', 'conditions': [], 'statement': 'strategy.close("ETLong",when=(ExitLongCondition==true))'}, {'kind': 'entry', 'call': 'strategy.entry("ETLong", strategy.long, qty=lots, comment="OpenLong",when=(EntryLongCondition==true))', 'conditions': [], 'statement': 'strategy.entry("ETLong", strategy.long, qty=lots, comment="OpenLong",when=(EntryLongCondition==true))'}]
    original_pine = '/*backtest\nstart: 2023-10-06 00:00:00\nend: 2023-11-05 00:00:00\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=4\nstrategy("ET Forex TurnaroundMonday", overlay=true)\nFirstYear = input(2018, minval=2000, maxval=2023, step=1)\nFirstMonth = 1 //input(1, minval=1, maxval=12, step=1)\nFirstDay = 1 //input(1, minval=1, maxval=31, step=1)\n\ndeltaDay = input(0)\nStartHour = input(0)\n\nf_barssince(_cond, _count) => _barssince=bar_index-valuewhen(_cond, bar_index, _count)\n\nHoldTime = input(6, step=1)\n\nMM = input(1)\n\nstartHour = input(-7, step=1)\nendHour = input(34, step=1)\nexitHour = input(30, step=1)\n\n\nstartdateCond = (year > FirstYear or (year == FirstYear and (month > FirstMonth or (month == FirstMonth and dayofmonth >= FirstDay))))\n\niHour = hour\nif iHour > 19 \n    iHour := iHour-20\nelse\n    iHour := iHour+4    \n    \n    \ntimeCondition = true //(iHour>=startHour and iHour<=endHour and iHour<=exitHour)\n\nsince_flat_condition = strategy.position_size == 0\n\nentryPrice=strategy.position_avg_price\nEntryLongCondition = dayofweek == (dayofweek.monday+deltaDay) and close[0] < close[1] and close[1]<close[2] and startdateCond //and timeCondition and iHour > StartHour\nExitTimeCondition = false//(f_barssince(since_flat_condition, 0)>=HoldTime)\nExitLongCondition = strategy.position_size > 0  and (close[0] > high[1])// or close[0]< entryPrice-abs(close[1]-close[2])*0.2)//(ExitTimeCondition) //iHour >= exitHour or \nstrategy.initial_capital =50000\n// MM Block\nlots = if MM < 2 \n    strategy.initial_capital \nelse \n    strategy.equity\n\nlots := lots/close\n\nentryPrice:=strategy.position_avg_price\nstrategy.close("ETLong",when=(ExitLongCondition==true))\nstrategy.entry("ETLong", strategy.long, qty=lots, comment="OpenLong",when=(EntryLongCondition==true))'

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
