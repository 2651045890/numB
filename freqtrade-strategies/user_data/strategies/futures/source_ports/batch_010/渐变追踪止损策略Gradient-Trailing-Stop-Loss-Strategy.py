"""Source-faithful deep-assisted port of 渐变追踪止损策略Gradient-Trailing-Stop-Loss-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_59b072f2(PinePortBase, IStrategy):
    source_file = '渐变追踪止损策略Gradient-Trailing-Stop-Loss-Strategy.md'
    timeframe = '10m'
    can_short = True
    source_defaults = {'startYear': 2020, 'startMonth': 1, 'startDay': 1, 'endYear': 9999, 'endMonth': 12, 'endDay': 31, 'atrPeriod': 10, 'factor': 3.0}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 15.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.entry', 'strategy.equity', 'var ']
    source_fidelity_notes = ['Uses persistent Pine state (var/varip); state is order-dependent and must be evaluated bar-by-bar, not replaced by a vectorized fill-forward approximation.', 'Reads broker/strategy state; signals depend on fill timing and cannot be reduced to indicator-only booleans without changing behavior.']
    pine_assignments = [{'mode': '', 'name': 'startYear', 'op': '=', 'expr': 'input(2020, title="Start Year")', 'conditions': []}, {'mode': '', 'name': 'startMonth', 'op': '=', 'expr': 'input(1, title="Start Month")', 'conditions': []}, {'mode': '', 'name': 'startDay', 'op': '=', 'expr': 'input(1, title="Start Day")', 'conditions': []}, {'mode': '', 'name': 'endYear', 'op': '=', 'expr': 'input(9999, title="End Year")', 'conditions': []}, {'mode': '', 'name': 'endMonth', 'op': '=', 'expr': 'input(12, title="End Month")', 'conditions': []}, {'mode': '', 'name': 'endDay', 'op': '=', 'expr': 'input(31, title="End Day")', 'conditions': []}, {'mode': '', 'name': 'backtestingTimeBool', 'op': '=', 'expr': '(year >= startYear and month >= startMonth and dayofmonth >= startDay) and (year <= endYear and month <= endMonth and dayofmonth <= endDay)', 'conditions': []}, {'mode': '', 'name': 'atrPeriod', 'op': '=', 'expr': 'input(10, "ATR Length")', 'conditions': []}, {'mode': '', 'name': 'factor', 'op': '=', 'expr': 'input.float(3.0, "Factor", step = 0.01)', 'conditions': []}, {'mode': 'var', 'name': 'longCondition', 'op': '=', 'expr': 'false', 'conditions': []}, {'mode': 'var', 'name': 'shortCondition', 'op': '=', 'expr': 'false', 'conditions': []}, {'mode': '', 'name': 'prevDirection', 'op': '=', 'expr': 'direction[1]', 'conditions': ['backtestingTimeBool']}, {'mode': '', 'name': 'longCondition', 'op': ':=', 'expr': 'false', 'conditions': ['backtestingTimeBool', 'direction < 0']}, {'mode': '', 'name': 'shortCondition', 'op': ':=', 'expr': 'true', 'conditions': ['backtestingTimeBool', 'direction < 0']}, {'mode': '', 'name': 'longCondition', 'op': ':=', 'expr': 'true', 'conditions': ['backtestingTimeBool', 'direction > 0']}, {'mode': '', 'name': 'shortCondition', 'op': ':=', 'expr': 'false', 'conditions': ['backtestingTimeBool', 'direction > 0']}]
    pine_user_functions = []
    pine_controls = [{'indent': 0, 'statement': 'if backtestingTimeBool'}, {'indent': 4, 'statement': 'if direction < 0'}, {'indent': 4, 'statement': 'else if direction > 0'}, {'indent': 0, 'statement': 'if longCondition'}, {'indent': 0, 'statement': 'if shortCondition'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("My Long Entry Id", strategy.long)', 'conditions': ['longCondition'], 'statement': 'strategy.entry("My Long Entry Id", strategy.long)'}, {'kind': 'entry', 'call': 'strategy.entry("My Short Entry Id", strategy.short)', 'conditions': ['shortCondition'], 'statement': 'strategy.entry("My Short Entry Id", strategy.short)'}]
    original_pine = '/*backtest\nstart: 2023-10-17 00:00:00\nend: 2023-10-24 00:00:00\nperiod: 10m\nbasePeriod: 1m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("Supertrend Strategy, by Ho.J.", overlay=true, default_qty_type=strategy.percent_of_equity, default_qty_value=15)\n\n// 백테스팅 시작일과 종료일 입력\nstartYear = input(2020, title="Start Year")\nstartMonth = input(1, title="Start Month")\nstartDay = input(1, title="Start Day")\n\nendYear = input(9999, title="End Year")\nendMonth = input(12, title="End Month")\nendDay = input(31, title="End Day")\n\n// 백테스팅 시간 범위 확인\nbacktestingTimeBool = (year >= startYear and month >= startMonth and dayofmonth >= startDay) and (year <= endYear and month <= endMonth and dayofmonth <= endDay)\n\natrPeriod = input(10, "ATR Length")\nfactor = input.float(3.0, "Factor", step = 0.01)\n\n[_, direction] = ta.supertrend(factor, atrPeriod)\n\nvar bool longCondition = false\nvar bool shortCondition = false\n\nif backtestingTimeBool\n    prevDirection = direction[1]\n    if direction < 0\n        longCondition := false\n        shortCondition := true\n    else if direction > 0\n        longCondition := true\n        shortCondition := false\n\nif longCondition\n    strategy.entry("My Long Entry Id", strategy.long)\n\nif shortCondition\n    strategy.entry("My Short Entry Id", strategy.short)\n\nplot(strategy.equity, title="equity", color=color.rgb(255, 255, 255), linewidth=2, style=plot.style_area)'

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
