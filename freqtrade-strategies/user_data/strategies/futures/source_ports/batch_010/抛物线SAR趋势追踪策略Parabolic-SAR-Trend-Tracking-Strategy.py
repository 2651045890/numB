"""Source-faithful deep-assisted port of 抛物线SAR趋势追踪策略Parabolic-SAR-Trend-Tracking-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_07b06d54(PinePortBase, IStrategy):
    source_file = '抛物线SAR趋势追踪策略Parabolic-SAR-Trend-Tracking-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'SlowEMALength': 100, 'FastEMALength': 10, 'emaoffset': 1.0, 'start': 0.01, 'increment': 0.005, 'maximum': 0.08, 'fromDay': 1, 'fromMonth': 1, 'fromYear': 2019, 'toDay': 1, 'toMonth': 1, 'toYear': 2020}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 100.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.entry', 'strategy.close']
    source_fidelity_notes = []
    pine_assignments = [{'mode': '', 'name': 'SlowEMALength', 'op': '=', 'expr': 'input(100, "Slow EMA Length")', 'conditions': []}, {'mode': '', 'name': 'FastEMALength', 'op': '=', 'expr': 'input(10, "Fast EMA Length")', 'conditions': []}, {'mode': '', 'name': 'emaoffset', 'op': '=', 'expr': 'input(1.00, "EMA Offset %")', 'conditions': []}, {'mode': '', 'name': 'start', 'op': '=', 'expr': 'input(0.01)', 'conditions': []}, {'mode': '', 'name': 'increment', 'op': '=', 'expr': 'input(0.005)', 'conditions': []}, {'mode': '', 'name': 'maximum', 'op': '=', 'expr': 'input(0.08)', 'conditions': []}, {'mode': '', 'name': 'fromDay', 'op': '=', 'expr': 'input(defval = 1, title = "From Day", minval = 1, maxval = 31)', 'conditions': []}, {'mode': '', 'name': 'fromMonth', 'op': '=', 'expr': 'input(defval = 1, title = "From Month", minval = 1, maxval = 12)', 'conditions': []}, {'mode': '', 'name': 'fromYear', 'op': '=', 'expr': 'input(defval = 2019, title = "From Year", minval = 1970)', 'conditions': []}, {'mode': '', 'name': 'toDay', 'op': '=', 'expr': 'input(defval = 1, title = "To Day", minval = 1, maxval = 31)', 'conditions': []}, {'mode': '', 'name': 'toMonth', 'op': '=', 'expr': 'input(defval = 1, title = "To Month", minval = 1, maxval = 12)', 'conditions': []}, {'mode': '', 'name': 'toYear', 'op': '=', 'expr': 'input(defval = 2020, title = "To Year", minval = 1970)', 'conditions': []}, {'mode': '', 'name': 'startDate', 'op': '=', 'expr': 'timestamp(fromYear, fromMonth, fromDay, 00, 00)', 'conditions': []}, {'mode': '', 'name': 'finishDate', 'op': '=', 'expr': 'timestamp(toYear, toMonth, toDay, 00, 00)', 'conditions': []}, {'mode': '', 'name': 'time_cond', 'op': '=', 'expr': 'true', 'conditions': []}, {'mode': '', 'name': 'psar', 'op': '=', 'expr': 'sar(start, increment, maximum)', 'conditions': []}, {'mode': '', 'name': 'ema', 'op': '=', 'expr': 'ema(close, SlowEMALength)', 'conditions': []}, {'mode': '', 'name': 'fastema', 'op': '=', 'expr': 'ema(close, FastEMALength)', 'conditions': []}, {'mode': '', 'name': 'offset', 'op': '=', 'expr': '(emaoffset / 100) * ema', 'conditions': []}, {'mode': '', 'name': 'long', 'op': '=', 'expr': 'high[1] < psar[2] and high >= psar[1] and close > ema + offset or crossunder(ema, fastema) and close > psar and close > ema + offset', 'conditions': []}, {'mode': '', 'name': 'short', 'op': '=', 'expr': 'low[1] > psar[2] and low <= psar[1] and close < ema - offset or crossover(ema, fastema) and close < psar and close < ema - offset', 'conditions': []}]
    pine_user_functions = []
    pine_controls = [{'indent': 0, 'statement': 'if(high > psar)'}, {'indent': 0, 'statement': 'if(low < psar)'}, {'indent': 0, 'statement': 'if(long and time_cond)'}, {'indent': 0, 'statement': 'if(short and time_cond)'}, {'indent': 0, 'statement': 'if (not time_cond)'}]
    pine_orders = [{'kind': 'close', 'call': 'strategy.close("Short")', 'conditions': [], 'statement': 'strategy.close("Short")'}, {'kind': 'close', 'call': 'strategy.close("Long")', 'conditions': [], 'statement': 'strategy.close("Long")'}, {'kind': 'entry', 'call': 'strategy.entry("Long", strategy.long, comment="Long")', 'conditions': [], 'statement': 'strategy.entry("Long", strategy.long, comment="Long")'}, {'kind': 'entry', 'call': 'strategy.entry("Short", strategy.short, comment="Short")', 'conditions': [], 'statement': 'strategy.entry("Short", strategy.short, comment="Short")'}, {'kind': 'close_all', 'call': 'strategy.close_all()', 'conditions': ['(not time_cond)'], 'statement': 'strategy.close_all()'}]
    original_pine = '/*backtest\nstart: 2023-01-11 00:00:00\nend: 2024-01-17 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=3\nstrategy("SAR Trend Trader Strategy By: jhanson107", shorttitle="SAR Trend Trader Strategy", overlay=true, default_qty_type=strategy.percent_of_equity, default_qty_value=100)\n\n\nSlowEMALength = input(100, "Slow EMA Length")\nFastEMALength = input(10, "Fast EMA Length")\nemaoffset = input(1.00, "EMA Offset %")\nstart = input(0.01)\nincrement = input(0.005)\nmaximum = input(0.08)\n\n////////////////////////////////////////////////////////////////////////////////\n// BACKTESTING RANGE\n \n// From Date Inputs\nfromDay = input(defval = 1, title = "From Day", minval = 1, maxval = 31)\nfromMonth = input(defval = 1, title = "From Month", minval = 1, maxval = 12)\nfromYear = input(defval = 2019, title = "From Year", minval = 1970)\n \n// To Date Inputs\ntoDay = input(defval = 1, title = "To Day", minval = 1, maxval = 31)\ntoMonth = input(defval = 1, title = "To Month", minval = 1, maxval = 12)\ntoYear = input(defval = 2020, title = "To Year", minval = 1970)\n \n// Calculate start/end date and time condition\nstartDate = timestamp(fromYear, fromMonth, fromDay, 00, 00)\nfinishDate = timestamp(toYear, toMonth, toDay, 00, 00)\ntime_cond = true\n \n////////////////////////////////////////////////////////////////////////////////\n\npsar = sar(start, increment, maximum)\nema = ema(close, SlowEMALength)\nfastema = ema(close, FastEMALength)\noffset = (emaoffset / 100) * ema\n\n// Signals\nlong = high[1] < psar[2] and high >= psar[1] and close > ema + offset or crossunder(ema, fastema) and close > psar and close > ema + offset\nshort = low[1] > psar[2] and low <= psar[1] and close < ema - offset or crossover(ema, fastema) and close < psar and close < ema - offset\n\n// Plot PSAR\nplot(psar, title="PSAR", color = low < psar and not long ? green : red, trackprice=true)\n\n//Barcolor\nbarcolor(close > psar and close > ema + offset and fastema > ema ? green : na)\nbarcolor(close > psar and close < ema + offset or close > psar and fastema < ema ? white : na)\nbarcolor(close < psar and close < ema - offset and fastema < ema and close? red : na)\nbarcolor(close < psar and close > ema - offset or close < psar and fastema > ema ? white : na)\n\n//Plot EMA\nplot(ema, color=blue, linewidth=1, transp=0, title="Slow EMA")\nplot(fastema, color=purple, linewidth=1, transp=0, title="Fast EMA")\n\n\nif(high > psar)\n    strategy.close("Short")\n    \nif(low < psar)\n    strategy.close("Long")\n    \nif(long and time_cond)\n    strategy.entry("Long", strategy.long, comment="Long")\n   \nif(short and time_cond)\n    strategy.entry("Short", strategy.short, comment="Short")\n\nif (not time_cond)\n    strategy.close_all()'

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
